"""传感器数据模型 - 只存储时序数据"""
from sqlalchemy import Column, Integer, Float, DateTime, String, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from core.database import Base


class SensorDataModel(Base):
    """传感器数据模型 - 时序数据"""
    __tablename__ = "sensor_data"

    id = Column(Integer, primary_key=True, index=True)
    sensor_config_id = Column(Integer, ForeignKey("sensor_configs.id"), nullable=False, index=True)
    value = Column(Float, nullable=False)
    timestamp = Column(DateTime, nullable=False, index=True, default=datetime.utcnow)
    alert_status = Column(String, nullable=True)  # 告警状态: normal, warning, alert

    # 关系
    sensor_config = relationship("SensorConfigModel", back_populates="sensor_data")

    def __repr__(self):
        return f"<SensorData(id={self.id}, sensor_config_id={self.sensor_config_id}, value={self.value}, timestamp={self.timestamp})>"
