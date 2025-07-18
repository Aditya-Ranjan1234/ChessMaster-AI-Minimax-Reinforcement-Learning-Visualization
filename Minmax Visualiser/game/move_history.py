import pygame

pygame.font.init()
my_font = pygame.font.SysFont("calibri", 15)


class MoveHistory(object):
  def __init__(self):
    self.move_log = []
    self.letters = ["a", "b", "c", "d", "e", "f", "g", "h"]

  def get_file(self, col):
    return self.letters[col]

  def draw_move_log(self, window):
    # Draw First 50 Moves
    if 0 <= len(self.move_log) < 50:
      self.show_move_log(0, window)

    # Draw next 50
    elif 50 <= len(self.move_log) < 100:
      self.show_move_log(50, window)

    # Draw next 50
    elif 100 <= len(self.move_log) < 150:
      self.show_move_log(100, window)

  def show_move_log(self, start, window):
    move_list = []
    move_string = []
    text = my_font.render("".join(move_string), True, (0, 0, 0))

    for i in range(start, len(self.move_log)):
      move = str(i + 1) + "." + self.move_log[i] + ", "
      move_string.append(move)
      text = my_font.render("".join(move_string), True, (0, 0, 0))

      # Every 11th move added to move string, append it to move list
      if i != 0 and i % 11 == 0:
        move_list.append("".join(move_string))
        move_string = []
        text = my_font.render("".join(move_string), True, (0, 0, 0))

    if len(move_list) == 0:
      window.blit(text, (10, 490))

    elif len(move_list) > 0:
      for move_ind in range(len(move_list)):
        list_text = my_font.render(move_list[move_ind], True, (0, 0, 0))
        window.blit(list_text, (10, 490 + 20 * move_ind))

      window.blit(text, (10, 490 + 20 * len(move_list)))
