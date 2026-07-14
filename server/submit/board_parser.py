from board import Board, EMPTY
from piece import _KIND_MAP


class BoardParser:
    def parse(self, text: str) -> Board:
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        if not lines:
            raise ValueError("Empty board definition")

        matrix = [line.split() for line in lines]
        cols = len(matrix[0])
        for row in matrix:
            if len(row) != cols:
                raise ValueError("Inconsistent row length")
            for token in row:
                if token != EMPTY and (len(token) != 2 or token[0] not in ("w", "b") or token[1] not in _KIND_MAP):
                    raise ValueError(f"Invalid token: {token}")

        return Board(matrix)
