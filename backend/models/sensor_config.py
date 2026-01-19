"""传感器配置模型 - 存储传感器的元信息和配置"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from core.database import Base


class SensorConfigModel(Base):
    """传感器配置数据模型 - 每个设备的每种传感器类型一条记录"""
    __tablename__ = "sensor_configs"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False, index=True)
    type = Column(String, nullable=False, index=True)  # 传感器类型
    display_name = Column(String, nullable=True)  # 自定义显示名称
    unit = Column(String, nullable=False, default="")  # 单位
    min_value = Column(Float, nullable=True)  # 最小值
    max_value = Column(Float, nullable=True)  # 最大值
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    device = relationship("DeviceModel", back_populates="sensor_configs")
    sensor_data = relationship("SensorDataModel", back_populates="sensor_config", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<SensorConfig(id={self.id}, device_id={self.device_id}, type={self.type}, display_name={self.display_name})>"
