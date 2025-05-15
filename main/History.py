# History.py
import copy

class History:
    def __init__(self, initial_board_state, initial_turn):
        self.history = []
        self.push(copy.deepcopy(initial_board_state), initial_turn)

    def push(self, board_snapshot, turn_snapshot_of_player_who_moved):
        self.history.append((board_snapshot, turn_snapshot_of_player_who_moved))

    def pop_last_move(self): 
        if len(self.history) > 1:
            return self.history.pop()
        return None 

    def get_last_state(self): 
        if self.history:
            return self.history[-1]
        return None

    def is_empty(self):
        return not self.history
    
    def can_undo(self):
        return len(self.history) > 1

    def reset(self):
        self.history = []

    # Utility to get the current board and turn without popping, if needed by other parts.
    # For undo, get_last_state after pop_last_move is the pattern.
    def get_current_board_and_turn(self):
        if not self.is_empty():
            return self.history[-1]
        return None, None # Or raise an exception