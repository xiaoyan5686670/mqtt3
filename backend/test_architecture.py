#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试新架构"""
import sys
sys.path.insert(0, '.')

from core.database import SessionLocal
from models import SensorDataModel, SensorConfigModel

db = SessionLocal()
print(f"配置数量: {db.query(SensorConfigModel).count()}")
print(f"数据数量: {db.query(SensorDataModel).count()}")

sample = db.query(SensorDataModel, SensorConfigModel).join(
    SensorConfigModel,
    SensorDataModel.sensor_config_id == SensorConfigModel.id
).first()

if sample:
    data, config = sample
    print(f"JOIN查询成功: {config.type} = {data.value}")

db.close()
print("✅ 测试通过")
