"""
Routers para la aplicación FastAPI
"""

from .health_check import router as health_check
from .reniec_endpoints import router as reniec_endpoints
from .document_management import router as document_management
from .citizen_services import router as citizen_services

__all__ = [
    "health_check",
    "reniec_endpoints", 
    "document_management",
    "citizen_services"
]