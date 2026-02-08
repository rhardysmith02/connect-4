from ._anvil_designer import Form1Template
from anvil import *
import anvil.users
import anvil.server

class Form1(Form1Template):
  def __init__(self, **properties):
    self.init_components(**properties)
    # 1. Force login
    anvil.users.login_with_form()

    # 2. Initialize logic
    self.board = [[0 for _ in range(7)] for _ in range(6)]
    self.current_player = 1
    self.game_over = False

    # 3. Apply visual setup immediately
    self.reset_board_ui()

  def reset_board_ui(self):
    """Turns all 42 buttons into empty white circles"""
    for r in range(6):
      for c in range(7):
        try:
          cell = getattr(self, f"cell_{r}_{c}")
          cell.background = "white"
          cell.text = ""
          cell.role = "circular" # Enforces the CSS role
        except AttributeError:
          pass

  def column_click(self, **event_args):
    if self.game_over:
      return

    col_index = event_args['sender'].tag 

    if self.current_player == 1:
      row = self.get_lowest_empty_row(col_index)
      if row is not None:
        self.make_move(row, col_index, 1) # User Move (Red)

        if self.check_winner(1):
          Notification("Congratulations! You beat the AI!").show()
          self.game_over = True
          return

        self.current_player = 2
        self.call_ai_on_aws()
      else:
        Notification("That column is full!").show()

  def get_lowest_empty_row(self, col):
    for r in range(5, -1, -1):
      if self.board[r][col] == 0:
        return r
    return None

  def make_move(self, row, col, player):
    """Updates matrix and enforces circular UI"""
    self.board[row][col] = player
    cell_name = f"cell_{row}_{col}"
    try:
      cell_component = getattr(self, cell_name)
      cell_component.background = "red" if player == 1 else "yellow"
      cell_component.text = ""
      cell_component.role = "circular" # Keep it circular after color change!
    except AttributeError:
      print(f"Error: Component {cell_name} not found.")

  def call_ai_on_aws(self):
    # Requirement #3: Bot selection
    selected_bot = self.drop_down_1.selected_value
    ai_col = anvil.server.call('get_move', self.board, selected_bot) 

    row = self.get_lowest_empty_row(ai_col)
    if row is not None:
      self.make_move(row, ai_col, 2)
      if self.check_winner(2):
        Notification("The AI won!").show()
        self.game_over = True
      else:
        self.current_player = 1

  def check_winner(self, player):
    # Horizontal check
    for r in range(6):
      for c in range(4):
        if self.board[r][c] == player and self.board[r][c+1] == player and \
        self.board[r][c+2] == player and self.board[r][c+3] == player:
          return True
    # Vertical check
    for r in range(3):
      for c in range(7):
        if self.board[r][c] == player and self.board[r+1][c] == player and \
        self.board[r+2][c] == player and self.board[r+3][c] == player:
          return True
    # Diagonal checks
    for r in range(3, 6):
      for c in range(4):
        if self.board[r][c] == player and self.board[r-1][c+1] == player and \
        self.board[r-2][c+2] == player and self.board[r-3][c+3] == player:
          return True
    for r in range(3):
      for c in range(4):
        if self.board[r][c] == player and self.board[r+1][c+1] == player and \
        self.board[r+2][c+2] == player and self.board[r+3][c+3] == player:
          return True
    return False

  def restart_btn_click(self, **event_args):
    self.board = [[0 for _ in range(7)] for _ in range(6)]
    self.game_over = False
    self.current_player = 1
    self.reset_board_ui()
    Notification("Game reset! User (Red) goes first.").show()
