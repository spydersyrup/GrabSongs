"""Tests for how the resolver handles input it cannot turn into a track.

The resolver falls back to a text search when a provider lookup returns nothing.
That fallback used to run for recognised provider links too, which meant a
failed Spotify scrape searched YouTube and Apple Music for the literal URL
string and then reported the track as not found.

Run with:  python -m unittest discover -s tests -t .
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.metadata import (
    AppleMusicMetadata, DeezerMetadata, GenericMetadata, MetadataResolver,
    SpotifyMetadata, YouTubeMetadata)


class _SearchRecorder:
    """Stands in for the provider search calls so a test can prove they were
    not made, and what they were called with."""

    def __init__(self):
        self.calls = []

    def install(self):
        for cls in (SpotifyMetadata, AppleMusicMetadata, DeezerMetadata, YouTubeMetadata):
            for name in ("search", "get_track", "get_album", "get_playlist"):
                if hasattr(cls, name):
                    self._patch(cls, name)
        self._patch(GenericMetadata, "resolve_url")

    def _patch(self, cls, name):
        def stub(query, *args, **kwargs):
            self.calls.append(f"{cls.__name__}.{name}({query!r})")
            return None if name.startswith("get_") else []
        setattr(cls, name, staticmethod(stub))

    def searched_for(self, needle):
        # Only the text-search fallback matters here; get_track/get_album and
        # resolve_url are the legitimate per-provider lookups and are expected
        # to receive the URL.
        return [c for c in self.calls if ".search(" in c and needle in c]


class ProviderLookupFailure(unittest.TestCase):
    """A provider link that resolves to nothing means the provider failed."""

    CASES = [
        ("https://open.spotify.com/track/4cOdK2wGLETKBW3PvgPWqT", "spotify"),
        ("https://music.apple.com/us/album/never-gonna-give-you-up/1234", "apple_music"),
        ("https://www.deezer.com/track/1234567", "deezer"),
        ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "youtube"),
    ]

    def setUp(self):
        self.recorder = _SearchRecorder()
        self.recorder.install()

    def test_reports_failure_instead_of_searching_the_url(self):
        for url, provider in self.CASES:
            with self.subTest(provider=provider):
                self.recorder.calls.clear()
                result = MetadataResolver.resolve(url)

                self.assertFalse(result["success"], f"{provider} should have failed")
                self.assertIn("error", result)
                self.assertFalse(
                    self.recorder.searched_for(url),
                    f"{provider}: the literal URL was passed to a search")

    def test_error_names_the_provider(self):
        result = MetadataResolver.resolve("https://open.spotify.com/track/4cOdK2wGLETKBW3PvgPWqT")
        self.assertIn("spotify", result["error"].lower())

    def test_apple_music_error_is_readable(self):
        result = MetadataResolver.resolve("https://music.apple.com/us/album/x/1234")
        self.assertIn("Apple Music", result["error"])
        self.assertNotIn("apple_music", result["error"])


class PlainSearchStillWorks(unittest.TestCase):
    """The fallback is only wrong for links; a real query must still search."""

    def setUp(self):
        self.recorder = _SearchRecorder()
        self.recorder.install()

    def test_text_query_is_searched(self):
        self.recorder.calls.clear()
        MetadataResolver.resolve("some song title")
        self.assertTrue(self.recorder.searched_for("some song title"))

    def test_empty_query_is_rejected(self):
        result = MetadataResolver.resolve("   ")
        self.assertFalse(result["success"])
        self.assertIn("error", result)


if __name__ == "__main__":
    unittest.main()