
模型¶
本页面描述了如何配置代理使用的聊天模型。

工具调用支持¶
要启用工具调用代理，底层 LLM 必须支持工具调用。

兼容模型可在LangChain 集成目录中找到。

按名称指定模型¶
您可以使用模型名称字符串配置代理


OpenAI
Anthropic
Azure
Google Gemini
AWS Bedrock

import os
from langgraph.prebuilt import create_react_agent

os.environ["OPENAI_API_KEY"] = "sk-..."

agent = create_react_agent(
    model="openai:gpt-4.1",
    # other parameters
)

使用 init_chat_model¶
init_chat_model 工具简化了模型初始化，并提供了可配置参数。


OpenAI
Anthropic
Azure
Google Gemini
AWS Bedrock

pip install -U "langchain[openai]"

import os
from langchain.chat_models import init_chat_model

os.environ["OPENAI_API_KEY"] = "sk-..."

model = init_chat_model(
    "openai:gpt-4.1",
    temperature=0,
    # other parameters
)

请参阅 API 参考了解高级选项。

使用特定提供商的 LLM¶
如果模型提供商无法通过 init_chat_model 获得，您可以直接实例化该提供商的模型类。该模型必须实现 BaseChatModel 接口并支持工具调用。

API 参考：ChatAnthropic | create_react_agent


from langchain_anthropic import ChatAnthropic
from langgraph.prebuilt import create_react_agent

model = ChatAnthropic(
    model="claude-3-7-sonnet-latest",
    temperature=0,
    max_tokens=2048
)

agent = create_react_agent(
    model=model,
    # other parameters
)
说明性示例

上面的示例使用了 ChatAnthropic，它已经被 init_chat_model 支持。显示此模式是为了说明如何手动实例化一个通过 init_chat_model 无法获得的模型。

禁用流式传输¶
要禁用单个 LLM 令牌的流式传输，请在初始化模型时设置 disable_streaming=True。


init_chat_model
ChatModel

from langchain.chat_models import init_chat_model

model = init_chat_model(
    "anthropic:claude-3-7-sonnet-latest",
    disable_streaming=True
)

请参阅 API 参考了解更多关于 disable_streaming 的信息。

添加模型回退¶
您可以使用 model.with_fallbacks([...]) 为不同的模型或不同的 LLM 提供商添加回退。


init_chat_model
ChatModel

from langchain.chat_models import init_chat_model

model_with_fallbacks = (
    init_chat_model("anthropic:claude-3-5-haiku-latest")
    .with_fallbacks([
        init_chat_model("openai:gpt-4.1-mini"),
    ])
)

请参阅此指南了解更多关于模型回退的信息。

其他资源¶
模型集成目录
使用 init_chat_model 进行通用初始化
返回顶部
上一个
流
下一个
工具
Copyright © 2025 LangChain, Inc | 同意偏好
使用 Material for MkDocs 制作
