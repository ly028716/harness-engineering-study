"""测试 AI 客户端"""
import os
import pytest
from unittest.mock import patch, MagicMock
from harness.ai_client import AIClient
from harness.prompts import WORKER_SYSTEM_PROMPT, build_work_prompt
from harness.executor import WorkerAgent
from harness.models import Task


class TestAIClient:
    """测试 AIClient"""

    def test_missing_api_key_raises_error(self):
        """测试缺少 API key 时抛出错误"""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="API 密钥"):
                AIClient()

    def test_api_key_from_env(self):
        """测试从环境变量读取 API key"""
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-test-key"}):
            client = AIClient()
            assert client.api_key == "sk-test-key"
            assert client.model == "claude-sonnet-4-20250514"

    def test_api_key_direct(self):
        """测试直接传入 API key"""
        client = AIClient(api_key="sk-direct-key")
        assert client.api_key == "sk-direct-key"

    def test_custom_model(self):
        """测试自定义模型"""
        client = AIClient(api_key="sk-test", model="claude-opus-4-20250514")
        assert client.model == "claude-opus-4-20250514"

    @patch("harness.ai_client.anthropic")
    def test_generate_code_success(self, mock_anthropic):
        """测试成功生成代码"""
        mock_message = MagicMock()
        mock_block = MagicMock()
        mock_block.text = "```python:hello.py\nprint('hello')\n```"
        mock_message.content = [mock_block]
        mock_anthropic.Anthropic.return_value.messages.create.return_value = mock_message

        client = AIClient(api_key="sk-test")
        result = client.generate_code("system prompt", "user prompt")

        assert "print('hello')" in result
        mock_anthropic.Anthropic.return_value.messages.create.assert_called_once()

    @patch("harness.ai_client.anthropic")
    def test_generate_code_no_text_blocks(self, mock_anthropic):
        """测试响应中无文本块"""
        mock_message = MagicMock()
        mock_message.content = []  # 空响应
        mock_anthropic.Anthropic.return_value.messages.create.return_value = mock_message

        client = AIClient(api_key="sk-test")
        result = client.generate_code("system", "prompt")
        assert result == ""


class TestPrompts:
    """测试 Prompt 模板"""

    def test_work_system_prompt_contains_principles(self):
        """测试 system prompt 包含核心原则"""
        assert "核心原则" in WORKER_SYSTEM_PROMPT
        assert "代码块" in WORKER_SYSTEM_PROMPT

    def test_build_work_prompt_full(self):
        """测试完整构建工作提示词"""
        prompt = build_work_prompt(
            task_title="实现登录功能",
            task_description="用户邮箱密码登录",
            acceptance_criteria=["返回 JWT token", "错误密码返回 401"],
            dependencies=[1],
        )
        assert "实现登录功能" in prompt
        assert "返回 JWT token" in prompt
        assert "错误密码返回 401" in prompt
        assert "依赖任务 [1]" in prompt

    def test_build_work_prompt_no_deps(self):
        """测试无依赖的提示词"""
        prompt = build_work_prompt(
            task_title="简单任务",
            task_description="",
            acceptance_criteria=[],
            dependencies=[],
        )
        assert "简单任务" in prompt
        assert "前置依赖" not in prompt

    def test_build_work_prompt_no_criteria(self):
        """测试无验收标准的提示词"""
        prompt = build_work_prompt(
            task_title="任务",
            task_description="描述",
            acceptance_criteria=[],
            dependencies=[],
        )
        # 无验收标准时，不生成验收标准章节
        assert "## 验收标准" not in prompt


class TestWorkerAgentWithAI:
    """测试 WorkerAgent AI 集成"""

    def test_worker_fallback_when_no_api_key(self, monkeypatch):
        """测试无 API key 时回退到模拟模式"""
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        task = Task(id=1, title="测试任务", description="测试描述")
        agent = WorkerAgent(task)
        result = agent.execute()

        assert result.task_id == 1
        # fallback 仍然被认为是成功（只是输出信息）
        assert result.success is True
        assert "测试描述" in result.output or "测试任务" in result.output

    def test_worker_parse_code_blocks(self):
        """测试解析 AI 响应中的代码块"""
        from harness.executor import WorkerAgent
        import tempfile
        task = Task(id=1, title="测试")
        agent = WorkerAgent(task)

        response = """
        ```python:src/utils.py
        def add(a, b):
            return a + b
        ```
        ```python:tests/test_utils.py
        def test_add():
            assert add(1, 2) == 3
        ```
        """
        with tempfile.TemporaryDirectory() as td:
            files = agent._parse_and_write_files(response, td)
            assert len(files) == 2
            assert any(f.endswith("utils.py") for f in files)

    def test_worker_empty_response(self):
        """测试 AI 返回空响应的处理"""
        task = Task(id=1, title="测试")
        agent = WorkerAgent(task)
        files = agent._parse_and_write_files("", "")
        assert files == []

    def test_parse_and_write_files(self, tmp_path):
        """测试解析并写入文件"""
        task = Task(id=1, title="测试")
        agent = WorkerAgent(task)

        response = """```python:hello.py
print("hello world")
```"""
        files = agent._parse_and_write_files(response, str(tmp_path))
        assert len(files) == 1
        assert (tmp_path / "hello.py").exists()
        assert (tmp_path / "hello.py").read_text(encoding='utf-8') == 'print("hello world")'
