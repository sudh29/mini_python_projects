from __future__ import annotations

from collections.abc import Callable
from tkinter import Button, Event, Frame
from tkinter import font as tkfont

import setting
import utils


class Cell:
    def __init__(self, row: int, col: int) -> None:
        self.row = row
        self.col = col
        self.cell_btn_object: Button | None = None
        self._font = tkfont.Font(
            family=setting.FONT_FAMILY,
            size=setting.FONT_SIZE_CELL,
            weight="bold",
        )
        self._has_symbol = False
        self._win_highlighted = False

    def create_btn_object(self, location: Frame, on_click: Callable[[Cell], None]) -> None:
        btn = Button(
            location,
            font=self._font,
            text=setting.EMPTY,
            bg=setting.CELL_BG,
            fg=setting.FG_TITLE,
            activebackground=setting.CELL_HOVER_BG,
            activeforeground=setting.FG_TITLE,
            relief="flat",
            borderwidth=0,
            highlightthickness=0,
            cursor="hand2",
            command=lambda: on_click(self),
        )
        btn.bind("<Enter>", self._on_enter)
        btn.bind("<Leave>", self._on_leave)
        self.cell_btn_object = btn

    def scale_font_to_button(self) -> None:
        btn = self.cell_btn_object
        if btn is None:
            return
        size = utils.font_size_from_box(
            btn.winfo_width(),
            btn.winfo_height(),
            setting.FONT_CELL_RATIO,
            min_size=setting.FONT_SIZE_CELL_MIN,
            max_size=setting.FONT_SIZE_CELL_MAX,
        )
        self._font.configure(size=size)
        btn.configure(font=self._font)

    def _current_bg(self) -> str:
        if self._win_highlighted:
            return setting.WIN_HIGHLIGHT_BG
        if self.cell_btn_object is not None and str(self.cell_btn_object.cget("state")) == "disabled":
            if not self._has_symbol:
                return setting.CELL_DISABLED_BG
        return setting.CELL_BG

    def _on_enter(self, _event: Event[object]) -> None:
        btn = self.cell_btn_object
        if btn is None or self._has_symbol or str(btn.cget("state")) == "disabled":
            return
        btn.configure(bg=setting.CELL_HOVER_BG)

    def _on_leave(self, _event: Event[object]) -> None:
        btn = self.cell_btn_object
        if btn is None or self._has_symbol or str(btn.cget("state")) == "disabled":
            return
        btn.configure(bg=self._current_bg())

    def set_symbol(self, symbol: str) -> None:
        if self.cell_btn_object is None:
            return
        self._has_symbol = True
        fg = (
            setting.PLAYER_X_COLOR
            if symbol == setting.PLAYER_X
            else setting.PLAYER_O_COLOR
        )
        self.cell_btn_object.configure(
            text=symbol,
            fg=fg,
            bg=setting.CELL_BG,
            font=self._font,
        )

    def highlight_win(self) -> None:
        if self.cell_btn_object is not None:
            self._win_highlighted = True
            self.cell_btn_object.configure(
                bg=setting.WIN_HIGHLIGHT_BG,
                fg=setting.WIN_HIGHLIGHT_FG,
                font=self._font,
            )

    def reset(self) -> None:
        if self.cell_btn_object is None:
            return
        self._has_symbol = False
        self._win_highlighted = False
        self.cell_btn_object.configure(
            text=setting.EMPTY,
            bg=setting.CELL_BG,
            fg=setting.FG_TITLE,
            state="normal",
            font=self._font,
        )

    def disable(self) -> None:
        if self.cell_btn_object is None:
            return
        if not self._has_symbol:
            self.cell_btn_object.configure(
                state="disabled",
                bg=setting.CELL_DISABLED_BG,
                font=self._font,
            )
        else:
            self.cell_btn_object.configure(state="disabled", font=self._font)

    def __repr__(self) -> str:
        return f"Cell({self.row},{self.col})"
