#!/usr/bin/env python3
"""
Sistema de Stress Testing para LP1 - Sistema Bancario
====================================================

Este módulo implementa pruebas de estrés para el sistema bancario LP1
con 1500+ registros y 50 hilos concurrentes.

Características:
- Pruebas concurrentes con 50 hilos
- Generación de 1500+ registros de prueba
- Métricas detalladas de performance
- Validación de integridad de datos
- Timeouts configurables
- Reportes detallados

Autor: Sistema de Testing Automatizado
Fecha: 2025-10-30
"""

import mysql.connector
import threading
import time
import random
import json
import logging
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Any, Tuple
import uuid
from dataclasses import dataclass
import sys

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('stress_test_lp1.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class TestMetrics:
    """Métricas de la prueba de estrés"""
    start_time: float
    end_time: float = 0
    total_operations: int = 0
    successful_operations: int = 0
    failed_operations: int = 0
    avg_response_time: float = 0
    min_response_time: float = float('inf')
    max_response_time: float = 0
    threads_count: int = 50
    records_generated: int = 0
    errors: List[str] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []

class LP1StressTest:
    """Clase principal para pruebas de estrés del sistema bancario LP1"""
    
    def __init__(self, db_config: Dict[str, Any]):
        """
        Inicializar el sistema de testing
        
        Args:
            db_config: Configuración de base de datos
        """
        self.db_config = db_config
        self.metrics = TestMetrics(start_time=time.time())
        self.lock = threading.Lock()
        self.stop_flag = threading.Event()
        
        # Configuración de la prueba
        self.target_records = 1500
        self.concurrent_threads = 50
        self.timeout_seconds = 30
        self.retry_attempts = 3
        
        # Pool de conexiones
        self.connection_pool = mysql.connector.pooling.MySQLConnectionPool(
            pool_name="stress_test_pool",
            pool_size=20,
            **db_config
        )
        
        logger.info("✅ Sistema de Stress Testing LP1 inicializado")
        logger.info(f"🎯 Objetivo: {self.target_records} registros con {self.concurrent_threads} hilos")

    def generate_test_client(self) -> Dict[str, Any]:
        """Generar datos de cliente de prueba"""
        nombres = [
            "Juan Carlos", "María Elena", "José Antonio", "Carmen Rosa",
            "Luis Miguel", "Ana Patricia", "Roberto Carlos", "Patricia Isabel",
            "Fernando José", "Sandra Milagros", "Eduardo René", "Gloria Esperanza"
        ]
        
        apellidos_paternos = [
            "González", "Rodríguez", "García", "Martínez", "López", "Sánchez",
            "Pérez", "Gómez", "Fernández", "Díaz", "Ramírez", "Torres"
        ]
        
        apellidos_maternos = [
            "Vargas", "Ramos", "Flores", "Rivera", "Morales", "Huerta",
            "Silva", "Castro", "Rojas", "Herrera", "Medina", "Guerrero"
        ]
        
        tipos_cuenta = ['ahorro', 'corriente', 'plazo_fijo']
        estados = ['activo', 'inactivo', 'suspendido']
        tipos_documento = ['DNI', 'RUC', 'PASS', 'CEX']
        
        return {
            'nombre': random.choice(nombres),
            'apellido_paterno': random.choice(apellidos_paternos),
            'apellido_materno': random.choice(apellidos_maternos),
            'email': f"{random.randint(1000, 9999)}@testbank.com",
            'telefono': f"+51{random.randint(900000000, 999999999)}",
            'direccion': f"Calle {random.randint(1, 999)} #{random.randint(1, 999)}",
            'tipo_documento': random.choice(tipos_documento),
            'numero_documento': f"{random.randint(10000000, 99999999)}",
            'estado': random.choice(estados)
        }

    def generate_test_account(self, client_id: int) -> Dict[str, Any]:
        """Generar datos de cuenta de prueba"""
        tipos_cuenta = ['ahorro', 'corriente', 'plazo_fijo']
        estados = ['activo', 'inactivo', 'bloqueado']
        
        return {
            'cliente_id': client_id,
            'numero_cuenta': f"20-{random.randint(10000000, 99999999)}-{random.randint(10, 99)}",
            'tipo_cuenta': random.choice(tipos_cuenta),
            'saldo': round(random.uniform(100.50, 50000.00), 2),
            'estado': random.choice(estados),
            'fecha_apertura': datetime.now() - timedelta(days=random.randint(1, 365))
        }

    def generate_test_transaction(self, account_id: int, client_id: int) -> Dict[str, Any]:
        """Generar datos de transacción de prueba"""
        tipos_transaccion = ['deposito', 'retiro', 'transferencia', 'pago_prestamo']
        estados = ['completada', 'pendiente', 'fallida']
        
        return {
            'cuenta_id': account_id,
            'cliente_id': client_id,
            'tipo_transaccion': random.choice(tipos_transaccion),
            'monto': round(random.uniform(10.00, 5000.00), 2),
            'descripcion': f"Transacción de prueba {uuid.uuid4().hex[:8]}",
            'fecha_transaccion': datetime.now() - timedelta(minutes=random.randint(1, 1440)),
            'estado': random.choice(estados),
            'numero_referencia': f"TXN{random.randint(1000000, 9999999)}"
        }

    def generate_test_loan(self, client_id: int) -> Dict[str, Any]:
        """Generar datos de préstamo de prueba"""
        tipos_prestamo = ['personal', 'hipotecario', 'vehicular', 'empresarial']
        estados = ['solicitado', 'aprobado', 'activo', 'pagado', 'vencido', 'refinanciado']
        
        return {
            'cliente_id': client_id,
            'monto_prestado': round(random.uniform(5000.00, 100000.00), 2),
            'monto_restante': round(random.uniform(1000.00, 50000.00), 2),
            'tasa_interes': round(random.uniform(5.50, 25.50), 2),
            'tipo_prestamo': random.choice(tipos_prestamo),
            'fecha_prestamo': datetime.now() - timedelta(days=random.randint(1, 730)),
            'fecha_vencimiento': datetime.now() + timedelta(days=random.randint(30, 1095)),
            'estado': random.choice(estados),
            'cuotas_pagadas': random.randint(0, 36),
            'cuotas_totales': random.randint(12, 60)
        }

    def insert_client(self, client_data: Dict[str, Any]) -> Tuple[bool, int, str]:
        """Insertar cliente en la base de datos"""
        connection = None
        cursor = None
        
        try:
            connection = self.connection_pool.get_connection()
            cursor = connection.cursor()
            
            query = """
            INSERT INTO clientes (nombre, apellido_paterno, apellido_materno, email, 
                                telefono, direccion, tipo_documento, numero_documento, estado)
            VALUES (%(nombre)s, %(apellido_paterno)s, %(apellido_materno)s, %(email)s,
                    %(telefono)s, %(direccion)s, %(tipo_documento)s, %(numero_documento)s, %(estado)s)
            """
            
            cursor.execute(query, client_data)
            client_id = cursor.lastrowid
            connection.commit()
            
            return True, client_id, "Cliente insertado correctamente"
            
        except mysql.connector.Error as e:
            error_msg = f"Error al insertar cliente: {str(e)}"
            logger.error(error_msg)
            return False, 0, error_msg
            
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    def insert_account(self, account_data: Dict[str, Any]) -> Tuple[bool, int, str]:
        """Insertar cuenta en la base de datos"""
        connection = None
        cursor = None
        
        try:
            connection = self.connection_pool.get_connection()
            cursor = connection.cursor()
            
            query = """
            INSERT INTO cuentas (cliente_id, numero_cuenta, tipo_cuenta, saldo, estado, fecha_apertura)
            VALUES (%(cliente_id)s, %(numero_cuenta)s, %(tipo_cuenta)s, %(saldo)s, %(estado)s, %(fecha_apertura)s)
            """
            
            cursor.execute(query, account_data)
            account_id = cursor.lastrowid
            connection.commit()
            
            return True, account_id, "Cuenta insertada correctamente"
            
        except mysql.connector.Error as e:
            error_msg = f"Error al insertar cuenta: {str(e)}"
            logger.error(error_msg)
            return False, 0, error_msg
            
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    def insert_transaction(self, transaction_data: Dict[str, Any]) -> Tuple[bool, int, str]:
        """Insertar transacción en la base de datos"""
        connection = None
        cursor = None
        
        try:
            connection = self.connection_pool.get_connection()
            cursor = connection.cursor()
            
            query = """
            INSERT INTO transacciones (cuenta_id, cliente_id, tipo_transaccion, monto, 
                                    descripcion, fecha_transaccion, estado, numero_referencia)
            VALUES (%(cuenta_id)s, %(cliente_id)s, %(tipo_transaccion)s, %(monto)s,
                    %(descripcion)s, %(fecha_transaccion)s, %(estado)s, %(numero_referencia)s)
            """
            
            cursor.execute(query, transaction_data)
            transaction_id = cursor.lastrowid
            connection.commit()
            
            return True, transaction_id, "Transacción insertada correctamente"
            
        except mysql.connector.Error as e:
            error_msg = f"Error al insertar transacción: {str(e)}"
            logger.error(error_msg)
            return False, 0, error_msg
            
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    def insert_loan(self, loan_data: Dict[str, Any]) -> Tuple[bool, int, str]:
        """Insertar préstamo en la base de datos"""
        connection = None
        cursor = None
        
        try:
            connection = self.connection_pool.get_connection()
            cursor = connection.cursor()
            
            query = """
            INSERT INTO prestamos (cliente_id, monto_prestado, monto_restante, tasa_interes,
                                 tipo_prestamo, fecha_prestamo, fecha_vencimiento, estado,
                                 cuotas_pagadas, cuotas_totales)
            VALUES (%(cliente_id)s, %(monto_prestado)s, %(monto_restante)s, %(tasa_interes)s,
                    %(tipo_prestamo)s, %(fecha_prestamo)s, %(fecha_vencimiento)s, %(estado)s,
                    %(cuotas_pagadas)s, %(cuotas_totales)s)
            """
            
            cursor.execute(query, loan_data)
            loan_id = cursor.lastrowid
            connection.commit()
            
            return True, loan_id, "Préstamo insertado correctamente"
            
        except mysql.connector.Error as e:
            error_msg = f"Error al insertar préstamo: {str(e)}"
            logger.error(error_msg)
            return False, 0, error_msg
            
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    def worker_thread(self, thread_id: int) -> Dict[str, Any]:
        """Función worker para hilos concurrentes"""
        thread_results = {
            'thread_id': thread_id,
            'clients_created': 0,
            'accounts_created': 0,
            'transactions_created': 0,
            'loans_created': 0,
            'errors': [],
            'start_time': time.time()
        }
        
        try:
            logger.info(f"🔧 Hilo {thread_id}: Iniciando operaciones")
            
            # Calcular registros por hilo
            records_per_thread = self.target_records // self.concurrent_threads
            
            for i in range(records_per_thread):
                if self.stop_flag.is_set():
                    break
                    
                # Crear cliente
                client_data = self.generate_test_client()
                success, client_id, message = self.insert_client(client_data)
                
                if success:
                    thread_results['clients_created'] += 1
                    
                    # Crear cuenta para el cliente
                    account_data = self.generate_test_account(client_id)
                    success_account, account_id, message_account = self.insert_account(account_data)
                    
                    if success_account:
                        thread_results['accounts_created'] += 1
                        
                        # Crear transacción
                        transaction_data = generate_test_transaction(account_id, client_id)
                        success_transaction, transaction_id, message_transaction = self.insert_transaction(transaction_data)
                        
                        if success_transaction:
                            thread_results['transactions_created'] += 1
                            
                            # Crear préstamo
                            loan_data = generate_test_loan(client_id)
                            success_loan, loan_id, message_loan = self.insert_loan(loan_data)
                            
                            if success_loan:
                                thread_results['loans_created'] += 1
                            else:
                                thread_results['errors'].append(f"Préstamo: {message_loan}")
                    else:
                        thread_results['errors'].append(f"Cuenta: {message_account}")
                else:
                    thread_results['errors'].append(f"Cliente: {message}")
                    
                # Pequeña pausa para evitar sobrecarga
                time.sleep(0.01)
                
            thread_results['end_time'] = time.time()
            thread_results['duration'] = thread_results['end_time'] - thread_results['start_time']
            
            logger.info(f"✅ Hilo {thread_id}: Completado - {thread_results['clients_created']} clientes creados")
            
        except Exception as e:
            error_msg = f"Hilo {thread_id}: Error inesperado - {str(e)}"
            logger.error(error_msg)
            thread_results['errors'].append(error_msg)
            thread_results['end_time'] = time.time()
            
        return thread_results

    def run_stress_test(self) -> Dict[str, Any]:
        """Ejecutar la prueba de estrés completa"""
        logger.info("🚀 Iniciando Stress Test LP1 - Sistema Bancario")
        logger.info("=" * 60)
        
        start_time = time.time()
        
        try:
            # Ejecutar hilos concurrentes
            with ThreadPoolExecutor(max_workers=self.concurrent_threads) as executor:
                futures = {
                    executor.submit(self.worker_thread, i): i 
                    for i in range(self.concurrent_threads)
                }
                
                thread_results = []
                
                for future in as_completed(futures):
                    result = future.result(timeout=self.timeout_seconds)
                    thread_results.append(result)
                    
                    # Actualizar métricas globales
                    with self.lock:
                        self.metrics.total_operations += (
                            result['clients_created'] + 
                            result['accounts_created'] + 
                            result['transactions_created'] + 
                            result['loans_created']
                        )
                        self.metrics.records_generated += result['clients_created']
                        
                        if result['errors']:
                            self.metrics.failed_operations += len(result['errors'])
                            self.metrics.errors.extend(result['errors'])
                        else:
                            self.metrics.successful_operations += (
                                result['clients_created'] + 
                                result['accounts_created'] + 
                                result['transactions_created'] + 
                                result['loans_created']
                            )
            
            self.metrics.end_time = time.time()
            self.metrics.avg_response_time = (
                (self.metrics.end_time - self.metrics.start_time) / 
                max(self.metrics.total_operations, 1)
            )
            
            # Generar reporte final
            final_report = self.generate_final_report(thread_results)
            
            logger.info("✅ Stress Test LP1 completado exitosamente")
            logger.info("=" * 60)
            
            return final_report
            
        except Exception as e:
            logger.error(f"❌ Error durante el stress test: {str(e)}")
            self.stop_flag.set()
            raise

    def generate_final_report(self, thread_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generar reporte final de la prueba"""
        total_duration = self.metrics.end_time - self.metrics.start_time
        
        # Calcular estadísticas por hilo
        clients_per_thread = [r['clients_created'] for r in thread_results]
        accounts_per_thread = [r['accounts_created'] for r in thread_results]
        
        report = {
            'test_info': {
                'test_name': 'Stress Test LP1 - Sistema Bancario',
                'timestamp': datetime.now().isoformat(),
                'target_records': self.target_records,
                'concurrent_threads': self.concurrent_threads,
                'timeout_seconds': self.timeout_seconds
            },
            'performance_metrics': {
                'total_duration': round(total_duration, 2),
                'total_operations': self.metrics.total_operations,
                'successful_operations': self.metrics.successful_operations,
                'failed_operations': self.metrics.failed_operations,
                'success_rate': round(
                    (self.metrics.successful_operations / max(self.metrics.total_operations, 1)) * 100, 2
                ),
                'avg_response_time': round(self.metrics.avg_response_time, 4),
                'operations_per_second': round(self.metrics.total_operations / total_duration, 2)
            },
            'data_generation': {
                'total_clients_created': sum(clients_per_thread),
                'total_accounts_created': sum(accounts_per_thread),
                'avg_clients_per_thread': round(sum(clients_per_thread) / len(clients_per_thread), 2),
                'client_distribution': {
                    'min_per_thread': min(clients_per_thread),
                    'max_per_thread': max(clients_per_thread),
                    'std_deviation': round(
                        (sum((x - sum(clients_per_thread)/len(clients_per_thread))**2 
                             for x in clients_per_thread) / len(clients_per_thread))**0.5, 2
                    )
                }
            },
            'thread_analysis': {
                'threads_completed': len([r for r in thread_results if not r['errors']]),
                'threads_with_errors': len([r for r in thread_results if r['errors']]),
                'total_errors': len(self.metrics.errors),
                'unique_errors': list(set(self.metrics.errors))
            },
            'database_stats': {
                'connection_pool_size': self.connection_pool.pool_size,
                'connection_pool_name': self.connection_pool.pool_name,
                'database_host': self.db_config.get('host', 'localhost'),
                'database_name': self.db_config.get('database', 'banco_lp1')
            },
            'recommendations': self._generate_recommendations()
        }
        
        # Guardar reporte en JSON
        with open('stress_test_lp1_report.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False, default=str)
        
        logger.info(f"📊 Reporte guardado en: stress_test_lp1_report.json")
        
        return report

    def _generate_recommendations(self) -> List[str]:
        """Generar recomendaciones basadas en los resultados"""
        recommendations = []
        
        if self.metrics.failed_operations > 0:
            recommendations.append("⚠️  Se detectaron operaciones fallidas. Revisar la capacidad del servidor.")
            
        if self.metrics.avg_response_time > 1.0:
            recommendations.append("⚡ Tiempo de respuesta promedio alto. Considerar optimizar índices.")
            
        if self.metrics.records_generated < self.target_records * 0.9:
            recommendations.append("📈 Objetivo de registros no alcanzado. Aumentar tiempo de timeout o capacidad.")
            
        if len(self.metrics.errors) > 10:
            recommendations.append("🔍 Muchos errores únicos detectados. Revisar configuración de BD.")
            
        if not recommendations:
            recommendations.append("✅ Sistema funcionando dentro de parámetros normales.")
            
        return recommendations

    def validate_database_integrity(self) -> Dict[str, Any]:
        """Validar integridad de la base de datos después de las pruebas"""
        logger.info("🔍 Validando integridad de la base de datos...")
        
        validation_results = {}
        connection = None
        cursor = None
        
        try:
            connection = self.connection_pool.get_connection()
            cursor = connection.cursor()
            
            # Verificar conteos por tabla
            tables = ['clientes', 'cuentas', 'transacciones', 'prestamos']
            
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                validation_results[f'{table}_count'] = count
            
            # Verificar integridad referencial
            cursor.execute("""
                SELECT COUNT(*) FROM clientes c
                LEFT JOIN cuentas cu ON c.id = cu.cliente_id
                WHERE cu.cliente_id IS NULL
            """)
            orphaned_clients = cursor.fetchone()[0]
            validation_results['orphaned_clients'] = orphaned_clients
            
            # Verificar transacciones válidas
            cursor.execute("""
                SELECT COUNT(*) FROM transacciones t
                LEFT JOIN cuentas cu ON t.cuenta_id = cu.id
                WHERE cu.id IS NULL
            """)
            orphaned_transactions = cursor.fetchone()[0]
            validation_results['orphaned_transactions'] = orphaned_transactions
            
            # Verificar préstamos válidos
            cursor.execute("""
                SELECT COUNT(*) FROM prestamos p
                LEFT JOIN clientes c ON p.cliente_id = c.id
                WHERE c.id IS NULL
            """)
            orphaned_loans = cursor.fetchone()[0]
            validation_results['orphaned_loans'] = orphaned_loans
            
            validation_results['integrity_status'] = 'PASS' if all([
                orphaned_clients == 0,
                orphaned_transactions == 0,
                orphaned_loans == 0
            ]) else 'FAIL'
            
            logger.info(f"✅ Validación completada. Estado: {validation_results['integrity_status']}")
            
        except mysql.connector.Error as e:
            logger.error(f"❌ Error durante validación: {str(e)}")
            validation_results['error'] = str(e)
            
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
                
        return validation_results


def main():
    """Función principal"""
    # Configuración de base de datos
    db_config = {
        'host': 'localhost',
        'port': 3306,
        'user': 'root',
        'password': 'password',
        'database': 'banco_lp1',
        'charset': 'utf8mb4',
        'autocommit': False
    }
    
    try:
        # Crear instancia del test
        stress_test = LP1StressTest(db_config)
        
        # Ejecutar prueba de estrés
        report = stress_test.run_stress_test()
        
        # Validar integridad
        integrity_report = stress_test.validate_database_integrity()
        
        # Mostrar resumen
        print("\n" + "="*60)
        print("📊 RESUMEN DEL STRESS TEST LP1")
        print("="*60)
        print(f"⏱️  Duración total: {report['performance_metrics']['total_duration']} segundos")
        print(f"🎯 Registros creados: {report['data_generation']['total_clients_created']}")
        print(f"✅ Operaciones exitosas: {report['performance_metrics']['successful_operations']}")
        print(f"❌ Operaciones fallidas: {report['performance_metrics']['failed_operations']}")
        print(f"📈 Tasa de éxito: {report['performance_metrics']['success_rate']}%")
        print(f"🚀 Ops/segundo: {report['performance_metrics']['operations_per_second']}")
        print(f"🔍 Estado de integridad: {integrity_report.get('integrity_status', 'UNKNOWN')}")
        print("="*60)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error en el stress test: {str(e)}")
        return False


if __name__ == "__main__":
    main()
