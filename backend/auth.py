from flask import request, jsonify
from extensions import db
from models import User
from werkzeug.security import generate_password_hash, check_password_hash
import re

def validate_password(password):
    """密码强度验证"""
    if len(password) < 6:
        return "密码长度至少 6 位"
    # if not re.search(r"[A-Z]", password):
    #     return "密码必须包含大写字母"
    # if not re.search(r"[a-z]", password):
    #     return "密码必须包含小写字母"
    # if not re.search(r"\d", password):
    #     return "密码必须包含数字"
    # if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
    #     return "密码必须包含特殊字符"
    return None

def register_user():
    data = request.json
    user_id = data.get('id')
    username = data.get('username')
    password = data.get('password')
    role = data.get('role')
    
    # 验证必填字段
    if not all([user_id, username, role]):
        return jsonify({"status": "error", "message": "缺少必填字段"}), 400
    
    # 验证系统管理员必须提供密码
    if role == 'admin' and not password:
        return jsonify({"status": "error", "message": "管理员必须设置密码"}), 400
    
    # 验证密码强度
    if password:
        pwd_error = validate_password(password)
        if pwd_error:
            return jsonify({"status": "error", "message": pwd_error}), 400
        hashed_password = generate_password_hash(password)
    else:
        hashed_password = None
    
    # 检查用户ID或用户名是否已存在
    if User.query.filter_by(id=user_id).first():
        return jsonify({"status": "error", "message": "用户ID已存在"}), 400
    if User.query.filter_by(username=username).first():
        return jsonify({"status": "error", "message": "用户名已存在"}), 400
    
    try:
        # 创建新用户
        new_user = User(
            id=user_id,
            username=username,
            password=hashed_password,
            role=role
        )
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify({
            "status": "success",
            "message": "用户注册成功",
            "user": {
                "id": user_id,
                "username": username,
                "role": role
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "status": "error",
            "message": "注册失败，请重试"
        }), 500

def login_user():
    data = request.json
    identifier = data.get('identifier')  # 可以是ID或用户名
    password = data.get('password')
    
    if not identifier:
        return jsonify({"status": "error", "message": "请输入用户名或ID"}), 400
    
    # 查找用户（按ID或用户名）
    user = User.query.filter((User.id == identifier) | (User.username == identifier)).first()
    
    if not user:
        return jsonify({"status": "error", "message": "用户不存在"}), 401
    
    # 检查密码（如果用户设置了密码）
    if user.password:
        if not check_password_hash(user.password, password):
            return jsonify({"status": "error", "message": "密码错误"}), 401
    # 如果用户没有设置密码，则无需验证（仅限非管理员）
    elif user.role == 'admin':
        return jsonify({"status": "error", "message": "管理员必须设置密码"}), 401
    
    return jsonify({
        "status": "success",
        "message": "登录成功",
        "user": {
            "id": user.id,
            "username": user.username,
            "role": user.role
        }
    }), 200