# 代码提取器使用指南

## 概述

`CodeBlockExtractor` 是一个健壮的 Markdown 代码块提取器，用于替代脆弱的正则表达式提取。它支持多种编程语言、多代码块、嵌套结构，以及灵活的文件路径指定方式。

## 特性

- ✅ 支持多种编程语言（Python, JavaScript, TypeScript, Java, Go, Rust, Bash 等）
- ✅ 支持语言别名（py → python, js → javascript, ts → typescript）
- ✅ 三种文件路径指定方式
- ✅ 提取所有代码块或按语言过滤
- ✅ 直接写入文件系统
- ✅ 处理空代码块和嵌套结构

## 文件路径指定格式

### 1. 冒号格式（推荐）

```python:src/main.py
def main():
    print("Hello, World!")
```

### 2. 引号格式

```python "test.py"
import unittest
```

### 3. 无路径（仅提取代码）

```python
# 临时代码片段
temp = True
```

## 基本使用

### 提取所有代码块

```python
from harness.code_extractor import extract_code_blocks

markdown_text = """
```python:app.py
def app():
    pass
```

```javascript:script.js
console.log('hello');
```
"""

blocks = extract_code_blocks(markdown_text)

for block in blocks:
    print(f"Language: {block.language}")
    print(f"File: {block.file_path}")
    print(f"Code: {block.code}")
```

### 按语言过滤

```python
# 仅提取 Python 代码块
python_blocks = extract_code_blocks(markdown_text, language="python")
```

### 直接写入文件

```python
from pathlib import Path
from harness.code_extractor import write_code_files

markdown_text = """
```python:src/main.py
def main():
    print("Hello")
```

```python:tests/test_main.py
def test_main():
    assert True
```
"""

# 将所有代码块写入文件
base_dir = Path("./output")
written_files = write_code_files(markdown_text, base_dir)

print(f"写入了 {len(written_files)} 个文件:")
for file_path in written_files:
    print(f"  ✅ {file_path}")
```

## 高级用法

### 使用 CodeBlockExtractor 类

```python
from harness.code_extractor import CodeBlockExtractor

extractor = CodeBlockExtractor()

# 提取所有代码块
all_blocks = extractor.extract_all(markdown_text)

# 提取指定语言
python_blocks = extractor.extract_by_language(markdown_text, "python")

# 仅提取带文件路径的代码块
blocks_with_paths = extractor.extract_with_paths(markdown_text)

# 获取文件映射 {路径: 代码}
files_map = extractor.extract_files_map(markdown_text)

# 写入文件（可选是否覆盖）
written = extractor.write_to_files(
    markdown_text,
    base_dir=Path("./output"),
    overwrite=True  # False 不覆盖已存在的文件
)
```

## 在 WorkerAgent 中的应用

`executor.py` 中的 `WorkerAgent._parse_and_write_files()` 方法使用新的代码提取器：

```python
from harness.code_extractor import CodeBlockExtractor

def _parse_and_write_files(self, response: str, work_dir: str) -> List[str]:
    """解析 AI 响应中的代码块并写入文件"""
    extractor = CodeBlockExtractor()
    
    # 提取所有带文件路径的代码块
    blocks = extractor.extract_with_paths(response)
    
    written = []
    for block in blocks:
        if not block.file_path:
            continue
        
        full_path = Path(work_dir) / block.file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(block.code, encoding='utf-8')
        written.append(str(full_path))
    
    # 如果没有找到带路径的代码块，使用默认文件名
    if not written:
        python_blocks = extractor.extract_by_language(response, 'python')
        if python_blocks:
            default_file = f"task_{self.task.id}_generated.py"
            full_path = Path(work_dir) / default_file
            combined_code = "\n\n".join(block.code for block in python_blocks)
            full_path.write_text(combined_code, encoding='utf-8')
            written.append(str(full_path))
    
    return written
```

## 真实世界示例

### AI 响应解析

```python
ai_response = """
我将为您创建以下文件：

1. 主程序文件

```python:src/main.py
def main():
    print("Hello, World!")

if __name__ == "__main__":
    main()
```

2. 测试文件

```python:tests/test_main.py
import unittest
from src.main import main

class TestMain(unittest.TestCase):
    def test_main(self):
        main()
```

3. 配置文件

```yaml:config.yml
app:
  name: MyApp
  version: 1.0
```

以上就是完整的项目文件。
"""

# 提取所有代码块
blocks = extract_code_blocks(ai_response)
print(f"找到 {len(blocks)} 个代码块")

# 写入文件
written = write_code_files(ai_response, Path("./project"))
print(f"写入了 {len(written)} 个文件")
```

### 混合格式处理

```python
markdown = """
```python:src/app.py
def app():
    pass
```

```python
# 临时代码，不保存到文件
temp = True
```

```python:src/utils.py
def util():
    pass
```
"""

extractor = CodeBlockExtractor()

# 提取所有代码块（包括无路径的）
all_blocks = extractor.extract_all(markdown)
print(f"所有代码块: {len(all_blocks)} 个")  # 输出: 3

# 仅写入带路径的文件
written = extractor.write_to_files(markdown, Path("./output"))
print(f"写入文件: {len(written)} 个")  # 输出: 2
```

## 支持的语言

标准语言标识：
- `python`, `py`
- `javascript`, `js`
- `typescript`, `ts`
- `java`
- `go`
- `rust`
- `bash`, `sh`
- `yaml`, `yml`
- `json`
- `markdown`, `md`
- `sql`
- `html`
- `css`
- `c`, `cpp`
- 以及更多...

## 向后兼容

保留了遗留的正则提取器用于向后兼容：

```python
from harness.code_extractor import LegacyCodeExtractor

# 遗留方法（仅支持 Python 和冒号格式）
blocks = LegacyCodeExtractor.extract_python_blocks(text)
# 返回: [(文件路径 或 None, 代码), ...]
```

## 错误处理

代码提取器是容错的：

- 空代码块 → 返回空字符串
- 无效语言标识 → 保持原样
- 文件路径缺失 → `file_path` 为 `None`
- 目录不存在 → 自动创建
- 编码问题 → 使用 UTF-8

## 测试

运行测试：

```bash
cd harness-mvp
python -m pytest tests/test_code_extractor.py -v
```

测试覆盖率：100%（20 个测试用例）

## 性能对比

| 方法 | 正则表达式 | CodeBlockExtractor |
|------|-----------|-------------------|
| **可靠性** | ⚠️ 脆弱 | ✅ 健壮 |
| **多语言支持** | ❌ 仅 Python | ✅ 所有语言 |
| **路径格式** | 仅冒号 | 三种格式 |
| **嵌套处理** | ❌ 失败 | ✅ 支持 |
| **空代码块** | ❌ 失败 | ✅ 支持 |
| **性能** | 快 | 略慢但可接受 |

## 最佳实践

1. **使用冒号格式指定文件路径**
   ```python:src/main.py
   ```

2. **多文件项目使用目录结构**
   ```python:src/models/user.py
   ```

3. **按语言过滤提升效率**
   ```python
   python_blocks = extractor.extract_by_language(text, "python")
   ```

4. **检查文件路径避免覆盖**
   ```python
   extractor.write_to_files(text, base_dir, overwrite=False)
   ```

## 常见问题

### Q: 如何处理同名文件？

A: 后面的代码块会覆盖前面的。如果需要合并，手动处理 `extract_files_map()`。

### Q: 支持嵌套的代码块吗？

A: 基本支持，但复杂嵌套可能失败。建议避免在代码中使用三个连续反引号。

### Q: 如何提取特定行号的代码块？

A: `CodeBlock` 对象包含 `line_number` 字段，表示在原 Markdown 中的起始行号。

### Q: 性能如何？

A: 对于典型的 AI 响应（<100KB），性能完全足够。大文件（>1MB）可能需要几毫秒。

## 更新日志

### v0.6.1 (2026-06-05)

- ✅ 新增 `CodeBlockExtractor` 类
- ✅ 支持多种编程语言
- ✅ 三种文件路径指定格式
- ✅ 100% 测试覆盖率
- ✅ 集成到 `executor.py`
- ✅ 向后兼容遗留 API

## 相关文档

- [API Reference](api-reference.md)
- [Quick Start](quick-start.md)
- [Executor Architecture](../design/mvp-architecture.md)
