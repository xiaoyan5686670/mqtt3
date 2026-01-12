#!/bin/bash
# 后端启动脚本

cd "$(dirname "$0")/backend"

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
echo "检查并安装依赖..."
pip install -r requirements.txt > /dev/null 2>&1

# 检查.env文件
if [ ! -f ".env" ]; then
    echo "创建.env文件..."
    cp env.example .env
    echo "⚠️  请编辑 .env 文件，设置 SECRET_KEY"
fi

# 启动服务
echo "启动后端服务..."
python main.py