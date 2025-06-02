"""
启动 XieShui 后端服务

在 backend 目录下使用如下命令
uv run app.py
"""
from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/")
def hello():
    return "Hello, XieShui!"

@app.route("/health")
def health_check():
    return "XieShui Service is running"

if __name__ == "__main__":
    app.run(port=7222)