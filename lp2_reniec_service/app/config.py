"""
Configuración avanzada del sistema LP2 RENIEC Service
Incluye configuraciones para MySQL, RabbitMQ, Redis, Logging y más
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional, Dict, Any
import os
from functools import lru_cache


class DatabaseConfig:
    """Configuración de base de datos MySQL"""
    
    def __init__(self, settings: 'Settings'):
        self.url = settings.database_url
        self.host = settings.database_host
        self.port = settings.database_port
        self.user = settings.database_user
        self.password = settings.database_password
        self.name = settings.database_name
        self.echo = settings.debug
        self.pool_size = 10
        self.max_overflow = 20
        self.pool_timeout = 30
        self.pool_recycle = 3600
        self.pool_pre_ping = True


class RabbitMQConfig:
    """Configuración de RabbitMQ"""
    
    def __init__(self, settings: 'Settings'):
        self.url = settings.rabbitmq_url
        self.host = settings.rabbitmq_host
        self.port = settings.rabbitmq_port
        self.user = settings.rabbitmq_user
        self.password = settings.rabbitmq_password
        self.queue = settings.rabbitmq_queue
        self.connection_attempts = 3
        self.retry_delay = 5
        self.heartbeat = 60
        self.prefetch_count = 10


class RedisConfig:
    """Configuración de Redis"""
    
    def __init__(self, settings: 'Settings'):
        self.url = settings.redis_url
        self.host = settings.redis_host
        self.port = settings.redis_port
        self.db = settings.redis_db
        self.password = settings.redis_password
        self.decode_responses = True
        self.health_check_interval = 30
        self.socket_timeout = 5
        self.socket_connect_timeout = 5


class LoggingConfig:
    """Configuración avanzada de logging"""
    
    def __init__(self, settings: 'Settings'):
        self.level = settings.log_level
        self.retention_days = settings.log_retention_days
        self.format = (
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level>"
        )
        self.rotation = "100 MB"
        self.retention = f"{settings.log_retention_days} days"
        self.compression = "gz"
        self.encoding = "utf8"
        self.backup_count = 5


class SecurityConfig:
    """Configuración de seguridad"""
    
    def __init__(self, settings: 'Settings'):
        self.secret_key = settings.secret_key
        self.algorithm = settings.algorithm
        self.access_token_expire_minutes = settings.access_token_expire_minutes
        self.allowed_hosts = settings.allowed_hosts
        self.cors_origins = settings.allowed_hosts
        self.cors_methods = ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"]
        self.cors_headers = ["*"]
        self.rate_limit_calls = 100
        self.rate_limit_window = 60  # segundos


class RENIECConfig:
    """Configuración específica de RENIEC"""
    
    def __init__(self, settings: 'Settings'):
        self.api_url = settings.reniec_api_url
        self.api_key = settings.reniec_api_key
        self.timeout = settings.reniec_timeout
        self.retry_attempts = 3
        self.retry_delay = 1


class EmailConfig:
    """Configuración de email"""
    
    def __init__(self, settings: 'Settings'):
        self.smtp_server = settings.smtp_server
        self.smtp_port = settings.smtp_port
        self.username = settings.smtp_username
        self.password = settings.smtp_password
        self.from_email = settings.email_from
        self.use_tls = True
        self.use_ssl = False


class Settings(BaseSettings):
    """Configuraciones principales de la aplicación"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )
    
    # === CONFIGURACIÓN BÁSICA ===
    app_name: str = "LP2 RENIEC Service"
    app_version: str = "2.0.0"
    debug: bool = False
    environment: str = "production"
    host: str = "0.0.0.0"
    port: int = 8000
    
    # === BASE DE DATOS MYSQL ===
    database_url: str = "mysql+pymysql://root:@localhost/reniec_db"
    database_host: str = "localhost"
    database_port: int = 3306
    database_user: str = "root"
    database_password: str = ""
    database_name: str = "reniec_db"
    
    # === RABBITMQ ===
    rabbitmq_url: str = "amqp://guest:guest@localhost:5672/"
    rabbitmq_host: str = "localhost"
    rabbitmq_port: int = 5672
    rabbitmq_user: str = "guest"
    rabbitmq_password: str = "guest"
    rabbitmq_queue: str = "reniec_queue"
    
    # === REDIS ===
    redis_url: str = "redis://localhost:6379/0"
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: str = ""
    
    # === SEGURIDAD ===
    secret_key: str = "tu-clave-secreta-super-segura-aqui"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # === CORS Y HOSTS PERMITIDOS ===
    allowed_hosts: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    # === RENIEC API EXTERNA ===
    reniec_api_url: str = "https://api.reniec.gob.pe"
    reniec_api_key: str = ""
    reniec_timeout: int = 30
    
    # === EMAIL ===
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    email_from: str = "noreply@reniec.gob.pe"
    
    # === LOGGING ===
    log_level: str = "INFO"
    log_retention_days: int = 30
    log_file_path: str = "logs/app.log"
    log_error_file_path: str = "logs/error.log"
    
    # === RATE LIMITING ===
    rate_limit_enabled: bool = True
    rate_limit_calls: int = 100
    rate_limit_window: int = 60  # segundos
    rate_limit_storage_url: str = "redis://localhost:6379/1"
    
    # === MIDDLEWARE ===
    enable_cors: bool = True
    enable_request_logging: bool = True
    enable_rate_limiting: bool = True
    enable_security_headers: bool = True
    
    # === HEALTH CHECKS ===
    health_check_enabled: bool = True
    health_check_interval: int = 30
    health_check_timeout: int = 5
    
    # === CACHÉ ===
    cache_enabled: bool = True
    cache_ttl: int = 300  # 5 minutos
    cache_max_size: int = 1000
    
    # === MONITOREO ===
    monitoring_enabled: bool = True
    metrics_enabled: bool = True
    tracing_enabled: bool = False
    
    # === VALIDACIÓN ===
    enable_input_validation: bool = True
    enable_output_validation: bool = False
    strict_validation: bool = False


@lru_cache()
def get_settings() -> Settings:
    """Obtener instancia cached de configuraciones"""
    return Settings()


# Instancia global de configuraciones
settings = get_settings()

# Crear instancias de configuración especializada
database_config = DatabaseConfig(settings)
rabbitmq_config = RabbitMQConfig(settings)
redis_config = RedisConfig(settings)
logging_config = LoggingConfig(settings)
security_config = SecurityConfig(settings)
reniec_config = RENIECConfig(settings)
email_config = EmailConfig(settings)

# Exportar configuraciones
__all__ = [
    "settings",
    "database_config",
    "rabbitmq_config",
    "redis_config", 
    "logging_config",
    "security_config",
    "reniec_config",
    "email_config",
    "Settings"
]