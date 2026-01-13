# -*- coding: utf-8 -*-
"""
创建默认管理员用户脚本
执行方式: python3 create_admin_user.py
"""
import sys
from pathlib import Path

# 添加backend目录到路径
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy.orm import Session
from core.database import SessionLocal
from services import user_service

def create_admin_user():
    """创建默认管理员用户"""
    db: Session = SessionLocal()
    try:
        # 检查是否已存在admin用户
        admin_user = user_service.get_user_by_username(db, "admin")
        if admin_user:
            print("管理员用户 'admin' 已存在")
            return
        
        # 创建管理员用户
        from schemas.user import UserCreate
        admin = UserCreate(
            username="admin",
            password="admin123",
            email=None,
            is_active=True,
            is_admin=True
        )
        
        user = user_service.create_user(db, admin)
        print(f"成功创建管理员用户:")
        print(f"  用户名: {user.username}")
        print(f"  密码: admin123")
        print(f"  角色: 管理员")
        print("\n⚠️  请在生产环境中立即修改默认密码！")
        
    except Exception as e:
        print(f"创建管理员用户失败: {e}")
        sys.exit(1)
    finally:
        db.close()

if __name__ == '__main__':
    create_admin_user()
