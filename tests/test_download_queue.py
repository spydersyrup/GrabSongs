"""Tests for cancelling a download without corrupting the file.

The worker used to be killed with QThread.terminate(), which left half-written
audio on disk and an orphaned ffmpeg process. Cancellation is cooperative now:
the worker stops at a cancellation point and reports back, and QueueManager
releases the slot when it unwinds.

Run with:  python -m unittest discover -s tests -t .
"""
import os
import sys
import tempfile
import time
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtCore import QCoreApplication, QThread

import yt_dlp

from core.config import AppConfig
from core.downloader.queue_manager import QueueManager

APP = QCoreApplication.instance() or QCoreApplication([])


def pump(seconds):
    """Drive the event loop the way app.exec() would."""
    deadline = time.time() + seconds
    while time.time() < deadline:
        APP.processEvents()
        time.sleep(0.005)


class _FakeYDL:
    """Stands in for yt-dlp: a slow search, then progress hooks forever."""

    def __init__(self, opts):
        self.opts = opts

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def extract_info(self, url, download=False):
        if url.startswith("ytsearch"):
            time.sleep(0.4)
            return {"entries": [{"title": "Artist - Song", "uploader": "Artist - Topic",
                                 "duration": 200, "webpage_url": "https://example/song"}]}
        hook = self.opts["progress_hooks"][0]
        for step in range(400):
            time.sleep(0.02)
            hook({"status": "downloading", "total_bytes": 1000,
                  "downloaded_bytes": step * 2, "speed": 50000, "eta": 8})
        return {"id": "x"}


class _ExplodingYDL:
    def __init__(self, opts):
        self.opts = opts

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def extract_info(self, url, download=False):
        raise RuntimeError("HTTP 403 Forbidden")


class QueueTestCase(unittest.TestCase):
    def setUp(self):
        self.real_ydl = yt_dlp.YoutubeDL
        self.terminated = []
        real_terminate = QThread.terminate

        def spy_terminate(self_):
            self.terminated.append(self_)
            real_terminate(self_)

        self.real_terminate = QThread.terminate
        QThread.terminate = spy_terminate

        self.tmp = tempfile.mkdtemp()
        self.config = AppConfig.get_instance()
        self.config.settings["download_dir"] = self.tmp
        self.config.settings["max_concurrent_downloads"] = 1
        self.config.settings["embed_lyrics"] = False

    def tearDown(self):
        yt_dlp.YoutubeDL = self.real_ydl
        QThread.terminate = self.real_terminate

    def add(self, manager, title="Song", artist="Artist"):
        return manager.add_tracks([{"title": title, "artist": artist,
                                    "album": "Album", "service": "youtube"}])[0]

    def wait_for(self, predicate, seconds=8):
        deadline = time.time() + seconds
        while time.time() < deadline and not predicate():
            pump(0.05)
        return predicate()


class CancelsCooperatively(QueueTestCase):
    def setUp(self):
        super().setUp()
        yt_dlp.YoutubeDL = _FakeYDL
        self.manager = QueueManager()
        self.errors = []
        self.manager.job_error.connect(lambda jid, msg: self.errors.append((jid, msg)))

    def test_never_calls_terminate(self):
        job = self.add(self.manager)
        self.wait_for(lambda: self.manager.job_store[job]["status"] == "Downloading...")
        self.manager.cancel_job(job)
        self.wait_for(lambda: not self.manager.active_workers)
        self.assertEqual(self.terminated, [])

    def test_job_stays_cancelled(self):
        # Progress already queued when the user cancelled used to drain
        # afterwards and flip the status back to Failed.
        job = self.add(self.manager)
        self.wait_for(lambda: self.manager.job_store[job]["status"] == "Downloading...")
        self.manager.cancel_job(job)
        self.wait_for(lambda: not self.manager.active_workers)
        self.assertEqual(self.manager.job_store[job]["status"], "Cancelled")

    def test_notifies_exactly_once(self):
        job = self.add(self.manager)
        self.wait_for(lambda: self.manager.job_store[job]["status"] == "Downloading...")
        self.manager.cancel_job(job)
        self.wait_for(lambda: not self.manager.active_workers)
        pump(0.3)
        self.assertEqual(len(self.errors), 1)

    def test_releases_the_slot(self):
        job = self.add(self.manager)
        self.wait_for(lambda: self.manager.job_store[job]["status"] == "Downloading...")
        self.manager.cancel_job(job)
        self.assertEqual(len(self.manager.active_workers), 1,
                         "slot must stay held until the worker unwinds")
        self.assertTrue(self.wait_for(lambda: not self.manager.active_workers))

    def test_queue_advances(self):
        first = self.add(self.manager, "One")
        second = self.add(self.manager, "Two")
        self.wait_for(lambda: self.manager.job_store[first]["status"] == "Downloading...")
        self.assertEqual(self.manager.job_store[second]["status"], "Queued")
        self.manager.cancel_job(first)
        self.wait_for(lambda: self.manager.job_store[second]["status"] == "Downloading...")
        self.manager.cancel_job(second)
        self.wait_for(lambda: not self.manager.active_workers)
        self.assertEqual(self.manager.job_store[first]["status"], "Cancelled")

    def test_cancelling_a_queued_job_never_starts_it(self):
        running = self.add(self.manager, "One")
        queued = self.add(self.manager, "Two")
        self.wait_for(lambda: self.manager.job_store[running]["status"] == "Downloading...")
        self.manager.cancel_job(queued)
        self.assertEqual(self.manager.job_store[queued]["status"], "Cancelled")
        self.assertNotIn(queued, self.manager.active_workers)
        self.manager.cancel_job(running)
        pump(0.3)
        self.assertNotIn(queued, self.manager.active_workers)

    def test_cancelling_an_unknown_job_is_harmless(self):
        self.manager.cancel_job("job_doesnotexist")
        pump(0.1)


class ReportsGenuineFailures(QueueTestCase):
    def setUp(self):
        super().setUp()
        self.manager = QueueManager()
        self.errors = []
        self.manager.job_error.connect(lambda jid, msg: self.errors.append((jid, msg)))

    def test_failure_is_reported_with_its_message(self):
        yt_dlp.YoutubeDL = _ExplodingYDL
        job = self.add(self.manager)
        self.wait_for(lambda: self.manager.job_store[job]["status"] == "Failed")
        self.assertEqual(len(self.errors), 1)
        self.assertIn("403", self.errors[0][1])

    def test_failure_releases_the_slot(self):
        yt_dlp.YoutubeDL = _ExplodingYDL
        job = self.add(self.manager)
        self.wait_for(lambda: not self.manager.active_workers)
        self.assertEqual(self.manager.job_store[job]["status"], "Failed")


class CancelsWithoutEndingTheRun(QueueTestCase):
    """Regression for a cancelled worker that reported nothing at all: the
    queue kept its slot forever and never started the next download."""

    def setUp(self):
        super().setUp()
        yt_dlp.YoutubeDL = _FakeYDL

    def test_queue_drains_completely(self):
        manager = QueueManager()
        jobs = [self.add(manager, f"Track {i}") for i in range(3)]
        for job in jobs:
            self.wait_for(
                lambda j=job: manager.job_store[j]["status"] == "Downloading...", 5)
            manager.cancel_job(job)
            self.wait_for(lambda: not manager.active_workers, 8)
        pump(0.3)
        self.assertEqual(manager.active_workers, {})
        for job in jobs:
            self.assertEqual(manager.job_store[job]["status"], "Cancelled")


if __name__ == "__main__":
    unittest.main()