"""
Base para modelos SQLAlchemy
Importa Base desde app.config.database
"""
from datetime import datetime
from sqlalchemy import Column, Integer, DateTime
from app.config.database import Base


class BaseModel(Base):
    """
    Clase base para todos los modelos con campos comunes
    """
    __abstract__ = True

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    fecha_registro = Column(DateTime, default=datetime.utcnow, nullable=False)
    fecha_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
