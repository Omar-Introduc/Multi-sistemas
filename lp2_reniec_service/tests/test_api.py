"""
Pruebas para endpoints FastAPI del servicio RENIEC
"""

import pytest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, date

# Importar la aplicación
from main import app
from app.config.database import Base


class TestHealthCheckEndpoints:
    """Pruebas para endpoints de health check"""
    
    @pytest.fixture
    def test_client(self):
        """Cliente de prueba"""
        return TestClient(app)
    
    def test_health_check_basic(self, test_client):
        """Test health check básico"""
        response = test_client.get("/api/v1/health/")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert "healthy" in data["status"]
    
    def test_health_check_detailed(self, test_client):
        """Test health check detallado"""
        response = test_client.get("/api/v1/health/detailed")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert "checks" in data
        assert "database" in data["checks"] or "reniec_api" in data["checks"]


class TestReniecEndpoints:
    """Pruebas para endpoints de RENIEC"""
    
    @pytest.fixture
    def test_client(self):
        """Cliente de prueba"""
        return TestClient(app)
    
    def test_consulta_dni_invalid_format(self, test_client):
        """Test consulta de DNI con formato inválido"""
        # DNI muy corto
        response = test_client.get("/api/v1/reniec/consulta-dni/12345")
        assert response.status_code == 400
        assert "8 dígitos" in response.json()["detail"]
    
    def test_consulta_dni_letters(self, test_client):
        """Test consulta de DNI con letras"""
        response = test_client.get("/api/v1/reniec/consulta-dni/12345abc")
        assert response.status_code == 400
        assert "8 dígitos" in response.json()["detail"]
    
    @patch('app.services.reniec_service.ReniecService.consultar_dni')
    def test_consulta_dni_valid_not_found(self, mock_consulta, test_client):
        """Test consulta de DNI válido pero no encontrado en RENIEC"""
        mock_consulta.return_value = None
        
        response = test_client.get("/api/v1/reniec/consulta-dni/12345678")
        assert response.status_code == 404
        assert "No se encontraron datos" in response.json()["detail"]
    
    @patch('app.services.reniec_service.ReniecService.consultar_dni')
    @patch('app.services.ciudadano_service.CiudadanoService.buscar_por_documento')
    def test_consulta_dni_success_new_citizen(self, mock_buscar, mock_consulta, test_client):
        """Test consulta de DNI exitosa - nuevo ciudadano"""
        # Mock de datos RENIEC
        mock_consulta.return_value = {
            "dni": "12345678",
            "nombres": "JUAN CARLOS",
            "apellido_paterno": "PEREZ",
            "apellido_materno": "GARCIA",
            "fecha_nacimiento": "1990-01-15",
            "lugar_nacimiento": "LIMA",
            "genero": "M",
            "direccion": "AV. PRINCIPAL 123"
        }
        
        # Mock ciudadano no encontrado
        mock_buscar.return_value = None
        
        response = test_client.get("/api/v1/reniec/consulta-dni/12345678")
        assert response.status_code == 200
        
        data = response.json()
        assert "documento_identidad" in data
        assert data["documento_identidad"] == "12345678"
        assert "nombres" in data
    
    @patch('app.services.reniec_service.ReniecService.consultar_dni')
    @patch('app.services.ciudadano_service.CiudadanoService.buscar_por_documento')
    def test_consulta_dni_success_existing_citizen(self, mock_buscar, mock_consulta, test_client):
        """Test consulta de DNI exitosa - ciudadano existente"""
        # Mock de datos RENIEC
        mock_consulta.return_value = {
            "dni": "12345678",
            "nombres": "JUAN CARLOS",
            "apellido_paterno": "PEREZ",
            "apellido_materno": "GARCIA"
        }
        
        # Mock ciudadano encontrado
        mock_buscar.return_value = Mock(
            documento_identidad="12345678",
            nombres="JUAN CARLOS",
            apellidos="PEREZ GARCIA"
        )
        
        response = test_client.get("/api/v1/reniec/consulta-dni/12345678")
        assert response.status_code == 200
        
        data = response.json()
        assert data["documento_identidad"] == "12345678"
    
    @patch('app.services.reniec_service.ReniecService.consultar_dni')
    def test_consulta_dni_internal_error(self, mock_consulta, test_client):
        """Test consulta de DNI con error interno"""
        mock_consulta.side_effect = Exception("Error interno RENIEC")
        
        response = test_client.get("/api/v1/reniec/consulta-dni/12345678")
        assert response.status_code == 500
        assert "Error interno" in response.json()["detail"]
    
    def test_verificar_dni_no_dni_provided(self, test_client):
        """Test verificar DNI sin proporcionar DNI"""
        response = test_client.post("/api/v1/reniec/verificar-dni", json={})
        assert response.status_code == 400
        assert "DNI es requerido" in response.json()["detail"]
    
    def test_verificar_dni_empty_dni(self, test_client):
        """Test verificar DNI con DNI vacío"""
        response = test_client.post("/api/v1/reniec/verificar-dni", json={"dni": ""})
        assert response.status_code == 400
    
    @patch('app.services.reniec_service.ReniecService.verificar_dni')
    def test_verificar_dni_success(self, mock_verificar, test_client):
        """Test verificación exitosa de DNI"""
        mock_verificar.return_value = {
            "valido": True,
            "datos": {
                "dni": "12345678",
                "nombres": "JUAN CARLOS"
            }
        }
        
        response = test_client.post("/api/v1/reniec/verificar-dni", json={"dni": "12345678"})
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "data" in data
        assert data["data"]["dni"] == "12345678"
        assert data["data"]["valido"] is True
    
    @patch('app.services.reniec_service.ReniecService.verificar_dni')
    def test_verificar_dni_invalid(self, mock_verificar, test_client):
        """Test verificación de DNI inválido"""
        mock_verificar.return_value = {
            "valido": False,
            "datos": {}
        }
        
        response = test_client.post("/api/v1/reniec/verificar-dni", json={"dni": "99999999"})
        assert response.status_code == 200
        
        data = response.json()
        assert data["data"]["valido"] is False
    
    @patch('app.services.reniec_service.ReniecService.verificar_dni')
    def test_verificar_dni_error(self, mock_verificar, test_client):
        """Test verificación de DNI con error"""
        mock_verificar.side_effect = Exception("Error verificando DNI")
        
        response = test_client.post("/api/v1/reniec/verificar-dni", json={"dni": "12345678"})
        assert response.status_code == 500
        assert "Error interno" in response.json()["detail"]


class TestDocumentEndpoints:
    """Pruebas para endpoints de documentos"""
    
    @pytest.fixture
    def test_client(self):
        """Cliente de prueba"""
        return TestClient(app)
    
    @patch('app.services.ciudadano_service.CiudadanoService.buscar_documento')
    def test_consultar_documento_not_found(self, mock_buscar, test_client):
        """Test consulta de documento no encontrado"""
        mock_buscar.return_value = None
        
        response = test_client.get("/api/v1/reniec/documento/12345678")
        assert response.status_code == 404
        assert "no encontrado" in response.json()["detail"]
    
    @patch('app.services.ciudadano_service.CiudadanoService.buscar_documento')
    @patch('app.services.reniec_service.ReniecService.consultar_dni')
    def test_consultar_documento_dni_success(self, mock_consulta, mock_buscar, test_client):
        """Test consulta de documento DNI exitoso"""
        # Mock documento
        mock_documento = Mock()
        mock_documento.numero_documento = "12345678"
        mock_documento.estado = "vigente"
        mock_documento.fecha_emision = date(2020, 1, 1)
        mock_documento.fecha_vencimiento = date(2030, 1, 1)
        
        # Mock tipo documento
        mock_tipo_doc = Mock()
        mock_tipo_doc.nombre = "Documento Nacional de Identidad"
        mock_documento.tipo_documento = mock_tipo_doc
        
        # Mock ciudadano
        mock_ciudadano = Mock()
        mock_ciudadano.nombres = "JUAN CARLOS"
        mock_ciudadano.apellidos = "PEREZ"
        mock_ciudadano.genero = "M"
        mock_documento.ciudadano = mock_ciudadano
        
        # Mock búsqueda de documento
        mock_buscar.return_value = mock_documento
        
        # Mock consulta RENIEC
        mock_consulta.return_value = {
            "dni": "12345678",
            "nombres": "JUAN CARLOS"
        }
        
        response = test_client.get("/api/v1/reniec/documento/12345678")
        assert response.status_code == 200
        
        data = response.json()
        assert "documento" in data
        assert "ciudadano" in data
        assert "reniec" in data
        assert data["documento"]["numero"] == "12345678"
    
    @patch('app.services.ciudadano_service.CiudadanoService.buscar_documento')
    def test_consultar_documento_non_dni(self, mock_buscar, test_client):
        """Test consulta de documento que no es DNI"""
        # Mock documento (no DNI)
        mock_documento = Mock()
        mock_documento.numero_documento = "CARTA-001"
        mock_documento.estado = "vigente"
        
        # Mock tipo documento
        mock_tipo_doc = Mock()
        mock_tipo_doc.nombre = "Carta de presentación"
        mock_documento.tipo_documento = mock_tipo_doc
        
        # Mock ciudadano
        mock_ciudadano = Mock()
        mock_ciudadano.nombres = "JUAN CARLOS"
        mock_ciudadano.apellidos = "PEREZ"
        mock_ciudadano.genero = "M"
        mock_documento.ciudadano = mock_ciudadano
        
        # Mock búsqueda de documento
        mock_buscar.return_value = mock_documento
        
        response = test_client.get("/api/v1/reniec/documento/CARTA-001")
        assert response.status_code == 200
        
        data = response.json()
        assert "documento" in data
        assert "ciudadano" in data
        assert "reniec" not in data  # No debe incluir datos de RENIEC para no-DNI


class TestStatisticsEndpoint:
    """Pruebas para endpoint de estadísticas"""
    
    @pytest.fixture
    def test_client(self):
        """Cliente de prueba"""
        return TestClient(app)
    
    @patch('app.services.reniec_service.ReniecService.obtener_estadisticas')
    @patch('app.services.ciudadano_service.CiudadanoService.obtener_estadisticas')
    def test_obtener_estadisticas_success(self, mock_db_stats, mock_reniec_stats, test_client):
        """Test obtención exitosa de estadísticas"""
        # Mock estadísticas RENIEC
        mock_reniec_stats.return_value = {
            "consultas_realizadas": 100,
            "consultas_exitosas": 95
        }
        
        # Mock estadísticas BD
        mock_db_stats.return_value = {
            "total_activos": 50,
            "total_inactivos": 10
        }
        
        response = test_client.get("/api/v1/reniec/estadisticas")
        assert response.status_code == 200
        
        data = response.json()
        assert "reniec_api" in data
        assert "base_datos" in data
        assert "timestamp" in data
        assert data["reniec_api"]["consultas_realizadas"] == 100
        assert data["base_datos"]["total_activos"] == 50
    
    @patch('app.services.reniec_service.ReniecService.obtener_estadisticas')
    def test_obtener_estadisticas_error(self, mock_reniec_stats, test_client):
        """Test obtención de estadísticas con error"""
        mock_reniec_stats.side_effect = Exception("Error obteniendo stats")
        
        response = test_client.get("/api/v1/reniec/estadisticas")
        assert response.status_code == 500
        assert "Error interno" in response.json()["detail"]


class TestCitizenEndpoints:
    """Pruebas para endpoints de ciudadanos"""
    
    @pytest.fixture
    def test_client(self):
        """Cliente de prueba"""
        return TestClient(app)
    
    def test_listar_ciudadanos_empty(self, test_client):
        """Test listado de ciudadanos vacío"""
        response = test_client.get("/api/v1/citizens/")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
    
    def test_listar_ciudadanos_with_pagination(self, test_client):
        """Test listado de ciudadanos con paginación"""
        response = test_client.get("/api/v1/citizens/?skip=0&limit=10")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
    
    def test_listar_ciudadanos_invalid_pagination(self, test_client):
        """Test listado con parámetros de paginación inválidos"""
        # Paginación con valores negativos o muy grandes
        response = test_client.get("/api/v1/citizens/?skip=-1&limit=1000")
        assert response.status_code == 200  # Debería manejar valores inválidos
    
    @patch('app.services.ciudadano_service.CiudadanoService.crear')
    def test_crear_ciudadano_success(self, mock_crear, test_client):
        """Test creación exitosa de ciudadano"""
        # Mock ciudadano creado
        mock_ciudadano = Mock(
            id=1,
            documento_identidad="12345678",
            nombres="JUAN CARLOS",
            apellidos="PEREZ"
        )
        mock_crear.return_value = mock_ciudadano
        
        ciudadano_data = {
            "documento_identidad": "12345678",
            "nombres": "JUAN CARLOS",
            "apellidos": "PEREZ",
            "fecha_nacimiento": "1990-01-15",
            "lugar_nacimiento": "LIMA",
            "genero": "M",
            "estado_civil": "SOLTERO",
            "direccion": "AV. PRINCIPAL 123",
            "telefono": "987654321",
            "email": "juan@example.com"
        }
        
        response = test_client.post("/api/v1/citizens/", json=ciudadano_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["documento_identidad"] == "12345678"
    
    def test_crear_ciudadano_invalid_data(self, test_client):
        """Test creación de ciudadano con datos inválidos"""
        # DNI inválido
        ciudadano_data = {
            "documento_identidad": "12345",  # Muy corto
            "nombres": "JUAN",
            "apellidos": "PEREZ",
            "fecha_nacimiento": "1990-01-15",
            "genero": "M"
        }
        
        response = test_client.post("/api/v1/citizens/", json=ciudadano_data)
        assert response.status_code == 422  # Validation error


class TestDocumentManagementEndpoints:
    """Pruebas para endpoints de gestión de documentos"""
    
    @pytest.fixture
    def test_client(self):
        """Cliente de prueba"""
        return TestClient(app)
    
    def test_listar_documentos_empty(self, test_client):
        """Test listado de documentos vacío"""
        response = test_client.get("/api/v1/documents/")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
    
    def test_listar_documentos_with_pagination(self, test_client):
        """Test listado de documentos con paginación"""
        response = test_client.get("/api/v1/documents/?skip=0&limit=10")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
    
    @patch('app.services.documento_service.DocumentoService.crear')
    def test_crear_documento_success(self, mock_crear, test_client):
        """Test creación exitosa de documento"""
        # Mock documento creado
        mock_documento = Mock(
            id=1,
            numero_documento="12345678",
            estado="vigente"
        )
        mock_crear.return_value = mock_documento
        
        documento_data = {
            "numero_documento": "12345678",
            "ciudadano_id": 1,
            "tipo_documento_id": 1,
            "fecha_emision": "2020-01-01"
        }
        
        response = test_client.post("/api/v1/documents/", json=documento_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["numero_documento"] == "12345678"
    
    def test_crear_documento_invalid_data(self, test_client):
        """Test creación de documento con datos inválidos"""
        # Datos faltantes
        documento_data = {
            "numero_documento": "12345678"
            # Faltan campos requeridos
        }
        
        response = test_client.post("/api/v1/documents/", json=documento_data)
        assert response.status_code == 422  # Validation error


class TestAPIIntegration:
    """Pruebas de integración de API"""
    
    @pytest.fixture
    def test_client(self):
        """Cliente de prueba"""
        return TestClient(app)
    
    def test_full_workflow_consulta_dni(self, test_client):
        """Test flujo completo de consulta de DNI"""
        with patch('app.services.reniec_service.ReniecService.consultar_dni') as mock_reniec, \
             patch('app.services.ciudadano_service.CiudadanoService.buscar_por_documento') as mock_buscar, \
             patch('app.services.ciudadano_service.CiudadanoService.crear') as mock_crear:
            
            # Mock secuencia de llamadas
            mock_reniec.return_value = {
                "dni": "12345678",
                "nombres": "JUAN CARLOS",
                "apellido_paterno": "PEREZ",
                "apellido_materno": "GARCIA"
            }
            mock_buscar.return_value = None  # No existe
            mock_crear.return_value = Mock(documento_identidad="12345678")
            
            # Realizar consulta
            response = test_client.get("/api/v1/reniec/consulta-dni/12345678")
            
            assert response.status_code == 200
            assert response.json()["documento_identidad"] == "12345678"
    
    def test_api_error_handling(self, test_client):
        """Test manejo de errores de API"""
        # Test con datos que generen error
        response = test_client.get("/api/v1/reniec/consulta-dni/123")  # DNI muy corto
        assert response.status_code == 400
        
        response = test_client.post("/api/v1/reniec/verificar-dni", json={})
        assert response.status_code == 400
    
    def test_api_response_structure(self, test_client):
        """Test estructura de respuestas de API"""
        response = test_client.get("/api/v1/health/")
        assert response.status_code == 200
        
        # Verificar estructura básica
        data = response.json()
        assert isinstance(data, dict)
        assert "status" in data


class TestAPIAuthentication:
    """Pruebas para autenticación y autorización (si aplica)"""
    
    @pytest.fixture
    def test_client(self):
        """Cliente de prueba"""
        return TestClient(app)
    
    def test_public_endpoints_accessible(self, test_client):
        """Test que endpoints públicos son accesibles"""
        # Health check debe ser público
        response = test_client.get("/api/v1/health/")
        assert response.status_code == 200
    
    def test_endpoints_without_auth_if_public(self, test_client):
        """Test endpoints sin auth si son públicos"""
        # Los endpoints de consulta deben ser públicos
        response = test_client.get("/api/v1/reniec/consulta-dni/12345678")
        # Puede fallar por datos, pero no por auth
        assert response.status_code in [200, 404, 400, 500]


if __name__ == "__main__":
    # Ejecutar tests manualmente
    pytest.main([__file__, "-v"])
