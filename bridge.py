import os
import sys
import json
import time
import base64
import hashlib
import glob
from typing import Dict, Any, List, Optional

from PyQt6.QtCore import (
    QObject, pyqtSignal, pyqtSlot, pyqtProperty, QUrl, QThread,
    QAbstractListModel, QModelIndex, Qt, QSize, QRectF, QPointF, QTimer
)
from PyQt6.QtGui import QImage, QPainter, QImageReader, QFontDatabase, QIcon, QBrush
from PyQt6.QtQuick import QQuickImageProvider
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput

from core.config import AppConfig
from core.metadata import MetadataResolver
from core.downloader.queue_manager import QueueManager
from core.downloader.tagger import AudioTagger


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


class SettingsBridge(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings_file = os.path.join(os.path.expanduser("~"), ".grabsongs", "settings.json")
        try:
            os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
        except Exception:
            self.settings_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "settings.json")
        self._data: Dict[str, Any] = {
            "ui/accentName": "recordRed",
            "ui/page": "home",
            "ui/sidebarCollapsed": False,
            "library/folders": [os.path.expanduser("~/Music/GrabSongs")],
            "search/recent": "[]"
        }
        self._load()

    def _load(self):
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, "r", encoding="utf-8") as f:
                    self._data.update(json.load(f))
            except Exception as e:
                print(f"[Settings] Load error: {e}")

    @pyqtSlot()
    def sync(self):
        try:
            with open(self.settings_file, "w", encoding="utf-8") as f:
                json.dump(self._data, f, indent=2)
        except Exception as e:
            print(f"[Settings] Save error: {e}")

    @pyqtSlot(str, result="QVariant")
    @pyqtSlot(str, "QVariant", result="QVariant")
    def value(self, key: str, default=None):
        return self._data.get(key, default)

    @pyqtSlot(str, "QVariant")
    def setValue(self, key: str, val):
        self._data[key] = val
        self.sync()

    @pyqtSlot("QVariantMap")
    def setValues(self, values: dict):
        self._data.update(values)
        self.sync()

    @pyqtSlot(QUrl, result=str)
    def readTextFile(self, url: QUrl) -> str:
        path = url.toLocalFile() if url.isLocalFile() else url.toString()
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        return ""

    @pyqtSlot(QUrl, str, result=bool)
    def exportTextFile(self, url: QUrl, text: str) -> bool:
        path = url.toLocalFile() if url.isLocalFile() else url.toString()
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(text)
            return True
        except Exception:
            return False

    @pyqtSlot(str)
    def copyToClipboard(self, text: str):
        pass

    @pyqtSlot(str)
    def showInFolder(self, file_path: str):
        if os.path.exists(file_path):
            import subprocess
            if sys.platform == "win32":
                subprocess.run(["explorer", f"/select,{os.path.abspath(file_path)}"])
            elif sys.platform == "darwin":
                subprocess.run(["open", "-R", os.path.abspath(file_path)])
            else:
                folder = os.path.dirname(os.path.abspath(file_path)) if os.path.isfile(file_path) else file_path
                subprocess.run(["xdg-open", folder])

    @pyqtSlot(result=str)
    def getLogFilePath(self) -> str:
        return os.path.join(os.path.expanduser("~"), ".grabsongs", "grabsongs.log")

    @pyqtSlot(result=str)
    @pyqtSlot(int, result=str)
    def readRecentLogs(self, maxLines: int = 150) -> str:
        return "GrabSongs CassetteCat System Ready\n"

    @pyqtSlot()
    def clearLogs(self):
        pass

    @pyqtSlot()
    def openLogFile(self):
        pass


class LibraryBridge(QAbstractListModel):
    TrackRole = Qt.ItemDataRole.UserRole + 1

    changed = pyqtSignal()
    tracksChanged = pyqtSignal()
    visibleTracksChanged = pyqtSignal()
    listensChanged = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.music_dir = os.path.expanduser("~/Music/GrabSongs")
        try:
            os.makedirs(self.music_dir, exist_ok=True)
        except Exception:
            self.music_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "downloads")
            os.makedirs(self.music_dir, exist_ok=True)
        self._folders = [self.music_dir]
        self._tracks: List[Dict[str, Any]] = []
        self._visible_tracks: List[Dict[str, Any]] = []
        self.refreshLibrary()

    def roleNames(self):
        return {self.TrackRole: b"track"}

    def rowCount(self, parent=QModelIndex()):
        return len(self._visible_tracks)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid() or index.row() >= len(self._visible_tracks):
            return None
        if role == self.TrackRole:
            return self._visible_tracks[index.row()]
        return None

    @pyqtProperty(int, notify=tracksChanged)
    def trackCount(self) -> int:
        return len(self._tracks)

    @pyqtProperty(int, notify=visibleTracksChanged)
    def visibleTrackCount(self) -> int:
        return len(self._visible_tracks)

    @pyqtProperty("QStringList", notify=changed)
    def folders(self) -> List[str]:
        return self._folders

    @pyqtProperty("QStringList", notify=tracksChanged)
    def availablePaths(self) -> List[str]:
        return [t["filePath"] for t in self._tracks]

    @pyqtSlot()
    def refreshLibrary(self):
        tracks = []
        for folder in self._folders:
            if not os.path.exists(folder):
                continue
            for ext in ("*.mp3", "*.flac", "*.m4a", "*.opus", "*.ogg", "*.wav"):
                for fpath in glob.glob(os.path.join(folder, ext)):
                    fpath = os.path.abspath(fpath)
                    fname = os.path.basename(fpath)
                    meta = AudioTagger.read_tags(fpath)
                    title = meta.get("title") or os.path.splitext(fname)[0]
                    artist = meta.get("artist") or "Unknown Artist"
                    album = meta.get("album") or "GrabSongs Library"
                    dur_sec = meta.get("duration", 0)
                    mins = int(dur_sec // 60)
                    secs = int(dur_sec % 60)
                    dur_str = f"{mins}:{secs:02d}" if dur_sec else "--:--"

                    cover_p = meta.get("cover_path") or ""
                    if cover_p and not cover_p.startswith("file:"):
                        cover_p = QUrl.fromLocalFile(os.path.abspath(cover_p)).toString()

                    lrc_path = os.path.splitext(fpath)[0] + ".lrc"
                    lyrics_text = ""
                    if os.path.exists(lrc_path):
                        try:
                            with open(lrc_path, "r", encoding="utf-8") as lf:
                                lyrics_text = lf.read()
                        except Exception:
                            pass

                    t_info = {
                        "title": title,
                        "artist": artist,
                        "album": album,
                        "genre": meta.get("genre", "Soundtrack"),
                        "year": meta.get("year", 2024),
                        "trackNumber": 1,
                        "discNumber": 1,
                        "duration": dur_str,
                        "durationSeconds": int(dur_sec),
                        "filePath": fpath,
                        "fileName": fname,
                        "format": os.path.splitext(fpath)[1].replace(".", "").upper(),
                        "artworkUrl": cover_p,
                        "lyrics": lyrics_text,
                        "fileSize": os.path.getsize(fpath) if os.path.exists(fpath) else 0,
                        "lastModified": int(os.path.getmtime(fpath)) if os.path.exists(fpath) else 0
                    }
                    tracks.append(t_info)

        self.beginResetModel()
        self._tracks = tracks
        self._visible_tracks = list(tracks)
        self.endResetModel()

        self.tracksChanged.emit()
        self.visibleTracksChanged.emit()
        self.changed.emit()

    @pyqtSlot(QUrl)
    def loadFolder(self, url: QUrl):
        path = url.toLocalFile() if url.isLocalFile() else url.toString()
        if path and os.path.exists(path) and path not in self._folders:
            self._folders.append(path)
            self.refreshLibrary()

    @pyqtSlot(str)
    def removeFolder(self, path: str):
        if path in self._folders:
            self._folders.remove(path)
            self.refreshLibrary()

    @pyqtSlot("QVariantMap", result=str)
    def matchKey(self, track: dict) -> str:
        title = str(track.get("title", "")).strip().lower()
        artist = str(track.get("artist", "")).strip().lower()
        return f"{title}:{artist}"

    @pyqtSlot(QUrl, result=str)
    def localPath(self, url: QUrl) -> str:
        return url.toLocalFile() if url.isLocalFile() else url.toString()

    @pyqtSlot(str, result=str)
    def artworkFor(self, filePath: str) -> str:
        for t in self._tracks:
            if t.get("filePath") == filePath:
                return t.get("artworkUrl", "")
        return ""

    @pyqtSlot(str, str)
    def setCustomArtwork(self, filePath: str, artworkPath: str):
        pass

    @pyqtSlot(str, str, str)
    def setAlbumArtwork(self, album: str, artist: str, artworkPath: str):
        pass

    @pyqtSlot("QVariantList", result="QVariantList")
    def tracksForPaths(self, paths: list) -> list:
        res = []
        path_set = {str(p) for p in paths}
        for t in self._tracks:
            if t.get("filePath") in path_set:
                res.append(t)
        return res

    @pyqtSlot(result="QStringList")
    def availablePaths(self) -> List[str]:
        return [t.get("filePath", "") for t in self._tracks if t.get("filePath")]

    @pyqtSlot(str, str, result=int)
    def compareNames(self, left: str, right: str) -> int:
        l = left.lower().lstrip("the ").lstrip("a ")
        r = right.lower().lstrip("the ").lstrip("a ")
        if l < r:
            return -1
        elif l > r:
            return 1
        return 0

    @pyqtSlot(str, result="QStringList")
    def artistNames(self, artist: str) -> List[str]:
        if not artist:
            return []
        import re
        tokens = re.split(r'[,;&/]|(?:\s+(?:feat\.?|ft\.?|with|x)\s+)', artist, flags=re.IGNORECASE)
        return [t.strip() for t in tokens if t.strip()]

    @pyqtSlot("QVariantMap", int)
    @pyqtSlot("QVariantMap", int, bool)
    def recordListen(self, track: dict, listenedMs: int, counted: bool = True):
        self.listensChanged.emit()

    @pyqtSlot(result="QVariantList")
    def listeningYears(self) -> list:
        return [2026, 2025, 2024]

    @pyqtSlot(int, result="QVariantMap")
    @pyqtSlot(int, int, result="QVariantMap")
    def listeningRecap(self, year: int, month: int = -1) -> dict:
        return {
            "plays": len(self._tracks),
            "uniquePlayed": len(self._tracks),
            "topSongs": self._tracks[:5],
            "topArtists": [],
            "topAlbums": [],
            "topGenres": []
        }

    @pyqtSlot()
    def clearListeningLog(self):
        self.listensChanged.emit()

    @pyqtSlot(result="QVariantMap")
    @pyqtSlot("QVariantMap", "QVariantMap", "QVariantMap", "QVariantList", result="QVariantMap")
    def homeRecommendations(self, playCounts=None, seenAt=None, favorites=None, history=None) -> dict:
        tracks = self._tracks
        spotlight = tracks[0] if tracks else {}
        albums = []
        artists = []
        seen_alb = set()
        seen_art = set()
        for t in tracks:
            alb = t.get("album", "")
            art = t.get("artist", "")
            if alb and alb not in seen_alb:
                seen_alb.add(alb)
                albums.append({"name": alb, "artist": art, "track": t, "count": 1})
            if art and art not in seen_art:
                seen_art.add(art)
                artists.append({"name": art, "track": t, "count": 1})

        return {
            "spotlight": spotlight,
            "spotlightTrack": spotlight,
            "quickPicks": tracks[:10],
            "heavyRotation": tracks[:10],
            "recentlyPlayed": tracks[:10],
            "recentlyAdded": tracks[:10],
            "forgottenFavs": tracks[:10],
            "albumsRotation": albums[:10],
            "artistsRotation": artists[:10]
        }

    @pyqtSlot("QVariantMap", result="QVariantMap")
    def updateTrackMetadata(self, metadata: dict) -> dict:
        return metadata

    @pyqtSlot("QStringList", "QVariantMap", result=int)
    def updateTracksMetadata(self, filePaths: list, changes: dict) -> int:
        return len(filePaths)

    @pyqtSlot(result="QVariantMap")
    def firstPlayableTrack(self) -> dict:
        return self._tracks[0] if self._tracks else {}

    @pyqtSlot(result="QVariantList")
    def playbackTracks(self) -> list:
        return self._tracks

    @pyqtSlot("QVariantMap", "QStringList", int, result="QVariantList")
    def similarTracks(self, seed: dict, excludePaths: list, limit: int) -> list:
        ex = set(excludePaths)
        return [t for t in self._tracks if t.get("filePath") not in ex][:limit]

    @pyqtSlot(result="QVariantMap")
    def catalogGroups(self) -> dict:
        art_map = {}
        alb_map = {}
        gen_map = {}
        fmt_map = {}

        for t in self._tracks:
            art = t.get("artist", "Unknown Artist")
            alb = t.get("album", "Unknown Album")
            gen = t.get("genre", "Soundtrack")
            fmt = t.get("format", "MP3")

            art_map[art] = art_map.get(art, 0) + 1
            alb_map[alb] = alb_map.get(alb, 0) + 1
            gen_map[gen] = gen_map.get(gen, 0) + 1
            fmt_map[fmt] = fmt_map.get(fmt, 0) + 1

        artists = [{"name": k, "count": v, "track": next((t for t in self._tracks if t.get("artist") == k), {})} for k, v in art_map.items()]
        albums = [{"name": k, "count": v, "track": next((t for t in self._tracks if t.get("album") == k), {})} for k, v in alb_map.items()]
        genres = [{"name": k, "count": v, "track": next((t for t in self._tracks if t.get("genre") == k), {})} for k, v in gen_map.items()]

        return {
            "artists": artists,
            "albums": albums,
            "genres": genres,
            "formats": fmt_map
        }

    @pyqtSlot(result="QVariantList")
    def visibleTracks(self) -> list:
        return self._visible_tracks

    @pyqtSlot(str, str, "QVariantMap", str, bool, "QVariantList", bool)
    def setLibraryFilter(self, query: str, filter_mode: str, favorites: dict,
                           sortMetric: str, ascending: bool, excludedFolders: list, ignoreShortClips: bool):
        q = query.strip().lower()
        res = []
        for t in self._tracks:
            if q and q not in t.get("title", "").lower() and q not in t.get("artist", "").lower():
                continue
            res.append(t)
        self.beginResetModel()
        self._visible_tracks = res
        self.endResetModel()
        self.visibleTracksChanged.emit()

    @pyqtSlot(str, str, "QVariantList", bool)
    def setSearchFilter(self, query: str, format_str: str, excludedFolders: list, ignoreShortClips: bool):
        q = query.strip().lower()
        res = []
        for t in self._tracks:
            if q and q not in t.get("title", "").lower() and q not in t.get("artist", "").lower():
                continue
            if format_str and format_str != "ALL" and t.get("format") != format_str:
                continue
            res.append(t)
        self.beginResetModel()
        self._visible_tracks = res
        self.endResetModel()
        self.visibleTracksChanged.emit()

    @pyqtSlot(str, result="QVariantList")
    def parseM3u(self, filePath: str) -> list:
        return []


class PlayerBridge(QObject):
    playbackRequested = pyqtSignal("QVariantList", int)
    currentTrackChanged = pyqtSignal()
    currentLyricsChanged = pyqtSignal()
    isPlayingChanged = pyqtSignal()
    positionChanged = pyqtSignal()
    durationChanged = pyqtSignal()
    volumeChanged = pyqtSignal()
    shuffleEnabledChanged = pyqtSignal()
    audioLevelChanged = pyqtSignal()
    audioMeterEnabledChanged = pyqtSignal()
    audioOutputsChanged = pyqtSignal()
    audioDeviceChanged = pyqtSignal()
    errorChanged = pyqtSignal()
    replayGainModeChanged = pyqtSignal()
    equalizerChanged = pyqtSignal()
    crossfadeMsChanged = pyqtSignal()
    trackEnded = pyqtSignal()
    crossfadeReady = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._player = QMediaPlayer(self)
        self._audio_output = QAudioOutput(self)
        self._player.setAudioOutput(self._audio_output)

        self._current_track: Dict[str, Any] = {}
        self._current_lyrics: str = ""
        self._is_playing: bool = False
        self._position: int = 0
        self._duration: int = 0
        self._volume: float = 0.85
        self._shuffle: bool = False
        self._error: str = ""
        self._audio_format: Dict[str, Any] = {}
        self._equalizer: Dict[str, Any] = {"enabled": False, "preset": "Flat", "preamp": 0.0, "bands": [0.0]*10}

        self._audio_output.setVolume(self._volume)
        self._player.playbackStateChanged.connect(self._on_state_changed)
        self._player.positionChanged.connect(self._on_pos_changed)
        self._player.durationChanged.connect(self._on_dur_changed)

    def _on_state_changed(self, state):
        playing = (state == QMediaPlayer.PlaybackState.PlayingState)
        if self._is_playing != playing:
            self._is_playing = playing
            self.isPlayingChanged.emit()

    def _on_pos_changed(self, pos):
        self._position = pos
        self.positionChanged.emit()

    def _on_dur_changed(self, dur):
        self._duration = dur
        self.durationChanged.emit()

    @pyqtProperty("QVariantMap", notify=currentTrackChanged)
    def currentTrack(self) -> dict:
        return self._current_track

    @pyqtProperty("QVariantMap", notify=currentTrackChanged)
    def audioFormat(self) -> dict:
        return self._audio_format

    @pyqtProperty(str, notify=currentLyricsChanged)
    def currentLyrics(self) -> str:
        return self._current_lyrics

    @pyqtProperty(bool, notify=isPlayingChanged)
    def isPlaying(self) -> bool:
        return self._is_playing

    @pyqtProperty(bool, notify=shuffleEnabledChanged)
    def shuffleEnabled(self) -> bool:
        return self._shuffle

    @pyqtProperty(float, notify=audioLevelChanged)
    def audioLevel(self) -> float:
        return 0.5 if self._is_playing else 0.0

    @pyqtProperty(bool, notify=audioMeterEnabledChanged)
    def audioMeterEnabled(self) -> bool:
        return False

    @audioMeterEnabled.setter
    def audioMeterEnabled(self, enabled: bool):
        pass

    @pyqtProperty(int, notify=positionChanged)
    def position(self) -> int:
        return self._position

    @pyqtProperty(int, notify=durationChanged)
    def duration(self) -> int:
        return self._duration

    @pyqtProperty(str, notify=positionChanged)
    def formattedPosition(self) -> str:
        sec = self._position // 1000
        return f"{sec // 60}:{sec % 60:02d}"

    @pyqtProperty(str, notify=durationChanged)
    def formattedDuration(self) -> str:
        sec = self._duration // 1000
        return f"{sec // 60}:{sec % 60:02d}"

    @pyqtProperty(float, notify=volumeChanged)
    def volume(self) -> float:
        return self._volume

    @pyqtProperty("QVariantList", notify=audioOutputsChanged)
    def audioOutputs(self) -> list:
        return [{"id": "default", "name": "Default Audio Device"}]

    @pyqtProperty(str, notify=audioDeviceChanged)
    def audioDeviceId(self) -> str:
        return "default"

    @pyqtProperty(str, notify=errorChanged)
    def error(self) -> str:
        return self._error

    @pyqtProperty(str, notify=replayGainModeChanged)
    def replayGainMode(self) -> str:
        return "off"

    @replayGainMode.setter
    def replayGainMode(self, mode: str):
        self.replayGainModeChanged.emit()

    @pyqtProperty(int, notify=crossfadeMsChanged)
    def crossfadeMs(self) -> int:
        return 0

    @crossfadeMs.setter
    def crossfadeMs(self, ms: int):
        self.crossfadeMsChanged.emit()

    @pyqtProperty("QVariantMap", notify=equalizerChanged)
    def equalizer(self) -> dict:
        return self._equalizer

    @pyqtSlot(str, result=str)
    def getLyrics(self, filePath: str) -> str:
        lrc = os.path.splitext(filePath)[0] + ".lrc"
        if os.path.exists(lrc):
            try:
                with open(lrc, "r", encoding="utf-8") as f:
                    return f.read()
            except Exception:
                pass
        return ""

    @pyqtSlot(str)
    def setCurrentLyrics(self, lyrics: str):
        self._current_lyrics = lyrics
        self.currentLyricsChanged.emit()

    @pyqtSlot(bool)
    def setShuffleEnabled(self, enabled: bool):
        self._shuffle = enabled
        self.shuffleEnabledChanged.emit()

    @pyqtSlot()
    def toggleShuffle(self):
        self._shuffle = not self._shuffle
        self.shuffleEnabledChanged.emit()

    @pyqtSlot(float)
    def setVolume(self, vol: float):
        self._volume = max(0.0, min(1.0, vol))
        self._audio_output.setVolume(self._volume)
        self.volumeChanged.emit()

    @pyqtSlot(str)
    def setReplayGainMode(self, mode: str):
        pass

    @pyqtSlot("QVariantMap")
    def setEqualizer(self, settings: dict):
        self._equalizer = settings
        self.equalizerChanged.emit()

    @pyqtSlot(str, result=bool)
    def setAudioDevice(self, dev_id: str) -> bool:
        return True

    @pyqtSlot("QVariantMap")
    @pyqtSlot("QVariantMap", int)
    def restoreTrack(self, track: dict, positionMs: int = 0):
        self._current_track = track
        self.currentTrackChanged.emit()
        if positionMs > 0:
            self._player.setPosition(positionMs)

    @pyqtSlot("QVariantMap", result=bool)
    def playTrack(self, track: dict) -> bool:
        self._current_track = track
        self.currentTrackChanged.emit()
        path = track.get("filePath", "")
        if path and os.path.exists(path):
            self._player.setSource(QUrl.fromLocalFile(path))
            self._player.play()
            self._current_lyrics = self.getLyrics(path)
            self.currentLyricsChanged.emit()
            return True
        return False

    @pyqtSlot()
    def togglePlay(self):
        if self._is_playing:
            self._player.pause()
        else:
            self._player.play()

    @pyqtSlot()
    def play(self):
        self._player.play()

    @pyqtSlot()
    def pause(self):
        self._player.pause()

    @pyqtSlot()
    def stop(self):
        self._player.stop()

    @pyqtSlot(int)
    def seek(self, positionMs: int):
        self._player.setPosition(positionMs)

    @pyqtSlot("QObject*", bool)
    def setWindowAlwaysOnTop(self, win, onTop: bool):
        pass

    @pyqtSlot(str)
    def updateCurrentTrackArtwork(self, artworkPath: str):
        self._current_track["artworkUrl"] = artworkPath
        self.currentTrackChanged.emit()

    @pyqtSlot("QVariantMap")
    def updateCurrentTrackMetadata(self, track: dict):
        self._current_track = track
        self.currentTrackChanged.emit()

    @pyqtSlot("QVariantList")
    @pyqtSlot("QVariantList", int)
    def requestPlayback(self, tracks: list, startIndex: int = 0):
        if not tracks or startIndex >= len(tracks):
            return
        track = tracks[startIndex]
        self.playTrack(track)
        self.playbackRequested.emit(tracks, startIndex)


class ServicesBridge(QObject):
    lyricsFetched = pyqtSignal(str, str, str, str)
    lyricsSearchResultsReady = pyqtSignal("QVariantList")
    coverSearchResultsReady = pyqtSignal("QVariantList")
    coverSearchFailed = pyqtSignal(str)
    coverApplied = pyqtSignal(str, str, str, str)
    radioStationsLoaded = pyqtSignal("QVariantList")
    artistBioLoaded = pyqtSignal(str, str)
    albumBioLoaded = pyqtSignal(str, str)
    artistImageLoaded = pyqtSignal(str, str)
    listenBrainzValidationFinished = pyqtSignal(bool, str, str)
    scrobbleAccountAuthFinished = pyqtSignal(str, bool, str, str)
    updateCheckFinished = pyqtSignal(bool, str, str, str, bool)
    updateCheckFailed = pyqtSignal(str, bool)

    def __init__(self, parent=None):
        super().__init__(parent)

    @pyqtSlot(str, result=str)
    def getArtistImage(self, artist: str) -> str:
        return ""

    @pyqtSlot(str, result=str)
    def localLyricsFor(self, filePath: str) -> str:
        lrc = os.path.splitext(filePath)[0] + ".lrc"
        if os.path.exists(lrc):
            try:
                with open(lrc, "r", encoding="utf-8") as f:
                    return f.read()
            except Exception:
                pass
        return ""

    @pyqtSlot(str, str, str, str, str, str)
    def cacheLyrics(self, title: str, artist: str, album: str, synced: str, plain: str, provider: str):
        pass

    @pyqtSlot(str, str, str, int)
    def fetchLyrics(self, title: str, artist: str, album: str, durationSeconds: int):
        # Fetch from LRCLIB asynchronously
        def _fetch():
            import requests
            try:
                url = f"https://lrclib.net/api/get?track_name={requests.utils.quote(title)}&artist_name={requests.utils.quote(artist)}"
                resp = requests.get(url, timeout=5)
                if resp.ok:
                    data = resp.json()
                    lyrics = data.get("syncedLyrics") or data.get("plainLyrics", "")
                    if lyrics:
                        self.lyricsFetched.emit(title, artist, lyrics, "LRCLIB")
            except Exception:
                pass
        QTimer.singleShot(10, _fetch)

    @pyqtSlot(str, str)
    def searchLyrics(self, title: str, artist: str):
        self.fetchLyrics(title, artist, "", 0)

    @pyqtSlot()
    @pyqtSlot(str)
    @pyqtSlot(str, str)
    @pyqtSlot(str, str, str)
    @pyqtSlot(str, str, str, str)
    @pyqtSlot(str, str, str, str, str)
    @pyqtSlot(str, str, str, str, str, bool)
    def fetchRadioStations(self, searchQuery="", country="", language="", tag="", sort="votes", reverse=True):
        pass

    @pyqtSlot()
    def cancelRadioRequests(self):
        pass

    @pyqtSlot()
    def cancelNetworkRequests(self):
        pass

    @pyqtSlot(bool)
    def setBlackoutEnabled(self, enabled: bool):
        pass

    @pyqtSlot(str)
    def fetchArtistBio(self, artist: str):
        pass

    @pyqtSlot(str, str)
    def fetchAlbumBio(self, album: str, artist: str):
        pass

    @pyqtSlot(str)
    def fetchArtistImage(self, artist: str):
        pass

    @pyqtSlot(str)
    def openExternalUrl(self, url: str):
        import webbrowser
        webbrowser.open(url)

    @pyqtSlot(str)
    def validateListenBrainzToken(self, token: str):
        pass

    @pyqtSlot(str, str, str)
    def authenticateScrobbleAccount(self, service: str, u: str, p: str):
        pass

    @pyqtSlot("QVariantMap")
    def scrobbleNowPlaying(self, track: dict):
        pass

    @pyqtSlot("QVariantMap", int)
    def scrobbleTrack(self, track: dict, timestampSec: int):
        pass

    @pyqtSlot(str, str)
    def saveListenBrainzSession(self, token: str, user: str):
        pass

    @pyqtSlot()
    def disconnectListenBrainz(self):
        pass

    @pyqtSlot(str)
    def disconnectScrobbleAccount(self, service: str):
        pass

    @pyqtSlot(result=bool)
    def hasListenBrainzSession(self) -> bool:
        return False

    @pyqtSlot(str, result=bool)
    def hasScrobbleSession(self, service: str) -> bool:
        return False

    @pyqtSlot(result=bool)
    def lastFmAvailable(self) -> bool:
        return False

    @pyqtSlot(str)
    @pyqtSlot(str, str)
    def searchAlbumCovers(self, album: str, artist: str = ""):
        pass

    @pyqtSlot(str, str, str)
    @pyqtSlot(str, str, str, str)
    def applyAlbumCover(self, album: str, artist: str, imageUrl: str, filePath: str = ""):
        pass

    @pyqtSlot()
    @pyqtSlot(bool)
    def checkForUpdates(self, manual: bool = False):
        pass

    @pyqtSlot(str, result="QStringList")
    def releaseNotes(self, version: str) -> List[str]:
        return []


class StreamingBridge(QObject):
    serverConnected = pyqtSignal(str, str)
    serverFailed = pyqtSignal(str, str)
    remoteTracksChanged = pyqtSignal()
    statusChanged = pyqtSignal()
    remoteArtChanged = pyqtSignal()
    remoteLibraryLoadingChanged = pyqtSignal()
    jellyfinQuickConnectChanged = pyqtSignal()
    jellyfinLyricsFetched = pyqtSignal(str, str, str)

    def __init__(self, parent=None):
        super().__init__(parent)

    @pyqtProperty(bool, notify=statusChanged)
    def subsonicConnected(self) -> bool:
        return False

    @pyqtProperty(bool, notify=statusChanged)
    def jellyfinConnected(self) -> bool:
        return False

    @pyqtProperty(str, notify=statusChanged)
    def subsonicStatus(self) -> str:
        return ""

    @pyqtProperty(str, notify=statusChanged)
    def jellyfinStatus(self) -> str:
        return ""

    @pyqtProperty(bool, notify=jellyfinQuickConnectChanged)
    def jellyfinQuickConnecting(self) -> bool:
        return False

    @pyqtProperty(str, notify=jellyfinQuickConnectChanged)
    def jellyfinQuickConnectCode(self) -> str:
        return ""

    @pyqtProperty(bool, notify=remoteLibraryLoadingChanged)
    def remoteLibraryLoading(self) -> bool:
        return False

    @pyqtProperty("QVariantList", notify=remoteTracksChanged)
    def remoteTracks(self) -> list:
        return []

    @pyqtProperty(int, notify=remoteArtChanged)
    def remoteArtRevision(self) -> int:
        return 0

    @pyqtSlot(result="QVariantMap")
    def serverConfigSnapshot(self) -> dict:
        return {}

    @pyqtSlot(str, result=str)
    def remoteArtwork(self, path: str) -> str:
        return ""

    @pyqtSlot()
    def refreshLibrary(self):
        pass

    @pyqtSlot(bool)
    def setBlackoutEnabled(self, enabled: bool):
        pass

    @pyqtSlot("QVariantMap")
    def fetchJellyfinLyrics(self, track: dict):
        pass


class WindowFrameBridge(QObject):
    maximizeClicked = pyqtSignal()
    maximizeHoveredChanged = pyqtSignal()
    maximizedMarginChanged = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

    @pyqtProperty(bool, notify=maximizeHoveredChanged)
    def maximizeHovered(self) -> bool:
        return False

    @pyqtProperty(float, notify=maximizedMarginChanged)
    def maximizedMargin(self) -> float:
        return 0.0

    @pyqtSlot("QObject*")
    def setMaximizeButton(self, btn):
        pass


class TrayBridge(QObject):
    showRequested = pyqtSignal()
    playPauseRequested = pyqtSignal()
    nextRequested = pyqtSignal()
    previousRequested = pyqtSignal()
    quitRequested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

    @pyqtProperty(bool, constant=True)
    def available(self) -> bool:
        return True

    @pyqtSlot(result=bool)
    def available(self) -> bool:
        return True

    @pyqtSlot()
    def notifyHidden(self):
        pass

    @pyqtSlot()
    def releaseMemory(self):
        pass

    @pyqtSlot(bool)
    def setPlaying(self, playing: bool):
        pass

    @pyqtSlot("QVariantMap")
    @pyqtSlot(str, str)
    def setTrack(self, *args):
        pass

    @pyqtSlot(str, str)
    def showNotification(self, title: str, msg: str):
        pass


class PhoneRemoteBridge(QObject):
    enabledChanged = pyqtSignal()
    codeChanged = pyqtSignal()
    pairedPhonesChanged = pyqtSignal()
    addressChanged = pyqtSignal()
    controllerChanged = pyqtSignal()
    phonePlaybackChanged = pyqtSignal()
    favoritePathsChanged = pyqtSignal()
    pairingRequestChanged = pyqtSignal()
    playRequested = pyqtSignal()
    pauseRequested = pyqtSignal()
    nextRequested = pyqtSignal()
    previousRequested = pyqtSignal()
    shuffleToggleRequested = pyqtSignal()
    repeatCycleRequested = pyqtSignal()
    volumeRequested = pyqtSignal(float)
    seekRequested = pyqtSignal(int)
    queueTrackRequested = pyqtSignal(int)
    queueMoveRequested = pyqtSignal(int, int)
    queueRemoveRequested = pyqtSignal(int)
    handoffRequested = pyqtSignal("QVariantList", int, int, bool)
    playlistReceived = pyqtSignal("QVariantMap")
    likesChangeRequested = pyqtSignal("QStringList")
    playNextRequested = pyqtSignal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._enabled = False
        self._code = ""
        self._paired_phones = []
        self._controller_name = ""
        self._favorite_paths = []
        self._playlists = []
        self._up_next = []
        self._repeat_mode = 0
        self._phone_playback = {}
        self._pairing_request = ""

    @pyqtProperty(bool, notify=enabledChanged)
    def enabled(self) -> bool:
        return self._enabled

    @enabled.setter
    def enabled(self, val: bool):
        self._enabled = val
        self.enabledChanged.emit()

    @pyqtProperty(str, notify=codeChanged)
    def code(self) -> str:
        return self._code

    @code.setter
    def code(self, val: str):
        self._code = val
        self.codeChanged.emit()

    @pyqtProperty("QVariantList", notify=pairedPhonesChanged)
    def pairedPhones(self) -> list:
        return self._paired_phones

    @pairedPhones.setter
    def pairedPhones(self, val: list):
        self._paired_phones = val
        self.pairedPhonesChanged.emit()

    @pyqtProperty(str, notify=addressChanged)
    def address(self) -> str:
        return ""

    @pyqtProperty(str, constant=True)
    def computerName(self) -> str:
        return "CassetteCat"

    @pyqtProperty(str, notify=controllerChanged)
    def controllerName(self) -> str:
        return self._controller_name

    @pyqtProperty("QVariantMap", notify=phonePlaybackChanged)
    def phonePlayback(self) -> dict:
        return self._phone_playback

    @pyqtProperty(int)
    def repeatMode(self) -> int:
        return self._repeat_mode

    @repeatMode.setter
    def repeatMode(self, val: int):
        self._repeat_mode = val

    @pyqtProperty("QVariantList")
    def upNext(self) -> list:
        return self._up_next

    @upNext.setter
    def upNext(self, val: list):
        self._up_next = val

    @pyqtProperty("QStringList", notify=favoritePathsChanged)
    def favoritePaths(self) -> list:
        return self._favorite_paths

    @favoritePaths.setter
    def favoritePaths(self, val: list):
        self._favorite_paths = val
        self.favoritePathsChanged.emit()

    @pyqtProperty("QVariantList")
    def playlists(self) -> list:
        return self._playlists

    @playlists.setter
    def playlists(self, val: list):
        self._playlists = val

    @pyqtProperty(str, notify=pairingRequestChanged)
    def pairingRequest(self) -> str:
        return self._pairing_request

    @pyqtSlot(bool)
    def answerPairing(self, accept: bool):
        pass

    @pyqtSlot(str)
    def sendToPhone(self, cmd: str):
        pass

    @pyqtSlot(str)
    def unpairPhone(self, code: str):
        pass

    @pyqtSlot()
    def regenerateCode(self):
        pass

    @pyqtSlot()
    def continueOnPhone(self):
        pass

    @pyqtSlot()
    def requestSync(self):
        pass

    @pyqtSlot(str, str)
    def playNextOnPhone(self, title: str, artist: str):
        pass


class GlobalShortcutsBridge(QObject):
    enabledChanged = pyqtSignal()
    statusChanged = pyqtSignal()
    shortcutsChanged = pyqtSignal()
    playPauseRequested = pyqtSignal()
    nextRequested = pyqtSignal()
    previousRequested = pyqtSignal()
    favoriteRequested = pyqtSignal()
    searchRequested = pyqtSignal()
    miniPlayerRequested = pyqtSignal()
    accessHintsRequested = pyqtSignal(bool)
    accessKeyRequested = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._enabled = False

    @pyqtProperty(bool, constant=True)
    def supported(self) -> bool:
        return True

    @pyqtProperty(bool, notify=enabledChanged)
    def enabled(self) -> bool:
        return self._enabled

    @enabled.setter
    def enabled(self, val: bool):
        self._enabled = val
        self.enabledChanged.emit()

    @pyqtProperty(str, notify=statusChanged)
    def status(self) -> str:
        return "Ready"

    @pyqtProperty("QVariantMap", notify=shortcutsChanged)
    def shortcuts(self) -> dict:
        return {}

    @pyqtSlot(bool)
    def setEnabled(self, enabled: bool):
        self.enabled = enabled

    @pyqtSlot(str, str, result=bool)
    def setShortcut(self, action: str, shortcut: str) -> bool:
        return True


class MprisBridge(QObject):
    playRequested = pyqtSignal()
    pauseRequested = pyqtSignal()
    playPauseRequested = pyqtSignal()
    nextRequested = pyqtSignal()
    previousRequested = pyqtSignal()
    seekRequested = pyqtSignal(int)
    raiseRequested = pyqtSignal()
    quitRequested = pyqtSignal()
    openUriRequested = pyqtSignal(str)
    repeatModeChanged = pyqtSignal(int)
    volumeRequested = pyqtSignal(float)
    shuffleRequested = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._repeat_mode = 0

    @pyqtProperty(int, notify=repeatModeChanged)
    def repeatMode(self) -> int:
        return self._repeat_mode

    @repeatMode.setter
    def repeatMode(self, mode: int):
        self._repeat_mode = mode
        self.repeatModeChanged.emit(mode)


class SmtcBridge(QObject):
    playRequested = pyqtSignal()
    pauseRequested = pyqtSignal()
    playPauseRequested = pyqtSignal()
    nextRequested = pyqtSignal()
    previousRequested = pyqtSignal()
    seekRequested = pyqtSignal(int)
    quitRequested = pyqtSignal()
    shuffleRequested = pyqtSignal(bool)
    repeatModeChanged = pyqtSignal(int)
    volumeRequested = pyqtSignal(float)

    def __init__(self, parent=None):
        super().__init__(parent)


class DiscordBridge(QObject):
    enabledChanged = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._enabled = False

    @pyqtProperty(bool, notify=enabledChanged)
    def enabled(self) -> bool:
        return self._enabled

    @enabled.setter
    def enabled(self, val: bool):
        self._enabled = val
        self.enabledChanged.emit()


class SearchWorker(QThread):
    finished = pyqtSignal(list)
    failed = pyqtSignal(str)

    def __init__(self, query: str, service: str = "all"):
        super().__init__()
        self.query = query.strip()
        self.service = service

    def run(self):
        try:
            if not self.query:
                self.finished.emit([])
                return
            result = MetadataResolver.resolve(self.query, self.service)
            if result.get("success"):
                tracks = result.get("tracks", [])
                config = AppConfig.get_instance()
                dl_dir = config.get("download_dir", os.path.expanduser("~/Music/GrabSongs"))
                for t in tracks:
                    expected_name = f"{t.get('artist', '')} - {t.get('title', '')}.mp3"
                    t["downloaded"] = os.path.exists(os.path.join(dl_dir, expected_name))
                self.finished.emit(tracks)
            else:
                self.failed.emit(result.get("error", "No tracks found."))
        except Exception as e:
            self.failed.emit(str(e))


class DownloaderBridge(QObject):
    searchStarted = pyqtSignal()
    searchFinished = pyqtSignal("QVariantList")
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

    def __init__(self, library_bridge: Optional[LibraryBridge] = None, parent=None):
        super().__init__(parent)
        self.library = library_bridge
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

        # Optional audio preview player
        try:
            from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
            self._player = QMediaPlayer(self)
            self._audio_output = QAudioOutput(self)
            self._player.setAudioOutput(self._audio_output)
            self._audio_output.setVolume(1.0)
            self._player.playbackStateChanged.connect(self._on_playback_state_changed)
            self._player.positionChanged.connect(self._on_pos_changed)
            self._player.durationChanged.connect(self._on_dur_changed)
        except Exception:
            self._player = None

    def _on_pos_changed(self, pos):
        self._position = pos
        self.positionChanged.emit(pos)

    def _on_dur_changed(self, dur):
        self._duration = dur
        self.durationChanged.emit(dur)

    def _on_playback_state_changed(self):
        if self._player:
            from PyQt6.QtMultimedia import QMediaPlayer
            self._preview_playing = (self._player.playbackState() == QMediaPlayer.PlaybackState.PlayingState)
            self.previewStateChanged.emit()

    def _on_progress(self, job_id, percent, speed, eta, status):
        self.jobProgress.emit(job_id, percent, speed, eta)

    def _on_finished(self, job_id, file_path, meta):
        self.jobFinished.emit(job_id, True, file_path)
        if self.library:
            self.library.refreshLibrary()
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
        self._is_searching = True
        self.isSearchingChanged.emit()
        self.searchStarted.emit()
        self._active_worker = SearchWorker(query, service)
        
        def _on_done(tracks):
            self._is_searching = False
            self.isSearchingChanged.emit()
            self.searchFinished.emit(tracks)

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

    @pyqtSlot()
    def openDownloadFolder(self):
        d = self.downloadDirectory
        os.makedirs(d, exist_ok=True)
        if sys.platform == "win32":
            os.startfile(d)

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
                "eta": str(j.get("eta", ""))
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
                        # Extract artist - title from name
                        name_no_ext = os.path.splitext(f)[0]
                        artist = ""
                        title = name_no_ext
                        if " - " in name_no_ext:
                            parts = name_no_ext.split(" - ", 1)
                            artist = parts[0].strip()
                            title = parts[1].strip()

                        size_mb = f"{stat.st_size / (1024 * 1024):.1f} MB"
                        items.append({
                            "title": title,
                            "artist": artist,
                            "filename": f,
                            "path": full_path,
                            "size": size_mb,
                            "modified": stat.st_mtime
                        })
            items.sort(key=lambda x: x["modified"], reverse=True)
        except Exception as e:
            print("Error scanning downloaded files:", e)
        return items

    @pyqtSlot(str)
    def openFile(self, path: str):
        if os.path.exists(path) and sys.platform == "win32":
            os.startfile(path)

    @pyqtSlot(str)
    def revealFileInExplorer(self, path: str):
        if os.path.exists(path) and sys.platform == "win32":
            import subprocess
            subprocess.run(["explorer", f"/select,{os.path.normpath(path)}"])

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
    def togglePreview(self, path: str):
        if not self._player:
            return
        from PyQt6.QtMultimedia import QMediaPlayer
        if self._preview_playing and self._preview_path == path:
            self._player.stop()
            self._preview_playing = False
            self.previewStateChanged.emit()
        else:
            self._preview_path = path
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
            self._player.setSource(QUrl.fromLocalFile(path))
            self._player.play()
            self._preview_playing = True
            self.previewStateChanged.emit()

    @pyqtSlot()
    def togglePlayPause(self):
        if not self._player:
            return
        from PyQt6.QtMultimedia import QMediaPlayer
        if self._preview_playing:
            self._player.pause()
            self._preview_playing = False
            self.previewStateChanged.emit()
        else:
            if self._preview_path and os.path.exists(self._preview_path):
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

    @pyqtSlot(str)
    def cancelJob(self, job_id: str):
        self.queue_manager.cancel_job(job_id)


