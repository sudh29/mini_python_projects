"""Legacy compatibility layer for Minesweeper Cell.

Maps to the modern decoupled MinesweeperCell and MinesweeperEngine.
"""

from game.minesweeper_game.engine import CellState, MinesweeperCell

# Re-export modern classes for backwards compatibility
Cell = MinesweeperCell
__all__ = ["Cell", "CellState", "MinesweeperCell"]
