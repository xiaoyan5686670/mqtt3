"""MQTT服务 - 处理MQTT连接和数据接收"""
import paho.mqtt.client as mqtt
import json
import re
import requests
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from core.database import SessionLocal
from core.logging_config import get_logger
from models.device import DeviceModel
from models.sensor_data_new import SensorDataModel
from models.sensor_config import SensorConfigModel
from models.mqtt_config import MQTTConfigModel
from services import topic_config_service
from services import sensor_config_service

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
            logger.info("MQTT连接成功，开始订阅主题...")
            self.is_connected = True
            # 订阅主题（这是正常的，用于接收传感器数据）
            self.subscribe_to_topics()
            logger.info("主题订阅完成")
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
                
                # 尝试为新设备自动匹配主题配置
                from services import topic_config_service
                matched_config = topic_config_service.find_topic_config_by_device_name(self.db, device_name)
                if matched_config:
                    device.topic_config_id = matched_config.id
                    logger.info(f"自动为新设备匹配到主题配置: {matched_config.name}")
                
                self.db.add(device)
                self.db.commit()
                self.db.refresh(device)
            
            # 获取解析配置
            json_parse_config = None
            if device.topic_config_id:
                from models.topic_config import TopicConfigModel
                config = self.db.query(TopicConfigModel).filter(TopicConfigModel.id == device.topic_config_id).first()
                if config and config.json_parse_config:
                    json_parse_config = config.json_parse_config
            
            # 如果设备没有关联配置，尝试根据当前主题直接查找配置
            if not json_parse_config:
                from models.topic_config import TopicConfigModel
                active_configs = self.db.query(TopicConfigModel).filter(TopicConfigModel.is_active == True).all()
                for config in active_configs:
                    topics = self.parse_topics(config.subscribe_topics)
                    if topic in topics and config.json_parse_config:
                        json_parse_config = config.json_parse_config
                        # 如果设备还没有关联配置，顺便关联一下
                        if not device.topic_config_id:
                            device.topic_config_id = config.id
                            self.db.commit()
                        break

            # 解析并保存传感器数据
            self.parse_and_save_sensor_data(device.id, payload, json_parse_config)
            self.db.commit()
            logger.debug(f"传感器数据已保存: 设备={device_name}")
        except Exception as e:
            logger.error(f"保存传感器数据时出错: {e}", exc_info=True)
            if self.db:
                self.db.rollback()

    def parse_and_save_sensor_data(self, device_id: int, payload: str, json_parse_config: str = None):
        """解析并保存传感器数据"""
        # 首先检查是否是继电器控制消息（relayon/relayoff）
        payload_stripped = payload.strip()
        payload_lower = payload_stripped.lower()
        
        if payload_lower == 'relayon':
            self.save_sensor_data(device_id, 'Relay Status', 1, '', '继电器')
            logger.info(f"收到继电器开启命令，设备ID: {device_id}")
            return
        elif payload_lower == 'relayoff':
            self.save_sensor_data(device_id, 'Relay Status', 0, '', '继电器')
            logger.info(f"收到继电器关闭命令，设备ID: {device_id}")
            return

        # 尝试作为 JSON 解析
        try:
            data = json.loads(payload_stripped)
            if isinstance(data, dict):
                logger.debug(f"成功解析 JSON 数据: {data}")
                
                # 如果有自定义解析配置
                if json_parse_config:
                    try:
                        parse_map = json.loads(json_parse_config)
                        for key, config in parse_map.items():
                            if key in data:
                                # 确保 config 是字典类型，如果不是，创建一个默认配置
                                if not isinstance(config, dict):
                                    logger.warning(f"JSON 配置格式错误: {key} 的配置不是字典类型，使用默认配置")
                                    config = {'type': key, 'unit': ''}
                                
                                # 核心改进：优先保持原始 key 作为 type，config 中的 type 作为 display_name 或 备用 type
                                # 如果 config 中有 type，且不等于 key，我们把它视为 display_name
                                raw_value = data[key]
                                
                                # 解析配置中的信息
                                conf_type = config.get('type', key)
                                unit = config.get('unit', '')
                                display_name = config.get('display_name') or config.get('name')
                                
                                # 如果配置里的 type 和原始 key 不一样，且没有显式的 display_name，
                                # 则把配置里的 type 当作 display_name
                                if not display_name and conf_type != key:
                                    display_name = conf_type
                                
                                # 处理值的类型转换
                                processed_value = raw_value
                                key_lower = key.lower()
                                
                                # 如果是字符串类型的继电器/开关状态，转换为数字
                                if isinstance(raw_value, str):
                                    value_lower = raw_value.lower().strip()
                                    if key_lower in ['relay_status', 'relay', 'switch', 'switch_status', 'realy_in_status', 'relay_in_status'] or \
                                       'relay' in key_lower or 'switch' in key_lower or 'realy' in key_lower:
                                        # 转换常见的开关状态字符串为数字
                                        if value_lower in ['on', 'open', 'true', '1', 'active', 'enabled']:
                                            processed_value = 1
                                        elif value_lower in ['off', 'close', 'false', '0', 'inactive', 'disabled']:
                                            processed_value = 0
                                        else:
                                            # 尝试直接转换为数字
                                            try:
                                                processed_value = float(raw_value)
                                            except ValueError:
                                                logger.warning(f"无法转换继电器状态值: {raw_value}，跳过该字段")
                                                continue
                                elif not isinstance(raw_value, (int, float)):
                                    # 如果不是数字也不是字符串，尝试转换为浮点数
                                    try:
                                        processed_value = float(raw_value)
                                    except (ValueError, TypeError):
                                        logger.warning(f"无法转换值类型: {raw_value} ({type(raw_value)}), 跳过字段 {key}")
                                        continue
                                
                                # 始终以原始 key 作为数据库的 type，除非配置中明确要求覆盖（这里我们选择保留原始 key 为 type 以便区分）
                                self.save_sensor_data(device_id, key, processed_value, unit, display_name)
                        return # 使用 JSON 配置解析成功，直接返回
                    except Exception as e:
                        logger.error(f"使用自定义 JSON 配置解析失败: {e}")
                        # 记录详细的调试信息
                        logger.error(f"JSON 配置内容: {json_parse_config}")
                        logger.error(f"接收到的数据: {data}")
                
                # 默认 JSON 解析逻辑（如果没有配置或解析失败）
                for key, value in data.items():
                    sensor_type = key
                    unit = ''
                    display_name = None
                    processed_value = value
                    
                    key_lower = key.lower()
                    
                    # 处理字符串类型的继电器/开关状态
                    if isinstance(value, str):
                        value_lower = value.lower().strip()
                        if key_lower in ['relay_status', 'relay', 'switch', 'switch_status', 'realy_in_status', 'relay_in_status'] or \
                           'relay' in key_lower or 'switch' in key_lower or 'realy' in key_lower:
                            if value_lower in ['on', 'open', 'true', '1', 'active', 'enabled']:
                                processed_value = 1
                            elif value_lower in ['off', 'close', 'false', '0', 'inactive', 'disabled']:
                                processed_value = 0
                            else:
                                logger.warning(f"无法识别继电器状态值: {value}，跳过字段 {key}")
                                continue
                            
                            # 支持两种拼写：realy_in_status（错误拼写）和 relay_in_status（正确拼写）
                            if key_lower in ['realy_in_status', 'relay_in_status']:
                                display_name = "继电器输入"
                            else:
                                display_name = "继电器"
                        else:
                            # 非继电器类型的字符串，跳过
                            continue
                    elif isinstance(value, (int, float)):
                        if 'temp' in key_lower:
                            unit = '°C'
                            # 尝试生成一个友好的显示名称，例如 air_temperature_1 -> 温度 1
                            num_match = re.search(r'\d+', key)
                            num = num_match.group() if num_match else ""
                            display_name = f"温度{num}" if num else "温度"
                        elif 'hum' in key_lower:
                            unit = '%'
                            num_match = re.search(r'\d+', key)
                            num = num_match.group() if num_match else ""
                            display_name = f"湿度{num}" if num else "湿度"
                        elif 'relay' in key_lower or 'realy' in key_lower:
                            # 支持两种拼写：realy_in_status（错误拼写）和 relay_in_status（正确拼写）
                            if key_lower in ['realy_in_status', 'relay_in_status']:
                                display_name = "继电器输入"
                            else:
                                display_name = "继电器"
                    else:
                        # 其他类型，跳过
                        continue
                    
                    self.save_sensor_data(device_id, sensor_type, processed_value, unit, display_name)
                return
        except json.JSONDecodeError:
            pass # 不是 JSON 格式，继续使用正则解析

        # 匹配常见的传感器数据格式（正则解析）
        patterns = [
            (r'Temperature1:\s*([\d.]+)\s*C', 'Temperature1', '°C', '温度1'),
            (r'Humidity1:\s*([\d.]+)\s*%', 'Humidity1', '%', '湿度1'),
            (r'Temperature2:\s*([\d.]+)\s*C', 'Temperature2', '°C', '温度2'),
            (r'Humidity2:\s*([\d.]+)\s*%', 'Humidity2', '%', '湿度2'),
            (r'Relay Status:\s*(\d)', 'Relay Status', '', '继电器'),
            (r'PB8 Level:\s*(\d)', 'PB8 Level', '', 'PB8电平'),
        ]
        
        for pattern, sensor_type, unit, display_name in patterns:
            match = re.search(pattern, payload)
            if match:
                try:
                    value = float(match.group(1)) if unit != '' else int(match.group(1))
                    self.save_sensor_data(device_id, sensor_type, value, unit, display_name)
                except ValueError as e:
                    logger.warning(f"转换数值失败: {match.group(1)}, 错误: {e}")

    def save_sensor_data(self, device_id: int, sensor_type: str, value: float, unit: str, display_name: str = None):
        """保存传感器数据到数据库（使用新架构：配置和数据分离）"""
        # 确定默认的最小值和最大值
        min_value = 0.0
        max_value = 100.0
        
        type_lower = sensor_type.lower()
        
        if 'temp' in type_lower:
            min_value = -40.0
            max_value = 80.0
        elif 'hum' in type_lower:
            min_value = 0.0
            max_value = 100.0
        
        # 确定告警状态
        alert_status = 'normal'
        try:
            val_float = float(value)
            if 'temp' in type_lower:
                if val_float > 30: alert_status = 'alert'
                elif val_float > 28: alert_status = 'warning'
            elif 'hum' in type_lower:
                if val_float > 70: alert_status = 'alert'
                elif val_float > 65: alert_status = 'warning'
        except:
            pass
        
        # 获取或创建传感器配置（配置只创建一次）
        sensor_config = sensor_config_service.get_or_create_sensor_config(
            db=self.db,
            device_id=device_id,
            sensor_type=sensor_type,
            unit=unit,
            display_name=display_name,
            min_value=min_value,
            max_value=max_value
        )
        
        # 创建传感器数据记录（只包含时序数据）
        sensor_data = SensorDataModel(
            sensor_config_id=sensor_config.id,
            value=value,
            timestamp=datetime.utcnow(),
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
        import time
        
        if not self.client:
            logger.warning("MQTT客户端未初始化，尝试初始化...")
            if not self.init_mqtt_client():
                logger.error("无法初始化MQTT客户端")
                return False
            if not self.start():
                logger.error("无法启动MQTT服务")
                return False
        
        # 等待连接完成（最多等待5秒）
        if not self.is_connected:
            logger.warning("MQTT未连接，尝试重新连接...")
            if not self.start():
                logger.error("无法连接到MQTT服务器")
                return False
            
            # 等待连接完成
            max_wait = 50  # 最多等待5秒（50 * 0.1秒）
            wait_count = 0
            while not self.is_connected and wait_count < max_wait:
                time.sleep(0.1)
                wait_count += 1
            
            if not self.is_connected:
                logger.error("等待MQTT连接超时")
                return False
        
        try:
            # 发布消息（注意：这是 PUBLISH 操作，不是 SUBSCRIBE）
            logger.info(f"准备发布消息到主题 {topic}: {message}")
            result = self.client.publish(topic, message, qos)
            
            # 等待发布完成（最多等待1秒）
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                # 等待消息发送完成
                try:
                    result.wait_for_publish(timeout=1.0)
                except Exception as wait_error:
                    logger.warning(f"等待发布完成时出错（可能已发送）: {wait_error}")
                
                logger.info(f"✅ 成功发布消息到主题 {topic}: {message} (消息ID: {result.mid})")
                return True
            else:
                logger.error(f"❌ 发布消息失败，返回码: {result.rc}")
                return False
        except Exception as e:
            logger.error(f"发布消息时出错: {e}", exc_info=True)
            return False

    def get_emqx_clients(self) -> Dict[str, Any]:
        """从EMQX API获取客户端连接状态"""
        try:
            if not self.db:
                self.db = SessionLocal()
            
            # 获取MQTT配置
            mqtt_config = self.db.query(MQTTConfigModel).filter(
                MQTTConfigModel.is_active == True
            ).first()
            
            if not mqtt_config:
                logger.warning("未找到激活的MQTT配置")
                return {"data": [], "meta": {"count": 0}}
            
            # 检查是否配置了 API Key
            api_key = mqtt_config.api_key
            api_secret = mqtt_config.api_secret
            
            if not api_key or not api_secret:
                logger.warning("未配置 EMQX API Key，请在系统中配置 API 密钥")
                return {"data": [], "meta": {"count": 0}}
            
            # 构建EMQX API URL
            api_port = mqtt_config.api_port or 18083
            api_url = f"http://{mqtt_config.server}:{api_port}/api/v5/clients"
            
            logger.info(f"正在调用 EMQX API: {api_url}")
            
            # 使用 API Key 和 Secret Key 进行认证
            response = requests.get(
                api_url,
                auth=(api_key, api_secret),
                timeout=10,
                params={'limit': 1000}  # EMQX API 限制最大 1000
            )
            
            if response.status_code == 200:
                data = response.json()
                client_count = len(data.get('data', []))
                logger.info(f"✅ 成功获取 EMQX 客户端列表，共 {client_count} 个客户端")
                return data
            elif response.status_code == 401:
                logger.error("❌ EMQX API 认证失败，请检查 API Key 和 Secret Key 是否正确")
                return {"data": [], "meta": {"count": 0}}
            else:
                logger.error(f"❌ 获取 EMQX 客户端列表失败，状态码: {response.status_code}, 响应: {response.text}")
                return {"data": [], "meta": {"count": 0}}
                
        except requests.exceptions.Timeout:
            logger.error("❌ EMQX API 请求超时")
            return {"data": [], "meta": {"count": 0}}
        except requests.exceptions.ConnectionError:
            logger.error("❌ 无法连接到 EMQX API，请检查服务器地址和端口")
            return {"data": [], "meta": {"count": 0}}
        except Exception as e:
            logger.error(f"❌ 获取 EMQX 客户端状态时出错: {e}", exc_info=True)
            return {"data": [], "meta": {"count": 0}}

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
    """重启MQTT服务（兼容旧版本，同时重启所有用户的MQTT服务）"""
    stop_mqtt_service()
    # 同时重启所有用户的MQTT服务
    restart_all_user_mqtt_services()
    return start_mqtt_service()


# ==================== 多租户支持：用户级MQTT服务（方案A） ====================

class UserMQTTService:
    """用户级MQTT服务类 - 每个用户拥有独立的MQTT连接"""
    
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.client: Optional[mqtt.Client] = None
        self.is_connected = False
        self.db: Optional[Session] = None
        self.mqtt_config_id: Optional[int] = None

    def init_mqtt_client(self) -> bool:
        """初始化该用户的MQTT客户端"""
        try:
            self.db = SessionLocal()
            
            # 获取该用户激活的主题配置
            active_configs = topic_config_service.get_active_topic_configs(self.db, user_id=self.user_id)
            
            if not active_configs:
                logger.warning(f"用户 {self.user_id} 没有激活的主题配置")
                return False

            # 检查是否所有激活的配置都使用相同的MQTT服务器
            mqtt_config_ids = set(config.mqtt_config_id for config in active_configs if config.mqtt_config_id)
            
            if len(mqtt_config_ids) > 1:
                logger.warning(f"用户 {self.user_id} 的多个激活配置使用不同的MQTT服务器，使用第一个配置的服务器")
            
            # 获取第一个配置的MQTT配置
            first_config = active_configs[0]
            if not first_config.mqtt_config_id:
                logger.error(f"用户 {self.user_id} 的主题配置没有关联的MQTT配置")
                return False
            
            mqtt_config = self.db.query(MQTTConfigModel).filter(
                MQTTConfigModel.id == first_config.mqtt_config_id
            ).first()
            
            if not mqtt_config:
                logger.error(f"用户 {self.user_id} 未找到ID为 {first_config.mqtt_config_id} 的MQTT配置")
                return False

            # 验证MQTT配置属于该用户（或为系统级配置）
            if mqtt_config.user_id is not None and mqtt_config.user_id != self.user_id:
                logger.error(f"用户 {self.user_id} 无权使用MQTT配置 {mqtt_config.id}")
                return False

            self.mqtt_config_id = mqtt_config.id

            # 创建MQTT客户端，使用用户ID作为客户端ID的一部分以确保唯一性
            client_id = f"mqtt_user_{self.user_id}_{mqtt_config.id}"
            self.client = mqtt.Client(client_id=client_id)
            self.client.on_connect = self.on_connect
            self.client.on_disconnect = self.on_disconnect
            self.client.on_message = self.on_message

            # 设置用户名密码（如果有）
            if mqtt_config.username and mqtt_config.password:
                self.client.username_pw_set(mqtt_config.username, mqtt_config.password)

            # 连接MQTT服务器
            self.client.connect(mqtt_config.server, mqtt_config.port, 60)
            logger.info(f"用户 {self.user_id} 的MQTT客户端初始化成功，连接到 {mqtt_config.server}:{mqtt_config.port}")
            return True
        except Exception as e:
            logger.error(f"用户 {self.user_id} 初始化MQTT客户端失败: {e}", exc_info=True)
            return False

    def on_connect(self, client, userdata, flags, rc):
        """连接成功回调"""
        if rc == 0:
            logger.info(f"用户 {self.user_id} MQTT连接成功，开始订阅主题...")
            self.is_connected = True
            self.subscribe_to_topics()
            logger.info(f"用户 {self.user_id} 主题订阅完成")
        else:
            logger.error(f"用户 {self.user_id} MQTT连接失败，返回码: {rc}")

    def on_disconnect(self, client, userdata, rc):
        """断开连接回调"""
        logger.warning(f"用户 {self.user_id} MQTT连接断开")
        self.is_connected = False

    def subscribe_to_topics(self):
        """订阅该用户的主题"""
        if not self.client or not self.db:
            logger.warning(f"用户 {self.user_id} MQTT客户端未初始化")
            return

        try:
            # 只获取该用户激活的主题配置
            active_configs = topic_config_service.get_active_topic_configs(self.db, user_id=self.user_id)
            
            for topic_config in active_configs:
                # 验证主题配置属于该用户
                if topic_config.user_id is not None and topic_config.user_id != self.user_id:
                    logger.warning(f"用户 {self.user_id} 无权订阅主题配置 {topic_config.id}，跳过")
                    continue
                
                topics = self.parse_topics(topic_config.subscribe_topics)
                for topic in topics:
                    self.client.subscribe(topic)
                    logger.info(f"用户 {self.user_id} 已订阅主题: {topic} (来自配置: {topic_config.name})")
        except Exception as e:
            logger.error(f"用户 {self.user_id} 订阅主题失败: {e}", exc_info=True)

    def parse_topics(self, topics_str: str) -> List[str]:
        """解析主题字符串为列表"""
        if not topics_str:
            return []
        
        try:
            parsed = json.loads(topics_str)
            if isinstance(parsed, list):
                return parsed
        except (json.JSONDecodeError, TypeError):
            if '\n' in topics_str:
                return [t.strip() for t in topics_str.split('\n') if t.strip()]
            else:
                return [t.strip() for t in topics_str.split(',') if t.strip()]
        
        return []

    def on_message(self, client, userdata, msg):
        """消息接收回调"""
        logger.debug(f"用户 {self.user_id} 收到消息: {msg.topic} - {msg.payload.decode()}")
        try:
            payload = msg.payload.decode()
            self.process_sensor_data(payload, msg.topic)
        except Exception as e:
            logger.error(f"用户 {self.user_id} 处理消息时出错: {e}", exc_info=True)

    def process_sensor_data(self, payload: str, topic: str):
        """处理传感器数据（只处理属于该用户的设备）"""
        logger.debug(f"用户 {self.user_id} 处理传感器数据，Topic: {topic}, Payload: {payload}")
        
        if not self.db:
            self.db = SessionLocal()
        
        try:
            # 从topic中提取设备信息
            parts = topic.split('/')
            if len(parts) < 2:
                logger.warning(f"用户 {self.user_id} 主题格式不正确，跳过处理: {topic}")
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
                # 只查找属于该用户的设备
                device = self.db.query(DeviceModel).filter(
                    DeviceModel.name == potential_name,
                    DeviceModel.user_id == self.user_id
                ).first()
                if device:
                    device_name = potential_name
                    logger.debug(f"用户 {self.user_id} 找到设备: {device_name}")
                    break
            
            # 如果没找到，创建新设备（自动关联到当前用户）
            if not device:
                device_name = f"{device_prefix}_{device_id}"
                logger.info(f"用户 {self.user_id} 未找到现有设备，将创建新设备: {device_name}")
                device = DeviceModel(
                    name=device_name,
                    device_type="自动创建设备",
                    status="在线",
                    location="未知位置",
                    remark=None,
                    show_on_dashboard=True,
                    user_id=self.user_id,  # 关联到当前用户
                    created_at=datetime.utcnow()
                )
                
                # 尝试为新设备自动匹配主题配置（只匹配该用户的配置）
                matched_config = topic_config_service.find_topic_config_by_device_name(self.db, device_name)
                if matched_config and (matched_config.user_id is None or matched_config.user_id == self.user_id):
                    device.topic_config_id = matched_config.id
                    logger.info(f"用户 {self.user_id} 自动为新设备匹配到主题配置: {matched_config.name}")
                
                self.db.add(device)
                self.db.commit()
                self.db.refresh(device)
            
            # 获取解析配置（只使用该用户的配置）
            json_parse_config = None
            if device.topic_config_id:
                from models.topic_config import TopicConfigModel
                config = self.db.query(TopicConfigModel).filter(
                    TopicConfigModel.id == device.topic_config_id,
                    (TopicConfigModel.user_id == self.user_id) | (TopicConfigModel.user_id.is_(None))
                ).first()
                if config and config.json_parse_config:
                    json_parse_config = config.json_parse_config
            
            # 如果设备没有关联配置，尝试根据当前主题直接查找配置（只查找该用户的）
            if not json_parse_config:
                from models.topic_config import TopicConfigModel
                active_configs = self.db.query(TopicConfigModel).filter(
                    TopicConfigModel.is_active == True,
                    (TopicConfigModel.user_id == self.user_id) | (TopicConfigModel.user_id.is_(None))
                ).all()
                for config in active_configs:
                    topics = self.parse_topics(config.subscribe_topics)
                    if topic in topics and config.json_parse_config:
                        json_parse_config = config.json_parse_config
                        if not device.topic_config_id:
                            device.topic_config_id = config.id
                            self.db.commit()
                        break

            # 解析并保存传感器数据（复用原有逻辑）
            self.parse_and_save_sensor_data(device.id, payload, json_parse_config)
            self.db.commit()
            logger.debug(f"用户 {self.user_id} 传感器数据已保存: 设备={device_name}")
        except Exception as e:
            logger.error(f"用户 {self.user_id} 保存传感器数据时出错: {e}", exc_info=True)
            if self.db:
                self.db.rollback()

    def parse_and_save_sensor_data(self, device_id: int, payload: str, json_parse_config: str = None):
        """解析并保存传感器数据（复用原有逻辑）"""
        # 复用原有的MQTTService的解析逻辑
        # 这里可以调用原有方法或直接复制逻辑
        # 为了简化，我们直接复用原有逻辑
        payload_stripped = payload.strip()
        payload_lower = payload_stripped.lower()
        
        if payload_lower == 'relayon':
            self.save_sensor_data(device_id, 'Relay Status', 1, '', '继电器')
            logger.info(f"用户 {self.user_id} 收到继电器开启命令，设备ID: {device_id}")
            return
        elif payload_lower == 'relayoff':
            self.save_sensor_data(device_id, 'Relay Status', 0, '', '继电器')
            logger.info(f"用户 {self.user_id} 收到继电器关闭命令，设备ID: {device_id}")
            return

        # 尝试作为 JSON 解析
        try:
            data = json.loads(payload_stripped)
            if isinstance(data, dict):
                logger.debug(f"用户 {self.user_id} 成功解析 JSON 数据: {data}")
                
                if json_parse_config:
                    try:
                        parse_map = json.loads(json_parse_config)
                        for key, config in parse_map.items():
                            if key in data:
                                if not isinstance(config, dict):
                                    logger.warning(f"用户 {self.user_id} JSON 配置格式错误: {key}")
                                    config = {'type': key, 'unit': ''}
                                
                                raw_value = data[key]
                                conf_type = config.get('type', key)
                                unit = config.get('unit', '')
                                display_name = config.get('display_name') or config.get('name')
                                
                                if not display_name and conf_type != key:
                                    display_name = conf_type
                                
                                processed_value = raw_value
                                key_lower = key.lower()
                                
                                if isinstance(raw_value, str):
                                    value_lower = raw_value.lower().strip()
                                    if key_lower in ['relay_status', 'relay', 'switch', 'switch_status', 'realy_in_status', 'relay_in_status'] or \
                                       'relay' in key_lower or 'switch' in key_lower or 'realy' in key_lower:
                                        if value_lower in ['on', 'open', 'true', '1', 'active', 'enabled']:
                                            processed_value = 1
                                        elif value_lower in ['off', 'close', 'false', '0', 'inactive', 'disabled']:
                                            processed_value = 0
                                        else:
                                            try:
                                                processed_value = float(raw_value)
                                            except ValueError:
                                                logger.warning(f"用户 {self.user_id} 无法转换继电器状态值: {raw_value}")
                                                continue
                                elif not isinstance(raw_value, (int, float)):
                                    try:
                                        processed_value = float(raw_value)
                                    except (ValueError, TypeError):
                                        logger.warning(f"用户 {self.user_id} 无法转换值类型: {raw_value}")
                                        continue
                                
                                self.save_sensor_data(device_id, key, processed_value, unit, display_name)
                        return
                    except Exception as e:
                        logger.error(f"用户 {self.user_id} 使用自定义 JSON 配置解析失败: {e}")
                
                # 默认 JSON 解析逻辑
                for key, value in data.items():
                    sensor_type = key
                    unit = ''
                    display_name = None
                    processed_value = value
                    
                    key_lower = key.lower()
                    
                    if isinstance(value, str):
                        value_lower = value.lower().strip()
                        if key_lower in ['relay_status', 'relay', 'switch', 'switch_status', 'realy_in_status', 'relay_in_status'] or \
                           'relay' in key_lower or 'switch' in key_lower or 'realy' in key_lower:
                            if value_lower in ['on', 'open', 'true', '1', 'active', 'enabled']:
                                processed_value = 1
                            elif value_lower in ['off', 'close', 'false', '0', 'inactive', 'disabled']:
                                processed_value = 0
                            else:
                                logger.warning(f"用户 {self.user_id} 无法识别继电器状态值: {value}")
                                continue
                            
                            if key_lower in ['realy_in_status', 'relay_in_status']:
                                display_name = "继电器输入"
                            else:
                                display_name = "继电器"
                        else:
                            continue
                    elif isinstance(value, (int, float)):
                        if 'temp' in key_lower:
                            unit = '°C'
                            num_match = re.search(r'\d+', key)
                            num = num_match.group() if num_match else ""
                            display_name = f"温度{num}" if num else "温度"
                        elif 'hum' in key_lower:
                            unit = '%'
                            num_match = re.search(r'\d+', key)
                            num = num_match.group() if num_match else ""
                            display_name = f"湿度{num}" if num else "湿度"
                        elif 'relay' in key_lower or 'realy' in key_lower:
                            if key_lower in ['realy_in_status', 'relay_in_status']:
                                display_name = "继电器输入"
                            else:
                                display_name = "继电器"
                    else:
                        continue
                    
                    self.save_sensor_data(device_id, sensor_type, processed_value, unit, display_name)
                return
        except json.JSONDecodeError:
            pass

        # 正则解析（复用原有逻辑）
        patterns = [
            (r'Temperature1:\s*([\d.]+)\s*C', 'Temperature1', '°C', '温度1'),
            (r'Humidity1:\s*([\d.]+)\s*%', 'Humidity1', '%', '湿度1'),
            (r'Temperature2:\s*([\d.]+)\s*C', 'Temperature2', '°C', '温度2'),
            (r'Humidity2:\s*([\d.]+)\s*%', 'Humidity2', '%', '湿度2'),
            (r'Relay Status:\s*(\d)', 'Relay Status', '', '继电器'),
            (r'PB8 Level:\s*(\d)', 'PB8 Level', '', 'PB8电平'),
        ]
        
        for pattern, sensor_type, unit, display_name in patterns:
            match = re.search(pattern, payload)
            if match:
                try:
                    value = float(match.group(1)) if unit != '' else int(match.group(1))
                    self.save_sensor_data(device_id, sensor_type, value, unit, display_name)
                except ValueError as e:
                    logger.warning(f"用户 {self.user_id} 转换数值失败: {match.group(1)}, 错误: {e}")

    def save_sensor_data(self, device_id: int, sensor_type: str, value: float, unit: str, display_name: str = None):
        """保存传感器数据到数据库"""
        min_value = 0.0
        max_value = 100.0
        
        type_lower = sensor_type.lower()
        
        if 'temp' in type_lower:
            min_value = -40.0
            max_value = 80.0
        elif 'hum' in type_lower:
            min_value = 0.0
            max_value = 100.0
        
        alert_status = 'normal'
        try:
            val_float = float(value)
            if 'temp' in type_lower:
                if val_float > 30: alert_status = 'alert'
                elif val_float > 28: alert_status = 'warning'
            elif 'hum' in type_lower:
                if val_float > 70: alert_status = 'alert'
                elif val_float > 65: alert_status = 'warning'
        except:
            pass
        
        sensor_config = sensor_config_service.get_or_create_sensor_config(
            db=self.db,
            device_id=device_id,
            sensor_type=sensor_type,
            unit=unit,
            display_name=display_name,
            min_value=min_value,
            max_value=max_value
        )
        
        sensor_data = SensorDataModel(
            sensor_config_id=sensor_config.id,
            value=value,
            timestamp=datetime.utcnow(),
            alert_status=alert_status
        )
        self.db.add(sensor_data)

    def start(self) -> bool:
        """启动该用户的MQTT服务"""
        if not self.client:
            if not self.init_mqtt_client():
                return False
        
        logger.info(f"启动用户 {self.user_id} 的MQTT服务...")
        self.client.loop_start()
        return True

    def publish_message(self, topic: str, message: str = "", qos: int = 0) -> bool:
        """发布消息到指定主题"""
        import time
        
        if not self.client:
            logger.warning(f"用户 {self.user_id} MQTT客户端未初始化，尝试初始化...")
            if not self.init_mqtt_client():
                logger.error(f"用户 {self.user_id} 无法初始化MQTT客户端")
                return False
            if not self.start():
                logger.error(f"用户 {self.user_id} 无法启动MQTT服务")
                return False
        
        if not self.is_connected:
            logger.warning(f"用户 {self.user_id} MQTT未连接，尝试重新连接...")
            if not self.start():
                logger.error(f"用户 {self.user_id} 无法连接到MQTT服务器")
                return False
            
            max_wait = 50
            wait_count = 0
            while not self.is_connected and wait_count < max_wait:
                time.sleep(0.1)
                wait_count += 1
            
            if not self.is_connected:
                logger.error(f"用户 {self.user_id} 等待MQTT连接超时")
                return False
        
        try:
            logger.info(f"用户 {self.user_id} 准备发布消息到主题 {topic}: {message}")
            result = self.client.publish(topic, message, qos)
            
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                try:
                    result.wait_for_publish(timeout=1.0)
                except Exception as wait_error:
                    logger.warning(f"用户 {self.user_id} 等待发布完成时出错: {wait_error}")
                
                logger.info(f"✅ 用户 {self.user_id} 成功发布消息到主题 {topic}: {message}")
                return True
            else:
                logger.error(f"❌ 用户 {self.user_id} 发布消息失败，返回码: {result.rc}")
                return False
        except Exception as e:
            logger.error(f"用户 {self.user_id} 发布消息时出错: {e}", exc_info=True)
            return False

    def stop(self):
        """停止该用户的MQTT服务"""
        if self.client:
            logger.info(f"停止用户 {self.user_id} 的MQTT服务...")
            self.client.loop_stop()
            self.client.disconnect()
            self.is_connected = False
        
        if self.db:
            self.db.close()


class MQTTServiceManager:
    """MQTT服务管理器 - 管理所有用户的MQTT连接（方案A：每个用户独立连接）"""
    
    def __init__(self):
        self.user_services: Dict[int, UserMQTTService] = {}
    
    def get_or_create_service(self, user_id: int) -> Optional[UserMQTTService]:
        """获取或创建用户的MQTT服务"""
        if user_id not in self.user_services:
            self.user_services[user_id] = UserMQTTService(user_id)
        return self.user_services[user_id]
    
    def start_user_service(self, user_id: int) -> bool:
        """启动指定用户的MQTT服务"""
        service = self.get_or_create_service(user_id)
        return service.start()
    
    def stop_user_service(self, user_id: int):
        """停止指定用户的MQTT服务"""
        if user_id in self.user_services:
            self.user_services[user_id].stop()
            del self.user_services[user_id]
    
    def restart_user_service(self, user_id: int) -> bool:
        """重启指定用户的MQTT服务"""
        self.stop_user_service(user_id)
        return self.start_user_service(user_id)
    
    def start_all_active_users(self):
        """启动所有有激活配置的用户的MQTT服务"""
        db = SessionLocal()
        try:
            from models.user import UserModel
            users = db.query(UserModel).filter(UserModel.is_active == True).all()
            
            for user in users:
                # 检查用户是否有激活的主题配置
                active_configs = topic_config_service.get_active_topic_configs(db, user_id=user.id)
                if active_configs:
                    logger.info(f"启动用户 {user.id} ({user.username}) 的MQTT服务...")
                    self.start_user_service(user.id)
        finally:
            db.close()
    
    def stop_all(self):
        """停止所有用户的MQTT服务"""
        for user_id in list(self.user_services.keys()):
            self.stop_user_service(user_id)
    
    def get_user_service(self, user_id: int) -> Optional[UserMQTTService]:
        """获取用户的MQTT服务（如果存在）"""
        return self.user_services.get(user_id)


# 全局MQTT服务管理器实例
_mqtt_service_manager: Optional[MQTTServiceManager] = None


def get_mqtt_service_manager() -> MQTTServiceManager:
    """获取MQTT服务管理器实例（单例模式）"""
    global _mqtt_service_manager
    if _mqtt_service_manager is None:
        _mqtt_service_manager = MQTTServiceManager()
    return _mqtt_service_manager


def start_all_user_mqtt_services():
    """启动所有有激活配置的用户的MQTT服务"""
    manager = get_mqtt_service_manager()
    manager.start_all_active_users()


def restart_all_user_mqtt_services():
    """重启所有用户的MQTT服务"""
    manager = get_mqtt_service_manager()
    manager.stop_all()
    manager.start_all_active_users()