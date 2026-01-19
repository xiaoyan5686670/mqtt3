# 设备在线状态功能 - 快速启动

## ✅ 已完成配置

您的 EMQX API Key 已经配置好：
- ✅ 数据库迁移完成
- ✅ API Key 已设置 (f3d064c3dacad617)
- ✅ 前端页面已创建
- ✅ 后端 API 已实现

## 🚀 立即启动

### 1. 启动后端

```bash
cd backend
source venv/bin/activate
python main.py
```

等待看到：
```
INFO: 启动应用: MQTT IoT管理系统 v1.0.0
INFO: MQTT服务启动成功
INFO: Uvicorn running on http://0.0.0.0:8000
```

### 2. 启动前端

打开新的终端：

```bash
cd frontend
npm run dev
```

等待看到：
```
VITE ready in xxx ms
➜  Local:   http://localhost:5173/
```

### 3. 访问系统

打开浏览器：http://localhost:5173

## 🎯 查看效果

### Dashboard 首页应该显示：

**1. 顶部统计卡片（3个卡片）**
```
┌─────────────┬─────────────┬─────────────┐
│ 总设备数: 10 │ 在线设备: 7  │ 离线设备: 3  │
│   (紫色)    │   (绿色)    │   (红色)    │
└─────────────┴─────────────┴─────────────┘
```

**2. 设备卡片状态指示器**
- 🟢 绿色圆点 = 在线（会脉冲闪烁）
- 🔴 红色圆点 = 离线

**3. 自动刷新**
- 每 5 秒自动更新一次

## 🔧 管理 API 配置

### 访问配置页面

点击导航栏的"EMQX API配置"菜单

### 页面功能

1. **查看当前配置**
   - API 端口: 18083
   - API Key: f3d064c3dacad617
   - Secret Key: ••••••••

2. **测试连接**
   - 点击"测试连接"按钮
   - 查看连接结果和客户端数量

3. **修改配置**
   - 输入新的 API Key 和 Secret Key
   - 点击"测试连接"验证
   - 点击"保存配置"

## 🐛 快速故障排查

### 如果所有设备显示离线：

**快速检查：**

```bash
# 1. 测试 EMQX API 是否可访问
curl -u f3d064c3dacad617:ezGnurOe8d4GV2LJF4Ptw46wnavTqL9AenBZyIoePWwP \
  http://172.16.208.176:18083/api/v5/clients

# 2. 查看后端日志
tail -20 backend/logs/app.log

# 3. 检查 EMQX 服务
curl http://172.16.208.176:18083
```

### 如果看到认证错误：

1. 在前端"EMQX API配置"页面重新保存 API Key
2. 点击"测试连接"验证
3. 刷新 Dashboard 页面

## 📱 界面预览

### 统计卡片效果

```
╔═══════════════════════╗
║  📊 总设备数          ║
║       10             ║
║                      ║
║  紫色渐变背景         ║
║  鼠标悬停有动画       ║
╚═══════════════════════╝
```

### 设备卡片效果

```
┌────────────────────────┐
│ ⚫ 温湿度传感器 A      │ <- 绿色脉冲圆点
│                        │
│ 🌡️ 温度: 25.0°C       │
│ 💧 湿度: 60.0%         │
│                        │
│ ID: 1  📅 2026-01-19   │
│           [查看详情]   │
└────────────────────────┘
```

## 🎓 5分钟快速体验

### 1. 启动系统 (2分钟)
```bash
# 终端1: 启动后端
cd backend && source venv/bin/activate && python main.py

# 终端2: 启动前端
cd frontend && npm run dev
```

### 2. 访问 Dashboard (1分钟)
- 打开浏览器: http://localhost:5173
- 登录系统
- 查看首页统计卡片和设备状态

### 3. 测试 API 配置 (1分钟)
- 点击"EMQX API配置"菜单
- 点击"测试连接"按钮
- 查看连接结果

### 4. 测试设备状态 (1分钟)
- 连接一个 MQTT 测试客户端
- 在 Dashboard 中观察设备变为在线
- 断开客户端，观察设备变为离线

## 📦 文件结构

```
mqtt3/
├── frontend/
│   ├── src/
│   │   ├── views/
│   │   │   ├── Dashboard.vue          ✅ 已更新
│   │   │   └── EmqxApiConfig.vue      ✅ 新建
│   │   ├── router/index.js            ✅ 已更新
│   │   └── App.vue                    ✅ 已更新
│   └── package.json
│
├── backend/
│   ├── api/
│   │   ├── emqx_api_config.py         ✅ 新建
│   │   ├── mqtt_publish.py            ✅ 已更新
│   │   └── __init__.py                ✅ 已更新
│   ├── services/
│   │   └── mqtt_service.py            ✅ 已更新
│   ├── models/
│   │   └── mqtt_config.py             ✅ 已更新
│   ├── migrate_add_emqx_api_fields.py ✅ 新建
│   ├── setup_emqx_api_key.py          ✅ 新建
│   └── requirements.txt               ✅ 已更新
│
└── 文档/
    ├── 设备在线状态功能-完整指南.md    ✅ 本文档
    ├── DEVICE_ONLINE_STATUS_FEATURE.md ✅ 技术文档
    ├── EMQX_API_CONFIG.md              ✅ 配置说明
    └── CHANGES.md                      ✅ 变更清单
```

## ✨ 立即开始使用

执行以下命令启动系统：

```bash
# 1. 启动后端（在backend目录）
cd backend
source venv/bin/activate
python main.py

# 2. 在新终端启动前端（在frontend目录）
cd frontend
npm run dev

# 3. 打开浏览器
# 访问: http://localhost:5173
```

就这么简单！🎉

---

**需要帮助？** 查看完整文档：`设备在线状态功能-完整指南.md`
