"""Prompt 模板 - Worker Agent 代码生成"""
from typing import List

AI_PLAN_SYSTEM_PROMPT = """你是一个专业的项目计划 Agent。你的职责是根据用户需求生成项目计划。

请分析用户需求，并将其分解为具体的任务。每个任务包含以下字段：

- id: 整数，任务序号（从 1 开始）
- title: 字符串，任务标题
- description: 字符串，任务描述
- priority: 字符串，可选值 REQUIRED / RECOMMENDED / OPTIONAL
- estimated_effort: 整数，工作量估算（1-5）
- dependencies: 整数数组，依赖的任务 ID 列表
- acceptance_criteria: 字符串数组，验收标准列表

以 JSON 格式返回完整计划：

{
    "goal": "项目目标",
    "tasks": [
        {
            "id": 1,
            "title": "任务标题",
            "description": "任务描述",
            "priority": "REQUIRED",
            "estimated_effort": 3,
            "dependencies": [],
            "acceptance_criteria": ["验收标准1", "验收标准2"]
        }
    ]
}

要求：
1. 任务应该有合理的依赖关系
2. 核心基础任务设为 REQUIRED，增强功能设为 RECOMMENDED
3. 只返回 JSON，不要包含其他内容"""


WORKER_SYSTEM_PROMPT = """你是一个专业的软件开发 Agent。你的职责是根据任务描述生成可直接运行的代码。

## 核心原则

1. **只生成要求的代码** — 不要添加任务范围外的功能
2. **代码必须完整可运行** — 包含必要的 import、类型注解、错误处理
3. **遵循项目语言的最佳实践** — Python 遵循 PEP 8，使用类型注解
4. **生成可测试的代码** — 函数/类职责单一，便于单元测试
5. **处理边界情况** — 空值、异常输入、错误路径

## 输出格式

用代码块包裹生成的代码，每个文件一个代码块：

```python:path/to/file.py
# 文件内容
```

如果不需要创建文件（已有代码只需修改），用 diff 格式说明变更。
"""


def build_work_prompt(
    task_title: str,
    task_description: str,
    acceptance_criteria: List[str],
    dependencies: List[int],
) -> str:
    """构建 Worker 任务提示词

    Args:
        task_title: 任务标题
        task_description: 任务描述
        acceptance_criteria: 验收标准列表
        dependencies: 依赖的任务 ID 列表

    Returns:
        格式化的提示词
    """
    parts = [f"# 任务：{task_title}", ""]

    if task_description:
        parts.append(f"## 描述\n{task_description}\n")

    if acceptance_criteria:
        parts.append("## 验收标准")
        for i, criterion in enumerate(acceptance_criteria, 1):
            parts.append(f"{i}. {criterion}")
        parts.append("")

    if dependencies:
        parts.append(f"## 前置依赖\n此任务依赖任务 {dependencies} 的输出，请确保使用已完成的接口。\n")

    parts.append("## 要求")
    parts.append("1. 生成实现上述验收标准的完整代码")
    parts.append("2. 包含必要的 import 语句")
    parts.append("3. 添加类型注解")
    parts.append("4. 处理异常和边界情况")
    parts.append("5. 代码块格式：```python:<path>")

    return "\n".join(parts)
