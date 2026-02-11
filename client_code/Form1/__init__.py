from ._anvil_designer import Form1Template
from anvil import *
import anvil.users
import anvil.server

class Form1(Form1Template):
  def __init__(self, **properties):
    self.init_components(**properties)
    # 1. Force login immediately
    anvil.users.login_with_form()

    # 2. Initialize HAL 9000 logic state
    self.board = [[0 for _ in range(7)] for _ in range(6)]
    self.current_player = 1
    self.game_over = False

    # 3. Apply visual setup and slots immediately
    self.reset_board_ui()

  def reset_board_ui(self):
    """Turns all 42 buttons into empty white circles"""
    for r in range(6):
      for c in range(7):
        try:
          cell = getattr(self, f"cell_{r}_{c}")
          cell.background = "white"
          cell.text = ""
          cell.role = "circular" 
        except AttributeError:
          pass
          
    slot_buttons = [self.button_3, self.button_4, self.button_5, 
                    self.button_6, self.button_7, self.button_8, self.button_9]
    for btn in slot_buttons:
      btn.text = ""

    # Reset status message to HAL theme
    self.label_status.text = "I am ready to begin. Your move."
    self.label_status.foreground = "black"

  def column_click(self, **event_args):
    """Event handler for the 7 interactive 'drop' buttons above the board"""
    if self.game_over:
      return

    # Identify which column was clicked using the 'Tag' property
    col_index = event_args['sender'].tag

    if self.current_player == 1:
      row = self.get_lowest_empty_row(col_index)
      if row is not None:
        self.make_move(row, col_index, 1) # User Move (Red)

        if self.check_winner(1):
          self.label_status.text = "Congratulations. You have defeated HAL 9000-1."
          self.label_status.foreground = "red"
          self.game_over = True
          return

        # Prepare for HAL's response
        self.current_player = 2
        self.label_status.text = "HAL 9000-1 is calculating..."
        self.call_ai_on_aws()
      else:
        Notification("This column is full. Please try another.").show()

  def get_lowest_empty_row(self, col):
    """Finds the lowest available row in a column"""
    for r in range(5, -1, -1):
      if self.board[r][col] == 0:
        return r
    return None

  def make_move(self, row, col, player):
    """Updates internal matrix and enforces visual chips"""
    self.board[row][col] = player
    cell_name = f"cell_{row}_{col}"
    try:
      cell_component = getattr(self, cell_name)
      cell_component.background = "red" if player == 1 else "yellow"
      cell_component.text = ""
      cell_component.role = "circular" 
    except AttributeError:
      print(f"Error: Component {cell_name} not found.")

  def call_ai_on_aws(self):
    """Revised for Integrated CSS Eye"""
    # 2. START FLICKER: Add the thinking class to the header role
  # (Assuming your header component is named headline_1)
  self.headline_1.role = ["hal-header", "hal-thinking"]

  self.label_status.text = "HAL 9000-1 is calculating..."
  self.label_status.foreground = "orange"

  selected_bot = self.drop_down_opponent.selected_value
  try:
    ai_col = anvil.server.call('get_move', self.board, selected_bot) 
  except Exception as e:
    print(f"Server Error: {e}")
    ai_col = 0 

    # 3. STOP FLICKER: Remove the thinking class
  self.headline_1.role = "hal-header"

  row = self.get_lowest_empty_row(ai_col)
  if row is not None:
    self.make_move(row, ai_col, 2)
    if self.check_winner(2):
      self.label_status.text = "I'm afraid I can't let you win."
      self.label_status.foreground = "red"
      self.game_over = True
    else:
      self.label_status.text = "Your move."
      self.label_status.foreground = "black"
      self.current_player = 1

  def check_winner(self, player):
    """Scans the 6x7 board for four connecting pieces"""
    # Horizontal
    for r in range(6):
      for c in range(4):
        if all(self.board[r][c+i] == player for i in range(4)):
          return True
    # Vertical
    for r in range(3):
      for c in range(7):
        if all(self.board[r+i][c] == player for i in range(4)):
          return True
    # Diagonals
    for r in range(3, 6):
      for c in range(4):
        if all(self.board[r-i][c+i] == player for i in range(4)):
          return True
    for r in range(3):
      for c in range(4):
        if all(self.board[r+i][c+i] == player for i in range(4)):
          return True
    return False

  def btn_read_more_click(self, **event_args):
    """Navigate to the full technical report"""
    open_form('ReportPage')

  def restart_btn_click(self, **event_args):
    """Requirement #4: Fully resets the game state"""
    self.board = [[0 for _ in range(7)] for _ in range(6)]
    self.game_over = False
    self.current_player = 1
    self.reset_board_ui()
    Notification("Memory banks cleared. System restarted.").show()
