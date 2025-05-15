# Chess Game

A classic chess game implemented in Python with a graphical user interface using Tkinter.

## Features

*   Graphical chess board and pieces.
*   Standard chess rules enforced for piece movement.
*   Turn-based gameplay for two players (White and Black).
*   Detection of game states:
    *   Check
    *   Checkmate
    *   Stalemate
*   Pawn promotion: When a pawn reaches the opposite end of the board, it can be promoted to a Queen, Rook, Bishop, or Knight.
*   Undo move: Allows players to revert the last move.
*   Reset board: Resets the game to its initial state.
*   Resign game: Allows the current player to resign, granting victory to the opponent.
*   Piece display:
    *   Uses SVG images for pieces if `Pillow` and `CairoSVG` libraries are installed.
    *   Falls back to Unicode characters if image libraries are not available.

## Requirements

*   Python 3.x
*   Tkinter (usually included with Python standard library)
*   (Optional) For image display of pieces:
    *   `Pillow`
    *   `CairoSVG`

    You can install these optional libraries using pip:
    ```bash
    pip install Pillow CairoSVG
    ```

## How to Run

1.  Ensure you have Python 3 installed.
2.  Clone or download the project repository.
3.  Navigate to the project's root directory in your terminal.
4.  Run the game using the launcher script:
    ```bash
    python launch_chess.py
    ```
    This script will execute the main game module (`main/main.py`).

## Project Structure (Simplified)

```
chess/
├── launch_chess.py       # Main launcher script for the game
├── main/
│   ├── __init__.py
│   ├── main.py           # Main application, UI setup, game loop
│   ├── Board.py          # Board representation, drawing, piece loading
│   ├── Rules.py          # Chess rules, move validation, check/checkmate/stalemate logic
│   ├── Moving.py         # Handles move execution, click events
│   ├── GameState.py      # Manages game state (current turn, etc.)
│   ├── History.py        # Manages move history for undo functionality
│   └── image/            # Directory for SVG piece images
│       ├── Chess_bdt45.svg
│       ├── Chess_blt45.svg
│       ├── ... (other piece images)
├── tests/
│   ├── __init__.py
│   ├── test_pawn_promotion.py # Example test file
│   └── ... (other test files)
└── README.md             # This file
```

## Notes

*   If the optional image libraries (`Pillow`, `CairoSVG`) are not found, the game will display a warning in the console and use Unicode characters to represent chess pieces instead of images.
*   The game is designed for local two-player gameplay. 