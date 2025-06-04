import json
import time

def generate_chat_response(history, current_text, current_image_paths):
    print(f"收到 Chat: text={current_text}, images={len(current_image_paths)}, len(history)={len(history)}")
    
    # 模拟流式响应生成器
    def generate():
        try:
            # 发送Agent状态
            event = {
                "type": "agent_status",
                "content": {"status": "processing", "message": "正在处理请求..."}
            }
            print(f"发送事件: {event}")
            yield "data: " + json.dumps(event) + "\n\n"
            
            time.sleep(0.1)  # 缩短模拟延迟
            
            # 发送文本片段
            event = {
                "type": "text",
                "content": {"data": "这是模拟回复的第一部分。"}
            }
            print(f"发送事件: {event}")
            yield "data: " + json.dumps(event) + "\n\n"
            
            time.sleep(0.1)
            
            event = {
                "type": "text",
                "content": {"data": "这是模拟回复的第二部分。"}
            }
            print(f"发送事件: {event}")
            yield "data: " + json.dumps(event) + "\n\n"
            
            time.sleep(0.1)
            
            # 发送停止标识
            event = {
                "type": "stop",
                "content": {"reason": "normal"}
            }
            print(f"发送事件: {event}")
            yield "data: " + json.dumps(event) + "\n\n"
            
            print("SSE流发送完成")
        except Exception as e:
            print(f"生成SSE流时出错: {str(e)}")
    
    return generate()