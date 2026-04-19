"""AI 生成：IPv4 / IPv6 验证器功能测试。"""

from __future__ import annotations

import pytest

from validators import ipv4, ipv6
from conftest import assert_invalid, assert_valid


class TestIPv4:
    @pytest.mark.parametrize(
        "value",
        [
            "0.0.0.0",
            "127.0.0.1",
            "192.168.1.1",
            "255.255.255.255",
            "8.8.8.8",
            "1.1.1.1/8",
            "203.0.113.0/24",
        ],
    )
    def test_valid(self, value):
        assert_valid(ipv4(value))

    @pytest.mark.parametrize(
        "value",
        [
            "",
            "256.0.0.1",
            "1.2.3",
            "1.2.3.4.5",
            "abc.def.ghi.jkl",
            "900.80.70.11",
            "1.2.3.4/33",
        ],
    )
    def test_invalid(self, value):
        assert_invalid(ipv4(value))

    def test_private_true_allows_private(self):
        assert_valid(ipv4("192.168.0.1", private=True))

    def test_private_false_rejects_private(self):
        assert_invalid(ipv4("192.168.0.1", private=False))

    def test_strict_requires_cidr(self):
        assert_invalid(ipv4("192.168.0.1", strict=True))


class TestIPv6:
    @pytest.mark.parametrize(
        "value",
        [
            "::1",
            "::1/128",
            "::ffff:192.0.2.128",
            "2001:db8::1",
            "fe80::1%eth0".split("%")[0],  # 去掉 zone id
            "2001:0db8:85a3:0000:0000:8a2e:0370:7334",
        ],
    )
    def test_valid(self, value):
        assert_valid(ipv6(value))

    @pytest.mark.parametrize(
        "value",
        [
            "",
            "abc.0.0.1",
            "2001::db8::1",       # 双 ::
            "12345::",            # 段越界
            "gggg::1",            # 非十六进制
            "2001:db8::1/129",    # 前缀越界
        ],
    )
    def test_invalid(self, value):
        assert_invalid(ipv6(value))

    def test_strict_requires_cidr(self):
        assert_invalid(ipv6("::1", strict=True))
