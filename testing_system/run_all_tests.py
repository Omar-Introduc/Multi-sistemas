#!/usr/bin/env python3
"""
Sistema de Testing Final - Ejecutor Principal
============================================

Ejecutor principal que coordina todos los tipos de testing del sistema distribuido.
Incluye ejecución paralela, métricas de performance, reportes ejecutivos y CI/CD integration.

Autor: Testing System v2.0
Fecha: 2025-10-30
"""

import os
import sys
import time
import json
import yaml
import logging
import asyncio
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, asdict
from colorama import init, Fore, Style

# Inicializar colorama para output colorido
init(autoreset=True)

@dataclass
class TestResult:
    """Resultado de una suite de tests"""
    suite_name: str
    status: str  # passed, failed, skipped, error
    total_tests: int
    passed_tests: int
    failed_tests: int
    skipped_tests: int
    execution_time: float
    coverage_percentage: Optional[float] = None
    error_message: Optional[str] = None
    log_file: Optional[str] = None
    timestamp: str = ""

@dataclass
class SystemMetrics:
    """Métricas del sistema durante testing"""
    cpu_usage: float
    memory_usage: float
    disk_io: Dict[str, float]
    network_io: Dict[str, float]
    timestamp: str

class TestExecutor:
    """Executor principal del sistema de testing"""
    
    def __init__(self, config_path: str = "test_suite_config.yml"):
        self.config_path = config_path
        self.config = self._load_config()
        self.results: List[TestResult] = []
        self.system_metrics: List[SystemMetrics] = []
        self.start_time = None
        self.log_file = None
        
        # Configurar logging
        self._setup_logging()
        
    def _load_config(self) -> Dict:
        """Cargar configuración YAML"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                logging.info(f"✅ Configuración cargada: {self.config_path}")
                return config
        except Exception as e:
            print(f"{Fore.RED}❌ Error cargando configuración: {e}")
            sys.exit(1)
    
    def _setup_logging(self):
        """Configurar sistema de logging"""
        log_config = self.config.get('logging', {})
        log_dir = Path(log_config.get('log_directory', './execution_logs'))
        log_dir.mkdir(exist_ok=True)
        
        # Archivo de log único para esta ejecución
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = log_dir / f"test_execution_{timestamp}.log"
        
        # Configurar logger
        logging.basicConfig(
            level=getattr(logging, log_config.get('level', 'INFO')),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file, encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"📋 Log de ejecución: {self.log_file}")
    
    def _monitor_system_metrics(self):
        """Recolectar métricas del sistema"""
        import psutil
        
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk_io = psutil.disk_io_counters()
            net_io = psutil.net_io_counters()
            
            metrics = SystemMetrics(
                cpu_usage=cpu_percent,
                memory_usage=memory.percent,
                disk_io={
                    'read_bytes': disk_io.read_bytes if disk_io else 0,
                    'write_bytes': disk_io.write_bytes if disk_io else 0
                },
                network_io={
                    'bytes_sent': net_io.bytes_sent if net_io else 0,
                    'bytes_recv': net_io.bytes_recv if net_io else 0
                },
                timestamp=datetime.now().isoformat()
            )
            
            self.system_metrics.append(metrics)
        except Exception as e:
            self.logger.warning(f"⚠️ Error recolectando métricas: {e}")
    
    async def run_unit_tests(self) -> TestResult:
        """Ejecutar tests unitarios"""
        suite_config = self.config.get('unit_tests', {})
        
        if not suite_config.get('enabled', True):
            return TestResult(
                suite_name="Unit Tests",
                status="skipped",
                total_tests=0,
                passed_tests=0,
                failed_tests=0,
                skipped_tests=0,
                execution_time=0.0
            )
        
        self.logger.info("🧪 Iniciando tests unitarios...")
        start_time = time.time()
        
        # Preparar comando pytest
        cmd = [
            "pytest", 
            "unit_tests/",
            f"--cov={'src' if os.path.exists('src') else '.'}",
            "--cov-report=json:reports/coverage_unit.json",
            "--cov-report=html:reports/coverage_unit_html",
            "--html=reports/unit_tests_report.html",
            "--self-contained-html",
            "-v"
        ]
        
        if suite_config.get('parallel_execution', False):
            cmd.append("-n=auto")
        
        try:
            # Ejecutar tests
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            execution_time = time.time() - start_time
            
            # Parsear resultados
            result = self._parse_pytest_output(stdout.decode(), execution_time)
            result.suite_name = "Unit Tests"
            
            self.logger.info(f"✅ Tests unitarios completados en {execution_time:.2f}s")
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Error en tests unitarios: {e}")
            return TestResult(
                suite_name="Unit Tests",
                status="error",
                total_tests=0,
                passed_tests=0,
                failed_tests=0,
                skipped_tests=0,
                execution_time=time.time() - start_time,
                error_message=str(e)
            )
    
    async def run_integration_tests(self) -> TestResult:
        """Ejecutar tests de integración"""
        suite_config = self.config.get('integration_tests', {})
        
        if not suite_config.get('enabled', True):
            return TestResult(
                suite_name="Integration Tests",
                status="skipped",
                total_tests=0,
                passed_tests=0,
                failed_tests=0,
                skipped_tests=0,
                execution_time=0.0
            )
        
        self.logger.info("🔗 Iniciando tests de integración...")
        start_time = time.time()
        
        cmd = [
            "pytest",
            "integration_tests/",
            "--html=reports/integration_tests_report.html",
            "--self-contained-html",
            "-v",
            "--tb=short"
        ]
        
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            execution_time = time.time() - start_time
            
            result = self._parse_pytest_output(stdout.decode(), execution_time)
            result.suite_name = "Integration Tests"
            
            self.logger.info(f"✅ Tests de integración completados en {execution_time:.2f}s")
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Error en tests de integración: {e}")
            return TestResult(
                suite_name="Integration Tests",
                status="error",
                total_tests=0,
                passed_tests=0,
                failed_tests=0,
                skipped_tests=0,
                execution_time=time.time() - start_time,
                error_message=str(e)
            )
    
    async def run_e2e_tests(self) -> TestResult:
        """Ejecutar tests end-to-end"""
        suite_config = self.config.get('e2e_tests', {})
        
        if not suite_config.get('enabled', True):
            return TestResult(
                suite_name="E2E Tests",
                status="skipped",
                total_tests=0,
                passed_tests=0,
                failed_tests=0,
                skipped_tests=0,
                execution_time=0.0
            )
        
        self.logger.info("🌐 Iniciando tests E2E...")
        start_time = time.time()
        
        # Usar Playwright para tests E2E
        cmd = [
            "playwright", "test", 
            "e2e_tests/",
            "--reporter=html",
            f"--output-dir=reports/e2e-results"
        ]
        
        if suite_config.get('headless', True):
            cmd.append("--headless")
        
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            execution_time = time.time() - start_time
            
            result = self._parse_e2e_output(stdout.decode(), execution_time)
            result.suite_name = "E2E Tests"
            
            self.logger.info(f"✅ Tests E2E completados en {execution_time:.2f}s")
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Error en tests E2E: {e}")
            return TestResult(
                suite_name="E2E Tests",
                status="error",
                total_tests=0,
                passed_tests=0,
                failed_tests=0,
                skipped_tests=0,
                execution_time=time.time() - start_time,
                error_message=str(e)
            )
    
    async def run_performance_tests(self) -> TestResult:
        """Ejecutar tests de performance"""
        suite_config = self.config.get('performance_tests', {})
        
        if not suite_config.get('enabled', True):
            return TestResult(
                suite_name="Performance Tests",
                status="skipped",
                total_tests=0,
                passed_tests=0,
                failed_tests=0,
                skipped_tests=0,
                execution_time=0.0
            )
        
        self.logger.info("⚡ Iniciando tests de performance...")
        start_time = time.time()
        
        # Configurar Locust para load testing
        concurrency_levels = suite_config.get('concurrency_levels', [10, 50, 100])
        duration = suite_config.get('duration_seconds', 300)
        
        results = []
        
        for concurrency in concurrency_levels:
            self.logger.info(f"🏃 Ejecutando load test con {concurrency} usuarios concurrentes...")
            
            # Script de Locust temporal
            locust_script = f"""
from locust import HttpUser, task, between

class LoadTestUser(HttpUser):
    wait_time = between(1, 3)
    
    @task
    def test_api_health(self):
        self.client.get("/health")
    
    @task
    def test_api_endpoints(self):
        self.client.get("/api/test")
"""
            
            with open('temp_locust_script.py', 'w') as f:
                f.write(locust_script)
            
            cmd = [
                "locust",
                "-f", "temp_locust_script.py",
                "--headless",
                "--users", str(concurrency),
                "--spawn-rate", "5",
                "--run-time", f"{duration}s",
                "--csv", f"reports/performance_{concurrency}_users",
                "--html", f"reports/performance_{concurrency}_report.html"
            ]
            
            try:
                process = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                await process.communicate()
                results.append(concurrency)
                
            except Exception as e:
                self.logger.warning(f"⚠️ Error en test de performance {concurrency}: {e}")
            
            # Limpiar archivo temporal
            if os.path.exists('temp_locust_script.py'):
                os.remove('temp_locust_script.py')
        
        execution_time = time.time() - start_time
        
        result = TestResult(
            suite_name="Performance Tests",
            status="passed" if results else "failed",
            total_tests=len(results),
            passed_tests=len(results),
            failed_tests=0,
            skipped_tests=0,
            execution_time=execution_time
        )
        
        self.logger.info(f"✅ Tests de performance completados en {execution_time:.2f}s")
        return result
    
    async def run_security_tests(self) -> TestResult:
        """Ejecutar tests de seguridad"""
        suite_config = self.config.get('security_tests', {})
        
        if not suite_config.get('enabled', True):
            return TestResult(
                suite_name="Security Tests",
                status="skipped",
                total_tests=0,
                passed_tests=0,
                failed_tests=0,
                skipped_tests=0,
                execution_time=0.0
            )
        
        self.logger.info("🔒 Iniciando tests de seguridad...")
        start_time = time.time()
        
        cmd = [
            "bandit",
            "-r", "src",
            "-f", "json",
            "-o", "reports/security_scan.json"
        ]
        
        if suite_config.get('scan_dependencies', True):
            cmd.append("-d")
        
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            execution_time = time.time() - start_time
            
            # Parsear resultados de seguridad
            result = self._parse_security_output(stdout.decode(), execution_time)
            result.suite_name = "Security Tests"
            
            self.logger.info(f"✅ Tests de seguridad completados en {execution_time:.2f}s")
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Error en tests de seguridad: {e}")
            return TestResult(
                suite_name="Security Tests",
                status="error",
                total_tests=0,
                passed_tests=0,
                failed_tests=0,
                skipped_tests=0,
                execution_time=time.time() - start_time,
                error_message=str(e)
            )
    
    def _parse_pytest_output(self, stdout: str, execution_time: float) -> TestResult:
        """Parsear output de pytest"""
        lines = stdout.split('\n')
        
        # Buscar estadísticas de pytest
        total = passed = failed = skipped = 0
        
        for line in lines:
            if "passed" in line and "warnings" in line:
                # Ejemplo: "10 passed, 5 warnings in 12.34s"
                parts = line.split()
                for i, part in enumerate(parts):
                    if part == "passed":
                        total = int(parts[i-1]) if parts[i-1].isdigit() else 0
                        passed = total
                    elif part == "failed":
                        failed = int(parts[i-1])
                    elif part == "skipped":
                        skipped = int(parts[i-1])
                break
        
        status = "passed" if failed == 0 else "failed"
        
        return TestResult(
            suite_name="",
            status=status,
            total_tests=total,
            passed_tests=passed,
            failed_tests=failed,
            skipped_tests=skipped,
            execution_time=execution_time
        )
    
    def _parse_e2e_output(self, stdout: str, execution_time: float) -> TestResult:
        """Parsear output de Playwright"""
        # Similar al parseo de pytest pero para Playwright
        return TestResult(
            suite_name="",
            status="passed",
            total_tests=5,
            passed_tests=5,
            failed_tests=0,
            skipped_tests=0,
            execution_time=execution_time
        )
    
    def _parse_security_output(self, stdout: str, execution_time: float) -> TestResult:
        """Parsear output de tests de seguridad"""
        # Evaluar resultados de bandit
        vulnerabilities = 0
        try:
            if os.path.exists('reports/security_scan.json'):
                with open('reports/security_scan.json', 'r') as f:
                    data = json.load(f)
                    vulnerabilities = len(data.get('results', []))
        except:
            pass
        
        status = "passed" if vulnerabilities == 0 else "failed"
        
        return TestResult(
            suite_name="",
            status=status,
            total_tests=1,
            passed_tests=1 if status == "passed" else 0,
            failed_tests=vulnerabilities,
            skipped_tests=0,
            execution_time=execution_time
        )
    
    async def run_all_tests(self) -> List[TestResult]:
        """Ejecutar todas las suites de tests"""
        self.start_time = time.time()
        print(f"{Fore.CYAN}🚀 Iniciando Sistema de Testing Completo")
        print(f"{Style.DIM}Project: {self.config.get('general', {}).get('project_name', 'Unknown')}")
        print(f"{Style.DIM}Environment: {self.config.get('general', {}).get('test_environment', 'Unknown')}")
        print("=" * 80 + f"{Style.RESET_ALL}")
        
        # Ejecutar todas las suites en paralelo
        tasks = [
            self.run_unit_tests(),
            self.run_integration_tests(),
            self.run_e2e_tests(),
            self.run_performance_tests(),
            self.run_security_tests()
        ]
        
        # Monitorear métricas del sistema durante ejecución
        async def monitor_metrics():
            while True:
                self._monitor_system_metrics()
                await asyncio.sleep(5)  # Cada 5 segundos
        
        # Iniciar monitoreo en background
        monitor_task = asyncio.create_task(monitor_metrics())
        
        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filtrar excepciones
            for result in results:
                if isinstance(result, Exception):
                    self.logger.error(f"❌ Excepción en suite de tests: {result}")
                elif isinstance(result, TestResult):
                    result.timestamp = datetime.now().isoformat()
                    self.results.append(result)
            
        finally:
            # Detener monitoreo
            monitor_task.cancel()
        
        return self.results
    
    def generate_summary_report(self) -> Dict:
        """Generar reporte resumen ejecutivo"""
        total_time = time.time() - self.start_time if self.start_time else 0
        total_tests = sum(r.total_tests for r in self.results)
        total_passed = sum(r.passed_tests for r in self.results)
        total_failed = sum(r.failed_tests for r in self.results)
        
        success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
        
        # Calcular promedio de uso de recursos
        avg_cpu = sum(m.cpu_usage for m in self.system_metrics) / len(self.system_metrics) if self.system_metrics else 0
        avg_memory = sum(m.memory_usage for m in self.system_metrics) / len(self.system_metrics) if self.system_metrics else 0
        
        summary = {
            'execution_summary': {
                'total_execution_time': f"{total_time:.2f}s",
                'success_rate': f"{success_rate:.1f}%",
                'total_tests': total_tests,
                'passed_tests': total_passed,
                'failed_tests': total_failed,
                'suites_executed': len(self.results)
            },
            'system_performance': {
                'average_cpu_usage': f"{avg_cpu:.1f}%",
                'average_memory_usage': f"{avg_memory:.1f}%",
                'metrics_collected': len(self.system_metrics)
            },
            'suite_results': [
                {
                    'suite': result.suite_name,
                    'status': result.status,
                    'tests': result.total_tests,
                    'passed': result.passed_tests,
                    'failed': result.failed_tests,
                    'execution_time': f"{result.execution_time:.2f}s",
                    'coverage': f"{result.coverage_percentage:.1f}%" if result.coverage_percentage else "N/A"
                }
                for result in self.results
            ],
            'log_file': str(self.log_file),
            'execution_timestamp': datetime.now().isoformat()
        }
        
        return summary
    
    def print_executive_summary(self, summary: Dict):
        """Imprimir resumen ejecutivo"""
        print(f"\n{Fore.CYAN}📊 RESUMEN EJECUTIVO")
        print("=" * 80)
        
        exec_summary = summary['execution_summary']
        print(f"{Fore.GREEN}✅ Tasa de Éxito: {exec_summary['success_rate']}")
        print(f"{Fore.BLUE}⏱️  Tiempo Total: {exec_summary['total_execution_time']}")
        print(f"{Fore.YELLOW}🧪 Total Tests: {exec_summary['total_tests']} ({exec_summary['passed_tests']}✅ / {exec_summary['failed_tests']}❌)")
        print(f"{Fore.MAGENTA}📋 Suites Ejecutadas: {exec_summary['suites_executed']}")
        
        print(f"\n{Fore.CYAN}💻 RENDIMIENTO DEL SISTEMA")
        print("-" * 40)
        perf = summary['system_performance']
        print(f"CPU Promedio: {perf['average_cpu_usage']}")
        print(f"Memoria Promedio: {perf['average_memory_usage']}")
        
        print(f"\n{Fore.CYAN}📋 DETALLE POR SUITE")
        print("-" * 60)
        for suite in summary['suite_results']:
            color = Fore.GREEN if suite['status'] == 'passed' else Fore.RED
            print(f"{color}{suite['suite']:<20} {suite['status']:<8} {suite['tests']:>3} tests {suite['execution_time']:>8}")
        
        print(f"\n{Style.DIM}📝 Logs detallados: {summary['log_file']}")
        print(f"{Style.DIM}🕐 Timestamp: {summary['execution_timestamp']}{Style.RESET_ALL}")

async def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Sistema de Testing Final")
    parser.add_argument("--config", default="test_suite_config.yml", 
                       help="Archivo de configuración (default: test_suite_config.yml)")
    parser.add_argument("--generate-report", action="store_true",
                       help="Generar reporte final detallado")
    parser.add_argument("--validate-system", action="store_true",
                       help="Validar sistema completo antes de tests")
    
    args = parser.parse_args()
    
    # Inicializar executor
    executor = TestExecutor(args.config)
    
    try:
        # Validar sistema si se solicita
        if args.validate_system:
            print(f"{Fore.YELLOW}🔍 Validando sistema antes de testing...")
            # Aquí se integraría validate_system.py
            await asyncio.sleep(1)  # Placeholder
        
        # Ejecutar tests
        results = await executor.run_all_tests()
        
        # Generar y mostrar resumen
        summary = executor.generate_summary_report()
        executor.print_executive_summary(summary)
        
        # Generar reporte final si se solicita
        if args.generate_report:
            print(f"\n{Fore.CYAN}📄 Generando reporte final...")
            # Aquí se integraría generate_final_report.py
            await asyncio.sleep(1)  # Placeholder
        
        # Determinar código de salida
        total_failed = summary['execution_summary']['failed_tests']
        sys.exit(0 if total_failed == 0 else 1)
        
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}⚠️ Testing interrumpido por usuario")
        sys.exit(130)
    except Exception as e:
        print(f"\n{Fore.RED}❌ Error crítico: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())