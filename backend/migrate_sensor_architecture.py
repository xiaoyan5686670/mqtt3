#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
传感器架构重构迁移脚本

将传感器数据分离为两个表：
1. sensor_configs - 传感器配置表（元信息）
2. sensor_data - 传感器数据表（时序数据）

从旧的 sensors 表迁移数据
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text, inspect
from core.database import SessionLocal, engine
from datetime import datetime

def migrate():
    """执行数据库迁移"""
    db = SessionLocal()
    inspector = inspect(engine)
    
    try:
        print("=" * 60)
        print("开始传感器架构重构迁移...")
        print("=" * 60)
        
        # 1. 检查旧表是否存在
        if 'sensors' not in inspector.get_table_names():
            print("❌ 错误：sensors 表不存在，无法迁移")
            return False
        
        # 2. 创建 sensor_configs 表
        print("\n📊 步骤1: 创建 sensor_configs 表...")
        if 'sensor_configs' in inspector.get_table_names():
            print("⚠️  sensor_configs 表已存在，跳过创建")
        else:
            db.execute(text("""
                CREATE TABLE sensor_configs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    device_id INTEGER NOT NULL,
                    type VARCHAR NOT NULL,
                    display_name VARCHAR,
                    unit VARCHAR DEFAULT '',
                    min_value FLOAT,
                    max_value FLOAT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (device_id) REFERENCES devices(id),
                    UNIQUE(device_id, type)
                )
            """))
            db.execute(text("CREATE INDEX ix_sensor_configs_device_id ON sensor_configs(device_id)"))
            db.execute(text("CREATE INDEX ix_sensor_configs_type ON sensor_configs(type)"))
            db.commit()
            print("✅ sensor_configs 表创建成功")
        
        # 3. 从 sensors 表提取唯一的传感器配置
        print("\n📊 步骤2: 提取传感器配置信息...")
        result = db.execute(text("""
            SELECT DISTINCT 
                device_id,
                type,
                display_name,
                unit,
                min_value,
                max_value
            FROM sensors
            ORDER BY device_id, type
        """))
        
        unique_sensors = result.fetchall()
        print(f"   找到 {len(unique_sensors)} 个唯一的传感器配置")
        
        # 4. 插入到 sensor_configs 表
        print("\n📊 步骤3: 插入传感器配置...")
        inserted_count = 0
        for sensor in unique_sensors:
            device_id, sensor_type, display_name, unit, min_value, max_value = sensor
            
            # 检查是否已存在
            existing = db.execute(text("""
                SELECT id FROM sensor_configs 
                WHERE device_id = :device_id AND type = :type
            """), {"device_id": device_id, "type": sensor_type}).fetchone()
            
            if not existing:
                db.execute(text("""
                    INSERT INTO sensor_configs (device_id, type, display_name, unit, min_value, max_value)
                    VALUES (:device_id, :type, :display_name, :unit, :min_value, :max_value)
                """), {
                    "device_id": device_id,
                    "type": sensor_type,
                    "display_name": display_name,
                    "unit": unit or "",
                    "min_value": min_value,
                    "max_value": max_value
                })
                inserted_count += 1
        
        db.commit()
        print(f"✅ 成功插入 {inserted_count} 条传感器配置")
        
        # 5. 创建新的 sensor_data 表
        print("\n📊 步骤4: 创建 sensor_data 表...")
        if 'sensor_data' in inspector.get_table_names():
            print("⚠️  sensor_data 表已存在，跳过创建")
        else:
            db.execute(text("""
                CREATE TABLE sensor_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sensor_config_id INTEGER NOT NULL,
                    value FLOAT NOT NULL,
                    timestamp DATETIME NOT NULL,
                    alert_status VARCHAR,
                    FOREIGN KEY (sensor_config_id) REFERENCES sensor_configs(id) ON DELETE CASCADE
                )
            """))
            db.execute(text("CREATE INDEX ix_sensor_data_sensor_config_id ON sensor_data(sensor_config_id)"))
            db.execute(text("CREATE INDEX ix_sensor_data_timestamp ON sensor_data(timestamp)"))
            db.commit()
            print("✅ sensor_data 表创建成功")
        
        # 6. 迁移数据（可选 - 因为数据量可能很大）
        print("\n📊 步骤5: 数据迁移选项...")
        print("   选项1: 迁移所有历史数据（可能耗时较长）")
        print("   选项2: 只迁移最近的数据")
        print("   选项3: 跳过数据迁移，从新数据开始")
        
        # 这里我们迁移最近1000条数据作为示例
        print("\n   执行：迁移每个传感器的最新数据...")
        
        # 获取所有 sensor_config
        configs = db.execute(text("SELECT id, device_id, type FROM sensor_configs")).fetchall()
        migrated_count = 0
        
        for config in configs:
            config_id, device_id, sensor_type = config
            
            # 获取该传感器类型的最新100条数据
            old_data = db.execute(text("""
                SELECT value, timestamp, alert_status
                FROM sensors
                WHERE device_id = :device_id AND type = :type
                ORDER BY timestamp DESC
                LIMIT 100
            """), {"device_id": device_id, "type": sensor_type}).fetchall()
            
            # 插入到新表
            for data in old_data:
                value, timestamp, alert_status = data
                db.execute(text("""
                    INSERT INTO sensor_data (sensor_config_id, value, timestamp, alert_status)
                    VALUES (:config_id, :value, :timestamp, :alert_status)
                """), {
                    "config_id": config_id,
                    "value": value,
                    "timestamp": timestamp,
                    "alert_status": alert_status
                })
                migrated_count += 1
        
        db.commit()
        print(f"✅ 成功迁移 {migrated_count} 条数据记录")
        
        # 7. 备份说明
        print("\n📊 步骤6: 备份说明...")
        print("   ✅ 原 sensors 表已保留作为备份")
        print("   ⚠️  如需删除旧表，请执行: DROP TABLE sensors;")
        print("   💡 建议：验证新架构运行正常后再删除旧表")
        
        print("\n" + "=" * 60)
        print("✅ 迁移完成！")
        print("=" * 60)
        print("\n📋 下一步：")
        print("1. 重启后端服务")
        print("2. 测试传感器数据的读取和写入")
        print("3. 验证 display_name 功能正常")
        print("4. 确认无误后，可删除旧的 sensors 表")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 迁移失败: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


if __name__ == "__main__":
    success = migrate()
    sys.exit(0 if success else 1)
