from mcp.server.fastmcp import FastMCP
from langgraph.types import interrupt
from typing import Optional
from typing import Annotated, List, Dict, Any

mcp_core = FastMCP("CoreTools")

@mcp_core.tool()
def attempt_completion(status: str, message: str) -> tuple[str, str]:
    """当任务完成时调用此工具，通知系统任务状态。必须提供状态和消息参数。"""
    return "finish", f"任务完成状态：{status}\n\n{message}"

@mcp_core.tool()
def question_tool(question: str, option1: str, option2: str, tool_call_id: str, option3: Optional[str] = None, option4: Optional[str] = None, option5: Optional[str] = None) -> Dict[str, Any]:
    """向用户提出问题并等待用户选择。Agent 将暂停直到用户提供答案。"""
    options = [option1, option2]
    if option3: options.append(option3)
    if option4: options.append(option4)
    if option5: options.append(option5)
    return interrupt({"question": question, "options": options, "tool_call_id": tool_call_id})

if __name__ == "__main__":
    mcp_core.run(transport="stdio")