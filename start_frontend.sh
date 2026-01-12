#!/bin/bash
# 前端启动脚本

cd "$(dirname "$0")/frontend"

# 检查node_modules
if [ ! -d "node_modules" ]; then
    echo "安装前端依赖..."
    npm install
fi

# 获取本机所有 IP 地址（用于显示）
echo "========================================="
echo "前端开发服务器启动中..."
echo "========================================="
echo "虚拟机内部 IP 地址："
if command -v ifconfig >/dev/null 2>&1; then
    INTERNAL_IP=$(ifconfig | grep -E "inet " | grep -v "127.0.0.1" | head -1 | awk '{print $2}')
    if [ ! -z "$INTERNAL_IP" ]; then
        echo "  - 虚拟机内网: http://$INTERNAL_IP:5173"
    fi
elif command -v ip >/dev/null 2>&1; then
    INTERNAL_IP=$(ip addr show | grep "inet " | grep -v "127.0.0.1" | head -1 | awk '{print $2}' | cut -d'/' -f1)
    if [ ! -z "$INTERNAL_IP" ]; then
        echo "  - 虚拟机内网: http://$INTERNAL_IP:5173"
    fi
else
    echo "  - 虚拟机内网: (无法自动检测，请查看 Vite 输出)"
fi

# 提示宿主机访问地址（如果是虚拟机环境）
echo ""
if [ ! -z "$VM_HOST_IP" ]; then
    echo "⚠️  虚拟机环境检测到 VM_HOST_IP 环境变量："
    echo "  - 远程访问地址: http://$VM_HOST_IP:5173"
    echo "  - (确保在虚拟化管理平台配置了端口转发: $VM_HOST_IP:5173 -> $INTERNAL_IP:5173)"
else
    echo "⚠️  如果是虚拟机环境："
    echo "  - Vite 显示的 Network 地址是虚拟机内部 IP（正常）"
    echo "  - 远程访问请使用宿主机/网关 IP + 端口转发"
    echo "  - 例如: http://172.16.208.176:5173 (需要在虚拟化管理平台配置端口转发)"
    echo "  - 提示: 可以设置环境变量 VM_HOST_IP=172.16.208.176 来自定义宿主机 IP"
fi
echo "  - 本地访问: http://localhost:5173"
echo "  - 虚拟机内网访问: http://$INTERNAL_IP:5173"
echo ""
echo "========================================="
echo ""

# 启动开发服务器
# 使用 --host 0.0.0.0 确保监听所有网络接口（已配置在 vite.config.js 中）
npm run dev