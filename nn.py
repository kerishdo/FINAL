#Student name: Kerish Do 
#Student ID:885324
#Date: 23/04/2023


#CPRG217
# Final Project: CPRG217 FINAL PROJECT

import configparser
import socket
import sys
import os
from datetime import datetime

# Existing config parsing functions

def display_menu():
    print("""\n
 _____ _  _____ _ __ __  _____ __ __ __  _ _    __  __  __ __ ___  
|_   _| |/ _/ |_   _/  \ / _/ |_   _/__\| __|  / _]/  \|  V  | __| 
  | | | | \__   | || /\ | \__   | || \/ | _|  | [/\ /\ | \_/ | _|  
  |_| |_|\__/   |_||_||_|\__/   |_| \__/|___|  \__/_||_|_| |_|___| """)
    print("---------------------")
    print("1. New game")
    print("2. Load saved game")
    print("3. Load configs")
    print("4. Show score")
    print("5. Exit")
    return input("Enter your choice (1-5): ")

# Define the connect_to_server function that takes server_ip and port as its input arguments.
def connect_to_server(server_ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    try:
        sock.connect((server_ip, port))
        return sock
    except Exception as e:
        print("Error connecting to server:", e)
        return None

#Define the get_basic_config function that takes a config object as its input argument 
def read_config(config_file):
    config = configparser.ConfigParser()
    config.read(config_file)
    return config

#Define the get_basic_config function that takes a config object as its input argument.
#Get the save directory value (save_dir) from the "BASIC" section of the config object.
def get_basic_config(config):
    save_dir = config.get("BASIC", "saveDir")
    score_file = config.get("BASIC", "score")
    return save_dir, score_file

#Define the get_network_config function that takes a config object as its input argument.
def get_network_config(config):
    server_ip = config.get("NETWORKING", "serverIP")
    port = config.getint("NETWORKING", "port")
    return server_ip, port

def get_filter_score_config(config):
    score_time_from = config.get("FILTER_SCORE", "scoreTimeFrom")
    score_time_to = config.get("FILTER_SCORE", "scoreTimeTo")
    return score_time_from, score_time_to

#Define the render_board function that takes board_data as its input argument.
def render_board(board_data):
    print(board_data) #Print the raw board_data.
    board = [int(i) for i in board_data.split(',')]
    symbols = {0: 'X', 1: 'O', 2: ' '}
#Iterate through the rows of the board (i) from 0 to 2:
#a. Initialize an empty string (row) with the row number (i) and a space.
#b. Iterate through the columns of the board (j) from 0 to 2:
#i. Calculate the index of the current cell (index) by using the formula: i * 3 + j.
#ii. Get the symbol for the current cell (cell_symbol) from the symbols dictionary using the value at the current index of the board.
#iii. Append the cell_symbol to the row string, surrounded by pipe characters and spaces.
#iv. If j is 2 (the last column), append a pipe character to the row string.
    print("\nCURRENT BOARD")
    print("    0   1   2 ")
    for i in range(3):
        row = str(i) + " "
        for j in range(3):
            index = i * 3 + j
            cell_symbol = symbols[board[index]]
            row += "| " + cell_symbol + " "
            if j == 2:
                row += "|"
        print(row)
        if i < 2:
            print("  " + "-" * 13)


def main():
    
    # Connect to the server
    sock = connect_to_server(server_ip, port)
    if sock is None:
        sys.exit(1)

    # Main loop
    while True:
        choice = display_menu()
        if choice == '1':
            send_packet(sock, 'NEWG')
            packet_head, packet_body = recv_packet(sock)
            if packet_head == "BORD":
                board_data = packet_body
                render_board(board_data)
                while True:
                    try:
                        move_x, move_y = get_player_move()
                        send_packet(sock, f"MOVE:{move_x},{move_y}")
                        packet_head, packet_body = recv_packet(sock)
                        if packet_head == "BORD":
                            board_data = packet_body
                            render_board(board_data)
                        elif packet_head == "ERROR":
                            handle_error(packet_body)
                            break
                        elif packet_head == "OVER":
                            handle_game_over(packet_body)
                            break
                    except KeyboardInterrupt:
                        print("\nExiting the game.")
                        break   
            # Recv BORD                 }
            # Render BORD # Input Move  } Loop
            # Send Move & Recv BORD/OVER     }
            # New game logic

        elif choice == '2':
            saveDir = "/tmp/savedGames"
            filename = input("Enter the filename of the saved game: ").strip()
            file_path = os.path.join(saveDir, filename)
            if os.path.exists(file_path):
                with open(filename, 'r') as file:
                    saved_game = file.read()
                    send_packet(sock, f"LOAD: {saved_game}")
                    packet_head, packet_body = recv_packet(sock)
                    if packet_head == "BORD":
                        board_data = packet_body
                        render_board(board_data)

                while True:
                    move_x, move_y = get_player_move()
                    send_packet(sock, f"MOVE:{move_x},{move_y}")
                    packet_head, packet_body = recv_packet(sock)

                    if packet_head == "BORD":
                        board_data = packet_body
                        render_board(board_data)
                    elif packet_head == "ERROR":
                        handle_error(packet_body)
                        break
                    elif packet_head == "OVER":
                        handle_game_over(packet_body)
                        break
            
            # Read BORd
            # Render BORD # Input Move  }
            # Send Move & Recv BORD     }
            # Load saved game logic
            
        elif choice == '3':
            display_config(config)
            # Load configs logic
            pass
        elif choice == '4':
            display_score(score_file, score_time_from, score_time_to)
            # Show score logic
            pass
        elif choice == '5':
            sock.sendall(b'CLOS') # packet CLOS
            sock.close()
            sys.exit(0)
        else:
            print("Invalid choice, please try again.")

def send_packet(sock, packet):
    sock.sendall(packet.encode('utf-8'))

def recv_packet(sock):
    response = sock.recv(1024).decode('utf-8')
    head, *body = response.split(':')
    return head, ':'.join(body)

def handle_error(error_message):
    print(f"ERROR: {error_message}")

#Define the handle_game_over function with one input agrument:packet_body 
def handle_game_over(packet_body):
    winner, board_data = packet_body.split(',', maxsplit=1)
    #Split packet_body by the comma with a maximum of one split, storing the first value in the variable winner and the remaining string in board_data.
    if winner =='C':
        print("You won!")
    elif winner == 'S':
        print("CPU won!")
    else:
        winner =='N'
        print("No one won!")
    render_board(board_data) #Call the render_board function with board_data as its argument.

#Define the get_player_move function with no input arguments.
def get_player_move():
    valid_move = False #Initialize a boolean variable (valid_move) to False.
    while not valid_move:
        try:
            move = input("Enter your move as x,y (e.g. 0,0 for top-left corner): ") #Prompt the user to enter their move as "x,y" (e.g., "0,0" for the top-left corner) and store it in the variable move.
            x, y = [int(i) for i in move.split(',')]
            if 0 <= x <= 2 and 0 <= y <= 2:
                valid_move = True
                #Split the move string by the comma and convert the x and y coordinates to integers, storing them in the variables x and y.
            else:
                print("Invalid input. Coordinates must be between 0 and 2.")
                # If true, set valid_move to True.
                #If false, print an error message stating that the coordinates must be between 0 and 2.
                #If a ValueError exception occurs:
        except ValueError:
            print("Invalid input. Please enter your move as x,y.")
    return x, y

def save_game(filename, player, board_data):
    saveDir = '/tmp/savedGames' #Set the save directory (saveDir) to '/tmp/savedGames'.
    print(filename)
    file_path = os.path.join(saveDir, filename) #Create the full file path (file_path) by joining saveDir and filename.
    try:
        with open(file_path, 'w') as file:
            game_data = f"{player},{','.join(board_data)}"
            file.write(game_data)
        print(f"Game saved in {file_path}")
    except IOError: #If an IOError occurs:
        #Print an error message informing the user that there was an error saving the game and to try again.
        print("Error saving the game. Please try again.")

#Define the display_config function with one input argument:config.
def display_config(config):
#   Call the get_basic_config function with config as its argument, and store the returned values in save_dir and score_file variables.

#   Call the get_network_config function with config as its argument, and store the returned values in server_ip and port variables.

#   Call the get_filter_score_config function with config as its argument, and store the returned values in score_time_from and score_time_to     variables.

    save_dir, score_file = get_basic_config(config)
    server_ip, port = get_network_config(config)
    score_time_from, score_time_to = get_filter_score_config(config)

    print("\nLoaded Configurations:")
    print("Basic config:")
    print("  Save directory:", save_dir)
    print("  Score file:", score_file)

    print("\nNetwork config:")
    print("  Server IP:", server_ip)
    print("  Port:", port)

    print("\nFilter score config:")
    print("  Score time from:", score_time_from)
    print("  Score time to:", score_time_to)

#Define the display_score 
def display_score(score_file, score_time_from, score_time_to):
    try:
        start_date = datetime.strptime(score_time_from, "%b %d %H:%M")
        end_date = datetime.strptime(score_time_to, "%b %d %H:%M")

        with open(score_file, 'r') as file:
            scores = file.readlines()

        print("\nSCORES: 4")
        for score in scores:
            date_str, result = score.strip().split(',', 1)
            date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")

            if start_date <= date <= end_date:
                print(f"{date_str} - {result}")
    except Exception as e:
        print(f"Error displaying scores: {e}")




if __name__ == "__main__":
    main()
