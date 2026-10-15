"""Tests for where settings are stored and that existing settings survive.

config.json used to be written next to the source, which fails once the app is
packaged or installed somewhere read-only. It now lives under the user's home,
and an older file next to the source is carried over once.

Run with:  python -m unittest discover -s tests -t .
"""
import json
import os
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtCore import QCoreApplication

QCoreApplication.instance() or QCoreApplication([])

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class ConfigLocation(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        os.environ["HOME"] = self.tmp
        self.config_dir = os.path.join(self.tmp, ".grabsongs")
        self.config_file = os.path.join(self.config_dir, "config.json")

        import core.config as config_module
        self.module = config_module
        self._real_dir = config_module.CONFIG_DIR
        self._real_file = config_module.CONFIG_FILE
        config_module.CONFIG_DIR = self.config_dir
        config_module.CONFIG_FILE = self.config_file
        config_module.LEGACY_CONFIG_FILE = os.path.join(REPO_ROOT, "config.json")
        config_module.AppConfig._instance = None

    def tearDown(self):
        self.module.AppConfig._instance = None
        self.module.CONFIG_DIR = self._real_dir
        self.module.CONFIG_FILE = self._real_file
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_writes_under_the_home_directory(self):
        config = self.module.AppConfig.get_instance()
        config.set("audio_format", "flac")
        self.assertTrue(os.path.exists(self.config_file),
                        "settings must not be written into the source tree")

    def test_round_trips(self):
        config = self.module.AppConfig.get_instance()
        config.set("audio_format", "opus")
        self.module.AppConfig._instance = None
        self.assertEqual(self.module.AppConfig.get_instance().get("audio_format"), "opus")

    def test_carries_over_a_legacy_file(self):
        legacy = os.path.join(REPO_ROOT, "config.json")
        self._skip_if_real_config(legacy)
        with open(legacy, "w", encoding="utf-8") as fh:
            json.dump({"audio_format": "m4a"}, fh)
        try:
            config = self.module.AppConfig.get_instance()
            self.assertEqual(config.get("audio_format"), "m4a")
            self.assertTrue(os.path.exists(self.config_file),
                            "legacy settings should have been carried over")
        finally:
            os.remove(legacy)

    def test_prefers_the_new_location(self):
        os.makedirs(self.config_dir, exist_ok=True)
        with open(self.config_file, "w", encoding="utf-8") as fh:
            json.dump({"audio_format": "flac"}, fh)
        legacy = os.path.join(REPO_ROOT, "config.json")
        self._skip_if_real_config(legacy)
        with open(legacy, "w", encoding="utf-8") as fh:
            json.dump({"audio_format": "m4a"}, fh)
        try:
            config = self.module.AppConfig.get_instance()
            self.assertEqual(config.get("audio_format"), "flac")
        finally:
            os.remove(legacy)

    def test_legacy_file_is_left_in_place(self):
        legacy = os.path.join(REPO_ROOT, "config.json")
        self._skip_if_real_config(legacy)
        with open(legacy, "w", encoding="utf-8") as fh:
            json.dump({"audio_format": "m4a"}, fh)
        try:
            self.module.AppConfig.get_instance()
            self.assertTrue(os.path.exists(legacy),
                            "the old file is copied, not moved, so a failed write costs nothing")
        finally:
            os.remove(legacy)

    def test_malformed_config_does_not_stop_startup(self):
        os.makedirs(self.config_dir, exist_ok=True)
        with open(self.config_file, "w", encoding="utf-8") as fh:
            fh.write("{not json")
        config = self.module.AppConfig.get_instance()
        self.assertEqual(config.get("audio_format"), "mp3", "defaults should still apply")

    def test_default_download_dir_follows_home(self):
        # DEFAULT_CONFIG is built at import time, so this checks the function
        # rather than the already-captured default.
        self.assertTrue(self.module.get_default_download_dir().startswith(self.tmp))

    def test_default_download_dir_is_never_inside_the_source(self):
        # It used to fall back to <repo>/downloads when ~/Music was missing,
        # which is unwritable once the app is packaged.
        self.assertNotIn(REPO_ROOT, self.module.get_default_download_dir())

    def test_loaded_config_does_not_point_into_the_source(self):
        config = self.module.AppConfig.get_instance()
        self.assertNotIn(REPO_ROOT, config.get("download_dir"))

    def _skip_if_real_config(self, path):
        if os.path.exists(path):
            self.skipTest(f"a real {path} exists; refusing to overwrite it")


if __name__ == "__main__":
    unittest.main()