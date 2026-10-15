"""Tests for the queue surviving an app restart.

The queue used to live only in memory, so closing the app mid-batch threw away
every pending and in-flight download.

These run with max_concurrent_downloads at 0 so no worker thread is ever
started. The point being tested is what lands on disk, not how a download
behaves, and a test that spins up a real yt-dlp to check a JSON file is a test
that will one day download a song.

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


class QueuePersistence(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        os.environ["HOME"] = self.tmp
        self.queue_file = os.path.join(self.tmp, "queue.json")

        import core.downloader.queue_manager as qm_module
        from core.config import AppConfig

        self.module = qm_module
        self._real_file = qm_module.QUEUE_FILE
        qm_module.QUEUE_FILE = self.queue_file

        cfg = AppConfig.get_instance()
        cfg.settings["download_dir"] = os.path.join(self.tmp, "dl")
        cfg.settings["max_concurrent_downloads"] = 0

    def tearDown(self):
        self.module.QUEUE_FILE = self._real_file
        shutil.rmtree(self.tmp, ignore_errors=True)

    def manager(self, restore=False):
        return self.module.QueueManager(restore=restore)

    def stored(self):
        with open(self.queue_file, encoding="utf-8") as fh:
            return json.load(fh)

    def write(self, payload):
        with open(self.queue_file, "w", encoding="utf-8") as fh:
            json.dump(payload, fh)

    # ---- what gets written ----

    def test_queued_tracks_are_written_to_disk(self):
        m = self.manager()
        m.add_tracks([{"title": "One", "artist": "A"},
                      {"title": "Two", "artist": "B"}])
        self.assertEqual([t["title"] for t in self.stored()], ["One", "Two"])

    def test_an_in_flight_track_is_still_persisted(self):
        # A download that was running when the app died is not terminal, so it
        # must come back. Driving the status directly avoids starting a thread.
        m = self.manager()
        ids = m.add_tracks([{"title": "One", "artist": "A"}])
        m.job_store[ids[0]]["status"] = "Downloading..."
        m._persist()
        self.assertEqual([t["title"] for t in self.stored()], ["One"])

    def test_cancelling_removes_it_from_disk(self):
        m = self.manager()
        ids = m.add_tracks([{"title": "One", "artist": "A"},
                            {"title": "Two", "artist": "B"}])
        m.cancel_job(ids[1])
        self.assertEqual([t["title"] for t in self.stored()], ["One"])

    def test_cancelling_everything_empties_the_file(self):
        m = self.manager()
        ids = m.add_tracks([{"title": "One", "artist": "A"},
                            {"title": "Two", "artist": "B"}])
        for job_id in ids:
            m.cancel_job(job_id)
        self.assertEqual(self.stored(), [])

    def test_finished_jobs_leave_the_file(self):
        m = self.manager()
        ids = m.add_tracks([{"title": "One", "artist": "A"}])
        m.job_store[ids[0]]["status"] = "Completed"
        m._persist()
        self.assertEqual(self.stored(), [])

    def test_an_untouched_queue_writes_no_file(self):
        # Nothing has been queued, so there is nothing to remember. restore()
        # already treats a missing file as an empty queue.
        m = self.manager()
        self.assertEqual(m.job_store, {})
        self.assertFalse(os.path.exists(self.queue_file))

    # ---- restore ----

    def test_restore_requeues_previous_tracks(self):
        self.write([{"title": "One", "artist": "A"},
                    {"title": "Two", "artist": "B"}])
        m = self.manager(restore=True)
        self.assertEqual(sorted(j["meta"]["title"] for j in m.job_store.values()),
                         ["One", "Two"])

    def test_restore_preserves_order(self):
        self.write([{"title": "First", "artist": "A"},
                    {"title": "Second", "artist": "B"},
                    {"title": "Third", "artist": "C"}])
        m = self.manager(restore=True)
        self.assertEqual([j["meta"]["title"] for j in m.queue],
                         ["First", "Second", "Third"])

    def test_restore_is_a_no_op_without_a_file(self):
        m = self.manager(restore=True)
        self.assertEqual(m.job_store, {})

    def test_restore_skips_malformed_entries(self):
        self.write([{"title": "Good", "artist": "A"}, {}, None,
                    {"artist": "no title"}, "junk"])
        m = self.manager(restore=True)
        self.assertEqual([j["meta"]["title"] for j in m.job_store.values()], ["Good"])

    def test_corrupt_file_does_not_stop_startup(self):
        with open(self.queue_file, "w", encoding="utf-8") as fh:
            fh.write("{not json")
        m = self.manager(restore=True)
        self.assertEqual(m.job_store, {})

    def test_wrong_shape_in_the_file_does_not_stop_startup(self):
        self.write({"not": "a list"})
        m = self.manager(restore=True)
        self.assertEqual(m.job_store, {})

    def test_restored_jobs_are_rewritten_to_disk(self):
        self.write([{"title": "One", "artist": "A"}])
        self.manager(restore=True)
        self.assertEqual([t["title"] for t in self.stored()], ["One"])

    def test_round_trip_is_stable(self):
        first = self.manager()
        first.add_tracks([{"title": "One", "artist": "A"},
                          {"title": "Two", "artist": "B"}])
        second = self.manager(restore=True)
        self.assertEqual([j["meta"]["title"] for j in second.queue],
                         [t["title"] for t in self.stored()])


if __name__ == "__main__":
    unittest.main()