"""AI 生成：URL 验证器功能测试（scheme / netloc / path / query / fragment）。"""

from __future__ import annotations

import pytest

from validators import url
from conftest import assert_invalid, assert_valid


class TestUrlPositive:
    @pytest.mark.parametrize(
        "value",
        [
            "http://duck.com",
            "https://example.com",
            "ftp://foobar.dk",
            "ssh://user@host.com:22",
            "http://10.0.0.1",
            "https://sub.domain.example.org/path/to?x=1&y=2#section",
            "http://例子.测试",
            "https://user:pass@example.com/",
            "git://github.com/user/repo.git",
            "https://example.com:8443/api?q=1",
        ],
    )
    def test_valid_urls(self, value):
        assert_valid(url(value))

    def test_rfc1034_trailing_dot(self):
        assert_valid(url("http://example.com./path", rfc_1034=True))

    def test_simple_host(self):
        assert_valid(url("http://localhost", simple_host=True))


class TestUrlNegative:
    @pytest.mark.parametrize(
        "value",
        [
            "",
            "not-a-url",
            "http://",
            "://no-scheme.com",
            "http://ex ample.com",  # 含空格
            "http:\\bad.com",
            'http://example.com/">user@example.com',
            "http://-leading-dash.com",
        ],
    )
    def test_invalid_urls(self, value):
        assert_invalid(url(value))

    def test_unknown_scheme(self):
        assert_invalid(url("javascript:alert(1)"))

    def test_simple_host_requires_flag(self):
        assert_invalid(url("http://localhost"))

    def test_ip_private_option(self):
        """显式声明 private=False 时，私网 IP 应被拒绝。"""
        assert_invalid(url("http://192.168.1.1", private=False))
