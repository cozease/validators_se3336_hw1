"""AI 生成：金融证券编号（CUSIP / ISIN / SEDOL）验证器测试。

说明：在测试生成过程中，AI 基于源码对 `_isin_checksum` 的实现做了符号执行，
发现其循环体内并未累加 check 变量（疑似缺陷），因此会将任意符合字符
集与长度要求的 ISIN 全部通过。对应用例以 `xfail(strict=True)` 的方式
显式标注，作为《测试报告》中上报的真实缺陷证据。
"""

from __future__ import annotations

import pytest

from validators import cusip, isin, sedol
from conftest import assert_invalid, assert_valid


class TestCUSIP:
    @pytest.mark.parametrize(
        "value",
        ["037833DP2", "037833100"],
    )
    def test_valid(self, value):
        assert_valid(cusip(value))

    @pytest.mark.parametrize(
        "value",
        ["", "037833DP", "037833DP23", "037833DP3", "!!!!!!!!!"],
    )
    def test_invalid(self, value):
        assert_invalid(cusip(value))


class TestSEDOL:
    @pytest.mark.parametrize("value", ["2936921", "B0WNLY7"])
    def test_valid(self, value):
        assert_valid(sedol(value))

    @pytest.mark.parametrize(
        "value",
        ["", "29A6922", "2936922", "AEIOU12"],  # AEIOU 禁用
    )
    def test_invalid(self, value):
        assert_invalid(sedol(value))


class TestISIN:
    def test_length_and_charset_rejection(self):
        """位数不对或含非法字符时，必须拒绝。"""
        assert_invalid(isin(""))
        assert_invalid(isin("SHORT"))
        assert_invalid(isin("TOOLONG_STRING_12"))

    def test_valid_known(self):
        """真实可核对的 ISIN（Apple）。"""
        assert_valid(isin("US0378331005"))

    @pytest.mark.xfail(
        strict=True,
        reason="[上游缺陷] _isin_checksum 未累加 check，任意 12 位合法字符集字符串均判为 True",
    )
    def test_bad_checksum_should_fail(self):
        """应当拒绝校验位错误的 ISIN，但实际实现返回 True。"""
        assert_invalid(isin("US0378331004"))

    @pytest.mark.xfail(
        strict=True,
        reason="[上游缺陷] 任意 12 位字母数字都会被判为 True",
    )
    def test_random_should_fail(self):
        assert_invalid(isin("BADINVALID01"))
