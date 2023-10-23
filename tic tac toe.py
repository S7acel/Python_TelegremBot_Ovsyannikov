import colorama
from colorama import Fore, Back, Style


def draw_colored_board(board):  # Визуализация доски с цветовой палитрой
    for i in board:
        row = ''
        for cell in i:
            if cell == 'X':
                row += f'| {Fore.RED}{cell}{Style.RESET_ALL} '
            elif cell == 'O':
                row += f'| {Fore.BLUE}{cell}{Style.RESET_ALL} '
            else:
                row += f'| {cell} '
        print(row + '|')
        print('-------------')


def check_win(board, f_p, s_p):  # Проверка на выйгрыш
    # Проверка выигрышных комбинаций по горизонтали и вертикали
    for i in range(3):
        if board[i] == [f_p, f_p, f_p]:
            print(f'The player who played for {f_p} won!')
            return True
        elif board[i] == [s_p, s_p, s_p]:
            print(f'The player who played for {s_p} won!')
            return True
        elif [board[0][i], board[1][i], board[2][i]] == [f_p, f_p, f_p]:
            print(f'The player who played for {f_p} won!')
            return True
        elif [board[0][i], board[1][i], board[2][i]] == [s_p, s_p, s_p]:
            print(f'The player who played for {s_p} won!')
            return True

    # Проверка выигрышной комбинации по диагонали
    if [board[0][0], board[1][1], board[2][2]] == [f_p, f_p, f_p]:
        print(f'The player who played for {f_p} won!')
        return True
    elif [board[0][0], board[1][1], board[2][2]] == [s_p, s_p, s_p]:
        print(f'The player who played for {s_p} won!')
        return True
    elif [board[0][2], board[1][1], board[2][0]] == [f_p, f_p, f_p]:
        print(f'The player who played for {f_p} won!')
        return True
    elif [board[0][2], board[1][1], board[2][0]] == [s_p, s_p, s_p]:
        print(f'The player who played for {s_p} won!')
        return True

    return False


def out_of_bounce(f_c, s_c):  # Проверка на корректность полей и координатов
    if not (0 <= f_c <= 2) and not (0 <= s_c <= 2):
        return True


def free_field_check(board, f_c, s_c):  # проверка на занятость поля
    if board[f_c][s_c] != ' ':
        return True


def check_tie(board):
    for row in board:
        for cell in row:
            if cell == ' ':
                return False
    print('Tie!')
    return True


def change_player(player, gamer, curr_player):  # смена хода
    return player if curr_player == gamer else gamer

    current_player = first_player


def ask_and_make_move(player, board):
    print(f'{player} Move')
    coordinate = input('write coordinate of x and y (e.g 0 0): ').strip().split()
    x, y = int(coordinate[0]), int(coordinate[1])
    if out_of_bounce(x, y):
        print('you should write between 0 and 2 ;)')
        return False
    if free_field_check(board, y, x):
        print('The field is already taken')
        return False
    board[y][x] = player
    return True


def tic_tac_toe():
    game_board = [[' ' for _ in range(3)] for _ in range(3)]
    draw_colored_board(game_board)

    first_player = 'X'
    second_player = 'O'

    current_player = first_player
    while True:
        if ask_and_make_move(current_player, game_board):
            draw_colored_board(game_board)
            current_player = change_player(first_player, second_player, current_player)
            if check_win(game_board, first_player, second_player):
                restart = input("Do you want to play again? (y/n) ")
                if restart.lower() != "y":
                    break
                else:
                    game_board = [[' ' for i in range(3)] for y in range(3)]
                    draw_colored_board(game_board)

            if check_tie(game_board):
                restart = input("Do you want to play again? (y/n) ")
                if restart.lower() != "y":
                    break
                else:

                    game_board = [[' ' for i in range(3)] for y in range(3)]
                    draw_colored_board(game_board)


tic_tac_toe()
