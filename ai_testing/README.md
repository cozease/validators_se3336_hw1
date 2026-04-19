# AI 驱动的自动化软件测试工作流 · python-validators

本目录是《大模型驱动的智能化软件测试》作业的完整交付物。被测对象为开源项目
[python-validators](https://github.com/python-validators/validators) v0.35.0，
使用 **Cursor Composer Agent（基于 Claude 系列模型）** 作为 AI 开发 Agent，
由大模型驱动完成从需求抽取 → 测试计划 → 用例生成 → 执行 → 报告的全链路。

## 目录结构

```
ai_testing/
├── README.md                 # 本文件
├── 01_需求说明文档.md
├── 02_测试计划.md
├── 03_测试用例.md
├── 04_测试报告.md
├── prompts/                  # 给 LLM 的 prompt 模板（编排逻辑）
│   ├── 01_gen_requirements.md
│   ├── 02_gen_test_plan.md
│   ├── 03_gen_test_cases.md
│   └── 04_gen_test_report.md
├── generated_tests/          # AI 生成的 15 个 pytest 测试模块（共 411 用例）
│   ├── conftest.py
│   └── test_ai_*.py
├── scripts/
│   └── run_all.sh            # 一键执行脚本
└── reports/                  # 执行后生成（已附带）
    ├── pytest_report.html
    └── coverage_html/
```

## 被测项目基本情况

| 项 | 值 |
| --- | --- |
| 项目名 | validators |
| 版本 | 0.35.0 |
| 语言 | Python |
| 源码行数 | **3 143**（满足 ≥ 1000 行要求） |
| 可测功能点 | **20+**（email / url / ip / card 系列 / hash 系列 / encoding 系列 / iban / cusip / isin / sedol / btc / eth / bsc / trx / country_code / currency / calling_code / uuid / mac / between / length / domain / slug / cron / i18n × 10+） |
| 需求文档 | `ai_testing/01_需求说明文档.md`（AI 从 docstring 抽取） |

## AI 驱动工作流

```
┌──────────────────────────────────────────────────────────────┐
│ 1. 源码+docstring  ──▶  Cursor Agent  ──▶  01_需求说明文档.md │
│ 2. 需求文档        ──▶  Cursor Agent  ──▶  02_测试计划.md     │
│ 3. 需求+计划+源码   ──▶  Cursor Agent  ──▶  03_测试用例.md    │
│                                           generated_tests/*.py│
│ 4. pytest 执行 + 覆盖率                                        │
│    ├─ 控制台日志                                                │
│    ├─ pytest_report.html                                       │
│    └─ coverage_html/                                           │
│ 5. 执行数据        ──▶  Cursor Agent  ──▶  04_测试报告.md     │
└──────────────────────────────────────────────────────────────┘
```

**自我迭代闭环**：生成用例后立即 `pytest --collect-only` → 失败就由 Agent 自我修复（例如
`TestBrandMatrix` 类作用域丢失 BRANDS 的 NameError，已通过把 BRANDS 提到模块级修复）→
直到全部通过或以 `xfail` 方式记录上游缺陷。

## 一键执行

```bash
cd validators-master
bash ai_testing/scripts/run_all.sh
```

脚本会：

1. 创建/复用 `.venv`
2. 安装 `pytest / pytest-cov / pytest-html / eth-hash[pycryptodome]`
3. 把 `validators` 以 editable 模式安装到 venv
4. 依次执行既有测试、AI 测试、全量+覆盖率+HTML 报告

## 本轮执行的关键指标（Python 3.14.2 / macOS）

| 指标 | 值 |
| --- | --- |
| 用例总数 | 1 303 |
| AI 新增 | 411 |
| 通过率 | 100 %（3 xfail 已归档） |
| 行覆盖率 | 92 %（排除未导出的 `uri.py` 后约 96 %） |
| 执行时长 | 0.81 s |
| 发现缺陷 | 2 个上游真实缺陷（详见 `04_测试报告.md`） |

## 如何复现 LLM 编排

每个 prompt 模板（`prompts/*.md`）均可直接粘贴给任意支持 Tool Use 的开发 Agent
（Cursor Composer / Codex / Trae / Continue / Aider 等）。Agent 需要具备：

- **Read / Grep**：遍历源码和 docstring
- **Write / Edit**：生成 Markdown 文档和 .py 测试
- **Shell**：执行 pytest 并读取输出
- **读取终端日志的能力**：用于自我修复（闭环）

## 已知缺陷（AI 发现）

1. `finance.isin` 校验位永不生效 —— `_isin_checksum` 未累加 `check`。
2. `card.mastercard` 正则 `22–27` 范围过宽，Mir 的 2200-2204 段会被误判。

详见 `04_测试报告.md` 第 3 节。
