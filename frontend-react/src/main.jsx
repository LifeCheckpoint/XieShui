import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './index.css';

// 导入Material UI的主题提供者以及创建主题的函数
import { ThemeProvider, createTheme } from '@mui/material/styles';

// 创建一个基础主题
const theme = createTheme();

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <ThemeProvider theme={theme}>
      <App />
    </ThemeProvider>
  </React.StrictMode>
);
