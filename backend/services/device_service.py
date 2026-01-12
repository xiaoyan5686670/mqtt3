"""设备服务层"""
from typing import List, Optional
from sqlalchemy.orm import Session
from models.device import DeviceModel
from schemas.device import DeviceCreate, DeviceUpdate


def get_device(db: Session, device_id: int) -> Optional[DeviceModel]:
    """根据ID获取设备"""
    return db.query(DeviceModel).filter(DeviceModel.id == device_id).first()


def get_device_by_name(db: Session, name: str) -> Optional[DeviceModel]:
    """根据名称获取设备"""
    return db.query(DeviceModel).filter(DeviceModel.name == name).first()


def get_devices(db: Session, skip: int = 0, limit: int = 100) -> List[DeviceModel]:
    """获取设备列表"""
    return db.query(DeviceModel).offset(skip).limit(limit).all()


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