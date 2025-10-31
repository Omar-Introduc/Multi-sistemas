"""
Router para endpoints de RENIEC
Contiene validación, consulta y listado de ciudadanos
"""
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
import logging
import time
import re
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuración de rate limiting
RATE_LIMIT_REQUESTS = 100
RATE_LIMIT_WINDOW = 60  # segundos
client_requests = {}

router = APIRouter(prefix="/api/reniec", tags=["reniec"])

# Modelos Pydantic
class CiudadanoResponse(BaseModel):
    """Modelo de respuesta para ciudadano"""
    dni: str = Field(..., description="Documento Nacional de Identidad")
    nombres: str = Field(..., description="Nombres del ciudadano")
    apellido_paterno: str = Field(..., description="Apellido paterno")
    apellido_materno: str = Field(..., description="Apellido materno")
    telefono: Optional[str] = Field(None, description="Número de teléfono")
    direccion: Optional[str] = Field(None, description="Dirección")
    fecha_nacimiento: Optional[str] = Field(None, description="Fecha de nacimiento")
    estado: str = Field("ACTIVO", description="Estado del ciudadano")

class ConsultarRequest(BaseModel):
    """Modelo para solicitud de consulta"""
    dni: str = Field(..., min_length=8, max_length=8, description="DNI a consultar")
    
    @validator('dni')
    def validate_dni(cls, v):
        if not v.isdigit():
            raise ValueError('El DNI debe contener solo números')
        if len(v) != 8:
            raise ValueError('El DNI debe tener exactamente 8 dígitos')
        return v

class ValidacionResponse(BaseModel):
    """Modelo de respuesta para validación"""
    dni: str
    es_valido: bool
    mensaje: str
    timestamp: datetime
    ciudadano: Optional[CiudadanoResponse] = None

class CiudadanoRequest(BaseModel):
    """Modelo para crear/actualizar ciudadano"""
    dni: str = Field(..., min_length=8, max_length=8, description="DNI")
    nombres: str = Field(..., min_length=1, description="Nombres")
    apellido_paterno: str = Field(..., min_length=1, description="Apellido paterno")
    apellido_materno: str = Field(..., min_length=1, description="Apellido materno")
    telefono: Optional[str] = Field(None, description="Teléfono")
    direccion: Optional[str] = Field(None, description="Dirección")
    
    @validator('dni')
    def validate_dni(cls, v):
        if not v.isdigit():
            raise ValueError('El DNI debe contener solo números')
        if len(v) != 8:
            raise ValueError('El DNI debe tener exactamente 8 dígitos')
        return v

class HealthResponse(BaseModel):
    """Modelo de respuesta para health check"""
    status: str
    timestamp: datetime
    version: str = "1.0.0"
    servicios: Dict[str, str]

# Simulación de base de datos en memoria
ciudadanos_db: Dict[str, CiudadanoResponse] = {
    "12345678": CiudadanoResponse(
        dni="12345678",
        nombres="Juan Carlos",
        apellido_paterno="García",
        apellido_materno="López",
        telefono="987654321",
        direccion="Av. Principal 123",
        fecha_nacimiento="1990-05-15"
    ),
    "87654321": CiudadanoResponse(
        dni="87654321",
        nombres="María Elena",
        apellido_paterno="Martínez",
        apellido_materno="Silva",
        telefono="912345678",
        direccion="Calle Secundaria 456",
        fecha_nacimiento="1985-08-22"
    )
}

def check_rate_limit(client_ip: str) -> bool:
    """Verificar rate limiting por cliente"""
    current_time = time.time()
    if client_ip not in client_requests:
        client_requests[client_ip] = []
    
    # Limpiar requests antiguos
    client_requests[client_ip] = [
        req_time for req_time in client_requests[client_ip]
        if current_time - req_time < RATE_LIMIT_WINDOW
    ]
    
    # Verificar límite
    if len(client_requests[client_ip]) >= RATE_LIMIT_REQUESTS:
        return False
    
    # Agregar request actual
    client_requests[client_ip].append(current_time)
    return True

def get_client_ip(request: Request) -> str:
    """Obtener IP del cliente"""
    return request.client.host if request.client else "unknown"

@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health Check",
    description="Verificar el estado del servicio RENIEC"
)
async def health_check():
    """
    Endpoint para verificar el estado del servicio.
    
    **Respuesta:**
    - 200: Servicio operativo con detalles de salud
    """
    try:
        logger.info("Health check solicitado")
        return HealthResponse(
            status="OK",
            timestamp=datetime.now(),
            servicios={
                "base_datos": "CONECTADO",
                "servidor": "OPERATIVO",
                "autenticacion": "ACTIVO"
            }
        )
    except Exception as e:
        logger.error(f"Error en health check: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail="Servicio no disponible"
        )

@router.get(
    "/validar/{dni}",
    response_model=ValidacionResponse,
    summary="Validar DNI",
    description="Validar si un DNI existe en el sistema"
)
async def validar_dni(
    dni: str,
    request: Request
):
    """
    Validar un DNI en el sistema RENIEC.
    
    **Parámetros:**
    - dni: DNI a validar (8 dígitos numéricos)
    
    **Respuesta:**
    - 200: DNI válido o inválido con detalles
    - 400: DNI con formato incorrecto
    - 429: Rate limit excedido
    """
    # Verificar rate limiting
    client_ip = get_client_ip(request)
    if not check_rate_limit(client_ip):
        logger.warning(f"Rate limit excedido para IP: {client_ip}")
        raise HTTPException(
            status_code=429,
            detail="Demasiadas solicitudes. Intente más tarde."
        )
    
    # Validar formato DNI
    if not dni.isdigit() or len(dni) != 8:
        logger.warning(f"DNI con formato inválido: {dni}")
        raise HTTPException(
            status_code=400,
            detail="DNI debe tener 8 dígitos numéricos"
        )
    
    try:
        logger.info(f"Validando DNI: {dni}")
        
        # Simular validación (en producción consultaría RENIEC)
        ciudadano = ciudadanos_db.get(dni)
        es_valido = ciudadano is not None
        
        response = ValidacionResponse(
            dni=dni,
            es_valido=es_valido,
            mensaje="DNI válido" if es_valido else "DNI no encontrado",
            timestamp=datetime.now(),
            ciudadano=ciudadano
        )
        
        logger.info(f"DNI {dni} {'válido' if es_valido else 'inválido'}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error validando DNI {dni}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error interno del servidor"
        )

@router.post(
    "/consultar",
    response_model=Optional[CiudadanoResponse],
    summary="Consultar Ciudadano",
    description="Consultar información completa de un ciudadano por DNI"
)
async def consultar_ciudadano(
    request_data: ConsultarRequest,
    request: Request
):
    """
    Consultar información detallada de un ciudadano.
    
    **Parámetros:**
    - request_data: Objeto con DNI a consultar
    
    **Respuesta:**
    - 200: Información del ciudadano
    - 400: Datos inválidos
    - 404: Ciudadano no encontrado
    - 429: Rate limit excedido
    """
    # Verificar rate limiting
    client_ip = get_client_ip(request)
    if not check_rate_limit(client_ip):
        logger.warning(f"Rate limit excedido para IP: {client_ip}")
        raise HTTPException(
            status_code=429,
            detail="Demasiadas solicitudes. Intente más tarde."
        )
    
    try:
        logger.info(f"Consultando ciudadano con DNI: {request_data.dni}")
        
        # Buscar ciudadano
        ciudadano = ciudadanos_db.get(request_data.dni)
        
        if not ciudadano:
            logger.warning(f"Ciudadano no encontrado: {request_data.dni}")
            raise HTTPException(
                status_code=404,
                detail="Ciudadano no encontrado"
            )
        
        logger.info(f"Ciudadano encontrado: {request_data.dni}")
        return ciudadano
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error consultando ciudadano {request_data.dni}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error interno del servidor"
        )

@router.get(
    "/ciudadanos",
    response_model=List[CiudadanoResponse],
    summary="Listar Ciudadanos",
    description="Obtener lista de ciudadanos registrados en el sistema"
)
async def listar_ciudadanos(
    limit: int = 100,
    offset: int = 0,
    request: Request = None
):
    """
    Listar ciudadanos registrados en el sistema.
    
    **Parámetros de consulta:**
    - limit: Número máximo de resultados (default: 100)
    - offset: Número de registros a omitir (default: 0)
    
    **Respuesta:**
    - 200: Lista de ciudadanos
    - 400: Parámetros inválidos
    - 429: Rate limit excedido
    """
    # Verificar rate limiting
    if request:
        client_ip = get_client_ip(request)
        if not check_rate_limit(client_ip):
            logger.warning(f"Rate limit excedido para IP: {client_ip}")
            raise HTTPException(
                status_code=429,
                detail="Demasiadas solicitudes. Intente más tarde."
            )
    
    # Validar parámetros
    if limit < 1 or limit > 1000:
        raise HTTPException(
            status_code=400,
            detail="Limit debe estar entre 1 y 1000"
        )
    
    if offset < 0:
        raise HTTPException(
            status_code=400,
            detail="Offset debe ser mayor o igual a 0"
        )
    
    try:
        logger.info(f"Listando ciudadanos - limit: {limit}, offset: {offset}")
        
        # Convertir a lista y aplicar paginación
        ciudadanos = list(ciudadanos_db.values())
        total = len(ciudadanos)
        
        # Aplicar paginación
        paginated_ciudadanos = ciudadanos[offset:offset + limit]
        
        logger.info(f"Retornando {len(paginated_ciudadanos)} de {total} ciudadanos")
        
        return paginated_ciudadanos
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listando ciudadanos: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error interno del servidor"
        )

# Manejador global de excepciones para el router
@router.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    """Manejador para errores 404"""
    logger.warning(f"Endpoint no encontrado: {request.url}")
    return JSONResponse(
        status_code=404,
        content={
            "error": "No encontrado",
            "detalle": "El endpoint solicitado no existe",
            "timestamp": datetime.now().isoformat()
        }
    )

@router.exception_handler(500)
async def internal_error_handler(request: Request, exc: HTTPException):
    """Manejador para errores 500"""
    logger.error(f"Error interno: {request.url}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Error interno del servidor",
            "detalle": "Ocurrió un error inesperado",
            "timestamp": datetime.now().isoformat()
        }
    )
