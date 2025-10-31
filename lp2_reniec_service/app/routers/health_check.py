"""
Router para verificación de salud del servicio
"""

from fastapi import APIRouter, HTTPException, status
from datetime import datetime
from app.config.settings import settings
from app.config.database import test_database_connection
from app.services.rabbit_service import test_rabbit_connection
from app.services.redis_service import test_redis_connection
from loguru import logger

router = APIRouter()


@router.get("/")
async def health_check():
    """
    Verificación básica de salud del servicio
    """
    try:
        return {
            "status": "healthy",
            "service": settings.app_name,
            "version": "1.0.0",
            "timestamp": datetime.now().isoformat(),
            "environment": "development" if settings.debug else "production"
        }
    except Exception as e:
        logger.error(f"Error en health check: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error en la verificación de salud"
        )


@router.get("/detailed")
async def detailed_health_check():
    """
    Verificación detallada de salud incluyendo dependencias
    """
    health_status = {
        "status": "healthy",
        "service": settings.app_name,
        "timestamp": datetime.now().isoformat(),
        "checks": {}
    }
    
    try:
        # Verificar base de datos
        db_healthy = test_database_connection()
        health_status["checks"]["database"] = {
            "status": "healthy" if db_healthy else "unhealthy",
            "type": "mysql"
        }
        
        # Verificar Redis
        redis_healthy = await test_redis_connection()
        health_status["checks"]["redis"] = {
            "status": "healthy" if redis_healthy else "unhealthy",
            "type": "cache"
        }
        
        # Verificar RabbitMQ
        rabbit_healthy = test_rabbit_connection()
        health_status["checks"]["rabbitmq"] = {
            "status": "healthy" if rabbit_healthy else "unhealthy",
            "type": "message_queue"
        }
        
        # Determinar estado general
        if not db_healthy or not redis_healthy or not rabbit_healthy:
            health_status["status"] = "degraded"
            if not db_healthy:
                health_status["status"] = "unhealthy"
        
        return health_status
        
    except Exception as e:
        logger.error(f"Error en detailed health check: {e}")
        health_status["status"] = "error"
        health_status["error"] = str(e)
        
        return health_status


@router.get("/ready")
async def readiness_check():
    """
    Verificación de readiness para Kubernetes
    """
    try:
        # Verificar que las dependencias críticas estén disponibles
        checks = {
            "database": test_database_connection(),
        }
        
        all_healthy = all(checks.values())
        
        if not all_healthy:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Service not ready"
            )
        
        return {
            "status": "ready",
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en readiness check: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service not ready"
        )


@router.get("/live")
async def liveness_check():
    """
    Verificación de liveness para Kubernetes
    """
    return {
        "status": "alive",
        "timestamp": datetime.now().isoformat()
    }