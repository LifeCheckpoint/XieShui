"""
工作流
"""
from functools import wraps
from typing import List, Dict
from .. import ToolInfo

def workflow(
    name: str,
    description: str = "工作流",
    parameters_description: Dict[str] = {},
    example: List[str] | str = "",
):
    """
    ## 工作流工具装饰器
    
    用于标记函数为工作流工具，同时元数据会被自动生成为文本描述添加到 workflows 字典

    - `name` 参数是工作流的名称，必须唯一
    - `description` 是工作流的描述，用于向 LLM 描述这个工作流的预期作用
    - `parameters_description` 是一个字典，描述工作流的参数及其含义，必须明确
    - `example` 为一个字符串或字符串列表，提供工作流的一个或多个使用示例，格式为 XML 风格标签，可参照如下范例

    工作流工具示例 1：

    ```python
    @workflow(
        name="zhaiyao",
        description="摘要生成工作流",
        parameters_description={
            "text": "(必填) 用户输入的文本",
            "max_len": "(必填) 生成摘要的最大长度，在 10 到 1000 之间",
        },
        example=\"\"\"
            <zhaiyao>
            <text>曾经有座山，山里有个庙...</text>
            <max_len>100</max_len>
            </zhaiyao>
        \"\"\",
    )
    def zhaiyao(model):
        # 工作流逻辑
        ...
    ```

    工作流工具示例 2：
    ```python
    @workflow(
        name="addition",
        description="执行两个数字的加法运算",
        parameters_description={
            "A": "(必填) 数字 A",
            "B": "(必填) 数字 B",
            "C": "(可选) 数字 C",
        },
        example=[
            \"\"\"
                // 执行3和5的加法
                <addition>
                <A>3</A>
                <B>5</B>
                </addition>
            \"\"\",
            \"\"\"
                // 执行10、20和30的加法
                <addition>
                <A>10</A>
                <B>20</B>
                <C>30</C>
                </addition>
            \"\"\",
        ]
    )
    def addition_workflow(A: float, B: float) -> float:
        # 加法工作流
        ...
    """
    from .. import tools
    
    # 检查工作流是否已存在
    if any(workflow.name == name for workflow in tools):
        raise ValueError(f"工作流工具 '{name}' 已经存在")
        
    if isinstance(example, str):
        example = [example]
    
    # 创建工作流描述
    text_description = f"## {name}\nDescription: {description}\n\nParameters:\n" \
        + "\n".join([f"- {key}: {value}" for key, value in parameters_description.items()]) \
        + "\n\nExamples:\n\n" \
        + "\n\n".join([f"Example {i+1}:\n{ex}" for i, ex in enumerate(example)])

    def workflow_deco(f):
        # 创建工作流信息
        workflow_info = ToolInfo(
            name=name,
            tool_type="workflow",
            tool_description=text_description,
            function=f
        )
        tools.append(workflow_info)

        @wraps(f)
        def wrapper(*args, **kwargs):
            return f(*args, **kwargs)
        return wrapper
    
    return workflow_deco