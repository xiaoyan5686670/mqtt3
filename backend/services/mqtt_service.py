"""MQTT服务 - 处理MQTT连接和数据接收"""
import paho.mqtt.client as mqtt
import json
import re
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session

from core.database import SessionLocal
from core.logging_config import get_logger
from models.device import DeviceModel
from models.sensor import SensorDataModel
from models.mqtt_config import MQTTConfigModel
from services import topic_config_service

logger = get_logger(__name__)


class MQTTService:
    """MQTT服务类"""
    
    def __init__(self):
        self.client: Optional[mqtt.Client] = None
        self.is_connected = False
        self.db: Optional[Session] = None

    def init_mqtt_client(self) -> bool:
        """初始化MQTT客户端"""
        try:
            self.db = SessionLocal()
            
            # 获取所有激活的主题配置
            active_configs = topic_config_service.get_active_topic_configs(self.db)
            
            if not active_configs:
                logger.warning("没有激活的主题配置")
                return False

            # 检查是否所有激活的配置都使用相同的MQTT服务器
            mqtt_config_ids = set(config.mqtt_config_id for config in active_configs if config.mqtt_config_id)
            
            if len(mqtt_config_ids) > 1:
                logger.warning("多个激活的配置使用不同的MQTT服务器，使用第一个配置的服务器")
            
            # 获取第一个配置的MQTT配置
            first_config = active_configs[0]
            if not first_config.mqtt_config_id:
                logger.error("主题配置没有关联的MQTT配置")
                return False
            
            mqtt_config = self.db.query(MQTTConfigModel).filter(
                MQTTConfigModel.id == first_config.mqtt_config_id
            ).first()
            
            if not mqtt_config:
                logger.error(f"未找到ID为 {first_config.mqtt_config_id} 的MQTT配置")
                return False

            # 创建MQTT客户端
            self.client = mqtt.Client()
            self.client.on_connect = self.on_connect
            self.client.on_disconnect = self.on_disconnect
            self.client.on_message = self.on_message

            # 设置用户名密码（如果有）
            if mqtt_config.username and mqtt_config.password:
                self.client.username_pw_set(mqtt_config.username, mqtt_config.password)

            # 连接MQTT服务器
            self.client.connect(mqtt_config.server, mqtt_config.port, 60)
            logger.info(f"MQTT客户端初始化成功，连接到 {mqtt_config.server}:{mqtt_config.port}")
            return True
        except Exception as e:
            logger.error(f"初始化MQTT客户端失败: {e}", exc_info=True)
            return False

    def on_connect(self, client, userdata, flags, rc):
        """连接成功回调"""
        if rc == 0:
            logger.info("MQTT连接成功")
            self.is_connected = True
            self.subscribe_to_topics()
        else:
            logger.error(f"MQTT连接失败，返回码: {rc}")

    def on_disconnect(self, client, userdata, rc):
        """断开连接回调"""
        logger.warning("MQTT连接断开")
        self.is_connected = False

    def subscribe_to_topics(self):
        """订阅主题"""
        if not self.client or not self.db:
            logger.warning("MQTT客户端未初始化")
            return

        try:
            active_configs = topic_config_service.get_active_topic_configs(self.db)
            
            for topic_config in active_configs:
                topics = self.parse_topics(topic_config.subscribe_topics)
                for topic in topics:
                    self.client.subscribe(topic)
                    logger.info(f"已订阅主题: {topic} (来自配置: {topic_config.name})")
        except Exception as e:
            logger.error(f"订阅主题失败: {e}", exc_info=True)

    def parse_topics(self, topics_str: str) -> List[str]:
        """解析主题字符串为列表"""
        if not topics_str:
            return []
        
        try:
            # 尝试解析为JSON数组
            parsed = json.loads(topics_str)
            if isinstance(parsed, list):
                return parsed
        except (json.JSONDecodeError, TypeError):
            # 如果不是JSON格式，则按换行符或逗号分割
            if '\n' in topics_str:
                return [t.strip() for t in topics_str.split('\n') if t.strip()]
            else:
                return [t.strip() for t in topics_str.split(',') if t.strip()]
        
        return []

    def on_message(self, client, userdata, msg):
        """消息接收回调"""
        logger.debug(f"收到消息: {msg.topic} - {msg.payload.decode()}")
        try:
            payload = msg.payload.decode()
            self.process_sensor_data(payload, msg.topic)
        except Exception as e:
            logger.error(f"处理消息时出错: {e}", exc_info=True)

    def process_sensor_data(self, payload: str, topic: str):
        """处理传感器数据"""
        logger.debug(f"处理传感器数据，Topic: {topic}, Payload: {payload}")
        
        if not self.db:
            self.db = SessionLocal()
        
        try:
            # 从topic中提取设备信息
            parts = topic.split('/')
            if len(parts) < 2:
                logger.warning(f"主题格式不正确，跳过处理: {topic}")
                return
            
            # 尝试多种设备名匹配策略
            device_prefix = parts[0]
            device_id = parts[1]
            potential_device_names = [
                f"{device_prefix}_{device_id}",
                device_id,
                device_prefix,
                f"{device_prefix}/{device_id}"
            ]
            
            device = None
            device_name = None
            for potential_name in potential_device_names:
                device = self.db.query(DeviceModel).filter(DeviceModel.name == potential_name).first()
                if device:
                    device_name = potential_name
                    logger.debug(f"找到设备: {device_name}")
                    break
            
            # 如果没找到，创建新设备
            if not device:
                device_name = f"{device_prefix}_{device_id}"
                logger.info(f"未找到现有设备，将创建新设备: {device_name}")
                device = DeviceModel(
                    name=device_name,
                    device_type="自动创建设备",
                    status="在线",
                    location="未知位置",
                    remark=None,  # 备注字段，可在编辑时填写
                    show_on_dashboard=True,  # 默认在首页展示
                    created_at=datetime.utcnow()  # 设置设备创建时间
                )
                self.db.add(device)
                self.db.commit()
                self.db.refresh(device)
            
            # 解析并保存传感器数据
            self.parse_and_save_sensor_data(device.id, payload)
            self.db.commit()
            logger.debug(f"传感器数据已保存: 设备={device_name}")
        except Exception as e:
            logger.error(f"保存传感器数据时出错: {e}", exc_info=True)
            if self.db:
                self.db.rollback()

    def parse_and_save_sensor_data(self, device_id: int, payload: str):
        """解析并保存传感器数据"""
        # 首先检查是否是继电器控制消息（relayon/relayoff）
        payload_lower = payload.strip().lower()
        if payload_lower == 'relayon':
            # 收到开启命令，设置继电器状态为1
            self.save_sensor_data(device_id, 'Relay Status', 1, '')
            logger.info(f"收到继电器开启命令，设备ID: {device_id}")
            return
        elif payload_lower == 'relayoff':
            # 收到关闭命令，设置继电器状态为0
            self.save_sensor_data(device_id, 'Relay Status', 0, '')
            logger.info(f"收到继电器关闭命令，设备ID: {device_id}")
            return
        
        # 匹配常见的传感器数据格式
        patterns = [
            (r'Temperature1:\s*([\d.]+)\s*C', 'Temperature1', '°C'),
            (r'Humidity1:\s*([\d.]+)\s*%', 'Humidity1', '%'),
            (r'Temperature2:\s*([\d.]+)\s*C', 'Temperature2', '°C'),
            (r'Humidity2:\s*([\d.]+)\s*%', 'Humidity2', '%'),
            (r'Relay Status:\s*(\d)', 'Relay Status', ''),
            (r'PB8 Level:\s*(\d)', 'PB8 Level', ''),
        ]
        
        for pattern, sensor_type, unit in patterns:
            match = re.search(pattern, payload)
            if match:
                try:
                    value = float(match.group(1)) if unit != '' else int(match.group(1))
                    self.save_sensor_data(device_id, sensor_type, value, unit)
                except ValueError as e:
                    logger.warning(f"转换数值失败: {match.group(1)}, 错误: {e}")

    def save_sensor_data(self, device_id: int, sensor_type: str, value: float, unit: str):
        """保存传感器数据到数据库"""
        # 检查是否已存在相同类型的传感器数据
        existing_sensor = self.db.query(SensorDataModel).filter(
            SensorDataModel.device_id == device_id,
            SensorDataModel.type == sensor_type
        ).first()
        
        # 确定默认的最小值和最大值
        min_value = 0.0
        max_value = 100.0
        if 'Temperature' in sensor_type:
            min_value = -40.0
            max_value = 80.0
        elif 'Humidity' in sensor_type:
            min_value = 0.0
            max_value = 100.0
        
        # 确定告警状态
        alert_status = 'normal'
        if 'Temperature' in sensor_type and float(value) > 28:
            alert_status = 'alert' if float(value) > 30 else 'warning'
        elif 'Humidity' in sensor_type and float(value) > 65:
            alert_status = 'alert' if float(value) > 70 else 'warning'
        
        if existing_sensor:
            # 更新现有传感器数据
            existing_sensor.value = value
            existing_sensor.unit = unit
            existing_sensor.timestamp = datetime.utcnow()
            existing_sensor.alert_status = alert_status
        else:
            # 创建新的传感器数据
            sensor_data = SensorDataModel(
                device_id=device_id,
                type=sensor_type,
                value=value,
                unit=unit,
                timestamp=datetime.utcnow(),
                min_value=min_value,
                max_value=max_value,
                alert_status=alert_status
            )
            self.db.add(sensor_data)

    def start(self) -> bool:
        """启动MQTT服务"""
        if not self.client:
            if not self.init_mqtt_client():
                return False
        
        logger.info("启动MQTT服务...")
        self.client.loop_start()
        return True

    def publish_message(self, topic: str, message: str = "", qos: int = 0) -> bool:
        """发布消息到指定主题"""
        if not self.client:
            logger.warning("MQTT客户端未初始化，尝试初始化...")
            if not self.init_mqtt_client():
                logger.error("无法初始化MQTT客户端")
                return False
            if not self.start():
                logger.error("无法启动MQTT服务")
                return False
        
        if not self.is_connected:
            logger.warning("MQTT未连接，尝试重新连接...")
            if not self.start():
                logger.error("无法连接到MQTT服务器")
                return False
        
        try:
            result = self.client.publish(topic, message, qos)
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                logger.info(f"成功发布消息到主题 {topic}: {message}")
                return True
            else:
                logger.error(f"发布消息失败，返回码: {result.rc}")
                return False
        except Exception as e:
            logger.error(f"发布消息时出错: {e}", exc_info=True)
            return False

    def stop(self):
        """停止MQTT服务"""
        if self.client:
            logger.info("停止MQTT服务...")
            self.client.loop_stop()
            self.client.disconnect()
            self.is_connected = False
        
        if self.db:
            self.db.close()


# 全局MQTT服务实例
_mqtt_service: Optional[MQTTService] = None


def get_mqtt_service() -> MQTTService:
    """获取MQTT服务实例（单例模式）"""
    global _mqtt_service
    if _mqtt_service is None:
        _mqtt_service = MQTTService()
    return _mqtt_service


def start_mqtt_service() -> bool:
    """启动MQTT服务"""
    service = get_mqtt_service()
    return service.start()


def stop_mqtt_service():
    """停止MQTT服务"""
    global _mqtt_service
    if _mqtt_service:
        _mqtt_service.stop()
        _mqtt_service = None


def restart_mqtt_service() -> bool:
    """重启MQTT服务"""
    stop_mqtt_service()
    return start_mqtt_service()