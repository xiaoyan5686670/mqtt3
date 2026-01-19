"""数据模型模块"""
from .device import DeviceModel
from .sensor_config import SensorConfigModel  # 传感器配置模型
from .sensor_data_new import SensorDataModel  # 传感器数据模型（新架构）
from .mqtt_config import MQTTConfigModel
from .topic_config import TopicConfigModel
from .user import UserModel

# 注意：旧的 sensor.py 模型已废弃，但文件保留作为备份
# 如需访问旧表，请直接使用：from models.sensor import SensorDataModel as SensorDataModelOld

__all__ = [
    "DeviceModel",
    "SensorDataModel",
    "SensorConfigModel",
    "MQTTConfigModel",
    "TopicConfigModel",
    "UserModel",
]