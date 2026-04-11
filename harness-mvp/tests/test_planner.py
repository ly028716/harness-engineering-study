"""测试 Planner Agent - Phase 2"""
import pytest
from harness.planner import PlannerAgent, PlanGenerator


class TestPlanGenerator:
    """测试 PlanGenerator"""

    def test_generate_task_from_description(self):
        """RED: 测试从描述生成任务"""
        generator = PlanGenerator()
        description = "实现用户登录功能，需要支持邮箱和密码验证"

        task_dict = generator.generate_task(
            title="实现登录功能",
            description=description,
            priority="REQUIRED"
        )

        assert task_dict["title"] == "实现登录功能"
        assert task_dict["priority"] == "REQUIRED"
        assert isinstance(task_dict["estimated_effort"], int)
        assert 1 <= task_dict["estimated_effort"] <= 5

    def test_parse_user_input_basic(self):
        """RED: 测试解析用户基本输入"""
        generator = PlanGenerator()
        user_input = "我想做一个用户认证系统"

        result = generator.parse_user_input(user_input)

        assert "goal" in result
        assert "用户认证" in result["goal"] or "认证" in result["goal"]

    def test_extract_keywords(self):
        """RED: 测试提取关键词"""
        generator = PlanGenerator()
        text = "实现 REST API 用户认证 JWT token"

        keywords = generator.extract_keywords(text)

        assert len(keywords) > 0
        assert any(kw in keywords for kw in ["API", "用户", "认证", "JWT", "token", "REST"])

    def test_categorize_priority_required(self):
        """RED: 测试分类优先级 - Required"""
        generator = PlanGenerator()
        description = "核心功能：用户登录和注册"

        priority = generator.categorize_priority(description)

        assert priority == "REQUIRED"

    def test_categorize_priority_optional(self):
        """RED: 测试分类优先级 - Optional"""
        generator = PlanGenerator()
        description = "可选功能：深色模式切换"

        priority = generator.categorize_priority(description)

        assert priority in ["OPTIONAL", "RECOMMENDED"]

    def test_estimate_effort_simple(self):
        """RED: 测试估算工作量 - 简单"""
        generator = PlanGenerator()
        description = "添加一个按钮"

        effort = generator.estimate_effort(description)

        assert 1 <= effort <= 2

    def test_estimate_effort_complex(self):
        """RED: 测试估算工作量 - 复杂"""
        generator = PlanGenerator()
        description = "实现完整的用户认证系统，包括注册、登录、密码重置、JWT token 管理"

        effort = generator.estimate_effort(description)

        assert 3 <= effort <= 5

    def test_generate_acceptance_criteria(self):
        """RED: 测试生成验收标准"""
        generator = PlanGenerator()
        title = "实现登录接口"
        description = "支持邮箱和密码验证，返回 JWT token"

        criteria = generator.generate_acceptance_criteria(title, description)

        assert len(criteria) > 0
        assert isinstance(criteria, list)


class TestPlannerAgent:
    """测试 PlannerAgent"""

    def test_collect_requirements(self):
        """RED: 测试收集需求"""
        agent = PlannerAgent()

        # 模拟用户需求
        requirements = agent.collect_requirements(
            goal="实现用户认证功能",
            key_features=["登录", "注册"],
            constraints=["使用 JWT"]
        )

        assert "goal" in requirements
        assert requirements["goal"] == "实现用户认证功能"
        assert "key_features" in requirements
        assert "constraints" in requirements

    def test_break_down_tasks(self):
        """RED: 测试任务分解"""
        agent = PlannerAgent()

        tasks = agent.break_down_tasks(
            goal="实现用户认证",
            features=["登录", "注册", "密码重置"]
        )

        assert len(tasks) >= 3
        assert all("id" in t for t in tasks)
        assert all("title" in t for t in tasks)

    def test_generate_plan(self):
        """RED: 测试生成完整计划"""
        agent = PlannerAgent()

        plan = agent.generate_plan(
            goal="实现简单的待办事项应用",
            features=["添加任务", "删除任务", "标记完成"],
            priority="REQUIRED"
        )

        assert "tasks" in plan
        assert len(plan["tasks"]) > 0
        assert all("id" in t for t in plan["tasks"])
        assert all("title" in t for t in plan["tasks"])
        assert all("priority" in t for t in plan["tasks"])

    def test_validate_plan(self):
        """RED: 测试验证计划"""
        agent = PlannerAgent()

        plan = {
            "tasks": [
                {"id": 1, "title": "Task 1", "dependencies": []},
                {"id": 2, "title": "Task 2", "dependencies": [1]},
            ]
        }

        is_valid, issues = agent.validate_plan(plan)

        assert is_valid is True
        assert len(issues) == 0

    def test_validate_plan_circular_dependency(self):
        """RED: 测试验证计划 - 循环依赖"""
        agent = PlannerAgent()

        plan = {
            "tasks": [
                {"id": 1, "title": "Task 1", "dependencies": [2]},
                {"id": 2, "title": "Task 2", "dependencies": [1]},
            ]
        }

        is_valid, issues = agent.validate_plan(plan)

        # 循环依赖应该被检测出来
        assert is_valid is False or len(issues) > 0
