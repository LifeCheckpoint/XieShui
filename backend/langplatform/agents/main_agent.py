from typing import Annotated, TypedDict, List, Any, Union, Dict, Optional, Generator
import logging # Add this line

logger = logging.getLogger(__name__) # Add this line
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command, Interrupt
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage, BaseMessage
from functools import partial # 导入 partial
from langchain_core.runnables import RunnableLambda, RunnableConfig, Runnable # 导入 Runnable
from langchain_core.tools import Tool # 导入 Tool 类
from pathlib import Path
from ..llms import *
from .. import tool_list, ToolInfo # 导入 ToolInfo
from utils.message_utils import send_text_msg, send_agent_msg, send_stop_msg
from models import ChatMessage, ChatResponsePayload, ChatResponseContent, QuestionRequestPayload, AgentStatusContent # 导入新的模型

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    # 可以添加其他自定义状态，例如：
    # current_task: str
    # tool_output: Any

class MainAgentGraph:
    def __init__(self):
        # 将 tool_list 转换为 LangChain Tool 对象列表
        self.langchain_tools = []
        for t_info in tool_list:
            if t_info.tool_type == "workflow":
                # 对于工作流，t_info.function() 返回一个 Runnable
                self.langchain_tools.append(
                    Tool(
                        name=t_info.name,
                        description=t_info.tool_description,
                        func=t_info.function() # 调用 function 获取 Runnable
                    )
                )
            elif t_info.tool_type == "toolfunc":
                # 对于函数，t_info.function 本身就是可调用的函数
                # 使用 partial 包装，确保它是一个可调用对象
                self.langchain_tools.append(
                    Tool(
                        name=t_info.name,
                        description=t_info.tool_description,
                        func=partial(t_info.function) # 使用 partial 包装
                    )
                )

        graph_builder = StateGraph(AgentState)
        graph_builder.add_node("agent", self.agent_node) # 修改为实例方法
        graph_builder.add_node("tools", self.custom_tool_node) # 修改为实例方法

        graph_builder.add_edge(START, "agent")

        graph_builder.add_conditional_edges(
            "agent",
            tools_condition,
            {
                "tools": "tools",
                END: END
            }
        )
        graph_builder.add_edge("tools", "agent")

        self.graph = graph_builder.compile(checkpointer=MemorySaver())

    def agent_node(self, state: AgentState): # 修改为实例方法
        try:
            llm = ModelDeepSeekR1().bind_tools(self.langchain_tools) # 使用转换后的工具列表
            response = llm.invoke(state["messages"])
            logger.info(f"Agent node response: {response}") # Add log
            return {"messages": [response]}
        except Exception as e:
            logger.error(f"Error in agent_node: {e}", exc_info=True) # Add log
            raise # Re-raise the exception to be caught by route_chat

    def custom_tool_node(self, state: AgentState): # 修改为实例方法
        try:
            tool_output = ToolNode(self.langchain_tools).invoke(state) # 使用转换后的工具列表
            logger.info(f"Tool node output: {tool_output}") # Add log
            return tool_output
        except Exception as e:
            logger.error(f"Error in custom_tool_node: {e}", exc_info=True) # Add log
            raise # Re-raise the exception to be caught by route_chat

    def process_chat_request(self, history: List[ChatMessage], current_text: str, current_image_paths: List[str], thread_id: str = "default_thread", resume_data: Optional[Dict[str, Any]] = None) -> Generator[ChatResponsePayload, None, None]:
        config = RunnableConfig(configurable={"thread_id": thread_id}) # 显式构造 RunnableConfig
        
        # 将 ChatMessage 转换为 LangChain 消息格式
        langchain_messages = []
        for msg in history:
            if msg.role == "user":
                langchain_messages.append(HumanMessage(content=msg.content.get("text", "")))
            elif msg.role == "assistant":
                langchain_messages.append(AIMessage(content=msg.content.get("text", "")))
        
        # 添加当前用户输入
        if current_text: # 只有当有新的文本输入时才添加
            langchain_messages.append(HumanMessage(content=current_text))
        # TODO: 处理图片路径，可能需要自定义工具来处理图片

        # 如果有恢复数据，则构建 Command 对象
        if resume_data:
            command = Command(resume=resume_data)
            stream_input = command
        else:
            stream_input = {"messages": langchain_messages}

        logger.info(f"Starting LangGraph stream with input: {stream_input}") # Add log
        # 迭代 LangGraph 的 stream 输出
        for s in self.graph.stream(stream_input, config=config):
            logger.info(f"LangGraph stream step output: {s}") # Add log
            # 检查是否有中断发生 (例如 question_tool)
            if "__end__" in s and isinstance(s["__end__"], Interrupt):
                interrupt_data = s["__end__"].data
                if "question" in interrupt_data and "options" in interrupt_data:
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

            # 检查是否有 Agent 状态信息 (例如进入某个节点)
            if "agent" in s: # Agent 节点执行
                yield send_agent_msg("thinking", "Agent 正在思考...", current_node="agent")
            if "tools" in s: # 工具节点执行
                yield send_agent_msg("tool_calling", "Agent 正在调用工具...", current_node="tools")
            
            # 提取最新的消息并转换为 ChatResponsePayload
            if "messages" in s:
                latest_message = s["messages"][-1]
                if isinstance(latest_message, AIMessage):
                    # 确保 content 是字符串
                    content_to_send = str(latest_message.content) if not isinstance(latest_message.content, str) else latest_message.content
                    yield send_text_msg(content_to_send)
                elif isinstance(latest_message, ToolMessage):
                    # 工具消息，表示工具执行结果
                    yield send_agent_msg("tool_result", f"工具 {latest_message.name} 执行完毕。", tool_name=latest_message.name)
                    # 确保 content 是字符串
                    content_to_send = str(latest_message.content) if not isinstance(latest_message.content, str) else latest_message.content
                    yield send_text_msg(content_to_send) # 工具的输出内容
                # 其他类型的消息根据需要处理
        
        yield send_stop_msg() # 任务结束