"""
Configuración de la base de datos MySQL con SQLAlchemy
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy.exc import OperationalError
from loguru import logger

from app.config.settings import settings, DATABASE_CONFIG


# Crear engine de SQLAlchemy
engine = create_engine(
    settings.database_url,
    **DATABASE_CONFIG,
    poolclass=StaticPool,
    connect_args={
        "check_same_thread": False,
        "charset": "utf8mb4",
        "collation": "utf8mb4_unicode_ci"
    }
)

# Crear SessionLocal
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base para modelos
Base = declarative_base()


def get_db():
    """
    Generador de sesiones de base de datos
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Error en la sesión de base de datos: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def test_database_connection():
    """
    Probar la conexión a la base de datos
    """
    try:
        with engine.connect() as connection:
            connection.execute("SELECT 1")
        logger.info("✅ Conexión a la base de datos establecida correctamente")
        return True
    except OperationalError as e:
        logger.error(f"❌ Error de conexión a la base de datos: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Error inesperado en la base de datos: {e}")
        return False


def close_database_connections():
    """
    Cerrar todas las conexiones de la base de datos
    """
    try:
        engine.dispose()
        logger.info("✅ Conexiones de base de datos cerradas")
    except Exception as e:
        logger.error(f"❌ Error al cerrar conexiones: {e}")