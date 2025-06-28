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
from utils.message_utils import send_text_msg, send_agent_msg, send_stop_msg, debug_output

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