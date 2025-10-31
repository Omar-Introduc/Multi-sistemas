"""
Pruebas para modelos SQLAlchemy del servicio RENIEC
"""

import pytest
from datetime import datetime, date
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Date, Boolean, ForeignKey
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import IntegrityError

# Importar modelos
from app.models.base import BaseModel
from app.models.ciudadano import Ciudadano, CiudadanoModel
from app.models.reniec_models import (
    Ciudadano as ReniecCiudadano,
    TipoDocumento,
    Documento,
    Solicitud,
    EventoSolicitud,
    SesionUsuario
)
from app.config.database import Base


class TestBaseModel:
    """Pruebas para el modelo base"""
    
    def test_base_model_creation(self):
        """Test creación de BaseModel"""
        class TestModel(BaseModel):
            __tablename__ = "test_model"
            
            name = Column(String(50), nullable=False)
        
        assert TestModel.__abstract__ == True
        assert hasattr(TestModel, 'id')
        assert hasattr(TestModel, 'fecha_registro')
        assert hasattr(TestModel, 'fecha_actualizacion')
    
    def test_base_model_fields(self):
        """Test campos del BaseModel"""
        # Los campos ya están definidos en BaseModel
        assert hasattr(BaseModel, 'id')
        assert hasattr(BaseModel, 'fecha_registro')
        assert hasattr(BaseModel, 'fecha_actualizacion')


class TestCiudadanoModel:
    """Pruebas para el modelo de ciudadano"""
    
    def test_ciudadano_model_creation(self):
        """Test creación de modelo Ciudadano"""
        # Test modelo Pydantic
        ciudadano_data = CiudadanoModel(
            dni="12345678",
            nombres="Juan Carlos",
            apellidos="Pérez García",
            fecha_nacimiento=date(1990, 1, 15),
            estado_civil="soltero",
            direccion="Av. Las Flores 123, Lima",
            telefono="987654321",
            email="juan.perez@example.com"
        )
        
        assert ciudadano_data.dni == "12345678"
        assert ciudadano_data.nombres == "Juan Carlos"
        assert ciudadano_data.apellidos == "Pérez García"
        assert ciudadano_data.email == "juan.perez@example.com"
        assert ciudadano_data.estado == True
    
    def test_ciudadano_model_validation_dni_no_numeric(self):
        """Test validación de DNI no numérico"""
        with pytest.raises(ValueError, match="El DNI debe contener solo números"):
            CiudadanoModel(
                dni="12345abc",
                nombres="Juan",
                apellidos="Pérez",
                fecha_nacimiento=date(1990, 1, 15),
                estado_civil="soltero",
                direccion="Av. Principal 123",
                telefono="987654321",
                email="test@example.com"
            )
    
    def test_ciudadano_model_validation_telefono_no_numeric(self):
        """Test validación de teléfono no numérico"""
        with pytest.raises(ValueError, match="El teléfono debe contener solo números"):
            CiudadanoModel(
                dni="12345678",
                nombres="Juan",
                apellidos="Pérez",
                fecha_nacimiento=date(1990, 1, 15),
                estado_civil="soltero",
                direccion="Av. Principal 123",
                telefono="987abc654",
                email="test@example.com"
            )
    
    def test_ciudadano_model_validation_fecha_nacimiento_future(self):
        """Test validación de fecha de nacimiento futura"""
        future_date = date.today()
        
        with pytest.raises(ValueError, match="La fecha de nacimiento debe ser en el pasado"):
            CiudadanoModel(
                dni="12345678",
                nombres="Juan",
                apellidos="Pérez",
                fecha_nacimiento=future_date,
                estado_civil="soltero",
                direccion="Av. Principal 123",
                telefono="987654321",
                email="test@example.com"
            )


class TestCiudadanoSQLAlchemy:
    """Pruebas para el modelo SQLAlchemy Ciudadano"""
    
    @pytest.fixture
    def test_db(self):
        """Fixture para base de datos de prueba"""
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(bind=engine)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        yield db
        db.close()
    
    def test_ciudadano_creation(self, test_db):
        """Test creación de ciudadano en BD"""
        ciudadano = Ciudadano(
            dni="12345678",
            nombres="Juan Carlos",
            apellidos="Pérez García",
            fecha_nacimiento=date(1990, 1, 15),
            estado_civil="soltero",
            direccion="Av. Las Flores 123, Lima",
            telefono="987654321",
            email="juan.perez@example.com"
        )
        
        test_db.add(ciudadano)
        test_db.commit()
        test_db.refresh(ciudadano)
        
        assert ciudadano.id is not None
        assert ciudadano.dni == "12345678"
        assert ciudadano.nombres == "Juan Carlos"
        assert ciudadano.estado == True
        assert ciudadano.fecha_registro is not None
        assert ciudadano.fecha_actualizacion is not None
    
    def test_ciudadano_repr(self, test_db):
        """Test representación string del ciudadano"""
        ciudadano = Ciudadano(
            dni="12345678",
            nombres="Juan",
            apellidos="Pérez",
            fecha_nacimiento=date(1990, 1, 15),
            estado_civil="soltero",
            direccion="Av. Principal 123",
            telefono="987654321",
            email="test@example.com"
        )
        
        test_db.add(ciudadano)
        test_db.commit()
        
        repr_str = repr(ciudadano)
        assert "12345678" in repr_str
        assert "Juan" in repr_str
        assert "Pérez" in repr_str
    
    def test_ciudadano_to_dict(self, test_db):
        """Test conversión a diccionario"""
        ciudadano = Ciudadano(
            dni="12345678",
            nombres="Juan",
            apellidos="Pérez",
            fecha_nacimiento=date(1990, 1, 15),
            estado_civil="soltero",
            direccion="Av. Principal 123",
            telefono="987654321",
            email="test@example.com"
        )
        
        test_db.add(ciudadano)
        test_db.commit()
        
        ciudadano_dict = ciudadano.to_dict()
        
        assert isinstance(ciudadano_dict, dict)
        assert "dni" in ciudadano_dict
        assert "nombres" in ciudadano_dict
        assert "apellidos" in ciudadano_dict
        assert "email" in ciudadano_dict
        assert "fecha_nacimiento" in ciudadano_dict
        
        assert ciudadano_dict["dni"] == "12345678"
        assert ciudadano_dict["nombres"] == "Juan"
        assert ciudadano_dict["email"] == "test@example.com"
    
    def test_ciudadano_unique_dni(self, test_db):
        """Test restricción de DNI único"""
        ciudadano1 = Ciudadano(
            dni="12345678",
            nombres="Juan",
            apellidos="Pérez",
            fecha_nacimiento=date(1990, 1, 15),
            estado_civil="soltero",
            direccion="Av. Principal 123",
            telefono="987654321",
            email="juan@example.com"
        )
        
        ciudadano2 = Ciudadano(
            dni="12345678",  # Mismo DNI
            nombres="Pedro",
            apellidos="González",
            fecha_nacimiento=date(1985, 5, 10),
            estado_civil="casado",
            direccion="Calle 456",
            telefono="987123456",
            email="pedro@example.com"
        )
        
        test_db.add(ciudadano1)
        test_db.commit()
        
        test_db.add(ciudadano2)
        with pytest.raises(IntegrityError):
            test_db.commit()
    
    def test_ciudadano_unique_email(self, test_db):
        """Test restricción de email único"""
        ciudadano1 = Ciudadano(
            dni="12345678",
            nombres="Juan",
            apellidos="Pérez",
            fecha_nacimiento=date(1990, 1, 15),
            estado_civil="soltero",
            direccion="Av. Principal 123",
            telefono="987654321",
            email="test@example.com"
        )
        
        ciudadano2 = Ciudadano(
            dni="87654321",
            nombres="Pedro",
            apellidos="González",
            fecha_nacimiento=date(1985, 5, 10),
            estado_civil="casado",
            direccion="Calle 456",
            telefono="987123456",
            email="test@example.com"  # Mismo email
        )
        
        test_db.add(ciudadano1)
        test_db.commit()
        
        test_db.add(ciudadano2)
        with pytest.raises(IntegrityError):
            test_db.commit()


class TestReniecModels:
    """Pruebas para modelos RENIEC"""
    
    @pytest.fixture
    def test_db(self):
        """Fixture para base de datos de prueba"""
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(bind=engine)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        yield db
        db.close()
    
    def test_tipo_documento_creation(self, test_db):
        """Test creación de tipo de documento"""
        tipo_doc = TipoDocumento(
            codigo="DNI",
            nombre="Documento Nacional de Identidad",
            descripcion="Documento de identidad principal",
            requiere_renovacion=False
        )
        
        test_db.add(tipo_doc)
        test_db.commit()
        test_db.refresh(tipo_doc)
        
        assert tipo_doc.id is not None
        assert tipo_doc.codigo == "DNI"
        assert tipo_doc.nombre == "Documento Nacional de Identidad"
        assert tipo_doc.activo == True
        assert tipo_doc.fecha_creacion is not None
    
    def test_documento_creation(self, test_db):
        """Test creación de documento"""
        # Crear ciudadano primero
        ciudadano = ReniecCiudadano(
            documento_identidad="12345678",
            nombres="Juan",
            apellidos="Pérez",
            fecha_nacimiento=date(1990, 1, 15),
            lugar_nacimiento="Lima",
            genero="M",
            direccion="Av. Principal 123",
            telefono="987654321",
            email="test@example.com"
        )
        test_db.add(ciudadano)
        test_db.commit()
        
        # Crear tipo de documento
        tipo_doc = TipoDocumento(
            codigo="DNI",
            nombre="Documento Nacional de Identidad"
        )
        test_db.add(tipo_doc)
        test_db.commit()
        
        # Crear documento
        documento = Documento(
            numero_documento="12345678",
            ciudadano_id=ciudadano.id,
            tipo_documento_id=tipo_doc.id,
            fecha_emision=date(2020, 1, 1),
            fecha_vencimiento=date(2030, 1, 1),
            estado="vigente"
        )
        test_db.add(documento)
        test_db.commit()
        test_db.refresh(documento)
        
        assert documento.id is not None
        assert documento.numero_documento == "12345678"
        assert documento.estado == "vigente"
        assert documento.fecha_creacion is not None
    
    def test_solicitud_creation(self, test_db):
        """Test creación de solicitud"""
        # Crear ciudadano primero
        ciudadano = ReniecCiudadano(
            documento_identidad="12345678",
            nombres="Juan",
            apellidos="Pérez",
            fecha_nacimiento=date(1990, 1, 15),
            lugar_nacimiento="Lima",
            genero="M",
            direccion="Av. Principal 123",
            telefono="987654321",
            email="test@example.com"
        )
        test_db.add(ciudadano)
        test_db.commit()
        
        # Crear solicitud
        solicitud = Solicitud(
            numero_solicitud="SOL-001",
            ciudadano_id=ciudadano.id,
            tipo_solicitud="primera_vez",
            motivo="Solicitud inicial",
            estado="pendiente"
        )
        test_db.add(solicitud)
        test_db.commit()
        test_db.refresh(solicitud)
        
        assert solicitud.id is not None
        assert solicitud.numero_solicitud == "SOL-001"
        assert solicitud.tipo_solicitud == "primera_vez"
        assert solicitud.estado == "pendiente"
        assert solicitud.fecha_solicitud is not None
    
    def test_evento_solicitud_creation(self, test_db):
        """Test creación de evento de solicitud"""
        # Crear estructura completa
        ciudadano = ReniecCiudadano(
            documento_identidad="12345678",
            nombres="Juan",
            apellidos="Pérez",
            fecha_nacimiento=date(1990, 1, 15),
            lugar_nacimiento="Lima",
            genero="M",
            direccion="Av. Principal 123",
            telefono="987654321",
            email="test@example.com"
        )
        test_db.add(ciudadano)
        test_db.commit()
        
        solicitud = Solicitud(
            numero_solicitud="SOL-001",
            ciudadano_id=ciudadano.id,
            tipo_solicitud="primera_vez",
            estado="pendiente"
        )
        test_db.add(solicitud)
        test_db.commit()
        
        # Crear evento
        evento = EventoSolicitud(
            solicitud_id=solicitud.id,
            evento="solicitud_creada",
            descripcion="Solicitud inicial creada",
            usuario="admin"
        )
        test_db.add(evento)
        test_db.commit()
        test_db.refresh(evento)
        
        assert evento.id is not None
        assert evento.evento == "solicitud_creada"
        assert evento.usuario == "admin"
        assert evento.fecha_evento is not None
    
    def test_sesion_usuario_creation(self, test_db):
        """Test creación de sesión de usuario"""
        import uuid
        
        token = str(uuid.uuid4())
        sesion = SesionUsuario(
            usuario_id=1,
            token_sesion=token,
            fecha_expiracion=datetime(2025, 12, 31),
            ip_address="127.0.0.1",
            user_agent="Mozilla/5.0"
        )
        
        test_db.add(sesion)
        test_db.commit()
        test_db.refresh(sesion)
        
        assert sesion.id is not None
        assert sesion.token_sesion == token
        assert sesion.usuario_id == 1
        assert sesion.activo == True
        assert sesion.fecha_creacion is not None


class TestModelRelationships:
    """Pruebas para relaciones entre modelos"""
    
    @pytest.fixture
    def test_db(self):
        """Fixture para base de datos de prueba"""
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(bind=engine)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        yield db
        db.close()
    
    def test_ciudadano_documentos_relationship(self, test_db):
        """Test relación ciudadano-documentos"""
        # Crear ciudadano
        ciudadano = ReniecCiudadano(
            documento_identidad="12345678",
            nombres="Juan",
            apellidos="Pérez",
            fecha_nacimiento=date(1990, 1, 15),
            lugar_nacimiento="Lima",
            genero="M",
            direccion="Av. Principal 123",
            telefono="987654321",
            email="test@example.com"
        )
        test_db.add(ciudadano)
        test_db.commit()
        
        # Crear tipo de documento
        tipo_doc = TipoDocumento(
            codigo="DNI",
            nombre="Documento Nacional de Identidad"
        )
        test_db.add(tipo_doc)
        test_db.commit()
        
        # Crear documento
        documento = Documento(
            numero_documento="12345678",
            ciudadano_id=ciudadano.id,
            tipo_documento_id=tipo_doc.id,
            fecha_emision=date(2020, 1, 1),
            estado="vigente"
        )
        test_db.add(documento)
        test_db.commit()
        
        # Verificar relación
        test_db.refresh(ciudadano)
        assert len(ciudadano.documentos) == 1
        assert ciudadano.documentos[0].numero_documento == "12345678"
    
    def test_solicitud_ciudadano_relationship(self, test_db):
        """Test relación solicitud-ciudadano"""
        # Crear ciudadano
        ciudadano = ReniecCiudadano(
            documento_identidad="12345678",
            nombres="Juan",
            apellidos="Pérez",
            fecha_nacimiento=date(1990, 1, 15),
            lugar_nacimiento="Lima",
            genero="M",
            direccion="Av. Principal 123",
            telefono="987654321",
            email="test@example.com"
        )
        test_db.add(ciudadano)
        test_db.commit()
        
        # Crear solicitud
        solicitud = Solicitud(
            numero_solicitud="SOL-001",
            ciudadano_id=ciudadano.id,
            tipo_solicitud="primera_vez",
            estado="pendiente"
        )
        test_db.add(solicitud)
        test_db.commit()
        
        # Verificar relación
        test_db.refresh(ciudadano)
        assert len(ciudadano.solicitudes) == 1
        assert ciudadano.solicitudes[0].numero_solicitud == "SOL-001"


if __name__ == "__main__":
    # Ejecutar tests manualmente
    pytest.main([__file__, "-v"])
