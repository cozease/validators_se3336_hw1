"""White-box tests for validators.between.

Design methods used:
    * Branch coverage on the four guards in ``between``:
        G1: value is None
        G2: max_val is None   -> AbsMax()
        G3: min_val is None   -> AbsMin()
        G4: min_val > max_val -> ValueError (and TypeError wrapping).
    * Data-flow on the ``min_val`` / ``max_val`` definitions: each is
      defined either from the caller or by the G2/G3 fallback, then used
      in both the order check (G4) and the final comparison. We exercise
      each def-use pair.
    * Cover the ``_extremes`` helpers used as default sentinels.
"""

# standard
from datetime import datetime

# external
import pytest

# local
from validators import ValidationError, between
from validators._extremes import AbsMax, AbsMin


# ---------------------------------------------------------------------------
# guard G1 — value is None
# ---------------------------------------------------------------------------


def test_between_none_value():
    assert isinstance(between(None, min_val=1, max_val=10), ValidationError)


# ---------------------------------------------------------------------------
# Guards G2 / G3 — default sentinels
# ---------------------------------------------------------------------------


def test_between_only_min():
    # max_val defaults to AbsMax → any finite upper bound passes
    assert between(10**9, min_val=0) is True


def test_between_only_max():
    # min_val defaults to AbsMin → any finite lower bound passes
    assert between(-(10**9), max_val=0) is True


def test_between_no_bounds_all_pass():
    # both guards fall through to AbsMax / AbsMin defaults
    assert between(42) is True


# ---------------------------------------------------------------------------
# Guard G4 — min > max  and TypeError path
# ---------------------------------------------------------------------------


def test_between_reversed_bounds_raises():
    # converted to ValidationError by the @validator decorator
    assert isinstance(between(5, min_val=10, max_val=1), ValidationError)


def test_between_type_mismatch_raises():
    # comparing datetime to int → TypeError path inside try/except
    assert isinstance(
        between(datetime(2024, 1, 1), min_val=0, max_val=10),
        ValidationError,
    )


# ---------------------------------------------------------------------------
# Happy-path value comparisons (final return statement)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "value, lo, hi, expected",
    [
        (5, 2, 10, True),
        (2, 2, 10, True),    # boundary low
        (10, 2, 10, True),   # boundary high
        (1, 2, 10, False),   # below
        (11, 2, 10, False),  # above
        (13.2, 13, 14, True),
        ("b", "a", "c", True),
        (datetime(2000, 1, 1), datetime(1999, 1, 1), datetime(2001, 1, 1), True),
    ],
)
def test_between_comparison(value, lo, hi, expected):
    result = between(value, min_val=lo, max_val=hi)
    if expected:
        assert result is True
    else:
        assert isinstance(result, ValidationError)


# ---------------------------------------------------------------------------
# _extremes module — reach the helper statements
# ---------------------------------------------------------------------------


def test_absmax_greater_than_everything():
    assert AbsMax() >= 10**18
    assert AbsMax() >= "zzz"


def test_absmin_less_than_everything():
    assert AbsMin() <= -(10**18)
    assert AbsMin() <= ""
