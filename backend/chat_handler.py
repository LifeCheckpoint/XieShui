# 在app.py中初始化后导入
socketio = None

def init_socketio(sio):
    global socketio
    socketio = sio

using_debug = False

def debug_output(func):
    """
    装饰器，用于在调试模式下 debug 调用
    """
    def wrapper(*args, **kwargs):
        if not using_debug:
            return func(*args, **kwargs)
        else:
            print(f"CALL: {func.__name__}, ARGS: {args}, {kwargs}")
            result = func(*args, **kwargs)
            print(f"FROM {func.__name__} RETURN: {result}")
            return result
    return wrapper

@debug_output
def send_agent_status_ws(sid, status: str, message: str):
    """
    发送 Agent 状态消息到指定客户端 (WebSocket)
    """
    socketio.emit('chat_response', {
        "type": "agent_status",
        "content": {"status": status, "message": message}
    }, room=sid)

@debug_output
def send_text_msg_ws(sid, text: str):
    """
    发送文本消息到指定客户端 (WebSocket)
    """
    socketio.emit('chat_response', {
        "type": "text",
        "content": {"data": text}
    }, room=sid)

@debug_output
def send_stop_msg_ws(sid, reason: str = "normal"):
    """
    发送停止消息到指定客户端 (WebSocket)
    """
    socketio.emit('chat_response', {
        "type": "stop",
        "content": {"reason": reason}
    }, room=sid)