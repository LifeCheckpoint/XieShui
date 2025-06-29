// frontend-react/src/utils/websocketService.js

let ws = null;
let messageListeners = [];
let connectionStatusListeners = [];
let isConnecting = false;

const WEBSOCKET_URL = 'ws://localhost:7223'; // 统一管理 WebSocket URL

const connectWebSocket = () => {
  if (ws && (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING)) {
    return; // Already connected or connecting
  }
  if (isConnecting) {
    return; // Prevent multiple connection attempts
  }

  isConnecting = true;
  console.log('Attempting to connect WebSocket...');
  ws = new WebSocket(WEBSOCKET_URL);

  ws.onopen = () => {
    console.log('WebSocket connected');
    isConnecting = false;
    connectionStatusListeners.forEach(listener => listener(true));
  };

  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      console.log('WebSocket message received:', data);
      messageListeners.forEach(listener => listener(data));
    } catch (error) {
      console.error('Failed to parse WebSocket message:', error, event.data);
    }
  };

  ws.onclose = () => {
    console.log('WebSocket disconnected');
    isConnecting = false;
    connectionStatusListeners.forEach(listener => listener(false));
    // Optional: Reconnect logic
    // setTimeout(connectWebSocket, 3000); // Attempt to reconnect after 3 seconds
  };

  ws.onerror = (error) => {
    console.error('WebSocket error:', error);
    isConnecting = false;
    connectionStatusListeners.forEach(listener => listener(false));
  };
};

const sendMessage = (message) => {
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify(message));
    console.log('WebSocket message sent:', message);
  } else {
    console.warn('WebSocket not connected, message not sent:', message);
    // Attempt to connect if not open, then send message
    connectWebSocket();
    // You might want to queue messages here if connection is not immediate
  }
};

const onMessage = (listener) => {
  messageListeners.push(listener);
  return () => {
    messageListeners = messageListeners.filter(l => l !== listener);
  };
};

const onConnectionStatusChange = (listener) => {
  connectionStatusListeners.push(listener);
  // Immediately provide current status
  if (ws) {
    listener(ws.readyState === WebSocket.OPEN);
  } else {
    listener(false);
  }
  return () => {
    connectionStatusListeners = connectionStatusListeners.filter(l => l !== listener);
  };
};

// Initial connection attempt when the service is imported
connectWebSocket();

export { connectWebSocket, sendMessage, onMessage, onConnectionStatusChange };