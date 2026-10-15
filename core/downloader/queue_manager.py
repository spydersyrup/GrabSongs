import os
import json
import uuid
from typing import Dict, Any, List, Callable, Optional
from PyQt6.QtCore import QObject, pyqtSignal
from core.downloader.worker import DownloadWorker
from core.config import AppConfig

QUEUE_FILE = os.path.join(os.path.expanduser("~"), ".grabsongs", "queue.json")
TERMINAL = ("Completed", "Failed", "Cancelled")

class QueueManager(QObject):
    job_progress = pyqtSignal(str, float, str, str, str)  # job_id, percent, speed, eta, status
    job_finished = pyqtSignal(str, str, dict)             # job_id, file_path, meta
    job_error = pyqtSignal(str, str)                      # job_id, error_msg

    _instance = None

    @classmethod
    def get_instance(cls, parent=None):
        if cls._instance is None:
            cls._instance = QueueManager(parent)
        return cls._instance

    def __init__(self, parent=None, restore=True):
        super().__init__(parent)
        self.config = AppConfig.get_instance()
        self.queue: List[Dict[str, Any]] = []
        self.active_workers: Dict[str, DownloadWorker] = {}
        self.completed_jobs: List[Dict[str, Any]] = []
        self.job_store: Dict[str, Dict[str, Any]] = {}
        self._subscribers: List[Callable[[str, Dict[str, Any]], None]] = []
        if restore:
            self.restore()

    def restore(self) -> int:
        """Re-queue whatever was still outstanding when the app last closed."""
        try:
            with open(QUEUE_FILE, "r", encoding="utf-8") as f:
                tracks = json.load(f)
        except FileNotFoundError:
            return 0
        except Exception as e:
            print(f"[Queue] Could not read {QUEUE_FILE}: {e}")
            return 0
        if not isinstance(tracks, list):
            return 0
        usable = [t for t in tracks if isinstance(t, dict) and t.get("title")]
        if not usable:
            return 0
        print(f"[Queue] Restored {len(usable)} unfinished download(s)")
        self.add_tracks(usable)
        return len(usable)

    def _persist(self):
        """Keep the on-disk copy equal to what would still be pending if the
        app closed right now. An interrupted download is still in job_store as
        non-terminal, so it comes back on the next launch."""
        pending = [j["meta"] for j in self.job_store.values()
                   if j.get("status") not in TERMINAL]
        try:
            os.makedirs(os.path.dirname(QUEUE_FILE), exist_ok=True)
            with open(QUEUE_FILE, "w", encoding="utf-8") as f:
                json.dump(pending, f)
        except Exception as e:
            print(f"[Queue] Could not write {QUEUE_FILE}: {e}")

    def subscribe(self, callback: Callable[[str, Dict[str, Any]], None]):
        if callback not in self._subscribers:
            self._subscribers.append(callback)

    def _notify(self, event_type: str, data: Dict[str, Any]):
        for sub in list(self._subscribers):
            try:
                sub(event_type, data)
            except Exception:
                pass

    def add_tracks(self, tracks: List[Dict[str, Any]]) -> List[str]:
        added_ids = []
        for track in tracks:
            job_id = f"job_{uuid.uuid4().hex[:8]}"
            job_data = {
                "id": job_id,
                "meta": track,
                "status": "Queued",
                "percent": 0.0,
                "speed": "",
                "eta": "",
                "file_path": None,
                "error": None,
                "cancelled": False
            }
            self.job_store[job_id] = job_data
            self.queue.append(job_data)
            added_ids.append(job_id)
            self._notify("job_added", {"job_id": job_id, "metadata": track})

        self._persist()
        self._process_queue()
        return added_ids

    def cancel_job(self, job_id: str):
        if job_id in self.active_workers:
            # Cooperative cancel. The worker stops at its next cancellation point
            # and reports back through _on_worker_error, which is what releases the
            # slot and advances the queue. terminate() would kill it mid-write,
            # leaving a half-written file and an orphaned ffmpeg child.
            self.active_workers[job_id].cancel()
            self._mark_cancelled(job_id)
            self.job_error.emit(job_id, "Download cancelled by user.")
        else:
            self.queue = [j for j in self.queue if j["id"] != job_id]
            self._mark_cancelled(job_id)
            self.job_error.emit(job_id, "Download cancelled.")

    def cancel_all(self):
        for j in list(self.queue):
            self._mark_cancelled(j.get("id"))
        self.queue.clear()
        for job_id, worker in list(self.active_workers.items()):
            worker.cancel()
            self._mark_cancelled(job_id)

    def _mark_cancelled(self, job_id: str):
        job = self.job_store.get(job_id)
        if job:
            job["cancelled"] = True
            job["status"] = "Cancelled"
        self._notify("job_cancelled", {"job_id": job_id})
        self._persist()

    def _process_queue(self):
        max_concurrent = int(self.config.get("max_concurrent_downloads", 2))

        while len(self.active_workers) < max_concurrent and self.queue:
            job = self.queue.pop(0)
            job_id = job["id"]
            track_meta = job["meta"]

            worker = DownloadWorker(
                job_id=job_id,
                track_meta=track_meta,
                config=self.config.settings,
                parent=self
            )
            worker.progress_signal.connect(self._on_worker_progress)
            worker.finished_signal.connect(self._on_worker_finished)
            worker.error_signal.connect(self._on_worker_error)

            self.active_workers[job_id] = worker
            worker.start()

    def _on_worker_progress(self, job_id: str, percent: float, speed: str, eta: str, status: str):
        job = self.job_store.get(job_id)
        # Progress already in flight when the user cancelled would otherwise
        # overwrite "Cancelled" with "Downloading..." as it drains the queue.
        if not job or job["cancelled"]:
            return
        job["percent"] = percent
        job["speed"] = speed
        job["eta"] = eta
        job["status"] = status
        self.job_progress.emit(job_id, percent, speed, eta, status)
        self._notify("job_progress", {
            "job_id": job_id,
            "progress": percent,
            "speed": speed,
            "eta": eta,
            "status": "downloading" if percent < 95 else "converting"
        })

    def _on_worker_finished(self, job_id: str, file_path: str, meta: dict):
        if job_id in self.active_workers:
            del self.active_workers[job_id]
        if job_id in self.job_store:
            self.job_store[job_id]["status"] = "Completed"
            self.job_store[job_id]["percent"] = 100.0
            self.job_store[job_id]["file_path"] = file_path
            self.completed_jobs.append(self.job_store[job_id])
        self._persist()
        self.job_finished.emit(job_id, file_path, meta)
        self._notify("job_completed", {
            "job_id": job_id,
            "file_path": file_path,
            "metadata": meta,
            "status": "completed"
        })
        self._process_queue()

    def _on_worker_error(self, job_id: str, error_msg: str):
        if job_id in self.active_workers:
            del self.active_workers[job_id]
        job = self.job_store.get(job_id)
        if job and not job["cancelled"]:
            job["status"] = "Failed"
            job["error"] = error_msg
            self.job_error.emit(job_id, error_msg)
            self._notify("job_failed", {
                "job_id": job_id,
                "error": error_msg,
                "status": "failed"
            })
        self._persist()
        self._process_queue()
