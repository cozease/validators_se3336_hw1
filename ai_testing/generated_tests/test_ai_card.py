"""AI 生成：信用卡号验证器功能测试（Luhn + 品牌前缀/长度）。"""

from __future__ import annotations

import pytest

from validators import (
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
from conftest import assert_invalid, assert_valid


class TestLuhn:
    @pytest.mark.parametrize(
        "value",
        [
            "4242424242424242",  # Visa
            "5555555555554444",  # Mastercard
            "378282246310005",   # Amex
            "6200000000000005",  # UnionPay
            "3056930009020004",  # Diners
            "3566002020360505",  # JCB
            "6011111111111117",  # Discover
            "2200123456789019",  # Mir
        ],
    )
    def test_valid_luhn(self, value):
        assert_valid(card_number(value))

    @pytest.mark.parametrize(
        "value",
        [
            "",
            "4242424242424241",  # 改末位导致 Luhn 失败
            "1234567890",
            "abcd1234efgh5678",
        ],
    )
    def test_invalid_luhn(self, value):
        assert_invalid(card_number(value))


BRANDS = {
    "visa": (visa, "4242424242424242"),
    "mastercard": (mastercard, "5555555555554444"),
    "amex": (amex, "378282246310005"),
    "unionpay": (unionpay, "6200000000000005"),
    "diners": (diners, "3056930009020004"),
    "jcb": (jcb, "3566002020360505"),
    "discover": (discover, "6011111111111117"),
    "mir": (mir, "2200123456789019"),
}

# Mir 样本 2200... 会与 Mastercard 的前缀 22 冲突，作为已知缺陷单列
_KNOWN_OVERLAP = {("mastercard", "2200123456789019")}


class TestBrandMatrix:
    """品牌-样本交叉矩阵：每个品牌验证函数只对自己的样本返回 True。"""

    @pytest.mark.parametrize("brand", list(BRANDS.keys()))
    def test_positive(self, brand):
        func, sample = BRANDS[brand]
        assert_valid(func(sample))

    @pytest.mark.parametrize(
        "brand,foreign_sample",
        [
            (b, s)
            for b in BRANDS
            for s in [v[1] for k, v in BRANDS.items() if k != b]
            if (b, s) not in _KNOWN_OVERLAP
        ],
    )
    def test_cross_brand_rejection(self, brand, foreign_sample):
        func, _ = BRANDS[brand]
        assert_invalid(func(foreign_sample))

    @pytest.mark.xfail(
        strict=True,
        reason="[上游缺陷] Mastercard 正则 ^(22|23|24|25|26|27) 过于宽松，"
        "Mir 的 2200-2204 段号码会被错误地判为合法 Mastercard。",
    )
    def test_mir_should_not_match_mastercard(self):
        assert_invalid(mastercard("2200123456789019"))
