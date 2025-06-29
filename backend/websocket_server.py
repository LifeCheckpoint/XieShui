import asyncio
import websockets
from typing import Any # 导入 Any
# from websockets.server import WebSocketServerProtocol # 导入 WebSocketServerProtocol
import json
import logging
import os
import traceback
from typing import Dict, Any, Set

# 从现有模块导入必要的函数和模型
from models import (
    WebSocketMessage, AuthRequestPayload, AuthResponsePayload,
    ChatRequestPayload, ChatResponsePayload, ImageUploadRequestPayload,
    ImageUploadResponsePayload, ChatMessage, QuestionRequestPayload, AgentStatusContent
)
from auth import register_user, login_user
from chat_handler import route_chat
from image_upload import handle_image_upload
from extensions import db # 导入数据库实例
from flask import Flask # 仅用于数据库上下文

# 配置日志记录器
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("websocket_server")

# 维护所有连接的客户端
connected_clients: Set[Any] = set()

# 初始化数据库 (需要一个 Flask app context)
# 由于 websockets 服务器是独立的，我们需要手动创建和管理数据库上下文
# 这是一个临时的 Flask app 实例，仅用于初始化 SQLAlchemy
_temp_app = Flask(__name__)
_temp_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
_temp_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(_temp_app)
with _temp_app.app_context():
    db.create_all()
logger.info("Database initialized for websocket server.")

# 创建临时图片目录 (如果不存在)
TEMP_IMAGE_DIR = 'backend/temp/images'
os.makedirs(TEMP_IMAGE_DIR, exist_ok=True)

async def send_message(websocket: Any, message: WebSocketMessage):
    """发送 WebSocket 消息到指定客户端"""
    try:
        message_json = json.dumps(message.model_dump())
        logger.info(f"Sending message to {websocket.remote_address}: {message_json}")
        await websocket.send(message_json)
    except websockets.exceptions.ConnectionClosedOK:
        logger.info(f"Client {websocket.remote_address} disconnected gracefully.")
    except Exception as e:
        logger.error(f"Failed to send message to {websocket.remote_address}: {e}")
        logger.error(traceback.format_exc())

async def handle_auth_request_ws(websocket: Any, payload: AuthRequestPayload):
    """处理认证请求"""
    logger.info(f"Received auth_request: {payload.model_dump()}")
    try:
        with _temp_app.app_context(): # 确保在数据库上下文中执行
            if payload.action == "register":
                response_data = register_user(payload.username, payload.password, payload.role, payload.identifier)
            elif payload.action == "login":
                response_data = login_user(payload.identifier, payload.password)
            else:
                response_data = AuthResponsePayload(status="error", message="无效的认证操作")
        logger.info(f"Emitting auth_response: {response_data.model_dump()}")
        await send_message(websocket, WebSocketMessage(type="auth_response", payload=response_data.model_dump()))
    except Exception as e:
        logger.error(f"认证请求处理失败: {str(e)}")
        logger.error(traceback.format_exc())
        await send_message(websocket, WebSocketMessage(type="error", payload={"message": f"认证失败: {str(e)}"}))

async def handle_chat_request_ws(websocket: Any, payload: ChatRequestPayload):
    """处理聊天请求"""
    try:
        thread_id = payload.thread_id if payload.thread_id is not None else "default_thread"
        resume_data = payload.resume_data

        with _temp_app.app_context(): # 确保在数据库上下文中执行
            async for response_payload in route_chat(payload.history, payload.current_text, payload.current_image_paths, thread_id, resume_data):
                logger.info(f"Emitting chat_response: {response_payload.model_dump()}")
                await send_message(websocket, WebSocketMessage(type="chat_response", payload=response_payload.model_dump()))
    except Exception as e:
        logger.error(f"聊天请求处理失败: {str(e)}")
        logger.error(traceback.format_exc())
        await send_message(websocket, WebSocketMessage(type="error", payload={"message": f"服务器内部错误: {str(e)}"}))

async def handle_image_upload_request_ws(websocket: Any, payload: ImageUploadRequestPayload):
    """处理图片上传请求"""
    try:
        response_data = handle_image_upload(payload.filename, payload.image_data)
        logger.info(f"Emitting image_upload_response: {response_data.model_dump()}")
        await send_message(websocket, WebSocketMessage(type="image_upload_response", payload=response_data.model_dump()))
    except Exception as e:
        logger.error(f"图片上传请求处理失败: {str(e)}")
        logger.error(traceback.format_exc())
        await send_message(websocket, WebSocketMessage(type="error", payload={"message": f"图片上传失败: {str(e)}"}))

async def handle_health_check_ws(websocket: Any):
    """处理健康检查请求"""
    logger.info(f"Emitting health_check_response")
    await send_message(websocket, WebSocketMessage(type="health_check_response", payload={"status": "XieShui Service is running"}))

async def websocket_handler(websocket: Any):
    """处理单个 WebSocket 连接"""
    connected_clients.add(websocket)
    logger.info(f"Client {websocket.remote_address} connected. Total clients: {len(connected_clients)}")
    try:
        # 模拟 Flask-SocketIO 的 connect 事件
        # app.logger.info("Client connected")
        # 在连接建立后，可以发送一些初始消息或进行认证
        # 或者等待前端发送认证消息

        async for message_str in websocket:
            logger.info(f"Received message from {websocket.remote_address}: {message_str}")
            try:
                data = json.loads(message_str)
                ws_message = WebSocketMessage.model_validate(data)
                logger.info(f"Parsed WebSocketMessage type: {ws_message.type}")

                if ws_message.type == "auth_request":
                    logger.info(f"Handling auth_request from {websocket.remote_address}")
                    await handle_auth_request_ws(websocket, AuthRequestPayload.model_validate(ws_message.payload))
                elif ws_message.type == "chat_request":
                    logger.info(f"Handling chat_request from {websocket.remote_address}")
                    await handle_chat_request_ws(websocket, ChatRequestPayload.model_validate(ws_message.payload))
                elif ws_message.type == "image_upload_request":
                    logger.info(f"Handling image_upload_request from {websocket.remote_address}")
                    await handle_image_upload_request_ws(websocket, ImageUploadRequestPayload.model_validate(ws_message.payload))
                elif ws_message.type == "health_check":
                    logger.info(f"Handling health_check from {websocket.remote_address}")
                    await handle_health_check_ws(websocket)
                else:
                    logger.info(f"Emitting error for unknown message type: {ws_message.type}")
                    await send_message(websocket, WebSocketMessage(type="error", payload={"message": f"未知消息类型: {ws_message.type}"}))

            except json.JSONDecodeError:
                logger.error(f"Invalid JSON received from {websocket.remote_address}: {message_str}")
                await send_message(websocket, WebSocketMessage(type="error", payload={"message": "无效的 JSON 格式"}))
            except Exception as e:
                logger.error(f"WebSocket消息处理失败 for {websocket.remote_address}: {str(e)}")
                logger.error(traceback.format_exc())
                await send_message(websocket, WebSocketMessage(type="error", payload={"message": f"服务器内部错误: {str(e)}"}))
    except websockets.exceptions.ConnectionClosedOK:
        logger.info(f"Client {websocket.remote_address} disconnected gracefully.")
    except Exception as e:
        logger.error(f"WebSocket connection error for {websocket.remote_address}: {e}")
        logger.error(traceback.format_exc())
    finally:
        connected_clients.remove(websocket)
        logger.info(f"Client {websocket.remote_address} disconnected. Total clients: {len(connected_clients)}")

async def main():
    """启动 WebSocket 服务器"""
    # 确保数据库上下文在服务器启动前被激活一次，以便 db.create_all() 能够执行
    with _temp_app.app_context():
        pass # 确保上下文被激活

    port = 7223 # WebSocket 服务器端口，与 Flask HTTP 服务器区分开
    logger.info(f"WebSocket server is starting on ws://localhost:{port}")
    async with websockets.serve(websocket_handler, "localhost", port):
        logger.info("WebSocket server started. Press Ctrl+C to exit.")
        await asyncio.Future() # Run forever

if __name__ == "__main__":
    asyncio.run(main())