"""AI 生成：国家相关验证器 calling_code / country_code / currency 功能测试。"""

from __future__ import annotations

import pytest

from validators import calling_code, country_code, currency
from conftest import assert_invalid, assert_valid


class TestCallingCode:
    @pytest.mark.parametrize("value", ["+91", "+1", "+86", "+44", "+33"])
    def test_valid(self, value):
        assert_valid(calling_code(value))

    @pytest.mark.parametrize("value", ["", "-31", "91", "+9999", "abc"])
    def test_invalid(self, value):
        assert_invalid(calling_code(value))


class TestCountryCode:
    @pytest.mark.parametrize(
        "value,fmt",
        [
            ("USA", "alpha3"),
            ("ZWE", "alpha3"),
            ("US", "alpha2"),
            ("CN", "alpha2"),
            ("840", "numeric"),
            ("156", "numeric"),
            ("US", "auto"),
            ("USA", "auto"),
            ("840", "auto"),
        ],
    )
    def test_valid(self, value, fmt):
        assert_valid(country_code(value, iso_format=fmt))

    @pytest.mark.parametrize(
        "value,fmt",
        [
            ("GB", "alpha3"),
            ("iN", "alpha2"),         # 大小写不符
            ("ZZ", "alpha2"),
            ("XXX", "alpha3"),
            ("999", "numeric"),
            ("", "auto"),
            ("TOOLONG", "auto"),
        ],
    )
    def test_invalid(self, value, fmt):
        assert_invalid(country_code(value, iso_format=fmt))

    def test_ignore_case(self):
        assert_valid(country_code("us", iso_format="alpha2", ignore_case=True))
        assert_valid(country_code("usa", iso_format="alpha3", ignore_case=True))


class TestCurrency:
    @pytest.mark.parametrize("value", ["USD", "EUR", "CNY", "JPY", "GBP"])
    def test_valid(self, value):
        assert_valid(currency(value))

    @pytest.mark.parametrize("value", ["", "ZWX", "usd", "DOLLAR"])
    def test_invalid(self, value):
        assert_invalid(currency(value))

    def test_symbols(self):
        assert_valid(currency("€", skip_symbols=False))
        assert_valid(currency("¥", skip_symbols=False))
        assert_invalid(currency("€"))  # 默认 skip_symbols=True

    def test_ignore_case(self):
        assert_valid(currency("usd", ignore_case=True))
