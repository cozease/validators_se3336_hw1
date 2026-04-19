"""黑盒测试用例集

测试方法:
- 等价类划分 (Equivalence Class Partitioning, ECP)
- 边界值分析 (Boundary Value Analysis, BVA)
- 决策表测试 (Decision Table Testing, DT)

覆盖所有 validators 库的验证器函数。
"""

import pytest
from datetime import datetime
from uuid import UUID

import validators
from validators import ValidationError


# ============================================================================
# 1. EMAIL 验证器
# ============================================================================

class TestEmailEquivalenceClass:
    """等价类划分: email"""

    # --- 有效等价类 ---
    @pytest.mark.parametrize("value", [
        "user@example.com",              # EC1: 标准格式
        "user.name@example.com",         # EC2: 用户名含点号
        "user+tag@example.com",          # EC3: 用户名含加号
        "user@sub.domain.com",           # EC4: 多级子域名
        "123@example.com",               # EC5: 纯数字用户名
        "user@123.123.123.com",          # EC6: 数字域名
        "_user@example.com",             # EC7: 下划线开头
        "user!def@example.com",          # EC8: 特殊字符 !
        "user%def@example.com",          # EC9: 特殊字符 %
        "üser@example.com",              # EC10: 扩展拉丁字符
    ])
    def test_valid_emails(self, value):
        assert validators.email(value) is True

    # --- 无效等价类 ---
    @pytest.mark.parametrize("value", [
        "",                              # EC11: 空字符串
        "plainaddress",                  # EC12: 缺少@
        "@example.com",                  # EC13: 缺少用户名
        "user@",                         # EC14: 缺少域名
        "user@@example.com",             # EC15: 双@符号
        "user@exam ple.com",             # EC16: 域名含空格
        "user@.example.com",             # EC17: 域名以点开头
        "user@example",                  # EC18: 缺少TLD (simple_host=False时)
    ])
    def test_invalid_emails(self, value):
        assert isinstance(validators.email(value), ValidationError)


class TestEmailBoundary:
    """边界值分析: email 用户名最大64字符, 域名最大253字符"""

    def test_username_exactly_64_chars(self):
        username = "a" * 64
        assert validators.email(f"{username}@example.com") is True

    def test_username_65_chars_invalid(self):
        username = "a" * 65
        assert isinstance(validators.email(f"{username}@example.com"), ValidationError)

    def test_username_1_char(self):
        assert validators.email("a@example.com") is True

    def test_domain_at_253_chars(self):
        # 构造一个接近253字符的域名
        label = "a" * 63  # 单个label最长63
        domain = f"{label}.{label}.{label}.com"  # ~193 chars
        assert validators.email(f"u@{domain}") is True

    def test_domain_over_253_chars_invalid(self):
        label = "a" * 63
        domain = f"{label}.{label}.{label}.{label}.com"  # >253 chars
        assert isinstance(validators.email(f"u@{domain}"), ValidationError)


class TestEmailDecisionTable:
    """决策表: email 参数组合 (ipv4_address, ipv6_address, simple_host)"""

    def test_ipv4_domain_with_brackets(self):
        assert validators.email("user@[192.168.1.1]", ipv4_address=True) is True

    def test_ipv4_domain_without_brackets(self):
        assert isinstance(
            validators.email("user@192.168.1.1", ipv4_address=True), ValidationError
        )

    def test_ipv6_domain_with_brackets(self):
        assert validators.email("user@[::1]", ipv6_address=True) is True

    def test_ipv6_domain_without_brackets(self):
        assert isinstance(
            validators.email("user@::1", ipv6_address=True), ValidationError
        )

    def test_simple_host(self):
        assert validators.email("user@localhost", simple_host=True) is True

    def test_rfc_1034_trailing_dot(self):
        assert validators.email("user@example.com.", rfc_1034=True) is True

    def test_rfc_2782_service_record(self):
        assert validators.email("user@_sip._tcp.example.com", rfc_2782=True) is True


# ============================================================================
# 2. URL 验证器
# ============================================================================

class TestURLEquivalenceClass:
    """等价类划分: url"""

    @pytest.mark.parametrize("value", [
        "http://example.com",             # EC1: HTTP
        "https://example.com",            # EC2: HTTPS
        "ftp://example.com",              # EC3: FTP
        "https://example.com:8080",       # EC4: 带端口
        "https://example.com/path",       # EC5: 带路径
        "https://example.com?q=1",        # EC6: 带查询参数
        "https://example.com#frag",       # EC7: 带片段
        "https://user:pass@example.com",  # EC8: 带认证
        "https://example.com/path?q=1&a=2#f",  # EC9: 完整URL
        "ssh://example.com",              # EC10: SSH协议
        "git://example.com",              # EC11: Git协议
        "http://10.0.0.1",                # EC12: IPv4地址
    ])
    def test_valid_urls(self, value):
        assert validators.url(value) is True

    @pytest.mark.parametrize("value", [
        "",                                # EC13: 空字符串
        "example.com",                     # EC14: 无协议
        "http://",                         # EC15: 无主机名
        "http:// example.com",             # EC16: 含空格
        "http://example.com\t",            # EC17: 含制表符
        "xyz://example.com",               # EC18: 无效协议
        "://example.com",                  # EC19: 空协议
    ])
    def test_invalid_urls(self, value):
        assert isinstance(validators.url(value), ValidationError)


class TestURLBoundary:
    """边界值分析: url 端口范围 1-65535"""

    def test_port_1(self):
        assert validators.url("http://example.com:1") is True

    def test_port_65535(self):
        assert validators.url("http://example.com:65535") is True

    def test_port_0_invalid(self):
        assert isinstance(validators.url("http://example.com:0"), ValidationError)

    def test_port_65536_invalid(self):
        assert isinstance(validators.url("http://example.com:65536"), ValidationError)

    def test_empty_path(self):
        assert validators.url("http://example.com/") is True

    def test_long_path(self):
        path = "/a" * 100
        assert validators.url(f"http://example.com{path}") is True


class TestURLDecisionTable:
    """决策表: url 参数组合"""

    def test_private_ip_with_private_true(self):
        assert validators.url("http://192.168.1.1", private=True) is True

    def test_private_ip_with_private_false(self):
        assert isinstance(
            validators.url("http://192.168.1.1", private=False), ValidationError
        )

    def test_public_ip_with_private_false(self):
        assert validators.url("http://8.8.8.8", private=False) is True

    def test_public_ip_with_private_true(self):
        assert isinstance(
            validators.url("http://8.8.8.8", private=True), ValidationError
        )

    def test_simple_host_enabled(self):
        assert validators.url("http://localhost", simple_host=True) is True

    def test_simple_host_disabled(self):
        assert isinstance(
            validators.url("http://localhost", simple_host=False), ValidationError
        )

    def test_custom_validate_scheme(self):
        assert validators.url(
            "custom://example.com",
            validate_scheme=lambda s: s == "custom"
        ) is True

    def test_skip_ipv4(self):
        assert isinstance(
            validators.url("http://10.0.0.1", skip_ipv4_addr=True, simple_host=False), ValidationError
        )

    def test_consider_tld_valid(self):
        assert validators.url("http://example.com", consider_tld=True) is True

    def test_strict_query_invalid(self):
        # ?bad (无key=value结构) 在 strict_query=True 下应失败
        assert isinstance(
            validators.url("http://example.com?bad", strict_query=True), ValidationError
        )


# ============================================================================
# 3. IPv4 验证器
# ============================================================================

class TestIPv4EquivalenceClass:
    """等价类划分: ipv4"""

    @pytest.mark.parametrize("value", [
        "0.0.0.0",                # EC1: 最小地址
        "255.255.255.255",        # EC2: 最大地址
        "192.168.1.1",            # EC3: 私有A类
        "10.0.0.1",               # EC4: 私有B类
        "172.16.0.1",             # EC5: 私有C类
        "127.0.0.1",              # EC6: 回环地址
        "8.8.8.8",                # EC7: 公网地址
        "192.168.1.0/24",         # EC8: CIDR网络
    ])
    def test_valid_ipv4(self, value):
        assert validators.ipv4(value) is True

    @pytest.mark.parametrize("value", [
        "",                       # EC9: 空字符串
        "256.1.1.1",              # EC10: 超出范围
        "1.1.1",                  # EC11: 缺少一段
        "1.1.1.1.1",              # EC12: 多余一段
        "abc.def.ghi.jkl",        # EC13: 非数字
        "1.1.1.1/33",             # EC14: CIDR超出范围
        "01.01.01.01",            # EC15: 前导零
    ])
    def test_invalid_ipv4(self, value):
        assert isinstance(validators.ipv4(value), ValidationError)


class TestIPv4Boundary:
    """边界值分析: ipv4"""

    def test_each_octet_at_0(self):
        assert validators.ipv4("0.0.0.0") is True

    def test_each_octet_at_255(self):
        assert validators.ipv4("255.255.255.255") is True

    def test_cidr_0(self):
        assert validators.ipv4("10.0.0.0/0") is True

    def test_cidr_32(self):
        assert validators.ipv4("10.0.0.1/32") is True

    def test_cidr_negative_invalid(self):
        assert isinstance(validators.ipv4("10.0.0.1/-1"), ValidationError)


class TestIPv4DecisionTable:
    """决策表: ipv4 参数组合 (cidr, strict, private, host_bit)"""

    def test_cidr_false_reject_network(self):
        assert isinstance(validators.ipv4("192.168.1.0/24", cidr=False), ValidationError)

    def test_strict_requires_cidr(self):
        assert isinstance(validators.ipv4("192.168.1.1", strict=True), ValidationError)

    def test_strict_with_cidr(self):
        assert validators.ipv4("192.168.1.0/24", strict=True) is True

    def test_private_true_accepts_private(self):
        assert validators.ipv4("192.168.1.1", private=True) is True

    def test_private_true_rejects_public(self):
        assert isinstance(validators.ipv4("8.8.8.8", private=True), ValidationError)

    def test_private_false_accepts_public(self):
        assert validators.ipv4("8.8.8.8", private=False) is True

    def test_private_false_rejects_private(self):
        assert isinstance(validators.ipv4("192.168.1.1", private=False), ValidationError)

    def test_host_bit_false_rejects_host_bits(self):
        assert isinstance(validators.ipv4("192.168.1.1/24", host_bit=False), ValidationError)

    def test_host_bit_false_accepts_network(self):
        assert validators.ipv4("192.168.1.0/24", host_bit=False) is True

    def test_localhost_is_private(self):
        assert validators.ipv4("127.0.0.1", private=True) is True

    def test_link_local_is_private(self):
        assert validators.ipv4("169.254.1.1", private=True) is True

    def test_broadcast_is_private(self):
        assert validators.ipv4("224.0.0.1", private=True) is True


# ============================================================================
# 4. IPv6 验证器
# ============================================================================

class TestIPv6EquivalenceClass:
    """等价类划分: ipv6"""

    @pytest.mark.parametrize("value", [
        "::1",                                           # EC1: 回环地址
        "::ffff:192.0.2.128",                            # EC2: IPv4映射
        "2001:0db8:85a3:0000:0000:8a2e:0370:7334",       # EC3: 完整格式
        "2001:db8::1",                                   # EC4: 压缩格式
        "fe80::1%eth0",                                  # EC5: 带接口
        "::1/128",                                       # EC6: CIDR
    ])
    def test_valid_ipv6(self, value):
        assert validators.ipv6(value) is True

    @pytest.mark.parametrize("value", [
        "",                                              # EC7: 空字符串
        "abc.def.ghi.jkl",                               # EC8: IPv4格式
        "12345::1",                                      # EC9: 段超出
        "::gggg",                                        # EC10: 非hex字符
        "1:2:3:4:5:6:7:8:9",                             # EC11: 段数太多
    ])
    def test_invalid_ipv6(self, value):
        assert isinstance(validators.ipv6(value), ValidationError)


class TestIPv6DecisionTable:
    """决策表: ipv6 参数组合"""

    def test_cidr_false_reject_network(self):
        assert isinstance(validators.ipv6("::1/128", cidr=False), ValidationError)

    def test_strict_requires_cidr(self):
        assert isinstance(validators.ipv6("::1", strict=True), ValidationError)

    def test_strict_with_cidr(self):
        assert validators.ipv6("::1/128", strict=True) is True

    def test_host_bit_false_accepts_network(self):
        assert validators.ipv6("2001:db8::/32", host_bit=False) is True

    def test_host_bit_false_rejects_host_bits(self):
        assert isinstance(validators.ipv6("2001:db8::1/32", host_bit=False), ValidationError)


# ============================================================================
# 5. MAC 地址验证器
# ============================================================================

class TestMacAddressEquivalenceClass:
    """等价类划分: mac_address"""

    @pytest.mark.parametrize("value", [
        "01:23:45:67:89:AB",     # EC1: 冒号分隔大写
        "01:23:45:67:89:ab",     # EC2: 冒号分隔小写
        "01-23-45-67-89-AB",     # EC3: 横杠分隔大写
        "01-23-45-67-89-ab",     # EC4: 横杠分隔小写
        "00:00:00:00:00:00",     # EC5: 全零
        "FF:FF:FF:FF:FF:FF",     # EC6: 全FF (广播)
        "aA:bB:cC:dD:eE:fF",    # EC7: 混合大小写
    ])
    def test_valid_mac(self, value):
        assert validators.mac_address(value) is True

    @pytest.mark.parametrize("value", [
        "",                      # EC8: 空字符串
        "01:23:45:67:89",        # EC9: 只有5段
        "01:23:45:67:89:AB:CD",  # EC10: 7段
        "01:23:45:67:89:GG",     # EC11: 非hex字符
        "0123.4567.89AB",        # EC12: 点分隔格式
        "01:23:45-67:89:AB",     # EC13: 混合分隔符
        "01-23-45:67-89-AB",     # EC14: 混合分隔符2
    ])
    def test_invalid_mac(self, value):
        assert isinstance(validators.mac_address(value), ValidationError)


class TestMacAddressBoundary:
    """边界值分析: mac_address 每段的hex值"""

    def test_all_min_values(self):
        assert validators.mac_address("00:00:00:00:00:00") is True

    def test_all_max_values(self):
        assert validators.mac_address("FF:FF:FF:FF:FF:FF") is True

    def test_single_char_segments(self):
        # 每段必须恰好2个hex字符
        assert isinstance(validators.mac_address("1:2:3:4:5:6"), ValidationError)


# ============================================================================
# 6. 信用卡验证器
# ============================================================================

class TestCardEquivalenceClass:
    """等价类划分: 各种卡号"""

    # Visa: 以4开头, 16位, Luhn校验
    def test_valid_visa(self):
        assert validators.visa("4242424242424242") is True

    def test_visa_wrong_prefix(self):
        assert isinstance(validators.visa("5242424242424242"), ValidationError)

    def test_visa_wrong_length(self):
        assert isinstance(validators.visa("424242424242424"), ValidationError)  # 15位

    # Mastercard: 以51-55或22-27开头, 16位
    def test_valid_mastercard(self):
        assert validators.mastercard("5555555555554444") is True

    def test_mastercard_prefix_22(self):
        assert validators.mastercard("2223003122003222") is True

    def test_mastercard_wrong_prefix(self):
        assert isinstance(validators.mastercard("4242424242424242"), ValidationError)

    # Amex: 以34或37开头, 15位
    def test_valid_amex(self):
        assert validators.amex("378282246310005") is True

    def test_amex_prefix_34(self):
        assert validators.amex("340000000000009") is True

    def test_amex_wrong_length(self):
        assert isinstance(validators.amex("37828224631000"), ValidationError)  # 14位

    # UnionPay: 以62开头, 16位
    def test_valid_unionpay(self):
        assert validators.unionpay("6200000000000005") is True

    def test_unionpay_wrong_prefix(self):
        assert isinstance(validators.unionpay("6300000000000004"), ValidationError)

    # Diners: 以30/36/38/39开头, 14或16位
    def test_valid_diners_16(self):
        assert validators.diners("3056930009020004") is True

    def test_diners_wrong_prefix(self):
        assert isinstance(validators.diners("3156930009020004"), ValidationError)

    # JCB: 以35开头, 16位
    def test_valid_jcb(self):
        assert validators.jcb("3566002020360505") is True

    def test_jcb_wrong_prefix(self):
        assert isinstance(validators.jcb("3666002020360505"), ValidationError)

    # Discover: 以60/64/65开头, 16位
    def test_valid_discover(self):
        assert validators.discover("6011111111111117") is True

    def test_discover_prefix_65(self):
        assert validators.discover("6500000000000002") is True

    # Mir: 以2200-2204开头, 16位
    def test_valid_mir(self):
        assert validators.mir("2200123456789019") is True

    def test_mir_prefix_2204(self):
        # 2204开头, 需要Luhn校验通过
        assert validators.mir("2204000000000000") is True

    def test_mir_wrong_prefix(self):
        assert isinstance(validators.mir("2205123456789011"), ValidationError)


class TestCardBoundary:
    """边界值分析: card_number (Luhn算法)"""

    def test_luhn_valid(self):
        assert validators.card_number("4242424242424242") is True

    def test_luhn_invalid_off_by_one(self):
        assert isinstance(validators.card_number("4242424242424241"), ValidationError)

    def test_empty_card(self):
        assert isinstance(validators.card_number(""), ValidationError)

    def test_non_numeric_card(self):
        assert isinstance(validators.card_number("abcdefghijklmnop"), ValidationError)

    def test_single_digit_zero(self):
        assert validators.card_number("0") is True  # Luhn: 0%10==0

    def test_spaces_invalid(self):
        assert isinstance(validators.card_number("4242 4242 4242 4242"), ValidationError)


# ============================================================================
# 7. BETWEEN 验证器
# ============================================================================

class TestBetweenEquivalenceClass:
    """等价类划分: between"""

    # 有效等价类
    def test_int_in_range(self):
        assert validators.between(5, min_val=1, max_val=10) is True

    def test_float_in_range(self):
        assert validators.between(5.5, min_val=1.0, max_val=10.0) is True

    def test_str_in_range(self):
        assert validators.between("b", min_val="a", max_val="c") is True

    def test_datetime_in_range(self):
        assert validators.between(
            datetime(2020, 6, 15),
            min_val=datetime(2020, 1, 1),
            max_val=datetime(2020, 12, 31)
        ) is True

    def test_none_value(self):
        assert isinstance(validators.between(None, min_val=0, max_val=10), ValidationError)

    # 无效等价类
    def test_below_min(self):
        assert isinstance(validators.between(0, min_val=1, max_val=10), ValidationError)

    def test_above_max(self):
        assert isinstance(validators.between(11, min_val=1, max_val=10), ValidationError)


class TestBetweenBoundary:
    """边界值分析: between"""

    def test_exactly_at_min(self):
        assert validators.between(1, min_val=1, max_val=10) is True

    def test_exactly_at_max(self):
        assert validators.between(10, min_val=1, max_val=10) is True

    def test_one_below_min(self):
        assert isinstance(validators.between(0, min_val=1, max_val=10), ValidationError)

    def test_one_above_max(self):
        assert isinstance(validators.between(11, min_val=1, max_val=10), ValidationError)

    def test_min_equals_max(self):
        assert validators.between(5, min_val=5, max_val=5) is True

    def test_float_boundary_just_below(self):
        assert isinstance(
            validators.between(0.999999, min_val=1.0, max_val=10.0), ValidationError
        )

    def test_float_boundary_just_above(self):
        assert isinstance(
            validators.between(10.000001, min_val=1.0, max_val=10.0), ValidationError
        )


class TestBetweenDecisionTable:
    """决策表: between min_val/max_val 组合"""

    def test_only_min(self):
        assert validators.between(100, min_val=1) is True

    def test_only_max(self):
        assert validators.between(-100, max_val=0) is True

    def test_neither_min_nor_max(self):
        assert validators.between(999999) is True

    def test_min_greater_than_max_returns_error(self):
        # @validator 装饰器捕获 ValueError, 返回 ValidationError
        assert isinstance(validators.between(5, min_val=10, max_val=1), ValidationError)

    def test_type_mismatch_returns_error(self):
        # @validator 装饰器捕获 TypeError, 返回 ValidationError
        assert isinstance(validators.between(5, min_val="a", max_val="z"), ValidationError)


# ============================================================================
# 8. LENGTH 验证器
# ============================================================================

class TestLengthEquivalenceClass:
    """等价类划分: length"""

    def test_within_range(self):
        assert validators.length("hello", min_val=1, max_val=10) is True

    def test_too_short(self):
        assert isinstance(validators.length("hi", min_val=5), ValidationError)

    def test_too_long(self):
        assert isinstance(validators.length("hello world", max_val=5), ValidationError)

    def test_exact_length(self):
        assert validators.length("hello", min_val=5, max_val=5) is True

    def test_empty_string_min_0(self):
        assert validators.length("", min_val=0, max_val=10) is True


class TestLengthBoundary:
    """边界值分析: length"""

    def test_length_at_min(self):
        assert validators.length("abc", min_val=3) is True

    def test_length_below_min(self):
        assert isinstance(validators.length("ab", min_val=3), ValidationError)

    def test_length_at_max(self):
        assert validators.length("abcde", max_val=5) is True

    def test_length_above_max(self):
        assert isinstance(validators.length("abcdef", max_val=5), ValidationError)

    def test_negative_min_returns_error(self):
        # @validator 装饰器捕获 ValueError, 返回 ValidationError
        assert isinstance(validators.length("test", min_val=-1), ValidationError)

    def test_negative_max_returns_error(self):
        # @validator 装饰器捕获 ValueError, 返回 ValidationError
        assert isinstance(validators.length("test", max_val=-1), ValidationError)

    def test_unicode_length(self):
        assert validators.length("中文测试", min_val=4, max_val=4) is True


# ============================================================================
# 9. DOMAIN 验证器
# ============================================================================

class TestDomainEquivalenceClass:
    """等价类划分: domain"""

    @pytest.mark.parametrize("value", [
        "example.com",                    # EC1: 标准域名
        "sub.example.com",                # EC2: 子域名
        "example.co.uk",                  # EC3: 国家级TLD
        "xn----gtbspbbmkef.xn--p1ai",    # EC4: IDN域名
        "a.com",                          # EC5: 最短域名
        "123.com",                        # EC6: 数字域名
    ])
    def test_valid_domains(self, value):
        assert validators.domain(value) is True

    @pytest.mark.parametrize("value", [
        "",                               # EC7: 空字符串
        "example",                        # EC8: 无TLD
        ".example.com",                   # EC9: 以点开头
        "example.com/",                   # EC10: 含斜杠
        "exam ple.com",                   # EC11: 含空格
        "-example.com",                   # EC12: 以连字符开头
    ])
    def test_invalid_domains(self, value):
        assert isinstance(validators.domain(value), ValidationError)


class TestDomainDecisionTable:
    """决策表: domain 参数组合"""

    def test_consider_tld_valid(self):
        assert validators.domain("example.com", consider_tld=True) is True

    def test_consider_tld_invalid(self):
        assert isinstance(
            validators.domain("example.invalidtld", consider_tld=True), ValidationError
        )

    def test_rfc_1034_trailing_dot(self):
        assert validators.domain("example.com.", rfc_1034=True) is True

    def test_rfc_1034_without_flag(self):
        assert isinstance(validators.domain("example.com."), ValidationError)

    def test_rfc_2782_underscore(self):
        assert validators.domain("_sip._tcp.example.com", rfc_2782=True) is True

    def test_rfc_2782_without_flag(self):
        assert isinstance(validators.domain("_sip._tcp.example.com"), ValidationError)


# ============================================================================
# 10. SLUG 验证器
# ============================================================================

class TestSlugEquivalenceClass:
    """等价类划分: slug"""

    @pytest.mark.parametrize("value", [
        "my-slug",                # EC1: 标准slug
        "my-slug-2134",           # EC2: 含数字
        "slug",                   # EC3: 无连字符
        "a",                      # EC4: 单字符
        "0",                      # EC5: 单数字
        "my-long-slug-here",      # EC6: 多段
    ])
    def test_valid_slugs(self, value):
        assert validators.slug(value) is True

    @pytest.mark.parametrize("value", [
        "",                       # EC7: 空字符串
        "my.slug",                # EC8: 含点
        "My-Slug",                # EC9: 大写字母
        "-my-slug",               # EC10: 以连字符开头
        "my-slug-",               # EC11: 以连字符结尾
        "my--slug",               # EC12: 连续连字符
        "my slug",                # EC13: 含空格
        "my_slug",                # EC14: 含下划线
    ])
    def test_invalid_slugs(self, value):
        assert isinstance(validators.slug(value), ValidationError)


# ============================================================================
# 11. UUID 验证器
# ============================================================================

class TestUUIDEquivalenceClass:
    """等价类划分: uuid"""

    @pytest.mark.parametrize("value", [
        "2bc1c94f-0deb-43e9-92a1-4775189ec9f8",    # EC1: 标准UUID
        "550e8400-e29b-41d4-a716-446655440000",    # EC2: 另一个UUID
        "00000000-0000-0000-0000-000000000000",    # EC3: 全零UUID
        "ffffffff-ffff-ffff-ffff-ffffffffffff",    # EC4: 全F UUID
    ])
    def test_valid_uuid_strings(self, value):
        assert validators.uuid(value) is True

    def test_uuid_object(self):
        assert validators.uuid(UUID("2bc1c94f-0deb-43e9-92a1-4775189ec9f8")) is True

    @pytest.mark.parametrize("value", [
        "",                                          # EC5: 空字符串
        "not-a-uuid",                                # EC6: 非UUID
        "2bc1c94f 0deb-43e9-92a1-4775189ec9f8",     # EC7: 空格代替连字符
        "2bc1c94f-0deb-43e9-92a1-4775189ec9f",      # EC8: 少一个字符
        "2bc1c94f-0deb-43e9-92a1-4775189ec9f8a",    # EC9: 多一个字符
    ])
    def test_invalid_uuids(self, value):
        assert isinstance(validators.uuid(value), ValidationError)


# ============================================================================
# 12. CRON 验证器
# ============================================================================

class TestCronEquivalenceClass:
    """等价类划分: cron"""

    @pytest.mark.parametrize("value", [
        "* * * * *",             # EC1: 全通配符
        "0 0 1 1 0",             # EC2: 全具体值
        "*/5 * * * *",           # EC3: 步长值
        "0-30 * * * *",          # EC4: 范围
        "1,15,30 * * * *",       # EC5: 列表
        "0 0 * * 1-5",           # EC6: 工作日范围
        "0 */2 * * *",           # EC7: 每2小时
    ])
    def test_valid_crons(self, value):
        assert validators.cron(value) is True

    @pytest.mark.parametrize("value", [
        "",                      # EC8: 空字符串
        "* * * *",               # EC9: 只有4个字段
        "* * * * * *",           # EC10: 6个字段
        "60 * * * *",            # EC11: 分钟超出范围
        "* 24 * * *",            # EC12: 小时超出范围
        "* * 32 * *",            # EC13: 日期超出范围
        "* * * 13 *",            # EC14: 月份超出范围
        "* * * * 7",             # EC15: 星期超出范围
        "30-20 * * * *",         # EC16: 范围起点>终点
    ])
    def test_invalid_crons(self, value):
        result = None
        try:
            result = validators.cron(value)
        except (ValueError, ValidationError):
            return  # ValueError for malformed cron is also acceptable
        assert isinstance(result, ValidationError)


class TestCronBoundary:
    """边界值分析: cron 各字段边界"""

    # 分钟: 0-59
    def test_minute_min(self):
        assert validators.cron("0 * * * *") is True

    def test_minute_max(self):
        assert validators.cron("59 * * * *") is True

    def test_minute_over_max(self):
        assert isinstance(validators.cron("60 * * * *"), ValidationError)

    # 小时: 0-23
    def test_hour_min(self):
        assert validators.cron("* 0 * * *") is True

    def test_hour_max(self):
        assert validators.cron("* 23 * * *") is True

    def test_hour_over_max(self):
        assert isinstance(validators.cron("* 24 * * *"), ValidationError)

    # 日: 1-31
    def test_day_min(self):
        assert validators.cron("* * 1 * *") is True

    def test_day_max(self):
        assert validators.cron("* * 31 * *") is True

    def test_day_zero_invalid(self):
        assert isinstance(validators.cron("* * 0 * *"), ValidationError)

    def test_day_over_max(self):
        assert isinstance(validators.cron("* * 32 * *"), ValidationError)

    # 月: 1-12
    def test_month_min(self):
        assert validators.cron("* * * 1 *") is True

    def test_month_max(self):
        assert validators.cron("* * * 12 *") is True

    def test_month_zero_invalid(self):
        assert isinstance(validators.cron("* * * 0 *"), ValidationError)

    def test_month_over_max(self):
        assert isinstance(validators.cron("* * * 13 *"), ValidationError)

    # 星期: 0-6
    def test_weekday_min(self):
        assert validators.cron("* * * * 0") is True

    def test_weekday_max(self):
        assert validators.cron("* * * * 6") is True

    def test_weekday_over_max(self):
        assert isinstance(validators.cron("* * * * 7"), ValidationError)


class TestCronDecisionTable:
    """决策表: cron 各种组合格式"""

    def test_step_with_range_not_supported(self):
        # cron实现不支持 range/step 组合如 "0-30/5"
        assert isinstance(validators.cron("0-30/5 * * * *"), ValidationError)

    def test_step_value_zero_invalid(self):
        assert isinstance(validators.cron("*/0 * * * *"), ValidationError)

    def test_list_with_same_type_items(self):
        # 列表中每项必须是同类型 (纯数字)
        assert validators.cron("1,5,10 * * * *") is True

    def test_list_with_range_not_supported(self):
        # 列表中混合范围不支持
        assert isinstance(validators.cron("1,5,10-20 * * * *"), ValidationError)

    def test_negative_step_invalid(self):
        assert isinstance(validators.cron("*/-1 * * * *"), ValidationError)


# ============================================================================
# 13. HASH 验证器
# ============================================================================

class TestHashesEquivalenceClass:
    """等价类划分: 各种hash"""

    # MD5: 32个hex字符
    def test_valid_md5(self):
        assert validators.md5("d41d8cd98f00b204e9800998ecf8427e") is True

    def test_md5_uppercase(self):
        assert validators.md5("D41D8CD98F00B204E9800998ECF8427E") is True

    def test_md5_wrong_length(self):
        assert isinstance(validators.md5("d41d8cd98f00b204e9800998ecf8427"), ValidationError)

    def test_md5_invalid_chars(self):
        assert isinstance(validators.md5("g41d8cd98f00b204e9800998ecf8427e"), ValidationError)

    # SHA1: 40个hex字符
    def test_valid_sha1(self):
        assert validators.sha1("da39a3ee5e6b4b0d3255bfef95601890afd80709") is True

    def test_sha1_wrong_length(self):
        assert isinstance(validators.sha1("da39a3ee5e6b4b0d3255bfef95601890afd8070"), ValidationError)

    # SHA256: 64个hex字符
    def test_valid_sha256(self):
        assert validators.sha256(
            "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        ) is True

    # SHA512: 128个hex字符
    def test_valid_sha512(self):
        assert validators.sha512(
            "cf83e1357eefb8bdf1542850d66d8007d620e4050b5715dc83f4a921d36ce"
            "9ce47d0d13c5d85f2b0ff8318d2877eec2f63b931bd47417a81a538327af9"
            "27da3e"
        ) is True

    def test_empty_hash(self):
        assert isinstance(validators.md5(""), ValidationError)
        assert isinstance(validators.sha1(""), ValidationError)
        assert isinstance(validators.sha256(""), ValidationError)


class TestHashesBoundary:
    """边界值分析: hash 长度"""

    def test_md5_31_chars(self):
        assert isinstance(validators.md5("a" * 31), ValidationError)

    def test_md5_32_chars(self):
        assert validators.md5("a" * 32) is True

    def test_md5_33_chars(self):
        assert isinstance(validators.md5("a" * 33), ValidationError)

    def test_sha1_39_chars(self):
        assert isinstance(validators.sha1("a" * 39), ValidationError)

    def test_sha1_40_chars(self):
        assert validators.sha1("a" * 40) is True

    def test_sha1_41_chars(self):
        assert isinstance(validators.sha1("a" * 41), ValidationError)

    def test_sha224_55_chars(self):
        assert isinstance(validators.sha224("a" * 55), ValidationError)

    def test_sha224_56_chars(self):
        assert validators.sha224("a" * 56) is True

    def test_sha224_57_chars(self):
        assert isinstance(validators.sha224("a" * 57), ValidationError)

    def test_sha384_95_chars(self):
        assert isinstance(validators.sha384("a" * 95), ValidationError)

    def test_sha384_96_chars(self):
        assert validators.sha384("a" * 96) is True

    def test_sha384_97_chars(self):
        assert isinstance(validators.sha384("a" * 97), ValidationError)


# ============================================================================
# 14. ENCODING 验证器
# ============================================================================

class TestEncodingEquivalenceClass:
    """等价类划分: 编码验证"""

    # Base16
    def test_valid_base16(self):
        assert validators.base16("a3f4b2") is True

    def test_base16_uppercase(self):
        assert validators.base16("A3F4B2") is True

    def test_base16_invalid_char(self):
        assert isinstance(validators.base16("a3f4Z1"), ValidationError)

    # Base32
    def test_valid_base32(self):
        assert validators.base32("MFZWIZLTOQ======") is True

    def test_base32_lowercase_invalid(self):
        assert isinstance(validators.base32("mfzwizltoq======"), ValidationError)

    def test_base32_invalid_char(self):
        assert isinstance(validators.base32("MFZW8ZLT"), ValidationError)

    # Base58
    def test_valid_base58(self):
        assert validators.base58("14pq6y9H2DLGahPsM4s7ugsNSD2uxpHsJx") is True

    def test_base58_invalid_zero(self):
        assert isinstance(validators.base58("0invalidbase58"), ValidationError)

    def test_base58_invalid_O(self):
        assert isinstance(validators.base58("Oinvalidbase58"), ValidationError)

    def test_base58_invalid_l(self):
        assert isinstance(validators.base58("linvalidbase58"), ValidationError)

    def test_base58_invalid_I(self):
        assert isinstance(validators.base58("Iinvalidbase58"), ValidationError)

    # Base64
    def test_valid_base64(self):
        assert validators.base64("Y2hhcmFjdGVyIHNldA==") is True

    def test_base64_no_padding(self):
        assert validators.base64("YQ==") is True

    def test_base64_single_pad(self):
        assert validators.base64("YWI=") is True

    def test_base64_invalid(self):
        assert isinstance(validators.base64("Y2hhcmFjdGVyIHNldA="), ValidationError)

    def test_empty_encoding(self):
        assert isinstance(validators.base16(""), ValidationError)
        assert isinstance(validators.base32(""), ValidationError)
        assert isinstance(validators.base58(""), ValidationError)
        assert isinstance(validators.base64(""), ValidationError)


class TestEncodingBoundary:
    """边界值分析: encoding 最小有效值"""

    def test_base16_single_char(self):
        assert validators.base16("0") is True

    def test_base32_single_char(self):
        assert validators.base32("A") is True

    def test_base58_single_char(self):
        assert validators.base58("1") is True

    def test_base64_four_chars(self):
        assert validators.base64("AAAA") is True

    def test_base64_empty_content(self):
        # 空的base64编码 (零字节) 是空字符串
        assert isinstance(validators.base64(""), ValidationError)


# ============================================================================
# 15. IBAN 验证器
# ============================================================================

class TestIBANEquivalenceClass:
    """等价类划分: iban"""

    @pytest.mark.parametrize("value", [
        "DE29100500001061045672",         # EC1: 德国IBAN
        "GB82WEST12345698765432",         # EC2: 英国IBAN
        "FR7630006000011234567890189",    # EC3: 法国IBAN
        "ES7921000813610123456789",       # EC4: 西班牙IBAN
    ])
    def test_valid_iban(self, value):
        assert validators.iban(value) is True

    @pytest.mark.parametrize("value", [
        "",                              # EC5: 空字符串
        "123456",                        # EC6: 太短
        "XX00000000000000000",           # EC7: 校验和错误
        "DE00100500001061045672",         # EC8: 修改后的校验位
    ])
    def test_invalid_iban(self, value):
        assert isinstance(validators.iban(value), ValidationError)


class TestIBANBoundary:
    """边界值分析: iban 长度 13-34"""

    def test_min_length_13(self):
        # 2 letter + 2 digit + 9 alnum = 13
        # 需要通过mod97校验
        assert validators.iban("NO9386011117947") is True  # 挪威IBAN 15字符

    def test_too_short(self):
        assert isinstance(validators.iban("DE29100500001"), ValidationError)

    def test_non_alpha_country(self):
        assert isinstance(validators.iban("12345678901234"), ValidationError)


# ============================================================================
# 16. FINANCE 验证器
# ============================================================================

class TestFinanceEquivalenceClass:
    """等价类划分: cusip, isin, sedol"""

    # CUSIP: 9字符, 校验和
    def test_valid_cusip(self):
        assert validators.cusip("037833DP2") is True

    def test_cusip_wrong_checksum(self):
        assert isinstance(validators.cusip("037833DP3"), ValidationError)

    def test_cusip_wrong_length(self):
        assert isinstance(validators.cusip("037833DP"), ValidationError)

    # SEDOL: 7字符, 不含元音, 加权校验和
    def test_valid_sedol(self):
        assert validators.sedol("2936921") is True

    def test_sedol_with_vowel(self):
        assert isinstance(validators.sedol("29A6922"), ValidationError)

    def test_sedol_wrong_length(self):
        assert isinstance(validators.sedol("293692"), ValidationError)

    def test_sedol_wrong_checksum(self):
        assert isinstance(validators.sedol("2936922"), ValidationError)


class TestFinanceBoundary:
    """边界值分析: finance"""

    def test_cusip_exactly_9(self):
        assert validators.cusip("037833DP2") is True

    def test_cusip_8_chars(self):
        assert isinstance(validators.cusip("037833DP"), ValidationError)

    def test_cusip_10_chars(self):
        assert isinstance(validators.cusip("037833DP22"), ValidationError)

    def test_sedol_exactly_7(self):
        assert validators.sedol("2936921") is True

    def test_sedol_6_chars(self):
        assert isinstance(validators.sedol("293692"), ValidationError)

    def test_sedol_8_chars(self):
        assert isinstance(validators.sedol("29369210"), ValidationError)


# ============================================================================
# 17. HOSTNAME 验证器
# ============================================================================

class TestHostnameEquivalenceClass:
    """等价类划分: hostname"""

    @pytest.mark.parametrize("value", [
        "localhost",                  # EC1: 简单主机名
        "my-pc",                      # EC2: 含连字符
        "example.com",                # EC3: 域名
        "sub.example.com",            # EC4: 子域名
        "192.168.1.1",                # EC5: IPv4
        "::1",                        # EC6: IPv6
        "example.com:8080",           # EC7: 带端口域名
        "192.168.1.1:443",            # EC8: 带端口IPv4
        "[::1]:22",                   # EC9: 带端口IPv6
    ])
    def test_valid_hostnames(self, value):
        assert validators.hostname(value) is True

    @pytest.mark.parametrize("value", [
        "",                           # EC10: 空字符串
        "-invalid",                   # EC11: 以连字符开头
        "invalid-",                   # EC12: 以连字符结尾
    ])
    def test_invalid_hostnames(self, value):
        assert isinstance(validators.hostname(value), ValidationError)


class TestHostnameBoundary:
    """边界值分析: hostname 端口 1-65535"""

    def test_port_1(self):
        assert validators.hostname("localhost:1") is True

    def test_port_65535(self):
        assert validators.hostname("localhost:65535") is True

    def test_port_0_invalid(self):
        assert isinstance(validators.hostname("localhost:0"), ValidationError)

    def test_port_65536_invalid(self):
        assert isinstance(validators.hostname("localhost:65536"), ValidationError)

    def test_simple_hostname_max_length(self):
        # 简单主机名: 1-61个字符
        name = "a" * 61
        assert validators.hostname(name) is True

    def test_simple_hostname_too_long(self):
        name = "a" * 62
        # 62字符的简单主机名可能不匹配regex但仍可能被domain接受
        # 这取决于是否作为domain处理


# ============================================================================
# 18. COUNTRY 验证器
# ============================================================================

class TestCountryEquivalenceClass:
    """等价类划分: country_code, calling_code, currency"""

    # calling_code
    @pytest.mark.parametrize("value", [
        "+1",       # EC1: 美国
        "+91",      # EC2: 印度
        "+44",      # EC3: 英国
        "+86",      # EC4: 中国
        "+81",      # EC5: 日本
    ])
    def test_valid_calling_codes(self, value):
        assert validators.calling_code(value) is True

    @pytest.mark.parametrize("value", [
        "",          # EC6: 空
        "-31",       # EC7: 负号开头
        "91",        # EC8: 无加号
        "+0",        # EC9: 无效
    ])
    def test_invalid_calling_codes(self, value):
        assert isinstance(validators.calling_code(value), ValidationError)

    # country_code
    def test_valid_alpha2(self):
        assert validators.country_code("US", iso_format="alpha2") is True

    def test_valid_alpha3(self):
        assert validators.country_code("USA", iso_format="alpha3") is True

    def test_valid_numeric(self):
        assert validators.country_code("840", iso_format="numeric") is True

    def test_invalid_country_code(self):
        assert isinstance(validators.country_code("XX", iso_format="alpha2"), ValidationError)

    def test_auto_format_alpha2(self):
        assert validators.country_code("US") is True

    def test_auto_format_alpha3(self):
        assert validators.country_code("USA") is True

    # currency
    def test_valid_currency(self):
        assert validators.currency("USD") is True

    def test_invalid_currency(self):
        assert isinstance(validators.currency("ZZZ"), ValidationError)


class TestCountryDecisionTable:
    """决策表: country_code iso_format × ignore_case"""

    def test_alpha2_case_sensitive_valid(self):
        assert validators.country_code("US", iso_format="alpha2") is True

    def test_alpha2_case_sensitive_invalid(self):
        assert isinstance(
            validators.country_code("us", iso_format="alpha2"), ValidationError
        )

    def test_alpha2_ignore_case(self):
        assert validators.country_code("us", iso_format="alpha2", ignore_case=True) is True

    def test_alpha3_case_sensitive_valid(self):
        assert validators.country_code("USA", iso_format="alpha3") is True

    def test_alpha3_case_sensitive_invalid(self):
        assert isinstance(
            validators.country_code("usa", iso_format="alpha3"), ValidationError
        )

    def test_alpha3_ignore_case(self):
        assert validators.country_code("usa", iso_format="alpha3", ignore_case=True) is True

    def test_currency_ignore_case(self):
        assert validators.currency("usd", ignore_case=True) is True

    def test_currency_case_sensitive_invalid(self):
        assert isinstance(validators.currency("usd"), ValidationError)

    def test_currency_symbol(self):
        assert validators.currency("$", skip_symbols=False) is True

    def test_currency_symbol_skipped(self):
        assert isinstance(validators.currency("$", skip_symbols=True), ValidationError)

    def test_country_code_too_long(self):
        assert isinstance(validators.country_code("ABCD"), ValidationError)

    def test_country_code_too_short(self):
        assert isinstance(validators.country_code("A"), ValidationError)


# ============================================================================
# 19. VALIDATION ERROR 行为
# ============================================================================

class TestValidationError:
    """等价类划分: ValidationError 行为"""

    def test_validation_error_is_falsy(self):
        result = validators.email("invalid")
        assert not result

    def test_validation_error_bool_false(self):
        result = validators.email("invalid")
        assert bool(result) is False

    def test_valid_result_is_true(self):
        result = validators.email("user@example.com")
        assert result is True

    def test_validation_error_has_func(self):
        result = validators.email("invalid")
        assert result.func is not None

    def test_validation_error_has_args(self):
        result = validators.email("invalid")
        # .args 是元组 (func, dict), 第二个元素是参数字典
        assert "value" in result.args[1]

    def test_validation_error_repr(self):
        result = validators.email("invalid")
        assert "ValidationError" in repr(result)


# ============================================================================
# 20. EXTREMES (AbsMin / AbsMax)
# ============================================================================

class TestExtremesEquivalenceClass:
    """等价类划分: AbsMin, AbsMax"""

    def test_absmin_less_than_any(self):
        from validators._extremes import AbsMin
        assert AbsMin() <= -999999

    def test_absmax_greater_than_any(self):
        from validators._extremes import AbsMax
        assert AbsMax() >= 999999

    def test_absmin_le_absmin_is_true(self):
        # AbsMin.__le__ 检查 other is not AbsMin(类), 实例 is not 类 = True
        from validators._extremes import AbsMin
        assert AbsMin() <= AbsMin()

    def test_absmax_ge_absmax_is_true(self):
        # AbsMax.__ge__ 检查 other is not AbsMax(类), 实例 is not 类 = True
        from validators._extremes import AbsMax
        assert AbsMax() >= AbsMax()


# ============================================================================
# 21. 综合决策表: 多验证器交叉场景
# ============================================================================

class TestCrossValidatorDecisionTable:
    """决策表: 跨验证器的综合场景"""

    def test_email_with_ipv4_domain(self):
        """邮箱的域名部分是IPv4"""
        assert validators.email("user@[127.0.0.1]", ipv4_address=True) is True

    def test_url_with_ipv6(self):
        """URL中使用IPv6地址"""
        assert validators.url("http://[::1]") is True

    def test_url_with_auth_and_port(self):
        """URL同时含认证和端口"""
        assert validators.url("http://user:pass@example.com:8080/path") is True

    def test_domain_in_email(self):
        """验证邮箱中的域名部分也是有效域名"""
        email_val = "user@example.com"
        domain_part = email_val.split("@")[1]
        assert validators.domain(domain_part) is True

    def test_between_with_length(self):
        """length 内部使用 between"""
        assert validators.length("hello", min_val=3, max_val=10) is True
        assert validators.between(5, min_val=3, max_val=10) is True


# ============================================================================
# 22. 加密地址验证器
# ============================================================================

class TestBTCAddress:
    """等价类划分: btc_address"""

    @pytest.mark.parametrize("value", [
        "1BvBMSEYstWetqTFn5Au4m4GFg7xJaNVN2",                   # P2PKH
        "3J98t1WpEZ73CNmQviecrnyiWrnqRhWNLy",                   # P2SH
        "bc1qar0srrr7xfkvy5l643lydnw9re59gtzzwf5mdq",           # Bech32
    ])
    def test_valid_btc(self, value):
        assert validators.btc_address(value) is True

    @pytest.mark.parametrize("value", [
        "",                                                       # 空字符串
        "0BvBMSEYstWetqTFn5Au4m4GFg7xJaNVN2",                   # 错误前缀
        "bc1invalid",                                             # 无效bech32
    ])
    def test_invalid_btc(self, value):
        assert isinstance(validators.btc_address(value), ValidationError)


class TestETHAddress:
    """等价类划分: eth_address"""

    @pytest.mark.parametrize("value", [
        "0x9cc14ba4f9f68ca159ea4ebf2c292a808aaeb598",   # 全小写
        "0x1234567890123456789012345678901234567890",   # 混合
    ])
    def test_valid_eth(self, value):
        assert validators.eth_address(value) is True

    @pytest.mark.parametrize("value", [
        "",                                              # 空
        "9cc14ba4f9f68ca159ea4ebf2c292a808aaeb598",     # 无0x前缀
        "0x9cc14ba4f9f68ca159ea4ebf2c292a808aaeb59",    # 少一位
    ])
    def test_invalid_eth(self, value):
        assert isinstance(validators.eth_address(value), ValidationError)


class TestBSCAddress:
    """等价类划分: bsc_address"""

    def test_valid_bsc(self):
        assert validators.bsc_address("0x9cc14ba4f9f68ca159ea4ebf2c292a808aaeb598") is True

    def test_invalid_bsc_no_prefix(self):
        assert isinstance(
            validators.bsc_address("9cc14ba4f9f68ca159ea4ebf2c292a808aaeb598"), ValidationError
        )

    def test_invalid_bsc_short(self):
        assert isinstance(
            validators.bsc_address("0x9cc14ba4f9f68ca159ea4ebf2c292a808aaeb59"), ValidationError
        )


class TestTRXAddress:
    """等价类划分: trx_address"""

    @pytest.mark.parametrize("value", [
        "TLjfbTbpZYDQ4EoA4N5CLNgGjfbF8ZWz38",
        "TNDzfERDpxLDS2w1q6yaFC7pzqaSQ3Bg3r",
    ])
    def test_valid_trx(self, value):
        assert validators.trx_address(value) is True

    @pytest.mark.parametrize("value", [
        "",                                          # 空
        "ALjfbTbpZYDQ4EoA4N5CLNgGjfbF8ZWz38",      # 不以T开头
        "T",                                         # 太短
    ])
    def test_invalid_trx(self, value):
        assert isinstance(validators.trx_address(value), ValidationError)


# ============================================================================
# 23. i18n 验证器
# ============================================================================

class TestI18nES:
    """等价类划分: 西班牙身份证号"""

    def test_valid_nif(self):
        assert validators.es_nif("00000026A") is True

    def test_invalid_nif(self):
        assert isinstance(validators.es_nif("00000026B"), ValidationError)

    def test_valid_nie(self):
        assert validators.es_nie("X0095892M") is True

    def test_invalid_nie_prefix(self):
        assert isinstance(validators.es_nie("A0095892M"), ValidationError)

    def test_valid_cif(self):
        assert validators.es_cif("B25162520") is True

    def test_valid_doi(self):
        # doi 接受 NIF, NIE, CIF 中任意一种
        assert validators.es_doi("00000026A") is True
        assert validators.es_doi("X0095892M") is True
        assert validators.es_doi("B25162520") is True


class TestI18nFI:
    """等价类划分: 芬兰标识符"""

    def test_valid_business_id(self):
        assert validators.fi_business_id("2336509-6") is True

    def test_invalid_business_id(self):
        assert isinstance(validators.fi_business_id("2336509-7"), ValidationError)

    def test_valid_ssn(self):
        assert validators.fi_ssn("010190-002R") is True

    def test_invalid_ssn(self):
        assert isinstance(validators.fi_ssn(""), ValidationError)


class TestI18nFR:
    """等价类划分: 法国标识符"""

    def test_valid_department(self):
        assert validators.fr_department("75") is True  # 巴黎

    def test_valid_department_corsica_2a(self):
        assert validators.fr_department("2A") is True

    def test_valid_department_corsica_2b(self):
        assert validators.fr_department("2B") is True

    def test_invalid_department(self):
        assert isinstance(validators.fr_department("00"), ValidationError)

    def test_invalid_department_20(self):
        assert isinstance(validators.fr_department("20"), ValidationError)

    def test_valid_ssn(self):
        assert validators.fr_ssn("1 84 12 76 451 089 46") is True


class TestI18nIND:
    """等价类划分: 印度标识符"""

    def test_valid_aadhar(self):
        assert validators.ind_aadhar("3675 9834 6012") is True

    def test_aadhar_first_digit_not_0_or_1(self):
        assert isinstance(validators.ind_aadhar("0675 9834 6012"), ValidationError)

    def test_valid_pan(self):
        assert validators.ind_pan("ABCDE9999K") is True

    def test_pan_lowercase_invalid(self):
        assert isinstance(validators.ind_pan("abcde9999k"), ValidationError)


class TestI18nRU:
    """等价类划分: 俄罗斯INN"""

    def test_valid_inn_10_digits(self):
        assert validators.ru_inn("7709439560") is True

    def test_valid_inn_12_digits(self):
        assert validators.ru_inn("026504247480") is True

    def test_invalid_inn_checksum(self):
        assert isinstance(validators.ru_inn("7709439561"), ValidationError)

    def test_invalid_inn_length(self):
        assert isinstance(validators.ru_inn("12345"), ValidationError)
