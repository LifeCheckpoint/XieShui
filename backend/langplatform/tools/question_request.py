from typing import Dict, Any, Optional
from langgraph.types import interrupt
from pydantic import BaseModel, Field
from langchain_core.tools import tool

class QuestionRequestSchema(BaseModel):
    """向用户提出问题并等待用户选择。Agent 将暂停直到用户提供答案。"""
    question: str = Field(
        description="要向用户提出的问题。",
        examples=["你喜欢哪种颜色？", "你更喜欢猫还是狗？"]
    )
    option1: str = Field(
        description="第一个选项。",
        examples=["红色", "猫"]
    )
    option2: str = Field(
        description="第二个选项。",
        examples=["蓝色", "狗"]
    )
    option3: Optional[str] = Field(
        description="第三个选项（可选）。",
        examples=["绿色", "兔子"]
    )
    option4: Optional[str] = Field(
        description="第四个选项（可选）。",
        examples=["黄色", "鸟"]
    )
    option5: Optional[str] = Field(
        description="第五个选项（可选）。",
        examples=["紫色", "鱼"]
    )

@tool("question_request", args_schema=QuestionRequestSchema)
def question_tool(question: str, option1: str, option2: str, tool_call_id: str, option3: Optional[str] = None, option4: Optional[str] = None, option5: Optional[str] = None) -> Dict[str, Any]:
    """向用户提出问题并等待用户选择。Agent 将暂停直到用户提供答案。"""
    options = [option1, option2]
    if option3: options.append(option3)
    if option4: options.append(option4)
    if option5: options.append(option5)
    return interrupt({"question": question, "options": options, "tool_call_id": tool_call_id})