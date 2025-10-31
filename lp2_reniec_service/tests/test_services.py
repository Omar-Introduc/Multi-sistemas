"""
Pruebas unitarias para servicios del servicio RENIEC
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, date
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Importar servicios
from app.services.ciudadano_service import CiudadanoService
from app.services.reniec_service import ReniecService
from app.services.documento_service import DocumentoService
from app.models.schemas import (
    CiudadanoCreate, CiudadanoUpdate, BusquedaCiudadano
)
from app.config.database import Base


class MockCiudadano:
    """Mock para modelo Ciudadano"""
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def __repr__(self):
        return f"<Ciudadano(id={self.id}, documento_identidad='{self.documento_identidad}')>"


class TestCiudadanoService:
    """Pruebas para CiudadanoService"""
    
    @pytest.fixture
    def mock_db(self):
        """Mock de base de datos"""
        return Mock(spec=Session)
    
    @pytest.fixture
    def ciudadano_service(self):
        """Instancia del servicio"""
        return CiudadanoService()
    
    @pytest.fixture
    def ciudadano_data(self):
        """Datos de ciudadano para pruebas"""
        return CiudadanoCreate(
            documento_identidad="12345678",
            nombres="Juan Carlos",
            apellidos="Pérez García",
            fecha_nacimiento=date(1990, 1, 15),
            lugar_nacimiento="Lima",
            genero="M",
            estado_civil="soltero",
            direccion="Av. Las Flores 123",
            telefono="987654321",
            email="juan.perez@example.com"
        )
    
    def test_crear_ciudadano_success(self, mock_db, ciudadano_service, ciudadano_data):
        """Test creación exitosa de ciudadano"""
        # Mock del ciudadano creado
        mock_ciudadano = MockCiudadano(
            id=1,
            documento_identidad="12345678",
            nombres="Juan Carlos",
            apellidos="Pérez García",
            fecha_nacimiento=date(1990, 1, 15),
            lugar_nacimiento="Lima",
            genero="M",
            estado_civil="soltero",
            direccion="Av. Las Flores 123",
            telefono="987654321",
            email="juan.perez@example.com",
            activo=True,
            fecha_creacion=datetime.now(),
            fecha_actualizacion=datetime.now()
        )
        
        mock_db.add = Mock()
        mock_db.commit = Mock()
        mock_db.refresh = Mock()
        
        # Configurar query mock
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        
        with patch('app.services.ciudadano_service.Ciudadano', return_value=mock_ciudadano):
            result = ciudadano_service.crear(mock_db, ciudadano_data)
            
            assert result is not None
            assert result.id == 1
            assert result.documento_identidad == "12345678"
            mock_db.add.assert_called_once()
            mock_db.commit.assert_called_once()
    
    def test_crear_ciudadano_error(self, mock_db, ciudadano_service, ciudadano_data):
        """Test error al crear ciudadano"""
        mock_db.add = Mock()
        mock_db.commit = Mock()
        mock_db.rollback = Mock()
        
        # Simular excepción
        with patch('app.services.ciudadano_service.Ciudadano', side_effect=Exception("Error de DB")):
            with pytest.raises(Exception):
                ciudadano_service.crear(mock_db, ciudadano_data)
            
            mock_db.rollback.assert_called_once()
    
    def test_obtener_por_id_success(self, mock_db, ciudadano_service):
        """Test obtención exitosa por ID"""
        mock_ciudadano = MockCiudadano(
            id=1,
            documento_identidad="12345678",
            nombres="Juan",
            activo=True
        )
        
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = mock_ciudadano
        mock_db.query.return_value = mock_query
        
        result = ciudadano_service.obtener_por_id(mock_db, 1)
        
        assert result is not None
        assert result.id == 1
        assert result.documento_identidad == "12345678"
    
    def test_obtener_por_id_not_found(self, mock_db, ciudadano_service):
        """Test obtención de ciudadano inexistente"""
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = None
        mock_db.query.return_value = mock_query
        
        result = ciudadano_service.obtener_por_id(mock_db, 999)
        
        assert result is None
    
    def test_buscar_por_documento_success(self, mock_db, ciudadano_service):
        """Test búsqueda exitosa por documento"""
        mock_ciudadano = MockCiudadano(
            id=1,
            documento_identidad="12345678",
            nombres="Juan",
            activo=True
        )
        
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = mock_ciudadano
        mock_db.query.return_value = mock_query
        
        result = ciudadano_service.buscar_por_documento(mock_db, "12345678")
        
        assert result is not None
        assert result.documento_identidad == "12345678"
    
    def test_buscar_por_documento_not_found(self, mock_db, ciudadano_service):
        """Test búsqueda de documento inexistente"""
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = None
        mock_db.query.return_value = mock_query
        
        result = ciudadano_service.buscar_por_documento(mock_db, "99999999")
        
        assert result is None
    
    def test_listar_ciudadanos_success(self, mock_db, ciudadano_service):
        """Test listado exitoso de ciudadanos"""
        mock_ciudadanos = [
            MockCiudadano(id=1, documento_identidad="12345678", activo=True),
            MockCiudadano(id=2, documento_identidad="87654321", activo=True)
        ]
        
        mock_query = Mock()
        mock_query.offset.return_value.limit.return_value.all.return_value = mock_ciudadanos
        mock_db.query.return_value = mock_query
        
        result = ciudadano_service.listar(mock_db, skip=0, limit=10)
        
        assert len(result) == 2
        assert result[0].id == 1
        assert result[1].id == 2
    
    def test_actualizar_ciudadano_success(self, mock_db, ciudadano_service):
        """Test actualización exitosa de ciudadano"""
        mock_ciudadano = MockCiudadano(
            id=1,
            documento_identidad="12345678",
            nombres="Juan",
            activo=True,
            fecha_actualizacion=datetime.now()
        )
        
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = mock_ciudadano
        mock_db.query.return_value = mock_query
        
        mock_db.commit = Mock()
        mock_db.refresh = Mock()
        
        update_data = CiudadanoUpdate(
            nombres="Juan Carlos",
            telefono="987654321"
        )
        
        result = ciudadano_service.actualizar(mock_db, 1, update_data)
        
        assert result is not None
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()
    
    def test_actualizar_ciudadano_not_found(self, mock_db, ciudadano_service):
        """Test actualización de ciudadano inexistente"""
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = None
        mock_db.query.return_value = mock_query
        
        update_data = CiudadanoUpdate(nombres="Juan")
        
        result = ciudadano_service.actualizar(mock_db, 999, update_data)
        
        assert result is None
    
    def test_eliminar_ciudadano_success(self, mock_db, ciudadano_service):
        """Test eliminación exitosa de ciudadano"""
        mock_ciudadano = MockCiudadano(
            id=1,
            documento_identidad="12345678",
            activo=True,
            fecha_actualizacion=datetime.now()
        )
        
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = mock_ciudadano
        mock_db.query.return_value = mock_query
        
        mock_db.commit = Mock()
        
        result = ciudadano_service.eliminar(mock_db, 1)
        
        assert result is True
        assert mock_ciudadano.activo == False
        mock_db.commit.assert_called_once()
    
    def test_eliminar_ciudadano_not_found(self, mock_db, ciudadano_service):
        """Test eliminación de ciudadano inexistente"""
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = None
        mock_db.query.return_value = mock_query
        
        result = ciudadano_service.eliminar(mock_db, 999)
        
        assert result is False
    
    def test_buscar_ciudadanos_success(self, mock_db, ciudadano_service):
        """Test búsqueda de ciudadanos por criterios"""
        mock_ciudadanos = [
            MockCiudadano(id=1, documento_identidad="12345678", nombres="Juan", activo=True)
        ]
        
        mock_query = Mock()
        mock_query.filter.return_value.all.return_value = mock_ciudadanos
        mock_db.query.return_value = mock_query
        
        criterio = BusquedaCiudadano(
            documento_identidad="12345678"
        )
        
        result = ciudadano_service.buscar(mock_db, criterio)
        
        assert len(result) == 1
        assert result[0].documento_identidad == "12345678"
    
    def test_existe_por_documento_true(self, mock_db, ciudadano_service):
        """Test existencia de ciudadano por documento (existe)"""
        mock_ciudadano = MockCiudadano(
            id=1,
            documento_identidad="12345678",
            activo=True
        )
        
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = mock_ciudadano
        mock_db.query.return_value = mock_query
        
        result = ciudadano_service.existe_por_documento(mock_db, "12345678")
        
        assert result is True
    
    def test_existe_por_documento_false(self, mock_db, ciudadano_service):
        """Test existencia de ciudadano por documento (no existe)"""
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = None
        mock_db.query.return_value = mock_query
        
        result = ciudadano_service.existe_por_documento(mock_db, "99999999")
        
        assert result is False
    
    def test_obtener_estadisticas_success(self, mock_db, ciudadano_service):
        """Test obtención exitosa de estadísticas"""
        mock_query = Mock()
        mock_query.filter.return_value.count.return_value = 10
        mock_db.query.return_value = mock_query
        
        result = ciudadano_service.obtener_estadisticas(mock_db)
        
        assert "total_activos" in result
        assert "total_inactivos" in result
        assert "total_general" in result
        assert result["total_activos"] == 10
        assert result["total_inactivos"] == 10


class TestReniecService:
    """Pruebas para ReniecService"""
    
    @pytest.fixture
    def reniec_service(self):
        """Instancia del servicio"""
        return ReniecService()
    
    def test_consultar_dni_success(self, reniec_service):
        """Test consulta exitosa de DNI"""
        mock_response = {
            "dni": "12345678",
            "nombres": "JUAN CARLOS",
            "apellido_paterno": "PEREZ",
            "apellido_materno": "GARCIA",
            "fecha_nacimiento": "1990-01-15",
            "lugar_nacimiento": "LIMA",
            "genero": "M"
        }
        
        with patch.object(reniec_service, 'consultar_dni_api', return_value=mock_response):
            result = reniec_service.consultar_dni("12345678")
            
            assert result is not None
            assert result["dni"] == "12345678"
            assert result["nombres"] == "JUAN CARLOS"
    
    def test_consultar_dni_not_found(self, reniec_service):
        """Test consulta de DNI inexistente"""
        with patch.object(reniec_service, 'consultar_dni_api', return_value=None):
            result = reniec_service.consultar_dni("99999999")
            
            assert result is None
    
    def test_consultar_dni_invalid_format(self, reniec_service):
        """Test consulta de DNI con formato inválido"""
        result = reniec_service.consultar_dni("12345")
        
        assert result is None
    
    def test_verificar_dni_success(self, reniec_service):
        """Test verificación exitosa de DNI"""
        mock_response = {
            "valido": True,
            "datos": {
                "dni": "12345678",
                "nombres": "JUAN CARLOS"
            }
        }
        
        with patch.object(reniec_service, 'consultar_dni_api', return_value=mock_response):
            result = reniec_service.verificar_dni("12345678")
            
            assert result is not None
            assert result["valido"] is True
            assert "datos" in result
    
    def test_verificar_dni_invalid(self, reniec_service):
        """Test verificación de DNI inválido"""
        with patch.object(reniec_service, 'consultar_dni_api', return_value=None):
            result = reniec_service.verificar_dni("99999999")
            
            assert result["valido"] is False
    
    def test_obtener_estadisticas_success(self, reniec_service):
        """Test obtención exitosa de estadísticas"""
        mock_stats = {
            "consultas_realizadas": 100,
            "consultas_exitosas": 95,
            "consultas_fallidas": 5
        }
        
        with patch.object(reniec_service, 'obtener_estadisticas_api', return_value=mock_stats):
            result = reniec_service.obtener_estadisticas()
            
            assert result is not None
            assert "consultas_realizadas" in result
            assert result["consultas_realizadas"] == 100


class TestDocumentoService:
    """Pruebas para DocumentoService"""
    
    @pytest.fixture
    def mock_db(self):
        """Mock de base de datos"""
        return Mock(spec=Session)
    
    @pytest.fixture
    def documento_service(self):
        """Instancia del servicio"""
        return DocumentoService()
    
    def test_crear_documento_success(self, mock_db, documento_service):
        """Test creación exitosa de documento"""
        # Mock de datos
        mock_tipo_doc = Mock(id=1, nombre="DNI")
        mock_ciudadano = Mock(id=1, documento_identidad="12345678")
        mock_documento = Mock(
            id=1,
            numero_documento="12345678",
            estado="vigente"
        )
        
        mock_db.query.return_value.filter.return_value.first.side_effect = [
            mock_ciudadano,  # Para el ciudadano
            mock_tipo_doc,   # Para el tipo de documento
            None            # Para verificar que no existe el documento
        ]
        
        mock_db.add = Mock()
        mock_db.commit = Mock()
        mock_db.refresh = Mock()
        
        with patch('app.services.documento_service.Documento', return_value=mock_documento):
            result = documento_service.crear(
                mock_db,
                numero_documento="12345678",
                ciudadano_id=1,
                tipo_documento_id=1,
                fecha_emision=date(2020, 1, 1)
            )
            
            assert result is not None
            assert result.id == 1
            mock_db.add.assert_called_once()
            mock_db.commit.assert_called_once()
    
    def test_crear_documento_ciudadano_not_found(self, mock_db, documento_service):
        """Test creación de documento con ciudadano inexistente"""
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        result = documento_service.crear(
            mock_db,
            numero_documento="12345678",
            ciudadano_id=999,
            tipo_documento_id=1,
            fecha_emision=date(2020, 1, 1)
        )
        
        assert result is None
    
    def test_buscar_documento_success(self, mock_db, documento_service):
        """Test búsqueda exitosa de documento"""
        mock_documento = Mock(
            id=1,
            numero_documento="12345678",
            estado="vigente"
        )
        
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = mock_documento
        mock_db.query.return_value = mock_query
        
        result = documento_service.buscar_documento(mock_db, "12345678")
        
        assert result is not None
        assert result.numero_documento == "12345678"
    
    def test_buscar_documento_not_found(self, mock_db, documento_service):
        """Test búsqueda de documento inexistente"""
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = None
        mock_db.query.return_value = mock_query
        
        result = documento_service.buscar_documento(mock_db, "99999999")
        
        assert result is None
    
    def test_listar_documentos_success(self, mock_db, documento_service):
        """Test listado exitoso de documentos"""
        mock_documentos = [
            Mock(id=1, numero_documento="12345678", estado="vigente"),
            Mock(id=2, numero_documento="87654321", estado="vencido")
        ]
        
        mock_query = Mock()
        mock_query.offset.return_value.limit.return_value.all.return_value = mock_documentos
        mock_db.query.return_value = mock_query
        
        result = documento_service.listar(mock_db, skip=0, limit=10)
        
        assert len(result) == 2
        assert result[0].id == 1
        assert result[1].id == 2
    
    def test_actualizar_estado_documento_success(self, mock_db, documento_service):
        """Test actualización exitosa de estado de documento"""
        mock_documento = Mock(
            id=1,
            numero_documento="12345678",
            estado="vigente"
        )
        
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = mock_documento
        mock_db.query.return_value = mock_query
        
        mock_db.commit = Mock()
        mock_db.refresh = Mock()
        
        result = documento_service.actualizar_estado(mock_db, 1, "vencido")
        
        assert result is not None
        assert mock_documento.estado == "vencido"
        mock_db.commit.assert_called_once()


class TestServiceErrorHandling:
    """Pruebas para manejo de errores en servicios"""
    
    @pytest.fixture
    def mock_db(self):
        """Mock de base de datos con error"""
        mock_db = Mock(spec=Session)
        mock_db.commit.side_effect = Exception("Database error")
        return mock_db
    
    @pytest.fixture
    def ciudadano_service(self):
        """Instancia del servicio"""
        return CiudadanoService()
    
    def test_crear_ciudadano_database_error(self, mock_db, ciudadano_service):
        """Test manejo de error de base de datos al crear ciudadano"""
        ciudadano_data = CiudadanoCreate(
            documento_identidad="12345678",
            nombres="Juan",
            apellidos="Pérez",
            fecha_nacimiento=date(1990, 1, 15),
            lugar_nacimiento="Lima",
            genero="M",
            estado_civil="soltero",
            direccion="Av. Principal 123",
            telefono="987654321",
            email="test@example.com"
        )
        
        with pytest.raises(Exception):
            with patch('app.services.ciudadano_service.Ciudadano'):
                ciudadano_service.crear(mock_db, ciudadano_data)
    
    def test_obtener_por_id_error(self):
        """Test manejo de error al obtener ciudadano"""
        mock_db = Mock(spec=Session))
        mock_db.query.side_effect = Exception("Database error")
        
        ciudadano_service = CiudadanoService()
        
        result = ciudadano_service.obtener_por_id(mock_db, 1)
        
        assert result is None


class TestServiceBusinessLogic:
    """Pruebas para lógica de negocio en servicios"""
    
    def test_buscar_ciudadanos_with_multiple_criteria(self):
        """Test búsqueda de ciudadanos con múltiples criterios"""
        mock_db = Mock(spec=Session)
        ciudadano_service = CiudadanoService()
        
        criterio = BusquedaCiudadano(
            nombres="Juan",
            apellidos="Pérez",
            email="juan@example.com"
        )
        
        # Mock query chain
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.filter.return_value.filter.return_value = mock_query
        mock_query.filter.return_value.filter.return_value.filter.return_value.all.return_value = []
        
        mock_db.query.return_value = mock_query
        
        result = ciudadano_service.buscar(mock_db, criterio)
        
        assert len(result) == 0
        # Verificar que se llamaron los filtros correctos
        assert mock_db.query.called
    
    def test_estadisticas_ciudadanos_empty_database(self):
        """Test estadísticas con base de datos vacía"""
        mock_db = Mock(spec=Session)
        ciudadano_service = CiudadanoService()
        
        mock_query = Mock()
        mock_query.filter.return_value.count.return_value = 0
        mock_db.query.return_value = mock_query
        
        result = ciudadano_service.obtener_estadisticas(mock_db)
        
        assert result["total_activos"] == 0
        assert result["total_inactivos"] == 0
        assert result["total_general"] == 0


if __name__ == "__main__":
    # Ejecutar tests manualmente
    pytest.main([__file__, "-v"])
