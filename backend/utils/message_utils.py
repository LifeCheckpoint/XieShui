from typing import List, Dict, Any, Generator, Optional
from models import (
    ChatResponsePayload, 
    ChatResponseContent, 
    AgentStatusContent
)

using_debug = False

def debug_output(func):
    """
    装饰器，用于在调试模式下 debug 调用
    """
    def wrapper(*args, **kwargs):
        if not using_debug:
            return func(*args, **kwargs)
        else:
            print(f"CALL: {func.__name__}, ARGS: {args}, {kwargs}")
            result = func(*args, **kwargs)
            print(f"FROM {func.__name__} RETURN: {result}")
            return result
    return wrapper

@debug_output
def send_agent_msg(status: str, message: str, current_node: Optional[str] = None, tool_name: Optional[str] = None) -> ChatResponsePayload:
    """
    生成 Agent 状态消息
    """
    return ChatResponsePayload(
        type="agent_status",
        content=ChatResponseContent(
            agent_status_content=AgentStatusContent(
                status=status,
                message=message,
                current_node=current_node,
                tool_name=tool_name
            )
        )
    )

@debug_output
def send_text_msg(text: str) -> ChatResponsePayload:
    """
    生成文本消息
    """
    return ChatResponsePayload(
        type="text",
        content=ChatResponseContent(data=text)
    )

@debug_output
def send_stop_msg(reason: str = "normal") -> ChatResponsePayload:
    """
    生成停止消息
    """
    return ChatResponsePayload(
        type="stop",
        content=ChatResponseContent(reason=reason)
    )