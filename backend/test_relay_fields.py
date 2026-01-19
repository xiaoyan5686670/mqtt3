#!/usr/bin/env python
"""测试relay字段是否存在"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text, inspect
from core.database import SessionLocal

def test_fields():
    db = SessionLocal()
    try:
        # 检查devices表
        print("=== 检查 devices 表 ===")
        result = db.execute(text("PRAGMA table_info(devices)"))
        columns = [(row[1], row[2]) for row in result.fetchall()]
        print(f"设备表共有 {len(columns)} 个字段:")
        for col_name, col_type in columns:
            print(f"  - {col_name}: {col_type}")
        
        relay_fields = [col for col in columns if 'relay' in col[0].lower()]
        if relay_fields:
            print(f"\n找到 {len(relay_fields)} 个relay相关字段:")
            for field in relay_fields:
                print(f"  ✓ {field[0]}: {field[1]}")
        else:
            print("\n❌ 未找到relay相关字段")
        
        # 检查topic_configs表
        print("\n=== 检查 topic_configs 表 ===")
        result = db.execute(text("PRAGMA table_info(topic_configs)"))
        columns = [(row[1], row[2]) for row in result.fetchall()]
        print(f"主题配置表共有 {len(columns)} 个字段:")
        for col_name, col_type in columns:
            print(f"  - {col_name}: {col_type}")
        
        relay_fields = [col for col in columns if 'relay' in col[0].lower()]
        if relay_fields:
            print(f"\n找到 {len(relay_fields)} 个relay相关字段:")
            for field in relay_fields:
                print(f"  ✓ {field[0]}: {field[1]}")
        else:
            print("\n❌ 未找到relay相关字段")
        
        # 测试查询设备
        print("\n=== 测试查询设备 ===")
        result = db.execute(text("SELECT id, name, relay_on_payload, relay_off_payload FROM devices LIMIT 5"))
        devices = result.fetchall()
        if devices:
            print(f"找到 {len(devices)} 个设备:")
            for device in devices:
                print(f"  设备 ID={device[0]}, name={device[1]}")
                print(f"    relay_on_payload: {device[2]}")
                print(f"    relay_off_payload: {device[3]}")
        else:
            print("没有找到设备")
            
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_fields()
