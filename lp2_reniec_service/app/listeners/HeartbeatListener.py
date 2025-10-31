"""
Listener para manejar heartbeats del banco.
Monitorea la conectividad y salud del servicio con el banco.
"""

import pika
import json
import logging
import time
import threading
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import uuid
import psutil
import os

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HeartbeatListener:
    """
    Listener que maneja los heartbeats del banco.
    Monitorea la conectividad y responde a health checks.
    """
    
    def __init__(self, rabbitmq_host: str = 'localhost', queue_name: str = 'bank.heartbeat.queue'):
        """
        Inicializa el listener de heartbeats.
        
        Args:
            rabbitmq_host: Host de RabbitMQ
            queue_name: Nombre de la cola de heartbeats
        """
        self.rabbitmq_host = rabbitmq_host
        self.queue_name = queue_name
        self.connection = None
        self.channel = None
        self.retry_attempts = 3
        self.retry_delay = 3  # segundos
        
        # Configuración de heartbeat
        self.heartbeat_interval = 30  # segundos
        self.heartbeat_timeout = 90   # segundos
        self.last_heartbeat_received = None
        self.bank_status = "unknown"
        self.service_status = "healthy"
        
        # Estadísticas del sistema
        self.stats = {
            'messages_received': 0,
            'messages_processed': 0,
            'messages_failed': 0,
            'heartbeats_sent': 0,
            'start_time': datetime.now(),
            'last_heartbeat_sent': None,
            'bank_heartbeats_received': 0,
            'service_uptime': 0
        }
        
        # Configuración de exchange y routing keys
        self.exchange_name = 'bank.heartbeat'
        self.routing_key_heartbeat = 'bank.heartbeat.request'
        self.routing_key_status = 'bank.status.update'
        self.routing_key_service_status = 'service.status.response'
        
        # Monitoreo de threads
        self.heartbeat_thread = None
        self.monitoring_thread = None
        self.should_stop = threading.Event()
        
        logger.info(f"Inicializando HeartbeatListener para queue: {queue_name}")
    
    def connect(self) -> bool:
        """
        Establece conexión con RabbitMQ.
        
        Returns:
            bool: True si la conexión fue exitosa
        """
        try:
            credentials = pika.PlainCredentials('guest', 'guest')
            parameters = pika.ConnectionParameters(
                host=self.rabbitmq_host,
                credentials=credentials,
                heartbeat=600,
                blocked_connection_timeout=300
            )
            
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            
            # Declarar exchanges
            self.channel.exchange_declare(
                exchange=self.exchange_name,
                exchange_type='topic',
                durable=True
            )
            
            # Declarar cola con configuraciones de QoS
            self.channel.queue_declare(
                queue=self.queue_name,
                durable=True,
                arguments={
                    'x-dead-letter-exchange': 'dlx',
                    'x-dead-letter-routing-key': 'heartbeat.failed',
                    'x-message-ttl': 180000  # 3 minutos para heartbeats
                }
            )
            
            # Configurar QoS - prefetch_count para manejo eficiente de mensajes
            self.channel.basic_qos(prefetch_count=1, global_qos=False)
            
            # Bind de la cola al exchange
            self.channel.queue_bind(
                exchange=self.exchange_name,
                queue=self.queue_name,
                routing_key=self.routing_key_heartbeat
            )
            
            # Declarar cola para envío de heartbeats del servicio
            self.service_heartbeat_queue = 'service.heartbeat'
            self.channel.queue_declare(
                queue=self.service_heartbeat_queue,
                durable=True,
                arguments={'x-message-ttl': 180000}
            )
            
            logger.info(f"Conectado exitosamente a RabbitMQ: {self.rabbitmq_host}")
            return True
            
        except Exception as e:
            logger.error(f"Error conectando a RabbitMQ: {str(e)}")
            return False
    
    def process_heartbeat_request(self, ch, method, properties, body) -> bool:
        """
        Procesa una solicitud de heartbeat desde el banco.
        
        Args:
            ch: Canal de RabbitMQ
            method: Método de entrega
            properties: Propiedades del mensaje
            body: Cuerpo del mensaje
            
        Returns:
            bool: True si el procesamiento fue exitoso
        """
        try:
            # Parse del mensaje JSON
            heartbeat_data = json.loads(body)
            correlation_id = properties.correlation_id or str(uuid.uuid4())
            
            logger.debug(f"Procesando heartbeat request - CorrelationID: {correlation_id}")
            logger.debug(f"Datos de heartbeat: {heartbeat_data}")
            
            # Actualizar estadísticas
            self.stats['messages_received'] += 1
            self.stats['bank_heartbeats_received'] += 1
            
            # Obtener estado del servicio
            service_health = self._get_service_health()
            
            # Preparar respuesta de heartbeat
            response_data = {
                'correlation_id': correlation_id,
                'service_name': 'lp2_reniec_service',
                'service_version': '1.0.0',
                'timestamp': datetime.now().isoformat(),
                'status': 'healthy',
                'health_data': service_health,
                'stats': self.stats.copy(),
                'bank_connection': {
                    'last_heartbeat_received': self.last_heartbeat_received.isoformat() if self.last_heartbeat_received else None,
                    'bank_status': self.bank_status
                }
            }
            
            # Enviar respuesta de heartbeat
            self._send_heartbeat_response(response_data)
            
            # Actualizar último heartbeat recibido
            self.last_heartbeat_received = datetime.now()
            self.bank_status = "connected"
            
            # Actualizar estadísticas
            self.stats['messages_processed'] += 1
            
            logger.debug(f"Heartbeat procesado exitosamente - CorrelationID: {correlation_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error procesando heartbeat: {str(e)}")
            self.stats['messages_failed'] += 1
            return False
    
    def _get_service_health(self) -> Dict[str, Any]:
        """
        Obtiene el estado de salud del servicio.
        
        Returns:
            Dict con información de salud del servicio
        """
        try:
            # Información del sistema
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Uptime del servicio
            uptime = datetime.now() - self.stats['start_time']
            
            health_data = {
                'status': 'healthy',
                'uptime_seconds': int(uptime.total_seconds()),
                'uptime_human': str(uptime).split('.')[0],
                'system': {
                    'cpu_usage_percent': cpu_percent,
                    'memory_usage_percent': memory.percent,
                    'memory_available_gb': round(memory.available / (1024**3), 2),
                    'disk_usage_percent': disk.percent,
                    'disk_free_gb': round(disk.free / (1024**3), 2),
                    'load_average': os.getloadavg() if hasattr(os, 'getloadavg') else [0, 0, 0]
                },
                'rabbitmq': {
                    'connection_status': 'connected' if self.connection and self.connection.is_open else 'disconnected',
                    'channel_status': 'connected' if self.channel and self.channel.is_open else 'disconnected'
                },
                'service': {
                    'messages_received': self.stats['messages_received'],
                    'messages_processed': self.stats['messages_processed'],
                    'messages_failed': self.stats['messages_failed'],
                    'success_rate_percent': round(
                        (self.stats['messages_processed'] / max(self.stats['messages_received'], 1)) * 100, 2
                    )
                },
                'timestamp': datetime.now().isoformat()
            }
            
            # Determinar estado general
            if cpu_percent > 90 or memory.percent > 90 or disk.percent > 90:
                health_data['status'] = 'warning'
            if cpu_percent > 95 or memory.percent > 95 or disk.percent > 95:
                health_data['status'] = 'critical'
            
            self.service_status = health_data['status']
            return health_data
            
        except Exception as e:
            logger.error(f"Error obteniendo salud del servicio: {str(e)}")
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _send_heartbeat_response(self, response_data: Dict[str, Any]):
        """
        Envía la respuesta de heartbeat al banco.
        
        Args:
            response_data: Datos de respuesta
        """
        try:
            message_body = json.dumps(response_data, ensure_ascii=False)
            
            self.channel.basic_publish(
                exchange=self.exchange_name,
                routing_key=self.routing_key_service_status,
                body=message_body,
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Make message persistent
                    correlation_id=response_data.get('correlation_id'),
                    content_type='application/json',
                    timestamp=int(time.time())
                )
            )
            
            logger.debug(f"Heartbeat response enviado - CorrelationID: {response_data.get('correlation_id')}")
            
        except Exception as e:
            logger.error(f"Error enviando respuesta de heartbeat: {str(e)}")
            raise
    
    def _send_service_heartbeat(self):
        """
        Envía heartbeat proactivo del servicio al banco.
        """
        try:
            heartbeat_data = {
                'service_name': 'lp2_reniec_service',
                'service_version': '1.0.0',
                'timestamp': datetime.now().isoformat(),
                'status': self.service_status,
                'health_data': self._get_service_health(),
                'stats': self.stats.copy()
            }
            
            message_body = json.dumps(heartbeat_data, ensure_ascii=False)
            
            self.channel.basic_publish(
                exchange=self.exchange_name,
                routing_key='service.heartbeat.notification',
                body=message_body,
                properties=pika.BasicProperties(
                    delivery_mode=2,
                    content_type='application/json',
                    timestamp=int(time.time())
                )
            )
            
            self.stats['heartbeats_sent'] += 1
            self.stats['last_heartbeat_sent'] = datetime.now()
            
            logger.debug(f"Service heartbeat enviado: {self.service_status}")
            
        except Exception as e:
            logger.error(f"Error enviando service heartbeat: {str(e)}")
    
    def _heartbeat_monitor(self):
        """
        Thread para envío proactivo de heartbeats.
        """
        logger.info("Thread de heartbeat monitor iniciado")
        
        while not self.should_stop.is_set():
            try:
                # Enviar heartbeat cada interval
                if self.connection and self.connection.is_open:
                    self._send_service_heartbeat()
                
                # Verificar conectividad con banco
                self._check_bank_connectivity()
                
                # Esperar siguiente heartbeat
                self.should_stop.wait(self.heartbeat_interval)
                
            except Exception as e:
                logger.error(f"Error en heartbeat monitor: {str(e)}")
                time.sleep(self.heartbeat_interval)
        
        logger.info("Thread de heartbeat monitor terminado")
    
    def _check_bank_connectivity(self):
        """
        Verifica la conectividad con el banco basada en heartbeats recibidos.
        """
        if self.last_heartbeat_received:
            time_since_last = datetime.now() - self.last_heartbeat_received
            
            if time_since_last.total_seconds() > self.heartbeat_timeout:
                if self.bank_status != "disconnected":
                    self.bank_status = "disconnected"
                    logger.warning(f"Banco desconectado - Último heartbeat hace {time_since_last}")
            else:
                if self.bank_status == "disconnected":
                    self.bank_status = "reconnected"
                    logger.info("Banco reconectado - Heartbeats recibidos")
        else:
            # Nunca se ha recibido heartbeat del banco
            if self.bank_status != "never_connected":
                self.bank_status = "never_connected"
                logger.info("Banco nunca ha enviado heartbeats")
    
    def _status_monitor(self):
        """
        Thread para monitoreo continuo del estado del servicio.
        """
        logger.info("Thread de status monitor iniciado")
        
        while not self.should_stop.is_set():
            try:
                # Actualizar uptime
                uptime = datetime.now() - self.stats['start_time']
                self.stats['service_uptime'] = int(uptime.total_seconds())
                
                # Log periódico de estadísticas
                if int(uptime.total_seconds()) % 300 == 0:  # Cada 5 minutos
                    logger.info(f"Estadísticas del servicio: {self.stats}")
                    logger.info(f"Estado del banco: {self.bank_status}")
                    logger.info(f"Estado del servicio: {self.service_status}")
                
                # Verificar estado de conexión RabbitMQ
                if not self.connection or not self.connection.is_open:
                    logger.error("Conexión RabbitMQ perdida, intentando reconectar...")
                    if self.connect():
                        logger.info("Reconexión exitosa a RabbitMQ")
                    else:
                        logger.error("Fallo en reconexión a RabbitMQ")
                
                time.sleep(30)  # Verificar cada 30 segundos
                
            except Exception as e:
                logger.error(f"Error en status monitor: {str(e)}")
                time.sleep(30)
        
        logger.info("Thread de status monitor terminado")
    
    def start_consuming(self):
        """
        Inicia el consumo de mensajes y threads de monitoreo.
        """
        if not self.connect():
            logger.error("No se pudo establecer conexión con RabbitMQ")
            return
        
        try:
            # Iniciar threads de monitoreo
            self.heartbeat_thread = threading.Thread(target=self._heartbeat_monitor, daemon=True)
            self.monitoring_thread = threading.Thread(target=self._status_monitor, daemon=True)
            
            self.heartbeat_thread.start()
            self.monitoring_thread.start()
            
            # Configurar callback con reintentos
            def process_with_retry(ch, method, properties, body):
                max_retries = self.retry_attempts
                current_retry = 0
                
                while current_retry < max_retries:
                    try:
                        success = self.process_heartbeat_request(ch, method, properties, body)
                        
                        if success:
                            # Acknowledge del mensaje
                            ch.basic_ack(delivery_tag=method.delivery_tag)
                            logger.debug("Heartbeat procesado y acknowledged")
                            break
                        else:
                            current_retry += 1
                            if current_retry < max_retries:
                                logger.warning(f"Reintentando procesamiento de heartbeat... Intento {current_retry}/{max_retries}")
                                time.sleep(self.retry_delay)
                            else:
                                logger.error("Max reintentos alcanzados para heartbeat, rejectando mensaje")
                                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
                                
                    except Exception as e:
                        current_retry += 1
                        logger.error(f"Error en intento {current_retry} de heartbeat: {str(e)}")
                        
                        if current_retry < max_retries:
                            logger.warning(f"Reintentando en {self.retry_delay} segundos...")
                            time.sleep(self.retry_delay)
                        else:
                            logger.error("Max reintentos alcanzados para heartbeat, rejectando mensaje")
                            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            
            # Configurar consumer
            self.channel.basic_consume(
                queue=self.queue_name,
                on_message_callback=process_with_retry,
                auto_ack=False
            )
            
            logger.info("Iniciando consumo de mensajes de heartbeat...")
            logger.info(f"Heartbeat monitor: {self.heartbeat_interval}s, Timeout: {self.heartbeat_timeout}s")
            self.channel.start_consuming()
            
        except KeyboardInterrupt:
            logger.info("Deteniendo listener de heartbeat...")
            self.stop()
        except Exception as e:
            logger.error(f"Error en consumo de mensajes de heartbeat: {str(e)}")
            self.stop()
    
    def stop(self):
        """
        Cierra la conexión y detiene todos los threads.
        """
        try:
            self.should_stop.set()
            
            # Cerrar conexión RabbitMQ
            if self.channel:
                self.channel.stop_consuming()
            if self.connection:
                self.connection.close()
            
            # Esperar threads
            if self.heartbeat_thread and self.heartbeat_thread.is_alive():
                self.heartbeat_thread.join(timeout=5)
            if self.monitoring_thread and self.monitoring_thread.is_alive():
                self.monitoring_thread.join(timeout=5)
            
            # Log final de estadísticas
            final_uptime = datetime.now() - self.stats['start_time']
            logger.info(f"Listener detenido. Uptime total: {final_uptime}")
            logger.info(f"Estadísticas finales: {self.stats}")
            
        except Exception as e:
            logger.error(f"Error cerrando listener de heartbeat: {str(e)}")
    
    def get_service_status(self) -> Dict[str, Any]:
        """
        Retorna el estado actual del servicio.
        
        Returns:
            Dict con estado del servicio
        """
        return {
            'service_status': self.service_status,
            'bank_status': self.bank_status,
            'last_heartbeat_received': self.last_heartbeat_received.isoformat() if self.last_heartbeat_received else None,
            'stats': self.stats.copy(),
            'health_data': self._get_service_health(),
            'timestamp': datetime.now().isoformat()
        }

def main():
    """
    Función principal para ejecutar el listener de heartbeat.
    """
    listener = HeartbeatListener()
    
    try:
        listener.start_consuming()
    except Exception as e:
        logger.error(f"Error ejecutando listener de heartbeat: {str(e)}")
    finally:
        listener.stop()

if __name__ == "__main__":
    main()