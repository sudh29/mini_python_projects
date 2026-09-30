"""Decoupled game engine for Minesweeper.

Manages board representation, mine distribution with safe first-click,
recursive zero-cascade revealing, flag toggling, and win/loss state resolution
independently of any GUI framework.
"""

import random
from collections import deque
from enum import Enum, auto

try:
    from game.minesweeper_game import setting
except ImportError:
    import setting


class CellState(Enum):
    HIDDEN = auto()
    REVEALED = auto()
    FLAGGED = auto()


class GameStatus(Enum):
    READY = auto()
    IN_PROGRESS = auto()
    WON = auto()
    LOST = auto()


class MinesweeperCell:
    """Represents a single cell on the Minesweeper grid."""

    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.is_mine = False
        self.state = CellState.HIDDEN
        self.adjacent_mines = 0

    def __repr__(self) -> str:
        return f"Cell({self.x}, {self.y}, mine={self.is_mine}, state={self.state.name})"


class MinesweeperEngine:
    """Core game engine for Minesweeper."""

    def __init__(
        self, grid_size: int = setting.GRID_SIZE, mines_count: int = setting.MINES_COUNT
    ):
        if mines_count >= grid_size * grid_size:
            raise ValueError("Mines count must be less than total number of cells.")
        self.grid_size = grid_size
        self.mines_count = mines_count
        self.board: list[list[MinesweeperCell]] = []
        self.status = GameStatus.READY
        self.first_click_done = False
        self.revealed_count = 0
        self.flagged_count = 0
        self.reset()

    def reset(self) -> None:
        """Initialize an empty board with all cells hidden."""
        self.board = [
            [MinesweeperCell(x, y) for y in range(self.grid_size)]
            for x in range(self.grid_size)
        ]
        self.status = GameStatus.READY
        self.first_click_done = False
        self.revealed_count = 0
        self.flagged_count = 0

    def get_cell(self, x: int, y: int) -> MinesweeperCell:
        """Retrieve cell at given coordinates."""
        if 0 <= x < self.grid_size and 0 <= y < self.grid_size:
            return self.board[x][y]
        raise IndexError(f"Cell coordinates ({x}, {y}) out of bounds.")

    def get_neighbors(self, x: int, y: int) -> list[MinesweeperCell]:
        """Return list of valid adjacent neighbor cells (up to 8)."""
        neighbors = []
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.grid_size and 0 <= ny < self.grid_size:
                    neighbors.append(self.board[nx][ny])
        return neighbors

    def place_mines(self, safe_x: int, safe_y: int, seed: int | None = None) -> None:
        """Distribute mines across the board, guaranteeing safe_x, safe_y is not a mine."""
        if seed is not None:
            random.seed(seed)

        all_coords = [
            (x, y)
            for x in range(self.grid_size)
            for y in range(self.grid_size)
            if (x, y) != (safe_x, safe_y)
        ]
        mine_coords = set(random.sample(all_coords, self.mines_count))

        for x in range(self.grid_size):
            for y in range(self.grid_size):
                if (x, y) in mine_coords:
                    self.board[x][y].is_mine = True

        # Calculate adjacent mine counts
        for x in range(self.grid_size):
            for y in range(self.grid_size):
                cell = self.board[x][y]
                if not cell.is_mine:
                    cell.adjacent_mines = sum(
                        1 for n in self.get_neighbors(x, y) if n.is_mine
                    )

        self.first_click_done = True
        self.status = GameStatus.IN_PROGRESS

    def reveal_cell(self, x: int, y: int) -> tuple[GameStatus, list[tuple[int, int]]]:
        """
        Reveal cell at (x, y).
        Returns (GameStatus, list of (x, y) coordinates newly revealed).
        """
        cell = self.get_cell(x, y)

        # Cannot reveal a flagged or already revealed cell
        if cell.state != CellState.HIDDEN or self.status in (
            GameStatus.WON,
            GameStatus.LOST,
        ):
            return self.status, []

        # On very first click, generate mines ensuring first clicked cell is never a mine
        if not self.first_click_done:
            self.place_mines(safe_x=x, safe_y=y)
            cell = self.get_cell(x, y)

        # If a mine was clicked: Game Over
        if cell.is_mine:
            cell.state = CellState.REVEALED
            self.status = GameStatus.LOST
            # Reveal all remaining mines
            all_mines = []
            for r in range(self.grid_size):
                for c in range(self.grid_size):
                    if self.board[r][c].is_mine:
                        self.board[r][c].state = CellState.REVEALED
                        all_mines.append((r, c))
            return self.status, all_mines

        # Breadth-first search cascade for safe cells
        revealed_coords: list[tuple[int, int]] = []
        queue = deque([cell])
        visited: set[tuple[int, int]] = {(x, y)}

        while queue:
            curr = queue.popleft()
            if curr.state == CellState.FLAGGED:
                continue

            curr.state = CellState.REVEALED
            self.revealed_count += 1
            revealed_coords.append((curr.x, curr.y))

            # Cascade only if current cell has zero adjacent mines
            if curr.adjacent_mines == 0:
                for neighbor in self.get_neighbors(curr.x, curr.y):
                    coord = (neighbor.x, neighbor.y)
                    if (
                        coord not in visited
                        and neighbor.state == CellState.HIDDEN
                        and not neighbor.is_mine
                    ):
                        visited.add(coord)
                        queue.append(neighbor)

        # Check win condition: all non-mine cells revealed
        total_safe_cells = (self.grid_size * self.grid_size) - self.mines_count
        if self.revealed_count >= total_safe_cells:
            self.status = GameStatus.WON

        return self.status, revealed_coords

    def toggle_flag(self, x: int, y: int) -> CellState:
        """Toggle flag on an unrevealed cell."""
        if self.status in (GameStatus.WON, GameStatus.LOST):
            return self.get_cell(x, y).state

        cell = self.get_cell(x, y)
        if cell.state == CellState.HIDDEN:
            cell.state = CellState.FLAGGED
            self.flagged_count += 1
        elif cell.state == CellState.FLAGGED:
            cell.state = CellState.HIDDEN
            self.flagged_count -= 1
        return cell.state

    @property
    def remaining_mines(self) -> int:
        """Return estimated remaining unflagged mines."""
        return self.mines_count - self.flagged_count
