import random
from .. import toolfunc
from langgraph.types import interrupt, Command
from langchain_core.tools import InjectedToolCallId
from typing import Annotated

@toolfunc(
    name="question_tool",
    description="向用户提出问题并等待用户选择。Agent 将暂停直到用户提供答案。",
    parameters_description={
        "question": "(必填) 问题内容",
        "option1": "(必填) 第一个选项内容",
        "option2": "(必填) 第二个选项内容",
        "option3": "(可选) 第三个选项内容",
        "option4": "(可选) 第四个选项内容",
        "option5": "(可选) 第五个选项内容"
    },
    example=[
"""<question_tool>
<question>你想要继续当前任务还是切换到新任务？</question>
<option1>继续当前任务</option1>
<option2>切换到新任务</option2>
<option3>请求更多信息</option3>
</question_tool>"""
    ]
)
def question_tool(question: str, option1: str, option2: str, tool_call_id: Annotated[str, InjectedToolCallId], option3: str = None, option4: str = None, option5: str = None):
    options = [option1, option2]
    if option3: options.append(option3)
    if option4: options.append(option4)
    if option5: options.append(option5)
    
    # 触发 LangGraph 的 interrupt
    # 返回一个字典，其中包含问题和选项，以及 tool_call_id
    # 这个字典会被传递给 interrupt 的 data 参数
    return interrupt({"question": question, "options": options, "tool_call_id": tool_call_id})