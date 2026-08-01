"""代码块提取器 - 健壮的 Markdown 代码提取

替换脆弱的正则表达式提取，使用解析器方式。
支持多种语言、多代码块、嵌套结构。
"""
import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Dict, Tuple


def resolve_output_path(base_dir: Path, file_path: str) -> Path:
    """解析并校验 AI 生成文件的输出路径。

    输出必须位于 ``base_dir`` 内，避免模型返回绝对路径或 ``..``
    路径遍历后覆盖工作目录以外的文件。
    """
    base_path = Path(base_dir).resolve()
    requested_path = Path(file_path)
    if requested_path.is_absolute():
        raise ValueError("生成文件路径必须位于工作目录内")

    output_path = (base_path / requested_path).resolve()
    if not output_path.is_relative_to(base_path):
        raise ValueError("生成文件路径不能逃逸工作目录")

    return output_path


@dataclass
class CodeBlock:
    """代码块数据类"""
    language: str
    code: str
    file_path: Optional[str] = None
    line_number: int = 0
    
    def __repr__(self) -> str:
        path_info = f" -> {self.file_path}" if self.file_path else ""
        return f"CodeBlock({self.language}{path_info}, {len(self.code)} chars)"


class CodeBlockExtractor:
    """代码块提取器
    
    从 Markdown 文本中提取代码块，支持多种格式：
    1. 标准格式: ```python
    2. 带文件路径: ```python:path/to/file.py
    3. 带文件名（引号）: ```python "file.py"
    4. 多语言支持: python, javascript, typescript, java, go, rust, etc.
    """
    
    # 支持的语言别名
    LANGUAGE_ALIASES = {
        'py': 'python',
        'js': 'javascript',
        'ts': 'typescript',
        'sh': 'bash',
        'yml': 'yaml',
        'md': 'markdown',
    }
    
    def __init__(self):
        """初始化提取器"""
        # 匹配代码块的正则：
        # ```语言[:文件路径] [可选引号文件名]
        # 代码内容
        # ```
        self.pattern = re.compile(
            r'```([a-zA-Z0-9_+-]+)'              # 语言标识
            r'(?::(\S+?))?'                       # 可选: :文件路径
            r'(?:\s+["\']([^"\']+)["\'])?'       # 可选: "文件名"
            r'\s*\n'                              # 换行
            r'(.*?)'                              # 代码内容（非贪婪，可为空）
            r'```',                               # 结束标记
            re.DOTALL | re.MULTILINE
        )
    
    def extract_all(self, markdown_text: str) -> List[CodeBlock]:
        """提取所有代码块
        
        Args:
            markdown_text: Markdown 文本
            
        Returns:
            代码块列表
        """
        blocks = []
        current_line = 1
        
        for match in self.pattern.finditer(markdown_text):
            lang = match.group(1)
            file_path_colon = match.group(2)      # :path/to/file
            file_path_quoted = match.group(3)     # "file.py"
            code = match.group(4)
            
            # 标准化语言名称
            lang = self._normalize_language(lang)
            
            # 确定文件路径（优先使用冒号格式）
            file_path = file_path_colon or file_path_quoted
            if file_path:
                file_path = file_path.strip("'\"` ")
            
            # 计算行号（在原文中的位置）
            line_number = markdown_text[:match.start()].count('\n') + 1
            
            blocks.append(CodeBlock(
                language=lang,
                code=code.strip(),
                file_path=file_path,
                line_number=line_number
            ))
        
        return blocks
    
    def extract_by_language(
        self,
        markdown_text: str,
        language: str
    ) -> List[CodeBlock]:
        """提取指定语言的代码块
        
        Args:
            markdown_text: Markdown 文本
            language: 目标语言（python, javascript, etc.）
            
        Returns:
            匹配语言的代码块列表
        """
        all_blocks = self.extract_all(markdown_text)
        language = self._normalize_language(language)
        
        return [
            block for block in all_blocks
            if block.language == language
        ]
    
    def extract_with_paths(self, markdown_text: str) -> List[CodeBlock]:
        """提取带文件路径的代码块
        
        Args:
            markdown_text: Markdown 文本
            
        Returns:
            带文件路径的代码块列表
        """
        all_blocks = self.extract_all(markdown_text)
        return [block for block in all_blocks if block.file_path]
    
    def extract_files_map(self, markdown_text: str) -> Dict[str, str]:
        """提取代码块并按文件路径组织
        
        如果同一文件路径出现多次，后面的会覆盖前面的。
        
        Args:
            markdown_text: Markdown 文本
            
        Returns:
            {文件路径: 代码内容} 字典
        """
        blocks = self.extract_with_paths(markdown_text)
        
        files_map = {}
        for block in blocks:
            if block.file_path:
                files_map[block.file_path] = block.code
        
        return files_map
    
    def write_to_files(
        self,
        markdown_text: str,
        base_dir: Path,
        overwrite: bool = True
    ) -> List[str]:
        """从 Markdown 提取代码并写入文件
        
        Args:
            markdown_text: Markdown 文本
            base_dir: 基础目录
            overwrite: 是否覆盖已存在的文件
            
        Returns:
            写入的文件路径列表
        """
        files_map = self.extract_files_map(markdown_text)
        written = []
        
        for file_path, code in files_map.items():
            full_path = resolve_output_path(base_dir, file_path)
            
            # 检查文件是否存在
            if not overwrite and full_path.exists():
                continue
            
            # 创建目录
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 写入文件
            full_path.write_text(code, encoding='utf-8')
            written.append(str(full_path))
        
        return written
    
    def _normalize_language(self, lang: str) -> str:
        """标准化语言名称
        
        Args:
            lang: 原始语言标识
            
        Returns:
            标准化的语言名称
        """
        lang = lang.lower().strip()
        return self.LANGUAGE_ALIASES.get(lang, lang)


class LegacyCodeExtractor:
    """遗留正则提取器（用于向后兼容）
    
    保留原有的简单正则提取逻辑作为备用方案。
    """
    
    @staticmethod
    def extract_python_blocks(text: str) -> List[Tuple[Optional[str], str]]:
        """提取 Python 代码块（遗留方法）
        
        Args:
            text: Markdown 文本
            
        Returns:
            [(文件路径, 代码)] 列表
        """
        pattern = r'```python(?::(\S+))?\s*\n(.*?)```'
        matches = re.findall(pattern, text, re.DOTALL)
        return [(path or None, code.strip()) for path, code in matches]


def extract_code_blocks(
    markdown_text: str,
    language: Optional[str] = None
) -> List[CodeBlock]:
    """便捷函数：提取代码块
    
    Args:
        markdown_text: Markdown 文本
        language: 可选，指定语言过滤
        
    Returns:
        代码块列表
    """
    extractor = CodeBlockExtractor()
    
    if language:
        return extractor.extract_by_language(markdown_text, language)
    else:
        return extractor.extract_all(markdown_text)


def write_code_files(
    markdown_text: str,
    base_dir: Path,
    overwrite: bool = True
) -> List[str]:
    """便捷函数：从 Markdown 写入代码文件
    
    Args:
        markdown_text: Markdown 文本
        base_dir: 基础目录
        overwrite: 是否覆盖已存在的文件
        
    Returns:
        写入的文件路径列表
    """
    extractor = CodeBlockExtractor()
    return extractor.write_to_files(markdown_text, base_dir, overwrite)
