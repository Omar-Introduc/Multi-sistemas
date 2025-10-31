"""
Tests básicos para el servicio RENIEC
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
import tempfile

# Configuración de test
TEST_DATABASE_URL = "sqlite:///:memory:"

# Crear engine de prueba
engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """
    Override para base de datos de test
    """
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


# Importar después de configurar el override
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from app.config.database import Base

# Crear tablas de prueba
Base.metadata.create_all(bind=engine)

# Aplicar override
app.dependency_overrides[None] = override_get_db

client = TestClient(app)


class TestHealthCheck:
    """Tests para endpoint de health check"""
    
    def test_health_check(self):
        """Test health check básico"""
        response = client.get("/api/v1/health/")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "healthy" in data["status"]
    
    def test_detailed_health_check(self):
        """Test health check detallado"""
        response = client.get("/api/v1/health/detailed")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "checks" in data


class TestReniecEndpoints:
    """Tests para endpoints de RENIEC"""
    
    def test_consulta_dni_invalido(self):
        """Test consulta de DNI con formato inválido"""
        response = client.get("/api/v1/reniec/consulta-dni/12345")
        assert response.status_code == 400
        assert "8 dígitos" in response.json()["detail"]
    
    def test_consulta_dni_formato_valido(self):
        """Test consulta de DNI con formato válido pero no existente"""
        response = client.get("/api/v1/reniec/consulta-dni/12345678")
        # Puede fallar por conexión con RENIEC, eso es normal
        assert response.status_code in [200, 404, 503]
    
    def test_verificar_dni_sin_dni(self):
        """Test verificar DNI sin proporcionar DNI"""
        response = client.post("/api/v1/reniec/verificar-dni", json={})
        assert response.status_code == 400
        assert "DNI es requerido" in response.json()["detail"]
    
    def test_verificar_dni_con_dni(self):
        """Test verificar DNI con DNI proporcionado"""
        response = client.post("/api/v1/reniec/verificar-dni", json={"dni": "12345678"})
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "data" in data


class TestDocumentManagement:
    """Tests para gestión de documentos"""
    
    def test_listar_documentos_vacio(self):
        """Test listar documentos cuando no hay ninguno"""
        response = client.get("/api/v1/documents/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_listar_documentos_con_paginacion(self):
        """Test listar documentos con parámetros de paginación"""
        response = client.get("/api/v1/documents/?skip=0&limit=10")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestCitizenServices:
    """Tests para servicios de ciudadanos"""
    
    def test_listar_ciudadanos_vacio(self):
        """Test listar ciudadanos cuando no hay ninguno"""
        response = client.get("/api/v1/citizens/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_listar_ciudadanos_con_paginacion(self):
        """Test listar ciudadanos con parámetros de paginación"""
        response = client.get("/api/v1/citizens/?skip=0&limit=10")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestUtils:
    """Tests para utilidades"""
    
    def test_file_handler_creation(self):
        """Test creación del manejador de archivos"""
        from app.utils.file_handler import FileHandler
        
        with tempfile.TemporaryDirectory() as temp_dir:
            handler = FileHandler(temp_dir)
            assert handler.base_path.exists()
    
    def test_validacion_archivo(self):
        """Test validación de archivos"""
        from app.utils.file_handler import FileHandler
        
        handler = FileHandler()
        
        # Crear mock de UploadFile
        class MockFile:
            def __init__(self, filename, size=0):
                self.filename = filename
                self.file = None
                self.size = size
        
        mock_file = MockFile("test.pdf", 1024)
        
        # Esta prueba solo verificaría la lógica básica
        # ya que no tenemos un archivo real para validar
        result = handler.validar_archivo(mock_file)
        assert "valido" in result


if __name__ == "__main__":
    # Ejecutar tests manualmente
    pytest.main([__file__, "-v"])