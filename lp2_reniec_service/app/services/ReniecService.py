"""
Servicio principal para operaciones de validación RENIEC
Maneja la lógica de negocio para validación de identidad y consultas ciudadanas
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import hashlib
import uuid

from .DatabaseService import DatabaseService
from .RabbitMQService import RabbitMQService
from .LogService import LogService

class EstadoValidacion(Enum):
    """Estados posibles de una validación"""
    PENDIENTE = "pendiente"
    VALIDANDO = "validando"
    EXITOSA = "exitosa"
    FALLIDA = "fallida"
    EXPIRADA = "expirada"

class TipoDocumento(Enum):
    """Tipos de documentos válidos"""
    DNI = "dni"
    CARNET_EXTRANJERIA = "ce"
    PASAPORTE = "pasaporte"

@dataclass
class DatosCiudadano:
    """Estructura de datos del ciudadano"""
    numero_documento: str
    nombres: str
    apellido_paterno: str
    apellido_materno: str
    fecha_nacimiento: Optional[str] = None
    estado_civil: Optional[str] = None
    direccion: Optional[str] = None
    distrito: Optional[str] = None
    provincia: Optional[str] = None
    departamento: Optional[str] = None

@dataclass
class RespuestaValidacion:
    """Estructura de respuesta de validación"""
    id_validacion: str
    estado: EstadoValidacion
    datos_ciudadano: Optional[DatosCiudadano]
    fecha_validacion: datetime
    mensaje: str
    score_confianza: Optional[float] = None

class ReniecService:
    """Servicio principal para operaciones RENIEC"""
    
    def __init__(self, database_service: DatabaseService, rabbit_service: RabbitMQService, log_service: LogService):
        self.database_service = database_service
        self.rabbit_service = rabbit_service
        self.log_service = log_service
        self.logger = logging.getLogger(__name__)
        
        # Configuración de validación
        self.tiempo_expiracion_session = timedelta(hours=24)
        self.max_intentos_validacion = 3
        
    def validarIdentidad(self, numero_dni: str, nombres: str, apellido_paterno: str, 
                        apellido_materno: str, id_solicitud: str) -> RespuestaValidacion:
        """
        Valida la identidad de un ciudadano contra la base de datos RENIEC
        
        Args:
            numero_dni: Número de DNI a validar
            nombres: Nombres del ciudadano
            apellido_paterno: Apellido paterno
            apellido_materno: Apellido materno
            id_solicitud: ID único de la solicitud de validación
            
        Returns:
            RespuestaValidacion con el resultado de la validación
        """
        try:
            self.logger.info(f"Iniciando validación de identidad para DNI: {numero_dni}")
            
            # Validar formato de DNI
            if not self._validarFormatoDni(numero_dni):
                return self._generarRespuestaValidacion(
                    id_solicitud, EstadoValidacion.FALLIDA, None,
                    "Formato de DNI inválido. Debe tener 8 dígitos numéricos."
                )
            
            # Validar formato de nombres
            if not self._validarFormatoNombres(nombres, apellido_paterno, apellido_materno):
                return self._generarRespuestaValidacion(
                    id_solicitud, EstadoValidacion.FALLIDA, None,
                    "Formato de nombres inválido. Solo se permiten letras y espacios."
                )
            
            # Consultar ciudadano en base de datos
            datos_ciudadano = self.consultarCiudadano(numero_dni)
            
            if not datos_ciudadano:
                return self._generarRespuestaValidacion(
                    id_solicitud, EstadoValidacion.FALLIDA, None,
                    "Ciudadano no encontrado en la base de datos RENIEC."
                )
            
            # Comparar datos proporcionados con datos de la base
            score_confianza = self._calcularScoreConfianza(datos_ciudadano, nombres, apellido_paterno, apellido_materno)
            
            if score_confianza >= 0.8:  # 80% de coincidencia mínima
                estado = EstadoValidacion.EXITOSA
                mensaje = "Validación exitosa. Identidad confirmada."
                
                # Registrar sesión de validación
                self.registrarSession(id_solicitud, numero_dni, EstadoValidacion.EXITOSA)
                
                # Log de auditoría
                self.log_service.registrarEvento(
                    "VALIDACION_EXITOSA",
                    f"Validación exitosa para DNI {numero_dni} - Score: {score_confianza}",
                    {"solicitud_id": id_solicitud, "dni": numero_dni, "score": score_confianza}
                )
                
                return self._generarRespuestaValidacion(
                    id_solicitud, estado, datos_ciudadano, mensaje, score_confianza
                )
            else:
                estado = EstadoValidacion.FALLIDA
                mensaje = f"Validación fallida. Los datos no coinciden con suficiente confianza (Score: {score_confianza:.2f})."
                
                # Log de auditoría
                self.log_service.registrarEvento(
                    "VALIDACION_FALLIDA",
                    f"Validación fallida para DNI {numero_dni} - Score: {score_confianza}",
                    {"solicitud_id": id_solicitud, "dni": numero_dni, "score": score_confianza}
                )
                
                return self._generarRespuestaValidacion(
                    id_solicitud, estado, datos_ciudadano, mensaje, score_confianza
                )
                
        except Exception as e:
            self.logger.error(f"Error en validarIdentidad para DNI {numero_dni}: {str(e)}")
            self.log_service.registrarError("ERROR_VALIDACION", str(e), {"dni": numero_dni})
            
            return self._generarRespuestaValidacion(
                id_solicitud, EstadoValidacion.FALLIDA, None,
                "Error interno en el sistema de validación."
            )
    
    def consultarCiudadano(self, numero_dni: str) -> Optional[DatosCiudadano]:
        """
        Consulta los datos de un ciudadano en la base de datos RENIEC
        
        Args:
            numero_dni: Número de DNI del ciudadano
            
        Returns:
            DatosCiudadano con los datos del ciudadano o None si no se encuentra
        """
        try:
            # Validar formato de DNI
            if not self._validarFormatoDni(numero_dni):
                return None
            
            # Consulta simulada a la base de datos (implementar según esquema real)
            query = """
            SELECT numero_documento, nombres, apellido_paterno, apellido_materno,
                   fecha_nacimiento, estado_civil, direccion, distrito, provincia, departamento
            FROM ciudadanos 
            WHERE numero_documento = %s AND activo = 1
            """
            
            resultado = self.database_service.ejecutarConsulta(query, (numero_dni,))
            
            if resultado:
                row = resultado[0]
                return DatosCiudadano(
                    numero_documento=row[0],
                    nombres=row[1],
                    apellido_paterno=row[2],
                    apellido_materno=row[3],
                    fecha_nacimiento=row[4],
                    estado_civil=row[5],
                    direccion=row[6],
                    distrito=row[7],
                    provincia=row[8],
                    departamento=row[9]
                )
            return None
            
        except Exception as e:
            self.logger.error(f"Error consultando ciudadano con DNI {numero_dni}: {str(e)}")
            self.log_service.registrarError("ERROR_CONSULTA_CIUDADANO", str(e), {"dni": numero_dni})
            return None
    
    def registrarSession(self, id_solicitud: str, numero_dni: str, estado: EstadoValidacion) -> bool:
        """
        Registra una sesión de validación en la base de datos
        
        Args:
            id_solicitud: ID único de la solicitud
            numero_dni: Número de DNI validado
            estado: Estado de la validación
            
        Returns:
            True si se registró correctamente, False en caso contrario
        """
        try:
            fecha_expiracion = datetime.now() + self.tiempo_expiracion_session
            
            query = """
            INSERT INTO sesiones_validacion 
            (id_solicitud, numero_dni, fecha_validacion, fecha_expiracion, estado, creado_en)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            
            parametros = (
                id_solicitud,
                numero_dni,
                datetime.now(),
                fecha_expiracion,
                estado.value,
                datetime.now()
            )
            
            filas_afectadas = self.database_service.ejecutarQuery(query, parametros)
            
            if filas_afectadas > 0:
                self.logger.info(f"Sesión registrada para solicitud {id_solicitud}")
                return True
            else:
                self.logger.warning(f"No se pudo registrar sesión para solicitud {id_solicitud}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error registrando sesión {id_solicitud}: {str(e)}")
            self.log_service.registrarError("ERROR_REGISTRO_SESSION", str(e), {"solicitud": id_solicitud})
            return False
    
    def validarDni(self, numero_dni: str) -> Dict[str, Any]:
        """
        Valida solo el formato y existencia de un DNI
        
        Args:
            numero_dni: Número de DNI a validar
            
        Returns:
            Dict con el resultado de la validación
        """
        try:
            # Validar formato
            if not self._validarFormatoDni(numero_dni):
                return {
                    "valido": False,
                    "mensaje": "Formato de DNI inválido. Debe tener 8 dígitos numéricos.",
                    "existe": False
                }
            
            # Verificar existencia en base de datos
            datos_ciudadano = self.consultarCiudadano(numero_dni)
            
            if datos_ciudadano:
                return {
                    "valido": True,
                    "mensaje": "DNI válido y encontrado en RENIEC.",
                    "existe": True,
                    "datos": {
                        "nombres": datos_ciudadano.nombres,
                        "apellido_paterno": datos_ciudadano.apellido_paterno,
                        "apellido_materno": datos_ciudadano.apellido_materno
                    }
                }
            else:
                return {
                    "valido": False,
                    "mensaje": "DNI no encontrado en la base de datos RENIEC.",
                    "existe": False
                }
                
        except Exception as e:
            self.logger.error(f"Error validando DNI {numero_dni}: {str(e)}")
            self.log_service.registrarError("ERROR_VALIDACION_DNI", str(e), {"dni": numero_dni})
            
            return {
                "valido": False,
                "mensaje": "Error interno validando DNI.",
                "existe": False
            }
    
    def generarRespuestaValidacion(self, respuesta: RespuestaValidacion, id_banco: str) -> bool:
        """
        Genera y envía la respuesta de validación al banco a través de RabbitMQ
        
        Args:
            respuesta: Respuesta de validación a enviar
            id_banco: Identificador del banco destino
            
        Returns:
            True si se envió correctamente, False en caso contrario
        """
        try:
            # Preparar mensaje para el banco
            mensaje = {
                "tipo_mensaje": "respuesta_validacion",
                "id_solicitud": respuesta.id_validacion,
                "estado_validacion": respuesta.estado.value,
                "fecha_validacion": respuesta.fecha_validacion.isoformat(),
                "mensaje": respuesta.mensaje,
                "datos_ciudadano": {
                    "numero_documento": respuesta.datos_ciudadano.numero_documento if respuesta.datos_ciudadano else None,
                    "nombres": respuesta.datos_ciudadano.nombres if respuesta.datos_ciudadano else None,
                    "apellido_paterno": respuesta.datos_ciudadano.apellido_paterno if respuesta.datos_ciudadano else None,
                    "apellido_materno": respuesta.datos_ciudadano.apellido_materno if respuesta.datos_ciudadano else None
                },
                "score_confianza": respuesta.score_confianza,
                "id_banco": id_banco,
                "timestamp": datetime.now().isoformat()
            }
            
            # Enviar a RabbitMQ
            routing_key = f"validacion.banco.{id_banco}"
            
            exito = self.rabbit_service.publicarMensaje(
                exchange="validacion_exchange",
                routing_key=routing_key,
                mensaje=mensaje
            )
            
            if exito:
                self.logger.info(f"Respuesta de validación enviada al banco {id_banco}")
                
                # Log de auditoría
                self.log_service.registrarEvento(
                    "RESPUESTA_ENVIADA",
                    f"Respuesta enviada al banco {id_banco}",
                    {
                        "solicitud_id": respuesta.id_validacion,
                        "banco_id": id_banco,
                        "estado": respuesta.estado.value
                    }
                )
                
                return True
            else:
                self.logger.error(f"Error enviando respuesta al banco {id_banco}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error generando respuesta de validación: {str(e)}")
            self.log_service.registrarError("ERROR_GENERAR_RESPUESTA", str(e), {"solicitud": respuesta.id_validacion})
            return False
    
    def _validarFormatoDni(self, numero_dni: str) -> bool:
        """Valida el formato del número de DNI"""
        return numero_dni.isdigit() and len(numero_dni) == 8
    
    def _validarFormatoNombres(self, nombres: str, apellido_paterno: str, apellido_materno: str) -> bool:
        """Valida el formato de los nombres y apellidos"""
        import re
        
        pattern = r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$'
        return (re.match(pattern, nombres) and 
                re.match(pattern, apellido_paterno) and 
                re.match(pattern, apellido_materno))
    
    def _calcularScoreConfianza(self, datos_ciudadano: DatosCiudadano, 
                              nombres_input: str, apellido_paterno_input: str, apellido_materno_input: str) -> float:
        """
        Calcula un score de confianza entre 0 y 1 basado en la similitud de los datos
        """
        try:
            # Normalizar strings (convertir a minúsculas y remover espacios extra)
            def normalizar(texto):
                return texto.strip().lower().replace(" ", "")
            
            nombres_db = normalizar(datos_ciudadano.nombres)
            nombres_input_norm = normalizar(nombres_input)
            
            apellido_p_db = normalizar(datos_ciudadano.apellido_paterno)
            apellido_p_input_norm = normalizar(apellido_paterno_input)
            
            apellido_m_db = normalizar(datos_ciudadano.apellido_materno)
            apellido_m_input_norm = normalizar(apellido_materno_input)
            
            # Calcular similitud para cada campo
            score_nombres = self._calcularSimilitudCadenas(nombres_db, nombres_input_norm)
            score_apellido_p = self._calcularSimilitudCadenas(apellido_p_db, apellido_p_input_norm)
            score_apellido_m = self._calcularSimilitudCadenas(apellido_m_db, apellido_m_input_norm)
            
            # Pesos para cada campo (los apellidos tienen mayor peso)
            peso_nombres = 0.3
            peso_apellido_p = 0.35
            peso_apellido_m = 0.35
            
            score_total = (score_nombres * peso_nombres + 
                          score_apellido_p * peso_apellido_p + 
                          score_apellido_m * peso_apellido_m)
            
            return min(score_total, 1.0)
            
        except Exception as e:
            self.logger.error(f"Error calculando score de confianza: {str(e)}")
            return 0.0
    
    def _calcularSimilitudCadenas(self, cadena1: str, cadena2: str) -> float:
        """Calcula la similitud entre dos cadenas usando el algoritmo de Levenshtein"""
        if cadena1 == cadena2:
            return 1.0
        
        if len(cadena1) == 0 or len(cadena2) == 0:
            return 0.0
        
        # Implementación simple de distancia de Levenshtein
        matriz = [[0] * (len(cadena2) + 1) for _ in range(len(cadena1) + 1)]
        
        for i in range(len(cadena1) + 1):
            matriz[i][0] = i
        for j in range(len(cadena2) + 1):
            matriz[0][j] = j
        
        for i in range(1, len(cadena1) + 1):
            for j in range(1, len(cadena2) + 1):
                if cadena1[i-1] == cadena2[j-1]:
                    matriz[i][j] = matriz[i-1][j-1]
                else:
                    matriz[i][j] = min(
                        matriz[i-1][j] + 1,     # eliminación
                        matriz[i][j-1] + 1,     # inserción
                        matriz[i-1][j-1] + 1    # sustitución
                    )
        
        distancia = matriz[len(cadena1)][len(cadena2)]
        longitud_maxima = max(len(cadena1), len(cadena2))
        
        return 1.0 - (distancia / longitud_maxima)
    
    def _generarRespuestaValidacion(self, id_validacion: str, estado: EstadoValidacion, 
                                  datos_ciudadano: Optional[DatosCiudadano], mensaje: str,
                                  score_confianza: Optional[float] = None) -> RespuestaValidacion:
        """Genera una respuesta de validación estructurada"""
        return RespuestaValidacion(
            id_validacion=id_validacion,
            estado=estado,
            datos_ciudadano=datos_ciudadano,
            fecha_validacion=datetime.now(),
            mensaje=mensaje,
            score_confianza=score_confianza
        )
    
    def limpiarSesionesExpiradas(self) -> int:
        """
        Limpia las sesiones de validación expiradas
        
        Returns:
            Número de sesiones limpiadas
        """
        try:
            query = """
            UPDATE sesiones_validacion 
            SET estado = 'expirada'
            WHERE fecha_expiracion < %s AND estado = 'exitosa'
            """
            
            filas_afectadas = self.database_service.ejecutarQuery(query, (datetime.now(),))
            
            self.logger.info(f"Limpiadas {filas_afectadas} sesiones expiradas")
            return filas_afectadas
            
        except Exception as e:
            self.logger.error(f"Error limpiando sesiones expiradas: {str(e)}")
            self.log_service.registrarError("ERROR_LIMPIAR_SESIONES", str(e))
            return 0