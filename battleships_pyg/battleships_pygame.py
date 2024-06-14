import pygame
import random
import serial
import threading
import requests

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
LIGHTGRAY = (211, 211, 211)

# Grid dimensions
GRID_SIZE = 8
CELL_SIZE = 50
MARGIN = 5

# Setup the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Battleship Game")

# Font for text
font = pygame.font.Font(None, 36)

# Game state variables
current_player = 'player1'
view_mode = 'placement'
boats_to_place = 5
cursor_position = [0, 0]
opponent_turn = False
game_started = False

# Placeholder for Serial communication
serial_comm = None
serial_thread = None
raspberry_pi_ip = None

# Placeholder for game board
player1_board = [['' for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
player2_board = [['' for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
player1_attacks = [['' for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
player2_attacks = [['' for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

def draw_grid(board, offset_x, offset_y):
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            color = LIGHTGRAY
            if board[row][col] == 'B':
                color = GREEN
            elif board[row][col] == 'X':
                color = RED
            elif board[row][col] == 'O':
                color = BLUE
            pygame.draw.rect(screen, color, [(MARGIN + CELL_SIZE) * col + MARGIN + offset_x,
                                             (MARGIN + CELL_SIZE) * row + MARGIN + offset_y,
                                             CELL_SIZE, CELL_SIZE])
            pygame.draw.rect(screen, BLACK, [(MARGIN + CELL_SIZE) * col + MARGIN + offset_x,
                                             (MARGIN + CELL_SIZE) * row + MARGIN + offset_y,
                                             CELL_SIZE, CELL_SIZE], 1)

def place_boat(board, row, col):
    global boats_to_place
    if boats_to_place > 0:
        size = 2
        orientation = random.choice(['H', 'V'])
        if orientation == 'H':
            if col + size <= GRID_SIZE and all(board[row][col+i] == '' for i in range(size)):
                for i in range(size):
                    board[row][col+i] = 'B'
                boats_to_place -= 1
        elif orientation == 'V':
            if row + size <= GRID_SIZE and all(board[row+i][col] == '' for i in range(size)):
                for i in range(size):
                    board[row+i][col] = 'B'
                boats_to_place -= 1

def attack(board, attacks, row, col):
    if board[row][col] == 'B':
        attacks[row][col] = 'X'
        board[row][col] = 'X'
        return True
    else:
        attacks[row][col] = 'O'
        return False

def draw_text(text, x, y, color):
    screen_text = font.render(text, True, color)
    screen.blit(screen_text, [x, y])

def serial_receive():
    global opponent_turn, game_started
    while True:
        if serial_comm:
            line = serial_comm.readline().decode().strip()
            if line:
                print(f"Received: {line}")
                if line.startswith("positions:"):
                    opponent_positions = [tuple(map(int, pos.split(','))) for pos in line.split(':')[1].split()]
                    for pos in opponent_positions:
                        player2_board[pos[0]][pos[1]] = 'B'
                    serial_comm.write("ready\n".encode())
                elif line == "ready":
                    game_started = True
                    opponent_turn = False
                elif line.startswith("attack:"):
                    _, pos = line.split(":")
                    row, col = map(int, pos.split(","))
                    if current_player == 'player1':
                        hit = attack(player1_board, player2_attacks, row, col)
                    elif current_player == 'player2':
                        hit = attack(player2_board, player1_attacks, row, col)
                    serial_comm.write(f"{'hit' if hit else 'miss'}\n".encode())
                    opponent_turn = False
                elif line in ["hit", "miss"]:
                    opponent_turn = False

def start_serial_thread():
    global serial_thread
    serial_thread = threading.Thread(target=serial_receive)
    serial_thread.daemon = True
    serial_thread.start()

def connect_serial(port, baudrate):
    global serial_comm
    serial_comm = serial.Serial(port, baudrate)
    print(f"Connected to serial device at port {port} with baudrate {baudrate}")
    start_serial_thread()

def connect_ip(ip_address):
    global raspberry_pi_ip
    raspberry_pi_ip = ip_address
    print(f"Connected to Raspberry Pi at {raspberry_pi_ip}")

def update_scoreboard():
    if raspberry_pi_ip is None:
        print("Please connect to a Raspberry Pi server before updating the scoreboard.")
        return

    player1_hits = sum(row.count('X') for row in player1_attacks)
    player1_misses = sum(row.count('O') for row in player1_attacks)
    player2_hits = sum(row.count('X') for row in player2_attacks)
    player2_misses = sum(row.count('O') for row in player2_attacks)

    url = f"http://{raspberry_pi_ip}:8000/update_scoreboard"
    params = {
        "player1_hits": player1_hits,
        "player1_misses": player1_misses,
        "player2_hits": player2_hits,
        "player2_misses": player2_misses
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        print("Scoreboard updated!")
    except requests.exceptions.RequestException as e:
        print(f"Failed to update scoreboard: {e}")

def display_menu():
    global current_player, view_mode, boats_to_place, cursor_position, opponent_turn, game_started, player1_board, player2_board, player1_attacks, player2_attacks

    screen.fill(WHITE)
    draw_text("Press 'S' to start the game", 50, 100, BLACK)
    draw_text("Press 'C' to connect to serial device", 50, 150, BLACK)
    draw_text("Press 'I' to connect to IP for scoreboard", 50, 200, BLACK)

    pygame.display.flip()

    waiting_for_input = True
    while waiting_for_input:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                waiting_for_input = False
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s:
                    waiting_for_input = False
                elif event.key == pygame.K_c:
                    port = input("Enter serial port (e.g., COM3 or /dev/ttyUSB0): ")
                    baudrate = input("Enter baud rate (e.g., 9600): ")
                    connect_serial(port, int(baudrate))
                elif event.key == pygame.K_i:
                    ip_address = input("Enter Raspberry Pi IP address: ")
                    connect_ip(ip_address)

# Main game loop
running = True
display_menu()

while running:
    screen.fill(WHITE)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                cursor_position[0] = (cursor_position[0] - 1) % GRID_SIZE
            elif event.key == pygame.K_DOWN:
                cursor_position[0] = (cursor_position[0] + 1) % GRID_SIZE
            elif event.key == pygame.K_LEFT:
                cursor_position[1] = (cursor_position[1] - 1) % GRID_SIZE
            elif event.key == pygame.K_RIGHT:
                cursor_position[1] = (cursor_position[1] + 1) % GRID_SIZE
            elif event.key == pygame.K_RETURN:
                if view_mode == 'placement' and boats_to_place > 0:
                    if current_player == 'player1':
                        place_boat(player1_board, cursor_position[0], cursor_position[1])
                    else:
                        place_boat(player2_board, cursor_position[0], cursor_position[1])
                if boats_to_place == 0 and current_player == 'player1':
                    positions = [(row, col) for row in range(GRID_SIZE) for col in range(GRID_SIZE) if player1_board[row][col] == 'B']
                    serial_comm.write(f"positions:{' '.join([f'{pos[0]},{pos[1]}' for pos in positions])}\n".encode())
                    current_player = 'player2'
                    boats_to_place = 5
                    view_mode = 'placement'
                elif boats_to_place == 0 and current_player == 'player2':
                    positions = [(row, col) for row in range(GRID_SIZE) for col in range(GRID_SIZE) if player2_board[row][col] == 'B']
                    serial_comm.write(f"positions:{' '.join([f'{pos[0]},{pos[1]}' for pos in positions])}\n".encode())
                elif view_mode == 'attacks':
                    if not opponent_turn:
                        if current_player == 'player1':
                            hit = attack(player2_board, player1_attacks, cursor_position[0], cursor_position[1])
                            serial_comm.write(f"attack:{cursor_position[0]},{cursor_position[1]}\n".encode())
                            opponent_turn = True
                        elif current_player == 'player2':
                            hit = attack(player1_board, player2_attacks, cursor_position[0], cursor_position[1])
                            serial_comm.write(f"attack:{cursor_position[0]},{cursor_position[1]}\n".encode())
                            opponent_turn = True
                            
# Draw the grids
    if current_player == 'player1':
        draw_grid(player1_board, 50, 50)
        draw_grid(player1_attacks, 450, 50)
    else:
        draw_grid(player2_board, 50, 50)
        draw_grid(player2_attacks, 450, 50)

    # Highlight the cursor position
    pygame.draw.rect(screen, YELLOW, [(MARGIN + CELL_SIZE) * cursor_position[1] + MARGIN + 50, (MARGIN + CELL_SIZE) * cursor_position[0] + MARGIN + 50, CELL_SIZE, CELL_SIZE], 3)

    if opponent_turn:
        draw_text("Waiting for opponent...", 50, 500, RED)
    else:
        draw_text("Your turn!", 50, 500, GREEN)

    pygame.display.flip()
    pygame.time.Clock().tick(30)