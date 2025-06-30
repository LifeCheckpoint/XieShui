from typing import List
from langchain_core.messages import HumanMessage, AIMessage
from models import ChatMessage

def convert_chat_messages_to_langchain_messages(history: List[ChatMessage], current_text: str) -> List[HumanMessage | AIMessage]:
    """
    将自定义的 ChatMessage 列表转换为 LangChain 消息格式。
    
    Args:
        history: 聊天历史记录，包含 ChatMessage 对象。
        current_text: 当前用户输入的文本。
        
    Returns:
        LangChain 消息格式的列表。
    """
    langchain_messages = []
    for msg in history:
        text_content = msg.content.get("text", "")
        # 过滤掉 Agent 状态消息
        if msg.role == "assistant" and text_content.startswith("Agent 状态:"):
            continue
        
        if msg.role == "user":
            langchain_messages.append(HumanMessage(content=text_content))
        elif msg.role == "assistant":
            langchain_messages.append(AIMessage(content=text_content))
    
    if current_text:
        langchain_messages.append(HumanMessage(content=current_text))
        
    return langchain_messages