import React from 'react';
import Chat, { Bubble, useMessages } from '@chatui/core';
import '@chatui/core/dist/index.css';
import '../styles/chatContainer.css';
import '../styles/chatui-theme.css';
import ImageUploadPreview from './ImageUploadPreview';
import useMessageStream from '../hooks/useMessageStream';

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
  const { isStreaming, setIsStreaming, processStreamResponse } = useMessageStream();
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
      
      try {
        const requestBody = {
          history: messages,
          current_text: val,
          current_image_paths: imageUrls
        };
        
        const response = await fetch('http://localhost:7222/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(requestBody)
        });
        
        if (!response.ok) {
          throw new Error(`请求失败: ${response.status}`);
        }
        
        console.log('开始处理流响应');
        await processStreamResponse(response, appendMsg);
        console.log('流处理完成');
        
        console.log('重置状态');
        setImageFiles([]);
        setImageUrls([]);
      } catch (error) {
        console.error('请求出错:', error);
        appendMsg({
          type: 'text',
          content: { text: `请求失败: ${error.message}` }
        });
      } finally {
        setIsStreaming(false);
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