from pydantic import BaseModel, Field
from langchain_core.tools import tool

class AttemptCompletionSchema(BaseModel):
    """当任务完成时调用此工具，通知系统任务状态。必须提供状态和消息参数。"""
    status: str = Field(
        description="任务状态，必须是 'success' 或 'failure'。",
        examples=["success", "failure"]
    )
    message: str = Field(
        description="任务状态的描述信息。",
        examples=["已经成功查找到用户所要求的地理位置", "由于信息不足，无法继续进行该有机合成题目的思考"]
    )

@tool("attempt_completion", args_schema=AttemptCompletionSchema)
def attempt_completion(status: str, message: str) -> tuple[str, str]:
    """当任务完成时调用此工具，通知系统任务状态。必须提供状态和消息参数。"""
    return "finish", f"任务完成状态：{status}\n\n{message}"