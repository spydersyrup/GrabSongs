import os
from PyQt6.QtCore import QObject, pyqtSignal, QUrl
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput

class PreviewPlayer(QObject):
    state_changed = pyqtSignal(bool)           # is_playing
    position_changed = pyqtSignal(int, int)    # current_ms, total_ms
    track_loaded = pyqtSignal(str, str, str)   # title, artist, file_path

    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = PreviewPlayer()
        return cls._instance

    def __init__(self, parent=None):
        super().__init__(parent)
        self.player = QMediaPlayer(self)
        self.audio_output = QAudioOutput(self)
        self.player.setAudioOutput(self.audio_output)
        self.audio_output.setVolume(0.85)

        self.current_title = ""
        self.current_artist = ""
        self.current_path = ""

        self.player.playbackStateChanged.connect(self._on_state_changed)
        self.player.positionChanged.connect(self._on_pos_changed)
        self.player.durationChanged.connect(self._on_duration_changed)

    def play_file(self, file_path: str, title: str = "", artist: str = ""):
        if not os.path.exists(file_path):
            return
        self.current_path = file_path
        self.current_title = title or os.path.basename(file_path)
        self.current_artist = artist
        self.player.setSource(QUrl.fromLocalFile(file_path))
        self.player.play()
        self.track_loaded.emit(self.current_title, self.current_artist, self.current_path)

    def toggle_play(self):
        if self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.player.pause()
        elif self.player.playbackState() == QMediaPlayer.PlaybackState.PausedState:
            self.player.play()
        elif self.current_path and os.path.exists(self.current_path):
            self.play_file(self.current_path, self.current_title, self.current_artist)

    def pause(self):
        self.player.pause()

    def stop(self):
        self.player.stop()

    def seek(self, position_ms: int):
        self.player.setPosition(position_ms)

    def set_volume(self, volume_float: float): # 0.0 to 1.0
        self.audio_output.setVolume(volume_float)

    def is_playing(self) -> bool:
        return self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState

    def _on_state_changed(self, state):
        self.state_changed.emit(state == QMediaPlayer.PlaybackState.PlayingState)

    def _on_pos_changed(self, pos):
        self.position_changed.emit(pos, self.player.duration())

    def _on_duration_changed(self, duration):
        self.position_changed.emit(self.player.position(), duration)
