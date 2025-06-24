"""
启动 XieShui 后端服务

在 backend 目录下使用如下命令
uv run app.py
"""
from flask import Flask, request, jsonify, Response, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from extensions import db
from auth import register_user, login_user
from image_upload import handle_image_upload
from chat_handler import route_chat
import traceback
import os
from models import WebSocketMessage, AuthRequestPayload, AuthResponsePayload, ChatRequestPayload, ChatResponsePayload, ImageUploadRequestPayload, ImageUploadResponsePayload, ChatMessage, QuestionRequestPayload, AgentStatusContent # 导入新的模型

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# 配置SQLite数据库
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 初始化数据库
db.init_app(app)

# 创建数据库表
with app.app_context():
    db.create_all()

# 创建临时图片目录
TEMP_IMAGE_DIR = 'backend/temp/images'
os.makedirs(TEMP_IMAGE_DIR, exist_ok=True)

@socketio.on('message')
def handle_message(data):
    try:
        ws_message = WebSocketMessage.parse_obj(data)
        
        if ws_message.type == "auth_request":
            auth_payload: AuthRequestPayload = ws_message.payload
            if auth_payload.action == "register":
                response_data = register_user(auth_payload.username, auth_payload.password)
            elif auth_payload.action == "login":
                response_data = login_user(auth_payload.username, auth_payload.password)
            else:
                response_data = AuthResponsePayload(status="error", message="无效的认证操作")
            emit('message', WebSocketMessage(type="auth_response", payload=response_data.model_dump()).model_dump())

        elif ws_message.type == "chat_request":
            chat_payload: ChatRequestPayload = ws_message.payload
            # 从 chat_payload 中获取 thread_id 和 resume_data
            thread_id = chat_payload.thread_id
            resume_data = chat_payload.resume_data

            for response_payload in route_chat(chat_payload.history, chat_payload.current_text, chat_payload.current_image_paths, thread_id, resume_data):
                emit('message', WebSocketMessage(type="chat_response", payload=response_payload.model_dump()).model_dump())

        elif ws_message.type == "image_upload_request":
            image_payload: ImageUploadRequestPayload = ws_message.payload
            response_data = handle_image_upload(image_payload.filename, image_payload.image_data)
            emit('message', WebSocketMessage(type="image_upload_response", payload=response_data.model_dump()).model_dump())
        
        elif ws_message.type == "health_check":
            emit('message', WebSocketMessage(type="health_check_response", payload={"status": "XieShui Service is running"}).model_dump())

        else:
            emit('message', WebSocketMessage(type="error", payload={"message": "未知消息类型"}).model_dump())

    except Exception as e:
        app.logger.error(f"WebSocket消息处理失败: {str(e)}")
        app.logger.error(traceback.format_exc())
        emit('message', WebSocketMessage(type="error", payload={"message": f"服务器内部错误: {str(e)}"}).model_dump())

# 提供临时图片访问 (此路由可以保留，因为它是静态文件服务，不涉及业务逻辑)
@app.route('/temp/images/<filename>')
def serve_temp_image(filename):
    return send_from_directory(TEMP_IMAGE_DIR, filename)

if __name__ == "__main__":
    socketio.run(app, port=7222)