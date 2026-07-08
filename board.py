class Board:
    def __init__(self, matrix):
        if matrix is None:
            raise ValueError("Board matrix cannot be None")

        self._rows = len(matrix)
        self._cols = len(matrix[0]) if self._rows > 0 else 0
        self._matrix = [list(row) for row in matrix]

        for row in self._matrix:
            if len(row) != self._cols:
                raise ValueError("All rows in the board matrix must have the same length")

    @property
    def rows(self):
        return self._rows

    @property
    def cols(self):
        return self._cols

    def is_in_bounds(self, row, col):
        return 0 <= row < self._rows and 0 <= col < self._cols

    def get_piece(self, row, col):
        if not self.is_in_bounds(row, col):
            raise IndexError(f"Board position out of bounds: ({row}, {col})")
        return self._matrix[row][col]

    def set_piece(self, row, col, piece):
        if not self.is_in_bounds(row, col):
            raise IndexError(f"Board position out of bounds: ({row}, {col})")
        self._matrix[row][col] = piece

    def is_empty(self, row, col):
        return self.get_piece(row, col) == '.'
