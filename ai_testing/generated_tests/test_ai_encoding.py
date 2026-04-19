"""AI 生成：base16 / base32 / base58 / base64 编码验证器功能测试。"""

from __future__ import annotations

import pytest

from validators import base16, base32, base58, base64
from conftest import assert_invalid, assert_valid


class TestBase16:
    @pytest.mark.parametrize("value", ["a3f4b2", "0123456789ABCDEF", "deadbeef"])
    def test_valid(self, value):
        assert_valid(base16(value))

    @pytest.mark.parametrize("value", ["", "a3f4Z1", "hello world", "aa-bb"])
    def test_invalid(self, value):
        assert_invalid(base16(value))


class TestBase32:
    @pytest.mark.parametrize(
        "value",
        ["MFZWIZLTOQ======", "JBSWY3DPEBLW64TMMQ======", "AAAA"],
    )
    def test_valid(self, value):
        assert_valid(base32(value))

    @pytest.mark.parametrize(
        "value",
        ["", "MfZW3zLT9Q======", "AAAA1", "lowercase"],
    )
    def test_invalid(self, value):
        assert_invalid(base32(value))


class TestBase58:
    @pytest.mark.parametrize(
        "value",
        [
            "14pq6y9H2DLGahPsM4s7ugsNSD2uxpHsJx",
            "cUSECm5YzcXJwP",
        ],
    )
    def test_valid(self, value):
        assert_valid(base58(value))

    @pytest.mark.parametrize(
        "value",
        ["", "0OIl0", "abc!def"],
    )
    def test_invalid(self, value):
        assert_invalid(base58(value))


class TestBase64:
    @pytest.mark.parametrize(
        "value",
        [
            "Y2hhcmFjdGVyIHNldA==",
            "YWJjZA==",
            "YWJjZGVm",
            "YWJjZGU=",
        ],
    )
    def test_valid(self, value):
        assert_valid(base64(value))

    @pytest.mark.parametrize(
        "value",
        ["", "cUSECm5YzcXJwP", "abc!def", "=abcd"],
    )
    def test_invalid(self, value):
        assert_invalid(base64(value))
