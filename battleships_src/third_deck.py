import random

class BattleshipGame:
    def __init__(self):
        self.board_size = 8
        self.player_boards = {
            'player1': [[' ' for _ in range(self.board_size)] for _ in range(self.board_size)],
            'player2': [[' ' for _ in range(self.board_size)] for _ in range(self.board_size)]
        }
        self.attacks = {
            'player1': [[' ' for _ in range(self.board_size)] for _ in range(self.board_size)],
            'player2': [[' ' for _ in range(self.board_size)] for _ in range(self.board_size)]
        }
        self.current_player = 'player1'

    def place_ship(self, player, row, col, size, orientation):
        board = self.player_boards[player]
        if orientation == 'H':
            if col + size > self.board_size:
                return False
            if any(board[row][col + i] != ' ' for i in range(size)):
                return False
            for i in range(size):
                board[row][col + i] = 'S'
        else:
            if row + size > self.board_size:
                return False
            if any(board[row + i][col] != ' ' for i in range(size)):
                return False
            for i in range(size):
                board[row + i][col] = 'S'
        return True

    def attack(self, player, row, col):
        opponent = 'player2' if player == 'player1' else 'player1'
        if self.player_boards[opponent][row][col] == 'S':
            self.player_boards[opponent][row][col] = 'X'
            self.attacks[player][row][col] = 'X'
            return True
        else:
            self.attacks[player][row][col] = 'O'
            return False

    def get_board(self, player):
        return self.player_boards[player]

    def get_attacks(self, player):
        return self.attacks[player]

    def switch_turn(self):
        self.current_player = 'player2' if self.current_player == 'player1' else 'player1'

    def get_current_player(self):
        return self.current_player