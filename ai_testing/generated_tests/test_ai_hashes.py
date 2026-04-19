"""AI 生成：哈希值（md5 / sha1 / sha224 / sha256 / sha384 / sha512）功能测试。"""

from __future__ import annotations

import pytest

from validators import md5, sha1, sha224, sha256, sha384, sha512
from conftest import assert_invalid, assert_valid


VALID_HASHES = {
    md5: ("0" * 32, "d41d8cd98f00b204e9800998ecf8427e", "D41D8CD98F00B204E9800998ECF8427E"),
    sha1: ("a" * 40, "da39a3ee5e6b4b0d3255bfef95601890afd80709"),
    sha224: ("b" * 56, "d14a028c2a3a2bc9476102bb288234c415a2b01f828ea62ac5b3e42f"),
    sha256: ("c" * 64,),
    sha384: ("d" * 96,),
    sha512: ("e" * 128,),
}


@pytest.mark.parametrize("func,sample", [(f, s) for f, samples in VALID_HASHES.items() for s in samples])
def test_valid_hashes(func, sample):
    assert_valid(func(sample))


@pytest.mark.parametrize(
    "func",
    [md5, sha1, sha224, sha256, sha384, sha512],
)
class TestInvalidHashes:
    def test_empty(self, func):
        assert_invalid(func(""))

    def test_has_non_hex(self, func):
        # 构造正确长度但包含非 hex 字符
        expected_len = {md5: 32, sha1: 40, sha224: 56, sha256: 64, sha384: 96, sha512: 128}[func]
        assert_invalid(func("z" * expected_len))

    def test_wrong_length(self, func):
        assert_invalid(func("a" * 5))

    def test_too_long(self, func):
        expected_len = {md5: 32, sha1: 40, sha224: 56, sha256: 64, sha384: 96, sha512: 128}[func]
        assert_invalid(func("a" * (expected_len + 1)))
