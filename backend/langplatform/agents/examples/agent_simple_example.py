from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.graph.message import add_messages

# 1. 定义状态 (State)
# 我们的状态只包含用户和机器人的消息历史
class State(TypedDict):
    messages: Annotated[list, add_messages]
    # 我们额外添加一个状态来记录是否找到匹配的回复
    found_match: bool

# 2. 定义节点 (Nodes)

# 节点 A: 检查用户输入并尝试匹配规则
def check_rules(state: State):
    user_message = state["messages"][-1].content.lower() # 获取最新一条用户消息
    response = ""
    found = False

    if "你好" in user_message:
        response = "你好！有什么我可以帮忙的吗？"
        found = True
    elif "天气" in user_message:
        response = "抱歉，我不知道今天的天气。"
        found = True
    elif "再见" in user_message:
        response = "再见！很高兴为你服务。"
        found = True

    # 返回状态更新：添加机器人回复（如果找到）和更新 found_match 状态
    updates = {"found_match": found}
    if response:
        updates["messages"] = AIMessage(response)
    return updates

# 节点 B: 处理未匹配规则的情况
def handle_no_match(state: State):
    response = "抱歉，我不明白你的意思。"
    # 返回状态更新：添加默认回复
    return {"messages": [AIMessage(response)], "found_match": False}

# 3. 构建图 (Graph)
graph_builder = StateGraph(State)

# 添加节点
graph_builder.add_node("check_rules", check_rules)
graph_builder.add_node("handle_no_match", handle_no_match)

# 添加边 (Edges)
# 从开始节点到 check_rules 节点
graph_builder.add_edge(START, "check_rules")

# 添加条件边 (Conditional Edges)
# 从 check_rules 节点出发，根据 found_match 的状态决定去向
# 如果 found_match 为 True，则结束 (END)
# 如果 found_match 为 False，则去 handle_no_match 节点
graph_builder.add_conditional_edges(
    "check_rules", # 源节点
    lambda state: "match_found" if state.get("found_match") else "no_match", # 条件函数
    {
        "match_found": END, # 条件为 "match_found" 时，去 END
        "no_match": "handle_no_match" # 条件为 "no_match" 时，去 handle_no_match 节点
    }
)

# 从 handle_no_match 节点到结束节点
graph_builder.add_edge("handle_no_match", END)

# 4. 编译图
graph = graph_builder.compile()

# 5. 运行图
print("简单的规则问答机器人 (输入 'quit' 退出)")
while True:
    user_input = input("你: ")
    if user_input.lower() == 'quit':
        print("机器人: 再见！")
        break

    # 运行图，初始状态包含用户输入
    # 注意：每次运行都是一个新的“线程”或“会话”，状态是独立的
    # 如果需要跨轮次记忆，需要使用 LangGraph 的持久化或内存功能
    initial_state = {"messages": [HumanMessage(user_input)], "found_match": False}
    # 使用 stream 可以看到每一步的状态变化，但这里我们只关心最终结果
    final_state = graph.invoke(initial_state)

    # 打印机器人回复 (最后一条消息)
    print(f"机器人: {final_state["messages"][-1]}")
