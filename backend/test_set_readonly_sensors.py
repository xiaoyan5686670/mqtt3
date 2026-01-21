#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
import json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text
from core.database import SessionLocal

def set_readonly_sensors():
    """测试：为第一个主题配置设置只读传感器类型"""
    db = SessionLocal()
    try:
        # 获取第一个主题配置
        result = db.execute(text("SELECT id, name FROM topic_configs LIMIT 1"))
        config = result.fetchone()
        
        if not config:
            print("No topic configs found!")
            return
        
        config_id = config[0]
        config_name = config[1]
        
        print(f"Setting readonly sensors for config: {config_name} (ID: {config_id})")
        
        # 设置只读传感器类型
        readonly_types = ["relay_in_status", "realy_in_status"]
        readonly_json = json.dumps(readonly_types)
        
        print(f"Readonly sensors JSON: {readonly_json}")
        
        # 更新配置
        db.execute(
            text("UPDATE topic_configs SET readonly_sensor_types = :readonly WHERE id = :id"),
            {"readonly": readonly_json, "id": config_id}
        )
        db.commit()
        
        print("✓ Updated successfully!")
        
        # 验证更新
        result = db.execute(
            text("SELECT id, name, readonly_sensor_types FROM topic_configs WHERE id = :id"),
            {"id": config_id}
        )
        row = result.fetchone()
        print(f"\nVerification:")
        print(f"  ID: {row[0]}")
        print(f"  Name: {row[1]}")
        print(f"  Readonly: {row[2]}")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    set_readonly_sensors()
