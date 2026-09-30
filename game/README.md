# 🎮 Python GUI Game Suite

> **Collection:** Desktop GUI Games in Python 3.12+  
> **Framework:** Standard Library `tkinter`  
> **Architecture:** Decoupled State Engines + Event-Driven Presentation  
> **Package Management:** `uv`  

---

## 1. Overview

The `game/` package contains three classic desktop arcade and puzzle games implemented in modern Python. Each game is designed with a **strict separation of concerns**: game rules, grid matrices, state mutations, and win/loss resolution exist as pure, headless Python engines that are 100% testable without a display server. The GUI layers render responsive Tkinter widgets with clean visual aesthetics.

---

## 2. Included Games

| Game | Directory | Description | Engine File | Test Suite |
|:---|:---|:---|:---|:---|
| **🐍 Snake** | [`snake_game/`](./snake_game/) | Real-time arcade snake with food growth, collision detection, scaling difficulty, and high score persistence. | [`snake_game/engine.py`](./snake_game/engine.py) | [`tests/test_snake_game.py`](../tests/test_snake_game.py) |
| **💣 Minesweeper** | [`minesweeper_game/`](./minesweeper_game/) | Classic puzzle with safe first-click, BFS zero-mine flood-fill cascade, flagging, and live timers. | [`minesweeper_game/engine.py`](./minesweeper_game/engine.py) | [`tests/test_minesweeper.py`](../tests/test_minesweeper.py) |
| **❌ Tic-Tac-Toe** | [`tic_tac_toe/`](./tic_tac_toe/) | Two-player grid game with dynamic score counters, win detection, turn indicators, and responsive scaling. | [`tic_tac_toe/board.py`](./tic_tac_toe/board.py) | [`tic_tac_toe/tests/test_board.py`](./tic_tac_toe/tests/test_board.py) |

---

## 3. Quick Start & Execution

All games can be launched using `uv` from the repository root:

```bash
# Run Snake Game
uv run python game/snake_game/main.py

# Run Minesweeper Game
uv run python game/minesweeper_game/main.py

# Run Tic-Tac-Toe Game
uv run python game/tic_tac_toe/main.py
```

### Running Automated Test Suite
All game engines include automated test suites that run headlessly in CI/CLI environments:

```bash
# Run all game tests
uv run pytest tests/test_snake_game.py tests/test_minesweeper.py game/tic_tac_toe/tests/
```

---

## 4. Key Architectural Patterns

1. **Decoupled Game State Engines:**
   - GUI controllers query deterministic methods (`engine.step()`, `engine.reveal_cell()`, `board.make_move()`).
   - Enables headless testing in Linux CI environments where no X11/Wayland display server is available.
2. **Cross-Platform Compatibility:**
   - Replaced Windows-only `ctypes.windll.user32.MessageBoxW` calls with standard `tkinter.messagebox` dialogs.
3. **Resilient Direction & Input Buffering:**
   - Prevents immediate 180° reversals in Snake when arrow keys are pressed in quick succession.
   - Prevents clicking on flagged cells in Minesweeper.
