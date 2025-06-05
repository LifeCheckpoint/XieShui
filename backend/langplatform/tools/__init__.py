"""
工具
"""
from functools import wraps
from typing import List, Dict
from .. import ToolInfo

def toolfunc(
    name: str,
    description: str = "工具",
    parameters_description: Dict[str] = {},
    example: List[str] | str = "",
):
    """
    ## 工具装饰器
    
    用于标记函数为工具，同时元数据会被自动生成为文本描述添加到 workflows 字典

    - `name` 参数是工具的名称，必须唯一
    - `description` 是工具的描述，用于向 LLM 描述这个工具的预期作用
    - `parameters_description` 是一个字典，描述工具的参数及其含义，必须明确
    - `example` 为一个字符串或字符串列表，提供工具的一个或多个使用示例，格式为 XML 风格标签，可参照如下范例

    工具示例：

    ```python
    @workflow(
        name="pycode",
        description="Python 执行工具",
        parameters_description={
            "code": "(必填) 要执行的代码",
            "safe": "(可选) 是否信任代码，可选true或false，默认为true",
        },
        example=\"\"\"
            <pycode>
            <code>[1,2].append([3])</code>
            <safe>false</safe>
            </pycode>
        \"\"\",
    )
    def pycode(model):
        # 工具逻辑
        ...
    ```
    """
    from backend.langplatform import tool_list
    
    # 检查工具是否已存在
    if any(toolfunc.name == name for toolfunc in tool_list):
        raise ValueError(f"工具 '{name}' 已经存在")
        
    if isinstance(example, str):
        example = [example]
    
    # 创建工具描述
    text_description = f"## {name}\nDescription: {description}\n\nParameters:\n" \
        + "\n".join([f"- {key}: {value}" for key, value in parameters_description.items()]) \
        + "\n\nExamples:\n\n" \
        + "\n\n".join([f"Example {i+1}:\n{ex}" for i, ex in enumerate(example)])

    def workflow_deco(f):
        # 创建工具信息
        workflow_info = ToolInfo(
            name=name,
            tool_type="toolfunc",
            tool_description=text_description,
            function=f
        )
        tool_list.append(workflow_info)

        @wraps(f)
        def wrapper(*args, **kwargs):
            return f(*args, **kwargs)
        return wrapper
    
    return workflow_deco