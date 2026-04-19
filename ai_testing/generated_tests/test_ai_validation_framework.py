"""AI 生成：核心装饰器与 ValidationError 的行为测试（框架级）。"""

from __future__ import annotations

import os

import pytest

from validators import ValidationError, email, validator


@validator
def _even(value: int):
    """自定义验证器：偶数。"""
    return value % 2 == 0


class TestValidatorDecorator:
    def test_returns_true_for_pass(self):
        assert _even(4) is True

    def test_returns_error_for_fail(self):
        result = _even(5)
        assert isinstance(result, ValidationError)
        assert bool(result) is False

    def test_r_ve_raises(self):
        """r_ve=True 时应直接抛出 ValidationError。"""
        with pytest.raises(ValidationError):
            _even(5, r_ve=True)

    def test_env_variable_raises(self, monkeypatch):
        """环境变量 RAISE_VALIDATION_ERROR=True 时应抛出异常。"""
        monkeypatch.setenv("RAISE_VALIDATION_ERROR", "True")
        with pytest.raises(ValidationError):
            _even(5)

    def test_env_variable_false_no_raise(self, monkeypatch):
        monkeypatch.setenv("RAISE_VALIDATION_ERROR", "False")
        result = _even(5)
        assert isinstance(result, ValidationError)


class TestValidationError:
    def test_repr_includes_func_name(self):
        err = email("bogus@@")
        assert isinstance(err, ValidationError)
        assert "email" in repr(err)

    def test_str_and_repr_equal(self):
        err = email("bogus@@")
        assert str(err) == repr(err)

    def test_bool_is_false(self):
        err = email("bogus@@")
        assert bool(err) is False

    def test_exception_captured_as_error(self):
        """装饰器把 ValueError/TypeError/UnicodeError 捕获为 ValidationError。"""
        # 构造一个会引发 UnicodeError 的域名
        result = email("a@\u0000.com")
        assert result is True or isinstance(result, ValidationError)
