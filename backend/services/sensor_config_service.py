"""传感器配置服务层"""
from typing import List, Optional
from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy import desc

from models.sensor_config import SensorConfigModel


def get_sensor_config(db: Session, config_id: int) -> Optional[SensorConfigModel]:
    """根据ID获取传感器配置"""
    return db.query(SensorConfigModel).filter(SensorConfigModel.id == config_id).first()


def get_device_sensor_configs(db: Session, device_id: int) -> List[SensorConfigModel]:
    """获取设备的所有传感器配置"""
    return db.query(SensorConfigModel).filter(
        SensorConfigModel.device_id == device_id
    ).all()


def get_sensor_config_by_device_and_type(
    db: Session, 
    device_id: int, 
    sensor_type: str
) -> Optional[SensorConfigModel]:
    """根据设备ID和传感器类型获取配置"""
    return db.query(SensorConfigModel).filter(
        SensorConfigModel.device_id == device_id,
        SensorConfigModel.type == sensor_type
    ).first()


def get_or_create_sensor_config(
    db: Session,
    device_id: int,
    sensor_type: str,
    unit: str = "",
    display_name: Optional[str] = None,
    min_value: Optional[float] = None,
    max_value: Optional[float] = None
) -> SensorConfigModel:
    """
    获取或创建传感器配置
    
    如果配置已存在，返回现有配置（不更新）
    如果配置不存在，创建新配置
    """
    # 尝试获取现有配置
    config = get_sensor_config_by_device_and_type(db, device_id, sensor_type)
    
    if config:
        # 配置已存在，直接返回（保持用户的自定义配置）
        return config
    
    # 配置不存在，创建新配置
    new_config = SensorConfigModel(
        device_id=device_id,
        type=sensor_type,
        display_name=display_name,
        unit=unit,
        min_value=min_value,
        max_value=max_value,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    db.add(new_config)
    db.flush()  # 刷新以获取ID，但不提交事务
    
    return new_config


def update_sensor_config_display_name(
    db: Session,
    device_id: int,
    sensor_type: str,
    display_name: Optional[str]
) -> Optional[SensorConfigModel]:
    """更新传感器配置的显示名称"""
    config = get_sensor_config_by_device_and_type(db, device_id, sensor_type)
    
    if not config:
        return None
    
    # 如果 display_name 为空字符串，设置为 None
    config.display_name = display_name if display_name and display_name.strip() else None
    config.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(config)
    
    return config


def delete_sensor_config(db: Session, config_id: int) -> bool:
    """删除传感器配置（会级联删除相关数据）"""
    config = get_sensor_config(db, config_id)
    
    if not config:
        return False
    
    db.delete(config)
    db.commit()
    
    return True
