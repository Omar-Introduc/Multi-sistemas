"""
Servicio para gestión de documentos
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional
from datetime import datetime, date
from loguru import logger

from app.models.schemas import (
    DocumentoCreate, DocumentoUpdate, DocumentoResponse,
    BusquedaDocumento
)


class DocumentoService:
    """
    Servicio para operaciones relacionadas con documentos
    """
    
    def crear(self, db: Session, documento_data: DocumentoCreate) -> DocumentoResponse:
        """
        Crear un nuevo documento
        """
        try:
            from app.models.reniec_models import Documento
            
            # Calcular fecha de vencimiento si aplica
            fecha_vencimiento = documento_data.fecha_vencimiento
            if not fecha_vencimiento and hasattr(documento_data, 'tipo_documento_id'):
                # Se podría calcular basándose en el tipo de documento
                pass
            
            db_documento = Documento(
                numero_documento=documento_data.numero_documento,
                ciudadano_id=documento_data.ciudadano_id,
                tipo_documento_id=documento_data.tipo_documento_id,
                fecha_emision=documento_data.fecha_emision,
                fecha_vencimiento=fecha_vencimiento,
                estado=documento_data.estado.value if hasattr(documento_data.estado, 'value') else documento_data.estado,
                archivo_documento=documento_data.archivo_documento,
                metadatos=documento_data.metadatos
            )
            
            db.add(db_documento)
            db.commit()
            db.refresh(db_documento)
            
            logger.info(f"Documento creado: {db_documento.id}")
            return db_documento
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error creando documento: {e}")
            raise
    
    def obtener_por_id(self, db: Session, documento_id: int) -> Optional[DocumentoResponse]:
        """
        Obtener documento por ID
        """
        try:
            from app.models.reniec_models import Documento
            
            return db.query(Documento).filter(
                and_(
                    Documento.id == documento_id,
                    Documento.activo == True
                )
            ).first()
            
        except Exception as e:
            logger.error(f"Error obteniendo documento {documento_id}: {e}")
            return None
    
    def buscar_documento(self, db: Session, numero_documento: str) -> Optional[DocumentoResponse]:
        """
        Buscar documento por número
        """
        try:
            from app.models.reniec_models import Documento
            
            return db.query(Documento).filter(
                and_(
                    Documento.numero_documento == numero_documento,
                    Documento.activo == True
                )
            ).first()
            
        except Exception as e:
            logger.error(f"Error buscando documento por número {numero_documento}: {e}")
            return None
    
    def listar(self, db: Session, skip: int = 0, limit: int = 100) -> List[DocumentoResponse]:
        """
        Listar documentos con paginación
        """
        try:
            from app.models.reniec_models import Documento
            
            return db.query(Documento).filter(
                Documento.activo == True
            ).offset(skip).limit(limit).all()
            
        except Exception as e:
            logger.error(f"Error listando documentos: {e}")
            return []
    
    def actualizar(self, db: Session, documento_id: int, documento_update: DocumentoUpdate) -> Optional[DocumentoResponse]:
        """
        Actualizar un documento
        """
        try:
            from app.models.reniec_models import Documento
            
            db_documento = db.query(Documento).filter(
                and_(
                    Documento.id == documento_id,
                    Documento.activo == True
                )
            ).first()
            
            if not db_documento:
                return None
            
            update_data = documento_update.dict(exclude_unset=True)
            
            for field, value in update_data.items():
                if hasattr(db_documento, field):
                    if field == 'estado' and hasattr(value, 'value'):
                        value = value.value
                    
                    setattr(db_documento, field, value)
            
            db_documento.fecha_actualizacion = datetime.utcnow()
            db.commit()
            db.refresh(db_documento)
            
            logger.info(f"Documento actualizado: {documento_id}")
            return db_documento
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error actualizando documento {documento_id}: {e}")
            return None
    
    def eliminar(self, db: Session, documento_id: int) -> bool:
        """
        Eliminar (desactivar) un documento
        """
        try:
            from app.models.reniec_models import Documento
            
            db_documento = db.query(Documento).filter(
                and_(
                    Documento.id == documento_id,
                    Documento.activo == True
                )
            ).first()
            
            if not db_documento:
                return False
            
            db_documento.activo = False
            db_documento.fecha_actualizacion = datetime.utcnow()
            db.commit()
            
            logger.info(f"Documento eliminado (desactivado): {documento_id}")
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error eliminando documento {documento_id}: {e}")
            return False
    
    def buscar(self, db: Session, criterio: BusquedaDocumento) -> List[DocumentoResponse]:
        """
        Buscar documentos por criterios
        """
        try:
            from app.models.reniec_models import Documento
            
            query = db.query(Documento).filter(Documento.activo == True)
            
            if criterio.numero_documento:
                query = query.filter(Documento.numero_documento.ilike(f"%{criterio.numero_documento}%"))
            
            if criterio.ciudadano_id:
                query = query.filter(Documento.ciudadano_id == criterio.ciudadano_id)
            
            if criterio.estado:
                estado_value = criterio.estado.value if hasattr(criterio.estado, 'value') else criterio.estado
                query = query.filter(Documento.estado == estado_value)
            
            return query.all()
            
        except Exception as e:
            logger.error(f"Error buscando documentos: {e}")
            return []
    
    def obtener_por_ciudadano(self, db: Session, ciudadano_id: int) -> List[DocumentoResponse]:
        """
        Obtener documentos de un ciudadano
        """
        try:
            from app.models.reniec_models import Documento
            
            return db.query(Documento).filter(
                and_(
                    Documento.ciudadano_id == ciudadano_id,
                    Documento.activo == True
                )
            ).all()
            
        except Exception as e:
            logger.error(f"Error obteniendo documentos del ciudadano {ciudadano_id}: {e}")
            return []
    
    def buscar_ciudadano(self, db: Session, ciudadano_id: int) -> Optional:
        """
        Buscar ciudadano por ID
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
            logger.error(f"Error buscando ciudadano {ciudadano_id}: {e}")
            return None
    
    def buscar_tipo_documento(self, db: Session, tipo_documento_id: int) -> Optional:
        """
        Buscar tipo de documento por ID
        """
        try:
            from app.models.reniec_models import TipoDocumento
            
            return db.query(TipoDocumento).filter(
                and_(
                    TipoDocumento.id == tipo_documento_id,
                    TipoDocumento.activo == True
                )
            ).first()
            
        except Exception as e:
            logger.error(f"Error buscando tipo de documento {tipo_documento_id}: {e}")
            return None
    
    def existe_documento(self, db: Session, numero_documento: str) -> bool:
        """
        Verificar si existe un documento por número
        """
        try:
            from app.models.reniec_models import Documento
            
            return db.query(Documento).filter(
                and_(
                    Documento.numero_documento == numero_documento,
                    Documento.activo == True
                )
            ).first() is not None
            
        except Exception as e:
            logger.error(f"Error verificando existencia de documento: {e}")
            return False
    
    def obtener_documentos_vencidos(self, db: Session) -> List[DocumentoResponse]:
        """
        Obtener documentos próximos a vencer o vencidos
        """
        try:
            from app.models.reniec_models import Documento
            
            hoy = date.today()
            # Documentos vencidos
            documentos_vencidos = db.query(Documento).filter(
                and_(
                    Documento.fecha_vencimiento < hoy,
                    Documento.estado == "vigente",
                    Documento.activo == True
                )
            ).all()
            
            return documentos_vencidos
            
        except Exception as e:
            logger.error(f"Error obteniendo documentos vencidos: {e}")
            return []
    
    def obtener_estadisticas(self, db: Session) -> dict:
        """
        Obtener estadísticas de documentos
        """
        try:
            from app.models.reniec_models import Documento
            
            total = db.query(Documento).filter(Documento.activo == True).count()
            vigentes = db.query(Documento).filter(
                and_(Documento.estado == "vigente", Documento.activo == True)
            ).count()
            vencidos = db.query(Documento).filter(
                and_(Documento.estado == "vencido", Documento.activo == True)
            ).count()
            
            return {
                "total_documentos": total,
                "documentos_vigentes": vigentes,
                "documentos_vencidos": vencidos,
                "otros_estados": total - vigentes - vencidos
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas de documentos: {e}")
            return {"error": str(e)}