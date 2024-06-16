import socket
import threading

# Define the scoreboard data
scoreboard = {
    "player1_hits": 0,
    "player1_misses": 0,
    "player2_hits": 0,
    "player2_misses": 0
}

# Function to handle each client connection
def handle_client(client_socket):
    data = f"Player 1 Hits: {scoreboard['player1_hits']}\n" \
           f"Player 1 Misses: {scoreboard['player1_misses']}\n" \
           f"Player 2 Hits: {scoreboard['player2_hits']}\n" \
           f"Player 2 Misses: {scoreboard['player2_misses']}\n"
    client_socket.sendall(data.encode('utf-8'))
    client_socket.close()

# Function to start the TCP server
def start_tcp_server(ip, port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((ip, port))
    server_socket.listen(5)
    print(f"TCP server listening on {ip}:{port}")

    while True:
        client_socket, addr = server_socket.accept()
        print(f"Connection from {addr}")
        client_handler = threading.Thread(target=handle_client, args=(client_socket,))
        client_handler.start()

if __name__ == "__main__":
    ip = "0.0.0.0"  # Change to your server's IP address if necessary
    port = 12345    # Port for the TCP server

    start_tcp_server(ip, port)