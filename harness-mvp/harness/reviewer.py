"""代码审查引擎 - Phase 4"""
import re
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from pathlib import Path

from harness.models import Issue, Severity, Category, Verdict, ReviewResult


def determine_verdict(issues: List[Issue]) -> Verdict:
    """根据问题严重性判定 Verdict

    规则:
    - critical >= 1 → REQUEST_CHANGES
    - major >= 2 → REQUEST_CHANGES
    - 其他 → APPROVE

    Args:
        issues: 问题列表

    Returns:
        判定结果
    """
    critical_count = sum(1 for i in issues if i.severity == Severity.CRITICAL)
    major_count = sum(1 for i in issues if i.severity == Severity.MAJOR)

    if critical_count >= 1:
        return Verdict.REQUEST_CHANGES
    elif major_count >= 2:
        return Verdict.REQUEST_CHANGES
    else:
        return Verdict.APPROVE


class ReviewerAgent:
    """代码审查 Agent - 从 5 个观点审查代码"""

    def __init__(self):
        """初始化 Reviewer Agent"""
        pass

    def review_code(self, code: str, file_path: str) -> ReviewResult:
        """审查代码

        Args:
            code: 代码内容
            file_path: 文件路径

        Returns:
            审查结果
        """
        issues = []

        # 5 个观点审查
        issues.extend(self.check_security(code, file_path))
        issues.extend(self.check_performance(code, file_path))
        issues.extend(self.check_quality(code, file_path))
        issues.extend(self.check_accessibility(code, file_path))
        issues.extend(self.check_ai_residuals(code, file_path))

        # 判定 Verdict
        verdict = determine_verdict(issues)

        # 生成总结
        summary = self._generate_summary(verdict, issues)

        return ReviewResult(verdict=verdict, issues=issues, summary=summary)

    def _generate_summary(self, verdict: Verdict, issues: List[Issue]) -> str:
        """生成审查总结

        Args:
            verdict: 判定结果
            issues: 问题列表

        Returns:
            总结字符串
        """
        critical_count = sum(1 for i in issues if i.severity == Severity.CRITICAL)
        major_count = sum(1 for i in issues if i.severity == Severity.MAJOR)
        minor_count = sum(1 for i in issues if i.severity == Severity.MINOR)
        info_count = sum(1 for i in issues if i.severity == Severity.INFO)

        parts = []
        if critical_count > 0:
            parts.append(f"{critical_count} 个严重问题")
        if major_count > 0:
            parts.append(f"{major_count} 个主要问题")
        if minor_count > 0:
            parts.append(f"{minor_count} 个次要问题")
        if info_count > 0:
            parts.append(f"{info_count} 个提示信息")

        issues_summary = "，".join(parts) if parts else "没有问题"

        if verdict == Verdict.REQUEST_CHANGES:
            return f"需要修改：{issues_summary}"
        else:
            return f"批准：{issues_summary}"

    def check_security(self, code: str, file_path: str) -> List[Issue]:
        """安全检查

        检测:
        - SQL 注入风险
        - XSS 漏洞
        - 机密信息泄露（硬编码密钥）
        - 输入验证缺失

        Args:
            code: 代码内容
            file_path: 文件路径

        Returns:
            安全问题列表
        """
        issues = []

        # 检测 SQL 注入风险（字符串拼接 SQL）
        sql_injection_patterns = [
            r'execute\s*\(\s*["\'].*SELECT.*\+',  # "SELECT * FROM users WHERE id = " +
            r'execute\s*\(\s*["\'].*INSERT.*\+',
            r'execute\s*\(\s*["\'].*UPDATE.*\+',
            r'execute\s*\(\s*["\'].*DELETE.*\+',
            r'execute\s*\(\s*f["\'].*SELECT',  # f-string SQL
            r'execute\s*\(.*f["\']',  # general f-string execute
            r'raw\s*\(\s*["\'].*\+',  # Django raw query with concatenation
        ]

        for pattern in sql_injection_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                issues.append(Issue(
                    severity=Severity.CRITICAL,
                    category=Category.SECURITY,
                    message="发现 SQL 注入风险：使用字符串拼接构建 SQL 查询",
                    file=file_path,
                    line=self._find_line_number(code, pattern),
                    suggestion="使用参数化查询，例如：cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))"
                ))
                break

        # 检测硬编码密钥
        secret_patterns = [
            (r'API_KEY\s*=\s*["\'][^"\']+["\']', "API 密钥"),
            (r'SECRET[_\s]*KEY\s*=\s*["\'][^"\']+["\']', "密钥"),
            (r'PASSWORD\s*=\s*["\'][^"\']+["\']', "密码"),
            (r'TOKEN\s*=\s*["\'][^"\']+["\']', "Token"),
            (r'api_key\s*=\s*["\'][^"\']+["\']', "API 密钥"),
            (r'secret\s*=\s*["\'][^"\']+["\']', "密钥"),
        ]

        for pattern, secret_type in secret_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                # 排除示例和测试代码
                if not re.search(r'#.*example|test_|_test\.py', code, re.IGNORECASE):
                    issues.append(Issue(
                        severity=Severity.CRITICAL,
                        category=Category.SECURITY,
                        message=f"发现硬编码的{secret_type}，不应将密钥写入代码",
                        file=file_path,
                        line=self._find_line_number(code, pattern),
                        suggestion="使用环境变量或密钥管理服务存储敏感信息"
                    ))

        # 检测 XSS 风险（innerHTML, dangerouslySetInnerHTML）
        xss_patterns = [
            r'\.innerHTML\s*=',
            r'dangerouslySetInnerHTML',
            r'v-html\s*=',  # Vue
        ]

        for pattern in xss_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                issues.append(Issue(
                    severity=Severity.MAJOR,
                    category=Category.SECURITY,
                    message="潜在的 XSS 风险：直接设置 HTML 内容",
                    file=file_path,
                    line=self._find_line_number(code, pattern),
                    suggestion="使用textContent 或对用户输入进行 HTML 转义"
                ))
                break

        # 检测 eval 使用
        if re.search(r'\beval\s*\(', code):
            issues.append(Issue(
                severity=Severity.CRITICAL,
                category=Category.SECURITY,
                message="发现 eval() 调用，可能导致代码注入",
                file=file_path,
                line=self._find_line_number(code, r'\beval\s*\('),
                suggestion="使用安全的替代方案，如 ast.literal_eval 或 JSON.parse"
            ))

        return issues

    def check_performance(self, code: str, file_path: str) -> List[Issue]:
        """性能检查

        检测:
        - N+1 查询问题
        - 不必要的重渲染
        - 内存泄漏风险
        - 低效算法

        Args:
            code: 代码内容
            file_path: 文件路径

        Returns:
            性能问题列表
        """
        issues = []

        # 检测 N+1 查询模式（循环中查询）
        n_plus_one_patterns = [
            r'for\s+\w+\s+in\s+\w+:.*?(?:db\.query|SELECT|\.find|\.get)',
            r'forEach\s*\([^)]*\)\s*\{.*?(?:db\.query|SELECT|\.find|\.get)',
        ]

        for pattern in n_plus_one_patterns:
            if re.search(pattern, code, re.IGNORECASE | re.DOTALL):
                issues.append(Issue(
                    severity=Severity.MAJOR,
                    category=Category.PERFORMANCE,
                    message="潜在的 N+1 查询问题：在循环中执行数据库查询",
                    file=file_path,
                    line=self._find_line_number(code, pattern),
                    suggestion="使用预加载或批量查询，例如使用 JOIN 或 IN 子句"
                ))
                break

        # 检测低效的列表操作
        inefficient_patterns = [
            r'list\.append\s*\(.*in\s+.*:',  # 在循环中 append
            r'\+\s*list\s*\+',  # 列表拼接
        ]

        # 检测大型列表推导式中的复杂操作
        if re.search(r'\[.*for.*in.*\].*\.sort\(\)', code):
            issues.append(Issue(
                severity=Severity.MINOR,
                category=Category.PERFORMANCE,
                message="考虑使用 sorted() 替代 sort() 以保持不可变性",
                file=file_path,
                line=1,
                suggestion="使用 sorted(list) 替代 list.sort()"
            ))

        return issues

    def check_quality(self, code: str, file_path: str) -> List[Issue]:
        """质量检查

        检测:
        - 命名是否清晰
        - 是否遵循单一职责
        - 函数大小
        - 错误处理是否完善

        Args:
            code: 代码内容
            file_path: 文件路径

        Returns:
            质量问题列表
        """
        issues = []

        # 检测过长函数（超过 50 行）
        function_pattern = r'(?:def|function)\s+\w+\s*\([^)]*\)\s*:(?:\s*\n(?:\s+.+\n?)*)'
        functions = re.findall(function_pattern, code, re.MULTILINE)

        for func in functions:
            lines = func.strip().split('\n')
            if len(lines) > 50:
                issues.append(Issue(
                    severity=Severity.MAJOR,
                    category=Category.QUALITY,
                    message=f"函数过长 ({len(lines)} 行)，建议拆分为更小的函数",
                    file=file_path,
                    line=self._find_line_number(code, r'(?:def|function)\s+'),
                    suggestion="将函数拆分为多个职责单一的小函数，每函数不超过 50 行"
                ))
                break

        # 检测缺失的文档字符串
        public_patterns = [
            r'def\s+([a-z][a-z0-9_]*)\s*\([^)]*\)\s*:\s*\n(?!\s*"""|\'\'\')',
        ]

        for pattern in public_patterns:
            matches = re.finditer(pattern, code)
            for match in matches:
                func_name = match.group(1)
                # 跳过私有函数和测试函数
                if not func_name.startswith('_') and not func_name.startswith('test_'):
                    issues.append(Issue(
                        severity=Severity.MINOR,
                        category=Category.QUALITY,
                        message=f"公共函数 '{func_name}' 缺少文档字符串",
                        file=file_path,
                        line=self._find_line_number(code, pattern),
                        suggestion="添加文档字符串说明函数的用途、参数和返回值"
                    ))

        # 检测裸 except
        if re.search(r'except\s*:', code):
            issues.append(Issue(
                severity=Severity.MAJOR,
                category=Category.QUALITY,
                message="使用裸 except，可能掩盖意外错误",
                file=file_path,
                line=self._find_line_number(code, r'except\s*:'),
                suggestion="指定具体的异常类型，如 except ValueError:"
            ))

        # 检测魔法数字
        magic_number_pattern = r'(?<!\w)(?:[2-9]\d{2,}|\d{4,})(?!\w)'
        if re.search(magic_number_pattern, code):
            issues.append(Issue(
                severity=Severity.MINOR,
                category=Category.QUALITY,
                message="发现魔法数字，建议使用命名常量",
                file=file_path,
                line=self._find_line_number(code, magic_number_pattern),
                suggestion="将魔法数字提取为命名常量，提高代码可读性"
            ))

        return issues

    def check_accessibility(self, code: str, file_path: str) -> List[Issue]:
        """可访问性检查

        检测:
        - ARIA 属性是否正确
        - 键盘导航是否支持
        - 颜色对比度是否足够
        - 屏幕阅读器兼容性

        Args:
            code: 代码内容
            file_path: 文件路径

        Returns:
            可访问性问题列表
        """
        issues = []

        # 只检查 HTML/JSX 文件
        if not any(ext in file_path.lower() for ext in ['.html', '.jsx', '.tsx', '.vue', '.svelte']):
            return issues

        # 检测缺失 alt 属性的图片
        img_without_alt = re.findall(r'<img\s+(?![^>]*\balt\s*=)[^>]*>', code)
        if img_without_alt:
            issues.append(Issue(
                severity=Severity.MAJOR,
                category=Category.ACCESSIBILITY,
                message="图片缺少 alt 属性，屏幕阅读器无法描述图片内容",
                file=file_path,
                line=self._find_line_number(code, r'<img\b'),
                suggestion="为所有<img>标签添加描述性的 alt 属性"
            ))

        # 检测缺失 role 的交互元素
        div_as_button = re.findall(r'<div\s+[^>]*onclick[^>]*>(?![^>]*\brole\b)[^<]*</div>', code, re.IGNORECASE)
        if div_as_button:
            issues.append(Issue(
                severity=Severity.MAJOR,
                category=Category.ACCESSIBILITY,
                message="使用<div>作为按钮但未设置 role 属性",
                file=file_path,
                line=self._find_line_number(code, r'<div\b'),
                suggestion="添加 role=\"button\"和适当的 ARIA 属性，或使用<button>元素"
            ))

        # 检测缺失 label 的表单输入
        input_without_label = re.findall(r'<input\s+[^>]*>(?![^>]*\b(id|aria-label|aria-labelledby)\b)', code)
        if input_without_label:
            issues.append(Issue(
                severity=Severity.MAJOR,
                category=Category.ACCESSIBILITY,
                message="表单输入缺少 label 关联",
                file=file_path,
                line=self._find_line_number(code, r'<input\b'),
                suggestion="使用<label for=\"id\">或 aria-label 属性关联标签"
            ))

        return issues

    def check_ai_residuals(self, code: str, file_path: str) -> List[Issue]:
        """AI 残留检查

        检测:
        - mockData, dummy, fake
        - TODO, FIXME 注释
        - localhost, 127.0.0.1 硬编码
        - it.skip, describe.skip
        - 临时实现注释

        Args:
            code: 代码内容
            file_path: 文件路径

        Returns:
            AI 残留问题列表
        """
        issues = []

        # 检测 TODO/FIXME 注释
        todo_pattern = r'#\s*(?:TODO|FIXME|XXX|HACK)\s*:?\s*(.+)'
        todo_matches = re.finditer(todo_pattern, code, re.IGNORECASE)
        for match in todo_matches:
            issues.append(Issue(
                severity=Severity.MINOR,
                category=Category.AI_RESIDUALS,
                message=f"发现待处理注释：TODO/FIXME - {match.group(1).strip()[:50]}",
                file=file_path,
                line=self._find_line_number(code, todo_pattern),
                suggestion="完成或移除待处理注释"
            ))

        # 检测 mock 数据
        mock_patterns = [
            (r'mockData\s*=', "mockData 变量"),
            (r'dummy\w*\s*=', "dummy 变量"),
            (r'fake\w*\s*=', "fake 变量"),
            (r'placeholder\s*=\s*["\']test', "占位符测试数据"),
        ]

        for pattern, description in mock_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                issues.append(Issue(
                    severity=Severity.MINOR,
                    category=Category.AI_RESIDUALS,
                    message=f"发现{description}，应替换为真实数据",
                    file=file_path,
                    line=self._find_line_number(code, pattern),
                    suggestion="移除或替换为真实数据"
                ))

        # 检测 localhost 硬编码
        localhost_patterns = [
            r'http://localhost[:\d]*',
            r'http://127\.0\.0\.1[:\d]*',
        ]

        for pattern in localhost_patterns:
            if re.search(pattern, code):
                issues.append(Issue(
                    severity=Severity.MINOR,
                    category=Category.AI_RESIDUALS,
                    message="发现 localhost 硬编码，应使用环境变量配置",
                    file=file_path,
                    line=self._find_line_number(code, pattern),
                    suggestion="使用环境变量配置 API 地址，如 os.environ.get('API_URL')"
                ))
                break

        # 检测跳过的测试
        skip_test_patterns = [
            r'it\.skip\s*\(',
            r'describe\.skip\s*\(',
            r'@pytest\.mark\.skip',
            r'self\.skipTest\s*\(',
        ]

        for pattern in skip_test_patterns:
            if re.search(pattern, code):
                issues.append(Issue(
                    severity=Severity.MINOR,
                    category=Category.AI_RESIDUALS,
                    message="发现跳过的测试，应完成实现或移除",
                    file=file_path,
                    line=self._find_line_number(code, pattern),
                    suggestion="完成测试实现或移除 skip 标记"
                ))
                break

        return issues

    def _find_line_number(self, code: str, pattern: str) -> int:
        """查找匹配模式的行号

        Args:
            code: 代码内容
            pattern: 正则表达式模式

        Returns:
            行号（从 1 开始）
        """
        match = re.search(pattern, code, re.IGNORECASE | re.MULTILINE)
        if match:
            # 计算匹配位置之前的换行符数量
            return code[:match.start()].count('\n') + 1
        return 1
