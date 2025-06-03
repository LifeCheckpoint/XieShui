# React 前端构建计划

## 目标

在 `frontend-react` 目录下，使用 React 实现与 `frontend` 目录中 `login.html`、`welcome.html` 和 `health_check.html` 相同的功能和界面。

## 技术选型

*   **框架：** React
*   **构建工具：** Vite (基于现有项目结构)
*   **路由：** React Router (用于页面导航)
*   **状态管理：** 使用 React 内置的 `useState` 和 `useEffect`
*   **样式：** 沿用现有 CSS 文件并导入

## 规划步骤

1.  **安装依赖：** 在 `frontend-react` 目录下安装必要的��赖，主要是 `react-router-dom`。
2.  **设置路由：** 在 `src/App.jsx` 或单独的路由文件中配置 React Router，定义 `/login`、`/welcome` 和 `/health-check` 三个路由。
3.  **创建组件：**
    *   创建 `LoginPage.jsx` 组件，对应 `login.html` 的功能。
    *   创建 `WelcomePage.jsx` 组件，对应 `welcome.html` 的功能。
    *   创建 `HealthCheckPage.jsx` 组件，对应 `health_check.html` 的功能。
    *   可以考虑创建一些小型可复用组件，例如 `Form.jsx`、`Tabs.jsx`、`MessageArea.jsx` 等。
4.  **实现登录/注册页面 (`LoginPage.jsx`)：**
    *   使用 `useState` 管理当前显示的选项卡（登��/注册）。
    *   使用 `useState` 管理表单输入框的值。
    *   实现选项卡切换逻辑，根据状态显示不同的表单。
    *   实现表单提交的事件处理函数，使用 `fetch` API 调用后端 `/login` 和 `/register` 接口。
    *   根据后端响应更新消息显示区域的状态。
    *   登录成功后，将用户信息存储到 `localStorage`，并使用 React Router 的导航功能跳转到 `/welcome` 路由。
    *   导入并应用 `frontend/css/login.css` 和 `frontend/css/style_health_check.css` 样式。
5.  **实现欢迎页面 (`WelcomePage.jsx`)：**
    *   使用 `useEffect` 在组件加载时从 `localStorage` 读取用户信息。
    *   如果用户信息不存在，使用 React Router 的导航功能重定向到 `/login` 路由。
    *   显示用户信息。
    *   实现退出登录按钮的点击事件处理函数，清除 `localStorage` 中的用户信息，并跳转到 `/login` 路由。
    *   导入并应用 `frontend/css/welcome.css` 和 `frontend/css/style_health_check.css` 样式。
6.  **实现健康检查页面 (`HealthCheckPage.jsx`)：**
    *   使用 `useState` 管理健康检查的状态和结果消息。
    *   实现按钮点击事件处理函数，使用 `fetch` API 调用后端 `/health` 接口。
    *   根据后端响应更新状态显示区域的内容和样式。
    *   导入并应用 `frontend/css/style_health_check.css` 样式。
7.  **集成 CSS：** 在各个组件中通过 `import` 语句导入相应的 CSS 文件。
8.  **更新入口文件 (`src/main.jsx`)：** 确保应用正确地渲染根组件（通常是包含路由的 `App` 组件）。

## 组件结构示意图

```mermaid
graph TD
    A[index.html] --> B(src/main.jsx);
    B --> C(src/App.jsx);
    C --> D{React Router};
    D -- /login --> E(src/components/LoginPage.jsx);
    D -- /welcome --> F(src/components/WelcomePage.jsx);
    D -- /health-check --> G(src/components/HealthCheckPage.jsx);
    E --> H(Tabs Component);
    E --> I(LoginForm Component);
    E --> J(RegisterForm Component);
    E --> K(MessageArea Component);
    F --> L(UserInfoDisplay Component);
    F --> M(LogoutButton Component);
    G --> N(HealthCheckButton Component);
    G --> O(StatusDisplay Component);