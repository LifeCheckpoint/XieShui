import json
from typing import List

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
def send_agent_msg(status: str, message: str):
    """
    生成 Agent 状态消息

    使用方式：
    ```python
    yield set_agent_status("Agent 状态", "附加信息")
    ```
    """
    event = {
        "type": "agent_status",
        "content": {"status": status, "message": message}
    }
    return "data: " + json.dumps(event) + "\n\n"

@debug_output
def send_text_msg(text: str):
    """
    生成文本消息

    使用方式：
    ```python
    yield set_text("文本内容")
    ```
    """
    event = {
        "type": "text",
        "content": {"data": text}
    }
    return "data: " + json.dumps(event) + "\n\n"

@debug_output
def send_stop_msg(reason: str = "normal"):
    """
    生成停止消息

    使用方式：
    ```python
    yield set_stop("中止原因")
    ```
    """
    event = {
        "type": "stop",
        "content": {"reason": reason}
    }
    return "data: " + json.dumps(event) + "\n\n"

def route_chat(
        history: List,
        current_text: str,
        current_image_paths: List
    ):
    """
    ## 路由聊天内容

    所有聊天内容都会被发送到这里进行处理。
    """
    def generate():
        try:
            # 构建LangChain兼容的上下文
            # langchain_context = {
            #     "history": [
            #         {
            #             "role": "user" if msg.get("position") == "right" else "assistant",
            #             "content": msg["content"]["text"] if msg["type"] == "text" else ""
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
            print(f"生成SSE流时出错: {str(e)}")
            yield send_text_msg(f"处理出错: {str(e)}")
    
    return generate()