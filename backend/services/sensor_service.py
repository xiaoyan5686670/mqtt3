"""传感器数据服务层 - 使用新架构（配置和数据分离）"""
from typing import List, Optional
from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy import desc

from models.sensor_data_new import SensorDataModel
from models.sensor_config import SensorConfigModel
from schemas.sensor import SensorDataCreate, SensorDataUpdate


def get_sensor_data(db: Session, sensor_id: int) -> Optional[dict]:
    """根据ID获取传感器数据（返回完整信息）"""
    data = db.query(SensorDataModel).filter(SensorDataModel.id == sensor_id).first()
    if not data:
        return None
    
    # 获取配置信息
    config = db.query(SensorConfigModel).filter(
        SensorConfigModel.id == data.sensor_config_id
    ).first()
    
    # 合并配置和数据
    return _merge_config_and_data(config, data)


def get_device_sensors(db: Session, device_id: int) -> List[dict]:
    """获取设备的所有传感器数据（返回完整信息）"""
    # JOIN 查询获取配置和数据
    results = db.query(SensorDataModel, SensorConfigModel).join(
        SensorConfigModel,
        SensorDataModel.sensor_config_id == SensorConfigModel.id
    ).filter(
        SensorConfigModel.device_id == device_id
    ).all()
    
    return [_merge_config_and_data(config, data) for data, config in results]


def get_latest_device_sensors(db: Session, device_id: int) -> List[dict]:
    """获取设备的最新传感器数据（按类型分组，返回完整信息）"""
    # 先获取该设备的所有传感器配置
    configs = db.query(SensorConfigModel).filter(
        SensorConfigModel.device_id == device_id
    ).all()
    
    # 使用字典来去重，确保每个传感器类型只保留一个配置（最新更新的）
    config_map = {}
    for config in configs:
        if config.type not in config_map:
            config_map[config.type] = config
        else:
            # 如果已存在该类型，保留 updated_at 更新的那个
            if config.updated_at > config_map[config.type].updated_at:
                config_map[config.type] = config
    
    result = []
    for config in config_map.values():
        # 获取该配置的最新数据
        latest_data = db.query(SensorDataModel).filter(
            SensorDataModel.sensor_config_id == config.id
        ).order_by(desc(SensorDataModel.timestamp)).first()
        
        if latest_data:
            result.append(_merge_config_and_data(config, latest_data))
    
    return result


def get_latest_sensors(db: Session, limit: int = 50) -> List[dict]:
    """获取最新的传感器数据（返回完整信息）"""
    # JOIN 查询获取最新数据及其配置
    results = db.query(SensorDataModel, SensorConfigModel).join(
        SensorConfigModel,
        SensorDataModel.sensor_config_id == SensorConfigModel.id
    ).order_by(desc(SensorDataModel.timestamp)).limit(limit).all()
    
    return [_merge_config_and_data(config, data) for data, config in results]


def get_device_sensors_by_time_range(
    db: Session,
    device_id: int,
    sensor_type: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    limit: Optional[int] = None,
) -> List[dict]:
    """
    根据时间范围获取设备的传感器数据（用于历史曲线，返回完整信息）
    
    - 可按设备ID、传感器类型、时间范围、数量限制查询
    - 按时间倒序返回（最新在前）
    """
    # 构建查询
    query = db.query(SensorDataModel, SensorConfigModel).join(
        SensorConfigModel,
        SensorDataModel.sensor_config_id == SensorConfigModel.id
    ).filter(
        SensorConfigModel.device_id == device_id
    )
    
    if sensor_type:
        query = query.filter(SensorConfigModel.type == sensor_type)
    
    if start_time:
        query = query.filter(SensorDataModel.timestamp >= start_time)
    
    if end_time:
        query = query.filter(SensorDataModel.timestamp <= end_time)
    
    if limit:
        # 如果提供了限制，获取最新的N条记录（按时间倒序）
        query = query.order_by(SensorDataModel.timestamp.desc()).limit(limit)
        results = query.all()
        # 然后在内存中按时间正序排列，以供图表正确显示
        merged = [_merge_config_and_data(config, data) for data, config in results]
        merged.sort(key=lambda x: x['timestamp'])
        return merged
    
    # 如果没有限制，直接按时间正序返回
    query = query.order_by(SensorDataModel.timestamp.asc())
    results = query.all()
    return [_merge_config_and_data(config, data) for data, config in results]


def create_sensor_data(db: Session, sensor_data: SensorDataCreate) -> dict:
    """
    创建传感器数据（使用新架构）
    
    注意：此方法仅用于手动创建数据，正常情况下应该通过 mqtt_service 保存数据
    """
    from services import sensor_config_service
    
    # 获取或创建配置
    config = sensor_config_service.get_or_create_sensor_config(
        db=db,
        device_id=sensor_data.device_id,
        sensor_type=sensor_data.type,
        unit=sensor_data.unit
    )
    
    # 创建数据记录
    db_sensor = SensorDataModel(
        sensor_config_id=config.id,
        value=sensor_data.value,
        timestamp=datetime.utcnow()
    )
    db.add(db_sensor)
    db.commit()
    db.refresh(db_sensor)
    
    return _merge_config_and_data(config, db_sensor)


def update_sensor_display_name(db: Session, sensor_id: int, display_name: Optional[str]) -> Optional[dict]:
    """
    更新传感器的显示名称（更新配置表）
    
    注意：这会更新配置，影响该设备该类型的所有数据显示
    """
    # 获取数据记录
    data = db.query(SensorDataModel).filter(SensorDataModel.id == sensor_id).first()
    if not data:
        return None
    
    # 获取配置
    config = db.query(SensorConfigModel).filter(
        SensorConfigModel.id == data.sensor_config_id
    ).first()
    
    if not config:
        return None
    
    # 更新配置的 display_name
    config.display_name = display_name if display_name and display_name.strip() else None
    config.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(config)
    
    return _merge_config_and_data(config, data)


def update_sensor_by_type_and_device(
    db: Session, 
    device_id: int, 
    sensor_type: str, 
    display_name: Optional[str]
) -> Optional[dict]:
    """根据设备ID和传感器类型更新显示名称（更新配置表）"""
    from services import sensor_config_service
    
    config = sensor_config_service.update_sensor_config_display_name(
        db, device_id, sensor_type, display_name
    )
    
    if not config:
        return None
    
    # 获取该配置的最新数据
    latest_data = db.query(SensorDataModel).filter(
        SensorDataModel.sensor_config_id == config.id
    ).order_by(desc(SensorDataModel.timestamp)).first()
    
    if latest_data:
        return _merge_config_and_data(config, latest_data)
    
    # 如果没有数据，返回配置信息
    return {
        'id': config.id,
        'device_id': config.device_id,
        'type': config.type,
        'display_name': config.display_name,
        'unit': config.unit,
        'min_value': config.min_value,
        'max_value': config.max_value,
        'value': 0.0,
        'timestamp': config.updated_at,
        'alert_status': 'normal'
    }


def _merge_config_and_data(config: SensorConfigModel, data: SensorDataModel) -> dict:
    """合并配置和数据信息，返回兼容前端的格式"""
    return {
        'id': data.id,
        'device_id': config.device_id,
        'type': config.type,
        'display_name': config.display_name,
        'unit': config.unit,
        'min_value': config.min_value,
        'max_value': config.max_value,
        'value': data.value,
        'timestamp': data.timestamp,
        'alert_status': data.alert_status
    }
