"""White-box tests for validators.utils (``@validator`` decorator).

Design methods used:
    * Path coverage on the decorator ``wrapper``:
        P1: func returns truthy, no r_ve, no env        -> True
        P2: func returns falsy, no r_ve, no env         -> ValidationError
        P3: r_ve=True, func truthy                      -> True
        P4: r_ve=True, func falsy                       -> raises ValidationError
        P5: RAISE_VALIDATION_ERROR env truthy           -> raises
        P6: func raises ValueError  (no r_ve)           -> ValidationError
        P7: func raises TypeError   (r_ve=True)         -> raises ValidationError
        P8: func raises UnicodeError                    -> ValidationError
    * Data-flow on the ``raise_validation_error`` flag — defined once,
      possibly re-assigned from kwargs or env, then used in the two
      branching points. Every def/use combination is exercised.
    * Exercise ``ValidationError`` dunder methods (__repr__, __str__,
      __bool__) for statement coverage.
"""

# standard
import os

# external
import pytest

# local
from validators.utils import ValidationError, validator, _func_args_as_dict


# ---------------------------------------------------------------------------
# Decorator paths
# ---------------------------------------------------------------------------


@validator
def _even(value, /):
    return value % 2 == 0


@validator
def _raises_value_error(value, /):
    raise ValueError("boom")


@validator
def _raises_type_error(value, /):
    raise TypeError("tboom")


@validator
def _raises_unicode_error(value, /):
    raise UnicodeError("uboom")


def test_validator_truthy_returns_true():          # P1
    assert _even(4) is True


def test_validator_falsy_returns_error():          # P2
    assert isinstance(_even(5), ValidationError)


def test_validator_r_ve_true_passes_through():     # P3
    assert _even(4, r_ve=True) is True


def test_validator_r_ve_raises_on_falsy():         # P4
    with pytest.raises(ValidationError):
        _even(5, r_ve=True)


def test_validator_env_variable_raises(monkeypatch):  # P5
    monkeypatch.setenv("RAISE_VALIDATION_ERROR", "True")
    with pytest.raises(ValidationError):
        _even(5)


def test_validator_env_variable_not_true(monkeypatch):
    # covers the env branch where the value is present but != "True"
    monkeypatch.setenv("RAISE_VALIDATION_ERROR", "false")
    assert isinstance(_even(5), ValidationError)


def test_validator_value_error_wrapped():          # P6
    assert isinstance(_raises_value_error("x"), ValidationError)


def test_validator_type_error_raised_when_r_ve():  # P7
    with pytest.raises(ValidationError):
        _raises_type_error("x", r_ve=True)


def test_validator_unicode_error_wrapped():        # P8
    assert isinstance(_raises_unicode_error("x"), ValidationError)


# ---------------------------------------------------------------------------
# _func_args_as_dict — data flow on the argument dict
# ---------------------------------------------------------------------------


def test_func_args_as_dict_positional_and_kwargs():
    def sample(a, b, /, *, c=None):
        return None

    out = _func_args_as_dict(sample, 1, 2, c=3)
    assert out == {"a": 1, "b": 2, "c": 3}


# ---------------------------------------------------------------------------
# ValidationError — dunders
# ---------------------------------------------------------------------------


def test_validation_error_repr_and_bool():
    def sample(value, /):
        return None

    err = ValidationError(sample, {"value": 42})
    assert "sample" in repr(err)
    assert "42" in repr(err)
    assert str(err) == repr(err)
    assert bool(err) is False


def test_validation_error_with_message_sets_reason():
    def sample(value, /):
        return None

    err = ValidationError(sample, {"value": 1}, message="bad")
    assert err.reason == "bad"
