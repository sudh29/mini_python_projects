"""Utility functions for Minesweeper layout and formatting."""

try:
    from game.minesweeper_game import setting
except ImportError:
    import setting


def format_timer(seconds: int) -> str:
    """Format an elapsed time in seconds to MM:SS string."""
    mins = seconds // 60
    secs = seconds % 60
    return f"{mins:02d}:{secs:02d}"


def calculate_button_geometry(grid_size: int = setting.GRID_SIZE) -> tuple[int, int]:
    """Return proportional width and height font size for grid buttons."""
    font_size = max(10, 24 - (grid_size * 2))
    return font_size, font_size + 4
