from extensions import db
from models import User, AuthRequestPayload, AuthResponsePayload
from werkzeug.security import generate_password_hash, check_password_hash
import re

def validate_password(password):
    """密码强度验证"""
    if len(password) < 6:
        return "密码长度至少 6 位"
    return None

def register_user(username, password, role, user_id=None):
    # 验证必填字段
    if not all([username, role]):
        return AuthResponsePayload(status="error", message="缺少必填字段")
    
    # 验证系统管理员必须提供密码
    if role == 'admin' and not password:
        return AuthResponsePayload(status="error", message="管理员必须设置密码")
    
    # 验证密码强度
    if password:
        pwd_error = validate_password(password)
        if pwd_error:
            return AuthResponsePayload(status="error", message=pwd_error)
        hashed_password = generate_password_hash(password)
    else:
        hashed_password = None
    
    # 检查用户ID或用户名是否已存在
    if user_id and User.query.filter_by(id=user_id).first():
        return AuthResponsePayload(status="error", message="用户ID已存在")
    if User.query.filter_by(username=username).first():
        return AuthResponsePayload(status="error", message="用户名已存在")
    
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
        
        return AuthResponsePayload(
            status="success",
            message="用户注册成功",
            user_id=new_user.id,
            username=new_user.username,
            role=new_user.role
        )
    except Exception as e:
        db.session.rollback()
        return AuthResponsePayload(
            status="error",
            message="注册失败，请重试"
        )

def login_user(identifier, password):
    if not identifier:
        return AuthResponsePayload(status="error", message="请输入用户名或ID")
    
    # 查找用户（按ID或用户名）
    user = User.query.filter((User.id == identifier) | (User.username == identifier)).first()
    
    if not user:
        return AuthResponsePayload(status="error", message="用户不存在")
    
    # 检查密码（如果用户设置了密码）
    if user.password:
        if not check_password_hash(user.password, password):
            return AuthResponsePayload(status="error", message="密码错误")
    # 如果用户没有设置密码，则无需验证（仅限非管理员）
    elif user.role == 'admin':
        return AuthResponsePayload(status="error", message="管理员必须设置密码")
    
    return AuthResponsePayload(
        status="success",
        message="登录成功",
        user_id=user.id,
        username=user.username,
        role=user.role
    )