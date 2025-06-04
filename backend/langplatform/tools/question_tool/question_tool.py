import random
from .. import toolfunc

@toolfunc(
    name="question_tool",
    description="向用户提出问题并模拟选择选项",
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
</question_tool>""",
"""
<question_tool>
<question>你想要通过哪一种架构实现异步操作？</question>
<option1>使用回调函数</option1>
<option2>使用Promise</option2>
<option3>使用async/await</option3>
<option4>使用生成器</option4>
<option5>使用事件驱动</option5>
</question_tool>
"""
    ]
)
def question_tool(option1: str, option2: str, option3: str = None, option4: str = None, option5: str = None):
    # 收集所有非空选项
    options = [option1, option2]
    if option3: options.append(option3)
    if option4: options.append(option4)
    if option5: options.append(option5)
    
    # 随机选择一个选项
    selected = random.choice(options)
    
    # 返回选择的选项内容
    return selected