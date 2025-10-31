#!/usr/bin/env python3
"""
Validador del Sistema Completo
=============================

Valida la integridad del sistema, dependencias, configuraciones y
prepara el entorno para la ejecución de tests completos.

Autor: Testing System v2.0
Fecha: 2025-10-30
"""

import os
import sys
import json
import yaml
import asyncio
import aiohttp
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from colorama import init, Fore, Style

# Inicializar colorama
init(autoreset=True)

@dataclass
class ValidationResult:
    """Resultado de validación"""
    component: str
    status: str  # passed, failed, warning
    message: str
    duration: float = 0.0

class SystemValidator:
    """Validador del sistema completo"""
    
    def __init__(self, config_path: str = "test_suite_config.yml"):
        self.config_path = config_path
        self.config = self._load_config()
        self.validation_results: List[ValidationResult] = []
        
    def _load_config(self) -> Dict:
        """Cargar configuración"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                print(f"{Fore.GREEN}✅ Configuración cargada: {self.config_path}")
                return config
        except Exception as e:
            print(f"{Fore.RED}❌ Error cargando configuración: {e}")
            return {}
    
    def _check_python_environment(self) -> ValidationResult:
        """Validar entorno Python y dependencias"""
        start_time = time.time()
        
        # Verificar versión de Python
        python_version = sys.version_info
        if python_version < (3, 8):
            return ValidationResult(
                component="Python Environment",
                status="failed",
                message=f"Python {python_version.major}.{python_version.minor} no es compatible. Se requiere Python 3.8+",
                duration=time.time() - start_time
            )
        
        # Verificar dependencias críticas
        critical_deps = [
            'pytest', 'requests', 'pyyaml', 'asyncio', 'pathlib',
            'dataclasses', 'concurrent.futures'
        ]
        
        missing_deps = []
        for dep in critical_deps:
            try:
                __import__(dep)
            except ImportError:
                missing_deps.append(dep)
        
        if missing_deps:
            return ValidationResult(
                component="Python Dependencies",
                status="failed",
                message=f"Dependencias faltantes: {', '.join(missing_deps)}",
                duration=time.time() - start_time
            )
        
        return ValidationResult(
            component="Python Environment",
            status="passed",
            message=f"Python {python_version.major}.{python_version.minor}.{python_version.micro} - Todas las dependencias disponibles",
            duration=time.time() - start_time
        )
    
    def _check_configuration_files(self) -> List[ValidationResult]:
        """Validar archivos de configuración"""
        results = []
        
        # Verificar archivo principal de configuración
        config_file = Path(self.config_path)
        if not config_file.exists():
            results.append(ValidationResult(
                component="Configuration Files",
                status="failed",
                message=f"Archivo de configuración no encontrado: {self.config_path}"
            ))
        else:
            results.append(ValidationResult(
                component="Configuration Files",
                status="passed",
                message=f"Configuración principal encontrada: {self.config_path}"
            ))
        
        # Validar estructura de configuración
        if self.config:
            required_sections = ['general', 'unit_tests', 'integration_tests', 'e2e_tests']
            for section in required_sections:
                if section not in self.config:
                    results.append(ValidationResult(
                        component="Configuration Structure",
                        status="failed",
                        message=f"Sección faltante en configuración: {section}"
                    ))
        
        # Verificar requirements-test.txt
        requirements_file = Path("requirements-test.txt")
        if requirements_file.exists():
            results.append(ValidationResult(
                component="Requirements File",
                status="passed",
                message="Archivo de requirements encontrado"
            ))
        else:
            results.append(ValidationResult(
                component="Requirements File",
                status="failed",
                message="requirements-test.txt no encontrado"
            ))
        
        return results
    
    async def _check_service_dependencies(self) -> List[ValidationResult]:
        """Verificar disponibilidad de servicios externos"""
        results = []
        services = self.config.get('services', {})
        
        for service_name, service_config in services.items():
            start_time = time.time()
            
            # Verificar URL del servicio
            url = service_config.get('url', '')
            health_check = service_config.get('health_check', '/health')
            
            if not url:
                results.append(ValidationResult(
                    component=f"Service {service_name}",
                    status="warning",
                    message="URL no configurada",
                    duration=time.time() - start_time
                ))
                continue
            
            try:
                async with aiohttp.ClientSession() as session:
                    full_url = f"{url}{health_check}"
                    async with session.get(full_url, timeout=10) as response:
                        if response.status == 200:
                            results.append(ValidationResult(
                                component=f"Service {service_name}",
                                status="passed",
                                message=f"Servicio disponible: {full_url} (Status: {response.status})",
                                duration=time.time() - start_time
                            ))
                        else:
                            results.append(ValidationResult(
                                component=f"Service {service_name}",
                                status="warning",
                                message=f"Servicio respondiendo con código {response.status}: {full_url}",
                                duration=time.time() - start_time
                            ))
            except asyncio.TimeoutError:
                results.append(ValidationResult(
                    component=f"Service {service_name}",
                    status="warning",
                    message=f"Timeout conectando al servicio: {url}",
                    duration=time.time() - start_time
                ))
            except Exception as e:
                results.append(ValidationResult(
                    component=f"Service {service_name}",
                    status="warning",
                    message=f"Error conectando al servicio: {str(e)}",
                    duration=time.time() - start_time
                ))
        
        return results
    
    async def _check_database_connectivity(self) -> List[ValidationResult]:
        """Verificar conectividad de bases de datos"""
        results = []
        services = self.config.get('services', {})
        
        # Verificar PostgreSQL (si está configurado)
        postgres_configs = [
            service for service in services.values() 
            if 'postgres' in service.get('name', '').lower()
        ]
        
        for db_config in postgres_configs:
            start_time = time.time()
            try:
                # Intentar conexión básica a PostgreSQL
                import psycopg2
                conn = psycopg2.connect(
                    host=db_config.get('host', 'localhost'),
                    port=db_config.get('port', 5432),
                    user=db_config.get('username', 'postgres'),
                    password=db_config.get('password', ''),
                    dbname=db_config.get('database', 'test')
                )
                conn.close()
                
                results.append(ValidationResult(
                    component="Database PostgreSQL",
                    status="passed",
                    message="Conexión a PostgreSQL exitosa",
                    duration=time.time() - start_time
                ))
            except Exception as e:
                results.append(ValidationResult(
                    component="Database PostgreSQL",
                    status="warning",
                    message=f"Error conectando a PostgreSQL: {str(e)}",
                    duration=time.time() - start_time
                ))
        
        # Verificar Redis
        redis_configs = [
            service for service in services.values() 
            if 'redis' in service.get('name', '').lower()
        ]
        
        for redis_config in redis_configs:
            start_time = time.time()
            try:
                import redis
                r = redis.from_url(redis_config.get('url', 'redis://localhost:6379'))
                r.ping()
                
                results.append(ValidationResult(
                    component="Database Redis",
                    status="passed",
                    message="Conexión a Redis exitosa",
                    duration=time.time() - start_time
                ))
            except Exception as e:
                results.append(ValidationResult(
                    component="Database Redis",
                    status="warning",
                    message=f"Error conectando a Redis: {str(e)}",
                    duration=time.time() - start_time
                ))
        
        return results
    
    async def _check_external_tools(self) -> List[ValidationResult]:
        """Verificar herramientas externas"""
        results = []
        tools = {
            'pytest': ['pytest', '--version'],
            'playwright': ['playwright', '--version'],
            'git': ['git', '--version'],
            'docker': ['docker', '--version'],
            'node': ['node', '--version'],
            'npm': ['npm', '--version']
        }
        
        for tool_name, command in tools.items():
            start_time = time.time()
            try:
                process = await asyncio.create_subprocess_exec(
                    *command,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, stderr = await process.communicate()
                
                if process.returncode == 0:
                    version = stdout.decode().strip().split('\n')[0]
                    results.append(ValidationResult(
                        component=f"External Tool {tool_name}",
                        status="passed",
                        message=f"{tool_name} disponible: {version}",
                        duration=time.time() - start_time
                    ))
                else:
                    results.append(ValidationResult(
                        component=f"External Tool {tool_name}",
                        status="warning",
                        message=f"{tool_name} no funciona correctamente",
                        duration=time.time() - start_time
                    ))
            except FileNotFoundError:
                results.append(ValidationResult(
                    component=f"External Tool {tool_name}",
                    status="warning",
                    message=f"{tool_name} no encontrado en PATH",
                    duration=time.time() - start_time
                ))
            except Exception as e:
                results.append(ValidationResult(
                    component=f"External Tool {tool_name}",
                    status="warning",
                    message=f"Error verificando {tool_name}: {str(e)}",
                    duration=time.time() - start_time
                ))
        
        return results
    
    async def _check_system_resources(self) -> ValidationResult:
        """Verificar recursos del sistema"""
        start_time = time.time()
        
        try:
            import psutil
            
            # Verificar memoria disponible
            memory = psutil.virtual_memory()
            memory_gb = memory.available / (1024**3)
            
            # Verificar espacio en disco
            disk = psutil.disk_usage('.')
            disk_free_gb = disk.free / (1024**3)
            
            # Verificar CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            
            messages = []
            warnings = []
            
            if memory_gb < 2:
                warnings.append(f"Memoria disponible baja: {memory_gb:.1f}GB")
            else:
                messages.append(f"Memoria disponible: {memory_gb:.1f}GB")
            
            if disk_free_gb < 5:
                warnings.append(f"Espacio en disco bajo: {disk_free_gb:.1f}GB")
            else:
                messages.append(f"Espacio libre: {disk_free_gb:.1f}GB")
            
            if cpu_percent > 90:
                warnings.append(f"CPU alta: {cpu_percent:.1f}%")
            else:
                messages.append(f"Uso de CPU: {cpu_percent:.1f}%")
            
            status = "passed" if not warnings else "warning"
            message = " | ".join(messages + warnings)
            
            return ValidationResult(
                component="System Resources",
                status=status,
                message=message,
                duration=time.time() - start_time
            )
            
        except ImportError:
            return ValidationResult(
                component="System Resources",
                status="warning",
                message="psutil no disponible para verificar recursos del sistema",
                duration=time.time() - start_time
            )
        except Exception as e:
            return ValidationResult(
                component="System Resources",
                status="warning",
                message=f"Error verificando recursos del sistema: {str(e)}",
                duration=time.time() - start_time
            )
    
    def _check_directory_structure(self) -> List[ValidationResult]:
        """Verificar estructura de directorios"""
        results = []
        required_dirs = [
            'unit_tests',
            'integration_tests', 
            'e2e_tests',
            'performance_tests',
            'security_tests',
            'reports',
            'execution_logs'
        ]
        
        for directory in required_dirs:
            start_time = time.time()
            dir_path = Path(directory)
            
            if dir_path.exists():
                # Verificar permisos de escritura
                if os.access(dir_path, os.W_OK):
                    results.append(ValidationResult(
                        component=f"Directory {directory}",
                        status="passed",
                        message=f"Directorio existe y es escribible: {directory}",
                        duration=time.time() - start_time
                    ))
                else:
                    results.append(ValidationResult(
                        component=f"Directory {directory}",
                        status="warning",
                        message=f"Directorio existe pero no es escribible: {directory}",
                        duration=time.time() - start_time
                    ))
            else:
                try:
                    dir_path.mkdir(parents=True, exist_ok=True)
                    results.append(ValidationResult(
                        component=f"Directory {directory}",
                        status="passed",
                        message=f"Directorio creado: {directory}",
                        duration=time.time() - start_time
                    ))
                except Exception as e:
                    results.append(ValidationResult(
                        component=f"Directory {directory}",
                        status="failed",
                        message=f"Error creando directorio {directory}: {str(e)}",
                        duration=time.time() - start_time
                    ))
        
        return results
    
    def _generate_environment_setup_script(self) -> str:
        """Generar script de configuración del entorno"""
        script_content = """#!/bin/bash
# Script de Configuración del Entorno de Testing
# ==============================================

echo "🚀 Configurando entorno de testing..."

# Instalar dependencias Python
echo "📦 Instalando dependencias Python..."
pip install -r requirements-test.txt

# Instalar herramientas de testing
echo "🛠️ Instalando herramientas de testing..."

# Playwright
if command -v playwright &> /dev/null; then
    echo "Playwright ya está instalado"
else
    echo "Instalando Playwright..."
    pip install playwright
    playwright install chromium
fi

# Configurar permisos
echo "🔧 Configurando permisos..."
chmod +x run_all_tests.py
chmod +x validate_system.py
chmod +x generate_final_report.py

# Crear directorios
echo "📁 Creando directorios..."
mkdir -p reports execution_logs
mkdir -p unit_tests integration_tests e2e_tests performance_tests security_tests

echo "✅ Configuración del entorno completada!"
        """
        
        script_file = Path("setup_testing_environment.sh")
        with open(script_file, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        script_file.chmod(0o755)  # Hacer ejecutable
        
        return str(script_file)
    
    async def validate_system(self) -> Tuple[bool, List[ValidationResult]]:
        """Ejecutar validación completa del sistema"""
        print(f"{Fore.CYAN}🔍 Iniciando validación del sistema completo...")
        print(f"{Style.DIM}{'='*80}{Style.RESET_ALL}")
        
        all_results = []
        
        # Ejecutar todas las validaciones
        validations = [
            (self._check_python_environment, "Python Environment"),
            (self._check_configuration_files, "Configuration Files"),
            (self._check_directory_structure, "Directory Structure"),
            (self._check_external_tools, "External Tools"),
            (self._check_system_resources, "System Resources"),
            (self._check_service_dependencies, "Service Dependencies"),
            (self._check_database_connectivity, "Database Connectivity"),
        ]
        
        for validation_func, description in validations:
            print(f"\n{Fore.YELLOW}⏳ Validando: {description}...")
            
            try:
                if asyncio.iscoroutinefunction(validation_func):
                    result = await validation_func()
                else:
                    result = validation_func()
                
                # Asegurar que result sea una lista
                if isinstance(result, list):
                    all_results.extend(result)
                else:
                    all_results.append(result)
                
                # Mostrar resultados
                for res in (result if isinstance(result, list) else [result]):
                    color = Fore.GREEN if res.status == 'passed' else (
                        Fore.RED if res.status == 'failed' else Fore.YELLOW
                    )
                    status_symbol = "✅" if res.status == 'passed' else (
                        "❌" if res.status == 'failed' else "⚠️"
                    )
                    print(f"  {color}{status_symbol} {res.component}: {res.message}")
                
            except Exception as e:
                error_result = ValidationResult(
                    component=description,
                    status="failed",
                    message=f"Error durante validación: {str(e)}"
                )
                all_results.append(error_result)
                print(f"  {Fore.RED}❌ {error_result.component}: {error_result.message}")
        
        # Generar script de configuración del entorno
        if any(r.status == 'warning' or r.status == 'failed' for r in all_results):
            script_file = self._generate_environment_setup_script()
            print(f"\n{Fore.BLUE}📝 Script de configuración generado: {script_file}")
            print(f"{Fore.BLUE}💡 Ejecuta: bash {script_file}")
        
        return all_results
    
    def generate_validation_report(self, results: List[ValidationResult]) -> str:
        """Generar reporte de validación"""
        # Estadísticas
        total = len(results)
        passed = len([r for r in results if r.status == 'passed'])
        failed = len([r for r in results if r.status == 'failed'])
        warnings = len([r for r in results if r.status == 'warning'])
        
        # Generar reporte JSON
        report = {
            'validation_timestamp': datetime.now().isoformat(),
            'summary': {
                'total_validations': total,
                'passed': passed,
                'failed': failed,
                'warnings': warnings,
                'success_rate': (passed / total * 100) if total > 0 else 0
            },
            'results': [
                {
                    'component': r.component,
                    'status': r.status,
                    'message': r.message,
                    'duration': r.duration
                }
                for r in results
            ],
            'recommendations': []
        }
        
        # Agregar recomendaciones
        if failed > 0:
            report['recommendations'].append("Resolver errores críticos antes de ejecutar tests")
        if warnings > 0:
            report['recommendations'].append("Revisar advertencias para optimizar performance")
        if passed == total:
            report['recommendations'].append("Sistema listo para ejecución de tests completa")
        
        # Guardar reporte
        report_file = Path("execution_logs") / f"validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        
        return str(report_file)
    
    def print_executive_summary(self, results: List[ValidationResult]):
        """Imprimir resumen ejecutivo de validación"""
        print(f"\n{Fore.CYAN}📊 RESUMEN DE VALIDACIÓN")
        print("=" * 60)
        
        total = len(results)
        passed = len([r for r in results if r.status == 'passed'])
        failed = len([r for r in results if r.status == 'failed'])
        warnings = len([r for r in results if r.status == 'warning'])
        
        print(f"{Fore.GREEN}✅ Passed: {passed}/{total} ({passed/total*100:.1f}%)")
        print(f"{Fore.YELLOW}⚠️ Warnings: {warnings}/{total}")
        print(f"{Fore.RED}❌ Failed: {failed}/{total}")
        
        # Estado general
        if failed == 0:
            if warnings == 0:
                print(f"\n{Fore.GREEN}🎉 SISTEMA COMPLETAMENTE VALIDADO - Listo para testing!")
                overall_status = "READY"
            else:
                print(f"\n{Fore.YELLOW}⚠️ SISTEMA VALIDADO CON ADVERTENCIAS - Testing posible pero optimizable")
                overall_status = "READY_WITH_WARNINGS"
        else:
            print(f"\n{Fore.RED}❌ SISTEMA NO VALIDADO - Resolver errores antes del testing")
            overall_status = "NOT_READY"
        
        return overall_status

async def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Validador del Sistema de Testing")
    parser.add_argument("--config", default="test_suite_config.yml",
                       help="Archivo de configuración (default: test_suite_config.yml)")
    parser.add_argument("--verbose", action="store_true",
                       help="Salida detallada")
    
    args = parser.parse_args()
    
    # Inicializar validador
    validator = SystemValidator(args.config)
    
    try:
        # Ejecutar validación
        results = await validator.validate_system()
        
        # Mostrar resumen
        overall_status = validator.print_executive_summary(results)
        
        # Generar reporte
        report_file = validator.generate_validation_report(results)
        print(f"\n{Fore.BLUE}📄 Reporte de validación guardado en: {report_file}")
        
        # Código de salida basado en el estado
        if overall_status == "READY":
            sys.exit(0)
        elif overall_status == "READY_WITH_WARNINGS":
            sys.exit(1)  # Advertencia
        else:
            sys.exit(2)  # Error crítico
            
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}⚠️ Validación interrumpida por usuario")
        sys.exit(130)
    except Exception as e:
        print(f"\n{Fore.RED}❌ Error crítico durante validación: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())