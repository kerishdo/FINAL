def render_board(board_data):
    board = [int(i) for i in board_data.split(',')]
    symbols = {0: 'X', 1: 'O', 2: ' '}

    print("\nGAME READY!!")
    print("  0   1   2")
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
            print("  " + "-" * 11)

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
