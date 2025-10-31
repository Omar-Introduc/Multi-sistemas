"""
Modelo de datos para Validador
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Index
from pydantic import BaseModel, Field, validator
from typing import Optional, Literal
from .base import BaseModel


class ValidadorModel(BaseModel):
    """
    Modelo Pydantic para validaciones de Validador
    """
    id: Optional[int] = Field(None, description="ID único del validador")
    nombre: str = Field(..., min_length=1, max_length=100, description="Nombre del validador")
    version: str = Field(..., min_length=1, max_length=50, description="Versión del validador")
    estado: Literal['activo', 'inactivo', 'mantenimiento'] = Field('inactivo', description="Estado del validador")
    fecha_activacion: Optional[datetime] = Field(None, description="Fecha de activación")
    fecha_registro: Optional[datetime] = Field(None, description="Fecha de registro")
    fecha_actualizacion: Optional[datetime] = Field(None, description="Fecha de última actualización")

    @validator('nombre')
    def nombre_must_be_valid(cls, v):
        """Validar formato del nombre"""
        import re
        # Permitir letras, espacios, guiones y puntos
        if not re.match(r'^[a-zA-Z0-9\s\._-]+$', v):
            raise ValueError('El nombre contiene caracteres no válidos')
        return v.strip()

    @validator('version')
    def version_must_be_valid(cls, v):
        """Validar formato de versión (formato semántico recomendado)"""
        import re
        # Permitir formatos como 1.0.0, v1.0.0, 1.2.3-alpha
        if not re.match(r'^(v?\d+\.\d+\.\d+(?:-[a-zA-Z0-9-]+)?)$', v):
            raise ValueError('La versión debe tener un formato válido (ej: 1.0.0, v1.0.0, 1.2.3-alpha)')
        return v

    @validator('estado')
    def estado_must_be_valid(cls, v):
        """Validar estado"""
        estados_validos = ['activo', 'inactivo', 'mantenimiento']
        if v not in estados_validos:
            raise ValueError(f'El estado debe ser uno de: {estados_validos}')
        return v

    class Config:
        """Configuración del modelo Pydantic"""
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }
        schema_extra = {
            "example": {
                "nombre": "ValidadorDNIv2",
                "version": "2.1.0",
                "estado": "activo"
            }
        }


class Validador(BaseModel, Base):
    """
    Modelo SQLAlchemy para Validador
    """
    __tablename__ = "validadores"

    # Índices
    __table_args__ = (
        Index('idx_validador_nombre', 'nombre'),
        Index('idx_validador_version', 'version'),
        Index('idx_validador_estado', 'estado'),
        Index('idx_validador_nombre_version', 'nombre', 'version', unique=True),
        {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4'}
    )

    # Heredar id de BaseModel (ya definido en la clase padre)
    nombre = Column(String(100), nullable=False, comment="Nombre del validador")
    version = Column(String(50), nullable=False, comment="Versión del validador")
    estado = Column(Boolean, default=False, nullable=False, comment="Estado del validador (True=activo, False=inactivo)")
    fecha_activacion = Column(DateTime, nullable=True, comment="Fecha de activación")

    def __repr__(self) -> str:
        estado_str = "activo" if self.estado else "inactivo"
        return f"<Validador(id={self.id}, nombre='{self.nombre}', version='{self.version}', estado={estado_str})>"

    def to_dict(self) -> dict:
        """Convertir modelo a diccionario"""
        return {
            'id': self.id,
            'nombre': self.nombre,
            'version': self.version,
            'estado': self.estado,
            'fecha_activacion': self.fecha_activacion.isoformat() if self.fecha_activacion else None,
            'fecha_registro': self.fecha_registro.isoformat() if self.fecha_registro else None,
            'fecha_actualizacion': self.fecha_actualizacion.isoformat() if self.fecha_actualizacion else None
        }

    def activate(self):
        """Activar el validador"""
        self.estado = True
        self.fecha_activacion = datetime.utcnow()

    def deactivate(self):
        """Desactivar el validador"""
        self.estado = False

    def is_active(self) -> bool:
        """Verificar si el validador está activo"""
        return self.estado

    @classmethod
    def create_validador(cls, nombre: str, version: str, activa: bool = False):
        """Método de clase para crear un nuevo validador"""
        validador = cls(
            nombre=nombre,
            version=version,
            estado=activa
        )
        if activa:
            validador.fecha_activacion = datetime.utcnow()
        return validador

    def update_version(self, nueva_version: str):
        """Actualizar la versión del validador"""
        self.version = nueva_version
        # Si está activo, actualizar fecha de activación
        if self.estado:
            self.fecha_activacion = datetime.utcnow()
