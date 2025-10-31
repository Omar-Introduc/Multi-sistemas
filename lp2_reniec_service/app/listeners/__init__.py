"""
Listeners para el sistema RENIEC
"""

from .event_listener import (
    EventListener,
    event_listener,
    CITIZEN_CREATED,
    DOCUMENT_CREATED,
    SOLICITUD_CREATED,
    RENIEC_QUERY,
    SYSTEM_ERROR
)

__all__ = [
    "EventListener",
    "event_listener",
    "CITIZEN_CREATED",
    "DOCUMENT_CREATED",
    "SOLICITUD_CREATED",
    "RENIEC_QUERY",
    "SYSTEM_ERROR"
]