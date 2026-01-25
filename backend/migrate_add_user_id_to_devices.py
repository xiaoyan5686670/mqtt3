import sys
import os
import sqlite3

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.config import settings
SQLALCHEMY_DATABASE_URL = settings.database_url

def migrate():
    """添加 user_id 字段到 devices 表"""
    print("开始迁移...")
    
    # 从 URL 中提取数据库文件路径
    # sqlite:///./mqtt_iot.db -> ./mqtt_iot.db
    if SQLALCHEMY_DATABASE_URL.startswith("sqlite:///"):
        db_path = SQLALCHEMY_DATABASE_URL.replace("sqlite:///", "")
        
        # 处理相对路径
        if db_path.startswith("./"):
            base_dir = os.path.dirname(os.path.abspath(__file__))
            db_path = os.path.join(base_dir, db_path[2:])
    else:
        print(f"不支持的数据库 URL: {SQLALCHEMY_DATABASE_URL}")
        return

    print(f"数据库路径: {db_path}")
    
    if not os.path.exists(db_path):
        print("数据库文件不存在！")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 检查 user_id 列是否存在
        print("正在检查 user_id 列...")
        cursor.execute("PRAGMA table_info(devices)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        if "user_id" in column_names:
            print("user_id 列已存在，跳过迁移。")
        else:
            print("正在添加 user_id 列...")
            # SQLite 不支持在 ADD COLUMN 时添加外键约束，所以我们只添加列
            # SQLAlchemy 的模型定义会处理应用层的外键逻辑
            cursor.execute("ALTER TABLE devices ADD COLUMN user_id INTEGER")
            conn.commit()
            print("user_id 列添加成功！")
            
    except Exception as e:
        print(f"迁移失败: {e}")
        conn.rollback()
    finally:
        conn.close()
        print("迁移完成。")

if __name__ == "__main__":
    migrate()
