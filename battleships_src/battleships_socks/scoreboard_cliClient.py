# 
#   Battleships Game: TCP Scoreboard Client Utility.
#   This module is a client utility to receive the scoreboard data from the server.
#   Tu be run from any device in the LAN.
#   By: aldrick-t (github.com/aldrick-t)
#   Version: June 2024 (v0.2.1) python3.11.2
#   

import socket

def receive_data_from_server(ip, port):
    # Create a socket object
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        # Connect to the server
        client_socket.connect((ip, port))
        print(f"Connected to server at {ip}:{port}")
        
        # Receive data from the server
        data = client_socket.recv(1024).decode('utf-8')
        if data:
            print("Received data from server:")
            print(data)
        else:
            print("No data received from server.")
            
    except Exception as e:
        print(f"Error: {e}")
    
    finally:
        # Close the connection
        client_socket.close()
        print("Connection closed.")

if __name__ == "__main__":
    ip = input("Enter the server IP address: ")
    port = int(input("Enter the server port: "))
    receive_data_from_server(ip, port)