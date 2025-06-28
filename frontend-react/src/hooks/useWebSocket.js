import { useState, useEffect, useRef, useCallback } from 'react';

const useWebSocket = (url, onConnected) => {
  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState(null);
  const wsRef = useRef(null); // 将 socketRef 改名为 wsRef

  useEffect(() => {
    wsRef.current = new WebSocket(url); // 使用原生 WebSocket

    wsRef.current.onopen = () => {
      setIsConnected(true);
      console.log('WebSocket connected');
      if (onConnected && typeof onConnected === 'function') {
        onConnected();
      }
    };

    wsRef.current.onclose = () => {
      setIsConnected(false);
      console.log('WebSocket disconnected');
    };

    wsRef.current.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        console.log('WebSocket message received:', data);
        setLastMessage(data);
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error, event.data);
      }
    };

    wsRef.current.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [url, onConnected]); // 添加 onConnected 到依赖数组

  const sendMessage = useCallback((message) => {
    if (wsRef.current && isConnected) {
      wsRef.current.send(JSON.stringify(message)); // 使用 ws.send 发送 JSON 字符串
      console.log('WebSocket message sent:', message);
    } else {
      console.warn('WebSocket not connected, message not sent:', message);
    }
  }, [isConnected]);

  return { isConnected, lastMessage, sendMessage };
};

export default useWebSocket;