"""MQTT配置模型"""
from sqlalchemy import Column, Integer, String, Boolean
from core.database import Base


class MQTTConfigModel(Base):
    """MQTT配置数据模型"""
    __tablename__ = "mqtt_configs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    server = Column(String, nullable=False)
    port = Column(Integer, nullable=False, default=1883)
    username = Column(String, nullable=True)
    password = Column(String, nullable=True)
    is_active = Column(Boolean, default=False, nullable=False)