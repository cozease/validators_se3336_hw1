"""White-box tests for validators.iban.

Design methods used:
    * Statement coverage of helpers ``_char_value`` and ``_mod_check``.
    * Basic path coverage on ``iban``:
        P1: value falsy             -> False
        P2: regex fails             -> ValidationError
        P3: regex matches + mod97   -> True
        P4: regex matches + !mod97  -> ValidationError
    * Data-flow on the ``rearranged`` string built inside ``_mod_check``:
      we verify its def (slice + concat) flows into the mod-97 use by
      constructing inputs where only the rearrangement order matters.
"""

# external
import pytest

# local
from validators import ValidationError, iban
from validators.iban import _char_value, _mod_check


# ---------------------------------------------------------------------------
# _char_value — branch coverage
# ---------------------------------------------------------------------------


def test_char_value_digit_branch():
    # digit branch: char is returned unchanged (as string)
    assert _char_value("7") == "7"


@pytest.mark.parametrize(
    "char, expected",
    [
        ("A", "10"),
        ("B", "11"),
        ("Z", "35"),
    ],
)
def test_char_value_letter_branch(char, expected):
    assert _char_value(char) == expected


# ---------------------------------------------------------------------------
# _mod_check — data-flow via rearranged string
# ---------------------------------------------------------------------------


def test_mod_check_accepts_valid_iban():
    assert _mod_check("DE29100500001061045672") is True


def test_mod_check_rejects_bad_checksum():
    # flip check digits so mod-97 != 1 (data-flow into the reshuffled string)
    assert _mod_check("DE00100500001061045672") is False


# ---------------------------------------------------------------------------
# iban — basic paths
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "value",
    [
        "DE29100500001061045672",
        "GB82WEST12345698765432",
        "NO9386011117947",
    ],
)
def test_iban_valid(value):
    assert iban(value) is True


def test_iban_empty_path():
    assert isinstance(iban(""), ValidationError)


@pytest.mark.parametrize(
    "value",
    [
        "123456",                        # shape wrong
        "DE!!100500001061045672",        # non-alnum inside
        "D29100500001061045672",         # too-short country block
    ],
)
def test_iban_regex_fail_path(value):
    assert isinstance(iban(value), ValidationError)


def test_iban_bad_checksum_path():
    # regex matches but mod-97 does not hold
    assert isinstance(iban("DE00100500001061045672"), ValidationError)
