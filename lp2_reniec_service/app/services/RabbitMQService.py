"""
Servicio de RabbitMQ para el sistema de validación RENIEC
Maneja el envío de respuestas de validación a los bancos
"""

import logging
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional, List
import threading
from dataclasses import dataclass
from enum import Enum

import pika
from pika.exceptions import (
    AMQPConnectionError, AMQPChannelError, 
    ConnectionClosed, ChannelClosed, ProbableAuthenticationError
)

from .LogService import LogService

class EstadoConexion(Enum):
    """Estados de la conexión RabbitMQ"""
    DESCONECTADO = "desconectado"
    CONECTANDO = "conectando"
    CONECTADO = "conectado"
    RECONECTANDO = "reconectando"
    ERROR = "error"

class TipoMensaje(Enum):
    """Tipos de mensajes en el sistema"""
    SOLICITUD_VALIDACION = "solicitud_validacion"
    RESPUESTA_VALIDACION = "respuesta_validacion"
    ERROR_VALIDACION = "error_validacion"
    HEARTBEAT = "heartbeat"

@dataclass
class MensajeRabbitMQ:
    """Estructura de un mensaje para RabbitMQ"""
    tipo: TipoMensaje
    payload: Dict[str, Any]
    mensaje_id: str
    timestamp: datetime
    routing_key: str
    exchange: str
    prioridad: int = 1
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el mensaje a diccionario para envío"""
        return {
            "tipo": self.tipo.value,
            "payload": self.payload,
            "mensaje_id": self.mensaje_id,
            "timestamp": self.timestamp.isoformat(),
            "routing_key": self.routing_key,
            "exchange": self.exchange,
            "prioridad": self.prioridad
        }

class RabbitMQService:
    """Servicio para manejo de RabbitMQ"""
    
    def __init__(self, log_service: LogService,
                 host: str = "localhost",
                 port: int = 5672,
                 username: str = "guest",
                 password: str = "guest",
                 virtual_host: str = "/",
                 heartbeat_interval: int = 30,
                 blocked_connection_timeout: int = 300):
        """
        Inicializa el servicio de RabbitMQ
        
        Args:
            log_service: Servicio de logging
            host: Host del servidor RabbitMQ
            port: Puerto del servidor RabbitMQ
            username: Usuario de RabbitMQ
            password: Contraseña de RabbitMQ
            virtual_host: Virtual host de RabbitMQ
            heartbeat_interval: Intervalo de heartbeat en segundos
            blocked_connection_timeout: Timeout de conexión bloqueada
        """
        self.logger = logging.getLogger(__name__)
        self.log_service = log_service
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.virtual_host = virtual_host
        self.heartbeat_interval = heartbeat_interval
        self.blocked_connection_timeout = blocked_connection_timeout
        
        # Estado de conexión
        self._estado = EstadoConexion.DESCONECTADO
        self._connection = None
        self._channel = None
        self._lock = threading.Lock()
        self._exchanges_configurados = set()
        
        # Configuración de reconexión
        self.max_reintentos = 5
        self.tiempo_reintento = 5  # segundos
        self.reintento_actual = 0
        
        # Configuración de exchanges y queues
        self.exchanges = {
            "validacion_exchange": {
                "type": "topic",
                "durable": True,
                "auto_delete": False
            },
            "error_exchange": {
                "type": "fanout", 
                "durable": True,
                "auto_delete": False
            },
            "audit_exchange": {
                "type": "topic",
                "durable": True,
                "auto_delete": False
            }
        }
        
        # Configuración de queues
        self.queues = {
            "validacion_respuestas": {
                "exchange": "validacion_exchange",
                "routing_key": "validacion.respuesta.*",
                "durable": True,
                "exclusive": False,
                "auto_delete": False,
                "arguments": {"x-message-ttl": 300000}  # 5 minutos TTL
            },
            "banco_respuestas": {
                "exchange": "validacion_exchange", 
                "routing_key": "banco.*",
                "durable": True,
                "exclusive": False,
                "auto_delete": False,
                "arguments": {"x-message-ttl": 300000}
            },
            "errores_sistema": {
                "exchange": "error_exchange",
                "routing_key": "error.*",
                "durable": True,
                "exclusive": False,
                "auto_delete": False
            }
        }
    
    def inicializar(self) -> bool:
        """
        Inicializa la conexión con RabbitMQ
        
        Returns:
            True si se inicializó correctamente
        """
        with self._lock:
            try:
                self._cambiarEstado(EstadoConexion.CONECTANDO)
                
                # Configurar parámetros de conexión
                credentials = pika.PlainCredentials(self.username, self.password)
                parameters = pika.ConnectionParameters(
                    host=self.host,
                    port=self.port,
                    credentials=credentials,
                    virtual_host=self.virtual_host,
                    heartbeat=self.heartbeat_interval,
                    blocked_connection_timeout=self.blocked_connection_timeout,
                    connection_attempts=3,
                    retry_delay=2
                )
                
                # Establecer conexión
                self._connection = pika.BlockingConnection(parameters)
                self._channel = self._connection.channel()
                
                # Configurar exchanges y queues
                self._configurarExchanges()
                self._configurarQueues()
                
                # Configurar callbacks de eventos de conexión
                self._connection.add_on_open_callback(self._on_connection_opened)
                self._connection.add_on_close_callback(self._on_connection_closed)
                self._connection.add_on_blocked_callback(self._on_connection_blocked)
                self._connection.add_on_unblocked_callback(self._on_connection_unblocked)
                
                self._cambiarEstado(EstadoConexion.CONECTADO)
                self.reintento_actual = 0
                
                self.logger.info("Conexión con RabbitMQ establecida exitosamente")
                self.log_service.registrarEvento(
                    "RABBIT_CONECTADO",
                    f"Conexión establecida con {self.host}:{self.port}",
                    {"host": self.host, "port": self.port}
                )
                
                return True
                
            except Exception as e:
                self.logger.error(f"Error inicializando RabbitMQ: {str(e)}")
                self._cambiarEstado(EstadoConexion.ERROR)
                self.log_service.registrarError("ERROR_RABBIT_INIT", str(e))
                return False
    
    def publicarMensaje(self, exchange: str, routing_key: str, mensaje: Dict[str, Any], 
                       prioridad: int = 1, content_type: str = "application/json") -> bool:
        """
        Publica un mensaje en RabbitMQ
        
        Args:
            exchange: Nombre del exchange
            routing_key: Routing key del mensaje
            mensaje: Contenido del mensaje
            prioridad: Prioridad del mensaje (1-10)
            content_type: Tipo de contenido
            
        Returns:
            True si se publicó correctamente
        """
        try:
            if self._estado != EstadoConexion.CONECTADO:
                self.logger.warning("Intentando publicar con conexión no activa")
                if not self._reconectar():
                    return False
            
            # Validar exchange
            if exchange not in self.exchanges:
                self.logger.error(f"Exchange no configurado: {exchange}")
                return False
            
            # Preparar mensaje
            mensaje_rabbit = {
                "contenido": mensaje,
                "timestamp": datetime.now().isoformat(),
                "exchange": exchange,
                "routing_key": routing_key,
                "prioridad": prioridad
            }
            
            # Configurar propiedades del mensaje
            properties = pika.BasicProperties(
                delivery_mode=2,  # Mensaje persistente
                priority=prioridad,
                content_type=content_type,
                message_id=str(int(time.time() * 1000)),
                timestamp=int(time.time()),
                headers={"tipo_mensaje": "validacion", "service": "reniec"}
            )
            
            # Publicar mensaje
            self._channel.basic_publish(
                exchange=exchange,
                routing_key=routing_key,
                body=json.dumps(mensaje_rabbit, ensure_ascii=False, default=str),
                properties=properties
            )
            
            self.logger.debug(f"Mensaje publicado en {exchange}/{routing_key}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error publicando mensaje: {str(e)}")
            self.log_service.registrarError("ERROR_RABBIT_PUBLICAR", str(e), {
                "exchange": exchange,
                "routing_key": routing_key
            })
            return False
    
    def consumirMensaje(self, queue: str, callback, auto_ack: bool = True) -> bool:
        """
        Consume un mensaje de una queue
        
        Args:
            queue: Nombre de la queue
            callback: Función callback para procesar el mensaje
            auto_ack: Si el mensaje debe ser acknowledged automáticamente
            
        Returns:
            True si se inició el consumo correctamente
        """
        try:
            if self._estado != EstadoConexion.CONECTADO:
                self.logger.warning("Intentando consumir con conexión no activa")
                if not self._reconectar():
                    return False
            
            # Configurar QoS
            self._channel.basic_qos(prefetch_count=1)
            
            # Iniciar consumo
            self._channel.basic_consume(
                queue=queue,
                on_message_callback=callback,
                auto_ack=auto_ack
            )
            
            self.logger.info(f"Iniciando consumo de mensajes desde queue: {queue}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error configurando consumo de mensajes: {str(e)}")
            self.log_service.registrarError("ERROR_RABBIT_CONSUMIR", str(e), {"queue": queue})
            return False
    
    def iniciar_consumo(self) -> bool:
        """
        Inicia el consumo de mensajes de todas las queues configuradas
        
        Returns:
            True si se inició correctamente
        """
        try:
            def callback_respuestas(ch, method, properties, body):
                try:
                    mensaje = json.loads(body.decode('utf-8'))
                    self._procesarRespuestaBanco(mensaje)
                    
                    if not properties.auto_ack:
                        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
                        
                except Exception as e:
                    self.logger.error(f"Error procesando mensaje de respuesta: {str(e)}")
                    self.log_service.registrarError("ERROR_PROCESAR_RESPUESTA", str(e))
                    
                    if not properties.auto_ack:
                        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
            
            # Consumir mensajes de respuestas
            self.consumirMensaje("validacion_respuestas", callback_respuestas, auto_ack=False)
            
            self.logger.info("Consumo de mensajes iniciado")
            return True
            
        except Exception as e:
            self.logger.error(f"Error iniciando consumo de mensajes: {str(e)}")
            self.log_service.registrarError("ERROR_RABBIT_INICIO_CONSUMO", str(e))
            return False
    
    def verificarConexion(self) -> bool:
        """
        Verifica el estado de la conexión RabbitMQ
        
        Returns:
            True si la conexión está activa
        """
        try:
            if not self._connection or not self._channel:
                return False
            
            # Verificar que la conexión esté abierta
            if not self._connection.is_open:
                return False
            
            # Verificar que el canal esté abierto
            if not self._channel.is_open:
                return False
            
            # Test simple de conexión
            self._channel.queue_declare(queue='test_queue', passive=True)
            self._channel.queue_delete(queue='test_queue')
            
            self.logger.debug("Conexión RabbitMQ verificada")
            return True
            
        except Exception as e:
            self.logger.error(f"Error verificando conexión RabbitMQ: {str(e)}")
            self.log_service.registrarError("ERROR_RABBIT_VERIFICAR", str(e))
            return False
    
    def obtenerEstado(self) -> Dict[str, Any]:
        """
        Obtiene el estado actual del servicio RabbitMQ
        
        Returns:
            Diccionario con información del estado
        """
        try:
            return {
                "estado": self._estado.value,
                "host": self.host,
                "port": self.port,
                "conexion_activa": self._connection.is_open if self._connection else False,
                "canal_activo": self._channel.is_open if self._channel else False,
                "exchanges_configurados": len(self.exchanges),
                "queues_configuradas": len(self.queues),
                "reintento_actual": self.reintento_actual
            }
            
        except Exception as e:
            self.logger.error(f"Error obteniendo estado de RabbitMQ: {str(e)}")
            return {
                "estado": "error",
                "error": str(e)
            }
    
    def enviarRespuestaValidacion(self, id_banco: str, respuesta: Dict[str, Any]) -> bool:
        """
        Envía una respuesta de validación específica a un banco
        
        Args:
            id_banco: Identificador del banco
            respuesta: Datos de la respuesta de validación
            
        Returns:
            True si se envió correctamente
        """
        try:
            routing_key = f"validacion.respuesta.{id_banco}"
            
            mensaje = {
                "id_banco": id_banco,
                "tipo_respuesta": "validacion_ciudadano",
                "datos": respuesta,
                "fecha_respuesta": datetime.now().isoformat(),
                "servicio_origen": "RENIEC"
            }
            
            exito = self.publicarMensaje(
                exchange="validacion_exchange",
                routing_key=routing_key,
                mensaje=mensaje,
                prioridad=5  # Alta prioridad para respuestas
            )
            
            if exito:
                self.logger.info(f"Respuesta de validación enviada al banco {id_banco}")
                self.log_service.registrarEvento(
                    "RESPUESTA_VALIDACION_ENVIADA",
                    f"Respuesta enviada al banco {id_banco}",
                    {"banco": id_banco, "solicitud": respuesta.get("id_solicitud")}
                )
            
            return exito
            
        except Exception as e:
            self.logger.error(f"Error enviando respuesta de validación al banco {id_banco}: {str(e)}")
            self.log_service.registrarError("ERROR_ENVIAR_RESPUESTA", str(e), {"banco": id_banco})
            return False
    
    def cerrarConexion(self):
        """Cierra la conexión con RabbitMQ"""
        try:
            self.logger.info("Cerrando conexión con RabbitMQ...")
            
            if self._channel and self._channel.is_open:
                self._channel.close()
                
            if self._connection and self._connection.is_open:
                self._connection.close()
            
            self._cambiarEstado(EstadoConexion.DESCONECTADO)
            
            self.logger.info("Conexión RabbitMQ cerrada")
            self.log_service.registrarEvento("RABBIT_DESCONECTADO", "Conexión cerrada")
            
        except Exception as e:
            self.logger.error(f"Error cerrando conexión RabbitMQ: {str(e)}")
            self.log_service.registrarError("ERROR_CERRAR_RABBIT", str(e))
    
    def _configurarExchanges(self):
        """Configura los exchanges necesarios"""
        for exchange_name, config in self.exchanges.items():
            try:
                self._channel.exchange_declare(
                    exchange=exchange_name,
                    exchange_type=config["type"],
                    durable=config["durable"],
                    auto_delete=config["auto_delete"]
                )
                
                self._exchanges_configurados.add(exchange_name)
                self.logger.debug(f"Exchange configurado: {exchange_name}")
                
            except Exception as e:
                self.logger.error(f"Error configurando exchange {exchange_name}: {str(e)}")
                raise
    
    def _configurarQueues(self):
        """Configura las queues necesarias"""
        for queue_name, config in self.queues.items():
            try:
                queue_args = config.get("arguments", {})
                
                self._channel.queue_declare(
                    queue=queue_name,
                    durable=config["durable"],
                    exclusive=config["exclusive"],
                    auto_delete=config["auto_delete"],
                    arguments=queue_args
                )
                
                # Bind queue al exchange
                self._channel.queue_bind(
                    queue=queue_name,
                    exchange=config["exchange"],
                    routing_key=config["routing_key"]
                )
                
                self.logger.debug(f"Queue configurada: {queue_name}")
                
            except Exception as e:
                self.logger.error(f"Error configurando queue {queue_name}: {str(e)}")
                raise
    
    def _reconectar(self) -> bool:
        """
        Intenta reconectar con RabbitMQ
        
        Returns:
            True si la reconexión fue exitosa
        """
        if self.reintento_actual >= self.max_reintentos:
            self.logger.error("Máximo número de reintentos alcanzado")
            return False
        
        self.reintento_actual += 1
        self.logger.info(f"Intentando reconectar con RabbitMQ (intento {self.reintento_actual})")
        
        try:
            self.cerrarConexion()
            time.sleep(self.tiempo_reintento)
            
            exito = self.inicializar()
            if exito:
                self.logger.info("Reconexión exitosa")
                self.reintento_actual = 0
            else:
                self.logger.warning(f"Reconexión fallida (intento {self.reintento_actual})")
            
            return exito
            
        except Exception as e:
            self.logger.error(f"Error durante la reconexión: {str(e)}")
            return False
    
    def _cambiarEstado(self, nuevo_estado: EstadoConexion):
        """Cambia el estado de la conexión"""
        estado_anterior = self._estado
        self._estado = nuevo_estado
        
        if estado_anterior != nuevo_estado:
            self.logger.info(f"Estado de conexión cambiado: {estado_anterior.value} -> {nuevo_estado.value}")
    
    def _procesarRespuestaBanco(self, mensaje: Dict[str, Any]):
        """Procesa un mensaje de respuesta recibido"""
        try:
            contenido = mensaje.get("contenido", {})
            
            # Log del mensaje recibido
            self.log_service.registrarEvento(
                "MENSAJE_RECIBIDO",
                f"Mensaje recibido: {contenido.get('tipo_respuesta')}",
                {
                    "contenido": contenido,
                    "timestamp": mensaje.get("timestamp")
                }
            )
            
            # Aquí se puede implementar lógica adicional para procesar mensajes
            # dependiendo del tipo de mensaje recibido
            
        except Exception as e:
            self.logger.error(f"Error procesando respuesta del banco: {str(e)}")
            self.log_service.registrarError("ERROR_PROCESAR_RESPUESTA_BANCO", str(e))
    
    # Callbacks de eventos de conexión
    def _on_connection_opened(self, connection):
        """Callback cuando la conexión se abre"""
        self.logger.info("Conexión RabbitMQ abierta")
        self._cambiarEstado(EstadoConexion.CONECTADO)
    
    def _on_connection_closed(self, connection, reply_code, reply_text):
        """Callback cuando la conexión se cierra"""
        self.logger.warning(f"Conexión RabbitMQ cerrada: {reply_code} - {reply_text}")
        self._cambiarEstado(EstadoConexion.DESCONECTADO)
        
        # Intentar reconexión si el cierre no fue intencional
        if reply_code not in [200, 0]:  # Códigos de cierre normal
            threading.Thread(target=self._reconectar, daemon=True).start()
    
    def _on_connection_blocked(self, connection, reason):
        """Callback cuando la conexión está bloqueada"""
        self.logger.warning(f"Conexión RabbitMQ bloqueada: {reason}")
        self.log_service.registrarEvento(
            "RABBIT_CONEXION_BLOQUEADA",
            f"Conexión bloqueada: {reason}",
            {"reason": reason}
        )
    
    def _on_connection_unblocked(self, connection):
        """Callback cuando la conexión se desbloquea"""
        self.logger.info("Conexión RabbitMQ desbloqueada")
        self.log_service.registrarEvento("RABBIT_CONEXION_DESBLOQUEADA", "Conexión desbloqueada")