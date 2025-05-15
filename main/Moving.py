# Moving.py

from .Rules import is_valid_move, is_checkmate, is_stalemate, is_in_check
import copy

class MoveController:
    def __init__(self, board, game_state, history):
        self.board = board
        self.state = game_state
        self.history = history
        self.game_over = False

    def handle_click(self, row, col):
        if self.game_over:
            return None

        selected = self.board.selected
        piece = self.board.board[row][col]
        move_status = "continue"

        if selected:
            if selected == (row, col):
                self.board.selected = None
                return move_status

            from_r, from_c = selected
            current_player_making_move = self.state.get_current_player()
            
            # --- Diagnostic print for is_valid_move call ---
            # print(f"[Controller] Checking is_valid_move: piece {self.board.board[from_r][from_c]} from ({from_r},{from_c}) to ({row},{col}) for player {current_player_making_move}")
            
            if is_valid_move(self.board.board, from_r, from_c, row, col, current_player_making_move):
                # Store the piece at the destination square before moving
                captured_piece = self.board.board[row][col]

                # Promotion logic is handled within board.move_piece if it's a pawn reaching promotion rank
                # The actual move on the board anvas and internal representation
                self.board.move_piece(from_r, from_c, row, col, current_player_making_move)
                
                # If no king was captured, proceed with normal turn switching and other checks
                self.state.switch_turn()
                # History is pushed AFTER turn switch. It stores the board state and WHOMST turn it is now.
                self.history.push(copy.deepcopy(self.board.board), self.state.turn)
                self.board.selected = None

                # Check for check/checkmate/stalemate for the *next* player (whose turn it is now)
                current_player_whose_turn_it_is = self.state.get_current_player()
                if is_in_check(self.board.board, current_player_whose_turn_it_is):
                    if is_checkmate(self.board.board, current_player_whose_turn_it_is):
                        self.game_over = True
                        return "checkmate"
                    return "check"
                elif is_stalemate(self.board.board, current_player_whose_turn_it_is):
                    self.game_over = True
                    return "stalemate"
                
                return "continue" # Move was valid, game continues
            else:
                # --- Diagnostic print for invalid move ---
                print(f"[Controller] Invalid move determined for piece {self.board.board[from_r][from_c]} from ({from_r},{from_c}) to ({row},{col}) for player {current_player_making_move}. Board state:")
                for r_idx, r_val in enumerate(self.board.board):
                    print(f"Row {r_idx}: {r_val}")
                # --- End diagnostic print ---
                self.board.selected = None
        else:
            if self.state.is_own_piece(piece):
                self.board.selected = (row, col)
        
        return move_status

    def undo(self):
        if not self.history.can_undo():
            return
            
        self.history.pop_last_move() # Remove the last move state
        # The new top of history is the state to restore
        board_snapshot, turn_snapshot = self.history.get_last_state()
        
        # Ensure a deep copy is assigned to the board to prevent shared references
        self.board.board = copy.deepcopy(board_snapshot)
        self.state.turn = turn_snapshot
        self.board.selected = None
        self.game_over = False

    def reset_game_state(self):
        self.game_over = False
