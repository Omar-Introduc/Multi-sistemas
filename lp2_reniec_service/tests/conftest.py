"""
Configuración y fixtures para pruebas pytest del servicio RENIEC
"""

import pytest
import tempfile
import os
from unittest.mock import Mock, patch
from datetime import datetime, date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

# Importar modelos y configuraciones
from app.config.database import Base, get_db
from app.config.settings import get_settings
from main import app


# ================== FIXTURES DE BASE DE DATOS ==================

@pytest.fixture(scope="session")
def test_database_url():
    """URL de base de datos para pruebas"""
    return "sqlite:///:memory:"


@pytest.fixture(scope="session")
def test_engine(test_database_url):
    """Engine de SQLAlchemy para pruebas"""
    engine = create_engine(
        test_database_url,
        connect_args={"check_same_thread": False},
        echo=False  # Cambiar a True para debug
    )
    
    # Crear todas las tablas
    Base.metadata.create_all(bind=engine)
    
    yield engine
    
    # Cleanup
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="session")
def TestingSessionLocal(test_engine):
    """Session maker para pruebas"""
    return sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=test_engine
    )


@pytest.fixture
def db_session(TestingSessionLocal):
    """Session de base de datos para cada test"""
    session = TestingSessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


@pytest.fixture
def test_db_override(db_session):
    """Override de dependencia de BD para tests"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    yield
    app.dependency_overrides.clear()


# ================== FIXTURES DE CLIENTE HTTP ==================

@pytest.fixture
def test_client(test_db_override):
    """Cliente de prueba para FastAPI"""
    return TestClient(app)


@pytest.fixture
def test_client_with_auth():
    """Cliente con autenticación simulada"""
    # Implementar según necesidades de auth
    def auth_headers():
        return {"Authorization": "Bearer test-token"}
    
    client = TestClient(app)
    client.headers.update(auth_headers())
    return client


# ================== FIXTURES DE MOCKS ==================

@pytest.fixture
def mock_reniec_api():
    """Mock de la API RENIEC"""
    with patch('app.services.reniec_service.ReniecService') as mock_service:
        yield mock_service.return_value


@pytest.fixture
def mock_ciudadano_service():
    """Mock del servicio de ciudadanos"""
    with patch('app.services.ciudadano_service.CiudadanoService') as mock_service:
        yield mock_service.return_value


@pytest.fixture
def mock_documento_service():
    """Mock del servicio de documentos"""
    with patch('app.services.documento_service.DocumentoService') as mock_service:
        yield mock_service.return_value


@pytest.fixture
def mock_rabbitmq_service():
    """Mock del servicio RabbitMQ"""
    with patch('app.services.rabbit_service.RabbitMQService') as mock_service:
        yield mock_service.return_value


@pytest.fixture
def mock_log_service():
    """Mock del servicio de logs"""
    with patch('app.services.log_service.LogService') as mock_service:
        yield mock_service.return_value


# ================== FIXTURES DE DATOS DE PRUEBA ==================

@pytest.fixture
def sample_ciudadano_data():
    """Datos de ejemplo para crear ciudadano"""
    return {
        "documento_identidad": "12345678",
        "nombres": "JUAN CARLOS",
        "apellidos": "PEREZ GARCIA",
        "fecha_nacimiento": "1990-01-15",
        "lugar_nacimiento": "LIMA",
        "genero": "M",
        "estado_civil": "SOLTERO",
        "direccion": "AV. PRINCIPAL 123",
        "telefono": "987654321",
        "email": "juan.perez@example.com"
    }


@pytest.fixture
def sample_tipo_documento_data():
    """Datos de ejemplo para tipo de documento"""
    return {
        "codigo": "DNI",
        "nombre": "Documento Nacional de Identidad",
        "descripcion": "Documento principal de identidad",
        "requiere_renovacion": False,
        "vigencia_meses": None
    }


@pytest.fixture
def sample_documento_data():
    """Datos de ejemplo para documento"""
    return {
        "numero_documento": "12345678",
        "ciudadano_id": 1,
        "tipo_documento_id": 1,
        "fecha_emision": "2020-01-01",
        "fecha_vencimiento": "2030-01-01",
        "estado": "vigente"
    }


@pytest.fixture
def sample_solicitud_data():
    """Datos de ejemplo para solicitud"""
    return {
        "numero_solicitud": "SOL-001",
        "ciudadano_id": 1,
        "documento_id": 1,
        "tipo_solicitud": "primera_vez",
        "motivo": "Solicitud inicial",
        "observaciones": "Ninguna",
        "estado": "pendiente"
    }


@pytest.fixture
def sample_reniec_response():
    """Respuesta de ejemplo de RENIEC"""
    return {
        "dni": "12345678",
        "nombres": "JUAN CARLOS",
        "apellido_paterno": "PEREZ",
        "apellido_materno": "GARCIA",
        "fecha_nacimiento": "1990-01-15",
        "lugar_nacimiento": "LIMA",
        "genero": "M",
        "direccion": "AV. PRINCIPAL 123"
    }


# ================== FIXTURES DE OBJETOS MOCK ==================

@pytest.fixture
def mock_ciudadano():
    """Objeto mock de ciudadano"""
    mock_obj = Mock()
    mock_obj.id = 1
    mock_obj.documento_identidad = "12345678"
    mock_obj.nombres = "JUAN CARLOS"
    mock_obj.apellidos = "PEREZ GARCIA"
    mock_obj.fecha_nacimiento = date(1990, 1, 15)
    mock_obj.lugar_nacimiento = "LIMA"
    mock_obj.genero = "M"
    mock_obj.estado_civil = "SOLTERO"
    mock_obj.direccion = "AV. PRINCIPAL 123"
    mock_obj.telefono = "987654321"
    mock_obj.email = "juan.perez@example.com"
    mock_obj.activo = True
    mock_obj.fecha_creacion = datetime.now()
    mock_obj.fecha_actualizacion = datetime.now()
    mock_obj.documentos = []
    mock_obj.solicitudes = []
    return mock_obj


@pytest.fixture
def mock_tipo_documento():
    """Objeto mock de tipo de documento"""
    mock_obj = Mock()
    mock_obj.id = 1
    mock_obj.codigo = "DNI"
    mock_obj.nombre = "Documento Nacional de Identidad"
    mock_obj.descripcion = "Documento principal"
    mock_obj.requiere_renovacion = False
    mock_obj.vigencia_meses = None
    mock_obj.activo = True
    mock_obj.fecha_creacion = datetime.now()
    return mock_obj


@pytest.fixture
def mock_documento():
    """Objeto mock de documento"""
    mock_obj = Mock()
    mock_obj.id = 1
    mock_obj.numero_documento = "12345678"
    mock_obj.ciudadano_id = 1
    mock_obj.tipo_documento_id = 1
    mock_obj.fecha_emision = date(2020, 1, 1)
    mock_obj.fecha_vencimiento = date(2030, 1, 1)
    mock_obj.estado = "vigente"
    mock_obj.archivo_documento = "/path/to/document.pdf"
    mock_obj.metadatos = {"size": 1024, "type": "pdf"}
    mock_obj.activo = True
    mock_obj.fecha_creacion = datetime.now()
    mock_obj.fecha_actualizacion = datetime.now()
    
    # Mock relaciones
    mock_obj.ciudadano = Mock()
    mock_obj.ciudadano.nombres = "JUAN CARLOS"
    mock_obj.ciudadano.apellidos = "PEREZ"
    mock_obj.ciudadano.genero = "M"
    
    mock_obj.tipo_documento = Mock()
    mock_obj.tipo_documento.nombre = "DNI"
    
    return mock_obj


@pytest.fixture
def mock_solicitud():
    """Objeto mock de solicitud"""
    mock_obj = Mock()
    mock_obj.id = 1
    mock_obj.numero_solicitud = "SOL-001"
    mock_obj.ciudadano_id = 1
    mock_obj.documento_id = 1
    mock_obj.tipo_solicitud = "primera_vez"
    mock_obj.motivo = "Solicitud inicial"
    mock_obj.observaciones = "Ninguna"
    mock_obj.estado = "pendiente"
    mock_obj.fecha_solicitud = datetime.now()
    mock_obj.fecha_procesamiento = None
    mock_obj.fecha_entrega = None
    
    # Mock relaciones
    mock_obj.ciudadano = Mock()
    mock_obj.ciudadano.documento_identidad = "12345678"
    
    mock_obj.documento = Mock()
    mock_obj.documento.numero_documento = "12345678"
    
    return mock_obj


# ================== FIXTURES DE ENTORNOS ==================

@pytest.fixture
def temp_directory():
    """Directorio temporal para pruebas"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def mock_settings():
    """Configuración mock para pruebas"""
    with patch('app.config.settings.get_settings') as mock_get_settings:
        settings = Mock()
        settings.DATABASE_URL = "sqlite:///:memory:"
        settings.RENIEC_API_URL = "https://test-reniec-api.com"
        settings.RENIEC_API_KEY = "test-api-key"
        settings.RABBITMQ_URL = "amqp://test:test@localhost:5672"
        settings.REDIS_URL = "redis://localhost:6379/0"
        settings.LOG_LEVEL = "DEBUG"
        settings.DEBUG = True
        mock_get_settings.return_value = settings
        yield settings


# ================== FIXTURES DE CONFIGURACIÓN ==================

@pytest.fixture(autouse=True)
def setup_test_environment():
    """Configuración automática del entorno de pruebas"""
    # Configurar variables de entorno para pruebas
    os.environ["ENVIRONMENT"] = "test"
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"
    os.environ["DEBUG"] = "true"
    
    yield
    
    # Cleanup
    # No es necesario limpiar variables de entorno ya que son por proceso


@pytest.fixture
def clean_db(db_session):
    """Limpiar BD antes y después de cada test"""
    # Limpiar antes
    for table in reversed(Base.metadata.sorted_tables):
        db_session.execute(table.delete())
    db_session.commit()
    
    yield
    
    # Limpiar después
    for table in reversed(Base.metadata.sorted_tables):
        db_session.execute(table.delete())
    db_session.commit()


# ================== FIXTURES ESPECIALIZADAS ==================

@pytest.fixture
def populated_db(clean_db):
    """Base de datos con datos de prueba"""
    from app.models.reniec_models import (
        Ciudadano, TipoDocumento, Documento, Solicitud, EventoSolicitud
    )
    
    # Crear ciudadano
    ciudadano = Ciudadano(
        documento_identidad="12345678",
        nombres="JUAN CARLOS",
        apellidos="PEREZ GARCIA",
        fecha_nacimiento=date(1990, 1, 15),
        lugar_nacimiento="LIMA",
        genero="M",
        estado_civil="SOLTERO",
        direccion="AV. PRINCIPAL 123",
        telefono="987654321",
        email="juan@example.com"
    )
    clean_db.add(ciudadano)
    clean_db.commit()
    
    # Crear tipo de documento
    tipo_doc = TipoDocumento(
        codigo="DNI",
        nombre="Documento Nacional de Identidad",
        descripcion="Documento principal",
        requiere_renovacion=False
    )
    clean_db.add(tipo_doc)
    clean_db.commit()
    
    # Crear documento
    documento = Documento(
        numero_documento="12345678",
        ciudadano_id=ciudadano.id,
        tipo_documento_id=tipo_doc.id,
        fecha_emision=date(2020, 1, 1),
        fecha_vencimiento=date(2030, 1, 1),
        estado="vigente"
    )
    clean_db.add(documento)
    clean_db.commit()
    
    # Crear solicitud
    solicitud = Solicitud(
        numero_solicitud="SOL-001",
        ciudadano_id=ciudadano.id,
        documento_id=documento.id,
        tipo_solicitud="primera_vez",
        estado="pendiente"
    )
    clean_db.add(solicitud)
    clean_db.commit()
    
    # Crear evento
    evento = EventoSolicitud(
        solicitud_id=solicitud.id,
        evento="solicitud_creada",
        descripcion="Solicitud inicial",
        usuario="admin"
    )
    clean_db.add(evento)
    clean_db.commit()
    
    return {
        "ciudadano": ciudadano,
        "tipo_documento": tipo_doc,
        "documento": documento,
        "solicitud": solicitud,
        "evento": evento
    }


@pytest.fixture
def mock_external_api():
    """Mock de APIs externas (RENIEC, etc.)"""
    responses = {}
    
    def setup_response(endpoint, response_data, status_code=200):
        responses[endpoint] = {
            "data": response_data,
            "status": status_code
        }
    
    with patch('requests.get') as mock_get, \
         patch('requests.post') as mock_post, \
         patch('httpx.get') as mock_httpx_get, \
         patch('httpx.post') as mock_httpx_post:
        
        def mock_response_func(url, *args, **kwargs):
            response = Mock()
            
            # Buscar respuesta mockeada
            for endpoint, response_data in responses.items():
                if endpoint in url:
                    response.status_code = response_data["status"]
                    response.json.return_value = response_data["data"]
                    return response
            
            # Respuesta por defecto
            response.status_code = 404
            response.json.return_value = {"error": "Not found"}
            return response
        
        mock_get.side_effect = mock_response_func
        mock_post.side_effect = mock_response_func
        mock_httpx_get.side_effect = mock_response_func
        mock_httpx_post.side_effect = mock_response_func
        
        yield {"setup": setup_response}


# ================== FIXTURES DE LOGGING ==================

@pytest.fixture
def caplog(caplog):
    """Fixture para capturar logs durante tests"""
    import logging
    
    # Configurar logging para pruebas
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    
    yield caplog


# ================== MARKERS ==================

# Definir markers personalizados
pytest_plugins = []


def pytest_configure(config):
    """Configuración personalizada de pytest"""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "unit: mark test as unit test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "external_api: mark test as requiring external API"
    )
    config.addinivalue_line(
        "markers", "database: mark test as requiring database"
    )


# ================== HOOKS ==================

def pytest_runtest_setup(item):
    """Setup antes de cada test"""
    # Configurar modo de prueba
    os.environ["TESTING"] = "true"


def pytest_runtest_teardown(item):
    """Cleanup después de cada test"""
    # Limpiar estado de prueba
    if hasattr(item, "request"):
        # Cerrar conexiones de BD si es necesario
        pass


def pytest_sessionstart(session):
    """Setup al inicio de la sesión de tests"""
    print("Iniciando suite de pruebas para LP2 RENIEC Service")
    print(f"Tests encontrados: {len(session.items)}")


def pytest_sessionfinish(session, exitstatus):
    """Cleanup al final de la sesión de tests"""
    print(f"\nFinalizando suite de pruebas")
    print(f"Exit status: {exitstatus}")
    print(f"Tests ejecutados: {session.testscollected}")
