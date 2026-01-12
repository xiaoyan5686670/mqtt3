"""传感器数据模型"""
from sqlalchemy import Column, Integer, String, Float, DateTime
from core.database import Base


class SensorDataModel(Base):
    """传感器数据模型"""
    __tablename__ = "sensors"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, nullable=False, index=True)
    type = Column(String, nullable=False)
    value = Column(Float, nullable=False)
    unit = Column(String, nullable=True)
    timestamp = Column(DateTime, nullable=False)
    min_value = Column(Float, nullable=True)
    max_value = Column(Float, nullable=True)
    alert_status = Column(String, nullable=True)