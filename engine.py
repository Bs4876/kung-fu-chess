from board import Board
from constants import EMPTY_CELL, JUMP_TRAVEL_TIME, MOVE_TRAVEL_TIME
from movement import MoveValidator

class ChessEngine:
    def __init__(self, board_matrix):
        self.board = board_matrix if isinstance(board_matrix, Board) else Board(board_matrix)
        self.rows = self.board.rows
        self.cols = self.board.cols
        self.selected_pos = None
        self.game_clock = 0
        self.ongoing_moves = []
        self.pieces_in_flight = set()
        self.game_over = False
        
        # Tracks pieces jumping in place: (arrival_time, row, col, piece_token)
        self.ongoing_jumps = []

    def jump(self, x, y):
        """Direct jump command route mapped from parser/router input rules."""
        self._refresh_board_state()
        if self.game_over:
            return

        row = y // 100
        col = x // 100

        if not (0 <= row < self.rows and 0 <= col < self.cols):
            return

        self._execute_jump(row, col)

    def click(self, x, y):
        self._refresh_board_state()
        if self.game_over:
            return

        row = y // 100
        col = x // 100

        if not (0 <= row < self.rows and 0 <= col < self.cols):
            return

        if (row, col) in self.pieces_in_flight and self.selected_pos is None:
            return

        token = self.board.get_piece(row, col)

        if token != EMPTY_CELL:
            if self.selected_pos is None:
                self.selected_pos = (row, col)
            else:
                curr_row, curr_col = self.selected_pos
                if curr_row == row and curr_col == col:
                    self._execute_jump(row, col)
                elif token[0] == self.board.get_piece(curr_row, curr_col)[0]:
                    self.selected_pos = (row, col)
                else:
                    self._execute_move(curr_row, curr_col, row, col)
        else:
            if self.selected_pos is not None:
                curr_row, curr_col = self.selected_pos
                if curr_row == row and curr_col == col:
                    self._execute_jump(row, col)
                else:
                    self._execute_move(curr_row, curr_col, row, col)

    def wait(self, ms):
        self.game_clock += ms
        self._refresh_board_state()

    def print_board(self):
        self._refresh_board_state()
        for row in range(self.rows):
            line = [self.board.get_piece(row, col) for col in range(self.cols)]
            print(" ".join(line))

    def _execute_jump(self, row, col):
        jumping_piece = self.board.get_piece(row, col)
        if jumping_piece == EMPTY_CELL:
            return

        if (row, col) in self.pieces_in_flight:
            return

        arrival_time = self.game_clock + JUMP_TRAVEL_TIME
        self.ongoing_jumps.append((arrival_time, row, col, jumping_piece))
        self.pieces_in_flight.add((row, col))
        self.selected_pos = None

    def _execute_move(self, from_row, from_col, to_row, to_col):
        if self.game_over:
            return

        moving_piece = self.board.get_piece(from_row, from_col)
        target_piece = self.board.get_piece(to_row, to_col)
        
        if moving_piece == EMPTY_CELL:
            return

        if (from_row, from_col) in self.pieces_in_flight:
            return

        piece_type = moving_piece[1]
        piece_color = moving_piece[0]

        for move in self.ongoing_moves:
            if move[5][0] != piece_color:
                return

        if target_piece != EMPTY_CELL and target_piece[0] == moving_piece[0]:
            return

        if not MoveValidator.is_valid_move(piece_type, from_row, from_col, to_row, to_col, self.board, piece_color):
            return

        arrival_time = self.game_clock + MOVE_TRAVEL_TIME

        self.ongoing_moves.append((arrival_time, from_row, from_col, to_row, to_col, moving_piece))
        self.pieces_in_flight.add((from_row, from_col))
        self.selected_pos = None

    def _refresh_board_state(self):
        # 1. Update jumps and track active airborne defense cells
        airborne_cells = {}
        remaining_jumps = []
        for jump in self.ongoing_jumps:
            end_time, r, c, token = jump
            airborne_cells[(r, c)] = token
            if self.game_clock < end_time:
                remaining_jumps.append(jump)
            else:
                self.pieces_in_flight.discard((r, c))
        self.ongoing_jumps = remaining_jumps

        # 2. Process moves
        remaining_moves = []
        self.ongoing_moves.sort(key=lambda m: m[0])

        for move in self.ongoing_moves:
            arrival_time, from_row, from_col, to_row, to_col, piece_token = move
            
            # Check if game ended
            if self.game_over:
                self.pieces_in_flight.discard((from_row, from_col))
                continue

            # NEW: Check if the moving piece's destination is currently defended by an airborne unit
            if (to_row, to_col) in airborne_cells:
                defender = airborne_cells[(to_row, to_col)]
                if defender[0] != piece_token[0]:
                    # The arriving piece hits an airborne defender and is destroyed immediately
                    self.board.set_piece(from_row, from_col, EMPTY_CELL)
                    self.pieces_in_flight.discard((from_row, from_col))
                    continue

            if self.game_clock >= arrival_time:
                # Execution logic
                if self.board.get_piece(from_row, from_col) != move[5]:
                    self.pieces_in_flight.discard((from_row, from_col))
                    continue

                current_target = self.board.get_piece(to_row, to_col)
                if current_target != EMPTY_CELL and current_target[0] == piece_token[0]:
                    self.pieces_in_flight.discard((from_row, from_col))
                    continue

                if current_target != EMPTY_CELL and current_target[1] == 'K':
                    self.game_over = True

                if piece_token[1] == 'P' and self.rows >= 8 and (to_row == 0 or to_row == self.rows - 1):
                    piece_token = piece_token[0] + 'Q'

                self.board.set_piece(from_row, from_col, EMPTY_CELL)
                self.board.set_piece(to_row, to_col, piece_token)
                self.pieces_in_flight.discard((from_row, from_col))
                
                if self.game_over:
                    self.ongoing_moves = []
                    return
            else:
                remaining_moves.append(move)
                
        self.ongoing_moves = remaining_moves