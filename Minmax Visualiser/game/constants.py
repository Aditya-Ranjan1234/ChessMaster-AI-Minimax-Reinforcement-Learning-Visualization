import pygame

# The width and height of the window
width, height = 720, 640

# An 8 x 8 board is the standard size for chess
num_rows, num_cols = 8, 8

# The size of each square on the board
square_size = 640 // 8 - 20

# Brown theme
light_brown = (222, 184, 135)  # Light brown
dark_brown = (139, 69, 19)     # Dark brown
brown_theme = (light_brown, dark_brown)
themes = [brown_theme]

# Used for promotion menu
light_gray = (230, 230, 230)

# Remove background images and images list

function_names = [
    "evaluate_board",
    "get_all_moves",
    "order_moves",
    "simulate_move",
    "undo_move"
]