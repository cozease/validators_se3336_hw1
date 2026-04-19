# Prompt — 生成《需求说明文档》

**Role**：你是一名资深软件测试工程师。

**Context**：
- 项目：`python-validators`（Python 数据校验库）
- 源码位置：`src/validators/`
- 请遍历 `src/validators/` 下的全部 `.py` 文件，针对每个被 `@validator` 装饰的公开函数，抽取：
  1. 函数签名、默认参数
  2. docstring 中列出的业务规则、RFC / 标准参考
  3. docstring 中给出的正/反示例

**Task**：按以下结构输出 Markdown：
1. 项目概述（一段话）
2. 功能清单（每一个 validator 为一个小节）
   - 功能 ID（FR-xx）
   - 接口签名
   - 业务规则（子弹头列表）
   - 典型合法输入 / 非法输入示例
3. 非功能需求（性能、稳定性、兼容性）

**Constraints**：
- 不要编造未在源码或 docstring 出现的规则
- 每个功能至少列 3 条业务规则
- 输出语言：中文
