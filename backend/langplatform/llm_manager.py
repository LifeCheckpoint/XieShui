import os
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
            
            # 从环境变量加载 API Key
            api_key = os.environ.get(model_config.get("api_key_env"))
            if not api_key:
                raise ValueError(f"API key for model '{model_name}' not found in environment variables")

            self.models[model_name] = init_chat_model(
                model=model_config.get("model"),
                model_provider=model_config.get("provider"),
                temperature=model_config.get("temperature", 0.7),
                # 其他参数...
            )
        return self.models[model_name]

# 示例配置
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
    }
}

llm_manager = LLMManager(llm_config)