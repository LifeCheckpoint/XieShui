import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import '../styles/login.css';

const LoginPage = () => {
  const [activeTab, setActiveTab] = useState('login');
  const [loginData, setLoginData] = useState({ identifier: '', password: '' });
  const [registerData, setRegisterData] = useState({ id: '', username: '', password: '', role: 'student' });
  const [message, setMessage] = useState({ text: '', type: '' });
  const navigate = useNavigate();

  const handleLoginSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch('http://localhost:7222/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(loginData)
      });
      
      const data = await response.json();
      
      if (data.status === 'success') {
        setMessage({ text: `登录成功！欢迎 ${data.user.username} (${data.user.role})`, type: 'success' });
        localStorage.setItem('user', JSON.stringify(data.user));
        setTimeout(() => navigate('/welcome'), 1500);
      } else {
        setMessage({ text: `登录失败: ${data.message}`, type: 'error' });
      }
    } catch (error) {
      setMessage({ text: `网络错误: ${error.message}`, type: 'error' });
    }
  };

  const handleRegisterSubmit = async (e) => {
    e.preventDefault();
    if (registerData.role === 'admin' && !registerData.password) {
      setMessage({ text: '管理员必须设置密码', type: 'error' });
      return;
    }
    
    try {
      const response = await fetch('http://localhost:7222/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(registerData)
      });
      
      const data = await response.json();
      
      if (response.status === 201) {
        setMessage({ text: '注册成功！请使用新账号登录', type: 'success' });
        setRegisterData({ id: '', username: '', password: '', role: 'student' });
        setActiveTab('login');
      } else {
        setMessage({ text: `注册失败: ${data.message}`, type: 'error' });
      }
    } catch (error) {
      setMessage({ text: `网络错误: ${error.message}`, type: 'error' });
    }
  };

  return (
    <div className="container">
      <h1>XieShui 登录/注册</h1>
      
      <div className="tabs">
        <button 
          className={`tab ${activeTab === 'login' ? 'active' : ''}`} 
          onClick={() => setActiveTab('login')}
        >
          登录
        </button>
        <button 
          className={`tab ${activeTab === 'register' ? 'active' : ''}`} 
          onClick={() => setActiveTab('register')}
        >
          注册
        </button>
      </div>
      
      <div className="form-wrapper">
        <div className={`form-container login-form ${activeTab === 'login' ? 'active' : ''}`}>
          <form onSubmit={handleLoginSubmit}>
            <div className="form-group">
              <label htmlFor="loginIdentifier">学号/ID 或 用户名:</label>
              <input
                type="text"
                id="loginIdentifier"
                value={loginData.identifier}
                onChange={(e) => setLoginData({...loginData, identifier: e.target.value})}
                required
              />
            </div>
            <div className="form-group">
              <label htmlFor="loginPassword">密码:</label>
              <input
                type="password"
                id="loginPassword"
                value={loginData.password}
                onChange={(e) => setLoginData({...loginData, password: e.target.value})}
              />
            </div>
            <button type="submit">登录</button>
          </form>
        </div>
        
        <div className={`form-container register-form ${activeTab === 'register' ? 'active' : ''}`}>
          <form onSubmit={handleRegisterSubmit}>
            <div className="form-group">
              <label htmlFor="registerId">学号/ID:</label>
              <input
                type="text"
                id="registerId"
                value={registerData.id}
                onChange={(e) => setRegisterData({...registerData, id: e.target.value})}
                required
              />
            </div>
            <div className="form-group">
              <label htmlFor="registerUsername">用户名:</label>
              <input
                type="text"
                id="registerUsername"
                value={registerData.username}
                onChange={(e) => setRegisterData({...registerData, username: e.target.value})}
                required
              />
            </div>
            <div className="form-group">
              <label htmlFor="registerPassword">密码 (学生/教师可为空):</label>
              <input
                type="password"
                id="registerPassword"
                value={registerData.password}
                onChange={(e) => setRegisterData({...registerData, password: e.target.value})}
              />
            </div>
            <div className="form-group">
              <label htmlFor="registerRole">角色:</label>
              <select
                id="registerRole"
                value={registerData.role}
                onChange={(e) => setRegisterData({...registerData, role: e.target.value})}
                required
              >
                <option value="student">学生</option>
                <option value="teacher">教师</option>
                <option value="admin">系统管理员</option>
              </select>
            </div>
            <button type="submit">注册</button>
          </form>
        </div>
      </div>
      
      <div className={`message-area ${message.type}`}>
        {message.text}
      </div>
    </div>
  );
};

export default LoginPage;