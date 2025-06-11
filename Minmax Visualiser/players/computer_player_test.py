import pygame
from pieces import pawn, knight, bishop, rook, queen, king
from game.profiler import Profiler
import requests
import json
import threading

# Global variable to store the root of the minimax tree for visualization
minimax_root_node = None

def send_minimax_tree_to_webapp(tree_data):
    try:
        # Ensure the Flask server is running on http://127.0.0.1:5000
        requests.post('http://127.0.0.1:5000/minimax_data', json=tree_data)
        # print("Minimax tree data sent to web app.")
    except requests.exceptions.ConnectionError:
        print("Could not connect to the Flask server. Make sure it's running at http://127.0.0.1:5000")
    except Exception as e:
        print(f"Error sending minimax data: {e}")


class Computer(object):
  WHITE = "White"
  BLACK = "Black"

  # Piece Evaluations from https://www.chessprogramming.org/Simplified_Evaluation_Function
  PIECE_TYPES = (pawn.Pawn, knight.Knight, bishop.Bishop, rook.Rook, queen.Queen, king.King)
  PIECE_EVALUATION_TABLES = {
    (WHITE, "Pawn"): (100, pawn.white_pawn_eval_table),
    (WHITE, "Knight"): (320, knight.white_knight_eval_table),
    (WHITE, "Bishop"): (330, bishop.white_bishop_eval_table),
    (WHITE, "Rook"): (500, rook.white_rook_eval_table),
    (WHITE, "Queen"): (900, queen.white_queen_eval_table),
    (WHITE, "King"): (20000, king.white_king_eval_table),

    (BLACK, "Pawn"): (100, pawn.black_pawn_eval_table),
    (BLACK, "Knight"): (320, knight.black_knight_eval_table),
    (BLACK, "Bishop"): (330, bishop.black_bishop_eval_table),
    (BLACK, "Rook"): (500, rook.black_rook_eval_table),
    (BLACK, "Queen"): (900, queen.black_queen_eval_table),
    (BLACK, "King"): (20000, king.black_king_eval_table),
  }

  def __init__(self, color, initial_depth=0):
    self.profiler = Profiler()
    self.color = color
    self.transposition_table = {}
    self.piece_value_cache = {}
    self.initial_depth = initial_depth

    # These values provide the user valuable information about the current state of the minimax search
    self.moves_evaluated = 0
    self.total_moves_found = 0
    self.current_best_evaluation = 0

  def minimax(self, board, game, depth, alpha, beta, max_player, node_data=None):
    """
    Implements the Minimax algorithm to calculate the move that would maximize the AI's positional evaluation.
    Includes alpha-beta pruning to reduce the size of the search tree and reduce redundant computations.
    """
    global minimax_root_node

    if node_data is None:
        # This is the root call, initialize the tree structure
        node_data = {"move": "Root", "evaluation": None, "pruned": False, "children": []}
        minimax_root_node = node_data

    if depth == 0 or game.game_over():
      evaluation = self.evaluate_board(board)
      node_data["evaluation"] = evaluation
      return evaluation, board

    best_move = None
    best_score = float("-inf") if max_player == self.WHITE else float("inf")
    other_player = self.BLACK if max_player == self.WHITE else self.WHITE

    all_moves = self.get_all_moves(board, game, max_player)
    # Only update total_moves_found for the root call
    if depth == self.initial_depth:
        self.total_moves_found += len(all_moves)

    for piece, move in all_moves:
      child_node_data = {
          "move": f"{piece.letter}{piece.col}{piece.row}->{move[1]}{move[0]}",
          "evaluation": None,
          "pruned": False,
          "children": []
      }
      node_data["children"].append(child_node_data)

      position = self.simulate_move(piece, board, game, move, max_player)
      self.draw_AI_calculations(game, piece, position)
      current_score, _ = self.minimax(position, game, depth - 1, alpha, beta, other_player, child_node_data)
      self.undo_move(board, game)

      if max_player == self.WHITE:
        if current_score > best_score:
          best_score = current_score
          best_move = (piece, move)
          alpha = max(alpha, best_score)

      if max_player == self.BLACK:
        if current_score < best_score:
          best_score = current_score
          best_move = (piece, move)
          beta = min(beta, best_score)

      self.current_best_evaluation = best_score
      child_node_data["evaluation"] = current_score

      # if beta <= alpha, it means that the maximizing player already has a move with a better outcome than the current branch's best possible outcome
      # this means that we can can prune this branch to reduce unneccessary computations since we know that the maximizing player will never choose this branch
      # ASIDE: alpha-beta pruning assumes that both players are making optimal moves to maximize or minimize their respective scores
      if beta <= alpha:
        child_node_data["pruned"] = True
        break

    node_data["evaluation"] = best_score
    
    if depth == self.initial_depth: # This is the top-level call
        # Send the entire minimax tree to the web app in a separate thread
        threading.Thread(target=send_minimax_tree_to_webapp, args=(minimax_root_node,)).start()

    return best_score, best_move

  def get_piece_value(self, piece):
    """
    Calculate the value of a piece using material and positional evaluation.
    """
    piece_key = (piece.color, piece.type, piece.row, piece.col)
    if piece_key in self.piece_value_cache:
      return self.piece_value_cache[piece_key]

    piece_material, piece_eval_table = self.PIECE_EVALUATION_TABLES[(piece_key[0], piece_key[1])]
    piece_index = (piece.row * 8) + piece.col
    piece_value = piece_material + piece_eval_table[piece_index]

    # cache this for future lookups
    self.piece_value_cache[piece_key] = piece_value
    return piece_value

  @Profiler.profile_function
  def evaluate_board(self, board):
    """
    Evaluate the board state, considering material and positional advantages.
    """
    position_eval = 0
    for row in board.board:
      for piece in row:
        if not piece:
          continue

        piece_key = (piece.color, piece.type, piece.row, piece.col)
        if piece_key not in self.piece_value_cache:
          self.piece_value_cache[piece_key] = self.get_piece_value(piece)

        if piece.color == self.BLACK:
          position_eval -= self.piece_value_cache[piece_key]
        else:
          position_eval += self.piece_value_cache[piece_key]

    return position_eval

  @Profiler.profile_function
  def get_all_moves(self, board, game, color):
    """
    Generates all possible moves for each piece that the player owns.
    """
    all_moves = []
    passive_moves = []
    moves_with_capture = []

    for piece in board.get_all_pieces(color):
      if isinstance(piece, pawn.Pawn):
        piece.update_valid_moves(board.board, game.move_history.move_log)
      else:
        piece.update_valid_moves(board.board)

      for row, col in piece.valid_moves:
        if board.board[row][col] != 0 and board.get_piece(row, col).color != color:
          moves_with_capture.append((piece, (row, col)))
        else:
          passive_moves.append((piece, (row, col)))

    moves_with_capture = self.order_moves(moves_with_capture, board.board)

    # by using move ordering and putting moves where the AI captured a piece first, we evaluate the moves
    # that are likely to be the strongest earlier in the search tree, making alpha-beta pruning more efficient.
    all_moves.extend(moves_with_capture)
    all_moves.extend(passive_moves)
    return all_moves

  @Profiler.profile_function
  def order_moves(self, moves, board):
    def mvv_lva(move):  # https://www.chessprogramming.org/MVV-LVA
      piece, (targetRow, targetCol) = move

      piece_key = (piece.color, piece.type, piece.row, piece.col)
      if piece_key not in self.piece_value_cache:
        self.piece_value_cache[piece_key] = self.get_piece_value(piece)
      
      target = board[targetRow][targetCol]
      target_key = (target.color, target.type, target.row, target.col)
      if target_key not in self.piece_value_cache:
        self.piece_value_cache[target_key] = self.get_piece_value(target)

      return self.piece_value_cache[target_key] - self.piece_value_cache[piece_key]

    return sorted(moves, key=mvv_lva, reverse=True)

  def draw_AI_calculations(self, game, piece, board):
    """
    If the user has enabled the visualize AI feature, show the current position that the AI is considering after every move.
    """
    self.moves_evaluated += 1

    if not game.board.show_AI_calculations:
      return

    if game.board.AI_speed == "Medium":
      pygame.time.delay(20)
    elif game.board.AI_speed == "Slow":
      pygame.time.delay(50)

    self.draw_moves(piece, game, board)

  @Profiler.profile_function
  def simulate_move(self, piece, board, game, move, color):
    """
    Simulates a move on the board.
    """
    target = board.get_piece(move[0], move[1])

    board.prev_square = (piece.row, piece.col)
    board.piece = piece
    board.target = (move[0], move[1])

    # Save state for undoing the move
    board.stored_moves.append({
      'piece': piece,
      'from': board.prev_square,
      'to': move,
      'captured': target,
      'can_castle': getattr(piece, 'can_castle', None),
      'en_passant_target': game.en_passant_target,
      'half_moves': game.half_moves,
      'full_moves': game.full_moves
    })

    # Update game state based on the move
    game.en_passant_target = None
    game.half_moves += 1
    game.full_moves += 1

    # Handle castling
    if isinstance(piece, king.King) and abs(piece.col - move[1]) == 2:
      rook_col = 7 if move[1] > piece.col else 0
      new_rook_col = 5 if move[1] > piece.col else 3
      rook = board.get_piece(piece.row, rook_col)
      board.move(rook, piece.row, new_rook_col)
      rook.can_castle = False

    # Handle en passant
    if isinstance(piece, pawn.Pawn) and abs(piece.row - move[0]) == 2:
      game.en_passant_target = (move[0] + 1 if piece.color == "Black" else move[0] - 1, move[1])

    elif isinstance(piece, pawn.Pawn) and move == game.en_passant_target:
      captured_pawn_row = piece.row
      if piece.color == "White":
        captured_pawn_row += 1
      else:
        captured_pawn_row -= 1
      board.board[captured_pawn_row][move[1]] = 0
      board.material.add_to_captured_pieces(target, board.material.captured_black_pieces if target.color == "Black" else board.material.captured_white_pieces)

    # Check for capture, reset half moves if capture occurs
    if target != 0:
      game.half_moves = 0
      board.material.add_to_captured_pieces(target, board.material.captured_black_pieces if target.color == "Black" else board.material.captured_white_pieces)

    # Check for pawn move, reset half moves if pawn moves
    if isinstance(piece, pawn.Pawn):
      game.half_moves = 0

    board.move(piece, move[0], move[1])
    piece.has_moved = True
    return board

  @Profiler.profile_function
  def undo_move(self, board, game):
    # Restore previous move data
    previous_move_data = board.stored_moves.pop()
    piece = previous_move_data['piece']
    from_pos = previous_move_data['from']
    to_pos = previous_move_data['to']
    captured_piece = previous_move_data['captured']
    original_can_castle = previous_move_data['can_castle']
    game.en_passant_target = previous_move_data['en_passant_target']
    game.half_moves = previous_move_data['half_moves']
    game.full_moves = previous_move_data['full_moves']

    # Restore piece to its original position
    board.board[from_pos[0]][from_pos[1]] = piece
    board.board[to_pos[0]][to_pos[1]] = 0
    piece.row, piece.col = from_pos[0], from_pos[1]

    # Restore captured piece if any
    if captured_piece != 0:
      if isinstance(piece, pawn.Pawn) and to_pos == game.en_passant_target:
        captured_pawn_row = piece.row
        if piece.color == "White":
          captured_pawn_row += 1
        else:
          captured_pawn_row -= 1
        board.board[captured_pawn_row][to_pos[1]] = captured_piece
      else:
        board.board[to_pos[0]][to_pos[1]] = captured_piece

    # Restore castling rights
    if original_can_castle is not None:
      piece.can_castle = original_can_castle

    # Restore castling (move rook back)
    if isinstance(piece, king.King) and abs(from_pos[1] - to_pos[1]) == 2:
      if to_pos[1] == 6:  # Kingside castle
        rook = board.get_piece(from_pos[0], 5)
        board.move(rook, from_pos[0], 7)
      elif to_pos[1] == 2:  # Queenside castle
        rook = board.get_piece(from_pos[0], 3)
        board.move(rook, from_pos[0], 0)

    # Remove captured piece from material list
    if captured_piece != 0:
      if captured_piece.color == "Black":
        board.material.captured_black_pieces.pop()
      else:
        board.material.captured_white_pieces.pop()

    board.prev_square = None
    board.piece = None
    board.target = None

  def draw_moves(self, piece, game, board):
    """
    This function was removed because it is only used for debugging the minimax algorithm.
    """
    pass

  def reset_visualizer_stats(self):
    self.moves_evaluated = 0
    self.total_moves_found = 0
    self.current_best_evaluation = 0

  def computer_move(self, game, move):
    game.board.previous_move = (move[0].row, move[0].col), move[1]
    game.board.material.update_advantages(game.board)
    game.board.move(move[0], move[1][0], move[1][1])
    move[0].has_moved = True
    game.update_game()
    game.check_game_status()

    self.profiler.print_profile_summary(self.moves_evaluated)
    self.profiler.reset_profiler()