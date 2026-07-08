import sys
from engine import ChessEngine
from parser import BoardParser
from router import TextCommandRouter

def main():
    # Read all input from standard input
    input_text = sys.stdin.read().strip()
    if not input_text:
        return

    parser = BoardParser()
    board_matrix, command_lines = parser.parse(input_text)

    if not board_matrix:
        return

    engine = ChessEngine(board_matrix)
    router = TextCommandRouter(engine)

    for command in command_lines:
        router.process_command(command)

if __name__ == "__main__":
    main()