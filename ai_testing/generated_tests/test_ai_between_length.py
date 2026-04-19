"""AI 生成：between / length 数值与长度范围验证器功能测试。"""

from __future__ import annotations

from datetime import datetime

import pytest

from validators import between, length
from conftest import assert_invalid, assert_valid


class TestBetweenNumeric:
    @pytest.mark.parametrize(
        "value,lo,hi,expected",
        [
            (5, 1, 10, True),
            (1, 1, 10, True),        # 下边界包含
            (10, 1, 10, True),       # 上边界包含
            (0, 1, 10, False),
            (11, 1, 10, False),
            (13.2, 13, 14, True),
            (-1, -5, 5, True),
        ],
    )
    def test_int_float(self, value, lo, hi, expected):
        result = between(value, min_val=lo, max_val=hi)
        if expected:
            assert_valid(result)
        else:
            assert_invalid(result)

    def test_only_min(self):
        assert_valid(between(5, min_val=2))

    def test_only_max(self):
        assert_invalid(between(500, max_val=400))

    def test_datetime(self):
        assert_valid(
            between(
                datetime(2000, 11, 11),
                min_val=datetime(1999, 11, 11),
                max_val=datetime(2001, 11, 11),
            )
        )

    def test_none_value(self):
        assert_invalid(between(None, min_val=1, max_val=10))

    def test_min_greater_than_max_raises(self):
        """min>max 必须导致校验失败。"""
        assert_invalid(between(5, min_val=10, max_val=1))


class TestLength:
    @pytest.mark.parametrize(
        "s,lo,hi,expected",
        [
            ("something", 2, None, True),
            ("something", 9, 9, True),
            ("something", None, 5, False),
            ("", 0, 0, True),
            ("abc", 3, 3, True),
            ("abc", 4, None, False),
        ],
    )
    def test_cases(self, s, lo, hi, expected):
        result = length(s, min_val=lo, max_val=hi)
        if expected:
            assert_valid(result)
        else:
            assert_invalid(result)

    def test_negative_min_raises(self):
        """min_val<0 需抛 ValueError；validators 封装后转化为 ValidationError。"""
        assert_invalid(length("abc", min_val=-1))

    def test_negative_max_raises(self):
        assert_invalid(length("abc", max_val=-1))
