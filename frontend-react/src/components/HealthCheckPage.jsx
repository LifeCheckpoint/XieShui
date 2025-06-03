import React, { useState } from 'react';
import '../styles/style_health_check.css';

const HealthCheckPage = () => {
  const [status, setStatus] = useState({ message: '点击按钮检查服务状态。', type: '' });
  const backendUrl = 'http://127.0.0.1:7222/health';

  const checkHealth = async () => {
    setStatus({ message: '正在检查...', type: '' });
    
    try {
      const response = await fetch(backendUrl);
      
      if (response.ok) {
        const text = await response.text();
        setStatus({ message: `状态: ${text}`, type: 'success' });
      } else {
        setStatus({ message: `错误: 服务返回状态码 ${response.status}`, type: 'error' });
      }
    } catch (error) {
      setStatus({ message: `错误: 无法连接到服务\n${error.message}`, type: 'error' });
    }
  };

  return (
    <div className="container">
      <h1>XieShui 服务状态检查</h1>
      <button id="checkHealthBtn" onClick={checkHealth}>检查健康状态</button>
      <div id="statusDisplay" className={`status-display ${status.type}`}>
        <p>{status.message}</p>
      </div>
    </div>
  );
};

export default HealthCheckPage;