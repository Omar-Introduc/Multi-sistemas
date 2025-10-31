"""
Servicio de base de datos MySQL para el sistema de validación RENIEC
Maneja conexiones, consultas y operaciones CRUD
"""

import logging
import mysql.connector
from mysql.connector import Error, pooling
from contextlib import contextmanager
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import threading

from .LogService import LogService

class DatabaseService:
    """Servicio para manejo de base de datos MySQL"""
    
    def __init__(self, log_service: LogService, 
                 host: str = "localhost",
                 port: int = 3306,
                 database: str = "reniec_db",
                 username: str = "reniec_user",
                 password: str = "reniec_password",
                 pool_size: int = 10,
                 pool_name: str = "reniec_pool"):
        """
        Inicializa el servicio de base de datos
        
        Args:
            log_service: Servicio de logging
            host: Host de la base de datos
            port: Puerto de la base de datos
            database: Nombre de la base de datos
            username: Usuario de la base de datos
            password: Contraseña de la base de datos
            pool_size: Tamaño del pool de conexiones
            pool_name: Nombre del pool de conexiones
        """
        self.logger = logging.getLogger(__name__)
        self.log_service = log_service
        self.host = host
        self.port = port
        self.database = database
        self.username = username
        self.password = password
        self.pool_size = pool_size
        self.pool_name = pool_name
        
        self._pool = None
        self._lock = threading.Lock()
        self._initialized = False
        
        # Configuración de reconexión
        self.max_reintentos = 3
        self.tiempo_reintento = 1  # segundos
        
    def inicializar(self) -> bool:
        """
        Inicializa el pool de conexiones de la base de datos
        
        Returns:
            True si se inicializó correctamente, False en caso contrario
        """
        with self._lock:
            if self._initialized:
                return True
                
            try:
                self._pool = pooling.MySQLConnectionPool(
                    pool_name=self.pool_name,
                    pool_size=self.pool_size,
                    host=self.host,
                    port=self.port,
                    database=self.database,
                    user=self.username,
                    password=self.password,
                    autocommit=True,
                    connection_timeout=30,
                    raise_on_warnings=True
                )
                
                # Probar conexión
                connection = self._obtenerConexion()
                if connection:
                    connection.close()
                
                self._initialized = True
                self.logger.info(f"Pool de conexiones inicializado: {self.pool_name}")
                self.log_service.registrarEvento(
                    "DB_POOL_INICIALIZADO",
                    f"Pool de conexiones creado exitosamente: {self.pool_name}",
                    {"pool_size": self.pool_size}
                )
                return True
                
            except Exception as e:
                self.logger.error(f"Error inicializando pool de conexiones: {str(e)}")
                self.log_service.registrarError("ERROR_DB_INIT", str(e))
                return False
    
    @contextmanager
    def obtenerConexion(self):
        """
        Context manager para obtener una conexión del pool
        
        Yields:
            Conexión de base de datos
            
        Raises:
            Exception: Si no se puede obtener una conexión
        """
        connection = None
        try:
            connection = self._obtenerConexion()
            yield connection
        except Exception as e:
            if connection:
                connection.close()
            raise e
        finally:
            if connection:
                connection.close()
    
    def _obtenerConexion(self):
        """Obtiene una conexión del pool con manejo de reintentos"""
        if not self._initialized:
            self.inicializar()
        
        for intento in range(self.max_reintentos):
            try:
                connection = self._pool.get_connection()
                if connection.is_connected():
                    return connection
                else:
                    connection.close()
                    raise Exception("Conexión obtenida pero no está conectada")
                    
            except Exception as e:
                self.logger.warning(f"Intento {intento + 1} de obtener conexión falló: {str(e)}")
                if intento < self.max_reintentos - 1:
                    import time
                    time.sleep(self.tiempo_reintento)
                else:
                    self.logger.error("No se pudo obtener conexión después de todos los reintentos")
                    raise
    
    def ejecutarQuery(self, query: str, parametros: Optional[Tuple] = None) -> int:
        """
        Ejecuta una consulta INSERT, UPDATE, DELETE
        
        Args:
            query: Consulta SQL a ejecutar
            parametros: Parámetros para la consulta
            
        Returns:
            Número de filas afectadas
            
        Raises:
            Error: Si hay error en la ejecución
        """
        try:
            with self.obtenerConexion() as connection:
                cursor = connection.cursor()
                
                self.logger.debug(f"Ejecutando query: {query[:100]}...")
                
                cursor.execute(query, parametros or ())
                filas_afectadas = cursor.rowcount
                
                cursor.close()
                
                self.logger.debug(f"Query ejecutado exitosamente. Filas afectadas: {filas_afectadas}")
                return filas_afectadas
                
        except Error as e:
            self.logger.error(f"Error ejecutando query: {str(e)}")
            self.log_service.registrarError("ERROR_DB_QUERY", str(e), {"query": query})
            raise
    
    def ejecutarConsulta(self, query: str, parametros: Optional[Tuple] = None) -> List[Dict[str, Any]]:
        """
        Ejecuta una consulta SELECT
        
        Args:
            query: Consulta SQL a ejecutar
            parametros: Parámetros para la consulta
            
        Returns:
            Lista de diccionarios con los resultados
            
        Raises:
            Error: Si hay error en la ejecución
        """
        try:
            with self.obtenerConexion() as connection:
                cursor = connection.cursor(dictionary=True)
                
                self.logger.debug(f"Ejecutando consulta: {query[:100]}...")
                
                cursor.execute(query, parametros or ())
                resultados = cursor.fetchall()
                
                cursor.close()
                
                self.logger.debug(f"Consulta ejecutada exitosamente. Registros encontrados: {len(resultados)}")
                return resultados
                
        except Error as e:
            self.logger.error(f"Error ejecutando consulta: {str(e)}")
            self.log_service.registrarError("ERROR_DB_CONSULTA", str(e), {"query": query})
            raise
    
    def ejecutarConsultaUnica(self, query: str, parametros: Optional[Tuple] = None) -> Optional[Dict[str, Any]]:
        """
        Ejecuta una consulta SELECT que devuelve un solo registro
        
        Args:
            query: Consulta SQL a ejecutar
            parametros: Parámetros para la consulta
            
        Returns:
            Diccionario con el resultado o None si no hay registros
            
        Raises:
            Error: Si hay error en la ejecución
        """
        try:
            with self.obtenerConexion() as connection:
                cursor = connection.cursor(dictionary=True)
                
                self.logger.debug(f"Ejecutando consulta única: {query[:100]}...")
                
                cursor.execute(query, parametros or ())
                resultado = cursor.fetchone()
                
                cursor.close()
                
                self.logger.debug(f"Consulta única ejecutada exitosamente")
                return resultado
                
        except Error as e:
            self.logger.error(f"Error ejecutando consulta única: {str(e)}")
            self.log_service.registrarError("ERROR_DB_CONSULTA_UNICA", str(e), {"query": query})
            raise
    
    def ejecutarProcedimiento(self, nombre_procedimiento: str, parametros: Optional[Tuple] = None) -> List[Dict[str, Any]]:
        """
        Ejecuta un procedimiento almacenado
        
        Args:
            nombre_procedimiento: Nombre del procedimiento
            parametros: Parámetros para el procedimiento
            
        Returns:
            Lista de resultados del procedimiento
            
        Raises:
            Error: Si hay error en la ejecución
        """
        try:
            with self.obtenerConexion() as connection:
                cursor = connection.cursor(dictionary=True)
                
                self.logger.debug(f"Ejecutando procedimiento: {nombre_procedimiento}")
                
                cursor.callproc(nombre_procedimiento, parametros or ())
                
                resultados = []
                for resultado in cursor.stored_results():
                    resultados.extend(resultado.fetchall())
                
                cursor.close()
                
                self.logger.debug(f"Procedimiento ejecutado exitosamente. Resultados: {len(resultados)}")
                return resultados
                
        except Error as e:
            self.logger.error(f"Error ejecutando procedimiento {nombre_procedimiento}: {str(e)}")
            self.log_service.registrarError("ERROR_DB_PROCEDIMIENTO", str(e), {"procedimiento": nombre_procedimiento})
            raise
    
    def iniciarTransaccion(self) -> bool:
        """
        Inicia una transacción
        
        Returns:
            True si se inició correctamente
        """
        try:
            with self.obtenerConexion() as connection:
                connection.start_transaction()
                self.logger.debug("Transacción iniciada")
                return True
        except Error as e:
            self.logger.error(f"Error iniciando transacción: {str(e)}")
            self.log_service.registrarError("ERROR_DB_TRANSACCION", str(e))
            return False
    
    def confirmarTransaccion(self) -> bool:
        """
        Confirma una transacción
        
        Returns:
            True si se confirmó correctamente
        """
        try:
            with self.obtenerConexion() as connection:
                connection.commit()
                self.logger.debug("Transacción confirmada")
                return True
        except Error as e:
            self.logger.error(f"Error confirmando transacción: {str(e)}")
            self.log_service.registrarError("ERROR_DB_COMMIT", str(e))
            return False
    
    def revertirTransaccion(self) -> bool:
        """
        Revierte una transacción
        
        Returns:
            True si se revertió correctamente
        """
        try:
            with self.obtenerConexion() as connection:
                connection.rollback()
                self.logger.debug("Transacción revertida")
                return True
        except Error as e:
            self.logger.error(f"Error revertiendo transacción: {str(e)}")
            self.log_service.registrarError("ERROR_DB_ROLLBACK", str(e))
            return False
    
    def verificarConexion(self) -> bool:
        """
        Verifica si la conexión a la base de datos está funcionando
        
        Returns:
            True si la conexión está activa
        """
        try:
            with self.obtenerConexion() as connection:
                cursor = connection.cursor()
                cursor.execute("SELECT 1")
                cursor.fetchone()
                cursor.close()
                
                self.logger.debug("Conexión a base de datos verificada")
                return True
                
        except Exception as e:
            self.logger.error(f"Error verificando conexión: {str(e)}")
            self.log_service.registrarError("ERROR_DB_CONEXION", str(e))
            return False
    
    def obtenerEstadoPool(self) -> Dict[str, Any]:
        """
        Obtiene el estado actual del pool de conexiones
        
        Returns:
            Diccionario con información del pool
        """
        try:
            if not self._pool:
                return {"estado": "no_inicializado"}
            
            return {
                "estado": "activo",
                "pool_name": self.pool_name,
                "pool_size": self.pool_size,
                "connections_in_pool": len(self._pool._all_connections),
                "connections_idle": len(self._pool._pool),
                "connections_in_use": len(self._pool._in_use_connections)
            }
            
        except Exception as e:
            self.logger.error(f"Error obteniendo estado del pool: {str(e)}")
            return {"estado": "error", "error": str(e)}
    
    def cerrarPool(self):
        """Cierra todas las conexiones del pool"""
        try:
            if self._pool:
                self.logger.info("Cerrando pool de conexiones...")
                
                # Cerrar todas las conexiones del pool
                for conn in self._pool._all_connections:
                    if conn.is_connected():
                        conn.close()
                
                self._pool = None
                self._initialized = False
                
                self.logger.info("Pool de conexiones cerrado exitosamente")
                self.log_service.registrarEvento("DB_POOL_CERRADO", "Pool de conexiones cerrado")
                
        except Exception as e:
            self.logger.error(f"Error cerrando pool: {str(e)}")
            self.log_service.registrarError("ERROR_DB_CERRAR_POOL", str(e))
    
    # Operaciones CRUD específicas para RENIEC
    
    def obtenerCiudadano(self, numero_documento: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene un ciudadano por su número de documento
        
        Args:
            numero_documento: Número de documento del ciudadano
            
        Returns:
            Diccionario con datos del ciudadano o None
        """
        query = """
        SELECT numero_documento, nombres, apellido_paterno, apellido_materno,
               fecha_nacimiento, estado_civil, direccion, distrito, provincia, 
               departamento, activo, fecha_actualizacion
        FROM ciudadanos 
        WHERE numero_documento = %s AND activo = 1
        """
        
        return self.ejecutarConsultaUnica(query, (numero_documento,))
    
    def crearCiudadano(self, datos_ciudadano: Dict[str, Any]) -> bool:
        """
        Crea un nuevo ciudadano
        
        Args:
            datos_ciudadano: Datos del ciudadano
            
        Returns:
            True si se creó correctamente
        """
        query = """
        INSERT INTO ciudadanos (
            numero_documento, nombres, apellido_paterno, apellido_materno,
            fecha_nacimiento, estado_civil, direccion, distrito, provincia, 
            departamento, activo, creado_en, actualizado_en
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 1, %s, %s)
        """
        
        parametros = (
            datos_ciudadano.get('numero_documento'),
            datos_ciudadano.get('nombres'),
            datos_ciudadano.get('apellido_paterno'),
            datos_ciudadano.get('apellido_materno'),
            datos_ciudadano.get('fecha_nacimiento'),
            datos_ciudadano.get('estado_civil'),
            datos_ciudadano.get('direccion'),
            datos_ciudadano.get('distrito'),
            datos_ciudadano.get('provincia'),
            datos_ciudadano.get('departamento'),
            datetime.now(),
            datetime.now()
        )
        
        filas_afectadas = self.ejecutarQuery(query, parametros)
        return filas_afectadas > 0
    
    def actualizarCiudadano(self, numero_documento: str, datos_actualizacion: Dict[str, Any]) -> bool:
        """
        Actualiza los datos de un ciudadano
        
        Args:
            numero_documento: Número de documento del ciudadano
            datos_actualizacion: Datos a actualizar
            
        Returns:
            True si se actualizó correctamente
        """
        # Construir query dinámico basado en campos a actualizar
        campos_actualizacion = []
        parametros = []
        
        for campo, valor in datos_actualizacion.items():
            if campo in ['nombres', 'apellido_paterno', 'apellido_materno', 'fecha_nacimiento', 
                        'estado_civil', 'direccion', 'distrito', 'provincia', 'departamento']:
                campos_actualizacion.append(f"{campo} = %s")
                parametros.append(valor)
        
        if not campos_actualizacion:
            return False
        
        campos_actualizacion.append("actualizado_en = %s")
        parametros.append(datetime.now())
        parametros.append(numero_documento)
        
        query = f"""
        UPDATE ciudadanos 
        SET {', '.join(campos_actualizacion)}
        WHERE numero_documento = %s AND activo = 1
        """
        
        filas_afectadas = self.ejecutarQuery(query, tuple(parametros))
        return filas_afectadas > 0
    
    def desactivarCiudadano(self, numero_documento: str) -> bool:
        """
        Desactiva un ciudadano (soft delete)
        
        Args:
            numero_documento: Número de documento del ciudadano
            
        Returns:
            True si se desactivó correctamente
        """
        query = """
        UPDATE ciudadanos 
        SET activo = 0, actualizado_en = %s
        WHERE numero_documento = %s AND activo = 1
        """
        
        filas_afectadas = self.ejecutarQuery(query, (datetime.now(), numero_documento))
        return filas_afectadas > 0
    
    def obtenerSesionValidacion(self, id_solicitud: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene una sesión de validación por su ID
        
        Args:
            id_solicitud: ID de la solicitud
            
        Returns:
            Datos de la sesión o None
        """
        query = """
        SELECT id_solicitud, numero_dni, fecha_validacion, fecha_expiracion, 
               estado, id_banco, intentos_validacion
        FROM sesiones_validacion 
        WHERE id_solicitud = %s
        """
        
        return self.ejecutarConsultaUnica(query, (id_solicitud,))
    
    def obtenerSesionesValidasPorDni(self, numero_dni: str) -> List[Dict[str, Any]]:
        """
        Obtiene las sesiones válidas para un DNI
        
        Args:
            numero_dni: Número de DNI
            
        Returns:
            Lista de sesiones válidas
        """
        query = """
        SELECT id_solicitud, numero_dni, fecha_validacion, fecha_expiracion, 
               estado, id_banco, intentos_validacion
        FROM sesiones_validacion 
        WHERE numero_dni = %s 
        AND fecha_expiracion > %s 
        AND estado = 'exitosa'
        ORDER BY fecha_validacion DESC
        """
        
        return self.ejecutarConsulta(query, (numero_dni, datetime.now()))