import unittest

import setting
from board import WIN_LINES, Board, generate_win_lines


class BoardTests(unittest.TestCase):
    def test_win_lines_for_grid_size(self) -> None:
        size = setting.GRID_SIZE
        lines = generate_win_lines(size)
        self.assertEqual(len(lines), 2 * size + 2)
        self.assertEqual(lines, WIN_LINES)

    def test_alternating_turns(self) -> None:
        board = Board()
        self.assertTrue(board.place(0, 0))
        self.assertEqual(board.current_player, setting.PLAYER_O)
        self.assertTrue(board.place(1, 1))
        self.assertEqual(board.current_player, setting.PLAYER_X)

    def test_rejects_occupied_cell(self) -> None:
        board = Board()
        self.assertTrue(board.place(0, 0))
        self.assertFalse(board.place(0, 0))

    def test_rejects_out_of_bounds(self) -> None:
        board = Board()
        self.assertFalse(board.place(-1, 0))
        self.assertFalse(board.place(setting.GRID_SIZE, 0))

    def test_row_win(self) -> None:
        board = Board()
        moves = [(0, 0), (1, 0), (0, 1), (1, 1), (0, 2)]
        for row, col in moves:
            board.place(row, col)
        self.assertEqual(board.winner, setting.PLAYER_X)
        self.assertEqual(board.winning_line, ((0, 0), (0, 1), (0, 2)))

    def test_diagonal_win(self) -> None:
        board = Board()
        moves = [(0, 0), (0, 1), (1, 1), (0, 2), (2, 2)]
        for row, col in moves:
            board.place(row, col)
        self.assertEqual(board.winner, setting.PLAYER_X)
        self.assertEqual(board.winning_line, ((0, 0), (1, 1), (2, 2)))

    def test_draw(self) -> None:
        board = Board()
        moves = [
            (0, 0),
            (0, 1),
            (0, 2),
            (1, 1),
            (1, 0),
            (1, 2),
            (2, 1),
            (2, 0),
            (2, 2),
        ]
        for row, col in moves:
            board.place(row, col)
        self.assertIsNone(board.winner)
        self.assertTrue(board.is_draw)

    def test_no_moves_after_game_over(self) -> None:
        board = Board()
        for row, col in [(0, 0), (1, 0), (0, 1), (1, 1), (0, 2)]:
            board.place(row, col)
        self.assertFalse(board.place(2, 2))

    def test_reset(self) -> None:
        board = Board()
        board.place(0, 0)
        board.reset()
        self.assertEqual(board.current_player, setting.PLAYER_X)
        self.assertIsNone(board.winner)
        self.assertIsNone(board.winning_line)
        self.assertFalse(board.is_draw)
        self.assertTrue(board.place(0, 0))


if __name__ == "__main__":
    unittest.main()
