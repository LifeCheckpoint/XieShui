// 选项卡切换逻辑
document.querySelectorAll('.tab').forEach(tab => {
    tab.addEventListener('click', function() {
        // 移除所有选项卡的active类
        document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
        // 添加当前选项卡的active类
        this.classList.add('active');
        
        // 隐藏所有表单容器
        document.querySelectorAll('.form-container').forEach(container => {
            container.classList.remove('active');
        });
        
        // 显示对应选项卡的表单容器
        const tabName = this.getAttribute('data-tab');
        document.getElementById(`${tabName}FormContainer`).classList.add('active');
    });
});

// 登录表单提交处理
document.getElementById('loginForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const identifier = document.getElementById('loginIdentifier').value;
    const password = document.getElementById('loginPassword').value;
    
    try {
        const response = await fetch('http://localhost:7222/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ identifier, password })
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            showMessage(`登录成功！欢迎 ${data.user.username} (${data.user.role})`, 'success');
            
            // 存储用户信息到本地存储
            localStorage.setItem('user', JSON.stringify(data.user));
            
            // 登录成功后跳转到欢迎页面
            setTimeout(() => {
                window.location.href = 'welcome.html';
            }, 1500);
        } else {
            showMessage(`登录失败: ${data.message}`, 'error');
        }
    } catch (error) {
        showMessage(`网络错误: ${error.message}`, 'error');
    }
});

// 注册表单提交处理
document.getElementById('registerForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const id = document.getElementById('registerId').value;
    const username = document.getElementById('registerUsername').value;
    const password = document.getElementById('registerPassword').value;
    const role = document.getElementById('registerRole').value;
    
    // 验证管理员密码
    if (role === 'admin' && !password) {
        showMessage('管理员必须设置密码', 'error');
        return;
    }
    
    try {
        const response = await fetch('http://localhost:7222/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ id, username, password, role })
        });
        
        const data = await response.json();
        
        if (response.status === 201) {
            showMessage('注册成功！请使用新账号登录', 'success');
            // 清空注册表单
            document.getElementById('registerForm').reset();
            // 切换到登录选项卡
            document.querySelector('.tab[data-tab="login"]').click();
        } else {
            showMessage(`注册失败: ${data.message}`, 'error');
        }
    } catch (error) {
        showMessage(`网络错误: ${error.message}`, 'error');
    }
});

// 显示消息函数
function showMessage(message, type) {
    const messageArea = document.getElementById('messageArea');
    messageArea.textContent = message;
    messageArea.className = 'message-area ' + type;
    
    // 3秒后自动隐藏消息
    setTimeout(() => {
        messageArea.textContent = '';
        messageArea.className = 'message-area';
    }, 3000);
}