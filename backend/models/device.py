"""设备模型"""
from sqlalchemy import Column, Integer, String
from core.database import Base


class DeviceModel(Base):
    """设备数据模型"""
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    device_type = Column(String, nullable=False)
    status = Column(String, default="offline", nullable=False)
    location = Column(String, nullable=True)
    mqtt_config_id = Column(Integer, nullable=True)
    topic_config_id = Column(Integer, nullable=True)