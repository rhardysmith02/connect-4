from ._anvil_designer import Form1Template
from anvil import *
import anvil.users
import anvil.server

class Form1(Form1Template):
  def __init__(self, **properties):
    self.init_components(**properties)
    # Force login immediately
    anvil.users.login_with_form()
    # Initialize board: 0=empty, 1=User, 2=AI
    self.board = [[0 for _ in range(7)] for _ in range(6)]
    self.current_player = 1
    self.game_over = False

  def column_click(self, **event_args):
    """Event handler for all top-row buttons"""
    if self.game_over:
      return

    # Get the column index from the 'Tag' property
    col_index = event_args['sender'].tag 

    if self.current_player == 1:
      row = self.get_lowest_empty_row(col_index)
      if row is not None:
        self.make_move(row, col_index, 1) # User Move (Red)

        # Check if User won
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
    self.board[row][col] = player
    cell_name = f"cell_{row}_{col}"
    try:
      cell_component = getattr(self, cell_name)
      cell_component.background = "red" if player == 1 else "yellow"
      cell_component.text = "" 
    except AttributeError:
      print(f"Error: Component {cell_name} not found.")

  def call_ai_on_aws(self):
    # Requirement #3: Allow user to select the bot
    selected_bot = self.drop_down_1.selected_value

    # Send the board AND the bot choice to AWS
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
    """Scans the board for 4 in a row"""
    # Check horizontal
    for r in range(6):
      for c in range(4):
        if self.board[r][c] == player and self.board[r][c+1] == player and \
        self.board[r][c+2] == player and self.board[r][c+3] == player:
          return True

    # Check vertical
    for r in range(3):
      for c in range(7):
        if self.board[r][c] == player and self.board[r+1][c] == player and \
        self.board[r+2][c] == player and self.board[r+3][c] == player:
          return True

    # Check positively sloped diagonals
    for r in range(3, 6):
      for c in range(4):
        if self.board[r][c] == player and self.board[r-1][c+1] == player and \
        self.board[r-2][c+2] == player and self.board[r-3][c+3] == player:
          return True

    # Check negatively sloped diagonals
    for r in range(3):
      for c in range(4):
        if self.board[r][c] == player and self.board[r+1][c+1] == player and \
        self.board[r+2][c+2] == player and self.board[r+3][c+3] == player:
          return True

    return False

  def restart_btn_click(self, **event_args):
    # Reset internal board matrix
    self.board = [[0 for _ in range(7)] for _ in range(6)]
    self.game_over = False
    self.current_player = 1

    # Loop through buttons and reset to 'empty' color
    for r in range(6):
      for c in range(7):
        cell = getattr(self, f"cell_{r}_{c}")
        cell.background = "white" # Or #eeeeee for a light gray look
        cell.text = "" 

    Notification("Game reset! User (Red) goes first.").show()
