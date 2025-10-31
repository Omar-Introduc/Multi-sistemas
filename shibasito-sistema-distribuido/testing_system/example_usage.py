#!/usr/bin/env python3
"""
Ejemplo de Uso del Sistema de Stress Testing
============================================

Este archivo demuestra cómo usar el sistema completo de stress testing
de manera práctica, incluyendo configuración, ejecución y análisis de resultados.

Ejemplos incluidos:
- Configuración básica y avanzada
- Ejecución de tests individuales
- Ejecución de suite completa
- Análisis de resultados
- Interpretación de métricas
- Solución de problemas comunes

Autor: Sistema de Testing Automatizado
Fecha: 2025-10-30
"""

import sys
import json
import time
from pathlib import Path
from typing import Dict, Any, List

# Agregar directorio actual al path
sys.path.append(str(Path(__file__).parent))

def create_example_config():
    """Crear archivo de configuración de ejemplo"""
    config = {
        "databases": {
            "lp1": {
                "host": "localhost",
                "port": 3306,
                "user": "root",
                "password": "password",
                "database": "banco_lp1",
                "charset": "utf8mb4"
            },
            "lp2": {
                "host": "localhost",
                "port": 3306,
                "user": "root",
                "password": "password",
                "database": "reniec_lp2", 
                "charset": "utf8mb4"
            }
        },
        "test_settings": {
            "target_records": 1500,
            "concurrent_threads": 50,
            "timeout_seconds": 30,
            "retry_attempts": 3,
            "parallel_execution": True,
            "max_parallel_tests": 2
        },
        "output_settings": {
            "reports_dir": "test_reports",
            "generate_html": True,
            "generate_json": True,
            "save_logs": True,
            "cleanup_old_reports": True,
            "reports_retention_days": 30
        },
        "thresholds": {
            "success_rate_minimum": 95.0,
            "response_time_maximum": 2.0,
            "error_rate_maximum": 5.0,
            "memory_usage_maximum": 80.0,
            "cpu_usage_maximum": 75.0
        },
        "scheduling": {
            "enable_scheduling": False,
            "daily_tests_time": "02:00",
            "weekly_tests_day": "sunday"
        }
    }
    
    with open('example_automation_config.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print("✅ Archivo de configuración creado: example_automation_config.json")

def example_1_basic_usage():
    """Ejemplo 1: Uso básico - Ejecutar tests individuales"""
    print("\n" + "="*60)
    print("📋 EJEMPLO 1: USO BÁSICO - TESTS INDIVIDUALES")
    print("="*60)
    
    try:
        # Importar módulos
        from stress_test_lp1 import LP1StressTest
        from stress_test_lp2 import LP2RENIECStressTest
        from validate_data_integrity import DataIntegrityValidator
        from persistence_tests import PersistenceTester
        
        print("\n1️⃣  Configurar conexiones a bases de datos...")
        
        # Configuraciones básicas
        lp1_config = {
            'host': 'localhost',
            'port': 3306,
            'user': 'root',
            'password': 'password',
            'database': 'banco_lp1',
            'charset': 'utf8mb4'
        }
        
        lp2_config = {
            'host': 'localhost',
            'port': 3306,
            'user': 'root',
            'password': 'password',
            'database': 'reniec_lp2',
            'charset': 'utf8mb4'
        }
        
        print("✅ Configuraciones preparadas")
        
        print("\n2️⃣  Ejecutar Stress Test LP1 (Sistema Bancario)...")
        
        # Crear instancia de test LP1
        lp1_test = LP1StressTest(lp1_config)
        
        # Ejecutar test (comentado para evitar ejecución real)
        # lp1_results = lp1_test.run_stress_test()
        print("   📊 Test LP1 preparado - En producción ejecutaría test de estrés")
        print("   🎯 Objetivo: 1500 clientes con 50 hilos concurrentes")
        
        print("\n3️⃣  Ejecutar Stress Test LP2 (Sistema RENIEC)...")
        
        # Crear instancia de test LP2
        lp2_test = LP2RENIECStressTest(lp2_config)
        
        # Ejecutar test (comentado para evitar ejecución real)
        # lp2_results = lp2_test.run_stress_test()
        print("   📊 Test LP2 preparado - En producción ejecutaría test de estrés")
        print("   🎯 Objetivo: 1500 ciudadanos con validaciones de DNI")
        
        print("\n4️⃣  Ejecutar Validación de Integridad...")
        
        # Crear validador
        validator = DataIntegrityValidator(lp1_config, lp2_config)
        
        # Ejecutar validación (comentado para evitar ejecución real)
        # integrity_results = validator.run_complete_validation()
        print("   🔍 Validador preparado - En producción validaría consistencia BD1 vs BD2")
        print("   🎯 Verificación: Integridad referencial y calidad de datos")
        
        print("\n5️⃣  Ejecutar Tests de Persistencia...")
        
        # Crear tester de persistencia
        persistence_tester = PersistenceTester(lp1_config)
        
        # Ejecutar tests (comentado para evitar ejecución real)
        # persistence_results = persistence_tester.run_persistence_tests()
        print("   💾 Tester de persistencia preparado - En producción validaría backups")
        print("   🎯 Verificación: Recuperación ante fallos y transacciones ACID")
        
        print("\n✅ Ejemplo 1 completado - Todos los componentes preparados")
        
    except ImportError as e:
        print(f"❌ Error de importación: {e}")
        print("💡 Asegúrate de que todos los módulos estén disponibles")

def example_2_automation_suite():
    """Ejemplo 2: Uso de la suite de automatización"""
    print("\n" + "="*60)
    print("🤖 EJEMPLO 2: SUITE DE AUTOMATIZACIÓN")
    print("="*60)
    
    try:
        from automation_test_suite import AutomationTestSuite, TestConfiguration
        
        print("\n1️⃣  Crear configuración...")
        
        # Crear configuración
        config = TestConfiguration()
        print("✅ Configuración creada con valores por defecto")
        
        # Aplicar configuración personalizada
        custom_config = {
            'test_settings': {
                'target_records': 500,  # Menos registros para ejemplo
                'concurrent_threads': 20,  # Menos hilos para ejemplo
                'timeout_seconds': 60,
                'parallel_execution': True
            },
            'thresholds': {
                'success_rate_minimum': 90.0,  # Umbral más bajo para ejemplo
                'response_time_maximum': 5.0
            }
        }
        
        # Actualizar configuración
        config._update_config_recursive(config.config, custom_config)
        print("✅ Configuración personalizada aplicada")
        
        print("\n2️⃣  Crear suite de automatización...")
        
        # Crear suite
        suite = AutomationTestSuite(config)
        print("✅ Suite de automatización creada")
        
        print("\n3️⃣  Ejecutar tests de estrés únicamente...")
        
        # Ejecutar solo tests de estrés (comentado para evitar ejecución real)
        # stress_results = suite.run_stress_tests()
        print("   ⚡ Tests de estrés preparados - LP1 + LP2")
        print("   🎯 Configuración: 500 registros, 20 hilos")
        
        print("\n4️⃣  Ejecutar suite completa...")
        
        # Ejecutar suite completa (comentado para evitar ejecución real)
        # full_results = suite.run_comprehensive_test_suite()
        print("   🚀 Suite completa preparada - Todos los tests")
        print("   📊 Incluiría: Stress + Integridad + Persistencia + Reportes")
        
        print("\n5️⃣  Verificar estado del sistema...")
        
        # Obtener estado
        status = suite.get_test_status()
        print("   📈 Estado del sistema:")
        print(f"   • Ejecución paralela: {status['configuration']['parallel_execution']}")
        print(f"   • Registros objetivo: {status['configuration']['target_records']}")
        print(f"   • Hilos concurrentes: {status['configuration']['concurrent_threads']}")
        
        print("\n✅ Ejemplo 2 completado - Suite de automatización lista")
        
    except ImportError as e:
        print(f"❌ Error de importación: {e}")
        print("💡 Verifica que automation_test_suite.py esté disponible")

def example_3_report_generation():
    """Ejemplo 3: Generación y análisis de reportes"""
    print("\n" + "="*60)
    print("📊 EJEMPLO 3: GENERACIÓN DE REPORTES")
    print("="*60)
    
    try:
        from generate_test_reports import TestReportGenerator
        
        print("\n1️⃣  Crear generador de reportes...")
        
        # Crear generador
        generator = TestReportGenerator(reports_dir="example_reports")
        print("✅ Generador de reportes creado")
        
        print("\n2️⃣  Simular datos de resultados...")
        
        # Datos de ejemplo simulados
        sample_results = {
            'test_info': {
                'test_name': 'Ejemplo de Stress Test',
                'timestamp': '2025-10-30T10:00:00',
                'target_records': 1500,
                'concurrent_threads': 50
            },
            'performance_metrics': {
                'total_duration': 125.5,
                'total_operations': 15750,
                'successful_operations': 15200,
                'failed_operations': 550,
                'success_rate': 96.5,
                'avg_response_time': 0.45,
                'operations_per_second': 130.6
            },
            'data_generation': {
                'total_clients_created': 1500,
                'total_accounts_created': 2350,
                'total_transactions_created': 8900,
                'total_loans_created': 3000
            },
            'thread_analysis': {
                'threads_completed': 48,
                'threads_with_errors': 2,
                'total_errors': 15,
                'unique_errors': ['Connection timeout', 'Duplicate key violation']
            },
            'errors': [
                'Connection timeout en hilo 7',
                'Duplicate key violation en tabla cuentas',
                'Deadlock detected en transacciones'
            ],
            'recommendations': [
                '⚡ Optimizar consultas de búsqueda por DNI',
                '🔧 Aumentar timeout de conexión',
                '📊 Implementar mejor manejo de transacciones',
                '🔄 Programar validaciones automáticas'
            ]
        }
        
        print("✅ Datos de ejemplo preparados")
        
        print("\n3️⃣  Generar reporte HTML...")
        
        # Generar reporte HTML (comentado para evitar archivos reales)
        # html_file = generator.generate_html_report(sample_results, "ejemplo_reporte.html")
        print("   📄 Reporte HTML preparado - Incluiría dashboard interactivo")
        print("   📊 Con gráficos, métricas y navegación")
        
        print("\n4️⃣  Generar reporte JSON...")
        
        # Generar reporte JSON (comentado para evitar archivos reales)
        # json_file = generator.generate_json_report(sample_results, "ejemplo_reporte.json")
        print("   📋 Reporte JSON preparado - Datos estructurados")
        print("   🔗 Para integración con otros sistemas")
        
        print("\n5️⃣  Generar reporte completo...")
        
        # Generar reporte completo (comentado para evitar archivos reales)
        # report_files = generator.generate_comprehensive_report(sample_results)
        print("   📁 Reporte completo preparado - HTML + JSON + Índice")
        print("   🏠 Con página índice navegable")
        
        print("\n6️⃣  Listar reportes existentes...")
        
        # Listar reportes (comentado para evitar lectura real)
        # reports = generator.list_reports()
        print("   📋 Lista de reportes preparada - En directorio example_reports/")
        
        print("\n✅ Ejemplo 3 completado - Generación de reportes lista")
        
    except ImportError as e:
        print(f"❌ Error de importación: {e}")
        print("💡 Verifica que generate_test_reports.py esté disponible")

def example_4_interpreting_results():
    """Ejemplo 4: Interpretación de resultados y métricas"""
    print("\n" + "="*60)
    print("🔍 EJEMPLO 4: INTERPRETACIÓN DE RESULTADOS")
    print("="*60)
    
    print("\n1️⃣  Métricas de Performance:")
    print("   📊 Tasa de Éxito > 95% = EXCELENTE")
    print("   📊 Tasa de Éxito 85-95% = BUENO")
    print("   📊 Tasa de Éxito < 85% = NECESITA ATENCIÓN")
    print("")
    print("   ⚡ Tiempo de Respuesta < 1s = EXCELENTE")
    print("   ⚡ Tiempo de Respuesta 1-2s = ACEPTABLE")
    print("   ⚡ Tiempo de Respuesta > 2s = LENTO")
    print("")
    print("   🚀 Operaciones/Segundo > 100 = ALTO RENDIMIENTO")
    print("   🚀 Operaciones/Segundo 50-100 = RENDIMIENTO NORMAL")
    print("   🚀 Operaciones/Segundo < 50 = RENDIMIENTO BAJO")
    
    print("\n2️⃣  Códigos de Estado:")
    print("   ✅ PASSED = Todos los criterios cumplidos")
    print("   ⚠️  WARNING = Criterios cumplidos con advertencias")
    print("   ❌ FAILED = Criterios no cumplidos, requiere atención")
    
    print("\n3️⃣  Análisis de Errores:")
    
    # Simular tipos de errores comunes
    error_examples = [
        {
            'error': 'Connection timeout',
            'causa': 'Servidor sobrecargado o red lenta',
            'solución': 'Aumentar timeout o optimizar servidor'
        },
        {
            'error': 'Duplicate key violation',
            'causa': 'Datos duplicados o constraints mal configuradas',
            'solución': 'Limpiar datos existentes o ajustar constraints'
        },
        {
            'error': 'Deadlock detected',
            'causa': 'Acceso concurrente a mismos recursos',
            'solución': 'Optimizar orden de transacciones o usar locking'
        }
    ]
    
    for i, error in enumerate(error_examples, 1):
        print(f"   {i}. {error['error']}")
        print(f"      Causa: {error['causa']}")
        print(f"      Solución: {error['solución']}")
        print("")
    
    print("4️⃣  Recomendaciones Automáticas:")
    recommendations_examples = [
        "⚡ Optimizar índices de base de datos",
        "🔧 Ajustar configuración de pool de conexiones",
        "📊 Implementar monitoreo en tiempo real",
        "💾 Configurar backups automáticos",
        "🔄 Programar validaciones periódicas",
        "🚨 Configurar alertas por umbrales"
    ]
    
    for i, rec in enumerate(recommendations_examples, 1):
        print(f"   {i}. {rec}")
    
    print("\n✅ Ejemplo 4 completado - Guía de interpretación lista")

def example_5_troubleshooting():
    """Ejemplo 5: Solución de problemas comunes"""
    print("\n" + "="*60)
    print("🔧 EJEMPLO 5: SOLUCIÓN DE PROBLEMAS")
    print("="*60)
    
    print("\n1️⃣  Problemas de Conexión:")
    problems = [
        {
            'problema': 'Access denied for user',
            'causa': 'Credenciales incorrectas o permisos insuficientes',
            'solución': 'Verificar usuario, password y grants en MySQL'
        },
        {
            'problema': 'Connection refused',
            'causa': 'Servidor MySQL no ejecutándose',
            'solución': 'Iniciar servicio MySQL y verificar puerto'
        }
    ]
    
    for problem in problems:
        print(f"   ❌ {problem['problema']}")
        print(f"   💡 Causa: {problem['causa']}")
        print(f"   🔧 Solución: {problem['solución']}")
        print("")
    
    print("2️⃣  Problemas de Performance:")
    perf_problems = [
        {
            'problema': 'Tests muy lentos',
            'causa': 'Configuración conservadora o servidor lento',
            'solución': 'Reducir threads o optimizar BD'
        },
        {
            'problema': 'Many timeouts',
            'causa': 'Timeout muy corto o consultas lentas',
            'solución': 'Aumentar timeout o optimizar consultas'
        }
    ]
    
    for problem in perf_problems:
        print(f"   ⏱️  {problem['problema']}")
        print(f"   💡 Causa: {problem['causa']}")
        print(f"   🔧 Solución: {problem['solución']}")
        print("")
    
    print("3️⃣  Problemas de Datos:")
    data_problems = [
        {
            'problema': 'Data integrity violations',
            'causa': 'Datos inconsistentes o constraints faltantes',
            'solución': 'Limpiar datos y verificar constraints'
        },
        {
            'problema': 'Duplicates detected',
            'causa': 'Datos de prueba anteriores no limpiados',
            'solución': 'Limpiar datos de prueba o usar datos únicos'
        }
    ]
    
    for problem in data_problems:
        print(f"   🗃️  {problem['problema']}")
        print(f"   💡 Causa: {problem['causa']}")
        print(f"   🔧 Solución: {problem['solución']}")
        print("")
    
    print("4️⃣  Comandos de Diagnóstico:")
    diagnostic_commands = [
        "# Verificar conexiones MySQL",
        "SHOW PROCESSLIST;",
        "",
        "# Verificar configuración",
        "SHOW VARIABLES LIKE 'max_connections';",
        "",
        "# Verificar logs",
        "tail -f /var/log/mysql/error.log",
        "",
        "# Verificar performance",
        "SHOW STATUS LIKE 'Threads_connected';"
    ]
    
    for cmd in diagnostic_commands:
        if cmd.startswith('#'):
            print(f"\n   {cmd}")
        else:
            print(f"   {cmd}")
    
    print("\n✅ Ejemplo 5 completado - Guía de troubleshooting lista")

def example_6_advanced_configuration():
    """Ejemplo 6: Configuración avanzada"""
    print("\n" + "="*60)
    print("⚙️  EJEMPLO 6: CONFIGURACIÓN AVANZADA")
    print("="*60)
    
    print("\n1️⃣  Configuración de Alto Rendimiento:")
    high_perf_config = {
        "test_settings": {
            "target_records": 5000,
            "concurrent_threads": 100,
            "timeout_seconds": 60,
            "parallel_execution": True,
            "max_parallel_tests": 4
        },
        "output_settings": {
            "reports_dir": "high_perf_reports",
            "generate_html": True,
            "generate_json": True,
            "cleanup_old_reports": False
        },
        "thresholds": {
            "success_rate_minimum": 98.0,
            "response_time_maximum": 1.0,
            "error_rate_maximum": 2.0
        }
    }
    
    print("   🎯 Para sistemas de alto rendimiento:")
    print("   • 5000+ registros objetivo")
    print("   • 100+ hilos concurrentes")
    print("   • Tasa de éxito >98%")
    print("   • Tiempo de respuesta <1s")
    
    print("\n2️⃣  Configuración de Desarrollo:")
    dev_config = {
        "test_settings": {
            "target_records": 100,
            "concurrent_threads": 10,
            "timeout_seconds": 30,
            "parallel_execution": False
        },
        "output_settings": {
            "reports_dir": "dev_reports",
            "generate_html": True,
            "generate_json": False,
            "cleanup_old_reports": True
        }
    }
    
    print("   🔧 Para entornos de desarrollo:")
    print("   • 100 registros para pruebas rápidas")
    print("   • 10 hilos para evitar sobrecarga")
    print("   • Ejecución secuencial")
    print("   • Solo reportes HTML")
    
    print("\n3️⃣  Configuración de Producción:")
    prod_config = {
        "test_settings": {
            "target_records": 10000,
            "concurrent_threads": 200,
            "timeout_seconds": 120,
            "parallel_execution": True,
            "max_parallel_tests": 6
        },
        "scheduling": {
            "enable_scheduling": True,
            "daily_tests_time": "02:00",
            "weekly_tests_day": "sunday"
        },
        "thresholds": {
            "success_rate_minimum": 99.0,
            "response_time_maximum": 0.5,
            "error_rate_maximum": 1.0
        }
    }
    
    print("   🚀 Para entornos de producción:")
    print("   • 10,000+ registros para stress máximo")
    print("   • 200 hilos concurrentes")
    print("   • Tests programados automáticamente")
    print("   • Umbrales muy estrictos")
    print("   • Monitoreo continuo")
    
    print("\n4️⃣  Configuración de CI/CD:")
    cicd_config = {
        "test_settings": {
            "target_records": 500,
            "concurrent_threads": 25,
            "timeout_seconds": 45,
            "parallel_execution": True
        },
        "output_settings": {
            "reports_dir": "cicd_reports",
            "generate_html": False,
            "generate_json": True,
            "save_logs": True
        }
    }
    
    print("   🔄 Para pipelines CI/CD:")
    print("   • 500 registros para validación rápida")
    print("   • Solo reportes JSON para parsing automático")
    print("   • Logs detallados para debugging")
    print("   • Salida rápida para feedback rápido")
    
    print("\n✅ Ejemplo 6 completado - Configuraciones avanzadas documentadas")

def main():
    """Función principal - Menú de ejemplos"""
    print("🎯 SISTEMA DE STRESS TESTING - EJEMPLOS DE USO")
    print("="*70)
    print("Selecciona un ejemplo para ejecutar:")
    print("")
    print("1. 📋 Uso Básico - Tests Individuales")
    print("2. 🤖 Suite de Automatización")  
    print("3. 📊 Generación de Reportes")
    print("4. 🔍 Interpretación de Resultados")
    print("5. 🔧 Solución de Problemas")
    print("6. ⚙️  Configuración Avanzada")
    print("7. 🛠️  Crear Configuración de Ejemplo")
    print("0. ❌ Salir")
    print("="*70)
    
    while True:
        try:
            choice = input("\n👉 Selecciona una opción (0-7): ").strip()
            
            if choice == "1":
                example_1_basic_usage()
            elif choice == "2":
                example_2_automation_suite()
            elif choice == "3":
                example_3_report_generation()
            elif choice == "4":
                example_4_interpreting_results()
            elif choice == "5":
                example_5_troubleshooting()
            elif choice == "6":
                example_6_advanced_configuration()
            elif choice == "7":
                create_example_config()
            elif choice == "0":
                print("\n👋 ¡Gracias por usar el sistema de stress testing!")
                break
            else:
                print("❌ Opción inválida. Selecciona 0-7.")
                
        except KeyboardInterrupt:
            print("\n\n👋 ¡Hasta luego!")
            break
        except Exception as e:
            print(f"\n❌ Error ejecutando ejemplo: {e}")
            print("💡 Verifica que todos los módulos estén disponibles")
    
    print("\n🚀 Sistema de ejemplos finalizado")

if __name__ == "__main__":
    main()
