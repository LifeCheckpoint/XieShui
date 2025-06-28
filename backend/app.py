"""
启动 XieShui 后端服务

在 backend 目录下使用如下命令
uv run app.py
"""
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from extensions import db
from auth import register_user, login_user
from image_upload import handle_image_upload
from chat_handler import send_text_msg_ws, send_agent_status_ws, send_stop_msg_ws
import traceback
import os
from models import AuthRequestPayload, AuthResponsePayload, ChatRequestPayload, ChatResponsePayload, ImageUploadRequestPayload, ImageUploadResponsePayload, ChatMessage, QuestionRequestPayload, AgentStatusContent # 导入新的模型

import logging # 导入 logging 模块

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# 初始化chat_handler的socketio
from chat_handler import init_socketio
init_socketio(socketio)

# 配置日志记录器
app.logger.setLevel(logging.INFO) # 设置日志级别为 INFO
handler = logging.StreamHandler() # 创建一个 StreamHandler，用于输出到控制台
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
app.logger.addHandler(handler)

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


# 提供临时图片访问 (此路由可以保留，因为它是静态文件服务，不涉及业务逻辑)
@app.route('/temp/images/<filename>')
def serve_temp_image(filename):
    return send_from_directory(TEMP_IMAGE_DIR, filename)

if __name__ == "__main__":
    app.logger.info("Flask HTTP server is starting...")
    app.logger.info(f"Listening on port 7222. CORS is enabled for all origins.")
    app.run(port=7222, debug=False)