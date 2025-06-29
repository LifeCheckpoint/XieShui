from typing import Annotated, TypedDict, List, Any, Dict, Optional, Generator
import logging
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import BaseTool
from utils.message_utils import send_text_msg, send_agent_msg, send_stop_msg
from models import ChatMessage, ChatResponsePayload, ChatResponseContent, QuestionRequestPayload, AgentStatusContent
from ..llm_manager import llm_manager
from .agent_message_converter import convert_chat_messages_to_langchain_messages
from .agent_response_handler import AgentResponseHandler

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
            llm = llm_manager.get_llm("gemini-2.5-flash")
            
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
        langchain_messages = convert_chat_messages_to_langchain_messages(history, current_text)
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
        response_handler = AgentResponseHandler()
        for s in self.graph.stream(stream_input, config=config):
            logger.info(f"LangGraph stream step output: {s}")
            yield from response_handler.handle_stream_output(s)
        
        yield send_stop_msg() # 任务结束，发送停止消息

async def create_main_agent_graph() -> MainAgentGraph:
    """
    异步创建 MainAgentGraph 实例
    这个函数负责初始化工具，并获取可用的工具。
    """
    try:
        from langplatform.tools import core_tools # 注册工具

        tools = core_tools.tools
        logger.info(f"Successfully retrieved {len(tools)} tools.")
        
        return MainAgentGraph(tools)
    except Exception as e:
        logger.error(f"Error during create_main_agent_graph: {e}", exc_info=True)
        raise # 重新抛出异常，以便上层捕获并处理