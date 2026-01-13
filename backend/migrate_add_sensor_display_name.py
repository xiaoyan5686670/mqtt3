# -*- coding: utf-8 -*-
"""
数据库迁移脚本：为 sensors 表添加 display_name 字段
用于存储传感器的自定义显示名称
"""
import sqlite3
import sys
from pathlib import Path


def get_database_path():
    """获取数据库文件路径（项目根目录）"""
    # 获取脚本所在目录
    script_dir = Path(__file__).parent
    # 项目根目录（backend 的父目录）
    project_root = script_dir.parent
    
    # 数据库文件路径
    db_path = project_root / 'mqtt_iot.db'
    
    return str(db_path)


def column_exists(cursor, table_name, column_name):
    """检查列是否存在"""
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    for col in columns:
        if col[1] == column_name:
            return True
    return False


def main():
    """执行迁移"""
    db_path = get_database_path()
    print(f"数据库路径: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        table_name = 'sensors'
        column_name = 'display_name'
        
        # 检查表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
        if not cursor.fetchone():
            print(f"错误: 表 '{table_name}' 不存在")
            sys.exit(1)
        
        # 检查列是否已存在
        if column_exists(cursor, table_name, column_name):
            print(f"列 '{column_name}' 已存在于表 '{table_name}' 中，跳过迁移")
            conn.close()
            return
        
        # 添加 display_name 列
        print(f"正在为表 '{table_name}' 添加列 '{column_name}'...")
        cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} VARCHAR(100) NULL")
        
        # 提交更改
        conn.commit()
        print(f"成功添加列 '{column_name}' 到表 '{table_name}'")
        
        # 验证
        if column_exists(cursor, table_name, column_name):
            print("验证成功: 列已存在")
        else:
            print("警告: 验证失败，列可能未正确添加")
        
        conn.close()
        
    except sqlite3.Error as e:
        print(f"数据库错误: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"错误: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
