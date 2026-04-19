# Validators 项目未来功能变更测试调整方案

> 文档生成日期：2026-04-19  
> 基于代码库版本：0.35.0

---

## 1. 代码库结构分析

### 1.1 核心架构

```
src/validators/
├── utils.py              # 核心基础设施
│   ├── @validator 装饰器  # 包装验证函数，统一返回 True 或 ValidationError
│   └── ValidationError 类  # 兼具异常和假值特性的错误对象
├── [验证器模块].py        # 40+ 独立验证函数
├── crypto_addresses/     # 加密货币地址验证子包
└── i18n/                # 国际化验证子包（西班牙、芬兰、法国、印度、俄罗斯）
```

### 1.2 关键设计模式

| 特性 | 实现方式 |
|------|----------|
| 统一返回格式 | `@validator` 装饰器确保返回 `True` 或 `ValidationError` |
| 异常/返回值双模式 | `r_ve` 参数或 `RAISE_VALIDATION_ERROR` 环境变量控制 |
| 参数化测试 | `pytest.mark.parametrize` 批量测试有效/无效输入 |
| 白盒测试 | 验证内部算法路径（如 Luhn 算法各分支）|
| 黑盒测试 | 验证输入输出行为，不关心内部实现 |

---

## 2. 推测的未来功能变更

基于当前代码趋势（CHANGES.md 分析）和验证库通用演进路径，推测以下 3 个可能的功能变更：

---

## 变更一：批量验证/Schema 验证功能

### 2.1.1 变更背景与动机

当前库定位为 "Schema-free"，但用户实际使用中经常需要同时验证多个字段（如用户注册时的 email + password + phone）。GitHub Issues 中多次出现关于 "如何验证对象/字典" 的询问。

**预计新增功能**：
- `validate_batch()` - 批量验证多个字段
- `Schema` 类 - 声明式验证规则组合

```python
# 预计新增API示例
from validators import Schema, email, length

schema = Schema({
    'email': email,
    'password': lambda v: length(v, min=8),
    'age': lambda v: between(v, min=18, max=120)
})

result = schema.validate({
    'email': 'user@example.com',
    'password': 'secure123',
    'age': 25
})
```

### 2.1.2 黑盒测试调整方案

| 测试类别 | 测试场景 | 预期输入 | 预期输出 |
|----------|----------|----------|----------|
| 功能测试 | 全部字段有效 | `{'email': 'a@b.com', 'password': '12345678'}` | `True` 或成功对象 |
| 功能测试 | 部分字段无效 | `{'email': 'invalid', 'password': '12345678'}` | 包含 email 错误的 ValidationError |
| 功能测试 | 全部字段无效 | `{'email': 'invalid', 'password': '12'}` | 包含所有错误的 ValidationError |
| 功能测试 | 缺少必填字段 | `{'email': 'a@b.com'}` | 缺少 password 的错误 |
| 功能测试 | 额外字段处理 | 输入含未定义字段 | 根据配置忽略/报错 |
| 边界测试 | 空字典验证 | `{}` | 根据配置返回错误或 True |
| 边界测试 | 空 Schema | `Schema({})` | 空验证通过 |
| 兼容性测试 | 与现有验证器集成 | 使用所有现有验证器作为规则 | 正常工作 |

**新增测试文件结构**：

```python
# tests/test_schema.py
"""Test Schema validation."""

import pytest
from validators import Schema, ValidationError, email, length, between

class TestSchemaBlackBox:
    """黑盒测试：不关心内部实现，只验证输入输出行为"""

    @pytest.mark.parametrize("data", [
        {'email': 'user@example.com', 'password': 'secure123'},
        {'email': 'test@test.org', 'password': 'verysecurepassword'},
    ])
    def test_valid_data_returns_true(self, data):
        """有效数据应返回 True"""
        schema = Schema({
            'email': email,
            'password': lambda v: length(v, min=8)
        })
        assert schema.validate(data) is True

    @pytest.mark.parametrize("data,missing_field", [
        ({'email': 'user@example.com'}, 'password'),
        ({'password': 'secure123'}, 'email'),
        ({}, 'email'),
    ])
    def test_missing_required_field_returns_error(self, data, missing_field):
        """缺少必填字段应返回 ValidationError"""
        schema = Schema({
            'email': email,
            'password': lambda v: length(v, min=8)
        })
        result = schema.validate(data)
        assert isinstance(result, ValidationError)
        # 黑盒：验证错误包含缺失字段信息
        assert missing_field in str(result) or hasattr(result, missing_field)

    @pytest.mark.parametrize("data", [
        {'email': 'invalid-email', 'password': 'secure123'},
        {'email': 'user@example.com', 'password': '12'},
        {'email': 'bad', 'password': '12'},
    ])
    def test_invalid_field_returns_error(self, data):
        """字段验证失败应返回 ValidationError"""
        schema = Schema({
            'email': email,
            'password': lambda v: length(v, min=8)
        })
        result = schema.validate(data)
        assert isinstance(result, ValidationError)
```

### 2.1.3 白盒测试调整方案

| 测试目标 | 内部实现路径 | 测试方法 |
|----------|--------------|----------|
| 验证器调用顺序 | 顺序遍历 vs 并行执行 | Mock 验证器，验证调用次数和顺序 |
| 错误收集策略 | 遇到即停 vs 全部收集 | 输入多错误数据，验证返回错误数量 |
| 短路机制 | 第一个错误后是否继续 | 检查性能计数器或 side-effect |
| 嵌套 Schema 处理 | 递归验证路径 | 构造多层嵌套 Schema，验证递归深度 |
| 异常转换逻辑 | `@validator` 装饰器包装 | 验证原始异常被正确转为 ValidationError |

**白盒测试代码示例**：

```python
# tests/test_schema_whitebox.py
"""White-box tests for Schema implementation."""

from unittest.mock import Mock, call
import pytest
from validators import Schema, email

class TestSchemaWhiteBox:
    """白盒测试：验证内部实现细节"""

    def test_validators_called_in_order(self):
        """验证验证器按定义顺序调用"""
        mock_validator1 = Mock(return_value=True)
        mock_validator2 = Mock(return_value=True)

        schema = Schema({
            'field1': mock_validator1,
            'field2': mock_validator2,
        })
        schema.validate({'field1': 'a', 'field2': 'b'})

        # 白盒：验证调用顺序
        assert mock_validator1.call_count == 1
        assert mock_validator2.call_count == 1
        # 验证 field1 先于 field2 被调用
        # 需要 Schema 内部记录调用顺序

    def test_collect_all_errors_mode(self):
        """验证 '收集全部错误' 模式下的内部行为"""
        schema = Schema({
            'email': email,
            'phone': lambda x: False,  # 总是失败
        }, mode='collect_all')  # 假设有此参数

        result = schema.validate({'email': 'bad', 'phone': 'bad'})

        # 白盒：验证返回多个错误
        assert hasattr(result, 'errors')
        assert len(result.errors) == 2

    def test_fail_fast_mode(self):
        """验证 '快速失败' 模式下遇到第一个错误即停止"""
        mock_validator = Mock(return_value=False)

        schema = Schema({
            'field1': mock_validator,
            'field2': mock_validator,  # 不应被调用
        }, mode='fail_fast')

        schema.validate({'field1': 'bad', 'field2': 'bad'})

        # 白盒：field2 不应被调用
        assert mock_validator.call_count == 1
```

### 2.1.4 回归测试清单

- [ ] 现有所有验证器与 Schema 组合使用正常
- [ ] `r_ve` 参数在 Schema 中工作正常
- [ ] `RAISE_VALIDATION_ERROR` 环境变量在 Schema 中工作正常
- [ ] ValidationError 的 `func`、`args`、`reason` 属性在 Schema 中正确设置

---

## 变更二：更多国家/地区的 i18n 验证器

### 2.2.1 变更背景与动机

当前 `i18n` 子包仅支持 5 个国家（西班牙、芬兰、法国、印度、俄罗斯）。根据全球用户分布和常见需求，预计会新增：

- **美国**：`us_ssn` (社会安全号), `us_ein` (雇主识别号)
- **中国**：`cn_id` (身份证号), `cn_phone` (手机号)
- **巴西**：`br_cpf` (个人税号), `br_cnpj` (企业税号)
- **英国**：`gb_nino` (国家保险号), `gb_vat` (增值税号)
- **德国**：`de_iban`, `de_vat`

### 2.2.2 黑盒测试调整方案

| 测试类别 | 测试场景 | 测试数据策略 |
|----------|----------|--------------|
| 功能测试 | 有效号码验证 | 收集各国官方测试号码/生成有效号码 |
| 功能测试 | 无效号码验证 | 随机字符串、格式错误号码、校验位错误号码 |
| 功能测试 | 边界长度 | 最短/最长有效长度 ±1 |
| 功能测试 | 特殊字符处理 | 含空格、连字符、前缀的情况 |
| 功能测试 | 大小写敏感 | 如 VAT 号码通常不区分大小写 |

**新增测试文件结构**（以中国身份证为例）：

```python
# tests/i18n/test_cn.py
"""Test Chinese validators."""

import pytest
from validators import ValidationError
from validators.i18n import cn_id, cn_phone

class TestChinaValidatorsBlackBox:
    """中国验证器黑盒测试"""

    # ========== 身份证验证 (cn_id) ==========
    @pytest.mark.parametrize("value", [
        "110101199001011234",  # 北京，1990年生
        "310101198001011234",  # 上海，1980年生
        "440106200001011234",  # 广州，2000年生
        "11010119900101123X",  # 含 X 校验码
    ])
    def test_cn_id_valid(self, value):
        """有效身份证应返回 True"""
        assert cn_id(value)

    @pytest.mark.parametrize("value", [
        "",                      # 空字符串
        "11010119900101123",     # 17位（缺1位）
        "1101011990010112345",   # 19位（多1位）
        "110101199001011235",    # 校验位错误
        "000000000000000000",    # 全零无效
        "110101189001011234",    # 超出合理年龄范围
        "990101199001011234",    # 无效行政区划代码
        "110101199013011234",    # 无效日期（13月）
        "110101199001321234",    # 无效日期（32日）
    ])
    def test_cn_id_invalid(self, value):
        """无效身份证应返回 ValidationError"""
        assert isinstance(cn_id(value), ValidationError)

    # ========== 手机号验证 (cn_phone) ==========
    @pytest.mark.parametrize("value", [
        "13800138000",
        "+8613800138000",
        "8613800138000",
        "13912345678",
        "18612345678",
    ])
    def test_cn_phone_valid(self, value):
        """有效手机号应返回 True"""
        assert cn_phone(value)

    @pytest.mark.parametrize("value", [
        "1380013800",       # 10位（缺1位）
        "138001380000",     # 12位（多1位）
        "12800138000",      # 无效号段
        "1380013800a",      # 含字母
        "138-0013-8000",    # 格式错误（默认不带分隔符）
    ])
    def test_cn_phone_invalid(self, value):
        """无效手机号应返回 ValidationError"""
        assert isinstance(cn_phone(value), ValidationError)
```

### 2.2.3 白盒测试调整方案

| 验证器 | 内部算法路径 | 白盒测试重点 |
|--------|--------------|--------------|
| `us_ssn` | 格式: `AAA-GG-SSSS` | 验证区号(AAA)有效性、组号(GG)范围、校验逻辑 |
| `cn_id` | 18位：6位区划 + 8位生日 + 3位顺序 + 1位校验 | 验证加权求和算法、模11得校验码(X=10)、生日有效性 |
| `br_cpf` | 11位数字，2位校验码 | 验证两次模11计算、首位补零处理 |
| `gb_nino` | 格式: `AA NN NN NN A` | 验证前缀/后缀字母组合、数字序列 |

**白盒测试代码示例**：

```python
# tests/i18n/test_cn_whitebox.py
"""White-box tests for Chinese validators."""

import pytest
from validators.i18n.cn import cn_id  # 假设内部实现

class TestChinaValidatorsWhiteBox:
    """中国验证器白盒测试"""

    def test_cn_id_checksum_calculation(self):
        """验证身份证校验码计算逻辑"""
        # 白盒：了解内部使用加权因子 [7,9,10,5,8,4,2,1,6,3,7,9,10,5,8,4,2]
        # 和模11映射 ['1','0','X','9','8','7','6','5','4','3','2']

        base_code = "11010119900101123"  # 前17位
        expected_check = "4"  # 预期校验码

        # 验证内部计算
        from validators.i18n.cn import _calculate_cn_id_checksum
        assert _calculate_cn_id_checksum(base_code) == expected_check

    def test_cn_id_region_code_lookup(self):
        """验证行政区划代码查询逻辑"""
        # 白盒：验证内部使用行政区划代码表
        from validators.i18n.cn import _is_valid_region_code

        assert _is_valid_region_code("110101") is True   # 北京东城区
        assert _is_valid_region_code("310101") is True   # 上海黄浦区
        assert _is_valid_region_code("990101") is False  # 不存在的代码

    def test_cn_id_date_validation_path(self):
        """验证日期检查代码路径"""
        # 白盒：确保闰年2月29日和非闰年2月29日有不同处理
        leap_year_valid = "11010120200229123"   # 2020是闰年
        leap_year_invalid = "11010120210229123"  # 2021不是闰年

        # 假设内部有 _validate_date_in_id 函数
        from validators.i18n.cn import _validate_date_in_id

        assert _validate_date_in_id(leap_year_valid[6:14]) is True
        assert _validate_date_in_id(leap_year_invalid[6:14]) is False
```

### 2.2.4 回归测试清单

- [ ] 现有 i18n 验证器（es, fi, fr, ind, ru）功能不受影响
- [ ] 新验证器遵循相同的 `@validator` 装饰器模式
- [ ] 新验证器正确导出到 `validators.i18n.__all__`
- [ ] 新验证器文档字符串包含示例（doctest 可用）
- [ ] 新验证器错误消息格式与其他验证器一致

---

## 变更三：异步验证器与外部API校验支持

### 2.3.1 变更背景与动机

当前所有验证器都是同步的。实际应用中，某些验证需要外部API调用：
- 验证VAT号码是否真实存在（调用欧盟VIES API）
- 验证邮箱是否可送达（调用邮箱验证服务）
- 验证IBAN对应的银行信息
- 验证加密货币地址是否有交易历史

**预计新增功能**：
- `async_email()` - 异步验证并检查MX记录
- `async_vat()` - 异步调用VIES API验证
- `@async_validator` 装饰器 - 支持异步验证函数

```python
# 预计新增API示例
import asyncio
from validators import async_email, async_vat

async def main():
    # 验证邮箱格式 + MX记录检查
    result = await async_email('user@example.com', check_mx=True)

    # 验证VAT号码（调用VIES API）
    result = await async_vat('DE123456789', validate_exists=True)

asyncio.run(main())
```

### 2.3.2 黑盒测试调整方案

| 测试类别 | 测试场景 | 测试策略 |
|----------|----------|----------|
| 功能测试 | 异步验证正常返回 | `asyncio.run()` 执行，验证返回 True/ValidationError |
| 功能测试 | 网络超时处理 | Mock 超时，验证返回特定错误 |
| 功能测试 | API返回错误 | Mock 404/500，验证错误处理 |
| 功能测试 | 无网络时的降级 | 离线模式下验证基本格式检查仍可用 |
| 边界测试 | 并发验证 | 多个异步验证同时执行 |
| 兼容性测试 | 与同步验证器混用 | 同步+异步验证器在同一代码库中工作 |

**新增测试文件结构**：

```python
# tests/test_async_validators.py
"""Test async validators."""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from validators import ValidationError, async_email, async_vat

class TestAsyncValidatorsBlackBox:
    """异步验证器黑盒测试"""

    @pytest.mark.asyncio
    @pytest.mark.parametrize("value", [
        "user@gmail.com",
        "test@example.org",
    ])
    async def test_async_email_format_valid(self, value):
        """异步邮箱格式验证（不检查MX）"""
        result = await async_email(value, check_mx=False)
        assert result is True

    @pytest.mark.asyncio
    @pytest.mark.parametrize("value", [
        "invalid-email",
        "@example.com",
        "user@",
    ])
    async def test_async_email_format_invalid(self, value):
        """异步邮箱格式验证失败"""
        result = await async_email(value, check_mx=False)
        assert isinstance(result, ValidationError)

    @pytest.mark.asyncio
    async def test_async_email_with_mx_check_success(self):
        """异步邮箱验证（含MX检查）成功"""
        with patch('validators.async_email._check_mx_record', new_callable=AsyncMock, return_value=True):
            result = await async_email("user@gmail.com", check_mx=True)
            assert result is True

    @pytest.mark.asyncio
    async def test_async_email_with_mx_check_failure(self):
        """异步邮箱验证（MX记录不存在）"""
        with patch('validators.async_email._check_mx_record', new_callable=AsyncMock, return_value=False):
            result = await async_email("user@nonexistent-domain-12345.com", check_mx=True)
            assert isinstance(result, ValidationError)

    @pytest.mark.asyncio
    async def test_async_email_timeout(self):
        """异步验证超时处理"""
        with patch('validators.async_email._check_mx_record', new_callable=AsyncMock, side_effect=asyncio.TimeoutError):
            result = await async_email("user@example.com", check_mx=True, timeout=1)
            assert isinstance(result, ValidationError)
            # 黑盒：错误应包含超时信息
            assert "timeout" in str(result).lower() or hasattr(result, 'reason')

    @pytest.mark.asyncio
    async def test_concurrent_validation(self):
        """并发执行多个异步验证"""
        emails = ["user1@gmail.com", "user2@gmail.com", "user3@gmail.com"]

        # 并发执行
        results = await asyncio.gather(
            *[async_email(e, check_mx=False) for e in emails]
        )

        assert all(r is True for r in results)
```

### 2.3.3 白盒测试调整方案

| 测试目标 | 内部实现路径 | 测试方法 |
|----------|--------------|----------|
| 事件循环处理 | `@async_validator` 装饰器 | 验证协程正确包装、返回 awaitable |
| HTTP客户端集成 | aiohttp / httpx 调用 | Mock HTTP客户端，验证请求参数 |
| 缓存机制 | API响应缓存 | 验证相同输入不会重复调用API |
| 错误重试 | 指数退避重试 | Mock 失败→重试→成功的序列 |
| 资源清理 | 会话关闭 | 验证 async context manager 正确关闭 |
| 同步包装 | sync_to_async 适配 | 验证同步验证器可被异步包装调用 |

**白盒测试代码示例**：

```python
# tests/test_async_validators_whitebox.py
"""White-box tests for async validator internals."""

import pytest
import asyncio
from unittest.mock import AsyncMock, Mock, patch, call
from validators import async_email

class TestAsyncValidatorsWhiteBox:
    """异步验证器白盒测试"""

    @pytest.mark.asyncio
    async def test_async_validator_decorator_wraps_coroutine(self):
        """验证 @async_validator 装饰器正确包装协程"""
        from validators.utils import async_validator

        @async_validator
        async def sample_async_validator(value):
            return value.startswith("valid")

        # 白盒：验证返回的是协程结果而非普通值
        result = await sample_async_validator("valid-input")
        assert result is True

        # 验证 ValidationError 被正确包装
        result = await sample_async_validator("invalid-input")
        from validators import ValidationError
        assert isinstance(result, ValidationError)

    @pytest.mark.asyncio
    async def test_mx_check_dns_resolution_path(self):
        """验证MX记录检查的DNS解析代码路径"""
        # 白盒：了解内部使用 aiodns 或 dnspython
        from validators.async_email import _check_mx_record

        with patch('aiodns.DNSResolver.query', new_callable=AsyncMock) as mock_query:
            mock_query.return_value = [Mock(type='MX')]

            result = await _check_mx_record("gmail.com")

            # 验证DNS查询被调用
            assert mock_query.called
            assert mock_query.call_args[0][0] == "gmail.com"
            assert result is True

    @pytest.mark.asyncio
    async def test_api_response_caching(self):
        """验证API响应被缓存避免重复请求"""
        # 白盒：假设内部有 lru_cache 或自定义缓存
        from validators.async_vat import _vies_api_check

        with patch('aiohttp.ClientSession.get', new_callable=AsyncMock) as mock_get:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value={"valid": True})
            mock_get.return_value = mock_response

            # 第一次调用
            await _vies_api_check("DE", "123456789")
            # 第二次调用相同参数
            await _vies_api_check("DE", "123456789")

            # 验证只发起一次HTTP请求
            assert mock_get.call_count == 1

    @pytest.mark.asyncio
    async def test_retry_mechanism_with_backoff(self):
        """验证失败重试机制使用指数退避"""
        from validators.async_email import _check_with_retry

        with patch('asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
            # Mock 前2次失败，第3次成功
            with patch.object(_check_with_retry, '_actual_check',
                            side_effect=[Exception("Error"), Exception("Error"), True]):

                await _check_with_retry("test", max_retries=3)

                # 验证指数退避：第1次等待1s，第2次等待2s
                assert mock_sleep.call_count == 2
                assert mock_sleep.call_args_list == [call(1), call(2)]

    def test_sync_validator_async_wrap(self):
        """验证同步验证器可被异步包装"""
        from validators.utils import _wrap_sync_validator_async
        from validators import email

        async_email_wrapped = _wrap_sync_validator_async(email)

        # 验证包装后可被 await
        result = asyncio.run(async_email_wrapped("test@example.com"))
        assert result is True
```

### 2.3.4 回归测试清单

- [ ] 现有同步验证器不受异步功能影响
- [ ] `@validator` 装饰器与 `@async_validator` 行为一致（除异步特性外）
- [ ] ValidationError 在异步上下文中包含正确信息
- [ ] `r_ve` 参数在异步验证器中工作正常
- [ ] 未使用异步验证器时，事件循环未被意外创建
- [ ] 异步验证器支持所有 Python 版本（3.9+）的 asyncio 特性

---

## 3. 测试基础设施调整建议

### 3.1 新增依赖

```toml
# pyproject.toml 新增测试依赖
[project.optional-dependencies]
test = [
    "pytest>=7.0",
    "pytest-asyncio>=0.21.0",  # 新增：异步测试支持
    "pytest-aiohttp>=1.0",      # 新增：aiohttp mock支持
    "aiodns>=3.0",              # 新增：异步DNS测试
    "respx>=0.20",              # 新增：HTTPX mock
]
```

### 3.2 目录结构调整

```
tests/
├── conftest.py                    # 新增：共享fixture（mock DNS、HTTP客户端）
├── test_*.py                      # 现有同步验证器测试
├── test_async_validators.py       # 新增：异步验证器黑盒测试
├── test_async_validators_whitebox.py  # 新增：异步验证器白盒测试
├── test_schema.py                 # 新增：Schema验证黑盒测试
├── test_schema_whitebox.py        # 新增：Schema验证白盒测试
├── crypto_addresses/
│   └── test_*.py                  # 现有测试
└── i18n/
    ├── test_*.py                  # 现有国家测试
    ├── test_cn.py                 # 新增：中国验证器测试
    ├── test_cn_whitebox.py        # 新增：中国验证器白盒测试
    ├── test_us.py                 # 新增：美国验证器测试
    └── ...                        # 其他国家
```

### 3.3 共享 Fixture 示例

```python
# tests/conftest.py
import pytest
from unittest.mock import AsyncMock

@pytest.fixture
def mock_dns_resolver():
    """提供Mock DNS解析器"""
    resolver = AsyncMock()
    resolver.query = AsyncMock(return_value=[Mock(type='MX', host='mx.example.com')])
    return resolver

@pytest.fixture
def mock_http_client():
    """提供Mock HTTP客户端"""
    client = AsyncMock()
    client.get = AsyncMock()
    client.post = AsyncMock()
    return client

@pytest.fixture
def valid_cn_ids():
    """提供有效中国身份证测试数据"""
    return [
        "110101199001011234",
        "310101198001011234",
        "11010119900101123X",
    ]

@pytest.fixture
def invalid_cn_ids():
    """提供无效中国身份证测试数据"""
    return [
        "11010119900101123",      # 17位
        "1101011990010112345",    # 19位
        "110101199001011235",     # 校验位错误
    ]
```

---


*文档结束*
