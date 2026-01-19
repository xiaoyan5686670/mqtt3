# relay_status 字段显示问题修复说明

## 问题描述

前端首页没有显示 `relay_status` 开关控制按钮，导致无法发送开关量控制命令。

原因：
1. JSON 数据中 `relay_status` 的值是**字符串类型** (`"off"`)，而不是数字
2. TopicConfig 的 JSON 配置助手只为**数字类型**的字段生成映射配置
3. 后端默认解析逻辑也只处理数字类型的值

## 修复内容

### 1. 前端修改 (`frontend/src/views/TopicConfig.vue`)

增强了 `generateMapping` 函数，使其能够识别字符串类型的继电器/开关字段：

```javascript
// 处理字符串类型的继电器/开关状态
else if (typeof value === 'string' && 
         (keyLow.includes('relay') || keyLow.includes('switch') || 
          keyLow.includes('status') || keyLow.includes('开关'))) {
  mapping[key] = { 
    type: key, 
    unit: '' 
  }
}
```

### 2. 后端修改 (`backend/services/mqtt_service.py`)

增强了 JSON 解析逻辑，自动将字符串类型的继电器状态转换为数字：

- `"on"`, `"open"`, `"true"`, `"1"`, `"active"`, `"enabled"` → `1`
- `"off"`, `"close"`, `"false"`, `"0"`, `"inactive"`, `"disabled"` → `0`

## 使用步骤

### 步骤 1: 配置 JSON 解析映射

1. 访问 http://192.168.1.102:5173/topic-config
2. 编辑你的主题配置
3. 在 **JSON 解析配置** 区域，点击"显示 JSON 配置助手"
4. 粘贴你的示例数据：

```json
{
  "air_temperature_1": 19.299999237060548,
  "air_humidity_1": 15.199999809265136,
  "air_temperature_2": 0,
  "air_humidity_2": 0,
  "air_temperature_3": 0,
  "air_humidity_3": 0,
  "air_temperature_4": 19.299999237060548,
  "air_humidity_4": 14.100000381469726,
  "comp1_in_temperature_F": 17.299999237060546,
  "comp1_out_temperature_F": 17.700000762939454,
  "comp2_in_temperature_F": 18.100000381469728,
  "comp2_out_temperature_F": 0,
  "relay_status": "off"
}
```

5. 点击"生成映射建议"
6. 查看生成的配置（现在应该包含 `relay_status` 字段）：

```json
{
  "air_temperature_1": {
    "type": "air_temperature_1",
    "unit": "°C"
  },
  "air_humidity_1": {
    "type": "air_humidity_1",
    "unit": "%"
  },
  // ... 其他字段 ...
  "relay_status": {
    "type": "relay_status",
    "unit": ""
  }
}
```

7. 点击"应用建议"
8. 保存配置

### 步骤 2: 验证前端显示

1. 访问首页 http://192.168.1.102:5173/
2. 找到你的设备卡片
3. 确认在"其他传感器数据"区域能看到 `relay_status` 字段
4. 应该显示：
   - 当前状态徽章（ON/OFF）
   - 控制按钮（开启/关闭）

### 步骤 3: 测试开关控制

1. 点击设备卡片上的开关按钮
2. 系统会发送 MQTT 消息：
   - 开启：发送 `"relayon"` 到设备的发布主题
   - 关闭：发送 `"relayoff"` 到设备的发布主题

## 支持的字符串值格式

后端现在支持以下字符串值（不区分大小写）：

**开启状态** (转换为 1)：
- `"on"`
- `"open"`
- `"true"`
- `"1"`
- `"active"`
- `"enabled"`

**关闭状态** (转换为 0)：
- `"off"`
- `"close"`
- `"false"`
- `"0"`
- `"inactive"`
- `"disabled"`

## 识别规则

字段会被识别为继电器/开关类型，如果其名称（不区分大小写）包含：
- `relay`
- `switch`
- `status`（仅在配置助手中）
- `开关`

前端 Dashboard 会为这些字段显示：
- ON/OFF 状态徽章
- 开启/关闭控制按钮（需要编辑权限）

## 注意事项

1. **必须配置 JSON 解析映射**：字符串类型的字段不会被默认解析逻辑处理，必须在 Topic Config 中明确配置
2. **发布主题**：确保设备配置中设置了正确的 `publish_topic`，否则会使用默认主题 `pc/{device_id}`
3. **权限要求**：只有具有编辑权限的用户才能看到并使用开关控制按钮
4. **实时更新**：前端每 5 秒自动刷新数据，控制命令发送后会立即在界面上反映预期状态

## 故障排查

### 错误: 'float' object has no attribute 'get'

**问题原因**：JSON 配置格式不正确，配置项不是字典对象。

**正确格式**：
```json
{
  "relay_status": {
    "type": "relay_status",
    "unit": ""
  }
}
```

**错误格式**（会导致此错误）：
```json
{
  "relay_status": 0
}
```

**解决方案**：
1. 访问 Topic Config 页面
2. 编辑你的主题配置
3. 删除或修正 JSON 解析配置
4. 使用"JSON 配置助手"重新生成正确的配置
5. 保存配置并重启后端服务

### relay_status 仍然不显示？

1. 检查 Topic Config 中是否已正确配置 JSON 解析映射
2. 确认该主题配置已"激活"
3. 检查设备是否正在发送数据（查看实时数据页面）
4. 查看浏览器控制台是否有错误信息
5. 检查后端日志，确认没有解析错误

### 点击按钮无反应？

1. 确认你有编辑权限（以管理员或编辑者身份登录）
2. 检查设备的 publish_topic 是否正确配置
3. 查看浏览器控制台网络请求，确认 MQTT 发布请求是否成功
4. 检查 EMQX 服务是否正常运行

### 后端日志在哪里？

后端日志会在终端中显示。如果使用 `start_backend.sh` 启动，所有日志都会输出到终端。

关键日志关键词：
- `ERROR` - 错误信息
- `WARNING` - 警告信息
- `JSON 配置格式错误` - 配置格式问题
- `无法转换` - 数据转换问题

## 相关文件

- 前端：`frontend/src/views/TopicConfig.vue`
- 前端：`frontend/src/views/Dashboard.vue`
- 后端：`backend/services/mqtt_service.py`
