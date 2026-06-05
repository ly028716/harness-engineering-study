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


class TestPlannerAIIntegration:
    """测试 AI 驱动的计划生成集成"""

    @pytest.fixture
    def mock_ai_client(self):
        """创建模拟的 AIClient"""
        from unittest.mock import MagicMock
        from harness.ai_client import AIClient
        client = MagicMock(spec=AIClient)
        return client

    def test_ai_plan_generates_tasks(self, mock_ai_client):
        """RED: 测试 AI 计划生成任务列表"""
        mock_ai_client.generate_code.return_value = '''{
            "goal": "实现用户认证系统",
            "tasks": [
                {
                    "id": 1,
                    "title": "用户注册",
                    "description": "支持邮箱和密码注册",
                    "priority": "REQUIRED",
                    "estimated_effort": 3,
                    "dependencies": [],
                    "acceptance_criteria": ["注册成功返回 token", "密码加密存储"]
                },
                {
                    "id": 2,
                    "title": "用户登录",
                    "description": "支持邮箱密码登录",
                    "priority": "REQUIRED",
                    "estimated_effort": 2,
                    "dependencies": [1],
                    "acceptance_criteria": ["登录验证通过", "错误密码返回 401"]
                }
            ]
        }'''

        agent = PlannerAgent(ai_client=mock_ai_client)
        plan = agent.ai_plan("实现用户认证系统")

        assert plan is not None
        assert "goal" in plan
        assert "tasks" in plan
        assert len(plan["tasks"]) == 2

        task1 = plan["tasks"][0]
        assert task1["id"] == 1
        assert task1["title"] == "用户注册"
        assert task1["priority"] == "REQUIRED"
        assert task1["dependencies"] == []

    def test_ai_plan_no_client_returns_none(self):
        """RED: 测试无 AIClient 时返回 None"""
        agent = PlannerAgent()
        plan = agent.ai_plan("实现用户认证系统")
        assert plan is None

    def test_ai_plan_handles_invalid_json(self, mock_ai_client):
        """RED: 测试 AI 返回无效 JSON 时返回 None"""
        mock_ai_client.generate_code.return_value = "这不是有效的 JSON 响应"

        agent = PlannerAgent(ai_client=mock_ai_client)
        plan = agent.ai_plan("实现用户认证系统")
        assert plan is None

    def test_ai_plan_handles_empty_response(self, mock_ai_client):
        """RED: 测试 AI 返回空字符串"""
        mock_ai_client.generate_code.return_value = ""

        agent = PlannerAgent(ai_client=mock_ai_client)
        plan = agent.ai_plan("实现用户认证系统")
        assert plan is None

    def test_ai_plan_missing_tasks_field(self, mock_ai_client):
        """RED: 测试 AI 返回缺少 tasks 字段的 JSON"""
        mock_ai_client.generate_code.return_value = '{"goal": "test", "other": "data"}'

        agent = PlannerAgent(ai_client=mock_ai_client)
        plan = agent.ai_plan("test")
        assert plan is None

    def test_ai_plan_empty_tasks_array(self, mock_ai_client):
        """RED: 测试 AI 返回空任务数组"""
        mock_ai_client.generate_code.return_value = '{"goal": "test", "tasks": []}'

        agent = PlannerAgent(ai_client=mock_ai_client)
        plan = agent.ai_plan("test")
        assert plan is not None
        assert len(plan["tasks"]) == 0

    def test_ai_plan_with_context(self, mock_ai_client):
        """RED: 测试 AI 计划使用上下文信息"""
        mock_ai_client.generate_code.return_value = '{"goal": "test", "tasks": []}'

        agent = PlannerAgent(ai_client=mock_ai_client)
        agent.ai_plan("test", context="Python 项目，使用 FastAPI")

        # 验证 context 被传递到 prompt 中
        args, kwargs = mock_ai_client.generate_code.call_args
        user_prompt = args[1]
        assert "FastAPI" in user_prompt

    def test_ai_plan_generate_code_called_with_prompt(self, mock_ai_client):
        """RED: 测试 ai_plan 正确调用 AIClient.generate_code"""
        mock_ai_client.generate_code.return_value = '{"goal": "test", "tasks": []}'

        agent = PlannerAgent(ai_client=mock_ai_client)
        agent.ai_plan("实现用户认证系统")

        mock_ai_client.generate_code.assert_called_once()
        args, kwargs = mock_ai_client.generate_code.call_args
        assert len(args) >= 2
        # system prompt 应包含计划生成指令
        assert "计划" in args[0] or "plan" in args[0].lower()

    def test_ai_plan_with_dependencies(self, mock_ai_client):
        """RED: 测试 AI 计划中的依赖关系"""
        mock_ai_client.generate_code.return_value = '''{
            "goal": "构建博客系统",
            "tasks": [
                {"id": 1, "title": "数据库模型", "description": "定义数据模型", "priority": "REQUIRED", "estimated_effort": 3, "dependencies": []},
                {"id": 2, "title": "API 端点", "description": "实现 CRUD 接口", "priority": "REQUIRED", "estimated_effort": 4, "dependencies": [1]},
                {"id": 3, "title": "前端页面", "description": "实现博客前端", "priority": "RECOMMENDED", "estimated_effort": 5, "dependencies": [2]}
            ]
        }'''

        agent = PlannerAgent(ai_client=mock_ai_client)
        plan = agent.ai_plan("构建博客系统")

        assert plan is not None
        task2 = plan["tasks"][1]
        assert 1 in task2["dependencies"]
        task3 = plan["tasks"][2]
        assert 2 in task3["dependencies"]

    def test_ai_plan_creates_task_objects(self, mock_ai_client):
        """RED: 测试 AI 计划可转换为 Task 对象"""
        mock_ai_client.generate_code.return_value = '''{
            "goal": "测试项目",
            "tasks": [
                {"id": 1, "title": "任务一", "description": "描述一", "priority": "REQUIRED", "estimated_effort": 2, "dependencies": []}
            ]
        }'''

        agent = PlannerAgent(ai_client=mock_ai_client)
        plan = agent.ai_plan("测试项目")
        tasks = agent.create_tasks(plan)

        assert len(tasks) == 1
        assert tasks[0].id == 1
        assert tasks[0].title == "任务一"
        assert tasks[0].priority.value == "REQUIRED"

    def test_ai_plan_handles_api_error(self, mock_ai_client):
        """RED: 测试 AI 计划处理 API 异常"""
        mock_ai_client.generate_code.side_effect = RuntimeError("API 错误")

        agent = PlannerAgent(ai_client=mock_ai_client)
        plan = agent.ai_plan("实现用户认证系统")
        assert plan is None

    def test_ai_plan_code_block_response(self, mock_ai_client):
        """RED: 测试 AI 返回 ```json 代码块格式"""
        mock_ai_client.generate_code.return_value = '''```json
{
    "goal": "测试项目",
    "tasks": [
        {"id": 1, "title": "任务一", "description": "描述", "priority": "REQUIRED", "estimated_effort": 1, "dependencies": []}
    ]
}
```'''

        agent = PlannerAgent(ai_client=mock_ai_client)
        plan = agent.ai_plan("测试项目")
        assert plan is not None
        assert len(plan["tasks"]) == 1
