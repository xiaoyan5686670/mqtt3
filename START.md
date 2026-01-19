# ⚡ 立即开始使用设备在线状态功能

## ✅ 配置已完成

API Key 已配置，功能可立即使用！

---

## 🚀 启动（2步）

### 1. 后端
```bash
cd backend
source venv/bin/activate
python main.py
```

### 2. 前端（新终端）
```bash
cd frontend
npm run dev
```

### 3. 访问
```
http://localhost:5173
```

---

## 👀 查看效果

登录后在 Dashboard 首页：

✅ 顶部看到 **3个统计卡片**  
✅ 设备卡片左上角有 **状态圆点**  
✅ 在线设备圆点 **绿色闪烁** 🟢  
✅ 离线设备圆点 **红色静止** 🔴  
✅ 每5秒 **自动刷新**  

---

## ⚙️ 管理配置

点击导航栏 **"EMQX API配置"** 可以：
- 查看当前配置
- 测试连接
- 修改 API Key

---

## 🐛 遇到问题？

### 快速检查
```bash
# 1. 测试 EMQX API
curl -u f3d064c3dacad617:ezGnurOe8d4GV2LJF4Ptw46wnavTqL9AenBZyIoePWwP \
  http://172.16.208.176:18083/api/v5/clients

# 2. 查看日志
tail -20 backend/logs/app.log
```

### 常见问题
- **全部离线？** → 检查 EMQX 服务和 API Key
- **不刷新？** → 按 F5 刷新浏览器
- **测试失败？** → 访问"EMQX API配置"测试连接

---

## 📚 详细文档

- [使用说明](./设备在线状态-使用说明.md)
- [完整指南](./设备在线状态功能-完整指南.md)
- [快速参考](./快速参考卡.md)

---

**就这么简单！现在启动看效果吧！** 🎉
