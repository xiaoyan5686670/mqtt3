# -*- coding: utf-8 -*-
"""
数据库迁移脚本：为 devices 表添加 show_on_dashboard 字段
执行方式: python3 migrate_add_show_on_dashboard.py
"""
import sqlite3
import os
from pathlib import Path
import re

# 使用和应用相同的配置逻辑来获取数据库路径
def get_database_path():
    """获取数据库文件路径，使用和应用相同的逻辑"""
    # 尝试从环境变量或配置文件读取
    database_url = os.getenv("DATABASE_URL", "sqlite:///./mqtt_iot.db")
    
    # 解析 SQLite URL: sqlite:///./mqtt_iot.db 或 sqlite:////absolute/path
    if database_url.startswith("sqlite:///"):
        # 移除 sqlite:/// 前缀
        path_part = database_url[10:]
        
        # 如果是绝对路径（以 / 开头）
        if path_part.startswith("/"):
            return Path(path_part)
        # 如果是相对路径（以 ./ 开头）
        elif path_part.startswith("./"):
            # 相对于当前工作目录
            return Path.cwd() / path_part[2:]
        else:
            # 直接是文件名，相对于当前工作目录
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
        # 检查 show_on_dashboard 列是否存在
        if not check_column_exists(cursor, "devices", "show_on_dashboard"):
            print("添加 show_on_dashboard 列...")
            # SQLite 使用 INTEGER 类型存储布尔值（0=false, 1=true）
            cursor.execute("ALTER TABLE devices ADD COLUMN show_on_dashboard INTEGER DEFAULT 1")
            # 为现有记录设置默认值（1表示true，在首页展示）
            cursor.execute("UPDATE devices SET show_on_dashboard = 1 WHERE show_on_dashboard IS NULL")
            print("✓ show_on_dashboard 列添加成功，已为现有记录设置默认值（在首页展示）")
        else:
            print("✓ show_on_dashboard 列已存在，跳过")
        
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
