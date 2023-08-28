import socket
import sys
import os
import configparser

# Replace 'SERVER_IP' with the actual IP address of the server
SERVER_IP = '127.0.0.1'
# Replace 'PORT' with the port number the server is running on
PORT = 6969
CONFIG_FILE = 'tictac.ini'
SCORE_FILE = 'score.txt'

def send_packet(s, head, body=None):
    packet = f"{head}:{body}" if body is not None else head
    s.sendall(packet.encode())

def receive_packet(s):
    received_data = s.recv(1024).decode()
    head, body = received_data.split(':', 1) if ':' in received_data else (received_data, None)
    return head, body


def connect_to_server():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((SERVER_IP, PORT))
        return s
    except socket.error as e:
        print(f"Error connecting to the server: {e}")
        sys.exit(1)

def load_config():
    config = configparser.ConfigParser()
    if os.path.isfile(CONFIG_FILE):
        try:
            config.read(CONFIG_FILE)
            return config
        except configparser.Error as e:
            print(f"Error reading the config file: {e}")
            sys.exit(1)
    else:
        
        sys.exit(1)

def main_menu():
    print("Welcome to Tic Tac Toe")
    print("1. New Game")
    print("2. Load Saved Game")
    print("3. Load Configs")
    print("4. Show Score")
    print("5. Exit")

def new_game(s):
    send_packet(s, "NEWG")
    head, body = receive_packet(s)
    if head == "ACKN":
        print("New game started!")
    else:
        print("Failed to start a new game.")
    pass  # Implement the new game logic here

def load_saved_game(s):
    pass  # Implement the load saved game logic here

def load_configs():
    pass  # Implement the load configs logic here

def show_score():
    if os.path.isfile(SCORE_FILE):
        with open(SCORE_FILE, 'r') as f:
            print(f.read())
    else:
        print("Score file not found.")

def main():
    s = connect_to_server()
    config = load_config()

    while True:
        main_menu()
        choice = input("Enter your choice: ")

        if choice == "1":
            new_game(s)
        elif choice == "2":
            load_saved_game(s)
        elif choice == "3":
            load_configs()
        elif choice == "4":
            show_score()
        elif choice == "5":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")

    s.close()

if __name__ == "__main__":
    main()






