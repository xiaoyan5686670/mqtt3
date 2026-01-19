# 设备在线/离线状态功能 🎉

## ✅ 功能已完成并配置

在 Dashboard 首页实现了设备在线/离线状态显示功能，集成 EMQX REST API 获取实时连接状态。

## 🎯 功能特性

| 功能 | 说明 | 状态 |
|------|------|------|
| 统计卡片 | 显示总设备数、在线设备数、离线设备数 | ✅ 完成 |
| 状态指示器 | 设备卡片显示绿色/红色圆点 | ✅ 完成 |
| 脉冲动画 | 在线设备圆点闪烁效果 | ✅ 完成 |
| 自动刷新 | 每5秒自动更新状态 | ✅ 完成 |
| API 配置页面 | 管理 EMQX API Key | ✅ 完成 |
| 连接测试 | 测试 API 连接是否正常 | ✅ 完成 |

## 🔑 当前配置

```yaml
EMQX 服务器: 172.16.208.176
API 端口: 18083
API Key: f3d064c3dacad617
Secret Key: ezGnurOe8d4GV2LJF4Ptw46wnavTqL9AenBZyIoePWwP
状态: ✅ 已配置
```

## 🚀 快速启动

### 一键启动

```bash
# 启动后端
cd backend && source venv/bin/activate && python main.py

# 启动前端（新终端）
cd frontend && npm run dev

# 访问系统
open http://localhost:5173
```

### 期望效果

访问 Dashboard 后应该看到：

1. ✅ 顶部显示3个统计卡片
2. ✅ 每个设备卡片左上角有状态圆点
3. ✅ 在线设备圆点是绿色且闪烁
4. ✅ 离线设备圆点是红色且静止
5. ✅ 每5秒自动刷新

## 📁 文件变更

### 新建文件（9个）

**前端：**
1. `frontend/src/views/EmqxApiConfig.vue` - API 配置页面

**后端：**
2. `backend/api/emqx_api_config.py` - API 配置接口
3. `backend/migrate_add_emqx_api_fields.py` - 数据库迁移
4. `backend/setup_emqx_api_key.py` - 配置脚本
5. `backend/test_emqx_api.py` - 测试工具

**文档：**
6. `功能实现总结.md`
7. `设备在线状态功能-完整指南.md`
8. `启动验证指南.md`
9. `设备在线状态-使用说明.md`

### 修改文件（7个）

**前端：**
1. `frontend/src/views/Dashboard.vue` - 添加统计和状态显示
2. `frontend/src/router/index.js` - 添加路由
3. `frontend/src/App.vue` - 添加菜单

**后端：**
4. `backend/models/mqtt_config.py` - 添加 API 字段
5. `backend/schemas/mqtt_config.py` - 更新 schema
6. `backend/services/mqtt_service.py` - 实现 EMQX API 调用
7. `backend/api/mqtt_publish.py` - 添加客户端状态接口

## 🧪 快速测试

### 测试1: 查看 Dashboard

```bash
# 1. 启动系统
# 2. 访问 http://localhost:5173
# 3. 登录
# 4. 查看统计卡片和设备状态
```

### 测试2: 测试 API 连接

```bash
# 在浏览器中：
# 1. 点击"EMQX API配置"菜单
# 2. 点击"测试连接"按钮
# 3. 查看连接结果
```

### 测试3: 设备上下线

```bash
# 连接测试设备
mosquitto_pub -h 172.16.208.176 -p 1883 \
  -i test_001 -t "test" -m "hi" -d

# 观察 Dashboard 统计变化
# 断开设备（Ctrl+C）
# 再次观察变化
```

## 📖 文档索引

| 文档 | 描述 | 推荐 |
|------|------|------|
| **设备在线状态-使用说明.md** | 简明使用指南 | ⭐⭐⭐ 必读 |
| **启动验证指南.md** | 启动步骤和验证清单 | ⭐⭐⭐ 必读 |
| **功能实现总结.md** | 完整的实现总结 | ⭐⭐ 推荐 |
| **设备在线状态功能-完整指南.md** | 详细功能说明 | ⭐⭐ 推荐 |
| **QUICKSTART_ONLINE_STATUS.md** | 5分钟快速入门 | ⭐ 参考 |

## 🎨 界面预览

### Dashboard 统计卡片

```
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│  📊 总设备数    │  │  ✅ 在线设备    │  │  ❌ 离线设备    │
│       10       │  │       7        │  │       3        │
│    (紫色)      │  │    (绿色)      │  │    (红色)      │
└─────────────────┘  └─────────────────┘  └─────────────────┘
```

### 设备状态指示器

```
在线设备：
┌──────────────────┐
│ ⚫ 温湿度传感器A │  <- 绿色脉冲圆点
│ 🌡️ 温度: 25.0°C │
│ 💧 湿度: 60.0%  │
└──────────────────┘

离线设备：
┌──────────────────┐
│ ⚫ 温湿度传感器B │  <- 红色静止圆点
│ 🌡️ 温度: --    │
│ 💧 湿度: --     │
└──────────────────┘
```

## 🔍 技术要点

### 在线状态判断

```javascript
// 设备与 MQTT 客户端 ID 匹配
const isOnline = 
  onlineClientIds.has(device.id) ||      // 匹配设备ID
  onlineClientIds.has(device.name)       // 匹配设备名称
```

### API 调用

```python
# 使用 API Key 认证
GET http://172.16.208.176:18083/api/v5/clients
Authorization: Basic base64(api_key:api_secret)
```

### 自动刷新

```javascript
// 每5秒刷新一次
setInterval(fetchDevicesWithSensors, 5000)
```

## ⚡ 性能说明

- **刷新频率：** 5秒/次
- **API 超时：** 10秒
- **客户端限制：** 最多获取 10000 个
- **网络流量：** 约 1-10KB/次
- **资源占用：** 极低

## 🛠️ 管理和维护

### 修改 API Key

**方式1：前端配置页面**
1. 访问"EMQX API配置"菜单
2. 输入新的 API Key 和 Secret Key
3. 测试连接
4. 保存配置

**方式2：后端脚本**
```bash
# 编辑 setup_emqx_api_key.py
# 修改 api_key 和 api_secret 变量
# 运行脚本
cd backend
source venv/bin/activate
python setup_emqx_api_key.py
```

### 修改刷新间隔

编辑 `frontend/src/views/Dashboard.vue`：

```javascript
// 找到这一行，修改 5000（毫秒）
refreshInterval = setInterval(fetchDevicesWithSensors, 5000)

// 例如改为 10 秒：
refreshInterval = setInterval(fetchDevicesWithSensors, 10000)
```

### 查看日志

```bash
# 实时查看日志
tail -f backend/logs/app.log

# 查看 EMQX 相关日志
grep "EMQX" backend/logs/app.log

# 查看错误日志
grep "ERROR" backend/logs/app.log
```

## 📞 获取帮助

### 常见问题

**Q: 为什么需要配置 API Key？**  
A: EMQX v5.0 之后，必须使用专门的 API Key 才能访问 REST API，Dashboard 用户不能直接用于 API 认证。

**Q: API Key 在哪里创建？**  
A: 在 EMQX Dashboard 的"系统设置" -> "API 密钥"中创建。

**Q: 设备为什么显示离线？**  
A: 检查设备的 MQTT ClientID 是否与系统中的设备 ID 或名称匹配。

**Q: 如何查看详细的客户端信息？**  
A: 运行 `test_emqx_api.py` 或访问 EMQX Dashboard。

### 技术支持

- 📖 查看完整文档
- 🔍 检查后端日志
- 🧪 运行测试脚本
- 📱 查看浏览器控制台

## 🎓 参考资料

- [EMQX v5.2 API 文档](https://docs.emqx.com/zh/emqx/v5.2/admin/api-docs.html)
- [客户端列表 API](https://docs.emqx.com/zh/emqx/v5.2/admin/api-docs.html#tag/Clients/paths/~1clients/get)
- [API 认证说明](https://docs.emqx.com/zh/emqx/v5.2/admin/api.html)

---

## 🎉 恭喜！

您已成功实现设备在线/离线状态功能！

**现在您可以：**
- ✅ 实时监控设备连接状态
- ✅ 查看在线/离线设备统计
- ✅ 管理 EMQX API 密钥
- ✅ 享受自动刷新的便利

**立即启动系统看看效果吧！** 🚀
