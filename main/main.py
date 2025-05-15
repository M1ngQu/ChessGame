# main.py

import tkinter as tk
from tkinter import messagebox # Import messagebox
from .Board import Board
from .Moving import MoveController
from .GameState import GameState
from .History import History

LABEL_SPACE = 30  # Space added for labels

def main():
    root = tk.Tk()
    root.title("ChessGame")

    # Increase canvas size to accommodate labels
    canvas_width = 640 + LABEL_SPACE
    canvas_height = 640 + LABEL_SPACE
    canvas = tk.Canvas(root, width=canvas_width, height=canvas_height)
    canvas.grid(row=0, column=0, columnspan=3)

    # Component: Turn display label
    turn_label = tk.Label(root, text="Turn: White", font=("Arial", 14))
    turn_label.grid(row=1, column=0, sticky="w", padx=(10, 0), pady=5)

    # Initialize components
    board = Board(canvas)
    game_state = GameState()
    history = History(board.board, game_state.turn)
    controller = MoveController(board, game_state, history)

    game_active = True # Flag to control if clicks are processed

    def set_game_active(is_active):
        nonlocal game_active
        game_active = is_active

    # Update display (board + turn)
    def update_display(status="continue"):
        nonlocal game_active # To modify game_active status
        board.draw()
        current_turn_player = game_state.get_current_player()
        turn_text_player = "White" if current_turn_player == "w" else "Black"
        
        base_turn_text = f"Turn: {turn_text_player}"
        final_message = ""
        title_message = "Game Information"

        if status == "check":
            turn_label.config(text=f"{base_turn_text} (Check!)")
        elif status == "checkmate":
            winner = "Black" if current_turn_player == 'w' else "White" # The player whose turn it WAS won
            final_message = f"Checkmate! {winner} wins!"
            turn_label.config(text=f"Game Over: {winner} wins!")
            set_game_active(False)
        elif status == "stalemate":
            final_message = "Stalemate! (No legal moves)"
            turn_label.config(text="Game Over: Stalemate")
            set_game_active(False)
        elif status == "white_king_captured":
            final_message = "Game Over! White king captured. Black wins!"
            turn_label.config(text=f"Game Over: {final_message}")
            set_game_active(False)
        elif status == "black_king_captured":
            final_message = "Game Over! Black king captured. White wins!"
            turn_label.config(text=f"Game Over: {final_message}")
            set_game_active(False)
        else: # "continue" or other unhandled
            turn_label.config(text=base_turn_text)

        if final_message:
            messagebox.showinfo(title_message, final_message)
            # Optionally unbind clicks here if game_active flag isn't sufficient
            # For now, the game_active flag in on_click should handle it.

    # Resign function
    def on_resign():
        nonlocal game_active
        if not game_active:
            messagebox.showinfo("Game Information", "The game has already ended.")
            return

        current_player_turn = game_state.get_current_player()
        winner_display_text = ""
        resign_message = ""

        if current_player_turn == "w": # White resigns
            winner_display_text = "Black"
            resign_message = f"White resigns. {winner_display_text} wins!"
        else: # Black resigns
            winner_display_text = "White"
            resign_message = f"Black resigns. {winner_display_text} wins!"
        
        turn_label.config(text=f"Game Over: {resign_message}")
        set_game_active(False)
        if controller: # Ensure controller exists
            controller.game_over = True # Also set controller's game_over flag
        messagebox.showinfo("Game Over", resign_message)

    # Mouse click event
    def on_click(event):
        nonlocal game_active
        if not game_active:
            messagebox.showinfo("Game Over", "Game has ended. Please reset the board to start a new game.")
            return

        row, col = board.get_cell(event)
        if row is not None and col is not None:
            status = controller.handle_click(row, col)
            if status: # if controller didn't return None (e.g. game was already over)
                 update_display(status)
            # if status is None, it means click was ignored, no need to update display

    # Undo move function
    def on_undo():
        controller.undo()
        set_game_active(True) # Game is active again after undo
        update_display() # Update with default "continue" status

    # Reset button function
    def reset_game():
        board.reset_board()
        game_state.turn = "w"
        history.reset()
        history.push(board.board, game_state.turn)
        controller.reset_game_state() # Reset the game_over flag in controller
        set_game_active(True) # Make game active
        update_display() # Update with default "continue" status

    # Create a Frame to hold the buttons
    button_frame = tk.Frame(root)
    button_frame.grid(row=1, column=2, sticky="e", padx=10)

    # Add Undo button to the Frame
    undo_button = tk.Button(button_frame, text="Undo", command=on_undo)
    undo_button.pack(side=tk.LEFT, padx=(0, 5)) # (left_margin, right_margin) -> add 5px margin on the right

    # Add Reset button to the Frame
    reset_button = tk.Button(button_frame, text="Reset Board", command=reset_game)
    reset_button.pack(side=tk.LEFT, padx=(5, 0)) # Add 5px margin on the left

    # Create and place Resign button (between turn_label and button_frame)
    resign_button = tk.Button(root, text="Resign", command=on_resign)
    resign_button.grid(row=1, column=1, sticky="w", padx=(0, 3), pady=5)
    
    canvas.bind("<Button-1>", on_click)

    update_display()
    root.mainloop()

if __name__ == "__main__":
    main()
