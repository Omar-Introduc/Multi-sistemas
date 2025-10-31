"""
Modelo de datos para ReniecSession
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Index, Text
from sqlalchemy.orm import relationship
from pydantic import BaseModel, Field, validator
from typing import Optional
from .base import BaseModel


class ReniecSessionModel(BaseModel):
    """
    Modelo Pydantic para validaciones de ReniecSession
    """
    id: Optional[int] = Field(None, description="ID único de la sesión")
    session_id: str = Field(..., min_length=10, max_length=255, description="ID único de la sesión")
    dni: str = Field(..., min_length=8, max_length=8, description="DNI del ciudadano")
    timestamp: datetime = Field(..., description="Timestamp de la sesión")
    estado: bool = Field(True, description="Estado de la sesión")
    ip_address: str = Field(..., min_length=7, max_length=45, description="Dirección IP")
    user_agent: str = Field(..., max_length=500, description="User agent del navegador")
    fecha_registro: Optional[datetime] = Field(None, description="Fecha de registro")
    fecha_actualizacion: Optional[datetime] = Field(None, description="Fecha de última actualización")

    @validator('dni')
    def dni_must_be_numeric(cls, v):
        """Validar que el DNI sea numérico"""
        if not v.isdigit():
            raise ValueError('El DNI debe contener solo números')
        return v

    @validator('session_id')
    def session_id_must_be_valid(cls, v):
        """Validar formato de session_id"""
        # Permitir caracteres alfanuméricos, guiones y guiones bajos
        import re
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('El session_id debe contener solo caracteres alfanuméricos, guiones y guiones bajos')
        return v

    @validator('ip_address')
    def ip_address_must_be_valid(cls, v):
        """Validar formato de IP"""
        import ipaddress
        try:
            ipaddress.ip_address(v)
        except ValueError:
            raise ValueError('La dirección IP no es válida')
        return v

    class Config:
        """Configuración del modelo Pydantic"""
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class ReniecSession(BaseModel, Base):
    """
    Modelo SQLAlchemy para ReniecSession
    """
    __tablename__ = "reniec_sessions"

    # Índices
    __table_args__ = (
        Index('idx_reniec_session_id', 'session_id', unique=True),
        Index('idx_reniec_session_dni', 'dni'),
        Index('idx_reniec_session_timestamp', 'timestamp'),
        Index('idx_reniec_session_estado', 'estado'),
        Index('idx_reniec_session_ip', 'ip_address'),
        {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4'}
    )

    # Heredar id de BaseModel (ya definido en la clase padre)
    session_id = Column(String(255), nullable=False, unique=True, comment="ID único de la sesión")
    dni = Column(String(8), nullable=False, comment="DNI del ciudadano")
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow, comment="Timestamp de la sesión")
    estado = Column(Boolean, default=True, nullable=False, comment="Estado de la sesión")
    ip_address = Column(String(45), nullable=False, comment="Dirección IP (IPv4 o IPv6)")
    user_agent = Column(Text, nullable=False, comment="User agent del navegador")

    # Claves foráneas
    ciudadano_id = Column(Integer, ForeignKey('ciudadanos.id', ondelete='CASCADE'), nullable=False, comment="ID del ciudadano")

    # Relaciones
    ciudadano = relationship(
        "Ciudadano",
        back_populates="sesiones",
        lazy="select"
    )

    def __repr__(self) -> str:
        return f"<ReniecSession(id={self.id}, session_id='{self.session_id}', dni='{self.dni}', estado={self.estado})>"

    def to_dict(self) -> dict:
        """Convertir modelo a diccionario"""
        return {
            'id': self.id,
            'session_id': self.session_id,
            'dni': self.dni,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'estado': self.estado,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'ciudadano_id': self.ciudadano_id,
            'fecha_registro': self.fecha_registro.isoformat() if self.fecha_registro else None,
            'fecha_actualizacion': self.fecha_actualizacion.isoformat() if self.fecha_actualizacion else None
        }

    @classmethod
    def create_expired_session(cls, session_id: str, dni: str, ip_address: str, user_agent: str, ciudadano_id: int):
        """Método de clase para crear una sesión expirada"""
        return cls(
            session_id=session_id,
            dni=dni,
            ip_address=ip_address,
            user_agent=user_agent,
            ciudadano_id=ciudadano_id,
            timestamp=datetime.utcnow(),
            estado=False
        )
