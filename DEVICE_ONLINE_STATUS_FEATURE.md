# 设备在线/离线状态功能说明

## 功能概述

在 Dashboard 首页增加了设备在线/离线状态显示功能，通过集成 EMQX REST API 实时获取 MQTT 客户端连接状态。

## 功能特性

### 1. 统计卡片

在 Dashboard 顶部显示三个统计卡片：

- **总设备数**：显示系统中所有设备的总数
- **在线设备**：显示当前连接到 MQTT 服务器的设备数量（绿色）
- **离线设备**：显示未连接到 MQTT 服务器的设备数量（红色）

### 2. 设备状态指示器

每个设备卡片的左上角显示状态指示器：

- **绿色圆点**：设备在线（带脉冲动画效果）
- **红色圆点**：设备离线

### 3. 自动刷新

系统每 5 秒自动刷新一次设备列表和连接状态，确保显示最新的在线/离线状态。

## 技术实现

### 前端修改

#### 文件：`frontend/src/views/Dashboard.vue`

**新增功能：**

1. **统计卡片 UI**
   ```vue
   <div class="stats-container mb-4">
     <div class="row g-3">
       <div class="col-md-4">
         <div class="stat-card stat-card-total">...</div>
       </div>
       <div class="col-md-4">
         <div class="stat-card stat-card-online">...</div>
       </div>
       <div class="col-md-4">
         <div class="stat-card stat-card-offline">...</div>
       </div>
     </div>
   </div>
   ```

2. **设备状态指示器**
   ```vue
   <span 
     class="status-indicator me-2" 
     :class="deviceData.isOnline ? 'status-online' : 'status-offline'"
   >
     <i class="fas fa-circle"></i>
   </span>
   ```

3. **JavaScript 方法**
   - `fetchClientStatus()`: 调用后端 API 获取 EMQX 客户端连接状态
   - 更新 `fetchDevicesWithSensors()`: 整合客户端状态到设备数据
   - 更新 `onlineDevices` 和 `offlineDevices` computed 属性

4. **CSS 样式**
   - 统计卡片样式（带渐变色和悬停效果）
   - 状态指示器样式（带脉冲动画）

### 后端修改

#### 1. 文件：`backend/services/mqtt_service.py`

**新增方法：**

```python
def get_emqx_clients(self) -> Dict[str, Any]:
    """从EMQX API获取客户端连接状态"""
    # 构建 EMQX API URL
    # 调用 EMQX REST API: GET /api/v5/clients
    # 返回客户端列表数据
```

**功能：**
- 从数据库获取 MQTT 配置
- 构建 EMQX API 请求（默认端口 18083）
- 使用基本认证（默认 admin/public）
- 返回客户端连接状态列表

#### 2. 文件：`backend/api/mqtt_publish.py`

**新增 API 端点：**

```python
@router.get("/clients")
async def get_mqtt_clients(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """获取EMQX客户端连接状态列表（仅管理员）"""
```

**端点信息：**
- 路径：`GET /api/mqtt-publish/clients`
- 权限：需要管理员权限
- 返回：EMQX 客户端连接状态数据

## 数据流程

```
1. 前端 Dashboard 页面加载
   ↓
2. 调用 fetchDevicesWithSensors()
   ↓
3. 并行调用：
   - fetchDevices(): 获取设备列表
   - fetchClientStatus(): 获取 EMQX 客户端状态
   ↓
4. 后端 /api/mqtt-publish/clients
   ↓
5. mqtt_service.get_emqx_clients()
   ↓
6. 调用 EMQX REST API: GET /api/v5/clients
   ↓
7. 返回客户端连接状态
   ↓
8. 前端匹配设备和客户端 ID
   ↓
9. 更新设备 isOnline 状态
   ↓
10. 渲染统计卡片和状态指示器
```

## 设备匹配规则

系统通过以下方式匹配设备和 MQTT 客户端：

```javascript
const isOnline = onlineClientIds.has(device.id) || onlineClientIds.has(device.name)
```

- 检查设备的 `id` 是否在在线客户端列表中
- 检查设备的 `name` 是否在在线客户端列表中

**重要提示：** 确保设备的 ID 或名称与 MQTT 客户端的 ClientID 一致。

## 配置说明

### EMQX API 默认配置

```python
api_port = 18083        # EMQX 管理 API 端口
api_username = 'admin'  # 默认用户名
api_password = 'public' # 默认密码
```

### 修改配置

如需修改认证信息，编辑 `backend/services/mqtt_service.py` 中的 `get_emqx_clients()` 方法：

```python
api_username = getattr(mqtt_config, 'api_username', 'your_username')
api_password = getattr(mqtt_config, 'api_password', 'your_password')
```

## 使用指南

### 1. 启动系统

```bash
# 启动后端
cd backend
python main.py

# 启动前端
cd frontend
npm run dev
```

### 2. 访问 Dashboard

打开浏览器访问：`http://localhost:5173`

### 3. 查看设备状态

- 顶部统计卡片显示总设备数、在线设备数、离线设备数
- 每个设备卡片左上角显示绿色（在线）或红色（离线）状态指示器
- 状态每 5 秒自动刷新

## 故障排查

### 设备显示全部离线

**可能原因：**
1. EMQX 服务未运行
2. EMQX API 端口未开放（18083）
3. 认证信息不正确
4. 设备 ClientID 与系统中的设备 ID/名称不匹配

**解决方案：**
1. 检查 EMQX 服务状态：`systemctl status emqx`
2. 检查端口可访问性：`curl http://localhost:18083/api/v5/clients`
3. 查看后端日志：`backend/logs/app.log`
4. 验证设备 ClientID 配置

### API 调用失败

**可能原因：**
1. 网络连接问题
2. EMQX API 认证失败
3. 防火墙阻止请求

**解决方案：**
1. 手动测试 API：
   ```bash
   curl -u admin:public http://localhost:18083/api/v5/clients
   ```
2. 检查 EMQX Dashboard 认证配置
3. 检查防火墙规则

## API 参考

### EMQX REST API

**端点：** `GET /api/v5/clients`

**响应示例：**
```json
{
  "data": [
    {
      "clientid": "device_001",
      "username": "user01",
      "connected": true,
      "ip_address": "127.0.0.1",
      "connected_at": "2026-01-19T10:00:00Z"
    }
  ],
  "meta": {
    "count": 1,
    "page": 1,
    "limit": 100
  }
}
```

**文档：** https://docs.emqx.com/zh/emqx/v5.2/admin/api-docs.html#tag/Clients/paths/~1clients/get

## 后续优化建议

1. **数据库迁移**：在 `mqtt_configs` 表中添加 `api_username`、`api_password`、`api_port` 字段
2. **配置界面**：在前端添加 EMQX API 配置管理页面
3. **连接历史**：记录设备上线/下线历史
4. **告警通知**：设备离线时发送告警通知
5. **批量操作**：支持批量查看和管理在线/离线设备
6. **性能优化**：添加客户端状态缓存，减少 API 调用频率

## 相关文件

- `frontend/src/views/Dashboard.vue` - 前端 Dashboard 页面
- `backend/services/mqtt_service.py` - MQTT 服务
- `backend/api/mqtt_publish.py` - MQTT 发布 API
- `EMQX_API_CONFIG.md` - EMQX API 配置说明
