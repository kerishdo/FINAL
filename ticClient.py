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

def parse_config(config_file):
    config = configparser.ConfigParser()
    config.read(config_file)
    
    # Parse configuration options
    save_dir = config['BASIC']['saveDir']
    score_file = config['BASIC']['score']
    server_ip = config['NETWORKING']['serverIP']
    server_port = int(config['NETWORKING']['port'])
    score_time_from = config['FILTER_SCORE']['scoreTimeFrom']
    score_time_to = config['FILTER_SCORE']['scoreTimeTo']

    return save_dir, score_file, server_ip, server_port, score_time_from, score_time_to

def main_menu():
    print("Tic Tac Toe")
    print("1. New Game")
    print("2. Load Saved Game")
    print("3. Load Configs")
    print("4. Show Score")
    print("5. Exit")

    choice = input("Enter your choice (1-5): ")
    return int(choice)

def new_game(server_ip, server_port):
    client_socket = connect_to_server(server_ip, server_port)
    board_state = new_game(client_socket)

    if board_state is not None:
        while True:
            x, y = input("Enter your move (x, y): ").split(',')
            x, y = int(x), int(y)

            if 0 <= x < 3 and 0 <= y < 3:
                board_state = move(client_socket, board_state, x, y)

                if board_state is None:
                    break
            else:
                print("Invalid move. Please try again.")
    close_connection(client_socket)


def load_saved_game(server_ip, server_port, save_dir):
    filename = input("Enter the name of the saved game file: ")
    filepath = os.path.join(save_dir, filename)

    if os.path.exists(filepath):
        with open(filepath, 'r') as file:
            saved_game_data = file.read()

        client_socket = connect_to_server(server_ip, server_port)
        board_state = load_game(client_socket, saved_game_data)

        if board_state is not None:
            while True:
                x, y = input("Enter your move (x, y): ").split(',')
                x, y = int(x), int(y)

                if 0 <= x < 3 and 0 <= y < 3:
                    board_state = move(client_socket, board_state, x, y)

                    if board_state is None:
                        break
                else:
                    print("Invalid move. Please try again.")
        close_connection(client_socket)
    else:
        print("Error: Saved game file not found")


def load_configs():
    save_dir, score_file, server_ip, server_port, score_time_from, score_time_to = parse_config('tictac.ini')
    print("Configuration loaded successfully")


def show_score(score_file, score_time_from, score_time_to):
    if os.path.exists(score_file):
        with open(score_file, 'r') as file:
            scores = file.readlines()

        # Parse and filter the score based on provided dates
        filtered_scores = [score.strip() for score in scores if score_time_from <= score.split(' ')[0] <= score_time_to]

        if len(filtered_scores) > 0:
            print("Scores:")
            for score in filtered_scores:
                print(score)
        else:
            print("No scores found in the specified time range")
    else:
        print("Error: Score file not found")

def connect_to_server(server_ip, server_port):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server_ip, server_port))
    return client_socket

def send_receive_packet(client_socket, packet_type, packet_body=None):
    packet = packet_type
    if packet_body:
        packet += f":{packet_body}"
    
    client_socket.send(packet.encode())
    
    response = client_socket.recv(1024).decode()
    response_packet_type, response_body = response.split(':', 1)

    return response_packet_type, response_body

def render_board(board_state):
    symbols = {0: "X", 1: "O", 2: " "}
    
    print("\n")
    for i in range(3):
        row = board_state[i * 3:i * 3 + 3]
        print(f" {symbols[row[0]]} | {symbols[row[1]]} | {symbols[row[2]]} ")
        if i < 2:
            print("-----------")
    print("\n")

def new_game(client_socket):
    packet_type, packet_body = send_receive_packet(client_socket, 'NEWG')
    
    if packet_type == 'BORD':
        board_state = list(map(int, packet_body.split(',')))
        render_board(board_state)
        return board_state
    else:
        print("Error: Unexpected response from server")
        return None


def end_game(client_socket, board_state):
    packet_type, packet_body = send_receive_packet(client_socket, 'ENDG')
    
    if packet_type == 'OVER':
        winner, *new_board_state = packet_body.split(',')
        board_state = list(map(int, new_board_state))
        render_board(board_state)
        print(f"Winner: {winner}")
        return board_state
    else:
        print("Error: Unexpected response from server")
        return board_state


def close_connection(client_socket):
    packet_type, _ = send_receive_packet(client_socket, 'CLOS')
    
    if packet_type == 'CLOS':
        client_socket.close()
        print("Connection closed")
    else:
        print("Error: Unexpected response from server")


def move(client_socket, board_state, x, y):
    packet_body = f"{x},{y}"
    packet_type, packet_body = send_receive_packet(client_socket, 'MOVE', packet_body)
    
    if packet_type == 'BORD':
        board_state = list(map(int, packet_body.split(',')))
        render_board(board_state)
    elif packet_type == 'EROR':
        print(f"Error: {packet_body}")
    elif packet_type == 'OVER':
        winner, *new_board_state = packet_body.split(',')
        board_state = list(map(int, new_board_state))
        render_board(board_state)
        print(f"Winner: {winner}")
    else:
        print("Error: Unexpected response from server")

    return board_state


def load_game(client_socket, saved_game_data):
    packet_type, packet_body = send_receive_packet(client_socket, 'LOAD', saved_game_data)
    
    if packet_type == 'BORD':
        board_state = list(map(int, packet_body.split(',')))
        render_board(board_state)
        return board_state
    else:
        print("Error: Unexpected response from server")
        return None


def handle_error(packet_body):
    print(f"Error: {packet_body}")


def handle_game_over(packet_body):
    winner, *new_board_state = packet_body.split(',')
    board_state = list(map(int, new_board_state))
    render_board(board_state)
    print(f"Winner: {winner}")
    return board_state

if __name__ == "__main__":
    server_ip = "127.0.0.1"
    port = 6969
    sock = connect_to_server(server_ip, port)
    main_menu(sock)

