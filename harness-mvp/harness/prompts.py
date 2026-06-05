"""Prompt 模板 - Worker Agent 代码生成"""
from typing import List

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
