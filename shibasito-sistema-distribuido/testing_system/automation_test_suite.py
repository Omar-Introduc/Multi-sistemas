#!/usr/bin/env python3
"""
Suite de Automatización de Tests
================================

Este módulo proporciona una suite completa de automatización para
ejecutar todos los tests del sistema de testing de manera coordinada.

Características:
- Ejecución secuencial y paralela de tests
- Configuración centralizada
- Manejo de dependencias entre tests
- Orquestación de reportes
- Programación de tests automáticos
- Monitoreo de resultados

Autor: Sistema de Testing Automatizado
Fecha: 2025-10-30
"""

import os
import sys
import json
import time
import logging
import subprocess
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import schedule
import signal

# Agregar el directorio actual al path para imports
sys.path.append(str(Path(__file__).parent))

# Importar módulos del sistema de testing
try:
    from stress_test_lp1 import LP1StressTest
    from stress_test_lp2 import LP2RENIECStressTest
    from validate_data_integrity import DataIntegrityValidator
    from generate_test_reports import TestReportGenerator
    from persistence_tests import PersistenceTester
except ImportError as e:
    print(f"❌ Error importando módulos: {e}")
    print("Asegúrate de que todos los módulos estén en el mismo directorio")
    sys.exit(1)

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('automation_suite.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class TestConfiguration:
    """Configuración centralizada del sistema de testing"""
    
    def __init__(self, config_file: str = None):
        """
        Inicializar configuración
        
        Args:
            config_file: Archivo de configuración JSON
        """
        self.config = self._load_default_config()
        
        if config_file and os.path.exists(config_file):
            self._load_config_file(config_file)
        
        logger.info("✅ Configuración inicializada")

    def _load_default_config(self) -> Dict[str, Any]:
        """Cargar configuración por defecto"""
        return {
            'databases': {
                'lp1': {
                    'host': 'localhost',
                    'port': 3306,
                    'user': 'root',
                    'password': 'password',
                    'database': 'banco_lp1',
                    'charset': 'utf8mb4'
                },
                'lp2': {
                    'host': 'localhost',
                    'port': 3306,
                    'user': 'root',
                    'password': 'password',
                    'database': 'reniec_lp2',
                    'charset': 'utf8mb4'
                }
            },
            'test_settings': {
                'target_records': 1500,
                'concurrent_threads': 50,
                'timeout_seconds': 30,
                'retry_attempts': 3,
                'parallel_execution': True,
                'max_parallel_tests': 2
            },
            'output_settings': {
                'reports_dir': 'test_reports',
                'generate_html': True,
                'generate_json': True,
                'save_logs': True,
                'cleanup_old_reports': True,
                'reports_retention_days': 30
            },
            'notification_settings': {
                'email_notifications': False,
                'email_smtp_server': '',
                'email_port': 587,
                'email_username': '',
                'email_password': '',
                'email_recipients': [],
                'webhook_url': '',
                'slack_webhook': ''
            },
            'scheduling': {
                'enable_scheduling': False,
                'daily_tests_time': '02:00',
                'weekly_tests_day': 'sunday',
                'stress_tests_schedule': '0 2 * * *',  # Cron format
                'integrity_tests_schedule': '0 3 * * *',
                'persistence_tests_schedule': '0 4 * * 0'
            },
            'thresholds': {
                'success_rate_minimum': 95.0,
                'response_time_maximum': 2.0,
                'error_rate_maximum': 5.0,
                'memory_usage_maximum': 80.0,
                'cpu_usage_maximum': 75.0
            }
        }

    def _load_config_file(self, config_file: str):
        """Cargar configuración desde archivo"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
            
            # Actualizar configuración con valores del usuario
            self._update_config_recursive(self.config, user_config)
            logger.info(f"📁 Configuración cargada desde: {config_file}")
            
        except Exception as e:
            logger.error(f"❌ Error cargando configuración: {str(e)}")
            raise

    def _update_config_recursive(self, base: Dict, update: Dict):
        """Actualizar configuración recursivamente"""
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._update_config_recursive(base[key], value)
            else:
                base[key] = value

    def get(self, key: str, default=None):
        """Obtener valor de configuración usando notación de puntos"""
        keys = key.split('.')
        value = self.config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default

    def save(self, config_file: str):
        """Guardar configuración actual a archivo"""
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            logger.info(f"💾 Configuración guardada en: {config_file}")
        except Exception as e:
            logger.error(f"❌ Error guardando configuración: {str(e)}")
            raise


class AutomationTestSuite:
    """Suite principal de automatización de tests"""
    
    def __init__(self, config: TestConfiguration):
        """
        Inicializar suite de automatización
        
        Args:
            config: Configuración del sistema
        """
        self.config = config
        self.test_results = {}
        self.test_history = []
        self.is_running = False
        self.stop_flag = threading.Event()
        
        # Inicializar componentes
        self.report_generator = TestReportGenerator(
            reports_dir=self.config.get('output_settings.reports_dir')
        )
        
        # Registrar manejador de señales
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        logger.info("✅ Suite de automatización inicializada")

    def _signal_handler(self, signum, frame):
        """Manejar señales de interrupción"""
        logger.info(f"🛑 Señal {signum} recibida. Iniciando shutdown...")
        self.stop()

    def run_stress_tests(self) -> Dict[str, Any]:
        """Ejecutar tests de stress para LP1 y LP2"""
        logger.info("🚀 Iniciando tests de stress")
        
        results = {
            'start_time': time.time(),
            'lp1_result': None,
            'lp2_result': None,
            'overall_success': False,
            'errors': []
        }
        
        try:
            # Configuraciones de base de datos
            lp1_config = self.config.get('databases.lp1')
            lp2_config = self.config.get('databases.lp2')
            
            if self.config.get('test_settings.parallel_execution'):
                # Ejecución paralela
                results = self._run_stress_tests_parallel(lp1_config, lp2_config)
            else:
                # Ejecución secuencial
                results = self._run_stress_tests_sequential(lp1_config, lp2_config)
            
            results['end_time'] = time.time()
            results['duration'] = results['end_time'] - results['start_time']
            
            # Evaluar resultados generales
            results['overall_success'] = self._evaluate_stress_test_results(results)
            
            self.test_results['stress_tests'] = results
            logger.info("✅ Tests de stress completados")
            
        except Exception as e:
            error_msg = f"Error ejecutando tests de stress: {str(e)}"
            logger.error(error_msg)
            results['errors'].append(error_msg)
            results['overall_success'] = False
        
        return results

    def _run_stress_tests_parallel(self, lp1_config: Dict, lp2_config: Dict) -> Dict[str, Any]:
        """Ejecutar tests de stress en paralelo"""
        results = {
            'start_time': time.time(),
            'lp1_result': None,
            'lp2_result': None,
            'overall_success': False,
            'errors': [],
            'execution_mode': 'parallel'
        }
        
        def run_lp1_test():
            try:
                test = LP1StressTest(lp1_config)
                return test.run_stress_test()
            except Exception as e:
                return {'error': str(e), 'overall_success': False}
        
        def run_lp2_test():
            try:
                test = LP2RENIECStressTest(lp2_config)
                return test.run_stress_test()
            except Exception as e:
                return {'error': str(e), 'overall_success': False}
        
        # Ejecutar en paralelo
        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = {
                executor.submit(run_lp1_test): 'lp1',
                executor.submit(run_lp2_test): 'lp2'
            }
            
            for future in as_completed(futures):
                test_name = futures[future]
                try:
                    result = future.result(timeout=self.config.get('test_settings.timeout_seconds') * 60)
                    results[f'{test_name}_result'] = result
                    logger.info(f"✅ Test {test_name.upper()} completado")
                except Exception as e:
                    error_msg = f"Error en test {test_name}: {str(e)}"
                    logger.error(error_msg)
                    results['errors'].append(error_msg)
        
        return results

    def _run_stress_tests_sequential(self, lp1_config: Dict, lp2_config: Dict) -> Dict[str, Any]:
        """Ejecutar tests de stress secuencialmente"""
        results = {
            'start_time': time.time(),
            'lp1_result': None,
            'lp2_result': None,
            'overall_success': False,
            'errors': [],
            'execution_mode': 'sequential'
        }
        
        # Ejecutar LP1 primero
        try:
            logger.info("🔄 Ejecutando stress test LP1...")
            test = LP1StressTest(lp1_config)
            results['lp1_result'] = test.run_stress_test()
            logger.info("✅ Stress test LP1 completado")
        except Exception as e:
            error_msg = f"Error en stress test LP1: {str(e)}"
            logger.error(error_msg)
            results['errors'].append(error_msg)
        
        # Ejecutar LP2 segundo
        try:
            logger.info("🔄 Ejecutando stress test LP2...")
            test = LP2RENIECStressTest(lp2_config)
            results['lp2_result'] = test.run_stress_test()
            logger.info("✅ Stress test LP2 completado")
        except Exception as e:
            error_msg = f"Error en stress test LP2: {str(e)}"
            logger.error(error_msg)
            results['errors'].append(error_msg)
        
        return results

    def _evaluate_stress_test_results(self, results: Dict[str, Any]) -> bool:
        """Evaluar resultados de tests de stress"""
        success_count = 0
        total_tests = 0
        
        # Verificar LP1
        if results['lp1_result']:
            total_tests += 1
            lp1_success = results['lp1_result'].get('performance_metrics', {}).get('success_rate', 0) >= 90
            if lp1_success:
                success_count += 1
        
        # Verificar LP2
        if results['lp2_result']:
            total_tests += 1
            lp2_success = results['lp2_result'].get('performance_metrics', {}).get('success_rate', 0) >= 90
            if lp2_success:
                success_count += 1
        
        # Considerar exitoso si al menos 1 de 2 tests es exitoso
        return success_count >= max(1, total_tests // 2)

    def run_integrity_validation(self) -> Dict[str, Any]:
        """Ejecutar validación de integridad de datos"""
        logger.info("🔍 Iniciando validación de integridad")
        
        results = {
            'start_time': time.time(),
            'validation_result': None,
            'overall_success': False,
            'errors': []
        }
        
        try:
            # Configuraciones de base de datos
            lp1_config = self.config.get('databases.lp1')
            lp2_config = self.config.get('databases.lp2')
            
            # Crear validador
            validator = DataIntegrityValidator(lp1_config, lp2_config)
            
            # Ejecutar validación
            results['validation_result'] = validator.run_complete_validation()
            
            # Evaluar resultado
            validation_summary = results['validation_result']['validation_summary']
            results['overall_success'] = validation_summary['overall_status'] == 'PASSED'
            
            results['end_time'] = time.time()
            results['duration'] = results['end_time'] - results['start_time']
            
            self.test_results['integrity_validation'] = results
            logger.info("✅ Validación de integridad completada")
            
        except Exception as e:
            error_msg = f"Error ejecutando validación de integridad: {str(e)}"
            logger.error(error_msg)
            results['errors'].append(error_msg)
            results['overall_success'] = False
        
        return results

    def run_persistence_tests(self) -> Dict[str, Any]:
        """Ejecutar tests de persistencia"""
        logger.info("💾 Iniciando tests de persistencia")
        
        results = {
            'start_time': time.time(),
            'persistence_result': None,
            'overall_success': False,
            'errors': []
        }
        
        try:
            # Configuración de base de datos
            db_config = self.config.get('databases.lp1')  # Usar LP1 como ejemplo
            
            # Crear tester de persistencia
            tester = PersistenceTester(db_config)
            
            # Ejecutar tests
            results['persistence_result'] = tester.run_persistence_tests()
            
            # Evaluar resultado
            results['overall_success'] = results['persistence_result'].get('overall_status') == 'PASSED'
            
            results['end_time'] = time.time()
            results['duration'] = results['end_time'] - results['start_time']
            
            self.test_results['persistence_tests'] = results
            logger.info("✅ Tests de persistencia completados")
            
        except Exception as e:
            error_msg = f"Error ejecutando tests de persistencia: {str(e)}"
            logger.error(error_msg)
            results['errors'].append(error_msg)
            results['overall_success'] = False
        
        return results

    def run_comprehensive_test_suite(self) -> Dict[str, Any]:
        """Ejecutar suite completa de tests"""
        logger.info("🚀 Iniciando suite completa de testing")
        
        suite_results = {
            'start_time': time.time(),
            'test_suite_version': '1.0.0',
            'tests': {},
            'overall_success': False,
            'execution_summary': {},
            'final_report': None
        }
        
        try:
            # 1. Ejecutar tests de stress
            logger.info("=" * 60)
            logger.info("FASE 1: TESTS DE STRESS")
            logger.info("=" * 60)
            stress_results = self.run_stress_tests()
            suite_results['tests']['stress_tests'] = stress_results
            
            # 2. Ejecutar validación de integridad
            logger.info("=" * 60)
            logger.info("FASE 2: VALIDACIÓN DE INTEGRIDAD")
            logger.info("=" * 60)
            integrity_results = self.run_integrity_validation()
            suite_results['tests']['integrity_validation'] = integrity_results
            
            # 3. Ejecutar tests de persistencia
            logger.info("=" * 60)
            logger.info("FASE 3: TESTS DE PERSISTENCIA")
            logger.info("=" * 60)
            persistence_results = self.run_persistence_tests()
            suite_results['tests']['persistence_tests'] = persistence_results
            
            # 4. Generar reporte final
            logger.info("=" * 60)
            logger.info("FASE 4: GENERACIÓN DE REPORTES")
            logger.info("=" * 60)
            final_report = self._generate_comprehensive_suite_report(suite_results)
            suite_results['final_report'] = final_report
            
            # 5. Evaluar resultado general
            suite_results['overall_success'] = self._evaluate_suite_results(suite_results)
            
            suite_results['end_time'] = time.time()
            suite_results['total_duration'] = suite_results['end_time'] - suite_results['start_time']
            
            # Guardar historial
            self._save_test_history(suite_results)
            
            logger.info("=" * 60)
            logger.info("✅ SUITE COMPLETA DE TESTING FINALIZADA")
            logger.info("=" * 60)
            
        except Exception as e:
            error_msg = f"Error ejecutando suite completa: {str(e)}"
            logger.error(error_msg)
            suite_results['errors'] = [error_msg]
            suite_results['overall_success'] = False
        
        return suite_results

    def _generate_comprehensive_suite_report(self, suite_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generar reporte comprensivo de la suite"""
        # Compilar resultados de todos los tests
        all_results = {}
        
        for test_name, test_result in suite_results['tests'].items():
            if test_result and 'overall_success' in test_result:
                all_results[test_name] = test_result
        
        # Si no hay resultados válidos, crear reporte mínimo
        if not all_results:
            return {
                'error': 'No hay resultados de tests disponibles',
                'overall_status': 'FAILED'
            }
        
        # Crear estructura de datos para el reporte
        combined_results = {
            'test_info': {
                'test_name': 'Suite Completa de Testing',
                'timestamp': datetime.now().isoformat(),
                'suite_version': suite_results.get('test_suite_version', '1.0.0'),
                'total_duration': suite_results.get('total_duration', 0)
            },
            'performance_metrics': self._aggregate_performance_metrics(all_results),
            'execution_summary': self._create_execution_summary(all_results),
            'test_phases': self._organize_test_phases(all_results),
            'recommendations': self._generate_suite_recommendations(all_results),
            'compliance_status': self._assess_suite_compliance(all_results),
            'overall_status': 'PASSED' if suite_results['overall_success'] else 'FAILED'
        }
        
        # Generar archivos de reporte
        report_files = self.report_generator.generate_comprehensive_report(combined_results)
        combined_results['report_files'] = report_files
        
        return combined_results

    def _aggregate_performance_metrics(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Agregar métricas de rendimiento de todos los tests"""
        metrics = {
            'total_duration': 0,
            'total_operations': 0,
            'successful_operations': 0,
            'failed_operations': 0,
            'avg_response_time': 0,
            'operations_per_second': 0,
            'success_rate': 0
        }
        
        response_times = []
        operation_counts = []
        
        for test_name, result in results.items():
            if 'performance_metrics' in result:
                test_metrics = result['performance_metrics']
                
                metrics['total_duration'] += test_metrics.get('total_duration', 0)
                metrics['total_operations'] += test_metrics.get('total_operations', 0)
                metrics['successful_operations'] += test_metrics.get('successful_operations', 0)
                metrics['failed_operations'] += test_metrics.get('failed_operations', 0)
                
                if test_metrics.get('avg_response_time'):
                    response_times.append(test_metrics['avg_response_time'])
                
                if test_metrics.get('operations_per_second'):
                    operation_counts.append(test_metrics['operations_per_second'])
        
        # Calcular promedios
        if response_times:
            metrics['avg_response_time'] = sum(response_times) / len(response_times)
        
        if operation_counts:
            metrics['operations_per_second'] = sum(operation_counts) / len(operation_counts)
        
        if metrics['total_operations'] > 0:
            metrics['success_rate'] = (metrics['successful_operations'] / metrics['total_operations']) * 100
        
        return metrics

    def _create_execution_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Crear resumen de ejecución"""
        summary = {
            'total_tests': len(results),
            'passed_tests': 0,
            'failed_tests': 0,
            'test_details': []
        }
        
        for test_name, result in results.items():
            test_detail = {
                'test_name': test_name,
                'status': 'PASSED' if result.get('overall_success', False) else 'FAILED',
                'duration': result.get('duration', 0),
                'errors_count': len(result.get('errors', []))
            }
            summary['test_details'].append(test_detail)
            
            if result.get('overall_success', False):
                summary['passed_tests'] += 1
            else:
                summary['failed_tests'] += 1
        
        return summary

    def _organize_test_phases(self, results: Dict[str, Any]) -> Dict[str, Dict]:
        """Organizar tests por fases"""
        phases = {}
        
        for test_name, result in results.items():
            phase = 'unknown'
            if 'stress' in test_name:
                phase = 'stress_testing'
            elif 'integrity' in test_name:
                phase = 'data_validation'
            elif 'persistence' in test_name:
                phase = 'persistence_testing'
            
            if phase not in phases:
                phases[phase] = {
                    'tests': [],
                    'overall_status': 'PASSED',
                    'total_duration': 0
                }
            
            phases[phase]['tests'].append({
                'name': test_name,
                'status': 'PASSED' if result.get('overall_success', False) else 'FAILED',
                'duration': result.get('duration', 0)
            })
            
            phases[phase]['total_duration'] += result.get('duration', 0)
            
            # Actualizar estado de la fase
            if not result.get('overall_success', False):
                phases[phase]['overall_status'] = 'FAILED'
        
        return phases

    def _generate_suite_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Generar recomendaciones basadas en toda la suite"""
        recommendations = []
        
        # Analizar patrones de errores
        all_errors = []
        for result in results.values():
            all_errors.extend(result.get('errors', []))
        
        if all_errors:
            error_counts = {}
            for error in all_errors:
                key = error.split(':')[0] if ':' in error else error
                error_counts[key] = error_counts.get(key, 0) + 1
            
            # Recomendar basado en errores más frecuentes
            for error_type, count in sorted(error_counts.items(), key=lambda x: x[1], reverse=True):
                if count > 1:
                    recommendations.append(f"🔧 Revisar errores frecuentes: {error_type} ({count} occurrences)")
        
        # Analizar rendimiento general
        avg_success_rate = 0
        test_count = 0
        
        for result in results.values():
            if 'performance_metrics' in result:
                test_count += 1
                avg_success_rate += result['performance_metrics'].get('success_rate', 0)
        
        if test_count > 0:
            avg_success_rate /= test_count
            
            if avg_success_rate < 95:
                recommendations.append("⚠️  Tasa de éxito promedio por debajo del umbral recomendado (95%)")
        
        # Recomendaciones específicas basadas en tipos de test
        if 'stress_tests' in results and not results['stress_tests'].get('overall_success', False):
            recommendations.append("⚡ Optimizar configuración de concurrencia y timeouts")
        
        if 'integrity_validation' in results and not results['integrity_validation'].get('overall_success', False):
            recommendations.append("🔍 Revisar integridad de datos y constraints de base de datos")
        
        if 'persistence_tests' in results and not results['persistence_tests'].get('overall_success', False):
            recommendations.append("💾 Verificar configuración de persistencia y manejo de transacciones")
        
        # Recomendación general
        if not recommendations:
            recommendations.append("✅ Suite de testing funcionando dentro de parámetros normales")
        
        return recommendations

    def _assess_suite_compliance(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluar cumplimiento normativo de toda la suite"""
        compliance = {
            'overall_compliance': 'COMPLIANT',
            'test_coverage': 0,
            'quality_standards': 'MET',
            'documentation_complete': True,
            'identified_issues': []
        }
        
        # Evaluar cobertura de tests
        required_tests = ['stress_tests', 'integrity_validation', 'persistence_tests']
        completed_tests = len([test for test in required_tests if test in results])
        compliance['test_coverage'] = (completed_tests / len(required_tests)) * 100
        
        # Evaluar calidad
        quality_issues = 0
        for test_name, result in results.items():
            if not result.get('overall_success', False):
                quality_issues += 1
        
        if quality_issues > 0:
            compliance['quality_standards'] = 'PARTIAL' if quality_issues <= 1 else 'NOT_MET'
            compliance['identified_issues'].append(f"{quality_issues} test(s) fallaron")
        
        # Determinar cumplimiento general
        if compliance['test_coverage'] < 100:
            compliance['overall_compliance'] = 'PARTIAL'
        elif compliance['quality_standards'] != 'MET':
            compliance['overall_compliance'] = 'PARTIAL'
        
        return compliance

    def _evaluate_suite_results(self, suite_results: Dict[str, Any]) -> bool:
        """Evaluar resultados generales de la suite"""
        test_results = suite_results.get('tests', {})
        
        # Al menos 2 de 3 tests principales deben ser exitosos
        successful_tests = sum(1 for result in test_results.values() if result.get('overall_success', False))
        total_tests = len(test_results)
        
        return successful_tests >= max(1, (total_tests * 2) // 3)

    def _save_test_history(self, suite_results: Dict[str, Any]):
        """Guardar historial de tests"""
        try:
            history_file = Path(self.config.get('output_settings.reports_dir')) / 'test_history.json'
            
            # Cargar historial existente
            if history_file.exists():
                with open(history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
            else:
                history = []
            
            # Agregar nuevo resultado
            history_entry = {
                'timestamp': datetime.now().isoformat(),
                'suite_version': suite_results.get('test_suite_version', '1.0.0'),
                'overall_success': suite_results.get('overall_success', False),
                'total_duration': suite_results.get('total_duration', 0),
                'test_summary': {
                    'stress_tests': suite_results.get('tests', {}).get('stress_tests', {}).get('overall_success', False),
                    'integrity_validation': suite_results.get('tests', {}).get('integrity_validation', {}).get('overall_success', False),
                    'persistence_tests': suite_results.get('tests', {}).get('persistence_tests', {}).get('overall_success', False)
                }
            }
            
            history.append(history_entry)
            
            # Mantener solo los últimos 100 registros
            if len(history) > 100:
                history = history[-100:]
            
            # Guardar
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, indent=2, ensure_ascii=False)
            
            logger.info(f"📚 Historial guardado en: {history_file}")
            
        except Exception as e:
            logger.error(f"❌ Error guardando historial: {str(e)}")

    def cleanup_old_reports(self):
        """Limpiar reportes antiguos"""
        try:
            retention_days = self.config.get('output_settings.reports_retention_days', 30)
            reports_dir = Path(self.config.get('output_settings.reports_dir'))
            
            cutoff_date = datetime.now() - timedelta(days=retention_days)
            deleted_count = 0
            
            for file_path in reports_dir.glob('*'):
                if file_path.is_file():
                    file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                    if file_time < cutoff_date:
                        file_path.unlink()
                        deleted_count += 1
            
            if deleted_count > 0:
                logger.info(f"🧹 Eliminados {deleted_count} archivos antiguos")
            
        except Exception as e:
            logger.error(f"❌ Error limpiando reportes: {str(e)}")

    def setup_scheduled_tests(self):
        """Configurar tests programados"""
        if not self.config.get('scheduling.enable_scheduling', False):
            logger.info("⏰ Programación de tests deshabilitada")
            return
        
        logger.info("⏰ Configurando tests programados")
        
        # Tests diarios
        daily_time = self.config.get('scheduling.daily_tests_time', '02:00')
        schedule.every().day.at(daily_time).do(self.run_comprehensive_test_suite)
        
        # Tests específicos por tipo
        stress_schedule = self.config.get('scheduling.stress_tests_schedule')
        if stress_schedule:
            # Nota: schedule no soporta cron directamente, se puede implementar con APScheduler
            logger.info(f"📅 Stress tests programados: {stress_schedule}")
        
        logger.info("✅ Tests programados configurados")

    def start_scheduled_runner(self):
        """Iniciar ejecutor de tests programados"""
        if not self.config.get('scheduling.enable_scheduling', False):
            logger.info("⏰ Ejecutor de programación deshabilitado")
            return
        
        logger.info("🚀 Iniciando ejecutor de tests programados")
        self.is_running = True
        
        try:
            while self.is_running and not self.stop_flag.is_set():
                schedule.run_pending()
                time.sleep(60)  # Verificar cada minuto
        except KeyboardInterrupt:
            logger.info("🛑 Interrupción recibida")
        finally:
            self.is_running = False
            logger.info("⏹️  Ejecutor de programación detenido")

    def stop(self):
        """Detener ejecución"""
        logger.info("🛑 Deteniendo suite de automatización...")
        self.is_running = False
        self.stop_flag.set()

    def get_test_status(self) -> Dict[str, Any]:
        """Obtener estado actual de los tests"""
        return {
            'is_running': self.is_running,
            'test_results_count': len(self.test_results),
            'last_test_time': datetime.now().isoformat(),
            'configuration': {
                'parallel_execution': self.config.get('test_settings.parallel_execution'),
                'target_records': self.config.get('test_settings.target_records'),
                'concurrent_threads': self.config.get('test_settings.concurrent_threads')
            }
        }


def create_sample_config():
    """Crear archivo de configuración de ejemplo"""
    config = TestConfiguration()
    config.save('automation_config.json')
    print("📁 Archivo de configuración creado: automation_config.json")


def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Suite de Automatización de Testing')
    parser.add_argument('--config', '-c', help='Archivo de configuración')
    parser.add_argument('--mode', '-m', choices=['stress', 'integrity', 'persistence', 'full', 'scheduled'],
                       default='full', help='Modo de ejecución')
    parser.add_argument('--parallel', '-p', action='store_true', help='Ejecución paralela')
    parser.add_argument('--create-config', action='store_true', help='Crear archivo de configuración')
    
    args = parser.parse_args()
    
    if args.create_config:
        create_sample_config()
        return
    
    try:
        # Crear configuración
        config = TestConfiguration(args.config)
        
        # Aplicar configuración de línea de comandos
        if args.parallel:
            config.config['test_settings']['parallel_execution'] = True
        
        # Crear suite
        suite = AutomationTestSuite(config)
        
        # Ejecutar según modo
        if args.mode == 'stress':
            results = suite.run_stress_tests()
        elif args.mode == 'integrity':
            results = suite.run_integrity_validation()
        elif args.mode == 'persistence':
            results = suite.run_persistence_tests()
        elif args.mode == 'scheduled':
            suite.setup_scheduled_tests()
            suite.start_scheduled_runner()
            return
        else:  # full
            results = suite.run_comprehensive_test_suite()
        
        # Mostrar resumen final
        print("\n" + "="*70)
        print("📊 RESUMEN FINAL DE LA SUITE DE TESTING")
        print("="*70)
        
        if isinstance(results, dict):
            if 'overall_success' in results:
                print(f"✅ Estado General: {'ÉXITO' if results['overall_success'] else 'FALLO'}")
                print(f"⏱️  Duración Total: {results.get('total_duration', 0):.1f} segundos")
            
            if 'tests' in results:
                print("\n🔍 Resultados por Test:")
                for test_name, test_result in results['tests'].items():
                    status = "✅ ÉXITO" if test_result.get('overall_success', False) else "❌ FALLO"
                    duration = test_result.get('duration', 0)
                    print(f"  • {test_name}: {status} ({duration:.1f}s)")
            
            if 'final_report' in results and results['final_report']:
                report_files = results['final_report'].get('report_files', {})
                if report_files:
                    print(f"\n📁 Reportes Generados:")
                    for file_type, file_path in report_files.items():
                        print(f"  • {file_type}: {file_path}")
        
        print("="*70)
        
        # Limpiar reportes antiguos si está habilitado
        if config.get('output_settings.cleanup_old_reports', True):
            suite.cleanup_old_reports()
        
    except Exception as e:
        logger.error(f"❌ Error en suite de automatización: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
