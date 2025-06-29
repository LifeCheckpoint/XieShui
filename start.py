"""
如果需要手动启动进程排查问题，分别运行：

```bash
uv run python backend/app.py
uv run python backend/websocket_server.py
npm --prefix frontend-react run dev
```
"""

import subprocess
import threading
import os
import sys

def stream_output(name, process):
    """
    实时打印进程的输出。
    """
    if process.stdout:
        for line in process.stdout:
            sys.stdout.write(f"[{name}] {line}")
            sys.stdout.flush()
    process.wait()
    print(f"--- {name} 已退出，返回码: {process.returncode} ---")

if __name__ == "__main__":
    processes = []
    threads = []

    # 启动 WebSocket 服务
    print("--- 启动 WebSocket ---")
    websocket_process = subprocess.Popen(
        ["uv", "run", "python", "backend/websocket_server.py"],
        cwd=os.getcwd(),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        universal_newlines=True,
        shell=False,
        encoding=None # 使用系统默认编码
    )
    processes.append(websocket_process)
    websocket_thread = threading.Thread(target=stream_output, args=("WebSocket", websocket_process))
    threads.append(websocket_thread)
    websocket_thread.start()

    # 启动前端服务
    print("--- 启动 前端 ---")
    frontend_process = subprocess.Popen(
        ["npm", "--prefix", "frontend-react", "run", "dev"],
        cwd=os.getcwd(),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        universal_newlines=True,
        shell=True, # npm 命令需要 shell
        encoding='utf-8'
    )
    processes.append(frontend_process)
    frontend_thread = threading.Thread(target=stream_output, args=("前端", frontend_process))
    threads.append(frontend_thread)
    frontend_thread.start()

    # 等待所有线程完成
    for thread in threads:
        thread.join()

    print("所有服务已停止。")