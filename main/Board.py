# Board.py
import tkinter as tk
from tkinter import simpledialog
from .Rules import is_valid_move
import os # For path joining
import io   # For BytesIO for image data stream

# Attempt to import image libraries and set a flag
USE_IMAGES = True
try:
    from PIL import Image, ImageTk
    import cairosvg
except ImportError:
    USE_IMAGES = False
    print("--------------------------------------------------------------------------")
    print("Warning: Libraries Pillow or CairoSVG not found.")
    print("Chess pieces will be displayed as Unicode characters instead of images.")
    print("To display images, please install them: pip install Pillow CairoSVG")
    print("--------------------------------------------------------------------------")

# Unicode pieces (used as fallback or if USE_IMAGES is False)
unicode_pieces_map = {
    "r": "♖", "n": "♘", "b": "♗", "q": "♕", "k": "♔", "p": "♙",
    "R": "♜", "N": "♞", "B": "♝", "Q": "♛", "K": "♚", "P": "♟",
}

def initial_board():
    return [
        ["R", "N", "B", "Q", "K", "B", "N", "R"],
        ["P"] * 8,
        [""] * 8,
        [""] * 8,
        [""] * 8,
        [""] * 8,
        ["p"] * 8,
        ["r", "n", "b", "q", "k", "b", "n", "r"],
    ]

class Board:
    def __init__(self, canvas):
        self.canvas = canvas
        self.cell_size = 80
        self.colors = ["#EEEED2", "#769656"]
        self.board = initial_board()
        self.selected = None
        self.margin_left = 30  # Left margin for row numbers
        self.margin_top = 0    # Top margin (if column labels were at top, also set to 30)
        self.margin_bottom = 30 # Bottom margin for column labels
        # Label font
        self.label_font = ("Arial", 12)

        self.use_images_flag = USE_IMAGES
        self.pil_images = {}  # Will store PIL Image objects
        self.tk_piece_images = {} # Will store PhotoImage objects (cached)

        if self.use_images_flag:
            self.image_dir = "image" # Relative to project root (chess/)
            # Define target display size for pieces, slightly smaller than cell
            self.image_display_size = int(self.cell_size * 0.85)

            image_filenames = {}
            # White pieces (p, r, n, b, q, k)
            for char_lower in ["p", "r", "n", "b", "q", "k"]:
                image_filenames[char_lower] = f"Chess_{char_lower}lt45.svg"
            # Black pieces (P, R, N, B, Q, K)
            for char_upper_candidate in ["P", "R", "N", "B", "Q", "K"]:
                image_filenames[char_upper_candidate] = f"Chess_{char_upper_candidate}dt45.svg"

            for piece_char, filename in image_filenames.items():
                image_path = os.path.join(self.image_dir, filename)
                try:
                    # Convert SVG to PNG bytes, scaled to desired size
                    png_bytes = cairosvg.svg2png(
                        url=image_path, 
                        output_width=self.image_display_size, 
                        output_height=self.image_display_size
                    )
                    pil_image = Image.open(io.BytesIO(png_bytes))
                    # Ensure RGBA for transparency if needed, though cairosvg usually handles this
                    # pil_image = pil_image.convert("RGBA") 
                    self.pil_images[piece_char] = pil_image # Store PIL image first
                except FileNotFoundError:
                    print(f"Image Load Error: File not found - {image_path}. Piece '{piece_char}' may use fallback.")
                    # self.piece_images[piece_char] = None
                    self.pil_images[piece_char] = None # Explicitly mark as not loaded
                except Exception as e:
                    print(f"Image Load Error: Failed to load/process {image_path} for piece '{piece_char}': {e}")
                    # self.piece_images[piece_char] = None
                    self.pil_images[piece_char] = None
                    # Potentially disable images entirely if a critical error occurs during setup
                    # self.use_images_flag = False
                    # break

    def reset_board(self):
        self.board = initial_board()
        self.selected = None

    def draw(self):
        self.canvas.delete("all")
        
        for row_idx in range(8):
            for col_idx in range(8):
                x0 = self.margin_left + col_idx * self.cell_size
                y0 = self.margin_top + row_idx * self.cell_size
                center_x = x0 + self.cell_size / 2
                center_y = y0 + self.cell_size / 2
                
                color = self.colors[(row_idx + col_idx) % 2]
                self.canvas.create_rectangle(x0, y0, x0 + self.cell_size, y0 + self.cell_size, fill=color)

                piece_char_on_board = self.board[row_idx][col_idx]
                if piece_char_on_board:
                    drawn_as_image = False
                    if self.use_images_flag:
                        # Check cache for PhotoImage first
                        tk_img_obj = self.tk_piece_images.get(piece_char_on_board)
                        if not tk_img_obj:
                            # If not cached, try to create from PIL image
                            pil_img = self.pil_images.get(piece_char_on_board)
                            if pil_img:
                                try:
                                    tk_img_obj = ImageTk.PhotoImage(pil_img)
                                    self.tk_piece_images[piece_char_on_board] = tk_img_obj # Cache it
                                except Exception as e_tk:
                                    print(f"Tkinter PhotoImage creation error for {piece_char_on_board}: {e_tk}")
                                    # Potentially mark this piece_char as not displayable with image
                        
                        if tk_img_obj: # If PhotoImage exists (either cached or newly created)
                            self.canvas.create_image(center_x, center_y, image=tk_img_obj)
                            drawn_as_image = True
                    
                    if not drawn_as_image: # Fallback to Unicode character
                        self.canvas.create_text(center_x, 
                                                center_y, 
                                                text=unicode_pieces_map.get(piece_char_on_board, "?"), # Default to ? if somehow not in map 
                                                font=("Arial", 40))
        
        # Draw row numbers (8, 7, ..., 1 from top to bottom)
        for row_idx in range(8):
            label_text = str(8 - row_idx)
            x_pos = self.margin_left / 2
            y_pos = self.margin_top + row_idx * self.cell_size + self.cell_size / 2
            self.canvas.create_text(x_pos, y_pos, text=label_text, font=self.label_font)

        # Draw column labels (A, B, ..., H from left to right)
        board_height_pixels = 8 * self.cell_size
        for col_idx in range(8):
            label_text = chr(ord('A') + col_idx)
            x_pos = self.margin_left + col_idx * self.cell_size + self.cell_size / 2
            y_pos = self.margin_top + board_height_pixels + self.margin_bottom / 2
            self.canvas.create_text(x_pos, y_pos, text=label_text, font=self.label_font)

        # Highlight selection
        if self.selected:
            r, c = self.selected
            x0 = self.margin_left + c * self.cell_size
            y0 = self.margin_top + r * self.cell_size
            self.canvas.create_rectangle(x0, y0, x0 + self.cell_size, y0 + self.cell_size,
                                         outline="red", width=3)

    def get_cell(self, event):
        # Calculate click coordinates relative to the top-left of the main board area
        effective_x = event.x - self.margin_left
        effective_y = event.y - self.margin_top # self.margin_top is currently 0

        # Check if the click is within the valid column range of the board (considers left margin)
        if effective_x < 0 or effective_x >= 8 * self.cell_size:
            return None, None
        
        # Check if the click is within the valid row range of the board (considers top margin, and potential bottom label area)
        # Here it's assumed clicks must be within the 8x8 grid, not including the bottom label area
        if effective_y < 0 or effective_y >= 8 * self.cell_size:
            return None, None
            
        col = effective_x // self.cell_size
        row = effective_y // self.cell_size

        # Double-check that calculated row/col are within 0-7 (though above checks should ensure this)
        if 0 <= row < 8 and 0 <= col < 8:
            return row, col
        else:
            return None, None # Just in case

    def move_piece(self, from_row, from_col, to_row, to_col, current_player):
        """
        Move piece and handle Pawn Promotion
        """
        piece = self.board[from_row][from_col]
        target = self.board[to_row][to_col]

        # Normal move rules (does not include promotion logic directly here other than calling is_valid_move)
        if not is_valid_move(self.board, from_row, from_col, to_row, to_col, current_player):
            return False

        # Execute move
        self.board[to_row][to_col] = piece
        self.board[from_row][from_col] = ""

        # Check if promotion is needed (pawn reaches the last rank)
        if piece.lower() == "p" and (to_row == 0 or to_row == 7):
            self.promote_pawn(to_row, to_col, piece)

        return True

    def promote_pawn(self, row, col, pawn):
        """Handles pawn promotion"""
        new_piece = simpledialog.askstring("Pawn Promotion", "Promote to: (Q)ueen, (R)ook, (B)ishop, (N)ight")
        if not new_piece:
            return  # User cancelled
        new_piece = new_piece.lower()
        if new_piece not in ["q", "r", "b", "n"]:
            return  # Invalid choice

        # White uses lowercase, Black uses uppercase
        if pawn.islower():
            self.board[row][col] = new_piece  # White
        else:
            self.board[row][col] = new_piece.upper()  # Black
