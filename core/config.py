import os
import json
import shutil

# Settings live under the user's home, alongside the cover-art cache, rather
# than next to the source - writing into the source tree fails once the app is
# packaged, installed read-only, or run from somewhere else.
CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".grabsongs")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")
LEGACY_CONFIG_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.json")

def get_default_download_dir():
    return os.path.join(os.path.expanduser("~"), "Music", "GrabSongs")

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
    # Tokens: {artist}, {title}, {album}, {track}. The result is sanitised into a
    # single filename, so "/" becomes "_" - subfolder patterns are not supported.
    "naming_pattern": "{artist} - {title}",
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
        # An existing config next to the source is carried over once. The copy is
        # left in place rather than moved, so a failed write here cannot cost
        # the user their settings.
        if not os.path.exists(CONFIG_FILE) and os.path.exists(LEGACY_CONFIG_FILE):
            try:
                os.makedirs(CONFIG_DIR, exist_ok=True)
                shutil.copy2(LEGACY_CONFIG_FILE, CONFIG_FILE)
            except Exception as e:
                print(f"[Config] Could not migrate {LEGACY_CONFIG_FILE}: {e}")

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
            os.makedirs(CONFIG_DIR, exist_ok=True)
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            print(f"[Config] Error writing {CONFIG_FILE}: {e}")

    def get(self, key, default=None):
        return self.settings.get(key, default)

    def set(self, key, value):
        self.settings[key] = value
        self.save()
