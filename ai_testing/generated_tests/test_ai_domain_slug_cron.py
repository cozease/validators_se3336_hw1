"""AI 生成：domain / slug / cron 验证器功能测试。"""

from __future__ import annotations

import pytest

from validators import cron, domain, slug
from conftest import assert_invalid, assert_valid


class TestDomain:
    @pytest.mark.parametrize(
        "value",
        [
            "example.com",
            "sub.example.org",
            "xn----gtbspbbmkef.xn--p1ai",  # IDN punycode
            "例子.测试",
            "a.co",
        ],
    )
    def test_valid(self, value):
        assert_valid(domain(value))

    @pytest.mark.parametrize(
        "value",
        [
            "",
            "example.com/",
            "example .com",
            "-leading-hyphen.com",
            "no_tld",
            "trailing.hyphen-.com",
        ],
    )
    def test_invalid(self, value):
        assert_invalid(domain(value))

    def test_rfc1034(self):
        assert_valid(domain("example.com.", rfc_1034=True))

    def test_consider_tld_rejects_bogus(self):
        assert_invalid(domain("example.xyzzz", consider_tld=True))


class TestSlug:
    @pytest.mark.parametrize(
        "value",
        ["my-slug-123", "abc", "abc-def-ghi", "0-1-2"],
    )
    def test_valid(self, value):
        assert_valid(slug(value))

    @pytest.mark.parametrize(
        "value",
        ["", "has space", "UPPER", "has_under", "--dash--", "emoji-😀"],
    )
    def test_invalid(self, value):
        assert_invalid(slug(value))


class TestCron:
    @pytest.mark.parametrize(
        "value",
        [
            "* * * * *",
            "0 0 * * *",
            "*/5 * * * *",
            "0,30 0-12 1-15 * 1-5",
            "15 3 * * 1,3,5",
        ],
    )
    def test_valid(self, value):
        assert_valid(cron(value))

    @pytest.mark.parametrize(
        "value",
        [
            "",
            "* * * *",          # 字段不足
            "* * * * * *",      # 字段过多
            "60 * * * *",       # 分钟越界
            "* 25 * * *",       # 小时越界
            "hello",
        ],
    )
    def test_invalid(self, value):
        assert_invalid(cron(value))
