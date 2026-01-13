"""传感器数据服务层"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from models.sensor import SensorDataModel
from schemas.sensor import SensorDataCreate, SensorDataUpdate


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


def update_sensor_display_name(db: Session, sensor_id: int, display_name: Optional[str]) -> Optional[SensorDataModel]:
    """更新传感器的显示名称"""
    sensor = db.query(SensorDataModel).filter(SensorDataModel.id == sensor_id).first()
    if not sensor:
        return None
    
    # 如果 display_name 为空字符串，设置为 None
    sensor.display_name = display_name if display_name and display_name.strip() else None
    db.commit()
    db.refresh(sensor)
    return sensor


def update_sensor_by_type_and_device(db: Session, device_id: int, sensor_type: str, display_name: Optional[str]) -> Optional[SensorDataModel]:
    """根据设备ID和传感器类型更新显示名称（更新该类型的所有传感器）"""
    sensors = db.query(SensorDataModel).filter(
        SensorDataModel.device_id == device_id,
        SensorDataModel.type == sensor_type
    ).all()
    
    if not sensors:
        return None
    
    # 更新所有匹配的传感器
    for sensor in sensors:
        sensor.display_name = display_name if display_name and display_name.strip() else None
    
    db.commit()
    if sensors:
        db.refresh(sensors[0])
        return sensors[0]
    return None