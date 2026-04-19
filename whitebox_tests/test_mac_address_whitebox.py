"""White-box tests for validators.mac_address.

Design methods used:
    * Decision coverage on the mixed-separator guard
      (``":" in value and "-" in value``).
    * Equivalence-class partition on the regex match:
      colon-separated / hyphen-separated / invalid-length / bad-chars / empty.
    * Data-flow: the input ``value`` has one def and two uses (the
      separator guard and the regex). Every path must read ``value``
      consistently — we exercise both the True and False arms of the
      separator guard before the regex use.
"""

# external
import pytest

# local
from validators import ValidationError, mac_address


@pytest.mark.parametrize(
    "value",
    [
        "01:23:45:67:ab:CD",
        "aa:bb:cc:dd:ee:ff",
        "AA-BB-CC-DD-EE-FF",
        "00-00-00-00-00-00",
    ],
)
def test_mac_valid(value):
    assert mac_address(value) is True


@pytest.mark.parametrize(
    "value",
    [
        "",                          # empty — falsy short-circuit path
        "00:00:00:00:00",            # too few octets
        "00:00:00:00:00:00:00",      # too many
        "ZZ:ZZ:ZZ:ZZ:ZZ:ZZ",        # non-hex
        "01:23:45-67:ab:CD",         # mixed separator — kills guard True branch
        "01-23-45:67-ab-CD",         # mixed separator variant
        "0123.4567.89ab",            # wrong separator class
    ],
)
def test_mac_invalid(value):
    assert isinstance(mac_address(value), ValidationError)
