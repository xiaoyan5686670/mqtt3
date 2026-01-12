#!/bin/bash
# Windows 10 部署构建脚本（在 macOS/Linux 上运行）
# 用于生成 Windows 部署版本

set -e

echo "========================================"
echo "MQTT IoT 管理系统 - Windows 部署构建"
echo "========================================"
echo

# 检查 Node.js
if ! command -v node &> /dev/null; then
    echo "[错误] 未找到 Node.js，请先安装 Node.js"
    echo "下载地址: https://nodejs.org/"
    exit 1
fi

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "[错误] 未找到 Python，请先安装 Python 3.8+"
    echo "下载地址: https://www.python.org/downloads/"
    exit 1
fi

echo "[1/4] 构建前端生产版本..."
cd frontend

# 清理之前的构建
if [ -d "dist" ]; then
    echo "清理之前的构建文件..."
    rm -rf dist
fi

# 清理 vite 缓存（解决权限问题）
if [ -d "node_modules/.vite-temp" ]; then
    echo "清理 Vite 缓存..."
    rm -rf node_modules/.vite-temp
fi

npm install
if [ $? -ne 0 ]; then
    echo "[错误] 前端依赖安装失败"
    cd ..
    exit 1
fi

# 确保 esbuild 已安装（rolldown-vite 需要）
if ! npm list esbuild > /dev/null 2>&1; then
    echo "[信息] 安装 esbuild（rolldown-vite 构建需要）..."
    npm install --save-dev esbuild@^0.25.0
    if [ $? -ne 0 ]; then
        echo "[警告] esbuild 安装失败，构建可能会失败"
    fi
fi

echo "开始构建前端..."
npm run build
if [ $? -ne 0 ]; then
    echo "[错误] 前端构建失败，请检查错误信息"
    echo "[提示] 如果是权限问题，请尝试: sudo npm run build"
    cd ..
    exit 1
fi
cd ..
echo "[完成] 前端构建成功"
echo

echo "[2/4] 准备后端文件..."
rm -rf deploy/backend
mkdir -p deploy/backend
cp -r backend/api deploy/backend/
cp -r backend/core deploy/backend/
cp -r backend/models deploy/backend/
cp -r backend/schemas deploy/backend/
cp -r backend/services deploy/backend/
cp backend/main.py deploy/backend/
cp backend/requirements.txt deploy/backend/
cp backend/env.example deploy/backend/
echo "[完成] 后端文件准备完成"
echo

echo "[3/4] 复制前端构建文件..."
if [ ! -d "frontend/dist" ]; then
    echo "[错误] 前端构建目录不存在，请先运行前端构建"
    exit 1
fi
mkdir -p deploy/backend/static
cp -r frontend/dist/* deploy/backend/static/
echo "[完成] 前端文件复制完成"
echo

echo "[4/4] 复制启动脚本和配置文件..."

# 确保 deploy 目录存在
mkdir -p deploy

# 复制 Windows 批处理脚本（如果存在）
if [ -f "deploy/start.bat" ]; then
    echo "[信息] 使用已存在的 start.bat 文件"
    # 确保 start.bat 使用 Windows CRLF 换行符
    python3 -c "
with open('deploy/start.bat', 'rb') as f:
    data = f.read()
# 转换为 CRLF 格式
data = data.replace(b'\r\n', b'\n').replace(b'\r', b'\n').replace(b'\n', b'\r\n')
data = data.rstrip(b'\r\n') + b'\r\n'
with open('deploy/start.bat', 'wb') as f:
    f.write(data)
" 2>/dev/null && echo "[信息] 已确保 start.bat 使用 Windows CRLF 换行符"
else
    echo "[错误] 未找到 deploy/start.bat 文件，请确保该文件存在"
    echo "[提示] start.bat 应该已经在 deploy 目录中，如果没有请手动创建"
fi

if [ -f "deploy/stop.bat" ]; then
    echo "[信息] 使用已存在的 stop.bat 文件"
    # 确保 stop.bat 使用 Windows CRLF 换行符
    python3 -c "
with open('deploy/stop.bat', 'rb') as f:
    data = f.read()
# 转换为 CRLF 格式
data = data.replace(b'\r\n', b'\n').replace(b'\r', b'\n').replace(b'\n', b'\r\n')
data = data.rstrip(b'\r\n') + b'\r\n'
with open('deploy/stop.bat', 'wb') as f:
    f.write(data)
" 2>/dev/null && echo "[信息] 已确保 stop.bat 使用 Windows CRLF 换行符"
else
    echo "[警告] 未找到 deploy/stop.bat 文件"
fi

if [ -f "deploy/README_Windows.txt" ]; then
    echo "[信息] 使用已存在的 README_Windows.txt 文件"
else
    echo "[警告] 未找到 deploy/README_Windows.txt 文件"
fi

echo "[完成] 部署包准备完成"
echo

echo "========================================"
echo "构建完成！"
echo "========================================"
echo
echo "部署文件位置: deploy 目录"
echo
echo "下一步:"
echo "1. 检查 deploy 目录下的文件"
echo "2. 打包 deploy 目录为 zip 文件"
echo "3. 在 Windows 10 系统上解压并运行 start.bat"
echo
