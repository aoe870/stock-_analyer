import math

import pytest

from stock_analyzer_app.indicators import cross, ema, ref


def assert_series_close(actual, expected):
    assert len(actual) == len(expected)
    for left, right in zip(actual, expected):
        if right is None:
            assert left is None
        else:
            assert left == pytest.approx(right)


def test_ref_returns_previous_values_with_none_padding():
    assert ref([10, 20, 30, 40]) == [None, 10, 20, 30]
    assert ref([10, 20, 30, 40], periods=2) == [None, None, 10, 20]


def test_cross_true_only_when_left_moves_above_right():
    left = [1, 2, 3, 2, 5]
    right = [2, 2, 2, 3, 4]

    assert cross(left, right) == [False, False, True, False, True]


def test_ema_uses_pandas_span_adjust_false_semantics():
    values = [10, 12, 13, 12]
    alpha = 2 / (3 + 1)
    expected = [
        10,
        10 + alpha * (12 - 10),
        11 + alpha * (13 - 11),
        12 + alpha * (12 - 12),
    ]

    assert_series_close(ema(values, 3), expected)


def test_ema_preserves_missing_values_until_next_real_value():
    actual = ema([None, 10, math.nan, 14], 3)

    assert actual[0] is None
    assert actual[1] == pytest.approx(10)
    assert actual[2] is None
    assert actual[3] == pytest.approx(12)

