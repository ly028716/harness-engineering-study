"""Planner Agent - Phase 2"""
import re
from typing import List, Dict, Any, Tuple
from harness.models import Task, Priority


class PlanGenerator:
    """计划生成器 - 基于规则的任务生成"""

    # 关键词到优先级的映射
    PRIORITY_KEYWORDS = {
        "REQUIRED": ["核心", "必须", "基础", "主要", "关键", "essential", "core", "must", "main", "critical"],
        "RECOMMENDED": ["推荐", "重要", "应该", "recommended", "important", "should"],
        "OPTIONAL": ["可选", "最好", "如果时间", "optional", "nice", "if time"]
    }

    # 复杂度关键词
    COMPLEXITY_KEYWORDS = [
        ("完整", 2), ("系统", 2), ("复杂", 2), ("集成", 2),
        ("简单", -1), ("基础", -1), ("添加", -1), ("修改", -1),
        ("实现", 1), ("设计", 1), ("重构", 1), ("优化", 1)
    ]

    def generate_task(
        self,
        title: str,
        description: str = "",
        priority: str = "REQUIRED",
        estimated_effort: int = None
    ) -> Dict[str, Any]:
        """生成任务字典

        Args:
            title: 任务标题
            description: 任务描述
            priority: 优先级
            estimated_effort: 估算工作量

        Returns:
            任务字典
        """
        return {
            "title": title,
            "description": description,
            "priority": priority,
            "estimated_effort": estimated_effort or self.estimate_effort(description or title)
        }

    def parse_user_input(self, user_input: str) -> Dict[str, str]:
        """解析用户输入

        Args:
            user_input: 用户输入文本

        Returns:
            解析结果
        """
        # 提取目标
        goal_patterns = [
            r"我想 (?:要做 | 构建 | 创建 | 实现|完成) (.+?)(?:。|$)",
            r"(?:目标是 | 目的是) (.+?)(?:。|$)",
            r"(?:做一个 | 做一个 | 开发|编写) (.+?)(?:。|$)"
        ]

        goal = user_input
        for pattern in goal_patterns:
            match = re.search(pattern, user_input)
            if match:
                goal = match.group(1).strip()
                break

        return {"goal": goal}

    def extract_keywords(self, text: str) -> List[str]:
        """提取关键词

        Args:
            text: 输入文本

        Returns:
            关键词列表
        """
        # 简单的中文分词（基于常见技术词汇）
        tech_keywords = [
            "API", "REST", "GraphQL", "JWT", "OAuth", "认证", "授权",
            "登录", "注册", "用户", "数据库", "缓存", "消息队列",
            "前端", "后端", "移动端", "桌面端", "Web", "小程序",
            "Vue", "React", "Angular", "Django", "Flask", "FastAPI",
            "MySQL", "PostgreSQL", "MongoDB", "Redis", "Elasticsearch"
        ]

        keywords = []
        for keyword in tech_keywords:
            if keyword in text:
                keywords.append(keyword)

        return keywords

    def categorize_priority(self, description: str) -> str:
        """分类优先级

        Args:
            description: 任务描述

        Returns:
            优先级字符串
        """
        description_lower = description.lower()

        for priority, keywords in self.PRIORITY_KEYWORDS.items():
            for keyword in keywords:
                if keyword.lower() in description_lower:
                    return priority

        # 默认：如果没有明确关键词，根据内容判断
        if any(kw in description_lower for kw in ["核心", "基础", "必须"]):
            return "REQUIRED"
        elif any(kw in description_lower for kw in ["可选", "如果"]):
            return "OPTIONAL"
        else:
            return "RECOMMENDED"

    def estimate_effort(self, description: str) -> int:
        """估算工作量

        Args:
            description: 任务描述

        Returns:
            工作量估算 (1-5)
        """
        base_effort = 2
        description_lower = description.lower()

        for keyword, modifier in self.COMPLEXITY_KEYWORDS:
            if keyword.lower() in description_lower:
                base_effort += modifier

        # 根据长度调整
        word_count = len(description)
        if word_count > 50:
            base_effort += 1
        if word_count > 100:
            base_effort += 1

        # 限制在 1-5 范围
        return max(1, min(5, base_effort))

    def generate_acceptance_criteria(self, title: str, description: str) -> List[str]:
        """生成验收标准

        Args:
            title: 任务标题
            description: 任务描述

        Returns:
            验收标准列表
        """
        criteria = []

        # 基于常见模式的验收标准
        if any(kw in title for kw in ["接口", "API", "端点"]):
            criteria.append("HTTP 状态码正确")
            criteria.append("请求参数验证通过")
            criteria.append("响应格式符合预期")

        if any(kw in title for kw in ["登录", "认证", "授权"]):
            criteria.append("成功时返回有效 token")
            criteria.append("失败时返回适当错误信息")
            criteria.append("密码加密存储")

        if any(kw in title for kw in ["数据库", "模型", "表"]):
            criteria.append("数据库迁移测试通过")
            criteria.append("字段约束正确")

        # 如果没有自动生成，返回通用标准
        if not criteria:
            criteria = [
                "功能按预期工作",
                "通过单元测试",
                "代码符合规范"
            ]

        return criteria


class PlannerAgent:
    """Planner Agent - 计划生成和管理"""

    def __init__(self):
        """初始化 Planner Agent"""
        self.generator = PlanGenerator()

    def collect_requirements(
        self,
        goal: str,
        key_features: List[str] = None,
        constraints: List[str] = None
    ) -> Dict[str, Any]:
        """收集需求

        Args:
            goal: 目标
            key_features: 关键功能列表
            constraints: 约束条件列表

        Returns:
            需求字典
        """
        return {
            "goal": goal,
            "key_features": key_features or [],
            "constraints": constraints or []
        }

    def break_down_tasks(
        self,
        goal: str,
        features: List[str]
    ) -> List[Dict[str, Any]]:
        """分解任务

        Args:
            goal: 目标
            features: 功能列表

        Returns:
            任务列表
        """
        tasks = []
        for i, feature in enumerate(features, 1):
            task = self.generator.generate_task(
                title=f"实现{feature}",
                description=f"{goal} - {feature}功能",
                priority="REQUIRED"
            )
            task["id"] = i
            task["dependencies"] = []
            tasks.append(task)

        return tasks

    def generate_plan(
        self,
        goal: str,
        features: List[str],
        priority: str = "REQUIRED"
    ) -> Dict[str, Any]:
        """生成计划

        Args:
            goal: 目标
            features: 功能列表
            priority: 优先级

        Returns:
            计划字典
        """
        tasks = self.break_down_tasks(goal, features)

        # 根据优先级重新分类
        for task in tasks:
            task["priority"] = self.generator.categorize_priority(
                f"{priority} {task['title']}"
            )

        return {
            "goal": goal,
            "tasks": tasks
        }

    def validate_plan(self, plan: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """验证计划

        Args:
            plan: 计划字典

        Returns:
            (是否有效，问题列表)
        """
        issues = []
        tasks = plan.get("tasks", [])

        # 检查任务 ID 唯一性
        task_ids = [t.get("id") for t in tasks]
        if len(task_ids) != len(set(task_ids)):
            issues.append("存在重复的任务 ID")

        # 检查依赖关系
        for task in tasks:
            deps = task.get("dependencies", [])
            for dep_id in deps:
                if dep_id not in task_ids:
                    issues.append(f"任务 {task['id']} 依赖不存在的任务 {dep_id}")

        # 检查循环依赖
        if self._has_circular_dependency(tasks):
            issues.append("检测到循环依赖")

        return len(issues) == 0, issues

    def _has_circular_dependency(self, tasks: List[Dict[str, Any]]) -> bool:
        """检查循环依赖

        Args:
            tasks: 任务列表

        Returns:
            是否存在循环依赖
        """
        # 构建依赖图
        graph = {t["id"]: t.get("dependencies", []) for t in tasks}

        def has_cycle(node: int, visited: set, rec_stack: set) -> bool:
            visited.add(node)
            rec_stack.add(node)

            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    if has_cycle(neighbor, visited, rec_stack):
                        return True
                elif neighbor in rec_stack:
                    return True

            rec_stack.remove(node)
            return False

        visited = set()
        rec_stack = set()

        for task_id in graph:
            if task_id not in visited:
                if has_cycle(task_id, visited, rec_stack):
                    return True

        return False

    def create_tasks(
        self,
        plan: Dict[str, Any]
    ) -> List[Task]:
        """创建 Task 对象

        Args:
            plan: 计划字典

        Returns:
            Task 对象列表
        """
        tasks = []
        for task_data in plan.get("tasks", []):
            task = Task(
                id=task_data["id"],
                title=task_data["title"],
                description=task_data.get("description", ""),
                priority=Priority.from_string(task_data.get("priority", "REQUIRED")),
                estimated_effort=task_data.get("estimated_effort", 1),
                dependencies=task_data.get("dependencies", [])
            )
            tasks.append(task)

        return tasks
