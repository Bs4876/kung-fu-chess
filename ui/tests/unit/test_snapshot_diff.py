from types import SimpleNamespace

from model.position import Position
from state.game_events import PieceArrived, PieceCaptured, PieceHalted, Promotion
from state.snapshot_diff import FrozenSnapshot, diff_completed_motion


class FakeSnapshot:
    """A minimal get_piece(pos)/rows/cols stand-in - no real Board needed."""

    def __init__(self, tokens: dict, rows=8, cols=8):
        self._tokens = tokens
        self.rows = rows
        self.cols = cols

    def get_piece(self, pos):
        return self._tokens.get(pos, ".")


def motion(source, destination, token, expected_target=".", is_jump=False):
    return SimpleNamespace(
        source=source, destination=destination, token=token, expected_target=expected_target, is_jump=is_jump
    )


def test_stale_target_cancellation_produces_no_events():
    src, dst = Position(0, 0), Position(0, 3)
    prev = FakeSnapshot({src: "wR"})
    curr = FakeSnapshot({src: "wR"})  # never left
    assert diff_completed_motion(motion(src, dst, "wR"), prev, curr) == []


def test_clean_arrival_onto_empty_square():
    src, dst = Position(0, 0), Position(0, 3)
    prev = FakeSnapshot({src: "wR"})
    curr = FakeSnapshot({dst: "wR"})
    events = diff_completed_motion(motion(src, dst, "wR"), prev, curr)
    assert events == [PieceArrived(source=src, destination=dst, token="wR")]


def test_capture_on_arrival():
    src, dst = Position(0, 0), Position(0, 3)
    prev = FakeSnapshot({src: "wR", dst: "bP"})
    curr = FakeSnapshot({dst: "wR"})
    events = diff_completed_motion(motion(src, dst, "wR", expected_target="bP"), prev, curr)
    assert events == [PieceCaptured(position=dst, captured_token="bP", by_token="wR")]


def test_promotion_on_arrival():
    src, dst = Position(1, 0), Position(0, 0)
    prev = FakeSnapshot({src: "wP"})
    curr = FakeSnapshot({dst: "wQ"})
    events = diff_completed_motion(motion(src, dst, "wP"), prev, curr)
    assert events == [Promotion(position=dst, from_token="wP", to_token="wQ")]


def test_mid_flight_halt_at_a_third_cell():
    src, dst, halt_cell = Position(2, 0), Position(0, 2), Position(1, 1)
    prev = FakeSnapshot({src: "wB"})
    curr = FakeSnapshot({halt_cell: "wB"})
    events = diff_completed_motion(motion(src, dst, "wB"), prev, curr)
    assert events == [PieceHalted(source=src, resting_at=halt_cell, token="wB")]


def test_mid_flight_kill_with_no_replacement_anywhere():
    src, dst = Position(2, 0), Position(0, 2)
    prev = FakeSnapshot({src: "wB"})
    curr = FakeSnapshot({})  # piece is just gone
    events = diff_completed_motion(motion(src, dst, "wB"), prev, curr)
    assert events == [PieceCaptured(position=src, captured_token="wB", by_token=None)]


def test_is_jump_propagates_from_the_motion_to_the_resulting_event():
    src, dst = Position(0, 0), Position(0, 3)
    prev = FakeSnapshot({src: "wR"})
    curr = FakeSnapshot({dst: "wR"})
    events = diff_completed_motion(motion(src, dst, "wR", is_jump=True), prev, curr)
    assert events == [PieceArrived(source=src, destination=dst, token="wR", is_jump=True)]


def test_frozen_snapshot_is_immune_to_later_mutation_of_the_source():
    class MutableSnapshot:
        def __init__(self):
            self.rows, self.cols = 1, 1
            self.token = "."

        def get_piece(self, pos):
            return self.token

    live = MutableSnapshot()
    frozen = FrozenSnapshot(live)
    live.token = "wQ"  # mutate the live board after freezing
    assert frozen.get_piece(Position(0, 0)) == "."
