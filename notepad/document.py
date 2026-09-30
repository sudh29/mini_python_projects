"""Decoupled text document model for Notepad application.

Manages text buffer content, file persistence, dirty state tracking,
cursor coordinates, and document statistics without GUI dependencies.
"""

from pathlib import Path


class NotepadDocument:
    """Represents a text document buffer with dirty-state tracking."""

    def __init__(self, initial_text: str = "", file_path: str | None = None):
        self._content = initial_text
        self.file_path = file_path
        self._saved_content = initial_text
        self.undo_stack: list[str] = []
        self.redo_stack: list[str] = []

    @property
    def content(self) -> str:
        return self._content

    @content.setter
    def content(self, new_text: str) -> None:
        if new_text != self._content:
            self.undo_stack.append(self._content)
            self.redo_stack.clear()
            self._content = new_text

    @property
    def is_dirty(self) -> bool:
        """Return True if content has unsaved modifications."""
        return self._content != self._saved_content

    @property
    def title(self) -> str:
        """Generate window title text based on file name and dirty status."""
        prefix = "*" if self.is_dirty else ""
        name = Path(self.file_path).name if self.file_path else "Untitled"
        return f"{prefix}{name} - Notepad"

    @property
    def line_count(self) -> int:
        return len(self._content.splitlines()) if self._content else 1

    @property
    def word_count(self) -> int:
        return len(self._content.split())

    @property
    def char_count(self) -> int:
        return len(self._content)

    def undo(self) -> str | None:
        """Revert to previous text buffer state."""
        if self.undo_stack:
            self.redo_stack.append(self._content)
            self._content = self.undo_stack.pop()
            return self._content
        return None

    def redo(self) -> str | None:
        """Re-apply previously undone text buffer state."""
        if self.redo_stack:
            self.undo_stack.append(self._content)
            self._content = self.redo_stack.pop()
            return self._content
        return None

    def open(self, file_path: str) -> str:
        """Load text from file path and mark buffer as clean."""
        p = Path(file_path)
        content = p.read_text(encoding="utf-8")
        self._content = content
        self._saved_content = content
        self.file_path = str(p.resolve())
        self.undo_stack.clear()
        self.redo_stack.clear()
        return self._content

    def save(self, file_path: str | None = None) -> bool:
        """Write buffer to disk and mark as clean."""
        target = file_path or self.file_path
        if not target:
            return False

        p = Path(target)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(self._content, encoding="utf-8")
        self.file_path = str(p.resolve())
        self._saved_content = self._content
        return True

    def calculate_line_col(self, char_index: int) -> tuple[int, int]:
        """Convert a 0-based character index into 1-based (line, column) tuple."""
        clamped = max(0, min(char_index, len(self._content)))
        before = self._content[:clamped]
        lines = before.split("\n")
        line_num = len(lines)
        col_num = len(lines[-1]) + 1
        return line_num, col_num
