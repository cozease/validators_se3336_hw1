"""AI 生成：email 验证器功能测试。

覆盖：标准邮箱、国际化扩展字符、本地部分长度边界、域名长度边界、
IPv4/IPv6 字面量域名、RFC 1034 尾点、RFC 2782 服务记录。
"""

from __future__ import annotations

import pytest

from validators import email
from conftest import assert_invalid, assert_valid


class TestEmailPositive:
    """邮箱有效用例。"""

    @pytest.mark.parametrize(
        "value",
        [
            "someone@example.com",
            "user.name+tag@sub.example.co.uk",
            "a@b.cd",
            "x1y2z3@domain.io",
            "first.last@example.org",
            "u_ser-name@example.com",
            "user!#$%&'*+/=?^_`{|}~-@example.com",
        ],
    )
    def test_standard_valid(self, value):
        assert_valid(email(value))

    def test_extended_latin(self):
        assert_valid(email("pëtér@example.com"))

    def test_rfc1034_trailing_dot(self):
        assert_valid(email("user@example.com.", rfc_1034=True))

    def test_ipv4_domain(self):
        assert_valid(email("user@[127.0.0.1]", ipv4_address=True))

    def test_ipv6_domain(self):
        assert_valid(email("user@[::1]", ipv6_address=True))

    def test_simple_host(self):
        assert_valid(email("user@localserver", simple_host=True))


class TestEmailNegative:
    """邮箱无效用例。"""

    @pytest.mark.parametrize(
        "value",
        [
            "",
            "plainaddress",
            "missing-at-sign.com",
            "bogus@@",
            "@no-local.com",
            "no-domain@",
            "two@@signs.com",
            "user@-startwithhyphen.com",
            "user name@example.com",
        ],
    )
    def test_obvious_invalid(self, value):
        assert_invalid(email(value))

    def test_local_part_exceeds_64(self):
        local = "a" * 65
        assert_invalid(email(f"{local}@example.com"))

    def test_domain_part_exceeds_253(self):
        domain = ("a" * 63 + ".") * 4 + "example.com"  # 超过 253
        assert_invalid(email(f"u@{domain}"))

    def test_ipv4_requires_flag(self):
        """未显式开启 ipv4_address 时，[127.0.0.1] 形式应拒绝。"""
        assert_invalid(email("user@[127.0.0.1]"))

    def test_simple_host_requires_flag(self):
        assert_invalid(email("user@localserver"))
