"""AI 客户端 - Anthropic SDK 封装"""
import os
from typing import List, Optional

try:
    import anthropic
except ImportError:
    anthropic = None  # type: ignore[assignment]


class AIClient:
    """封装 Anthropic SDK 调用"""

    def __init__(self, api_key: Optional[str] = None, model: str = "claude-sonnet-4-20250514"):
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY", "")
        if not self.api_key:
            raise ValueError(
                "缺少 Anthropic API 密钥。请设置 ANTHROPIC_API_KEY 环境变量。"
            )
        self.model = model

    def generate_code(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 4096,
    ) -> str:
        """调用 Claude 生成代码

        Args:
            system_prompt: 系统提示词
            user_prompt: 用户提示词
            max_tokens: 最大输出 token 数

        Returns:
            生成的代码文本
        """
        if anthropic is None:
            raise ImportError(
                "缺少 anthropic 包，请运行: pip install anthropic"
            )

        client = anthropic.Anthropic(api_key=self.api_key)
        message = client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )

        content_parts: List[str] = []
        for block in message.content:
            if hasattr(block, "text"):
                content_parts.append(block.text)

        return "\n".join(content_parts)
