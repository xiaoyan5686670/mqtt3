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

echo "[4/5] 复制启动脚本和配置文件..."

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

echo "[完成] 启动脚本和配置文件复制完成"
echo

echo "[5/5] 复制用户初始化脚本..."

# 复制用户初始化 Python 脚本
if [ -f "deploy/init_admin_user.py" ]; then
    echo "[信息] 使用已存在的 init_admin_user.py 文件"
else
    echo "[警告] 未找到 deploy/init_admin_user.py 文件，将创建默认版本..."
    # 创建默认的 init_admin_user.py（从模板创建）
    cat > deploy/init_admin_user.py << 'INIT_SCRIPT_EOF'
# -*- coding: utf-8 -*-
"""
初始化管理员用户脚本
用于部署系统后创建默认管理员账户
执行方式: python init_admin_user.py

默认管理员账户:
  用户名: admin
  密码: admin123
⚠️  请在生产环境中立即修改默认密码！
"""
import sqlite3
import sys
import os
from pathlib import Path
from datetime import datetime

# 使用 passlib 的 pbkdf2_sha256 算法生成密码哈希
try:
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
except ImportError:
    print("错误: 请先安装 passlib: pip install passlib")
    sys.exit(1)


def get_database_path():
    """获取数据库文件路径"""
    # 脚本所在目录（deploy目录）
    script_dir = Path(__file__).parent
    
    # 尝试在 deploy 目录下查找数据库
    db_path = script_dir / "mqtt_iot.db"
    if db_path.exists():
        return str(db_path)
    
    # 尝试在 deploy/backend 目录下查找
    db_path = script_dir / "backend" / "mqtt_iot.db"
    if db_path.exists():
        return str(db_path)
    
    # 尝试在当前目录查找
    current_db = Path.cwd() / "mqtt_iot.db"
    if current_db.exists():
        return str(current_db)
    
    # 默认创建在脚本目录
    return str(script_dir / "mqtt_iot.db")


def check_user_exists(cursor, username):
    """检查用户是否存在"""
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    return cursor.fetchone() is not None


def create_admin_user():
    """创建默认管理员用户"""
    db_path = get_database_path()
    print(f"数据库路径: {db_path}")
    
    if not os.path.exists(db_path):
        print(f"错误: 数据库文件不存在: {db_path}")
        print("请先启动一次应用程序以创建数据库和表结构")
        sys.exit(1)
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查 users 表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        if not cursor.fetchone():
            print("错误: users 表不存在")
            print("请先运行数据库迁移脚本或启动应用程序以创建表结构")
            conn.close()
            sys.exit(1)
        
        # 检查是否已存在 admin 用户
        if check_user_exists(cursor, "admin"):
            print("管理员用户 'admin' 已存在，跳过创建")
            conn.close()
            return
        
        # 生成密码哈希（密码: admin123）
        password_hash = pwd_context.hash("admin123")
        
        # 获取当前时间
        now = datetime.utcnow().isoformat()
        
        # 插入管理员用户
        cursor.execute("""
            INSERT INTO users (username, email, hashed_password, is_active, is_admin, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            "admin",
            None,
            password_hash,
            1,  # is_active = True
            1,  # is_admin = True
            now,
            now
        ))
        
        conn.commit()
        print("=" * 50)
        print("✅ 成功创建默认管理员用户")
        print("=" * 50)
        print("用户名: admin")
        print("密码: admin123")
        print("角色: 管理员")
        print("=" * 50)
        print("\n⚠️  请在生产环境中立即修改默认密码！")
        print("\n提示: 登录后可以在 '用户管理' 页面修改密码")
        
        conn.close()
        
    except sqlite3.Error as e:
        print(f"数据库错误: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"错误: {e}")
        sys.exit(1)


if __name__ == '__main__':
    create_admin_user()
INIT_SCRIPT_EOF
fi

# 复制用户初始化批处理脚本
if [ -f "deploy/init_admin_user.bat" ]; then
    echo "[信息] 使用已存在的 init_admin_user.bat 文件"
    # 确保 init_admin_user.bat 使用 Windows CRLF 换行符
    python3 -c "
with open('deploy/init_admin_user.bat', 'rb') as f:
    data = f.read()
# 转换为 CRLF 格式
data = data.replace(b'\r\n', b'\n').replace(b'\r', b'\n').replace(b'\n', b'\r\n')
data = data.rstrip(b'\r\n') + b'\r\n'
with open('deploy/init_admin_user.bat', 'wb') as f:
    f.write(data)
" 2>/dev/null && echo "[信息] 已确保 init_admin_user.bat 使用 Windows CRLF 换行符"
else
    echo "[警告] 未找到 deploy/init_admin_user.bat 文件，将创建默认版本..."
    # 创建默认的 init_admin_user.bat
    cat > deploy/init_admin_user.bat << 'INIT_BAT_EOF'
@echo off
REM 初始化管理员用户脚本（Windows）
REM 用于部署系统后创建默认管理员账户

echo ================================================
echo 初始化管理员用户
echo ================================================
echo.

REM 检查 Python 是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到 Python，请先安装 Python 3.8+
    pause
    exit /b 1
)

REM 运行初始化脚本
python init_admin_user.py

echo.
echo ================================================
echo 按任意键退出...
pause >nul
INIT_BAT_EOF
    # 转换为 CRLF 格式
    python3 -c "
with open('deploy/init_admin_user.bat', 'rb') as f:
    data = f.read()
data = data.replace(b'\r\n', b'\n').replace(b'\r', b'\n').replace(b'\n', b'\r\n')
data = data.rstrip(b'\r\n') + b'\r\n'
with open('deploy/init_admin_user.bat', 'wb') as f:
    f.write(data)
" 2>/dev/null && echo "[信息] 已创建 init_admin_user.bat 并使用 Windows CRLF 换行符"
fi

# 复制用户初始化说明文档
if [ -f "deploy/INIT_ADMIN_USER.md" ]; then
    echo "[信息] 使用已存在的 INIT_ADMIN_USER.md 文件"
else
    echo "[警告] 未找到 deploy/INIT_ADMIN_USER.md 文件，将创建默认版本..."
    # 创建默认的 INIT_ADMIN_USER.md
    cat > deploy/INIT_ADMIN_USER.md << 'INIT_DOC_EOF'
# 初始化管理员用户

## 说明

部署系统后，`users` 表为空，无法登录系统。使用此脚本可以快速创建默认管理员账户。

## 默认管理员账户

- **用户名**: `admin`
- **密码**: `admin123`
- **角色**: 管理员（拥有所有权限）

⚠️ **重要**: 请在生产环境中立即修改默认密码！

## 使用方法

### Windows 系统

1. **方法一（推荐）**: 双击运行 `init_admin_user.bat`

2. **方法二**: 在命令行中执行
   ```cmd
   python init_admin_user.py
   ```

### Linux/Mac 系统

在终端中执行：
```bash
python3 init_admin_user.py
```

## 前提条件

1. **数据库已创建**: 确保已经启动过一次应用程序，或者数据库文件 `mqtt_iot.db` 已经存在且包含 `users` 表

2. **Python 环境**: 需要安装 Python 3.8+ 和 `passlib` 库
   ```bash
   pip install passlib
   ```

## 脚本说明

- 脚本会自动查找数据库文件位置
- 如果管理员用户已存在，会跳过创建
- 如果数据库或表不存在，会提示错误信息

## 修改密码

创建管理员账户后，可以：

1. 使用默认账户登录系统
2. 进入"用户管理"页面
3. 编辑 admin 用户，修改密码

## 注意事项

- 默认密码仅用于初始登录，请尽快修改
- 如果忘记管理员密码，可以重新运行此脚本（需要先删除现有 admin 用户）
- 建议在生产环境中使用强密码
INIT_DOC_EOF
fi

echo "[完成] 用户初始化脚本复制完成"
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
