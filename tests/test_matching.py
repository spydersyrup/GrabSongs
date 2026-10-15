"""Tests for choosing which YouTube result is the actual song.

find_best_audio_match filters out live cuts, remixes, covers and karaoke. It
once fell through to entries[0] when every result was filtered, handing back
exactly what it had just rejected.

Run with:  python -m unittest discover -s tests -t .
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.downloader.worker import find_best_audio_match


class _FakeYDL:
    def __init__(self, entries):
        self._entries = entries

    def extract_info(self, url, download=False):
        return {"entries": self._entries}


def entry(title, uploader="Some Channel", duration=200, url="https://example/x"):
    return {"title": title, "uploader": uploader, "duration": duration,
            "webpage_url": url}


class RejectsUnwantedVersions(unittest.TestCase):
    def assertRejected(self, entry_obj):
        self.assertIsNone(find_best_audio_match(_FakeYDL([entry_obj]), "Song", "Artist", 200))

    def test_live_cut_is_rejected(self):
        self.assertRejected(entry("Artist - Song (Live at Wembley)"))

    def test_concert_is_rejected(self):
        self.assertRejected(entry("Artist - Song (Concert)"))

    def test_remix_is_rejected_when_target_is_not_a_remix(self):
        self.assertRejected(entry("Artist - Song (Remix)"))

    def test_mashup_is_rejected(self):
        self.assertRejected(entry("Artist - Song Mashup"))

    def test_cover_is_rejected(self):
        self.assertRejected(entry("Artist - Song (Cover)"))

    def test_karaoke_is_rejected(self):
        self.assertRejected(entry("Artist - Song (Karaoke Version)"))

    def test_instrumental_is_rejected(self):
        self.assertRejected(entry("Artist - Song (Instrumental)"))

    def test_live_cut_is_allowed_when_the_target_is_a_live_cut(self):
        found = find_best_audio_match(
            _FakeYDL([entry("Artist - Song (Live)")]), "Song (Live)", "Artist", 200)
        self.assertEqual(found, "https://example/x")


class NoRejectedFallback(unittest.TestCase):
    """The regression: when everything is filtered, the function returned
    entries[0] anyway, so a studio track got a live or karaoke version."""

    def test_all_rejected_returns_none(self):
        entries = [
            entry("Artist - Song (Live at Wembley)", url="https://example/LIVE"),
            entry("Artist - Song (Karaoke Version)", url="https://example/KARAOKE"),
        ]
        self.assertIsNone(find_best_audio_match(_FakeYDL(entries), "Song", "Artist", 200))

    def test_empty_results_return_none(self):
        self.assertIsNone(find_best_audio_match(_FakeYDL([]), "Song", "Artist", 200))

    def test_one_surviving_result_is_returned(self):
        entries = [
            entry("Artist - Song (Live)", url="https://example/LIVE"),
            entry("Artist - Song", uploader="Artist - Topic", url="https://example/GOOD"),
        ]
        self.assertEqual(
            find_best_audio_match(_FakeYDL(entries), "Song", "Artist", 200),
            "https://example/GOOD")

    def test_extract_failure_returns_none(self):
        class Broken:
            def extract_info(self, url, download=False):
                raise RuntimeError("network down")
        self.assertIsNone(find_best_audio_match(Broken(), "Song", "Artist", 200))


class PrefersTheLikelierMatch(unittest.TestCase):
    def pick(self, entries, title="Song", duration=200):
        return find_best_audio_match(_FakeYDL(entries), title, "Artist", duration)

    def test_topic_channel_wins(self):
        found = self.pick([
            entry("Artist - Song", uploader="Random Channel", url="https://example/RANDOM"),
            entry("Artist - Song", uploader="Artist - Topic", url="https://example/TOPIC"),
        ])
        self.assertEqual(found, "https://example/TOPIC")

    def test_duration_match_wins_over_mismatch(self):
        found = self.pick([
            entry("Artist - Song", duration=400, url="https://example/LONG"),
            entry("Artist - Song", duration=201, url="https://example/CLOSE"),
        ])
        self.assertEqual(found, "https://example/CLOSE")

    def test_falls_back_to_webpage_url_then_id(self):
        bare = {"title": "Artist - Song", "uploader": "Artist - Topic",
                "duration": 200, "id": "abc123"}
        found = find_best_audio_match(_FakeYDL([bare]), "Song", "Artist", 200)
        self.assertEqual(found, "https://www.youtube.com/watch?v=abc123")

    def test_empty_result_is_empty_list_not_an_error(self):
        self.assertIsNone(find_best_audio_match(_FakeYDL([None, None]), "Song", "Artist", 200))


if __name__ == "__main__":
    unittest.main()