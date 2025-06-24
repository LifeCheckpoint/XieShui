import React, { useEffect } from 'react';
import Chat, { Bubble, useMessages } from '@chatui/core';
import '@chatui/core/dist/index.css';
import '../styles/chatContainer.css';
import '../styles/chatui-theme.css';
import ImageUploadPreview from './ImageUploadPreview';
import useWebSocket from '../hooks/useWebSocket'; // 导入 useWebSocket Hook

const initialMessages = [
  {
    type: 'text',
    content: { text: '你好，我是 XieShui 智能教学辅助 Agent' },
    user: {
      avatar: 'avatar.png',
    },
  },
];

const defaultQuickReplies = [
  {
    icon: 'message',
    name: '提示词库',
    isNew: true,
    isHighlight: true,
  },
];

export default function() {
  const { messages, appendMsg, updateMsg } = useMessages(initialMessages);
  const [imageFiles, setImageFiles] = React.useState([]);
  const [imageUrls, setImageUrls] = React.useState([]);
  const [isStreaming, setIsStreaming] = React.useState(false); // 保持 isStreaming 状态
  const { sendMessage, lastMessage } = useWebSocket('http://localhost:7222'); // 使用 WebSocket Hook

  useEffect(() => {
    if (lastMessage) {
      if (lastMessage.type === 'chat_response') {
        const data = lastMessage.payload;
        switch (data.type) {
          case 'text':
            if (data.content?.data) {
              appendMsg({
                type: 'text',
                content: { text: data.content.data }
              });
            }
            break;
          case 'agent_status':
            if (data.content?.message) {
              appendMsg({
                type: 'text',
                content: { text: data.content.message }
              });
            }
            break;
          case 'stop':
            setIsStreaming(false);
            break;
          default:
            console.warn('未知聊天响应类型:', data.type);
        }
      } else if (lastMessage.type === 'image_upload_response') {
        const data = lastMessage.payload;
        if (data.status === 'success' && data.image_path) {
          setImageUrls(prev => [...prev, data.image_path]);
        } else {
          console.error('图片上传失败:', data.message);
          // 移除失败的图片预览
          setImageFiles(prev => prev.slice(0, prev.length - 1));
        }
      } else if (lastMessage.type === 'error') {
        appendMsg({
          type: 'text',
          content: { text: `服务器错误: ${lastMessage.payload.message}` }
        });
        setIsStreaming(false);
      }
    }
  }, [lastMessage, appendMsg, setIsStreaming, setImageUrls, setImageFiles]);

  // 发送回调
  async function handleSend(type, val) {
    if (type === 'text' && val.trim() && !isStreaming) {
      setIsStreaming(true);
      
      // 添加用户消息
      const userMsg = {
        type: 'text',
        content: { text: val },
        position: 'right',
      };
      appendMsg(userMsg);
      
      // 构建 Pydantic 兼容的 history 结构
      const pydanticHistory = messages.map(msg => ({
        role: msg.position === 'right' ? 'user' : 'assistant',
        content: { text: msg.content.text }
      }));

      sendMessage({
        type: 'chat_request',
        payload: {
          history: pydanticHistory,
          current_text: val,
          current_image_paths: imageUrls
        }
      });
      
      // 重置状态
      setImageFiles([]);
      setImageUrls([]);
    }
  }

  // 图片上传处理
  async function handleImageSend(file) {
    setImageFiles(prev => [...prev, file]);
    
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onloadend = () => {
      sendMessage({
        type: 'image_upload_request',
        payload: {
          filename: file.name,
          image_data: reader.result // Base64 编码的图片数据
        }
      });
    };
    reader.onerror = (error) => {
      console.error('文件读取失败:', error);
      setImageFiles(prev => prev.filter(f => f !== file));
    };
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
      <div className="chat-wrapper">
        <Chat
          navbar={{ title: 'XieShui Agent' }}
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