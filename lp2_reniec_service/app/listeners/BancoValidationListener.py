"""
Listener para solicitudes de validación desde el banco.
Procesa validaciones de identidad y envía respuestas.
"""

import pika
import json
import logging
import time
from typing import Dict, Any, Optional
from datetime import datetime
import uuid

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BancoValidationListener:
    """
    Listener que maneja las solicitudes de validación desde el banco.
    Procesa validaciones de documentos de identidad y retorna resultados.
    """
    
    def __init__(self, rabbitmq_host: str = 'localhost', queue_name: str = 'banco.validation.queue'):
        """
        Inicializa el listener de validaciones.
        
        Args:
            rabbitmq_host: Host de RabbitMQ
            queue_name: Nombre de la cola de validaciones
        """
        self.rabbitmq_host = rabbitmq_host
        self.queue_name = queue_name
        self.connection = None
        self.channel = None
        self.retry_attempts = 3
        self.retry_delay = 5  # segundos
        
        # Configuración de exchange y routing keys
        self.exchange_name = 'banco.validations'
        self.routing_key_validation_request = 'banco.validation.request'
        self.routing_key_validation_response = 'banco.validation.response'
        
        logger.info(f"Inicializando BancoValidationListener para queue: {queue_name}")
    
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
                    'x-dead-letter-routing-key': 'validation.failed',
                    'x-message-ttl': 300000  # 5 minutos
                }
            )
            
            # Configurar QoS - prefetch_count para manejo eficiente de mensajes
            self.channel.basic_qos(prefetch_count=1, global_qos=False)
            
            # Bind de la cola al exchange
            self.channel.queue_bind(
                exchange=self.exchange_name,
                queue=self.queue_name,
                routing_key=self.routing_key_validation_request
            )
            
            logger.info(f"Conectado exitosamente a RabbitMQ: {self.rabbitmq_host}")
            return True
            
        except Exception as e:
            logger.error(f"Error conectando a RabbitMQ: {str(e)}")
            return False
    
    def process_validation_request(self, ch, method, properties, body) -> bool:
        """
        Procesa una solicitud de validación desde el banco.
        
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
            request_data = json.loads(body)
            correlation_id = properties.correlation_id or str(uuid.uuid4())
            
            logger.info(f"Procesando solicitud de validación - CorrelationID: {correlation_id}")
            logger.debug(f"Datos de solicitud: {request_data}")
            
            # Extraer datos de validación
            documento_identidad = request_data.get('documento_identidad')
            tipo_documento = request_data.get('tipo_documento', 'DNI')
            solicitud_id = request_data.get('solicitud_id')
            
            if not documento_identidad:
                raise ValueError("documento_identidad es requerido")
            
            # Simular validación de identidad (aquí iría la lógica real)
            validation_result = self._validate_identity(
                documento_identidad=documento_identidad,
                tipo_documento=tipo_documento
            )
            
            # Preparar respuesta
            response_data = {
                'correlation_id': correlation_id,
                'solicitud_id': solicitud_id,
                'documento_identidad': documento_identidad,
                'tipo_documento': tipo_documento,
                'validation_result': validation_result,
                'timestamp': datetime.now().isoformat(),
                'processed_by': 'lp2_reniec_service'
            }
            
            # Enviar respuesta al banco
            self._send_validation_response(response_data)
            
            logger.info(f"Validación procesada exitosamente - CorrelationID: {correlation_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error procesando solicitud de validación: {str(e)}")
            return False
    
    def _validate_identity(self, documento_identidad: str, tipo_documento: str) -> Dict[str, Any]:
        """
        Realiza la validación de identidad contra RENIEC.
        
        Args:
            documento_identidad: Número de documento
            tipo_documento: Tipo de documento (DNI, CE, etc.)
            
        Returns:
            Dict con resultado de validación
        """
        try:
            logger.debug(f"Validando identidad: {documento_identidad} ({tipo_documento})")
            
            # Simular consulta a RENIEC (aquí iría la llamada real al servicio RENIEC)
            time.sleep(1)  # Simular latencia de red
            
            # Lógica simulada de validación
            if len(documento_identidad) == 8 and tipo_documento == 'DNI':
                is_valid = True
                nombres = "JUAN CARLOS"
                apellidos = "PEREZ GARCIA"
                estado_civil = "SOLTERO"
            else:
                is_valid = False
                nombres = ""
                apellidos = ""
                estado_civil = ""
            
            return {
                'valido': is_valid,
                'datos': {
                    'nombres': nombres,
                    'apellidos': apellidos,
                    'estado_civil': estado_civil
                },
                'fuente': 'RENIEC',
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error en validación de identidad: {str(e)}")
            return {
                'valido': False,
                'error': str(e),
                'fuente': 'RENIEC',
                'timestamp': datetime.now().isoformat()
            }
    
    def _send_validation_response(self, response_data: Dict[str, Any]):
        """
        Envía la respuesta de validación al banco.
        
        Args:
            response_data: Datos de respuesta
        """
        try:
            message_body = json.dumps(response_data, ensure_ascii=False)
            
            self.channel.basic_publish(
                exchange=self.exchange_name,
                routing_key=self.routing_key_validation_response,
                body=message_body,
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Make message persistent
                    correlation_id=response_data.get('correlation_id'),
                    content_type='application/json',
                    timestamp=int(time.time())
                )
            )
            
            logger.info(f"Respuesta enviada - CorrelationID: {response_data.get('correlation_id')}")
            
        except Exception as e:
            logger.error(f"Error enviando respuesta de validación: {str(e)}")
            raise
    
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
                        success = self.process_validation_request(ch, method, properties, body)
                        
                        if success:
                            # Acknowledge del mensaje solo si fue procesado exitosamente
                            ch.basic_ack(delivery_tag=method.delivery_tag)
                            logger.info("Mensaje procesado y acknowledged")
                            break
                        else:
                            current_retry += 1
                            if current_retry < max_retries:
                                logger.warning(f"Reintentando procesamiento... Intento {current_retry}/{max_retries}")
                                time.sleep(self.retry_delay)
                            else:
                                logger.error("Max reintentos alcanzados, rejectando mensaje")
                                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
                                
                    except Exception as e:
                        current_retry += 1
                        logger.error(f"Error en intento {current_retry}: {str(e)}")
                        
                        if current_retry < max_retries:
                            logger.warning(f"Reintentando en {self.retry_delay} segundos...")
                            time.sleep(self.retry_delay)
                        else:
                            logger.error("Max reintentos alcanzados, rejectando mensaje")
                            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            
            # Configurar consumer
            self.channel.basic_consume(
                queue=self.queue_name,
                on_message_callback=process_with_retry,
                auto_ack=False
            )
            
            logger.info("Iniciando consumo de mensajes de validación...")
            self.channel.start_consuming()
            
        except KeyboardInterrupt:
            logger.info("Deteniendo listener...")
            self.stop()
        except Exception as e:
            logger.error(f"Error en consumo de mensajes: {str(e)}")
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
            logger.info("Conexión cerrada exitosamente")
        except Exception as e:
            logger.error(f"Error cerrando conexión: {str(e)}")

def main():
    """
    Función principal para ejecutar el listener.
    """
    listener = BancoValidationListener()
    
    try:
        listener.start_consuming()
    except Exception as e:
        logger.error(f"Error ejecutando listener: {str(e)}")
    finally:
        listener.stop()

if __name__ == "__main__":
    main()