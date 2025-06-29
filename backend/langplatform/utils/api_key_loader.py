import os
import json
from pathlib import Path
from typing import Dict, Optional

def load_api_key(provider: str, api_key_file: str = "api_key.json") -> Optional[str]:
    """
    从环境变量或指定的 JSON 文件中加载 API Key。
    优先从环境变量加载，如果环境变量不存在，则尝试从 JSON 文件加载。
    
    Args:
        provider: API Key 的提供商名称（例如 "openrouter", "openai"）。
        api_key_file: 包含 API Key 的 JSON 文件名。
        
    Returns:
        API Key 字符串，如果未找到则返回 None。
    """
    # 尝试从环境变量加载
    env_var_name = f"{provider.upper()}_API_KEY"
    api_key = os.getenv(env_var_name)
    if api_key:
        return api_key

    # 如果环境变量不存在，尝试从 JSON 文件加载
    file_path = Path(__file__).parent.parent / api_key_file
    if file_path.exists():
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                api_keys = json.load(f)
                return api_keys.get(provider)
        except json.JSONDecodeError:
            print(f"Error decoding JSON from {api_key_file}")
            return None
    return None

def get_api_keys_from_file(api_key_file: str = "api_key.json") -> Dict[str, str]:
    """
    从指定的 JSON 文件中获取所有 API Key。
    
    Args:
        api_key_file: 包含 API Key 的 JSON 文件名。
        
    Returns:
        包含所有 API Key 的字典。
    """
    file_path = Path(__file__).parent.parent / api_key_file
    if file_path.exists():
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            print(f"Error decoding JSON from {api_key_file}")
            return {}
    return {}