from .. import toolfunc
from backend.chat_handler import send_stop_msg

@toolfunc(
    name="attempt_completion",
    description="当任务完成时调用此工具，通知系统任务状态。必须提供状态和消息参数。",
    parameters_description={
        "status": "(必填) 任务状态 (success/error/warning)",
        "message": "(必填) 完成任务的详细消息或详细错误信息，要求能够涵盖刚才所有任务的内容，并且能够让系统理解任务的完成情况。",
    },
    example=[
"""<attempt_completion>
<status>success</status>
<message>我已经阅读了您指定的 `backend/langplatform` 目录下的所有文件以及 `backend/chat_handler.py `文件，并对您系统的工作方式进行了分析和推断。

系统核心组件和结构如下：

backend/langplatform/__init__.py: 定义了工具和工作流的注册机制和调用分发器。
backend/langplatform/llms.py: 负责配置和实例化 LLM 模型。
backend/langplatform/tools/__init__.py: 定义了 @toolfunc 装饰器，用于注册工具函数。
backend/langplatform/tools/question_tool/question_tool.py: 实现了 question_tool 工具，用于模拟向用户提问。</message>
</attempt_completion>
""",
"""// 用户试图查找地理资料并要求根据本地知识库提供详细数据，但知识库中没有相关资料，因此任务没有继续进行的必要
<attempt_completion>
<status>error</status>
<message>依照读取的文件，我已经查找如下网络资料：

- `加利福尼亚州红木国家公园`： 尤罗克人通过传统的红木独木舟旅游分享他们的文化和与土地的联系。

- `蒙大拿州冰川国家公园`： 黑脚人通过太阳之旅分享他们对公园的理解和管理，并努力让更多黑脚族人了解和认同公园是他们的。

- `阿拉斯加科迪亚克岛`： 阿鲁蒂克人通过科迪亚克棕熊中心控制叙事，分享他们与野生动物和生态系统的深层联系，并通过旅游收入支持社区发展。

但是知识库中没有任何相关的资料，我无法进一步提供其详细信息，因此任务未能成功执行。

如果希望能够继续进行任务，您可能需要提供更多相关的地理资料或指定其他主题。
</message>
"""
    ]

)
def attempt_completion(status: str, message: str):
    return ("finish", f"任务完成状态：{status}\n\n{message}")