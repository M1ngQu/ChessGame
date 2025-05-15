import copy

# --- Basic movement rules specific to piece types ---
def is_valid_pawn_move(board, fr, fc, tr, tc, piece, target):
    direction = -1 if piece.islower() else 1  # White moves up (-1), Black moves down (+1)
    start_row = 6 if piece.islower() else 1
    dr, dc = tr - fr, tc - fc

    # Move one step forward
    if dc == 0 and dr == direction and board[tr][tc] == "":
        return True
    # Move two steps from starting position
    if dc == 0 and dr == 2 * direction and fr == start_row and board[fr + direction][fc] == "" and board[tr][tc] == "":
        return True
    # Capture
    if abs(dc) == 1 and dr == direction and target: # target ensures there is a piece at the target position
        return True
    return False

def is_valid_knight_move(fr, fc, tr, tc):
    dr, dc = abs(tr - fr), abs(tc - fc)
    return (dr, dc) in [(2, 1), (1, 2)]

def is_valid_king_move(fr, fc, tr, tc):
    # Does not handle castling or moving into check (handled by main is_valid_move)
    dr, dc = abs(tr - fr), abs(tc - fc)
    return (dr <= 1 and dc <= 1) and (dr != 0 or dc != 0)

def is_path_clear_horizontal(board, row, col1, col2):
    step = 1 if col2 > col1 else -1
    for c in range(col1 + step, col2, step):
        if board[row][c]: return False
    return True

def is_path_clear_vertical(board, col, row1, row2):
    step = 1 if row2 > row1 else -1
    for r in range(row1 + step, row2, step):
        if board[r][col]: return False
    return True

def is_path_clear_diagonal(board, fr, fc, tr, tc):
    dr = 1 if tr > fr else -1
    dc = 1 if tc > fc else -1
    for i in range(1, abs(tr - fr)):
        if board[fr + i * dr][fc + i * dc]: return False
    return True

def is_valid_rook_move(board, fr, fc, tr, tc):
    if fr == tr: return is_path_clear_horizontal(board, fr, fc, tc)
    if fc == tc: return is_path_clear_vertical(board, fc, fr, tr)
    return False

def is_valid_bishop_move(board, fr, fc, tr, tc):
    if abs(fr - tr) == abs(fc - tc): return is_path_clear_diagonal(board, fr, fc, tr, tc)
    return False

def is_valid_queen_move(board, fr, fc, tr, tc):
    if fr == tr: return is_path_clear_horizontal(board, fr, fc, tc)
    if fc == tc: return is_path_clear_vertical(board, fc, fr, tr)
    if abs(fr - tr) == abs(fc - tc): return is_path_clear_diagonal(board, fr, fc, tr, tc)
    return False

# --- Helper functions for attack and check detection ---
def get_king_position(board_array, player_color):
    """Finds the position of the king for the given player color."""
    king_piece = 'k' if player_color == 'w' else 'K' # White king 'k', Black king 'K'
    for r_idx, row in enumerate(board_array):
        for c_idx, piece_on_square in enumerate(row):
            if piece_on_square == king_piece:
                return r_idx, c_idx
    return None  # Should not happen in a valid game state

def _is_valid_move_for_attack_check(board, from_row, from_col, to_row, to_col, current_player_of_piece):
    """Internal helper: Can piece at (fr,fc) of current_player_of_piece attack square (tr,tc)?
       This does NOT check for self-check. It's purely about attack capability.
    """
    if not (0 <= from_row < 8 and 0 <= from_col < 8 and 0 <= to_row < 8 and 0 <= to_col < 8):
        return False

    piece = board[from_row][from_col]
    if not piece: return False

    # Check piece color matches current_player_of_piece (the attacker's color)
    if current_player_of_piece == "w" and not piece.islower(): return False
    if current_player_of_piece == "b" and not piece.isupper(): return False

    # For attack check, the target square can be empty or occupied by an opponent.
    # It cannot be occupied by a friendly piece (of the attacker).
    target_piece_on_square = board[to_row][to_col]
    if target_piece_on_square:
        is_target_friendly_to_attacker = (current_player_of_piece == 'w' and target_piece_on_square.islower()) or \
                                         (current_player_of_piece == 'b' and target_piece_on_square.isupper())
        if is_target_friendly_to_attacker:
            return False

    kind = piece.lower()

    if kind == "p": # Pawn attack logic is specific: diagonal one step
        direction = -1 if piece.islower() else 1 
        dr, dc = to_row - from_row, to_col - from_col
        return abs(dc) == 1 and dr == direction
    elif kind == "n": return is_valid_knight_move(from_row, from_col, to_row, to_col)
    elif kind == "b": return is_valid_bishop_move(board, from_row, from_col, to_row, to_col)
    elif kind == "r": return is_valid_rook_move(board, from_row, from_col, to_row, to_col)
    elif kind == "q": return is_valid_queen_move(board, from_row, from_col, to_row, to_col)
    elif kind == "k": return is_valid_king_move(from_row, from_col, to_row, to_col) 
    return False

def is_square_attacked(board_array, r_coord_to_check, c_coord_to_check, attacker_color):
    """Checks if a square (r_coord_to_check, c_coord_to_check) is attacked by any piece of attacker_color."""
    for r_idx, row_content in enumerate(board_array):
        for c_idx, piece_on_square in enumerate(row_content):
            if not piece_on_square: continue

            piece_owner_is_attacker = (attacker_color == 'w' and piece_on_square.islower()) or \
                                      (attacker_color == 'b' and piece_on_square.isupper())

            if piece_owner_is_attacker:
                if _is_valid_move_for_attack_check(board_array, r_idx, c_idx, r_coord_to_check, c_coord_to_check, attacker_color):
                    return True
    return False

def is_in_check(board_array, player_color_king_to_check):
    """Checks if the player_color_king_to_check's king is currently in check."""
    king_pos = get_king_position(board_array, player_color_king_to_check)
    if not king_pos:
        # This case should ideally not happen if a king is always on the board for each player.
        # However, if king_pos is None, the king is not on the board, so not in check.
        return False 
    
    opponent_color = 'b' if player_color_king_to_check == 'w' else 'w'
    return is_square_attacked(board_array, king_pos[0], king_pos[1], opponent_color)

# --- Main move validation function (this is the version actually called by the game engine) ---
def is_valid_move(board, from_row, from_col, to_row, to_col, current_player):
    """
    Validates if a move is legal according to chess rules, including:
    1. Basic piece movement and capture rules.
    2. The move does not leave the current player's own king in check.
    """
    # 1. Basic checks (boundaries, piece existence, own piece, not capturing own piece)
    if not (0 <= to_row < 8 and 0 <= to_col < 8 and 0 <= from_row < 8 and 0 <= from_col < 8):
        return False
    
    piece = board[from_row][from_col]
    if not piece:  # Moving an empty square
        return False
    
    # Check if the piece belongs to the current player
    if current_player == "w" and not piece.islower(): # White's turn, but piece is uppercase (Black)
        return False
    if current_player == "b" and not piece.isupper(): # Black's turn, but piece is lowercase (White)
        return False
    
    target = board[to_row][to_col]
    if target: # If target square is not empty
        is_target_friendly = (current_player == "w" and target.islower()) or \
                             (current_player == "b" and target.isupper())
        if is_target_friendly: # Cannot capture own piece
            return False

    # 2. Check basic movement/capture rules specific to piece type
    kind = piece.lower()
    basic_move_valid = False
    if kind == "p":
        basic_move_valid = is_valid_pawn_move(board, from_row, from_col, to_row, to_col, piece, target)
    elif kind == "n":
        basic_move_valid = is_valid_knight_move(from_row, from_col, to_row, to_col)
    elif kind == "k":
        basic_move_valid = is_valid_king_move(from_row, from_col, to_row, to_col)
    elif kind == "r":
        basic_move_valid = is_valid_rook_move(board, from_row, from_col, to_row, to_col)
    elif kind == "b":
        basic_move_valid = is_valid_bishop_move(board, from_row, from_col, to_row, to_col)
    elif kind == "q":
        basic_move_valid = is_valid_queen_move(board, from_row, from_col, to_row, to_col)
    else: # Unknown piece type
        return False

    if not basic_move_valid:
        return False

    # 3. Check if own king will be in check after this move
    # Create a temporary board to simulate the move
    temp_board = copy.deepcopy(board)
    temp_board[to_row][to_col] = piece  # Move the piece to the target position
    temp_board[from_row][from_col] = ""    # Clear the original position

    # If the current player's king is in check after simulating the move, this move is illegal
    if is_in_check(temp_board, current_player):
        return False

    return True # All checks passed, it's a legal move

# --- Get all legal moves, check for checkmate and stalemate ---
def get_all_legal_moves_for_player(board_array, player_color):
    """Generates all legal moves for the given player.
    A move is ((from_r, from_c), (to_r, to_c)).
    """
    legal_moves = []
    for r_idx, row_content in enumerate(board_array):
        for c_idx, piece_on_square in enumerate(row_content):
            if not piece_on_square: # Empty square
                continue

            # Check if the piece belongs to the current player
            piece_belongs_to_player = (player_color == 'w' and piece_on_square.islower()) or \
                                      (player_color == 'b' and piece_on_square.isupper())

            if piece_belongs_to_player:
                # Try moving this piece to all possible squares on the board
                for to_r in range(8):
                    for to_c in range(8):
                        if r_idx == to_r and c_idx == to_c: # Cannot move to the same square
                            continue
                        
                        # Use the main is_valid_move which includes self-check prevention
                        if is_valid_move(board_array, r_idx, c_idx, to_r, to_c, player_color):
                            legal_moves.append(((r_idx, c_idx), (to_r, to_c)))
    return legal_moves

def is_checkmate(board_array, player_color):
    """Checks if the given player is checkmated."""
    if not is_in_check(board_array, player_color):
        return False # Not in check, so cannot be checkmate
    
    # In check, see if there are any legal moves
    if not get_all_legal_moves_for_player(board_array, player_color): # No legal moves
        return True # In check and no legal moves = checkmate
    
    return False # In check but has legal moves

def is_stalemate(board_array, player_color):
    """Checks if the given player is stalemated."""
    if is_in_check(board_array, player_color): # If in check, it's not stalemate
        return False 
        
    # Not in check, see if there are any legal moves
    if not get_all_legal_moves_for_player(board_array, player_color): # No legal moves
        return True # Not in check and no legal moves = stalemate
        
    return False # Not in check and has legal moves
