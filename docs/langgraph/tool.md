
工具¶
工具是一种封装函数及其输入模式的方式，可以将其传递给支持工具调用的聊天模型。这允许模型请求以特定输入执行此函数。

您可以定义自己的工具，也可以使用 LangChain 提供的预构建集成。

定义简单工具¶
您可以将普通函数传递给 create_react_agent 作为工具使用。

API 参考：create_react_agent


from langgraph.prebuilt import create_react_agent

def multiply(a: int, b: int) -> int:
    """Multiply two numbers."""
    return a * b

create_react_agent(
    model="anthropic:claude-3-7-sonnet",
    tools=[multiply]
)
create_react_agent 自动将普通函数转换为LangChain 工具。

自定义工具¶
要更好地控制工具行为，请使用 @tool 装饰器。

API 参考：tool


from langchain_core.tools import tool

@tool("multiply_tool", parse_docstring=True)
def multiply(a: int, b: int) -> int:
    """Multiply two numbers.

    Args:
        a: First operand
        b: Second operand
    """
    return a * b
您还可以使用 Pydantic 定义自定义输入模式。


from pydantic import BaseModel, Field

class MultiplyInputSchema(BaseModel):
    """Multiply two numbers"""
    a: int = Field(description="First operand")
    b: int = Field(description="Second operand")

@tool("multiply_tool", args_schema=MultiplyInputSchema)
def multiply(a: int, b: int) -> int:
    return a * b
有关其他自定义设置，请参阅自定义工具指南。

向模型隐藏参数¶
某些工具需要运行时参数（例如，用户 ID 或会话上下文），这些参数不应由模型控制。

您可以将这些参数放入代理的 state 或 config 中，并在工具内部访问此信息。

API 参考：InjectedState | AgentState | RunnableConfig


from langgraph.prebuilt import InjectedState
from langgraph.prebuilt.chat_agent_executor import AgentState
from langchain_core.runnables import RunnableConfig

def my_tool(
    # This will be populated by an LLM
    tool_arg: str,
    # access information that's dynamically updated inside the agent
    state: Annotated[AgentState, InjectedState],
    # access static data that is passed at agent invocation
    config: RunnableConfig,
) -> str:
    """My tool."""
    do_something_with_state(state["messages"])
    do_something_with_config(config)
    ...
禁用并行工具调用¶
一些模型提供商支持并行执行多个工具，但允许用户禁用此功能。

对于支持的提供商，您可以通过 model.bind_tools() 方法设置 parallel_tool_calls=False 来禁用并行工具调用。

API 参考：init_chat_model


from langchain.chat_models import init_chat_model

def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

def multiply(a: int, b: int) -> int:
    """Multiply two numbers."""
    return a * b

model = init_chat_model("anthropic:claude-3-5-sonnet-latest", temperature=0)
tools = [add, multiply]
agent = create_react_agent(
    # disable parallel tool calls
    model=model.bind_tools(tools, parallel_tool_calls=False),
    tools=tools
)

agent.invoke(
    {"messages": [{"role": "user", "content": "what's 3 + 5 and 4 * 7?"}]}
)
直接返回工具结果¶
使用 return_direct=True 可立即返回工具结果并停止代理循环。

API 参考：tool


from langchain_core.tools import tool

@tool(return_direct=True)
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

agent = create_react_agent(
    model="anthropic:claude-3-7-sonnet-latest",
    tools=[add]
)

agent.invoke(
    {"messages": [{"role": "user", "content": "what's 3 + 5?"}]}
)
强制使用工具¶
要强制代理使用特定工具，您可以在 model.bind_tools() 中设置 tool_choice 选项。

API 参考：tool


from langchain_core.tools import tool

@tool(return_direct=True)
def greet(user_name: str) -> int:
    """Greet user."""
    return f"Hello {user_name}!"

tools = [greet]

agent = create_react_agent(
    model=model.bind_tools(tools, tool_choice={"type": "tool", "name": "greet"}),
    tools=tools
)

agent.invoke(
    {"messages": [{"role": "user", "content": "Hi, I am Bob"}]}
)
避免无限循环

在没有停止条件的情况下强制使用工具可能会创建无限循环。请使用以下防护措施之一：

将工具标记为 return_direct=True，以在执行后结束循环。
设置 recursion_limit 以限制执行步骤的数量。
处理工具错误¶
默认情况下，代理将捕获工具调用期间引发的所有异常，并将其作为工具消息传递给 LLM。要控制错误处理方式，您可以通过其 handle_tool_errors 参数使用预构建的 ToolNode（在 create_react_agent 内部执行工具的节点）。


启用错误处理（默认）
禁用错误处理
自定义错误处理

from langgraph.prebuilt import create_react_agent

def multiply(a: int, b: int) -> int:
    """Multiply two numbers."""
    if a == 42:
        raise ValueError("The ultimate error")
    return a * b

# Run with error handling (default)
agent = create_react_agent(
    model="anthropic:claude-3-7-sonnet-latest",
    tools=[multiply]
)
agent.invoke(
    {"messages": [{"role": "user", "content": "what's 42 x 7?"}]}
)

有关不同工具错误处理选项的更多信息，请参阅API 参考。

使用内存¶
LangGraph 允许从工具访问短期和长期内存。有关以下内容的更多信息，请参阅内存指南：

如何从短期内存中读取和写入
如何从长期内存中读取和写入
预构建工具¶
您可以通过将带有工具规范的字典传递给 create_react_agent 的 tools 参数来使用模型提供商的预构建工具。例如，要使用 OpenAI 的 web_search_preview 工具：

API 参考：create_react_agent


from langgraph.prebuilt import create_react_agent

agent = create_react_agent(
    model="openai:gpt-4o-mini", 
    tools=[{"type": "web_search_preview"}]
)
response = agent.invoke(
    {"messages": ["What was a positive news story from today?"]}
)
此外，LangChain 支持广泛的预构建工具集成，用于与 API、数据库、文件系统、网络数据等进行交互。这些工具扩展了代理的功能，并实现了快速开发。

您可以在LangChain 集成目录中浏览可用集成的完整列表。

一些常用的工具类别包括：

搜索：Bing、SerpAPI、Tavily
代码解释器：Python REPL、Node.js REPL
数据库：SQL、MongoDB、Redis
网络数据：网页抓取和浏览
API：OpenWeatherMap、NewsAPI 等
这些集成可以使用上述示例中所示的相同 tools 参数进行配置并添加到您的代理中。

返回顶部
上一页
模型
下一页
MCP 集成
版权所有 © 2025 LangChain, Inc | 同意偏好
使用 Material for MkDocs 制作
