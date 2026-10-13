import os
import requests
import mutagen
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, APIC, USLT, COMM, TIT2, TPE1, TALB, TRCK, TPOS, TDRC, TCON
from mutagen.mp4 import MP4, MP4Cover
from mutagen.flac import FLAC, Picture
from mutagen.oggvorbis import OggVorbis
from typing import Dict, Any, Optional

class AudioTagger:
    @staticmethod
    def _download_image_bytes(url: str) -> Optional[bytes]:
        if not url:
            return None
        try:
            resp = requests.get(url, timeout=10)
            if resp.ok and len(resp.content) > 100:
                return resp.content
        except Exception as e:
            print(f"[Tagger] Error downloading cover art from {url}: {e}")
        return None

    @classmethod
    def tag_file(cls, file_path: str, metadata: Dict[str, Any], lyrics_data: Optional[Dict[str, Any]] = None, save_lrc: bool = False):
        if not os.path.exists(file_path):
            return False

        ext = os.path.splitext(file_path)[1].lower()
        title = metadata.get("title", "")
        artist = metadata.get("artist", "")
        album = metadata.get("album", "")
        track_num = metadata.get("track_number", 1)
        disc_num = metadata.get("disc_number", 1)
        release_date = str(metadata.get("release_date", ""))
        genre = metadata.get("genre", "")
        cover_url = metadata.get("cover_url", "")

        cover_bytes = cls._download_image_bytes(cover_url)

        # Handle .lrc file export if requested
        if save_lrc and lyrics_data and lyrics_data.get("synced"):
            lrc_path = os.path.splitext(file_path)[0] + ".lrc"
            try:
                with open(lrc_path, "w", encoding="utf-8") as f:
                    f.write(lyrics_data["synced"])
            except Exception as e:
                print(f"[Tagger] Failed to save .lrc file: {e}")

        # Plain or synced lyrics for embedding
        lyrics_text = ""
        if lyrics_data:
            lyrics_text = lyrics_data.get("plain") or lyrics_data.get("synced", "")

        try:
            if ext == ".mp3":
                cls._tag_mp3(file_path, title, artist, album, track_num, disc_num, release_date, genre, lyrics_text, cover_bytes)
            elif ext in (".m4a", ".mp4"):
                cls._tag_m4a(file_path, title, artist, album, track_num, disc_num, release_date, genre, lyrics_text, cover_bytes)
            elif ext == ".flac":
                cls._tag_flac(file_path, title, artist, album, track_num, disc_num, release_date, genre, lyrics_text, cover_bytes)
            return True
        except Exception as e:
            print(f"[Tagger] Error tagging {file_path}: {e}")
            return False

    @classmethod
    def _tag_mp3(cls, path: str, title: str, artist: str, album: str, track_num: int, disc_num: int, release_date: str, genre: str, lyrics: str, cover_bytes: Optional[bytes]):
        try:
            tags = ID3(path)
        except Exception:
            tags = ID3()

        tags.delall("TIT2")
        tags.add(TIT2(encoding=3, text=title))
        tags.delall("TPE1")
        tags.add(TPE1(encoding=3, text=artist))
        tags.delall("TALB")
        tags.add(TALB(encoding=3, text=album))
        tags.delall("TRCK")
        tags.add(TRCK(encoding=3, text=str(track_num)))
        tags.delall("TPOS")
        tags.add(TPOS(encoding=3, text=str(disc_num)))

        if release_date:
            tags.delall("TDRC")
            tags.add(TDRC(encoding=3, text=release_date[:4]))
        if genre:
            tags.delall("TCON")
            tags.add(TCON(encoding=3, text=genre))
        if lyrics:
            tags.delall("USLT")
            tags.add(USLT(encoding=3, lang="eng", desc="", text=lyrics))
        if cover_bytes:
            tags.delall("APIC")
            tags.add(APIC(
                encoding=3,
                mime="image/jpeg",
                type=3, # Cover (front)
                desc="Cover",
                data=cover_bytes
            ))
        tags.save(path, v2_version=3)

    @classmethod
    def _tag_m4a(cls, path: str, title: str, artist: str, album: str, track_num: int, disc_num: int, release_date: str, genre: str, lyrics: str, cover_bytes: Optional[bytes]):
        audio = MP4(path)
        audio["\xa9nam"] = title
        audio["\xa9ART"] = artist
        audio["\xa9alb"] = album
        audio["trkn"] = [(int(track_num), 0)]
        audio["disk"] = [(int(disc_num), 0)]
        if release_date:
            audio["\xa9day"] = release_date[:4]
        if genre:
            audio["\xa9gen"] = genre
        if lyrics:
            audio["\xa9lyr"] = lyrics
        if cover_bytes:
            image_format = MP4Cover.FORMAT_JPEG
            if cover_bytes.startswith(b"\x89PNG"):
                image_format = MP4Cover.FORMAT_PNG
            audio["covr"] = [MP4Cover(cover_bytes, imageformat=image_format)]
        audio.save()

    @classmethod
    def _tag_flac(cls, path: str, title: str, artist: str, album: str, track_num: int, disc_num: int, release_date: str, genre: str, lyrics: str, cover_bytes: Optional[bytes]):
        audio = FLAC(path)
        audio["title"] = title
        audio["artist"] = artist
        audio["album"] = album
        audio["tracknumber"] = str(track_num)
        audio["discnumber"] = str(disc_num)
        if release_date:
            audio["date"] = release_date[:4]
        if genre:
            audio["genre"] = genre
        if lyrics:
            audio["lyrics"] = lyrics
        if cover_bytes:
            pic = Picture()
            pic.type = 3
            pic.mime = "image/jpeg"
            pic.desc = "Cover"
            pic.data = cover_bytes
            audio.clear_pictures()
            audio.add_picture(pic)
        audio.save()

    @classmethod
    def read_tags(cls, file_path: str) -> Dict[str, Any]:
        if not os.path.exists(file_path):
            return {}
        try:
            f = mutagen.File(file_path, easy=True)
            if f is None:
                return {}
            title = f.get("title", [""])[0] if f.get("title") else ""
            artist = f.get("artist", [""])[0] if f.get("artist") else ""
            album = f.get("album", [""])[0] if f.get("album") else ""
            duration = int(f.info.length) if hasattr(f, "info") and f.info else 0
            return {
                "title": title,
                "artist": artist,
                "album": album,
                "duration": duration
            }
        except Exception:
            return {}
