# 设备在线/离线状态功能 - 修改清单

## 修改日期
2026-01-19

## 功能说明
在 Dashboard 首页增加设备在线/离线状态显示功能，通过集成 EMQX REST API 实时获取 MQTT 客户端连接状态。

## 修改文件列表

### 前端修改 (Frontend)

#### 1. `frontend/src/views/Dashboard.vue`
**修改内容：**
- ✅ 新增统计卡片区域（总设备数、在线设备数、离线设备数）
- ✅ 新增设备状态指示器（绿色/红色圆点）
- ✅ 新增 `fetchClientStatus()` 方法获取 EMQX 客户端状态
- ✅ 更新 `fetchDevicesWithSensors()` 方法集成在线状态
- ✅ 更新 `onlineDevices` 和 `offlineDevices` computed 属性
- ✅ 新增 CSS 样式（统计卡片、状态指示器、动画效果）

**关键代码：**
```javascript
// 获取EMQX客户端连接状态
const fetchClientStatus = async () => {
  const response = await axios.get('/api/mqtt-publish/clients')
  // 处理并返回在线客户端ID集合
}

// 判断设备在线状态
const isOnline = onlineClientIds.has(device.id) || onlineClientIds.has(device.name)
```

### 后端修改 (Backend)

#### 2. `backend/services/mqtt_service.py`
**修改内容：**
- ✅ 导入 `requests` 和 `Dict`, `Any` 类型
- ✅ 新增 `get_emqx_clients()` 方法

**新增方法：**
```python
def get_emqx_clients(self) -> Dict[str, Any]:
    """从EMQX API获取客户端连接状态"""
    # 获取MQTT配置
    # 构建EMQX API URL (默认端口18083)
    # 调用 GET /api/v5/clients
    # 返回客户端列表
```

#### 3. `backend/api/mqtt_publish.py`
**修改内容：**
- ✅ 新增 `/clients` API 端点

**新增端点：**
```python
@router.get("/clients")
async def get_mqtt_clients(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """获取EMQX客户端连接状态列表（仅管理员）"""
```

#### 4. `backend/requirements.txt`
**修改内容：**
- ✅ 新增 `requests==2.31.0` 依赖

### 新增文档 (Documentation)

#### 5. `EMQX_API_CONFIG.md`
**内容：**
- EMQX API 配置说明
- 默认配置参数
- 修改认证信息方法
- 功能验证步骤
- 故障排查指南

#### 6. `DEVICE_ONLINE_STATUS_FEATURE.md`
**内容：**
- 功能完整说明
- 技术实现细节
- 数据流程图
- 使用指南
- 故障排查
- 后续优化建议

#### 7. `设备在线状态功能-快速开始.md`
**内容：**
- 快速启动指南
- 预期效果展示
- 常见问题解答
- 技术支持信息

## API 变更

### 新增 API

**端点：** `GET /api/mqtt-publish/clients`  
**权限：** 需要管理员权限  
**功能：** 获取 EMQX 客户端连接状态列表  
**返回：** 
```json
{
  "data": [
    {
      "clientid": "device_001",
      "connected": true,
      "ip_address": "127.0.0.1",
      ...
    }
  ],
  "meta": {
    "count": 1
  }
}
```

## 数据库变更

**无数据库变更**

当前使用默认配置（admin/public）连接 EMQX API。

**未来优化：**
可在 `mqtt_configs` 表中添加以下字段：
- `api_username` - EMQX API 用户名
- `api_password` - EMQX API 密码
- `api_port` - EMQX API 端口（默认18083）

## 依赖变更

### Python 依赖
```diff
+ requests==2.31.0
```

### JavaScript 依赖
无变更

## 配置要求

### EMQX 服务器
- 版本：EMQX v5.x
- 管理 API 端口：18083（默认）
- 认证：admin/public（默认）

### 网络要求
- 后端服务需要能访问 EMQX API（http://{emqx_server}:18083）
- 防火墙开放 18083 端口（如需要）

## 部署步骤

### 1. 更新代码
```bash
git pull origin main
```

### 2. 安装新依赖
```bash
cd backend
pip install -r requirements.txt
```

### 3. 重启服务
```bash
# 重启后端
python main.py

# 重启前端（开发环境）
cd frontend
npm run dev
```

### 4. 验证功能
1. 访问 Dashboard：http://localhost:5173
2. 检查统计卡片是否显示正确
3. 检查设备状态指示器是否正常
4. 观察自动刷新（每5秒）

## 回滚方案

如需回滚此功能：

### 1. 前端回滚
恢复 `frontend/src/views/Dashboard.vue` 到修改前版本

### 2. 后端回滚
恢复以下文件：
- `backend/services/mqtt_service.py`
- `backend/api/mqtt_publish.py`
- `backend/requirements.txt`

### 3. 重启服务

## 已知问题

无

## 测试建议

### 功能测试
1. ✅ 设备在线时显示绿色状态
2. ✅ 设备离线时显示红色状态
3. ✅ 统计数字准确
4. ✅ 自动刷新正常工作
5. ✅ 权限控制正常（仅管理员可访问）

### 性能测试
1. ✅ 大量设备（100+）时响应速度
2. ✅ API 调用频率（5秒间隔）
3. ✅ 错误处理（EMQX 服务不可用时）

### 兼容性测试
1. ✅ Chrome
2. ✅ Firefox
3. ✅ Safari
4. ✅ Edge

## 相关链接

- [EMQX API 文档](https://docs.emqx.com/zh/emqx/v5.2/admin/api-docs.html#tag/Clients/paths/~1clients/get)
- [快速开始指南](./设备在线状态功能-快速开始.md)
- [完整功能说明](./DEVICE_ONLINE_STATUS_FEATURE.md)
- [EMQX API 配置](./EMQX_API_CONFIG.md)

## 贡献者

- 开发：AI Assistant
- 需求：用户
- 日期：2026-01-19
