"""Configuration settings and design tokens for Minesweeper."""

# Dimensions
WINDOW_WIDTH = 540
WINDOW_HEIGHT = 620
HEADER_HEIGHT = 80

# Board Configurations
GRID_SIZE = 8  # 8x8 beginner grid
CELL_COUNT = GRID_SIZE**2
MINES_COUNT = 10  # 10 mines (standard beginner density ~15%)

# Visual Styling
COLOR_BG = "#0f172a"  # Slate 900
COLOR_HEADER_BG = "#1e293b"  # Slate 800
COLOR_GRID_BG = "#334155"  # Slate 700
COLOR_CELL_HIDDEN = "#cbd5e1"  # Slate 300
COLOR_CELL_REVEALED = "#f1f5f9"  # Slate 100
COLOR_CELL_MINE = "#ef4444"  # Red 500
COLOR_CELL_FLAGGED = "#f59e0b"  # Amber 500
COLOR_TEXT_PRIMARY = "#f8fafc"
COLOR_TEXT_MUTED = "#94a3b8"

# Number Colors for Adjacent Mines
NUMBER_COLORS = {
    1: "#2563eb",  # Blue
    2: "#16a34a",  # Green
    3: "#dc2626",  # Red
    4: "#7c3aed",  # Purple
    5: "#b91c1c",  # Dark Red
    6: "#0d9488",  # Teal
    7: "#1e293b",  # Dark Slate
    8: "#64748b",  # Gray
}
