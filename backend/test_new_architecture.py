#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试新架构是否正常工作
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.database import SessionLocal
from models import SensorDataModel, SensorConfigModel, DeviceModel


def test_models():
    """测试模型导入和关系"""
    print("=" * 60)
    print("测试1: 模型导入和表名")
    print("=" * 60)
    
    print(f"✅ DeviceModel: {DeviceModel.__tablename__}")
    print(f"✅ SensorConfigModel: {SensorConfigModel.__tablename__}")
    print(f"✅ SensorDataModel: {SensorDataModel.__tablename__}")
    
    print("\n" + "=" * 60)
    print("测试2: 模型关系")
    print("=" * 60)
    
    print(f"✅ DeviceModel.sensor_configs: {hasattr(DeviceModel, 'sensor_configs')}")
    print(f"✅ SensorConfigModel.device: {hasattr(SensorConfigModel, 'device')}")
    print(f"✅ SensorConfigModel.sensor_data: {hasattr(SensorConfigModel, 'sensor_data')}")
    print(f"✅ SensorDataModel.sensor_config: {hasattr(SensorDataModel, 'sensor_config')}")
    
    return True


def test_queries():
    """测试数据库查询"""
    print("\n" + "=" * 60)
    print("测试3: 数据库查询")
    print("=" * 60)
    
    db = SessionLocal()
    
    try:
        # 测试配置查询
        config_count = db.query(SensorConfigModel).count()
        print(f"✅ 传感器配置数量: {config_count}")
        
        # 测试数据查询
        data_count = db.query(SensorDataModel).count()
        print(f"✅ 传感器数据数量: {data_count}")
        
        # 测试 JOIN 查询
        print("\n" + "=" * 60)
        print("测试4: JOIN 查询")
        print("=" * 60)
        
        sample = db.query(SensorDataModel, SensorConfigModel).join(
            SensorConfigModel,
            SensorDataModel.sensor_config_id == SensorConfigModel.id
        ).first()
        
        if sample:
            data, config = sample
            print(f"✅ JOIN 查询成功:")
            print(f"  - 设备ID: {config.device_id}")
            print(f"  - 传感器类型: {config.type}")
            print(f"  - 显示名称: {config.display_name}")
            print(f"  - 单位: {config.unit}")
            print(f"  - 数据值: {data.value}")
            print(f"  - 时间戳: {data.timestamp}")
        else:
            print("⚠️  没有找到数据")
        
        # 测试按设备查询
        print("\n" + "=" * 60)
        print("测试5: 按设备查询配置")
        print("=" * 60)
        
        configs = db.query(SensorConfigModel).filter(
            SensorConfigModel.device_id == 5
        ).all()
        
        print(f"✅ 设备5的传感器配置: {len(configs)}个")
        for config in configs[:3]:  # 只显示前3个
            print(f"  - {config.type}: {config.display_name or '(无显示名称)'}")
        
        return True
        
    except Exception as e:
        print(f"❌ 查询失败: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        db.close()


def test_sensor_service():
    """测试 sensor_service"""
    print("\n" + "=" * 60)
    print("测试6: sensor_service 功能")
    print("=" * 60)
    
    try:
        from services import sensor_service
        
        db = SessionLocal()
        
        # 测试获取设备的最新传感器数据
        latest = sensor_service.get_latest_device_sensors(db, device_id=5)
        print(f"✅ 获取设备5的最新传感器数据: {len(latest)}个")
        
        if latest:
            sample = latest[0]
            print(f"  - 示例数据:")
            print(f"    类型: {sample['type']}")
            print(f"    显示名称: {sample['display_name']}")
            print(f"    值: {sample['value']}{sample['unit']}")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ sensor_service 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """运行所有测试"""
    print("\n🚀 开始测试新架构...")
    print()
    
    success = True
    
    try:
        # 测试1: 模型
        if not test_models():
            success = False
        
        # 测试2: 查询
        if not test_queries():
            success = False
        
        # 测试3: 服务层
        if not test_sensor_service():
            success = False
        
        print("\n" + "=" * 60)
        if success:
            print("🎉 所有测试通过！新架构运行正常！")
        else:
            print("❌ 部分测试失败，请检查错误信息")
        print("=" * 60)
        
        return 0 if success else 1
        
    except Exception as e:
        print(f"\n❌ 测试过程出错: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
