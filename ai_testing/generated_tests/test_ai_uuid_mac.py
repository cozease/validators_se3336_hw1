"""AI 生成：UUID 与 MAC 地址验证器功能测试。"""

from __future__ import annotations

from uuid import UUID, uuid4

import pytest

from validators import mac_address, uuid
from conftest import assert_invalid, assert_valid


class TestUUID:
    @pytest.mark.parametrize(
        "value",
        [
            "2bc1c94f-0deb-43e9-92a1-4775189ec9f8",
            "00000000-0000-0000-0000-000000000000",
            "ffffffff-ffff-ffff-ffff-ffffffffffff",
            "2BC1C94F-0DEB-43E9-92A1-4775189EC9F8",
        ],
    )
    def test_valid_str(self, value):
        assert_valid(uuid(value))

    def test_accepts_uuid_object(self):
        assert_valid(uuid(uuid4()))

    def test_accepts_uuid_v1(self):
        assert_valid(uuid(UUID("c232ab00-9414-11ec-b3c8-9e6bdeced846")))

    @pytest.mark.parametrize(
        "value",
        [
            "",
            "2bc1c94f 0deb-43e9-92a1-4775189ec9f8",  # 含空格
            "not-a-uuid",
            "2bc1c94f-0deb-43e9-92a1",  # 长度不足
        ],
    )
    def test_invalid(self, value):
        assert_invalid(uuid(value))


class TestMAC:
    @pytest.mark.parametrize(
        "value",
        [
            "01:23:45:67:ab:CD",
            "01-23-45-67-ab-CD",
            "aa:bb:cc:dd:ee:ff",
            "AA-BB-CC-DD-EE-FF",
        ],
    )
    def test_valid(self, value):
        assert_valid(mac_address(value))

    @pytest.mark.parametrize(
        "value",
        [
            "",
            "00:00:00:00:00",               # 段不足
            "00:00:00:00:00:00:00",         # 段过多
            "ZZ:ZZ:ZZ:ZZ:ZZ:ZZ",           # 非十六进制
            "00:00:00:00:0000",             # 分隔错误
            "00 00 00 00 00 00",
        ],
    )
    def test_invalid(self, value):
        assert_invalid(mac_address(value))
