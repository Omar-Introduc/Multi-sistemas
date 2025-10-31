"""
Servicio para integración con RabbitMQ
"""

import pika
import json
import asyncio
from typing import Callable, Optional, Dict, Any
from loguru import logger
from app.config.settings import settings, RABBITMQ_CONFIG


class RabbitService:
    """
    Servicio para manejo de colas RabbitMQ
    """
    
    def __init__(self):
        self.connection = None
        self.channel = None
        self.connected = False
        self.exchange_name = "reniec_exchange"
    
    async def initialize_rabbit(self):
        """
        Inicializar conexión con RabbitMQ
        """
        try:
            logger.info("Inicializando conexión con RabbitMQ...")
            
            # Crear conexión síncrona pero manejar en thread pool
            def _connect():
                return pika.BlockingConnection(
                    pika.URLParameters(settings.rabbitmq_url)
                )
            
            loop = asyncio.get_event_loop()
            self.connection = await loop.run_in_executor(None, _connect)
            
            # Crear canal
            self.channel = self.connection.channel()
            
            # Declarar exchange
            self.channel.exchange_declare(
                exchange=self.exchange_name,
                exchange_type='topic',
                durable=True
            )
            
            # Declarar cola principal
            self.channel.queue_declare(
                queue=settings.rabbitmq_queue,
                durable=True,
                exclusive=False,
                auto_delete=False
            )
            
            # Vincular cola al exchange
            self.channel.queue_bind(
                exchange=self.exchange_name,
                queue=settings.rabbitmq_queue,
                routing_key="reniec.*"
            )
            
            self.connected = True
            logger.info("✅ Conexión con RabbitMQ establecida correctamente")
            
        except Exception as e:
            logger.error(f"❌ Error inicializando RabbitMQ: {e}")
            self.connected = False
            raise
    
    def close_rabbit(self):
        """
        Cerrar conexión con RabbitMQ
        """
        try:
            if self.connection and not self.connection.is_closed:
                self.connection.close()
                logger.info("✅ Conexión RabbitMQ cerrada correctamente")
        except Exception as e:
            logger.error(f"❌ Error cerrando RabbitMQ: {e}")
        finally:
            self.connected = False
            self.connection = None
            self.channel = None
    
    async def publish_message(self, routing_key: str, message: Dict[str, Any], priority: int = 0):
        """
        Publicar mensaje en la cola
        """
        if not self.connected:
            logger.warning("RabbitMQ no está conectado, intentando reconectar...")
            await self.initialize_rabbit()
        
        try:
            message_body = json.dumps(message, default=str)
            
            def _publish():
                self.channel.basic_publish(
                    exchange=self.exchange_name,
                    routing_key=routing_key,
                    body=message_body,
                    properties=pika.BasicProperties(
                        delivery_mode=2,  # Hacer mensaje persistente
                        priority=priority,
                        message_id=message.get('id', ''),
                        timestamp=int(asyncio.get_event_loop().time())
                    )
                )
            
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, _publish)
            
            logger.info(f"Mensaje publicado en cola {routing_key}")
            
        except Exception as e:
            logger.error(f"Error publicando mensaje: {e}")
            raise
    
    async def consume_messages(self, callback: Callable, queue_name: str = None):
        """
        Consumir mensajes de la cola
        """
        if not self.connected:
            raise RuntimeError("RabbitMQ no está conectado")
        
        queue_name = queue_name or settings.rabbitmq_queue
        
        def _callback(ch, method, properties, body):
            try:
                message = json.loads(body.decode('utf-8'))
                asyncio.create_task(callback(message))
                ch.basic_ack(delivery_tag=method.delivery_tag)
            except Exception as e:
                logger.error(f"Error procesando mensaje: {e}")
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
        
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(
            queue=queue_name,
            on_message_callback=_callback,
            auto_ack=False
        )
        
        logger.info(f"Iniciando consumo de mensajes de cola {queue_name}")
        
        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            self.channel.stop_consuming()
        except Exception as e:
            logger.error(f"Error en consumo de mensajes: {e}")
            raise
    
    async def publish_citizen_created(self, citizen_data: Dict[str, Any]):
        """
        Publicar evento de ciudadano creado
        """
        event_message = {
            "event": "citizen.created",
            "timestamp": asyncio.get_event_loop().time(),
            "data": citizen_data
        }
        
        await self.publish_message(
            routing_key="reniec.citizen.created",
            message=event_message,
            priority=1
        )
    
    async def publish_document_created(self, document_data: Dict[str, Any]):
        """
        Publicar evento de documento creado
        """
        event_message = {
            "event": "document.created",
            "timestamp": asyncio.get_event_loop().time(),
            "data": document_data
        }
        
        await self.publish_message(
            routing_key="reniec.document.created",
            message=event_message,
            priority=1
        )
    
    async def publish_reniec_query(self, query_data: Dict[str, Any]):
        """
        Publicar consulta a RENIEC
        """
        event_message = {
            "event": "reniec.query",
            "timestamp": asyncio.get_event_loop().time(),
            "data": query_data
        }
        
        await self.publish_message(
            routing_key="reniec.api.query",
            message=event_message,
            priority=2
        )


# Instancia global del servicio
rabbit_service = RabbitService()


async def initialize_rabbit():
    """Función para inicializar RabbitMQ"""
    await rabbit_service.initialize_rabbit()


def close_rabbit():
    """Función para cerrar RabbitMQ"""
    rabbit_service.close_rabbit()


def test_rabbit_connection() -> bool:
    """Probar conexión a RabbitMQ"""
    try:
        if rabbit_service.connected:
            return True
        
        # Intentar conexión básica
        connection = pika.BlockingConnection(
            pika.URLParameters(settings.rabbitmq_url)
        )
        connection.close()
        return True
        
    except Exception as e:
        logger.error(f"Error probando conexión RabbitMQ: {e}")
        return False