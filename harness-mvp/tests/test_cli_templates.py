"""CLI Template Integration Tests - Task 7.1"""
import pytest
from click.testing import CliRunner
from pathlib import Path
import json
import shutil

from harness.cli import main
from harness.store import TaskStore


@pytest.fixture
def temp_harness_dir(tmp_path):
    """Create a temporary .harness directory"""
    harness_dir = tmp_path / ".harness"
    harness_dir.mkdir()
    
    # Create state.json
    state_file = harness_dir / "state.json"
    state_file.write_text(json.dumps({"tasks": []}), encoding='utf-8')
    
    # Create config.json
    config_file = harness_dir / "config.json"
    config_file.write_text(json.dumps({
        "ai_model": "gpt-4",
        "execution_mode": "solo",
        "max_workers": 1
    }), encoding='utf-8')
    
    # Create events.json (HistoryManager expects a list, not a dict)
    events_file = harness_dir / "events.json"
    events_file.write_text(json.dumps([]), encoding='utf-8')
    
    return harness_dir


@pytest.fixture
def runner():
    """Create a Click CLI runner"""
    return CliRunner()


class TestCLITemplateIntegration:
    """Test CLI template commands - Requirements 3.3.1"""
    
    def test_plan_add_with_template_non_interactive(self, runner, temp_harness_dir, monkeypatch):
        """Test harness plan add --template with --var arguments (non-interactive mode)"""
        # Change to temp directory
        monkeypatch.chdir(temp_harness_dir.parent)
        
        # Run command with template and variables
        result = runner.invoke(main, [
            'plan', 'add',
            '--template', 'feature',
            '--var', 'feature_name=User Authentication',
            '--var', 'description=Implement JWT-based authentication'
        ])
        
        # Check command succeeded
        assert result.exit_code == 0, f"Command failed: {result.output}"
        
        # Check success message displayed
        assert "✅ 任务创建成功!" in result.output
        assert "标题: 实现 User Authentication 功能" in result.output
        assert "优先级: REQUIRED" in result.output
        assert "工作量: 3" in result.output
        
        # Verify task was created in store
        store = TaskStore(temp_harness_dir)
        tasks = store.load_tasks()
        assert len(tasks) == 1
        
        task = tasks[0]
        assert task.title == "实现 User Authentication 功能"
        assert "Implement JWT-based authentication" in task.description
        assert task.priority.value == "REQUIRED"
        assert task.estimated_effort == 3
    
    def test_plan_add_with_template_interactive(self, runner, temp_harness_dir, monkeypatch):
        """Test harness plan add --template in interactive mode (no --var)"""
        # Change to temp directory
        monkeypatch.chdir(temp_harness_dir.parent)
        
        # Simulate user input for interactive prompts
        user_inputs = "API Gateway\nCentral API routing system\n"
        
        result = runner.invoke(main, [
            'plan', 'add',
            '--template', 'feature'
        ], input=user_inputs)
        
        # Check command succeeded
        assert result.exit_code == 0, f"Command failed: {result.output}"
        
        # Check success message displayed
        assert "✅ 任务创建成功!" in result.output
        assert "标题: 实现 API Gateway 功能" in result.output
        
        # Verify task was created
        store = TaskStore(temp_harness_dir)
        tasks = store.load_tasks()
        assert len(tasks) == 1
        assert tasks[0].title == "实现 API Gateway 功能"
    
    def test_plan_add_template_not_found_error(self, runner, temp_harness_dir, monkeypatch):
        """Test error handling for non-existent template"""
        # Change to temp directory
        monkeypatch.chdir(temp_harness_dir.parent)
        
        result = runner.invoke(main, [
            'plan', 'add',
            '--template', 'nonexistent'
        ])
        
        # Check error message displayed
        assert "❌ 错误:" in result.output
        assert "not found" in result.output
        
        # Check available templates are listed
        assert "可用模板:" in result.output
        assert "feature" in result.output
        assert "bugfix" in result.output
        assert "refactor" in result.output
        
        # Verify no task was created
        store = TaskStore(temp_harness_dir)
        tasks = store.load_tasks()
        assert len(tasks) == 0
    
    def test_plan_add_missing_required_variable_error(self, runner, temp_harness_dir, monkeypatch):
        """Test error handling for missing required variables"""
        # Change to temp directory
        monkeypatch.chdir(temp_harness_dir.parent)
        
        # Only provide feature_name, not description (which is required)
        result = runner.invoke(main, [
            'plan', 'add',
            '--template', 'feature',
            '--var', 'feature_name=Incomplete Feature'
        ])
        
        # Check error message displayed
        assert "❌ 错误:" in result.output
        assert "Missing required variables" in result.output
        assert "description" in result.output
        
        # Verify no task was created
        store = TaskStore(temp_harness_dir)
        tasks = store.load_tasks()
        assert len(tasks) == 0
    
    def test_plan_add_invalid_var_format(self, runner, temp_harness_dir, monkeypatch):
        """Test error handling for invalid --var format"""
        # Change to temp directory
        monkeypatch.chdir(temp_harness_dir.parent)
        
        # Invalid format: no equals sign
        result = runner.invoke(main, [
            'plan', 'add',
            '--template', 'feature',
            '--var', 'invalid_format'
        ])
        
        # Check error message displayed
        assert "❌ 错误:" in result.output
        assert "无效的变量格式" in result.output
        assert "key=value" in result.output
        
        # Verify no task was created
        store = TaskStore(temp_harness_dir)
        tasks = store.load_tasks()
        assert len(tasks) == 0
    
    def test_plan_add_bugfix_template(self, runner, temp_harness_dir, monkeypatch):
        """Test using bugfix template"""
        # Change to temp directory
        monkeypatch.chdir(temp_harness_dir.parent)
        
        result = runner.invoke(main, [
            'plan', 'add',
            '--template', 'bugfix',
            '--var', 'bug_description=Login 500 Error',
            '--var', 'description=Server returns 500 when logging in',
            '--var', 'reproduction_steps=1. Go to /login\\n2. Enter credentials\\n3. Click submit',
            '--var', 'fix_plan=Check database connection'
        ])
        
        # Check command succeeded
        assert result.exit_code == 0, f"Command failed: {result.output}"
        assert "✅ 任务创建成功!" in result.output
        assert "修复 Login 500 Error" in result.output
        
        # Verify task details
        store = TaskStore(temp_harness_dir)
        tasks = store.load_tasks()
        assert len(tasks) == 1
        
        task = tasks[0]
        assert task.title == "修复 Login 500 Error"
        assert task.priority.value == "REQUIRED"
        assert task.estimated_effort == 2
    
    def test_plan_add_refactor_template(self, runner, temp_harness_dir, monkeypatch):
        """Test using refactor template"""
        # Change to temp directory
        monkeypatch.chdir(temp_harness_dir.parent)
        
        result = runner.invoke(main, [
            'plan', 'add',
            '--template', 'refactor',
            '--var', 'module_name=executor module',
            '--var', 'goal=Reduce cyclomatic complexity',
            '--var', 'scope=ExecutionEngine class'
        ])
        
        # Check command succeeded
        assert result.exit_code == 0, f"Command failed: {result.output}"
        assert "✅ 任务创建成功!" in result.output
        assert "重构 executor module" in result.output
        
        # Verify task details
        store = TaskStore(temp_harness_dir)
        tasks = store.load_tasks()
        assert len(tasks) == 1
        
        task = tasks[0]
        assert task.title == "重构 executor module"
        assert task.priority.value == "RECOMMENDED"
        assert task.estimated_effort == 3
    
    def test_plan_add_backward_compatibility_manual_mode(self, runner, temp_harness_dir, monkeypatch):
        """Test backward compatibility - manual task creation without template"""
        # Change to temp directory
        monkeypatch.chdir(temp_harness_dir.parent)
        
        # Use manual mode (no --template)
        result = runner.invoke(main, [
            'plan', 'add',
            '--title', 'Manual Task',
            '--description', 'Created without template',
            '--priority', 'RECOMMENDED',
            '--estimate', '2'
        ])
        
        # Check command succeeded
        assert result.exit_code == 0, f"Command failed: {result.output}"
        assert "已添加任务" in result.output
        assert "Manual Task" in result.output
        
        # Verify task was created
        store = TaskStore(temp_harness_dir)
        tasks = store.load_tasks()
        assert len(tasks) == 1
        
        task = tasks[0]
        assert task.title == "Manual Task"
        assert task.description == "Created without template"
        assert task.priority.value == "RECOMMENDED"
        assert task.estimated_effort == 2
    
    def test_plan_add_custom_template_override(self, runner, temp_harness_dir, monkeypatch):
        """Test custom template overriding built-in template"""
        # Change to temp directory
        monkeypatch.chdir(temp_harness_dir.parent)
        
        # Create custom templates directory
        templates_dir = temp_harness_dir / "templates"
        templates_dir.mkdir()
        
        # Create custom feature template that overrides built-in
        custom_template = {
            "name": "feature",
            "title": "Custom {feature_name}",
            "description": "Custom description: {description}",
            "priority": "OPTIONAL",
            "estimated_effort": 1,
            "prompts": [
                {"key": "feature_name", "question": "Feature name?", "required": True},
                {"key": "description", "question": "Description?", "required": True}
            ]
        }
        
        custom_file = templates_dir / "feature.json"
        custom_file.write_text(json.dumps(custom_template), encoding='utf-8')
        
        # Use the custom template
        result = runner.invoke(main, [
            'plan', 'add',
            '--template', 'feature',
            '--var', 'feature_name=Custom Test',
            '--var', 'description=Testing custom override'
        ])
        
        # Check command succeeded
        assert result.exit_code == 0, f"Command failed: {result.output}"
        
        # Verify custom template was used (different title format and priority)
        store = TaskStore(temp_harness_dir)
        tasks = store.load_tasks()
        assert len(tasks) == 1
        
        task = tasks[0]
        assert task.title == "Custom Custom Test"  # Custom format
        assert task.priority.value == "OPTIONAL"  # Custom priority
        assert task.estimated_effort == 1  # Custom effort
    
    def test_plan_add_multiple_vars_with_equals_in_value(self, runner, temp_harness_dir, monkeypatch):
        """Test handling --var with equals sign in the value"""
        # Change to temp directory
        monkeypatch.chdir(temp_harness_dir.parent)
        
        # Value contains equals sign (e.g., code snippet)
        result = runner.invoke(main, [
            'plan', 'add',
            '--template', 'feature',
            '--var', 'feature_name=Math Parser',
            '--var', 'description=Support expressions like x=2+3'
        ])
        
        # Check command succeeded
        assert result.exit_code == 0, f"Command failed: {result.output}"
        assert "✅ 任务创建成功!" in result.output
        
        # Verify task was created with correct values
        store = TaskStore(temp_harness_dir)
        tasks = store.load_tasks()
        assert len(tasks) == 1
        
        task = tasks[0]
        assert task.title == "实现 Math Parser 功能"
        assert "x=2+3" in task.description  # Value with = preserved


class TestCLITemplateHelp:
    """Test CLI help text for template options"""
    
    def test_plan_add_help_shows_template_options(self, runner):
        """Test that help text shows template and var options"""
        result = runner.invoke(main, ['plan', 'add', '--help'])
        
        assert result.exit_code == 0
        assert '--template' in result.output or '-t' in result.output
        assert '--var' in result.output
        assert 'key=value' in result.output.lower() or '格式' in result.output


class TestCLITemplateCommandGroup:
    """Test template command group - Task 7.2"""
    
    def test_template_command_group_exists(self, runner):
        """Test that 'harness template' command group exists - Requirements 3.3"""
        result = runner.invoke(main, ['--help'])
        
        assert result.exit_code == 0
        assert 'template' in result.output
        assert '模板管理命令' in result.output
    
    def test_template_command_group_accessible(self, runner):
        """Test that 'harness template' command group is accessible"""
        result = runner.invoke(main, ['template', '--help'])
        
        assert result.exit_code == 0
        assert '模板管理命令' in result.output


class TestCLITemplateListCommand:
    """Test template list command - Task 7.3"""
    
    def test_template_list_shows_built_in_templates(self, runner, temp_harness_dir, monkeypatch):
        """Test that 'harness template list' displays all built-in templates - Requirements 3.3.2"""
        # Change to temp directory
        monkeypatch.chdir(temp_harness_dir.parent)
        
        result = runner.invoke(main, ['template', 'list'])
        
        # Check command succeeded
        assert result.exit_code == 0, f"Command failed: {result.output}"
        
        # Check header is displayed
        assert "可用模板:" in result.output
        
        # Check all built-in templates are listed
        assert "feature" in result.output
        assert "bugfix" in result.output
        assert "refactor" in result.output
        
        # Check descriptions are displayed
        assert "功能开发任务" in result.output
        assert "Bug修复任务" in result.output
        assert "代码重构任务" in result.output
        
        # Check priority and effort are displayed
        assert "优先级:" in result.output
        assert "工作量:" in result.output
        
        # Check usage hint is displayed
        assert "使用方式:" in result.output
        assert "harness plan add --template" in result.output
    
    def test_template_list_shows_custom_templates(self, runner, temp_harness_dir, monkeypatch):
        """Test that custom templates are marked with (自定义) suffix"""
        # Change to temp directory
        monkeypatch.chdir(temp_harness_dir.parent)
        
        # Create custom templates directory
        templates_dir = temp_harness_dir / "templates"
        templates_dir.mkdir()
        
        # Create a custom template
        custom_template = {
            "name": "documentation",
            "title": "编写 {document_name} 文档",
            "description": "Documentation template",
            "priority": "OPTIONAL",
            "estimated_effort": 1,
            "prompts": [
                {"key": "document_name", "question": "Document name?", "required": True}
            ]
        }
        
        custom_file = templates_dir / "documentation.json"
        custom_file.write_text(json.dumps(custom_template), encoding='utf-8')
        
        result = runner.invoke(main, ['template', 'list'])
        
        # Check command succeeded
        assert result.exit_code == 0, f"Command failed: {result.output}"
        
        # Check custom template is listed with suffix
        assert "documentation (自定义)" in result.output


class TestCLITemplateShowCommand:
    """Test template show command - Task 7.4"""
    
    def test_template_show_displays_feature_template(self, runner, temp_harness_dir, monkeypatch):
        """Test 'harness template show feature' displays template details - Requirements 3.3.3"""
        # Change to temp directory
        monkeypatch.chdir(temp_harness_dir.parent)
        
        result = runner.invoke(main, ['template', 'show', 'feature'])
        
        # Check command succeeded
        assert result.exit_code == 0, f"Command failed: {result.output}"
        
        # Check template metadata is displayed
        assert "=== 模板: feature ===" in result.output
        assert "标题: 实现 {feature_name} 功能" in result.output
        assert "优先级: REQUIRED" in result.output
        assert "工作量: 3" in result.output
        
        # Check description is displayed
        assert "描述:" in result.output
        assert "### 功能描述" in result.output
        assert "{description}" in result.output
        
        # Check prompts are displayed
        assert "变量:" in result.output
        assert "feature_name (必填)" in result.output
        assert "请输入功能名称" in result.output
        assert "description (必填)（多行）" in result.output
        assert "请输入功能描述" in result.output
    
    def test_template_show_displays_bugfix_template(self, runner, temp_harness_dir, monkeypatch):
        """Test 'harness template show bugfix' displays template with optional fields"""
        # Change to temp directory
        monkeypatch.chdir(temp_harness_dir.parent)
        
        result = runner.invoke(main, ['template', 'show', 'bugfix'])
        
        # Check command succeeded
        assert result.exit_code == 0, f"Command failed: {result.output}"
        
        # Check template metadata
        assert "=== 模板: bugfix ===" in result.output
        assert "优先级: REQUIRED" in result.output
        assert "工作量: 2" in result.output
        
        # Check required prompt
        assert "bug_description (必填)" in result.output
        
        # Check optional prompt with default value
        assert "fix_plan (可选)" in result.output
        assert "默认值: 待分析" in result.output
    
    def test_template_show_displays_refactor_template(self, runner, temp_harness_dir, monkeypatch):
        """Test 'harness template show refactor' displays template details"""
        # Change to temp directory
        monkeypatch.chdir(temp_harness_dir.parent)
        
        result = runner.invoke(main, ['template', 'show', 'refactor'])
        
        # Check command succeeded
        assert result.exit_code == 0, f"Command failed: {result.output}"
        
        # Check template metadata
        assert "=== 模板: refactor ===" in result.output
        assert "优先级: RECOMMENDED" in result.output
        assert "工作量: 3" in result.output
        
        # Check prompts
        assert "module_name (必填)" in result.output
        assert "goal (必填)（多行）" in result.output
        assert "scope (必填)（多行）" in result.output
    
    def test_template_show_handles_not_found_error(self, runner, temp_harness_dir, monkeypatch):
        """Test error handling when template doesn't exist - Requirements 3.3.3"""
        # Change to temp directory
        monkeypatch.chdir(temp_harness_dir.parent)
        
        result = runner.invoke(main, ['template', 'show', 'nonexistent'])
        
        # Check command succeeded (returns 0 even with error message)
        assert result.exit_code == 0, f"Command failed: {result.output}"
        
        # Check friendly error message is displayed
        assert "模板 'nonexistent' 不存在" in result.output
    
    def test_template_show_displays_custom_template(self, runner, temp_harness_dir, monkeypatch):
        """Test 'harness template show' works with custom templates"""
        # Change to temp directory
        monkeypatch.chdir(temp_harness_dir.parent)
        
        # Create custom templates directory
        templates_dir = temp_harness_dir / "templates"
        templates_dir.mkdir()
        
        # Create a custom template with various prompt types
        custom_template = {
            "name": "api",
            "title": "实现 {endpoint} API接口",
            "description": "### API 描述\n{description}\n\n### 请求方法\n{method}",
            "priority": "REQUIRED",
            "estimated_effort": 2,
            "prompts": [
                {"key": "endpoint", "question": "请输入API端点", "required": True},
                {"key": "description", "question": "请输入API功能描述", "required": True, "multiline": True},
                {"key": "method", "question": "请输入HTTP方法", "required": True, "default": "GET"}
            ]
        }
        
        custom_file = templates_dir / "api.json"
        custom_file.write_text(json.dumps(custom_template), encoding='utf-8')
        
        result = runner.invoke(main, ['template', 'show', 'api'])
        
        # Check command succeeded
        assert result.exit_code == 0, f"Command failed: {result.output}"
        
        # Check template metadata
        assert "=== 模板: api ===" in result.output
        assert "标题: 实现 {endpoint} API接口" in result.output
        assert "优先级: REQUIRED" in result.output
        assert "工作量: 2" in result.output
        
        # Check prompts with various attributes
        assert "endpoint (必填)" in result.output
        assert "description (必填)（多行）" in result.output
        assert "method (必填)" in result.output
        assert "默认值: GET" in result.output
