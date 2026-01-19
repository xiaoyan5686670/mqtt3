# EMQX API 配置说明

## 功能说明

系统已集成 EMQX REST API，用于实时获取 MQTT 客户端的连接状态，在 Dashboard 首页显示设备的在线/离线状态。

## 配置要求

### 1. EMQX 服务器要求

- EMQX 版本：v5.x
- 管理 API 端口：默认 18083
- API 认证：默认用户名 `admin`，密码 `public`

### 2. 默认配置

系统默认使用以下配置连接 EMQX API：

```
API 端口: 18083
用户名: admin
密码: public
```

### 3. 如果需要修改认证信息

如果你的 EMQX 使用了不同的管理 API 认证信息，需要：

1. 修改 `backend/services/mqtt_service.py` 中的以下代码：

```python
# 在 get_emqx_clients 方法中
api_username = getattr(mqtt_config, 'api_username', 'admin')  # 修改默认用户名
api_password = getattr(mqtt_config, 'api_password', 'public')  # 修改默认密码
```

2. 或者在数据库的 `mqtt_configs` 表中添加 `api_username` 和 `api_password` 字段（需要数据库迁移）

### 4. 功能验证

启动系统后，打开 Dashboard 首页，应该能看到：

1. **统计卡片**：显示总设备数、在线设备数、离线设备数
2. **状态指示器**：每个设备卡片左上角显示绿色（在线）或红色（离线）圆点
3. **自动刷新**：每 5 秒自动刷新一次设备状态

### 5. 故障排查

如果设备状态显示不正确：

1. 检查 EMQX 服务是否正常运行
2. 检查 EMQX 管理 API 端口（18083）是否可访问
3. 检查认证信息是否正确
4. 查看后端日志：`backend/logs/app.log`

### 6. EMQX API 参考

本功能使用的 EMQX API 端点：

```
GET http://{emqx_server}:18083/api/v5/clients
```

详细文档：https://docs.emqx.com/zh/emqx/v5.2/admin/api-docs.html#tag/Clients/paths/~1clients/get

### 7. 客户端 ID 匹配规则

系统通过以下方式匹配设备和 MQTT 客户端：

- 设备的 `id` 字段匹配客户端的 `clientid`
- 设备的 `name` 字段匹配客户端的 `clientid`

确保设备配置的 ID 或名称与 MQTT 客户端的 ClientID 一致。
