"""Classic Snake Game built with Python and Tkinter.

Features:
- Responsive Tkinter Canvas rendering with modern dark aesthetics
- Decoupled game engine logic in engine.py for headless testing
- Dynamic difficulty: Snake speed increases progressively with score
- Persistent high score saved to disk
- Dual control support: Arrow Keys or WASD
- Start, Pause, Resume, and Restart capabilities
"""

import sys
import tkinter as tk

try:
    from game.snake_game import setting
    from game.snake_game.engine import (
        Direction,
        GameState,
        SnakeGame,
        StepResult,
    )
    from game.snake_game.utils import grid_to_canvas_coords
except ImportError:
    import setting
    from engine import Direction, GameState, SnakeGame, StepResult
    from utils import grid_to_canvas_coords


class SnakeApp:
    """Tkinter GUI application for the Snake game."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Python Classic Snake")
        self.root.configure(bg=setting.COLOR_BG)
        self.root.resizable(False, False)

        self.game = SnakeGame(grid_size=setting.GRID_SIZE)
        self.loop_id: str | None = None

        self._build_ui()
        self._bind_keys()
        self._render()

    def _build_ui(self) -> None:
        """Create header dashboard and game canvas."""
        # Top Header Frame
        header = tk.Frame(self.root, bg=setting.COLOR_BG, height=setting.HEADER_HEIGHT)
        header.pack(fill=tk.X, padx=20, pady=(15, 5))

        # Title and instructions
        title_frame = tk.Frame(header, bg=setting.COLOR_BG)
        title_frame.pack(side=tk.LEFT)

        self.lbl_title = tk.Label(
            title_frame,
            text="🐍 SNAKE",
            font=("Helvetica", 20, "bold"),
            fg=setting.COLOR_SNAKE_HEAD,
            bg=setting.COLOR_BG,
        )
        self.lbl_title.pack(anchor=tk.W)

        self.lbl_status = tk.Label(
            title_frame,
            text="Press SPACE to Start / Pause • R to Restart",
            font=("Helvetica", 9),
            fg=setting.COLOR_TEXT_MUTED,
            bg=setting.COLOR_BG,
        )
        self.lbl_status.pack(anchor=tk.W)

        # Score & High Score Panel
        score_frame = tk.Frame(header, bg=setting.COLOR_BG)
        score_frame.pack(side=tk.RIGHT)

        self.lbl_score = tk.Label(
            score_frame,
            text=f"Score: {self.game.score}",
            font=("Helvetica", 14, "bold"),
            fg=setting.COLOR_TEXT_PRIMARY,
            bg=setting.COLOR_BG,
        )
        self.lbl_score.pack(anchor=tk.E)

        self.lbl_high_score = tk.Label(
            score_frame,
            text=f"High: {self.game.high_score}",
            font=("Helvetica", 10),
            fg=setting.COLOR_ACCENT,
            bg=setting.COLOR_BG,
        )
        self.lbl_high_score.pack(anchor=tk.E)

        # Game Canvas
        self.canvas = tk.Canvas(
            self.root,
            width=setting.CANVAS_WIDTH,
            height=setting.CANVAS_HEIGHT,
            bg=setting.COLOR_CANVAS_BG,
            highlightthickness=2,
            highlightbackground=setting.COLOR_GRID,
        )
        self.canvas.pack(padx=20, pady=(5, 20))

    def _bind_keys(self) -> None:
        """Register keyboard controls."""
        # Arrow Keys
        self.root.bind("<Up>", lambda _: self._on_direction(Direction.UP))
        self.root.bind("<Down>", lambda _: self._on_direction(Direction.DOWN))
        self.root.bind("<Left>", lambda _: self._on_direction(Direction.LEFT))
        self.root.bind("<Right>", lambda _: self._on_direction(Direction.RIGHT))

        # WASD Keys
        self.root.bind("<w>", lambda _: self._on_direction(Direction.UP))
        self.root.bind("<s>", lambda _: self._on_direction(Direction.DOWN))
        self.root.bind("<a>", lambda _: self._on_direction(Direction.LEFT))
        self.root.bind("<d>", lambda _: self._on_direction(Direction.RIGHT))
        self.root.bind("<W>", lambda _: self._on_direction(Direction.UP))
        self.root.bind("<S>", lambda _: self._on_direction(Direction.DOWN))
        self.root.bind("<A>", lambda _: self._on_direction(Direction.LEFT))
        self.root.bind("<D>", lambda _: self._on_direction(Direction.RIGHT))

        # Action Keys
        self.root.bind("<space>", lambda _: self._on_space())
        self.root.bind("<r>", lambda _: self._on_restart())
        self.root.bind("<R>", lambda _: self._on_restart())
        self.root.bind("<Escape>", lambda _: self.root.destroy())

    def _on_direction(self, direction: Direction) -> None:
        """Handle direction change input."""
        if self.game.state == GameState.READY:
            self.game.start()
            self._schedule_tick()
        self.game.set_direction(direction)

    def _on_space(self) -> None:
        """Handle start / pause toggle."""
        if self.game.state == GameState.GAME_OVER:
            self._on_restart()
            return

        new_state = self.game.toggle_pause()
        if new_state == GameState.RUNNING:
            self.lbl_status.config(
                text="Game Running • Press SPACE to Pause", fg=setting.COLOR_ACCENT
            )
            self._schedule_tick()
        elif new_state == GameState.PAUSED:
            self.lbl_status.config(
                text="Game Paused • Press SPACE to Resume", fg="#fbbf24"
            )
        self._render()

    def _on_restart(self) -> None:
        """Reset the game state."""
        if self.loop_id:
            self.root.after_cancel(self.loop_id)
            self.loop_id = None
        self.game.reset()
        self.lbl_status.config(
            text="Press SPACE to Start / Pause • R to Restart",
            fg=setting.COLOR_TEXT_MUTED,
        )
        self.lbl_score.config(text=f"Score: {self.game.score}")
        self.lbl_high_score.config(text=f"High: {self.game.high_score}")
        self._render()

    def _schedule_tick(self) -> None:
        """Schedule next animation step."""
        if self.loop_id:
            self.root.after_cancel(self.loop_id)
        if self.game.state == GameState.RUNNING:
            self.loop_id = self.root.after(self.game.current_speed_ms, self._tick)

    def _tick(self) -> None:
        """Advance game state by one frame."""
        result = self.game.step()
        self.lbl_score.config(text=f"Score: {self.game.score}")
        self.lbl_high_score.config(text=f"High: {self.game.high_score}")

        if result == StepResult.GAME_OVER:
            self.lbl_status.config(
                text="Game Over! Press R or SPACE to Restart", fg=setting.COLOR_FOOD
            )
            self._render()
            return

        self._render()
        if self.game.state == GameState.RUNNING:
            self._schedule_tick()

    def _render(self) -> None:
        """Redraw canvas elements."""
        self.canvas.delete("all")

        # 1. Subtle Grid Lines
        for i in range(1, setting.GRID_SIZE):
            pos = i * setting.CELL_SIZE
            self.canvas.create_line(
                pos, 0, pos, setting.CANVAS_HEIGHT, fill=setting.COLOR_GRID, width=1
            )
            self.canvas.create_line(
                0, pos, setting.CANVAS_WIDTH, pos, fill=setting.COLOR_GRID, width=1
            )

        # 2. Draw Food (Glow and Inner Dot)
        fx1, fy1, fx2, fy2 = grid_to_canvas_coords(self.game.food.x, self.game.food.y)
        self.canvas.create_oval(
            fx1 + 2, fy1 + 2, fx2 - 2, fy2 - 2, fill=setting.COLOR_FOOD, outline=""
        )
        self.canvas.create_oval(
            fx1 + 6, fy1 + 6, fx2 - 6, fy2 - 6, fill="#ffffff", outline=""
        )

        # 3. Draw Snake Body and Head
        for index, segment in enumerate(self.game.snake):
            sx1, sy1, sx2, sy2 = grid_to_canvas_coords(segment.x, segment.y)
            if index == 0:
                # Head
                self.canvas.create_rectangle(
                    sx1 + 1,
                    sy1 + 1,
                    sx2 - 1,
                    sy2 - 1,
                    fill=setting.COLOR_SNAKE_HEAD,
                    outline="",
                )
                # Eyes
                eye_radius = 2
                mid_x = (sx1 + sx2) // 2
                mid_y = (sy1 + sy2) // 2
                dx = self.game.direction.dx
                dy = self.game.direction.dy

                if dx != 0:
                    eye_x = mid_x + dx * 4
                    self.canvas.create_oval(
                        eye_x - eye_radius,
                        mid_y - 4,
                        eye_x + eye_radius,
                        mid_y - 2,
                        fill=setting.COLOR_SNAKE_EYE,
                        outline="",
                    )
                    self.canvas.create_oval(
                        eye_x - eye_radius,
                        mid_y + 2,
                        eye_x + eye_radius,
                        mid_y + 4,
                        fill=setting.COLOR_SNAKE_EYE,
                        outline="",
                    )
                else:
                    eye_y = mid_y + dy * 4
                    self.canvas.create_oval(
                        mid_x - 4,
                        eye_y - eye_radius,
                        mid_x - 2,
                        eye_y + eye_radius,
                        fill=setting.COLOR_SNAKE_EYE,
                        outline="",
                    )
                    self.canvas.create_oval(
                        mid_x + 2,
                        eye_y - eye_radius,
                        mid_x + 4,
                        eye_y + eye_radius,
                        fill=setting.COLOR_SNAKE_EYE,
                        outline="",
                    )
            else:
                # Body Segment
                self.canvas.create_rectangle(
                    sx1 + 1,
                    sy1 + 1,
                    sx2 - 1,
                    sy2 - 1,
                    fill=setting.COLOR_SNAKE_BODY,
                    outline="",
                )

        # 4. Overlay if Paused or Game Over
        if self.game.state == GameState.PAUSED:
            self._render_overlay("PAUSED", "Press SPACE to Resume")
        elif self.game.state == GameState.GAME_OVER:
            self._render_overlay(
                "GAME OVER", f"Final Score: {self.game.score} • Press R to Play Again"
            )
        elif self.game.state == GameState.READY:
            self._render_overlay("READY", "Press SPACE or Any Arrow Key to Begin")

    def _render_overlay(self, title: str, subtitle: str) -> None:
        """Render a modal text overlay over the canvas."""
        cx = setting.CANVAS_WIDTH // 2
        cy = setting.CANVAS_HEIGHT // 2
        self.canvas.create_rectangle(
            cx - 190,
            cy - 50,
            cx + 190,
            cy + 50,
            fill=setting.COLOR_BG,
            outline=setting.COLOR_GRID,
            width=2,
        )
        self.canvas.create_text(
            cx,
            cy - 14,
            text=title,
            font=("Helvetica", 18, "bold"),
            fill=setting.COLOR_TEXT_PRIMARY,
        )
        self.canvas.create_text(
            cx,
            cy + 18,
            text=subtitle,
            font=("Helvetica", 9),
            fill=setting.COLOR_TEXT_MUTED,
        )


def main() -> None:
    """Entry point for the Snake game application."""
    try:
        root = tk.Tk()
        _app = SnakeApp(root)
        root.mainloop()
    except tk.TclError as e:
        print(
            f"Tkinter display unavailable: {e}. If running in headless environment, run pytest test suite."
        )
        sys.exit(0)


if __name__ == "__main__":
    main()
