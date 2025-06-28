import { useEffect, useState } from 'react';
import io from 'socket.io-client';

export default function useWebSocket() {
  const [socket, setSocket] = useState(null);
  
  useEffect(() => {
    const newSocket = io('http://localhost:7222');
    setSocket(newSocket);
    
    return () => newSocket.disconnect();
  }, []);
  
  return socket;
}