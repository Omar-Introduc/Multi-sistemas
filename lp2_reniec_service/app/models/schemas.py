"""
Esquemas Pydantic para validación de datos
"""

from pydantic import BaseModel, EmailStr, validator, Field
from typing import Optional, List
from datetime import date, datetime
from enum import Enum


class EstadoCivil(str, Enum):
    """Estados civiles disponibles"""
    SOLTERO = "soltero"
    CASADO = "casado"
    VIUDO = "viudo"
    DIVORCIADO = "divorciado"
    CONVIVIENTE = "conviviente"


class Genero(str, Enum):
    """Géneros disponibles"""
    MASCULINO = "M"
    FEMENINO = "F"


class EstadoDocumento(str, Enum):
    """Estados de documentos"""
    VIGENTE = "vigente"
    VENCIDO = "vencido"
    PERDIDO = "perdido"
    ROBADO = "robado"
    ANULADO = "anulado"


class TipoSolicitud(str, Enum):
    """Tipos de solicitudes"""
    PRIMERA_VEZ = "primera_vez"
    RENOVACION = "renovacion"
    DUPLICADO = "duplicado"
    ACTUALIZACION = "actualizacion"


class EstadoSolicitud(str, Enum):
    """Estados de solicitudes"""
    PENDIENTE = "pendiente"
    EN_PROCESO = "en_proceso"
    APROBADO = "aprobado"
    RECHAZADO = "rechazado"
    ENTREGADO = "entregado"


# ==================== CIUDADANOS ====================

class CiudadanoBase(BaseModel):
    """Esquema base para ciudadano"""
    documento_identidad: str = Field(..., description="Documento de identidad (DNI)", min_length=8, max_length=8)
    nombres: str = Field(..., description="Nombres", min_length=1, max_length=255)
    apellidos: str = Field(..., description="Apellidos", min_length=1, max_length=255)
    fecha_nacimiento: date = Field(..., description="Fecha de nacimiento")
    lugar_nacimiento: str = Field(..., description="Lugar de nacimiento", min_length=1, max_length=255)
    genero: Genero = Field(..., description="Género")
    estado_civil: Optional[EstadoCivil] = Field(None, description="Estado civil")
    direccion: Optional[str] = Field(None, description="Dirección", max_length=500)
    telefono: Optional[str] = Field(None, description="Teléfono", max_length=15)
    email: Optional[EmailStr] = Field(None, description="Email")


class CiudadanoCreate(CiudadanoBase):
    """Esquema para crear ciudadano"""
    pass


class CiudadanoUpdate(BaseModel):
    """Esquema para actualizar ciudadano"""
    nombres: Optional[str] = Field(None, min_length=1, max_length=255)
    apellidos: Optional[str] = Field(None, min_length=1, max_length=255)
    fecha_nacimiento: Optional[date] = None
    lugar_nacimiento: Optional[str] = Field(None, min_length=1, max_length=255)
    genero: Optional[Genero] = None
    estado_civil: Optional[EstadoCivil] = None
    direccion: Optional[str] = Field(None, max_length=500)
    telefono: Optional[str] = Field(None, max_length=15)
    email: Optional[EmailStr] = None
    activo: Optional[bool] = None


class CiudadanoResponse(CiudadanoBase):
    """Esquema de respuesta para ciudadano"""
    id: int
    activo: bool
    fecha_creacion: datetime
    fecha_actualizacion: Optional[datetime]

    class Config:
        from_attributes = True


# ==================== DOCUMENTOS ====================

class TipoDocumentoBase(BaseModel):
    """Esquema base para tipo de documento"""
    codigo: str = Field(..., description="Código del tipo de documento", min_length=1, max_length=20)
    nombre: str = Field(..., description="Nombre del tipo de documento", min_length=1, max_length=100)
    descripcion: Optional[str] = Field(None, description="Descripción", max_length=1000)
    requiere_renovacion: bool = Field(False, description="Requiere renovación")
    vigencia_meses: Optional[int] = Field(None, description="Vigencia en meses", ge=1)


class TipoDocumentoCreate(TipoDocumentoBase):
    """Esquema para crear tipo de documento"""
    pass


class TipoDocumentoResponse(TipoDocumentoBase):
    """Esquema de respuesta para tipo de documento"""
    id: int
    activo: bool
    fecha_creacion: datetime

    class Config:
        from_attributes = True


class DocumentoBase(BaseModel):
    """Esquema base para documento"""
    numero_documento: str = Field(..., description="Número de documento", min_length=1, max_length=20)
    ciudadano_id: int = Field(..., description="ID del ciudadano", gt=0)
    tipo_documento_id: int = Field(..., description="ID del tipo de documento", gt=0)
    fecha_emision: date = Field(..., description="Fecha de emisión")
    fecha_vencimiento: Optional[date] = Field(None, description="Fecha de vencimiento")
    estado: EstadoDocumento = Field(EstadoDocumento.VIGENTE, description="Estado del documento")
    archivo_documento: Optional[str] = Field(None, description="Ruta del archivo")
    metadatos: Optional[dict] = Field(None, description="Metadatos adicionales")


class DocumentoCreate(DocumentoBase):
    """Esquema para crear documento"""
    pass


class DocumentoUpdate(BaseModel):
    """Esquema para actualizar documento"""
    fecha_vencimiento: Optional[date] = None
    estado: Optional[EstadoDocumento] = None
    archivo_documento: Optional[str] = None
    metadatos: Optional[dict] = None
    activo: Optional[bool] = None


class DocumentoResponse(DocumentoBase):
    """Esquema de respuesta para documento"""
    id: int
    activo: bool
    fecha_creacion: datetime
    fecha_actualizacion: Optional[datetime]

    class Config:
        from_attributes = True


# ==================== SOLICITUDES ====================

class SolicitudBase(BaseModel):
    """Esquema base para solicitud"""
    numero_solicitud: str = Field(..., description="Número de solicitud", min_length=1, max_length=20)
    ciudadano_id: int = Field(..., description="ID del ciudadano", gt=0)
    documento_id: Optional[int] = Field(None, description="ID del documento", gt=0)
    tipo_solicitud: TipoSolicitud = Field(..., description="Tipo de solicitud")
    motivo: Optional[str] = Field(None, description="Motivo", max_length=255)
    observaciones: Optional[str] = Field(None, description="Observaciones", max_length=1000)
    estado: EstadoSolicitud = Field(EstadoSolicitud.PENDIENTE, description="Estado de la solicitud")


class SolicitudCreate(SolicitudBase):
    """Esquema para crear solicitud"""
    pass


class SolicitudUpdate(BaseModel):
    """Esquema para actualizar solicitud"""
    estado: Optional[EstadoSolicitud] = None
    motivo: Optional[str] = Field(None, max_length=255)
    observaciones: Optional[str] = Field(None, max_length=1000)
    fecha_procesamiento: Optional[datetime] = None
    fecha_entrega: Optional[datetime] = None


class SolicitudResponse(SolicitudBase):
    """Esquema de respuesta para solicitud"""
    id: int
    fecha_solicitud: datetime
    fecha_procesamiento: Optional[datetime]
    fecha_entrega: Optional[datetime]

    class Config:
        from_attributes = True


# ==================== EVENTOS ====================

class EventoSolicitudBase(BaseModel):
    """Esquema base para evento de solicitud"""
    solicitud_id: int = Field(..., description="ID de la solicitud", gt=0)
    evento: str = Field(..., description="Tipo de evento", min_length=1, max_length=100)
    descripcion: Optional[str] = Field(None, description="Descripción", max_length=1000)
    usuario: Optional[str] = Field(None, description="Usuario que realizó el evento", max_length=100)


class EventoSolicitudCreate(EventoSolicitudBase):
    """Esquema para crear evento de solicitud"""
    pass


class EventoSolicitudResponse(EventoSolicitudBase):
    """Esquema de respuesta para evento de solicitud"""
    id: int
    fecha_evento: datetime

    class Config:
        from_attributes = True


# ==================== BÚSQUEDAS ====================

class BusquedaCiudadano(BaseModel):
    """Esquema para búsqueda de ciudadano"""
    documento_identidad: Optional[str] = Field(None, min_length=8, max_length=8)
    email: Optional[EmailStr] = None
    nombres: Optional[str] = Field(None, min_length=1, max_length=100)
    apellidos: Optional[str] = Field(None, min_length=1, max_length=100)


class BusquedaDocumento(BaseModel):
    """Esquema para búsqueda de documento"""
    numero_documento: Optional[str] = Field(None, min_length=1, max_length=20)
    ciudadano_id: Optional[int] = Field(None, gt=0)
    estado: Optional[EstadoDocumento] = None


class BusquedaSolicitud(BaseModel):
    """Esquema para búsqueda de solicitud"""
    numero_solicitud: Optional[str] = Field(None, min_length=1, max_length=20)
    ciudadano_id: Optional[int] = Field(None, gt=0)
    estado: Optional[EstadoSolicitud] = None
    tipo_solicitud: Optional[TipoSolicitud] = None


# ==================== RESPUESTAS COMUNES ====================

class ResponseError(BaseModel):
    """Esquema para respuestas de error"""
    detail: str = Field(..., description="Descripción del error")
    error_code: Optional[str] = Field(None, description="Código del error")
    timestamp: datetime = Field(default_factory=datetime.now)


class ResponseSuccess(BaseModel):
    """Esquema para respuestas de éxito"""
    message: str = Field(..., description="Mensaje de éxito")
    data: Optional[dict] = Field(None, description="Datos de respuesta")
    timestamp: datetime = Field(default_factory=datetime.now)


class PaginationParams(BaseModel):
    """Parámetros de paginación"""
    page: int = Field(1, ge=1, description="Número de página")
    size: int = Field(10, ge=1, le=100, description="Tamaño de página")


class PaginatedResponse(BaseModel):
    """Respuesta paginada"""
    items: List[dict]
    total: int
    page: int
    size: int
    pages: int