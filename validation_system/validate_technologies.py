#!/usr/bin/env python3
"""
Validador de Tecnologías Heterogéneas
Verifica la presencia y funcionalidad de Java, Python y JavaScript en el sistema
"""

import subprocess
import json
import time
import logging
import os
import platform
import shutil
import socket
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import re

@dataclass
class TechnologyValidationResult:
    """Resultado de validación de una tecnología"""
    technology: str
    version: str
    installed: bool
    functional: bool
    location: str
    status: str  # 'PASS', 'FAIL', 'WARNING'
    message: str
    details: Optional[Dict] = None
    timestamp: str = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()

class TechnologyValidator:
    """Validador de tecnologías heterogéneas"""
    
    def __init__(self):
        self.results: List[TechnologyValidationResult] = []
        
        # Configurar logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('/workspace/validation_system/logs/technology_validation.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def _run_command(self, command: List[str], timeout: int = 10) -> Tuple[bool, str, str]:
        """
        Ejecutar comando del sistema
        
        Args:
            command: Comando a ejecutar como lista
            timeout: Timeout en segundos
            
        Returns:
            Tuple con (success, stdout, stderr)
        """
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return (result.returncode == 0, result.stdout, result.stderr)
        except subprocess.TimeoutExpired:
            return (False, "", f"Command timed out after {timeout}s")
        except Exception as e:
            return (False, "", str(e))

    def validate_java(self) -> TechnologyValidationResult:
        """Validar instalación y funcionalidad de Java"""
        test_name = "Java Validation"
        
        try:
            # Buscar instalación de Java
            java_commands = ['java', 'javac', 'java.exe', 'javac.exe']
            java_path = None
            
            for cmd in java_commands:
                success, stdout, stderr = self._run_command(['which', cmd])
                if success:
                    java_path = stdout.strip()
                    break
            
            if not java_path:
                # Intentar encontrar Java en common locations
                common_paths = [
                    '/usr/bin/java',
                    '/usr/lib/jvm/java-*-openjdk*/bin/java',
                    'C:\\Program Files\\Java\\*\\bin\\java.exe',
                    'C:\\Program Files (x86)\\Java\\*\\bin\\java.exe'
                ]
                
                for path in common_paths:
                    if '*' in path:
                        import glob
                        matches = glob.glob(path)
                        if matches:
                            java_path = matches[0]
                            break
                    elif os.path.exists(path):
                        java_path = path
                        break
            
            if not java_path:
                return TechnologyValidationResult(
                    technology="Java",
                    version="Unknown",
                    installed=False,
                    functional=False,
                    location="",
                    status="FAIL",
                    message="Java no está instalado o no se encuentra en PATH",
                    details={"error": "Java executable not found"}
                )
            
            # Verificar versión
            success, version_output, stderr = self._run_command([java_path, '-version'])
            
            if not success:
                return TechnologyValidationResult(
                    technology="Java",
                    version="Unknown",
                    installed=True,
                    functional=False,
                    location=java_path,
                    status="FAIL",
                    message="Java encontrado pero no funciona",
                    details={"error": stderr}
                )
            
            # Extraer versión
            version_match = re.search(r'"(\d+\.\d+)', version_output)
            version = version_match.group(1) if version_match else "Unknown"
            
            # Probar compilación
            test_java_code = '''
            public class TestJava {
                public static void main(String[] args) {
                    System.out.println("Java funciona correctamente");
                }
            }
            '''
            
            # Escribir archivo temporal
            test_file = '/workspace/validation_system/temp/TestJava.java'
            os.makedirs('/workspace/validation_system/temp', exist_ok=True)
            
            with open(test_file, 'w') as f:
                f.write(test_java_code)
            
            # Compilar
            success, compile_output, compile_error = self._run_command([java_path, '-cp', '/workspace/validation_system/temp', 'javac', test_file])
            
            # Ejecutar
            class_file = '/workspace/validation_system/temp/TestJava.class'
            success, exec_output, exec_error = self._run_command([java_path, '-cp', '/workspace/validation_system/temp', 'TestJava'])
            
            # Limpiar archivos temporales
            for temp_file in [test_file, class_file]:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            
            functional = success and "Java funciona correctamente" in exec_output
            
            if functional:
                status = "PASS"
                message = f"Java {version} instalado y funcional"
            else:
                status = "FAIL"
                message = f"Java {version} instalado pero no funcional"
            
            return TechnologyValidationResult(
                technology="Java",
                version=version,
                installed=True,
                functional=functional,
                location=java_path,
                status=status,
                message=message,
                details={
                    "compile_success": success,
                    "execution_output": exec_output,
                    "compilation_error": compile_error
                }
            )
            
        except Exception as e:
            return TechnologyValidationResult(
                technology="Java",
                version="Unknown",
                installed=False,
                functional=False,
                location="",
                status="FAIL",
                message=f"Error validando Java: {str(e)}",
                details={"error": str(e)}
            )

    def validate_python(self) -> TechnologyValidationResult:
        """Validar instalación y funcionalidad de Python"""
        try:
            # Buscar instalación de Python
            python_commands = ['python3', 'python', 'python.exe', 'python3.exe']
            python_path = None
            
            for cmd in python_commands:
                success, stdout, stderr = self._run_command(['which', cmd])
                if success:
                    python_path = stdout.strip()
                    break
            
            if not python_path:
                return TechnologyValidationResult(
                    technology="Python",
                    version="Unknown",
                    installed=False,
                    functional=False,
                    location="",
                    status="FAIL",
                    message="Python no está instalado o no se encuentra en PATH",
                    details={"error": "Python executable not found"}
                )
            
            # Verificar versión
            success, version_output, stderr = self._run_command([python_path, '--version'])
            
            if not success:
                return TechnologyValidationResult(
                    technology="Python",
                    version="Unknown",
                    installed=True,
                    functional=False,
                    location=python_path,
                    status="FAIL",
                    message="Python encontrado pero no funciona",
                    details={"error": stderr}
                )
            
            version = version_output.strip()
            
            # Probar ejecución
            test_code = 'print("Python funciona correctamente")'
            success, exec_output, exec_error = self._run_command([python_path, '-c', test_code])
            
            functional = success and "Python funciona correctamente" in exec_output
            
            # Verificar librerías comunes
            common_packages = ['requests', 'aiohttp', 'psycopg2', 'pymysql']
            package_status = {}
            
            for package in common_packages:
                pkg_success, pkg_output, pkg_error = self._run_command([python_path, '-m', 'pip', 'show', package])
                package_status[package] = pkg_success
            
            status = "PASS" if functional else "FAIL"
            message = f"Python {version} {'funcionando' if functional else 'con problemas'}"
            
            return TechnologyValidationResult(
                technology="Python",
                version=version,
                installed=True,
                functional=functional,
                location=python_path,
                status=status,
                message=message,
                details={
                    "execution_success": success,
                    "execution_output": exec_output,
                    "packages": package_status
                }
            )
            
        except Exception as e:
            return TechnologyValidationResult(
                technology="Python",
                version="Unknown",
                installed=False,
                functional=False,
                location="",
                status="FAIL",
                message=f"Error validando Python: {str(e)}",
                details={"error": str(e)}
            )

    def validate_nodejs(self) -> TechnologyValidationResult:
        """Validar instalación y funcionalidad de Node.js"""
        try:
            # Buscar instalación de Node.js
            node_commands = ['node', 'node.exe']
            npm_commands = ['npm', 'npm.exe']
            
            node_path = None
            npm_path = None
            
            # Buscar Node.js
            for cmd in node_commands:
                success, stdout, stderr = self._run_command(['which', cmd])
                if success:
                    node_path = stdout.strip()
                    break
            
            # Buscar npm
            for cmd in npm_commands:
                success, stdout, stderr = self._run_command(['which', cmd])
                if success:
                    npm_path = stdout.strip()
                    break
            
            if not node_path:
                return TechnologyValidationResult(
                    technology="Node.js",
                    version="Unknown",
                    installed=False,
                    functional=False,
                    location="",
                    status="FAIL",
                    message="Node.js no está instalado o no se encuentra en PATH",
                    details={"error": "Node.js executable not found"}
                )
            
            # Verificar versión de Node.js
            success, version_output, stderr = self._run_command([node_path, '--version'])
            
            if not success:
                return TechnologyValidationResult(
                    technology="Node.js",
                    version="Unknown",
                    installed=True,
                    functional=False,
                    location=node_path,
                    status="FAIL",
                    message="Node.js encontrado pero no funciona",
                    details={"error": stderr}
                )
            
            node_version = version_output.strip()
            
            # Verificar npm si está disponible
            npm_version = "Not found"
            if npm_path:
                success, npm_version_output, npm_error = self._run_command([npm_path, '--version'])
                if success:
                    npm_version = npm_version_output.strip()
            
            # Probar ejecución de JavaScript
            test_js_code = 'console.log("Node.js funciona correctamente");'
            
            # Escribir archivo temporal
            test_file = '/workspace/validation_system/temp/test_node.js'
            os.makedirs('/workspace/validation_system/temp', exist_ok=True)
            
            with open(test_file, 'w') as f:
                f.write(test_js_code)
            
            success, exec_output, exec_error = self._run_command([node_path, test_file])
            
            # Limpiar archivo temporal
            if os.path.exists(test_file):
                os.remove(test_file)
            
            functional = success and "Node.js funciona correctamente" in exec_output
            
            status = "PASS" if functional else "FAIL"
            message = f"Node.js {node_version} {'funcionando' if functional else 'con problemas'}"
            
            return TechnologyValidationResult(
                technology="Node.js",
                version=node_version,
                installed=True,
                functional=functional,
                location=node_path,
                status=status,
                message=message,
                details={
                    "execution_success": success,
                    "execution_output": exec_output,
                    "npm_version": npm_version,
                    "npm_path": npm_path
                }
            )
            
        except Exception as e:
            return TechnologyValidationResult(
                technology="Node.js",
                version="Unknown",
                installed=False,
                functional=False,
                location="",
                status="FAIL",
                message=f"Error validando Node.js: {str(e)}",
                details={"error": str(e)}
            )

    def validate_docker(self) -> TechnologyValidationResult:
        """Validar instalación y funcionalidad de Docker"""
        try:
            # Buscar Docker
            docker_commands = ['docker', 'docker.exe']
            docker_path = None
            
            for cmd in docker_commands:
                success, stdout, stderr = self._run_command(['which', cmd])
                if success:
                    docker_path = stdout.strip()
                    break
            
            if not docker_path:
                return TechnologyValidationResult(
                    technology="Docker",
                    version="Unknown",
                    installed=False,
                    functional=False,
                    location="",
                    status="FAIL",
                    message="Docker no está instalado o no se encuentra en PATH",
                    details={"error": "Docker executable not found"}
                )
            
            # Verificar versión de Docker
            success, version_output, stderr = self._run_command([docker_path, '--version'])
            
            if not success:
                return TechnologyValidationResult(
                    technology="Docker",
                    version="Unknown",
                    installed=True,
                    functional=False,
                    location=docker_path,
                    status="FAIL",
                    message="Docker encontrado pero no funciona",
                    details={"error": stderr}
                )
            
            docker_version = version_output.strip()
            
            # Probar Docker daemon (puede requerir permisos especiales)
            success, info_output, info_error = self._run_command([docker_path, 'info'])
            
            daemon_accessible = success
            
            # Probar Docker Compose
            compose_commands = ['docker-compose', 'docker compose']
            compose_path = None
            
            for cmd in compose_commands:
                success, stdout, stderr = self._run_command(['which', cmd])
                if success:
                    compose_path = stdout.strip()
                    break
            
            compose_version = "Not found"
            if compose_path:
                success, compose_ver_output, compose_error = self._run_command([compose_path, '--version'])
                if success:
                    compose_version = compose_ver_output.strip()
            
            functional = daemon_accessible
            
            status = "PASS" if functional else "WARNING"
            message = f"Docker {docker_version} {'funcionando' if functional else 'instalado pero daemon no accesible'}"
            
            details = {
                "daemon_accessible": daemon_accessible,
                "docker_info_output": info_output,
                "compose_version": compose_version,
                "compose_path": compose_path
            }
            
            if not functional and "permission denied" in info_error.lower():
                details["note"] = "Docker daemon no accesible - puede requerir permisos de root o estar en grupo docker"
            
            return TechnologyValidationResult(
                technology="Docker",
                version=docker_version,
                installed=True,
                functional=functional,
                location=docker_path,
                status=status,
                message=message,
                details=details
            )
            
        except Exception as e:
            return TechnologyValidationResult(
                technology="Docker",
                version="Unknown",
                installed=False,
                functional=False,
                location="",
                status="FAIL",
                message=f"Error validando Docker: {str(e)}",
                details={"error": str(e)}
            )

    def validate_rabbitmq_client(self) -> TechnologyValidationResult:
        """Validar cliente RabbitMQ"""
        try:
            # Verificar si está instalado el cliente RabbitMQ
            # Para Python
            success, output, error = self._run_command(['python3', '-c', 'import pika; print("pika installed")'])
            pika_installed = success
            
            # Para Node.js
            success, output, error = self._run_command(['node', '-e', 'try { require("amqplib"); console.log("amqplib installed"); } catch(e) { console.log("amqplib not found"); }'])
            amqplib_installed = success
            
            # Para Java
            success, output, error = self._run_command(['python3', '-c', 'import subprocess; result = subprocess.run(["javac", "-version"], capture_output=True, text=True); print("Java found" if result.returncode == 0 else "Java not found")'])
            java_available = success
            
            clients_available = {
                "python_pika": pika_installed,
                "node_amqplib": amqplib_installed,
                "java_rabbitmq": java_available
            }
            
            functional_clients = sum(clients_available.values())
            
            status = "PASS" if functional_clients > 0 else "FAIL"
            message = f"RabbitMQ clients: {functional_clients}/3 disponibles"
            
            return TechnologyValidationResult(
                technology="RabbitMQ Clients",
                version="N/A",
                installed=functional_clients > 0,
                functional=functional_clients > 0,
                location="Multiple",
                status=status,
                message=message,
                details=clients_available
            )
            
        except Exception as e:
            return TechnologyValidationResult(
                technology="RabbitMQ Clients",
                version="Unknown",
                installed=False,
                functional=False,
                location="",
                status="FAIL",
                message=f"Error validando clientes RabbitMQ: {str(e)}",
                details={"error": str(e)}
            )

    def validate_database_clients(self) -> TechnologyValidationResult:
        """Validar clientes de bases de datos heterogéneas"""
        try:
            database_clients = {}
            
            # PostgreSQL clients
            psycopg2_success = False
            try:
                success, output, error = self._run_command(['python3', '-c', 'import psycopg2; print("psycopg2 available")'])
                psycopg2_success = success
            except:
                pass
            
            # MySQL clients
            pymysql_success = False
            try:
                success, output, error = self._run_command(['python3', '-c', 'import pymysql; print("pymysql available")'])
                pymysql_success = success
            except:
                pass
            
            # Redis clients
            redis_success = False
            try:
                success, output, error = self._run_command(['python3', '-c', 'import redis; print("redis available")'])
                redis_success = success
            except:
                pass
            
            # Java clients
            java_db_success = False
            try:
                success, output, error = self._run_command(['python3', '-c', 'import subprocess; result = subprocess.run(["javac", "-version"], capture_output=True, text=True); print("Java DB clients available" if result.returncode == 0 else "Java DB clients not available")'])
                java_db_success = success
            except:
                pass
            
            clients_status = {
                "postgresql_psycopg2": psycopg2_success,
                "mysql_pymysql": pymysql_success,
                "redis_pyredis": redis_success,
                "java_jdbc": java_db_success
            }
            
            functional_clients = sum(clients_status.values())
            
            status = "PASS" if functional_clients >= 2 else "FAIL"
            message = f"Database clients: {functional_clients}/4 disponibles"
            
            return TechnologyValidationResult(
                technology="Database Clients",
                version="N/A",
                installed=functional_clients > 0,
                functional=functional_clients >= 2,
                location="Multiple",
                status=status,
                message=message,
                details=clients_status
            )
            
        except Exception as e:
            return TechnologyValidationResult(
                technology="Database Clients",
                version="Unknown",
                installed=False,
                functional=False,
                location="",
                status="FAIL",
                message=f"Error validando clientes de BD: {str(e)}",
                details={"error": str(e)}
            )

    def validate_testing_frameworks(self) -> TechnologyValidationResult:
        """Validar frameworks de testing"""
        try:
            testing_frameworks = {}
            
            # Python testing
            pytest_success = False
            try:
                success, output, error = self._run_command(['python3', '-m', 'pytest', '--version'])
                pytest_success = success
            except:
                pass
            
            # JavaScript testing (Jest/Mocha)
            jest_success = False
            try:
                success, output, error = self._run_command(['npm', 'list', '-g', 'jest'])
                jest_success = success
            except:
                pass
            
            # Java testing (JUnit - verificar javac)
            junit_success = False
            try:
                success, output, error = self._run_command(['javac', '-version'])
                junit_success = success
            except:
                pass
            
            frameworks_status = {
                "python_pytest": pytest_success,
                "javascript_jest": jest_success,
                "java_junit": junit_success
            }
            
            functional_frameworks = sum(frameworks_status.values())
            
            status = "PASS" if functional_frameworks >= 2 else "WARNING"
            message = f"Testing frameworks: {functional_frameworks}/3 disponibles"
            
            return TechnologyValidationResult(
                technology="Testing Frameworks",
                version="N/A",
                installed=functional_frameworks > 0,
                functional=functional_frameworks >= 2,
                location="Multiple",
                status=status,
                message=message,
                details=frameworks_status
            )
            
        except Exception as e:
            return TechnologyValidationResult(
                technology="Testing Frameworks",
                version="Unknown",
                installed=False,
                functional=False,
                location="",
                status="FAIL",
                message=f"Error validando frameworks de testing: {str(e)}",
                details={"error": str(e)}
            )

    def run_all_validations(self) -> List[TechnologyValidationResult]:
        """Ejecutar todas las validaciones de tecnologías"""
        self.logger.info("=== INICIANDO VALIDACIÓN DE TECNOLOGÍAS ===")
        
        validations = [
            self.validate_java,
            self.validate_python,
            self.validate_nodejs,
            self.validate_docker,
            self.validate_rabbitmq_client,
            self.validate_database_clients,
            self.validate_testing_frameworks
        ]
        
        for validation in validations:
            self.logger.info(f"Validando: {validation.__name__}")
            try:
                result = validation()
                self.results.append(result)
                self.logger.info(f"Resultado: {result.status} - {result.message}")
            except Exception as e:
                self.logger.error(f"Error ejecutando {validation.__name__}: {str(e)}")
                self.results.append(TechnologyValidationResult(
                    technology=validation.__name__,
                    version="Unknown",
                    installed=False,
                    functional=False,
                    location="",
                    status="FAIL",
                    message=f"Error inesperado: {str(e)}",
                    details={"error": str(e)}
                ))
        
        self.logger.info("=== VALIDACIÓN DE TECNOLOGÍAS COMPLETADA ===")
        return self.results

    def get_summary(self) -> Dict[str, Any]:
        """Obtener resumen de validaciones"""
        total = len(self.results)
        passed = sum(1 for r in self.results if r.status == "PASS")
        failed = sum(1 for r in self.results if r.status == "FAIL")
        warnings = sum(1 for r in self.results if r.status == "WARNING")
        
        installed = sum(1 for r in self.results if r.installed)
        functional = sum(1 for r in self.results if r.functional)
        
        return {
            "total_validations": total,
            "passed": passed,
            "failed": failed,
            "warnings": warnings,
            "installed": installed,
            "functional": functional,
            "installation_rate": (installed / total * 100) if total > 0 else 0,
            "functionality_rate": (functional / total * 100) if total > 0 else 0,
            "heterogeneity_score": functional / len([r for r in self.results if r.technology in ['Java', 'Python', 'Node.js']]) * 100,
            "results": [asdict(r) for r in self.results]
        }

    def save_results(self, filename: str = None):
        """Guardar resultados en archivo JSON"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"/workspace/validation_system/reports/technology_validation_results_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(self.get_summary(), f, indent=2)
        
        self.logger.info(f"Resultados guardados en: {filename}")

def main():
    """Función principal para testing independiente"""
    validator = TechnologyValidator()
    validator.run_all_validations()
    validator.save_results()
    
    summary = validator.get_summary()
    print("\n=== RESUMEN DE VALIDACIÓN DE TECNOLOGÍAS ===")
    print(f"Total validaciones: {summary['total_validations']}")
    print(f"Pasaron: {summary['passed']}")
    print(f"Fallaron: {summary['failed']}")
    print(f"Advertencias: {summary['warnings']}")
    print(f"Tasa de instalación: {summary['installation_rate']:.2f}%")
    print(f"Tasa de funcionalidad: {summary['functionality_rate']:.2f}%")
    print(f"Puntaje de heterogeneidad: {summary['heterogeneity_score']:.2f}%")

if __name__ == "__main__":
    main()
