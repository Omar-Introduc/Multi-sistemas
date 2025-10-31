"""
Manejo avanzado de errores personalizados
Incluye excepciones específicas del dominio, manejo de errores HTTP y logging
"""

from typing import Any, Dict, Optional, List, Union
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.responses import Response
from pydantic import ValidationError
from sqlalchemy.exc import (
    SQLAlchemyError, 
    IntegrityError, 
    OperationalError,
    DisconnectionError,
    TimeoutError,
    NoResultFound,
    MultipleResultsFound
)
from sqlalchemy.orm import Session
import httpx
import asyncio
from loguru import logger
import traceback
from datetime import datetime
import uuid


# === EXCEPCIONES BASE DEL DOMINIO ===
class BaseAppException(Exception):
    """Excepción base de la aplicación"""
    
    def __init__(
        self, 
        message: str, 
        error_code: str = None, 
        details: Dict[str, Any] = None,
        status_code: int = 500,
        cause: Exception = None
    ):
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}
        self.status_code = status_code
        self.cause = cause
        self.timestamp = datetime.utcnow()
        self.request_id = None
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir excepción a diccionario para respuestas JSON"""
        return {
            "error": {
                "code": self.error_code,
                "message": self.message,
                "details": self.details,
                "timestamp": self.timestamp.isoformat(),
                "request_id": self.request_id
            }
        }


# === EXCEPCIONES DE NEGOCIO ===
class BusinessException(BaseAppException):
    """Excepción de reglas de negocio"""
    
    def __init__(self, message: str, error_code: str = "BUSINESS_ERROR", **kwargs):
        super().__init__(message, error_code, status_code=400, **kwargs)


class ValidationException(BaseAppException):
    """Excepción de validación de datos"""
    
    def __init__(self, message: str, field: str = None, **kwargs):
        details = kwargs.get("details", {})
        if field:
            details["field"] = field
        kwargs["details"] = details
        super().__init__(message, "VALIDATION_ERROR", status_code=422, **kwargs)


class AuthenticationException(BaseAppException):
    """Excepción de autenticación"""
    
    def __init__(self, message: str = "Authentication required", **kwargs):
        super().__init__(message, "AUTHENTICATION_ERROR", status_code=401, **kwargs)


class AuthorizationException(BaseAppException):
    """Excepción de autorización"""
    
    def __init__(self, message: str = "Insufficient permissions", **kwargs):
        super().__init__(message, "AUTHORIZATION_ERROR", status_code=403, **kwargs)


class ResourceNotFoundException(BaseAppException):
    """Excepción de recurso no encontrado"""
    
    def __init__(self, resource_type: str = "Resource", resource_id: Any = None, **kwargs):
        message = f"{resource_type} not found"
        if resource_id:
            message += f" (ID: {resource_id})"
        
        details = kwargs.get("details", {})
        details.update({
            "resource_type": resource_type,
            "resource_id": resource_id
        })
        kwargs["details"] = details
        
        super().__init__(message, "RESOURCE_NOT_FOUND", status_code=404, **kwargs)


class ResourceAlreadyExistsException(BaseAppException):
    """Excepción de recurso ya existente"""
    
    def __init__(self, resource_type: str = "Resource", resource_id: Any = None, **kwargs):
        message = f"{resource_type} already exists"
        if resource_id:
            message += f" (ID: {resource_id})"
        
        details = kwargs.get("details", {})
        details.update({
            "resource_type": resource_type,
            "resource_id": resource_id
        })
        kwargs["details"] = details
        
        super().__init__(message, "RESOURCE_ALREADY_EXISTS", status_code=409, **kwargs)


# === EXCEPCIONES DE BASE DE DATOS ===
class DatabaseException(BaseAppException):
    """Excepción base de base de datos"""
    
    def __init__(self, message: str, original_error: Exception = None, **kwargs):
        details = kwargs.get("details", {})
        if original_error:
            details["original_error"] = str(original_error)
            details["error_type"] = type(original_error).__name__
        
        kwargs["details"] = details
        super().__init__(message, "DATABASE_ERROR", status_code=500, cause=original_error, **kwargs)


class DatabaseConnectionException(DatabaseException):
    """Excepción de conexión a base de datos"""
    
    def __init__(self, message: str = "Database connection failed", **kwargs):
        super().__init__(message, "DATABASE_CONNECTION_ERROR", status_code=503, **kwargs)


class DatabaseTimeoutException(DatabaseException):
    """Excepción de timeout de base de datos"""
    
    def __init__(self, message: str = "Database operation timeout", **kwargs):
        super().__init__(message, "DATABASE_TIMEOUT", status_code=504, **kwargs)


class DatabaseIntegrityException(DatabaseException):
    """Excepción de integridad de base de datos"""
    
    def __init__(self, message: str = "Database integrity violation", **kwargs):
        super().__init__(message, "DATABASE_INTEGRITY_ERROR", status_code=409, **kwargs)


# === EXCEPCIONES DE RABBITMQ ===
class RabbitMQException(BaseAppException):
    """Excepción base de RabbitMQ"""
    
    def __init__(self, message: str, original_error: Exception = None, **kwargs):
        details = kwargs.get("details", {})
        if original_error:
            details["original_error"] = str(original_error)
            details["error_type"] = type(original_error).__name__
        
        kwargs["details"] = details
        super().__init__(message, "RABBITMQ_ERROR", status_code=503, cause=original_error, **kwargs)


class RabbitMQConnectionException(RabbitMQException):
    """Excepción de conexión a RabbitMQ"""
    
    def __init__(self, message: str = "RabbitMQ connection failed", **kwargs):
        super().__init__(message, "RABBITMQ_CONNECTION_ERROR", **kwargs)


class RabbitMQMessageException(RabbitMQException):
    """Excepción de mensaje en RabbitMQ"""
    
    def __init__(self, message: str = "RabbitMQ message processing failed", **kwargs):
        super().__init__(message, "RABBITMQ_MESSAGE_ERROR", **kwargs)


# === EXCEPCIONES DE RENIEC API ===
class RENIECAPIException(BaseAppException):
    """Excepción base de RENIEC API"""
    
    def __init__(self, message: str, status_code: int = None, response_data: Dict = None, **kwargs):
        details = kwargs.get("details", {})
        if response_data:
            details["api_response"] = response_data
        
        status_code = status_code or 502
        super().__init__(message, "RENIEC_API_ERROR", status_code=status_code, **kwargs)


class RENIECAPIUnavailableException(RENIECAPIException):
    """Excepción de RENIEC API no disponible"""
    
    def __init__(self, message: str = "RENIEC API service unavailable", **kwargs):
        super().__init__(message, status_code=503, **kwargs)


class RENIECDataNotFoundException(RENIECAPIException):
    """Excepción de datos no encontrados en RENIEC"""
    
    def __init__(self, message: str = "Data not found in RENIEC", **kwargs):
        super().__init__(message, status_code=404, **kwargs)


# === EXCEPCIONES DE CACHE ===
class CacheException(BaseAppException):
    """Excepción base de cache"""
    
    def __init__(self, message: str, original_error: Exception = None, **kwargs):
        super().__init__(message, "CACHE_ERROR", status_code=500, cause=original_error, **kwargs)


class CacheConnectionException(CacheException):
    """Excepción de conexión a cache"""
    
    def __init__(self, message: str = "Cache connection failed", **kwargs):
        super().__init__(message, "CACHE_CONNECTION_ERROR", status_code=503, **kwargs)


# === MANEJADOR GLOBAL DE EXCEPCIONES ===
class ExceptionHandler:
    """Manejador global de excepciones con logging y trazabilidad"""
    
    def __init__(self):
        self.error_counts = {}
        self.recent_errors = []
        self.max_recent_errors = 100
    
    async def __call__(self, request: Request, exc: Exception) -> Response:
        """Manejar excepciones globalmente"""
        
        # Generar ID único para trazabilidad
        error_id = str(uuid.uuid4())
        request_id = getattr(request.state, 'request_id', error_id)
        
        # Determinar tipo de excepción y respuesta
        if isinstance(exc, HTTPException):
            # FastAPI HTTPException
            response_data = {
                "error": {
                    "code": f"HTTP_{exc.status_code}",
                    "message": exc.detail,
                    "status_code": exc.status_code,
                    "timestamp": datetime.utcnow().isoformat(),
                    "request_id": request_id,
                    "error_id": error_id
                }
            }
            status_code = exc.status_code
            
        elif isinstance(exc, BaseAppException):
            # Excepción personalizada de la app
            exc.request_id = request_id
            exc.details["error_id"] = error_id
            exc.details["request_id"] = request_id
            response_data = exc.to_dict()
            status_code = exc.status_code
            
        elif isinstance(exc, ValidationError):
            # Pydantic ValidationError
            response_data = {
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Data validation failed",
                    "details": exc.errors(),
                    "timestamp": datetime.utcnow().isoformat(),
                    "request_id": request_id,
                    "error_id": error_id
                }
            }
            status_code = 422
            
        elif isinstance(exc, (IntegrityError, DatabaseIntegrityException)):
            # Errores de integridad de BD
            response_data = {
                "error": {
                    "code": "DATABASE_INTEGRITY_ERROR",
                    "message": "Database integrity violation",
                    "timestamp": datetime.utcnow().isoformat(),
                    "request_id": request_id,
                    "error_id": error_id
                }
            }
            status_code = 409
            
        elif isinstance(exc, (OperationalError, DatabaseConnectionException)):
            # Errores de conexión a BD
            response_data = {
                "error": {
                    "code": "DATABASE_ERROR",
                    "message": "Database operation failed",
                    "timestamp": datetime.utcnow().isoformat(),
                    "request_id": request_id,
                    "error_id": error_id
                }
            }
            status_code = 503
            
        elif isinstance(exc, TimeoutError):
            # Timeouts
            response_data = {
                "error": {
                    "code": "TIMEOUT_ERROR",
                    "message": "Operation timeout",
                    "timestamp": datetime.utcnow().isoformat(),
                    "request_id": request_id,
                    "error_id": error_id
                }
            }
            status_code = 504
            
        else:
            # Error interno inesperado
            response_data = {
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "Internal server error",
                    "timestamp": datetime.utcnow().isoformat(),
                    "request_id": request_id,
                    "error_id": error_id
                }
            }
            status_code = 500
        
        # Loggear error
        self._log_error(request, exc, error_id, request_id, status_code)
        
        # Actualizar contadores
        self._update_error_counts(exc)
        
        # Retornar respuesta JSON
        return JSONResponse(
            status_code=status_code,
            content=response_data,
            headers={
                "X-Error-ID": error_id,
                "X-Request-ID": request_id
            }
        )
    
    def _log_error(self, request: Request, exc: Exception, error_id: str, request_id: str, status_code: int):
        """Loggear error con información completa"""
        error_info = {
            "error_id": error_id,
            "request_id": request_id,
            "method": request.method,
            "url": str(request.url),
            "client_ip": self._get_client_ip(request),
            "status_code": status_code,
            "error_type": type(exc).__name__,
            "error_message": str(exc),
            "traceback": traceback.format_exc() if status_code >= 500 else None
        }
        
        # Log según severidad
        if status_code >= 500:
            logger.error(f"🚨 Error crítico [{error_id}]: {json.dumps(error_info, default=str)}")
        elif status_code >= 400:
            logger.warning(f"⚠️  Error de cliente [{error_id}]: {json.dumps(error_info, default=str)}")
        else:
            logger.info(f"ℹ️  Error info [{error_id}]: {json.dumps(error_info, default=str)}")
    
    def _get_client_ip(self, request: Request) -> str:
        """Obtener IP real del cliente"""
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        if hasattr(request.client, "host"):
            return request.client.host
        
        return "unknown"
    
    def _update_error_counts(self, exc: Exception):
        """Actualizar contadores de errores"""
        error_type = type(exc).__name__
        self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1
        
        # Agregar a errores recientes
        self.recent_errors.append({
            "error_type": error_type,
            "timestamp": datetime.utcnow().isoformat(),
            "message": str(exc)
        })
        
        # Mantener solo los últimos N errores
        if len(self.recent_errors) > self.max_recent_errors:
            self.recent_errors = self.recent_errors[-self.max_recent_errors:]
    
    def get_error_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas de errores"""
        return {
            "error_counts": self.error_counts,
            "recent_errors_count": len(self.recent_errors),
            "total_errors": sum(self.error_counts.values())
        }


# === DECORADORES PARA MANEJO DE EXCEPCIONES ===
def handle_exceptions(func):
    """Decorador para manejo automático de excepciones en funciones"""
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except BaseAppException:
            # Re-lanzar excepciones de la app
            raise
        except Exception as e:
            # Convertir excepciones inesperadas
            logger.error(f"❌ Error inesperado en {func.__name__}: {e}")
            raise BaseAppException(
                message="An unexpected error occurred",
                error_code="UNEXPECTED_ERROR",
                cause=e
            )
    return wrapper


def handle_database_exceptions(func):
    """Decorador para manejo de excepciones de base de datos"""
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except IntegrityError as e:
            logger.error(f"❌ Error de integridad en {func.__name__}: {e}")
            raise DatabaseIntegrityException(
                message="Database integrity violation",
                original_error=e
            )
        except OperationalError as e:
            logger.error(f"❌ Error operacional de DB en {func.__name__}: {e}")
            raise DatabaseConnectionException(
                message="Database connection failed",
                original_error=e
            )
        except TimeoutError as e:
            logger.error(f"❌ Timeout de DB en {func.__name__}: {e}")
            raise DatabaseTimeoutException(
                message="Database operation timeout",
                original_error=e
            )
        except Exception as e:
            logger.error(f"❌ Error inesperado de DB en {func.__name__}: {e}")
            raise DatabaseException(
                message="Database operation failed",
                original_error=e
            )
    return wrapper


# === FUNCIONES DE UTILIDAD ===
def create_http_exception(status_code: int, message: str, details: Dict = None) -> HTTPException:
    """Crear HTTPException con formato consistente"""
    return HTTPException(
        status_code=status_code,
        detail={
            "message": message,
            "details": details or {},
            "timestamp": datetime.utcnow().isoformat()
        }
    )


def raise_not_found(resource_type: str = "Resource", resource_id: Any = None):
    """Lanzar excepción de recurso no encontrado"""
    raise ResourceNotFoundException(resource_type=resource_type, resource_id=resource_id)


def raise_already_exists(resource_type: str = "Resource", resource_id: Any = None):
    """Lanzar excepción de recurso existente"""
    raise ResourceAlreadyExistsException(resource_type=resource_type, resource_id=resource_id)


def raise_validation_error(message: str, field: str = None):
    """Lanzar excepción de validación"""
    raise ValidationException(message=message, field=field)


# === INSTANCIA GLOBAL DEL MANEJADOR ===
exception_handler = ExceptionHandler()

# === EXPORTACIONES ===
__all__ = [
    # Excepciones base
    "BaseAppException",
    
    # Excepciones de negocio
    "BusinessException",
    "ValidationException", 
    "AuthenticationException",
    "AuthorizationException",
    "ResourceNotFoundException",
    "ResourceAlreadyExistsException",
    
    # Excepciones de base de datos
    "DatabaseException",
    "DatabaseConnectionException",
    "DatabaseTimeoutException", 
    "DatabaseIntegrityException",
    
    # Excepciones de servicios externos
    "RabbitMQException",
    "RabbitMQConnectionException",
    "RabbitMQMessageException",
    "RENIECAPIException",
    "RENIECAPIUnavailableException",
    "RENIECDataNotFoundException",
    "CacheException",
    "CacheConnectionException",
    
    # Manejador global
    "ExceptionHandler",
    "exception_handler",
    
    # Decoradores
    "handle_exceptions",
    "handle_database_exceptions",
    
    # Utilidades
    "create_http_exception",
    "raise_not_found",
    "raise_already_exists", 
    "raise_validation_error"
]