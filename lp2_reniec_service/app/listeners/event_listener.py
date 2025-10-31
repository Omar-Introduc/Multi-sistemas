"""
Listeners para eventos del sistema
"""

import asyncio
from typing import Callable, Dict, Any
from loguru import logger


class EventListener:
    """
    Sistema simple de listeners para eventos
    """
    
    def __init__(self):
        self.listeners: Dict[str, list] = {}
    
    def on(self, event_name: str, callback: Callable):
        """
        Registrar listener para un evento
        """
        if event_name not in self.listeners:
            self.listeners[event_name] = []
        
        self.listeners[event_name].append(callback)
        logger.debug(f"Listener registrado para evento: {event_name}")
    
    async def emit(self, event_name: str, data: Any = None):
        """
        Emitir evento y ejecutar listeners
        """
        if event_name not in self.listeners:
            return
        
        tasks = []
        for callback in self.listeners[event_name]:
            try:
                if asyncio.iscoroutinefunction(callback):
                    task = asyncio.create_task(callback(data))
                    tasks.append(task)
                else:
                    callback(data)
            except Exception as e:
                logger.error(f"Error ejecutando listener para {event_name}: {e}")
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)


# Instancia global del event listener
event_listener = EventListener()


# Eventos predefinidos
CITIZEN_CREATED = "citizen.created"
DOCUMENT_CREATED = "document.created"
SOLICITUD_CREATED = "solicitud.created"
RENIEC_QUERY = "reniec.query"
SYSTEM_ERROR = "system.error"


# Listeners de ejemplo
async def log_event_listener(event_data: Dict[str, Any]):
    """
    Listener para loggear todos los eventos
    """
    logger.info(f"Evento emitido: {event_data}")


async def citizen_created_listener(data: Dict[str, Any]):
    """
    Listener cuando se crea un ciudadano
    """
    logger.info(f"Nuevo ciudadano creado: {data.get('documento_identidad', 'N/A')}")
    
    # Aquí se podría enviar notificación, generar PDF, etc.


async def document_created_listener(data: Dict[str, Any]):
    """
    Listener cuando se crea un documento
    """
    logger.info(f"Documento creado: {data.get('numero_documento', 'N/A')}")


# Registrar listeners por defecto
event_listener.on(CITIZEN_CREATED, citizen_created_listener)
event_listener.on(DOCUMENT_CREATED, document_created_listener)
event_listener.on("*", log_event_listener)  # Listener global para debugging