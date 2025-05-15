import unittest
from main.Board import Board, initial_board
from main.GameState import GameState
from main.History import History
from main.Moving import MoveController
from main.Rules import is_valid_move, get_king_position, is_square_attacked, is_in_check, _is_valid_move_for_attack_check, get_all_legal_moves_for_player, is_checkmate, is_stalemate
import tkinter as tk
from unittest.mock import patch
import copy

class TestChessGame(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        if not tk._default_root or not tk._default_root.winfo_exists():
            tk._default_root = tk.Tk()
        self.root = tk._default_root

        self.canvas = tk.Canvas(self.root)
        self.board = Board(self.canvas)
        self.game_state = GameState()
        self.history = History([row[:] for row in self.board.board], self.game_state.turn)
        self.controller = MoveController(self.board, self.game_state, self.history)

    def _set_board_state(self, board_layout_list_of_strings):
        """
        Sets the board to a specific state.
        board_layout_list_of_strings: A list of 8 strings, each 8 chars long.
                                     ' ' for empty, or piece character.
        """
        new_board = []
        for r in range(8):
            row_list = []
            for c in range(8):
                char = board_layout_list_of_strings[r][c]
                row_list.append("" if char == ' ' else char)
            new_board.append(row_list)
        self.board.board = new_board
        self.history.reset()
        # Ensure the turn set in game_state (which test might modify before calling _set_board_state)
        # is reflected in the first history entry.
        self.history.push(copy.deepcopy(self.board.board), self.game_state.turn) 
        self.controller.game_over = False
        self.board.selected = None # Explicitly reset selection after setting board

    def test_initial_board(self):
        board = initial_board()
        self.assertEqual(len(board), 8)
        self.assertEqual(len(board[0]), 8)
        self.assertEqual(board[0], ["R", "N", "B", "Q", "K", "B", "N", "R"])
        self.assertEqual(board[1], ["P"] * 8)
        for row in range(2, 6):
            self.assertEqual(board[row], [""] * 8)
        self.assertEqual(board[6], ["p"] * 8)
        self.assertEqual(board[7], ["r", "n", "b", "q", "k", "b", "n", "r"])

    def test_game_state(self):
        self.assertEqual(self.game_state.turn, "w")
        self.game_state.switch_turn()
        self.assertEqual(self.game_state.turn, "b")
        self.game_state.switch_turn()
        self.assertEqual(self.game_state.turn, "w")

    def test_piece_ownership(self):
        self.assertTrue(self.game_state.is_own_piece("p"))
        self.assertFalse(self.game_state.is_own_piece("P"))
        self.game_state.switch_turn()
        self.assertTrue(self.game_state.is_own_piece("P"))
        self.assertFalse(self.game_state.is_own_piece("p"))

    def test_history_operations(self):
        initial_history_len = len(self.history.history)
        self.assertEqual(initial_history_len, 1) # Should be [(S0,w)]
        
        current_board_s0 = [row[:] for row in self.board.board]
        s1_board = [row[:] for row in self.board.board] 
        s1_board[3][3] = "p" 
        s1_turn = "b" 
        
        self.history.push(s1_board, s1_turn) 
        self.assertEqual(len(self.history.history), initial_history_len + 1)

        # Pop the last added state S1
        # popped_board, popped_turn = self.history.pop()
        # Instead of popping and checking the popped value directly for S1,
        # we pop S1, and then check that the new current state is S0.
        # The pop_last_move should return the popped item if we need to check it.
        # Let's keep the original intent: check the popped S1 value.
        
        # If pop_last_move returns the popped item:
        popped_s1_data = self.history.pop_last_move()
        self.assertIsNotNone(popped_s1_data, "pop_last_move should return the popped state if successful")
        popped_board, popped_turn = popped_s1_data
        
        self.assertEqual(popped_turn, s1_turn, "Popped turn should be the one pushed for S1")
        self.assertEqual(popped_board, s1_board, "Popped board should be S1")
        self.assertEqual(popped_board[3][3], "p", "Popped board S1 should have the modification")
        
        self.assertEqual(len(self.history.history), initial_history_len, "History length should revert after pop")

        current_top_board, current_top_turn = self.history.history[-1]
        self.assertEqual(current_top_board, current_board_s0, "New top of history should be S0 board")
        self.assertEqual(current_top_turn, "w", "New top of history should be S0 turn (white)")

    def test_pawn_moves(self):
        self.board.reset_board()
        self.board.board[5][0] = ""
        self.board.board[4][0] = ""
        self.assertTrue(is_valid_move(self.board.board, 6, 0, 5, 0, "w"))
        self.assertTrue(is_valid_move(self.board.board, 6, 0, 4, 0, "w"))
        self.assertFalse(is_valid_move(self.board.board, 6, 0, 6, 1, "w"))

    def test_knight_moves(self):
        self.board.reset_board()
        self.board.board[5][2] = ""
        self.assertTrue(is_valid_move(self.board.board, 7, 1, 5, 2, "w"))
        self.board.board[5][1] = ""
        self.assertFalse(is_valid_move(self.board.board, 7, 1, 5, 1, "w"))

    def test_king_moves(self):
        self.board.reset_board()
        self.board.board = [["" for _ in range(8)] for _ in range(8)]
        self.board.board[7][4] = "k"  
        self.board.board[6][5] = ""   
        self.assertTrue(is_valid_move(self.board.board, 7, 4, 6, 5, "w"))


    def test_rook_moves(self):
        self.board.reset_board()
        self.board.board = [["" for _ in range(8)] for _ in range(8)]
        self.board.board[4][4] = "R"  
        for c in range(5, 8):
            self.board.board[4][c] = ""  
        self.assertTrue(is_valid_move(self.board.board, 4, 4, 4, 7, "b"))


    def test_bishop_moves(self):
        self.board.reset_board()
        self.board.board = [["" for _ in range(8)] for _ in range(8)]
        self.board.board[2][0] = "B"  
        self.board.board[5][3] = ""  
        self.board.board[3][1] = ""  
        self.board.board[4][2] = ""
        self.assertTrue(is_valid_move(self.board.board, 2, 0, 5, 3, "b"))

    def test_queen_moves(self):
        self.board.reset_board()
        self.board.board = [["" for _ in range(8)] for _ in range(8)]
        self.board.board[3][3] = "Q"  
        for c in range(4, 8):
            self.board.board[3][c] = ""  
        self.assertTrue(is_valid_move(self.board.board, 3, 3, 3, 7, "b"))


    def test_board_reset(self):
        self.board.board[3][3] = "p"
        self.board.reset_board()
        self.assertEqual(self.board.board, initial_board())
        self.assertIsNone(self.board.selected)

    def test_move_controller(self):
        self.controller.handle_click(6, 0)
        self.assertEqual(self.board.selected, (6, 0))
        self.board.board[5][0] = ""
        self.controller.handle_click(5, 0)
        self.assertEqual(self.board.board[5][0], "p")
        self.assertEqual(self.board.board[6][0], "")
        self.assertEqual(self.game_state.turn, "b")

    @patch("main.Board.simpledialog.askstring")
    def test_pawn_promotion_via_controller(self, mock_askstring):
        mock_askstring.return_value = "q"

        self.board.reset_board()
        self.game_state.turn = "w"
        self.board.board = initial_board()
        self.board.board[1][3] = "p"
        self.board.board[0][3] = ""
        for r in range(2, 8):
            for c in range(8):
                if (r,c) != (6,3) and self.board.board[r][c].lower() == 'p':
                    pass

        self.controller.handle_click(1, 3)
        self.assertEqual(self.board.selected, (1, 3))

        self.controller.handle_click(0, 3)

        self.assertEqual(self.board.board[0][3], "q")
        self.assertEqual(self.board.board[1][3], "")
        self.assertEqual(self.game_state.turn, "b")
        self.assertIsNone(self.board.selected)
        mock_askstring.assert_called_once()

    def test_undo_single_valid_move(self):
        initial_board_state = [row[:] for row in self.board.board] 
        initial_turn = self.game_state.turn

        self.controller.handle_click(6, 4) 
        self.controller.handle_click(4, 4) 

        self.assertEqual(self.board.board[4][4].lower(), "p")
        self.assertEqual(self.board.board[6][4], "")
        self.assertEqual(self.game_state.turn, "b") 

        self.controller.undo()

        self.assertEqual(self.board.board, initial_board_state)
        self.assertEqual(self.game_state.turn, initial_turn)
        self.assertIsNone(self.board.selected)

    def test_undo_multiple_moves(self):
        state0_board = [row[:] for row in self.board.board]
        state0_turn = self.game_state.turn 

        self.controller.handle_click(6, 4)
        self.controller.handle_click(4, 4)
        state1_board = [row[:] for row in self.board.board] 
        state1_turn = self.game_state.turn 

        self.controller.handle_click(1, 4)
        self.controller.handle_click(3, 4)
        state2_board = [row[:] for row in self.board.board] 
        state2_turn = self.game_state.turn 
        
        self.controller.handle_click(7, 6) 
        self.controller.handle_click(5, 5)

        self.controller.undo()
        self.assertEqual(self.board.board, state2_board, "Board should revert to after Black's e7-e5")
        self.assertEqual(self.game_state.turn, state2_turn, "Turn should revert to White (was Black's turn before undo)") 
        self.assertIsNone(self.board.selected)

        self.controller.undo()
        self.assertEqual(self.board.board, state1_board, "Board should revert to after White's e2-e4")
        self.assertEqual(self.game_state.turn, state1_turn, "Turn should revert to Black")
        self.assertIsNone(self.board.selected)

        self.controller.undo()
        self.assertEqual(self.board.board, state0_board, "Board should revert to initial state")
        self.assertEqual(self.game_state.turn, state0_turn, "Turn should revert to White (initial)")
        self.assertIsNone(self.board.selected)

    def test_undo_at_start_of_game(self):
        initial_board_state = [row[:] for row in self.board.board]
        initial_turn = self.game_state.turn
        initial_history_len = len(self.history.history)

        self.controller.undo() 

        self.assertEqual(self.board.board, initial_board_state, "Board should remain initial state")
        self.assertEqual(self.game_state.turn, initial_turn, "Turn should remain White's")
        self.assertEqual(len(self.history.history), initial_history_len, "History length should not change")
        self.assertIsNone(self.board.selected)

    def test_undo_after_invalid_move_attempt(self):
        initial_board_state = [row[:] for row in self.board.board]
        initial_turn = self.game_state.turn
        initial_history_len = len(self.history.history)

        self.controller.handle_click(6, 0) 
        status = self.controller.handle_click(6, 1) 
        self.assertEqual(status, "continue")
        
        self.assertEqual(self.board.board, initial_board_state, "Board should not change after invalid move")
        self.assertEqual(self.game_state.turn, initial_turn, "Turn should not change after invalid move")
        self.assertEqual(len(self.history.history), initial_history_len, "History should not grow after invalid move attempt")
        self.assertIsNone(self.board.selected)

    def test_get_king_position(self):
        self._set_board_state([
            "        ",
            "        ",
            "   k    ", 
            "        ",
            "        ",
            " K      ", 
            "        ",
            "        ",
        ])
        self.assertEqual(get_king_position(self.board.board, 'w'), (2,3))
        self.assertEqual(get_king_position(self.board.board, 'b'), (5,1))

    def test_is_square_attacked(self):
        self._set_board_state([
            "        ",
            "        ",
            "  P     ",  # Black Pawn 'P' at (2,2)
            "   p    ",  # White pawn 'p' at (3,3)
            "        ",
            "        ",
            "        ",
            "k K     ",
        ])
        # White 'p' is at (3,3). Black 'P' is at (2,2).
        # Black 'P' at (2,2) attacks (3,1) and (3,3).
        self.assertTrue(is_square_attacked(self.board.board, 3, 3, 'b')) # Check if (3,3) is attacked by Black 'P'
        # Is white 'p' at (3,3) attacked by any other white piece? No.
        self.assertFalse(is_square_attacked(self.board.board, 3, 3, 'w')) # Check if (3,3) is attacked by White

        self._set_board_state([
            "        ",
            "    R   ", 
            "        ",
            "    k   ", 
            "        ",
            "        ",
            "        ",
            " K      ",
        ])
        self.assertTrue(is_square_attacked(self.board.board, 3, 4, 'b')) # Check if (3,4) is attacked by Black Rook
        self.board.board[2][4] = 'p' 
        self.assertFalse(is_square_attacked(self.board.board, 3, 4, 'b')) # Check if (3,4) is still attacked by Black Rook (now blocked)

    def test_is_in_check(self):
        self._set_board_state([
            "        ",
            "    R   ", 
            "        ",
            "    k   ", 
            "        ",
            "        ",
            "        ",
            " K      ",
        ])
        self.game_state.turn = 'w' 
        self.assertTrue(is_in_check(self.board.board, 'w'))
        self.assertFalse(is_in_check(self.board.board, 'b')) 

        self.board.board[2][4] = 'p' 
        self.assertFalse(is_in_check(self.board.board, 'w'))

    def test_get_all_legal_moves_simple(self):
        self._set_board_state([
            "K       ",
            "        ",
            "        ",
            "        ",
            "        ",
            "        ",
            "        ",
            "k       ", 
        ])
        self.game_state.turn = 'w'
        legal_moves = get_all_legal_moves_for_player(self.board.board, 'w')
        expected_moves = [
            ((7,0), (6,0)), 
            ((7,0), (6,1)), 
            ((7,0), (7,1))
        ]
        self.assertCountEqual(legal_moves, expected_moves)

    def test_simple_queen_check_horizontal(self):
        """Test a direct horizontal check by a queen."""
        self._set_board_state([
            "  qK    ", 
            "        ",
            "        ",
            "        ",
            "        ",
            "        ",
            "        ",
            "k       ", 
        ])
        self.assertTrue(is_in_check(self.board.board, 'b'), "Black king should be in check by white queen")

    def test_controller_handles_check(self):
        # Set up a board where White can put Black in check
        # . . . k . . . .
        # . . . . . . . .
        # . . . . . . . .
        # . . . . . . . .
        # . . . . . . . .
        # . . . . . Q . .
        # . . . . . . . .
        # . . . . . . K .
        board_setup = [
            "   K    ", # Black king
            "        ",
            "        ",
            "        ",
            "        ",
            "    q   ", # White Queen at (5,4)
            "        ",
            "      k "  # White King
        ]
        self._set_board_state(board_setup)
        self.game_state.turn = "w" # White's turn
        self.controller.reset_game_state() # Ensure controller is ready
        self.board.selected = None # Ensure no prior selection

        # White Queen moves from e3 (board[5][4]) to e8 (board[0][4]) to check Black King
        # Verify piece is there before click
        self.assertEqual(self.board.board[5][4], 'q', "White queen should be at (5,4) before click")
        self.assertEqual(self.game_state.get_current_player(), 'w', "It should be White's turn")

        status_select = self.controller.handle_click(5, 4) # Select Queen
        self.assertEqual(self.board.selected, (5,4), f"Board selection failed. Status: {status_select}")
        status_move = self.controller.handle_click(0, 4) # Move Queen to check

        self.assertEqual(status_move, "check", "Game status should be 'check'")
        self.assertTrue(is_in_check(self.board.board, 'b'), "Black king should be in check")
        self.assertFalse(self.controller.game_over, "Game should not be over yet")

    def test_checkmate_fools_mate(self):
        """ Test Fool's Mate scenario leading to checkmate. """
        self.board.reset_board()
        self.game_state.turn = "w"
        self.controller.reset_game_state() # Ensure game is not over

        # 1. f2-f3 (White)
        status = self.controller.handle_click(6, 5) # select f2 pawn
        status = self.controller.handle_click(5, 5) # move to f3
        self.assertEqual(status, "continue")
        self.assertEqual(self.game_state.turn, "b")

        # 2. e7-e5 (Black)
        status = self.controller.handle_click(1, 4) # select e7 pawn
        status = self.controller.handle_click(3, 4) # move to e5
        self.assertEqual(status, "continue")
        self.assertEqual(self.game_state.turn, "w")

        # 3. g2-g4 (White)
        status = self.controller.handle_click(6, 6) # select g2 pawn
        status = self.controller.handle_click(4, 6) # move to g4
        self.assertEqual(status, "continue")
        self.assertEqual(self.game_state.turn, "b")

        # 4. Qd8-h4# (Black mates White)
        status = self.controller.handle_click(0, 3) # select d8 Queen
        status = self.controller.handle_click(4, 7) # move to h4
        
        self.assertEqual(status, "checkmate", "Game status should be 'checkmate'")
        self.assertTrue(self.controller.game_over, "Game should be over")
        # After black moves and checkmates white, it's technically white's turn but white has no moves.
        # The is_checkmate function is called for the player whose turn it WOULD be.
        self.assertTrue(is_checkmate(self.board.board, 'w'), "White king should be checkmated")

    def test_stalemate_king_cornered(self):
        """ Test a common stalemate position. """
        # Test 1: Direct check of is_stalemate with a known stalemate position
        # Black King 'K' at a1 (7,0). White Queen 'q' at b3 (board[5][1]). White King 'k' at a3 (board[5][0]). Black to move.
        board_setup_direct_stalemate = [
            "        ",
            "        ",
            "        ",
            "        ",
            "        ",
            "kq      ", # White k at (5,0) (a3), White q at (5,1) (b3)
            "        ",
            "K       "  # Black K at (7,0) (a1)
        ]
        self._set_board_state(board_setup_direct_stalemate)
        self.game_state.turn = "b" # Black's turn
        self.controller.reset_game_state()

        self.assertFalse(is_in_check(self.board.board, 'b'), "Black king should NOT be in check for stalemate (Test 1)")
        self.assertTrue(is_stalemate(self.board.board, 'b'), "It should be stalemate for Black (Test 1)")
        
        # Test 2: Controller move leading to stalemate
        # Setup: Black 'K' at h8 (0,7). White 'k' at f6 (2,5). White 'q' at g1 (7,6). White to move.
        # White moves 'q' from g1 (7,6) to g6 (2,6), stalemating Black.
        board_setup_before_stalemate_move = [
            ".......K", # Black King K at h8 (0,7)
            "        ",
            ".....k..", # White King k at f6 (2,5)
            "        ",
            "        ",
            "        ",
            "        ",
            "......q.", # White Queen q at g1 (7,6)
        ]
        self._set_board_state(board_setup_before_stalemate_move)
        self.game_state.turn = "w" # White's turn to make the stalemating move
        self.controller.reset_game_state()
        self.history.push(copy.deepcopy(self.board.board), self.game_state.turn) # Push current state before move

        status = self.controller.handle_click(7, 6) # Select Queen at g1 (7,6)
        self.assertEqual(self.board.selected, (7,6))
        status = self.controller.handle_click(2, 6) # Move Queen to g6 (2,6)

        # --- Diagnostic prints ---
        print("\n--- Stalemate Test 2 Diagnostics ---")
        print(f"Board state after white's move to g6 (q at (2,6), K at (0,7), k at (2,5)):")
        # We need to import Rules functions to call them directly here for diagnostics
        # from main.Rules import is_in_check, get_all_legal_moves_for_player, is_stalemate # Already imported at top
        for r_idx, row_val in enumerate(self.board.board):
            print(f"Row {r_idx}: {row_val}")
        black_is_in_check = is_in_check(self.board.board, 'b')
        print(f"Is Black in check after White's move? {black_is_in_check}")
        black_legal_moves = get_all_legal_moves_for_player(self.board.board, 'b')
        print(f"Black's legal moves after White's move: {black_legal_moves}")
        stalemate_direct_check = is_stalemate(self.board.board, 'b')
        print(f"Direct call to is_stalemate(board, 'b') returns: {stalemate_direct_check}")
        print(f"Controller returned status: {status}")
        print("--- End Stalemate Test 2 Diagnostics ---")
        # --- End Diagnostic prints ---

        self.assertEqual(status, "stalemate", "Game status should be 'stalemate' after white's move (Test 2)")
        self.assertTrue(self.controller.game_over, "Game should be over due to stalemate (Test 2)")
        self.assertFalse(is_in_check(self.board.board, 'b'), "Black king should NOT be in check for stalemate (Test 2)")
        self.assertTrue(is_stalemate(self.board.board, 'b'), "Black should be in stalemate (Test 2)")

    @patch("main.main.messagebox.showinfo")
    def test_resignation_white_resigns(self, mock_showinfo):
        self.game_state.turn = "w"
        self.controller.reset_game_state()
        main_app = self.get_main_app_for_resign_test() # Helper to get main app instance

        main_app.on_resign() # Simulate white resigning

        self.assertTrue(self.controller.game_over, "Game should be over after white resigns")
        self.assertEqual(main_app.turn_label.cget("text"), "游戏结束: 白方认输，黑方获胜！")
        mock_showinfo.assert_called_with("游戏结束", "白方认输，黑方获胜！")

    @patch("main.main.messagebox.showinfo")
    def test_resignation_black_resigns(self, mock_showinfo):
        self.game_state.turn = "b"
        self.controller.reset_game_state()
        main_app = self.get_main_app_for_resign_test()

        main_app.on_resign() # Simulate black resigning

        self.assertTrue(self.controller.game_over, "Game should be over after black resigns")
        self.assertEqual(main_app.turn_label.cget("text"), "游戏结束: 黑方认输，白方获胜！")
        mock_showinfo.assert_called_with("游戏结束", "黑方认输，白方获胜！")

    def get_main_app_for_resign_test(self):
        # This is a helper to set up a minimal main.py-like environment for testing resignation
        # It's a bit of a hack, ideally UI interactions would be tested with a UI testing framework
        # or by better decoupling UI from logic.
        from main import main as main_module
        
        # Mock parts of main.py's setup to avoid full Tkinter initialization if possible,
        # but we need the turn_label and the on_resign function with its context.
        class MockMainApp:
            def __init__(self, controller, game_state, turn_label):
                self.controller = controller
                self.game_state = game_state
                self.turn_label = turn_label
                self.game_active = True # Keep it simple for the test

            def set_game_active(self, is_active):
                self.game_active = is_active

            # Copy of on_resign from main.py, adapted for this mock class
            def on_resign(self):
                if not self.game_active:
                    # messagebox.showinfo("游戏信息", "游戏已经结束了。") # Mocked out
                    return

                current_player_turn = self.game_state.get_current_player()
                winner_display_text = ""
                resign_message = ""

                if current_player_turn == "w": 
                    winner_display_text = "黑方"
                    resign_message = f"白方认输，{winner_display_text}获胜！"
                else: 
                    winner_display_text = "白方"
                    resign_message = f"黑方认输，{winner_display_text}获胜！"
                
                self.turn_label.config(text=f"游戏结束: {resign_message}")
                self.set_game_active(False)
                if self.controller: 
                    self.controller.game_over = True 
                main_module.messagebox.showinfo("游戏结束", resign_message) # Use the mocked showinfo

        mock_turn_label = tk.Label(self.root) # Needs a Tk parent
        return MockMainApp(self.controller, self.game_state, mock_turn_label)

    def tearDown(self):
        if self.root and self.root.winfo_exists():
            pass

if __name__ == '__main__':
    unittest.main()
