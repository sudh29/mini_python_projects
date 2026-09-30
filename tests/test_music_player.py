"""Unit tests for the AudioEngine and playback state machine."""

import pytest

from music_player.audio_engine import (
    AudioEngine,
    MockAudioDriver,
    PlaybackState,
)


@pytest.fixture
def engine() -> AudioEngine:
    """Fixture providing an AudioEngine with a Mock driver and sample tracks."""
    eng = AudioEngine(driver=MockAudioDriver())
    eng.load_playlist(
        [
            "/music/song1.mp3",
            "/music/song2.wav",
            "/music/song3.flac",
            "/music/invalid.pdf",  # Should be filtered out
        ]
    )
    return eng


def test_playlist_loading(engine: AudioEngine):
    """Verify loading and extension filtering."""
    assert len(engine.playlist) == 3
    assert engine.current_track == "/music/song1.mp3"
    assert engine.current_track_name == "song1.mp3"
    assert engine.state == PlaybackState.STOPPED


def test_playback_lifecycle(engine: AudioEngine):
    """Verify play, pause, resume, and stop state transitions."""
    assert engine.play() is True
    assert engine.state == PlaybackState.PLAYING
    assert engine.driver.is_playing is True

    assert engine.pause() is True
    assert engine.state == PlaybackState.PAUSED
    assert engine.driver.is_paused is True

    assert engine.stop() is True
    assert engine.state == PlaybackState.STOPPED
    assert engine.driver.is_playing is False


def test_playlist_navigation(engine: AudioEngine):
    """Verify advancing and rewinding through tracks."""
    assert engine.current_index == 0
    assert engine.previous_track() is False  # Already at beginning

    assert engine.next_track() is True
    assert engine.current_index == 1
    assert engine.current_track_name == "song2.wav"

    assert engine.next_track() is True
    assert engine.current_index == 2
    assert engine.current_track_name == "song3.flac"

    assert engine.next_track() is False  # At end of playlist

    assert engine.previous_track() is True
    assert engine.current_index == 1


def test_volume_clamping(engine: AudioEngine):
    """Verify volume adjustments stay within [0.0, 1.0]."""
    assert engine.set_volume(0.8) == 0.8
    assert engine.set_volume(1.5) == 1.0
    assert engine.set_volume(-0.5) == 0.0


def test_progress_tracking_and_formatting(engine: AudioEngine):
    """Verify playback position advancement and time formatting."""
    engine.simulated_duration = 200.0
    engine.play()

    engine.update_position(50.0)
    assert engine.simulated_position == 50.0
    assert engine.get_progress_percentage() == 25.0

    assert AudioEngine.format_time(0) == "00:00"
    assert AudioEngine.format_time(65) == "01:05"
    assert AudioEngine.format_time(3600) == "60:00"


def test_track_auto_advance(engine: AudioEngine):
    """Verify track advances automatically when playback reaches duration end."""
    engine.simulated_duration = 10.0
    engine.play()
    assert engine.current_index == 0

    # Advance past duration
    engine.update_position(12.0)
    # Should have auto-advanced to track 1
    assert engine.current_index == 1
