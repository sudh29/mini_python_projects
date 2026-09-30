from pathlib import Path

try:
    from game.snake_game import setting
except ImportError:
    import setting


def grid_to_canvas_coords(
    grid_x: int, grid_y: int, cell_size: int = setting.CELL_SIZE
) -> tuple[int, int, int, int]:
    """Convert grid cell coordinates (x, y) to canvas rectangle bounding box (x1, y1, x2, y2)."""
    x1 = grid_x * cell_size
    y1 = grid_y * cell_size
    x2 = x1 + cell_size
    y2 = y1 + cell_size
    return x1, y1, x2, y2


def load_high_score(file_path: str = setting.HIGH_SCORE_FILE) -> int:
    """Read saved high score from file safely, returning 0 if missing or corrupt."""
    p = Path(file_path)
    if not p.exists():
        return 0
    try:
        content = p.read_text(encoding="utf-8").strip()
        return max(0, int(content))
    except (ValueError, OSError):
        return 0


def save_high_score(score: int, file_path: str = setting.HIGH_SCORE_FILE) -> bool:
    """Persist high score to disk safely."""
    try:
        p = Path(file_path)
        current = load_high_score(file_path)
        if score > current:
            p.write_text(str(score), encoding="utf-8")
            return True
        return False
    except OSError:
        return False
