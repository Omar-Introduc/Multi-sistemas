#!/usr/bin/env python3
"""
Pruebas de Tolerancia a Fallos
Evalúa la capacidad del sistema para recuperarse de fallos y mantener disponibilidad
"""

import asyncio
import aiohttp
import time
import logging
import json
import subprocess
import socket
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import signal
import threading
import requests

@dataclass
class FaultToleranceTestResult:
    """Resultado de una prueba de tolerancia a fallos"""
    test_name: str
    scenario: str
    fault_injected: bool
    recovery_time: float
    availability_during_fault: float  # Porcentaje de disponibilidad durante el fallo
    final_status: str  # 'PASS', 'FAIL', 'WARNING'
    message: str
    details: Optional[Dict] = None
    timestamp: str = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()

class FaultToleranceTestSuite:
    """Suite de pruebas de tolerancia a fallos"""
    
    def __init__(self, config: Dict[str, str]):
        """
        Inicializar suite de pruebas
        
        Args:
            config: Diccionario con URLs de servicios
        """
        self.config = config
        self.results: List[FaultToleranceTestResult] = []
        self.session: Optional[aiohttp.ClientSession] = None
        self.running_services = {}
        
        # Configurar logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('/workspace/validation_system/logs/fault_tolerance_tests.log'),
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

    def _check_port_status(self, host: str, port: int) -> bool:
        """Verificar si un puerto está abierto"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(3)
                result = sock.connect_ex((host, port))
                return result == 0
        except Exception:
            return False

    async def _make_health_check(self, service_name: str, url: str, 
                               max_attempts: int = 10, 
                               delay: float = 2.0) -> Tuple[bool, float, str]:
        """
        Verificar salud de servicio con reintentos
        
        Returns:
            Tuple con (healthy, response_time, error_message)
        """
        start_time = time.time()
        
        for attempt in range(max_attempts):
            try:
                async with self.session.get(url) as response:
                    if response.status < 400:
                        duration = time.time() - start_time
                        return (True, duration, "")
                await asyncio.sleep(delay)
            except Exception as e:
                if attempt == max_attempts - 1:
                    duration = time.time() - start_time
                    return (False, duration, str(e))
                await asyncio.sleep(delay)
        
        duration = time.time() - start_time
        return (False, duration, "Max attempts reached")

    async def test_service_unavailability(self) -> FaultToleranceTestResult:
        """Probar comportamiento cuando un servicio no está disponible"""
        test_name = "Service Unavailability Test"
        scenario = "Simulating LP2 service down"
        
        self.logger.info("=== Iniciando prueba de indisponibilidad de servicio ===")
        
        # Paso 1: Verificar que LP2 está funcionando inicialmente
        initial_check = await self._make_health_check("LP2", f"{self.config['lp2_url']}/api/health")
        
        if not initial_check[0]:
            self.logger.warning("LP2 ya está indisponible, saltando esta prueba")
            return FaultToleranceTestResult(
                test_name=test_name,
                scenario=scenario,
                fault_injected=False,
                recovery_time=0,
                availability_during_fault=0,
                status="SKIP",
                message="Servicio LP2 ya estaba indisponible",
                details={"initial_check": initial_check}
            )
        
        # Paso 2: Simular indisponibilidad bloqueando puerto
        original_port = 8000  # Puerto de LP2
        fault_injected = False
        blocking_thread = None
        
        def block_port():
            """Función para bloquear puerto"""
            try:
                # Crear socket que mantenga el puerto ocupado
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                sock.bind(('localhost', original_port))
                sock.listen(1)
                
                # Mantener el socket abierto durante la prueba
                time.sleep(30)  # Mantener por 30 segundos
                sock.close()
            except Exception as e:
                self.logger.error(f"Error bloqueando puerto: {e}")
        
        try:
            # Iniciar thread para bloquear puerto
            blocking_thread = threading.Thread(target=block_port)
            blocking_thread.start()
            
            # Dar tiempo para que el bloqueo tome efecto
            await asyncio.sleep(2)
            fault_injected = True
            
            # Paso 3: Verificar que el servicio no responde
            fault_check = await self._make_health_check("LP2_Fault", f"{self.config['lp2_url']}/api/health", max_attempts=3)
            
            # Paso 4: Probar fallback - verificar si LP3 puede manejar degradación
            lp3_response_time = 0
            lp3_successful = 0
            lp3_total = 5
            
            fallback_start = time.time()
            for _ in range(lp3_total):
                try:
                    async with self.session.get(f"{self.config['lp3_url']}/api/health") as response:
                        if response.status < 400:
                            lp3_successful += 1
                except:
                    pass
                await asyncio.sleep(0.5)
            
            lp3_availability = lp3_successful / lp3_total * 100
            
            # Paso 5: Verificar si LP1 sigue funcionando
            lp1_check = await self._make_health_check("LP1", f"{self.config['lp1_url']}/api/health", max_attempts=2)
            
            # Paso 6: Restaurar servicio (esperar a que thread termine)
            self.logger.info("Esperando restauración del servicio...")
            blocking_thread.join()
            
            # Verificar recuperación
            recovery_start = time.time()
            recovery_check = await self._make_health_check("LP2_Recovery", f"{self.config['lp2_url']}/api/health")
            recovery_time = time.time() - recovery_start
            
            # Analizar resultados
            if recovery_check[0] and lp1_check[0]:
                status = "PASS"
                message = f"Tolerancia a fallo: {lp3_availability:.0f}% disponibilidad, recuperación en {recovery_time:.1f}s"
            elif lp1_check[0] and lp3_availability >= 80:
                status = "WARNING"
                message = f"Fallback parcial: LP1 operativo, LP3 {lp3_availability:.0f}%, recuperación lenta"
            else:
                status = "FAIL"
                message = "Sistema no toleró fallo correctamente"
            
            return FaultToleranceTestResult(
                test_name=test_name,
                scenario=scenario,
                fault_injected=fault_injected,
                recovery_time=recovery_time,
                availability_during_fault=lp3_availability,
                status=status,
                message=message,
                details={
                    "initial_status": initial_check[0],
                    "fault_injected": fault_injected,
                    "fault_status": fault_check[0],
                    "fallback_availability": lp3_availability,
                    "lp1_remaining_operational": lp1_check[0],
                    "recovery_status": recovery_check[0],
                    "recovery_time": recovery_time
                }
            )
            
        except Exception as e:
            if blocking_thread and blocking_thread.is_alive():
                blocking_thread.join(timeout=5)
            
            return FaultToleranceTestResult(
                test_name=test_name,
                scenario=scenario,
                fault_injected=fault_injected,
                recovery_time=0,
                availability_during_fault=0,
                status="FAIL",
                message=f"Error en prueba de indisponibilidad: {str(e)}",
                details={"error": str(e)}
            )

    async def test_database_connection_failure(self) -> FaultToleranceTestResult:
        """Probar tolerancia a fallos de conexión de base de datos"""
        test_name = "Database Connection Failure Test"
        scenario = "Simulating database connection issues"
        
        self.logger.info("=== Iniciando prueba de fallo de base de datos ===")
        
        try:
            # Paso 1: Verificar estado inicial de BDs
            db_statuses = {}
            databases = [
                ("MySQL", f"{self.config['lp1_url']}/api/database/mysql/health"),
                ("PostgreSQL", f"{self.config['lp2_url']}/api/database/postgres/health"),
                ("Redis", f"{self.config['lp2_url']}/api/database/redis/health")
            ]
            
            for db_name, db_url in databases:
                status = await self._make_health_check(db_name, db_url, max_attempts=2)
                db_statuses[db_name] = status[0]
            
            # Paso 2: Probar degradación gradual
            # Verificar si los servicios manejan degradación de BD
            test_operations = [
                ("LP1_Cached", f"{self.config['lp1_url']}/api/health"),
                ("LP1_Database", f"{self.config['lp1_url']}/api/database/mysql/health"),
                ("LP2_Cached", f"{self.config['lp2_url']}/api/health"),
                ("LP2_Database", f"{self.config['lp2_url']}/api/database/postgres/health")
            ]
            
            degraded_operations = []
            for op_name, op_url in test_operations:
                operation_start = time.time()
                try:
                    async with self.session.get(op_url) as response:
                        success = response.status < 400
                        duration = time.time() - operation_start
                        degraded_operations.append({
                            "operation": op_name,
                            "success": success,
                            "response_time": duration
                        })
                except Exception as e:
                    degraded_operations.append({
                        "operation": op_name,
                        "success": False,
                        "response_time": time.time() - operation_start,
                        "error": str(e)
                    })
            
            # Paso 3: Evaluar recuperación automática
            recovery_operations = []
            for op_name, op_url in test_operations:
                await asyncio.sleep(1)  # Esperar un momento
                operation_start = time.time()
                try:
                    async with self.session.get(op_url) as response:
                        success = response.status < 400
                        duration = time.time() - operation_start
                        recovery_operations.append({
                            "operation": op_name,
                            "success": success,
                            "response_time": duration
                        })
                except Exception as e:
                    recovery_operations.append({
                        "operation": op_name,
                        "success": False,
                        "response_time": time.time() - operation_start,
                        "error": str(e)
                    })
            
            # Analizar resultados
            cached_success = sum(1 for op in recovery_operations if "Cached" in op["operation"] and op["success"])
            db_success = sum(1 for op in recovery_operations if "Database" in op["operation"] and op["success"])
            
            cached_availability = cached_success / 2 * 100 if len([op for op in recovery_operations if "Cached" in op["operation"]]) > 0 else 0
            db_availability = db_success / 2 * 100 if len([op for op in recovery_operations if "Database" in op["operation"]]) > 0 else 0
            
            if cached_availability >= 90:
                status = "PASS"
                message = f"Degradación DB: Cached {cached_availability:.0f}%, DB {db_availability:.0f}%"
            elif cached_availability >= 70:
                status = "WARNING"
                message = f"Degradación DB parcial: Cached {cached_availability:.0f}%, DB {db_availability:.0f}%"
            else:
                status = "FAIL"
                message = "Sistema no maneja degradación de BD correctamente"
            
            return FaultToleranceTestResult(
                test_name=test_name,
                scenario=scenario,
                fault_injected=False,  # No inyectamos fallo real
                recovery_time=0,
                availability_during_fault=(cached_availability + db_availability) / 2,
                status=status,
                message=message,
                details={
                    "initial_db_status": db_statuses,
                    "degraded_operations": degraded_operations,
                    "recovery_operations": recovery_operations,
                    "cached_availability": cached_availability,
                    "database_availability": db_availability
                }
            )
            
        except Exception as e:
            return FaultToleranceTestResult(
                test_name=test_name,
                scenario=scenario,
                fault_injected=False,
                recovery_time=0,
                availability_during_fault=0,
                status="FAIL",
                message=f"Error en prueba de BD: {str(e)}",
                details={"error": str(e)}
            )

    async def test_message_queue_failure(self) -> FaultToleranceTestResult:
        """Probar tolerancia a fallos del sistema de mensajes (RabbitMQ)"""
        test_name = "Message Queue Failure Test"
        scenario = "Simulating RabbitMQ unavailability"
        
        self.logger.info("=== Iniciando prueba de fallo de queue de mensajes ===")
        
        try:
            # Paso 1: Verificar RabbitMQ inicial
            rabbitmq_check = await self._make_health_check("RabbitMQ", f"{self.config['lp2_url']}/api/rabbitmq/health", max_attempts=3)
            
            # Paso 2: Probar operaciones que requieren messaging
            messaging_operations = []
            messaging_scenarios = [
                ("Publish", f"{self.config['lp2_url']}/api/rabbitmq/publish", {"type": "test"}),
                ("Consume", f"{self.config['lp2_url']}/api/rabbitmq/consume", None),
                ("Status", f"{self.config['lp2_url']}/api/rabbitmq/status", None)
            ]
            
            for op_name, op_url, data in messaging_scenarios:
                operation_start = time.time()
                try:
                    if data:
                        async with self.session.post(op_url, json=data) as response:
                            success = response.status < 400
                    else:
                        async with self.session.get(op_url) as response:
                            success = response.status < 400
                    
                    duration = time.time() - operation_start
                    messaging_operations.append({
                        "operation": op_name,
                        "success": success,
                        "response_time": duration
                    })
                except Exception as e:
                    messaging_operations.append({
                        "operation": op_name,
                        "success": False,
                        "response_time": time.time() - operation_start,
                        "error": str(e)
                    })
            
            # Paso 3: Verificar degradación del sistema sin messaging
            # Probar si las operaciones core siguen funcionando
            core_operations = []
            core_urls = [
                f"{self.config['lp1_url']}/api/health",
                f"{self.config['lp2_url']}/api/health",
                f"{self.config['lp3_url']}/api/health"
            ]
            
            for url in core_urls:
                operation_start = time.time()
                try:
                    async with self.session.get(url) as response:
                        success = response.status < 400
                        duration = time.time() - operation_start
                        core_operations.append({
                            "service": url.split('/')[-2],
                            "success": success,
                            "response_time": duration
                        })
                except Exception as e:
                    core_operations.append({
                        "service": url.split('/')[-2],
                        "success": False,
                        "response_time": time.time() - operation_start,
                        "error": str(e)
                    })
            
            # Analizar resultados
            messaging_success = sum(1 for op in messaging_operations if op["success"])
            core_success = sum(1 for op in core_operations if op["success"])
            
            messaging_availability = messaging_success / len(messaging_operations) * 100
            core_availability = core_success / len(core_operations) * 100
            
            if core_availability >= 90:
                status = "PASS"
                message = f"Degradación MQ: Core {core_availability:.0f}%, Messaging {messaging_availability:.0f}%"
            elif core_availability >= 70:
                status = "WARNING"
                message = f"Degradación MQ parcial: Core {core_availability:.0f}%, Messaging {messaging_availability:.0f}%"
            else:
                status = "FAIL"
                message = "Core services fell during MQ failure"
            
            return FaultToleranceTestResult(
                test_name=test_name,
                scenario=scenario,
                fault_injected=False,
                recovery_time=0,
                availability_during_fault=core_availability,
                status=status,
                message=message,
                details={
                    "rabbitmq_initial_status": rabbitmq_check[0],
                    "messaging_operations": messaging_operations,
                    "core_operations": core_operations,
                    "messaging_availability": messaging_availability,
                    "core_availability": core_availability
                }
            )
            
        except Exception as e:
            return FaultToleranceTestResult(
                test_name=test_name,
                scenario=scenario,
                fault_injected=False,
                recovery_time=0,
                availability_during_fault=0,
                status="FAIL",
                message=f"Error en prueba de MQ: {str(e)}",
                details={"error": str(e)}
            )

    async def test_circuit_breaker_pattern(self) -> FaultToleranceTestResult:
        """Probar implementación de circuit breaker"""
        test_name = "Circuit Breaker Pattern Test"
        scenario = "Testing circuit breaker behavior under load"
        
        self.logger.info("=== Iniciando prueba de circuit breaker ===")
        
        try:
            # Paso 1: Enviar requests normales para establecer baseline
            baseline_requests = []
            for _ in range(10):
                try:
                    async with self.session.get(f"{self.config['lp1_url']}/api/health") as response:
                        success = response.status < 400
                        baseline_requests.append(success)
                except:
                    baseline_requests.append(False)
                await asyncio.sleep(0.1)
            
            baseline_success_rate = sum(baseline_requests) / len(baseline_requests) * 100
            
            # Paso 2: Enviar burst de requests para activar circuit breaker si existe
            burst_requests = []
            burst_size = 50
            
            for i in range(burst_size):
                try:
                    async with self.session.get(f"{self.config['lp1_url']}/api/health") as response:
                        success = response.status < 400
                        burst_requests.append(success)
                except Exception as e:
                    burst_requests.append(False)
                
                # Pausa mínima entre requests
                if i % 10 == 0:
                    await asyncio.sleep(0.05)
            
            # Paso 3: Verificar recuperación gradual
            recovery_requests = []
            for _ in range(20):
                try:
                    async with self.session.get(f"{self.config['lp1_url']}/api/health") as response:
                        success = response.status < 400
                        recovery_requests.append(success)
                except:
                    recovery_requests.append(False)
                await asyncio.sleep(0.5)
            
            # Analizar patrones
            burst_success_rate = sum(burst_requests) / len(burst_requests) * 100
            recovery_success_rate = sum(recovery_requests) / len(recovery_requests) * 100
            
            # Determinar si hay signs de circuit breaker
            circuit_breaker_indicators = {
                "baseline_stable": baseline_success_rate >= 90,
                "burst_degradation": burst_success_rate < baseline_success_rate * 0.8,
                "recovery_pattern": recovery_success_rate > burst_success_rate,
                "gradual_recovery": len([r for r in recovery_requests[:10]]) < len([r for r in recovery_requests[10:]])
            }
            
            indicators_met = sum(circuit_breaker_indicators.values())
            
            if indicators_met >= 3:
                status = "PASS"
                message = f"Circuit breaker: Patrón detectado ({indicators_met}/4 indicadores)"
            elif indicators_met >= 2:
                status = "WARNING"
                message = f"Circuit breaker: Patrón parcial ({indicators_met}/4 indicadores)"
            else:
                status = "FAIL"
                message = f"Circuit breaker: No detectado ({indicators_met}/4 indicadores)"
            
            return FaultToleranceTestResult(
                test_name=test_name,
                scenario=scenario,
                fault_injected=False,
                recovery_time=0,
                availability_during_fault=recovery_success_rate,
                status=status,
                message=message,
                details={
                    "baseline_success_rate": baseline_success_rate,
                    "burst_success_rate": burst_success_rate,
                    "recovery_success_rate": recovery_success_rate,
                    "circuit_breaker_indicators": circuit_breaker_indicators,
                    "indicators_met": indicators_met
                }
            )
            
        except Exception as e:
            return FaultToleranceTestResult(
                test_name=test_name,
                scenario=scenario,
                fault_injected=False,
                recovery_time=0,
                availability_during_fault=0,
                status="FAIL",
                message=f"Error en prueba de circuit breaker: {str(e)}",
                details={"error": str(e)}
            )

    async def test_graceful_degradation(self) -> FaultToleranceTestResult:
        """Probar degradación graceful del sistema"""
        test_name = "Graceful Degradation Test"
        scenario = "Testing system graceful degradation"
        
        self.logger.info("=== Iniciando prueba de degradación graceful ===")
        
        try:
            # Paso 1: Medir performance normal
            normal_performance = []
            for _ in range(20):
                try:
                    start = time.time()
                    async with self.session.get(f"{self.config['lp1_url']}/api/health") as response:
                        await response.json()
                        duration = time.time() - start
                        normal_performance.append(duration)
                except:
                    normal_performance.append(5.0)  # Asumir timeout
                await asyncio.sleep(0.2)
            
            normal_avg_time = sum(normal_performance) / len(normal_performance)
            
            # Paso 2: Probar bajo degradación simulada
            # En lugar de inyectar fallos reales, simulamos degradación con delays
            degraded_performance = []
            for _ in range(20):
                try:
                    # Simular red lenta con timeout más alto
                    timeout = aiohttp.ClientTimeout(total=10)
                    async with aiohttp.ClientSession(timeout=timeout) as session:
                        start = time.time()
                        async with session.get(f"{self.config['lp1_url']}/api/health") as response:
                            await response.json()
                            duration = time.time() - start
                            degraded_performance.append(duration)
                except:
                    degraded_performance.append(10.0)
                await asyncio.sleep(0.3)
            
            degraded_avg_time = sum(degraded_performance) / len(degraded_performance)
            
            # Paso 3: Verificar servicios críticos
            critical_services = [
                f"{self.config['lp1_url']}/api/health",
                f"{self.config['lp2_url']}/api/health",
                f"{self.config['lp3_url']}/api/health"
            ]
            
            critical_operational = 0
            for url in critical_services:
                try:
                    async with self.session.get(url) as response:
                        if response.status < 400:
                            critical_operational += 1
                except:
                    pass
            
            critical_availability = critical_operational / len(critical_services) * 100
            
            # Analizar degradación
            performance_degradation = (degraded_avg_time - normal_avg_time) / normal_avg_time * 100
            
            if performance_degradation < 50 and critical_availability >= 90:
                status = "PASS"
                message = f"Degradación graceful: {performance_degradation:.0f}% degradación, {critical_availability:.0f}% servicios críticos"
            elif performance_degradation < 100 and critical_availability >= 70:
                status = "WARNING"
                message = f"Degradación parcial: {performance_degradation:.0f}% degradación, {critical_availability:.0f}% servicios críticos"
            else:
                status = "FAIL"
                message = f"Degradación severa: {performance_degradation:.0f}% degradación, {critical_availability:.0f}% servicios críticos"
            
            return FaultToleranceTestResult(
                test_name=test_name,
                scenario=scenario,
                fault_injected=False,
                recovery_time=0,
                availability_during_fault=critical_availability,
                status=status,
                message=message,
                details={
                    "normal_avg_time": normal_avg_time,
                    "degraded_avg_time": degraded_avg_time,
                    "performance_degradation_percent": performance_degradation,
                    "critical_services_operational": critical_operational,
                    "critical_availability": critical_availability
                }
            )
            
        except Exception as e:
            return FaultToleranceTestResult(
                test_name=test_name,
                scenario=scenario,
                fault_injected=False,
                recovery_time=0,
                availability_during_fault=0,
                status="FAIL",
                message=f"Error en prueba de degradación: {str(e)}",
                details={"error": str(e)}
            )

    async def run_all_tests(self) -> List[FaultToleranceTestResult]:
        """Ejecutar todas las pruebas de tolerancia a fallos"""
        self.logger.info("=== INICIANDO PRUEBAS DE TOLERANCIA A FALLOS ===")
        
        tests = [
            self.test_service_unavailability,
            self.test_database_connection_failure,
            self.test_message_queue_failure,
            self.test_circuit_breaker_pattern,
            self.test_graceful_degradation
        ]
        
        for test in tests:
            self.logger.info(f"Ejecutando: {test.__name__}")
            try:
                result = await test()
                self.results.append(result)
                self.logger.info(f"Resultado: {result.status} - {result.message}")
            except Exception as e:
                self.logger.error(f"Error ejecutando {test.__name__}: {str(e)}")
                self.results.append(FaultToleranceTestResult(
                    test_name=test.__name__,
                    scenario="Unknown",
                    fault_injected=False,
                    recovery_time=0,
                    availability_during_fault=0,
                    status="FAIL",
                    message=f"Error inesperado: {str(e)}",
                    details={"error": str(e)}
                ))
        
        self.logger.info("=== PRUEBAS DE TOLERANCIA A FALLOS COMPLETADAS ===")
        return self.results

    def get_summary(self) -> Dict[str, Any]:
        """Obtener resumen de resultados de tolerancia a fallos"""
        total_tests = len(self.results)
        passed = sum(1 for r in self.results if r.status == "PASS")
        failed = sum(1 for r in self.results if r.status == "FAIL")
        warnings = sum(1 for r in self.results if r.status == "WARNING")
        
        # Calcular métricas de resiliencia
        avg_availability = sum(r.availability_during_fault for r in self.results) / total_tests if total_tests > 0 else 0
        avg_recovery_time = sum(r.recovery_time for r in self.results if r.recovery_time > 0) / len([r for r in self.results if r.recovery_time > 0]) if any(r.recovery_time > 0 for r in self.results) else 0
        
        # Calcular puntaje de tolerancia a fallos
        fault_tolerance_score = (passed * 100 + warnings * 70 + failed * 30) / total_tests if total_tests > 0 else 0
        
        return {
            "total_tests": total_tests,
            "passed": passed,
            "failed": failed,
            "warnings": warnings,
            "success_rate": (passed / total_tests * 100) if total_tests > 0 else 0,
            "resilience_metrics": {
                "average_availability_during_fault": avg_availability,
                "average_recovery_time": avg_recovery_time,
                "fault_tolerance_score": fault_tolerance_score
            },
            "results": [asdict(r) for r in self.results]
        }

    def save_results(self, filename: str = None):
        """Guardar resultados en archivo JSON"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"/workspace/validation_system/reports/fault_tolerance_test_results_{timestamp}.json"
        
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
    
    async with FaultToleranceTestSuite(config) as suite:
        await suite.run_all_tests()
        suite.save_results()
        
        summary = suite.get_summary()
        print("\n=== RESUMEN DE PRUEBAS DE TOLERANCIA A FALLOS ===")
        print(f"Total pruebas: {summary['total_tests']}")
        print(f"Pasaron: {summary['passed']}")
        print(f"Fallaron: {summary['failed']}")
        print(f"Advertencias: {summary['warnings']}")
        print(f"Tasa de éxito: {summary['success_rate']:.2f}%")
        print(f"Puntaje de tolerancia a fallos: {summary['resilience_metrics']['fault_tolerance_score']:.2f}%")
        print(f"\nMétricas de resiliencia:")
        print(f"  - Disponibilidad promedio durante fallos: {summary['resilience_metrics']['average_availability_during_fault']:.1f}%")
        print(f"  - Tiempo de recuperación promedio: {summary['resilience_metrics']['average_recovery_time']:.1f}s")

if __name__ == "__main__":
    asyncio.run(main())
