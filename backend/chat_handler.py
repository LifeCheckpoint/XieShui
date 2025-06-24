from typing import List, Dict, Any, Generator, Optional
from models import (
    ChatResponsePayload, 
    ChatResponseContent, 
    ChatRequestPayload, 
    ChatMessage, 
    WebSocketMessage, 
    QuestionRequestPayload, 
    AgentStatusContent
) # 导入新的模型
from langplatform.agents.main_agent import MainAgentGraph

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
def send_agent_msg(status: str, message: str, current_node: str = None, tool_name: str = None) -> ChatResponsePayload:
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

main_agent_instance = MainAgentGraph() # 实例化主 Agent

def route_chat(
        history: List[ChatMessage],
        current_text: str,
        current_image_paths: List[str],
        thread_id: str = "default_thread", # 添加 thread_id 参数
        resume_data: Optional[Dict[str, Any]] = None # 添加 resume_data 参数
    ) -> Generator[ChatResponsePayload, None, None]:
    """
    ## 路由聊天内容

    所有聊天内容都会被发送到这里进行处理。
    """
    try:
        # 调用主Agent处理上下文
        for response_payload in main_agent_instance.process_chat_request(history, current_text, current_image_paths, thread_id, resume_data):
            yield response_payload
        
    except Exception as e:
        print(f"处理聊天请求时出错: {str(e)}")
        yield send_text_msg(f"处理出错: {str(e)}")