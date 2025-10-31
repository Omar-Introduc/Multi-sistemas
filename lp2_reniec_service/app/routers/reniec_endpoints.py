"""
Router para endpoints de RENIEC
"""

from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import List, Optional
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.models.schemas import (
    CiudadanoCreate, CiudadanoResponse, CiudadanoUpdate,
    BusquedaCiudadano, ResponseSuccess, ResponseError
)
from app.services.reniec_service import ReniecService
from app.services.ciudadano_service import CiudadanoService
from loguru import logger

router = APIRouter()
reniec_service = ReniecService()
ciudadano_service = CiudadanoService()


@router.get("/consulta-dni/{dni}", response_model=CiudadanoResponse)
async def consultar_dni(dni: str, db: Session = Depends(get_db)):
    """
    Consultar información por DNI usando RENIEC
    """
    try:
        logger.info(f"Consultando DNI: {dni}")
        
        # Validar DNI
        if len(dni) != 8 or not dni.isdigit():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="DNI debe tener exactamente 8 dígitos"
            )
        
        # Consultar RENIEC
        datos_reniec = await reniec_service.consultar_dni(dni)
        
        if not datos_reniec:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No se encontraron datos para el DNI especificado"
            )
        
        # Buscar o crear ciudadano
        ciudadano = ciudadano_service.buscar_por_documento(db, dni)
        
        if not ciudadano:
            # Crear nuevo ciudadano con datos de RENIEC
            ciudadano_data = CiudadanoCreate(
                documento_identidad=dni,
                nombres=datos_reniec.get("nombres", ""),
                apellidos=f"{datos_reniec.get('apellido_paterno', '')} {datos_reniec.get('apellido_materno', '')}",
                fecha_nacimiento=datos_reniec.get("fecha_nacimiento"),
                lugar_nacimiento=datos_reniec.get("lugar_nacimiento", "No especificado"),
                genero=datos_reniec.get("genero", "M"),
                estado_civil="soltero",  # RENIEC no siempre proporciona este dato
                direccion=datos_reniec.get("direccion", "")
            )
            
            ciudadano = ciudadano_service.crear(db, ciudadano_data)
        
        return ciudadano
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error consultando DNI {dni}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno consultando información de RENIEC"
        )


@router.post("/verificar-dni", response_model=ResponseSuccess)
async def verificar_dni(datos: dict, db: Session = Depends(get_db)):
    """
    Verificar autenticidad de DNI
    """
    try:
        dni = datos.get("dni")
        if not dni:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="DNI es requerido"
            )
        
        # Verificar con RENIEC
        resultado = await reniec_service.verificar_dni(dni)
        
        return {
            "message": "Verificación completada",
            "data": {
                "dni": dni,
                "valido": resultado.get("valido", False),
                "datos": resultado.get("datos", {})
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verificando DNI: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno verificando DNI"
        )


@router.get("/documento/{numero}", response_model=dict)
async def consultar_documento(numero: str, db: Session = Depends(get_db)):
    """
    Consultar información de un documento
    """
    try:
        logger.info(f"Consultando documento: {numero}")
        
        # Buscar documento en base de datos
        documento = ciudadano_service.buscar_documento(db, numero)
        
        if not documento:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Documento no encontrado"
            )
        
        # Si el documento es un DNI, complementar con datos de RENIEC
        if len(numero) == 8 and numero.isdigit():
            datos_reniec = await reniec_service.consultar_dni(numero)
            return {
                "documento": {
                    "numero": numero,
                    "tipo": documento.tipo_documento.nombre,
                    "estado": documento.estado,
                    "fecha_emision": documento.fecha_emision,
                    "fecha_vencimiento": documento.fecha_vencimiento
                },
                "ciudadano": {
                    "nombres": documento.ciudadano.nombres,
                    "apellidos": documento.ciudadano.apellidos,
                    "genero": documento.ciudadano.genero
                },
                "reniec": datos_reniec
            }
        
        return {
            "documento": {
                "numero": numero,
                "tipo": documento.tipo_documento.nombre,
                "estado": documento.estado,
                "fecha_emision": documento.fecha_emision,
                "fecha_vencimiento": documento.fecha_vencimiento
            },
            "ciudadano": {
                "nombres": documento.ciudadano.nombres,
                "apellidos": documento.ciudadano.apellidos,
                "genero": documento.ciudadano.genero
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error consultando documento {numero}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno consultando documento"
        )


@router.get("/estadisticas", response_model=dict)
async def obtener_estadisticas(db: Session = Depends(get_db)):
    """
    Obtener estadísticas del servicio RENIEC
    """
    try:
        stats = await reniec_service.obtener_estadisticas()
        db_stats = ciudadano_service.obtener_estadisticas(db)
        
        return {
            "reniec_api": stats,
            "base_datos": db_stats,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno obteniendo estadísticas"
        )