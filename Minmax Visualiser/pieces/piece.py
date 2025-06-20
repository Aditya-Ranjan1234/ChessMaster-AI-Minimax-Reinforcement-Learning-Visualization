from game.constants import square_size


class Piece(object):
  def __init__(self, row, col, color):
    self.row = row
    self.col = col
    self.type = self.__class__.__name__
    self.color = color
    self.selected = False
    self.valid_moves = []

  def is_selected(self):
    return self.selected

  def move(self, row, col):
    self.row = row
    self.col = col

  def draw(self, window, image):
    window.blit(image, (self.col * square_size, self.row * square_size))
