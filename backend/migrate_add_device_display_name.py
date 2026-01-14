# -*- coding: utf-8 -*-
"""
数据库迁移脚本：为 devices 表添加 display_name 字段
用于存储设备的自定义显示名称
执行方式: python3 migrate_add_device_display_name.py
"""
import sqlite3
import os
from pathlib import Path

# 使用和应用相同的配置逻辑来获取数据库路径
def get_database_path():
    """获取数据库文件路径，使用和应用相同的逻辑"""
    # 尝试从环境变量或配置文件读取
    database_url = os.getenv("DATABASE_URL", "sqlite:///../mqtt_iot.db")
    
    # 解析 SQLite URL: sqlite:///./mqtt_iot.db 或 sqlite:////absolute/path
    if database_url.startswith("sqlite:///"):
        # 移除 sqlite:/// 前缀
        path_part = database_url[10:]
        
        # 如果是绝对路径（以 / 开头）
        if path_part.startswith("/"):
            return Path(path_part)
        # 如果是相对路径（以 ./ 或 ../ 开头）
        elif path_part.startswith("./"):
            # 相对于当前工作目录
            return Path.cwd() / path_part[2:]
        elif path_part.startswith("../"):
            # 相对于当前工作目录的父目录（项目根目录）
            return Path.cwd().parent / path_part[3:]
        else:
            # 直接是文件名，先尝试项目根目录
            script_dir = Path(__file__).parent
            project_root = script_dir.parent
            root_db = project_root / path_part
            if root_db.exists():
                return root_db
            # 如果项目根目录不存在，则使用当前工作目录
            return Path.cwd() / path_part
    else:
        # 如果不是 SQLite URL，直接作为路径处理
        return Path(database_url)

db_path = get_database_path()

def check_column_exists(cursor, table_name, column_name):
    """检查列是否存在"""
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [row[1] for row in cursor.fetchall()]
    return column_name in columns

def table_exists(cursor, table_name):
    """检查表是否存在"""
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
    return cursor.fetchone() is not None

def migrate():
    """执行数据库迁移"""
    if not db_path.exists():
        print(f"数据库文件不存在: {db_path}")
        print("将在首次启动应用时自动创建数据库表")
        return
    
    print(f"开始迁移数据库: {db_path}")
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    try:
        # 检查 devices 表是否存在
        if not table_exists(cursor, "devices"):
            print("❌ devices 表不存在，请先创建设备表")
            return
        
        # 检查 display_name 列是否存在
        if not check_column_exists(cursor, "devices", "display_name"):
            print("添加 display_name 列...")
            # SQLite 使用 VARCHAR 类型存储字符串
            cursor.execute("ALTER TABLE devices ADD COLUMN display_name VARCHAR(100) NULL")
            print("✓ display_name 列添加成功")
        else:
            print("✓ display_name 列已存在，跳过")
        
        conn.commit()
        print("\n数据库迁移完成！")
        
        # 显示表结构
        print("\n当前 devices 表结构:")
        cursor.execute("PRAGMA table_info(devices)")
        for row in cursor.fetchall():
            print(f"  - {row[1]} ({row[2]})")
            
    except Exception as e:
        conn.rollback()
        print(f"\n❌ 迁移失败: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
