"""
启动 XieShui 后端服务

在 backend 目录下使用如下命令
uv run app.py
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
from extensions import db
from auth import register_user, login_user
import traceback

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

if __name__ == "__main__":
    app.run(port=7222)