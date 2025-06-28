from typing import Annotated, TypedDict, List, Any, Union, Dict, Optional, Generator
import logging
import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient, StdioConnection
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command, Interrupt
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage, BaseMessage
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import BaseTool
from pathlib import Path
from ..llm_manager import llm_manager
from utils.message_utils import send_text_msg, send_agent_msg, send_stop_msg
from models import ChatMessage, ChatResponsePayload, ChatResponseContent, QuestionRequestPayload, AgentStatusContent

logger = logging.getLogger(__name__)

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]

class MainAgentGraph:
    def __init__(self, tools: List[BaseTool]):
        self.langchain_tools = tools
        graph_builder = StateGraph(AgentState)
        graph_builder.add_node("agent", self.agent_node)
        graph_builder.add_node("tools", self.custom_tool_node)
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

    def agent_node(self, state: AgentState):
        try:
            llm = llm_manager.get_llm("deepseek_r1").bind_tools(self.langchain_tools)
            response = llm.invoke(state["messages"])
            logger.info(f"Agent node response: {response}")
            return {"messages": [response]}
        except Exception as e:
            logger.error(f"Error in agent_node: {e}", exc_info=True)
            raise

    def custom_tool_node(self, state: AgentState):
        try:
            tool_output = ToolNode(self.langchain_tools).invoke(state)
            logger.info(f"Tool node output: {tool_output}")
            return tool_output
        except Exception as e:
            logger.error(f"Error in custom_tool_node: {e}", exc_info=True)
            raise

    def process_chat_request(self, history: List[ChatMessage], current_text: str, current_image_paths: List[str], thread_id: str = "default_thread", resume_data: Optional[Dict[str, Any]] = None) -> Generator[ChatResponsePayload, None, None]:
        config = RunnableConfig(configurable={"thread_id": thread_id})
        langchain_messages = []
        for msg in history:
            if msg.role == "user":
                langchain_messages.append(HumanMessage(content=msg.content.get("text", "")))
            elif msg.role == "assistant":
                langchain_messages.append(AIMessage(content=msg.content.get("text", "")))
        
        if current_text:
            langchain_messages.append(HumanMessage(content=current_text))

        if resume_data:
            command = Command(resume=resume_data)
            stream_input = command
        else:
            stream_input = {"messages": langchain_messages}

        logger.info(f"Starting LangGraph stream with input: {stream_input}")
        for s in self.graph.stream(stream_input, config=config):
            logger.info(f"LangGraph stream step output: {s}")
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
                    return

            if "agent" in s:
                yield send_agent_msg("thinking", "Agent 正在思考...", current_node="agent")
            if "tools" in s:
                yield send_agent_msg("tool_calling", "Agent 正在调用工具...", current_node="tools")
            
            if "messages" in s:
                latest_message = s["messages"][-1]
                if isinstance(latest_message, AIMessage):
                    content_to_send = str(latest_message.content) if not isinstance(latest_message.content, str) else latest_message.content
                    yield send_text_msg(content_to_send)
                elif isinstance(latest_message, ToolMessage):
                    yield send_agent_msg("tool_result", f"工具 {latest_message.name} 执行完毕。", tool_name=latest_message.name)
                    content_to_send = str(latest_message.content) if not isinstance(latest_message.content, str) else latest_message.content
                    yield send_text_msg(content_to_send)
        
        yield send_stop_msg()

async def create_main_agent_graph() -> MainAgentGraph:
    """
    异步创建 MainAgentGraph 实例，并从 MCP 服务器获取工具。
    """
    connection = StdioConnection(
        command=["python", "-m", "backend.langplatform.tools.mcp_core_tools"]
    )
    mcp_client = MultiServerMCPClient(connections={"core_tools": connection})
    tools = await mcp_client.get_tools()
    return MainAgentGraph(tools)