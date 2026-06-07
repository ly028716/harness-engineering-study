"""测试自定义审查规则功能"""
import json
import pytest
import tempfile
from pathlib import Path

from harness.models import CustomReviewRule, Severity, Category, Issue
from harness.custom_rules import (
    CustomRuleStore, CustomRuleEngine,
    CustomRuleError, RuleNotFoundError, RuleNameConflictError,
)
from harness.reviewer import ReviewerAgent


# ===== 测试 CustomReviewRule 数据模型 =====

class TestCustomReviewRule:
    """测试 CustomReviewRule 数据模型"""

    def test_create_rule(self):
        """测试创建自定义规则"""
        rule = CustomReviewRule(
            name="no_print",
            pattern=r"print\s*\(",
            message="禁止使用 print",
            suggestion="使用 logging 模块",
        )
        assert rule.name == "no_print"
        assert rule.pattern == r"print\s*\("
        assert rule.message == "禁止使用 print"
        assert rule.suggestion == "使用 logging 模块"
        assert rule.severity == Severity.MAJOR
        assert rule.category == Category.QUALITY
        assert rule.file_pattern == "*.py"
        assert rule.enabled is True
        assert rule.description == ""

    def test_create_full_rule(self):
        """测试创建完整的自定义规则"""
        rule = CustomReviewRule(
            name="no_eval",
            pattern=r"\beval\s*\(",
            message="禁止使用 eval",
            suggestion="使用 ast.literal_eval",
            severity=Severity.CRITICAL,
            category=Category.SECURITY,
            file_pattern="*.py",
            enabled=True,
            description="防止代码注入",
        )
        assert rule.severity == Severity.CRITICAL
        assert rule.category == Category.SECURITY
        assert rule.file_pattern == "*.py"
        assert rule.description == "防止代码注入"

    def test_matches_file(self):
        """测试文件匹配"""
        rule = CustomReviewRule(name="test", pattern=r"test", message="test", file_pattern="*.py")
        assert rule.matches_file("src/main.py") is True
        assert rule.matches_file("src/test.js") is False
        assert rule.matches_file("test.ts") is False

    def test_matches_file_glob_star(self):
        """测试通配符文件匹配"""
        rule = CustomReviewRule(name="test", pattern=r"test", message="test", file_pattern="*")
        assert rule.matches_file("any/file.txt") is True
        assert rule.matches_file("noext") is True

    def test_matches_file_specific(self):
        """测试特定文件匹配"""
        rule = CustomReviewRule(
            name="test", pattern=r"test", message="test",
            file_pattern="src/*.py",
        )
        assert rule.matches_file("src/main.py") is True
        assert rule.matches_file("src/utils.py") is True
        assert rule.matches_file("tests/test_main.py") is False

    def test_to_dict(self):
        """测试序列化"""
        rule = CustomReviewRule(
            name="no_print",
            pattern=r"print\s*\(",
            message="禁止使用 print",
            suggestion="使用 logging 模块",
            severity=Severity.MAJOR,
            category=Category.QUALITY,
            file_pattern="*.py",
            enabled=True,
            description="测试规则",
        )
        data = rule.to_dict()
        assert data["name"] == "no_print"
        assert data["pattern"] == r"print\s*\("
        assert data["severity"] == "MAJOR"
        assert data["category"] == "QUALITY"
        assert data["enabled"] is True

    def test_from_dict(self):
        """测试反序列化"""
        data = {
            "name": "no_eval",
            "pattern": r"\beval\s*\(",
            "message": "禁止 eval",
            "suggestion": "使用替代方案",
            "severity": "CRITICAL",
            "category": "SECURITY",
            "file_pattern": "*.py",
            "enabled": False,
            "description": "安全规则",
        }
        rule = CustomReviewRule.from_dict(data)
        assert rule.name == "no_eval"
        assert rule.severity == Severity.CRITICAL
        assert rule.category == Category.SECURITY
        assert rule.enabled is False
        assert rule.description == "安全规则"

    def test_from_dict_minimal(self):
        """测试从最小字典反序列化"""
        data = {
            "name": "minimal",
            "pattern": r"test",
            "message": "test",
        }
        rule = CustomReviewRule.from_dict(data)
        assert rule.name == "minimal"
        assert rule.severity == Severity.MAJOR
        assert rule.category == Category.QUALITY
        assert rule.enabled is True
        assert rule.suggestion == ""

    def test_str_representation(self):
        """测试字符串表示"""
        enabled_rule = CustomReviewRule(name="r1", pattern=r"a", message="a")
        assert "✓" in str(enabled_rule)
        assert "r1" in str(enabled_rule)

        disabled_rule = CustomReviewRule(name="r2", pattern=r"a", message="a", enabled=False)
        assert "✗" in str(disabled_rule)


# ===== 测试 CustomRuleStore =====

class TestCustomRuleStore:
    """测试自定义规则存储"""

    @pytest.fixture
    def harness_dir(self):
        """创建临时 .harness 目录"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir) / ".harness"

    def test_load_empty(self, harness_dir):
        """测试加载空存储"""
        harness_dir.mkdir(parents=True)
        store = CustomRuleStore(harness_dir)
        assert store.list_rules() == []

    def test_add_and_list(self, harness_dir):
        """测试添加和列出规则"""
        harness_dir.mkdir(parents=True)
        store = CustomRuleStore(harness_dir)

        rule = CustomReviewRule(
            name="no_print",
            pattern=r"print\s*\(",
            message="禁止使用 print",
        )
        store.add_rule(rule)
        rules = store.list_rules()
        assert len(rules) == 1
        assert rules[0].name == "no_print"

    def test_add_duplicate(self, harness_dir):
        """测试添加重复规则"""
        harness_dir.mkdir(parents=True)
        store = CustomRuleStore(harness_dir)

        rule1 = CustomReviewRule(name="dup", pattern=r"a", message="a")
        rule2 = CustomReviewRule(name="dup", pattern=r"b", message="b")
        store.add_rule(rule1)
        with pytest.raises(RuleNameConflictError):
            store.add_rule(rule2)

    def test_get_rule(self, harness_dir):
        """测试获取规则"""
        harness_dir.mkdir(parents=True)
        store = CustomRuleStore(harness_dir)

        rule = CustomReviewRule(name="my_rule", pattern=r"test", message="test")
        store.add_rule(rule)

        found = store.get_rule("my_rule")
        assert found is not None
        assert found.name == "my_rule"

        assert store.get_rule("nonexistent") is None

    def test_remove_rule(self, harness_dir):
        """测试删除规则"""
        harness_dir.mkdir(parents=True)
        store = CustomRuleStore(harness_dir)

        rule = CustomReviewRule(name="remove_me", pattern=r"a", message="a")
        store.add_rule(rule)
        assert len(store.list_rules()) == 1

        store.remove_rule("remove_me")
        assert len(store.list_rules()) == 0

    def test_remove_nonexistent(self, harness_dir):
        """测试删除不存在的规则"""
        harness_dir.mkdir(parents=True)
        store = CustomRuleStore(harness_dir)
        with pytest.raises(RuleNotFoundError):
            store.remove_rule("ghost")

    def test_toggle_rule(self, harness_dir):
        """测试切换规则状态"""
        harness_dir.mkdir(parents=True)
        store = CustomRuleStore(harness_dir)

        rule = CustomReviewRule(name="tog", pattern=r"a", message="a", enabled=True)
        store.add_rule(rule)

        # 切换到禁用
        new_state = store.toggle_rule("tog")
        assert new_state is False
        assert store.get_rule("tog").enabled is False

        # 再切换回启用
        new_state = store.toggle_rule("tog")
        assert new_state is True
        assert store.get_rule("tog").enabled is True

    def test_toggle_nonexistent(self, harness_dir):
        """测试切换不存在的规则"""
        harness_dir.mkdir(parents=True)
        store = CustomRuleStore(harness_dir)
        with pytest.raises(RuleNotFoundError):
            store.toggle_rule("ghost")

    def test_list_filter_by_category(self, harness_dir):
        """测试按类别过滤规则"""
        harness_dir.mkdir(parents=True)
        store = CustomRuleStore(harness_dir)

        store.add_rule(CustomReviewRule(name="sec1", pattern=r"a", message="a",
                                        category=Category.SECURITY))
        store.add_rule(CustomReviewRule(name="sec2", pattern=r"b", message="b",
                                        category=Category.SECURITY))
        store.add_rule(CustomReviewRule(name="qual1", pattern=r"c", message="c",
                                        category=Category.QUALITY))

        sec_rules = store.list_rules(category=Category.SECURITY)
        assert len(sec_rules) == 2

        qual_rules = store.list_rules(category=Category.QUALITY)
        assert len(qual_rules) == 1

    def test_persistence(self, harness_dir):
        """测试持久化"""
        harness_dir.mkdir(parents=True)

        # 写入
        store1 = CustomRuleStore(harness_dir)
        store1.add_rule(CustomReviewRule(name="persist", pattern=r"x", message="x"))
        assert len(store1.list_rules()) == 1

        # 新实例读取
        store2 = CustomRuleStore(harness_dir)
        assert len(store2.list_rules()) == 1
        assert store2.get_rule("persist") is not None

    def test_corrupted_file(self, harness_dir):
        """测试损坏的文件"""
        harness_dir.mkdir(parents=True)
        rules_file = harness_dir / "custom_rules.json"
        rules_file.write_text("{invalid json}", encoding="utf-8")

        with pytest.raises(CustomRuleError):
            CustomRuleStore(harness_dir)


# ===== 测试 CustomRuleEngine =====

class TestCustomRuleEngine:
    """测试自定义规则引擎"""

    @pytest.fixture
    def store(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            d = Path(tmpdir) / ".harness"
            d.mkdir(parents=True)
            yield CustomRuleStore(d)

    def test_no_rules(self, store):
        """测试无规则时返回空列表"""
        engine = CustomRuleEngine(store)
        issues = engine.evaluate("print('hello')", "test.py")
        assert issues == []

    def test_simple_match(self, store):
        """测试简单正则匹配"""
        store.add_rule(CustomReviewRule(
            name="no_print",
            pattern=r"print\s*\(",
            message="禁止使用 print",
            severity=Severity.MAJOR,
            category=Category.QUALITY,
        ))
        engine = CustomRuleEngine(store)
        issues = engine.evaluate("print('hello')", "test.py")
        assert len(issues) == 1
        assert issues[0].message == "禁止使用 print"
        assert issues[0].severity == Severity.MAJOR
        assert issues[0].category == Category.QUALITY
        assert issues[0].file == "test.py"
        assert issues[0].line == 1

    def test_disabled_rule_skipped(self, store):
        """测试禁用的规则不触发"""
        store.add_rule(CustomReviewRule(
            name="no_print",
            pattern=r"print\s*\(",
            message="禁止使用 print",
            enabled=False,
        ))
        engine = CustomRuleEngine(store)
        issues = engine.evaluate("print('hello')", "test.py")
        assert issues == []

    def test_file_pattern_filter(self, store):
        """测试文件模式过滤"""
        store.add_rule(CustomReviewRule(
            name="js_only",
            pattern=r"console\.log",
            message="禁止 console.log",
            file_pattern="*.js",
        ))
        engine = CustomRuleEngine(store)

        # js 文件应匹配
        js_issues = engine.evaluate("console.log('test')", "app.js")
        assert len(js_issues) == 1

        # py 文件不应匹配
        py_issues = engine.evaluate("console.log('test')", "app.py")
        assert len(py_issues) == 0

    def test_multiple_matches(self, store):
        """测试匹配多次"""
        store.add_rule(CustomReviewRule(
            name="no_todo",
            pattern=r"#\s*TODO",
            message="不应有 TODO 残留",
        ))
        engine = CustomRuleEngine(store)
        code = "# TODO: fix this\nprint('ok')\n# TODO: also this"
        issues = engine.evaluate(code, "test.py")
        assert len(issues) == 2
        assert issues[0].line == 1
        assert issues[1].line == 3

    def test_severity_and_category_carried(self, store):
        """测试规则中的 severity/category 正确传递到 issue"""
        store.add_rule(CustomReviewRule(
            name="hardcoded_key",
            pattern=r"API_KEY\s*=",
            message="发现硬编码密钥",
            severity=Severity.CRITICAL,
            category=Category.SECURITY,
            suggestion="使用环境变量",
        ))
        engine = CustomRuleEngine(store)
        issues = engine.evaluate("API_KEY = 'abc123'", "config.py")
        assert len(issues) == 1
        assert issues[0].severity == Severity.CRITICAL
        assert issues[0].category == Category.SECURITY
        assert issues[0].suggestion == "使用环境变量"

    def test_invalid_regex_skipped(self, store):
        """测试无效正则静默跳过"""
        store.add_rule(CustomReviewRule(
            name="bad_regex",
            pattern=r"[invalid",
            message="无效正则",
        ))
        engine = CustomRuleEngine(store)
        # 不应该抛出异常
        issues = engine.evaluate("just text", "test.py")
        assert issues == []

    def test_mixed_rules(self, store):
        """测试混合规则（启用+禁用）"""
        store.add_rule(CustomReviewRule(
            name="enabled_rule",
            pattern=r"print",
            message="启用规则",
            enabled=True,
        ))
        store.add_rule(CustomReviewRule(
            name="disabled_rule",
            pattern=r"print",
            message="禁用规则",
            enabled=False,
        ))
        engine = CustomRuleEngine(store)
        issues = engine.evaluate("print('hi')", "test.py")
        # 只有启用规则会触发
        assert len(issues) >= 1
        # 所有问题都应该来自启用规则
        for issue in issues:
            assert issue.message == "启用规则"


# ===== 测试 ReviewerAgent 集成 =====

class TestReviewerAgentWithCustomRules:
    """测试自定义规则与审查引擎的集成"""

    @pytest.fixture
    def store(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            d = Path(tmpdir) / ".harness"
            d.mkdir(parents=True)
            yield CustomRuleStore(d)

    def test_no_rule_engine(self):
        """测试未配置规则引擎时的行为"""
        agent = ReviewerAgent()  # 不传 rule_engine
        result = agent.review_code("print('hello')", "test.py")
        assert result is not None
        # 应该有内置的 quality 检查（如缺少 docstring）但没有自定义规则
        assert isinstance(result.issues, list)

    def test_custom_rules_integrated(self, store):
        """测试自定义规则集成到审查流程"""
        store.add_rule(CustomReviewRule(
            name="no_print",
            pattern=r"print\s*\(",
            message="禁止使用 print",
            severity=Severity.MAJOR,
            category=Category.QUALITY,
        ))
        engine = CustomRuleEngine(store)
        agent = ReviewerAgent(rule_engine=engine)

        code = """def greet(name):
    print(f"Hello, {name}")
    return name
"""
        result = agent.review_code(code, "test.py")
        # 应该包含自定义规则的问题
        custom_issues = [i for i in result.issues if i.message == "禁止使用 print"]
        assert len(custom_issues) == 1

    def test_custom_rule_affects_verdict(self, store):
        """测试自定义规则影响最终判定"""
        store.add_rule(CustomReviewRule(
            name="critical_issue",
            pattern=r"eval\s*\(",
            message="禁止使用 eval",
            severity=Severity.CRITICAL,
            category=Category.SECURITY,
        ))
        engine = CustomRuleEngine(store)
        agent = ReviewerAgent(rule_engine=engine)

        code = "result = eval(user_input)"
        result = agent.review_code(code, "test.py")
        assert result.verdict.value == "REQUEST_CHANGES"

    def test_disabled_custom_rule_not_in_verdict(self, store):
        """测试禁用的自定义规则不影响判定"""
        store.add_rule(CustomReviewRule(
            name="critical_but_disabled",
            pattern=r"something",
            message="禁止的规则",
            severity=Severity.CRITICAL,
            enabled=False,
        ))
        engine = CustomRuleEngine(store)
        agent = ReviewerAgent(rule_engine=engine)

        code = "x = something"
        result = agent.review_code(code, "test.py")
        # 禁用规则不应产生问题
        custom_issues = [i for i in result.issues if i.message == "禁止的规则"]
        assert len(custom_issues) == 0

    def test_file_pattern_excludes_custom_rule(self, store):
        """测试文件模式排除"""
        store.add_rule(CustomReviewRule(
            name="js_only",
            pattern=r"console\.log",
            message="禁止 console.log",
            file_pattern="*.js",
        ))
        engine = CustomRuleEngine(store)
        agent = ReviewerAgent(rule_engine=engine)

        code = "console.log('test')"

        # py 文件不受影响
        py_result = agent.review_code(code, "test.py")
        py_custom = [i for i in py_result.issues if i.message == "禁止 console.log"]
        assert len(py_custom) == 0

        # js 文件受影响
        js_result = agent.review_code(code, "test.js")
        js_custom = [i for i in js_result.issues if i.message == "禁止 console.log"]
        assert len(js_custom) == 1
