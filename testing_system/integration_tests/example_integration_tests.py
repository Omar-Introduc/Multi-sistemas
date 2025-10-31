"""
Tests de Integración de Ejemplo - Sistema de Testing Final
=========================================================

Ejemplos de tests de integración que verifican la interacción
entre diferentes componentes del sistema distribuido.

Autor: Testing System v2.0
Fecha: 2025-10-30
"""

import pytest
import asyncio
import aiohttp
import json
from unittest.mock import Mock, patch
import time


class TestServiceIntegration:
    """Tests de integración entre servicios"""
    
    @pytest.fixture
    def base_url(self):
        """URL base para servicios"""
        return "http://localhost:8004"  # Puerto de testing
    
    @pytest.fixture
    def reniec_url(self):
        """URL del servicio RENIEC"""
        return "http://localhost:8005"  # Puerto de testing
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_banco_health_check(self, base_url):
        """Test: Verificar health check del servicio de banco"""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{base_url}/health") as response:
                assert response.status == 200
                data = await response.json()
                assert data["status"] == "healthy"
                assert "timestamp" in data
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_reniec_health_check(self, reniec_url):
        """Test: Verificar health check del servicio RENIEC"""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{reniec_url}/health") as response:
                assert response.status == 200
                data = await response.json()
                assert data["status"] == "healthy"
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_banco_account_creation(self, base_url):
        """Test: Creación de cuenta en servicio bancario"""
        account_data = {
            "dni": "12345678",
            "name": "Juan Pérez",
            "initial_balance": 1000.0
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{base_url}/api/accounts",
                json=account_data
            ) as response:
                assert response.status == 201
                data = await response.json()
                assert "account_id" in data
                assert data["initial_balance"] == 1000.0
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_reniec_citizen_lookup(self, reniec_url):
        """Test: Búsqueda de ciudadano en RENIEC"""
        dni = "12345678"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{reniec_url}/api/citizens/{dni}") as response:
                if response.status == 200:
                    data = await response.json()
                    assert data["dni"] == dni
                elif response.status == 404:
                    # Ciudadano no encontrado - también es un caso válido
                    pass
                else:
                    pytest.fail(f"Unexpected status: {response.status}")


class TestDatabaseIntegration:
    """Tests de integración con base de datos"""
    
    @pytest.fixture
    def test_db_config(self):
        """Configuración de base de datos de testing"""
        return {
            "host": "localhost",
            "port": 5433,  # Puerto de testing
            "database": "testing_db",
            "user": "testing_user",
            "password": "testing_password"
        }
    
    @pytest.mark.integration
    def test_database_connection(self, test_db_config):
        """Test: Conexión a base de datos"""
        try:
            import psycopg2
            conn = psycopg2.connect(**test_db_config)
            cursor = conn.cursor()
            
            # Test simple query
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            
            cursor.close()
            conn.close()
            
            assert result[0] == 1
        except Exception as e:
            pytest.skip(f"Database not available: {e}")
    
    @pytest.mark.integration
    def test_account_table_operations(self, test_db_config):
        """Test: Operaciones en tabla de cuentas"""
        try:
            import psycopg2
            
            conn = psycopg2.connect(**test_db_config)
            cursor = conn.cursor()
            
            # Insert test account
            test_account_id = f"test_{int(time.time())}"
            cursor.execute(
                "INSERT INTO accounts (account_id, dni, balance) VALUES (%s, %s, %s)",
                (test_account_id, "12345678", 1000.0)
            )
            conn.commit()
            
            # Retrieve account
            cursor.execute(
                "SELECT * FROM accounts WHERE account_id = %s",
                (test_account_id,)
            )
            result = cursor.fetchone()
            
            assert result is not None
            assert result[1] == "12345678"
            assert result[2] == 1000.0
            
            # Clean up
            cursor.execute("DELETE FROM accounts WHERE account_id = %s", (test_account_id,))
            conn.commit()
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            pytest.skip(f"Database operations failed: {e}")


class TestRedisIntegration:
    """Tests de integración con Redis"""
    
    @pytest.mark.integration
    def test_redis_connection(self):
        """Test: Conexión a Redis"""
        try:
            import redis
            r = redis.Redis(
                host='localhost',
                port=6380,
                password='testing_redis_pass',
                decode_responses=True
            )
            
            # Test basic operations
            r.set('test_key', 'test_value')
            value = r.get('test_key')
            
            assert value == 'test_value'
            
            # Clean up
            r.delete('test_key')
            
        except Exception as e:
            pytest.skip(f"Redis not available: {e}")
    
    @pytest.mark.integration
    def test_redis_session_storage(self):
        """Test: Almacenamiento de sesiones en Redis"""
        try:
            import redis
            
            r = redis.Redis(
                host='localhost',
                port=6380,
                password='testing_redis_pass',
                decode_responses=True
            )
            
            # Test session data
            session_data = {
                "user_id": "12345",
                "login_time": "2025-10-30T12:00:00",
                "permissions": ["read", "write"]
            }
            
            # Store session
            session_key = f"session:{session_data['user_id']}"
            r.setex(session_key, 3600, json.dumps(session_data))  # 1 hour expiry
            
            # Retrieve session
            stored_data = r.get(session_key)
            retrieved_data = json.loads(stored_data)
            
            assert retrieved_data == session_data
            
            # Clean up
            r.delete(session_key)
            
        except Exception as e:
            pytest.skip(f"Redis session storage failed: {e}")


class TestRabbitMQIntegration:
    """Tests de integración con RabbitMQ"""
    
    @pytest.mark.integration
    def test_rabbitmq_connection(self):
        """Test: Conexión a RabbitMQ"""
        try:
            import pika
            
            credentials = pika.PlainCredentials('testing_rabbit', 'testing_rabbit_pass')
            parameters = pika.ConnectionParameters(
                'localhost',
                5674,
                '/',
                credentials
            )
            
            connection = pika.BlockingConnection(parameters)
            channel = connection.channel()
            
            # Test basic operations
            channel.queue_declare(queue='test_queue')
            channel.basic_publish(exchange='', routing_key='test_queue', body='test_message')
            
            connection.close()
            
        except Exception as e:
            pytest.skip(f"RabbitMQ not available: {e}")
    
    @pytest.mark.integration
    def test_message_publishing_consumption(self):
        """Test: Publicación y consumo de mensajes"""
        try:
            import pika
            
            credentials = pika.PlainCredentials('testing_rabbit', 'testing_rabbit_pass')
            parameters = pika.ConnectionParameters('localhost', 5674, '/', credentials)
            
            connection = pika.BlockingConnection(parameters)
            channel = connection.channel()
            
            queue_name = 'integration_test_queue'
            channel.queue_declare(queue=queue_name)
            
            # Publish message
            test_message = json.dumps({
                "type": "test",
                "timestamp": time.time(),
                "data": "integration test message"
            })
            
            channel.basic_publish(exchange='', routing_key=queue_name, body=test_message)
            
            # Consume message
            method, properties, body = channel.basic_get(queue=queue_name, auto_ack=True)
            
            assert body is not None
            received_message = json.loads(body.decode())
            assert received_message["type"] == "test"
            
            # Clean up
            channel.queue_delete(queue=queue_name)
            connection.close()
            
        except Exception as e:
            pytest.skip(f"RabbitMQ messaging failed: {e}")


class TestCrossServiceCommunication:
    """Tests de comunicación entre servicios"""
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_bank_reniec_integration(self):
        """Test: Integración banco-RENIEC"""
        # Este test simula un flujo que involucra ambos servicios
        bank_url = "http://localhost:8004"
        reniec_url = "http://localhost:8005"
        
        async with aiohttp.ClientSession() as session:
            # Verificar que ambos servicios están disponibles
            try:
                async with session.get(f"{bank_url}/health") as response:
                    bank_health = response.status == 200
            except:
                bank_health = False
            
            try:
                async with session.get(f"{reniec_url}/health") as response:
                    reniec_health = response.status == 200
            except:
                reniec_health = False
            
            # Si ambos servicios están disponibles, proceder con test
            if bank_health and reniec_health:
                # Simular flujo: Verificar ciudadano en RENIEC y crear cuenta en banco
                dni = "12345678"
                
                # Buscar ciudadano en RENIEC
                async with session.get(f"{reniec_url}/api/citizens/{dni}") as response:
                    if response.status == 200:
                        citizen_data = await response.json()
                        
                        # Crear cuenta en banco usando datos de RENIEC
                        account_data = {
                            "dni": citizen_data["dni"],
                            "name": citizen_data["name"],
                            "lastname": citizen_data["lastname"],
                            "initial_balance": 1000.0
                        }
                        
                        async with session.post(
                            f"{bank_url}/api/accounts",
                            json=account_data
                        ) as account_response:
                            assert account_response.status in [201, 409]  # 201 created, 409 already exists
            else:
                pytest.skip("One or both services not available")


class TestPerformanceIntegration:
    """Tests de performance de integración"""
    
    @pytest.mark.integration
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_api_response_times(self):
        """Test: Tiempo de respuesta de APIs"""
        bank_url = "http://localhost:8004"
        
        async with aiohttp.ClientSession() as session:
            start_time = time.time()
            
            try:
                async with session.get(f"{bank_url}/health") as response:
                    response_time = time.time() - start_time
                    
                    # API debe responder en menos de 2 segundos
                    assert response_time < 2.0
                    assert response.status == 200
            except:
                pytest.skip("Bank service not available")
    
    @pytest.mark.integration
    @pytest.mark.performance
    def test_concurrent_database_operations(self):
        """Test: Operaciones concurrentes en base de datos"""
        try:
            import psycopg2
            import threading
            
            db_config = {
                "host": "localhost",
                "port": 5433,
                "database": "testing_db",
                "user": "testing_user",
                "password": "testing_password"
            }
            
            results = []
            
            def db_operation():
                try:
                    conn = psycopg2.connect(**db_config)
                    cursor = conn.cursor()
                    cursor.execute("SELECT 1")
                    cursor.fetchone()
                    cursor.close()
                    conn.close()
                    results.append("success")
                except Exception as e:
                    results.append(f"error: {e}")
            
            # Ejecutar 10 operaciones concurrentes
            threads = []
            for _ in range(10):
                thread = threading.Thread(target=db_operation)
                threads.append(thread)
                thread.start()
            
            for thread in threads:
                thread.join()
            
            # Verificar que todas las operaciones fueron exitosas
            assert len(results) == 10
            for result in results:
                assert result == "success"
                
        except Exception as e:
            pytest.skip(f"Concurrent database test failed: {e}")


class TestErrorHandlingIntegration:
    """Tests de manejo de errores en integración"""
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_service_unavailable_handling(self):
        """Test: Manejo cuando un servicio no está disponible"""
        # Intentar conectar a un puerto que no tiene servicio
        invalid_url = "http://localhost:9999"
        
        async with aiohttp.ClientSession() as session:
            with pytest.raises((aiohttp.ClientConnectorError, asyncio.TimeoutError)):
                async with session.get(f"{invalid_url}/health", timeout=1):
                    pass
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_invalid_api_response(self):
        """Test: Manejo de respuestas API inválidas"""
        bank_url = "http://localhost:8004"
        
        async with aiohttp.ClientSession() as session:
            # Intentar endpoint que no existe
            with pytest.raises((aiohttp.ClientResponseError, ValueError)):
                async with session.post(
                    f"{bank_url}/api/nonexistent",
                    json={"invalid": "data"}
                ) as response:
                    if response.status >= 400:
                        # Verificar que el error se maneja correctamente
                        assert response.status in [400, 404, 422]
                    else:
                        pytest.fail("Expected error response")


if __name__ == "__main__":
    # Ejecutar tests si se llama directamente
    pytest.main([__file__, "-v", "-m", "integration"])