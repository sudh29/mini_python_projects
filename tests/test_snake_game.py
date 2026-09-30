"""Unit tests for the Snake game engine and utilities."""

from pathlib import Path

import pytest

from game.snake_game.engine import Direction, GameState, Point, SnakeGame, StepResult
from game.snake_game.utils import (
    grid_to_canvas_coords,
    load_high_score,
    save_high_score,
)


@pytest.fixture
def tmp_highscore(tmp_path: Path) -> str:
    """Fixture providing a temporary high score file path."""
    return str(tmp_path / ".test_snake_highscore")


@pytest.fixture
def game(tmp_highscore: str) -> SnakeGame:
    """Fixture providing a fresh SnakeGame instance."""
    return SnakeGame(grid_size=10, high_score_file=tmp_highscore)


def test_initial_state(game: SnakeGame):
    """Verify snake initial coordinates, length, and state."""
    assert len(game.snake) == 3
    assert game.direction == Direction.RIGHT
    assert game.score == 0
    assert game.state == GameState.READY
    # Head at (5, 5), body at (4, 5), tail at (3, 5)
    assert game.snake[0] == Point(5, 5)
    assert game.snake[1] == Point(4, 5)
    assert game.snake[2] == Point(3, 5)


def test_start_and_step(game: SnakeGame):
    """Verify movement advances the snake in current direction."""
    game.start()
    assert game.state == GameState.RUNNING

    result = game.step()
    assert result == StepResult.MOVED
    assert len(game.snake) == 3
    # Head moved right to (6, 5)
    assert game.snake[0] == Point(6, 5)
    assert game.snake[1] == Point(5, 5)
    assert game.snake[2] == Point(4, 5)


def test_direction_changes(game: SnakeGame):
    """Verify steering into perpendicular directions."""
    game.start()
    assert game.set_direction(Direction.UP) is True
    game.step()
    assert game.snake[0] == Point(5, 4)

    assert game.set_direction(Direction.LEFT) is True
    game.step()
    assert game.snake[0] == Point(4, 4)


def test_prevent_reverse_direction(game: SnakeGame):
    """Disallow instant 180-degree reversal which would cause self-collision."""
    game.start()
    assert game.direction == Direction.RIGHT
    # Trying to reverse directly LEFT while moving RIGHT must be rejected
    assert game.set_direction(Direction.LEFT) is False
    assert game.next_direction == Direction.RIGHT


def test_food_consumption_and_growth(game: SnakeGame):
    """Verify snake grows, score increments, and food respawns upon consumption."""
    game.start()
    # Place food directly ahead of snake head (6, 5)
    game.food = Point(6, 5)

    result = game.step()
    assert result == StepResult.ATE_FOOD
    assert len(game.snake) == 4
    assert game.score == 1
    assert game.snake[0] == Point(6, 5)
    # Food has been moved to a new cell
    assert game.food != Point(6, 5)


def test_wall_collision_causes_game_over(game: SnakeGame):
    """Verify snake crashing into grid boundary results in GAME_OVER."""
    game.start()
    # Step until hitting right wall (grid_size is 10, max x is 9)
    # Start at x=5, takes 5 steps to hit x=10 (out of bounds)
    for _ in range(4):
        res = game.step()
        assert res == StepResult.MOVED

    res = game.step()
    assert res == StepResult.GAME_OVER
    assert game.state == GameState.GAME_OVER


def test_self_collision_causes_game_over(game: SnakeGame):
    """Verify snake running into its own tail causes GAME_OVER."""
    game.start()
    # Artificially create a longer snake in a loop:
    # (5,5) -> (5,4) -> (4,4) -> (4,5) -> (5,5)
    game.snake.clear()
    game.snake.extend(
        [
            Point(5, 4),
            Point(4, 4),
            Point(4, 5),
            Point(5, 5),
            Point(6, 5),
        ]
    )
    game.direction = Direction.DOWN
    game.next_direction = Direction.DOWN

    # Moving DOWN from (5,4) attempts to enter (5,5), which is part of the body
    result = game.step()
    assert result == StepResult.GAME_OVER
    assert game.state == GameState.GAME_OVER


def test_pause_toggle(game: SnakeGame):
    """Verify pause and resume state transitions."""
    assert game.toggle_pause() == GameState.RUNNING
    assert game.toggle_pause() == GameState.PAUSED
    assert game.toggle_pause() == GameState.RUNNING


def test_speed_scaling(game: SnakeGame):
    """Verify tick speed decreases (runs faster) as score increases."""
    speed_0 = game.current_speed_ms
    game.score = 10
    speed_10 = game.current_speed_ms
    assert speed_10 < speed_0
    game.score = 50
    assert game.current_speed_ms >= 50  # Must not go below MIN_SPEED_MS


def test_high_score_persistence(tmp_highscore: str):
    """Verify high score persistence utility functions."""
    assert load_high_score(tmp_highscore) == 0
    assert save_high_score(15, tmp_highscore) is True
    assert load_high_score(tmp_highscore) == 15
    # Lower score does not overwrite
    assert save_high_score(10, tmp_highscore) is False
    assert load_high_score(tmp_highscore) == 15


def test_grid_to_canvas_coords():
    """Verify grid cell to canvas bounding box calculation."""
    x1, y1, x2, y2 = grid_to_canvas_coords(2, 3, cell_size=20)
    assert (x1, y1, x2, y2) == (40, 60, 60, 80)
