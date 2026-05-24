from tkinter import E, Button, Frame, Label, Tk, W
from tkinter import font as tkfont

import setting
import utils
from board import Board
from cell import Cell


class TicTacToeApp:
    def __init__(self) -> None:
        self.board = Board()
        self.cells: list[Cell] = []
        self.scores = {setting.PLAYER_X: 0, setting.PLAYER_O: 0, "draw": 0}
        self.root = Tk()
        self.status_label: Label | None = None
        self.turn_badge: Label | None = None
        self.score_labels: dict[str, Label] = {}
        self._score_rows: list[Frame] = []
        self._score_name_labels: list[Label] = []
        self._resize_job: str | None = None
        self._layout_ready = False

        self._font_title = tkfont.Font(
            family=setting.FONT_FAMILY, size=setting.FONT_SIZE_TITLE, weight="bold"
        )
        self._font_subtitle = tkfont.Font(
            family=setting.FONT_FAMILY, size=setting.FONT_SIZE_SUBTITLE
        )
        self._font_status = tkfont.Font(
            family=setting.FONT_FAMILY, size=setting.FONT_SIZE_STATUS
        )
        self._font_badge = tkfont.Font(
            family=setting.FONT_FAMILY,
            size=setting.FONT_SIZE_BADGE,
            weight="bold",
        )
        self._font_score = tkfont.Font(
            family=setting.FONT_FAMILY, size=setting.FONT_SIZE_SCORE, weight="bold"
        )
        self._font_button = tkfont.Font(
            family=setting.FONT_FAMILY, size=setting.FONT_SIZE_BUTTON, weight="bold"
        )

        self._build_ui()
        self.root.bind("<Configure>", self._on_configure)
        self.root.after_idle(self._apply_scale)

    def _build_ui(self) -> None:
        root = self.root
        root.configure(bg=setting.BG_COLOR)
        root.minsize(setting.MIN_WIDTH, setting.MIN_HEIGHT)
        root.geometry(f"{setting.DEFAULT_WIDTH}x{setting.DEFAULT_HEIGHT}")
        root.title("Tic Tac Toe")
        root.resizable(True, True)

        root.grid_rowconfigure(0, weight=1)
        root.grid_columnconfigure(0, weight=1)

        self.container = Frame(root, bg=setting.BG_COLOR)
        self.container.grid(row=0, column=0, sticky="nsew")

        weights = (
            setting.LAYOUT_WEIGHT_HEADER,
            setting.LAYOUT_WEIGHT_STATUS,
            setting.LAYOUT_WEIGHT_BOARD,
            setting.LAYOUT_WEIGHT_FOOTER,
        )
        for row, weight in enumerate(weights):
            self.container.grid_rowconfigure(row, weight=weight)
        self.container.grid_columnconfigure(0, weight=1)

        self.header = Frame(self.container, bg=setting.BG_COLOR)
        self.header.grid(row=0, column=0, sticky="nsew")
        self.header.grid_rowconfigure(0, weight=1)
        self.header.grid_rowconfigure(2, weight=1)
        self.header.grid_columnconfigure(0, weight=1)

        self.title_label = Label(
            self.header,
            text="Tic Tac Toe",
            font=self._font_title,
            bg=setting.BG_COLOR,
            fg=setting.FG_TITLE,
        )
        self.title_label.grid(row=1, column=0)
        self.subtitle_label = Label(
            self.header,
            text="First to three in a row wins",
            font=self._font_subtitle,
            bg=setting.BG_COLOR,
            fg=setting.FG_SUBTITLE,
        )
        self.subtitle_label.grid(row=2, column=0, pady=(0, 0))

        self.status_row = Frame(self.container, bg=setting.BOARD_FRAME_BG)
        self.status_row.grid(row=1, column=0, sticky="nsew")
        self.status_row.grid_columnconfigure(1, weight=1)

        self.turn_badge = Label(
            self.status_row,
            text=self.board.current_player,
            font=self._font_badge,
            bg=setting.BG_COLOR,
            fg=self._player_color(self.board.current_player),
        )
        self.turn_badge.grid(row=0, column=0, sticky="ns")

        self.status_label = Label(
            self.status_row,
            text=self._status_text(),
            font=self._font_status,
            bg=setting.BOARD_FRAME_BG,
            fg=setting.FG_STATUS,
            anchor=W,
        )
        self.status_label.grid(row=0, column=1, sticky="nsew", padx=0)

        self.board_outer = Frame(self.container, bg=setting.BOARD_BORDER_COLOR)
        self.board_outer.grid(row=2, column=0, sticky="nsew")
        self.board_outer.grid_rowconfigure(0, weight=1)
        self.board_outer.grid_columnconfigure(0, weight=1)

        self.board_inner = Frame(self.board_outer, bg=setting.BOARD_FRAME_BG)
        self.board_inner.grid(row=0, column=0, sticky="nsew")
        self.board_inner.bind("<Configure>", self._on_section_resize)

        for i in range(setting.GRID_SIZE):
            self.board_inner.grid_rowconfigure(i, weight=1, uniform="cells")
            self.board_inner.grid_columnconfigure(i, weight=1, uniform="cells")

        self.cells = []
        for row in range(setting.GRID_SIZE):
            for col in range(setting.GRID_SIZE):
                cell = Cell(row, col)
                cell.create_btn_object(self.board_inner, self._on_cell_click)
                btn = cell.cell_btn_object
                if btn is None:
                    raise RuntimeError("Cell button was not created")
                btn.grid(column=col, row=row, sticky="nsew")
                self.cells.append(cell)

        self.footer = Frame(self.container, bg=setting.BG_COLOR)
        self.footer.grid(row=3, column=0, sticky="nsew")
        self.footer.grid_rowconfigure(0, weight=3)
        self.footer.grid_rowconfigure(1, weight=2)
        self.footer.grid_columnconfigure(0, weight=1)

        self.score_frame = Frame(self.footer, bg=setting.BG_COLOR)
        self.score_frame.grid(row=0, column=0, sticky="nsew")
        self.score_frame.grid_columnconfigure(0, weight=1)
        for i in range(3):
            self.score_frame.grid_rowconfigure(i, weight=1)

        self._build_score_row(self.score_frame, 0, setting.PLAYER_X, "X wins")
        self._build_score_row(self.score_frame, 1, "draw", "Draws")
        self._build_score_row(self.score_frame, 2, setting.PLAYER_O, "O wins")

        self.new_game_btn = Button(
            self.footer,
            text="New Game",
            font=self._font_button,
            bg=setting.BTN_NEW_GAME_BG,
            fg=setting.BTN_NEW_GAME_FG,
            activebackground=setting.BTN_NEW_GAME_ACTIVE,
            activeforeground=setting.BTN_NEW_GAME_FG,
            relief="flat",
            borderwidth=0,
            highlightthickness=0,
            cursor="hand2",
            command=self._new_game,
        )
        self.new_game_btn.grid(row=1, column=0, sticky="nsew")

    def _build_score_row(
        self, parent: Frame, grid_row: int, key: str, label_text: str
    ) -> None:
        row = Frame(parent, bg=setting.BG_COLOR)
        row.grid(row=grid_row, column=0, sticky="ew")
        row.grid_columnconfigure(0, weight=1)
        row.grid_columnconfigure(1, weight=1)
        self._score_rows.append(row)

        name_label = Label(
            row,
            text=label_text,
            font=self._font_score,
            bg=setting.BG_COLOR,
            fg=setting.FG_SUBTITLE,
            anchor=W,
        )
        name_label.grid(row=0, column=0, sticky="w")
        self._score_name_labels.append(name_label)
        score_label = Label(
            row,
            text="0",
            font=self._font_score,
            bg=setting.BG_COLOR,
            fg=(
                self._player_color(key)
                if key in (setting.PLAYER_X, setting.PLAYER_O)
                else setting.FG_STATUS
            ),
            anchor=E,
        )
        score_label.grid(row=0, column=1, sticky="e")
        self.score_labels[key] = score_label

    def _on_configure(self, event: object) -> None:
        if event.widget is not self.root:
            return
        self._schedule_scale()

    def _on_section_resize(self, event: object) -> None:
        if event.widget is not self.board_inner:
            return
        self._schedule_scale()

    def _schedule_scale(self) -> None:
        if self._resize_job is not None:
            self.root.after_cancel(self._resize_job)
        self._resize_job = self.root.after(50, self._apply_scale)

    def _apply_scale(self) -> None:
        self._resize_job = None
        self.root.update_idletasks()

        width = max(self.root.winfo_width(), setting.MIN_WIDTH)
        height = max(self.root.winfo_height(), setting.MIN_HEIGHT)
        board_h = self.board_inner.winfo_height()

        if board_h < 40:
            self._resize_job = self.root.after(50, self._apply_scale)
            return

        factor = utils.scale_factor(width, height)
        pad_outer = utils.scaled_size(28, factor)
        pad_section = utils.scaled_size(8, factor)
        pad_status_x = utils.scaled_size(16, factor)
        pad_status_y = utils.scaled_size(12, factor)
        pad_badge = utils.scaled_size(14, factor)
        pad_title_gap = utils.scaled_size(4, factor)
        pad_score_row = utils.scaled_size(4, factor)
        pad_btn = utils.scaled_size(12, factor)
        border = max(2, utils.scaled_size(2, factor))
        cell_gap = max(2, utils.scaled_size(setting.CELL_GAP, factor))
        board_pad = max(4, utils.scaled_size(8, factor))

        self.container.grid_configure(padx=pad_outer, pady=pad_outer)
        self.header.grid_configure(pady=(0, pad_section))
        self.title_label.grid_configure(pady=(0, pad_title_gap))
        self.status_row.grid_configure(
            padx=pad_status_x,
            pady=pad_section,
        )
        self.turn_badge.grid_configure(padx=(pad_status_x, pad_badge))
        self.status_label.grid_configure(padx=(0, pad_status_x))
        self.board_outer.grid_configure(pady=pad_section, padx=0)
        self.board_outer.configure(padx=border, pady=border)
        self.board_inner.grid_configure(padx=board_pad, pady=board_pad)
        self.footer.grid_configure(pady=(pad_section, 0))

        for score_row in self._score_rows:
            score_row.grid_configure(pady=pad_score_row)

        self.new_game_btn.grid_configure(padx=pad_btn, pady=pad_btn)

        for cell in self.cells:
            btn = cell.cell_btn_object
            if btn is not None:
                btn.grid_configure(padx=cell_gap, pady=cell_gap)

        self._scale_text_fonts()
        self._layout_ready = True

    def _scale_text_fonts(self) -> None:
        header_w = self.header.winfo_width()
        header_h = self.header.winfo_height()
        status_w = self.status_row.winfo_width()
        status_h = self.status_row.winfo_height()
        btn_w = self.new_game_btn.winfo_width()
        btn_h = self.new_game_btn.winfo_height()

        self._set_font(
            self._font_title,
            header_w,
            header_h,
            setting.FONT_TITLE_RATIO,
            widgets=[self.title_label],
        )
        self._set_font(
            self._font_subtitle,
            header_w,
            header_h,
            setting.FONT_SUBTITLE_RATIO,
            widgets=[self.subtitle_label],
        )
        self._set_font(
            self._font_status,
            status_w,
            status_h,
            setting.FONT_STATUS_RATIO,
            widgets=[self.status_label],
        )
        self._set_font(
            self._font_badge,
            status_h,
            status_h,
            setting.FONT_BADGE_RATIO,
            widgets=[self.turn_badge],
        )

        if self._score_rows:
            row = self._score_rows[0]
            score_size = utils.font_size_from_box(
                row.winfo_width(),
                row.winfo_height(),
                setting.FONT_SCORE_RATIO,
            )
            self._font_score.configure(size=score_size)
            score_widgets = list(self._score_name_labels) + list(self.score_labels.values())
            for widget in score_widgets:
                widget.configure(font=self._font_score)

        self._set_font(
            self._font_button,
            btn_w,
            btn_h,
            setting.FONT_BUTTON_RATIO,
            widgets=[self.new_game_btn],
        )

        for cell in self.cells:
            cell.scale_font_to_button()

    @staticmethod
    def _set_font(
        font: tkfont.Font,
        width: int,
        height: int,
        ratio: float,
        *,
        widgets: list[Label | Button],
    ) -> None:
        size = utils.font_size_from_box(width, height, ratio)
        font.configure(size=size)
        for widget in widgets:
            widget.configure(font=font)

    @staticmethod
    def _player_color(player: str) -> str:
        if player == setting.PLAYER_X:
            return setting.PLAYER_X_COLOR
        if player == setting.PLAYER_O:
            return setting.PLAYER_O_COLOR
        return setting.FG_STATUS

    def _status_text(self) -> str:
        if self.board.winner:
            return f"Player {self.board.winner} wins!"
        if self.board.is_draw:
            return "It's a draw — well played!"
        return f"Player {self.board.current_player}'s turn"

    def _update_status(self) -> None:
        if self.status_label is not None:
            self.status_label.configure(text=self._status_text())

        if self.turn_badge is not None and not self.board.game_over:
            player = self.board.current_player
            self.turn_badge.configure(
                text=player,
                fg=self._player_color(player),
            )
        elif self.turn_badge is not None and self.board.winner:
            self.turn_badge.configure(
                text=self.board.winner,
                fg=self._player_color(self.board.winner),
            )
        elif self.turn_badge is not None:
            self.turn_badge.configure(text="—", fg=setting.FG_SUBTITLE)

    def _update_scores(self) -> None:
        for key, label in self.score_labels.items():
            label.configure(text=str(self.scores[key]))

    def _on_cell_click(self, cell: Cell) -> None:
        if not self.board.place(cell.row, cell.col):
            return

        cell.set_symbol(self.board.grid[cell.row][cell.col])
        cell.scale_font_to_button()

        if self.board.game_over:
            self._end_game()
            return

        self._update_status()

    def _end_game(self) -> None:
        if self.board.winner:
            self.scores[self.board.winner] += 1
            self._highlight_winning_line()
        else:
            self.scores["draw"] += 1

        for cell in self.cells:
            cell.disable()
        self._update_scores()
        self._update_status()

    def _highlight_winning_line(self) -> None:
        line = self.board.winning_line
        if not line:
            return

        cells_by_pos = {(cell.row, cell.col): cell for cell in self.cells}
        for row, col in line:
            cells_by_pos[(row, col)].highlight_win()

    def _new_game(self) -> None:
        self.board.reset()
        for cell in self.cells:
            cell.reset()
        self._update_status()
        if self._layout_ready:
            self._scale_text_fonts()

    def run(self) -> None:
        self.root.mainloop()


def main() -> None:
    TicTacToeApp().run()


if __name__ == "__main__":
    main()
