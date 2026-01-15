# 继电器控制逻辑文档

## 概述

本文档说明继电器开关控制的前后端逻辑。**主题默认按设备隔离**（如 `pc/{device_id}`），也可通过设备关联的 TopicConfig 配置 `publish_topic` 覆盖，避免多个设备互相影响。

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
  let topic = `pc/${selectedDeviceId.value}`  // 默认：按设备隔离
  try {
    const topicResponse = await axios.get(`/api/devices/${selectedDeviceId.value}/publish-topic`)
    if (topicResponse.data && topicResponse.data.publish_topic) {
      topic = topicResponse.data.publish_topic
      console.log(`使用设备发布主题: ${topic} (来源: ${topicResponse.data.source})`)
    }
  } catch (topicError) {
    console.warn('获取设备发布主题失败，使用按设备隔离的默认主题:', topicError)
    // 如果获取失败，继续使用默认主题
  }
  
  // 根据当前状态决定发送的消息内容
  const isCurrentlyOn = sensorData.value.relay === 1
  const message = isCurrentlyOn ? 'relayoff' : 'relayon'
  
  const response = await axios.post('/api/mqtt-publish/publish', {
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
- **乐观更新**: 发送命令后立即更新前端显示，无需等待 MQTT 消息返回
- 容错: 如果获取主题失败，使用默认主题 `pc/{device_id}`（按设备隔离）

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
  let topic = `pc/${deviceId}`  // 默认：按设备隔离
  try {
    const topicResponse = await axios.get(`/api/devices/${deviceId}/publish-topic`)
    if (topicResponse.data && topicResponse.data.publish_topic) {
      topic = topicResponse.data.publish_topic
      console.log(`使用设备发布主题: ${topic} (来源: ${topicResponse.data.source})`)
    }
  } catch (topicError) {
    console.warn('获取设备发布主题失败，使用按设备隔离的默认主题:', topicError)
    // 如果获取失败，继续使用默认主题
  }
  
  // 根据当前状态决定发送的消息内容
  const isCurrentlyOn = sensor.value > 0
  const message = isCurrentlyOn ? 'relayoff' : 'relayon'
  
  const response = await axios.post('/api/mqtt-publish/publish', {
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
- **乐观更新**: 发送命令后立即更新前端显示，无需等待 MQTT 消息返回
- 权限控制: 仅管理员可见 (`authStore.canEdit`)
- 容错: 如果获取主题失败，使用默认主题 `pc/{device_id}`（按设备隔离）

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
    # 或使用默认主题 pc/{device_id}
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
- 最后使用默认主题 `pc/{device_id}` 作为后备（按设备隔离，避免串扰）

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
| 开启继电器 | `pc/{device_id}`（例：`pc/1`） | `relayon` | 0 |
| 关闭继电器 | `pc/{device_id}`（例：`pc/1`） | `relayoff` | 0 |

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
     "publish_topic": "pc/1"（示例）或设备配置的主题,
     "source": "topic_config" | "device_name" | "default" | "auto_matched_topic_config"
   }
   ↓
4. 前端发送 POST /api/mqtt/publish 请求
   {
     "topic": "pc/1"（示例）或设备配置的主题,
     "message": "relayon" 或 "relayoff",
     "qos": 0
   }
   ↓
5. 【乐观更新】前端立即更新显示状态（无需等待）
   - 立即更新 UI 显示（开启/关闭）
   - 记录期望状态和操作时间戳
   ↓
6. 后端 API 接收请求，验证管理员权限
   ↓
7. MQTT 服务发布消息到设备对应的主题
   ↓
8. MQTT 服务订阅并接收到消息（同一服务）
   ↓
9. 解析消息，识别 relayon/relayoff
   ↓
10. 更新数据库 sensors 表（仅更新对应设备）
    - Relay Status = 1 (relayon)
    - Relay Status = 0 (relayoff)
    ↓
11. 前端轮询获取最新数据
    ↓
12. 【期望状态保护】检查轮询到的数据
    - 如果在保护期内（5秒）且数据与期望状态一致 → 确认状态，清除保护
    - 如果在保护期内但数据不一致 → 保持期望状态显示（可能是旧数据）
    - 如果超过保护期 → 使用服务器数据
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

## 乐观更新机制（Optimistic Update）

### ✅ 解决的问题

**问题场景**:
1. 用户点击关闭按钮 → 发送 `relayoff` 命令
2. 前端状态仍显示"开启"（因为需要等待 MQTT 消息返回）
3. 用户再次点击 → 系统认为当前是"开启"，又发送 `relayoff` → 无效操作
4. 需要等待 MQTT 消息回来，状态才会更新
5. **结果**: 用户感觉开关"失灵"，无法快速连续操作

### ✅ 实现方案

**乐观更新（Optimistic Update）**:
- 发送命令后**立即更新前端显示状态**，无需等待 MQTT 消息返回
- 用户可以立即看到状态变化，可以快速连续操作

**期望状态保护机制**:
- 发送命令后记录**期望状态**（0 或 1）和操作时间戳
- 在 **5 秒保护期**内：
  - 如果轮询到的新数据与期望状态**一致** → 确认状态，清除保护
  - 如果轮询到的新数据与期望状态**不一致** → 可能是旧数据，保持期望状态显示
- 超过 5 秒后 → 使用服务器数据（避免永久不一致）

### 实现细节

#### RealTimeData.vue

```javascript
// 期望状态记录
const relayExpectedState = ref({
  value: null,      // 期望的状态值（0或1），null表示没有待确认的状态
  timestamp: 0,     // 最后操作的时间戳
  timeout: 5000     // 超时时间（5秒）
})

// 发送命令后立即更新
if (response.data.success) {
  const newState = isCurrentlyOn ? 0 : 1
  sensorData.value.relay = newState  // 乐观更新
  
  // 记录期望状态
  relayExpectedState.value = {
    value: newState,
    timestamp: Date.now(),
    timeout: 5000
  }
}

// 轮询数据时检查期望状态
if (sensor.type === 'Relay Status') {
  const now = Date.now()
  const timeSinceOperation = now - relayExpectedState.value.timestamp
  
  if (relayExpectedState.value.value !== null && 
      timeSinceOperation < relayExpectedState.value.timeout) {
    // 在保护期内
    if (sensor.value === relayExpectedState.value.value) {
      // 状态已确认，清除保护
      relayExpectedState.value.value = null
      tempSensorData.relay = sensor.value
    } else {
      // 状态不一致，保持期望状态
      tempSensorData.relay = relayExpectedState.value.value
    }
  } else {
    // 超过保护期，使用服务器数据
    tempSensorData.relay = sensor.value
  }
}
```

#### Dashboard.vue

```javascript
// 期望状态映射（支持多个设备）
const relayExpectedStates = ref(new Map())  // deviceId-sensorType -> {value, timestamp, timeout}

// 发送命令后立即更新
if (response.data.success) {
  const newState = isCurrentlyOn ? 0 : 1
  
  // 记录期望状态
  relayExpectedStates.value.set(sensorKey, {
    value: newState,
    timestamp: Date.now(),
    timeout: 5000
  })
  
  // 乐观更新本地状态
  sensorToUpdate.value = newState
}
```

### 效果

**之前**:
- ❌ 点击后需要等待 MQTT 消息才能看到状态变化
- ❌ 快速连续点击会"失灵"
- ❌ 用户体验差

**现在**:
- ✅ 点击后**立即**看到状态变化
- ✅ 可以快速连续操作，不会"失灵"
- ✅ 用户体验流畅
- ✅ 自动处理数据延迟和冲突

## 总结

✅ **主题按设备隔离**: 默认使用 `pc/{device_id}`（或 TopicConfig 配置的 `publish_topic`），避免多个设备互相影响

✅ **自动匹配 TopicConfig**: 当设备未关联 TopicConfig 时，根据设备名称自动匹配（通过 `subscribe_topics` 匹配）

✅ **消息格式统一**: 
- 开启: `relayon`
- 关闭: `relayoff`

✅ **权限控制完善**: 前后端都有管理员权限检查

✅ **防抖机制完善**: 防止重复点击和并发请求

✅ **乐观更新机制**: 发送命令后立即更新前端显示，无需等待 MQTT 消息返回，支持快速连续操作，避免"开关失灵"问题

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

#### 方式一：手动关联 TopicConfig（推荐）

1. **创建主题配置**:
   - 进入"主题配置"页面
   - 创建新的主题配置
   - 设置 `publish_topic` 字段（如 `pc/2`、`device1/relay` 等）
   - 设置 `subscribe_topics` 字段（如 `stm32/3`、`pc/2` 等）
   - 激活配置

2. **关联设备**:
   - 编辑设备
   - 选择对应的主题配置（`topic_config_id`）
   - 保存

3. **效果**:
   - 控制该设备的继电器时，会自动使用配置的发布主题
   - 不会影响其他设备的继电器控制

#### 方式二：自动匹配 TopicConfig（无需手动关联）

1. **创建主题配置**:
   - 进入"主题配置"页面
   - 创建新的主题配置
   - 设置 `publish_topic` 字段（如 `pc/2`）
   - 设置 `subscribe_topics` 字段，包含与设备名相关的主题（如设备名是 `stm32_3`，则设置 `stm32/3` 或 `stm32_3`）
   - 激活配置

2. **无需关联设备**:
   - 系统会自动根据设备名称匹配 TopicConfig
   - 匹配规则：设备名 `stm32_3` 会匹配 `subscribe_topics` 包含 `stm32/3` 或 `stm32_3` 的 TopicConfig

3. **效果**:
   - 控制该设备的继电器时，会自动使用匹配到的 TopicConfig 的发布主题
   - 支持设备名格式：`stm32_3`、`stm32/3`、`stm32-3` 等
