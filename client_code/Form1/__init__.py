from ._anvil_designer import Form1Template
from anvil import *
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.users
import anvil.server


class Form1(Form1Template):
  def __init__(self, **properties):
    self.init_components(**properties)
    # Force the login form to appear immediately
    anvil.users.login_with_form()
    # Initialize a 6x7 board with 0s (empty)
    self.board = [[0 for _ in range(7)] for _ in range(6)]
    self.current_player = 1

  # This ONE function handles ALL column clicks
  def column_click(self, **event_args):
    # This identifies which button was clicked (e.g., 'cell_0_3')
    button_name = event_args['sender'].name
    col_index = int(button_name.split('_')[-1]) 

    if self.current_player == 1:
      row = self.get_lowest_empty_row(col_index)

      if row is not None:
        self.make_move(row, col_index, 1) # User Move
        self.current_player = 2

        # Now we tell the AI on AWS to move
        self.call_ai_on_aws()
      else:
        Notification("That column is full!").show()

  def get_lowest_empty_row(self, col):
    for r in range(5, -1, -1):
      if self.board[r][col] == 0:
        return r
    return None

  def make_move(self, row, col, player):
    # 1. Update the internal matrix
    self.board[row][col] = player
    # 2. Update the UI colors
    cell_name = f"cell_{row}_{col}"
    # This finds the button on your screen by its name string
    cell_component = getattr(self, cell_name)
    cell_component.background = "red" if player == 1 else "yellow"

  def call_ai_on_aws(self):
    # This sends your self.board matrix to the 'get_move' function on AWS
    ai_col = anvil.server.call('get_move', self.board) 

    row = self.get_lowest_empty_row(ai_col)
    if row is not None:
      self.make_move(row, ai_col, 2) # AI is Yellow
      self.current_player = 1
