from __future__ import annotations

import setting


def generate_win_lines(size: int) -> list[tuple[tuple[int, int], ...]]:
    """Return all row, column, and diagonal lines for a square board."""
    lines: list[tuple[tuple[int, int], ...]] = []
    for row in range(size):
        lines.append(tuple((row, col) for col in range(size)))
    for col in range(size):
        lines.append(tuple((row, col) for row in range(size)))
    lines.append(tuple((i, i) for i in range(size)))
    lines.append(tuple((i, size - 1 - i) for i in range(size)))
    return lines


WIN_LINES = generate_win_lines(setting.GRID_SIZE)


class Board:
    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        size = setting.GRID_SIZE
        self.grid: list[list[str]] = [
            [setting.EMPTY for _ in range(size)] for _ in range(size)
        ]
        self.current_player = setting.PLAYER_X
        self.winner: str | None = None
        self.winning_line: tuple[tuple[int, int], ...] | None = None
        self.is_draw = False

    @property
    def game_over(self) -> bool:
        return self.winner is not None or self.is_draw

    def is_empty(self, row: int, col: int) -> bool:
        return self.grid[row][col] == setting.EMPTY

    def place(self, row: int, col: int) -> bool:
        if not self._in_bounds(row, col) or self.game_over or not self.is_empty(row, col):
            return False

        self.grid[row][col] = self.current_player
        self._evaluate_win()
        if self.winner:
            return True

        if self._is_full():
            self.is_draw = True
            return True

        self.current_player = (
            setting.PLAYER_O
            if self.current_player == setting.PLAYER_X
            else setting.PLAYER_X
        )
        return True

    @staticmethod
    def _in_bounds(row: int, col: int) -> bool:
        return 0 <= row < setting.GRID_SIZE and 0 <= col < setting.GRID_SIZE

    def _line_winner(self, line: tuple[tuple[int, int], ...]) -> str | None:
        values = [self.grid[r][c] for r, c in line]
        if values[0] and values[0] == values[1] == values[2]:
            return values[0]
        return None

    def _evaluate_win(self) -> None:
        self.winner = None
        self.winning_line = None
        for line in WIN_LINES:
            symbol = self._line_winner(line)
            if symbol:
                self.winner = symbol
                self.winning_line = line
                return

    def _is_full(self) -> bool:
        return all(cell != setting.EMPTY for row in self.grid for cell in row)
