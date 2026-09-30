"""Decoupled Audio Playback Engine and Playlist State Machine.

Provides cross-platform track queue management, volume control, progress
tracking, and pluggable audio driver backends (supporting Mock driver for headless
testing and subprocess driver for interactive playback).
"""

import os
import subprocess
from enum import Enum, auto
from pathlib import Path


class PlaybackState(Enum):
    STOPPED = auto()
    PLAYING = auto()
    PAUSED = auto()


class AudioDriver:
    """Base interface for audio output backends."""

    def play(self, file_path: str, volume: float) -> bool:
        raise NotImplementedError

    def pause(self) -> bool:
        raise NotImplementedError

    def stop(self) -> bool:
        raise NotImplementedError

    def set_volume(self, volume: float) -> None:
        pass


class MockAudioDriver(AudioDriver):
    """Headless driver for automated testing and CI environments."""

    def __init__(self):
        self.is_playing = False
        self.is_paused = False
        self.current_file: str | None = None
        self.volume: float = 0.5

    def play(self, file_path: str, volume: float) -> bool:
        self.current_file = file_path
        self.volume = volume
        self.is_playing = True
        self.is_paused = False
        return True

    def pause(self) -> bool:
        if self.is_playing:
            self.is_playing = False
            self.is_paused = True
            return True
        return False

    def stop(self) -> bool:
        self.is_playing = False
        self.is_paused = False
        return True

    def set_volume(self, volume: float) -> None:
        self.volume = max(0.0, min(1.0, volume))


class SubprocessAudioDriver(AudioDriver):
    """Subprocess audio playback using ffplay with volume scaling."""

    def __init__(self):
        self.process: subprocess.Popen | None = None
        self.current_file: str | None = None
        self.volume: float = 0.5

    def play(self, file_path: str, volume: float) -> bool:
        self.stop()
        self.current_file = file_path
        self.volume = volume

        # ffplay volume flag is 0 to 100
        vol_pct = int(self.volume * 100)
        try:
            self.process = subprocess.Popen(
                [
                    "ffplay",
                    "-nodisp",
                    "-autoexit",
                    "-volume",
                    str(vol_pct),
                    "-v",
                    "error",
                    file_path,
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return True
        except FileNotFoundError:
            return False

    def pause(self) -> bool:
        # ffplay does not have interactive stdin pause without complex terminal handling
        # so pause halts playback
        return self.stop()

    def stop(self) -> bool:
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=1.0)
            except (subprocess.TimeoutExpired, OSError):
                self.process.kill()
            finally:
                self.process = None
        return True

    def set_volume(self, volume: float) -> None:
        self.volume = max(0.0, min(1.0, volume))


class AudioEngine:
    """Manages playlist state, playback lifecycle, volume, and progress."""

    def __init__(self, driver: AudioDriver | None = None):
        self.driver = driver if driver is not None else MockAudioDriver()
        self.playlist: list[str] = []
        self.current_index: int = 0
        self.state = PlaybackState.STOPPED
        self.volume: float = 0.5
        self.simulated_duration: float = 180.0  # 3:00 default duration
        self.simulated_position: float = 0.0

    @property
    def current_track(self) -> str | None:
        """Return the absolute path of the currently selected track."""
        if 0 <= self.current_index < len(self.playlist):
            return self.playlist[self.current_index]
        return None

    @property
    def current_track_name(self) -> str:
        """Return the basename of the current track or a placeholder."""
        track = self.current_track
        return os.path.basename(track) if track else "No track loaded"

    def load_playlist(self, track_paths: list[str]) -> int:
        """Set the playlist with valid audio file paths."""
        valid_extensions = {".mp3", ".wav", ".ogg", ".flac", ".m4a"}
        self.playlist = [
            p for p in track_paths if Path(p).suffix.lower() in valid_extensions
        ]
        self.current_index = 0
        self.state = PlaybackState.STOPPED
        self.simulated_position = 0.0
        return len(self.playlist)

    def add_track(self, track_path: str) -> bool:
        """Append a track to the active playlist."""
        valid_extensions = {".mp3", ".wav", ".ogg", ".flac", ".m4a"}
        if Path(track_path).suffix.lower() in valid_extensions:
            self.playlist.append(track_path)
            return True
        return False

    def play(self) -> bool:
        """Start playback of the active track."""
        track = self.current_track
        if not track:
            return False

        success = self.driver.play(track, self.volume)
        if success:
            self.state = PlaybackState.PLAYING
        return success

    def pause(self) -> bool:
        """Pause the current playback."""
        if self.state == PlaybackState.PLAYING:
            self.driver.pause()
            self.state = PlaybackState.PAUSED
            return True
        return False

    def stop(self) -> bool:
        """Stop playback and rewind position."""
        self.driver.stop()
        self.state = PlaybackState.STOPPED
        self.simulated_position = 0.0
        return True

    def next_track(self) -> bool:
        """Advance to the next track in the playlist."""
        if not self.playlist:
            return False
        if self.current_index < len(self.playlist) - 1:
            self.current_index += 1
            if self.state == PlaybackState.PLAYING:
                return self.play()
            return True
        return False

    def previous_track(self) -> bool:
        """Move to the previous track in the playlist."""
        if not self.playlist:
            return False
        if self.current_index > 0:
            self.current_index -= 1
            if self.state == PlaybackState.PLAYING:
                return self.play()
            return True
        return False

    def set_volume(self, value: float) -> float:
        """Adjust volume level clamped between 0.0 and 1.0."""
        self.volume = max(0.0, min(1.0, value))
        self.driver.set_volume(self.volume)
        return self.volume

    def update_position(self, delta_seconds: float) -> float:
        """Simulate playback progress advancement."""
        if self.state == PlaybackState.PLAYING:
            self.simulated_position = min(
                self.simulated_duration, self.simulated_position + delta_seconds
            )
            if self.simulated_position >= self.simulated_duration:
                # Track ended, auto advance
                if not self.next_track():
                    self.stop()
        return self.simulated_position

    def get_progress_percentage(self) -> float:
        """Return the current playback progress as a percentage (0.0 to 100.0)."""
        if self.simulated_duration <= 0:
            return 0.0
        return (self.simulated_position / self.simulated_duration) * 100.0

    @staticmethod
    def format_time(seconds: float) -> str:
        """Format seconds into MM:SS string representation."""
        total_seconds = int(max(0, seconds))
        mins = total_seconds // 60
        secs = total_seconds % 60
        return f"{mins:02d}:{secs:02d}"
