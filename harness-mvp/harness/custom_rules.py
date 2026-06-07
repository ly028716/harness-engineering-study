"""自定义审查规则管理 - 加载/保存/CRUD"""
import json
import re
from copy import deepcopy
from pathlib import Path
from typing import List, Dict, Any, Optional

from harness.models import CustomReviewRule, Issue, Severity, Category


DEFAULT_RULES_FILE = "custom_rules.json"


class CustomRuleError(Exception):
    """自定义规则相关错误"""
    pass


class RuleNotFoundError(CustomRuleError):
    """规则未找到"""
    pass


class RuleNameConflictError(CustomRuleError):
    """规则名称冲突"""
    pass


class CustomRuleStore:
    """自定义规则存储 - 管理 .harness/custom_rules.json 的增删改查"""

    def __init__(self, harness_dir: Path):
        """初始化规则存储

        Args:
            harness_dir: .harness 目录路径
        """
        self.rules_file = Path(harness_dir) / DEFAULT_RULES_FILE
        self._rules: List[CustomReviewRule] = []
        self._load()

    def _load(self):
        """从文件加载规则"""
        if not self.rules_file.exists():
            self._rules = []
            return

        try:
            with open(self.rules_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            self._rules = [CustomReviewRule.from_dict(item) for item in data]
        except (json.JSONDecodeError, KeyError) as e:
            raise CustomRuleError(f"解析规则文件失败: {e}")

    def save(self):
        """保存规则到文件"""
        self.rules_file.parent.mkdir(parents=True, exist_ok=True)
        data = [rule.to_dict() for rule in self._rules]
        with open(self.rules_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def list_rules(self, category: Optional[Category] = None) -> List[CustomReviewRule]:
        """列出所有规则（可按类别过滤）

        Args:
            category: 可选的类别过滤器

        Returns:
            规则列表
        """
        if category:
            return [r for r in self._rules if r.category == category]
        return list(self._rules)

    def get_rule(self, name: str) -> Optional[CustomReviewRule]:
        """按名称获取规则

        Args:
            name: 规则名称

        Returns:
            规则对象，未找到时返回 None
        """
        for rule in self._rules:
            if rule.name == name:
                return rule
        return None

    def add_rule(self, rule: CustomReviewRule):
        """添加规则

        Args:
            rule: 规则对象

        Raises:
            RuleNameConflictError: 规则名称已存在
        """
        if self.get_rule(rule.name):
            raise RuleNameConflictError(f"规则 '{rule.name}' 已存在")
        self._rules.append(rule)
        self.save()

    def remove_rule(self, name: str):
        """删除规则

        Args:
            name: 规则名称

        Raises:
            RuleNotFoundError: 规则未找到
        """
        rule = self.get_rule(name)
        if not rule:
            raise RuleNotFoundError(f"未找到规则 '{name}'")
        self._rules.remove(rule)
        self.save()

    def toggle_rule(self, name: str) -> bool:
        """切换规则启用/禁用状态

        Args:
            name: 规则名称

        Returns:
            切换后的状态（True=启用）

        Raises:
            RuleNotFoundError: 规则未找到
        """
        rule = self.get_rule(name)
        if not rule:
            raise RuleNotFoundError(f"未找到规则 '{name}'")
        rule.enabled = not rule.enabled
        self.save()
        return rule.enabled


class CustomRuleEngine:
    """自定义规则引擎 - 执行规则匹配"""

    def __init__(self, store: CustomRuleStore):
        """初始化规则引擎

        Args:
            store: 规则存储实例
        """
        self.store = store

    def evaluate(self, code: str, file_path: str) -> List[Issue]:
        """对代码执行所有启用的自定义规则

        Args:
            code: 代码内容
            file_path: 文件路径

        Returns:
            匹配到的问题列表
        """
        issues: List[Issue] = []

        for rule in self.store.list_rules():
            if not rule.enabled:
                continue
            if not rule.matches_file(file_path):
                continue

            try:
                matches = re.finditer(rule.pattern, code)
                for match in matches:
                    line_number = code[:match.start()].count('\n') + 1
                    issues.append(Issue(
                        severity=deepcopy(rule.severity),
                        category=deepcopy(rule.category),
                        message=rule.message,
                        file=file_path,
                        line=line_number,
                        suggestion=rule.suggestion if rule.suggestion else None,
                    ))
            except re.error:
                # 无效正则静默跳过
                continue

        return issues
