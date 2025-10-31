"""
Modelos de base de datos para el sistema RENIEC
"""

from sqlalchemy import Column, Integer, String, Date, Boolean, DateTime, Text, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.types import JSON
from app.config.database import Base
import uuid


class Ciudadano(Base):
    """
    Modelo para ciudadano
    """
    __tablename__ = "ciudadanos"
    
    id = Column(Integer, primary_key=True, index=True)
    documento_identidad = Column(String(8), unique=True, index=True, nullable=False)
    nombres = Column(String(255), nullable=False)
    apellidos = Column(String(255), nullable=False)
    fecha_nacimiento = Column(Date, nullable=False)
    lugar_nacimiento = Column(String(255), nullable=False)
    genero = Column(String(1), nullable=False)  # M/F
    estado_civil = Column(String(20), nullable=True)
    direccion = Column(String(500), nullable=True)
    telefono = Column(String(15), nullable=True)
    email = Column(String(255), nullable=True)
    
    # Campos de auditoría
    activo = Column(Boolean, default=True)
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_actualizacion = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relaciones
    documentos = relationship("Documento", back_populates="ciudadano")


class TipoDocumento(Base):
    """
    Modelo para tipos de documentos
    """
    __tablename__ = "tipos_documento"
    
    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(20), unique=True, nullable=False)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(Text, nullable=True)
    requiere_renovacion = Column(Boolean, default=False)
    vigencia_meses = Column(Integer, nullable=True)
    
    # Campos de auditoría
    activo = Column(Boolean, default=True)
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relaciones
    documentos = relationship("Documento", back_populates="tipo_documento")


class Documento(Base):
    """
    Modelo para documentos
    """
    __tablename__ = "documentos"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_documento = Column(String(20), unique=True, index=True, nullable=False)
    ciudadano_id = Column(Integer, ForeignKey("ciudadanos.id"), nullable=False)
    tipo_documento_id = Column(Integer, ForeignKey("tipos_documento.id"), nullable=False)
    
    # Datos del documento
    fecha_emision = Column(Date, nullable=False)
    fecha_vencimiento = Column(Date, nullable=True)
    estado = Column(String(20), default="vigente")  # vigente, vencido, perdido, robado
    
    # Archivos y metadatos
    archivo_documento = Column(String(500), nullable=True)
    metadatos = Column(JSON, nullable=True)
    
    # Campos de auditoría
    activo = Column(Boolean, default=True)
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_actualizacion = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relaciones
    ciudadano = relationship("Ciudadano", back_populates="documentos")
    tipo_documento = relationship("TipoDocumento", back_populates="documentos")
    solicitudes = relationship("Solicitud", back_populates="documento")


class Solicitud(Base):
    """
    Modelo para solicitudes de documentos
    """
    __tablename__ = "solicitudes"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_solicitud = Column(String(20), unique=True, index=True, nullable=False)
    ciudadano_id = Column(Integer, ForeignKey("ciudadanos.id"), nullable=False)
    documento_id = Column(Integer, ForeignKey("documentos.id"), nullable=True)
    
    # Datos de la solicitud
    tipo_solicitud = Column(String(50), nullable=False)  # primera_vez, renovacion, duplicado
    motivo = Column(String(255), nullable=True)
    observaciones = Column(Text, nullable=True)
    estado = Column(String(20), default="pendiente")  # pendiente, en_proceso, aprobado, rechazado, entregado
    
    # Campos de auditoría
    fecha_solicitud = Column(DateTime(timezone=True), server_default=func.now())
    fecha_procesamiento = Column(DateTime(timezone=True), nullable=True)
    fecha_entrega = Column(DateTime(timezone=True), nullable=True)
    
    # Relaciones
    ciudadano = relationship("Ciudadano")
    documento = relationship("Documento", back_populates="solicitudes")
    eventos = relationship("EventoSolicitud", back_populates="solicitud")


class EventoSolicitud(Base):
    """
    Modelo para eventos/historial de solicitudes
    """
    __tablename__ = "eventos_solicitud"
    
    id = Column(Integer, primary_key=True, index=True)
    solicitud_id = Column(Integer, ForeignKey("solicitudes.id"), nullable=False)
    evento = Column(String(100), nullable=False)
    descripcion = Column(Text, nullable=True)
    usuario = Column(String(100), nullable=True)
    
    # Campos de auditoría
    fecha_evento = Column(DateTime(timezone=True), server_default=func.now())


class SesionUsuario(Base):
    """
    Modelo para sesiones de usuario
    """
    __tablename__ = "sesiones_usuario"
    
    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, nullable=False)
    token_sesion = Column(String(255), unique=True, index=True, nullable=False)
    fecha_expiracion = Column(DateTime(timezone=True), nullable=False)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    
    # Campos de auditoría
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    activo = Column(Boolean, default=True)