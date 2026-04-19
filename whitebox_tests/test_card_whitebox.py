"""White-box tests for validators.card.

Design methods used:
    * Condition/decision coverage on the compound boolean expression
      ``card_number(value) and len(value) == N and pattern.match(value)`` —
      each of the three conjuncts is independently falsified.
    * Basic-path coverage on ``card_number`` (Luhn): empty-string path,
      ValueError path (non-digit char), valid-sum path, invalid-sum path.
    * Data-flow on the ``digits`` definition inside ``card_number``: the
      variable is defined once and consumed in the odd/even slice uses
      — the ValueError case kills the def before the use.
"""

# external
import pytest

# local
from validators import (
    ValidationError,
    amex,
    card_number,
    diners,
    discover,
    jcb,
    mastercard,
    mir,
    unionpay,
    visa,
)


# ---------------------------------------------------------------------------
# card_number — Luhn basic paths
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "value",
    [
        "4242424242424242",   # Visa test card
        "5555555555554444",   # Mastercard test card
        "378282246310005",    # Amex test card (15 digits)
        "6011111111111117",   # Discover test card
    ],
)
def test_card_number_valid_luhn(value):
    assert card_number(value) is True


def test_card_number_invalid_luhn():
    # last digit tweaked to break the mod-10 sum
    assert isinstance(card_number("4242424242424241"), ValidationError)


def test_card_number_empty():
    # early-return branch at line 33
    assert isinstance(card_number(""), ValidationError)


def test_card_number_non_digit_triggers_value_error():
    # "list(map(int, value))" raises ValueError → caught and converted
    # to ValidationError by the @validator decorator.
    assert isinstance(card_number("4242abcd42424242"), ValidationError)


# ---------------------------------------------------------------------------
# Brand validators — condition/decision coverage
# ---------------------------------------------------------------------------
# For every brand we exercise:
#   (a) fully valid number                 -> True
#   (b) Luhn valid but wrong length        -> False (kills 2nd conjunct)
#   (c) Luhn valid, right length, wrong prefix -> False (kills 3rd conjunct)
#   (d) Luhn invalid                       -> False (kills 1st conjunct)


@pytest.mark.parametrize(
    "func, good, wrong_len, wrong_prefix",
    [
        (visa,       "4242424242424242",     "4242424242424",      "5555555555554444"),
        (mastercard, "5555555555554444",     "555555555555444",    "4242424242424242"),
        (amex,       "378282246310005",      "3782822463100051",   "4242424242424242"),
        (unionpay,   "6200000000000005",     "620000000000005",    "4242424242424242"),
        (jcb,        "3566002020360505",     "356600202036050",    "4242424242424242"),
        (discover,   "6011111111111117",     "601111111111117",    "4242424242424242"),
        (mir,        "2200123456789019",     "220012345678901",    "4242424242424242"),
    ],
)
def test_brand_condition_coverage(func, good, wrong_len, wrong_prefix):
    assert func(good) is True
    assert isinstance(func(wrong_len), ValidationError)
    assert isinstance(func(wrong_prefix), ValidationError)
    # Luhn-invalid kill — flip last digit
    bad_luhn = good[:-1] + ("0" if good[-1] != "0" else "1")
    assert isinstance(func(bad_luhn), ValidationError)


def test_diners_both_accepted_lengths():
    # diners accepts len in {14, 16} — exercise both arms of the set-membership
    # condition (data-flow on the computed `len(value)` use).
    assert diners("30569309025904") is True       # 14 digits
    assert diners("3056930009020004") is True     # 16 digits
    assert isinstance(diners("305693090259040"), ValidationError)  # 15 digits
