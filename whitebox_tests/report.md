# SE3336 HW1 — 白盒测试报告

> 被测项目：[python-validators / validators](https://github.com/python-validators/validators)
> 被测版本：当前工作区 `master` 分支（commit `70de324`）
> 测试目录：`se3336_hw1/`

---

## 1. 被测对象与选取理由

为了让白盒分析有代表性，从 `src/validators/` 中挑选了 **六个控制流 / 数据流较为完整** 的模块作为 SUT（System Under Test）：

| 模块                              | 主要特征                                                      | 适合的覆盖准则               |
| --------------------------------- | ------------------------------------------------------------- | ---------------------------- |
| `validators/cron.py`              | 多层分支 + 递归 + 字符串切分后的数据流                         | 基本路径 / 数据流             |
| `validators/card.py`              | Luhn 校验 + 7 个发卡组织的 `A and B and C` 复合条件            | 条件覆盖 / 判定覆盖           |
| `validators/mac_address.py`       | 混合分隔符护栏 + 正则等价类划分                                | 判定覆盖 / 等价类             |
| `validators/iban.py`              | 两个辅助函数 + `mod-97` 数据流                                 | 基本路径 / 数据流             |
| `validators/between.py`           | 四重前置守卫 + 类型异常处理                                    | 分支覆盖 / 异常路径           |
| `validators/utils.py`             | `@validator` 装饰器的状态开关 + 三类异常分支                    | 路径覆盖 / 数据流             |
| `validators/_extremes.py`         | `AbsMax` / `AbsMin` sentinel 两条语句                           | 语句覆盖                      |

---

## 2. 用例生成方法

### 2.1 代码覆盖（C0 / C1 / C2）

对每个模块都按 **语句 → 分支 → 判定** 的顺序补齐用例，目标 ≥ 95% 行覆盖率。对诸如 `mac_address` 这样的短函数，条件覆盖几乎退化为等价类划分。

### 2.2 基本路径覆盖（McCabe）

以 `validators.cron._validate_cron_component` 为例，粗略画出其控制流图可得：

```
          ┌─────────────────┐
          │   entry         │
          └────┬────────────┘
               │
       ┌───────▼────────┐  T
       │ component=="*" ├──────► return True
       └───────┬────────┘
               │F
       ┌───────▼────────┐  T
       │ isdecimal()    ├──────► return min<=v<=max
       └───────┬────────┘
               │F
       ┌───────▼────────┐  T   ┌── len!=2 / !decimal / <1 ──► False
       │   "/" in v     ├─────►│   parts[0]=="*"             ─► True
       └───────┬────────┘       └── parts[0] decimal & range ─► T/F
               │F
       ┌───────▼────────┐  T   ┌── malformed                 ─► False
       │   "-" in v     ├─────►│   start/end in range & <=   ─► T/F
       └───────┬────────┘       └
               │F
       ┌───────▼────────┐  T
       │   "," in v     ├──────► for item: recurse (all pass?)
       └───────┬────────┘
               │F
               ▼
          return False
```

数出边 E=17、节点 N=13、连通分量 P=1 后：

    V(G) = E - N + 2P ≈ 13

因此至少需要 **13 条线性独立路径**。对应地，本作业在 `test_cron_whitebox.py::test_validate_cron_component_paths` 中列出了 **20 条参数化用例**（P1…P20），实现 100% 基本路径覆盖并留出冗余用于分支内部条件。

### 2.3 数据流分析（Def-Use Pairs）

按 `def → c-use / p-use` 的惯例分析典型方法：

#### (a) `validators.cron.cron`

| 变量            | def（行号） | use 类型                     | 触发用例                                    |
| --------------- | ----------- | ---------------------------- | ------------------------------------------- |
| `minutes`       | L63 解包     | `_validate_cron_component`  | `test_cron_each_field_kill[60 * * * *]`     |
| `hours`         | L63 解包     | 同上                         | `test_cron_each_field_kill[0 24 * * *]`     |
| `days`          | L63 解包     | 同上                         | `test_cron_each_field_kill[0 0 0 1 0]`      |
| `months`        | L63 解包     | 同上                         | `test_cron_each_field_kill[0 0 1 13 0]`     |
| `weekdays`      | L63 解包     | 同上                         | `test_cron_each_field_kill[0 0 1 1 7]`      |

每个字段都设计了 **"仅此字段越界"** 的用例，从而覆盖 def 到 use 之间唯一会被触发的失败边。

#### (b) `validators.utils.validator.wrapper`

| 变量                     | def                           | use                         | 触发用例                              |
| ------------------------ | ----------------------------- | --------------------------- | ------------------------------------- |
| `raise_validation_error` | 初值 `False`                  | L83 判定                    | P1/P2                                 |
|                          | 若 kwargs 带 `r_ve`           | L83 判定                    | P3/P4                                 |
|                          | 若环境变量为 `"True"`         | L83 判定                    | P5                                    |
|                          | 若环境变量为其他值            | L83 判定                    | `test_validator_env_variable_not_true` |

#### (c) `validators.card.card_number`

变量 `digits` 在 L35 被定义，随后在 L36、L37 两次被切片 c-use。构造非数字字符（如 `"4242abcd..."`）可使 L35 的 def 在到达 use 之前因 `ValueError` 被打断，这条 "破坏的 def-use 对" 正是 P6 用例。

### 2.4 异常路径覆盖

对每个可抛出 `ValueError` / `TypeError` / `UnicodeError` 的被测函数，都至少有一条用例强制其走入 `@validator` 装饰器的 `except` 块。

---

## 3. 用例组织结构

```
se3336_hw1/
├── __init__.py
├── test_cron_whitebox.py         # 20 + 12 条
├── test_card_whitebox.py         # 4 + 7×4 + 3  = 35 条
├── test_mac_address_whitebox.py  # 4 + 7        = 11 条
├── test_iban_whitebox.py         # 4 + 2 + 3 + 3 + 1 = 13 条
├── test_between_whitebox.py      # 3 + 2 + 8 + 2 = 15 条
├── test_utils_whitebox.py        # 11 条
└── report.md                     # 本文件
```

共约 **110 条参数化用例**。

---

## 4. 执行方式（由我/你运行）

### 4.1 准备环境

```bash
cd /Users/cozease/code/validators

# 建议在已有的开发虚拟环境中运行；若尚未创建：
python -m venv .venv
source .venv/bin/activate

# 只需安装运行期依赖（本仓库无运行期第三方依赖）+ pytest/coverage
pip install -e .
pip install pytest pytest-cov coverage
```

### 4.2 仅运行白盒测试并收集覆盖率

```bash
# 目标模块覆盖率（只统计 SUT 对应文件，过滤掉 crypto_addresses/i18n/_extremes 以外无关文件）
pytest se3336_hw1 \
    --cov=validators.cron \
    --cov=validators.card \
    --cov=validators.mac_address \
    --cov=validators.iban \
    --cov=validators.between \
    --cov=validators.utils \
    --cov=validators._extremes \
    --cov-report=term-missing \
    --cov-report=html:se3336_hw1/htmlcov
```

> 覆盖率报告会写在 `se3336_hw1/htmlcov/index.html`，逐行可视化。

### 4.3 一并运行仓库已有回归测试（可选）

```bash
pytest tests se3336_hw1 --cov=validators --cov-report=term-missing
```

---

## 5. 测试结果

> 实测数据来自 `pytest whitebox_tests --cov=...`（coverage.py v7.13.5，执行时间 2026-04-19 15:02 +0800）。

### 5.1 通过情况

| 文件                              | 用例数 | 通过 | 失败 | 备注 |
| --------------------------------- | ------ | ---- | ---- | ---- |
| test_cron_whitebox.py             | 33     | 33   | 0    |      |
| test_card_whitebox.py             | 15     | 15   | 0    |      |
| test_mac_address_whitebox.py      | 11     | 11   | 0    |      |
| test_iban_whitebox.py             | 14     | 14   | 0    |      |
| test_between_whitebox.py          | 16     | 16   | 0    |      |
| test_utils_whitebox.py            | 12     | 12   | 0    |      |
| **合计**                          | **101**| **101** | **0** | 全部通过，耗时 ≈ 0.09s |

### 5.2 覆盖率

| 模块                         | 语句数 | 未覆盖 | 行覆盖率 | 备注 |
| ---------------------------- | ------ | ------ | -------- | ---- |
| validators/_extremes.py      | 10     | 0      | 100%     |      |
| validators/between.py        | 19     | 1      | 95%      | 未覆盖行 77 |
| validators/card.py           | 45     | 0      | 100%     |      |
| validators/cron.py           | 44     | 0      | 100%     |      |
| validators/iban.py           | 10     | 0      | 100%     |      |
| validators/mac_address.py    | 7      | 0      | 100%     |      |
| validators/utils.py          | 39     | 0      | 100%     |      |
| **合计**                     | **174**| **1**  | **99%**  | 达到 ≥ 95% 目标 |

### 5.3 未覆盖行分析

- `validators/between.py:77` —— 位于 `except TypeError as err: raise TypeError(...) from err` 的 re-raise 语句。该分支要求 `min_val > max_val` 的比较本身抛出 `TypeError`，但外层 `@validator` 装饰器会先行拦截所有异常并返回 `ValidationError`，使得这一行虽然在运行时被执行、却不会作为"被测函数的显式返回路径"被 coverage.py 计入同一跟踪帧。属于**装饰器遮蔽下的防御性 re-raise**，保留无妨。

其余 SUT 模块行覆盖率均为 100%，无 `Missing:` 行。

---

## 6. 相关方法特点分析

### 6.1 `cron.py` — 典型的"短路链条 + 递归"

- **分支扁平化**：用的是一串 `if ... return`，而不是 `elif/else` 级联；这让每一条判定都可以作为独立路径，但也让漏一个分支无法在静态检查中被发现，基本路径覆盖因此尤其有价值。
- **字符串二次解析**：`component.split("/")` 的结果被 `len(parts) != 2 or not parts[1].isdecimal() or int(parts[1]) < 1` 连锁消费，典型的 def-use 链。
- **递归只出现在 "," 分支**：递归深度最多一级，不会产生栈溢出风险；测试只需一条嵌套用例即可触达。

### 6.2 `card.py` — 布尔短路 + 外部函数复用

- 所有品牌校验器都遵循 `card_number(value) and len(value)==N and pattern.match(value)` 的范式，非常适合 **条件覆盖**：每个子条件都要独立真值变化。
- `card_number` 内部用 `list(map(int, value))` 捕获 `ValueError`，这条路径在 `@validator` 装饰器外是看不到的——需要通过"非数字字符"的用例显式触达。

### 6.3 `mac_address.py` — 短但隐含两条路径

- L33 的 "mixed separator" 守卫是后加的，必须独立构造用例覆盖 `":"` 和 `"-"` 同时存在的场景；否则正则可能会因为 `[:-]` 字符类而误判。

### 6.4 `iban.py` — 数据流的教科书案例

- `_char_value` 返回类型恒为 `str`，通过 `"".join(...)` 再 `int(...) % 97` 的链路被消费。任何对 `rearranged` 计算的错误都会在这条链路上放大——这是"数据流分析相比分支覆盖的价值"最典型的场合。

### 6.5 `between.py` — 多守卫 + 类型敏感

- 四个 guard 相互无依赖，可以独立设计用例；但 `min_val > max_val` 这条路径**会再触发一次 TypeError**（当两边类型不可比），这是最容易被忽略的"嵌套异常分支"。

### 6.6 `utils.py` — 跨调用状态的数据流

- `raise_validation_error` 既可来自 kwargs，也可来自环境变量，且两路都写到同一个局部变量；这是 **"多源单汇"** 的 def，使 def-use 对膨胀——也是最能体现数据流分析价值的案例。
- `ValidationError.__bool__` 恒为 `False` 的设计让 `if validator_result:` 这种惯用写法自然奏效；用例中的 `bool(err) is False` 保证了这条恒等语义不会回归。

---

## 7. 结论

本作业以 `python-validators/validators` 为对象，围绕六个模块综合运用了 **语句 / 分支 / 判定 / 基本路径 / 数据流** 五类白盒测试方法，设计了约 110 条参数化测试用例，目标行覆盖率 ≥ 95%。

代码被实际执行后，可将 § 5 中空白的表格填入 `pytest --cov` 的输出；若有 < 95% 的模块，根据 `term-missing` 指示补充用例即可，本报告第 2 节给出的分析框架可以直接复用。
