from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent))

# 导入工具模块以注册工具
from attempt_completion import attempt_completion
from question_request import question_tool

tools = [
    attempt_completion,
    question_tool,
]