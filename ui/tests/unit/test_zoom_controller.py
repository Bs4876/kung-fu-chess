from user_input.zoom_controller import ZoomController

IN_KEYS = frozenset({ord("+"), ord("=")})
OUT_KEYS = frozenset({ord("-"), ord("_")})


def build(min_multiplier=0.5, max_multiplier=2.0, step=0.25):
    return ZoomController(
        base_cell_size=100,
        min_multiplier=min_multiplier,
        max_multiplier=max_multiplier,
        step=step,
        zoom_in_keys=IN_KEYS,
        zoom_out_keys=OUT_KEYS,
    )


def test_starts_at_base_cell_size():
    zoom = build()
    assert zoom.cell_size == 100


def test_zoom_in_increases_cell_size_by_one_step():
    zoom = build()
    changed = zoom.handle_key(ord("+"))
    assert changed
    assert zoom.cell_size == 125


def test_zoom_out_decreases_cell_size_by_one_step():
    zoom = build()
    changed = zoom.handle_key(ord("-"))
    assert changed
    assert zoom.cell_size == 75


def test_shifted_and_unshifted_zoom_in_keys_both_work():
    zoom = build()
    zoom.handle_key(ord("="))
    assert zoom.cell_size == 125


def test_shifted_and_unshifted_zoom_out_keys_both_work():
    zoom = build()
    zoom.handle_key(ord("_"))
    assert zoom.cell_size == 75


def test_unrelated_key_is_a_no_op():
    zoom = build()
    changed = zoom.handle_key(ord("a"))
    assert not changed
    assert zoom.cell_size == 100


def test_none_key_is_a_no_op():
    zoom = build()
    changed = zoom.handle_key(None)
    assert not changed
    assert zoom.cell_size == 100


def test_zoom_in_clamps_at_max_multiplier():
    zoom = build(max_multiplier=1.25)
    zoom.handle_key(ord("+"))
    changed = zoom.handle_key(ord("+"))
    assert not changed
    assert zoom.cell_size == 125


def test_zoom_out_clamps_at_min_multiplier():
    zoom = build(min_multiplier=0.75)
    zoom.handle_key(ord("-"))
    changed = zoom.handle_key(ord("-"))
    assert not changed
    assert zoom.cell_size == 75
