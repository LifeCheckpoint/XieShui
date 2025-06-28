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
    <Box sx={{
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      minHeight: '100vh',
      backgroundColor: '#f5f5f5',
      padding: 2
    }}>
      <Container maxWidth="sm" sx={{ position: 'relative' }}>
        {/* 选项卡放在顶部 */}
        <Box sx={{ display: 'flex', justifyContent: 'center', mb: 3 }}>
          <Tabs
            value={activeTab}
            onChange={(e, newValue) => setActiveTab(newValue)}
            variant="fullWidth"
            sx={{ width: '100%' }}
          >
            <Tab label="登录" value="login" />
            <Tab label="注册" value="register" />
          </Tabs>
        </Box>
        
        {/* 简化布局，移除动画 */}
        <Box sx={{ mb: 3 }}>
          {activeTab === 'login' ? (
            <Paper elevation={3} sx={{ padding: 3 }}>
              <Typography variant="h5" align="center" gutterBottom>
                登录 XieShui
              </Typography>
              <Box component="form" onSubmit={handleLoginSubmit} sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                <TextField
                  label="学号/ID 或 用户名"
                  id="loginIdentifier"
                  value={loginData.identifier}
                  onChange={(e) => setLoginData({...loginData, identifier: e.target.value})}
                  required
                  fullWidth
                />
                <TextField
                  label="密码"
                  id="loginPassword"
                  type="password"
                  value={loginData.password}
                  onChange={(e) => setLoginData({...loginData, password: e.target.value})}
                  fullWidth
                />
                <Button type="submit" variant="contained" color="primary">
                  登录
                </Button>
              </Box>
            </Paper>
          ) : (
            <Paper elevation={3} sx={{ padding: 3 }}>
              <Typography variant="h5" align="center" gutterBottom>
                注册 XieShui
              </Typography>
              <Box component="form" onSubmit={handleRegisterSubmit} sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                <TextField
                  label="学号/ID"
                  id="registerId"
                  value={registerData.id}
                  onChange={(e) => setRegisterData({...registerData, id: e.target.value})}
                  required
                  fullWidth
                />
                <TextField
                  label="用户名"
                  id="registerUsername"
                  value={registerData.username}
                  onChange={(e) => setRegisterData({...registerData, username: e.target.value})}
                  required
                  fullWidth
                />
                <TextField
                  label="密码 (学生/教师可为空)"
                  id="registerPassword"
                  type="password"
                  value={registerData.password}
                  onChange={(e) => setRegisterData({...registerData, password: e.target.value})}
                  fullWidth
                />
                <FormControl fullWidth>
                  <InputLabel id="registerRole-label">角色</InputLabel>
                  <Select
                    labelId="registerRole-label"
                    id="registerRole"
                    value={registerData.role}
                    label="角色"
                    onChange={(e) => setRegisterData({...registerData, role: e.target.value})}
                    required
                  >
                    <MenuItem value="student">学生</MenuItem>
                    <MenuItem value="teacher">教师</MenuItem>
                    <MenuItem value="admin">系统管理员</MenuItem>
                  </Select>
                </FormControl>
                <Button type="submit" variant="contained" color="primary">
                  注册
                </Button>
              </Box>
            </Paper>
          )}
        </Box>
        
        {message.text && (
          <Box
            sx={{
              p: 2,
              backgroundColor: message.type === 'error' ? '#ffebee' : '#e8f5e9',
              color: message.type === 'error' ? '#b71c1c' : '#2e7d32',
              borderRadius: 1
            }}
          >
            {message.text}
          </Box>
        )}
      </Container>
    </Box>
  );
};

export default LoginPage;