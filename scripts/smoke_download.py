"""Manual smoke check: resolve a track and drive it through the real queue.

Downloads a real file, hits the live network, and asserts nothing, so it is not
part of the test suite (see tests/). It exists to confirm the whole pipeline
works end to end against the current state of the sites.

Run from the repo root:  python scripts/smoke_download.py
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from PyQt6.QtCore import QCoreApplication
from core.metadata import MetadataResolver
from core.downloader.queue_manager import QueueManager

app = QCoreApplication(sys.argv)
qm = QueueManager.get_instance()
finished = False
success_result = None

def on_queue_event(event_type: str, data: dict):
    global finished, success_result
    jid = (data.get("job_id") or data.get("id", ""))[:8]
    if event_type == "job_progress":
        pct = data.get("progress", data.get("percent", 0.0))
        spd = data.get("speed", "")
        eta = data.get("eta", "")
        stat = data.get("status", "")
        print(f"[{jid}] Progress: {pct:.1f}% | Speed: {spd} | ETA: {eta} | Status: {stat}")
    elif event_type in ("job_completed", "job_finished"):
        path = data.get("file_path", "")
        print(f"[{jid}] SUCCESS! Saved to: {path}")
        success_result = path
        finished = True
    elif event_type in ("job_failed", "job_error"):
        err = data.get("error", "Unknown error")
        print(f"[{jid}] ERROR: {err}")
        finished = True

qm.subscribe(on_queue_event)

# Resolve an Apple Music track and drive it through the real download queue.
res = MetadataResolver.resolve("Blinding Lights", "apple")
if res.get("success") and res.get("tracks"):
    track = res["tracks"][0]
    print(f"Queueing: {track['title']} by {track['artist']} (Service: {track.get('service')})")
    qm.add_tracks([track])

    start = time.time()
    while not finished and time.time() - start < 60:
        app.processEvents()
        time.sleep(0.05)

    if success_result and os.path.exists(success_result):
        print("Download test PASSED! File size:", os.path.getsize(success_result), "bytes")
    else:
        print("Download test timed out or failed.")
else:
    print("Could not resolve track (offline sandbox or network blocked):", res.get("error"))
