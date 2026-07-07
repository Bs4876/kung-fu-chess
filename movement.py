class MoveValidator:
    @staticmethod
    def is_valid_move(piece_type, from_row, from_col, to_row, to_col):
        # Remaining in the exact same spot is an illegal operation
        if from_row == to_row and from_col == to_col:
            return False

        # Calculate absolute vector deltas
        d_row = abs(to_row - from_row)
        d_col = abs(to_col - from_col)

        # King movement strategy
        if piece_type == 'K':
            return d_row <= 1 and d_col <= 1

        # Rook movement strategy
        elif piece_type == 'R':
            return d_row == 0 or d_col == 0

        # Bishop movement strategy
        elif piece_type == 'B':
            return d_row == d_col

        # Queen movement strategy
        elif piece_type == 'Q':
            return (d_row == 0 or d_col == 0) or (d_row == d_col)

        # Knight movement strategy
        elif piece_type == 'N':
            return (d_row == 2 and d_col == 1) or (d_row == 1 and d_col == 2)

        return False