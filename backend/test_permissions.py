import sys
import os
import unittest
from fastapi.testclient import TestClient

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.database import SessionLocal, engine, Base
from models.user import UserModel
from models.device import DeviceModel
from core.config import settings
from main import app

class TestPermissions(unittest.TestCase):
    def setUp(self):
        # 能够直接操作数据库以创建测试用户
        self.db = SessionLocal()
        self.client = TestClient(app)
        
        # 清理测试数据 (如果存在)
        self.cleanup()
        
        # 创建 Admin 用户
        self.admin = UserModel(username="test_admin", hashed_password="hashed_password", is_admin=True, is_active=True)
        self.db.add(self.admin)
        
        # 创建 Regular 用户
        self.user = UserModel(username="test_user", hashed_password="hashed_password", is_admin=False, is_active=True)
        self.db.add(self.user)
        
        self.db.commit()
        self.db.refresh(self.admin)
        self.db.refresh(self.user)
        
        # 模拟登录获取 Token
        from api.auth import create_access_token
        
        self.admin_token = create_access_token(data={"sub": self.admin.username})
        self.user_token = create_access_token(data={"sub": self.user.username})
        
        self.admin_headers = {"Authorization": f"Bearer {self.admin_token}"}
        self.user_headers = {"Authorization": f"Bearer {self.user_token}"}
        
        self.api_prefix = settings.api_prefix

    def tearDown(self):
        self.cleanup()
        self.db.close()
        
    def cleanup(self):
        # 删除测试创建的用户和设备
        self.db.query(DeviceModel).filter(DeviceModel.name.in_(["user_device", "admin_device"])).delete(synchronize_session=False)
        self.db.query(UserModel).filter(UserModel.username.in_(["test_admin", "test_user"])).delete(synchronize_session=False)
        self.db.commit()

    def test_create_device_ownership(self):
        # 普通用户创建设备
        response = self.client.post(
            f"{self.api_prefix}/devices",
            headers=self.user_headers,
            json={"name": "user_device", "device_type": "test", "status": "online"}
        )
        self.assertEqual(response.status_code, 201)
        device_data = response.json()
        self.assertEqual(device_data.get("user_id"), self.user.id)
        self.user_device_id = device_data["id"]

        # 管理员创建设备
        response = self.client.post(
            f"{self.api_prefix}/devices",
            headers=self.admin_headers,
            json={"name": "admin_device", "device_type": "test", "status": "online"}
        )
        self.assertEqual(response.status_code, 201)
        device_data = response.json()
        self.assertEqual(device_data.get("user_id"), self.admin.id)
        self.admin_device_id = device_data["id"]

    def test_get_devices_isolation(self):
        # 先创建设备
        self.test_create_device_ownership()
        
        # 普通用户获取列表 -> 应该只看到 1 个 (自己的)
        response = self.client.get(f"{self.api_prefix}/devices", headers=self.user_headers)
        self.assertEqual(response.status_code, 200)
        devices = response.json()
        
        # 过滤出测试设备（防止干扰）
        my_devices = [d for d in devices if d["id"] == self.user_device_id]
        self.assertEqual(len(my_devices), 1)
        self.assertEqual(my_devices[0]["id"], self.user_device_id) 
        
        # 确保看不到 id 为 admin_device_id 的
        admin_devices_seen = [d for d in devices if d["id"] == self.admin_device_id]
        self.assertEqual(len(admin_devices_seen), 0)

        # 管理员获取列表 -> 应该看到所有
        response = self.client.get(f"{self.api_prefix}/devices", headers=self.admin_headers)
        self.assertEqual(response.status_code, 200)
        devices = response.json()
        found_ids = [d["id"] for d in devices]
        self.assertIn(self.user_device_id, found_ids)
        self.assertIn(self.admin_device_id, found_ids)

    def test_access_control(self):
        # 先创建设备
        self.test_create_device_ownership()
        
        # 普通用户尝试访问管理员的设备 -> 403
        response = self.client.get(f"{self.api_prefix}/devices/{self.admin_device_id}", headers=self.user_headers)
        self.assertEqual(response.status_code, 403)
        
        # 普通用户尝试修改管理员的设备 -> 403
        response = self.client.put(
            f"{self.api_prefix}/devices/{self.admin_device_id}", 
            headers=self.user_headers,
            json={"status": "offline"}
        )
        self.assertEqual(response.status_code, 403)

        # 管理员尝试访问普通用户的设备 -> 200
        response = self.client.get(f"{self.api_prefix}/devices/{self.user_device_id}", headers=self.admin_headers)
        self.assertEqual(response.status_code, 200)

if __name__ == "__main__":
    unittest.main()
