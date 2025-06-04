from langchain_core.runnables.base import Runnable
from typing import List, Dict, Union, Callable, Any, Literal
from ..chat_handler import send_agent_msg
from pydantic import BaseModel
from pathlib import Path
import importlib

class ToolInfo(BaseModel):
    """
    工具信息模型
    """
    name: str
    tool_description: str
    tool_type: Literal["workflow", "toolfunc"]
    function: Callable[[], Union[Runnable, str]]

tools: List[ToolInfo] = []
"""
现有工具列表

- 如果为工作流，通过 @workflow 装饰器注册
- 如果为函数，通过 @toolfunc 装饰器注册

列表内容示例：

```python
tools = [
    ToolInfo(
        name="addition",
        tool_type="workflow",
        tool_description=\"\"\"
            ## addition
            Description: 执行两个数字的加法运算
            Parameters:
            - A: (required) 数字 A
            - B: (required) 数字 B

            Examples:

            Example 1:
            // 尝试计算 3 和 5 的和
            <addition>
            <A>3</A>
            <B>5</B>
            </addition>
        \"\"\",
        function=addition_workflow
    ),
    ToolInfo(
        name="subtraction",
        tool_type="function",
        tool_description=\"\"\"
            ## subtraction
            Description: 执行三个数字的减法运算
            Parameters:
            - A: (required) 数字 A
            - B: (required) 数字 B
            - C: (可空) 数字 C

            Examples:

            Example 1:
            // 尝试计算 3-5-2
            <subtraction>
            <A>3</A>
            <B>5</B>
            <C>2</C>
            </subtraction>
        \"\"\",
        function=subtraction_function
    ),
    ...
]
```
"""

def call_tools(call_dict: Dict[str, Union[str, Dict[str, str]]]) -> str:
    """
    调用指定名称的工具，迭代返回状态

    `call_dict` 可以通过 utils.parser.parse_trailing_xml 解析文本，得到位于末尾的命令

    使用方法，在 Agent 中：
    ```python
    yield call_workflows(...)
    ```
    """
    # 从字典中提取工具名称和参数
    name = call_dict.get("name")
    if not name:
        raise ValueError("工具调用字典中缺少 'name' 字段")
    params = call_dict.get("parameters", {})

    for tool in tools:
        if tool.name == name:
            if not tool.function:
                raise ValueError(f"工具 '{name}' 没有定义函数")
            
            # 检查工具类型
            if tool.tool_type == "workflow":
                # 如果是工作流类型，通过 invoke 方法执行
                result = tool.function().invoke(params)

            elif tool.tool_type == "toolfunc":
                # 如果是函数类型，直接调用
                result = tool.function(**params)
            
            return result
    
    raise ValueError(f"未找到名为 '{name}' 的工具")

def set_agent_status(status: str, message: str) -> Callable[[Any], Any]:
    """
    生成 Agent 状态消息，注意这里返回的是提供给 RunnableLambda 的函数

    用法：
    ```python
    RunnableLambda(set_agent_status("Agent 状态", "附加信息"))
    ```
    """
    status_msg = send_agent_msg(status, message)
    print(status_msg)
    ...  # TODO
    return lambda data: data

# 获取当前目录
current_dir = Path(__file__).parent

# 注册workflows模块中的所有工具
workflows_dir = current_dir / "workflows"
if workflows_dir.exists():
    for file in workflows_dir.glob("*.py"):
        if file.name != "__init__.py":
            module_name = f"langplatform.workflows.{file.stem}"
            try:
                importlib.import_module(module_name)
            except ImportError as e:
                print(f"导入工作流模块 {module_name} 失败: {e}")

# 注册tools模块中的所有工具
tools_dir = current_dir / "tools"
if tools_dir.exists():
    for file in tools_dir.glob("*.py"):
        if file.name != "__init__.py":
            module_name = f"langplatform.tools.{file.stem}"
            try:
                importlib.import_module(module_name)
            except ImportError as e:
                print(f"导入工具模块 {module_name} 失败: {e}")
