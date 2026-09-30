"""Feature-rich Notepad Text Editor built with Python and Tkinter.

Features:
- Decoupled document buffer model in document.py for headless testing
- File operations: New, Open, Save, Save As
- Live word, character, line, and column position tracking
- Clean undo/redo support and unsaved changes confirmation dialog
- Keyboard shortcuts and cross-platform compatibility
"""

import sys
import tkinter as tk
from tkinter import filedialog, messagebox

try:
    from notepad.document import NotepadDocument
except ImportError:
    from document import NotepadDocument


class Notepad:
    """Tkinter-based GUI Notepad application."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.doc = NotepadDocument()
        self.root.title(self.doc.title)
        self.root.geometry("850x600")
        self.root.minsize(400, 300)

        # Create Text Area with scrollbar
        self.text_area = tk.Text(self.root, font=("Consolas", 12), undo=True)
        self.text_area.pack(fill=tk.BOTH, expand=1)

        self.scrollbar = tk.Scrollbar(self.text_area)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_area.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.text_area.yview)

        # Status Bar showing line, column, words, chars
        self.status_bar = tk.Label(
            self.root, text="Ln 1, Col 1 | Words: 0 | Chars: 0", anchor=tk.E, padx=10
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        self._create_menu_bar()
        self._bind_shortcuts()

        # Update status and title on text changes
        self.text_area.bind("<KeyRelease>", self._on_text_modified)
        self.text_area.bind("<ButtonRelease-1>", self._on_text_modified)

        # Window closing protocol
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def _create_menu_bar(self) -> None:
        """Create menu bar with File, Edit, and Help menus."""
        menu_bar = tk.Menu(self.root)
        self.root.config(menu=menu_bar)

        # File Menu
        file_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New", command=self.new_file, accelerator="Ctrl+N")
        file_menu.add_command(
            label="Open", command=self.open_file, accelerator="Ctrl+O"
        )
        file_menu.add_command(
            label="Save", command=self.save_file, accelerator="Ctrl+S"
        )
        file_menu.add_command(
            label="Save As", command=self.save_as_file, accelerator="Ctrl+Shift+S"
        )
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_closing)

        # Edit Menu
        edit_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(
            label="Undo", command=self.text_area.edit_undo, accelerator="Ctrl+Z"
        )
        edit_menu.add_command(
            label="Redo", command=self.text_area.edit_redo, accelerator="Ctrl+Y"
        )
        edit_menu.add_separator()
        edit_menu.add_command(
            label="Cut",
            command=lambda: self.root.focus_get().event_generate("<<Cut>>"),
            accelerator="Ctrl+X",
        )
        edit_menu.add_command(
            label="Copy",
            command=lambda: self.root.focus_get().event_generate("<<Copy>>"),
            accelerator="Ctrl+C",
        )
        edit_menu.add_command(
            label="Paste",
            command=lambda: self.root.focus_get().event_generate("<<Paste>>"),
            accelerator="Ctrl+V",
        )
        edit_menu.add_separator()
        edit_menu.add_command(
            label="Select All", command=self.select_all, accelerator="Ctrl+A"
        )

        # Help Menu
        help_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)

    def _bind_shortcuts(self) -> None:
        """Bind common keyboard shortcuts."""
        self.root.bind("<Control-n>", lambda _: self.new_file())
        self.root.bind("<Control-o>", lambda _: self.open_file())
        self.root.bind("<Control-s>", lambda _: self.save_file())
        self.root.bind("<Control-Shift-S>", lambda _: self.save_as_file())
        self.root.bind("<Control-a>", lambda _: self.select_all())

    def _sync_document(self) -> None:
        """Synchronize UI text area with underlying document model."""
        raw = self.text_area.get("1.0", "end-1c")
        self.doc.content = raw
        self.root.title(self.doc.title)

    def _on_text_modified(self, _event=None) -> None:
        """Handle content modification and cursor move."""
        self._sync_document()
        cursor = self.text_area.index(tk.INSERT)
        line, col = cursor.split(".")
        self.status_bar.config(
            text=f"Ln {line}, Col {int(col) + 1} | Words: {self.doc.word_count} | Chars: {self.doc.char_count}"
        )

    def new_file(self) -> None:
        """Create a new empty document, prompting if current document has unsaved changes."""
        if self.doc.is_dirty:
            resp = messagebox.askyesnocancel(
                "Unsaved Changes", "Save changes to current document first?"
            )
            if resp is None:
                return
            if resp:
                self.save_file()

        self.text_area.delete("1.0", tk.END)
        self.doc = NotepadDocument()
        self.root.title(self.doc.title)
        self._on_text_modified()

    def open_file(self) -> None:
        """Prompt user to open a text file from disk."""
        if self.doc.is_dirty:
            resp = messagebox.askyesnocancel(
                "Unsaved Changes", "Save changes to current document first?"
            )
            if resp is None:
                return
            if resp:
                self.save_file()

        file_path = filedialog.askopenfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
        )
        if file_path:
            try:
                content = self.doc.open(file_path)
                self.text_area.delete("1.0", tk.END)
                self.text_area.insert("1.0", content)
                self.root.title(self.doc.title)
                self._on_text_modified()
            except Exception as e:
                messagebox.showerror("Error Opening File", str(e))

    def save_file(self) -> bool:
        """Save document to existing path or trigger Save As."""
        if self.doc.file_path:
            self._sync_document()
            try:
                self.doc.save()
                self.root.title(self.doc.title)
                return True
            except Exception as e:
                messagebox.showerror("Error Saving File", str(e))
                return False
        return self.save_as_file()

    def save_as_file(self) -> bool:
        """Prompt user for target file path and save."""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
        )
        if file_path:
            self._sync_document()
            try:
                self.doc.save(file_path)
                self.root.title(self.doc.title)
                return True
            except Exception as e:
                messagebox.showerror("Error Saving File", str(e))
                return False
        return False

    def select_all(self, _event=None) -> str:
        """Select all text within editor."""
        self.text_area.tag_add(tk.SEL, "1.0", tk.END)
        self.text_area.mark_set(tk.INSERT, "1.0")
        self.text_area.see(tk.INSERT)
        return "break"

    def show_about(self) -> None:
        """Display About information dialog."""
        messagebox.showinfo(
            "About",
            "Python Notepad Application\nVersion 2.0\nBuilt with Python & Tkinter",
        )

    def on_closing(self) -> None:
        """Handle window close event with dirty buffer confirmation."""
        if self.doc.is_dirty:
            response = messagebox.askyesnocancel(
                "Unsaved Changes", "Do you want to save changes before closing?"
            )
            if response is None:
                return
            elif response:
                if not self.save_file():
                    return
        self.root.destroy()


def main() -> None:
    """Entry point for the Notepad application."""
    try:
        root = tk.Tk()
        _app = Notepad(root)
        root.mainloop()
    except tk.TclError as e:
        print(
            f"Tkinter display unavailable: {e}. To test headlessly, run:\n  uv run pytest tests/test_notepad.py"
        )
        sys.exit(0)


if __name__ == "__main__":
    main()
