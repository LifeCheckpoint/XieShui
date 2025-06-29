// 导入Material UI组件
import Container from '@mui/material/Container';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Tabs from '@mui/material/Tabs';
import Tab from '@mui/material/Tab';
import TextField from '@mui/material/TextField';
import Button from '@mui/material/Button';
import Paper from '@mui/material/Paper';
import FormControl from '@mui/material/FormControl';
import InputLabel from '@mui/material/InputLabel';
import Select from '@mui/material/Select';
import MenuItem from '@mui/material/MenuItem';
import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import '../styles/login.css';
import useWebSocket from '../hooks/useWebSocket'; // 导入 useWebSocket Hook

const LoginPage = () => {
  const [activeTab, setActiveTab] = useState('login');
  const [loginData, setLoginData] = useState({ identifier: '', password: '' });
  const [registerData, setRegisterData] = useState({ id: '', username: '', password: '', role: 'student' });
  const [message, setMessage] = useState({ text: '', type: '' });
  const navigate = useNavigate();

  const [pendingAuth, setPendingAuth] = useState(null); // 用于存储待发送的认证请求

  const handleConnected = useCallback(() => {
    if (pendingAuth) {
      sendMessage(pendingAuth);
      setPendingAuth(null); // 发送后清除待处理请求
    }
  }, [pendingAuth]);

  const { sendMessage, lastMessage } = useWebSocket(handleConnected); // 使用 WebSocket Hook，并传入回调

  useEffect(() => {
    if (lastMessage) {
      if (lastMessage.type === 'auth_response') {
        const data = lastMessage.payload;
        if (data.status === 'success') {
          setMessage({ text: `登录成功！欢迎 ${data.username} (${data.role})`, type: 'success' });
          localStorage.setItem('user', JSON.stringify({ id: data.user_id, username: data.username, role: data.role }));
          setTimeout(() => navigate('/welcome'), 1500);
        } else {
          setMessage({ text: `认证失败: ${data.message}`, type: 'error' });
        }
      } else if (lastMessage.type === 'error') {
        setMessage({ text: `服务器错误: ${lastMessage.payload.message}`, type: 'error' });
      }
    }
  }, [lastMessage, navigate]);

  const handleLoginSubmit = async (e) => {
    e.preventDefault();
    setMessage({ text: '', type: '' }); // 清除之前的消息
    const authRequest = {
      type: 'auth_request',
      payload: {
        action: 'login',
        identifier: loginData.identifier,
        password: loginData.password,
      },
    };
    setPendingAuth(authRequest); // 设置待处理请求
    sendMessage(authRequest); // 尝试立即发送，如果未连接则会在 handleConnected 中发送
  };

  const handleRegisterSubmit = async (e) => {
    e.preventDefault();
    setMessage({ text: '', type: '' }); // 清除之前的消息
    if (registerData.role === 'admin' && !registerData.password) {
      setMessage({ text: '管理员必须设置密码', type: 'error' });
      return;
    }
    
    const authRequest = {
      type: 'auth_request',
      payload: {
        action: 'register',
        id: registerData.id,
        username: registerData.username,
        password: registerData.password,
        role: registerData.role,
      },
    };
    setPendingAuth(authRequest); // 设置待处理请求
    sendMessage(authRequest); // 尝试立即发送，如果未连接则会在 handleConnected 中发送
  };

  return (
    <Box sx={{
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      minHeight: '100vh',
      backgroundColor: '#f5f5f5',
      padding: 2
    }}>
      <Container maxWidth="sm" sx={{ position: 'relative' }}>
        <Paper elevation={3} sx={{ p: 4 }}>
          <Typography variant="h4" component="h1" gutterBottom align="center">
            欢迎使用XieShui
          </Typography>
          <Tabs
            value={activeTab}
            onChange={(e, newValue) => setActiveTab(newValue)}
            variant="fullWidth"
            sx={{ mb: 3 }}
          >
            <Tab label="登录" value="login" />
            <Tab label="注册" value="register" />
          </Tabs>

          {activeTab === 'login' ? (
            <form onSubmit={handleLoginSubmit}>
              <TextField
                label="学号/工号"
                variant="outlined"
                fullWidth
                margin="normal"
                value={loginData.identifier}
                onChange={(e) => setLoginData({ ...loginData, identifier: e.target.value })}
              />
              <TextField
                label="密码"
                type="password"
                variant="outlined"
                fullWidth
                margin="normal"
                value={loginData.password}
                onChange={(e) => setLoginData({ ...loginData, password: e.target.value })}
              />
              <Button
                type="submit"
                variant="contained"
                color="primary"
                fullWidth
                size="large"
                sx={{ mt: 2 }}
              >
                登录
              </Button>
            </form>
          ) : (
            <form onSubmit={handleRegisterSubmit}>
              <TextField
                label="学号/工号"
                variant="outlined"
                fullWidth
                margin="normal"
                value={registerData.id}
                onChange={(e) => setRegisterData({ ...registerData, id: e.target.value })}
              />
              <TextField
                label="用户名"
                variant="outlined"
                fullWidth
                margin="normal"
                value={registerData.username}
                onChange={(e) => setRegisterData({ ...registerData, username: e.target.value })}
              />
              <TextField
                label="密码"
                type="password"
                variant="outlined"
                fullWidth
                margin="normal"
                value={registerData.password}
                onChange={(e) => setRegisterData({ ...registerData, password: e.target.value })}
              />
              <FormControl fullWidth margin="normal">
                <InputLabel>角色</InputLabel>
                <Select
                  value={registerData.role}
                  label="角色"
                  onChange={(e) => setRegisterData({ ...registerData, role: e.target.value })}
                >
                  <MenuItem value="student">学生</MenuItem>
                  <MenuItem value="teacher">教师</MenuItem>
                  <MenuItem value="admin">管理员</MenuItem>
                </Select>
              </FormControl>
              <Button
                type="submit"
                variant="contained"
                color="primary"
                fullWidth
                size="large"
                sx={{ mt: 2 }}
              >
                注册
              </Button>
            </form>
          )}

          {message.text && (
            <Typography
              color={message.type === 'error' ? 'error' : 'primary'}
              align="center"
              sx={{ mt: 2 }}
            >
              {message.text}
            </Typography>
          )}
        </Paper>
      </Container>
    </Box>
  );
};

export default LoginPage;