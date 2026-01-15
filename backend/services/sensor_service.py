"""传感器数据服务层"""
from typing import List, Optional
from datetime import datetime

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


def get_device_sensors_by_time_range(
    db: Session,
    device_id: int,
    sensor_type: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    limit: Optional[int] = None,
) -> List[SensorDataModel]:
    """
    根据时间范围获取设备的传感器数据（用于历史曲线）

    - 可按设备ID、传感器类型、时间范围、数量限制查询
    - 按时间倒序返回（最新在前）
    """
    query = db.query(SensorDataModel).filter(SensorDataModel.device_id == device_id)

    if sensor_type:
        query = query.filter(SensorDataModel.type == sensor_type)

    if start_time:
        query = query.filter(SensorDataModel.timestamp >= start_time)

    if end_time:
        query = query.filter(SensorDataModel.timestamp <= end_time)

    if limit:
        # 如果提供了限制，获取最新的N条记录（按时间倒序）
        query = query.order_by(SensorDataModel.timestamp.desc()).limit(limit)
        # 然后在内存中按时间正序排列，以供图表正确显示
        results = query.all()
        results.sort(key=lambda x: x.timestamp)
        return results

    # 如果没有限制，直接按时间正序返回
    query = query.order_by(SensorDataModel.timestamp.asc())
    return query.all()


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