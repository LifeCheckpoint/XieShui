// 添加动画效果
import { keyframes } from '@emotion/react';
import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import ChatContainer from './ChatContainer';
// 导入Material UI组件
import AppBar from '@mui/material/AppBar';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import IconButton from '@mui/material/IconButton';
import Menu from '@mui/material/Menu';
import MenuItem from '@mui/material/MenuItem';
import Container from '@mui/material/Container';
import Box from '@mui/material/Box';
import AccountCircle from '@mui/icons-material/AccountCircle';

const WelcomePage = () => {
  const navigate = useNavigate();
  const user = JSON.parse(localStorage.getItem('user'));
  const [anchorEl, setAnchorEl] = useState(null);
  const open = Boolean(anchorEl);

  useEffect(() => {
    if (!user) {
      navigate('/login');
    }
  }, [user, navigate]);

  const handleLogout = () => {
    localStorage.removeItem('user');
    navigate('/login');
  };

  const handleMenu = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  // 定义淡入动画
  const fadeIn = keyframes`
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
  `;

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1, fontWeight: 'bold', textAlign: 'center' }}>
            XieShui
          </Typography>
          {user && (
            <div>
              <IconButton
                size="large"
                aria-label="account of current user"
                aria-controls="menu-appbar"
                aria-haspopup="true"
                onClick={handleMenu}
                color="inherit"
              >
                <AccountCircle />
                <Typography variant="body1" component="span" sx={{ marginLeft: 1 }}>
                  {user.username}
                </Typography>
              </IconButton>
              <Menu
                id="menu-appbar"
                anchorEl={anchorEl}
                anchorOrigin={{
                  vertical: 'top',
                  horizontal: 'right',
                }}
                keepMounted
                transformOrigin={{
                  vertical: 'top',
                  horizontal: 'right',
                }}
                open={open}
                onClose={handleClose}
              >
                <MenuItem disabled>
                  <Typography variant="body2">
                    <strong>用户ID:</strong> {user.id}<br />
                    <strong>用户名:</strong> {user.username}<br />
                    <strong>角色:</strong> {user.role === 'student' ? '学生' : user.role === 'teacher' ? '教师' : '系统管理员'}
                  </Typography>
                </MenuItem>
                <MenuItem onClick={handleLogout}>退出登录</MenuItem>
                <MenuItem >个人资料</MenuItem>
              </Menu>
            </div>
          )}
        </Toolbar>
      </AppBar>
      <Container component="main" sx={{ flexGrow: 1, display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
        <Box sx={{ textAlign: 'center', width: '100%', maxWidth: 1200, padding: 3 }}>
          <Box
            sx={{
              animation: `${fadeIn} 0.8s ease-out forwards`,
              opacity: 0 // 初始状态为透明
            }}
          >
            {/* <Typography variant="h3" gutterBottom>
              欢迎使用 XieShui 系统
            </Typography>
            <Typography variant="body1" paragraph>
              您已成功登录系统
            </Typography> */}
            <Box sx={{ width: '100%', maxWidth: 800, margin: '40px auto' }}>
              <ChatContainer />
            </Box>
          </Box>
        </Box>
      </Container>
    </Box>
  );
};

export default WelcomePage;