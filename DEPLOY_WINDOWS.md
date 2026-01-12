# Windows 10 部署指南

本指南说明如何为 Windows 10 平台生成和部署 MQTT IoT 管理系统。

## 构建部署包

### 在 macOS/Linux 上构建

1. 确保已安装 Node.js 和 Python 3.8+
2. 运行构建脚本：
   ```bash
   chmod +x build_windows.sh
   ./build_windows.sh
   ```

### 在 Windows 上构建

1. 确保已安装 Node.js 和 Python 3.8+
2. 运行构建脚本：
   ```batch
   build_windows.bat
   ```

构建完成后，所有部署文件将位于 `deploy` 目录中。

## 打包部署文件

构建完成后，将 `deploy` 目录打包成 zip 文件：

```bash
cd deploy
zip -r ../mqtt-iot-windows-v1.0.0.zip .
```

或在 Windows 上使用压缩工具将 `deploy` 目录压缩为 zip 文件。

## Windows 10 安装部署

### 系统要求

- Windows 10 或更高版本
- Python 3.8 或更高版本
- 网络连接（用于首次安装依赖）

### 安装步骤

1. **解压部署包**
   - 将 zip 文件解压到任意目录（例如: `C:\mqtt-iot`）

2. **运行启动脚本**
   - 进入解压后的目录
   - 双击运行 `start.bat`
   - 首次运行会自动：
     - 创建 Python 虚拟环境
     - 安装所需的依赖包
     - 创建配置文件（`.env`）
     - 创建数据库文件（`mqtt_iot.db`）
     - 启动后端服务

3. **访问系统**
   - 等待服务启动完成（命令行窗口显示启动信息）
   - 打开浏览器访问：
     - **前端界面**: http://localhost:8000
     - **API 文档**: http://localhost:8000/docs
     - **健康检查**: http://localhost:8000/health

### 配置文件

首次运行后，会在 `backend` 目录下创建 `.env` 配置文件。

主要配置项：

- **SECRET_KEY**: JWT 签名密钥（生产环境必须修改）
- **HOST**: 服务器监听地址（默认: 0.0.0.0）
- **PORT**: 服务器端口（默认: 8000）
- **CORS_ORIGINS**: 允许的前端源地址（逗号分隔）
- **DATABASE_URL**: 数据库连接 URL（默认: sqlite:///./mqtt_iot.db）
- **DEBUG**: 调试模式开关（默认: false）

详细配置说明请参考 `deploy/README_Windows.txt`。

## 使用说明

### 启动服务

双击运行 `start.bat` 或右键选择"以管理员身份运行"（如果遇到权限问题）

### 停止服务

- **方法1**: 在运行 `start.bat` 的窗口中按 `Ctrl+C`
- **方法2**: 双击运行 `stop.bat`
- **方法3**: 直接关闭运行 `start.bat` 的命令行窗口

### 查看日志

日志文件位置: `backend\logs\app.log`

### 查看数据库

数据库文件位置: `backend\mqtt_iot.db`

可以使用 SQLite 工具查看，推荐工具：
- [DB Browser for SQLite](https://sqlitebrowser.org/)
- [SQLiteStudio](https://sqlitestudio.pl/)

## 常见问题

### 1. 端口被占用

**问题**: 启动时提示端口 8000 已被占用

**解决**: 修改 `backend\.env` 文件中的 `PORT` 配置为其他端口（如 8001）

### 2. Python 未找到

**问题**: 提示"未找到 Python"

**解决**:
- 安装 Python 3.8 或更高版本
- 下载地址: https://www.python.org/downloads/
- 安装时务必勾选 "Add Python to PATH"

### 3. 依赖安装失败

**问题**: 安装 Python 依赖包时出错

**解决**:
- 检查网络连接
- 使用国内镜像源（修改 `start.bat` 中的 pip 命令）:
  ```batch
  pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
  ```

### 4. 无法访问前端

**问题**: 浏览器访问 http://localhost:8000 无法打开

**解决**:
- 检查后端服务是否正常启动
- 访问 http://localhost:8000/docs 查看 API 文档是否可用
- 检查防火墙设置，确保允许端口访问
- 查看日志文件 `backend\logs\app.log` 查看错误信息

### 5. 前端页面空白或报错

**问题**: 前端页面加载但显示不正常

**解决**:
- 检查浏览器控制台（F12）的错误信息
- 确认后端 API 服务正常（访问 /docs）
- 清除浏览器缓存后重试
- 检查 `backend\static` 目录是否存在且包含前端文件

### 6. 数据库错误

**问题**: 数据库相关错误

**解决**:
- 删除 `backend\mqtt_iot.db` 文件重新创建
- 检查是否有足够的磁盘空间和文件权限
- 确认 SQLite 支持正常

## 性能优化建议

### 生产环境配置

1. **修改默认配置**
   - 将 `DEBUG` 设置为 `false`
   - 修改 `SECRET_KEY` 为随机生成的强密钥（可使用 `openssl rand -hex 32` 生成）
   - 设置合适的 `LOG_LEVEL`（建议 `INFO` 或 `WARNING`）

2. **数据库优化**
   - 如果数据量大，考虑使用 PostgreSQL 或 MySQL
   - 定期备份数据库文件
   - 配置数据库连接池

3. **安全建议**
   - 修改默认的 `SECRET_KEY`
   - 在生产环境使用 HTTPS（需要配置反向代理，如 Nginx）
   - 配置防火墙规则，限制访问来源
   - 定期更新依赖包
   - 使用环境变量管理敏感配置

4. **服务管理**
   - 可以配置为 Windows 服务，实现开机自启
   - 使用进程管理工具（如 Supervisor）管理服务
   - 配置日志轮转，避免日志文件过大

## 架构说明

### 部署架构

```
用户浏览器
    ↓
http://localhost:8000
    ↓
FastAPI 后端 (main.py)
    ├── API 路由 (/api/v1/*)
    └── 静态文件服务 (/static/*)
        └── 前端构建文件 (Vue 3 + Vite)
```

### 目录结构

```
deploy/
├── backend/              # 后端代码
│   ├── api/             # API 路由
│   ├── core/            # 核心模块
│   ├── models/          # 数据模型
│   ├── schemas/         # 数据模式
│   ├── services/        # 业务逻辑
│   ├── static/          # 前端静态文件（构建后）
│   ├── logs/            # 日志文件（运行时生成）
│   ├── venv/            # Python 虚拟环境（运行时生成）
│   ├── main.py          # 主程序入口
│   ├── requirements.txt # Python 依赖
│   └── .env             # 配置文件（运行时生成）
├── start.bat            # 启动脚本
├── stop.bat             # 停止脚本
└── README_Windows.txt   # 详细说明文档
```

## 技术支持

如果遇到其他问题，请：

1. 查看日志文件: `backend\logs\app.log`
2. 检查后端服务状态: http://localhost:8000/health
3. 查看 API 文档: http://localhost:8000/docs
4. 检查错误信息和控制台输出

## 版本信息

- **当前版本**: v1.0.0
- **目标平台**: Windows 10 或更高版本
- **Python 版本**: 3.8+
- **Node.js 版本**: 16+（仅用于构建）
