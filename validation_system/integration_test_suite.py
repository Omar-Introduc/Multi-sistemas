#!/usr/bin/env python3
"""
Suite de Pruebas de Integración - Sistema Distribuido Bancario
Prueba la comunicación entre LP1, LP2 y LP3
"""

import asyncio
import aiohttp
import json
import time
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import traceback

@dataclass
class TestResult:
    """Resultado de una prueba individual"""
    test_name: str
    status: str  # 'PASS', 'FAIL', 'SKIP'
    duration: float
    message: str
    details: Optional[Dict] = None
    timestamp: str = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()

class IntegrationTestSuite:
    """Suite de pruebas de integración entre servicios"""
    
    def __init__(self, config: Dict[str, str]):
        """
        Inicializar suite de pruebas
        
        Args:
            config: Diccionario con URLs de servicios
                - lp1_url: URL del servicio LP1 (Banco)
                - lp2_url: URL del servicio LP2 (RENIEC)
                - lp3_url: URL del servicio LP3 (Cliente)
        """
        self.config = config
        self.results: List[TestResult] = []
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Configurar logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('/workspace/validation_system/logs/integration_tests.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    async def __aenter__(self):
        """Enter async context"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            connector=aiohttp.TCPConnector(limit=100)
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit async context"""
        if self.session:
            await self.session.close()

    async def _make_request(self, method: str, url: str, data: Dict = None, 
                          service_name: str = "") -> Dict[str, Any]:
        """
        Realizar request HTTP con manejo de errores
        
        Args:
            method: Método HTTP (GET, POST, PUT, DELETE)
            url: URL del endpoint
            data: Datos a enviar (opcional)
            service_name: Nombre del servicio para logging
            
        Returns:
            Dict con resultado de la petición
        """
        try:
            async with self.session.request(method, url, json=data) as response:
                response_data = await response.json()
                status = "OK" if response.status < 400 else "ERROR"
                
                self.logger.info(f"{service_name} - {method} {url} - Status: {response.status}")
                
                return {
                    "status": status,
                    "status_code": response.status,
                    "data": response_data,
                    "response_time": 0  # Se calculará externamente
                }
        except Exception as e:
            self.logger.error(f"{service_name} - Error en request: {str(e)}")
            return {
                "status": "ERROR",
                "status_code": 0,
                "error": str(e),
                "data": None
            }

    async def test_lp1_health(self) -> TestResult:
        """Probar salud del servicio LP1 (Banco)"""
        start_time = time.time()
        test_name = "LP1 Health Check"
        
        try:
            result = await self._make_request(
                "GET", 
                f"{self.config['lp1_url']}/api/health", 
                service_name="LP1"
            )
            
            duration = time.time() - start_time
            
            if result["status"] == "OK":
                return TestResult(
                    test_name=test_name,
                    status="PASS",
                    duration=duration,
                    message="LP1 está funcionando correctamente",
                    details=result
                )
            else:
                return TestResult(
                    test_name=test_name,
                    status="FAIL",
                    duration=duration,
                    message=f"LP1 responded with error: {result.get('error', 'Unknown')}",
                    details=result
                )
                
        except Exception as e:
            duration = time.time() - start_time
            return TestResult(
                test_name=test_name,
                status="FAIL",
                duration=duration,
                message=f"Error al conectar con LP1: {str(e)}",
                details={"error": str(e), "traceback": traceback.format_exc()}
            )

    async def test_lp2_health(self) -> TestResult:
        """Probar salud del servicio LP2 (RENIEC)"""
        start_time = time.time()
        test_name = "LP2 Health Check"
        
        try:
            result = await self._make_request(
                "GET", 
                f"{self.config['lp2_url']}/api/health", 
                service_name="LP2"
            )
            
            duration = time.time() - start_time
            
            if result["status"] == "OK":
                return TestResult(
                    test_name=test_name,
                    status="PASS",
                    duration=duration,
                    message="LP2 está funcionando correctamente",
                    details=result
                )
            else:
                return TestResult(
                    test_name=test_name,
                    status="FAIL",
                    duration=duration,
                    message=f"LP2 responded with error: {result.get('error', 'Unknown')}",
                    details=result
                )
                
        except Exception as e:
            duration = time.time() - start_time
            return TestResult(
                test_name=test_name,
                status="FAIL",
                duration=duration,
                message=f"Error al conectar con LP2: {str(e)}",
                details={"error": str(e), "traceback": traceback.format_exc()}
            )

    async def test_lp3_health(self) -> TestResult:
        """Probar salud del servicio LP3 (Cliente)"""
        start_time = time.time()
        test_name = "LP3 Health Check"
        
        try:
            result = await self._make_request(
                "GET", 
                f"{self.config['lp3_url']}/api/health", 
                service_name="LP3"
            )
            
            duration = time.time() - start_time
            
            if result["status"] == "OK":
                return TestResult(
                    test_name=test_name,
                    status="PASS",
                    duration=duration,
                    message="LP3 está funcionando correctamente",
                    details=result
                )
            else:
                return TestResult(
                    test_name=test_name,
                    status="FAIL",
                    duration=duration,
                    message=f"LP3 responded with error: {result.get('error', 'Unknown')}",
                    details=result
                )
                
        except Exception as e:
            duration = time.time() - start_time
            return TestResult(
                test_name=test_name,
                status="FAIL",
                duration=duration,
                message=f"Error al conectar con LP3: {str(e)}",
                details={"error": str(e), "traceback": traceback.format_exc()}
            )

    async def test_customer_validation_flow(self) -> TestResult:
        """
        Probar flujo completo de validación de cliente:
        LP3 -> LP2 (validación RENIEC) -> LP1 (validación bancaria)
        """
        start_time = time.time()
        test_name = "Customer Validation Flow"
        
        # Datos de prueba
        test_data = {
            "dni": "12345678",
            "nombres": "Juan",
            "apellidos": "Pérez García",
            "fecha_nacimiento": "1990-01-01"
        }
        
        try:
            # Paso 1: LP3 solicita validación
            self.logger.info("Paso 1: LP3 solicita validación de cliente")
            step1_result = await self._make_request(
                "POST",
                f"{self.config['lp3_url']}/api/validate-customer",
                data=test_data,
                service_name="LP3"
            )
            
            if step1_result["status"] != "OK":
                return TestResult(
                    test_name=test_name,
                    status="FAIL",
                    duration=time.time() - start_time,
                    message="LP3 rechazó la solicitud de validación",
                    details={"step1": step1_result}
                )
            
            # Paso 2: Validar con LP2 (RENIEC)
            self.logger.info("Paso 2: Validación con LP2 (RENIEC)")
            step2_result = await self._make_request(
                "POST",
                f"{self.config['lp2_url']}/api/reniec/validate",
                data={"dni": test_data["dni"]},
                service_name="LP2"
            )
            
            if step2_result["status"] != "OK":
                return TestResult(
                    test_name=test_name,
                    status="FAIL",
                    duration=time.time() - start_time,
                    message="LP2 no pudo validar el DNI",
                    details={"step1": step1_result, "step2": step2_result}
                )
            
            # Paso 3: Validar con LP1 (Banco)
            self.logger.info("Paso 3: Validación con LP1 (Banco)")
            step3_result = await self._make_request(
                "POST",
                f"{self.config['lp1_url']}/api/banco/validate-customer",
                data=test_data,
                service_name="LP1"
            )
            
            if step3_result["status"] != "OK":
                return TestResult(
                    test_name=test_name,
                    status="FAIL",
                    duration=time.time() - start_time,
                    message="LP1 no pudo validar el cliente",
                    details={
                        "step1": step1_result,
                        "step2": step2_result,
                        "step3": step3_result
                    }
                )
            
            duration = time.time() - start_time
            
            return TestResult(
                test_name=test_name,
                status="PASS",
                duration=duration,
                message="Flujo de validación completado exitosamente",
                details={
                    "step1": step1_result,
                    "step2": step2_result,
                    "step3": step3_result,
                    "total_flow_time": duration
                }
            )
            
        except Exception as e:
            duration = time.time() - start_time
            return TestResult(
                test_name=test_name,
                status="FAIL",
                duration=duration,
                message=f"Error en flujo de validación: {str(e)}",
                details={
                    "error": str(e),
                    "traceback": traceback.format_exc()
                }
            )

    async def test_rabbitmq_integration(self) -> TestResult:
        """Probar integración con RabbitMQ"""
        start_time = time.time()
        test_name = "RabbitMQ Integration"
        
        try:
            # Probar publicar mensaje
            message_data = {
                "type": "validation_request",
                "data": {"dni": "12345678"},
                "timestamp": datetime.now().isoformat()
            }
            
            publish_result = await self._make_request(
                "POST",
                f"{self.config['lp2_url']}/api/rabbitmq/publish",
                data=message_data,
                service_name="RabbitMQ"
            )
            
            if publish_result["status"] != "OK":
                return TestResult(
                    test_name=test_name,
                    status="FAIL",
                    duration=time.time() - start_time,
                    message="No se pudo publicar mensaje en RabbitMQ",
                    details=publish_result
                )
            
            # Probar consumir mensaje
            consume_result = await self._make_request(
                "GET",
                f"{self.config['lp2_url']}/api/rabbitmq/consume",
                service_name="RabbitMQ"
            )
            
            duration = time.time() - start_time
            
            if consume_result["status"] == "OK":
                return TestResult(
                    test_name=test_name,
                    status="PASS",
                    duration=duration,
                    message="RabbitMQ funcionando correctamente",
                    details={
                        "publish": publish_result,
                        "consume": consume_result
                    }
                )
            else:
                return TestResult(
                    test_name=test_name,
                    status="FAIL",
                    duration=duration,
                    message="Problema al consumir mensaje de RabbitMQ",
                    details={
                        "publish": publish_result,
                        "consume": consume_result
                    }
                )
                
        except Exception as e:
            duration = time.time() - start_time
            return TestResult(
                test_name=test_name,
                status="FAIL",
                duration=duration,
                message=f"Error en integración RabbitMQ: {str(e)}",
                details={"error": str(e)}
            )

    async def test_database_connectivity(self) -> TestResult:
        """Probar conectividad con bases de datos heterogéneas"""
        start_time = time.time()
        test_name = "Database Connectivity"
        
        results = {}
        
        # Probar MySQL
        try:
            mysql_result = await self._make_request(
                "GET",
                f"{self.config['lp1_url']}/api/database/mysql/health",
                service_name="MySQL"
            )
            results["mysql"] = mysql_result
        except Exception as e:
            results["mysql"] = {"status": "ERROR", "error": str(e)}
        
        # Probar PostgreSQL
        try:
            postgres_result = await self._make_request(
                "GET",
                f"{self.config['lp2_url']}/api/database/postgres/health",
                service_name="PostgreSQL"
            )
            results["postgres"] = postgres_result
        except Exception as e:
            results["postgres"] = {"status": "ERROR", "error": str(e)}
        
        # Probar Redis
        try:
            redis_result = await self._make_request(
                "GET",
                f"{self.config['lp2_url']}/api/database/redis/health",
                service_name="Redis"
            )
            results["redis"] = redis_result
        except Exception as e:
            results["redis"] = {"status": "ERROR", "error": str(e)}
        
        duration = time.time() - start_time
        
        # Verificar que todas las BDs estén disponibles
        all_ok = all(
            db.get("status") == "OK" 
            for db in results.values()
        )
        
        if all_ok:
            return TestResult(
                test_name=test_name,
                status="PASS",
                duration=duration,
                message="Todas las bases de datos están disponibles",
                details=results
            )
        else:
            return TestResult(
                test_name=test_name,
                status="FAIL",
                duration=duration,
                message="Algunas bases de datos no están disponibles",
                details=results
            )

    async def test_concurrent_requests(self) -> TestResult:
        """Probar manejo de peticiones concurrentes"""
        start_time = time.time()
        test_name = "Concurrent Requests"
        
        try:
            # Crear múltiples peticiones concurrentes
            tasks = []
            for i in range(10):
                task = self._make_request(
                    "GET",
                    f"{self.config['lp1_url']}/api/health",
                    service_name=f"Concurrent-{i}"
                )
                tasks.append(task)
            
            # Ejecutar todas las peticiones concurrentemente
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            duration = time.time() - start_time
            
            # Analizar resultados
            successful = sum(1 for r in results if isinstance(r, dict) and r.get("status") == "OK")
            failed = len(results) - successful
            
            if successful == len(results):
                return TestResult(
                    test_name=test_name,
                    status="PASS",
                    duration=duration,
                    message=f"Manejo concurrente exitoso: {successful}/{len(results)} requests",
                    details={
                        "total_requests": len(results),
                        "successful": successful,
                        "failed": failed,
                        "avg_response_time": duration / len(results)
                    }
                )
            else:
                return TestResult(
                    test_name=test_name,
                    status="FAIL",
                    duration=duration,
                    message=f"Manejo concurrente fallido: {successful}/{len(results)} requests",
                    details={
                        "total_requests": len(results),
                        "successful": successful,
                        "failed": failed,
                        "results": results
                    }
                )
                
        except Exception as e:
            duration = time.time() - start_time
            return TestResult(
                test_name=test_name,
                status="FAIL",
                duration=duration,
                message=f"Error en prueba de concurrencia: {str(e)}",
                details={"error": str(e)}
            )

    async def run_all_tests(self) -> List[TestResult]:
        """Ejecutar todas las pruebas de integración"""
        self.logger.info("=== INICIANDO SUITE DE PRUEBAS DE INTEGRACIÓN ===")
        
        tests = [
            self.test_lp1_health,
            self.test_lp2_health,
            self.test_lp3_health,
            self.test_rabbitmq_integration,
            self.test_database_connectivity,
            self.test_concurrent_requests,
            self.test_customer_validation_flow
        ]
        
        for test in tests:
            self.logger.info(f"Ejecutando: {test.__name__}")
            try:
                result = await test()
                self.results.append(result)
                self.logger.info(f"Resultado: {result.status} - {result.message}")
            except Exception as e:
                self.logger.error(f"Error ejecutando {test.__name__}: {str(e)}")
                self.results.append(TestResult(
                    test_name=test.__name__,
                    status="FAIL",
                    duration=0,
                    message=f"Error inesperado: {str(e)}",
                    details={"error": str(e), "traceback": traceback.format_exc()}
                ))
        
        self.logger.info("=== SUITE DE PRUEBAS DE INTEGRACIÓN COMPLETADA ===")
        return self.results

    def get_summary(self) -> Dict[str, Any]:
        """Obtener resumen de resultados"""
        total = len(self.results)
        passed = sum(1 for r in self.results if r.status == "PASS")
        failed = sum(1 for r in self.results if r.status == "FAIL")
        skipped = sum(1 for r in self.results if r.status == "SKIP")
        
        total_duration = sum(r.duration for r in self.results)
        
        return {
            "total_tests": total,
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
            "success_rate": (passed / total * 100) if total > 0 else 0,
            "total_duration": total_duration,
            "results": [asdict(r) for r in self.results]
        }

    def save_results(self, filename: str = None):
        """Guardar resultados en archivo JSON"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"/workspace/validation_system/reports/integration_test_results_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(self.get_summary(), f, indent=2)
        
        self.logger.info(f"Resultados guardados en: {filename}")

async def main():
    """Función principal para testing independiente"""
    config = {
        "lp1_url": "http://localhost:8080",
        "lp2_url": "http://localhost:8000",
        "lp3_url": "http://localhost:3000"
    }
    
    async with IntegrationTestSuite(config) as suite:
        await suite.run_all_tests()
        suite.save_results()
        
        summary = suite.get_summary()
        print("\n=== RESUMEN DE PRUEBAS ===")
        print(f"Total: {summary['total_tests']}")
        print(f"Pasaron: {summary['passed']}")
        print(f"Fallaron: {summary['failed']}")
        print(f"Tasa de éxito: {summary['success_rate']:.2f}%")

if __name__ == "__main__":
    asyncio.run(main())
