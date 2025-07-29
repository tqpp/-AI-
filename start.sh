#!/bin/bash

# 检查虚拟环境是否存在
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# 激活虚拟环境
source .venv/bin/activate

# 检查依赖是否已安装
if [ ! -f ".venv/bin/uvicorn" ]; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
fi

# 启动应用
echo "Starting application..."
python -m uvicorn src.backend.main:app --reload

# 捕获 Ctrl+C 信号
trap 'echo "Stopping application..."; deactivate' SIGINT 