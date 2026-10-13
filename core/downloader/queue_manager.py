import os
import uuid
from typing import Dict, Any, List
from PyQt6.QtCore import QObject, pyqtSignal
from core.downloader.worker import DownloadWorker
from core.config import AppConfig


class QueueManager(QObject):
    job_added = pyqtSignal(str, dict)                     # job_id, meta
    job_progress = pyqtSignal(str, float, str, str, str)  # job_id, percent, speed, eta, status
    job_finished = pyqtSignal(str, str, dict)             # job_id, file_path, meta
    job_error = pyqtSignal(str, str)                      # job_id, error_msg
    all_completed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.config = AppConfig.get_instance()
        self.queue: List[Dict[str, Any]] = []             # List of pending job dicts
        self.active_workers: Dict[str, DownloadWorker] = {}
        self.completed_jobs: List[Dict[str, Any]] = []
        self.job_store: Dict[str, Dict[str, Any]] = {}

    def add_tracks(self, tracks: List[Dict[str, Any]]):
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
                "error": None
            }
            self.job_store[job_id] = job_data
            self.queue.append(job_data)
            self.job_added.emit(job_id, track)

        self._process_queue()

    def cancel_job(self, job_id: str):
        # If in active workers
        if job_id in self.active_workers:
            worker = self.active_workers[job_id]
            worker.cancel()
            worker.terminate()
            del self.active_workers[job_id]
            if job_id in self.job_store:
                self.job_store[job_id]["status"] = "Cancelled"
            self.job_error.emit(job_id, "Download cancelled by user.")
            self._process_queue()
        else:
            # If still queued
            self.queue = [j for j in self.queue if j["id"] != job_id]
            if job_id in self.job_store:
                self.job_store[job_id]["status"] = "Cancelled"
            self.job_error.emit(job_id, "Download cancelled.")

    def cancel_all(self):
        self.queue.clear()
        for job_id, worker in list(self.active_workers.items()):
            worker.cancel()
            worker.terminate()
            if job_id in self.job_store:
                self.job_store[job_id]["status"] = "Cancelled"
            self.job_error.emit(job_id, "Cancelled.")
        self.active_workers.clear()

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

        if not self.active_workers and not self.queue:
            self.all_completed.emit()

    def _on_worker_progress(self, job_id: str, percent: float, speed: str, eta: str, status: str):
        if job_id in self.job_store:
            self.job_store[job_id]["percent"] = percent
            self.job_store[job_id]["speed"] = speed
            self.job_store[job_id]["eta"] = eta
            self.job_store[job_id]["status"] = status
        self.job_progress.emit(job_id, percent, speed, eta, status)

    def _on_worker_finished(self, job_id: str, file_path: str, meta: dict):
        if job_id in self.active_workers:
            del self.active_workers[job_id]
        if job_id in self.job_store:
            self.job_store[job_id]["status"] = "Completed"
            self.job_store[job_id]["percent"] = 100.0
            self.job_store[job_id]["file_path"] = file_path
            self.completed_jobs.append(self.job_store[job_id])
        self.job_finished.emit(job_id, file_path, meta)
        self._process_queue()

    def _on_worker_error(self, job_id: str, error_msg: str):
        if job_id in self.active_workers:
            del self.active_workers[job_id]
        if job_id in self.job_store:
            self.job_store[job_id]["status"] = "Failed"
            self.job_store[job_id]["error"] = error_msg
        self.job_error.emit(job_id, error_msg)
        self._process_queue()
