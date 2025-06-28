import asyncio
from typing import List, Dict, Any, AsyncGenerator, Optional
from models import (
    ChatResponsePayload,
    ChatResponseContent,
    ChatRequestPayload,
    ChatMessage,
    WebSocketMessage,
    QuestionRequestPayload,
    AgentStatusContent
)
from langplatform.agents.main_agent import MainAgentGraph, create_main_agent_graph
from utils.message_utils import send_text_msg, send_agent_msg, send_stop_msg, debug_output

main_agent_instance: Optional[MainAgentGraph] = None

async def initialize_main_agent():
    global main_agent_instance
    if main_agent_instance is None:
        main_agent_instance = await create_main_agent_graph()

async def route_chat(
        history: List[ChatMessage],
        current_text: str,
        current_image_paths: List[str],
        thread_id: str = "default_thread",
        resume_data: Optional[Dict[str, Any]] = None
    ) -> AsyncGenerator[ChatResponsePayload, None]:
    """
    ## 路由聊天内容

    所有聊天内容都会被发送到这里进行处理。
    """
    try:
        if main_agent_instance is None:
            await initialize_main_agent()
        
        for response_payload in main_agent_instance.process_chat_request(history, current_text, current_image_paths, thread_id, resume_data): # type: ignore
            yield response_payload
        
    except Exception as e:
        print(f"处理聊天请求时出错: {str(e)}")
        yield send_text_msg(f"处理出错: {str(e)}")