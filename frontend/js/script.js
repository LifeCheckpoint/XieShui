document.addEventListener('DOMContentLoaded', () => {
    const checkHealthBtn = document.getElementById('checkHealthBtn');
    const statusDisplay = document.getElementById('statusDisplay');

    const backendUrl = 'http://127.0.0.1:7222/health'; // 确保这里的URL和端口与你的后端服务一致

    checkHealthBtn.addEventListener('click', async () => {
        statusDisplay.innerHTML = '<p>正在检查...</p>';
        statusDisplay.className = 'status-display'; // 重置样式

        try {
            const response = await fetch(backendUrl);

            if (response.ok) {
                const text = await response.text();
                statusDisplay.innerHTML = `<p>状态: ${text}</p>`;
                statusDisplay.classList.add('success');
            } else {
                statusDisplay.innerHTML = `<p>错误: 服务返回状态码 ${response.status}</p>`;
                statusDisplay.classList.add('error');
            }
        } catch (error) {
            statusDisplay.innerHTML = `<p>错误: 无法连接到服务</p><p>${error.message}</p>`;
            statusDisplay.classList.add('error');
        }
    });
});