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

class QuestionRequestPayload(BaseModel):
    question: str
    options: List[str]
    tool_call_id: Optional[str] = None # 用于关联到 LangGraph 的 interrupt

class AgentStatusContent(BaseModel):
    status: str # 例如 "thinking", "tool_calling", "waiting_for_human_input", "finished"
    message: str # 详细描述
    current_node: Optional[str] = None
    tool_name: Optional[str] = None

class ChatRequestPayload(BaseModel):
    history: List[ChatMessage]
    current_text: str
    current_image_paths: List[str]
    thread_id: Optional[str] = "default_thread" # 新增
    resume_data: Optional[Dict[str, Any]] = None # 新增

class ChatResponseContent(BaseModel):
    data: Optional[str] = None
    status: Optional[str] = None # For agent_status
    message: Optional[str] = None # For agent_status
    reason: Optional[str] = None # For stop
    question_payload: Optional[QuestionRequestPayload] = None # For question_request
    agent_status_content: Optional[AgentStatusContent] = None # For agent_status

class ChatResponsePayload(BaseModel):
    type: str # "text", "agent_status", "stop", "question_request"
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