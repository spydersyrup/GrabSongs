"""Tests for the tag read that backs the library view.

read_tags() runs on the GUI thread for every file in the library, so it
memoises on (mtime, size). The cache is only correct if it invalidates when a
file really changes and does not grow entries for files that are not there.

Run with:  python -m unittest discover -s tests -t .
"""
import os
import shutil
import subprocess
import sys
import tempfile
import time
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtCore import QCoreApplication

QCoreApplication.instance() or QCoreApplication([])


def make_mp3(path, seconds=1):
    import imageio_ffmpeg
    subprocess.run(
        [imageio_ffmpeg.get_ffmpeg_exe(), "-loglevel", "quiet", "-f", "lavfi",
         "-i", f"sine=frequency=440:duration={seconds}", "-ac", "2", path, "-y"],
        check=True, capture_output=True)


class ReadTagsCache(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from mutagen.id3 import TIT2
        cls.TIT2 = TIT2

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        os.environ["HOME"] = self.tmp
        self.track = os.path.join(self.tmp, "track.mp3")
        make_mp3(self.track)
        from core.downloader import tagger
        self.tagger = tagger
        tagger._TAG_CACHE.clear()

    def tearDown(self):
        self.tagger._TAG_CACHE.clear()
        shutil.rmtree(self.tmp, ignore_errors=True)

    def retag(self, title):
        from mutagen.id3 import ID3
        tags = ID3(self.track)
        tags.add(self.TIT2(encoding=3, text=title))
        tags.save()

    def test_reads_the_written_title(self):
        self.retag("Original Title")
        self.assertEqual(self.tagger.AudioTagger.read_tags(self.track)["title"],
                         "Original Title")

    def test_second_read_is_served_from_cache(self):
        self.retag("Original Title")
        first = self.tagger.AudioTagger.read_tags(self.track)
        second = self.tagger.AudioTagger.read_tags(self.track)
        self.assertIs(first, second)

    def test_retagging_invalidates_the_entry(self):
        self.retag("Original Title")
        self.assertEqual(self.tagger.AudioTagger.read_tags(self.track)["title"],
                         "Original Title")
        time.sleep(0.02)
        self.retag("Edited Title")
        self.assertEqual(self.tagger.AudioTagger.read_tags(self.track)["title"],
                         "Edited Title")

    def test_missing_file_returns_empty(self):
        self.assertEqual(
            self.tagger.AudioTagger.read_tags(os.path.join(self.tmp, "nope.mp3")), {})

    def test_missing_file_is_not_cached(self):
        self.tagger.AudioTagger.read_tags(os.path.join(self.tmp, "nope.mp3"))
        self.assertEqual(self.tagger._TAG_CACHE, {})

    def test_unreadable_file_returns_empty_rather_than_raising(self):
        broken = os.path.join(self.tmp, "broken.mp3")
        with open(broken, "wb") as fh:
            fh.write(b"this is not audio")
        self.assertEqual(self.tagger.AudioTagger.read_tags(broken), {})


if __name__ == "__main__":
    unittest.main()