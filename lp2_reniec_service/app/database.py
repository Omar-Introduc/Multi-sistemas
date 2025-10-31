"""
Configuración avanzada de base de datos MySQL con SQLAlchemy
Incluye SessionLocal, engine, base y funciones de utilidad
"""

from sqlalchemy import create_engine, event, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool, StaticPool
from sqlalchemy.exc import (
    OperationalError, 
    DisconnectionError, 
    TimeoutError,
    SQLAlchemyError
)
from sqlalchemy.engine import Engine
from sqlalchemy import pool
from contextlib import contextmanager
from typing import Generator, Optional, Dict, Any
from loguru import logger
import time
import traceback

from app.config import settings, database_config


# === ENGINE DE SQLALCHEMY ===
engine = create_engine(
    database_config.url,
    # Pool configuration
    poolclass=QueuePool,
    pool_size=database_config.pool_size,
    max_overflow=database_config.max_overflow,
    pool_timeout=database_config.pool_timeout,
    pool_recycle=database_config.pool_recycle,
    pool_pre_ping=database_config.pool_pre_ping,
    
    # MySQL specific configuration
    connect_args={
        "charset": "utf8mb4",
        "collation": "utf8mb4_unicode_ci",
        "connect_timeout": 60,
        "read_timeout": 60,
        "write_timeout": 60,
        "autocommit": False,
        "connection_timeout": 60,
        "pool_pre_ping": True,
        "retry_on_timeout": True,
    },
    
    # Echo configuration
    echo=database_config.echo,
    
    # Future configuration
    future=True,
    #isolation_level="READ COMMITTED"  # Descomenta si necesitas control de aislamiento
)


# === EVENT LISTENERS PARA EL ENGINE ===
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Configurar pragmas de MySQL al establecer conexión"""
    try:
        cursor = dbapi_connection.cursor()
        cursor.execute("SET time_zone = '+00:00'")
        cursor.execute("SET sql_mode = 'STRICT_TRANS_TABLES,NO_ZERO_DATE,NO_ZERO_IN_DATE,ERROR_FOR_DIVISION_BY_ZERO'")
        cursor.execute("SET character_set_client = utf8mb4")
        cursor.execute("SET character_set_connection = utf8mb4")
        cursor.execute("SET character_set_results = utf8mb4")
        cursor.close()
        logger.debug("✅ Pragma de MySQL configurados correctamente")
    except Exception as e:
        logger.warning(f"⚠️  No se pudieron configurar pragmas MySQL: {e}")


@event.listens_for(engine, "checkout")
def ping_connection(dbapi_connection, connection_record, connection_proxy):
    """Verificar conexión antes de usar"""
    try:
        # Ejecutar SELECT 1 para verificar que la conexión está viva
        dbapi_connection.execute(text("SELECT 1"))
        logger.debug("🔍 Conexión verificada correctamente")
    except Exception as e:
        logger.warning(f"⚠️  Error al verificar conexión: {e}")
        raise DisconnectionError("Connection is invalid")


# === SESSION LOCAL ===
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False,
    future=True
)


# === BASE PARA MODELOS ===
Base = declarative_base()


# === CLASE DE BASE DE DATOS AVANZADA ===
class DatabaseManager:
    """Gestor avanzado de base de datos con pool de conexiones"""
    
    def __init__(self):
        self.engine = engine
        self.session_factory = SessionLocal
        self.is_initialized = False
        self._start_time = None
        
    def initialize(self) -> bool:
        """Inicializar la base de datos"""
        try:
            logger.info("🚀 Inicializando base de datos...")
            
            # Probar conexión
            if self.test_connection():
                # Crear todas las tablas
                Base.metadata.create_all(bind=self.engine)
                self.is_initialized = True
                self._start_time = time.time()
                logger.info("✅ Base de datos inicializada correctamente")
                return True
            else:
                logger.error("❌ No se pudo inicializar la base de datos")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error al inicializar base de datos: {e}")
            logger.error(traceback.format_exc())
            return False
    
    def get_session(self) -> Generator[Session, None, None]:
        """Obtener sesión de base de datos con manejo de errores"""
        session = self.session_factory()
        try:
            yield session
            if not self.is_initialized:
                session.rollback()
                logger.warning("⚠️  Transacción rollback debido a base de datos no inicializada")
        except Exception as e:
            session.rollback()
            logger.error(f"❌ Error en sesión de base de datos: {e}")
            logger.error(traceback.format_exc())
            raise
        finally:
            session.close()
    
    @contextmanager
    def get_db_context(self) -> Generator[Session, None, None]:
        """Context manager para sesiones de base de datos"""
        with self.get_session() as session:
            try:
                yield session
                session.commit()
            except Exception as e:
                session.rollback()
                logger.error(f"❌ Error en contexto de base de datos: {e}")
                raise
            finally:
                session.close()
    
    def test_connection(self) -> bool:
        """Probar la conexión a la base de datos"""
        try:
            with self.engine.connect() as connection:
                result = connection.execute(text("SELECT 1 as test"))
                row = result.fetchone()
                if row and row.test == 1:
                    logger.info("✅ Conexión a MySQL establecida correctamente")
                    return True
                else:
                    logger.error("❌ Prueba de conexión falló")
                    return False
        except OperationalError as e:
            logger.error(f"❌ Error operacional de MySQL: {e}")
            return False
        except TimeoutError as e:
            logger.error(f"❌ Timeout de conexión MySQL: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Error inesperado en MySQL: {e}")
            logger.error(traceback.format_exc())
            return False
    
    def get_database_info(self) -> Dict[str, Any]:
        """Obtener información de la base de datos"""
        try:
            with self.engine.connect() as connection:
                # Versión de MySQL
                version_result = connection.execute(text("SELECT VERSION() as version"))
                version = version_result.fetchone().version
                
                # Información de la base de datos
                db_result = connection.execute(text("SELECT DATABASE() as db_name"))
                db_name = db_result.fetchone().db_name
                
                # Configuración actual
                config_result = connection.execute(text("SHOW VARIABLES LIKE 'max_connections'"))
                max_connections = config_result.fetchone()
                
                return {
                    "version": version,
                    "database": db_name,
                    "max_connections": max_connections[1] if max_connections else "N/A",
                    "is_initialized": self.is_initialized,
                    "uptime": time.time() - self._start_time if self._start_time else 0
                }
        except Exception as e:
            logger.error(f"❌ Error al obtener info de base de datos: {e}")
            return {"error": str(e)}
    
    def close_connections(self):
        """Cerrar todas las conexiones de la base de datos"""
        try:
            self.engine.dispose()
            logger.info("✅ Conexiones de base de datos cerradas correctamente")
        except Exception as e:
            logger.error(f"❌ Error al cerrar conexiones: {e}")


# === INSTANCIA GLOBAL ===
db_manager = DatabaseManager()


# === FUNCIONES DE UTILIDAD ===
def get_db() -> Generator[Session, None, None]:
    """
    Dependencia de FastAPI para obtener sesión de base de datos
    """
    with db_manager.get_db_context() as db:
        yield db


def init_db() -> bool:
    """Inicializar base de datos"""
    return db_manager.initialize()


def close_db():
    """Cerrar base de datos"""
    db_manager.close_connections()


def get_db_info() -> Dict[str, Any]:
    """Obtener información de la base de datos"""
    return db_manager.get_database_info()


# === DECORADORES PARA TRANSACCIONES ===
def database_transaction(func):
    """Decorador para ejecutar funciones en una transacción"""
    def wrapper(*args, **kwargs):
        with db_manager.get_db_context() as db:
            try:
                result = func(db, *args, **kwargs)
                db.commit()
                return result
            except Exception as e:
                db.rollback()
                logger.error(f"❌ Error en transacción: {e}")
                raise
    return wrapper


def read_only_transaction(func):
    """Decorador para transacciones de solo lectura"""
    def wrapper(*args, **kwargs):
        with db_manager.get_db_context() as db:
            # Configurar sesión como read-only
            db.execute(text("SET TRANSACTION READ ONLY"))
            db.commit()
            try:
                result = func(db, *args, **kwargs)
                return result
            except Exception as e:
                logger.error(f"❌ Error en transacción de solo lectura: {e}")
                raise
    return wrapper


# === FUNCIONES DE MIGRACIÓN ===
def create_tables():
    """Crear todas las tablas"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Tablas creadas correctamente")
        return True
    except Exception as e:
        logger.error(f"❌ Error al crear tablas: {e}")
        return False


def drop_tables():
    """Eliminar todas las tablas (solo en desarrollo)"""
    if settings.environment != "development":
        logger.error("❌ No se pueden eliminar tablas en producción")
        return False
    
    try:
        Base.metadata.drop_all(bind=engine)
        logger.info("✅ Tablas eliminadas correctamente")
        return True
    except Exception as e:
        logger.error(f"❌ Error al eliminar tablas: {e}")
        return False


# === EXPORTACIONES ===
__all__ = [
    "engine",
    "SessionLocal", 
    "Base",
    "db_manager",
    "DatabaseManager",
    "get_db",
    "init_db",
    "close_db",
    "get_db_info",
    "database_transaction",
    "read_only_transaction",
    "create_tables",
    "drop_tables"
]