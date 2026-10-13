import os
import time
from core.metadata import MetadataResolver
from core.downloader.queue_manager import QueueManager
from PyQt6.QtCore import QCoreApplication

app = QCoreApplication([])

qm = QueueManager()
finished = False
success_result = None

def on_prog(jid, pct, spd, eta, stat):
    print(f"[{jid[:8]}] Progress: {pct:.1f}% | Speed: {spd} | ETA: {eta} | Status: {stat}")

def on_fin(jid, path, meta):
    global finished, success_result
    print(f"[{jid[:8]}] SUCCESS! Saved to: {path}")
    finished = True
    success_result = path

def on_err(jid, err):
    global finished
    print(f"[{jid[:8]}] ERROR: {err}")
    finished = True

qm.job_progress.connect(on_prog)
qm.job_finished.connect(on_fin)
qm.job_error.connect(on_err)

# Resolve a quick track
res = MetadataResolver.resolve("Mo City Flexologist", "youtube")
track = res["tracks"][0]
print(f"Queueing: {track['title']} by {track['artist']}")
qm.add_tracks([track])

start = time.time()
while not finished and time.time() - start < 45:
    app.processEvents()
    time.sleep(0.1)

if success_result and os.path.exists(success_result):
    print("Download test PASSED! File size:", os.path.getsize(success_result), "bytes")
else:
    print("Download test timed out or failed.")
