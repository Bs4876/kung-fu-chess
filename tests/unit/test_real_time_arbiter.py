from model.position import Position
from realtime.real_time_arbiter import RealTimeArbiter


def test_no_active_motion_initially():
    arb = RealTimeArbiter()
    assert not arb.has_active_motion()


def test_has_active_motion_after_start():
    arb = RealTimeArbiter()
    arb.start_motion("wR", Position(0, 0), Position(0, 2))
    assert arb.has_active_motion()


def test_one_cell_arrives_after_1000ms():
    arb = RealTimeArbiter()
    arb.start_motion("wR", Position(0, 0), Position(0, 1))
    events = arb.advance_time(1000)
    assert len(events) == 1
    assert events[0].piece_token == "wR"
    assert events[0].src == Position(0, 0)
    assert events[0].dst == Position(0, 1)


def test_two_cells_arrives_after_2000ms():
    arb = RealTimeArbiter()
    arb.start_motion("wR", Position(0, 0), Position(0, 2))
    events = arb.advance_time(2000)
    assert len(events) == 1


def test_not_arrived_before_full_time():
    arb = RealTimeArbiter()
    arb.start_motion("wR", Position(0, 0), Position(0, 1))
    events = arb.advance_time(999)
    assert len(events) == 0
    assert arb.has_active_motion()


def test_partial_wait_then_remaining():
    arb = RealTimeArbiter()
    arb.start_motion("wR", Position(0, 0), Position(0, 1))
    arb.advance_time(500)
    assert arb.has_active_motion()
    events = arb.advance_time(500)
    assert len(events) == 1
    assert not arb.has_active_motion()


def test_no_active_motion_after_arrival():
    arb = RealTimeArbiter()
    arb.start_motion("wR", Position(0, 0), Position(0, 1))
    arb.advance_time(1000)
    assert not arb.has_active_motion()



def test_diagonal_uses_max_distance():
    arb = RealTimeArbiter()
    arb.start_motion("wB", Position(0, 0), Position(3, 3))
    events = arb.advance_time(2999)
    assert len(events) == 0
    events = arb.advance_time(1)
    assert len(events) == 1
