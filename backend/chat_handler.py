from typing import List, Dict, Any
from models import ChatResponsePayload, ChatResponseContent, ChatRequestPayload, ChatMessage

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
def send_agent_msg(status: str, message: str) -> ChatResponsePayload:
    """
    生成 Agent 状态消息
    """
    return ChatResponsePayload(
        type="agent_status",
        content=ChatResponseContent(status=status, message=message)
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

def route_chat(
        history: List[ChatMessage],
        current_text: str,
        current_image_paths: List[str]
    ) -> List[ChatResponsePayload]:
    """
    ## 路由聊天内容

    所有聊天内容都会被发送到这里进行处理。
    """
    try:
        # 构建LangChain兼容的上下文
        # langchain_context = {
        #     "history": [
        #         {
        #             "role": msg.role,
        #             "content": msg.content.get("text", "")
        #         }
        #         for msg in history
        #     ],
        #     "current_input": {
        #         "text": current_text,
        #         "images": current_image_paths
        #     }
        # }
        
        # 这里将调用主Agent处理上下文
        # agent_response = main_agent.process(langchain_context)
        # yield agent_response
        
        # 临时示例响应
        yield send_text_msg("LangChain上下文已构建，等待主Agent实现")
    except Exception as e:
        print(f"处理聊天请求时出错: {str(e)}")
        yield send_text_msg(f"处理出错: {str(e)}")