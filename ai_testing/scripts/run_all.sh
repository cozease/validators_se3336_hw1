#!/usr/bin/env bash
# AI 驱动自动化测试工作流一键执行脚本
# 依赖: bash >= 4, python3 (3.9+)
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

echo "[1/5] 准备虚拟环境..."
if [[ ! -d .venv ]]; then
  python3 -m venv .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate

echo "[2/5] 安装依赖..."
python -m pip install --upgrade pip >/dev/null
pip install --quiet pytest pytest-cov pytest-html "eth-hash[pycryptodome]"
pip install --quiet -e .

echo "[3/5] 运行既有测试套件（基线）..."
pytest tests -q --no-header | tail -5

echo "[4/5] 运行 AI 生成测试套件..."
pytest ai_testing/generated_tests -q --no-header | tail -5

echo "[5/5] 全量测试 + 覆盖率 + HTML 报告..."
pytest tests ai_testing/generated_tests \
  --cov=src/validators \
  --cov-report=term \
  --cov-report=html:ai_testing/reports/coverage_html \
  --html=ai_testing/reports/pytest_report.html \
  --self-contained-html \
  -q --no-header | tail -8

echo ""
echo "报告已输出到:"
echo "  - ai_testing/reports/pytest_report.html      (pytest HTML 报告)"
echo "  - ai_testing/reports/coverage_html/index.html (覆盖率 HTML 报告)"
