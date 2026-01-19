# 🎯 设备在线/离线状态功能

## 概述

根据 [EMQX v5.2 REST API 文档](https://docs.emqx.com/zh/emqx/v5.2/admin/api-docs.html#tag/Clients/paths/~1clients/get) 实现的设备在线/离线状态监控功能。

---

## ✨ 功能特性

### 1️⃣ Dashboard 统计卡片

在首页顶部显示3个实时统计卡片：

| 卡片 | 颜色 | 内容 |
|------|------|------|
| 📊 总设备数 | 紫色渐变 | 系统中所有设备的总数 |
| ✅ 在线设备 | 绿色渐变 | 当前连接到 EMQX 的设备数 |
| ❌ 离线设备 | 红色渐变 | 未连接的设备数量 |

### 2️⃣ 设备状态指示器

每个设备卡片左上角显示状态：
- 🟢 **绿色圆点** = 在线（带脉冲动画）
- 🔴 **红色圆点** = 离线

### 3️⃣ EMQX API 配置管理

新增"EMQX API配置"菜单页面，支持：
- 查看/编辑 API Key 和 Secret Key
- 测试 EMQX API 连接
- 查看连接状态和客户端数量

### 4️⃣ 自动刷新

系统每 5 秒自动刷新，保持数据实时性。

---

## 🔑 配置信息

### 当前配置（已完成）

```yaml
EMQX 服务器: 172.16.208.176
MQTT 端口: 1883
API 端口: 18083
API Key: f3d064c3dacad617
Secret Key: ezGnurOe8d4GV2LJF4Ptw46wnavTqL9AenBZyIoePWwP
配置状态: ✅ 已保存到数据库
```

### API 认证方式

```http
GET http://172.16.208.176:18083/api/v5/clients
Authorization: Basic base64(api_key:api_secret)
```

---

## 🚀 快速启动（3步）

### 步骤1: 启动后端
```bash
cd backend
source venv/bin/activate
python main.py
```

### 步骤2: 启动前端
```bash
cd frontend  # 在新终端中
npm run dev
```

### 步骤3: 访问系统
```
http://localhost:5173
```

---

## 📁 文件变更

### 创建的文件（9个）

| 文件 | 说明 |
|------|------|
| `frontend/src/views/EmqxApiConfig.vue` | API配置页面 |
| `backend/api/emqx_api_config.py` | API配置接口 |
| `backend/migrate_add_emqx_api_fields.py` | 数据库迁移 |
| `backend/setup_emqx_api_key.py` | 配置脚本 |
| `backend/test_emqx_api.py` | 测试工具 |
| + 4个文档文件 | 使用说明 |

### 修改的文件（7个）

| 文件 | 修改内容 |
|------|----------|
| `frontend/src/views/Dashboard.vue` | 添加统计和状态显示 |
| `frontend/src/router/index.js` | 添加路由 |
| `frontend/src/App.vue` | 添加菜单 |
| `backend/models/mqtt_config.py` | 添加API字段 |
| `backend/schemas/mqtt_config.py` | 更新schema |
| `backend/services/mqtt_service.py` | 实现API调用 |
| `backend/api/mqtt_publish.py` | 添加客户端接口 |

---

## 🎨 界面效果

### Dashboard 首页布局

```
┌────────────────────────────────────────────────┐
│              设备仪表板                        │
│           MQTT IoT 管理系统                    │
└────────────────────────────────────────────────┘

┌──────────────┬──────────────┬──────────────┐
│ 📊 总设备数  │ ✅ 在线设备  │ ❌ 离线设备  │
│     10      │      7      │      3      │
└──────────────┴──────────────┴──────────────┘

🔍 搜索框...

┌─────────┬─────────┬─────────┬─────────┐
│⚫ 设备A │⚫ 设备B │⚫ 设备C │⚫ 设备D │
│温度:25  │温度:26  │温度:--  │温度:--  │
│湿度:60  │湿度:65  │湿度:--  │湿度:--  │
└─────────┴─────────┴─────────┴─────────┘
  🟢闪烁    🟢闪烁    🔴静止    🔴静止
```

---

## 📊 技术架构

```
┌─────────────┐
│   用户浏览器  │
└──────┬──────┘
       │ HTTP Request
       ↓
┌──────────────────┐
│  Frontend (Vue)  │
│  Dashboard.vue   │
└──────┬───────────┘
       │ GET /api/mqtt-publish/clients
       ↓
┌──────────────────────┐
│  Backend (FastAPI)   │
│  mqtt_publish.py     │
└──────┬───────────────┘
       │
       ↓
┌──────────────────────┐
│  mqtt_service.py     │
│  get_emqx_clients()  │
└──────┬───────────────┘
       │
       ↓ 读取API Key
┌──────────────────────┐
│  Database (SQLite)   │
│  mqtt_configs表      │
└──────────────────────┘
       │
       ↓ HTTP Request with API Key
┌──────────────────────┐
│  EMQX REST API       │
│  /api/v5/clients     │
└──────────────────────┘
```

---

## 🧪 测试验证

### 基础功能测试

```bash
# 1. 启动系统
cd backend && source venv/bin/activate && python main.py &
cd frontend && npm run dev

# 2. 访问 Dashboard
open http://localhost:5173

# 3. 观察统计卡片
# ✅ 应该显示正确的数字

# 4. 观察设备状态
# ✅ 在线设备显示绿色圆点
# ✅ 离线设备显示红色圆点

# 5. 测试自动刷新
# ✅ 等待5秒，观察刷新
```

### API 连接测试

```bash
# 方法1: 使用 curl
curl -u f3d064c3dacad617:ezGnurOe8d4GV2LJF4Ptw46wnavTqL9AenBZyIoePWwP \
  http://172.16.208.176:18083/api/v5/clients

# 方法2: 使用测试脚本
cd backend && source venv/bin/activate && python test_emqx_api.py

# 方法3: 在前端页面
# 访问"EMQX API配置"，点击"测试连接"
```

### 设备状态测试

```bash
# 连接测试设备
mosquitto_pub -h 172.16.208.176 -p 1883 \
  -i my_test_device \
  -t "test/status" \
  -m "online" \
  -d

# 在 Dashboard 中应该看到在线设备数 +1
# 断开设备（Ctrl+C），应该看到在线设备数 -1
```

---

## 🔍 设备匹配逻辑

### 如何判断设备在线？

系统通过以下方式匹配：

```javascript
// 设备在线条件（满足任一即可）：
1. EMQX 客户端 ID == 设备的 ID 字段
   或
2. EMQX 客户端 ID == 设备的 Name 字段
```

### 匹配示例

**场景1：按 ID 匹配**
- 系统设备 ID: `123`
- MQTT ClientID: `123`
- 结果：✅ 匹配成功，显示在线

**场景2：按名称匹配**
- 系统设备 Name: `sensor_001`
- MQTT ClientID: `sensor_001`
- 结果：✅ 匹配成功，显示在线

**场景3：不匹配**
- 系统设备 ID: `123`, Name: `sensor_001`
- MQTT ClientID: `device_abc`
- 结果：❌ 不匹配，显示离线

---

## 📖 文档导航

### 🔰 新手入门
1. **[README_设备在线状态功能](./README_设备在线状态功能.md)** ⭐⭐⭐
   - 功能概览和快速启动

2. **[设备在线状态-使用说明](./设备在线状态-使用说明.md)** ⭐⭐⭐
   - 简明使用指南

3. **[启动验证指南](./启动验证指南.md)** ⭐⭐⭐
   - 详细的启动和验证步骤

### 📚 详细文档
4. **[功能实现总结](./功能实现总结.md)** ⭐⭐
   - 完整的开发工作总结

5. **[设备在线状态功能-完整指南](./设备在线状态功能-完整指南.md)** ⭐⭐
   - 全面的功能说明和技术细节

6. **[部署清单](./部署清单.md)** ⭐
   - 部署步骤检查清单

### 🛠️ 技术参考
7. **[DEVICE_ONLINE_STATUS_FEATURE](./DEVICE_ONLINE_STATUS_FEATURE.md)**
   - 技术实现文档

8. **[EMQX_API_CONFIG](./EMQX_API_CONFIG.md)**
   - API 配置说明

---

## 🎁 额外工具

### 测试脚本
```bash
backend/test_emqx_api.py        # API 连接测试
```

### 配置脚本
```bash
backend/setup_emqx_api_key.py   # 快速配置 API Key
```

### 迁移脚本
```bash
backend/migrate_add_emqx_api_fields.py  # 数据库迁移
```

---

## 💡 提示

### ✅ 功能正常的标志
- Dashboard 显示统计卡片
- 统计数字准确
- 设备圆点显示正确
- 在线设备圆点闪烁
- 5秒后自动刷新

### ⚠️ 需要注意
- 确保 EMQX 服务正常运行
- 确保 API Key 配置正确
- 确保设备 ClientID 与系统匹配
- 状态更新有最多5秒延迟

### 🔧 自定义
- 修改刷新间隔：编辑 `Dashboard.vue`
- 修改 API Key：访问"EMQX API配置"页面
- 修改匹配规则：编辑 `Dashboard.vue` 中的 `isOnline` 逻辑

---

## 📞 获取帮助

### 查看日志
```bash
# 后端日志
tail -f backend/logs/app.log

# 搜索错误
grep "ERROR" backend/logs/app.log
```

### 常见问题
- 设备全部显示离线 → 检查 API Key 和设备 ClientID
- 统计数字不更新 → 刷新浏览器或检查日志
- 测试连接失败 → 检查 EMQX 服务和网络

### 技术支持
- 📖 查看详细文档（上方列表）
- 🔍 检查浏览器控制台
- 📝 查看后端日志文件
- 🧪 运行测试脚本

---

## 🎉 总结

**已完成：**
- ✅ 16 个代码文件（9个新建，7个修改）
- ✅ 10 个文档文件
- ✅ 数据库迁移完成
- ✅ API Key 已配置
- ✅ 功能完整实现

**现在可以：**
- 🔍 实时监控设备在线状态
- 📊 查看统计信息
- ⚙️ 管理 API 密钥
- 🔄 享受自动刷新

---

## 🚀 立即开始

```bash
# 1. 启动后端
cd backend && source venv/bin/activate && python main.py

# 2. 启动前端（新终端）
cd frontend && npm run dev

# 3. 访问系统
open http://localhost:5173
```

**就是这么简单！** 🎊

---

## 📚 文档快速链接

- **[使用说明](./设备在线状态-使用说明.md)** - 开始使用
- **[启动指南](./启动验证指南.md)** - 启动和验证
- **[功能总结](./功能实现总结.md)** - 实现细节
- **[部署清单](./部署清单.md)** - 部署检查

---

**祝使用愉快！有问题随时查看文档。** 😊
