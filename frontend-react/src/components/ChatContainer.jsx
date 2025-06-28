import React, { useEffect } from 'react';
import Chat, { Bubble, useMessages } from '@chatui/core';
import '@chatui/core/dist/index.css';
import '../styles/chatContainer.css';
import '../styles/chatui-theme.css';
import ImageUploadPreview from './ImageUploadPreview';
import useWebSocket from '../hooks/useWebSocket'; // 导入 useWebSocket Hook
import { v4 as uuidv4 } from 'uuid'; // 用于生成 thread_id

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
  const [isStreaming, setIsStreaming] = React.useState(false);
  const [threadId, setThreadId] = React.useState(null); // 新增 threadId 状态
  const [waitingForQuestionAnswer, setWaitingForQuestionAnswer] = React.useState(false); // 新增状态
  const [questionPayload, setQuestionPayload] = React.useState(null); // 存储问题和选项

  const { sendMessage, lastMessage } = useWebSocket('http://localhost:7222');

  useEffect(() => {
    // 初始化 threadId
    if (!threadId) {
      setThreadId(uuidv4());
    }
  }, [threadId]);

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
            if (data.content?.agent_status_content) { // 使用新的 agent_status_content
              const statusMsg = `Agent 状态: ${data.content.agent_status_content.message}`;
              appendMsg({
                type: 'text',
                content: { text: statusMsg },
                position: 'left', // Agent 状态消息通常是系统消息
              });
            }
            break;
          case 'stop':
            setIsStreaming(false);
            setWaitingForQuestionAnswer(false); // 停止时也解除等待
            break;
          case 'question_request': // 处理新的 question_request
            if (data.content?.question_payload) {
              setQuestionPayload(data.content.question_payload);
              setWaitingForQuestionAnswer(true);
              setIsStreaming(false); // 暂停流式传输，等待用户回答
              appendMsg({
                type: 'text',
                content: { text: data.content.question_payload.question },
                position: 'left',
              });
              // 可以在这里显示选项，例如通过 quickReplies
              // 或者自定义渲染
            }
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
  }, [lastMessage, appendMsg, setIsStreaming, setImageUrls, setImageFiles, setWaitingForQuestionAnswer, setQuestionPayload, threadId]); // 添加 threadId 到依赖数组

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

      let resumeData = null;
      if (waitingForQuestionAnswer && questionPayload) {
        // 如果是回答问题，构建 resume_data
        resumeData = {
          answer: val, // 用户输入的答案
          tool_call_id: questionPayload.tool_call_id // 关联到中断的 tool_call_id
        };
        setWaitingForQuestionAnswer(false);
        setQuestionPayload(null);
      }

      sendMessage({
        type: 'chat_request',
        payload: {
          history: pydanticHistory,
          current_text: val,
          current_image_paths: imageUrls,
          thread_id: threadId, // 传递 thread_id
          resume_data: resumeData // 传递 resume_data
        }
      });
      
      // 重置状态
      setImageFiles([]);
      setImageUrls([]);
    }
  }

  // 处理图片发送
  async function handleImageSend(file) {
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (e) => {
      const base64Image = e.target.result.split(',')[1]; // 获取 Base64 编码的图片数据
      const filename = file.name;

      // 将图片添加到预览
      setImageFiles(prev => [...prev, file]);
      setImageUrls(prev => [...prev, URL.createObjectURL(file)]);

      // 发送图片上传请求
      sendMessage({
        type: 'image_upload_request',
        payload: {
          filename: filename,
          image_data: base64Image,
        },
      });
    };
    reader.readAsDataURL(file);
  }

  // 处理问题选项点击
  function handleQuestionOptionClick(option) {
    if (waitingForQuestionAnswer && questionPayload) {
      handleSend('text', option); // 将选项作为文本发送
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
          quickReplies={
            waitingForQuestionAnswer && questionPayload
              ? questionPayload.options.map(option => ({ name: option }))
              : defaultQuickReplies
          }
          onQuickReplyClick={handleQuickReplyClick}
          onSend={handleSend}
          onImageSend={handleImageSend}
          // 禁用输入框，如果正在等待问题答案
          inputOptions={{
            // 可以在这里根据 waitingForQuestionAnswer 状态禁用输入框
            // 或者在 renderInput 中自定义渲染
            // disabled: waitingForQuestionAnswer, // 禁用输入框
            // placeholder: waitingForQuestionAnswer ? "请选择一个选项..." : "输入消息...",
          }}
        />
        
        {imageUrls.length > 0 && (
          <ImageUploadPreview
            images={imageUrls}
            onRemove={removeImage}
          />
        )}

        {/*
          // 选项可以通过 quickReplies 动态渲染，这里可以移除
          {waitingForQuestionAnswer && questionPayload && (
            <div className="question-options">
              {questionPayload.options.map((option, index) => (
                <button key={index} onClick={() => handleQuestionOptionClick(option)}>
                  {option}
                </button>
              ))}
            </div>
          )}
        */}
      </div>
    </div>
  );
}