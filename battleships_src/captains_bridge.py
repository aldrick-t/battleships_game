import tkinter as tk
from tkinter import simpledialog
from tkinter import ttk
from tkinter.ttk import Combobox, Style


from telegraph import BAUDRATES, SerialCommunicator
from utils import locate_ports
from third_deck import BattleshipGame

class BattleshipApp:
    def __init__(self, root):
        self.root = root
        self.game = BattleshipGame()
        self.cursor_position = [0, 0]
        self.view_mode = 'ships'  # can be 'ships' or 'attacks'
        self.current_player = 'player1'  # Start with player1
        self.opponent_type = None  # 'serial', 'lan', or 'web'

        self.setup_ui()

    def setup_ui(self):
        self.root.title("Battleship Game")

        self.grid_frame = tk.Frame(self.root)
        self.grid_frame.grid(row=1, column=0, columnspan=3)

        self.info_label = tk.Label(self.root, text="Use arrow keys to move, Enter to select")
        self.info_label.grid(row=0, column=0, columnspan=3, pady=5)

        self.switch_button = tk.Button(self.root, text="Switch View", command=self.switch_view)
        self.switch_button.grid(row=2, column=0, padx=5, pady=5)

        self.opponent_label = tk.Label(self.root, text="Select Connection:")
        self.opponent_label.grid(row=3, column=1, padx=5, pady=5)

        self.opponent_combobox = ttk.Combobox(self.root, values=["serial", "lan", "web"])
        self.opponent_combobox.grid(row=3, column=2, padx=5, pady=5)

        self.connect_button = tk.Button(self.root, text="Select", command=self.select_opponent)
        self.connect_button.grid(row=3, column=3, padx=5, pady=5)
        
        self.serial_label = tk.Label(self.root, text="Serial Connections:")
        self.serial_label.grid(row=4, column=0, padx=5, pady=5)
        
        self.refresh_serial_devices_button: tk.Button = self.create_serial_devices_refresh_button()
        self.refresh_serial_devices_button.grid(row=4, column=1, padx=5, pady=5)
        
        self.serial_devices_combobox: Combobox = self._init_serial_devices_combobox()
        self.serial_devices_combobox.grid(row=4, column=2, padx=5, pady=5)

        self.baudrate_label = tk.Label(self.root, text="Serial Baudrates:")
        self.baudrate_label.grid(row=5, column=0, padx=5, pady=5)
        
        self.baudrate_combobox: Combobox = self.create_baudrate_combobox() 
        self.baudrate_combobox.grid(row=5, column=2, padx=5, pady=5)
        
        self.connect_serial_button: tk.Button = self.create_connect_serial_button()
        self.connect_serial_button.grid(row=4, column=3, padx=5, pady=5)
        

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
                elif value == 'X':
                    button.config(bg='red')
                elif value == 'O':
                    button.config(bg='blue')
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

    
        
    def select_opponent(self):
        self.opponent_type = self.opponent_combobox.get()
        if self.opponent_type == 'serial':
            self.connect_serial()
        elif self.opponent_type == 'lan':
            self.connect_lan()
        elif self.opponent_type == 'web':
            self.connect_web()

        

    def connect_serial(self):
        # Implement connection logic to serial device
        pass

    def connect_lan(self):
        # Implement connection logic to LAN player
        pass

    def connect_web(self):
        # Implement connection logic to web player
        pass
    
    def _init_serial_devices_combobox(self) -> Combobox:  
        ports = locate_ports() 
        return Combobox(self.root, values=ports)
    
    def create_baudrate_combobox(self) -> Combobox:
        return Combobox(
            self.root, 
            values=BAUDRATES
        )
    def create_serial_devices_refresh_button(self) -> tk.Button:
        button = tk.Button(
            self.root, 
            text='Refresh', 
            command=self.refresh_serial_devices,
            bg='lightblue',
            activebackground='lightblue'
        )
        return button
    
    def refresh_serial_devices(self) -> None:
        ports = locate_ports()
        self.serial_devices_combobox.selection_clear()
        self.serial_devices_combobox['values'] = ports
        
    def create_connect_serial_button(self) -> tk.Button:
        button = tk.Button(
            self.root,
            text='Connect',
            #command=self.create_sensor_serial,
            bg='lightblue',
            activebackground='lightblue'
        )
        return button

if __name__ == "__main__":
    root = tk.Tk()
    app = BattleshipApp(root)
    root.mainloop()