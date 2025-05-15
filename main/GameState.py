# GameState.py

class GameState:
    def __init__(self):
        self.turn = "w"  # w: White (lowercase pieces), b: Black (uppercase pieces)

    def switch_turn(self):
        self.turn = "b" if self.turn == "w" else "w"

    def get_current_player(self):
        return self.turn

    def is_own_piece(self, piece):
        if not piece:
            return False
        return piece.islower() if self.turn == "w" else piece.isupper()

    def is_enemy_piece(self, piece):
        if not piece:
            return False
        return piece.isupper() if self.turn == "w" else piece.islower()
