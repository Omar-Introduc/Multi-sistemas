"""
Modelo de datos para Ciudadano
"""
from datetime import datetime, date
from sqlalchemy import Column, Integer, String, DateTime, Date, Boolean, Index
from sqlalchemy.orm import relationship
from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional
from .base import BaseModel


class CiudadanoModel(BaseModel):
    """
    Modelo Pydantic para validaciones de Ciudadano
    """
    id: Optional[int] = Field(None, description="ID único del ciudadano")
    dni: str = Field(..., min_length=8, max_length=8, description="Documento Nacional de Identidad")
    nombres: str = Field(..., min_length=1, max_length=100, description="Nombres del ciudadano")
    apellidos: str = Field(..., min_length=1, max_length=100, description="Apellidos del ciudadano")
    fecha_nacimiento: date = Field(..., description="Fecha de nacimiento")
    estado_civil: str = Field(..., min_length=1, max_length=50, description="Estado civil")
    direccion: str = Field(..., min_length=1, max_length=255, description="Dirección completa")
    telefono: str = Field(..., min_length=9, max_length=15, description="Número de teléfono")
    email: EmailStr = Field(..., description="Correo electrónico")
    estado: bool = Field(True, description="Estado del registro (activo/inactivo)")
    fecha_registro: Optional[datetime] = Field(None, description="Fecha de registro")
    fecha_actualizacion: Optional[datetime] = Field(None, description="Fecha de última actualización")

    @validator('dni')
    def dni_must_be_numeric(cls, v):
        """Validar que el DNI sea numérico"""
        if not v.isdigit():
            raise ValueError('El DNI debe contener solo números')
        return v

    @validator('telefono')
    def telefono_must_be_valid(cls, v):
        """Validar formato de teléfono"""
        if not v.isdigit():
            raise ValueError('El teléfono debe contener solo números')
        return v

    @validator('fecha_nacimiento')
    def fecha_nacimiento_must_be_past(cls, v):
        """Validar que la fecha de nacimiento sea en el pasado"""
        if v >= date.today():
            raise ValueError('La fecha de nacimiento debe ser en el pasado')
        return v

    class Config:
        """Configuración del modelo Pydantic"""
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None,
            date: lambda v: v.isoformat() if v else None
        }


class Ciudadano(BaseModel, Base):
    """
    Modelo SQLAlchemy para Ciudadano
    """
    __tablename__ = "ciudadanos"

    # Índices únicos y compuestos
    __table_args__ = (
        Index('idx_ciudadano_dni', 'dni', unique=True),
        Index('idx_ciudadano_email', 'email'),
        Index('idx_ciudadano_estado', 'estado'),
        {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4'}
    )

    # Heredar id de BaseModel (ya definido en la clase padre)
    dni = Column(String(8), nullable=False, comment="Documento Nacional de Identidad")
    nombres = Column(String(100), nullable=False, comment="Nombres del ciudadano")
    apellidos = Column(String(100), nullable=False, comment="Apellidos del ciudadano")
    fecha_nacimiento = Column(Date, nullable=False, comment="Fecha de nacimiento")
    estado_civil = Column(String(50), nullable=False, comment="Estado civil")
    direccion = Column(String(255), nullable=False, comment="Dirección completa")
    telefono = Column(String(15), nullable=False, comment="Número de teléfono")
    email = Column(String(255), nullable=False, unique=True, comment="Correo electrónico")
    estado = Column(Boolean, default=True, nullable=False, comment="Estado del registro")

    # Relaciones
    sesiones = relationship(
        "ReniecSession",
        back_populates="ciudadano",
        cascade="all, delete-orphan",
        lazy="select"
    )

    def __repr__(self) -> str:
        return f"<Ciudadano(id={self.id}, dni='{self.dni}', nombres='{self.nombres}', apellidos='{self.apellidos}')>"

    def to_dict(self) -> dict:
        """Convertir modelo a diccionario"""
        return {
            'id': self.id,
            'dni': self.dni,
            'nombres': self.nombres,
            'apellidos': self.apellidos,
            'fecha_nacimiento': self.fecha_nacimiento.isoformat() if self.fecha_nacimiento else None,
            'estado_civil': self.estado_civil,
            'direccion': self.direccion,
            'telefono': self.telefono,
            'email': self.email,
            'estado': self.estado,
            'fecha_registro': self.fecha_registro.isoformat() if self.fecha_registro else None,
            'fecha_actualizacion': self.fecha_actualizacion.isoformat() if self.fecha_actualizacion else None
        }
