import os
import json
import shutil
import pathlib

CONFIG_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.json")

def get_default_download_dir():
    music_dir = os.path.join(os.path.expanduser("~"), "Music")
    if os.path.exists(music_dir):
        return os.path.join(music_dir, "GrabSongs")
    return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "downloads")

def detect_ffmpeg_path():
    # 1. Check system PATH
    sys_ffmpeg = shutil.which("ffmpeg")
    if sys_ffmpeg:
        return sys_ffmpeg
    # 2. Check imageio_ffmpeg bundled binary
    try:
        import imageio_ffmpeg
        bundled = imageio_ffmpeg.get_ffmpeg_exe()
        if bundled and os.path.exists(bundled):
            return bundled
    except ImportError:
        pass
    return ""

DEFAULT_CONFIG = {
    "download_dir": get_default_download_dir(),
    "audio_format": "mp3",          # mp3, m4a, flac, opus
    "audio_quality": "320",         # 320, 256, 192, lossless
    "embed_artwork": True,
    "embed_lyrics": True,
    "save_lrc_file": False,
    "naming_pattern": "{artist} - {title}",  # e.g., "{artist}/{album}/{track:02d} - {title}"
    "max_concurrent_downloads": 2,
    "ffmpeg_path": detect_ffmpeg_path(),
    "theme": "dark",
}

class AppConfig:
    _instance = None

    def __init__(self):
        self.settings = dict(DEFAULT_CONFIG)
        self.load()

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = AppConfig()
        return cls._instance

    def load(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    saved = json.load(f)
                    self.settings.update(saved)
            except Exception as e:
                print(f"[Config] Error reading {CONFIG_FILE}: {e}")
        # Always verify ffmpeg path if empty
        if not self.settings.get("ffmpeg_path"):
            self.settings["ffmpeg_path"] = detect_ffmpeg_path()
        # Ensure download dir exists
        try:
            os.makedirs(self.settings["download_dir"], exist_ok=True)
        except Exception:
            pass

    def save(self):
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            print(f"[Config] Error writing {CONFIG_FILE}: {e}")

    def get(self, key, default=None):
        return self.settings.get(key, default)

    def set(self, key, value):
        self.settings[key] = value
        self.save()
