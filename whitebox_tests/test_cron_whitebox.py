"""White-box tests for validators.cron.

Design methods used:
    * Statement & branch coverage (C1/C2).
    * Basic path coverage on ``_validate_cron_component`` — cyclomatic
      complexity V(G) ≈ 13, so 13 linearly-independent paths are covered.
    * Data-flow analysis on ``cron`` — track def-use of the five split
      fields (minutes/hours/days/months/weekdays) through each validation
      gate.
"""

# external
import pytest

# local
from validators import ValidationError, cron
from validators.cron import _validate_cron_component


# ---------------------------------------------------------------------------
# _validate_cron_component — basic-path coverage
# ---------------------------------------------------------------------------
# CFG nodes of interest:
#   N1  component == "*"                                 (early True)
#   N2  component.isdecimal()                            (range check)
#   N3  "/" in component                                 (step form)
#   N3a   len(parts)!=2 / parts[1] non-decimal / int<1   (False)
#   N3b   parts[0] == "*"                                (True)
#   N3c   parts[0] decimal, range check
#   N4  "-" in component                                 (range form)
#   N4a   malformed dash                                 (False)
#   N4b   start/end range check
#   N5  "," in component                                 (list form, recurses)
#   N6  fall-through                                     (False)
#
# The parametrization below exercises every independent path at least once.


@pytest.mark.parametrize(
    "component, lo, hi, expected",
    [
        # P1  N1 — wildcard
        ("*", 0, 59, True),
        # P2  N2 — decimal in range
        ("30", 0, 59, True),
        # P3  N2 — decimal out of range (upper)
        ("60", 0, 59, False),
        # P4  N2 — decimal out of range (lower, via smaller domain)
        ("0", 1, 31, False),
        # P5  N3a — "/" wrong number of parts
        ("*/5/2", 0, 59, False),
        # P6  N3a — "/" step not decimal
        ("*/a", 0, 59, False),
        # P7  N3a — "/" step < 1
        ("*/0", 0, 59, False),
        # P8  N3b — "*/n" wildcard base
        ("*/5", 0, 59, True),
        # P9  N3c — "n/m" valid
        ("10/5", 0, 59, True),
        # P10 N3c — "n/m" base not decimal
        ("a/5", 0, 59, False),
        # P11 N3c — "n/m" base out of range
        ("60/5", 0, 59, False),
        # P12 N4a — "-" malformed
        ("-1", 0, 59, False),
        # P13 N4a — "-" non-decimal end
        ("5-a", 0, 59, False),
        # P14 N4b — valid range
        ("3-6", 0, 23, True),
        # P15 N4b — reversed range (start > end)
        ("30-20", 0, 59, False),
        # P16 N4b — endpoint out of range
        ("0-60", 0, 59, False),
        # P17 N5 — comma list, all valid (recursion hits N2 multiple times)
        ("1,3,5", 0, 6, True),
        # P18 N5 — comma list, one invalid item
        ("1,3,9", 0, 6, False),
        # P19 N5 — mixed digits in comma list
        ("0,12,23", 0, 23, True),
        # P20 N6 — fall-through (unknown symbol)
        ("&", 0, 59, False),
    ],
)
def test_validate_cron_component_paths(component, lo, hi, expected):
    assert _validate_cron_component(component, lo, hi) is expected


# ---------------------------------------------------------------------------
# cron — data-flow coverage
# ---------------------------------------------------------------------------
# Each of the five fields has a def (tuple-unpacking on line 63) and a use
# (inside the corresponding _validate_cron_component guard). The cases below
# kill each guard in turn so every (def, use) pair is exercised on both the
# passing and failing edge.


@pytest.mark.parametrize(
    "value",
    [
        "* * * * *",
        "*/5 * * * *",
        "0 0 1 1 0",
        "59 23 31 12 6",
        "1,3,5 0-6 */2 1-12 0,6",
    ],
)
def test_cron_all_fields_valid(value):
    assert cron(value) is True


@pytest.mark.parametrize(
    "value",
    [
        # minute field invalid
        "60 * * * *",
        # hour field invalid
        "0 24 * * *",
        # day field invalid (day uses 1..31 — "0" is a lower-bound kill)
        "0 0 0 1 0",
        # month field invalid
        "0 0 1 13 0",
        # weekday field invalid
        "0 0 1 1 7",
    ],
)
def test_cron_each_field_kill(value):
    assert isinstance(cron(value), ValidationError)


def test_cron_empty_string():
    # guard at line 59
    assert isinstance(cron(""), ValidationError)


def test_cron_wrong_arity_raises():
    # tuple-unpacking ValueError → re-raised, wrapped by @validator
    result = cron("* * * *")
    assert isinstance(result, ValidationError)


def test_cron_too_many_fields():
    assert isinstance(cron("* * * * * *"), ValidationError)
