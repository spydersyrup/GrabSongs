"""Tests for the tag memo in read_tags.

read_tags() is called for every file in the library on the GUI thread, so an
unparseable file that never reaches the cache is re-opened on every single
call. That is what these tests pin down.

Run with:  python -m unittest discover -s tests -t .
"""
import os
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import mutagen

from core.downloader import tagger
from core.downloader.tagger import AudioTagger


class TagCache(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.calls = 0
        self._real_file = mutagen.File

        def counting(path, *a, **kw):
            self.calls += 1
            return self._real_file(path, *a, **kw)

        mutagen.File = counting
        tagger._TAG_CACHE.clear()
        self.addCleanup(self.restore)
        self.addCleanup(shutil.rmtree, self.tmp, True)

    def restore(self):
        mutagen.File = self._real_file
        tagger._TAG_CACHE.clear()

    def path(self, name="t.mp3"):
        full = os.path.join(self.tmp, name)
        with open(full, "wb") as fh:
            fh.write(b"\xff\xfb\x90d" + b"\x00" * 2000)
        return full

    # ---- the bug ----

    def test_unparseable_file_is_not_reopened(self):
        p = self.path()
        self.assertEqual(AudioTagger.read_tags(p), {})
        first = self.calls
        AudioTagger.read_tags(p)
        AudioTagger.read_tags(p)
        self.assertEqual(self.calls, first, "unparseable file was reopened")

    def test_editing_an_unparseable_file_is_picked_up(self):
        # Caching the failure must not turn into caching a stale failure.
        p = self.path()
        AudioTagger.read_tags(p)
        tagger._TAG_CACHE.clear()
        before = self.calls
        AudioTagger.read_tags(p)
        self.assertEqual(self.calls, before + 1, "clear() must force a reparse")

    def test_touching_a_file_invalidates_the_cached_failure(self):
        p = self.path()
        AudioTagger.read_tags(p)
        before = self.calls
        os.utime(p, (0, 0))
        AudioTagger.read_tags(p)
        self.assertEqual(self.calls, before + 1, "mtime change must invalidate")

    # ---- the existing behaviour this must not break ----

    def test_missing_file_returns_empty(self):
        self.assertEqual(AudioTagger.read_tags(os.path.join(self.tmp, "nope.mp3")), {})

    def test_directory_path_returns_empty(self):
        self.assertEqual(AudioTagger.read_tags(self.tmp), {})


if __name__ == "__main__":
    unittest.main()