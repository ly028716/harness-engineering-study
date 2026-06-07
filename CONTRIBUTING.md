# 贡献指南 (Contributing Guide)

欢迎来到 **Harness Engineering Study** 项目！我们非常高兴你有兴趣为这个项目做出贡献。

本指南将帮助你了解如何参与项目开发、提交代码、报告问题以及与社区互动。

---

## 📑 目录

- [行为准则](#-行为准则)
- [如何贡献](#-如何贡献)
  - [报告 Bug](#1-报告-bug)
  - [提出功能建议](#2-提出功能建议)
  - [改进文档](#3-改进文档)
  - [贡献代码](#4-贡献代码)
- [开发环境搭建](#-开发环境搭建)
- [代码规范](#-代码规范)
- [提交规范](#-提交规范)
- [Pull Request 流程](#-pull-request-流程)
- [测试要求](#-测试要求)
- [文档要求](#-文档要求)
- [代码审查](#-代码审查)
- [社区交流](#-社区交流)
- [认可与奖励](#-认可与奖励)

---

## 🤝 行为准则

### 我们的承诺

为了营造一个开放、友好的环境，我们作为贡献者和维护者承诺：无论年龄、体型、残疾、民族、性别认同和表达、经验水平、国籍、个人外貌、种族、宗教或性认同和取向如何，参与我们的项目和社区对每个人都是无骚扰的体验。

### 我们的标准

**积极行为的例子：**
- ✅ 使用友好和包容的语言
- ✅ 尊重不同的观点和经验
- ✅ 优雅地接受建设性批评
- ✅ 关注对社区最有利的事情
- ✅ 对其他社区成员表示同理心

**不可接受行为的例子：**
- ❌ 使用性化的语言或图像
- ❌ 侮辱性/贬损性评论和人身或政治攻击
- ❌ 公开或私下骚扰
- ❌ 未经明确许可发布他人的私人信息
- ❌ 其他在专业环境中可以合理认为不适当的行为

### 执行责任

项目维护者有责任澄清可接受行为的标准，并对任何不可接受的行为采取适当和公平的纠正措施。

---

## 🎯 如何贡献

我们欢迎以下各种形式的贡献：

### 1. 报告 Bug

发现 Bug？请帮助我们改进！

**提交 Bug 报告前：**
- 🔍 检查 [Issues](https://github.com/yourusername/harness-engineering-study/issues) 确保问题尚未被报告
- 📖 查看 [文档](docs/) 确认这不是预期行为
- 🧪 在最新版本上重现问题

**提交 Bug 报告时，请包含：**
- 📝 清晰简洁的标题
- 🐛 详细的问题描述
- 🔄 重现步骤（越详细越好）
- ✅ 预期行为
- ❌ 实际行为
- 💻 环境信息（操作系统、Python 版本、依赖版本）
- 📸 截图或日志（如果适用）

**Bug 报告模板：**
```markdown
**描述问题**
简短描述 bug 是什么。

**重现步骤**
1. 执行命令 '...'
2. 输入参数 '...'
3. 观察到错误

**预期行为**
应该发生什么。

**实际行为**
实际发生了什么。

**环境信息**
- OS: [例如 Windows 11]
- Python 版本: [例如 3.12.0]
- 项目版本: [例如 0.6.0]

**附加信息**
添加任何其他有助于解决问题的信息。
```

### 2. 提出功能建议

有好的想法？我们很乐意听取！

**提交功能建议前：**
- 🔍 检查是否已有类似建议
- 💭 思考该功能如何帮助其他用户
- 📊 考虑实现的可行性

**提交功能建议时，请包含：**
- 📝 清晰的功能描述
- 🎯 解决的问题或满足的需求
- 💡 可能的实现方案
- 📈 预期收益
- 🤔 潜在的挑战

**功能建议模板：**
```markdown
**功能描述**
简洁描述你想要的功能。

**解决的问题**
这个功能解决什么问题？为什么有用？

**建议的解决方案**
你希望如何实现这个功能？

**替代方案**
你考虑过哪些其他方案？

**附加信息**
任何其他相关信息或截图。
```

### 3. 改进文档

文档对项目至关重要！

**文档贡献包括：**
- 📖 修复错别字和语法错误
- 🌐 翻译文档（中英文）
- 💡 添加使用示例
- 📚 完善 API 文档
- 🎓 编写教程和指南
- 📹 创建视频教程

**文档标准：**
- 使用清晰简洁的语言
- 提供实际可运行的示例
- 保持中英文同步（如果可能）
- 遵循 Markdown 格式规范

### 4. 贡献代码

准备好贡献代码了吗？太棒了！

**贡献类型：**
- 🐛 修复 Bug
- ✨ 实现新功能
- ⚡ 性能优化
- 🎨 代码重构
- ✅ 增加测试
- 📦 更新依赖

请继续阅读下面的详细指南。

---

## 🛠️ 开发环境搭建

### 1. Fork 项目

点击 GitHub 页面右上角的 "Fork" 按钮，将项目 fork 到你的账户下。

### 2. 克隆仓库

```bash
# 克隆你 fork 的仓库
git clone https://github.com/YOUR_USERNAME/harness-engineering-study.git
cd harness-engineering-study
```

### 3. 添加上游仓库

```bash
# 添加原始仓库为上游
git remote add upstream https://github.com/ORIGINAL_OWNER/harness-engineering-study.git

# 验证远程仓库
git remote -v
```

### 4. 安装依赖

```bash
# 进入 MVP 目录
cd harness-mvp

# 创建虚拟环境（推荐）
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# 安装开发依赖
pip install -e ".[dev]"
```

### 5. 验证安装

```bash
# 运行测试确保环境正常
pytest tests/ -v

# 查看覆盖率
pytest tests/ --cov=harness --cov-report=html

# 验证 CLI
harness --version
```

---

## 📐 代码规范

### Python 代码风格

我们遵循 [PEP 8](https://www.python.org/dev/peps/pep-0008/) 代码风格指南。

**核心原则：**
- ✅ 使用 4 个空格缩进（不使用 Tab）
- ✅ 每行最多 100 字符（文档字符串 72 字符）
- ✅ 函数和类之间空 2 行
- ✅ 方法之间空 1 行
- ✅ 使用有意义的变量名和函数名

**命名规范：**
```python
# 模块名：小写+下划线
file_name.py

# 类名：大驼峰
class TaskManager:
    pass

# 函数名：小写+下划线
def execute_task():
    pass

# 常量：大写+下划线
MAX_WORKERS = 4

# 私有成员：前缀单下划线
def _internal_method():
    pass
```

### 类型注解

使用类型注解提高代码可读性：

```python
from typing import List, Optional, Dict

def process_tasks(
    tasks: List[Task],
    config: Optional[Dict[str, Any]] = None
) -> bool:
    """处理任务列表。
    
    Args:
        tasks: 要处理的任务列表
        config: 可选的配置字典
        
    Returns:
        处理是否成功
    """
    pass
```

### 文档字符串

使用 Google 风格的文档字符串：

```python
def create_task(
    title: str,
    description: str,
    priority: Priority = Priority.OPTIONAL
) -> Task:
    """创建新任务。
    
    Args:
        title: 任务标题
        description: 任务描述
        priority: 任务优先级，默认为 OPTIONAL
        
    Returns:
        创建的任务对象
        
    Raises:
        ValueError: 如果标题为空
        
    Example:
        >>> task = create_task("实现功能", "添加用户登录")
        >>> print(task.title)
        实现功能
    """
    if not title:
        raise ValueError("标题不能为空")
    
    return Task(title=title, description=description, priority=priority)
```

### 导入顺序

```python
# 1. 标准库导入
import os
import sys
from typing import List, Optional

# 2. 第三方库导入
import click
from anthropic import Anthropic

# 3. 本地应用导入
from harness.models import Task
from harness.store import TaskStore
```

### 代码质量工具

我们推荐使用以下工具（可选）：

```bash
# 格式化工具
pip install black isort

# 代码检查
pip install flake8 pylint mypy

# 运行格式化
black harness/
isort harness/

# 运行检查
flake8 harness/
mypy harness/
```

---

## 📝 提交规范

我们使用 [Conventional Commits](https://www.conventionalcommits.org/) 规范。

### 提交消息格式

```
<类型>(<范围>): <简短描述>

<详细描述>

<Footer>
```

### 类型（Type）

| 类型 | 说明 | 示例 |
|------|------|------|
| `feat` | 新功能 | `feat(executor): 添加并行执行模式` |
| `fix` | Bug 修复 | `fix(git): 修复 worktree 路径问题` |
| `docs` | 文档更新 | `docs: 更新 API 参考文档` |
| `style` | 代码格式（不影响逻辑） | `style: 统一缩进为 4 空格` |
| `refactor` | 重构 | `refactor(store): 简化任务存储逻辑` |
| `perf` | 性能优化 | `perf(executor): 优化任务调度算法` |
| `test` | 测试相关 | `test(reviewer): 添加边界情况测试` |
| `build` | 构建系统或依赖 | `build: 升级 anthropic SDK 到 0.49.0` |
| `ci` | CI/CD 配置 | `ci: 添加 Python 3.13 测试` |
| `chore` | 其他杂项 | `chore: 更新 .gitignore` |

### 示例

**简单提交：**
```bash
git commit -m "feat(templates): 添加任务模板系统"
```

**详细提交：**
```bash
git commit -m "feat(templates): 添加任务模板系统

- 新增 templates.py 和 template_loader.py 模块
- 内置 3 种模板：feature、bugfix、refactor
- 支持自定义模板（JSON 格式）
- CLI 命令集成

Closes #123"
```

### 范围（Scope）建议

常用的范围：
- `cli` - CLI 相关
- `executor` - 执行引擎
- `reviewer` - 代码审查
- `planner` - 任务规划
- `git` - Git 集成
- `config` - 配置系统
- `templates` - 模板系统
- `tests` - 测试
- `docs` - 文档

---

## 🔄 Pull Request 流程

### 1. 创建分支

```bash
# 同步上游最新代码
git fetch upstream
git checkout main
git merge upstream/main

# 创建新分支
git checkout -b feature/your-feature-name
# 或
git checkout -b fix/bug-description
```

**分支命名规范：**
- `feature/功能名称` - 新功能
- `fix/bug描述` - Bug 修复
- `docs/文档主题` - 文档更新
- `refactor/模块名` - 重构
- `test/测试内容` - 测试

### 2. 开发和测试

```bash
# 进行开发
# ... 编写代码 ...

# 运行测试
pytest tests/ -v

# 检查覆盖率
pytest tests/ --cov=harness --cov-report=html

# 确保所有测试通过
```

### 3. 提交代码

```bash
# 添加文件
git add <changed-files>

# 提交（遵循提交规范）
git commit -m "feat(module): description"

# 如果需要修改提交信息
git commit --amend
```

### 4. 推送到 GitHub

```bash
# 首次推送
git push -u origin feature/your-feature-name

# 后续推送
git push
```

### 5. 创建 Pull Request

1. 访问你的 Fork 仓库
2. 点击 "Compare & pull request" 按钮
3. 填写 PR 信息（使用下面的模板）
4. 等待代码审查

### PR 模板

```markdown
## 变更说明

简要描述这次改动做了什么。

## 变更类型

- [ ] 🐛 Bug 修复
- [ ] ✨ 新功能
- [ ] 📝 文档更新
- [ ] 🎨 代码重构
- [ ] ⚡ 性能优化
- [ ] ✅ 测试相关

## 关联 Issue

Closes #issue_number

## 改动范围

- 修改的文件/模块
- 影响的功能

## 测试情况

- [ ] 所有现有测试通过
- [ ] 添加了新测试
- [ ] 手动测试通过

## 测试方法

描述如何验证这次改动：

```bash
# 示例命令
harness plan add --template feature
```

## 检查清单

- [ ] 代码遵循项目规范
- [ ] 添加了必要的文档
- [ ] 添加了测试（如果适用）
- [ ] 所有测试通过
- [ ] 提交消息符合规范
- [ ] 更新了 CHANGELOG（如果需要）

## 截图（如果适用）

添加截图或 GIF 展示变更。

## 附加信息

任何其他需要审查者知道的信息。
```

### 6. 代码审查和修改

- 💬 响应审查意见
- ✏️ 根据反馈修改代码
- 🔄 推送更新（自动更新 PR）

```bash
# 进行修改后
git add <files>
git commit -m "fix: 根据审查意见修改"
git push
```

### 7. 合并

审查通过后，维护者会合并你的 PR。恭喜你成为贡献者！🎉

---

## ✅ 测试要求

高质量的测试是项目质量的保证。

### 测试覆盖率要求

- 🎯 **核心模块覆盖率：≥ 90%**
- 📊 **总体覆盖率：≥ 85%**
- ✅ **所有新增代码必须有测试**

### 测试类型

**1. 单元测试**
```python
# 测试单个函数/方法
def test_task_creation():
    """测试任务创建功能"""
    task = Task(
        title="Test Task",
        description="This is a test",
        priority=Priority.REQUIRED
    )
    
    assert task.title == "Test Task"
    assert task.priority == Priority.REQUIRED
    assert task.status == TaskStatus.TODO
```

**2. 集成测试**
```python
# 测试多个组件协作
def test_task_workflow():
    """测试完整任务流程"""
    store = TaskStore()
    task = store.create_task("Feature", "Implement login")
    
    # 执行任务
    result = executor.execute(task)
    
    # 验证结果
    assert result.success
    assert store.get_task(task.id).status == TaskStatus.DONE
```

**3. 端到端测试**
```python
# 测试完整用户场景
def test_cli_workflow(cli_runner):
    """测试 CLI 完整流程"""
    # 添加任务
    result = cli_runner.invoke(cli, ['plan', 'add', '--title', 'Test'])
    assert result.exit_code == 0
    
    # 列出任务
    result = cli_runner.invoke(cli, ['plan', 'list'])
    assert 'Test' in result.output
    
    # 执行任务
    result = cli_runner.invoke(cli, ['plan', 'execute'])
    assert result.exit_code == 0
```

### 测试编写指南

**良好的测试应该：**

✅ **有清晰的名称**
```python
# 好的命名
def test_task_creation_with_empty_title_raises_error():
    pass

# 不好的命名
def test_task1():
    pass
```

✅ **遵循 AAA 模式（Arrange-Act-Assert）**
```python
def test_task_execution():
    # Arrange - 准备
    task = Task("Feature", "Login")
    executor = TaskExecutor()
    
    # Act - 执行
    result = executor.execute(task)
    
    # Assert - 断言
    assert result.success
    assert task.status == TaskStatus.DONE
```

✅ **测试边界条件**
```python
def test_task_with_edge_cases():
    # 空字符串
    with pytest.raises(ValueError):
        Task("", "")
    
    # 超长字符串
    long_title = "x" * 1000
    task = Task(long_title, "Description")
    assert len(task.title) <= 500  # 假设有长度限制
    
    # 特殊字符
    task = Task("Task with émojis 🎉", "描述")
    assert task.title == "Task with émojis 🎉"
```

✅ **使用 Fixtures 复用代码**
```python
import pytest

@pytest.fixture
def task_store():
    """创建测试用的任务存储"""
    store = TaskStore(":memory:")
    yield store
    store.close()

def test_add_task(task_store):
    task = task_store.create_task("Test", "Description")
    assert task.id is not None
```

### 运行测试

```bash
# 运行所有测试
pytest tests/

# 运行特定文件
pytest tests/test_executor.py

# 运行特定测试
pytest tests/test_executor.py::test_task_execution

# 显示详细输出
pytest tests/ -v

# 显示打印输出
pytest tests/ -s

# 生成覆盖率报告
pytest tests/ --cov=harness --cov-report=html

# 并行运行测试（需要 pytest-xdist）
pytest tests/ -n auto
```

### 测试检查清单

提交代码前确保：

- [ ] 所有测试通过
- [ ] 新增代码有对应测试
- [ ] 测试覆盖率达标
- [ ] 没有跳过的测试（除非有充分理由）
- [ ] 测试运行速度合理（单元测试应该很快）

---

## 📚 文档要求

良好的文档让项目更易于使用和维护。

### 文档类型

**1. 代码文档（Docstrings）**

每个公共类、函数、方法都应该有文档字符串：

```python
def execute_task(
    task: Task,
    config: Optional[ExecutorConfig] = None
) -> ExecutionResult:
    """执行单个任务。
    
    这是一个同步执行方法，会阻塞直到任务完成。
    如果需要异步执行，请使用 execute_async 方法。
    
    Args:
        task: 要执行的任务对象
        config: 可选的执行器配置，如果为 None 则使用默认配置
        
    Returns:
        包含执行结果的 ExecutionResult 对象
        
    Raises:
        ExecutionError: 如果任务执行失败
        ValidationError: 如果任务配置无效
        
    Example:
        >>> task = Task("Feature", "Add login")
        >>> result = execute_task(task)
        >>> print(result.success)
        True
        
    See Also:
        - execute_async: 异步执行任务
        - ExecutorConfig: 执行器配置选项
    """
    pass
```

**2. README 和指南**

保持以下文档更新：
- `README.md` - 项目概述
- `docs/quick-start.md` - 快速入门
- `docs/api-reference.md` - API 参考
- `docs/learning-plan.md` - 学习计划
- 阶段完成文档（phase*-completion.md）

**3. 示例代码**

提供可运行的示例：

```python
# examples/basic_usage.py
"""基本使用示例"""

from harness import Harness, Task, Priority

# 创建 Harness 实例
harness = Harness()

# 添加任务
task = harness.plan.add(
    title="实现用户登录",
    description="添加基于邮箱和密码的登录功能",
    priority=Priority.REQUIRED
)

# 执行任务
result = harness.execute(task)

print(f"任务完成: {result.success}")
```

**4. 变更日志**

重大变更应更新 `CHANGELOG.md`：

```markdown
## [0.7.0] - 2026-06-15

### Added
- 新增任务模板系统
- 支持自定义模板

### Changed
- 优化任务执行性能
- 改进错误提示信息

### Fixed
- 修复 Git worktree 路径问题
- 修复配置文件加载 bug

### Deprecated
- `old_method()` 将在 v1.0 中移除，请使用 `new_method()`
```

### 文档编写指南

**清晰简洁：**
- 使用简单的语言
- 避免行话和术语（或提供解释）
- 一个概念一个段落

**提供上下文：**
- 解释"为什么"，不只是"怎么做"
- 说明使用场景
- 提供完整示例

**保持更新：**
- 代码变更时同步更新文档
- 定期审查文档准确性
- 修复文档中的错误

**双语支持：**
- 关键文档提供中英文版本
- 使用清晰的中文（避免生硬翻译）
- 技术术语保留英文原文

### 文档检查清单

- [ ] 所有公共 API 有文档字符串
- [ ] 示例代码可以运行
- [ ] 文档与代码同步
- [ ] 没有错别字和语法错误
- [ ] 链接都有效
- [ ] 截图清晰（如果有）

---

## 👀 代码审查

代码审查帮助我们保持代码质量。

### 审查者关注点

**1. 正确性**
- ✅ 代码是否实现了预期功能？
- ✅ 逻辑是否正确？
- ✅ 边界条件是否处理？
- ✅ 错误处理是否完善？

**2. 代码质量**
- 📐 代码是否遵循项目规范？
- 🎨 命名是否清晰准确？
- 🧹 代码是否整洁易读？
- 🔄 是否有重复代码？

**3. 性能**
- ⚡ 是否有明显的性能问题？
- 💾 内存使用是否合理？
- 🔁 循环和递归是否优化？

**4. 测试**
- ✅ 测试是否充分？
- 🎯 测试是否覆盖关键路径？
- 🐛 测试是否能发现 bug？

**5. 安全**
- 🔒 是否有安全漏洞？
- 🛡️ 输入是否验证？
- 🔐 敏感信息是否保护？

**6. 文档**
- 📝 代码是否有适当注释？
- 📚 文档是否完整？
- 💡 复杂逻辑是否有说明？

### 审查反馈建议

**建设性反馈：**

✅ **好的反馈：**
```
这里建议使用 `with` 语句来管理文件资源，确保文件正确关闭：

```python
with open(path, 'r') as f:
    content = f.read()
```

这样可以避免资源泄漏。
```

❌ **不好的反馈：**
```
这里写错了。
```

**反馈类型标注：**
- 🚨 **必须修复** - 严重问题（bug、安全漏洞）
- ⚠️ **建议修改** - 重要问题（性能、可维护性）
- 💡 **可选优化** - 改进建议（代码风格、优化）
- ❓ **疑问** - 需要澄清的地方

### 作为被审查者

**接受审查反馈时：**
- 🙏 感谢审查者的时间和建议
- 💭 认真考虑反馈意见
- 💬 礼貌地讨论不同观点
- ✏️ 及时响应和修改
- ✅ 修改后回复反馈

**示例回复：**
```
感谢建议！我已经：
1. 使用 with 语句管理文件资源
2. 添加了异常处理
3. 补充了单元测试

请再看一下更新后的代码。
```

---

## 💬 社区交流

我们欢迎你加入社区！

### 交流渠道

**GitHub Discussions**
- 💬 一般讨论和问答
- 💡 功能建议讨论
- 🎓 学习交流
- 📢 公告和更新

**GitHub Issues**
- 🐛 Bug 报告
- ✨ 功能请求
- 📝 文档问题

**邮件**
- 📧 私密问题或合作建议
- 联系维护者

### 提问指南

**好的提问包含：**
1. 📝 清晰的问题描述
2. 🎯 你想要实现什么
3. 🔄 你尝试了什么
4. ❌ 遇到了什么问题
5. 💻 相关环境信息
6. 📋 最小可重现示例（如果适用）

**提问模板：**
```markdown
**我想要实现：**
描述你的目标

**我尝试了：**
1. 步骤 1
2. 步骤 2

**遇到的问题：**
具体的错误信息或行为

**环境信息：**
- OS: Windows 11
- Python: 3.12.0
- 版本: 0.6.0

**代码示例：**
```python
# 最小可重现代码
```
```

### 社区准则

**友善和尊重：**
- 👋 欢迎新手
- 🤝 尊重不同观点
- 💪 鼓励学习和成长
- 🚫 零容忍骚扰和歧视

**有效沟通：**
- 📝 清晰表达
- 🎯 保持主题相关
- 🔍 搜索现有讨论
- 🙏 感谢帮助

---

## 🏆 认可与奖励

我们珍视每一位贡献者！

### 贡献者名单

所有贡献者都会被列入：
- 📜 README.md 贡献者名单
- 🎉 项目发布说明
- 💫 GitHub Contributors 页面

### 贡献类型认可

我们认可各种形式的贡献：
- 💻 代码贡献
- 📝 文档改进
- 🐛 Bug 报告
- 💡 功能建议
- 🎓 教程和示例
- 💬 社区支持
- 🌐 翻译工作

### 特殊认可

**核心贡献者：**
持续做出重大贡献的成员可能被邀请成为核心团队成员，获得：
- ⭐ 仓库写入权限
- 🎯 参与项目决策
- 📋 优先功能开发权
- 🏅 特殊徽章标识

**月度之星：**
每月我们会表彰：
- 🌟 最佳代码贡献
- 📚 最佳文档贡献
- 🆘 最佳社区帮助

---

## 📞 联系我们

### 项目维护者

如果你有任何问题或建议，可以通过以下方式联系我们：

- 📧 **邮箱**: your-email@example.com
- 💬 **GitHub**: [@yourusername](https://github.com/yourusername)
- 🐛 **Issues**: [提交 Issue](https://github.com/yourusername/harness-engineering-study/issues)
- 💭 **Discussions**: [参与讨论](https://github.com/yourusername/harness-engineering-study/discussions)

---

## 📖 相关资源

**项目文档：**
- 📘 [快速入门](docs/quick-start.md)
- 📗 [API 参考](docs/api-reference.md)
- 📙 [学习计划](docs/learning-plan.md)
- 📕 [架构设计](design/mvp-architecture.md)

**开发工具：**
- 🐍 [Python 官方文档](https://docs.python.org/3/)
- 🧪 [pytest 文档](https://docs.pytest.org/)
- 🤖 [Anthropic API](https://docs.anthropic.com/)
- 📦 [pip 包管理](https://pip.pypa.io/)

**学习资源：**
- 📚 [Python 最佳实践](https://docs.python-guide.org/)
- 🎓 [测试驱动开发](https://testdriven.io/)
- 🔧 [Git 协作流程](https://git-scm.com/book/zh/v2)

---

## 🙏 致谢

感谢所有为本项目做出贡献的开发者！

特别感谢：
- 🌟 **核心贡献者** - 持续推动项目发展
- 📝 **文档团队** - 让项目更易于使用
- 🐛 **测试人员** - 帮助发现和修复问题
- 💬 **社区成员** - 提供宝贵的反馈和建议

你的贡献让这个项目变得更好！💙

---

## 📄 许可证

通过贡献代码，你同意你的贡献将在 [MIT License](LICENSE) 下授权。

---

**再次感谢你的贡献！** 🎉

如果你有任何疑问，随时通过 Issues 或 Discussions 与我们联系。

Happy Coding! 💻✨
