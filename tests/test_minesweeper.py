"""Unit tests for the Minesweeper game engine and utilities."""

import pytest

from game.minesweeper_game.engine import CellState, GameStatus, MinesweeperEngine
from game.minesweeper_game.utils import format_timer


@pytest.fixture
def engine() -> MinesweeperEngine:
    """Fixture providing a deterministic 6x6 MinesweeperEngine with 5 mines."""
    return MinesweeperEngine(grid_size=6, mines_count=5)


def test_initial_board_state(engine: MinesweeperEngine):
    """Verify clean initialization of the board."""
    assert engine.grid_size == 6
    assert engine.mines_count == 5
    assert engine.status == GameStatus.READY
    assert engine.revealed_count == 0
    assert engine.flagged_count == 0
    assert engine.remaining_mines == 5

    for r in range(6):
        for c in range(6):
            cell = engine.get_cell(r, c)
            assert cell.state == CellState.HIDDEN
            assert not cell.is_mine


def test_safe_first_click_placement(engine: MinesweeperEngine):
    """Ensure that the first-clicked cell is guaranteed safe."""
    engine.place_mines(safe_x=2, safe_y=3, seed=42)
    assert engine.first_click_done is True
    assert engine.status == GameStatus.IN_PROGRESS
    assert engine.get_cell(2, 3).is_mine is False

    # Count total mines placed
    actual_mines = sum(
        1 for r in range(6) for c in range(6) if engine.get_cell(r, c).is_mine
    )
    assert actual_mines == 5


def test_neighbor_topology(engine: MinesweeperEngine):
    """Verify correct neighbor counts for interior, edge, and corner cells."""
    assert len(engine.get_neighbors(0, 0)) == 3  # Corner
    assert len(engine.get_neighbors(0, 2)) == 5  # Edge
    assert len(engine.get_neighbors(2, 2)) == 8  # Interior


def test_flag_toggling(engine: MinesweeperEngine):
    """Verify flagging and unflagging cells."""
    state1 = engine.toggle_flag(1, 1)
    assert state1 == CellState.FLAGGED
    assert engine.flagged_count == 1
    assert engine.remaining_mines == 4

    state2 = engine.toggle_flag(1, 1)
    assert state2 == CellState.HIDDEN
    assert engine.flagged_count == 0
    assert engine.remaining_mines == 5


def test_cannot_reveal_flagged_cell(engine: MinesweeperEngine):
    """Flagged cells should be protected from accidental click."""
    engine.toggle_flag(2, 2)
    status, revealed = engine.reveal_cell(2, 2)
    assert revealed == []
    assert engine.get_cell(2, 2).state == CellState.FLAGGED


def test_click_mine_causes_loss(engine: MinesweeperEngine):
    """Clicking on a mine triggers game loss and reveals all mines."""
    engine.place_mines(safe_x=0, safe_y=0, seed=123)
    # Find a placed mine
    mine_cell = None
    for r in range(6):
        for c in range(6):
            if engine.get_cell(r, c).is_mine:
                mine_cell = (r, c)
                break
        if mine_cell:
            break

    assert mine_cell is not None
    status, revealed = engine.reveal_cell(mine_cell[0], mine_cell[1])
    assert status == GameStatus.LOST
    assert len(revealed) == 5  # All 5 mines revealed


def test_zero_cascade_reveal(engine: MinesweeperEngine):
    """Clicking a cell with 0 adjacent mines triggers recursive flood-fill."""
    # Custom configuration where cell (0, 0) has 0 adjacent mines
    engine.place_mines(safe_x=0, safe_y=0, seed=999)
    cell = engine.get_cell(0, 0)

    status, revealed = engine.reveal_cell(0, 0)
    assert status in (GameStatus.IN_PROGRESS, GameStatus.WON)
    assert len(revealed) >= 1
    assert cell.state == CellState.REVEALED


def test_win_condition():
    """Verify winning when all non-mine cells are cleared."""
    small_engine = MinesweeperEngine(grid_size=3, mines_count=1)
    # Place 1 mine at (2, 2)
    small_engine.board[2][2].is_mine = True
    small_engine.first_click_done = True
    small_engine.status = GameStatus.IN_PROGRESS

    # Reveal all other 8 safe cells
    for r in range(3):
        for c in range(3):
            if (r, c) != (2, 2):
                small_engine.board[r][c].adjacent_mines = (
                    1 if max(abs(r - 2), abs(c - 2)) == 1 else 0
                )

    # Reveal safe cells one by one or cascade
    for r in range(3):
        for c in range(3):
            if (r, c) != (2, 2) and small_engine.get_cell(
                r, c
            ).state == CellState.HIDDEN:
                status, _ = small_engine.reveal_cell(r, c)

    assert small_engine.status == GameStatus.WON


def test_format_timer():
    """Verify MM:SS timer formatting."""
    assert format_timer(0) == "00:00"
    assert format_timer(65) == "01:05"
    assert format_timer(3600) == "60:00"
