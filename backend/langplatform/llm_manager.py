import os
from pathlib import Path
from typing import Dict, Any
from langchain_core.language_models import BaseChatModel
from langchain_openai import ChatOpenAI
from .utils.api_key_loader import load_api_key

class LLMManager:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.models: Dict[str, BaseChatModel] = {}

    def get_llm(self, model_name: str) -> BaseChatModel:
        if model_name not in self.models:
            model_config = self.config.get(model_name)
            if not model_config:
                raise ValueError(f"Model '{model_name}' not found in config")
            
            provider = model_config.get("provider")
            if not provider:
                raise ValueError(f"Model '{model_name}' has no provider defined in config")

            api_key = load_api_key(provider)

            if not api_key:
                raise ValueError(f"API key for provider '{provider}' not found in environment variables or api_key.json")

            base_url = model_config.get("base_url")
            if not base_url:
                raise ValueError(f"Model '{model_name}' has no base_url defined in config")

            self.models[model_name] = ChatOpenAI(
                model=model_config.get("model"),
                temperature=model_config.get("temperature", 0.7),
                base_url=base_url,
                api_key=api_key,
                disable_streaming=True,
            )

        return self.models[model_name]

llm_config = {
    "deepseek-r1": {
        "provider": "openrouter",
        "model": "deepseek/deepseek-r1-0528",
        "base_url": "https://openrouter.ai/api/v1",
        "temperature": 0.25,
    },
    "deepseek-v3": {
        "provider": "openrouter",
        "model": "deepseek/deepseek-chat-v3-0324",
        "base_url": "https://openrouter.ai/api/v1",
        "temperature": 0.25,
    },
    "gemini-2.5-flash": {
        "provider": "openrouter",
        "model": "google/gemini-2.5-flash",
        "base_url": "https://openrouter.ai/api/v1",
        "temperature": 0.55,
    }
}

llm_manager = LLMManager(llm_config)