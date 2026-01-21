"""
应用配置管理模块
使用pydantic-settings统一管理所有配置项
"""
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator
import os
from pathlib import Path
from typing import List


class Settings(BaseSettings):
    """应用配置类"""
    
    # 应用基础配置
    app_name: str = "MQTT IoT管理系统"
    app_version: str = "1.0.0"
    debug: bool = Field(default=False)
    api_prefix: str = "/api/v1"
    
    # 安全配置
    secret_key: str = Field(
        default="change-me-in-production-use-openssl-rand-hex-32",
        description="用于JWT签名的密钥，生产环境必须更改"
    )
    algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=30)
    
    # 数据库配置
    database_url: str = Field(
        default="sqlite:///./mqtt_iot.db",
        description="数据库连接URL（将在初始化时解析为项目根目录的绝对路径）"
    )
    
    @field_validator('database_url', mode='after')
    @classmethod
    def resolve_database_path(cls, v: str) -> str:
        """解析数据库路径，确保指向项目根目录"""
        if not v.startswith("sqlite:///"):
            return v
        
        # 移除 sqlite:/// 前缀
        path_part = v[10:]
        
        # 如果是绝对路径，直接返回
        if path_part.startswith("/"):
            return v
        
        # 获取项目根目录（backend目录的父目录）
        # 假设config.py在backend/core/目录下
        backend_dir = Path(__file__).parent.parent
        project_root = backend_dir.parent
        
        # 处理相对路径
        if path_part.startswith("./"):
            # 相对于项目根目录
            db_path = project_root / path_part[2:]
        elif path_part.startswith("../"):
            # 相对于backend目录的父目录（项目根目录）
            db_path = project_root / path_part[3:]
        else:
            # 直接是文件名，放在项目根目录
            db_path = project_root / path_part
        
        # 转换为绝对路径的SQLite URL
        abs_path = db_path.absolute()
        return f"sqlite:///{abs_path}"
    
    # MQTT默认配置
    mqtt_default_port: int = Field(default=1883)
    mqtt_default_timeout: int = Field(default=60)
    mqtt_keepalive: int = Field(default=60)
    
    # 日志配置
    log_level: str = Field(default="INFO")
    log_file: str = Field(default="logs/app.log")
    log_max_bytes: int = Field(default=10485760)  # 10MB
    log_backup_count: int = Field(default=5)
    
    # 服务器配置
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000)
    
    # CORS配置
    cors_origins: List[str] = Field(
        default=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173", "http://192.168.1.102:5173", "http://192.168.1.103:5173"],
        description="允许的前端源地址列表"
    )
    
    @field_validator('cors_origins', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        """解析CORS来源列表，支持字符串（逗号分隔）或列表"""
        # 如果值为 None，返回 None（让默认值生效）
        if v is None:
            return None
        
        # 如果是字符串
        if isinstance(v, str):
            # 处理空字符串，返回 None（让默认值生效）
            if not v.strip():
                return None
            # 处理逗号分隔的字符串
            origins = [origin.strip() for origin in v.split(',') if origin.strip()]
            return origins if origins else None
        
        # 如果已经是列表，直接返回
        if isinstance(v, list):
            return v if v else None
        
        # 如果是字节类型，先解码
        if isinstance(v, (bytes, bytearray)):
            try:
                v = v.decode('utf-8')
                if not v.strip():
                    return None
                origins = [origin.strip() for origin in v.split(',') if origin.strip()]
                return origins if origins else None
            except (UnicodeDecodeError, AttributeError):
                return None
        
        # 其他情况返回 None（让默认值生效）
        return None
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# 创建全局配置实例
settings = Settings()


def get_settings() -> Settings:
    """获取配置实例（用于依赖注入）"""
    return settings


def validate_settings():
    """验证关键配置是否正确"""
    errors = []
    
    # 检查SECRET_KEY是否为默认值（生产环境安全警告）
    if settings.secret_key == "change-me-in-production-use-openssl-rand-hex-32":
        if not settings.debug:
            errors.append(
                "警告: SECRET_KEY使用默认值，生产环境存在安全风险！"
                "请设置环境变量SECRET_KEY或使用openssl rand -hex 32生成"
            )
    
    # 检查日志目录是否存在
    log_dir = os.path.dirname(settings.log_file)
    if log_dir and not os.path.exists(log_dir):
        try:
            os.makedirs(log_dir, exist_ok=True)
        except Exception as e:
            errors.append(f"无法创建日志目录 {log_dir}: {e}")
    
    return errors