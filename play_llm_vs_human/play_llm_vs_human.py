import os
import sys
import datetime
import json
import chess
import chess.pgn
from state_tracking.state_tracker import ChessStateTracker
from state_tracking.local_llm import LocalLLM
# from state_tracking.groq_interface import GroqInterface  # Uncomment to use Groq LLM

LOG_DIR = os.path.dirname(os.path.abspath(__file__))


def algebraic_to_uci(board, move_str):
    """Convert algebraic notation (e.g., e5, Nf3, Qg1) to UCI if possible."""
    try:
        move = board.parse_san(move_str)
        return move.uci()
    except Exception:
        return None


def log_game(log_data):
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = os.path.join(LOG_DIR, f"terminal_log_llm_vs_human_{timestamp}.json")
    with open(log_path, 'w') as f:
        json.dump(log_data, f, indent=2)
    print(f"[LOG] Game saved to {log_path}")


def print_board_with_coords(board):
    # Print files
    print("    a b c d e f g h")
    print("   -----------------")
    for rank in range(8, 0, -1):
        row = f"{rank} | "
        for file in range(8):
            square = chess.square(file, rank - 1)
            piece = board.piece_at(square)
            row += (piece.symbol() if piece else '.') + ' '
        print(row + f"| {rank}")
    print("   -----------------")
    print("    a b c d e f g h\n")


def get_legal_moves_san(board):
    return [board.san(move) for move in board.legal_moves]


def main():
    print("\n=== Play Chess vs LLM (Terminal, No UI) ===\n")
    print("You will play against a local LLM (TinyLlama by default). Enter moves in algebraic notation (e.g., e5, Nf3, Qg1). Type 'resign' to quit.\n")

    tracker = ChessStateTracker()
    llm = LocalLLM()  # Or use GroqInterface()

    # Choose color
    while True:
        color = input("Play as (w)hite or (b)lack? ").strip().lower()
        if color in ['w', 'b']:
            break
        print("Please enter 'w' or 'b'.")
    human_is_white = (color == 'w')

    log_data = {
        'moves': [],
        'result': None,
        'start_time': str(datetime.datetime.now()),
        'llm_model': llm.name,
    }

    board = tracker.board
    move_num = 1
    while not board.is_game_over():
        print_board_with_coords(board)
        if (board.turn and human_is_white) or (not board.turn and not human_is_white):
            # Human's turn
            while True:
                move_str = input(f"Your move ({'White' if board.turn else 'Black'}): ").strip()
                if move_str.lower() == 'resign':
                    print("You resigned.")
                    log_data['result'] = '0-1' if board.turn else '1-0'
                    log_data['moves'].append({'move': 'resign', 'by': 'human'})
                    log_game(log_data)
                    return
                uci = algebraic_to_uci(board, move_str)
                if uci and chess.Move.from_uci(uci) in board.legal_moves:
                    tracker.make_move(uci)
                    log_data['moves'].append({'move': move_str, 'uci': uci, 'by': 'human'})
                    break
                else:
                    print("Invalid move. Please use standard notation (e.g., e5, Nf3, Qg1) and ensure the move is legal.")
                    print("Legal moves:", ', '.join(get_legal_moves_san(board)))
        else:
            # LLM's turn
            fen = board.fen()
            llm_result = llm.get_move(fen)
            move_uci = llm_result['move']
            llm_full_output = llm_result.get('raw_output', None) if isinstance(llm_result, dict) else None
            if move_uci is None:
                print("LLM failed to generate a move. You win!")
                log_data['result'] = '1-0' if board.turn else '0-1'
                break
            if chess.Move.from_uci(move_uci) not in board.legal_moves:
                if llm_full_output:
                    print(f"[DEBUG] LLM full output: {llm_full_output}")
                print(f"[DEBUG] LLM raw output: {move_uci}")
                print(f"LLM generated illegal move: {move_uci}. You win!")
                log_data['result'] = '1-0' if board.turn else '0-1'
                log_data['moves'].append({'move': move_uci, 'by': 'llm-illegal'})
                log_game(log_data)
                return
            tracker.make_move(move_uci)
            # Only now is the move on the board, so SAN is safe
            try:
                move_san = board.san(board.move_stack[-1])
            except Exception as e:
                print(f"[ERROR] Could not convert move to SAN: {e}")
                move_san = move_uci
            print(f"LLM ({'White' if board.turn else 'Black'}) plays: {move_san}")
            log_data['moves'].append({'move': move_san, 'uci': move_uci, 'by': 'llm'})
        move_num += 1

    print("\nGame over!")
    print(board.result())
    log_data['result'] = board.result()
    log_game(log_data)

if __name__ == "__main__":
    main() 