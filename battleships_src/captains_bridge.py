import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from tkinter.ttk import Combobox
import random
import requests

from telegraph import BAUDRATES, SerialCommunicator
from utils import locate_ports
from third_deck import BattleshipGame

class BattleshipApp:
    def __init__(self, root):
        self.root = root
        self.game = BattleshipGame()
        self.cursor_position = [0, 0]
        self.view_mode = 'placement'  # placement, ships, or attacks
        self.current_player = 'player1'
        self.serial_comm = None
        self.raspberry_pi_ip = None
        self.boats_to_place = 5

        self.setup_ui()

    def setup_ui(self):
        self.root.title("Battleship Game")

        self.grid_frame = tk.Frame(self.root)
        self.grid_frame.grid(row=1, column=0, columnspan=3)

        self.info_label = tk.Label(self.root, text="Place your boats.")
        self.info_label.grid(row=0, column=0, columnspan=3, pady=5)

        self.confirm_button = tk.Button(self.root, text="Confirm Placement", command=self.confirm_placement)
        self.confirm_button.grid(row=2, column=1, padx=5, pady=5)

        self.switch_button = tk.Button(self.root, text="Switch View", command=self.switch_view)
        self.switch_button.grid(row=2, column=0, padx=5, pady=5)

        self.update_scoreboard_button = tk.Button(self.root, text="Update Scoreboard", command=self.update_scoreboard)
        self.update_scoreboard_button.grid(row=2, column=2, padx=5, pady=5)

        self.opponent_label = tk.Label(self.root, text="Select Connection:")
        self.opponent_label.grid(row=3, column=1, padx=5, pady=5)

        self.opponent_combobox = ttk.Combobox(self.root, values=["serial"])
        self.opponent_combobox.grid(row=3, column=2, padx=5, pady=5)

        self.connect_button = tk.Button(self.root, text="Select", command=self.select_opponent)
        self.connect_button.grid(row=3, column=3, padx=5, pady=5)
        
        self.serial_label = tk.Label(self.root, text="Serial Connections:")
        self.serial_label.grid(row=4, column=0, padx=5, pady=5)
        
        self.refresh_serial_devices_button = self.create_serial_devices_refresh_button()
        self.refresh_serial_devices_button.grid(row=4, column=1, padx=5, pady=5)
        
        self.serial_devices_combobox = self._init_serial_devices_combobox()
        self.serial_devices_combobox.grid(row=4, column=2, padx=5, pady=5)

        self.baudrate_label = tk.Label(self.root, text="Serial Baudrates:")
        self.baudrate_label.grid(row=5, column=0, padx=5, pady=5)
        
        self.baudrate_combobox = self.create_baudrate_combobox()
        self.baudrate_combobox.grid(row=5, column=2, padx=5, pady=5)
        
        self.connect_serial_button = self.create_connect_serial_button()
        self.connect_serial_button.grid(row=4, column=3, padx=5, pady=5)

        # IP Address Input and Connection
        self.ip_label = tk.Label(self.root, text="Enter IP Address:")
        self.ip_label.grid(row=6, column=0, padx=5, pady=5)

        self.ip_entry = tk.Entry(self.root)
        self.ip_entry.grid(row=6, column=1, padx=5, pady=5)

        self.connect_ip_button = tk.Button(self.root, text="Connect", command=self.connect_ip)
        self.connect_ip_button.grid(row=6, column=2, padx=5, pady=5)

        self.draw_grid()

        self.root.bind('<Up>', self.move_up)
        self.root.bind('<Down>', self.move_down)
        self.root.bind('<Left>', self.move_left)
        self.root.bind('<Right>', self.move_right)
        self.root.bind('<Return>', self.select_position)

    def draw_grid(self):
        for row in range(8):
            for col in range(8):
                if self.view_mode == 'placement' or self.view_mode == 'ships':
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
        if self.view_mode == 'placement':
            if self.boats_to_place > 0:
                size = 2
                orientation = random.choice(['H', 'V'])
                if self.game.place_boat(self.current_player, row, col, size, orientation):
                    self.boats_to_place -= 1
                    self.draw_grid()
                else:
                    messagebox.showerror("Error", "Invalid boat placement.")
            if self.boats_to_place == 0:
                self.info_label.config(text="Confirm placement to continue.")
        elif self.view_mode == 'attacks':
            if self.game.attack(self.current_player, row, col):
                self.info_label.config(text=f"Hit at ({row}, {col})!")
            else:
                self.info_label.config(text=f"Miss at ({row}, {col}).")
            self.game.switch_turn()
            self.current_player = self.game.get_current_player()
            self.draw_grid()
            if self.current_player == 'player2':
                self.receive_serial_attack()

    def switch_view(self):
        if self.view_mode == 'placement':
            self.view_mode = 'ships'
        elif self.view_mode == 'ships':
            self.view_mode = 'attacks'
        self.draw_grid()

    def confirm_placement(self):
        if self.boats_to_place > 0:
            messagebox.showerror("Error", "You must place all boats before confirming.")
            return

        if self.serial_comm is None:
            messagebox.showerror("Error", "Please connect to a serial device before confirming.")
            return

        positions = self.game.get_boat_positions(self.current_player)
        if self.current_player == 'player1':
            self.serial_comm.send(f"positions:{positions}")
            self.info_label.config(text="Waiting for opponent to confirm...")
        else:
            self.serial_comm.send(f"ready:{positions}")
        self.receive_serial_positions()

    def receive_serial_positions(self):
        response = self.serial_comm.receive()
        if response and response.startswith("positions:"):
            opponent_positions = eval(response.split(":", 1)[1])
            self.game.set_boat_positions('player2', opponent_positions)
            self.info_label.config(text="Opponent positions received. Game start!")
            self.view_mode = 'attacks'
            self.current_player = 'player1'
            self.draw_grid()

    def receive_serial_attack(self):
        response = self.serial_comm.receive()
        if response and response.startswith("attack:"):
            row, col = map(int, response.split(":", 1)[1].split(","))
            hit = self.game.attack('player2', row, col)
            self.serial_comm.send(f"result:{'hit' if hit else 'miss'}")
            self.info_label.config(text=f"Opponent attacked ({row}, {col}) and it was a {'hit' if hit else 'miss'}.")
            self.draw_grid()

    def update_scoreboard(self):
        if self.raspberry_pi_ip is None:
            messagebox.showerror("Error", "Please connect to a Raspberry Pi server before updating the scoreboard.")
            return

        player1_hits = sum(row.count('X') for row in self.game.get_attacks('player1'))
        player1_misses = sum(row.count('O') for row in self.game.get_attacks('player1'))
        player2_hits = sum(row.count('X') for row in self.game.get_attacks('player2'))
        player2_misses = sum(row.count('O') for row in self.game.get_attacks('player2'))

        url = f"http://{self.raspberry_pi_ip}:8000/update_scoreboard"
        params = {
            "player1_hits": player1_hits,
            "player1_misses": player1_misses,
            "player2_hits": player2_hits,
            "player2_misses": player2_misses
        }
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            messagebox.showinfo("Scoreboard", "Scoreboard updated!")
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Error", f"Failed to update scoreboard: {e}")

    def select_opponent(self):
        self.opponent_type = self.opponent_combobox.get()
        if self.opponent_type == 'serial':
            self.connect_serial()

    def connect_serial(self):
        port = self.serial_devices_combobox.get()
        baudrate = self.baudrate_combobox.get()
        self.serial_comm = SerialCommunicator(port, baudrate)
        messagebox.showinfo("Serial Connection", "Connected to serial device.")

    def connect_ip(self):
        ip_address = self.ip_entry.get()
        if not ip_address:
            messagebox.showerror("Error", "Please enter an IP address.")
            return
        self.raspberry_pi_ip = ip_address
        messagebox.showinfo("IP Connection", f"Connected to Raspberry Pi at {self.raspberry_pi_ip}")

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
            command=self.connect_serial,
            bg='lightblue',
            activebackground='lightblue'
        )
        return button
    
if __name__ == "__main__":
    root = tk.Tk()
    app = BattleshipApp(root)
    root.mainloop()