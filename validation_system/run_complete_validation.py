#!/usr/bin/env python3
"""
Ejecutor Maestro de Validación Integral
Coordina todos los módulos de validación y genera reporte consolidado
"""

import asyncio
import json
import os
import sys
import time
import logging
import argparse
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

# Importar módulos de validación
try:
    from integration_test_suite import IntegrationTestSuite
    from validate_technologies import TechnologyValidator
    from validate_architecture import ArchitectureValidator
    from scalability_tests import ScalabilityTestSuite
    from fault_tolerance_tests import FaultToleranceTestSuite
except ImportError as e:
    print(f"Error importando módulos de validación: {e}")
    print("Asegúrese de ejecutar desde el directorio validation_system/")
    sys.exit(1)

class ValidationOrchestrator:
    """Orquestador principal de validación integral"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Inicializar orquestador
        
        Args:
            config_path: Ruta al archivo de configuración
        """
        self.config_path = config_path or "/workspace/validation_system/validation_config.json"
        self.config = self._load_config()
        self.results: Dict[str, Any] = {}
        self.start_time = None
        self.end_time = None
        
        # Configurar logging
        self._setup_logging()
        self.logger = logging.getLogger(__name__)

    def _load_config(self) -> Dict[str, Any]:
        """Cargar configuración de validación"""
        default_config = {
            "services": {
                "lp1_banco": {
                    "name": "Servicio Bancario",
                    "url": "http://localhost:8080",
                    "port": 8080,
                    "technology": "Java",
                    "database": "MySQL"
                },
                "lp2_reniec": {
                    "name": "Servicio RENIEC", 
                    "url": "http://localhost:8000",
                    "port": 8000,
                    "technology": "Python",
                    "database": "PostgreSQL"
                },
                "lp3_cliente": {
                    "name": "Aplicación Cliente",
                    "url": "http://localhost:3000",
                    "port": 3000,
                    "technology": "JavaScript"
                }
            },
            "validation_modules": {
                "integration_tests": {
                    "enabled": True,
                    "timeout": 300
                },
                "technology_validation": {
                    "enabled": True,
                    "timeout": 120
                },
                "architecture_validation": {
                    "enabled": True,
                    "timeout": 180
                },
                "scalability_tests": {
                    "enabled": True,
                    "timeout": 600
                },
                "fault_tolerance_tests": {
                    "enabled": True,
                    "timeout": 480
                }
            },
            "reports": {
                "html": True,
                "json": True,
                "directory": "/workspace/validation_system/reports"
            }
        }
        
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                # Merge con defaults
                self._merge_config(default_config, config)
                return default_config
            else:
                # Crear archivo de configuración por defecto
                os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
                with open(self.config_path, 'w') as f:
                    json.dump(default_config, f, indent=2)
                return default_config
        except Exception as e:
            print(f"Warning: Error cargando configuración: {e}. Usando configuración por defecto.")
            return default_config

    def _merge_config(self, default: Dict, user: Dict):
        """Recursivamente merge configuración user sobre default"""
        for key, value in user.items():
            if key in default and isinstance(default[key], dict) and isinstance(value, dict):
                self._merge_config(default[key], value)
            else:
                default[key] = value

    def _setup_logging(self):
        """Configurar sistema de logging"""
        log_dir = Path("/workspace/validation_system/logs")
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / f"validation_orchestrator_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
                logging.StreamHandler()
            ]
        )

    def _extract_urls(self) -> Dict[str, str]:
        """Extraer URLs de servicios de la configuración"""
        return {
            "lp1_url": self.config["services"]["lp1_banco"]["url"],
            "lp2_url": self.config["services"]["lp2_reniec"]["url"],
            "lp3_url": self.config["services"]["lp3_cliente"]["url"]
        }

    def _check_services_availability(self) -> Dict[str, bool]:
        """Verificar disponibilidad básica de servicios"""
        self.logger.info("=== Verificando disponibilidad de servicios ===")
        
        services = self.config["services"]
        availability = {}
        
        for service_key, service_config in services.items():
            url = service_config["url"]
            name = service_config["name"]
            
            try:
                import requests
                response = requests.get(f"{url}/api/health", timeout=5)
                available = response.status_code < 400
                availability[service_key] = available
                
                status = "✓" if available else "✗"
                self.logger.info(f"{status} {name} ({url}): {'Disponible' if available else 'No disponible'}")
                
            except Exception as e:
                availability[service_key] = False
                self.logger.warning(f"✗ {name} ({url}): Error - {str(e)}")
        
        return availability

    async def run_integration_tests(self) -> Dict[str, Any]:
        """Ejecutar suite de pruebas de integración"""
        self.logger.info("=== INICIANDO PRUEBAS DE INTEGRACIÓN ===")
        
        if not self.config["validation_modules"]["integration_tests"]["enabled"]:
            self.logger.info("Pruebas de integración deshabilitadas")
            return {"status": "SKIPPED", "message": "Module disabled"}
        
        try:
            urls = self._extract_urls()
            
            async with IntegrationTestSuite(urls) as suite:
                results = await suite.run_all_tests()
                suite.save_results()
                
                summary = suite.get_summary()
                self.logger.info(f"Pruebas de integración completadas: {summary['passed']}/{summary['total_tests']} pasaron")
                
                return {
                    "status": "COMPLETED",
                    "summary": summary,
                    "success": summary["passed"] == summary["total_tests"],
                    "message": f"{summary['passed']}/{summary['total_tests']} pruebas pasaron"
                }
                
        except Exception as e:
            self.logger.error(f"Error en pruebas de integración: {str(e)}")
            return {
                "status": "ERROR",
                "error": str(e),
                "success": False,
                "message": f"Error: {str(e)}"
            }

    def run_technology_validation(self) -> Dict[str, Any]:
        """Ejecutar validación de tecnologías heterogéneas"""
        self.logger.info("=== INICIANDO VALIDACIÓN DE TECNOLOGÍAS ===")
        
        if not self.config["validation_modules"]["technology_validation"]["enabled"]:
            self.logger.info("Validación de tecnologías deshabilitada")
            return {"status": "SKIPPED", "message": "Module disabled"}
        
        try:
            validator = TechnologyValidator()
            results = validator.run_all_validations()
            validator.save_results()
            
            summary = validator.get_summary()
            self.logger.info(f"Validación de tecnologías completada: {summary['passed']}/{summary['total_validations']} pasaron")
            
            return {
                "status": "COMPLETED",
                "summary": summary,
                "success": summary["passed"] == summary["total_validations"],
                "message": f"Heterogeneidad: {summary['heterogeneity_score']:.1f}%"
            }
            
        except Exception as e:
            self.logger.error(f"Error en validación de tecnologías: {str(e)}")
            return {
                "status": "ERROR",
                "error": str(e),
                "success": False,
                "message": f"Error: {str(e)}"
            }

    def run_architecture_validation(self) -> Dict[str, Any]:
        """Ejecutar validación de arquitectura distribuida"""
        self.logger.info("=== INICIANDO VALIDACIÓN DE ARQUITECTURA ===")
        
        if not self.config["validation_modules"]["architecture_validation"]["enabled"]:
            self.logger.info("Validación de arquitectura deshabilitada")
            return {"status": "SKIPPED", "message": "Module disabled"}
        
        try:
            validator = ArchitectureValidator()
            results = validator.run_all_validations()
            validator.save_results()
            
            summary = validator.get_summary()
            self.logger.info(f"Validación de arquitectura completada: {summary['passed']}/{summary['total_validations']} pasaron")
            
            return {
                "status": "COMPLETED",
                "summary": summary,
                "success": summary["passed"] == summary["total_validations"],
                "message": f"Arquitectura: {summary['architecture_score']:.1f}% puntuación"
            }
            
        except Exception as e:
            self.logger.error(f"Error en validación de arquitectura: {str(e)}")
            return {
                "status": "ERROR",
                "error": str(e),
                "success": False,
                "message": f"Error: {str(e)}"
            }

    async def run_scalability_tests(self) -> Dict[str, Any]:
        """Ejecutar pruebas de escalabilidad"""
        self.logger.info("=== INICIANDO PRUEBAS DE ESCALABILIDAD ===")
        
        if not self.config["validation_modules"]["scalability_tests"]["enabled"]:
            self.logger.info("Pruebas de escalabilidad deshabilitadas")
            return {"status": "SKIPPED", "message": "Module disabled"}
        
        try:
            urls = self._extract_urls()
            
            async with ScalabilityTestSuite(urls) as suite:
                results = await suite.run_all_tests()
                suite.save_results()
                
                summary = suite.get_summary()
                self.logger.info(f"Pruebas de escalabilidad completadas: {summary['passed']}/{summary['total_tests']} pasaron")
                
                return {
                    "status": "COMPLETED",
                    "summary": summary,
                    "success": summary["passed"] == summary["total_tests"],
                    "message": f"Escalabilidad: {summary['scalability_score']:.1f}% puntuación"
                }
                
        except Exception as e:
            self.logger.error(f"Error en pruebas de escalabilidad: {str(e)}")
            return {
                "status": "ERROR",
                "error": str(e),
                "success": False,
                "message": f"Error: {str(e)}"
            }

    async def run_fault_tolerance_tests(self) -> Dict[str, Any]:
        """Ejecutar pruebas de tolerancia a fallos"""
        self.logger.info("=== INICIANDO PRUEBAS DE TOLERANCIA A FALLOS ===")
        
        if not self.config["validation_modules"]["fault_tolerance_tests"]["enabled"]:
            self.logger.info("Pruebas de tolerancia a fallos deshabilitadas")
            return {"status": "SKIPPED", "message": "Module disabled"}
        
        try:
            urls = self._extract_urls()
            
            async with FaultToleranceTestSuite(urls) as suite:
                results = await suite.run_all_tests()
                suite.save_results()
                
                summary = suite.get_summary()
                self.logger.info(f"Pruebas de tolerancia completadas: {summary['passed']}/{summary['total_tests']} pasaron")
                
                return {
                    "status": "COMPLETED",
                    "summary": summary,
                    "success": summary["passed"] == summary["total_tests"],
                    "message": f"Resiliencia: {summary['resilience_metrics']['fault_tolerance_score']:.1f}% puntuación"
                }
                
        except Exception as e:
            self.logger.error(f"Error en pruebas de tolerancia a fallos: {str(e)}")
            return {
                "status": "ERROR",
                "error": str(e),
                "success": False,
                "message": f"Error: {str(e)}"
            }

    def _calculate_overall_score(self) -> float:
        """Calcular puntaje general del sistema"""
        total_score = 0
        modules_count = 0
        
        # Scores de cada módulo
        integration_score = self.results.get("integration_tests", {}).get("summary", {}).get("success_rate", 0)
        technology_score = self.results.get("technology_validation", {}).get("summary", {}).get("functionality_rate", 0)
        architecture_score = self.results.get("architecture_validation", {}).get("summary", {}).get("architecture_score", 0)
        scalability_score = self.results.get("scalability_tests", {}).get("summary", {}).get("scalability_score", 0)
        fault_tolerance_score = self.results.get("fault_tolerance_tests", {}).get("summary", {}).get("resilience_metrics", {}).get("fault_tolerance_score", 0)
        
        scores = {
            "Integration Tests": integration_score,
            "Technology Validation": technology_score,
            "Architecture Validation": architecture_score,
            "Scalability Tests": scalability_score,
            "Fault Tolerance": fault_tolerance_score
        }
        
        for module, score in scores.items():
            if score > 0:  # Solo contar módulos ejecutados
                total_score += score
                modules_count += 1
        
        return total_score / modules_count if modules_count > 0 else 0

    def _generate_consolidated_summary(self) -> Dict[str, Any]:
        """Generar resumen consolidado de todos los módulos"""
        return {
            "validation_overview": {
                "start_time": self.start_time.isoformat() if self.start_time else None,
                "end_time": self.end_time.isoformat() if self.end_time else None,
                "total_duration": (self.end_time - self.start_time).total_seconds() if self.start_time and self.end_time else 0,
                "modules_executed": len([r for r in self.results.values() if r.get("status") == "COMPLETED"]),
                "overall_success": all(r.get("success", False) for r in self.results.values() if r.get("status") == "COMPLETED")
            },
            "module_results": self.results,
            "overall_scores": {
                "integration_tests": self.results.get("integration_tests", {}).get("summary", {}).get("success_rate", 0),
                "technology_validation": self.results.get("technology_validation", {}).get("summary", {}).get("functionality_rate", 0),
                "architecture_validation": self.results.get("architecture_validation", {}).get("summary", {}).get("architecture_score", 0),
                "scalability_tests": self.results.get("scalability_tests", {}).get("summary", {}).get("scalability_score", 0),
                "fault_tolerance": self.results.get("fault_tolerance_tests", {}).get("summary", {}).get("resilience_metrics", {}).get("fault_tolerance_score", 0),
                "overall_system_score": self._calculate_overall_score()
            },
            "system_health": {
                "services_available": sum(1 for available in self.results.get("service_availability", {}).values() if available),
                "total_services": len(self.results.get("service_availability", {})),
                "health_percentage": (sum(1 for available in self.results.get("service_availability", {}).values() if available) / len(self.results.get("service_availability", {})) * 100) if self.results.get("service_availability") else 0
            }
        }

    async def run_complete_validation(self) -> Dict[str, Any]:
        """Ejecutar validación integral completa"""
        self.logger.info("=== INICIANDO VALIDACIÓN INTEGRAL COMPLETA ===")
        self.start_time = datetime.now()
        
        try:
            # Verificar disponibilidad de servicios
            self.results["service_availability"] = self._check_services_availability()
            
            # Ejecutar módulos de validación
            validation_tasks = [
                ("integration_tests", self.run_integration_tests()),
                ("technology_validation", self.run_technology_validation()),
                ("architecture_validation", self.run_architecture_validation()),
                ("scalability_tests", self.run_scalability_tests()),
                ("fault_tolerance_tests", self.run_fault_tolerance_tests())
            ]
            
            # Ejecutar tasks de forma concurrente donde sea apropiado
            for task_name, task in validation_tasks:
                try:
                    if task_name in ["integration_tests", "scalability_tests", "fault_tolerance_tests"]:
                        # Estos son async
                        result = await task
                    else:
                        # Estos son sync
                        result = task
                    
                    self.results[task_name] = result
                    
                    # Log resultado
                    if result.get("status") == "COMPLETED":
                        self.logger.info(f"✓ {task_name}: {result.get('message', 'OK')}")
                    elif result.get("status") == "SKIPPED":
                        self.logger.info(f"⊘ {task_name}: {result.get('message', 'Skipped')}")
                    else:
                        self.logger.error(f"✗ {task_name}: {result.get('message', 'Failed')}")
                        
                except Exception as e:
                    self.logger.error(f"✗ Error ejecutando {task_name}: {str(e)}")
                    self.results[task_name] = {
                        "status": "ERROR",
                        "error": str(e),
                        "success": False,
                        "message": f"Error: {str(e)}"
                    }
            
            self.end_time = datetime.now()
            
            # Generar resumen consolidado
            consolidated_summary = self._generate_consolidated_summary()
            
            # Guardar resumen consolidado
            reports_dir = Path(self.config["reports"]["directory"])
            reports_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            consolidated_report = reports_dir / f"consolidated_validation_report_{timestamp}.json"
            
            with open(consolidated_report, 'w') as f:
                json.dump(consolidated_summary, f, indent=2)
            
            self.logger.info(f"Reporte consolidado guardado: {consolidated_report}")
            
            return consolidated_summary
            
        except Exception as e:
            self.end_time = datetime.now()
            self.logger.error(f"Error en validación integral: {str(e)}")
            return {
                "status": "ERROR",
                "error": str(e),
                "overall_success": False
            }

    def print_final_report(self, summary: Dict[str, Any]):
        """Imprimir reporte final en consola"""
        print("\n" + "="*80)
        print("REPORTE FINAL - VALIDACIÓN INTEGRAL DEL SISTEMA DISTRIBUIDO")
        print("="*80)
        
        # Información general
        overview = summary.get("validation_overview", {})
        print(f"\n⏰ Duración total: {overview.get('total_duration', 0):.1f} segundos")
        print(f"📊 Módulos ejecutados: {overview.get('modules_executed', 0)}")
        
        # Estado general
        overall_success = overview.get("overall_success", False)
        status_icon = "✅" if overall_success else "❌"
        print(f"{status_icon} Estado general: {'ÉXITO' if overall_success else 'FALLOS DETECTADOS'}")
        
        # Puntajes por módulo
        print(f"\n📈 PUNTAJES POR MÓDULO:")
        scores = summary.get("overall_scores", {})
        for module, score in scores.items():
            if module != "overall_system_score":
                module_name = module.replace("_", " ").title()
                bar = "█" * int(score / 10) + "░" * (10 - int(score / 10))
                print(f"  {module_name:.<30} [{bar}] {score:.1f}%")
        
        # Puntaje general
        overall_score = scores.get("overall_system_score", 0)
        print(f"\n🎯 PUNTAJE GENERAL DEL SISTEMA:")
        overall_bar = "█" * int(overall_score / 10) + "░" * (10 - int(overall_score / 10))
        print(f"  {'Sistema General':.<30} [{overall_bar}] {overall_score:.1f}%")
        
        # Salud de servicios
        health = summary.get("system_health", {})
        services_ok = health.get("services_available", 0)
        services_total = health.get("total_services", 0)
        health_pct = health.get("health_percentage", 0)
        
        print(f"\n🏥 SALUD DE SERVICIOS:")
        print(f"  Servicios operativos: {services_ok}/{services_total} ({health_pct:.1f}%)")
        
        # Detalles por módulo
        print(f"\n📋 DETALLES POR MÓDULO:")
        module_results = summary.get("module_results", {})
        for module_name, result in module_results.items():
            status = result.get("status", "UNKNOWN")
            message = result.get("message", "Sin mensaje")
            
            if status == "COMPLETED":
                status_icon = "✅"
            elif status == "SKIPPED":
                status_icon = "⊘"
            else:
                status_icon = "❌"
            
            print(f"  {status_icon} {module_name}: {message}")
        
        print("\n" + "="*80)

async def main():
    """Función principal"""
    parser = argparse.ArgumentParser(description="Ejecutor de Validación Integral")
    parser.add_argument("--config", "-c", help="Ruta al archivo de configuración")
    parser.add_argument("--modules", "-m", nargs="+", 
                       choices=["integration", "technology", "architecture", "scalability", "fault_tolerance", "all"],
                       default=["all"], help="Módulos a ejecutar")
    
    args = parser.parse_args()
    
    # Crear orquestador
    orchestrator = ValidationOrchestrator(config_path=args.config)
    
    # Filtrar módulos si es necesario
    if args.modules != ["all"]:
        for module in orchestrator.config["validation_modules"].keys():
            module_key = module.replace("_", "")  # integration_tests -> integrationtests
            if module_key not in [m.replace("_", "") for m in args.modules]:
                orchestrator.config["validation_modules"][module]["enabled"] = False
    
    # Ejecutar validación completa
    try:
        summary = await orchestrator.run_complete_validation()
        
        # Mostrar reporte final
        orchestrator.print_final_report(summary)
        
        # Exit code basado en éxito general
        overall_success = summary.get("validation_overview", {}).get("overall_success", False)
        sys.exit(0 if overall_success else 1)
        
    except KeyboardInterrupt:
        print("\n⚠️ Validación interrumpida por el usuario")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Error fatal: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
