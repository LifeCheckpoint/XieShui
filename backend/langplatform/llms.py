"""
LLM 模型基座选择
"""
import json
from pathlib import Path
from langchain_community.chat_models import ChatOpenAI

api_key_path = Path(__file__).parent / "api_key.json"
api_keys = json.load(api_key_path.read_text(encoding="utf-8"))

class ModelDeepSeekV3(ChatOpenAI):
    """
    DeepSeek V3 模型配置
    """
    def __init__(self, temperature: float = 0.25, max_retries: int = 3, max_tokens: int = 8192, **kwargs):
        super().__init__(
            model="deepseek/deepseek-chat-v3-0324",
            base_url="https://openrouter.ai/api/v1",
            api_key=api_keys.get("OpenRouter"),
            temperature=temperature,
            max_retries=max_retries,
            max_tokens=max_tokens,
            **kwargs
        )

class ModelDeepSeekR1(ChatOpenAI):
    """
    DeepSeek R1 模型配置
    """
    def __init__(self, temperature: float = 0.25, max_retries: int = 3, max_tokens: int = 16384, **kwargs):
        super().__init__(
            model="deepseek/deepseek-r1-0528",
            base_url="https://openrouter.ai/api/v1",
            api_key=api_keys.get("OpenRouter"),
            temperature=temperature,
            max_retries=max_retries,
            max_tokens=max_tokens,
            **kwargs
        )
