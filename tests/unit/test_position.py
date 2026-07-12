from model.position import Position


def test_equal_positions():
    assert Position(1, 2) == Position(1, 2)


def test_different_row_not_equal():
    assert Position(1, 2) != Position(2, 2)


def test_different_col_not_equal():
    assert Position(1, 2) != Position(1, 3)


def test_position_usable_as_dict_key():
    d = {Position(0, 0): "wK"}
    assert d[Position(0, 0)] == "wK"


def test_position_usable_in_set():
    s = {Position(0, 0), Position(0, 0), Position(1, 1)}
    assert len(s) == 2


def test_repr_is_readable():
    assert repr(Position(3, 4)) == "Position(3, 4)"
