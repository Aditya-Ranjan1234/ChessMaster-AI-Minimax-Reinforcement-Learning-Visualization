import os
import torch as T
import numpy as np
import pygame
from chess import Chess
from learnings.ppo.ppo import PPO

# Settings (should match training)
HIDDEN_LAYERS = (2048,) * 4
EPOCHS = 100
BUFFER_SIZE = 64
BATCH_SIZE = 128
MODEL_DIR = "results/DoubleAgents"
MODEL_FILES = {"white": "white_ppo.pt", "black": "black_ppo.pt"}

# UI settings
DEFAULT_WINDOW_SIZE = 512
EVAL_BAR_HEIGHT = 40  # Height for evaluation breakdown area (now used globally)
LIGHT_SQUARE = (240, 217, 181)
DARK_SQUARE = (181, 136, 99)
BOARD_BORDER = (80, 60, 30)
SELECTED_COLOR = (255, 215, 0)
LAST_MOVE_COLOR = (120, 200, 255)
EVAL_BAR_BG = (230, 230, 230, 220)
PIECE_SYMBOLS = {0: ".", 1: "♟", 2: "♝", 3: "♞", 4: "♜", 5: "♛", 6: "♚"}  # Black pieces
PIECE_SYMBOLS_WHITE = {0: ".", 1: "♙", 2: "♗", 3: "♘", 4: "♖", 5: "♕", 6: "♔"}  # White pieces

# Piece values for evaluation
PIECE_VALUES = {1: 1, 2: 3, 3: 3, 4: 5, 5: 9, 6: 0}  # Pawn, Bishop/Knight, Rook, Queen, King

def evaluate_position(chess_env):
    """Evaluate the current position based on material and piece positions"""
    evaluation = 0
    # Material count
    for color in [0, 1]:  # Black, White
        for row in range(8):
            for col in range(8):
                piece = chess_env.board[color, row, col]
                if piece != 0:
                    value = PIECE_VALUES[piece]
                    # Add value for white, subtract for black
                    evaluation += value if color == 1 else -value
    return evaluation

def evaluate_position_breakdown(chess_env):
    """Return evaluation, and breakdown for both sides as dicts and a formula string."""
    white_counts = {k: 0 for k in PIECE_VALUES}
    black_counts = {k: 0 for k in PIECE_VALUES}
    white_total = 0
    black_total = 0
    for row in range(8):
        for col in range(8):
            wp = chess_env.board[1, row, col]
            bp = chess_env.board[0, row, col]
            if wp != 0:
                white_counts[wp] += 1
                white_total += PIECE_VALUES[wp]
            if bp != 0:
                black_counts[bp] += 1
                black_total += PIECE_VALUES[bp]
    evaluation = white_total - black_total
    return evaluation, white_counts, black_counts, white_total, black_total

def select_color():
    pygame.init()
    screen = pygame.display.set_mode((DEFAULT_WINDOW_SIZE, DEFAULT_WINDOW_SIZE))
    pygame.display.set_caption("Select Color")
    font = pygame.font.Font(None, 36)
    white_text = font.render("Play as White", True, (255, 255, 255))
    black_text = font.render("Play as Black", True, (255, 255, 255))
    white_rect = white_text.get_rect(center=(DEFAULT_WINDOW_SIZE // 2, DEFAULT_WINDOW_SIZE // 2 - 50))
    black_rect = black_text.get_rect(center=(DEFAULT_WINDOW_SIZE // 2, DEFAULT_WINDOW_SIZE // 2 + 50))
    running = True
    while running:
        screen.fill((0, 0, 0))
        screen.blit(white_text, white_rect)
        screen.blit(black_text, black_rect)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if white_rect.collidepoint(event.pos):
                    return 1  # WHITE
                if black_rect.collidepoint(event.pos):
                    return 0  # BLACK
    pygame.quit()

def move_to_action(chess_env, from_pos, to_pos, turn):
    # from_pos and to_pos are (row, col) tuples
    source_pos, possibles, actions_mask = chess_env.get_all_actions(turn)
    for idx, (src, dst, mask) in enumerate(zip(source_pos, possibles, actions_mask)):
        if not mask:
            continue
        if tuple(src) == from_pos and tuple(dst) == to_pos:
            return idx
    return None

def main():
    print("Welcome to Chess RL! Play against the trained PPO model.")
    human_color = select_color()  # 1 for white, 0 for black
    model_color = 1 - human_color
    model_file = MODEL_FILES["white" if model_color == 1 else "black"]
    model_path = os.path.join(MODEL_DIR, model_file)

    # Start in fullscreen
    pygame.init()
    pygame.font.init()
    info = pygame.display.Info()
    screen_width, screen_height = info.current_w, info.current_h
    board_size = min(screen_width, screen_height - EVAL_BAR_HEIGHT)
    cell_size = board_size // 8
    eval_bar_height = EVAL_BAR_HEIGHT
    window_size = board_size
    screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
    pygame.display.set_caption("Chess RL")

    # Create fonts based on cell size
    piece_font = pygame.font.SysFont('segoeuisymbol', cell_size - 8)
    eval_font = pygame.font.SysFont('arial', max(20, cell_size // 2))

    chess_env = Chess(window_size=window_size, max_steps=128, render_mode="human")
    chess_env.reset()

    # Dummy PPO for env and shape
    ppo = PPO(
        chess_env,
        hidden_layers=HIDDEN_LAYERS,
        epochs=EPOCHS,
        buffer_size=BUFFER_SIZE,
        batch_size=BATCH_SIZE,
    )
    # Load model
    device = ppo.device
    ppo = T.load(model_path, map_location=device)
    ppo.to(device)
    print(f"Loaded model from {model_path}")

    turn = 1  # White starts
    selected_piece = None
    running = True
    fullscreen = True
    while running and not chess_env.is_game_done():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    fullscreen = not fullscreen
                    if fullscreen:
                        screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
                    else:
                        screen = pygame.display.set_mode((window_size, window_size + eval_bar_height))
            if turn == human_color and event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if y < window_size:  # Only process clicks on the board
                    col, row = x // cell_size, 7 - (y // cell_size)
                    if selected_piece is None:
                        # Select piece
                        if chess_env.board[human_color, row, col] != 0:
                            selected_piece = (row, col)
                    else:
                        # Move piece
                        action = move_to_action(chess_env, selected_piece, (row, col), turn)
                        if action is not None:
                            rewards, done, infos = chess_env.step(action)
                            turn = 1 - turn
                        selected_piece = None
            if turn == model_color:
                # Model's turn
                state = chess_env.get_state(turn)
                _, _, actions_mask = chess_env.get_all_actions(turn)
                action, _, _ = ppo.take_action(state, actions_mask)
                rewards, done, infos = chess_env.step(action)
                turn = 1 - turn

        # Draw board border
        pygame.draw.rect(screen, BOARD_BORDER, (0, 0, board_size, board_size), 8, border_radius=12)

        # Draw the board
        for row in range(8):
            for col in range(8):
                color = LIGHT_SQUARE if (row + col) % 2 == 0 else DARK_SQUARE
                pygame.draw.rect(screen, color, (col * cell_size, row * cell_size, cell_size, cell_size))
                piece = chess_env.board[1, 7 - row, col]
                if piece != 0:
                    text = piece_font.render(PIECE_SYMBOLS_WHITE[piece], True, (0, 0, 0))
                    text_rect = text.get_rect(center=(col * cell_size + cell_size//2, row * cell_size + cell_size//2))
                    screen.blit(text, text_rect)
                piece = chess_env.board[0, row, col]
                if piece != 0:
                    text = piece_font.render(PIECE_SYMBOLS[piece], True, (0, 0, 0))
                    text_rect = text.get_rect(center=(col * cell_size + cell_size//2, row * cell_size + cell_size//2))
                    screen.blit(text, text_rect)
        # Highlight selected piece
        if selected_piece:
            row, col = selected_piece
            pygame.draw.rect(screen, SELECTED_COLOR, (col * cell_size, (7 - row) * cell_size, cell_size, cell_size), 5, border_radius=8)

        # --- PPO value head evaluation ---
        state = chess_env.get_state(turn)
        state_tensor = T.Tensor(state).unsqueeze(0).to(device)
        with T.no_grad():
            value = float(ppo.critic(state_tensor).item())
        # Calculate win probability (sigmoid-like, for display)
        win_prob = 1 / (1 + np.exp(-value * 2))  # scale for more contrast
        win_side = 'White' if value > 0 else ('Black' if value < 0 else 'Equal')
        win_percent = int(100 * win_prob) if value > 0 else int(100 * (1 - win_prob))
        # --- Evaluation Bar ---
        eval_bar_y = window_size + 10
        eval_bar_x = 10
        eval_bar_w = board_size - 20
        # Draw background
        s = pygame.Surface((eval_bar_w, EVAL_BAR_HEIGHT), pygame.SRCALPHA)
        s.fill(EVAL_BAR_BG)
        screen.blit(s, (eval_bar_x, eval_bar_y))
        # Draw colored bar
        if abs(value) < 0.1:
            bar_color = (180, 180, 180)
        elif value > 0:
            bar_color = (80, 200, 80)
        else:
            bar_color = (220, 80, 80)
        bar_width = int(eval_bar_w * win_prob)
        pygame.draw.rect(screen, bar_color, (eval_bar_x, eval_bar_y, bar_width, EVAL_BAR_HEIGHT), border_radius=10)
        # Draw evaluation text
        main_eval_font = pygame.font.SysFont('arial', max(28, cell_size // 2), bold=True)
        arrow = '↑' if value > 0.1 else ('↓' if value < -0.1 else '→')
        eval_text = f"{arrow} {win_side} {value:+.2f}  (Winning: {win_percent}%)"
        text = main_eval_font.render(eval_text, True, (30, 30, 30))
        text_rect = text.get_rect(center=(eval_bar_x + eval_bar_w // 2, eval_bar_y + EVAL_BAR_HEIGHT // 2))
        screen.blit(text, text_rect)

        # --- Live explanation of PPO evaluation logic ---
        explanation_lines = [
            "How is this evaluated?",
            "Input: Board state (flattened, from current player's perspective)",
            f"Input shape: {state.shape}  (showing first 16 values)",
            str(np.array2string(state[:16], separator=',')),
            "→ PPO Critic Network (neural net) → Output: Value",
            "Output: Expected return for the current player (higher = better)",
            "Positive: White is better, Negative: Black is better"
        ]
        # Draw explanation with semi-transparent background
        exp_bg_y = eval_bar_y + EVAL_BAR_HEIGHT + 8
        exp_bg_h = (eval_font.get_height() + 2) * len(explanation_lines) + 10
        exp_bg = pygame.Surface((eval_bar_w, exp_bg_h), pygame.SRCALPHA)
        exp_bg.fill((255, 255, 255, 180))
        screen.blit(exp_bg, (eval_bar_x, exp_bg_y))
        y_exp = exp_bg_y + 5
        for line in explanation_lines:
            text = eval_font.render(line, True, (80, 80, 80))
            screen.blit(text, (eval_bar_x + 8, y_exp))
            y_exp += eval_font.get_height() + 2

        # --- Turn indicator ---
        turn_text = "White's turn" if turn == 1 else "Black's turn"
        turn_font = pygame.font.SysFont('arial', max(24, cell_size // 2), bold=True)
        text = turn_font.render(turn_text, True, (40, 40, 120))
        screen.blit(text, (screen_width - 220, window_size + 18))
        pygame.display.flip()

    pygame.quit()
    chess_env.close()

if __name__ == "__main__":
    main() 