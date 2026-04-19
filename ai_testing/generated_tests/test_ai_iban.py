"""AI 生成：IBAN 国际银行账号验证器测试（mod-97 校验）。"""

from __future__ import annotations

import pytest

from validators import iban
from conftest import assert_invalid, assert_valid


class TestIBAN:
    @pytest.mark.parametrize(
        "value",
        [
            "DE29100500001061045672",
            "GB82WEST12345698765432",
            "FR1420041010050500013M02606",
            "NL91ABNA0417164300",
        ],
    )
    def test_valid(self, value):
        assert_valid(iban(value))

    @pytest.mark.parametrize(
        "value",
        [
            "",
            "123456",
            "DE00100500001061045672",  # 校验位错误
            "XX29100500001061045672",  # 校验位错误
            "DE291005",                # 过短
            "DE29-1005-0000-1061-0456-72",  # 含连字符
        ],
    )
    def test_invalid(self, value):
        assert_invalid(iban(value))
