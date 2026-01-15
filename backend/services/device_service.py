"""设备服务层"""
from typing import List, Optional
from sqlalchemy.orm import Session
from models.device import DeviceModel
from schemas.device import DeviceCreate, DeviceUpdate


def get_device(db: Session, device_id: int) -> Optional[DeviceModel]:
    """根据ID获取设备"""
    device = db.query(DeviceModel).filter(DeviceModel.id == device_id).first()
    if device:
        device.publish_topic = get_device_publish_topic(db, device)
    return device


def get_device_by_name(db: Session, name: str) -> Optional[DeviceModel]:
    """根据名称获取设备"""
    return db.query(DeviceModel).filter(DeviceModel.name == name).first()


def get_devices(db: Session, skip: int = 0, limit: int = 100) -> List[DeviceModel]:
    """获取设备列表"""
    devices = db.query(DeviceModel).offset(skip).limit(limit).all()
    # 为每个设备填充 publish_topic
    for device in devices:
        device.publish_topic = get_device_publish_topic(db, device)
    return devices


def get_device_publish_topic(db: Session, device: DeviceModel) -> str:
    """获取设备的发布主题"""
    import re
    from services import topic_config_service
    
    # 1. 如果设备明确关联了 TopicConfig
    if device.topic_config_id:
        topic_config = topic_config_service.get_topic_config(db, device.topic_config_id)
        if topic_config and topic_config.publish_topic:
            return topic_config.publish_topic
            
    # 2. 尝试根据设备名自动匹配 TopicConfig
    if device.name:
        matched_config = topic_config_service.find_topic_config_by_device_name(db, device.name)
        if matched_config and matched_config.publish_topic:
            return matched_config.publish_topic
            
    # 3. 尝试从设备名称提取主题
    if device.name:
        name = device.name.strip().lower()
        if "/" in name and name.startswith("pc/"):
            return name
        
        m = re.match(r"^pc[_-](.+)$", name)
        if m:
            return f"pc/{m.group(1)}"
            
    # 4. 默认兜底
    return f"pc/{device.id}"


def create_device(db: Session, device: DeviceCreate) -> DeviceModel:
    """创建设备"""
    db_device = DeviceModel(**device.model_dump())
    db.add(db_device)
    db.commit()
    db.refresh(db_device)
    return db_device


def update_device(db: Session, device_id: int, device_update: DeviceUpdate) -> Optional[DeviceModel]:
    """更新设备"""
    db_device = db.query(DeviceModel).filter(DeviceModel.id == device_id).first()
    if not db_device:
        return None
    
    update_data = device_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_device, key, value)
    
    db.commit()
    db.refresh(db_device)
    return db_device


def delete_device(db: Session, device_id: int) -> bool:
    """删除设备"""
    db_device = db.query(DeviceModel).filter(DeviceModel.id == device_id).first()
    if not db_device:
        return False
    
    db.delete(db_device)
    db.commit()
    return True