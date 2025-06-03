"""
启动 XieShui 后端服务

在 backend 目录下使用如下命令
uv run app.py
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
CORS(app)

# 配置SQLite数据库
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# 定义用户模型
class User(db.Model):
    id = db.Column(db.String(20), primary_key=True)  # 学号/ID
    username = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(50))  # 允许为空
    role = db.Column(db.String(20), nullable=False)  # 角色: student, teacher, admin

    def __repr__(self):
        return f'<User {self.username}>'

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
    data = request.json
    user_id = data.get('id')
    username = data.get('username')
    password = data.get('password')
    role = data.get('role')
    
    # 验证系统管理员必须提供密码
    if role == 'admin' and not password:
        return jsonify({"status": "error", "message": "管理员必须设置密码"}), 400
    
    # 检查用户ID或用户名是否已存在
    if User.query.filter_by(id=user_id).first():
        return jsonify({"status": "error", "message": "用户ID已存在"}), 400
    if User.query.filter_by(username=username).first():
        return jsonify({"status": "error", "message": "用户名已存在"}), 400
    
    # 创建新用户
    new_user = User(id=user_id, username=username, password=password, role=role)
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({"status": "success", "message": "用户注册成功"}), 201

# 登录接口
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    identifier = data.get('identifier')  # 可以是ID或用户名
    password = data.get('password')
    
    # 查找用户（按ID或用户名）
    user = User.query.filter((User.id == identifier) | (User.username == identifier)).first()
    
    if not user:
        return jsonify({"status": "error", "message": "用户不存在"}), 401
    
    # 检查密码（如果用户设置了密码）
    if user.password:
        if user.password != password:
            return jsonify({"status": "error", "message": "密码错误"}), 401
    # 如果用户没有设置密码，则无需验证
    
    return jsonify({
        "status": "success",
        "message": "登录成功",
        "user": {
            "id": user.id,
            "username": user.username,
            "role": user.role
        }
    }), 200

if __name__ == "__main__":
    app.run(port=7222)