"""AI 生成测试套件的 pytest 共享配置。

由 Cursor (Composer Agent) 依据《需求说明文档》和源码签名自动生成。
作用：
- 将 src 目录加入 sys.path，保证 `import validators` 可用。
- 供测试用例集中导入断言辅助。
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def assert_valid(result):
    """断言验证结果为 True（validators 成功返回 True）。"""
    assert result is True, f"期望 True, 实际为 {result!r}"


def assert_invalid(result):
    """断言验证结果为 ValidationError（校验失败）。

    validators 在失败时返回 ValidationError 实例，其 __bool__ 为 False。
    """
    assert result is not True, f"期望失败, 实际为 True"
    assert bool(result) is False, f"期望 bool(result)==False, 实际 True"
