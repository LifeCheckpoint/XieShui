
附加资源
MCP 集成¶
模型上下文协议 (MCP) 是一个开放协议，用于标准化应用程序如何向语言模型提供工具和上下文。LangGraph 代理可以通过 langchain-mcp-adapters 库使用 MCP 服务器上定义的工具。

MCP

安装 langchain-mcp-adapters 库以在 LangGraph 中使用 MCP 工具


pip install langchain-mcp-adapters
使用 MCP 工具¶
langchain-mcp-adapters 包使代理能够使用一个或多个 MCP 服务器上定义的工具。

使用 MCP 服务器上定义的工具的代理

from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent

client = MultiServerMCPClient(
    {
        "math": {
            "command": "python",
            # Replace with absolute path to your math_server.py file
            "args": ["/path/to/math_server.py"],
            "transport": "stdio",
        },
        "weather": {
            # Ensure your start your weather server on port 8000
            "url": "http://localhost:8000/mcp",
            "transport": "streamable_http",
        }
    }
)
tools = await client.get_tools()
agent = create_react_agent(
    "anthropic:claude-3-7-sonnet-latest",
    tools
)
math_response = await agent.ainvoke(
    {"messages": [{"role": "user", "content": "what's (3 + 5) x 12?"}]}
)
weather_response = await agent.ainvoke(
    {"messages": [{"role": "user", "content": "what is the weather in nyc?"}]}
)
自定义 MCP 服务器¶
要创建您自己的 MCP 服务器，您可以使用 mcp 库。该库提供了一种定义工具并将其作为服务器运行的简单方法。

安装 MCP 库


pip install mcp
使用以下参考实现来测试您的代理与 MCP 工具服务器的交互。
数学服务器示例（stdio 传输）

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Math")

@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

@mcp.tool()
def multiply(a: int, b: int) -> int:
    """Multiply two numbers"""
    return a * b

if __name__ == "__main__":
    mcp.run(transport="stdio")
天气服务器示例（可流式 HTTP 传输）

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Weather")

@mcp.tool()
async def get_weather(location: str) -> str:
    """Get weather for location."""
    return "It's always sunny in New York"

if __name__ == "__main__":
    mcp.run(transport="streamable-http")
附加资源¶
MCP 文档
MCP 传输文档
回到顶部
上一个
工具
下一个
上下文
版权所有 © 2025 LangChain, Inc | 同意偏好
使用 Material for MkDocs 制作
