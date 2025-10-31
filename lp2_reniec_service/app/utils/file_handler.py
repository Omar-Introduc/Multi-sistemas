"""
Utilidades para manejo de archivos
"""

import os
import shutil
from pathlib import Path
from typing import Optional
from fastapi import UploadFile
from loguru import logger
import uuid
from datetime import datetime


class FileHandler:
    """
    Utilidades para manejo de archivos
    """
    
    def __init__(self, base_path: str = "uploads"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        
        # Crear directorios específicos
        self.subdirs = {
            "documentos": self.base_path / "documentos",
            "imagenes": self.base_path / "imagenes", 
            "temporales": self.base_path / "temporales",
            "respaldos": self.base_path / "respaldos"
        }
        
        for subdir in self.subdirs.values():
            subdir.mkdir(parents=True, exist_ok=True)
    
    async def guardar_archivo(self, file: UploadFile, categoria: str = "general") -> str:
        """
        Guardar archivo subido
        """
        try:
            if not file.filename:
                raise ValueError("El archivo debe tener un nombre")
            
            # Generar nombre único
            file_extension = Path(file.filename).suffix
            unique_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}{file_extension}"
            
            # Determinar directorio destino
            destino_dir = self.subdirs.get(categoria, self.base_path)
            file_path = destino_dir / unique_filename
            
            # Guardar archivo
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            logger.info(f"Archivo guardado: {file_path}")
            return str(file_path)
            
        except Exception as e:
            logger.error(f"Error guardando archivo: {e}")
            raise
    
    def eliminar_archivo(self, file_path: str) -> bool:
        """
        Eliminar archivo
        """
        try:
            path = Path(file_path)
            if path.exists() and path.is_file():
                path.unlink()
                logger.info(f"Archivo eliminado: {file_path}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error eliminando archivo {file_path}: {e}")
            return False
    
    def obtener_info_archivo(self, file_path: str) -> Optional[dict]:
        """
        Obtener información de un archivo
        """
        try:
            path = Path(file_path)
            if not path.exists():
                return None
            
            stat = path.stat()
            return {
                "nombre": path.name,
                "ruta_completa": str(path.absolute()),
                "ruta_relativa": str(path),
                "tamaño": stat.st_size,
                "fecha_creacion": datetime.fromtimestamp(stat.st_ctime),
                "fecha_modificacion": datetime.fromtimestamp(stat.st_mtime),
                "extension": path.suffix,
                "es_directorio": path.is_dir(),
                "existe": True
            }
        except Exception as e:
            logger.error(f"Error obteniendo info de archivo {file_path}: {e}")
            return None
    
    def validar_archivo(self, file: UploadFile, tipos_permitidos: list = None, tamaño_maximo: int = 10*1024*1024) -> dict:
        """
        Validar archivo subido
        """
        if not file.filename:
            return {"valido": False, "error": "Archivo sin nombre"}
        
        # Validar extensión
        extension = Path(file.filename).suffix.lower()
        
        if tipos_permitidos and extension not in [ext.lower() for ext in tipos_permitidos]:
            return {
                "valido": False, 
                "error": f"Tipo de archivo no permitido. Permitidos: {', '.join(tipos_permitidos)}"
            }
        
        # Validar tamaño (leer parte del archivo)
        try:
            file.file.seek(0, 2)  # Ir al final
            file_size = file.file.tell()
            file.file.seek(0)  # Volver al inicio
            
            if file_size > tamaño_maximo:
                return {
                    "valido": False,
                    "error": f"Archivo muy grande. Máximo permitido: {tamaño_maximo / (1024*1024):.1f} MB"
                }
        except Exception as e:
            logger.warning(f"No se pudo validar el tamaño del archivo: {e}")
        
        return {"valido": True}
    
    def crear_directorio_respaldos(self, nombre_backup: str) -> str:
        """
        Crear directorio de respaldos
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_dir = self.subdirs["respaldos"] / f"{nombre_backup}_{timestamp}"
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        return str(backup_dir)
    
    def limpiar_archivos_temporales(self, dias_antiguedad: int = 7):
        """
        Limpiar archivos temporales antiguos
        """
        try:
            temp_dir = self.subdirs["temporales"]
            cutoff_time = datetime.now().timestamp() - (dias_antiguedad * 24 * 60 * 60)
            
            archivos_eliminados = 0
            for file_path in temp_dir.rglob("*"):
                if file_path.is_file() and file_path.stat().st_mtime < cutoff_time:
                    file_path.unlink()
                    archivos_eliminados += 1
            
            logger.info(f"Archivos temporales eliminados: {archivos_eliminados}")
            return archivos_eliminados
            
        except Exception as e:
            logger.error(f"Error limpiando archivos temporales: {e}")
            return 0
    
    def obtener_espacio_disponible(self) -> dict:
        """
        Obtener información del espacio en disco
        """
        try:
            stat = shutil.disk_usage(self.base_path)
            return {
                "total": stat.total,
                "usado": stat.used,
                "libre": stat.free,
                "porcentaje_usado": (stat.used / stat.total) * 100
            }
        except Exception as e:
            logger.error(f"Error obteniendo espacio en disco: {e}")
            return {}