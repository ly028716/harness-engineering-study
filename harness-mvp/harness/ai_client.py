"""AI 客户端 - Anthropic SDK 封装"""
import os
from pathlib import Path
from typing import List, Optional

try:
    import anthropic
except ImportError:
    anthropic = None  # type: ignore[assignment]


class AIClient:
    """封装 Anthropic SDK 调用"""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY", "")
        if not self.api_key:
            raise ValueError(
                "缺少 Anthropic API 密钥。请设置 ANTHROPIC_API_KEY 环境变量。"
            )
        resolved = model or self._load_model_from_config()
        # 验证模型名称，未知则回退默认
        try:
            from harness.config import ModelName
            ModelName.from_string(resolved)
        except ValueError:
            resolved = "claude-sonnet-4-20250514"
        self.model = resolved

    @staticmethod
    def _load_model_from_config() -> str:
        """从配置加载 AI 模型"""
        try:
            from harness.config import load_config
            config = load_config(Path.cwd() / ".harness")
            return config.ai_model
        except Exception:
            return "claude-sonnet-4-20250514"

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

        try:
            client = anthropic.Anthropic(api_key=self.api_key)
            message = client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}],
            )
        except anthropic.AuthenticationError:
            raise ValueError(
                "Anthropic API 认证失败，请检查 ANTHROPIC_API_KEY 是否有效"
            )
        except anthropic.RateLimitError:
            raise RuntimeError("API 请求超限，请稍后重试")
        except anthropic.APIConnectionError:
            raise RuntimeError("无法连接到 Anthropic API，请检查网络连接")
        except anthropic.APITimeoutError:
            raise RuntimeError("Anthropic API 请求超时，请稍后重试")
        except anthropic.BadRequestError as e:
            raise ValueError(f"API 请求参数错误: {e.message}")
        except anthropic.APIError as e:
            raise RuntimeError(f"Anthropic API 错误: {e.message}")

        content_parts: List[str] = []
        for block in message.content:
            if hasattr(block, "text"):
                content_parts.append(block.text)

        return "\n".join(content_parts)
