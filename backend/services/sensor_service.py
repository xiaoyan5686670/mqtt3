"""传感器数据服务层"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from models.sensor import SensorDataModel
from schemas.sensor import SensorDataCreate


def get_sensor_data(db: Session, sensor_id: int) -> Optional[SensorDataModel]:
    """根据ID获取传感器数据"""
    return db.query(SensorDataModel).filter(SensorDataModel.id == sensor_id).first()


def get_device_sensors(db: Session, device_id: int) -> List[SensorDataModel]:
    """获取设备的所有传感器数据"""
    return db.query(SensorDataModel).filter(SensorDataModel.device_id == device_id).all()


def get_latest_device_sensors(db: Session, device_id: int) -> List[SensorDataModel]:
    """获取设备的最新传感器数据（按类型分组）"""
    all_sensors = db.query(SensorDataModel).filter(
        SensorDataModel.device_id == device_id
    ).order_by(desc(SensorDataModel.timestamp)).all()
    
    # 按传感器类型分组，只保留每种类型最新的数据
    latest_sensors = {}
    for sensor in all_sensors:
        if sensor.type not in latest_sensors:
            latest_sensors[sensor.type] = sensor
    
    return list(latest_sensors.values())


def get_latest_sensors(db: Session, limit: int = 50) -> List[SensorDataModel]:
    """获取最新的传感器数据"""
    return db.query(SensorDataModel).order_by(desc(SensorDataModel.timestamp)).limit(limit).all()


def create_sensor_data(db: Session, sensor_data: SensorDataCreate) -> SensorDataModel:
    """创建传感器数据"""
    db_sensor = SensorDataModel(**sensor_data.model_dump())
    db.add(db_sensor)
    db.commit()
    db.refresh(db_sensor)
    return db_sensor