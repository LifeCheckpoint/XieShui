# WebSocket 迁移计划：使用独立 `websockets` 库

## 核心思路

我们将把 WebSocket 服务从 Flask 应用中剥离出来，作为一个独立的 Python 进程运行，使用 `websockets` 库来处理所有的 WebSocket 连接和消息。Flask 应用将继续处理传统的 HTTP 请求。

## 架构图

```mermaid
graph TD
    subgraph Frontend
        A[Web Browser] -->|HTTP Request| B(Flask Backend)
        A -->|WebSocket Connection| C(Standalone WebSocket Server)
    end

    subgraph Backend Services
        B(Flask Backend)
        C(Standalone WebSocket Server)
        D[Database (SQLite)]
        E[Image Storage (backend/temp/images)]
    end

    C -->|Calls Python Functions| F{Auth, Chat, Image Upload Logic}
    F --> D
    F --> E
    B --> D
    B --> E
```

## 详细计划步骤

1.  **环境准备**:
    *   确保您的 Python 环境中安装了 `websockets` 库。如果未安装，需要执行 `pip install websockets`。

2.  **创建独立的 WebSocket 服务器文件**:
    *   在 `backend` 目录下创建一个新的 Python 文件，命名为 `websocket_server.py`。
    *   这个文件将包含 `websockets` 服务器的启动逻辑和所有 WebSocket 消息处理逻辑。

3.  **迁移 WebSocket 消息处理逻辑**:
    *   将 `backend/app.py` 中所有 `@socketio.on` 装饰器下的函数（`handle_connect`, `handle_message`, `handle_auth_request`）及其内部逻辑，迁移到 `websocket_server.py` 中。
    *   这些函数需要修改以适应 `websockets` 库的 API。例如，`emit('message', ...)` 将被替换为 `await websocket.send(json.dumps(...))`。
    *   需要维护一个全局的 `connected_clients` 集合（或字典），用于存储所有活跃的 WebSocket 连接，以便服务器可以向特定客户端发送消息。

4.  **重构认证、聊天和图片上传逻辑**:
    *   `auth.py` 中的 `register_user` 和 `login_user` 函数可以保持不变。
    *   `chat_handler.py` 和 `image_upload.py` 中的核心逻辑也可以保持不变。
    *   `websocket_server.py` 将负责从客户端接收请求，调用这些处理函数，并将结果通过 WebSocket 发送回客户端。

5.  **修改 `backend/app.py`**:
    *   移除所有 `flask_socketio` 相关的导入和代码（包括 `SocketIO` 的初始化和所有 `@socketio.on` 装饰器）。
    *   保留 Flask 的 HTTP 路由（例如 `/temp/images/<filename>`）。
    *   `app.py` 将只作为传统的 HTTP 服务器运行。

6.  **修改前端 `frontend-react/src/hooks/useWebSocket.js`**:
    *   将 WebSocket 连接的 URL 更新，指向新的独立 WebSocket 服务器的地址和端口（例如，如果 WebSocket 服务器运行在 `ws://localhost:7223`，则修改连接字符串）。

7.  **修改启动方式**:
    *   由于现在有两个独立的服务器（Flask HTTP 服务器和 `websockets` 服务器），您需要同时启动它们。
    *   最简单的方式是创建两个独立的启动命令，分别运行 `backend/app.py` (作为 Flask 应用) 和 `backend/websocket_server.py` (作为 WebSocket 服务器)。
    *   或者，可以编写一个主脚本，使用 `asyncio.gather` 或 `subprocess` 同时启动这两个服务。