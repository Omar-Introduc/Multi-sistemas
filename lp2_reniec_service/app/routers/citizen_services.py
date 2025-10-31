"""
Router para servicios de ciudadanos
"""

from fastapi import APIRouter, HTTPException, status, Depends
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime
from app.config.database import get_db
from app.models.schemas import (
    CiudadanoCreate, CiudadanoResponse, CiudadanoUpdate,
    BusquedaCiudadano, ResponseSuccess
)
from app.services.ciudadano_service import CiudadanoService
from loguru import logger

router = APIRouter()
ciudadano_service = CiudadanoService()


@router.post("/", response_model=CiudadanoResponse)
async def crear_ciudadano(
    ciudadano: CiudadanoCreate,
    db: Session = Depends(get_db)
):
    """
    Crear un nuevo ciudadano
    """
    try:
        logger.info(f"Creando ciudadano: {ciudadano.documento_identidad}")
        
        # Verificar que el documento de identidad no existe
        if ciudadano_service.existe_por_documento(db, ciudadano.documento_identidad):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe un ciudadano con este documento de identidad"
            )
        
        # Crear ciudadano
        nuevo_ciudadano = ciudadano_service.crear(db, ciudadano)
        
        logger.info(f"Ciudadano creado exitosamente: {nuevo_ciudadano.id}")
        return nuevo_ciudadano
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creando ciudadano: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno creando ciudadano"
        )


@router.get("/", response_model=List[CiudadanoResponse])
async def listar_ciudadanos(
    skip: int = 0,
    limit: int = 100,
    activo: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """
    Listar ciudadanos con paginación y filtro opcional por estado
    """
    try:
        ciudadanos = ciudadano_service.listar(db, skip=skip, limit=limit, activo=activo)
        return ciudadanos
        
    except Exception as e:
        logger.error(f"Error listando ciudadanos: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno listando ciudadanos"
        )


@router.get("/{ciudadano_id}", response_model=CiudadanoResponse)
async def obtener_ciudadano(
    ciudadano_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtener un ciudadano por ID
    """
    try:
        ciudadano = ciudadano_service.obtener_por_id(db, ciudadano_id)
        if not ciudadano:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ciudadano no encontrado"
            )
        
        return ciudadano
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo ciudadano {ciudadano_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno obteniendo ciudadano"
        )


@router.get("/documento/{documento_identidad}", response_model=CiudadanoResponse)
async def obtener_por_documento(
    documento_identidad: str,
    db: Session = Depends(get_db)
):
    """
    Obtener ciudadano por documento de identidad
    """
    try:
        ciudadano = ciudadano_service.buscar_por_documento(db, documento_identidad)
        if not ciudadano:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ciudadano no encontrado"
            )
        
        return ciudadano
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo ciudadano por documento {documento_identidad}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno obteniendo ciudadano"
        )


@router.put("/{ciudadano_id}", response_model=CiudadanoResponse)
async def actualizar_ciudadano(
    ciudadano_id: int,
    ciudadano_update: CiudadanoUpdate,
    db: Session = Depends(get_db)
):
    """
    Actualizar un ciudadano
    """
    try:
        ciudadano = ciudadano_service.actualizar(db, ciudadano_id, ciudadano_update)
        if not ciudadano:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ciudadano no encontrado"
            )
        
        logger.info(f"Ciudadano actualizado exitosamente: {ciudadano_id}")
        return ciudadano
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error actualizando ciudadano {ciudadano_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno actualizando ciudadano"
        )


@router.delete("/{ciudadano_id}")
async def eliminar_ciudadano(
    ciudadano_id: int,
    db: Session = Depends(get_db)
):
    """
    Eliminar (desactivar) un ciudadano
    """
    try:
        success = ciudadano_service.eliminar(db, ciudadano_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ciudadano no encontrado"
            )
        
        logger.info(f"Ciudadano eliminado exitosamente: {ciudadano_id}")
        return {"message": "Ciudadano eliminado exitosamente"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error eliminando ciudadano {ciudadano_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno eliminando ciudadano"
        )


@router.post("/buscar", response_model=List[CiudadanoResponse])
async def buscar_ciudadanos(
    criterio: BusquedaCiudadano,
    db: Session = Depends(get_db)
):
    """
    Buscar ciudadanos por criterios
    """
    try:
        ciudadanos = ciudadano_service.buscar(db, criterio)
        return ciudadanos
        
    except Exception as e:
        logger.error(f"Error buscando ciudadanos: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno buscando ciudadanos"
        )


@router.get("/{ciudadano_id}/documentos")
async def obtener_documentos_ciudadano(
    ciudadano_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtener todos los documentos de un ciudadano
    """
    try:
        ciudadano = ciudadano_service.obtener_por_id(db, ciudadano_id)
        if not ciudadano:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ciudadano no encontrado"
            )
        
        documentos = ciudadano_service.obtener_documentos(db, ciudadano_id)
        
        return {
            "ciudadano": {
                "id": ciudadano.id,
                "nombres": ciudadano.nombres,
                "apellidos": ciudadano.apellidos,
                "documento_identidad": ciudadano.documento_identidad
            },
            "documentos": [
                {
                    "id": doc.id,
                    "numero_documento": doc.numero_documento,
                    "tipo": doc.tipo_documento.nombre,
                    "estado": doc.estado,
                    "fecha_emision": doc.fecha_emision,
                    "fecha_vencimiento": doc.fecha_vencimiento
                }
                for doc in documentos
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo documentos del ciudadano {ciudadano_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno obteniendo documentos del ciudadano"
        )


@router.get("/{ciudadano_id}/solicitudes")
async def obtener_solicitudes_ciudadano(
    ciudadano_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtener todas las solicitudes de un ciudadano
    """
    try:
        ciudadano = ciudadano_service.obtener_por_id(db, ciudadano_id)
        if not ciudadano:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ciudadano no encontrado"
            )
        
        solicitudes = ciudadano_service.obtener_solicitudes(db, ciudadano_id)
        
        return {
            "ciudadano": {
                "id": ciudadano.id,
                "nombres": ciudadano.nombres,
                "apellidos": ciudadano.apellidos,
                "documento_identidad": ciudadano.documento_identidad
            },
            "solicitudes": [
                {
                    "id": sol.id,
                    "numero_solicitud": sol.numero_solicitud,
                    "tipo_solicitud": sol.tipo_solicitud,
                    "estado": sol.estado,
                    "fecha_solicitud": sol.fecha_solicitud,
                    "fecha_procesamiento": sol.fecha_procesamiento,
                    "fecha_entrega": sol.fecha_entrega
                }
                for sol in solicitudes
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo solicitudes del ciudadano {ciudadano_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno obteniendo solicitudes del ciudadano"
        )


@router.get("/estadisticas/resumen")
async def obtener_estadisticas_ciudadanos(db: Session = Depends(get_db)):
    """
    Obtener estadísticas de ciudadanos
    """
    try:
        stats = ciudadano_service.obtener_estadisticas(db)
        return {
            "estadisticas": stats,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas de ciudadanos: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno obteniendo estadísticas"
        )