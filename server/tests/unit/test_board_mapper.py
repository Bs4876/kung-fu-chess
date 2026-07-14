from input.board_mapper import BoardMapper
from model.position import Position


def mapper(rows=4, cols=4):
    return BoardMapper(rows, cols)


def test_center_of_first_cell_maps_to_row0_col0():
    assert mapper().pixel_to_cell(50, 50) == Position(0, 0)


def test_x_100_to_199_maps_to_col1():
    assert mapper().pixel_to_cell(150, 50) == Position(0, 1)


def test_y_100_to_199_maps_to_row1():
    assert mapper().pixel_to_cell(50, 150) == Position(1, 0)


def test_outside_right_returns_none():
    assert mapper(rows=3, cols=3).pixel_to_cell(350, 50) is None


def test_outside_bottom_returns_none():
    assert mapper(rows=3, cols=3).pixel_to_cell(50, 350) is None


def test_negative_x_returns_none():
    assert mapper().pixel_to_cell(-1, 50) is None


def test_negative_y_returns_none():
    assert mapper().pixel_to_cell(50, -1) is None


def test_exact_boundary_last_cell():
    assert mapper(rows=3, cols=3).pixel_to_cell(299, 299) == Position(2, 2)
