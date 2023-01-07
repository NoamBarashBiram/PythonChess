from re import match, sub
from colorama import Fore, Back, Style
from os import system


def clear():
    """
    a function that clears the terminal, works in both windows and linux
    """
    system("cls || clear")


def pprint(*args, **kwargs):
    """
    print without "\n" at the end
    """
    print(*args, **kwargs, end="")


def get_position(prompt):
    """
    a function that gets a position on the board (i.e. B5) from the user and turns it into an index list
    :param prompt: to show the user
    :return: [y, x] position on the board
    """
    new_pos = input(prompt).upper()
    while not match("^[A-H][1-8]$", new_pos):
        new_pos = input("Pardon? ").upper()

    new_pos = [int(new_pos[1]) - 1,
               ord(new_pos[0]) - ord("A")]
    return new_pos


NFormat = Fore.LIGHTWHITE_EX + Back.LIGHTBLACK_EX
colors = ("white", "black")
board = []
WHITE = 0
BLACK = 1

for i in range(8):
    line = []
    for j in range(8):
        line += [None]
    board += [line]


def print_board(color):
    """
    a function that prints the board
    :param color: a text to display above the board, representing the color now playing
    """
    clear()

    print(" " * 11, Style.BRIGHT + NFormat + color.upper() + Style.RESET_ALL)  # prints player's color

    # print upper A-H indices row
    pprint("  ", NFormat)
    for i in range(8):
        pprint(f" {chr(ord('A') + i)} ")
    print(Style.RESET_ALL)

    # print the board
    for i in range(7, -1, -1):
        pprint(NFormat + f" {i + 1} " + Style.RESET_ALL)  # prints the number at the line's start
        for j in range(8):
            # if cell is empty, make white when i,j are both even or both odd, and black if one even and one odd
            if board[i][j] is None:
                if (i + j) % 2:
                    pprint(Back.WHITE, "  ")
                else:
                    pprint(Back.LIGHTBLACK_EX, "  ")
            else:
                # set background color to piece's color
                if board[i][j].color == "white":
                    pprint(Back.LIGHTWHITE_EX + Fore.BLACK)
                else:
                    pprint(Back.BLACK + Fore.LIGHTWHITE_EX)
                pprint(f" {board[i][j].letter} ")  # print the piece's letter
        print(NFormat + f" {i + 1} " + Style.RESET_ALL)  # prints the number at the line's end

    # print lower A-H indices row
    pprint("  ", NFormat)
    for i in range(8):
        pprint(f" {chr(ord('A') + i)} ")

    print(Style.RESET_ALL)  # reset style before exiting


class Piece:
    def __init__(self, color, position=None):
        if position is None:
            position = [0, 0]

        self.name = None
        self.letter = None
        self.position = position
        self.color = color
        board[position[0]][position[1]] = self

    def validate_move(self, new_pos, verbose=False):
        if new_pos == self.position:
            if verbose:
                print("You can't stay in place you dummy")
            return False

        if not self.legal_move(new_pos):
            if verbose:
                print("The move police just arrested you, you can't do that!")
            return False

        if board[new_pos[0]][new_pos[1]] is not None:
            if board[new_pos[0]][new_pos[1]].color == self.color:
                if verbose:
                    print("You wanna eat yourself mate?")
                return False
            if verbose:
                print(f"Whoa, you just ate that {board[new_pos[0]][new_pos[1]].name}!")
        return True

    def move(self, new_pos):
        if not self.validate_move(new_pos, True):
            return False
        board[self.position[0]][self.position[1]] = None
        self.position = new_pos
        board[self.position[0]][self.position[1]] = self
        return True

    @property
    def colorValue(self):
        return 1 if self.color == "white" else -1

    def legal_move(self, new_pos):
        pass

    def generate_moves(self):
        pass


class Pawn(Piece):
    def __init__(self, color, position):
        super().__init__(color, position)
        self.name = "Pawn"
        self.letter = "P"
        self.first_move = True

    def legal_move(self, new_pos):
        if board[new_pos[0]][new_pos[1]] is None:
            if new_pos[1] != self.position[1]:
                return False

            d = (new_pos[0] - self.position[0]) * self.colorValue
            if d < 0 or d > (2 if self.first_move else 1):
                return False
            if self.first_move and abs(new_pos[0] - self.position[0]) == 2:
                if board[(self.position[0] + new_pos[0]) // 2][self.position[1]] is not None:
                    return False
        else:
            if (new_pos[0] - self.position[0]) != self.colorValue:
                return False
            if abs((new_pos[1] - self.position[1])) != 1:
                return False

        return True

    def move(self, new_pos):
        if super().move(new_pos):
            self.first_move = False

    def generate_moves(self):
        if self.position[1] == 7:
            return []

        new_pos = []

        if (0 <= self.position[0] + self.colorValue <= 7) and \
                board[self.position[0] + self.colorValue][self.position[1]] is None:
            new_pos += [[self.position[0] + self.colorValue, self.position[1]]]

            if (0 <= self.position[0] + 2 * self.colorValue <= 7) and self.first_move and \
                    board[self.position[0] + 2 * self.colorValue][self.position[1]] is None:
                new_pos += [[self.position[0] + 2 * self.colorValue, self.position[1]]]

        for i in range(-1, 2, 2):
            if not 0 <= self.position[1] + i <= 7 or not 0 <= self.position[0] + self.colorValue <= 7:
                continue
            new_pos_piece = board[self.position[0] + self.colorValue][self.position[1] + i]
            if new_pos_piece is not None and new_pos_piece.color != self.color:
                new_pos += [[self.position[0] + self.colorValue, self.position[1] + i]]

        return new_pos


class Bishop(Piece):
    def __init__(self, color, position):
        super().__init__(color, position)
        self.name = "Bishop"
        self.letter = "B"

    def legal_move(self, new_pos):
        if abs(new_pos[0] - self.position[0]) != abs(new_pos[1] - self.position[1]):
            return False

        dy = new_pos[0] - self.position[0]
        dx = 1 if (new_pos[1] - self.position[1]) > 0 else -1
        sign = 1 if dy > 0 else -1
        dx *= sign
        for i in range(sign, dy, sign):
            if board[self.position[0] + i][self.position[1] + i * dx] is not None:
                return False
        return True


class Rook(Piece):
    def __init__(self, color, position):
        super().__init__(color, position)
        self.name = "Rook"
        self.letter = "R"

    def legal_move(self, new_pos):
        dx = new_pos[1] - self.position[1]
        dy = new_pos[0] - self.position[0]

        if dx == 0:
            sign = 1 if dy > 0 else -1
            for i in range(sign, dy, sign):
                if board[self.position[0] + i][self.position[1]] is not None:
                    return False
        elif dy == 0:
            sign = 1 if dx > 0 else -1
            for i in range(sign, dx, sign):
                if board[self.position[0]][self.position[1] + i] is not None:
                    return False
        else:
            return False

        return True


class Knight(Piece):
    def __init__(self, color, position):
        super().__init__(color, position)
        self.name = "Knight"
        self.letter = "N"

    def legal_move(self, new_pos):
        dx = abs(new_pos[1] - self.position[1])
        dy = abs(new_pos[0] - self.position[0])

        return (dx == 2 and dy == 1) or (dx == 1 and dy == 2)


class King(Piece):
    def __init__(self, color, position):
        super().__init__(color, position)
        self.name = "King"
        self.letter = "K"

    def legal_move(self, new_pos):
        dx = abs(new_pos[1] - self.position[1])
        dy = abs(new_pos[0] - self.position[0])

        return dx <= 1 and dy <= 1


class Queen(Piece):
    def __init__(self, color, position):
        super().__init__(color, position)
        self.name = "Queen"
        self.letter = "Q"

    def legal_move(self, new_pos):
        dy = new_pos[0] - self.position[0]
        dx = new_pos[1] - self.position[1]

        if dx == 0:
            sign = 1 if dy > 0 else -1
            for i in range(sign, dy, sign):
                if board[self.position[0] + i][self.position[1]] is not None:
                    return False
        elif dy == 0:
            sign = 1 if dx > 0 else -1
            for i in range(sign, dx, sign):
                if board[self.position[0]][self.position[1] + i] is not None:
                    return False
        elif abs(dx) == abs(dy):
            sign_y = 1 if dy > 0 else -1
            sign_x_correction = sign_y if dx > 0 else -sign_y

            for i in range(sign_y, dy, sign_y):
                if board[self.position[0] + i][self.position[1] + i * sign_x_correction] is not None:
                    return False
        else:
            return False

        return True


def init_board():
    for i in range(8):
        Pawn("white", [1, i])
        Pawn("black", [6, i])

    for i in range(2):
        Bishop("white", [0, 5 - 3 * i])
        Bishop("black", [7, 5 - 3 * i])
        Knight("white", [0, 6 - 5 * i])
        Knight("black", [7, 6 - 5 * i])
        Rook("white", [0, 7 * i])
        Rook("black", [7, 7 * i])

    King("white", [0, 4])
    King("black", [7, 4])
    Queen("white", [0, 3])
    Queen("black", [7, 3])


def game_over():
    white_king_present = any(
        piece is not None and piece.name == "King" and piece.color == "white" for piece in sum(board, []))
    black_king_present = any(
        piece is not None and piece.name == "King" and piece.color == "black" for piece in sum(board, []))

    if white_king_present and black_king_present:
        return False

    winning_color = ("White" if white_king_present else "Black")
    print_board(winning_color)
    print(Back.GREEN + Fore.WHITE + Style.BRIGHT + winning_color, "has WON!" + Style.RESET_ALL)
    return True


def game():
    turn = WHITE
    init_board()
    print_board(colors[turn])
    while not game_over():
        new_pos = get_position("Your move? ")
        possibilities = []
        for line in board:
            for piece in line:
                if piece is not None and piece.color == colors[turn] and piece.validate_move(new_pos):
                    possibilities += [piece]
        if not len(possibilities):
            print_board(colors[turn])
            print("No piece can move there")
            continue
        elif len(possibilities) == 1:
            possibilities[0].move(new_pos)
        else:
            positions = [piece.position for piece in possibilities]
            piece_pos = None
            while piece_pos not in positions:
                piece_pos = get_position("Where is the piece you wanna move? ")

            possibilities[positions.index(piece_pos)].move(new_pos)

        turn = (turn + 1) % 2
        print_board(colors[turn])


if __name__ == '__main__':
    game()
