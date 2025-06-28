from langgraph.prebuilt import create_react_agent
from typing import Optional, Any, Union, Tuple
from pathlib import Path
from .. import tool_list
from ..llms import *

class MainAgent:
    """
    主 Agent 类，用于创建和运行主 Agent 实例
    """
    def __init__(self, model: Optional[Any]):
        self.avaliable_tools = [
            "attempt_completion",
            "question_tool",
            "summary",
        ]

        self.tool_description = ""
        for tool in tool_list:
            if tool.name in self.avaliable_tools:
                self.tool_description += f"{tool.tool_description}\n\n"
                
        for tool in self.avaliable_tools:
            if tool not in [t for t in tool_list]:
                print(f"Warning: 工具 {tool} 未在工具列表中定义")

        self.agent_prompt = (Path(__file__).parent / "init_agent_instruction.txt").read_text(encoding="utf-8")
        self.agent_prompt = self.agent_prompt.format(
            TOOLS_DESCRIPTIONS=self.tool_description,
        )

        self.agent = create_react_agent(
            model=model or ModelDeepSeekR1(),
            prompt=self.agent_prompt,
        )

    def run(self, input: str) -> Union[str, Tuple[str, str]]:
        """
        运行 Agent 实例，处理输入并返回结果

        返回结果有以下类型：
        - str: 文本输出
        - Tuple[str, str]: 包含特定信息的输出
        """