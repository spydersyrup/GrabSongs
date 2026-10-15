import os
import re
import yt_dlp
from PyQt6.QtCore import QThread, pyqtSignal
from typing import Dict, Any, Optional
from core.metadata.lyrics import LyricsFetcher
from core.downloader.tagger import AudioTagger

def sanitize_filename(name: str) -> str:
    return re.sub(r'[<>:"/\\|?*]', '_', name).strip()

def find_best_audio_match(ydl, title: str, artist: str, target_duration: int = 0) -> Optional[str]:
    clean_title = re.sub(r'[\(\[].*?(official|video|audio|lyrics|explicit|remastered).*?[\)\]]', '', title, flags=re.IGNORECASE).strip()
    query = f"{artist} - {clean_title} audio"
    search_target = f"ytsearch5:{query}"

    try:
        results = ydl.extract_info(search_target, download=False)
        entries = results.get('entries') if results else []
        if not entries:
            return None

        best_entry = None
        best_score = -999.0

        target_lower = title.lower()
        is_live_target = "live" in target_lower
        is_remix_target = "remix" in target_lower

        for entry in entries:
            if not entry:
                continue

            entry_title = (entry.get('title') or '').lower()
            uploader = (entry.get('uploader') or '').lower()
            duration = int(entry.get('duration') or 0)

            if not is_live_target and ("live" in entry_title or "concert" in entry_title):
                continue
            if not is_remix_target and ("remix" in entry_title or "mashup" in entry_title):
                continue
            if "cover" in entry_title or "karaoke" in entry_title or "instrumental" in entry_title:
                continue

            score = 100.0

            if target_duration > 0 and duration > 0:
                diff = abs(duration - target_duration)
                if diff <= 3:
                    score += 50.0
                elif diff <= 7:
                    score += 30.0
                elif diff <= 15:
                    score += 10.0
                elif diff > 35:
                    score -= 40.0

            artist_parts = [p.strip().lower() for p in re.split(r'[,&/]', artist)]
            for ap in artist_parts:
                if ap and (ap in uploader or ap in entry_title):
                    score += 20.0
                    break

            if "topic" in uploader:
                score += 35.0
            if "official audio" in entry_title or "audio" in entry_title:
                score += 15.0

            if score > best_score:
                best_score = score
                best_entry = entry

        if best_entry:
            return best_entry.get('webpage_url') or best_entry.get('url') or f"https://www.youtube.com/watch?v={best_entry.get('id')}"

        first = entries[0]
        return first.get('webpage_url') or first.get('url') or f"https://www.youtube.com/watch?v={first.get('id')}"
    except Exception as e:
        print(f"[Matcher] Error finding match: {e}")
        return None

class DownloadWorker(QThread):
    progress_signal = pyqtSignal(str, float, str, str, str)  # job_id, percent, speed, eta, status
    finished_signal = pyqtSignal(str, str, dict)            # job_id, file_path, metadata
    error_signal = pyqtSignal(str, str)                     # job_id, error_message

    def __init__(self, job_id: str, track_meta: Dict[str, Any], config: Dict[str, Any], parent=None):
        super().__init__(parent)
        self.job_id = job_id
        self.meta = dict(track_meta)
        self.config = dict(config)
        self._is_cancelled = False

    def cancel(self):
        self._is_cancelled = True

    def run(self):
        try:
            self.progress_signal.emit(self.job_id, 0.0, "", "", "Searching audio stream...")

            artist = sanitize_filename(self.meta.get("artist", "Unknown Artist"))
            title = sanitize_filename(self.meta.get("title", "Unknown Track"))
            album = sanitize_filename(self.meta.get("album", "Unknown Album"))
            track_num = self.meta.get("track_number", 1)
            duration = int(self.meta.get("duration", 0))

            audio_fmt = self.config.get("audio_format", "mp3").lower()
            quality = self.config.get("audio_quality", "320")
            download_dir = self.config.get("download_dir", os.path.expanduser("~/Music/GrabSongs"))
            os.makedirs(download_dir, exist_ok=True)

            naming_pattern = self.config.get("naming_pattern", "{artist} - {title}")
            try:
                base_name = naming_pattern.format(
                    artist=artist,
                    title=title,
                    album=album,
                    track=int(track_num)
                )
            except Exception:
                base_name = f"{artist} - {title}"

            base_name = sanitize_filename(base_name)
            out_tmpl = os.path.join(download_dir, f"{base_name}.%(ext)s")

            # Determine source or search target
            service = self.meta.get("service")
            source_url = self.meta.get("source_url", "")
            if service in ("youtube", "generic") and source_url:
                target_url = source_url
            else:
                self.progress_signal.emit(self.job_id, 5.0, "", "", "Matching studio audio stream...")
                with yt_dlp.YoutubeDL({'quiet': True, 'extract_flat': True}) as search_ydl:
                    matched_url = find_best_audio_match(search_ydl, title, artist, duration)
                if matched_url:
                    target_url = matched_url
                else:
                    query_str = self.meta.get("search_query") or f"{artist} - {title} audio"
                    target_url = f"ytsearch1:{query_str}"

            ffmpeg_path = self.config.get("ffmpeg_path", "")

            def progress_hook(d):
                if self._is_cancelled:
                    raise Exception("Download cancelled by user.")
                status = d.get('status')
                if status == 'downloading':
                    total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate') or 0
                    downloaded = d.get('downloaded_bytes') or 0
                    percent = (downloaded / total_bytes * 100.0) if total_bytes > 0 else 0.0
                    speed_bytes = d.get('speed') or 0
                    speed_str = f"{speed_bytes / 1024 / 1024:.2f} MB/s" if speed_bytes > 0 else ""
                    eta_sec = d.get('eta') or 0
                    eta_str = f"{int(eta_sec)}s" if eta_sec > 0 else ""
                    self.progress_signal.emit(self.job_id, percent, speed_str, eta_str, "Downloading...")
                elif status == 'finished':
                    self.progress_signal.emit(self.job_id, 95.0, "", "", "Converting audio...")

            ydl_opts: Dict[str, Any] = {
                'format': 'bestaudio/best',
                'outtmpl': out_tmpl,
                'progress_hooks': [progress_hook],
                'quiet': True,
                'no_warnings': True,
                'noplaylist': True,
            }

            if ffmpeg_path and os.path.exists(ffmpeg_path):
                ydl_opts['ffmpeg_location'] = ffmpeg_path

            if audio_fmt in ("mp3", "m4a", "flac", "opus"):
                codec_map = {
                    "mp3": "mp3",
                    "m4a": "m4a",
                    "flac": "flac",
                    "opus": "opus",
                }
                preferred_codec = codec_map.get(audio_fmt, "mp3")
                postproc = {
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': preferred_codec,
                }
                if audio_fmt in ("mp3", "m4a"):
                    postproc['preferredquality'] = quality if quality != "lossless" else "320"
                ydl_opts['postprocessors'] = [postproc]

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(target_url, download=True)
                if not info:
                    raise Exception("Audio stream could not be found.")

            expected_ext = audio_fmt if audio_fmt != "opus" else "opus"
            final_path = os.path.join(download_dir, f"{base_name}.{expected_ext}")

            if not os.path.exists(final_path):
                for candidate in os.listdir(download_dir):
                    if candidate.startswith(base_name):
                        final_path = os.path.join(download_dir, candidate)
                        break

            if not os.path.exists(final_path):
                raise Exception("Output audio file not found after processing.")

            # progress_hook is the only cancellation point yt-dlp gives us, and it
            # stops firing once the transfer ends. Tagging and lyrics have no hook
            # of their own, so they have to poll the flag themselves.
            if self._is_cancelled:
                raise Exception("Download cancelled by user.")

            self.progress_signal.emit(self.job_id, 98.0, "", "", "Embedding metadata & lyrics...")

            lyrics_data = None
            if self.config.get("embed_lyrics", True) or self.config.get("save_lrc_file", False):
                lyrics_data = LyricsFetcher.get_lyrics(
                    track_name=self.meta.get("title", ""),
                    artist_name=self.meta.get("artist", ""),
                    album_name=self.meta.get("album", ""),
                    duration=self.meta.get("duration", 0)
                )

            AudioTagger.tag_file(
                file_path=final_path,
                metadata=self.meta,
                lyrics_data=lyrics_data,
                save_lrc=self.config.get("save_lrc_file", False)
            )

            self.progress_signal.emit(self.job_id, 100.0, "", "", "Completed")
            self.finished_signal.emit(self.job_id, final_path, self.meta)

        except Exception as e:
            if self._is_cancelled:
                # Always report a terminal state. QueueManager releases the worker
                # slot from this signal, so staying silent strands the queue.
                self.error_signal.emit(self.job_id, "Download cancelled.")
            else:
                print(f"[DownloadWorker] Error on job {self.job_id}: {e}")
                self.error_signal.emit(self.job_id, str(e))
