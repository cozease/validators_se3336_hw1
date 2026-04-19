# Prompt — 生成测试用例（文档 + pytest 代码）

**Role**：自动化测试开发。

**Input**：需求文档 + 源码。

**Task**：
1. 针对每个 FR-xx 设计 ≥ 4 个用例（正/反/边界/参数组合），并按以下字段生成 Markdown 表：
   - 用例 ID (TC-xxx)、关联 FR、优先级、输入、预期输出、类型（正/反/边界）
2. 同时产出可执行 pytest 代码（`ai_testing/generated_tests/test_ai_*.py`）：
   - 使用 `pytest.mark.parametrize` 压缩冗余
   - 使用共享 `conftest.assert_valid/assert_invalid`
3. 若源码存在可疑缺陷，用 `@pytest.mark.xfail(strict=True, reason="...")` 标注，保留断言真值。

**Constraints**：
- 不允许用例之间互相依赖
- 每个测试函数只聚焦一个行为
