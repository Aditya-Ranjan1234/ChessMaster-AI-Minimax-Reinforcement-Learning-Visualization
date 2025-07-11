from pieces.piece import Piece
from pieces.rook import Rook
from pieces.bishop import Bishop
import pygame

white_queen = pygame.image.load("pieces/assets/White_Queen.png")
black_queen = pygame.image.load("pieces/assets/Black_Queen.png")
queens = [white_queen, black_queen]

# Piece Square Table
white_queen_eval_table = [
  -20, -10, -10, -5, -5, -10, -10, -20,
  -10, 0, 0, 0, 0, 0, 0, -10,
  -10, 0, 5, 5, 5, 5, 0, -10,
  -5, 0, 5, 5, 5, 5, 0, -5,
  0, 0, 5, 5, 5, 5, 0, -5,
  -10, 5, 5, 5, 5, 5, 0, -10,
  -10, 0, 5, 0, 0, 0, 0, -10,
  -20, -10, -10, -5, -5, -10, -10, -20
]

black_queen_eval_table = white_queen_eval_table[::-1]


class Queen(Piece):
  def __init__(self, row, col, color):
    super().__init__(row, col, color)
    self.valid_moves = []
    self.letter = "Q"

  def update_valid_moves(self, board):
    self.valid_moves = self.get_valid_moves(board)
    return self.valid_moves

  def get_valid_moves(self, board):
    diagonal_moves = Bishop.get_valid_moves(
      Bishop(self.row, self.col, self.color), board)
    straight_moves = Rook.get_valid_moves(
      Rook(self.row, self.col, self.color), board)

    return diagonal_moves + straight_moves
