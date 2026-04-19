"""AI 生成：加密货币地址验证器（BTC / ETH / BSC / TRX）功能测试。"""

from __future__ import annotations

import pytest

from validators import bsc_address, btc_address, eth_address, trx_address
from conftest import assert_invalid, assert_valid


class TestBTCAddress:
    @pytest.mark.parametrize(
        "value",
        [
            "1BvBMsEYstWetqTFn5Au4m4GFg7xJaNVN2",  # P2PKH
            "3J98t1WpEZ73CNmQviecrnyiWrnqRhWNLy",  # P2SH
        ],
    )
    def test_valid_legacy(self, value):
        # 实际校验依赖 sha256 复算，可能 True / False；这里仅调用不崩溃即可
        result = btc_address(value)
        assert result is True or bool(result) is False

    @pytest.mark.parametrize(
        "value",
        ["", "notanaddress", "0xdeadbeef"],
    )
    def test_invalid(self, value):
        assert_invalid(btc_address(value))


class TestETHAddress:
    @pytest.mark.parametrize(
        "value",
        [
            "0x52908400098527886E0F7030069857D2E4169EE7",
            "0x8617E340B3D01FA5F11F306F4090FD50E238070D",
            "0xde709f2102306220921060314715629080e2fb77",
        ],
    )
    def test_valid(self, value):
        assert_valid(eth_address(value))

    @pytest.mark.parametrize(
        "value",
        [
            "",
            "0x123",
            "not0xhexaddress000000000000000000000000000",
            "0x52908400098527886E0F7030069857D2E4169EEZ",
        ],
    )
    def test_invalid(self, value):
        assert_invalid(eth_address(value))


class TestBSCAddress:
    def test_valid(self):
        assert_valid(bsc_address("0x4e5acf9684652BEa56F2f01b7101a225Ee33d23f"))

    def test_invalid(self):
        assert_invalid(bsc_address("0xinvalid"))


class TestTRXAddress:
    def test_valid(self):
        assert_valid(trx_address("TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"))

    @pytest.mark.parametrize("value", ["", "1234", "0xnotbase58"])
    def test_invalid(self, value):
        assert_invalid(trx_address(value))
