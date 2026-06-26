import math
from collections.abc import Sequence


Number = int | float


def _is_missing(value: object) -> bool:
    return value is None or (isinstance(value, float) and math.isnan(value))


def ref(values: Sequence[object], periods: int = 1) -> list[object | None]:
    if periods < 1:
        raise ValueError("periods must be at least 1")
    return [None] * min(periods, len(values)) + list(values[:-periods])


def cross(left: Sequence[Number | None], right: Sequence[Number | None]) -> list[bool]:
    if len(left) != len(right):
        raise ValueError("left and right must have the same length")

    result: list[bool] = []
    for index, (left_value, right_value) in enumerate(zip(left, right)):
        if index == 0:
            result.append(False)
            continue

        prev_left = left[index - 1]
        prev_right = right[index - 1]
        has_missing = any(_is_missing(value) for value in (left_value, right_value, prev_left, prev_right))
        result.append(False if has_missing else left_value > right_value and prev_left <= prev_right)  # type: ignore[operator]
    return result


def ema(values: Sequence[Number | None], period: int) -> list[float | None]:
    if period < 1:
        raise ValueError("period must be at least 1")

    alpha = 2 / (period + 1)
    previous: float | None = None
    output: list[float | None] = []

    for value in values:
        if _is_missing(value):
            output.append(None)
            continue

        numeric = float(value)
        previous = numeric if previous is None else previous + alpha * (numeric - previous)
        output.append(previous)

    return output

