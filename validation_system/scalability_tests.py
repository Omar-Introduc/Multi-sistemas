#!/usr/bin/env python3
"""
Pruebas de Escalabilidad y Concurrencia
Evalúa la capacidad del sistema para manejar carga y múltiples usuarios concurrentes
"""

import asyncio
import aiohttp
import time
import logging
import json
import statistics
import threading
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor, as_completed
import random

@dataclass
class ScalabilityTestResult:
    """Resultado de una prueba de escalabilidad"""
    test_name: str
    concurrency_level: int
    total_requests: int
    successful_requests: int
    failed_requests: int
    total_duration: float
    avg_response_time: float
    min_response_time: float
    max_response_time: float
    requests_per_second: float
    status: str  # 'PASS', 'FAIL', 'WARNING'
    message: str
    details: Optional[Dict] = None
    timestamp: str = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()

class ScalabilityTestSuite:
    """Suite de pruebas de escalabilidad y concurrencia"""
    
    def __init__(self, config: Dict[str, str]):
        """
        Inicializar suite de pruebas
        
        Args:
            config: Diccionario con URLs de servicios
        """
        self.config = config
        self.results: List[ScalabilityTestResult] = []
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Configurar logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('/workspace/validation_system/logs/scalability_tests.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    async def __aenter__(self):
        """Enter async context"""
        connector = aiohttp.TCPConnector(limit=200)
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(connector=connector, timeout=timeout)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit async context"""
        if self.session:
            await self.session.close()

    async def _make_request_with_timing(self, url: str, method: str = "GET", 
                                      data: Dict = None, session: aiohttp.ClientSession = None) -> Tuple[bool, float, str]:
        """
        Realizar petición HTTP con timing
        
        Returns:
            Tuple con (success, response_time, error_message)
        """
        start_time = time.time()
        error_message = ""
        
        try:
            if session:
                async with session.request(method, url, json=data) as response:
                    await response.json()
                    duration = time.time() - start_time
                    return (response.status < 400, duration, "")
            else:
                async with self.session.request(method, url, json=data) as response:
                    await response.json()
                    duration = time.time() - start_time
                    return (response.status < 400, duration, "")
                    
        except Exception as e:
            duration = time.time() - start_time
            error_message = str(e)
            return (False, duration, error_message)

    async def _run_concurrent_requests(self, url: str, concurrency: int, 
                                     total_requests: int, method: str = "GET", 
                                     data: Dict = None) -> List[Tuple[bool, float]]:
        """Ejecutar múltiples requests concurrentes"""
        
        # Crear sessions individuales para evitar problemas de concurrencia
        connector = aiohttp.TCPConnector(limit=concurrency + 10)
        timeout = aiohttp.ClientTimeout(total=20)
        
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            # Crear semaphore para controlar concurrencia
            semaphore = asyncio.Semaphore(concurrency)
            
            async def bounded_request():
                async with semaphore:
                    return await self._make_request_with_timing(url, method, data, session)
            
            # Crear todas las tareas
            tasks = []
            for _ in range(total_requests):
                task = asyncio.create_task(bounded_request())
                tasks.append(task)
            
            # Esperar a que todas completen
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Procesar resultados
            valid_results = []
            for result in results:
                if isinstance(result, tuple):
                    valid_results.append(result)
                else:
                    # Excepción ocurrió
                    valid_results.append((False, 0))
            
            return valid_results

    async def test_basic_concurrency(self) -> ScalabilityTestResult:
        """Probar concurrencia básica"""
        test_name = "Basic Concurrency Test"
        concurrency_levels = [1, 5, 10, 25, 50]
        total_requests = 100
        
        all_results = []
        
        for concurrency in concurrency_levels:
            self.logger.info(f"Probando concurrencia: {concurrency}")
            
            start_time = time.time()
            results = await self._run_concurrent_requests(
                f"{self.config['lp1_url']}/api/health",
                concurrency,
                total_requests,
                "GET"
            )
            total_duration = time.time() - start_time
            
            # Analizar resultados
            successful = sum(1 for success, _ in results if success)
            failed = len(results) - successful
            
            response_times = [duration for success, duration in results if success]
            avg_response_time = statistics.mean(response_times) if response_times else 0
            min_response_time = min(response_times) if response_times else 0
            max_response_time = max(response_times) if response_times else 0
            
            requests_per_second = successful / total_duration if total_duration > 0 else 0
            
            result_data = {
                "concurrency": concurrency,
                "successful": successful,
                "failed": failed,
                "avg_response_time": avg_response_time,
                "requests_per_second": requests_per_second,
                "total_duration": total_duration
            }
            all_results.append(result_data)
            
            # Determinar si el nivel de concurrencia es aceptable
            success_rate = successful / len(results) * 100
            if success_rate >= 95 and avg_response_time < 2.0:
                status = "PASS"
                message = f"Concurrencia {concurrency}: Excelente rendimiento"
            elif success_rate >= 90 and avg_response_time < 5.0:
                status = "WARNING"
                message = f"Concurrencia {concurrency}: Rendimiento aceptable"
            else:
                status = "FAIL"
                message = f"Concurrencia {concurrency}: Rendimiento pobre"
            
            # Guardar resultado individual
            result = ScalabilityTestResult(
                test_name=f"{test_name} - {concurrency} concurrentes",
                concurrency_level=concurrency,
                total_requests=total_requests,
                successful_requests=successful,
                failed_requests=failed,
                total_duration=total_duration,
                avg_response_time=avg_response_time,
                min_response_time=min_response_time,
                max_response_time=max_response_time,
                requests_per_second=requests_per_second,
                status=status,
                message=message,
                details=result_data
            )
            self.results.append(result)
        
        # Resultado general del test
        avg_success_rate = statistics.mean([r["successful"]/total_requests*100 for r in all_results])
        max_throughput = max(r["requests_per_second"] for r in all_results)
        
        if avg_success_rate >= 95:
            overall_status = "PASS"
            overall_message = f"Concurrencia básica: {avg_success_rate:.1f}% éxito, {max_throughput:.1f} RPS pico"
        elif avg_success_rate >= 90:
            overall_status = "WARNING"
            overall_message = f"Concurrencia básica: {avg_success_rate:.1f}% éxito, necesita optimización"
        else:
            overall_status = "FAIL"
            overall_message = f"Concurrencia básica: {avg_success_rate:.1f}% éxito, problemas de rendimiento"
        
        return ScalabilityTestResult(
            test_name=test_name,
            concurrency_level=0,
            total_requests=0,
            successful_requests=0,
            failed_requests=0,
            total_duration=0,
            avg_response_time=0,
            min_response_time=0,
            max_response_time=0,
            requests_per_second=0,
            status=overall_status,
            message=overall_message,
            details={
                "all_levels": all_results,
                "avg_success_rate": avg_success_rate,
                "max_throughput": max_throughput
            }
        )

    async def test_load_stress(self) -> ScalabilityTestResult:
        """Probar carga de estrés"""
        test_name = "Load Stress Test"
        
        # Test de incremento gradual de carga
        load_levels = [10, 25, 50, 100, 200]
        requests_per_level = 50
        max_duration = 300  # 5 minutos máximo
        
        cumulative_results = []
        total_start_time = time.time()
        
        for load in load_levels:
            if time.time() - total_start_time > max_duration:
                self.logger.warning("Tiempo máximo de prueba alcanzado")
                break
                
            self.logger.info(f"Probando carga: {load} usuarios concurrentes")
            
            level_start_time = time.time()
            results = await self._run_concurrent_requests(
                f"{self.config['lp1_url']}/api/health",
                load,
                requests_per_level,
                "GET"
            )
            level_duration = time.time() - level_start_time
            
            successful = sum(1 for success, _ in results if success)
            failed = len(results) - successful
            
            response_times = [duration for success, duration in results if success]
            avg_response_time = statistics.mean(response_times) if response_times else 0
            
            requests_per_second = successful / level_duration if level_duration > 0 else 0
            success_rate = successful / len(results) * 100
            
            level_result = {
                "load": load,
                "successful": successful,
                "failed": failed,
                "success_rate": success_rate,
                "avg_response_time": avg_response_time,
                "requests_per_second": requests_per_second,
                "duration": level_duration
            }
            cumulative_results.append(level_result)
            
            # Analizar si el sistema se comporta bien bajo esta carga
            if success_rate < 80 or avg_response_time > 10:
                self.logger.warning(f"Sistema bajo estrés en carga {load}")
        
        total_duration = time.time() - total_start_time
        
        # Calcular métricas generales
        avg_success_rate = statistics.mean([r["success_rate"] for r in cumulative_results])
        max_achievable_load = max(r["load"] for r in cumulative_results if r["success_rate"] >= 90)
        
        if not cumulative_results:
            max_achievable_load = 0
        
        if max_achievable_load >= 100:
            status = "PASS"
            message = f"Prueba de estrés: Maneja {max_achievable_load} usuarios concurrentes"
        elif max_achievable_load >= 50:
            status = "WARNING"
            message = f"Prueba de estrés: Maneja {max_achievable_load} usuarios concurrentes (limitado)"
        else:
            status = "FAIL"
            message = f"Prueba de estrés: Solo maneja {max_achievable_load} usuarios concurrentes"
        
        return ScalabilityTestResult(
            test_name=test_name,
            concurrency_level=max_achievable_load,
            total_requests=len(cumulative_results) * requests_per_level,
            successful_requests=sum(r["successful"] for r in cumulative_results),
            failed_requests=sum(r["failed"] for r in cumulative_results),
            total_duration=total_duration,
            avg_response_time=statistics.mean([r["avg_response_time"] for r in cumulative_results]),
            min_response_time=min([r["avg_response_time"] for r in cumulative_results]),
            max_response_time=max([r["avg_response_time"] for r in cumulative_results]),
            requests_per_second=sum(r["requests_per_second"] for r in cumulative_results),
            status=status,
            message=message,
            details={
                "load_test_results": cumulative_results,
                "max_achievable_load": max_achievable_load,
                "avg_success_rate": avg_success_rate
            }
        )

    async def test_memory_usage(self) -> ScalabilityTestResult:
        """Probar uso de memoria bajo carga"""
        test_name = "Memory Usage Test"
        
        import psutil
        import os
        
        # Obtener proceso principal del sistema
        try:
            current_process = psutil.Process(os.getpid())
            initial_memory = current_process.memory_info().rss / 1024 / 1024  # MB
        except:
            initial_memory = 0
        
        # Ejecutar carga moderada
        load = 25
        requests = 100
        
        self.logger.info("Probando uso de memoria bajo carga")
        
        start_time = time.time()
        results = await self._run_concurrent_requests(
            f"{self.config['lp1_url']}/api/health",
            load,
            requests,
            "GET"
        )
        duration = time.time() - start_time
        
        # Verificar uso de memoria final
        try:
            final_memory = current_process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = final_memory - initial_memory
        except:
            memory_increase = 0
        
        successful = sum(1 for success, _ in results if success)
        failed = len(results) - successful
        
        # Analizar leaks de memoria
        if memory_increase < 10:  # Menos de 10MB de incremento
            memory_status = "OK"
            memory_message = f"Incremento de memoria: {memory_increase:.1f}MB (Normal)"
        elif memory_increase < 50:  # Menos de 50MB
            memory_status = "WARNING"
            memory_message = f"Incremento de memoria: {memory_increase:.1f}MB (Moderado)"
        else:
            memory_status = "FAIL"
            memory_message = f"Incremento de memoria: {memory_increase:.1f}MB (Posible leak)"
        
        if successful / len(results) >= 0.95 and memory_status == "OK":
            status = "PASS"
        elif successful / len(results) >= 0.90 and memory_status != "FAIL":
            status = "WARNING"
        else:
            status = "FAIL"
        
        return ScalabilityTestResult(
            test_name=test_name,
            concurrency_level=load,
            total_requests=requests,
            successful_requests=successful,
            failed_requests=failed,
            total_duration=duration,
            avg_response_time=statistics.mean([duration for success, duration in results if success]) if successful > 0 else 0,
            min_response_time=min([duration for success, duration in results if success]) if successful > 0 else 0,
            max_response_time=max([duration for success, duration in results if success]) if successful > 0 else 0,
            requests_per_second=successful / duration if duration > 0 else 0,
            status=status,
            message=memory_message,
            details={
                "initial_memory_mb": initial_memory,
                "final_memory_mb": final_memory,
                "memory_increase_mb": memory_increase,
                "successful": successful,
                "failed": failed,
                "memory_status": memory_status
            }
        )

    async def test_database_scalability(self) -> ScalabilityTestResult:
        """Probar escalabilidad de base de datos"""
        test_name = "Database Scalability Test"
        
        # Test específico para operaciones de BD
        db_operations = [
            ("GET", f"{self.config['lp1_url']}/api/database/mysql/health"),
            ("GET", f"{self.config['lp2_url']}/api/database/postgres/health"),
            ("GET", f"{self.config['lp2_url']}/api/database/redis/health"),
        ]
        
        concurrency = 15
        requests_per_operation = 30
        
        all_db_results = []
        
        for method, url in db_operations:
            self.logger.info(f"Probando BD: {url}")
            
            start_time = time.time()
            results = await self._run_concurrent_requests(
                url,
                concurrency,
                requests_per_operation,
                method
            )
            duration = time.time() - start_time
            
            successful = sum(1 for success, _ in results if success)
            
            response_times = [duration for success, duration in results if success]
            avg_response_time = statistics.mean(response_times) if response_times else 0
            
            db_result = {
                "operation": url,
                "successful": successful,
                "total": requests_per_operation,
                "success_rate": successful / requests_per_operation * 100,
                "avg_response_time": avg_response_time,
                "duration": duration
            }
            all_db_results.append(db_result)
        
        # Analizar resultados generales de BD
        avg_success_rate = statistics.mean([r["success_rate"] for r in all_db_results])
        avg_response_time = statistics.mean([r["avg_response_time"] for r in all_db_results])
        
        if avg_success_rate >= 95 and avg_response_time < 1.0:
            status = "PASS"
            message = f"Escalabilidad BD: {avg_success_rate:.1f}% éxito, {avg_response_time:.2f}s promedio"
        elif avg_success_rate >= 90 and avg_response_time < 3.0:
            status = "WARNING"
            message = f"Escalabilidad BD: {avg_success_rate:.1f}% éxito, {avg_response_time:.2f}s promedio"
        else:
            status = "FAIL"
            message = f"Escalabilidad BD: {avg_success_rate:.1f}% éxito, problemas de rendimiento"
        
        return ScalabilityTestResult(
            test_name=test_name,
            concurrency_level=concurrency,
            total_requests=len(all_db_results) * requests_per_operation,
            successful_requests=sum(r["successful"] for r in all_db_results),
            failed_requests=len(all_db_results) * requests_per_operation - sum(r["successful"] for r in all_db_results),
            total_duration=max(r["duration"] for r in all_db_results),
            avg_response_time=avg_response_time,
            min_response_time=min([r["avg_response_time"] for r in all_db_results]),
            max_response_time=max([r["avg_response_time"] for r in all_db_results]),
            requests_per_second=sum(r["successful"] for r in all_db_results) / max(r["duration"] for r in all_db_results) if all_db_results else 0,
            status=status,
            message=message,
            details={
                "database_results": all_db_results,
                "avg_success_rate": avg_success_rate,
                "avg_response_time": avg_response_time
            }
        )

    async def test_concurrent_operations(self) -> ScalabilityTestResult:
        """Probar operaciones concurrentes entre servicios"""
        test_name = "Concurrent Operations Test"
        
        # Operaciones que involucran múltiples servicios
        operations = [
            ("LP1 Health", f"{self.config['lp1_url']}/api/health", "GET"),
            ("LP2 Health", f"{self.config['lp2_url']}/api/health", "GET"),
            ("LP3 Health", f"{self.config['lp3_url']}/api/health", "GET"),
            ("Customer Validation", f"{self.config['lp3_url']}/api/validate-customer", "POST", {"dni": "12345678"}),
        ]
        
        concurrency = 20
        requests_per_operation = 25
        
        all_operation_results = []
        
        for operation_info in operations:
            if len(operation_info) == 3:
                name, url, method = operation_info
                data = None
            else:
                name, url, method, data = operation_info
            
            self.logger.info(f"Probando operación: {name}")
            
            start_time = time.time()
            results = await self._run_concurrent_requests(
                url,
                concurrency,
                requests_per_operation,
                method,
                data
            )
            duration = time.time() - start_time
            
            successful = sum(1 for success, _ in results if success)
            failed = len(results) - successful
            
            response_times = [duration for success, duration in results if success]
            avg_response_time = statistics.mean(response_times) if response_times else 0
            
            operation_result = {
                "operation": name,
                "url": url,
                "successful": successful,
                "failed": failed,
                "success_rate": successful / len(results) * 100,
                "avg_response_time": avg_response_time,
                "duration": duration
            }
            all_operation_results.append(operation_result)
        
        # Análisis general
        avg_success_rate = statistics.mean([r["success_rate"] for r in all_operation_results])
        avg_response_time = statistics.mean([r["avg_response_time"] for r in all_operation_results])
        
        if avg_success_rate >= 95 and avg_response_time < 2.0:
            status = "PASS"
            message = f"Operaciones concurrentes: {avg_success_rate:.1f}% éxito"
        elif avg_success_rate >= 90 and avg_response_time < 5.0:
            status = "WARNING"
            message = f"Operaciones concurrentes: {avg_success_rate:.1f}% éxito"
        else:
            status = "FAIL"
            message = f"Operaciones concurrentes: {avg_success_rate:.1f}% éxito, problemas de rendimiento"
        
        total_successful = sum(r["successful"] for r in all_operation_results)
        total_requests = sum(r["successful"] + r["failed"] for r in all_operation_results)
        
        return ScalabilityTestResult(
            test_name=test_name,
            concurrency_level=concurrency,
            total_requests=total_requests,
            successful_requests=total_successful,
            failed_requests=total_requests - total_successful,
            total_duration=max(r["duration"] for r in all_operation_results),
            avg_response_time=avg_response_time,
            min_response_time=min([r["avg_response_time"] for r in all_operation_results]),
            max_response_time=max([r["avg_response_time"] for r in all_operation_results]),
            requests_per_second=total_successful / max(r["duration"] for r in all_operation_results) if all_operation_results else 0,
            status=status,
            message=message,
            details={
                "operation_results": all_operation_results,
                "avg_success_rate": avg_success_rate,
                "avg_response_time": avg_response_time
            }
        )

    async def run_all_tests(self) -> List[ScalabilityTestResult]:
        """Ejecutar todas las pruebas de escalabilidad"""
        self.logger.info("=== INICIANDO PRUEBAS DE ESCALABILIDAD ===")
        
        tests = [
            self.test_basic_concurrency,
            self.test_load_stress,
            self.test_memory_usage,
            self.test_database_scalability,
            self.test_concurrent_operations
        ]
        
        for test in tests:
            self.logger.info(f"Ejecutando: {test.__name__}")
            try:
                result = await test()
                self.results.append(result)
                self.logger.info(f"Resultado: {result.status} - {result.message}")
            except Exception as e:
                self.logger.error(f"Error ejecutando {test.__name__}: {str(e)}")
                self.results.append(ScalabilityTestResult(
                    test_name=test.__name__,
                    concurrency_level=0,
                    total_requests=0,
                    successful_requests=0,
                    failed_requests=0,
                    total_duration=0,
                    avg_response_time=0,
                    min_response_time=0,
                    max_response_time=0,
                    requests_per_second=0,
                    status="FAIL",
                    message=f"Error inesperado: {str(e)}",
                    details={"error": str(e)}
                ))
        
        self.logger.info("=== PRUEBAS DE ESCALABILIDAD COMPLETADAS ===")
        return self.results

    def get_summary(self) -> Dict[str, Any]:
        """Obtener resumen de resultados de escalabilidad"""
        total_tests = len(self.results)
        passed = sum(1 for r in self.results if r.status == "PASS")
        failed = sum(1 for r in self.results if r.status == "FAIL")
        warnings = sum(1 for r in self.results if r.status == "WARNING")
        
        # Calcular métricas generales
        total_successful = sum(r.successful_requests for r in self.results)
        total_requests = sum(r.total_requests for r in self.results)
        total_duration = sum(r.total_duration for r in self.results)
        avg_response_time = statistics.mean([r.avg_response_time for r in self.results if r.avg_response_time > 0])
        max_throughput = max(r.requests_per_second for r in self.results)
        
        return {
            "total_tests": total_tests,
            "passed": passed,
            "failed": failed,
            "warnings": warnings,
            "success_rate": (passed / total_tests * 100) if total_tests > 0 else 0,
            "system_throughput": {
                "total_requests": total_requests,
                "successful_requests": total_successful,
                "overall_success_rate": (total_successful / total_requests * 100) if total_requests > 0 else 0,
                "total_duration": total_duration,
                "average_response_time": avg_response_time,
                "max_throughput_rps": max_throughput
            },
            "scalability_score": self._calculate_scalability_score(),
            "results": [asdict(r) for r in self.results]
        }

    def _calculate_scalability_score(self) -> float:
        """Calcular puntaje general de escalabilidad"""
        if not self.results:
            return 0.0
        
        scores = []
        for result in self.results:
            if result.status == "PASS":
                scores.append(100)
            elif result.status == "WARNING":
                scores.append(70)
            else:
                scores.append(30)
        
        return sum(scores) / len(scores)

    def save_results(self, filename: str = None):
        """Guardar resultados en archivo JSON"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"/workspace/validation_system/reports/scalability_test_results_{timestamp}.json"
        
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
    
    async with ScalabilityTestSuite(config) as suite:
        await suite.run_all_tests()
        suite.save_results()
        
        summary = suite.get_summary()
        print("\n=== RESUMEN DE PRUEBAS DE ESCALABILIDAD ===")
        print(f"Total pruebas: {summary['total_tests']}")
        print(f"Pasaron: {summary['passed']}")
        print(f"Fallaron: {summary['failed']}")
        print(f"Advertencias: {summary['warnings']}")
        print(f"Tasa de éxito: {summary['success_rate']:.2f}%")
        print(f"Puntaje de escalabilidad: {summary['scalability_score']:.2f}%")
        print(f"\nMétricas del sistema:")
        print(f"  - Requests exitosos: {summary['system_throughput']['successful_requests']}/{summary['system_throughput']['total_requests']}")
        print(f"  - Tasa de éxito general: {summary['system_throughput']['overall_success_rate']:.2f}%")
        print(f"  - Tiempo de respuesta promedio: {summary['system_throughput']['average_response_time']:.2f}s")
        print(f"  - RPS máximo: {summary['system_throughput']['max_throughput_rps']:.1f}")

if __name__ == "__main__":
    asyncio.run(main())
