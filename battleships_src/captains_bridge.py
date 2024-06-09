import tkinter as tk
from third_deck import BattleshipGame

class BattleshipApp:
    def __init__(self, root):
        self.root = root
        self.game = BattleshipGame()
        self.cursor_position = [0, 0]
        self.view_mode = 'ships'  # can be 'ships' or 'attacks'
        self.current_player = 'player1'  # Start with player1

        self.setup_ui()

    def setup_ui(self):
        self.root.title("Battleship Game")
        self.grid_frame = tk.Frame(self.root)
        self.grid_frame.pack()

        self.info_label = tk.Label(self.root, text="Use arrow keys to move, Enter to select")
        self.info_label.pack()

        self.switch_button = tk.Button(self.root, text="Switch View", command=self.switch_view)
        self.switch_button.pack()

        self.draw_grid()

        self.root.bind('<Up>', self.move_up)
        self.root.bind('<Down>', self.move_down)
        self.root.bind('<Left>', self.move_left)
        self.root.bind('<Right>', self.move_right)
        self.root.bind('<Return>', self.select_position)

    def draw_grid(self):
        for row in range(8):
            for col in range(8):
                if self.view_mode == 'ships':
                    value = self.game.get_board(self.current_player)[row][col]
                else:
                    value = self.game.get_attacks(self.current_player)[row][col]
                button = tk.Button(self.grid_frame, text=value, width=2, height=1)
                button.grid(row=row, column=col)
                if [row, col] == self.cursor_position:
                    button.config(bg='yellow')
                else:
                    button.config(bg='lightgray')

    def move_cursor(self, row_delta, col_delta):
        new_row = (self.cursor_position[0] + row_delta) % 8
        new_col = (self.cursor_position[1] + col_delta) % 8
        self.cursor_position = [new_row, new_col]
        self.draw_grid()

    def move_up(self, event):
        self.move_cursor(-1, 0)

    def move_down(self, event):
        self.move_cursor(1, 0)

    def move_left(self, event):
        self.move_cursor(0, -1)

    def move_right(self, event):
        self.move_cursor(0, 1)

    def select_position(self, event):
        row, col = self.cursor_position
        if self.view_mode == 'attacks':
            hit = self.game.attack(self.current_player, row, col)
            if hit:
                self.info_label.config(text=f"Hit at ({row}, {col})!")
            else:
                self.info_label.config(text=f"Miss at ({row}, {col}).")
            self.game.switch_turn()
            self.current_player = self.game.get_current_player()
        self.draw_grid()

    def switch_view(self):
        self.view_mode = 'attacks' if self.view_mode == 'ships' else 'ships'
        self.draw_grid()

if __name__ == "__main__":
    root = tk.Tk()
    app = BattleshipApp(root)
    root.mainloop()