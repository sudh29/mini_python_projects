# 💣 Python Minesweeper

> **Category:** Desktop GUI & Puzzle Game  
> **Framework:** Python standard library (`tkinter`)  
> **Architecture:** Decoupled State Engine (`engine.py`) + Event-Driven Button Grid (`main.py`)  
> **Package Management:** `uv`  

---

## 1. Overview & Features

A complete, cross-platform implementation of the classic logic puzzle **Minesweeper**, built with Python and `tkinter`. The application features a decoupled game engine, safe first-click mechanics, flood-fill recursive revealing, live mine tracking, and cross-platform alerts.

### Key Features
- **Safe First Click:** The board places mines only *after* the player makes their initial move, guaranteeing that the first clicked cell is never a mine.
- **Recursive Zero-Cascade:** Uncovering a cell with 0 adjacent mines automatically triggers a flood-fill algorithm (BFS) to reveal all contiguous safe territory.
- **Cross-Platform Compatibility:** Utilizes standard `tkinter.messagebox` dialogs, eliminating platform-specific `ctypes.windll` dependencies and supporting Linux, macOS, and Windows.
- **Flag Mechanics:** Right-click flags suspected mine locations and updates the live counter in real time.
- **Live Elapsed Timer:** Tracks game duration in `MM:SS` format.
- **Replay & Reset:** Reset button (`🙂`) allows starting a new game instantly without restarting the Python process.
- **Decoupled Architecture:** Game state, mine placement, and win/loss verification reside in `engine.py`, fully testable headlessly without an X11/Wayland display.

---

## 2. Directory Structure

```
game/minesweeper_game/
├── engine.py          # Pure game logic engine (MinesweeperEngine, CellState, GameStatus)
├── cell.py            # Backwards compatibility layer
├── main.py            # Tkinter GUI interface, header dashboard, and button grid
├── setting.py         # Window size, grid dimensions (8x8), mine counts, and color tokens
├── utils.py           # Timer formatter and geometry helpers
└── README.md          # Project documentation
```

---

## 3. Controls & Rules

| Input | Action |
|:---|:---|
| **Left Click** | Reveal the selected cell |
| **Right Click** | Toggle flag (`🚩`) on an unrevealed cell |
| **`🙂` Button** | Reset and start a new game |

### Objective
Uncover all safe cells without detonating any of the hidden mines. The numbers indicate how many mines are located in the 8 adjacent neighboring cells.

---

## 4. How to Run

### Interactive GUI Mode
From the repository root using `uv`:

```bash
uv run python game/minesweeper_game/main.py
```

Or from within the `game/minesweeper_game` directory:

```bash
cd game/minesweeper_game
python3 main.py
```

### Automated Headless Tests
The engine runs headlessly in automated test environments:

```bash
uv run pytest tests/test_minesweeper.py
```

---

## 5. Technical Specifications

- **Grid Dimensions:** 8 × 8 grid cells (64 total cells).
- **Mines Density:** 10 mines (~15.6% mine density, classic beginner level).
- **Cascade Algorithm:** Breadth-First Search (BFS) queue.
- **Color Standards:** Standard classic color hierarchy (1: Blue, 2: Green, 3: Red, 4: Purple, 5: Dark Red, 6: Teal).
