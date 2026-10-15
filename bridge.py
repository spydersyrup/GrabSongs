import os
import sys
import base64
import hashlib
from typing import Dict, Any, List, Optional

from PyQt6.QtCore import (
    QObject, pyqtSignal, pyqtSlot, pyqtProperty, QUrl, QThread,
    Qt, QSize, QRectF
)
from PyQt6.QtGui import QImage, QPainter, QImageReader, QBrush
from PyQt6.QtQuick import QQuickImageProvider
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput

from core.config import AppConfig
from core.metadata import MetadataResolver
from core.downloader.queue_manager import QueueManager
from core.downloader.tagger import AudioTagger
from core.downloader.worker import build_base_name


class PyCoverImageProvider(QQuickImageProvider):
    def __init__(self):
        super().__init__(QQuickImageProvider.ImageType.Image)
        self.cache_dir = os.path.join(os.path.expanduser("~"), ".grabsongs", "covers")
        try:
            os.makedirs(self.cache_dir, exist_ok=True)
        except Exception:
            self.cache_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".covers")
            os.makedirs(self.cache_dir, exist_ok=True)

    def requestImage(self, id_str: str, requested_size: QSize):
        parts = id_str.split('/', 1)
        try:
            fraction = float(parts[0])
        except Exception:
            fraction = 0.0
        source = parts[1] if len(parts) > 1 else ""

        img_path = ""
        if source.startswith("track:"):
            try:
                b64 = source[6:].replace("-", "+").replace("_", "/")
                b64 += "=" * ((4 - len(b64) % 4) % 4)
                track_path = base64.b64decode(b64).decode("utf-8")
                h = hashlib.md5(track_path.encode("utf-8")).hexdigest()
                cached_art = os.path.join(self.cache_dir, f"{h}.jpg")
                if os.path.exists(cached_art):
                    img_path = cached_art
                else:
                    tags = AudioTagger.read_tags(track_path)
                    img_path = tags.get("cover_path", "")
            except Exception:
                pass
        elif source.startswith("file:"):
            img_path = QUrl(source).toLocalFile()
        elif source.startswith("../assets/") or source.startswith("assets/"):
            img_path = os.path.abspath(source)
            if not os.path.exists(img_path):
                img_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", os.path.basename(source))
        else:
            if os.path.exists(source):
                img_path = source
            else:
                asset_cand = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", os.path.basename(source))
                if os.path.exists(asset_cand):
                    img_path = asset_cand

        if not img_path or not os.path.exists(img_path):
            img = QImage(1, 1, QImage.Format.Format_ARGB32_Premultiplied)
            img.fill(Qt.GlobalColor.transparent)
            return img, QSize(1, 1)

        reader = QImageReader(img_path)
        reader.setAutoTransform(True)
        img = reader.read()
        if img.isNull():
            img = QImage(1, 1, QImage.Format.Format_ARGB32_Premultiplied)
            img.fill(Qt.GlobalColor.transparent)
            return img, QSize(1, 1)

        orig_size = img.size()
        target_w = requested_size.width() if requested_size.width() > 0 else orig_size.width()
        target_h = requested_size.height() if requested_size.height() > 0 else orig_size.height()

        if target_w > 0 and target_h > 0:
            img = img.scaled(
                target_w, target_h,
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation
            )
            crop_x = max(0, (img.width() - target_w) // 2)
            crop_y = max(0, (img.height() - target_h) // 2)
            img = img.copy(crop_x, crop_y, target_w, target_h)

        if fraction > 0:
            radius = fraction * min(img.width(), img.height())
            rounded = QImage(img.size(), QImage.Format.Format_ARGB32_Premultiplied)
            rounded.fill(Qt.GlobalColor.transparent)
            p = QPainter(rounded)
            p.setRenderHint(QPainter.RenderHint.Antialiasing)
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QBrush(img))
            p.drawRoundedRect(QRectF(0, 0, img.width(), img.height()), radius, radius)
            p.end()
            img = rounded

        return img, img.size()


class SearchWorker(QThread):
    finished = pyqtSignal(list, "QVariant")
    failed = pyqtSignal(str)

    def __init__(self, query: str, service: str = "all"):
        super().__init__()
        self.query = query.strip()
        self.service = service

    def run(self):
        try:
            if not self.query:
                self.finished.emit([], None)
                return
            result = MetadataResolver.resolve(self.query, self.service)
            # A newer search superseded this one while the metadata calls were in
            # flight. Emitting now would overwrite the newer results with stale ones.
            if self.isInterruptionRequested():
                return
            if result.get("success"):
                tracks = result.get("tracks", [])
                config = AppConfig.get_instance()
                dl_dir = config.get("download_dir", os.path.expanduser("~/Music/GrabSongs"))
                ext = config.get("audio_format", "mp3").lower()
                for t in tracks:
                    expected = os.path.join(dl_dir, f"{build_base_name(t, config.settings)}.{ext}")
                    t["downloaded"] = os.path.exists(expected)
                collection = None
                if result.get("type") in ("album", "playlist") and result.get("item"):
                    item = result.get("item")
                    collection = {
                        "title": item.get("title", ""),
                        "artist": item.get("artist", ""),
                        "cover_url": item.get("cover_url", ""),
                        "count": len(tracks),
                        "service": result.get("service", "")
                    }
                self.finished.emit(tracks, collection)
            else:
                self.failed.emit(result.get("error", "No tracks found."))
        except Exception as e:
            self.failed.emit(str(e))


class DownloaderBridge(QObject):
    searchStarted = pyqtSignal()
    searchFinished = pyqtSignal("QVariantList", "QVariant")
    searchFailed = pyqtSignal(str)
    jobProgress = pyqtSignal(str, float, str, str)
    jobFinished = pyqtSignal(str, bool, str)
    isSearchingChanged = pyqtSignal()
    configChanged = pyqtSignal()
    downloadedFilesChanged = pyqtSignal()
    previewStateChanged = pyqtSignal()
    positionChanged = pyqtSignal(int)
    durationChanged = pyqtSignal(int)
    volumeChanged = pyqtSignal(float)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.queue_manager = QueueManager(self)
        self.queue_manager.job_progress.connect(self._on_progress)
        self.queue_manager.job_finished.connect(self._on_finished)
        self.queue_manager.job_error.connect(self._on_error)
        self._active_worker: Optional[SearchWorker] = None
        self._is_searching = False
        self._preview_playing = False
        self._preview_path = ""
        self._preview_meta = {}
        self._position = 0
        self._duration = 0

        try:
            self._player = QMediaPlayer(self)
            self._audio_output = QAudioOutput(self)
            self._player.setAudioOutput(self._audio_output)
            self._audio_output.setVolume(1.0)
            self._player.playbackStateChanged.connect(self._on_playback_state_changed)
            self._player.positionChanged.connect(self._on_pos_changed)
            self._player.durationChanged.connect(self._on_dur_changed)
        except Exception:
            self._player = None
            self._audio_output = None

    def _on_pos_changed(self, pos):
        self._position = pos
        self.positionChanged.emit(pos)

    def _on_dur_changed(self, dur):
        self._duration = dur
        self.durationChanged.emit(dur)

    def _on_playback_state_changed(self):
        if self._player:
            self._preview_playing = (self._player.playbackState() == QMediaPlayer.PlaybackState.PlayingState)
            self.previewStateChanged.emit()

    def _on_progress(self, job_id, percent, speed, eta, status):
        self.jobProgress.emit(job_id, percent, speed, eta)

    def _on_finished(self, job_id, file_path, meta):
        self.jobFinished.emit(job_id, True, file_path)
        self.downloadedFilesChanged.emit()

    def _on_error(self, job_id, error_msg):
        self.jobFinished.emit(job_id, False, error_msg)

    @pyqtProperty(bool, notify=isSearchingChanged)
    def isSearching(self) -> bool:
        return self._is_searching

    @pyqtProperty(bool, notify=previewStateChanged)
    def previewPlaying(self) -> bool:
        return self._preview_playing

    @pyqtProperty(str, notify=previewStateChanged)
    def currentPreviewPath(self) -> str:
        return self._preview_path

    @pyqtSlot(str)
    @pyqtSlot(str, str)
    def search(self, query: str, service: str = "all"):
        if self._active_worker is not None:
            self._active_worker.requestInterruption()

        self._is_searching = True
        self.isSearchingChanged.emit()
        self.searchStarted.emit()
        self._active_worker = SearchWorker(query, service)
        
        def _on_done(tracks, collection):
            self._is_searching = False
            self.isSearchingChanged.emit()
            self.searchFinished.emit(tracks, collection)

        def _on_fail(err):
            self._is_searching = False
            self.isSearchingChanged.emit()
            self.searchFailed.emit(err)

        self._active_worker.finished.connect(_on_done)
        self._active_worker.failed.connect(_on_fail)
        self._active_worker.start()

    @pyqtSlot("QVariantMap")
    def downloadTrack(self, track: dict):
        self.queue_manager.add_tracks([track])

    @pyqtSlot("QVariantList")
    def downloadAll(self, tracks: list):
        self.queue_manager.add_tracks(tracks)

    @pyqtProperty(str, notify=configChanged)
    def downloadDirectory(self) -> str:
        config = AppConfig.get_instance()
        return config.get("download_dir", os.path.expanduser("~/Music/GrabSongs"))

    @pyqtSlot(str)
    def setDownloadDirectory(self, path: str):
        if path and os.path.exists(path):
            config = AppConfig.get_instance()
            config.set("download_dir", path)
            self.configChanged.emit()
            self.downloadedFilesChanged.emit()

    @pyqtProperty(str, notify=configChanged)
    def audioFormat(self) -> str:
        return AppConfig.get_instance().get("audio_format", "mp3")

    @pyqtSlot(str)
    def setAudioFormat(self, fmt: str):
        AppConfig.get_instance().set("audio_format", fmt.lower())
        self.configChanged.emit()

    @pyqtProperty(str, notify=configChanged)
    def audioQuality(self) -> str:
        return AppConfig.get_instance().get("audio_quality", "320")

    @pyqtSlot(str)
    def setAudioQuality(self, quality: str):
        AppConfig.get_instance().set("audio_quality", quality)
        self.configChanged.emit()

    @pyqtProperty(bool, notify=configChanged)
    def embedLyrics(self) -> bool:
        return AppConfig.get_instance().get("embed_lyrics", True)

    @pyqtSlot(bool)
    def setEmbedLyrics(self, val: bool):
        AppConfig.get_instance().set("embed_lyrics", val)
        self.configChanged.emit()

    @pyqtProperty(bool, notify=configChanged)
    def embedArtwork(self) -> bool:
        return AppConfig.get_instance().get("embed_artwork", True)

    @pyqtSlot(bool)
    def setEmbedArtwork(self, val: bool):
        AppConfig.get_instance().set("embed_artwork", val)
        self.configChanged.emit()

    @pyqtProperty(bool, notify=configChanged)
    def saveLrcFile(self) -> bool:
        return AppConfig.get_instance().get("save_lrc_file", False)

    @pyqtSlot(bool)
    def setSaveLrcFile(self, val: bool):
        AppConfig.get_instance().set("save_lrc_file", val)
        self.configChanged.emit()

    @pyqtProperty(int, notify=configChanged)
    def maxConcurrentDownloads(self) -> int:
        return int(AppConfig.get_instance().get("max_concurrent_downloads", 2))

    @pyqtSlot(int)
    def setMaxConcurrentDownloads(self, val: int):
        val = max(1, min(4, val))
        AppConfig.get_instance().set("max_concurrent_downloads", val)
        self.configChanged.emit()

    @pyqtProperty(str, notify=configChanged)
    def ffmpegPath(self) -> str:
        return AppConfig.get_instance().get("ffmpeg_path", "")

    @pyqtProperty(str, notify=configChanged)
    def accentName(self) -> str:
        return AppConfig.get_instance().get("accent", "terracotta")

    @pyqtSlot(str)
    def setAccentName(self, val: str):
        AppConfig.get_instance().set("accent", val)
        self.configChanged.emit()

    @pyqtSlot(result=str)
    def chooseDownloadDirectory(self) -> str:
        from PyQt6.QtWidgets import QFileDialog
        path = QFileDialog.getExistingDirectory(None, "Select Download Directory", self.downloadDirectory)
        if path:
            self.setDownloadDirectory(path)
            return path
        return ""

    @pyqtSlot()
    def openDownloadFolder(self):
        d = self.downloadDirectory
        os.makedirs(d, exist_ok=True)
        if sys.platform == "win32":
            os.startfile(d)
        elif sys.platform == "darwin":
            import subprocess
            subprocess.run(["open", d])
        else:
            import subprocess
            subprocess.run(["xdg-open", d])

    @pyqtSlot(result="QVariantList")
    def getActiveJobs(self) -> list:
        jobs = []
        for j in self.queue_manager.job_store.values():
            meta = j.get("meta", {})
            jobs.append({
                "id": j.get("id", ""),
                "title": meta.get("title", ""),
                "artist": meta.get("artist", ""),
                "album": meta.get("album", ""),
                "cover_url": meta.get("cover_url", ""),
                "service": meta.get("service", ""),
                "percent": j.get("percent", 0.0),
                "status": str(j.get("status", "Queued")),
                "speed": str(j.get("speed", "")),
                "eta": str(j.get("eta", "")),
                "file_path": str(j.get("file_path", "") or ""),
                "error": str(j.get("error", "") or "")
            })
        return jobs

    @pyqtSlot(result="QVariantList")
    def getDownloadedFiles(self) -> list:
        d = self.downloadDirectory
        if not os.path.exists(d):
            return []
        items = []
        try:
            for root, _, files in os.walk(d):
                for f in files:
                    if f.lower().endswith((".mp3", ".flac", ".m4a", ".opus", ".wav")):
                        full_path = os.path.join(root, f)
                        stat = os.stat(full_path)
                        name_no_ext = os.path.splitext(f)[0]
                        artist = ""
                        title = name_no_ext
                        album = ""
                        duration = 0
                        cover_url = ""
                        cover_path = ""

                        if " - " in name_no_ext:
                            parts = name_no_ext.split(" - ", 1)
                            artist = parts[0].strip()
                            title = parts[1].strip()

                        try:
                            tags = AudioTagger.read_tags(full_path)
                            if tags:
                                if tags.get("title"):
                                    title = tags["title"]
                                if tags.get("artist"):
                                    artist = tags["artist"]
                                album = tags.get("album", "")
                                duration = tags.get("duration", 0)
                                cover_path = tags.get("cover_path", "")
                                if cover_path and os.path.exists(cover_path):
                                    cover_url = QUrl.fromLocalFile(cover_path).toString()
                        except Exception:
                            pass

                        size_mb = f"{stat.st_size / (1024 * 1024):.1f} MB"
                        items.append({
                            "title": title,
                            "artist": artist,
                            "album": album,
                            "filename": f,
                            "path": full_path,
                            "size": size_mb,
                            "duration": duration,
                            "cover_url": cover_url,
                            "cover_path": cover_path,
                            "modified": stat.st_mtime
                        })
            items.sort(key=lambda x: x["modified"], reverse=True)
        except Exception as e:
            print("Error scanning downloaded files:", e)
        return items

    @pyqtSlot(str)
    def revealFileInExplorer(self, path: str):
        if not os.path.exists(path):
            return
        if sys.platform == "win32":
            import subprocess
            subprocess.run(["explorer", f"/select,{os.path.normpath(path)}"])
        elif sys.platform == "darwin":
            import subprocess
            subprocess.run(["open", "-R", path])
        else:
            import subprocess
            try:
                subprocess.run(["dbus-send", "--session", "--dest=org.freedesktop.FileManager1",
                                "--type=method_call", "/org/freedesktop/FileManager1",
                                "org.freedesktop.FileManager1.ShowItems",
                                f"array:string:file://{os.path.abspath(path)}", "string:"])
            except Exception:
                subprocess.run(["xdg-open", os.path.dirname(path)])

    @pyqtSlot(str)
    def deleteFile(self, path: str):
        if os.path.exists(path):
            try:
                os.remove(path)
                self.downloadedFilesChanged.emit()
            except Exception as e:
                print("Error deleting file:", e)

    @pyqtProperty(int, notify=positionChanged)
    def previewPosition(self) -> int:
        return self._position

    @pyqtProperty(int, notify=durationChanged)
    def previewDuration(self) -> int:
        return self._duration

    @pyqtSlot(int)
    def seekPreview(self, pos_ms: int):
        if self._player:
            self._player.setPosition(pos_ms)

    @pyqtProperty(float, notify=volumeChanged)
    def previewVolume(self) -> float:
        if self._audio_output:
            return float(self._audio_output.volume())
        return 1.0

    @pyqtSlot(float)
    def setPreviewVolume(self, vol: float):
        if self._audio_output:
            self._audio_output.setVolume(max(0.0, min(1.0, vol)))
            self.volumeChanged.emit(vol)

    @pyqtProperty("QVariantMap", notify=previewStateChanged)
    def currentPreviewTrack(self) -> dict:
        if self._preview_meta:
            return self._preview_meta
        if self._preview_path:
            name_no_ext = os.path.splitext(os.path.basename(self._preview_path))[0]
            artist = "GrabSongs"
            title = name_no_ext
            if " - " in name_no_ext:
                parts = name_no_ext.split(" - ", 1)
                artist, title = parts[0].strip(), parts[1].strip()
            return {"title": title, "artist": artist, "path": self._preview_path, "cover_path": ""}
        return {
            "title": "GrabSongs Audio Engine",
            "artist": "Ready to grab from Spotify, Apple Music, YouTube & Deezer",
            "path": "",
            "cover_path": ""
        }

    @pyqtSlot(result=str)
    def getClipboardText(self) -> str:
        try:
            from PyQt6.QtWidgets import QApplication
            cb = QApplication.clipboard()
            return cb.text() if cb else ""
        except Exception:
            return ""

    @pyqtSlot()
    def clearCompletedJobs(self):
        to_del = [k for k, v in self.queue_manager.job_store.items() if v.get("status") in ["Completed", "Failed", "Cancelled"]]
        for k in to_del:
            self.queue_manager.job_store.pop(k, None)

    @pyqtSlot(str)
    @pyqtSlot(str, "QVariant")
    def togglePreview(self, path: str, meta: Any = None):
        if not self._player or not path:
            return
        if self._preview_playing and self._preview_path == path:
            self._player.stop()
            self._preview_playing = False
            self.previewStateChanged.emit()
        else:
            self._preview_path = path
            if meta and isinstance(meta, dict):
                self._preview_meta = {
                    "title": meta.get("title", "Track"),
                    "artist": meta.get("artist", "Artist"),
                    "path": path,
                    "cover_path": meta.get("cover_url", "")
                }
            else:
                name_no_ext = os.path.splitext(os.path.basename(path))[0]
                artist = "GrabSongs"
                title = name_no_ext
                if " - " in name_no_ext:
                    parts = name_no_ext.split(" - ", 1)
                    artist, title = parts[0].strip(), parts[1].strip()
                self._preview_meta = {
                    "title": title,
                    "artist": artist,
                    "path": path,
                    "cover_path": ""
                }

            if path.startswith("http://") or path.startswith("https://"):
                self._player.setSource(QUrl(path))
            else:
                self._player.setSource(QUrl.fromLocalFile(path))
            self._player.play()
            self._preview_playing = True
            self.previewStateChanged.emit()

    @pyqtSlot()
    def togglePlayPause(self):
        if not self._player:
            return
        if self._preview_playing:
            self._player.pause()
            self._preview_playing = False
            self.previewStateChanged.emit()
        else:
            if self._preview_path:
                self._player.play()
                self._preview_playing = True
                self.previewStateChanged.emit()
            else:
                files = self.getDownloadedFiles()
                if files:
                    self.togglePreview(files[0]["path"])

    @pyqtSlot()
    def stopPreview(self):
        if self._player:
            self._player.stop()
            self._preview_playing = False
            self.previewStateChanged.emit()

    @pyqtSlot()
    def cancelAll(self):
        self.queue_manager.cancel_all()

    @pyqtSlot(str)
    def dismissJob(self, job_id: str):
        if job_id in self.queue_manager.job_store:
            j = self.queue_manager.job_store[job_id]
            if j.get("status") in ["Completed", "Failed", "Cancelled"]:
                self.queue_manager.job_store.pop(job_id, None)
            else:
                self.queue_manager.cancel_job(job_id)
                self.queue_manager.job_store.pop(job_id, None)

