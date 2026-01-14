# MQTT IoT管理系统 v3.0

基于前后端分离架构的MQTT物联网设备管理系统。

## 技术栈

### 后端
- **框架**: FastAPI (Python 3.12+)
- **数据库**: SQLite (SQLAlchemy ORM)
- **MQTT**: paho-mqtt
- **认证**: JWT (python-jose)

### 前端
- **框架**: Vue 3
- **构建工具**: Vite
- **UI库**: Bootstrap 5
- **状态管理**: Pinia
- **路由**: Vue Router
- **HTTP客户端**: Axios

## 项目结构

```
mqtt3/
├── backend/                 # 后端API服务
│   ├── api/                # API路由
│   │   ├── devices.py      # 设备管理API
│   │   ├── sensors.py      # 传感器数据API
│   │   ├── mqtt_configs.py # MQTT配置API
│   │   └── topic_configs.py # 主题配置API
│   ├── core/               # 核心模块
│   │   ├── config.py       # 配置管理
│   │   ├── database.py     # 数据库配置
│   │   └── logging_config.py # 日志配置
│   ├── models/             # 数据模型
│   │   ├── device.py
│   │   ├── sensor.py
│   │   ├── mqtt_config.py
│   │   └── topic_config.py
│   ├── schemas/            # Pydantic schemas
│   │   ├── device.py
│   │   ├── sensor.py
│   │   ├── mqtt_config.py
│   │   └── topic_config.py
│   ├── services/           # 业务逻辑层
│   │   ├── device_service.py
│   │   ├── sensor_service.py
│   │   ├── mqtt_config_service.py
│   │   ├── topic_config_service.py
│   │   └── mqtt_service.py # MQTT服务
│   ├── main.py             # FastAPI应用入口
│   ├── requirements.txt    # Python依赖
│   └── .env.example        # 环境变量示例
│
└── frontend/               # 前端Vue应用
    ├── src/
    │   ├── api/            # API调用
    │   ├── components/     # 组件
    │   ├── views/          # 页面视图
    │   ├── router/         # 路由配置
    │   ├── stores/         # Pinia状态管理
    │   └── main.js         # 应用入口
    ├── package.json
    └── vite.config.js
```

## 快速开始

### 后端设置

1. **创建虚拟环境**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **配置环境变量**
```bash
cp .env.example .env
# 编辑 .env 文件，设置 SECRET_KEY 等配置
```

4. **启动后端服务**
```bash
# 开发模式
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 或直接运行
python main.py
```

后端API文档将自动生成在: http://localhost:8000/docs

### 前端设置

1. **安装依赖**
```bash
cd frontend
npm install
```

2. **启动开发服务器**
```bash
npm run dev
```

前端应用将运行在: http://localhost:5173

## 环境变量配置

### 后端 (.env)

```env
# 应用配置
APP_NAME="MQTT IoT管理系统"
DEBUG=false

# 安全配置（必须修改！）
SECRET_KEY=your-secret-key-here

# 数据库配置
DATABASE_URL=sqlite:///./mqtt_iot.db

# 服务器配置
HOST=0.0.0.0
PORT=8000

# CORS配置
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

## API端点

### 设备管理
- `GET /api/v1/devices` - 获取设备列表
- `GET /api/v1/devices/{id}` - 获取单个设备
- `POST /api/v1/devices` - 创建设备
- `PUT /api/v1/devices/{id}` - 更新设备
- `DELETE /api/v1/devices/{id}` - 删除设备

### 传感器数据
- `GET /api/v1/sensors/device/{device_id}` - 获取设备传感器数据
- `GET /api/v1/sensors/device/{device_id}/latest` - 获取设备最新传感器数据
- `GET /api/v1/sensors/latest` - 获取最新传感器数据

### MQTT配置
- `GET /api/v1/mqtt-configs` - 获取MQTT配置列表
- `POST /api/v1/mqtt-configs` - 创建MQTT配置
- `PUT /api/v1/mqtt-configs/{id}` - 更新MQTT配置
- `POST /api/v1/mqtt-configs/{id}/activate` - 激活MQTT配置

### 主题配置
- `GET /api/v1/topic-configs` - 获取主题配置列表
- `POST /api/v1/topic-configs` - 创建主题配置
- `PUT /api/v1/topic-configs/{id}` - 更新主题配置

## 主要功能

- ✅ 设备管理（增删改查）
- ✅ 传感器数据实时监控
- ✅ MQTT服务器配置管理
- ✅ 主题订阅配置
- ✅ 自动设备发现和创建
- ✅ 传感器数据自动解析和存储
- ✅ RESTful API接口
- ✅ 前后端完全分离

## 开发说明

### 后端开发

- 使用依赖注入管理数据库会话
- 服务层负责业务逻辑，API层负责请求处理
- 使用Pydantic进行数据验证
- 统一的异常处理和日志记录

### 前端开发

- Vue 3 Composition API
- Pinia进行状态管理
- Axios进行API调用
- 响应式设计，支持移动端

## 部署

### 后端部署

```bash
# 使用Gunicorn + Uvicorn Workers
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### 前端部署

```bash
# 构建生产版本
npm run build

# 构建产物在 dist/ 目录
# 可使用 Nginx 等Web服务器部署
```

## 许可证

MIT License

## 作者

基于原mqtt2项目重构优化# mqtt3
# mqtt3

BUG修复记录：
继电器控制按钮优化完成
修复的问题
防抖机制
添加 300ms 延迟，防止快速连续点击
使用 Set 作为锁，跟踪正在发送的传感器
双重检查
函数开始时检查是否已在发送中
如果正在发送，直接返回，忽略重复点击
事件处理优化
使用 @click.stop.prevent 防止事件冒泡和默认行为
确保点击事件只触发一次
状态管理
使用 isRelaySending() 函数统一检查发送状态
按钮禁用状态基于双重检查（sendingRelayId 和 relayToggleLock）
日志改进
添加更详细的日志，便于调试
记录设备ID和消息内容