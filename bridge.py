import os
import sys
import glob
from typing import Dict, Any, List
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot, pyqtProperty, QUrl, QThread
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtGui import QDesktopServices

from core.config import AppConfig
from core.metadata import MetadataResolver
from core.downloader.queue_manager import QueueManager
from core.downloader.tagger import AudioTagger


class SearchWorker(QThread):
    finished = pyqtSignal(list)
    failed = pyqtSignal(str)

    def __init__(self, query: str, service: str = "all"):
        super().__init__()
        self.query = query.strip()
        self.service = service

    def run(self):
        try:
            if not self.query:
                self.finished.emit([])
                return

            # Direct resolve if URL or general search
            result = MetadataResolver.resolve(self.query)
            if result.get("success"):
                tracks = result.get("tracks", [])
                # Tag downloaded status
                config = AppConfig.get_instance()
                dl_dir = config.get("download_dir", os.path.expanduser("~/Music/Harmonix"))
                for t in tracks:
                    # Check if matching file exists
                    expected_name = f"{t.get('artist', '')} - {t.get('title', '')}.mp3"
                    t["downloaded"] = os.path.exists(os.path.join(dl_dir, expected_name))
                self.finished.emit(tracks)
            else:
                self.failed.emit(result.get("error", "No tracks found matching your query."))
        except Exception as e:
            self.failed.emit(str(e))


class PlayerBridge(QObject):
    playingChanged = pyqtSignal(bool)
    currentTrackChanged = pyqtSignal()
    positionChanged = pyqtSignal(int)
    durationChanged = pyqtSignal(int)
    volumeChanged = pyqtSignal(float)
    errorChanged = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._player = QMediaPlayer(self)
        self._audio_output = QAudioOutput(self)
        self._player.setAudioOutput(self._audio_output)

        self._current_track = {}
        self._is_playing = False
        self._position = 0
        self._duration = 0
        self._volume = 0.85
        self._error = ""

        self._audio_output.setVolume(self._volume)

        self._player.playbackStateChanged.connect(self._on_playback_state_changed)
        self._player.positionChanged.connect(self._on_position_changed)
        self._player.durationChanged.connect(self._on_duration_changed)
        self._player.errorOccurred.connect(self._on_error_occurred)

    def _on_playback_state_changed(self, state):
        is_p = (state == QMediaPlayer.PlaybackState.PlayingState)
        if self._is_playing != is_p:
            self._is_playing = is_p
            self.playingChanged.emit(self._is_playing)

    def _on_position_changed(self, pos):
        self._position = pos
        self.positionChanged.emit(pos)

    def _on_duration_changed(self, dur):
        self._duration = dur
        self.durationChanged.emit(dur)

    def _on_error_occurred(self, error, error_string):
        self._error = error_string
        self.errorChanged.emit(error_string)

    @pyqtProperty(bool, notify=playingChanged)
    def isPlaying(self):
        return self._is_playing

    @pyqtProperty("QVariantMap", notify=currentTrackChanged)
    def currentTrack(self):
        return self._current_track

    @pyqtProperty(int, notify=positionChanged)
    def position(self):
        return self._position

    @pyqtProperty(int, notify=durationChanged)
    def duration(self):
        return self._duration

    @pyqtProperty(float, notify=volumeChanged)
    def volume(self):
        return self._volume

    @pyqtProperty(str, notify=errorChanged)
    def error(self):
        return self._error

    @pyqtSlot("QVariantMap")
    def playTrack(self, track_dict):
        self._current_track = dict(track_dict)
        self.currentTrackChanged.emit()

        file_path = self._current_track.get("filePath") or self._current_track.get("file_path")
        if file_path and os.path.exists(file_path):
            self._player.setSource(QUrl.fromLocalFile(file_path))
            self._player.play()
        else:
            # Check if preview URL is available
            preview = self._current_track.get("preview_url") or self._current_track.get("previewUrl")
            if preview:
                self._player.setSource(QUrl(preview))
                self._player.play()
            else:
                self._error = "No local file or preview audio available."
                self.errorChanged.emit(self._error)

    @pyqtSlot()
    def togglePlay(self):
        if self._is_playing:
            self._player.pause()
        else:
            self._player.play()

    @pyqtSlot()
    def play(self):
        self._player.play()

    @pyqtSlot()
    def pause(self):
        self._player.pause()

    @pyqtSlot()
    def stop(self):
        self._player.stop()

    @pyqtSlot(int)
    def seek(self, ms):
        self._player.setPosition(ms)

    @pyqtSlot(float)
    def setVolume(self, vol):
        self._volume = max(0.0, min(1.0, float(vol)))
        self._audio_output.setVolume(self._volume)
        self.volumeChanged.emit(self._volume)


class DownloaderBridge(QObject):
    searchStarted = pyqtSignal()
    searchResultsReady = pyqtSignal(list)
    searchFailed = pyqtSignal(str)

    queueUpdated = pyqtSignal(list)
    activeCountChanged = pyqtSignal(int)
    completedCountChanged = pyqtSignal(int)

    libraryUpdated = pyqtSignal(list)
    settingsChanged = pyqtSignal("QVariantMap")

    def __init__(self, player_bridge: PlayerBridge, parent=None):
        super().__init__(parent)
        self.player = player_bridge
        self.config = AppConfig.get_instance()
        self.queue_mgr = QueueManager(self)

        self._search_worker = None
        self._search_results = []
        self._is_searching = False

        self._jobs_list = []
        self._library_tracks = []

        # Connect queue manager signals
        self.queue_mgr.job_added.connect(self._on_job_added)
        self.queue_mgr.job_progress.connect(self._on_job_progress)
        self.queue_mgr.job_finished.connect(self._on_job_finished)
        self.queue_mgr.job_error.connect(self._on_job_error)

        self.refreshLibrary()

    def _on_job_added(self, job_id, meta):
        self._sync_jobs()

    def _on_job_progress(self, job_id, percent, speed, eta, status):
        self._sync_jobs()

    def _on_job_finished(self, job_id, file_path, meta):
        self._sync_jobs()
        self.refreshLibrary()
        # Update search results downloaded status
        for track in self._search_results:
            if track.get("id") == meta.get("id") or (track.get("title") == meta.get("title") and track.get("artist") == meta.get("artist")):
                track["downloaded"] = True
                track["filePath"] = file_path
        self.searchResultsReady.emit(self._search_results)

    def _on_job_error(self, job_id, error_msg):
        self._sync_jobs()

    def _sync_jobs(self):
        jobs = []
        active_count = 0
        completed_count = 0

        for j_id, j_data in self.queue_mgr.job_store.items():
            meta = j_data.get("meta", {})
            st = j_data.get("status", "Queued")
            if st in ("Queued", "Downloading", "Transcoding", "Tagging"):
                active_count += 1
            elif st == "Completed":
                completed_count += 1

            jobs.append({
                "id": j_id,
                "title": meta.get("title", "Unknown"),
                "artist": meta.get("artist", "Unknown"),
                "album": meta.get("album", ""),
                "service": meta.get("service", "spotify"),
                "artworkUrl": meta.get("artwork_url", ""),
                "status": st,
                "percent": float(j_data.get("percent", 0.0)),
                "speed": j_data.get("speed", ""),
                "eta": j_data.get("eta", ""),
                "filePath": j_data.get("file_path", ""),
                "error": j_data.get("error", "")
            })

        self._jobs_list = list(reversed(jobs))
        self.queueUpdated.emit(self._jobs_list)
        self.activeCountChanged.emit(active_count)
        self.completedCountChanged.emit(completed_count)

    @pyqtSlot(str, str)
    def search(self, query: str, service: str = "all"):
        if not query.strip():
            return

        self._is_searching = True
        self.searchStarted.emit()

        self._search_worker = SearchWorker(query, service)
        self._search_worker.finished.connect(self._on_search_finished)
        self._search_worker.failed.connect(self._on_search_failed)
        self._search_worker.start()

    def _on_search_finished(self, results):
        self._is_searching = False
        # Normalize fields for QML components
        for r in results:
            if "cover_url" in r and "artworkUrl" not in r:
                r["artworkUrl"] = r["cover_url"]
            if "artwork_url" in r and "artworkUrl" not in r:
                r["artworkUrl"] = r["artwork_url"]
            if "duration_formatted" in r and "duration" not in r:
                r["duration"] = r["duration_formatted"]
        self._search_results = results
        self.searchResultsReady.emit(results)

    def _on_search_failed(self, error):
        self._is_searching = False
        self.searchFailed.emit(error)

    @pyqtSlot("QVariantMap")
    def downloadTrack(self, track_dict):
        t = dict(track_dict)
        self.queue_mgr.add_tracks([t])

    @pyqtSlot("QVariantList")
    def downloadAll(self, tracks_list):
        tracks = [dict(t) for t in tracks_list]
        self.queue_mgr.add_tracks(tracks)

    @pyqtSlot(str)
    def cancelJob(self, job_id):
        self.queue_mgr.cancel_job(job_id)

    @pyqtSlot()
    def cancelAll(self):
        self.queue_mgr.cancel_all()

    @pyqtSlot(str)
    def openFolder(self, path: str = ""):
        if not path:
            path = self.config.get("download_dir", os.path.expanduser("~/Music/Harmonix"))
        os.makedirs(path, exist_ok=True)
        QDesktopServices.openUrl(QUrl.fromLocalFile(path))

    @pyqtSlot()
    def refreshLibrary(self):
        dl_dir = self.config.get("download_dir", os.path.expanduser("~/Music/Harmonix"))
        os.makedirs(dl_dir, exist_ok=True)

        tracks = []
        audio_files = []
        for ext in ("*.mp3", "*.flac", "*.m4a", "*.aac", "*.opus"):
            audio_files.extend(glob.glob(os.path.join(dl_dir, ext)))

        audio_files.sort(key=os.path.getmtime, reverse=True)

        for fpath in audio_files:
            fname = os.path.basename(fpath)
            meta = AudioTagger.read_tags(fpath)

            title = meta.get("title") or os.path.splitext(fname)[0]
            artist = meta.get("artist") or "Harmonix"
            album = meta.get("album") or "Downloads"
            duration = meta.get("duration", 0)

            # Check if synced LRC file exists
            lrc_path = os.path.splitext(fpath)[0] + ".lrc"
            has_lrc = os.path.exists(lrc_path)

            cover_p = meta.get("cover_path") or ""
            if cover_p and not cover_p.startswith("file:"):
                cover_p = QUrl.fromLocalFile(os.path.abspath(cover_p)).toString()

            tracks.append({
                "filePath": fpath,
                "fileName": fname,
                "title": title,
                "artist": artist,
                "album": album,
                "duration": f"{int(duration // 60)}:{int(duration % 60):02d}" if duration else "--:--",
                "format": os.path.splitext(fpath)[1].replace(".", "").upper(),
                "artworkUrl": cover_p,
                "hasLyrics": has_lrc,
                "downloaded": True
            })

        self._library_tracks = tracks
        self.libraryUpdated.emit(tracks)

    @pyqtSlot("QVariantMap")
    def saveSettings(self, s_dict):
        for k, v in s_dict.items():
            self.config.set(k, v)
        self.config.save()
        self.settingsChanged.emit(self.getSettings())

    @pyqtSlot(result="QVariantMap")
    def getSettings(self):
        return {
            "download_dir": self.config.get("download_dir", os.path.expanduser("~/Music/Harmonix")),
            "preferred_format": self.config.get("preferred_format", "mp3"),
            "embed_lyrics": self.config.get("embed_lyrics", True),
            "embed_artwork": self.config.get("embed_artwork", True),
            "max_concurrent": int(self.config.get("max_concurrent_downloads", 2))
        }
