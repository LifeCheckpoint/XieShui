import os
from pathlib import Path
from typing import Dict, Any
from langchain_core.language_models import BaseChatModel
from langchain.chat_models import init_chat_model

class LLMManager:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.models: Dict[str, BaseChatModel] = {}

    def get_llm(self, model_name: str) -> BaseChatModel:
        if model_name not in self.models:
            model_config = self.config.get(model_name)
            if not model_config:
                raise ValueError(f"Model '{model_name}' not found in config")
            
            # 从文件加载 API Key
            file = Path(__file__).parent / "api_key.json"
            if file.exists():
                import json
                with open(file, 'r') as f:
                    api_keys = json.load(f)
            else:
                api_keys = {}
            
            # 检查是否有对应模型的 API Key
            api_key = api_keys.get("openrouter", None) # TODO 不同供应商

            if not api_key:
                raise ValueError(f"API key for model '{model_name}' not found in environment variables")

            self.models[model_name] = init_chat_model(
                model=model_config.get("model"),
                model_provider=model_config.get("provider"),
                temperature=model_config.get("temperature", 0.7),
                api_key=api_key,
            )
        return self.models[model_name]

llm_config = {
    "deepseek_r1": {
        "provider": "openrouter",
        "model": "deepseek/deepseek-r1-0528",
        "api_key_env": "OPENROUTER_API_KEY",
        "temperature": 0.25,
    },
    "deepseek_v3": {
        "provider": "openrouter",
        "model": "deepseek/deepseek-chat-v3-0324",
        "api_key_env": "OPENROUTER_API_KEY",
        "temperature": 0.25,
    },
    "gemini_2.5_flash": {
        "provider": "openrouter",
        "model": "google/gemini-2.5-flash",
        "api_key_env": "OPENROUTER_API_KEY",
        "temperature": 0.55,
    }
}

llm_manager = LLMManager(llm_config)