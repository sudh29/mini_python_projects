"""Decoupled game engine for the Snake game.

Provides pure game state management, movement vector calculation,
collision checking, food placement, and score tracking with zero GUI dependencies.
"""

import random
from collections import deque
from enum import Enum, auto
from typing import NamedTuple

try:
    from game.snake_game import setting
    from game.snake_game.utils import load_high_score, save_high_score
except ImportError:
    import setting
    from utils import load_high_score, save_high_score


class Point(NamedTuple):
    x: int
    y: int


class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

    @property
    def dx(self) -> int:
        return self.value[0]

    @property
    def dy(self) -> int:
        return self.value[1]

    def is_opposite(self, other: "Direction") -> bool:
        return self.dx + other.dx == 0 and self.dy + other.dy == 0


class GameState(Enum):
    READY = auto()
    RUNNING = auto()
    PAUSED = auto()
    GAME_OVER = auto()


class StepResult(Enum):
    MOVED = auto()
    ATE_FOOD = auto()
    GAME_OVER = auto()


class SnakeGame:
    """Manages the full state and logic of a Snake game session."""

    def __init__(
        self,
        grid_size: int = setting.GRID_SIZE,
        high_score_file: str = setting.HIGH_SCORE_FILE,
    ):
        self.grid_size = grid_size
        self.high_score_file = high_score_file
        self.high_score = load_high_score(high_score_file)
        self.snake: deque[Point] = deque()
        self.direction = Direction.RIGHT
        self.next_direction = Direction.RIGHT
        self.food = Point(0, 0)
        self.score = 0
        self.state = GameState.READY
        self.reset()

    def reset(self) -> None:
        """Reset the game state to initial values with a 3-segment snake centered on the grid."""
        mid_x = self.grid_size // 2
        mid_y = self.grid_size // 2
        # Head at mid_x, tail extends to the left
        self.snake = deque(
            [
                Point(mid_x, mid_y),
                Point(mid_x - 1, mid_y),
                Point(mid_x - 2, mid_y),
            ]
        )
        self.direction = Direction.RIGHT
        self.next_direction = Direction.RIGHT
        self.score = 0
        self.state = GameState.READY
        self.spawn_food()

    def spawn_food(self, seed: int | None = None) -> Point:
        """Place a food item on a random open tile not occupied by the snake."""
        if seed is not None:
            random.seed(seed)

        occupied = set(self.snake)
        available = [
            Point(x, y)
            for x in range(self.grid_size)
            for y in range(self.grid_size)
            if Point(x, y) not in occupied
        ]
        if not available:
            # Snake filled the entire board
            self.state = GameState.GAME_OVER
            return Point(-1, -1)

        self.food = random.choice(available)
        return self.food

    def set_direction(self, new_direction: Direction) -> bool:
        """Buffer a direction change, disallowing direct 180-degree reversals."""
        if self.state in (GameState.READY, GameState.RUNNING):
            # Compare with currently buffered direction to handle rapid double keystrokes
            if not new_direction.is_opposite(self.direction):
                self.next_direction = new_direction
                return True
        return False

    def toggle_pause(self) -> GameState:
        """Toggle between RUNNING and PAUSED states."""
        if self.state == GameState.RUNNING:
            self.state = GameState.PAUSED
        elif self.state == GameState.PAUSED:
            self.state = GameState.RUNNING
        elif self.state == GameState.READY:
            self.state = GameState.RUNNING
        return self.state

    def start(self) -> None:
        """Start the game loop from READY state."""
        if self.state == GameState.READY:
            self.state = GameState.RUNNING

    def step(self) -> StepResult:
        """Advance the snake by one tick in the active direction."""
        if self.state != GameState.RUNNING:
            return StepResult.MOVED

        self.direction = self.next_direction
        head = self.snake[0]
        new_head = Point(head.x + self.direction.dx, head.y + self.direction.dy)

        # 1. Wall Collision Check
        if not (0 <= new_head.x < self.grid_size and 0 <= new_head.y < self.grid_size):
            self.state = GameState.GAME_OVER
            self._update_high_score()
            return StepResult.GAME_OVER

        # 2. Self Collision Check
        # If moving into the tail cell, it will vacate this turn UNLESS food is eaten
        will_grow = new_head == self.food
        body_to_check = set(self.snake) if will_grow else set(list(self.snake)[:-1])
        if new_head in body_to_check:
            self.state = GameState.GAME_OVER
            self._update_high_score()
            return StepResult.GAME_OVER

        # 3. Valid Movement
        self.snake.appendleft(new_head)

        if will_grow:
            self.score += 1
            self._update_high_score()
            self.spawn_food()
            return StepResult.ATE_FOOD
        else:
            self.snake.pop()
            return StepResult.MOVED

    def _update_high_score(self) -> None:
        """Update and persist high score if current score exceeds it."""
        if self.score > self.high_score:
            self.high_score = self.score
            save_high_score(self.high_score, self.high_score_file)

    @property
    def current_speed_ms(self) -> int:
        """Calculate the current tick delay in ms based on score."""
        decrement = self.score * setting.SPEED_DECREMENT_PER_FOOD_MS
        speed = setting.INITIAL_SPEED_MS - decrement
        return max(setting.MIN_SPEED_MS, speed)
