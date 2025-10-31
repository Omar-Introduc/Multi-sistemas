"""
Aplicación FastAPI para el servicio LP2 RENIEC
Sistema de gestión de documentos de identidad

Este módulo contiene la aplicación FastAPI principal con:
- Configuración de middlewares (CORS, autenticación, logging, rate limiting)
- Gestión del lifecycle de la aplicación (startup/shutdown con lifespan)
- Registro de routers para diferentes servicios
- Manejo global de excepciones
- Configuración de servicios externos (MySQL, RabbitMQ, Redis)
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.exception_handlers import (
    http_exception_handler,
    request_validation_exception_handler
)
from starlette.exceptions import HTTPException, RequestValidationError
import uvicorn
from loguru import logger
import sys
import os
from pathlib import Path

# Importaciones de configuración
from app.config import settings, database_config, rabbitmq_config, redis_config, logging_config
from app.config.database import engine, Base, get_db
from app.routers import (
    health_check,
    reniec_endpoints,
    document_management,
    citizen_services,
    reniec_router,
    admin_router
)
from app.middleware.auth import AuthMiddleware
from app.middleware.logging import LoggingMiddleware
from app.middleware.rate_limiter import RateLimitMiddleware


# Configurar logging antes de crear la aplicación
def setup_logging():
    """Configurar sistema de logging con Loguru"""
    # Remover handler por defecto
    logger.remove()
    
    # Agregar handler para stderr (console)
    logger.add(
        sys.stderr,
        format=logging_config.format,
        level=logging_config.level,
        colorize=True
    )
    
    # Crear directorio de logs si no existe
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Agregar handler para archivo de logs general
    logger.add(
        log_dir / "app_{time:YYYY-MM-DD}.log",
        format=logging_config.format,
        level=logging_config.level,
        rotation=logging_config.rotation,
        retention=logging_config.retention,
        compression=logging_config.compression,
        encoding=logging_config.encoding,
        backup_count=logging_config.backup_count
    )
    
    # Agregar handler para errores单独的
    logger.add(
        log_dir / "error_{time:YYYY-MM-DD}.log",
        format=logging_config.format,
        level="ERROR",
        rotation=logging_config.rotation,
        retention=logging_config.retention,
        compression=logging_config.compression,
        encoding=logging_config.encoding,
        backup_count=logging_config.backup_count
    )


# Context manager para el lifecycle de la aplicación
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gestión del lifecycle de la aplicación FastAPI
    Maneja inicialización y cleanup de recursos
    """
    # ========== STARTUP ==========
    logger.info("🚀 Iniciando aplicación LP2 RENIEC Service")
    logger.info(f"📋 Versión: {settings.app_version}")
    logger.info(f"🌍 Entorno: {settings.environment}")
    logger.info(f"🔧 Debug: {settings.debug}")
    
    try:
        # Crear tablas en la base de datos
        logger.info("📊 Verificando tablas de base de datos...")
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Tablas de base de datos verificadas")
        
        # Inicializar servicios externos
        logger.info("🔌 Inicializando servicios externos...")
        
        # Inicializar RabbitMQ
        try:
            from app.services.rabbit_service import initialize_rabbit
            await initialize_rabbit()
            logger.info("✅ RabbitMQ inicializado")
        except Exception as e:
            logger.error(f"⚠️  Error inicializando RabbitMQ: {e}")
        
        # Inicializar Redis
        try:
            from app.services.redis_service import initialize_redis
            await initialize_redis()
            logger.info("✅ Redis inicializado")
        except Exception as e:
            logger.error(f"⚠️  Error inicializando Redis: {e}")
        
        # Inicializar listeners de eventos
        try:
            from app.listeners.event_listener import initialize_event_listeners
            await initialize_event_listeners()
            logger.info("✅ Event listeners inicializados")
        except Exception as e:
            logger.error(f"⚠️  Error inicializando event listeners: {e}")
        
        logger.info("✅ Servicios inicializados correctamente")
        logger.info("🎉 Aplicación lista para recibir peticiones")
        
    except Exception as e:
        logger.error(f"❌ Error durante inicialización: {e}")
        raise
    
    # Yield control back to FastAPI
    yield
    
    # ========== SHUTDOWN ==========
    logger.info("🔄 Cerrando aplicación LP2 RENIEC Service")
    
    try:
        # Cerrar conexiones de servicios externos
        logger.info("🔌 Cerrando conexiones de servicios...")
        
        # Cerrar RabbitMQ
        try:
            from app.services.rabbit_service import close_rabbit
            await close_rabbit()
            logger.info("✅ RabbitMQ cerrado")
        except Exception as e:
            logger.error(f"⚠️  Error cerrando RabbitMQ: {e}")
        
        # Cerrar Redis
        try:
            from app.services.redis_service import close_redis
            await close_redis()
            logger.info("✅ Redis cerrado")
        except Exception as e:
            logger.error(f"⚠️  Error cerrando Redis: {e}")
        
        # Cerrar event listeners
        try:
            from app.listeners.event_listener import close_event_listeners
            await close_event_listeners()
            logger.info("✅ Event listeners cerrados")
        except Exception as e:
            logger.error(f"⚠️  Error cerrando event listeners: {e}")
        
        # Cerrar conexiones de base de datos
        try:
            from app.config.database import close_database_connections
            close_database_connections()
            logger.info("✅ Conexiones de base de datos cerradas")
        except Exception as e:
            logger.error(f"⚠️  Error cerrando conexiones DB: {e}")
        
        logger.info("✅ Aplicación cerrada correctamente")
        
    except Exception as e:
        logger.error(f"❌ Error durante cierre: {e}")


def create_app() -> FastAPI:
    """
    Factory para crear la aplicación FastAPI con todas las configuraciones
    """
    # Configurar logging
    setup_logging()
    
    # Crear aplicación con lifespan management
    app = FastAPI(
        title=settings.app_name,
        description="Servicio FastAPI para gestión de documentos de identidad - RENIEC",
        version=settings.app_version,
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
        openapi_url="/openapi.json" if settings.debug else None,
        lifespan=lifespan,
        debug=settings.debug,
        default_response_class=None
    )
    
    # ========== MIDDLEWARE ==========
    
    # CORS - debe ser uno de los primeros middlewares
    if settings.enable_cors:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.allowed_hosts,
            allow_credentials=settings.security_config.cors_origins,
            allow_methods=settings.security_config.cors_methods,
            allow_headers=settings.security_config.cors_headers,
            expose_headers=["X-Total-Count", "X-Page-Count"],
            max_age=600  # 10 minutos
        )
    
    # Trusted Host - para seguridad en producción
    if not settings.debug:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["*"]  # Configurar apropiadamente en producción
        )
    
    # Middlewares personalizados (agregar después de CORS)
    if settings.enable_request_logging:
        app.add_middleware(LoggingMiddleware)
    
    if settings.enable_rate_limiting:
        app.add_middleware(RateLimitMiddleware)
    
    # Auth middleware debe ir después de otros middlewares
    app.add_middleware(AuthMiddleware)
    
    # ========== EXCEPTION HANDLERS ==========
    
    @app.exception_handler(HTTPException)
    async def http_exception_handler_custom(request: Request, exc: HTTPException):
        """Manejador personalizado para excepciones HTTP"""
        logger.warning(f"HTTP Exception: {exc.status_code} - {exc.detail} - {request.url}")
        return await http_exception_handler(request, exc)
    
    @app.exception_handler(RequestValidationError)
    async def request_validation_exception_handler_custom(request: Request, exc: RequestValidationError):
        """Manejador personalizado para errores de validación"""
        logger.warning(f"Validation Error: {exc.errors()} - {request.url}")
        return await request_validation_exception_handler(request, exc)
    
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        """Manejador global para excepciones no controladas"""
        logger.error(f"Error global en {request.method} {request.url}: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Error interno del servidor",
                "error_id": f"ERR_{id(exc)}",  # ID único para tracking
            }
        )
    
    # ========== ROUTERS ==========
    
    # Router de health check (alta prioridad)
    app.include_router(
        health_check.router, 
        prefix="/api/v1/health", 
        tags=["Health Check"]
    )
    
    # Routers principales
    app.include_router(
        reniec_endpoints.router, 
        prefix="/api/v1/reniec", 
        tags=["RENIEC API"]
    )
    app.include_router(
        document_management.router, 
        prefix="/api/v1/documents", 
        tags=["Document Management"]
    )
    app.include_router(
        citizen_services.router, 
        prefix="/api/v1/citizens", 
        tags=["Citizen Services"]
    )
    
    # Routers públicos y administrativos
    app.include_router(
        reniec_router.router, 
        prefix="/api/reniec", 
        tags=["RENIEC Public"]
    )
    app.include_router(
        admin_router.router, 
        prefix="/api/admin", 
        tags=["Admin"]
    )
    
    # ========== ENDPOINTS ADICIONALES ==========
    
    @app.get("/", tags=["Root"])
    async def root():
        """Endpoint raíz con información de la API"""
        return {
            "service": settings.app_name,
            "version": settings.app_version,
            "status": "running",
            "environment": settings.environment,
            "timestamp": logger._format_time(None),  # Loguru time format
            "docs": "/docs" if settings.debug else "Not available in production",
            "health": "/api/v1/health"
        }
    
    @app.get("/status", tags=["Status"])
    async def status():
        """Endpoint de estado simplificado"""
        return {"status": "ok", "service": settings.app_name}
    
    # ========== METADATA ==========
    
    # Agregar información adicional al OpenAPI
    app.openapi_tags = [
        {"name": "Health Check", "description": "Endpoints de verificación de salud del servicio"},
        {"name": "RENIEC API", "description": "API principal para operaciones con RENIEC"},
        {"name": "Document Management", "description": "Gestión de documentos de identidad"},
        {"name": "Citizen Services", "description": "Servicios para ciudadanos"},
        {"name": "RENIEC Public", "description": "Endpoints públicos de RENIEC"},
        {"name": "Admin", "description": "Endpoints de administración"},
        {"name": "Root", "description": "Información general de la API"}
    ]
    
    logger.info(f"✅ Aplicación FastAPI creada: {settings.app_name}")
    
    return app


# Instancia global de la aplicación
app = create_app()


if __name__ == "__main__":
    # Configuraciones adicionales para ejecución directa
    logger.info("🚀 Iniciando servidor directamente con Python")
    logger.info(f"🌐 Host: {settings.host}")
    logger.info(f"🔌 Puerto: {settings.port}")
    logger.info(f"🔧 Debug: {settings.debug}")
    
    # Configurar variables de entorno adicionales si es necesario
    if not os.getenv("PYTHONPATH"):
        os.environ["PYTHONPATH"] = str(Path.cwd())
    
    # Ejecutar servidor con uvicorn
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug and settings.environment == "development",
        log_level=logging_config.level.lower(),
        access_log=True,
        date_format="%Y-%m-%d %H:%M:%S"
    )