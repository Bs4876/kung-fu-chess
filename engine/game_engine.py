from model.board import Board, EMPTY
from model.position import Position
from rules.rule_engine import RuleEngine
from realtime.real_time_arbiter import RealTimeArbiter


class MoveResult:
    def __init__(self, is_accepted: bool, reason: str):
        self.is_accepted = is_accepted
        self.reason = reason


class GameSnapshot:
    def __init__(self, rows: int, cols: int, pieces: dict, game_over: bool):
        self.rows = rows
        self.cols = cols
        self._pieces = pieces
        self.game_over = game_over

    def get_piece(self, pos) -> str:
        return self._pieces.get((pos.row, pos.col), EMPTY)


class GameEngine:
    def __init__(self, board: Board):
        self._board = board
        self._rule_engine = RuleEngine()
        self._arbiter = RealTimeArbiter()
        self._game_over = False

    @property
    def game_over(self) -> bool:
        return self._game_over

    def request_move(self, source: Position, destination: Position) -> MoveResult:
        if self._game_over:
            return MoveResult(False, "game_over")

        if self._arbiter.has_active_motion():
            return MoveResult(False, "motion_in_progress")

        validation = self._rule_engine.validate_move(self._board, source, destination)
        if not validation.is_valid:
            return MoveResult(False, validation.reason)

        token = self._board.get_piece(source)
        self._arbiter.start_motion(token, source, destination)
        return MoveResult(True, "ok")

    def wait(self, ms: int) -> None:
        events = self._arbiter.advance_time(ms)
        for event in events:
            self._apply_arrival(event)

    def snapshot(self) -> GameSnapshot:
        pieces = {}
        for r in range(self._board.rows):
            for c in range(self._board.cols):
                from model.position import Position as P
                token = self._board.get_piece(P(r, c))
                if token != EMPTY:
                    pieces[(r, c)] = token
        return GameSnapshot(self._board.rows, self._board.cols, pieces, self._game_over)

    def _apply_arrival(self, event) -> None:
        src, dst = event.src, event.dst

        if self._board.get_piece(src) != event.piece_token:
            return

        target = self._board.get_piece(dst)
        if target != EMPTY and target[0] == event.piece_token[0]:
            return

        if target != EMPTY and target[1] == "K":
            self._game_over = True

        self._board.move_piece(src, dst)
