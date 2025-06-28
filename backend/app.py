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

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# 初始化chat_handler的socketio
from chat_handler import init_socketio
init_socketio(socketio)

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

# 提供临时图片访问
@app.route('/temp/images/<filename>')
def serve_temp_image(filename):
    return send_from_directory(TEMP_IMAGE_DIR, filename)

# 用户会话管理全局变量
user_sid_map = {}  # user_id -> sid
sid_user_map = {}  # sid -> user_id
user_contexts = {}  # user_id -> context

# 身份验证事件
@socketio.on('authenticate')
def handle_authenticate(data):
    try:
        token = data.get('token')
        # 实际应用中应验证token有效性
        user_id = token  # 简化处理，实际应解码token获取用户ID
        sid = request.sid
        
        # 更新映射关系
        user_sid_map[user_id] = sid
        sid_user_map[sid] = user_id
        
        emit('chat_response', {
            "type": "system",
            "content": {"message": "认证成功"}
        })
    except Exception as e:
        app.logger.error(f"认证失败: {str(e)}")
        emit('error', {'message': f'认证失败: {str(e)}'})

# 开始会话事件
@socketio.on('start_conversation')
def handle_start_conversation():
    try:
        sid = request.sid
        user_id = sid_user_map.get(sid)
        if not user_id:
            emit('error', {'message': '用户未认证'})
            return
        
        # 初始化用户上下文
        user_contexts[user_id] = {
            "history": [],
            "agent_state": {}
        }
        
        emit('chat_response', {
            "type": "conversation_status",
            "content": {"status": "started"}
        })
    except Exception as e:
        app.logger.error(f"开始会话失败: {str(e)}")
        emit('error', {'message': f'开始会话失败: {str(e)}'})

# 发送消息事件
@socketio.on('send_message')
def handle_send_message(data):
    try:
        print(f"[INFO] 收到消息: {data}")

        sid = request.sid
        user_id = sid_user_map.get(sid)
        if not user_id:
            socketio.emit('error', {'message': '用户未认证'}, room=sid)
            return
        
        context = user_contexts.get(user_id, {})
        current_text = data.get('current_text', '')
        current_image_paths = data.get('current_image_paths', [])
        
        # 处理用户消息（后续接入Agent）
        from chat_handler import send_text_msg_ws, send_agent_status_ws, send_stop_msg_ws
        send_text_msg_ws(sid, f"收到消息: {current_text}")
        send_agent_status_ws(sid, "processing", "正在处理中...")
        
        # 模拟处理完成
        send_text_msg_ws(sid, "处理完成")
        send_stop_msg_ws(sid)
        
    except Exception as e:
        app.logger.error(f"消息处理失败: {str(e)}")
        socketio.emit('error', {'message': f'消息处理失败: {str(e)}'}, room=sid)

# 结束会话事件
@socketio.on('end_conversation')
def handle_end_conversation():
    try:
        sid = request.sid
        user_id = sid_user_map.get(sid)
        if not user_id:
            emit('error', {'message': '用户未认证'})
            return
        
        # 清理用户上下文
        if user_id in user_contexts:
            del user_contexts[user_id]
        
        emit('chat_response', {
            "type": "conversation_status",
            "content": {"status": "ended"}
        })
    except Exception as e:
        app.logger.error(f"结束会话失败: {str(e)}")
        emit('error', {'message': f'结束会话失败: {str(e)}'})

# 连接断开处理
@socketio.on('disconnect')
def handle_disconnect():
    try:
        sid = request.sid
        user_id = sid_user_map.get(sid)
        if user_id:
            # 清理映射关系
            if user_id in user_sid_map:
                del user_sid_map[user_id]
            if sid in sid_user_map:
                del sid_user_map[sid]
            
            # 清理用户上下文
            if user_id in user_contexts:
                del user_contexts[user_id]
    except Exception as e:
        app.logger.error(f"断开连接处理失败: {str(e)}")

if __name__ == "__main__":
    socketio.run(app, port=7222)