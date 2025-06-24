from extensions import db
from pydantic import BaseModel
from typing import Union, List, Dict, Any, Optional

class User(db.Model):
    id = db.Column(db.String(20), primary_key=True)  # 学号/ID
    username = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(255))  # 扩展长度以存储哈希密码
    role = db.Column(db.String(20), nullable=False)  # 角色: student, teacher, admin

    def __repr__(self):
        return f'<User {self.username}>'

# Pydantic Models for WebSocket Communication
class AuthRequestPayload(BaseModel):
    action: str # "register" or "login"
    username: str
    password: str

class AuthResponsePayload(BaseModel):
    status: str # "success" or "error"
    message: str
    token: Optional[str] = None
    user_id: Optional[str] = None
    username: Optional[str] = None
    role: Optional[str] = None

class ChatMessage(BaseModel):
    role: str
    content: Dict[str, Any]

class ChatRequestPayload(BaseModel):
    history: List[ChatMessage]
    current_text: str
    current_image_paths: List[str]

class ChatResponseContent(BaseModel):
    data: Optional[str] = None
    status: Optional[str] = None
    message: Optional[str] = None
    reason: Optional[str] = None

class ChatResponsePayload(BaseModel):
    type: str # "text", "agent_status", "stop"
    content: ChatResponseContent

class ImageUploadRequestPayload(BaseModel):
    filename: str
    image_data: str # Base64 encoded image data

class ImageUploadResponsePayload(BaseModel):
    status: str
    message: str
    image_path: Optional[str] = None

class WebSocketMessage(BaseModel):
    type: str
    payload: Union[
        AuthRequestPayload,
        AuthResponsePayload,
        ChatRequestPayload,
        ChatResponsePayload,
        ImageUploadRequestPayload,
        ImageUploadResponsePayload,
        Dict[str, Any] # Fallback for unknown or generic payloads
    ]