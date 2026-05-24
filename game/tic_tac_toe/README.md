# Tic-Tac-Toe

Two-player Tic-Tac-Toe with a Tkinter GUI. Players alternate placing **X** and **O** on a 3×3 board until someone wins or the game is a draw.

## Requirements

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) package manager
- Tkinter (usually included with Python; on Linux: `sudo apt install python3-tk`)

## Run

From this directory:

```bash
uv run main.py
```

Or:

```bash
uv run python main.py
```

## How to play

1. Player **X** goes first (shown in the turn badge).
2. Click an empty cell to place your mark — **X** is cyan, **O** is orange.
3. Get three in a row (horizontal, vertical, or diagonal) to win.
4. Session scores track wins and draws across rounds.
5. Click **New Game** to reset the board (scores are kept).

Resize the window to scale every section (header, status, board, scores, button), fonts, and spacing together. Minimum size is 380×480.

## Tests

```bash
uv run python -m unittest discover -s tests -v
```

## Project layout

| File        | Role                                      |
|-------------|-------------------------------------------|
| `main.py`   | Tkinter window, status bar, game loop     |
| `board.py`  | Grid state, turns, win/draw detection     |
| `cell.py`   | Board buttons and visual updates          |
| `setting.py`| Theme, fonts, colors, and size constants   |
| `utils.py`  | Window scale factor helpers                |
| `tests/`    | Unit tests for board logic                |
