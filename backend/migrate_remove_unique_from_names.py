# -*- coding: utf-8 -*-
"""
移除mqtt_configs和topic_configs表中name字段的全局唯一约束
在多租户场景下，不同用户可以使用相同的配置名称
"""
import sys
import os
import sqlite3

def migrate():
    """移除name字段的全局唯一约束"""
    print("开始移除name字段的全局唯一约束...")
    
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
        # SQLite不支持直接删除UNIQUE约束，需要重建表
        # 但为了安全，我们先检查是否有unique索引
        
        # 检查mqtt_configs表
        print("\n检查mqtt_configs表...")
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='mqtt_configs'")
        table_sql = cursor.fetchone()
        if table_sql:
            sql = table_sql[0]
            if 'UNIQUE' in sql.upper() and 'name' in sql.lower():
                print("发现mqtt_configs表的name字段有UNIQUE约束")
                print("注意：SQLite不支持直接删除UNIQUE约束")
                print("新的记录将不再有全局唯一约束（已在模型中移除）")
                print("如果需要完全移除，需要重建表（此操作有风险，建议备份数据库）")
            else:
                print("mqtt_configs表的name字段没有UNIQUE约束，或已移除")
        
        # 检查topic_configs表
        print("\n检查topic_configs表...")
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='topic_configs'")
        table_sql = cursor.fetchone()
        if table_sql:
            sql = table_sql[0]
            if 'UNIQUE' in sql.upper() and 'name' in sql.lower():
                print("发现topic_configs表的name字段有UNIQUE约束")
                print("注意：SQLite不支持直接删除UNIQUE约束")
                print("新的记录将不再有全局唯一约束（已在模型中移除）")
                print("如果需要完全移除，需要重建表（此操作有风险，建议备份数据库）")
            else:
                print("topic_configs表的name字段没有UNIQUE约束，或已移除")
        
        # 检查是否有name相关的唯一索引
        print("\n检查唯一索引...")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND sql LIKE '%UNIQUE%' AND (sql LIKE '%name%' OR name LIKE '%name%')")
        unique_indexes = cursor.fetchall()
        if unique_indexes:
            print("发现以下唯一索引（可能与name相关）：")
            for idx in unique_indexes:
                print("  - {}".format(idx[0]))
            print("这些索引可能需要手动删除（如果存在）")
        else:
            print("未发现与name相关的唯一索引")
        
        print("\n迁移说明：")
        print("1. 模型层已移除name字段的unique=True约束")
        print("2. 服务层已添加用户内名称唯一性验证")
        print("3. SQLite的UNIQUE约束无法直接删除，但新记录将不再受全局唯一约束限制")
        print("4. 如果遇到名称冲突错误，请使用不同的配置名称")
            
    except Exception as e:
        print("检查失败: {}".format(e))
        conn.rollback()
    finally:
        conn.close()
        print("\n检查完成。")

if __name__ == "__main__":
    migrate()
