"""
Router para gestión de documentos
"""

from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime
from app.config.database import get_db
from app.models.schemas import (
    DocumentoCreate, DocumentoResponse, DocumentoUpdate,
    BusquedaDocumento, ResponseSuccess
)
from app.services.documento_service import DocumentoService
from app.utils.file_handler import FileHandler
from loguru import logger

router = APIRouter()
documento_service = DocumentoService()
file_handler = FileHandler()


@router.post("/", response_model=DocumentoResponse)
async def crear_documento(
    documento: DocumentoCreate,
    db: Session = Depends(get_db)
):
    """
    Crear un nuevo documento
    """
    try:
        logger.info(f"Creando documento: {documento.numero_documento}")
        
        # Verificar que el ciudadano existe
        ciudadano = documento_service.buscar_ciudadano(db, documento.ciudadano_id)
        if not ciudadano:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ciudadano no encontrado"
            )
        
        # Verificar que el tipo de documento existe
        tipo_doc = documento_service.buscar_tipo_documento(db, documento.tipo_documento_id)
        if not tipo_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tipo de documento no encontrado"
            )
        
        # Verificar que el número de documento no exista
        if documento_service.existe_documento(db, documento.numero_documento):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe un documento con este número"
            )
        
        # Crear documento
        nuevo_documento = documento_service.crear(db, documento)
        
        logger.info(f"Documento creado exitosamente: {nuevo_documento.id}")
        return nuevo_documento
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creando documento: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno creando documento"
        )


@router.get("/", response_model=List[DocumentoResponse])
async def listar_documentos(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Listar documentos con paginación
    """
    try:
        documentos = documento_service.listar(db, skip=skip, limit=limit)
        return documentos
        
    except Exception as e:
        logger.error(f"Error listando documentos: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno listando documentos"
        )


@router.get("/{documento_id}", response_model=DocumentoResponse)
async def obtener_documento(
    documento_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtener un documento por ID
    """
    try:
        documento = documento_service.obtener_por_id(db, documento_id)
        if not documento:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Documento no encontrado"
            )
        
        return documento
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo documento {documento_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno obteniendo documento"
        )


@router.put("/{documento_id}", response_model=DocumentoResponse)
async def actualizar_documento(
    documento_id: int,
    documento_update: DocumentoUpdate,
    db: Session = Depends(get_db)
):
    """
    Actualizar un documento
    """
    try:
        documento = documento_service.actualizar(db, documento_id, documento_update)
        if not documento:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Documento no encontrado"
            )
        
        logger.info(f"Documento actualizado exitosamente: {documento_id}")
        return documento
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error actualizando documento {documento_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno actualizando documento"
        )


@router.delete("/{documento_id}")
async def eliminar_documento(
    documento_id: int,
    db: Session = Depends(get_db)
):
    """
    Eliminar (desactivar) un documento
    """
    try:
        success = documento_service.eliminar(db, documento_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Documento no encontrado"
            )
        
        logger.info(f"Documento eliminado exitosamente: {documento_id}")
        return {"message": "Documento eliminado exitosamente"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error eliminando documento {documento_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno eliminando documento"
        )


@router.post("/subir-archivo/{documento_id}")
async def subir_archivo_documento(
    documento_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Subir archivo para un documento
    """
    try:
        # Verificar que el documento existe
        documento = documento_service.obtener_por_id(db, documento_id)
        if not documento:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Documento no encontrado"
            )
        
        # Validar archivo
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nombre de archivo requerido"
            )
        
        # Subir archivo
        archivo_path = await file_handler.guardar_archivo(file, "documentos")
        
        # Actualizar documento con ruta del archivo
        documento_update = DocumentoUpdate(archivo_documento=archivo_path)
        documento = documento_service.actualizar(db, documento_id, documento_update)
        
        logger.info(f"Archivo subido para documento {documento_id}: {archivo_path}")
        return {
            "message": "Archivo subido exitosamente",
            "archivo": archivo_path,
            "documento_id": documento_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error subiendo archivo para documento {documento_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno subiendo archivo"
        )


@router.post("/buscar", response_model=List[DocumentoResponse])
async def buscar_documentos(
    criterio: BusquedaDocumento,
    db: Session = Depends(get_db)
):
    """
    Buscar documentos por criterios
    """
    try:
        documentos = documento_service.buscar(db, criterio)
        return documentos
        
    except Exception as e:
        logger.error(f"Error buscando documentos: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno buscando documentos"
        )


@router.get("/ciudadano/{ciudadano_id}", response_model=List[DocumentoResponse])
async def obtener_documentos_ciudadano(
    ciudadano_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtener todos los documentos de un ciudadano
    """
    try:
        documentos = documento_service.obtener_por_ciudadano(db, ciudadano_id)
        return documentos
        
    except Exception as e:
        logger.error(f"Error obteniendo documentos del ciudadano {ciudadano_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno obteniendo documentos del ciudadano"
        )


@router.get("/verificar/{numero_documento}")
async def verificar_documento(numero_documento: str, db: Session = Depends(get_db)):
    """
    Verificar autenticidad de un documento
    """
    try:
        documento = documento_service.buscar_documento(db, numero_documento)
        if not documento:
            return {
                "valido": False,
                "mensaje": "Documento no encontrado en el sistema"
            }
        
        # Verificar estado
        estado_valido = documento.estado in ["vigente"]
        
        # Si es DNI, verificar con RENIEC
        datos_reniec = None
        if len(numero_documento) == 8 and numero_documento.isdigit():
            from app.services.reniec_service import ReniecService
            reniec_service = ReniecService()
            datos_reniec = await reniec_service.consultar_dni(numero_documento)
        
        return {
            "valido": estado_valido,
            "documento": {
                "numero": documento.numero_documento,
                "tipo": documento.tipo_documento.nombre,
                "estado": documento.estado,
                "fecha_emision": documento.fecha_emision,
                "fecha_vencimiento": documento.fecha_vencimiento
            },
            "reniec": datos_reniec
        }
        
    except Exception as e:
        logger.error(f"Error verificando documento {numero_documento}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno verificando documento"
        )