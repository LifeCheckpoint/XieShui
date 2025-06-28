import { useState, useEffect, useCallback } from 'react';
import { 
  sendMessage as wsSendMessage,
  onMessage as wsOnMessage,
  onConnectionStatusChange as wsOnConnectionStatusChange
} from '../utils/websocketService';

const useWebSocket = (onConnected) => {
  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState(null);

  useEffect(() => {
    // 监听连接状态变化
    const cleanupStatusListener = wsOnConnectionStatusChange((connected) => {
      setIsConnected(connected);
      if (connected && onConnected && typeof onConnected === 'function') {
        onConnected();
      }
    });

    // 监听消息
    const cleanupMessageListener = wsOnMessage((message) => {
      console.log('WebSocket message received:', message);
      setLastMessage(message);
    });

    return () => {
      cleanupStatusListener();
      cleanupMessageListener();
    };
  }, [onConnected]);

  const sendMessage = useCallback((message) => {
    console.log('WebSocket message sent:', message);
    wsSendMessage(message);
  }, []);

  return { isConnected, lastMessage, sendMessage };
};

export default useWebSocket;