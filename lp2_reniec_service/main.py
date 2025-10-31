"""
Servicio LP2 RENIEC - API REST para consultas al Registro Nacional de Identificación y Estado Civil
Autor: Sistema Distribuido LP2
Fecha: 2025-10-30
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import uvicorn
import os
import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Crear aplicación FastAPI
app = FastAPI(
    title="LP2 RENIEC Service",
    description="Servicio de consultas al Registro Nacional de Identificación y Estado Civil",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelos Pydantic
class DniConsulta(BaseModel):
    """Modelo para consulta por DNI"""
    dni: str = Field(..., min_length=8, max_length=8, description="DNI a consultar")
    fecha_consulta: Optional[datetime] = Field(default_factory=datetime.now)

class PersonaResponse(BaseModel):
    """Respuesta de datos personales"""
    dni: str
    nombres: str
    apellido_paterno: str
    apellido_materno: str
    estado_civil: Optional[str] = None
    domicilio: Optional[str] = None
    fecha_nacimiento: Optional[str] = None
    lugar_nacimiento: Optional[str] = None
    estado: str = "activo"

class SaludResponse(BaseModel):
    """Respuesta de health check"""
    status: str
    timestamp: str
    service: str
    version: str

# Simulación de base de datos (en producción usar BD real)
database_simulada = {
    "12345678": {
        "dni": "12345678",
        "nombres": "JUAN CARLOS",
        "apellido_paterno": "PEREZ",
        "apellido_materno": "GARCIA",
        "estado_civil": "SOLTERO",
        "domicilio": "AV. PRINCIPAL 123",
        "fecha_nacimiento": "1990-01-15",
        "lugar_nacimiento": "LIMA"
    },
    "87654321": {
        "dni": "87654321",
        "nombres": "MARIA ELENA",
        "apellido_paterno": "LOPEZ",
        "apellido_materno": "RODRIGUEZ",
        "estado_civil": "CASADA",
        "domicilio": "CALLE SECUNDARIA 456",
        "fecha_nacimiento": "1985-05-20",
        "lugar_nacimiento": "AREQUIPA"
    }
}

@app.get("/health", response_model=SaludResponse)
async def health_check():
    """
    Endpoint de health check para monitoreo del servicio
    """
    return SaludResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        service="LP2 RENIEC Service",
        version="1.0.0"
    )

@app.get("/", tags=["raíz"])
async def raiz():
    """
    Endpoint raíz con información del servicio
    """
    return {
        "mensaje": "Servicio LP2 RENIEC activo",
        "version": "1.0.0",
        "documentacion": "/docs",
        "endpoints": {
            "health": "/health",
            "consulta_dni": "/consulta/dni/{dni}",
            "buscar_por_nombre": "/buscar/nombre"
        }
    }

@app.get("/consulta/dni/{dni}", response_model=PersonaResponse)
async def consultar_por_dni(dni: str):
    """
    Consulta datos de una persona por su DNI
    """
    logger.info(f"Consultando DNI: {dni}")
    
    # Validar formato de DNI
    if not dni.isdigit() or len(dni) != 8:
        raise HTTPException(
            status_code=400,
            detail="DNI debe tener exactamente 8 dígitos numéricos"
        )
    
    # Buscar en base de datos simulada
    persona = database_simulada.get(dni)
    
    if not persona:
        logger.warning(f"DNI no encontrado: {dni}")
        raise HTTPException(
            status_code=404,
            detail=f"No se encontró información para DNI: {dni}"
        )
    
    logger.info(f"DNI encontrado: {dni}")
    return PersonaResponse(**persona)

@app.post("/buscar/nombre", response_model=PersonaResponse)
async def buscar_por_nombre(datos_consulta: DniConsulta):
    """
    Endpoint alternativo para consulta por DNI (POST)
    """
    return await consultar_por_dni(datos_consulta.dni)

@app.get("/info")
async def info_sistema():
    """
    Información detallada del sistema
    """
    return {
        "servicio": "LP2 RENIEC",
        "descripcion": "Servicio de consultas al RENIEC",
        "version": "1.0.0",
        "fecha_inicio": datetime.now().isoformat(),
        "variables_entorno": {
            "host": os.getenv("HOST", "0.0.0.0"),
            "puerto": os.getenv("PORT", "8000")
        },
        "endpoints_disponibles": [
            "GET / - Información del servicio",
            "GET /health - Health check",
            "GET /consulta/dni/{dni} - Consulta por DNI",
            "POST /buscar/nombre - Búsqueda alternativa",
            "GET /info - Información del sistema",
            "GET /docs - Documentación Swagger",
            "GET /redoc - Documentación ReDoc"
        ]
    }

if __name__ == "__main__":
    # Configuración desde variables de entorno
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    
    logger.info(f"Iniciando servidor LP2 RENIEC en {host}:{port}")
    
    # Iniciar servidor
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=False,
        log_level="info",
        access_log=True
    )