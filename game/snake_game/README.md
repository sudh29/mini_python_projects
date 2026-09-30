# 🐍 Python Classic Snake Game

> **Category:** Desktop GUI & 2D Arcade Game  
> **Framework:** Python standard library (`tkinter`)  
> **Architecture:** Decoupled State Engine (`engine.py`) + Event-Driven Canvas GUI (`main.py`)  
> **Package Management:** `uv`  

---

## 1. Overview & Features

A modern, responsive implementation of the classic arcade game **Snake**, built using Python's built-in `tkinter` library. The application follows clean software engineering principles by decoupling pure game mechanics from visual presentation, enabling headless automated unit testing.

### Key Features
- **Modern Dark UI:** Custom slate color palette (`#0f172a`, sky blue snake, glowing rose food item) with grid lines and status banners.
- **Decoupled Architecture:** Game state, movement vectors, collision detection, and score tracking reside in `engine.py`, completely independent of Tkinter.
- **Dynamic Difficulty:** Snake speed scales progressively with score (tick delay decreases from 120ms to a minimum of 50ms).
- **Persistent High Score:** Automatic high score saving and loading across sessions via `.snake_highscore`.
- **Dual Control Scheme:** Supports standard **Arrow Keys** and **WASD**.
- **Self-Collision Safeguard:** Direction buffering prevents accidental 180-degree self-collisions when pressing arrow keys in rapid succession.
- **Lifecycle Controls:** Start, Pause, Resume, and Instant Restart without restarting the application.

---

## 2. Directory Structure

```
game/snake_game/
├── engine.py          # Pure game logic engine (SnakeGame, Point, Direction, StepResult)
├── main.py            # Tkinter Canvas rendering and keyboard event loop
├── setting.py         # Canvas dimensions, grid sizes, speeds, and color palette
├── utils.py           # Coordinate converters and high score persistence
└── README.md          # Project documentation
```

---

## 3. Controls & Gameplay

| Key | Action |
|:---|:---|
| `↑` or `W` | Move Up |
| `↓` or `S` | Move Down |
| `←` or `A` | Move Left |
| `→` or `D` | Move Right |
| `Space` | Start game / Pause / Resume |
| `R` | Restart game at any time |
| `Esc` | Exit application |

---

## 4. How to Run

### Interactive GUI Mode
From the repository root using `uv`:

```bash
uv run python game/snake_game/main.py
```

Or from within the `game/snake_game` directory:

```bash
cd game/snake_game
python3 main.py
```

### Automated Headless Tests
The engine runs headlessly in automated test environments:

```bash
uv run pytest tests/test_snake_game.py
```

---

## 5. Technical Specifications

- **Grid Dimensions:** 24 × 24 grid cells.
- **Canvas Size:** 600 × 600 pixels (25px per cell).
- **Initial Speed:** 120ms tick delay.
- **Max Speed:** 50ms tick delay.
- **Food Spawning:** Uniform pseudo-random distribution across available unoccupied cells.
