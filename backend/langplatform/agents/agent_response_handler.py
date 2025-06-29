from typing import Any, Dict, Generator
from langgraph.types import Interrupt
from langchain_core.messages import AIMessage, ToolMessage
from models import ChatResponsePayload, ChatResponseContent, QuestionRequestPayload
from utils.message_utils import send_text_msg, send_agent_msg, send_stop_msg

class AgentResponseHandler:
    """
    处理 LangGraph 的流式输出，并将其转换为 ChatResponsePayload。
    """
    def handle_stream_output(self, stream_output: Dict[str, Any]) -> Generator[ChatResponsePayload, None, None]:
        """
        处理 LangGraph 的单个流式输出步骤。
        
        Args:
            stream_output: LangGraph 的单个流式输出步骤的字典。
            
        Yields:
            ChatResponsePayload: 包含文本消息、Agent 状态或问题请求。
        """
        # 检查是否有中断发生 (例如 question_tool 触发的中断)
        if "__end__" in stream_output and isinstance(stream_output["__end__"], Interrupt):
            interrupt_data = stream_output["__end__"].data
            if "question" in interrupt_data and "options" in interrupt_data:
                # 如果是问题请求中断，则生成 ChatResponsePayload 返回给前端
                yield ChatResponsePayload(
                    type="question_request",
                    content=ChatResponseContent(
                        question_payload=QuestionRequestPayload(
                            question=interrupt_data["question"],
                            options=interrupt_data["options"],
                            tool_call_id=interrupt_data.get("tool_call_id")
                        )
                    )
                )
                return # 暂停处理，等待用户响应

        # 检查流输出中是否有节点名称
        for node_name, node_output in stream_output.items():
            if node_name == "__end__":
                continue # 跳过结束标记

            # 发送节点状态消息
            if node_name == "agent":
                yield send_agent_msg("thinking", "Agent 正在思考...", current_node="agent")
            elif node_name == "tools":
                yield send_agent_msg("tool_calling", "Agent 正在调用工具...", current_node="tools")

            # 检查节点输出中是否有消息
            if isinstance(node_output, dict) and "messages" in node_output:
                latest_message = node_output["messages"][-1]
                
                # 添加日志以检查消息类型和内容
                print(f"DEBUG: latest_message type: {type(latest_message)}")
                print(f"DEBUG: latest_message content: {latest_message.content}")

                if isinstance(latest_message, AIMessage):
                    # 如果是 AI 的文本响应
                    content_to_send = str(latest_message.content) if not isinstance(latest_message.content, str) else latest_message.content
                    print(f"DEBUG: Yielding text message: {content_to_send}")
                    yield send_text_msg(content_to_send)
                elif isinstance(latest_message, ToolMessage):
                    # 如果是工具消息，表示工具执行结果
                    print(f"DEBUG: Yielding tool result message for tool: {latest_message.name}")
                    yield send_agent_msg("tool_result", f"工具 {latest_message.name} 执行完毕。", tool_name=latest_message.name)
                    # 确保 content 是字符串
                    content_to_send = str(latest_message.content) if not isinstance(latest_message.content, str) else latest_message.content
                    print(f"DEBUG: Yielding text message for tool output: {content_to_send}")
                    yield send_text_msg(content_to_send) # 工具的输出内容
                    
                    # 检查是否是 attempt_completion 工具的返回，如果是，则停止对话
                    if latest_message.name == "attempt_completion" and isinstance(latest_message.content, str):
                        print("DEBUG: Attempt completion tool called. Sending stop message.")
                        yield send_stop_msg()
                        return # 停止处理，因为对话已完成
                else:
                    print(f"DEBUG: Unhandled message type: {type(latest_message)}")
                # 其他类型的消息根据需要处理