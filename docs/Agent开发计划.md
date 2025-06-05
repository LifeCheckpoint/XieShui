# LLM Agent 教育助手开发计划

## 目标

开发一个符合教育助手身份、遵循严格输入输出格式、并能动态利用工具的 LLM 主 Agent。

## 核心要求回顾

1.  **Agent 身份**：知识渊博、耐心友好的教育助手。
2.  **用户输入处理**：使用 XML+Markdown 混合结构进行系统注入。
3.  **工具描述**：动态收集所有可用工具的描述并附加到 Agent 提示注入中。
4.  **Agent 输出**：
    *   严格的工具调用格式：必须是输出的末尾，且只能调用一个工具。
    *   提问：遇到问题必须调用 `question_tool`。
    *   任务完成：完成任务后，必须调用新创建的 `attempt_completion` 工具（包含 `status` 和 `message` 参数）。

## 详细计划

1.  **定义 Agent 身份 Prompt (`backend/langplatform/agents/main_agent_instruction.txt`)**
    *   XML + Markdown 混合格式，XML 为大块，用于放置混淆
    *   编辑 `backend/langplatform/agents/main_agent_instruction.txt` 文件，编写清晰、结构化的系统指令。
    *   Prompt 将明确 Agent 的角色是“知识渊博、耐心友好的教育助手”，其目标是帮助用户理解概念、解决问题、提供学习支持。
    *   Prompt 中会包含 Agent 的行为规范，例如鼓励提问、解释复杂概念、提供示例等。

2.  **实现用户输入结构化注入**
    *   修改 `backend/chat_handler.py` 中的 `route_chat` 函数。
    *   在将用户输入传递给主 Agent 之前，将其包装在一个结构化的容器中，例如 `<user_input>` 标签。
    *   同时，将聊天历史（如果存在）也结构化地包含在 Prompt 中，例如使用 `<chat_history>` 标签。
    *   最终传递给 Agent 的 Prompt 将是一个包含系统指令、工具描述、聊天历史和当前用户输入的 XML+Markdown 混合结构。

    ```xml
    <system_instruction>
    你是一个教育助手...
    <available_tools>
    ... 动态注入的工具描述 ...
    </available_tools>
    </system_instruction>

    <chat_history>
    <user>用户消息 1</user>
    <agent>Agent 回复 1</agent>
    ...
    </chat_history>

    <user_input>
    用户当前的输入文本
    </user_input>
    ```

3.  **动态聚合工具描述并注入 Prompt**
    *   在构建 Agent 的输入 Prompt 时，遍历 `backend.langplatform.tools` 列表中注册的所有工具，应该有一个列表标注哪些工具可被使用。
    *   提取每个工具的 `tool_description` 字段。
    *   将这些描���文本拼接起来，并插入到 Agent 系统指令 Prompt 中的 `<available_tools>` 标签内。这样 Agent 在接收输入时就能知道所有可用的工具及其用法。

4.  **明确 Agent 输出格式和工具使用规则**
    *   在 Agent 的系统指令 Prompt （应该尽可能详细！！）中，明确告知 Agent 必须遵循的输出规则：
        *   “你的输出必须以一个且仅一个 XML 格式的工具调用标签结束。”
        *   “如果你需要向用户提问或寻求澄清，请使用 `<question_tool>` 工具，并提供问题和选项。”
        *   “当你认为已经完全理解并处理了用户的请求，任务完成时，请使用 `<attempt_completion>` 工具，并提供任务的状态和消息。”
        *   “除了末尾的工具调用标签，你可以在前面输出解释性文本，但这些文本不应包含其他工具调用标签。”
        *   每一步输出、每一步工具调用，都必须明确指出你的
    *   **创建 `attempt_completion` 工具**
        *   在 `backend/langplatform/tools` 目录下创建一个新的 Python 文件，例如 `completion_tool.py`。
        *   使用 `@toolfunc` 装饰器定义 `attempt_completion` 函数。
        *   该函数将接收 `status` (字符串) 和 `message` (字符串) 作为参数。
        *   这个工具的实现将负责向系统发送任务完成的信号，可能通过调用 `backend.chat_handler.send_stop_msg` 或其他机制，并将 `status` 和 `message` 传递出去。

5.  **实现主 Agent 逻辑 (`backend/langplatform/agents/main_agent.py`)**
    *   编辑 `backend/langplatform/agents/main_agent.py` 文件。
    *   使用 Langchain 或其他框架构建 Agent 逻辑。
    *   Agent 的核心逻辑将接收结构化输入 Prompt，利用 LLM 的能力理解用户意图，并根据意图和可用的工具描述，生成符合指定格式的输出（即末尾的工具调用）。
    *   Agent 需要学习如何根据用户意图选择正确的工具（`question_tool`、`attempt_completion` 或其他业务工具）。
