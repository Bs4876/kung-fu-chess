import pytest

from persistence.elo import expected_score, update_ratings


def test_expected_score_is_half_for_equal_ratings():
    assert expected_score(1200, 1200) == 0.5


def test_expected_score_favors_the_higher_rated_player():
    assert expected_score(1400, 1200) > 0.5
    assert expected_score(1200, 1400) < 0.5


def test_expected_scores_for_both_sides_sum_to_one():
    assert expected_score(1350, 1180) + expected_score(1180, 1350) == pytest.approx(1.0)


def test_winner_gains_rating_and_loser_loses_it_by_the_same_amount():
    new_winner, new_loser = update_ratings(1200, 1200, score_a=1.0)
    assert new_winner > 1200
    assert new_loser < 1200
    assert (new_winner - 1200) == (1200 - new_loser)  # equal ratings -> symmetric swing


def test_upset_win_gains_more_than_an_expected_win():
    # A(1000) beating B(1400) is a bigger surprise than A(1400) beating B(1000).
    upset_gain = update_ratings(1000, 1400, score_a=1.0)[0] - 1000
    expected_gain = update_ratings(1400, 1000, score_a=1.0)[0] - 1400
    assert upset_gain > expected_gain


def test_a_loss_moves_ratings_the_opposite_direction_of_a_win():
    win_a, win_b = update_ratings(1200, 1200, score_a=1.0)
    loss_a, loss_b = update_ratings(1200, 1200, score_a=0.0)
    assert win_a > 1200 > loss_a
    assert win_b < 1200 < loss_b
