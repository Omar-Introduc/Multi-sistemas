"""
Servicio de logging y auditoría para el sistema de validación RENIEC
Maneja todos los aspectos de registro de eventos, errores y auditoría
"""

import logging
import json
import logging.handlers
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from pathlib import Path
import threading
import os
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib

# Importar DatabaseService si está disponible, o usar un mock
try:
    from .DatabaseService import DatabaseService
except ImportError:
    DatabaseService = None

class NivelLog(Enum):
    """Niveles de log del sistema"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class TipoEvento(Enum):
    """Tipos de eventos del sistema"""
    VALIDACION_INICIADA = "VALIDACION_INICIADA"
    VALIDACION_EXITOSA = "VALIDACION_EXITOSA"
    VALIDACION_FALLIDA = "VALIDACION_FALLIDA"
    ERROR_VALIDACION = "ERROR_VALIDACION"
    CONSULTA_CIUDADANO = "CONSULTA_CIUDADANO"
    REGISTRO_SESSION = "REGISTRO_SESSION"
    ERROR_DB = "ERROR_DB"
    ERROR_RABBIT = "ERROR_RABBIT"
    MENSAJE_ENVIADO = "MENSAJE_ENVIADO"
    MENSAJE_RECIBIDO = "MENSAJE_RECIBIDO"
    SESSION_CREADA = "SESSION_CREADA"
    SESSION_VALIDADA = "SESSION_VALIDADA"
    SESSION_EXPIRADA = "SESSION_EXPIRADA"

@dataclass
class RegistroAuditoria:
    """Registro de auditoría estructurado"""
    evento_id: str
    tipo_evento: str
    timestamp: datetime
    usuario: Optional[str]
    ip_origen: Optional[str]
    datos_evento: Dict[str, Any]
    session_id: Optional[str]
    resultado: str
    duracion_ms: Optional[int]
    hash_integridad: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el registro a diccionario"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data

@dataclass
class RegistroError:
    """Registro de error estructurado"""
    error_id: str
    tipo_error: str
    mensaje: str
    stack_trace: Optional[str]
    timestamp: datetime
    contexto: Dict[str, Any]
    severidad: str
    resuelto: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el registro a diccionario"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data

class LogService:
    """Servicio centralizado de logging y auditoría"""
    
    def __init__(self, database_service: Optional[DatabaseService] = None,
                 log_level: str = "INFO",
                 log_dir: str = "./logs",
                 max_log_size: int = 50 * 1024 * 1024,  # 50MB
                 backup_count: int = 10,
                 enable_audit_db: bool = True,
                 enable_file_logging: bool = True):
        """
        Inicializa el servicio de logging
        
        Args:
            database_service: Servicio de base de datos para auditoría
            log_level: Nivel de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_dir: Directorio para archivos de log
            max_log_size: Tamaño máximo de archivo de log
            backup_count: Número de backups a mantener
            enable_audit_db: Habilitar auditoría en base de datos
            enable_file_logging: Habilitar logging en archivos
        """
        self.database_service = database_service
        self.log_level = NivelLog(log_level.upper())
        self.log_dir = Path(log_dir)
        self.max_log_size = max_log_size
        self.backup_count = backup_count
        self.enable_audit_db = enable_audit_db
        self.enable_file_logging = enable_file_logging
        
        # Crear directorio de logs
        if self.enable_file_logging:
            self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Configurar logging principal
        self._configurar_logging()
        
        # Contadores y estadísticas
        self._contadores_eventos = {}
        self._lock = threading.Lock()
        
        # Configuración de patrones de filtrado
        self._patrones_sensibles = [
            "password", "token", "clave", "contraseña", "pwd", "auth",
            "dni", "documento", "numero_documento"  # Para PII
        ]
    
    def _configurar_logging(self):
        """Configura el sistema de logging"""
        # Crear formatter personalizado
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Logger principal
        self.logger = logging.getLogger("reniec_service")
        self.logger.setLevel(getattr(logging, self.log_level.value))
        
        # Limpiar handlers existentes
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # Handler para archivo general
        if self.enable_file_logging:
            general_log_file = self.log_dir / "reniec_general.log"
            general_handler = logging.handlers.RotatingFileHandler(
                general_log_file,
                maxBytes=self.max_log_size,
                backupCount=self.backup_count,
                encoding='utf-8'
            )
            general_handler.setLevel(logging.INFO)
            general_handler.setFormatter(formatter)
            self.logger.addHandler(general_handler)
        
        # Handler para archivo de errores
        if self.enable_file_logging:
            error_log_file = self.log_dir / "reniec_errors.log"
            error_handler = logging.handlers.RotatingFileHandler(
                error_log_file,
                maxBytes=self.max_log_size,
                backupCount=self.backup_count,
                encoding='utf-8'
            )
            error_handler.setLevel(logging.ERROR)
            error_handler.setFormatter(formatter)
            self.logger.addHandler(error_handler)
        
        # Handler para archivo de auditoría
        if self.enable_file_logging:
            audit_log_file = self.log_dir / "reniec_audit.log"
            audit_handler = logging.handlers.RotatingFileHandler(
                audit_log_file,
                maxBytes=self.max_log_size,
                backupCount=self.backup_count,
                encoding='utf-8'
            )
            audit_handler.setLevel(logging.DEBUG)
            audit_handler.setFormatter(formatter)
            self.logger.addHandler(audit_handler)
        
        # Handler para consola (solo en desarrollo)
        if self.log_level == NivelLog.DEBUG:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.DEBUG)
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
    
    def registrarEvento(self, tipo_evento: str, mensaje: str, datos_adicionales: Optional[Dict[str, Any]] = None,
                       usuario: Optional[str] = None, ip_origen: Optional[str] = None,
                       session_id: Optional[str] = None) -> str:
        """
        Registra un evento en el sistema de auditoría
        
        Args:
            tipo_evento: Tipo de evento (usar constantes de TipoEvento)
            mensaje: Descripción del evento
            datos_adicionales: Datos adicionales del evento
            usuario: Usuario que realizó la acción
            ip_origen: IP de origen de la solicitud
            session_id: ID de la sesión
            
        Returns:
            ID del evento registrado
        """
        try:
            evento_id = self._generar_id_evento()
            timestamp = datetime.now()
            
            # Preparar datos del evento
            datos_evento = {
                "mensaje": mensaje,
                "tipo_evento": tipo_evento,
                **(datos_adicionales or {})
            }
            
            # Filtrar datos sensibles
            datos_evento = self._filtrar_datos_sensibles(datos_evento)
            
            # Crear registro de auditoría
            registro = RegistroAuditoria(
                evento_id=evento_id,
                tipo_evento=tipo_evento,
                timestamp=timestamp,
                usuario=usuario,
                ip_origen=ip_origen,
                datos_evento=datos_evento,
                session_id=session_id,
                resultado="exito",
                duracion_ms=None,
                hash_integridad=self._calcular_hash_integridad(datos_evento, timestamp)
            )
            
            # Log del evento
            self.logger.info(f"EVENTO: {tipo_evento} - {mensaje}")
            
            # Guardar en base de datos si está habilitada
            if self.enable_audit_db:
                self._guardar_evento_db(registro)
            
            # Guardar en archivo de auditoría
            if self.enable_file_logging:
                self._guardar_evento_archivo(registro)
            
            # Actualizar contadores
            self._actualizar_contador(tipo_evento)
            
            self.logger.debug(f"Evento registrado: {evento_id}")
            return evento_id
            
        except Exception as e:
            self.logger.error(f"Error registrando evento {tipo_evento}: {str(e)}")
            return ""
    
    def registrarError(self, tipo_error: str, mensaje: str, contexto: Optional[Dict[str, Any]] = None,
                      stack_trace: Optional[str] = None, severidad: str = "ERROR") -> str:
        """
        Registra un error en el sistema
        
        Args:
            tipo_error: Tipo de error
            mensaje: Descripción del error
            contexto: Contexto adicional del error
            stack_trace: Traceback del error
            severidad: Severidad del error (WARNING, ERROR, CRITICAL)
            
        Returns:
            ID del error registrado
        """
        try:
            error_id = self._generar_id_error()
            timestamp = datetime.now()
            
            # Preparar contexto del error
            contexto_error = {
                "tipo_error": tipo_error,
                "mensaje": mensaje,
                **(contexto or {})
            }
            
            # Filtrar datos sensibles del contexto
            contexto_error = self._filtrar_datos_sensibles(contexto_error)
            
            # Crear registro de error
            registro = RegistroError(
                error_id=error_id,
                tipo_error=tipo_error,
                mensaje=mensaje,
                stack_trace=stack_trace,
                timestamp=timestamp,
                contexto=contexto_error,
                severidad=severidad,
                resuelto=False
            )
            
            # Log del error
            nivel_log = getattr(logging, severidad.upper())
            self.logger.log(nivel_log, f"ERROR: {tipo_error} - {mensaje}")
            
            # Guardar en base de datos si está habilitada
            if self.enable_audit_db:
                self._guardar_error_db(registro)
            
            # Guardar en archivo de errores
            if self.enable_file_logging:
                self._guardar_error_archivo(registro)
            
            # Actualizar contadores
            self._actualizar_contador(f"ERROR_{tipo_error}")
            
            self.logger.error(f"Error registrado: {error_id}")
            return error_id
            
        except Exception as e:
            self.logger.error(f"Error registrando error {tipo_error}: {str(e)}")
            return ""
    
    def registrarMetrica(self, nombre_metrica: str, valor: float, unidad: str = "count",
                        etiquetas: Optional[Dict[str, str]] = None) -> str:
        """
        Registra una métrica del sistema
        
        Args:
            nombre_metrica: Nombre de la métrica
            valor: Valor de la métrica
            unidad: Unidad de medida
            etiquetas: Etiquetas adicionales
            
        Returns:
            ID de la métrica registrada
        """
        try:
            metrica_id = self._generar_id_evento()
            timestamp = datetime.now()
            
            datos_metrica = {
                "nombre": nombre_metrica,
                "valor": valor,
                "unidad": unidad,
                "etiquetas": etiquetas or {}
            }
            
            # Log de la métrica
            self.logger.debug(f"MÉTRICA: {nombre_metrica} = {valor} {unidad}")
            
            # Guardar métrica
            if self.enable_audit_db:
                self._guardar_metrica_db(metrica_id, timestamp, datos_metrica)
            
            # Actualizar contadores
            self._actualizar_contador(f"METRICA_{nombre_metrica}", valor)
            
            return metrica_id
            
        except Exception as e:
            self.logger.error(f"Error registrando métrica {nombre_metrica}: {str(e)}")
            return ""
    
    def obtenerEventos(self, filtro: Optional[Dict[str, Any]] = None, 
                      limite: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Obtiene eventos de auditoría de la base de datos
        
        Args:
            filtro: Filtros a aplicar
            limite: Número máximo de registros
            offset: Offset para paginación
            
        Returns:
            Lista de eventos
        """
        if not self.enable_audit_db or not self.database_service:
            return []
        
        try:
            # Construir query dinámico
            where_conditions = []
            parametros = []
            
            if filtro:
                if "tipo_evento" in filtro:
                    where_conditions.append("tipo_evento = %s")
                    parametros.append(filtro["tipo_evento"])
                
                if "fecha_desde" in filtro:
                    where_conditions.append("timestamp >= %s")
                    parametros.append(filtro["fecha_desde"])
                
                if "fecha_hasta" in filtro:
                    where_conditions.append("timestamp <= %s")
                    parametros.append(filtro["fecha_hasta"])
                
                if "usuario" in filtro:
                    where_conditions.append("usuario = %s")
                    parametros.append(filtro["usuario"])
            
            where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
            
            query = f"""
            SELECT evento_id, tipo_evento, timestamp, usuario, ip_origen, 
                   datos_evento, session_id, resultado, duracion_ms, hash_integridad
            FROM auditoria_eventos 
            WHERE {where_clause}
            ORDER BY timestamp DESC
            LIMIT %s OFFSET %s
            """
            
            parametros.extend([limite, offset])
            
            resultados = self.database_service.ejecutarConsulta(query, tuple(parametros))
            
            return resultados
            
        except Exception as e:
            self.logger.error(f"Error obteniendo eventos: {str(e)}")
            return []
    
    def obtenerErrores(self, filtro: Optional[Dict[str, Any]] = None,
                      limite: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Obtiene errores de la base de datos
        
        Args:
            filtro: Filtros a aplicar
            limite: Número máximo de registros
            offset: Offset para paginación
            
        Returns:
            Lista de errores
        """
        if not self.enable_audit_db or not self.database_service:
            return []
        
        try:
            # Construir query dinámico
            where_conditions = []
            parametros = []
            
            if filtro:
                if "tipo_error" in filtro:
                    where_conditions.append("tipo_error = %s")
                    parametros.append(filtro["tipo_error"])
                
                if "fecha_desde" in filtro:
                    where_conditions.append("timestamp >= %s")
                    parametros.append(filtro["fecha_desde"])
                
                if "fecha_hasta" in filtro:
                    where_conditions.append("timestamp <= %s")
                    parametros.append(filtro["fecha_hasta"])
                
                if "severidad" in filtro:
                    where_conditions.append("severidad = %s")
                    parametros.append(filtro["severidad"])
            
            where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
            
            query = f"""
            SELECT error_id, tipo_error, mensaje, stack_trace, timestamp, 
                   contexto, severidad, resuelto
            FROM auditoria_errores 
            WHERE {where_clause}
            ORDER BY timestamp DESC
            LIMIT %s OFFSET %s
            """
            
            parametros.extend([limite, offset])
            
            resultados = self.database_service.ejecutarConsulta(query, tuple(parametros))
            
            return resultados
            
        except Exception as e:
            self.logger.error(f"Error obteniendo errores: {str(e)}")
            return []
    
    def obtenerEstadisticas(self, periodo_horas: int = 24) -> Dict[str, Any]:
        """
        Obtiene estadísticas del sistema en un período
        
        Args:
            periodo_horas: Período en horas
            
        Returns:
            Diccionario con estadísticas
        """
        try:
            fecha_inicio = datetime.now() - timedelta(hours=periodo_horas)
            
            # Eventos por tipo
            query_eventos = """
            SELECT tipo_evento, COUNT(*) as cantidad
            FROM auditoria_eventos 
            WHERE timestamp >= %s
            GROUP BY tipo_evento
            ORDER BY cantidad DESC
            """
            
            eventos_por_tipo = self.database_service.ejecutarConsulta(
                query_eventos, (fecha_inicio,)
            ) if self.enable_audit_db and self.database_service else []
            
            # Errores por tipo
            query_errores = """
            SELECT tipo_error, COUNT(*) as cantidad
            FROM auditoria_errores 
            WHERE timestamp >= %s
            GROUP BY tipo_error
            ORDER BY cantidad DESC
            """
            
            errores_por_tipo = self.database_service.ejecutarConsulta(
                query_errores, (fecha_inicio,)
            ) if self.enable_audit_db and self.database_service else []
            
            # Estadísticas generales
            estadisticas = {
                "periodo_horas": periodo_horas,
                "fecha_inicio": fecha_inicio.isoformat(),
                "eventos_total": sum(e["cantidad"] for e in eventos_por_tipo),
                "errores_total": sum(e["cantidad"] for e in errores_por_tipo),
                "eventos_por_tipo": {e["tipo_evento"]: e["cantidad"] for e in eventos_por_tipo},
                "errores_por_tipo": {e["tipo_error"]: e["cantidad"] for e in errores_por_tipo},
                "contadores_actuales": self._contadores_eventos.copy()
            }
            
            return estadisticas
            
        except Exception as e:
            self.logger.error(f"Error obteniendo estadísticas: {str(e)}")
            return {}
    
    def limpiar_logs_antiguos(self, dias_retencion: int = 30) -> int:
        """
        Limpia logs y registros antiguos
        
        Args:
            dias_retencion: Días de retención de logs
            
        Returns:
            Número de registros eliminados
        """
        try:
            fecha_limite = datetime.now() - timedelta(days=dias_retencion)
            registros_eliminados = 0
            
            if self.enable_audit_db and self.database_service:
                # Limpiar eventos antiguos
                query_eventos = "DELETE FROM auditoria_eventos WHERE timestamp < %s"
                filas_afectadas_eventos = self.database_service.ejecutarQuery(
                    query_eventos, (fecha_limite,)
                )
                
                # Limpiar errores antiguos
                query_errores = "DELETE FROM auditoria_errores WHERE timestamp < %s"
                filas_afectadas_errores = self.database_service.ejecutarQuery(
                    query_errores, (fecha_limite,)
                )
                
                registros_eliminados = filas_afectadas_eventos + filas_afectadas_errores
            
            self.logger.info(f"Limpiados {registros_eliminados} registros antiguos")
            return registros_eliminados
            
        except Exception as e:
            self.logger.error(f"Error limpiando logs antiguos: {str(e)}")
            return 0
    
    def crear_tablas_auditoria(self) -> bool:
        """
        Crea las tablas necesarias para auditoría
        
        Returns:
            True si se crearon correctamente
        """
        if not self.enable_audit_db or not self.database_service:
            return False
        
        try:
            # Tabla de eventos
            query_eventos = """
            CREATE TABLE IF NOT EXISTS auditoria_eventos (
                evento_id VARCHAR(64) PRIMARY KEY,
                tipo_evento VARCHAR(100) NOT NULL,
                timestamp DATETIME NOT NULL,
                usuario VARCHAR(100),
                ip_origen VARCHAR(45),
                datos_evento JSON,
                session_id VARCHAR(64),
                resultado VARCHAR(20),
                duracion_ms INT,
                hash_integridad VARCHAR(64),
                INDEX idx_tipo_evento (tipo_evento),
                INDEX idx_timestamp (timestamp),
                INDEX idx_usuario (usuario),
                INDEX idx_session (session_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """
            
            # Tabla de errores
            query_errores = """
            CREATE TABLE IF NOT EXISTS auditoria_errores (
                error_id VARCHAR(64) PRIMARY KEY,
                tipo_error VARCHAR(100) NOT NULL,
                mensaje TEXT,
                stack_trace LONGTEXT,
                timestamp DATETIME NOT NULL,
                contexto JSON,
                severidad VARCHAR(20),
                resuelto BOOLEAN DEFAULT FALSE,
                INDEX idx_tipo_error (tipo_error),
                INDEX idx_timestamp (timestamp),
                INDEX idx_severidad (severidad),
                INDEX idx_resuelto (resuelto)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """
            
            # Tabla de métricas
            query_metricas = """
            CREATE TABLE IF NOT EXISTS auditoria_metricas (
                metrica_id VARCHAR(64) PRIMARY KEY,
                timestamp DATETIME NOT NULL,
                nombre_metrica VARCHAR(100) NOT NULL,
                valor DECIMAL(15,6),
                unidad VARCHAR(20),
                etiquetas JSON,
                INDEX idx_nombre_metrica (nombre_metrica),
                INDEX idx_timestamp (timestamp)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """
            
            # Ejecutar queries
            self.database_service.ejecutarQuery(query_eventos)
            self.database_service.ejecutarQuery(query_errores)
            self.database_service.ejecutarQuery(query_metricas)
            
            self.logger.info("Tablas de auditoría creadas exitosamente")
            return True
            
        except Exception as e:
            self.logger.error(f"Error creando tablas de auditoría: {str(e)}")
            return False
    
    # Métodos privados
    
    def _generar_id_evento(self) -> str:
        """Genera un ID único para un evento"""
        timestamp = str(int(datetime.now().timestamp() * 1000))
        random_part = str(os.urandom(8).hex())
        return hashlib.sha256(f"{timestamp}{random_part}".encode()).hexdigest()[:16]
    
    def _generar_id_error(self) -> str:
        """Genera un ID único para un error"""
        return self._generar_id_evento()
    
    def _calcular_hash_integridad(self, datos: Dict[str, Any], timestamp: datetime) -> str:
        """Calcula un hash de integridad para los datos"""
        data_str = json.dumps(datos, sort_keys=True, default=str)
        timestamp_str = timestamp.isoformat()
        hash_input = f"{data_str}{timestamp_str}".encode()
        return hashlib.sha256(hash_input).hexdigest()[:16]
    
    def _filtrar_datos_sensibles(self, datos: Dict[str, Any]) -> Dict[str, Any]:
        """Filtra datos sensibles del diccionario"""
        datos_filtrados = {}
        
        for clave, valor in datos.items():
            # Verificar si la clave contiene patrones sensibles
            clave_lower = clave.lower()
            if any(patron in clave_lower for patron in self._patrones_sensibles):
                # Enmascarar el valor
                if isinstance(valor, str):
                    if len(valor) <= 4:
                        valor_filtrado = "*" * len(valor)
                    else:
                        valor_filtrado = valor[:2] + "*" * (len(valor) - 4) + valor[-2:]
                else:
                    valor_filtrado = "***"
                datos_filtrados[clave] = valor_filtrado
            else:
                datos_filtrados[clave] = valor
        
        return datos_filtrados
    
    def _actualizar_contador(self, tipo_evento: str, valor: float = 1.0):
        """Actualiza los contadores de eventos"""
        with self._lock:
            self._contadores_eventos[tipo_evento] = self._contadores_eventos.get(tipo_evento, 0) + valor
    
    def _guardar_evento_db(self, registro: RegistroAuditoria):
        """Guarda un evento en la base de datos"""
        try:
            query = """
            INSERT INTO auditoria_eventos (
                evento_id, tipo_evento, timestamp, usuario, ip_origen,
                datos_evento, session_id, resultado, duracion_ms, hash_integridad
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            parametros = (
                registro.evento_id,
                registro.tipo_evento,
                registro.timestamp,
                registro.usuario,
                registro.ip_origen,
                json.dumps(registro.datos_evento, default=str),
                registro.session_id,
                registro.resultado,
                registro.duracion_ms,
                registro.hash_integridad
            )
            
            self.database_service.ejecutarQuery(query, parametros)
            
        except Exception as e:
            self.logger.error(f"Error guardando evento en DB: {str(e)}")
    
    def _guardar_evento_archivo(self, registro: RegistroAuditoria):
        """Guarda un evento en archivo"""
        try:
            archivo_audit = self.log_dir / "reniec_audit.log"
            
            with open(archivo_audit, 'a', encoding='utf-8') as f:
                f.write(f"{registro.to_dict()}\n")
                
        except Exception as e:
            self.logger.error(f"Error guardando evento en archivo: {str(e)}")
    
    def _guardar_error_db(self, registro: RegistroError):
        """Guarda un error en la base de datos"""
        try:
            query = """
            INSERT INTO auditoria_errores (
                error_id, tipo_error, mensaje, stack_trace, timestamp,
                contexto, severidad, resuelto
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            parametros = (
                registro.error_id,
                registro.tipo_error,
                registro.mensaje,
                registro.stack_trace,
                registro.timestamp,
                json.dumps(registro.contexto, default=str),
                registro.severidad,
                registro.resuelto
            )
            
            self.database_service.ejecutarQuery(query, parametros)
            
        except Exception as e:
            self.logger.error(f"Error guardando error en DB: {str(e)}")
    
    def _guardar_error_archivo(self, registro: RegistroError):
        """Guarda un error en archivo"""
        try:
            archivo_errors = self.log_dir / "reniec_errors.log"
            
            with open(archivo_errors, 'a', encoding='utf-8') as f:
                f.write(f"{registro.to_dict()}\n")
                
        except Exception as e:
            self.logger.error(f"Error guardando error en archivo: {str(e)}")
    
    def _guardar_metrica_db(self, metrica_id: str, timestamp: datetime, datos: Dict[str, Any]):
        """Guarda una métrica en la base de datos"""
        try:
            query = """
            INSERT INTO auditoria_metricas (
                metrica_id, timestamp, nombre_metrica, valor, unidad, etiquetas
            ) VALUES (%s, %s, %s, %s, %s, %s)
            """
            
            parametros = (
                metrica_id,
                timestamp,
                datos["nombre"],
                datos["valor"],
                datos["unidad"],
                json.dumps(datos["etiquetas"], default=str)
            )
            
            self.database_service.ejecutarQuery(query, parametros)
            
        except Exception as e:
            self.logger.error(f"Error guardando métrica en DB: {str(e)}")