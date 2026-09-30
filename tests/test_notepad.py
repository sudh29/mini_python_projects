"""Unit tests for Notepad document model and buffer manipulation."""

from pathlib import Path

import pytest

from notepad.document import NotepadDocument


@pytest.fixture
def empty_doc() -> NotepadDocument:
    """Fixture providing an empty NotepadDocument."""
    return NotepadDocument()


def test_initial_state(empty_doc: NotepadDocument):
    """Verify document initialization defaults."""
    assert empty_doc.content == ""
    assert empty_doc.file_path is None
    assert empty_doc.is_dirty is False
    assert empty_doc.title == "Untitled - Notepad"
    assert empty_doc.line_count == 1
    assert empty_doc.word_count == 0
    assert empty_doc.char_count == 0


def test_dirty_flag_and_title(empty_doc: NotepadDocument):
    """Verify modifying text triggers dirty flag and title indicator."""
    empty_doc.content = "Hello, world!"
    assert empty_doc.is_dirty is True
    assert empty_doc.title == "*Untitled - Notepad"


def test_document_statistics():
    """Verify line, word, and character counts."""
    doc = NotepadDocument("First line\nSecond line has five words\nThird")
    assert doc.line_count == 3
    assert doc.word_count == 8
    assert doc.char_count == len("First line\nSecond line has five words\nThird")


def test_save_and_open(tmp_path: Path):
    """Verify saving to disk and opening existing files."""
    file_path = tmp_path / "notes.txt"
    doc = NotepadDocument()
    doc.content = "Sample content to persist."
    assert doc.is_dirty is True

    # Save to file
    assert doc.save(str(file_path)) is True
    assert doc.is_dirty is False
    assert doc.title == "notes.txt - Notepad"
    assert file_path.read_text(encoding="utf-8") == "Sample content to persist."

    # Open into new document
    new_doc = NotepadDocument()
    loaded_text = new_doc.open(str(file_path))
    assert loaded_text == "Sample content to persist."
    assert new_doc.is_dirty is False
    assert new_doc.file_path == str(file_path.resolve())
    assert new_doc.title == "notes.txt - Notepad"


def test_undo_and_redo(empty_doc: NotepadDocument):
    """Verify linear undo and redo stack behavior."""
    empty_doc.content = "State 1"
    empty_doc.content = "State 2"
    empty_doc.content = "State 3"

    assert empty_doc.undo() == "State 2"
    assert empty_doc.undo() == "State 1"
    assert empty_doc.undo() == ""
    assert empty_doc.undo() is None  # Stack exhausted

    assert empty_doc.redo() == "State 1"
    assert empty_doc.redo() == "State 2"
    assert empty_doc.redo() == "State 3"
    assert empty_doc.redo() is None


def test_calculate_line_col():
    """Verify character offset conversion to 1-based (line, column)."""
    text = "Hello\nWorld\nPython"
    doc = NotepadDocument(text)

    # Index 0 is 'H' -> Line 1, Col 1
    assert doc.calculate_line_col(0) == (1, 1)
    # Index 4 is 'o' -> Line 1, Col 5
    assert doc.calculate_line_col(4) == (1, 5)
    # Index 6 is 'W' (after \n) -> Line 2, Col 1
    assert doc.calculate_line_col(6) == (2, 1)
    # Index 12 is 'P' (after \nWorld\n) -> Line 3, Col 1
    assert doc.calculate_line_col(12) == (3, 1)
