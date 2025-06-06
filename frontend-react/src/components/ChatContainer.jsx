import React, { useEffect } from 'react';
import Chat, { Bubble, useMessages } from '@chatui/core';
import '@chatui/core/dist/index.css';
import '../styles/chatContainer.css';
import '../styles/chatui-theme.css';
import ImageUploadPreview from './ImageUploadPreview';
import useWebSocket from '../hooks/useWebSocket';

const initialMessages = [
  {
    type: 'text',
    content: { text: '你好，我是 XieShui 智能教学辅助 Agent~' },
    user: {
      avatar: 'avatar.png',
    },
  },
];

const defaultQuickReplies = [
  {
    icon: 'message',
    name: '提示词库',
    isNew: false,
    isHighlight: true,
  },
  {
    icon: 'message',
    name: '学科总结',
    isNew: false,
    isHighlight: false,
  },
];

export default function() {
  const { messages, appendMsg, resetList } = useMessages(initialMessages);
  const [imageFiles, setImageFiles] = React.useState([]);
  const [imageUrls, setImageUrls] = React.useState([]);
  const [isProcessing, setIsProcessing] = React.useState(false);
  const socket = useWebSocket();
  
  // 设置消息监听
  useEffect(() => {
    if (!socket) return;
    
    socket.on('chat_response', (data) => {
      switch(data.type) {
        case 'text':
          appendMsg({type: 'text', content: {text: data.content.data}});
          break;
        case 'agent_status':
          appendMsg({type: 'text', content: {text: data.content.message}});
          break;
        case 'stop':
          setIsProcessing(false);
          setImageFiles([]);
          setImageUrls([]);
          break;
        case 'error':
          appendMsg({type: 'text', content: {text: `错误: ${data.content.message}`}});
          setIsProcessing(false);
          break;
        case 'conversation_status':
          if (data.content.status === 'ended') {
            // 会话结束，前端可做额外清理
          }
          break;
      }
    });
    
    // 连接后发送认证和开始会话事件
    socket.emit('authenticate', { token: 'user-token' }); // 简化处理，实际应从登录状态获取
    socket.emit('start_conversation');
    
    return () => {
      socket.off('chat_response');
    };
  }, [socket, appendMsg]);
  
  // 清空聊天
  function handleClearChat() {
    resetList(initialMessages);
    setImageFiles([]);
    setImageUrls([]);
    socket.emit('end_conversation');
  }
  
  // 发送回调
  async function handleSend(type, val) {
    if (type === 'text' && val.trim() && !isProcessing) {
      setIsProcessing(true);
      
      // 添加用户消息
      const userMsg = {
        type: 'text',
        content: { text: val },
        position: 'right',
      };
      appendMsg(userMsg);
      
      try {
        // 通过 WebSocket 发送消息
        socket.emit('send_message', {
          current_text: val,
          current_image_paths: imageUrls
        });
      } catch (error) {
        console.error('请求出错:', error);
        appendMsg({
          type: 'text',
          content: { text: `请求失败: ${error.message}` }
        });
        setIsProcessing(false);
      }
    }
  }

  // 图片上传处理
  async function handleImageSend(file) {
    try {
      setImageFiles(prev => [...prev, file]);
      
      const formData = new FormData();
      formData.append('image', file);
      
      const response = await fetch('http://localhost:7222/upload_image', {
        method: 'POST',
        body: formData
      });
      
      if (!response.ok) {
        throw new Error(`上传失败: ${response.status}`);
      }
      
      const data = await response.json();
      setImageUrls(prev => [...prev, data.image_url]);
    } catch (error) {
      console.error('图片上传失败:', error);
      setImageFiles(prev => prev.filter(f => f !== file));
    }
  }
  
  // 删除图片
  function removeImage(index) {
    setImageFiles(prev => prev.filter((_, i) => i !== index));
    setImageUrls(prev => prev.filter((_, i) => i !== index));
  }
  
  function handleQuickReplyClick(item) {
    handleSend('text', item.name);
  }

  function renderMessageContent(msg) {
    const { type, content } = msg;

    switch (type) {
      case 'text':
        return <Bubble content={content.text} />;
      case 'image':
        return (
          <Bubble type="image">
            <img src={content.picUrl} alt="" />
          </Bubble>
        );
      default:
        return null;
    }
  }

  return (
    <div className="chat-container">
      <div className="chat-header">
        <h2>XieShui Agent</h2>
        <button
          className="clear-chat-btn"
          onClick={handleClearChat}
          disabled={isProcessing}
        >
          清空聊天
        </button>
      </div>
      <div className="chat-wrapper">
        <Chat
          navbar={{ title: '' }}
          messages={messages}
          renderMessageContent={renderMessageContent}
          quickReplies={defaultQuickReplies}
          onQuickReplyClick={handleQuickReplyClick}
          onSend={handleSend}
          onImageSend={handleImageSend}
        />
        
        {imageUrls.length > 0 && (
          <ImageUploadPreview
            images={imageUrls}
            onRemove={removeImage}
          />
        )}
      </div>
    </div>
  );
}