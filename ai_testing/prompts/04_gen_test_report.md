# Prompt — 生成《测试报告》

**Role**：QA Lead。

**Input**：pytest 控制台输出、`coverage_html/index.html`、`pytest_report.html`。

**Task**：
1. 综述：总用例数、通过 / 失败 / xfail、执行时长、覆盖率
2. 按模块分解覆盖率与用例数
3. 缺陷清单：对每个 xfail 给出
   - 缺陷编号、严重级别、重现步骤、根因分析、建议修复
4. 风险与后续工作（未覆盖分支、性能、安全）
5. 结论（是否达到退出准则）

**Constraints**：
- 所有数字必须来自执行日志，不得臆造
- 输出为 Markdown，便于提交
