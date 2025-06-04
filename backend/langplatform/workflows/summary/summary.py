from pathlib import Path
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from ...workflows import workflow # 导入工作流装饰器
from ... import set_agent_status # 导入设置 Agent 状态的函数
from ...llms import ModelDeepSeekV3 # 导入我们要用到的模型

@workflow(
    name="summary_workflow",
    description="创建基于学科特点的文本总结工作流",
    parameters_description={
        "text": "(必填) 待总结文本"
    },
    example=[
"""<summary_workflow>
<text>前面我们讨论的都是在函数连续、单调等情况下的解。但如果函数f(x)可以不连续，甚至可以极其“不规则”呢？...</text>
</summary_workflow>""",
"""<summary_workflow>
<text>...我们通常将人类的发展历史分为以下四种阶段...</text>
</summary_workflow>"""
    ]
)
def create_summary_workflow():
    # 提示词模板
    feature_prompt = PromptTemplate.from_file(Path("subject_features.txt"), encoding="utf-8") # 有字段 "feature"
    summary_prompt = PromptTemplate.from_file(Path("summary_text.txt"), encoding="utf-8") # 有字段 "text" 和 "feature"
    
    # 提取特征并生成摘要
    feature_extraction = (
        RunnablePassthrough()
        | RunnableLambda(set_agent_status("摘要生成", "提取学科特征"))
        | feature_prompt
        | ModelDeepSeekV3()
        | StrOutputParser()
    )
    workflow = (
        {
            "feature": feature_extraction, 
            "text": RunnablePassthrough()
        }
        | RunnableLambda(set_agent_status("摘要生成", "生成文本摘要"))
        | summary_prompt
        | ModelDeepSeekV3()
        | StrOutputParser()
    )
    
    return workflow