"""
Servicio para gestión de ciudadanos
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional
from datetime import datetime
from loguru import logger

from app.models.schemas import (
    CiudadanoCreate, CiudadanoUpdate, CiudadanoResponse,
    BusquedaCiudadano
)


class CiudadanoService:
    """
    Servicio para operaciones relacionadas con ciudadanos
    """
    
    def crear(self, db: Session, ciudadano_data: CiudadanoCreate) -> CiudadanoResponse:
        """
        Crear un nuevo ciudadano
        """
        try:
            from app.models.reniec_models import Ciudadano
            
            db_ciudadano = Ciudadano(
                documento_identidad=ciudadano_data.documento_identidad,
                nombres=ciudadano_data.nombres,
                apellidos=ciudadano_data.apellidos,
                fecha_nacimiento=ciudadano_data.fecha_nacimiento,
                lugar_nacimiento=ciudadano_data.lugar_nacimiento,
                genero=ciudadano_data.genero.value if hasattr(ciudadano_data.genero, 'value') else ciudadano_data.genero,
                estado_civil=ciudadano_data.estado_civil.value if ciudadano_data.estado_civil and hasattr(ciudadano_data.estado_civil, 'value') else ciudadano_data.estado_civil,
                direccion=ciudadano_data.direccion,
                telefono=ciudadano_data.telefono,
                email=ciudadano_data.email
            )
            
            db.add(db_ciudadano)
            db.commit()
            db.refresh(db_ciudadano)
            
            logger.info(f"Ciudadano creado: {db_ciudadano.id}")
            return db_ciudadano
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error creando ciudadano: {e}")
            raise
    
    def obtener_por_id(self, db: Session, ciudadano_id: int) -> Optional[CiudadanoResponse]:
        """
        Obtener ciudadano por ID
        """
        try:
            from app.models.reniec_models import Ciudadano
            
            return db.query(Ciudadano).filter(
                and_(
                    Ciudadano.id == ciudadano_id,
                    Ciudadano.activo == True
                )
            ).first()
            
        except Exception as e:
            logger.error(f"Error obteniendo ciudadano {ciudadano_id}: {e}")
            return None
    
    def buscar_por_documento(self, db: Session, documento_identidad: str) -> Optional[CiudadanoResponse]:
        """
        Buscar ciudadano por documento de identidad
        """
        try:
            from app.models.reniec_models import Ciudadano
            
            return db.query(Ciudadano).filter(
                and_(
                    Ciudadano.documento_identidad == documento_identidad,
                    Ciudadano.activo == True
                )
            ).first()
            
        except Exception as e:
            logger.error(f"Error buscando ciudadano por documento {documento_identidad}: {e}")
            return None
    
    def listar(self, db: Session, skip: int = 0, limit: int = 100, activo: Optional[bool] = True) -> List[CiudadanoResponse]:
        """
        Listar ciudadanos con paginación
        """
        try:
            from app.models.reniec_models import Ciudadano
            
            query = db.query(Ciudadano)
            
            if activo is not None:
                query = query.filter(Ciudadano.activo == activo)
            else:
                query = query.filter(Ciudadano.activo == True)
            
            return query.offset(skip).limit(limit).all()
            
        except Exception as e:
            logger.error(f"Error listando ciudadanos: {e}")
            return []
    
    def actualizar(self, db: Session, ciudadano_id: int, ciudadano_update: CiudadanoUpdate) -> Optional[CiudadanoResponse]:
        """
        Actualizar un ciudadano
        """
        try:
            from app.models.reniec_models import Ciudadano
            
            db_ciudadano = db.query(Ciudadano).filter(
                and_(
                    Ciudadano.id == ciudadano_id,
                    Ciudadano.activo == True
                )
            ).first()
            
            if not db_ciudadano:
                return None
            
            update_data = ciudadano_update.dict(exclude_unset=True)
            
            for field, value in update_data.items():
                if hasattr(db_ciudadano, field):
                    if field == 'genero' and hasattr(value, 'value'):
                        value = value.value
                    elif field == 'estado_civil' and value and hasattr(value, 'value'):
                        value = value.value
                    
                    setattr(db_ciudadano, field, value)
            
            db_ciudadano.fecha_actualizacion = datetime.utcnow()
            db.commit()
            db.refresh(db_ciudadano)
            
            logger.info(f"Ciudadano actualizado: {ciudadano_id}")
            return db_ciudadano
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error actualizando ciudadano {ciudadano_id}: {e}")
            return None
    
    def eliminar(self, db: Session, ciudadano_id: int) -> bool:
        """
        Eliminar (desactivar) un ciudadano
        """
        try:
            from app.models.reniec_models import Ciudadano
            
            db_ciudadano = db.query(Ciudadano).filter(
                and_(
                    Ciudadano.id == ciudadano_id,
                    Ciudadano.activo == True
                )
            ).first()
            
            if not db_ciudadano:
                return False
            
            db_ciudadano.activo = False
            db_ciudadano.fecha_actualizacion = datetime.utcnow()
            db.commit()
            
            logger.info(f"Ciudadano eliminado (desactivado): {ciudadano_id}")
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error eliminando ciudadano {ciudadano_id}: {e}")
            return False
    
    def buscar(self, db: Session, criterio: BusquedaCiudadano) -> List[CiudadanoResponse]:
        """
        Buscar ciudadanos por criterios
        """
        try:
            from app.models.reniec_models import Ciudadano
            
            query = db.query(Ciudadano).filter(Ciudadano.activo == True)
            
            if criterio.documento_identidad:
                query = query.filter(Ciudadano.documento_identidad == criterio.documento_identidad)
            
            if criterio.email:
                query = query.filter(Ciudadano.email == criterio.email)
            
            if criterio.nombres:
                query = query.filter(Ciudadano.nombres.ilike(f"%{criterio.nombres}%"))
            
            if criterio.apellidos:
                query = query.filter(Ciudadano.apellidos.ilike(f"%{criterio.apellidos}%"))
            
            return query.all()
            
        except Exception as e:
            logger.error(f"Error buscando ciudadanos: {e}")
            return []
    
    def existe_por_documento(self, db: Session, documento_identidad: str) -> bool:
        """
        Verificar si existe un ciudadano por documento de identidad
        """
        try:
            from app.models.reniec_models import Ciudadano
            
            return db.query(Ciudadano).filter(
                and_(
                    Ciudadano.documento_identidad == documento_identidad,
                    Ciudadano.activo == True
                )
            ).first() is not None
            
        except Exception as e:
            logger.error(f"Error verificando existencia de ciudadano: {e}")
            return False
    
    def obtener_documentos(self, db: Session, ciudadano_id: int) -> List:
        """
        Obtener documentos de un ciudadano
        """
        try:
            from app.models.reniec_models import Ciudadano, Documento
            
            ciudadano = db.query(Ciudadano).filter(
                and_(
                    Ciudadano.id == ciudadano_id,
                    Ciudadano.activo == True
                )
            ).first()
            
            if not ciudadano:
                return []
            
            return ciudadano.documentos
            
        except Exception as e:
            logger.error(f"Error obteniendo documentos del ciudadano {ciudadano_id}: {e}")
            return []
    
    def obtener_solicitudes(self, db: Session, ciudadano_id: int) -> List:
        """
        Obtener solicitudes de un ciudadano
        """
        try:
            from app.models.reniec_models import Ciudadano, Solicitud
            
            ciudadano = db.query(Ciudadano).filter(
                and_(
                    Ciudadano.id == ciudadano_id,
                    Ciudadano.activo == True
                )
            ).first()
            
            if not ciudadano:
                return []
            
            return ciudadano.solicitudes if hasattr(ciudadano, 'solicitudes') else []
            
        except Exception as e:
            logger.error(f"Error obteniendo solicitudes del ciudadano {ciudadano_id}: {e}")
            return []
    
    def obtener_estadisticas(self, db: Session) -> dict:
        """
        Obtener estadísticas de ciudadanos
        """
        try:
            from app.models.reniec_models import Ciudadano
            
            total_ciudadanos = db.query(Ciudadano).filter(Ciudadano.activo == True).count()
            total_inactivos = db.query(Ciudadano).filter(Ciudadano.activo == False).count()
            
            return {
                "total_activos": total_ciudadanos,
                "total_inactivos": total_inactivos,
                "total_general": total_ciudadanos + total_inactivos
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas: {e}")
            return {"error": str(e)}