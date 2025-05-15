import unittest
from unittest.mock import patch
from main.Board import Board, initial_board
from main.GameState import GameState
from main.History import History
from main.Moving import MoveController
from main.Rules import is_valid_move
import tkinter as tk

class DummyCanvas:
    def delete(self, *args, **kwargs): pass
    def create_rectangle(self, *args, **kwargs): pass
    def create_text(self, *args, **kwargs): pass


class TestPromotion(unittest.TestCase):
    @patch("main.Board.simpledialog.askstring")
    def test_promote_pawn_white(self, mock_askstring):
        mock_askstring.return_value = "q"
        board = Board(DummyCanvas())
        board.board[0][0] = "p"  # White pawn reaches the promotion rank
        board.promote_pawn(0, 0, "p")
        self.assertEqual(board.board[0][0], "q")  # White promotes to lowercase

    @patch("main.Board.simpledialog.askstring")
    def test_promote_pawn_black(self, mock_askstring):
        mock_askstring.return_value = "R"
        board = Board(DummyCanvas())
        board.board[7][7] = "P"  # Black pawn reaches the promotion rank
        board.promote_pawn(7, 7, "P")
        self.assertEqual(board.board[7][7], "R")  # Black promotes to uppercase

    @patch("main.Board.simpledialog.askstring")
    def test_promote_pawn_cancel(self, mock_askstring):
        mock_askstring.return_value = None
        board = Board(DummyCanvas())
        board.board[0][1] = "p"
        board.promote_pawn(0, 1, "p")
        self.assertEqual(board.board[0][1], "p")  # No promotion

if __name__ == '__main__':
    unittest.main()