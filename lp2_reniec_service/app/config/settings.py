"""
Configuración principal de la aplicación
"""

from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Configuraciones de la aplicación usando Pydantic"""
    
    # Configuración básica
    app_name: str = "LP2 RENIEC Service"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Base de datos
    database_url: str
    database_host: str = "localhost"
    database_port: int = 3306
    database_user: str = "root"
    database_password: str = ""
    database_name: str = "reniec_db"
    
    # RabbitMQ
    rabbitmq_url: str
    rabbitmq_host: str = "localhost"
    rabbitmq_port: int = 5672
    rabbitmq_user: str = "guest"
    rabbitmq_password: str = "guest"
    rabbitmq_queue: str = "reniec_queue"
    
    # Redis
    redis_url: str
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: str = ""
    
    # Seguridad
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # CORS
    allowed_hosts: List[str] = ["http://localhost:3000"]
    
    # RENIEC API Externa
    reniec_api_url: str
    reniec_api_key: str
    reniec_timeout: int = 30
    
    # Email
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    email_from: str = "noreply@reniec.gob.pe"
    
    # Logging
    log_level: str = "INFO"
    log_retention_days: int = 30
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Instancia global de configuraciones
settings = Settings()


# Configuraciones de validación
DATABASE_CONFIG = {
    "echo": settings.debug,
    "pool_pre_ping": True,
    "pool_recycle": 3600,
}

RABBITMQ_CONFIG = {
    "connection_attempts": 3,
    "retry_delay": 5,
    "heartbeat": 60,
}

REDIS_CONFIG = {
    "decode_responses": True,
    "health_check_interval": 30,
}