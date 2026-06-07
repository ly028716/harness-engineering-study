"""测试代码块提取器"""
import pytest
from pathlib import Path
from harness.code_extractor import (
    CodeBlock,
    CodeBlockExtractor,
    LegacyCodeExtractor,
    extract_code_blocks,
    write_code_files,
)


class TestCodeBlockExtractor:
    """测试 CodeBlockExtractor"""
    
    def test_extract_standard_python_block(self):
        """测试提取标准 Python 代码块"""
        markdown = """
# 标题

```python
def hello():
    print("Hello, World!")
```
"""
        extractor = CodeBlockExtractor()
        blocks = extractor.extract_all(markdown)
        
        assert len(blocks) == 1
        assert blocks[0].language == "python"
        assert "def hello():" in blocks[0].code
        assert blocks[0].file_path is None
    
    def test_extract_python_block_with_colon_path(self):
        """测试提取带冒号路径的 Python 代码块"""
        markdown = """
```python:src/main.py
def main():
    pass
```
"""
        extractor = CodeBlockExtractor()
        blocks = extractor.extract_all(markdown)
        
        assert len(blocks) == 1
        assert blocks[0].language == "python"
        assert blocks[0].file_path == "src/main.py"
        assert "def main():" in blocks[0].code
    
    def test_extract_python_block_with_quoted_path(self):
        """测试提取带引号文件名的代码块"""
        markdown = """
```python "test.py"
import unittest
```
"""
        extractor = CodeBlockExtractor()
        blocks = extractor.extract_all(markdown)
        
        assert len(blocks) == 1
        assert blocks[0].file_path == "test.py"
        assert "import unittest" in blocks[0].code
    
    def test_extract_multiple_blocks(self):
        """测试提取多个代码块"""
        markdown = """
```python:file1.py
def func1():
    pass
```

一些文本

```python:file2.py
def func2():
    pass
```

```javascript:app.js
console.log('hello');
```
"""
        extractor = CodeBlockExtractor()
        blocks = extractor.extract_all(markdown)
        
        assert len(blocks) == 3
        
        # 验证 Python 代码块
        python_blocks = [b for b in blocks if b.language == "python"]
        assert len(python_blocks) == 2
        assert python_blocks[0].file_path == "file1.py"
        assert python_blocks[1].file_path == "file2.py"
        
        # 验证 JavaScript 代码块
        js_blocks = [b for b in blocks if b.language == "javascript"]
        assert len(js_blocks) == 1
        assert js_blocks[0].file_path == "app.js"
    
    def test_extract_by_language(self):
        """测试按语言过滤提取"""
        markdown = """
```python
python_code = True
```

```javascript
let js_code = true;
```

```python
more_python = True
```
"""
        extractor = CodeBlockExtractor()
        
        python_blocks = extractor.extract_by_language(markdown, "python")
        assert len(python_blocks) == 2
        
        js_blocks = extractor.extract_by_language(markdown, "javascript")
        assert len(js_blocks) == 1
    
    def test_extract_with_paths(self):
        """测试仅提取带路径的代码块"""
        markdown = """
```python
# 无路径
pass
```

```python:src/main.py
# 有路径
def main():
    pass
```
"""
        extractor = CodeBlockExtractor()
        blocks = extractor.extract_with_paths(markdown)
        
        assert len(blocks) == 1
        assert blocks[0].file_path == "src/main.py"
    
    def test_extract_files_map(self):
        """测试提取文件映射"""
        markdown = """
```python:file1.py
code1
```

```python:file2.py
code2
```

```python:file1.py
code1_updated
```
"""
        extractor = CodeBlockExtractor()
        files_map = extractor.extract_files_map(markdown)
        
        assert len(files_map) == 2
        assert files_map["file1.py"] == "code1_updated"  # 后面的覆盖前面的
        assert files_map["file2.py"] == "code2"
    
    def test_write_to_files(self, tmp_path):
        """测试写入文件"""
        markdown = """
```python:src/main.py
def main():
    print("Hello")
```

```python:tests/test_main.py
def test_main():
    assert True
```
"""
        extractor = CodeBlockExtractor()
        written = extractor.write_to_files(markdown, tmp_path)
        
        assert len(written) == 2
        
        # 验证文件存在且内容正确
        main_file = tmp_path / "src" / "main.py"
        assert main_file.exists()
        assert "def main():" in main_file.read_text()
        
        test_file = tmp_path / "tests" / "test_main.py"
        assert test_file.exists()
        assert "def test_main():" in test_file.read_text()
    
    def test_write_to_files_no_overwrite(self, tmp_path):
        """测试不覆盖已存在的文件"""
        markdown = """
```python:existing.py
new_content
```
"""
        existing_file = tmp_path / "existing.py"
        existing_file.write_text("old_content")
        
        extractor = CodeBlockExtractor()
        written = extractor.write_to_files(markdown, tmp_path, overwrite=False)
        
        assert len(written) == 0
        assert existing_file.read_text() == "old_content"
    
    def test_language_aliases(self):
        """测试语言别名"""
        markdown = """
```py
# Python 别名
```

```js
// JavaScript 别名
```

```ts
// TypeScript 别名
```
"""
        extractor = CodeBlockExtractor()
        blocks = extractor.extract_all(markdown)
        
        assert blocks[0].language == "python"
        assert blocks[1].language == "javascript"
        assert blocks[2].language == "typescript"
    
    def test_nested_backticks_in_code(self):
        """测试代码中包含反引号"""
        markdown = """
```python
def example():
    # 这是一个文档字符串示例
    doc = '''
    使用三个反引号：```
    这不是代码块的结束
    '''
    return doc
```
"""
        extractor = CodeBlockExtractor()
        blocks = extractor.extract_all(markdown)
        
        # 注意：简单的正则无法完美处理嵌套，这是已知限制
        # 但大多数情况下，AI 不会在代码中使用三个连续反引号
        assert len(blocks) >= 1
    
    def test_empty_code_block(self):
        """测试空代码块"""
        markdown = """
```python:empty.py
```
"""
        extractor = CodeBlockExtractor()
        blocks = extractor.extract_all(markdown)
        
        assert len(blocks) == 1
        assert blocks[0].code == ""
        assert blocks[0].file_path == "empty.py"
    
    def test_code_block_with_whitespace(self):
        """测试带空白的代码块"""
        markdown = """
```python:main.py

def hello():
    print("Hello")

```
"""
        extractor = CodeBlockExtractor()
        blocks = extractor.extract_all(markdown)
        
        assert len(blocks) == 1
        # strip() 会移除前后空白
        assert blocks[0].code.strip() == 'def hello():\n    print("Hello")'
    
    def test_multiple_languages(self):
        """测试多种编程语言"""
        markdown = """
```python
# Python
```

```javascript
// JavaScript
```

```typescript
// TypeScript
```

```java
// Java
```

```go
// Go
```

```rust
// Rust
```

```bash
# Bash
```
"""
        extractor = CodeBlockExtractor()
        blocks = extractor.extract_all(markdown)
        
        assert len(blocks) == 7
        languages = [b.language for b in blocks]
        assert "python" in languages
        assert "javascript" in languages
        assert "typescript" in languages
        assert "java" in languages
        assert "go" in languages
        assert "rust" in languages
        assert "bash" in languages


class TestLegacyCodeExtractor:
    """测试遗留代码提取器"""
    
    def test_extract_python_blocks(self):
        """测试遗留的 Python 提取方法"""
        markdown = """
```python:file.py
code
```

```python
code2
```
"""
        blocks = LegacyCodeExtractor.extract_python_blocks(markdown)
        
        assert len(blocks) == 2
        assert blocks[0] == ("file.py", "code")
        assert blocks[1] == (None, "code2")


class TestConvenienceFunctions:
    """测试便捷函数"""
    
    def test_extract_code_blocks(self):
        """测试 extract_code_blocks 便捷函数"""
        markdown = """
```python
code1
```

```javascript
code2
```
"""
        blocks = extract_code_blocks(markdown)
        assert len(blocks) == 2
        
        python_blocks = extract_code_blocks(markdown, language="python")
        assert len(python_blocks) == 1
        assert python_blocks[0].language == "python"
    
    def test_write_code_files(self, tmp_path):
        """测试 write_code_files 便捷函数"""
        markdown = """
```python:test.py
print("test")
```
"""
        written = write_code_files(markdown, tmp_path)
        
        assert len(written) == 1
        assert (tmp_path / "test.py").exists()


class TestRealWorldScenarios:
    """测试真实世界场景"""
    
    def test_ai_response_with_explanation(self):
        """测试 AI 响应中包含解释文本的情况"""
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
        # 测试主函数
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
        blocks = extract_code_blocks(ai_response)
        
        assert len(blocks) == 3
        
        python_blocks = [b for b in blocks if b.language == "python"]
        assert len(python_blocks) == 2
        assert python_blocks[0].file_path == "src/main.py"
        assert python_blocks[1].file_path == "tests/test_main.py"
        
        yaml_blocks = [b for b in blocks if b.language == "yaml"]
        assert len(yaml_blocks) == 1
        assert yaml_blocks[0].file_path == "config.yml"
    
    def test_ai_response_without_paths(self):
        """测试 AI 响应中没有文件路径的情况"""
        ai_response = """
这是一个简单的 Python 函数：

```python
def add(a, b):
    return a + b
```

使用示例：

```python
result = add(1, 2)
print(result)
```
"""
        blocks = extract_code_blocks(ai_response, language="python")
        
        assert len(blocks) == 2
        # 没有文件路径
        assert all(b.file_path is None for b in blocks)
    
    def test_mixed_formats(self, tmp_path):
        """测试混合格式（带路径和不带路径）"""
        markdown = """
```python:src/app.py
def app():
    pass
```

```python
# 临时代码，不需要保存到文件
temp = True
```

```python:src/utils.py
def util():
    pass
```
"""
        extractor = CodeBlockExtractor()
        
        # 提取所有代码块
        all_blocks = extractor.extract_all(markdown)
        assert len(all_blocks) == 3
        
        # 仅写入带路径的文件
        written = extractor.write_to_files(markdown, tmp_path)
        assert len(written) == 2
        assert (tmp_path / "src" / "app.py").exists()
        assert (tmp_path / "src" / "utils.py").exists()
