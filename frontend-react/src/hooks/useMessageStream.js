import { useState } from 'react';

const useMessageStream = () => {
  const [isStreaming, setIsStreaming] = useState(false);
  
  const processStreamResponse = async (response, appendMsg) => {
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';
    
    try {
      while (true) {
        const { done, value } = await reader.read();
        if (done) {
          console.log('SSE流结束');
          break;
        }
        
        buffer += decoder.decode(value, { stream: true });
        const events = buffer.split('\n\n');
        buffer = events.pop() || '';
        
        for (const event of events) {
          if (!event.startsWith('data: ')) continue;
          
          const jsonStr = event.replace('data: ', '');
          console.log('收到SSE事件:', jsonStr);
          
          try {
            const data = JSON.parse(jsonStr);
            
            switch (data.type) {
              case 'text':
                if (data.content?.data) {
                  // 为每个text事件创建新消息
                  appendMsg({
                    type: 'text',
                    content: { text: data.content.data }
                  });
                  console.log('添加新消息:', data.content.data);
                }
                break;
                
              case 'agent_status':
                // 添加状态消息
                appendMsg({
                  type: 'text',
                    content: { text: data.content.message }
                });
                console.log('添加状态消息:', data.content.message);
                break;
                
              case 'stop':
                console.log('收到停止事件');
                // 不再提前返回，确保处理完所有事件
                break;
                
              default:
                console.warn('未知事件类型:', data.type);
            }
          } catch (e) {
            console.error('解析SSE事件失败:', e, '原始数据:', jsonStr);
          }
        }
      }
    } catch (error) {
      console.error('流处理失败:', error);
      setIsStreaming(false);
    } finally {
      setIsStreaming(false);
    }
  };

  return {
    isStreaming,
    setIsStreaming,
    processStreamResponse
  };
};

export default useMessageStream;