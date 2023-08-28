import configparser
import socket
import sys

# Existing config parsing functions

def display_menu():
    print("\nWelcome to Tic Tac Toe")
    print("-----------")
    print("1. New game")
    print("2. Load saved game")
    print("3. Load configs")
    print("4. Show score")
    print("5. Exit")
    return input("Enter your choice (1-5): ")

def connect_to_server(server_ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((server_ip, port))
        return sock
    except Exception as e:
        print("Error connecting to server:", e)
        return None

def read_config(config_file):
    config = configparser.ConfigParser()
    config.read(config_file)
    return config

def get_basic_config(config):
    save_dir = config.get("BASIC", "saveDir")
    score_file = config.get("BASIC", "score")
    return save_dir, score_file

def get_network_config(config):
    server_ip = config.get("NETWORKING", "serverIP")
    port = config.getint("NETWORKING", "port")
    return server_ip, port

def get_filter_score_config(config):
    score_time_from = config.get("FILTER_SCORE", "scoreTimeFrom")
    score_time_to = config.get("FILTER_SCORE", "scoreTimeTo")
    return score_time_from, score_time_to

def render_board(board_data):
    board = [int(i) for i in board_data.split(',')]
    symbols = {0: 'X', 1: 'O', 2: ' '}
    
    print("\nGAME READY!!")
    for i in range(3):
        row = ''
        for j in range(3):
            row += symbols[board[i * 3 + j]] + ' | '
        print(row[:-3])
        if i < 2:
            print("-" * 9)


def main():
    try:
        config = read_config("tictac.ini")
        save_dir, score_file = get_basic_config(config)
        server_ip, port = get_network_config(config)
        score_time_from, score_time_to = get_filter_score_config(config)

        print("Basic config:")
        print("Save directory:", save_dir)
        print("Score file:", score_file)

        print("\nNetwork config:")
        print("Server IP:", server_ip)
        print("Port:", port)

        print("\nFilter score config:")
        print("Score time from:", score_time_from)
        print("Score time to:", score_time_to)

    except Exception as e:
        print("Error reading config file:", e)
        sys.exit(1)

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
               
            # Recv BORD                 }
            # Render BORD # Input Move  } Loop
            # Send Move & Recv BORD/OVER     }
            # New game logic

        elif choice == '2':
            filename = input("Enter the filename of the saved game: ")
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
            player = ''
            filename = input("Enter a filename to save game: ")
            save_game(filename, player, board_data)
            print("Game saved successfully. ")
            # Load configs logic
            pass
        elif choice == '4':
            # Show score logic
            pass
        elif choice == '5':
            sock.sendall(b'CLOS')
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

def handle_game_over(packet_body):
    winner, *board_data = packet_body.split(',')
    if winner =='C':
        print("You won!")
    elif winner == 'S':
        print("CPU won!")
    else:
        winner =='N'
        print("No one won!")
    render_board(',').join(board_data)

def get_player_move():
    valid_move = False
    while not valid_move:
        try:
            move = input("Enter your move as x,y (e.g. 0,0 for top-left corner): ")
            x, y = [int(i) for i in move.split(',')]
            if 0 <= x <= 2 and 0 <= y <= 2:
                valid_move = True
            else:
                print("Invalid input. Coordinates must be between 0 and 2.")
        except ValueError:
            print("Invalid input. Please enter your move as x,y.")
    return x, y

def save_game(filename, player, board_data):
    with open(filename, 'w') as file:
        game_data = f"{player},{','.join(board_data)}"
        file.write(game_data)





if __name__ == "__main__":
    main()
