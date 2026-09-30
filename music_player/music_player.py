"""Kivy Music Player Application.

A clean desktop audio player GUI built with Kivy and powered by a decoupled
AudioEngine backend.

Features:
- Decoupled playback state machine (audio_engine.py)
- Play, Pause, Stop, Previous, Next track controls
- Real-time progress bar tracking and volume slider
- File chooser playlist loader
- Safe fallback when running in headless / CLI environments
"""

import logging
import os
import sys

# Suppress Kivy audio warnings on headless environments
logging.getLogger("kivy.core.audio").setLevel(logging.ERROR)
os.environ["KIVY_AUDIO"] = "sdl2"

try:
    from music_player.audio_engine import (
        AudioEngine,
        PlaybackState,
        SubprocessAudioDriver,
    )
except ImportError:
    from audio_engine import AudioEngine, PlaybackState, SubprocessAudioDriver

try:
    from kivy.app import App
    from kivy.clock import Clock
    from kivy.uix.boxlayout import BoxLayout
    from kivy.uix.button import Button
    from kivy.uix.filechooser import FileChooserListView
    from kivy.uix.gridlayout import GridLayout
    from kivy.uix.label import Label
    from kivy.uix.popup import Popup
    from kivy.uix.slider import Slider

    KIVY_AVAILABLE = True
except (ImportError, Exception):
    KIVY_AVAILABLE = False
    App = object
    BoxLayout = None
    GridLayout = None
    Button = None
    Label = None
    Slider = None
    Popup = None
    Clock = None
    FileChooserListView = None


class MusicPlayerApp(App if KIVY_AVAILABLE else object):
    """Kivy-based music player application with play, pause, and volume controls."""

    def __init__(self, **kwargs):
        if KIVY_AVAILABLE:
            super().__init__(**kwargs)
        self.engine = AudioEngine(driver=SubprocessAudioDriver())

        # Load default audio file if it exists
        default_audio = os.path.join(os.path.dirname(__file__), "audio.mp3")
        if os.path.exists(default_audio):
            self.engine.load_playlist([default_audio])

    def build(self):
        """Build the UI layout for the music player."""
        if not KIVY_AVAILABLE:
            print("Kivy is not installed or display server is unavailable.")
            return None

        # Main vertical layout
        self.root = BoxLayout(orientation="vertical", padding=15, spacing=10)

        # ===== Display Section =====
        display_layout = BoxLayout(orientation="vertical", size_hint_y=0.3, spacing=5)

        title_layout = BoxLayout(size_hint_y=0.4)
        self.title_label = Label(
            text="🎵 Music Player", font_size="22sp", bold=True, color=(1, 1, 1, 1)
        )
        title_layout.add_widget(self.title_label)
        display_layout.add_widget(title_layout)

        song_layout = BoxLayout(size_hint_y=0.3)
        self.song_label = Label(
            text=f"Now Playing: {self.engine.current_track_name}",
            font_size="13sp",
            color=(0.8, 0.8, 0.8, 1),
        )
        song_layout.add_widget(self.song_label)
        display_layout.add_widget(song_layout)

        time_layout = BoxLayout(size_hint_y=0.3)
        self.time_label = Label(
            text="00:00 / 03:00", font_size="11sp", color=(0.6, 0.6, 0.6, 1)
        )
        time_layout.add_widget(self.time_label)
        display_layout.add_widget(time_layout)

        self.root.add_widget(display_layout)

        # ===== Progress Bar =====
        self.progress_slider = Slider(min=0, max=100, value=0, size_hint_y=0.1)
        self.root.add_widget(self.progress_slider)

        # ===== Control Buttons Section =====
        controls_layout = GridLayout(cols=5, size_hint_y=0.25, spacing=5)

        prev_button = Button(
            text="⏮ Prev", background_color=(0.2, 0.2, 0.2, 1), font_size="12sp"
        )
        prev_button.bind(on_release=self.previous_song)
        controls_layout.add_widget(prev_button)

        self.play_button = Button(
            text="▶ Play", background_color=(0.2, 0.6, 0.2, 1), font_size="12sp"
        )
        self.play_button.bind(on_release=self.play_music)
        controls_layout.add_widget(self.play_button)

        self.pause_button = Button(
            text="⏸ Pause", background_color=(0.6, 0.6, 0.2, 1), font_size="12sp"
        )
        self.pause_button.bind(on_release=self.pause_music)
        controls_layout.add_widget(self.pause_button)

        self.stop_button = Button(
            text="⏹ Stop", background_color=(0.6, 0.2, 0.2, 1), font_size="12sp"
        )
        self.stop_button.bind(on_release=self.stop_music)
        controls_layout.add_widget(self.stop_button)

        next_button = Button(
            text="Next ⏭", background_color=(0.2, 0.2, 0.2, 1), font_size="12sp"
        )
        next_button.bind(on_release=self.next_song)
        controls_layout.add_widget(next_button)

        self.root.add_widget(controls_layout)

        # ===== Volume Control Section =====
        volume_layout = BoxLayout(size_hint_y=0.15, spacing=10)
        volume_label = Label(text="Volume:", size_hint_x=0.2, font_size="12sp")
        volume_layout.add_widget(volume_label)

        self.volume_slider = Slider(
            min=0, max=1, value=self.engine.volume, size_hint_x=0.8
        )
        self.volume_slider.bind(value=self.set_volume)
        volume_layout.add_widget(self.volume_slider)

        self.root.add_widget(volume_layout)

        # ===== Playlist Section =====
        playlist_button = Button(
            text="📁 Load Playlist",
            size_hint_y=0.1,
            background_color=(0.3, 0.3, 0.5, 1),
            font_size="12sp",
        )
        playlist_button.bind(on_release=self.load_playlist)
        self.root.add_widget(playlist_button)

        self.status_label = Label(
            text="Status: Ready",
            size_hint_y=0.1,
            font_size="11sp",
            color=(0.5, 1, 0.5, 1),
        )
        self.root.add_widget(self.status_label)

        # Schedule progress updates
        Clock.schedule_interval(self.update_progress, 0.5)

        return self.root

    def play_music(self, _instance) -> None:
        """Trigger track playback."""
        if not self.engine.current_track:
            self.status_label.text = "Status: No track loaded"
            return

        success = self.engine.play()
        if success:
            self.play_button.text = "▶ Playing"
            self.song_label.text = f"Now Playing: {self.engine.current_track_name}"
            self.status_label.text = "Status: Playing"
        else:
            self.status_label.text = (
                "Status: Audio playback driver unavailable (install ffmpeg)"
            )

    def pause_music(self, _instance) -> None:
        """Pause track playback."""
        self.engine.pause()
        self.play_button.text = "▶ Play"
        self.status_label.text = "Status: Paused"

    def stop_music(self, _instance) -> None:
        """Stop playback and reset slider."""
        self.engine.stop()
        self.play_button.text = "▶ Play"
        self.progress_slider.value = 0
        self.time_label.text = "00:00 / 03:00"
        self.status_label.text = "Status: Stopped"

    def set_volume(self, _instance, value: float) -> None:
        """Adjust engine volume."""
        self.engine.set_volume(value)

    def next_song(self, _instance) -> None:
        """Advance to next track."""
        if self.engine.next_track():
            self.song_label.text = f"Now Playing: {self.engine.current_track_name}"
            self.status_label.text = "Status: Next track"
        else:
            self.status_label.text = "Status: End of playlist"

    def previous_song(self, _instance) -> None:
        """Move to previous track."""
        if self.engine.previous_track():
            self.song_label.text = f"Now Playing: {self.engine.current_track_name}"
            self.status_label.text = "Status: Previous track"
        else:
            self.status_label.text = "Status: At first track"

    def update_progress(self, dt: float) -> None:
        """Update progress bar and timer display."""
        if self.engine.state == PlaybackState.PLAYING:
            pos = self.engine.update_position(dt)
            self.progress_slider.value = self.engine.get_progress_percentage()
            curr = AudioEngine.format_time(pos)
            total = AudioEngine.format_time(self.engine.simulated_duration)
            self.time_label.text = f"{curr} / {total}"

    def load_playlist(self, _instance) -> None:
        """Open file browser popup to select track."""
        if not KIVY_AVAILABLE:
            return

        content = BoxLayout(orientation="vertical")
        filechooser = FileChooserListView(filters=["*.mp3", "*.wav", "*.ogg", "*.flac"])
        content.add_widget(filechooser)

        btn_layout = BoxLayout(size_hint_y=0.15, spacing=5)
        popup = Popup(title="Select Audio Track", content=content, size_hint=(0.9, 0.9))

        def on_select(_):
            if filechooser.selection:
                selected = filechooser.selection[0]
                self.engine.load_playlist([selected])
                self.song_label.text = f"Selected: {self.engine.current_track_name}"
                self.status_label.text = "Status: Track loaded"
                popup.dismiss()

        load_btn = Button(text="Load", on_release=on_select)
        cancel_btn = Button(text="Cancel", on_release=lambda _: popup.dismiss())
        btn_layout.add_widget(load_btn)
        btn_layout.add_widget(cancel_btn)
        content.add_widget(btn_layout)

        popup.open()


def main() -> None:
    """Entry point for the Music Player application."""
    if not KIVY_AVAILABLE:
        print(
            "Kivy GUI framework is not installed in the default environment.\n"
            "To test the audio playback engine headlessly, run:\n"
            "  uv run pytest tests/test_music_player.py"
        )
        sys.exit(0)
    MusicPlayerApp().run()


if __name__ == "__main__":
    main()
