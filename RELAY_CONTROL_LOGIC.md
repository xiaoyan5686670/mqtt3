# 继电器控制逻辑文档

## 概述

本文档说明继电器开关控制的前后端逻辑，确认统一使用 `pc/1` 主题。

## 控制流程

```
前端页面 → API请求 → MQTT发布 → MQTT订阅 → 数据库更新 → 前端显示更新
```

## 前端实现

### 1. 实时数据页面 (`RealTimeData.vue`)

**位置**: `frontend/src/views/RealTimeData.vue`

**功能**:
- 显示继电器状态（开启/关闭）
- 提供切换按钮控制继电器

**关键代码**:
```javascript
// 切换继电器状态
const toggleRelay = async () => {
  // 获取设备的发布主题（根据设备配置，避免硬编码）
  let topic = 'pc/1'  // 默认主题
  try {
    const topicResponse = await axios.get(`/api/devices/${selectedDeviceId.value}/publish-topic`)
    if (topicResponse.data && topicResponse.data.publish_topic) {
      topic = topicResponse.data.publish_topic
      console.log(`使用设备发布主题: ${topic} (来源: ${topicResponse.data.source})`)
    }
  } catch (topicError) {
    console.warn('获取设备发布主题失败，使用默认主题 pc/1:', topicError)
    // 如果获取失败，继续使用默认主题
  }
  
  // 根据当前状态决定发送的消息内容
  const isCurrentlyOn = sensorData.value.relay === 1
  const message = isCurrentlyOn ? 'relayoff' : 'relayon'
  
  const response = await axios.post('/api/mqtt/publish', {
    topic: topic,
    message: message,
    qos: 0
  })
}
```

**特点**:
- 主题: 动态获取（从设备配置或默认值）
- 消息: `relayon` (开启) / `relayoff` (关闭)
- QoS: 0
- 状态管理: 使用 `sendingRelay` 防止重复点击
- 容错: 如果获取主题失败，使用默认主题 `pc/1`

### 2. 首页仪表板 (`Dashboard.vue`)

**位置**: `frontend/src/views/Dashboard.vue`

**功能**:
- 在设备卡片中显示继电器状态
- 提供切换按钮控制继电器（仅管理员可见）

**关键代码**:
```javascript
// 切换继电器状态（带防抖和锁机制）
const toggleRelay = async (deviceId, sensor) => {
  // 获取设备的发布主题（根据设备配置，避免硬编码）
  let topic = 'pc/1'  // 默认主题
  try {
    const topicResponse = await axios.get(`/api/devices/${deviceId}/publish-topic`)
    if (topicResponse.data && topicResponse.data.publish_topic) {
      topic = topicResponse.data.publish_topic
      console.log(`使用设备发布主题: ${topic} (来源: ${topicResponse.data.source})`)
    }
  } catch (topicError) {
    console.warn('获取设备发布主题失败，使用默认主题 pc/1:', topicError)
    // 如果获取失败，继续使用默认主题
  }
  
  // 根据当前状态决定发送的消息内容
  const isCurrentlyOn = sensor.value > 0
  const message = isCurrentlyOn ? 'relayoff' : 'relayon'
  
  const response = await axios.post('/api/mqtt/publish', {
    topic: topic,
    message: message,
    qos: 0
  })
}
```

**特点**:
- 主题: 动态获取（从设备配置或默认值），与实时数据页面逻辑一致
- 消息: `relayon` (开启) / `relayoff` (关闭)
- QoS: 0
- 防抖机制: 使用 `relayToggleLock` 和 `sendingRelayId` 防止重复点击
- 权限控制: 仅管理员可见 (`authStore.canEdit`)
- 容错: 如果获取主题失败，使用默认主题 `pc/1`

## 后端实现

### 1. 设备发布主题 API (`devices.py`)

**位置**: `backend/api/devices.py`

**功能**:
- 根据设备ID获取该设备的发布主题
- 支持从主题配置、设备名称推断或使用默认值

**关键代码**:
```python
@router.get("/{device_id}/publish-topic")
def get_device_publish_topic(
    device_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取设备的发布主题（用于继电器控制等）"""
    device = device_service_module.get_device(db, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    # 如果设备有关联的主题配置，使用配置的发布主题
    if device.topic_config_id:
        topic_config = topic_config_service.get_topic_config(db, device.topic_config_id)
        if topic_config and topic_config.publish_topic:
            return {
                "device_id": device_id,
                "publish_topic": topic_config.publish_topic,
                "source": "topic_config"
            }
    
    # 尝试从设备名称推断主题（例如：pc_1 -> pc/1）
    # 或使用默认主题 pc/1
    ...
```

**特点**:
- 优先级: 主题配置 > 设备名称推断 > 默认值
- 返回: `{device_id, publish_topic, source}`

### 2. MQTT 发布 API (`mqtt_publish.py`)

**位置**: `backend/api/mqtt_publish.py`

**功能**:
- 接收前端发布请求
- 通过 MQTT 服务发布消息到指定主题

**关键代码**:
```python
@router.post("/publish")
async def publish_message(
    request: MQTTPublishRequest, 
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """发布消息到MQTT主题（仅管理员）"""
    mqtt_service = get_mqtt_service()
    success = mqtt_service.publish_message(request.topic, request.message, request.qos)
```

**特点**:
- 权限: 仅管理员可访问 (`require_admin`)
- 参数: `topic`, `message`, `qos`
- 返回: 成功/失败状态

### 2. MQTT 服务 (`mqtt_service.py`)

**位置**: `backend/services/mqtt_service.py`

**功能**:
- 订阅 MQTT 主题并处理消息
- 识别继电器控制命令并更新数据库

**关键代码**:
```python
def parse_and_save_sensor_data(self, device_id: int, payload: str):
    """解析并保存传感器数据"""
    # 首先检查是否是继电器控制消息（relayon/relayoff）
    payload_lower = payload.strip().lower()
    if payload_lower == 'relayon':
        # 收到开启命令，设置继电器状态为1
        self.save_sensor_data(device_id, 'Relay Status', 1, '')
        logger.info(f"收到继电器开启命令，设备ID: {device_id}")
        return
    elif payload_lower == 'relayoff':
        # 收到关闭命令，设置继电器状态为0
        self.save_sensor_data(device_id, 'Relay Status', 0, '')
        logger.info(f"收到继电器关闭命令，设备ID: {device_id}")
        return
```

**特点**:
- 消息识别: 不区分大小写 (`payload_lower`)
- 状态更新: 
  - `relayon` → `Relay Status = 1`
  - `relayoff` → `Relay Status = 0`
- 日志记录: 记录所有继电器控制命令

## 主题配置机制

### ✅ 支持设备独立主题配置（已修复硬编码问题）

**问题**: 之前硬编码使用 `pc/1` 主题，导致控制一个继电器会影响所有订阅该主题的设备。

**解决方案**: 
- 后端提供 API 端点 `/api/devices/{device_id}/publish-topic` 获取设备的发布主题
- 前端在控制继电器时，动态获取设备的发布主题
- 如果设备配置了主题配置（`topic_config_id`），使用配置的 `publish_topic`
- 如果没有配置，尝试从设备名称推断（如 `pc_1` → `pc/1`）
- 最后使用默认主题 `pc/1` 作为后备

**前端**:
- ✅ `RealTimeData.vue`: 动态获取设备发布主题
- ✅ `Dashboard.vue`: 动态获取设备发布主题

**后端**:
- ✅ `devices.py`: 提供 `/api/devices/{device_id}/publish-topic` 端点
- ✅ `mqtt_service.py`: 订阅所有配置的主题，处理各设备主题的消息

## 消息格式

### 发布消息格式

| 操作 | 主题 | 消息内容 | QoS |
|------|------|----------|-----|
| 开启继电器 | `pc/1` | `relayon` | 0 |
| 关闭继电器 | `pc/1` | `relayoff` | 0 |

### 接收消息格式

后端接收到的消息（不区分大小写）:
- `relayon` → 设置继电器状态为 1（开启）
- `relayoff` → 设置继电器状态为 0（关闭）

## 数据流

```
1. 用户点击继电器控制按钮（前端）
   ↓
2. 前端获取设备发布主题
   GET /api/devices/{device_id}/publish-topic
   ↓
3. 后端返回设备的发布主题
   {
     "device_id": 1,
     "publish_topic": "pc/1" 或设备配置的主题,
     "source": "topic_config" | "device_name" | "default"
   }
   ↓
4. 前端发送 POST /api/mqtt/publish 请求
   {
     "topic": "pc/1" 或设备配置的主题,
     "message": "relayon" 或 "relayoff",
     "qos": 0
   }
   ↓
5. 后端 API 接收请求，验证管理员权限
   ↓
6. MQTT 服务发布消息到设备对应的主题
   ↓
7. MQTT 服务订阅并接收到消息（同一服务）
   ↓
8. 解析消息，识别 relayon/relayoff
   ↓
9. 更新数据库 sensors 表（仅更新对应设备）
   - Relay Status = 1 (relayon)
   - Relay Status = 0 (relayoff)
   ↓
10. 前端轮询或 WebSocket 更新显示
```

## 权限控制

- **前端**: 继电器控制按钮仅管理员可见 (`authStore.canEdit`)
- **后端**: MQTT 发布 API 需要管理员权限 (`require_admin`)

## 防抖机制

### RealTimeData.vue
- 使用 `sendingRelay` 状态防止重复点击

### Dashboard.vue
- 使用 `relayToggleLock` (Set) 和 `sendingRelayId` 防止重复点击
- 添加 300ms 延迟后解锁

## 总结

✅ **主题已统一**: 所有继电器控制都使用 `pc/1` 主题

✅ **消息格式统一**: 
- 开启: `relayon`
- 关闭: `relayoff`

✅ **权限控制完善**: 前后端都有管理员权限检查

✅ **防抖机制完善**: 防止重复点击和并发请求

## 相关文件

- `frontend/src/views/RealTimeData.vue` - 实时数据页面继电器控制
- `frontend/src/views/Dashboard.vue` - 首页仪表板继电器控制
- `backend/api/devices.py` - 设备 API（包含获取发布主题端点）
- `backend/api/mqtt_publish.py` - MQTT 发布 API
- `backend/services/mqtt_service.py` - MQTT 服务（订阅和处理消息）
- `backend/models/device.py` - 设备模型（包含 `topic_config_id` 字段）
- `backend/models/topic_config.py` - 主题配置模型（包含 `publish_topic` 字段）

## 配置说明

### 如何为设备配置独立的发布主题

1. **创建主题配置**:
   - 进入"主题配置"页面
   - 创建新的主题配置
   - 设置 `publish_topic` 字段（如 `pc/2`、`device1/relay` 等）

2. **关联设备**:
   - 编辑设备
   - 选择对应的主题配置（`topic_config_id`）
   - 保存

3. **效果**:
   - 控制该设备的继电器时，会自动使用配置的发布主题
   - 不会影响其他设备的继电器控制
