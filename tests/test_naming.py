"""Tests for how a track maps to a filename, and whether that agrees with the
worker. Both bugs here shipped because two places each guessed the same path.

Run with:  python -m unittest discover -s tests -t .
"""
import os
import shutil
import sys
import tempfile
import time
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.downloader.worker import build_base_name, sanitize_filename


class SanitizeFilename(unittest.TestCase):
    def test_replaces_characters_illegal_in_filenames(self):
        for bad in '<>:"/\\|?*':
            self.assertNotIn(bad, sanitize_filename(f"a{bad}b"))

    def test_strips_surrounding_whitespace(self):
        self.assertEqual(sanitize_filename("  a b  "), "a b")

    def test_leaves_legal_characters_alone(self):
        self.assertEqual(sanitize_filename("AC/DC - T?"), "AC_DC - T_")


class BuildBaseName(unittest.TestCase):
    DEFAULT = {"naming_pattern": "{artist} - {title}"}
    TRACK = {
        "artist": "Pink Floyd",
        "title": "Time",
        "album": "The Dark Side of the Moon",
        "track_number": 3,
    }

    def name_for(self, pattern, track=None):
        return build_base_name(track or self.TRACK, {"naming_pattern": pattern})

    def test_default_pattern(self):
        self.assertEqual(self.name_for("{artist} - {title}"), "Pink Floyd - Time")

    def test_track_token_is_zero_padded(self):
        self.assertEqual(self.name_for("{track:02d} - {title}"), "03 - Time")

    def test_album_token(self):
        self.assertEqual(self.name_for("{album}/{title}"), "The Dark Side of the Moon_Time")

    def test_unknown_token_falls_back_to_artist_title(self):
        # A malformed pattern is user input, not a crash.
        self.assertEqual(self.name_for("{nope}"), "Pink Floyd - Time")

    def test_result_is_sanitised(self):
        self.assertEqual(self.name_for("{artist}"), "Pink Floyd")

    def test_slash_becomes_underscore_not_a_subdirectory(self):
        # sanitize_filename turns "/" into "_" because it is illegal in a
        # filename. config.py used to advertise subfolder patterns that could
        # never work; this pins the behaviour that actually happens.
        self.assertEqual(self.name_for("{artist}/{title}"), "Pink Floyd_Time")

    def test_missing_fields_get_placeholders(self):
        self.assertEqual(build_base_name({}, self.DEFAULT), "Unknown Artist - Unknown Track")

    def test_non_numeric_track_token_falls_back(self):
        track = dict(self.TRACK, track_number="not-a-number")
        self.assertEqual(build_base_name(track, self.DEFAULT), "Pink Floyd - Time")


class DuplicateDetection(unittest.TestCase):
    """The bridge flags a track as downloaded by looking for the file the
    worker would have written. These cover the change that broke whenever
    naming_pattern or audio_format was anything but the default."""

    @classmethod
    def setUpClass(cls):
        from PyQt6.QtCore import QCoreApplication
        cls.app = QCoreApplication.instance() or QCoreApplication([])

    def setUp(self):
        import bridge as bridge_module
        from core.config import AppConfig
        self.bridge_module = bridge_module
        # A fresh directory per test: these tests assert that a file which does
        # not match the current settings is *not* counted, so a file left behind
        # by an earlier test would mask a real failure.
        self.tmp = tempfile.mkdtemp()
        os.environ["HOME"] = self.tmp
        self.config = AppConfig.get_instance()
        self.config.settings["download_dir"] = self.tmp
        self.track = {"title": "Time", "artist": "Pink Floyd", "service": "x"}
        self._real_resolve = bridge_module.MetadataResolver.resolve
        bridge_module.MetadataResolver.resolve = staticmethod(self._resolve)

    def tearDown(self):
        self.bridge_module.MetadataResolver.resolve = self._real_resolve
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _resolve(self, query, service="all"):
        return {"success": True, "tracks": [dict(self.track)]}

    def _download_flag(self):
        from PyQt6.QtCore import QTimer
        from bridge import DownloaderBridge
        bridge = DownloaderBridge()
        flags = []
        bridge.searchFinished.connect(lambda t: flags.append(t[0]["downloaded"]))
        bridge.search("x", "all")
        deadline = time.time() + 5
        while time.time() < deadline and not flags:
            self.app.processEvents()
            time.sleep(0.01)
        self.app.processEvents()
        return flags[0] if flags else None

    def write(self, filename):
        with open(os.path.join(self.tmp, filename), "wb") as fh:
            fh.write(b"x")

    def test_absent_file_is_not_downloaded(self):
        self.config.settings["audio_format"] = "mp3"
        self.config.settings["naming_pattern"] = "{artist} - {title}"
        self.assertIs(self._download_flag(), False)

    def test_matching_filename_is_downloaded(self):
        self.config.settings["audio_format"] = "mp3"
        self.config.settings["naming_pattern"] = "{artist} - {title}"
        self.write("Pink Floyd - Time.mp3")
        self.assertIs(self._download_flag(), True)

    def test_follows_the_output_format(self):
        self.config.settings["audio_format"] = "flac"
        self.config.settings["naming_pattern"] = "{artist} - {title}"
        self.write("Pink Floyd - Time.flac")
        self.assertIs(self._download_flag(), True)

    def test_ignores_a_file_in_the_old_format(self):
        self.config.settings["audio_format"] = "flac"
        self.config.settings["naming_pattern"] = "{artist} - {title}"
        self.write("Pink Floyd - Time.mp3")
        self.assertIs(self._download_flag(), False)

    def test_follows_the_naming_pattern(self):
        self.config.settings["audio_format"] = "mp3"
        self.config.settings["naming_pattern"] = "{track:02d} {artist}"
        self.track["track_number"] = 3
        self.write("03 Pink Floyd.mp3")
        self.assertIs(self._download_flag(), True)

    def test_ignores_a_file_matching_the_old_pattern(self):
        self.config.settings["audio_format"] = "mp3"
        self.config.settings["naming_pattern"] = "{track:02d} {artist}"
        self.track["track_number"] = 3
        self.write("Pink Floyd - Time.mp3")
        self.assertIs(self._download_flag(), False)


if __name__ == "__main__":
    unittest.main()