"""
启动 XieShui 后端服务

在 backend 目录下使用如下命令
uv run app.py
"""
from flask import Flask, request, jsonify, Response, send_from_directory
from flask_cors import CORS
from extensions import db
from auth import register_user, login_user
from image_upload import handle_image_upload
from chat_handler import route_chat
import traceback
import os

app = Flask(__name__)
CORS(app)

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

@app.route("/")
def hello():
    return "Hello, XieShui!"

@app.route("/health")
def health_check():
    return "XieShui Service is running"

# 注册接口
@app.route("/register", methods=["POST"])
def register():
    try:
        return register_user()
    except Exception as e:
        app.logger.error(f"注册失败: {str(e)}")
        app.logger.error(traceback.format_exc())
        return jsonify({
            "status": "error",
            "message": "服务器内部错误"
        }), 500

# 登录接口
@app.route("/login", methods=["POST"])
def login():
    try:
        return login_user()
    except Exception as e:
        app.logger.error(f"登录失败: {str(e)}")
        app.logger.error(traceback.format_exc())
        return jsonify({
            "status": "error",
            "message": "服务器内部错误"
        }), 500

# 图片上传接口
@app.route('/upload_image', methods=['POST'])
def upload_image():
    return handle_image_upload(request)

# 聊天接口（流式响应）
@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        history = data.get('history', [])
        current_text = data.get('current_text', '')
        current_image_paths = data.get('current_image_paths', [])
        
        return Response(
            route_chat(history, current_text, current_image_paths),
            mimetype='text/event-stream'
        )
        
    except Exception as e:
        app.logger.error(f"聊天请求处理失败: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "聊天请求处理失败"
        }), 500

# 提供临时图片访问
@app.route('/temp/images/<filename>')
def serve_temp_image(filename):
    return send_from_directory(TEMP_IMAGE_DIR, filename)

if __name__ == "__main__":
    app.run(port=7222)