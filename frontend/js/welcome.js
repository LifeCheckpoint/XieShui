// 显示用户信息
document.addEventListener('DOMContentLoaded', function() {
    // 从本地存储获取用户信息
    const user = JSON.parse(localStorage.getItem('user'));
    
    if (user) {
        const userInfo = document.getElementById('userInfo');
        userInfo.innerHTML = `
            <p><strong>用户ID:</strong> ${user.id}</p>
            <p><strong>用户名:</strong> ${user.username}</p>
            <p><strong>角色:</strong> ${user.role === 'student' ? '学生' : user.role === 'teacher' ? '教师' : '系统管理员'}</p>
        `;
    } else {
        // 如果没有用户信息，跳转到登录页
        window.location.href = 'login.html';
    }
});

// 退出登录
document.getElementById('logoutBtn').addEventListener('click', function() {
    localStorage.removeItem('user');
    window.location.href = 'login.html';
});