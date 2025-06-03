import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import '../styles/welcome.css';

const WelcomePage = () => {
  const navigate = useNavigate();
  const user = JSON.parse(localStorage.getItem('user'));

  useEffect(() => {
    if (!user) {
      navigate('/login');
    }
  }, [user, navigate]);

  const handleLogout = () => {
    localStorage.removeItem('user');
    navigate('/login');
  };

  return (
    <div className="container">
      <h1>欢迎使用 XieShui 系统</h1>
      <p>您已成功登录系统</p>
      {user && (
        <div id="userInfo">
          <p><strong>用户ID:</strong> {user.id}</p>
          <p><strong>用户名:</strong> {user.username}</p>
          <p><strong>角色:</strong> {user.role === 'student' ? '学生' : user.role === 'teacher' ? '教师' : '系统管理员'}</p>
        </div>
      )}
      <button id="logoutBtn" onClick={handleLogout}>退出登录</button>
    </div>
  );
};

export default WelcomePage;