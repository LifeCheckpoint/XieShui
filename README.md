# XieShui

面向教与学的 Agent 系统

## Install

### UV 安装与同步依赖

```bash
pip install uv
uv sync
```

### 前端依赖安装

首先确保安装了 `NodeJS`

然后执行

```bash
cd frontend-react
npm install
```

## Launch

### 运行后端

```bash
uv run backend/app.py
```

### 运行前端

```bash
npm --prefix "frontend-react" run dev
```