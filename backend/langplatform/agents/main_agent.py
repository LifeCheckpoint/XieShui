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
    """
    定义 Agent 的状态。
    LangGraph 的每个节点都会接收并返回这个状态。
    `messages`: 聊天消息列表，使用 `add_messages` 批注，确保消息能够正确地添加到历史记录中。
    """
    messages: Annotated[list, add_messages]
    # 可以添加其他自定义状态，例如：
    # current_task: str
    # tool_output: Any

class MainAgentGraph:
    """
    主 Agent 图，使用 LangGraph 构建。
    负责管理 Agent 的决策流，包括调用 LLM 进行思考和调用工具。
    """
    def __init__(self, tools: List[BaseTool]):
        """
        初始化 MainAgentGraph。
        Args:
            tools: 从 MCP 服务器获取的 LangChain 工具列表。
        """
        self.langchain_tools = tools
        
        # 构建 LangGraph 状态图
        graph_builder = StateGraph(AgentState)
        
        # 添加 Agent 节点：负责 LLM 的思考和决策
        graph_builder.add_node("agent", self.agent_node)
        
        # 添加工具节点：负责执行 Agent 决策调用的工具
        graph_builder.add_node("tools", self.custom_tool_node)
        
        # 定义图的入口点：从 START 节点进入 "agent" 节点
        graph_builder.add_edge(START, "agent")
        
        # 定义条件边：根据 "agent" 节点的输出决定下一步走向
        # 如果 Agent 决定调用工具，则进入 "tools" 节点；否则，结束图的执行。
        graph_builder.add_conditional_edges(
            "agent",
            tools_condition, # LangGraph 预设的工具调用条件函数
            {
                "tools": "tools", # 如果满足工具调用条件，转移到 "tools" 节点
                END: END          # 否则，结束图的执行
            }
        )
        
        # 定义从 "tools" 节点到 "agent" 节点的边：工具执行完毕后，返回 "agent" 节点继续思考
        graph_builder.add_edge("tools", "agent")
        
        # 编译图，并设置检查点（用于保存和恢复 Agent 状态）
        self.graph = graph_builder.compile(checkpointer=MemorySaver())

    def agent_node(self, state: AgentState):
        """
        Agent 节点：负责 LLM 的思考和决策。
        Args:
            state: 当前 Agent 的状态，包含消息历史。
        Returns:
            更新后的 Agent 状态，包含 LLM 的响应。
        """
        try:
            # 获取 LLM 实例并绑定工具
            # LLM 会根据消息历史和可用工具，决定是生成文本响应还是调用工具。
            llm = llm_manager.get_llm("google/gemini-2.5-flash").bind_tools(self.langchain_tools)
            
            # 调用 LLM 处理当前消息历史
            response = llm.invoke(state["messages"])
            
            logger.info(f"Agent node response: {response}")
            
            # 返回 LLM 的响应，更新 Agent 状态中的消息历史
            return {"messages": [response]}
        except Exception as e:
            logger.error(f"Error in agent_node: {e}", exc_info=True)
            raise # 重新抛出异常，由上层调用者处理

    def custom_tool_node(self, state: AgentState):
        """
        工具节点：负责执行 Agent 决策调用的工具。
        Args:
            state: 当前 Agent 的状态，包含工具调用请求。
        Returns:
            更新后的 Agent 状态，包含工具执行结果。
        """
        try:
            # 使用 ToolNode 执行工具调用
            # ToolNode 会解析 LLM 的工具调用请求，并执行相应的工具。
            tool_output = ToolNode(self.langchain_tools).invoke(state)
            
            logger.info(f"Tool node output: {tool_output}")
            
            # 返回工具执行结果，更新 Agent 状态
            return tool_output
        except Exception as e:
            logger.error(f"Error in custom_tool_node: {e}", exc_info=True)
            raise # 重新抛出异常，由上层调用者处理

    def process_chat_request(self, history: List[ChatMessage], current_text: str, current_image_paths: List[str], thread_id: str = "default_thread", resume_data: Optional[Dict[str, Any]] = None) -> Generator[ChatResponsePayload, None, None]:
        """
        处理聊天请求，并以流式方式返回 Agent 的响应。
        Args:
            history: 聊天历史记录。
            current_text: 当前用户输入的文本。
            current_image_paths: 当前用户输入的图片路径列表。
            thread_id: 聊天线程 ID，用于 LangGraph 的检查点。
            resume_data: 如果 Agent 之前被中断，用于恢复状态的数据。
        Yields:
            ChatResponsePayload: 包含文本消息、Agent 状态或问题请求。
        """
        # 配置 LangGraph 的可配置参数，例如线程 ID
        config = RunnableConfig(configurable={"thread_id": thread_id})
        
        # 将 ChatMessage 转换为 LangChain 消息格式
        langchain_messages = []
        for msg in history:
            if msg.role == "user":
                langchain_messages.append(HumanMessage(content=msg.content.get("text", "")))
            elif msg.role == "assistant":
                langchain_messages.append(AIMessage(content=msg.content.get("text", "")))
        
        # 添加当前用户输入到消息历史
        if current_text: # 只有当有新的文本输入时才添加
            langchain_messages.append(HumanMessage(content=current_text))
        # TODO: 处理图片路径，可能需要自定义工具来处理图片

        # 如果有恢复数据，则构建 Command 对象以恢复 LangGraph 的执行
        if resume_data:
            command = Command(resume=resume_data)
            stream_input = command
        else:
            # 否则，以新的消息历史开始 LangGraph 的执行
            stream_input = {"messages": langchain_messages}

        logger.info(f"Starting LangGraph stream with input: {stream_input}")
        
        # 迭代 LangGraph 的 stream 输出
        # LangGraph 会逐步执行图中的节点，并流式返回状态更新。
        for s in self.graph.stream(stream_input, config=config):
            logger.info(f"LangGraph stream step output: {s}")
            
            # 检查是否有中断发生 (例如 question_tool 触发的中断)
            if "__end__" in s and isinstance(s["__end__"], Interrupt):
                interrupt_data = s["__end__"].data
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

            # 检查是否有 Agent 状态信息 (例如进入某个节点)
            if "agent" in s: # Agent 节点执行
                yield send_agent_msg("thinking", "Agent 正在思考...", current_node="agent")
            if "tools" in s: # 工具节点执行
                yield send_agent_msg("tool_calling", "Agent 正在调用工具...", current_node="tools")
            
            # 提取最新的消息并转换为 ChatResponsePayload
            if "messages" in s:
                latest_message = s["messages"][-1]
                if isinstance(latest_message, AIMessage):
                    # 如果是 AI 的文本响应
                    content_to_send = str(latest_message.content) if not isinstance(latest_message.content, str) else latest_message.content
                    yield send_text_msg(content_to_send)
                elif isinstance(latest_message, ToolMessage):
                    # 如果是工具消息，表示工具执行结果
                    yield send_agent_msg("tool_result", f"工具 {latest_message.name} 执行完毕。", tool_name=latest_message.name)
                    # 确保 content 是字符串
                    content_to_send = str(latest_message.content) if not isinstance(latest_message.content, str) else latest_message.content
                    yield send_text_msg(content_to_send) # 工具的输出内容
                # 其他类型的消息根据需要处理
        
        yield send_stop_msg() # 任务结束，发送停止消息

async def create_main_agent_graph() -> MainAgentGraph:
    """
    异步创建 MainAgentGraph 实例，并从 MCP 服务器获取工具。
    这个函数负责初始化 MCP 客户端，连接到工具服务，并获取可用的工具。
    """
    # 获取当前工作目录，用于 MCP 服务器的 cwd 参数
    # .parent.parent.parent.parent 是项目根目录 d:/wroot/XieShui
    cwd = Path(__file__).parent.parent.parent.parent
    logger.info(f"Current MCP connection directory: {cwd}")
    
    # 创建 StdioConnection 配置，用于连接 MCP 工具服务
    # command: 启动 MCP 服务器的命令
    # args: 传递给命令的参数
    # cwd: MCP 服务器的工作目录
    # encoding: 用于标准输入/输出的编码
    connection = StdioConnection(
        command="uv",
        args=["run", "python", "-m", "backend.langplatform.tools.mcp_core_tools"],
        cwd=cwd,
        encoding="utf-8",
    )
    
    # 创建 MultiServerMCPClient 实例，连接到配置的 MCP 工具服务
    mcp_client = MultiServerMCPClient(connections={"core_tools": connection})
    
    # 从 MCP 客户端获取所有可用的工具
    tools = await mcp_client.get_tools()
    
    # 使用获取到的工具列表初始化 MainAgentGraph
    return MainAgentGraph(tools)