import setting


def scale_factor(width: int, height: int) -> float:
    """Scale relative to the default window size, clamped for readability."""
    w_ratio = width / setting.DEFAULT_WIDTH
    h_ratio = height / setting.DEFAULT_HEIGHT
    return max(0.65, min(min(w_ratio, h_ratio), 2.0))


def scaled_size(base: int, factor: float) -> int:
    return max(1, round(base * factor))


def font_size_from_box(
    width: int,
    height: int,
    ratio: float,
    *,
    min_size: int = 8,
    max_size: int = 120,
) -> int:
    """Pick a font point size that fits inside the given pixel box."""
    if width < 2 or height < 2:
        return min_size
    return max(min_size, min(max_size, int(min(width, height) * ratio)))
