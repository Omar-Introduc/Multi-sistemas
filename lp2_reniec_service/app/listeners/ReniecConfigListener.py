"""
Listener para recibir configuraciones del sistema desde el servidor central.
Maneja actualizaciones de configuración dinámicas.
"""

import pika
import json
import logging
import time
import yaml
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path
import threading

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ReniecConfigListener:
    """
    Listener que maneja las configuraciones del sistema RENIEC.
    Recibe actualizaciones de configuración dinámicas y las aplica.
    """
    
    def __init__(self, rabbitmq_host: str = 'localhost', queue_name: str = 'reniec.config.queue'):
        """
        Inicializa el listener de configuraciones.
        
        Args:
            rabbitmq_host: Host de RabbitMQ
            queue_name: Nombre de la cola de configuraciones
        """
        self.rabbitmq_host = rabbitmq_host
        self.queue_name = queue_name
        self.connection = None
        self.channel = None
        self.retry_attempts = 3
        self.retry_delay = 5  # segundos
        
        # Configuración del sistema
        self.config_path = Path(__file__).parent.parent.parent / 'config' / 'system_config.yaml'
        self.config_lock = threading.Lock()
        self.current_config = {}
        
        # Configuración de exchange y routing keys
        self.exchange_name = 'reniec.config'
        self.routing_key_config_update = 'reniec.config.update'
        self.routing_key_config_request = 'reniec.config.request'
        
        logger.info(f"Inicializando ReniecConfigListener para queue: {queue_name}")
        self._load_current_config()
    
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
                    'x-dead-letter-routing-key': 'config.failed',
                    'x-message-ttl': 600000  # 10 minutos para configuraciones
                }
            )
            
            # Configurar QoS - prefetch_count para manejo eficiente de mensajes
            self.channel.basic_qos(prefetch_count=1, global_qos=False)
            
            # Bind de la cola al exchange
            self.channel.queue_bind(
                exchange=self.exchange_name,
                queue=self.queue_name,
                routing_key=self.routing_key_config_update
            )
            
            # Declarar cola de respuesta para solicitudes de configuración
            self.response_queue = 'reniec.config.response'
            self.channel.queue_declare(
                queue=self.response_queue,
                durable=True,
                exclusive=True,
                auto_delete=True
            )
            
            logger.info(f"Conectado exitosamente a RabbitMQ: {self.rabbitmq_host}")
            return True
            
        except Exception as e:
            logger.error(f"Error conectando a RabbitMQ: {str(e)}")
            return False
    
    def _load_current_config(self):
        """
        Carga la configuración actual desde archivo.
        """
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self.current_config = yaml.safe_load(f) or {}
                logger.info("Configuración actual cargada exitosamente")
            else:
                # Configuración por defecto
                self.current_config = self._get_default_config()
                self._save_config()
                logger.info("Configuración por defecto creada")
        except Exception as e:
            logger.error(f"Error cargando configuración: {str(e)}")
            self.current_config = self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """
        Retorna configuración por defecto del sistema.
        
        Returns:
            Dict con configuración por defecto
        """
        return {
            'service': {
                'name': 'lp2_reniec_service',
                'version': '1.0.0',
                'environment': 'development'
            },
            'rabbitmq': {
                'host': 'localhost',
                'port': 5672,
                'username': 'guest',
                'password': 'guest'
            },
            'reniec': {
                'endpoint': 'https://api.reniec.gob.pe',
                'timeout': 30,
                'max_retries': 3,
                'retry_delay': 5
            },
            'logging': {
                'level': 'INFO',
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            },
            'validation': {
                'enabled': True,
                'cache_ttl': 300,
                'max_concurrent_requests': 100
            },
            'heartbeat': {
                'enabled': True,
                'interval': 30,
                'timeout': 10
            }
        }
    
    def _save_config(self):
        """
        Guarda la configuración actual al archivo.
        """
        try:
            # Crear directorio si no existe
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.current_config, f, default_flow_style=False, allow_unicode=True)
            
            logger.info("Configuración guardada exitosamente")
        except Exception as e:
            logger.error(f"Error guardando configuración: {str(e)}")
    
    def process_config_update(self, ch, method, properties, body) -> bool:
        """
        Procesa una actualización de configuración.
        
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
            config_data = json.loads(body)
            correlation_id = properties.correlation_id
            
            logger.info(f"Procesando actualización de configuración - CorrelationID: {correlation_id}")
            logger.debug(f"Datos de configuración: {config_data}")
            
            # Validar estructura de configuración
            if not self._validate_config_structure(config_data):
                raise ValueError("Estructura de configuración inválida")
            
            # Aplicar configuración con thread safety
            with self.config_lock:
                self.current_config = self._merge_configs(self.current_config, config_data)
                self._save_config()
            
            # Enviar confirmación
            self._send_config_confirmation(correlation_id)
            
            # Aplicar cambios en tiempo real si es necesario
            self._apply_runtime_config_changes(config_data)
            
            logger.info(f"Configuración actualizada exitosamente - CorrelationID: {correlation_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error procesando actualización de configuración: {str(e)}")
            return False
    
    def _validate_config_structure(self, config_data: Dict[str, Any]) -> bool:
        """
        Valida la estructura de los datos de configuración.
        
        Args:
            config_data: Datos de configuración a validar
            
        Returns:
            bool: True si la estructura es válida
        """
        try:
            # Validaciones básicas de estructura
            if not isinstance(config_data, dict):
                return False
            
            # Validar secciones permitidas
            allowed_sections = {'service', 'rabbitmq', 'reniec', 'logging', 'validation', 'heartbeat', 'custom'}
            for section in config_data.keys():
                if section not in allowed_sections and not section.startswith('custom_'):
                    logger.warning(f"Sección de configuración no reconocida: {section}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error validando estructura de configuración: {str(e)}")
            return False
    
    def _merge_configs(self, current: Dict[str, Any], new: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge de configuraciones actuales con nuevas.
        
        Args:
            current: Configuración actual
            new: Nueva configuración
            
        Returns:
            Dict con configuraciones mergeadas
        """
        merged = current.copy()
        
        for key, value in new.items():
            if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                merged[key] = self._merge_configs(merged[key], value)
            else:
                merged[key] = value
        
        return merged
    
    def _apply_runtime_config_changes(self, config_data: Dict[str, Any]):
        """
        Aplica cambios de configuración que requieren aplicación en tiempo real.
        
        Args:
            config_data: Nuevos datos de configuración
        """
        try:
            # Aplicar cambios de logging en tiempo real
            if 'logging' in config_data:
                log_level = config_data['logging'].get('level')
                if log_level:
                    logging.getLogger().setLevel(getattr(logging, log_level.upper()))
                    logger.info(f"Nivel de logging actualizado: {log_level}")
            
            # Aplicar cambios de heartbeat en tiempo real
            if 'heartbeat' in config_data:
                heartbeat_config = config_data['heartbeat']
                logger.info(f"Configuración de heartbeat actualizada: {heartbeat_config}")
            
            # Aplicar cambios de validación en tiempo real
            if 'validation' in config_data:
                validation_config = config_data['validation']
                logger.info(f"Configuración de validación actualizada: {validation_config}")
            
        except Exception as e:
            logger.error(f"Error aplicando cambios en tiempo real: {str(e)}")
    
    def _send_config_confirmation(self, correlation_id: str):
        """
        Envía confirmación de actualización de configuración.
        
        Args:
            correlation_id: ID de correlación del mensaje original
        """
        try:
            confirmation_data = {
                'correlation_id': correlation_id,
                'status': 'success',
                'timestamp': datetime.now().isoformat(),
                'message': 'Configuración actualizada exitosamente',
                'updated_config': self.current_config
            }
            
            message_body = json.dumps(confirmation_data, ensure_ascii=False)
            
            self.channel.basic_publish(
                exchange=self.exchange_name,
                routing_key=self.routing_key_config_update + '.response',
                body=message_body,
                properties=pika.BasicProperties(
                    delivery_mode=2,
                    correlation_id=correlation_id,
                    content_type='application/json',
                    timestamp=int(time.time())
                )
            )
            
            logger.info(f"Confirmación enviada para CorrelationID: {correlation_id}")
            
        except Exception as e:
            logger.error(f"Error enviando confirmación de configuración: {str(e)}")
    
    def get_current_config(self) -> Dict[str, Any]:
        """
        Retorna la configuración actual (thread-safe).
        
        Returns:
            Dict con configuración actual
        """
        with self.config_lock:
            return self.current_config.copy()
    
    def request_config_update(self, config_data: Dict[str, Any], timeout: int = 30) -> bool:
        """
        Solicita una actualización de configuración y espera confirmación.
        
        Args:
            config_data: Datos de configuración a actualizar
            timeout: Timeout en segundos para la respuesta
            
        Returns:
            bool: True si la actualización fue confirmada
        """
        try:
            correlation_id = f"config_request_{int(time.time())}"
            
            message_body = json.dumps(config_data, ensure_ascii=False)
            
            # Crear callback para recibir respuesta
            response_received = threading.Event()
            response_data = {}
            
            def config_callback(ch, method, properties, body):
                if properties.correlation_id == correlation_id:
                    response_data['data'] = json.loads(body)
                    response_received.set()
            
            # Iniciar consumer temporal para la respuesta
            self.channel.basic_consume(
                queue=self.response_queue,
                on_message_callback=config_callback,
                auto_ack=True
            )
            
            # Enviar solicitud de actualización
            self.channel.basic_publish(
                exchange=self.exchange_name,
                routing_key=self.routing_key_config_update,
                body=message_body,
                properties=pika.BasicProperties(
                    delivery_mode=2,
                    correlation_id=correlation_id,
                    content_type='application/json',
                    reply_to=self.response_queue,
                    timestamp=int(time.time())
                )
            )
            
            # Esperar confirmación con timeout
            if response_received.wait(timeout):
                return response_data.get('data', {}).get('status') == 'success'
            else:
                logger.warning("Timeout esperando confirmación de configuración")
                return False
                
        except Exception as e:
            logger.error(f"Error solicitando actualización de configuración: {str(e)}")
            return False
    
    def start_consuming(self):
        """
        Inicia el consumo de mensajes con manejo de reintentos.
        """
        if not self.connect():
            logger.error("No se pudo establecer conexión con RabbitMQ")
            return
        
        try:
            # Configurar callback con reintentos
            def process_with_retry(ch, method, properties, body):
                max_retries = self.retry_attempts
                current_retry = 0
                
                while current_retry < max_retries:
                    try:
                        success = self.process_config_update(ch, method, properties, body)
                        
                        if success:
                            # Acknowledge del mensaje
                            ch.basic_ack(delivery_tag=method.delivery_tag)
                            logger.info("Configuración procesada y acknowledged")
                            break
                        else:
                            current_retry += 1
                            if current_retry < max_retries:
                                logger.warning(f"Reintentando procesamiento de configuración... Intento {current_retry}/{max_retries}")
                                time.sleep(self.retry_delay)
                            else:
                                logger.error("Max reintentos alcanzados para configuración, rejectando mensaje")
                                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
                                
                    except Exception as e:
                        current_retry += 1
                        logger.error(f"Error en intento {current_retry} de configuración: {str(e)}")
                        
                        if current_retry < max_retries:
                            logger.warning(f"Reintentando en {self.retry_delay} segundos...")
                            time.sleep(self.retry_delay)
                        else:
                            logger.error("Max reintentos alcanzados para configuración, rejectando mensaje")
                            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            
            # Configurar consumer
            self.channel.basic_consume(
                queue=self.queue_name,
                on_message_callback=process_with_retry,
                auto_ack=False
            )
            
            logger.info("Iniciando consumo de mensajes de configuración...")
            self.channel.start_consuming()
            
        except KeyboardInterrupt:
            logger.info("Deteniendo listener de configuración...")
            self.stop()
        except Exception as e:
            logger.error(f"Error en consumo de mensajes de configuración: {str(e)}")
            self.stop()
    
    def stop(self):
        """
        Cierra la conexión con RabbitMQ.
        """
        try:
            if self.channel:
                self.channel.stop_consuming()
            if self.connection:
                self.connection.close()
            logger.info("Conexión de configuración cerrada exitosamente")
        except Exception as e:
            logger.error(f"Error cerrando conexión de configuración: {str(e)}")

def main():
    """
    Función principal para ejecutar el listener de configuración.
    """
    listener = ReniecConfigListener()
    
    try:
        listener.start_consuming()
    except Exception as e:
        logger.error(f"Error ejecutando listener de configuración: {str(e)}")
    finally:
        listener.stop()

if __name__ == "__main__":
    main()