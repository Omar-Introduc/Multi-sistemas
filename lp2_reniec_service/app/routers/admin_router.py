"""
Router para endpoints de administración
Contiene gestión de sesiones, estadísticas y validación masiva
"""
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
import logging
import time
import asyncio
from datetime import datetime, timedelta
from enum import Enum

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuración de rate limiting
RATE_LIMIT_ADMIN_REQUESTS = 50
RATE_LIMIT_WINDOW = 60  # segundos
admin_client_requests = {}

router = APIRouter(prefix="/api/admin", tags=["admin"])

# Enums
class EstadoSesion(str, Enum):
    ACTIVA = "ACTIVA"
    INACTIVA = "INACTIVA"
    EXPIRADA = "EXPIRADA"

class TipoValidacion(str, Enum):
    INDIVIDUAL = "INDIVIDUAL"
    MASIVA = "MASIVA"

# Modelos Pydantic
class SesionResponse(BaseModel):
    """Modelo de respuesta para sesión"""
    id_sesion: str = Field(..., description="ID único de la sesión")
    usuario: str = Field(..., description="Usuario de la sesión")
    ip_cliente: str = Field(..., description="IP del cliente")
    inicio_sesion: datetime = Field(..., description="Fecha de inicio")
    ultima_actividad: datetime = Field(..., description="Última actividad")
    estado: EstadoSesion = Field(..., description="Estado de la sesión")
    requests_totales: int = Field(default=0, description="Total de requests")

class EstadisticasResponse(BaseModel):
    """Modelo de respuesta para estadísticas"""
    timestamp: datetime
    total_requests: int = Field(..., description="Total de requests")
    requests_exitosos: int = Field(..., description="Requests exitosos")
    requests_fallidos: int = Field(..., description="Requests fallidos")
    ciudadanos_registrados: int = Field(..., description="Total de ciudadanos")
    sesiones_activas: int = Field(..., description="Sesiones activas")
    validaciones_ultima_hora: int = Field(..., description="Validaciones en la última hora")
    promedio_requests_por_segundo: float = Field(..., description="Promedio RPS")
    top_ips: List[Dict[str, Any]] = Field(..., description="Top IPs por actividad")

class ValidacionMasivaRequest(BaseModel):
    """Modelo para validación masiva"""
    lista_dnis: List[str] = Field(..., min_items=1, max_items=1000, description="Lista de DNIs a validar")
    incluir_detalle: bool = Field(default=False, description="Incluir detalles de cada ciudadano")
    
    @validator('lista_dnis')
    def validate_dnis(cls, v):
        if not v:
            raise ValueError('La lista no puede estar vacía')
        
        for dni in v:
            if not dni.isdigit() or len(dni) != 8:
                raise ValueError(f'DNI inválido: {dni}. Debe tener 8 dígitos numéricos')
        
        return v

class ResultadoValidacionIndividual(BaseModel):
    """Resultado de validación individual"""
    dni: str
    es_valido: bool
    mensaje: str
    tiempo_respuesta: float

class ValidacionMasivaResponse(BaseModel):
    """Respuesta para validación masiva"""
    total_consultados: int
    validos: int
    invalidos: int
    tiempo_total: float
    promedio_tiempo_respuesta: float
    resultados: List[ResultadoValidacionIndividual]

class SessionStats(BaseModel):
    """Estadísticas de sesión"""
    total_sesiones: int
    sesiones_activas: int
    sesiones_inactivas: int
    promedio_duracion: float  # en minutos

# Simulación de base de datos en memoria para administración
sesiones_db = {
    "sess_001": {
        "id_sesion": "sess_001",
        "usuario": "admin",
        "ip_cliente": "192.168.1.100",
        "inicio_sesion": datetime.now() - timedelta(hours=2),
        "ultima_actividad": datetime.now() - timedelta(minutes=5),
        "estado": EstadoSesion.ACTIVA,
        "requests_totales": 150
    },
    "sess_002": {
        "id_sesion": "sess_002",
        "usuario": "operator",
        "ip_cliente": "192.168.1.101",
        "inicio_sesion": datetime.now() - timedelta(hours=1),
        "ultima_actividad": datetime.now() - timedelta(minutes=30),
        "estado": EstadoSesion.ACTIVA,
        "requests_totales": 75
    },
    "sess_003": {
        "id_sesion": "sess_003",
        "usuario": "viewer",
        "ip_cliente": "192.168.1.102",
        "inicio_sesion": datetime.now() - timedelta(hours=5),
        "ultima_actividad": datetime.now() - timedelta(hours=3),
        "estado": EstadoSesion.EXPIRADA,
        "requests_totales": 25
    }
}

# Estadísticas simuladas
estadisticas_db = {
    "total_requests": 15420,
    "requests_exitosos": 14789,
    "requests_fallidos": 631,
    "ciudadanos_registrados": 234567,
    "validaciones_ultima_hora": 234,
    "requests_por_ip": {
        "192.168.1.100": 1250,
        "192.168.1.101": 890,
        "192.168.1.102": 670,
        "192.168.1.103": 445,
        "192.168.1.104": 320
    }
}

def check_admin_rate_limit(client_ip: str) -> bool:
    """Verificar rate limiting para endpoints de administración"""
    current_time = time.time()
    if client_ip not in admin_client_requests:
        admin_client_requests[client_ip] = []
    
    # Limpiar requests antiguos
    admin_client_requests[client_ip] = [
        req_time for req_time in admin_client_requests[client_ip]
        if current_time - req_time < RATE_LIMIT_WINDOW
    ]
    
    # Verificar límite
    if len(admin_client_requests[client_ip]) >= RATE_LIMIT_ADMIN_REQUESTS:
        return False
    
    # Agregar request actual
    admin_client_requests[client_ip].append(current_time)
    return True

def get_client_ip(request: Request) -> str:
    """Obtener IP del cliente"""
    return request.client.host if request.client else "unknown"

async def simular_validacion_dni(dni: str) -> bool:
    """Simular validación de DNI (en producción consultaría RENIEC)"""
    await asyncio.sleep(0.1)  # Simular latencia de red
    # Simular que algunos DNIs son válidos
    return int(dni) % 3 != 0

@router.get(
    "/sessions",
    response_model=List[SesionResponse],
    summary="Listar Sesiones Activas",
    description="Obtener lista de sesiones activas en el sistema"
)
async def listar_sesiones(
    estado: Optional[EstadoSesion] = None,
    limit: int = 50,
    request: Request = None
):
    """
    Listar sesiones activas en el sistema.
    
    **Parámetros de consulta:**
    - estado: Filtrar por estado de sesión (opcional)
    - limit: Número máximo de resultados (default: 50)
    
    **Respuesta:**
    - 200: Lista de sesiones
    - 400: Parámetros inválidos
    - 429: Rate limit excedido
    """
    # Verificar rate limiting
    if request:
        client_ip = get_client_ip(request)
        if not check_admin_rate_limit(client_ip):
            logger.warning(f"Rate limit excedido para IP: {client_ip}")
            raise HTTPException(
                status_code=429,
                detail="Demasiadas solicitudes administrativas. Intente más tarde."
            )
    
    # Validar parámetros
    if limit < 1 or limit > 200:
        raise HTTPException(
            status_code=400,
            detail="Limit debe estar entre 1 y 200"
        )
    
    try:
        logger.info(f"Listando sesiones - estado: {estado}, limit: {limit}")
        
        # Filtrar por estado si se especifica
        sesiones = list(sesiones_db.values())
        if estado:
            sesiones = [s for s in sesiones if s["estado"] == estado]
        
        # Actualizar estados de sesión basados en tiempo
        for sesion in sesiones:
            if sesion["estado"] == EstadoSesion.ACTIVA:
                tiempo_inactivo = datetime.now() - sesion["ultima_actividad"]
                if tiempo_inactivo > timedelta(hours=1):
                    sesion["estado"] = EstadoSesion.EXPIRADA
        
        # Limitar resultados
        sesiones_limited = sesiones[:limit]
        
        # Convertir a modelos de respuesta
        sesion_responses = [
            SesionResponse(**sesion) for sesion in sesiones_limited
        ]
        
        logger.info(f"Retornando {len(sesion_responses)} sesiones")
        return sesion_responses
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listando sesiones: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error interno del servidor"
        )

@router.get(
    "/estadisticas",
    response_model=EstadisticasResponse,
    summary="Obtener Estadísticas",
    description="Obtener estadísticas detalladas del sistema"
)
async def obtener_estadisticas(request: Request = None):
    """
    Obtener estadísticas detalladas del sistema.
    
    **Respuesta:**
    - 200: Estadísticas del sistema
    - 429: Rate limit excedido
    """
    # Verificar rate limiting
    if request:
        client_ip = get_client_ip(request)
        if not check_admin_rate_limit(client_ip):
            logger.warning(f"Rate limit excedido para IP: {client_ip}")
            raise HTTPException(
                status_code=429,
                detail="Demasiadas solicitudes administrativas. Intente más tarde."
            )
    
    try:
        logger.info("Obteniendo estadísticas del sistema")
        
        # Calcular promedio RPS (simulado)
        promedio_rps = estadisticas_db["total_requests"] / 3600  # Simulación
        
        # Crear top IPs
        top_ips = []
        for ip, count in sorted(
            estadisticas_db["requests_por_ip"].items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]:
            top_ips.append({
                "ip": ip,
                "requests": count,
                "porcentaje": round((count / estadisticas_db["total_requests"]) * 100, 2)
            })
        
        response = EstadisticasResponse(
            timestamp=datetime.now(),
            total_requests=estadisticas_db["total_requests"],
            requests_exitosos=estadisticas_db["requests_exitosos"],
            requests_fallidos=estadisticas_db["requests_fallidos"],
            ciudadanos_registrados=estadisticas_db["ciudadanos_registrados"],
            sesiones_activas=len([s for s in sesiones_db.values() if s["estado"] == EstadoSesion.ACTIVA]),
            validaciones_ultima_hora=estadisticas_db["validaciones_ultima_hora"],
            promedio_requests_por_segundo=round(promedio_rps, 2),
            top_ips=top_ips
        )
        
        logger.info("Estadísticas obtenidas exitosamente")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error interno del servidor"
        )

@router.post(
    "/validar-masivo",
    response_model=ValidacionMasivaResponse,
    summary="Validación Masiva",
    description="Validar múltiples DNIs en una sola operación"
)
async def validar_masivo(
    request_data: ValidacionMasivaRequest,
    request: Request = None
):
    """
    Validar múltiples DNIs de forma masiva.
    
    **Parámetros:**
    - request_data: Objeto con lista de DNIs a validar
    
    **Respuesta:**
    - 200: Resultados de validación masiva
    - 400: Datos inválidos
    - 429: Rate limit excedido
    - 503: Servicio no disponible para validación masiva
    """
    # Verificar rate limiting
    if request:
        client_ip = get_client_ip(request)
        if not check_admin_rate_limit(client_ip):
            logger.warning(f"Rate limit excedido para IP: {client_ip}")
            raise HTTPException(
                status_code=429,
                detail="Demasiadas solicitudes administrativas. Intente más tarde."
            )
    
    try:
        logger.info(f"Iniciando validación masiva para {len(request_data.lista_dnis)} DNIs")
        
        start_time = time.time()
        resultados = []
        validos = 0
        invalidos = 0
        
        # Procesar validaciones de forma concurrente
        tasks = [simular_validacion_dni(dni) for dni in request_data.lista_dnis]
        validaciones = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Procesar resultados
        for i, (dni, es_valido) in enumerate(zip(request_data.lista_dnis, validaciones)):
            if isinstance(es_valido, Exception):
                resultado = ResultadoValidacionIndividual(
                    dni=dni,
                    es_valido=False,
                    mensaje=f"Error en validación: {str(es_valido)}",
                    tiempo_respuesta=0.0
                )
                invalidos += 1
            else:
                if es_valido:
                    validos += 1
                    mensaje = "DNI válido"
                else:
                    invalidos += 1
                    mensaje = "DNI no encontrado"
                
                resultado = ResultadoValidacionIndividual(
                    dni=dni,
                    es_valido=es_valido,
                    mensaje=mensaje,
                    tiempo_respuesta=0.1  # Tiempo simulado
                )
            
            resultados.append(resultado)
        
        tiempo_total = time.time() - start_time
        promedio_tiempo = tiempo_total / len(request_data.lista_dnis)
        
        response = ValidacionMasivaResponse(
            total_consultados=len(request_data.lista_dnis),
            validos=validos,
            invalidos=invalidos,
            tiempo_total=round(tiempo_total, 3),
            promedio_tiempo_respuesta=round(promedio_tiempo, 3),
            resultados=resultados
        )
        
        logger.info(f"Validación masiva completada: {validos}/{len(request_data.lista_dnis)} válidos")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en validación masiva: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Error interno del servidor"
        )

# Manejadores de excepciones para el router admin
@router.exception_handler(401)
async def unauthorized_handler(request: Request, exc: HTTPException):
    """Manejador para errores 401 (no autorizado)"""
    logger.warning(f"Acceso no autorizado: {request.url}")
    return JSONResponse(
        status_code=401,
        content={
            "error": "No autorizado",
            "detalle": "Se requiere autenticación para acceder a este recurso",
            "timestamp": datetime.now().isoformat()
        }
    )

@router.exception_handler(403)
async def forbidden_handler(request: Request, exc: HTTPException):
    """Manejador para errores 403 (prohibido)"""
    logger.warning(f"Acceso prohibido: {request.url}")
    return JSONResponse(
        status_code=403,
        content={
            "error": "Prohibido",
            "detalle": "No tiene permisos para acceder a este recurso",
            "timestamp": datetime.now().isoformat()
        }
    )
