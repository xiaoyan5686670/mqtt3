# -*- coding: utf-8 -*-
import sys
import os
import sqlite3

def migrate():
    """添加 user_id 字段到 topic_configs 表"""
    print("开始迁移 topic_configs 表...")
    
    # 获取项目根目录（backend的父目录）
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(backend_dir)
    
    # 数据库文件通常在项目根目录
    db_path = os.path.join(project_root, "mqtt_iot.db")
    
    # 如果环境变量中有设置，优先使用
    if "DATABASE_URL" in os.environ:
        db_url = os.environ["DATABASE_URL"]
        if db_url.startswith("sqlite:///"):
            db_path = db_url.replace("sqlite:///", "")
            if not os.path.isabs(db_path):
                if db_path.startswith("./"):
                    db_path = os.path.join(project_root, db_path[2:])
                else:
                    db_path = os.path.join(project_root, db_path)

    print("数据库路径: {}".format(db_path))
    
    if not os.path.exists(db_path):
        print("数据库文件不存在！")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 检查 user_id 列是否存在
        print("正在检查 user_id 列...")
        cursor.execute("PRAGMA table_info(topic_configs)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        if "user_id" in column_names:
            print("user_id 列已存在，跳过迁移。")
        else:
            print("正在添加 user_id 列...")
            # SQLite 不支持在 ADD COLUMN 时添加外键约束，所以我们只添加列
            # SQLAlchemy 的模型定义会处理应用层的外键逻辑
            cursor.execute("ALTER TABLE topic_configs ADD COLUMN user_id INTEGER")
            conn.commit()
            print("user_id 列添加成功！")
            
            # 创建索引以提高查询性能
            print("正在创建索引...")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_topic_configs_user_id ON topic_configs(user_id)")
            conn.commit()
            print("索引创建成功！")
            
    except Exception as e:
        print("迁移失败: {}".format(e))
        conn.rollback()
    finally:
        conn.close()
        print("迁移完成。")

if __name__ == "__main__":
    migrate()
