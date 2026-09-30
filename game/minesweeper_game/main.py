"""Classic Minesweeper Game with Tkinter GUI.

Features:
- Pure game logic separated into engine.py for headless testing
- Fully cross-platform using standard tkinter.messagebox (no ctypes.windll Windows dependency)
- Safe first-click guarantee (first clicked cell is never a mine)
- Automatic recursive cascade reveal for zero-mine regions
- Right-click cell flagging with live remaining-mine counter
- Elapsed timer and instant replay/reset functionality
"""

import sys
import tkinter as tk
from tkinter import messagebox

try:
    from game.minesweeper_game import setting
    from game.minesweeper_game.engine import CellState, GameStatus, MinesweeperEngine
    from game.minesweeper_game.utils import format_timer
except ImportError:
    import setting
    from engine import CellState, GameStatus, MinesweeperEngine
    from utils import format_timer


class MinesweeperApp:
    """Tkinter GUI application for Minesweeper."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Python Minesweeper")
        self.root.configure(bg=setting.COLOR_BG)
        self.root.resizable(False, False)

        self.engine = MinesweeperEngine(
            grid_size=setting.GRID_SIZE, mines_count=setting.MINES_COUNT
        )
        self.buttons: dict[tuple[int, int], tk.Button] = {}
        self.timer_seconds = 0
        self.timer_job: str | None = None

        self._build_ui()
        self._start_timer()

    def _build_ui(self) -> None:
        """Create the header and grid widgets."""
        # Top Header Bar
        header = tk.Frame(
            self.root, bg=setting.COLOR_HEADER_BG, height=setting.HEADER_HEIGHT
        )
        header.pack(fill=tk.X, padx=15, pady=(15, 10))

        # Mine Counter
        self.lbl_mines = tk.Label(
            header,
            text=f"🚩 {self.engine.remaining_mines}",
            font=("Helvetica", 14, "bold"),
            fg=setting.COLOR_CELL_FLAGGED,
            bg=setting.COLOR_HEADER_BG,
            width=8,
            anchor=tk.W,
        )
        self.lbl_mines.pack(side=tk.LEFT, padx=10, pady=10)

        # Reset / Face Button
        self.btn_reset = tk.Button(
            header,
            text="🙂",
            font=("Helvetica", 16),
            width=3,
            command=self.reset_game,
            relief=tk.RAISED,
            bd=2,
            bg=setting.COLOR_CELL_HIDDEN,
        )
        self.btn_reset.pack(side=tk.LEFT, expand=True, pady=10)

        # Elapsed Timer
        self.lbl_timer = tk.Label(
            header,
            text="⏱ 00:00",
            font=("Helvetica", 14, "bold"),
            fg=setting.COLOR_TEXT_PRIMARY,
            bg=setting.COLOR_HEADER_BG,
            width=8,
            anchor=tk.E,
        )
        self.lbl_timer.pack(side=tk.RIGHT, padx=10, pady=10)

        # Grid Container Frame
        self.grid_frame = tk.Frame(
            self.root, bg=setting.COLOR_GRID_BG, bd=3, relief=tk.SUNKEN
        )
        self.grid_frame.pack(padx=15, pady=(0, 15))

        # Build Grid Buttons
        for r in range(self.engine.grid_size):
            for c in range(self.engine.grid_size):
                btn = tk.Button(
                    self.grid_frame,
                    width=3,
                    height=1,
                    font=("Helvetica", 12, "bold"),
                    bg=setting.COLOR_CELL_HIDDEN,
                    relief=tk.RAISED,
                    bd=2,
                )
                # Left Click -> Reveal
                btn.bind(
                    "<Button-1>", lambda event, x=r, y=c: self._on_left_click(x, y)
                )
                # Right Click -> Flag (Linux/Win Button-3, macOS Button-2)
                btn.bind(
                    "<Button-3>", lambda event, x=r, y=c: self._on_right_click(x, y)
                )
                btn.bind(
                    "<Button-2>", lambda event, x=r, y=c: self._on_right_click(x, y)
                )

                btn.grid(row=r, column=c, padx=1, pady=1)
                self.buttons[(r, c)] = btn

    def _start_timer(self) -> None:
        """Increment elapsed timer every second while game is active."""
        if self.engine.status == GameStatus.IN_PROGRESS:
            self.timer_seconds += 1
            self.lbl_timer.config(text=f"⏱ {format_timer(self.timer_seconds)}")
        self.timer_job = self.root.after(1000, self._start_timer)

    def _on_left_click(self, x: int, y: int) -> None:
        """Handle cell reveal action."""
        if self.engine.status in (GameStatus.WON, GameStatus.LOST):
            return

        status, revealed_coords = self.engine.reveal_cell(x, y)
        self.lbl_mines.config(text=f"🚩 {self.engine.remaining_mines}")

        for rx, ry in revealed_coords:
            btn = self.buttons[(rx, ry)]
            cell = self.engine.get_cell(rx, ry)

            if cell.is_mine:
                btn.config(text="💣", bg=setting.COLOR_CELL_MINE, relief=tk.SUNKEN)
            else:
                btn.config(relief=tk.SUNKEN, bg=setting.COLOR_CELL_REVEALED)
                if cell.adjacent_mines > 0:
                    color = setting.NUMBER_COLORS.get(cell.adjacent_mines, "#000000")
                    btn.config(text=str(cell.adjacent_mines), fg=color)
                else:
                    btn.config(text="")

        if status == GameStatus.LOST:
            self.btn_reset.config(text="😵")
            messagebox.showerror("Game Over", "BOOM! You clicked on a mine.")
        elif status == GameStatus.WON:
            self.btn_reset.config(text="😎")
            messagebox.showinfo(
                "Victory!",
                f"Congratulations! You cleared all mines in {format_timer(self.timer_seconds)}!",
            )

    def _on_right_click(self, x: int, y: int) -> None:
        """Handle cell flagging action."""
        if self.engine.status in (GameStatus.WON, GameStatus.LOST):
            return

        new_state = self.engine.toggle_flag(x, y)
        btn = self.buttons[(x, y)]

        if new_state == CellState.FLAGGED:
            btn.config(text="🚩", fg=setting.COLOR_CELL_FLAGGED)
        elif new_state == CellState.HIDDEN:
            btn.config(text="", fg="#000000")

        self.lbl_mines.config(text=f"🚩 {self.engine.remaining_mines}")

    def reset_game(self) -> None:
        """Reset board, timer, and UI for a new game."""
        self.engine.reset()
        self.timer_seconds = 0
        self.lbl_timer.config(text="⏱ 00:00")
        self.lbl_mines.config(text=f"🚩 {self.engine.remaining_mines}")
        self.btn_reset.config(text="🙂")

        for (r, c), btn in self.buttons.items():
            btn.config(
                text="",
                bg=setting.COLOR_CELL_HIDDEN,
                relief=tk.RAISED,
                state=tk.NORMAL,
                fg="#000000",
            )


def main() -> None:
    """Entry point for the Minesweeper application."""
    try:
        root = tk.Tk()
        _app = MinesweeperApp(root)
        root.mainloop()
    except tk.TclError as e:
        print(
            f"Tkinter display unavailable: {e}. If running in headless environment, run pytest test suite."
        )
        sys.exit(0)


if __name__ == "__main__":
    main()
