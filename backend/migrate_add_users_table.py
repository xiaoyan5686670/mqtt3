# -*- coding: utf-8 -*-
"""
数据库迁移脚本：创建 users 表
执行方式: python3 migrate_add_users_table.py
"""
import sqlite3
import sys
from pathlib import Path


def get_database_path():
    """获取数据库文件路径（项目根目录）"""
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    db_path = project_root / 'mqtt_iot.db'
    return str(db_path)


def table_exists(cursor, table_name):
    """检查表是否存在"""
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
    return cursor.fetchone() is not None


def main():
    """执行迁移"""
    db_path = get_database_path()
    print(f"数据库路径: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        table_name = 'users'
        
        # 检查表是否已存在
        if table_exists(cursor, table_name):
            print(f"表 '{table_name}' 已存在，跳过迁移")
            conn.close()
            return
        
        # 创建 users 表
        print(f"正在创建表 '{table_name}'...")
        cursor.execute("""
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username VARCHAR NOT NULL UNIQUE,
                email VARCHAR UNIQUE,
                hashed_password VARCHAR NOT NULL,
                is_active INTEGER NOT NULL DEFAULT 1,
                is_admin INTEGER NOT NULL DEFAULT 0,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 创建索引
        cursor.execute("CREATE INDEX ix_users_username ON users(username)")
        cursor.execute("CREATE INDEX ix_users_email ON users(email)")
        
        # 提交更改
        conn.commit()
        print(f"成功创建表 '{table_name}'")
        
        # 注意：默认管理员用户需要通过API创建
        # 可以使用以下命令创建：
        # curl -X POST "http://localhost:8000/api/v1/auth/register" \
        #   -H "Content-Type: application/json" \
        #   -d '{"username":"admin","password":"admin123","is_admin":true}'
        print("提示: 请通过API创建管理员用户")
        
        # 验证
        if table_exists(cursor, table_name):
            print("验证成功: 表已存在")
        else:
            print("警告: 验证失败，表可能未正确创建")
        
        conn.close()
        
    except sqlite3.Error as e:
        print(f"数据库错误: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"错误: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
