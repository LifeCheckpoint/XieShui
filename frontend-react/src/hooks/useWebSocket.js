import { useState, useEffect, useRef, useCallback } from 'react';
import io from 'socket.io-client';

const useWebSocket = (url) => {
  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState(null);
  const socketRef = useRef(null);

  useEffect(() => {
    socketRef.current = io(url, {
      transports: ['websocket'],
      reconnectionAttempts: 5,
      reconnectionDelay: 1000,
    });

    socketRef.current.on('connect', () => {
      setIsConnected(true);
      console.log('WebSocket connected');
    });

    socketRef.current.on('disconnect', () => {
      setIsConnected(false);
      console.log('WebSocket disconnected');
    });

    socketRef.current.on('message', (data) => {
      console.log('WebSocket message received:', data);
      setLastMessage(data);
    });

    socketRef.current.on('connect_error', (err) => {
      console.error('WebSocket connection error:', err);
    });

    return () => {
      if (socketRef.current) {
        socketRef.current.disconnect();
      }
    };
  }, [url]);

  const sendMessage = useCallback((message) => {
    if (socketRef.current && isConnected) {
      socketRef.current.emit('message', message);
      console.log('WebSocket message sent:', message);
    } else {
      console.warn('WebSocket not connected, message not sent:', message);
    }
  }, [isConnected]);

  return { isConnected, lastMessage, sendMessage };
};

export default useWebSocket;