"""Configuration settings for the Snake game."""

# Window and Canvas Dimensions
WINDOW_WIDTH = 640
WINDOW_HEIGHT = 700
HEADER_HEIGHT = 80
CANVAS_WIDTH = 600
CANVAS_HEIGHT = 600

# Grid Dimensions
GRID_SIZE = 24  # 24x24 grid cells
CELL_SIZE = CANVAS_WIDTH // GRID_SIZE  # 25 pixels per cell

# Timing and Difficulty (in milliseconds)
INITIAL_SPEED_MS = 120
MIN_SPEED_MS = 50
SPEED_DECREMENT_PER_FOOD_MS = 3  # Increases speed as score climbs

# Visual Theme (Dark Mode Palette)
COLOR_BG = "#0f172a"  # Slate 900
COLOR_CANVAS_BG = "#1e293b"  # Slate 800
COLOR_GRID = "#334155"  # Slate 700
COLOR_SNAKE_HEAD = "#38bdf8"  # Sky 400
COLOR_SNAKE_BODY = "#0ea5e9"  # Sky 500
COLOR_SNAKE_EYE = "#0f172a"  # Dark eye dot
COLOR_FOOD = "#f43f5e"  # Rose 500
COLOR_TEXT_PRIMARY = "#f8fafc"
COLOR_TEXT_MUTED = "#94a3b8"
COLOR_ACCENT = "#22c55e"  # Green 500
COLOR_OVERLAY = "#0f172a"  # Semi-transparent overlay bg

# High score persistence file
HIGH_SCORE_FILE = ".snake_highscore"
