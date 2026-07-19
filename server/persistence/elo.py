"""Standard ELO rating math - pure functions, no persistence/game knowledge."""

from config import ELO_K_FACTOR


def expected_score(rating_a: int, rating_b: int) -> float:
    """Probability A is expected to score against B, per the standard ELO curve."""
    return 1 / (1 + 10 ** ((rating_b - rating_a) / 400))


def update_ratings(rating_a: int, rating_b: int, score_a: float) -> tuple[int, int]:
    """New (rating_a, rating_b) after a game where A actually scored score_a
    (1.0 win, 0.0 loss). The engine's only end condition is king capture -
    no draw concept exists today - so 0.5 is never actually reached, but
    accepted here for forward compatibility rather than restricting the
    type to {0, 1}."""
    expected_a = expected_score(rating_a, rating_b)
    score_b = 1 - score_a
    expected_b = 1 - expected_a
    new_a = round(rating_a + ELO_K_FACTOR * (score_a - expected_a))
    new_b = round(rating_b + ELO_K_FACTOR * (score_b - expected_b))
    return new_a, new_b
