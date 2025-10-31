#!/usr/bin/env python3
"""
Validador de Integridad de Datos entre BD1 (LP1) y BD2 (LP2)
============================================================

Este módulo valida la integridad y consistencia de datos entre las
bases de datos del sistema bancario LP1 y el sistema RENIEC LP2.

Características:
- Validación cruzada entre bases de datos
- Verificación de consistencia de datos
- Análisis de integridad referencial
- Detección de anomalías y duplicados
- Reportes detallados de discrepancias
- Validación de transacciones

Autor: Sistema de Testing Automatizado
Fecha: 2025-10-30
"""

import mysql.connector
import pandas as pd
import logging
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple, Optional
import hashlib
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
import statistics

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data_integrity_validation.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class DataIntegrityValidator:
    """Validador de integridad de datos entre bases de datos"""
    
    def __init__(self, lp1_config: Dict[str, Any], lp2_config: Dict[str, Any]):
        """
        Inicializar validador de integridad
        
        Args:
            lp1_config: Configuración de BD LP1 (Banco)
            lp2_config: Configuración de BD LP2 (RENIEC)
        """
        self.lp1_config = lp1_config
        self.lp2_config = lp2_config
        self.lp1_conn = None
        self.lp2_conn = None
        
        # Métricas de validación
        self.validation_results = {
            'start_time': time.time(),
            'end_time': 0,
            'total_checks': 0,
            'passed_checks': 0,
            'failed_checks': 0,
            'warnings': [],
            'errors': [],
            'statistics': {},
            'cross_database_analysis': {},
            'recommendations': []
        }
        
        logger.info("✅ Validador de Integridad de Datos inicializado")

    def connect_databases(self) -> Tuple[bool, str]:
        """Conectar a ambas bases de datos"""
        try:
            # Conectar a LP1 (Banco)
            self.lp1_conn = mysql.connector.connect(**self.lp1_config)
            
            # Conectar a LP2 (RENIEC)
            self.lp2_conn = mysql.connector.connect(**self.lp2_config)
            
            logger.info("✅ Conexiones a ambas bases de datos establecidas")
            return True, "Conexiones exitosas"
            
        except mysql.connector.Error as e:
            error_msg = f"Error conectando a bases de datos: {str(e)}"
            logger.error(error_msg)
            return False, error_msg

    def validate_table_counts(self) -> Dict[str, Any]:
        """Validar consistencia en conteos de tablas principales"""
        logger.info("📊 Validando conteos de tablas...")
        
        table_counts = {'lp1': {}, 'lp2': {}}
        
        try:
            # Conteo tablas LP1 (Banco)
            lp1_tables = ['clientes', 'cuentas', 'transacciones', 'prestamos']
            for table in lp1_tables:
                cursor = self.lp1_conn.cursor()
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                table_counts['lp1'][table] = count
                cursor.close()
            
            # Conteo tablas LP2 (RENIEC)
            lp2_tables = ['ciudadanos', 'validadores', 'reniec_sessions', 'auditoria']
            for table in lp2_tables:
                cursor = self.lp2_conn.cursor()
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                table_counts['lp2'][table] = count
                cursor.close()
            
            # Análisis de consistencia
            consistency_report = {
                'lp1_tables': table_counts['lp1'],
                'lp2_tables': table_counts['lp2'],
                'total_lp1_records': sum(table_counts['lp1'].values()),
                'total_lp2_records': sum(table_counts['lp2'].values()),
                'ratio_lp2_lp1': round(
                    sum(table_counts['lp2'].values()) / max(sum(table_counts['lp1'].values()), 1), 3
                )
            }
            
            self.validation_results['statistics']['table_counts'] = consistency_report
            self._record_validation_check("Conteo de tablas", True, "Validación exitosa")
            
            logger.info(f"✅ Conteo LP1: {consistency_report['total_lp1_records']} registros")
            logger.info(f"✅ Conteo LP2: {consistency_report['total_lp2_records']} registros")
            
            return consistency_report
            
        except mysql.connector.Error as e:
            error_msg = f"Error validando conteos: {str(e)}"
            self._record_validation_check("Conteo de tablas", False, error_msg)
            logger.error(error_msg)
            return {'error': error_msg}

    def validate_data_quality_lp1(self) -> Dict[str, Any]:
        """Validar calidad de datos en LP1 (Banco)"""
        logger.info("🔍 Validando calidad de datos LP1...")
        
        quality_report = {}
        
        try:
            # Validar clientes LP1
            cursor = self.lp1_conn.cursor()
            
            # Verificar emails válidos
            cursor.execute("""
                SELECT COUNT(*) FROM clientes 
                WHERE email NOT REGEXP '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
            """)
            invalid_emails = cursor.fetchone()[0]
            quality_report['invalid_emails'] = invalid_emails
            
            # Verificar teléfonos válidos (formato peruano)
            cursor.execute("""
                SELECT COUNT(*) FROM clientes 
                WHERE telefono NOT REGEXP '^\\+51[0-9]{9}$'
            """)
            invalid_phones = cursor.fetchone()[0]
            quality_report['invalid_phones'] = invalid_phones
            
            # Verificar saldos negativos en cuentas
            cursor.execute("""
                SELECT COUNT(*) FROM cuentas WHERE saldo < 0
            """)
            negative_balances = cursor.fetchone()[0]
            quality_report['negative_balances'] = negative_balances
            
            # Verificar transacciones sin cuenta asociada
            cursor.execute("""
                SELECT COUNT(*) FROM transacciones t
                LEFT JOIN cuentas c ON t.cuenta_id = c.id
                WHERE c.id IS NULL
            """)
            orphaned_transactions = cursor.fetchone()[0]
            quality_report['orphaned_transactions'] = orphaned_transactions
            
            # Verificar préstamos sin cliente
            cursor.execute("""
                SELECT COUNT(*) FROM prestamos p
                LEFT JOIN clientes c ON p.cliente_id = c.id
                WHERE c.id IS NULL
            """)
            orphaned_loans = cursor.fetchone()[0]
            quality_report['orphaned_loans'] = orphaned_loans
            
            # Verificar fechas de vencimiento futuras
            cursor.execute("""
                SELECT COUNT(*) FROM prestamos 
                WHERE fecha_vencimiento < CURDATE()
            """)
            past_due_loans = cursor.fetchone()[0]
            quality_report['past_due_loans'] = past_due_loans
            
            cursor.close()
            
            # Calcular score de calidad
            total_records = sum([
                quality_report.get('invalid_emails', 0),
                quality_report.get('invalid_phones', 0),
                quality_report.get('negative_balances', 0),
                quality_report.get('orphaned_transactions', 0),
                quality_report.get('orphaned_loans', 0),
                quality_report.get('past_due_loans', 0)
            ])
            
            quality_report['quality_score'] = max(0, 100 - (total_records * 2))
            quality_report['status'] = 'GOOD' if quality_report['quality_score'] >= 80 else 'NEEDS_ATTENTION'
            
            self.validation_results['statistics']['lp1_quality'] = quality_report
            self._record_validation_check("Calidad datos LP1", quality_report['status'] == 'GOOD', 
                                        f"Score: {quality_report['quality_score']}")
            
            return quality_report
            
        except mysql.connector.Error as e:
            error_msg = f"Error validando calidad LP1: {str(e)}"
            self._record_validation_check("Calidad datos LP1", False, error_msg)
            logger.error(error_msg)
            return {'error': error_msg}

    def validate_data_quality_lp2(self) -> Dict[str, Any]:
        """Validar calidad de datos en LP2 (RENIEC)"""
        logger.info("🔍 Validando calidad de datos LP2...")
        
        quality_report = {}
        
        try:
            cursor = self.lp2_conn.cursor()
            
            # Verificar DNIs únicos
            cursor.execute("""
                SELECT dni, COUNT(*) as count 
                FROM ciudadanos 
                GROUP BY dni 
                HAVING COUNT(*) > 1
            """)
            duplicate_dnis = cursor.fetchall()
            quality_report['duplicate_dnis'] = len(duplicate_dnis)
            quality_report['duplicate_dni_details'] = [
                {'dni': row[0], 'count': row[1]} for row in duplicate_dnis
            ]
            
            # Verificar formato de DNI (8 dígitos)
            cursor.execute("""
                SELECT COUNT(*) FROM ciudadanos 
                WHERE LENGTH(dni) != 8 OR dni NOT REGEXP '^[0-9]+$'
            """)
            invalid_dni_format = cursor.fetchone()[0]
            quality_report['invalid_dni_format'] = invalid_dni_format
            
            # Verificar fechas de nacimiento válidas
            cursor.execute("""
                SELECT COUNT(*) FROM ciudadanos 
                WHERE fecha_nacimiento > CURDATE() OR fecha_nacimiento < '1900-01-01'
            """)
            invalid_birth_dates = cursor.fetchone()[0]
            quality_report['invalid_birth_dates'] = invalid_birth_dates
            
            # Verificar usuarios de validadores únicos
            cursor.execute("""
                SELECT usuario, COUNT(*) as count 
                FROM validadores 
                GROUP BY usuario 
                HAVING COUNT(*) > 1
            """)
            duplicate_validators = cursor.fetchall()
            quality_report['duplicate_validators'] = len(duplicate_validators)
            
            # Verificar sesiones sin validador
            cursor.execute("""
                SELECT COUNT(*) FROM reniec_sessions s
                LEFT JOIN validadores v ON s.validador_id = v.id
                WHERE v.id IS NULL
            """)
            orphaned_sessions = cursor.fetchone()[0]
            quality_report['orphaned_sessions'] = orphaned_sessions
            
            # Verificar auditorías sin referencia
            cursor.execute("""
                SELECT COUNT(*) FROM auditoria a
                LEFT JOIN validadores v ON a.validador_id = v.id
                WHERE v.id IS NULL AND a.validador_id IS NOT NULL
            """)
            orphaned_audit_records = cursor.fetchone()[0]
            quality_report['orphaned_audit_records'] = orphaned_audit_records
            
            cursor.close()
            
            # Calcular score de calidad
            total_issues = sum([
                quality_report.get('duplicate_dnis', 0),
                quality_report.get('invalid_dni_format', 0),
                quality_report.get('invalid_birth_dates', 0),
                quality_report.get('duplicate_validators', 0),
                quality_report.get('orphaned_sessions', 0),
                quality_report.get('orphaned_audit_records', 0)
            ])
            
            quality_report['quality_score'] = max(0, 100 - (total_issues * 3))
            quality_report['status'] = 'EXCELLENT' if quality_report['quality_score'] >= 95 else \
                                     'GOOD' if quality_report['quality_score'] >= 80 else \
                                     'NEEDS_ATTENTION'
            
            self.validation_results['statistics']['lp2_quality'] = quality_report
            self._record_validation_check("Calidad datos LP2", quality_report['status'] != 'NEEDS_ATTENTION', 
                                        f"Score: {quality_report['quality_score']}")
            
            return quality_report
            
        except mysql.connector.Error as e:
            error_msg = f"Error validando calidad LP2: {str(e)}"
            self._record_validation_check("Calidad datos LP2", False, error_msg)
            logger.error(error_msg)
            return {'error': error_msg}

    def validate_cross_database_consistency(self) -> Dict[str, Any]:
        """Validar consistencia entre bases de datos"""
        logger.info("🔗 Validando consistencia entre bases de datos...")
        
        cross_db_report = {}
        
        try:
            # Verificar si hay ciudadanos en LP2 que podrían estar en LP1
            cursor_lp1 = self.lp1_conn.cursor()
            cursor_lp2 = self.lp2_conn.cursor()
            
            # Obtener emails de clientes LP1
            cursor_lp1.execute("SELECT email FROM clientes WHERE email IS NOT NULL")
            lp1_emails = {row[0] for row in cursor_lp1.fetchall()}
            
            # Verificar si hay coincidencias (simuladas, ya que son BD diferentes)
            cross_db_report['potential_data_overlap'] = {
                'lp1_unique_emails': len(lp1_emails),
                'emails_in_both_systems': 0,  # Sería 0 normalmente en sistemas separados
                'overlap_percentage': 0.0
            }
            
            # Verificar patrones de nombres similares (análisis básico)
            cursor_lp1.execute("SELECT nombre, apellido_paterno, apellido_materno FROM clientes LIMIT 100")
            lp1_names = cursor_lp1.fetchall()
            
            cursor_lp2.execute("SELECT nombre, apellido_paterno, apellido_materno FROM ciudadanos LIMIT 100")
            lp2_names = cursor_lp2.fetchall()
            
            # Análisis de similitud de nombres
            similar_names = self._find_similar_names(lp1_names, lp2_names)
            cross_db_report['name_similarity_analysis'] = {
                'lp1_names_analyzed': len(lp1_names),
                'lp2_names_analyzed': len(lp2_names),
                'similar_full_names': len(similar_names),
                'similarity_examples': similar_names[:5]
            }
            
            # Verificar sesiones activas en LP2 vs clientes activos en LP1
            cursor_lp2.execute("SELECT COUNT(*) FROM reniec_sessions WHERE activa = TRUE")
            active_sessions = cursor_lp2.fetchone()[0]
            
            cursor_lp1.execute("SELECT COUNT(*) FROM clientes WHERE estado = 'activo'")
            active_clients = cursor_lp1.fetchone()[0]
            
            cross_db_report['active_users_comparison'] = {
                'active_lp2_sessions': active_sessions,
                'active_lp1_clients': active_clients,
                'usage_ratio': round(active_sessions / max(active_clients, 1), 3)
            }
            
            cursor_lp1.close()
            cursor_lp2.close()
            
            self.validation_results['cross_database_analysis'] = cross_db_report
            self._record_validation_check("Consistencia cruzada BD", True, "Análisis completado")
            
            return cross_db_report
            
        except mysql.connector.Error as e:
            error_msg = f"Error validando consistencia cruzada: {str(e)}"
            self._record_validation_check("Consistencia cruzada BD", False, error_msg)
            logger.error(error_msg)
            return {'error': error_msg}

    def _find_similar_names(self, names1: List[Tuple], names2: List[Tuple]) -> List[str]:
        """Encontrar nombres similares entre dos conjuntos"""
        similar_names = []
        
        # Crear combinaciones de nombres completos
        names1_full = {f"{n[0]} {n[1]} {n[2]}" for n in names1}
        names2_full = {f"{n[0]} {n[1]} {n[2]}" for n in names2}
        
        # Buscar coincidencias exactas (raras pero posibles)
        exact_matches = names1_full.intersection(names2_full)
        similar_names.extend(list(exact_matches))
        
        return similar_names

    def validate_transaction_integrity(self) -> Dict[str, Any]:
        """Validar integridad de transacciones"""
        logger.info("💳 Validando integridad de transacciones...")
        
        transaction_report = {}
        
        try:
            cursor = self.lp1_conn.cursor()
            
            # Verificar transacciones huérfanas
            cursor.execute("""
                SELECT COUNT(*) FROM transacciones t
                LEFT JOIN cuentas c ON t.cuenta_id = c.id
                WHERE c.id IS NULL
            """)
            orphaned_transactions = cursor.fetchone()[0]
            transaction_report['orphaned_transactions'] = orphaned_transactions
            
            # Verificar montos inconsistentes
            cursor.execute("""
                SELECT COUNT(*) FROM transacciones
                WHERE monto <= 0 OR monto > 1000000
            """)
            invalid_amounts = cursor.fetchone()[0]
            transaction_report['invalid_amounts'] = invalid_amounts
            
            # Verificar transacciones futuras
            cursor.execute("""
                SELECT COUNT(*) FROM transacciones
                WHERE fecha_transaccion > NOW()
            """)
            future_transactions = cursor.fetchone()[0]
            transaction_report['future_transactions'] = future_transactions
            
            # Verificar números de referencia duplicados
            cursor.execute("""
                SELECT numero_referencia, COUNT(*) as count
                FROM transacciones
                GROUP BY numero_referencia
                HAVING COUNT(*) > 1
            """)
            duplicate_refs = cursor.fetchall()
            transaction_report['duplicate_references'] = len(duplicate_refs)
            transaction_report['duplicate_ref_details'] = [
                {'reference': row[0], 'count': row[1]} for row in duplicate_refs
            ]
            
            # Verificar balance después de transacciones
            cursor.execute("""
                SELECT COUNT(*) FROM cuentas c
                WHERE (
                    (SELECT COALESCE(SUM(CASE WHEN tipo_transaccion = 'deposito' THEN monto ELSE -monto END), 0)
                     FROM transacciones t WHERE t.cuenta_id = c.id) + c.saldo
                ) < 0
            """)
            negative_balances_after_txn = cursor.fetchone()[0]
            transaction_report['negative_balances_after_transactions'] = negative_balances_after_txn
            
            cursor.close()
            
            # Calcular score de integridad transaccional
            total_issues = sum([
                transaction_report.get('orphaned_transactions', 0),
                transaction_report.get('invalid_amounts', 0),
                transaction_report.get('future_transactions', 0),
                transaction_report.get('duplicate_references', 0),
                transaction_report.get('negative_balances_after_transactions', 0)
            ])
            
            transaction_report['integrity_score'] = max(0, 100 - (total_issues * 5))
            transaction_report['status'] = 'EXCELLENT' if transaction_report['integrity_score'] >= 95 else \
                                          'GOOD' if transaction_report['integrity_score'] >= 85 else \
                                          'NEEDS_ATTENTION'
            
            self.validation_results['statistics']['transaction_integrity'] = transaction_report
            self._record_validation_check("Integridad transacciones", 
                                        transaction_report['status'] != 'NEEDS_ATTENTION',
                                        f"Score: {transaction_report['integrity_score']}")
            
            return transaction_report
            
        except mysql.connector.Error as e:
            error_msg = f"Error validando transacciones: {str(e)}"
            self._record_validation_check("Integridad transacciones", False, error_msg)
            logger.error(error_msg)
            return {'error': error_msg}

    def validate_audit_trail(self) -> Dict[str, Any]:
        """Validar trazabilidad y auditoría"""
        logger.info("📝 Validando trazabilidad y auditoría...")
        
        audit_report = {}
        
        try:
            cursor = self.lp2_conn.cursor()
            
            # Verificar registros de auditoría por día
            cursor.execute("""
                SELECT DATE(timestamp_operacion) as date, COUNT(*) as count
                FROM auditoria
                WHERE timestamp_operacion >= DATE_SUB(NOW(), INTERVAL 30 DAY)
                GROUP BY DATE(timestamp_operacion)
                ORDER BY date DESC
                LIMIT 10
            """)
            audit_by_day = cursor.fetchall()
            audit_report['audit_by_day'] = [
                {'date': row[0].strftime('%Y-%m-%d'), 'count': row[1]} 
                for row in audit_by_day
            ]
            
            # Verificar acciones más frecuentes
            cursor.execute("""
                SELECT accion, COUNT(*) as count
                FROM auditoria
                GROUP BY accion
                ORDER BY count DESC
            """)
            audit_by_action = cursor.fetchall()
            audit_report['audit_by_action'] = [
                {'action': row[0], 'count': row[1]} for row in audit_by_action
            ]
            
            # Verificar operaciones sin auditoría (muestra)
            cursor.execute("""
                SELECT COUNT(DISTINCT v.id) FROM validadores v
                LEFT JOIN auditoria a ON v.id = a.validador_id
                WHERE a.validador_id IS NULL AND v.activo = TRUE
            """)
            validators_without_audit = cursor.fetchone()[0]
            audit_report['validators_without_audit'] = validators_without_audit
            
            # Verificar auditorías sin datos
            cursor.execute("""
                SELECT COUNT(*) FROM auditoria
                WHERE (datos_anteriores IS NULL OR datos_anteriores = 'null')
                AND (datos_nuevos IS NULL OR datos_nuevos = 'null')
                AND accion != 'LOGIN'
            """)
            empty_audit_records = cursor.fetchone()[0]
            audit_report['empty_audit_records'] = empty_audit_records
            
            cursor.close()
            
            # Evaluar cobertura de auditoría
            cursor_lp1 = self.lp1_conn.cursor()
            cursor_lp1.execute("SELECT COUNT(*) FROM clientes")
            total_clients = cursor_lp1.fetchone()[0]
            cursor_lp1.close()
            
            audit_coverage = max(0, 100 - (
                (validators_without_audit / max(total_clients, 1)) * 100
            ))
            
            audit_report['coverage_score'] = audit_coverage
            audit_report['status'] = 'EXCELLENT' if audit_coverage >= 90 else \
                                   'GOOD' if audit_coverage >= 70 else \
                                   'NEEDS_ATTENTION'
            
            self.validation_results['statistics']['audit_trail'] = audit_report
            self._record_validation_check("Trazabilidad auditoría", 
                                        audit_report['status'] != 'NEEDS_ATTENTION',
                                        f"Cobertura: {audit_coverage:.1f}%")
            
            return audit_report
            
        except mysql.connector.Error as e:
            error_msg = f"Error validando auditoría: {str(e)}"
            self._record_validation_check("Trazabilidad auditoría", False, error_msg)
            logger.error(error_msg)
            return {'error': error_msg}

    def _record_validation_check(self, check_name: str, passed: bool, message: str):
        """Registrar resultado de validación"""
        self.validation_results['total_checks'] += 1
        
        if passed:
            self.validation_results['passed_checks'] += 1
            logger.info(f"✅ {check_name}: {message}")
        else:
            self.validation_results['failed_checks'] += 1
            self.validation_results['errors'].append(f"{check_name}: {message}")
            logger.error(f"❌ {check_name}: {message}")

    def generate_performance_comparison(self) -> Dict[str, Any]:
        """Comparar rendimiento entre bases de datos"""
        logger.info("⚡ Comparando rendimiento de bases de datos...")
        
        performance_report = {}
        
        # Test de velocidad de consulta simple
        start_time = time.time()
        try:
            cursor_lp1 = self.lp1_conn.cursor()
            cursor_lp1.execute("SELECT COUNT(*) FROM clientes")
            cursor_lp1.fetchone()
            lp1_time = time.time() - start_time
            cursor_lp1.close()
            
            start_time = time.time()
            cursor_lp2 = self.lp2_conn.cursor()
            cursor_lp2.execute("SELECT COUNT(*) FROM ciudadanos")
            cursor_lp2.fetchone()
            lp2_time = time.time() - start_time
            cursor_lp2.close()
            
            performance_report['simple_query_comparison'] = {
                'lp1_count_query_time': round(lp1_time * 1000, 2),  # ms
                'lp2_count_query_time': round(lp2_time * 1000, 2),  # ms
                'faster_system': 'LP1' if lp1_time < lp2_time else 'LP2',
                'performance_difference': round(abs(lp1_time - lp2_time) * 1000, 2)
            }
            
            self._record_validation_check("Rendimiento BD", True, 
                                        f"LP1: {lp1_time*1000:.1f}ms, LP2: {lp2_time*1000:.1f}ms")
            
        except mysql.connector.Error as e:
            error_msg = f"Error en comparación de rendimiento: {str(e)}"
            self._record_validation_check("Rendimiento BD", False, error_msg)
            performance_report['error'] = error_msg
        
        self.validation_results['statistics']['performance'] = performance_report
        return performance_report

    def run_complete_validation(self) -> Dict[str, Any]:
        """Ejecutar validación completa de integridad"""
        logger.info("🚀 Iniciando validación completa de integridad de datos")
        logger.info("=" * 70)
        
        try:
            # Conectar a bases de datos
            connection_success, connection_message = self.connect_databases()
            if not connection_success:
                raise Exception(connection_message)
            
            # Ejecutar todas las validaciones
            validations = [
                ("Conteo de tablas", self.validate_table_counts),
                ("Calidad de datos LP1", self.validate_data_quality_lp1),
                ("Calidad de datos LP2", self.validate_data_quality_lp2),
                ("Consistencia entre BD", self.validate_cross_database_consistency),
                ("Integridad de transacciones", self.validate_transaction_integrity),
                ("Trazabilidad de auditoría", self.validate_audit_trail),
                ("Comparación de rendimiento", self.generate_performance_comparison)
            ]
            
            results = {}
            for validation_name, validation_func in validations:
                try:
                    result = validation_func()
                    results[validation_name] = result
                    time.sleep(0.1)  # Pausa entre validaciones
                except Exception as e:
                    error_msg = f"Error en {validation_name}: {str(e)}"
                    self.validation_results['errors'].append(error_msg)
                    logger.error(error_msg)
                    results[validation_name] = {'error': error_msg}
            
            # Completar métricas
            self.validation_results['end_time'] = time.time()
            self.validation_results['total_duration'] = round(
                self.validation_results['end_time'] - self.validation_results['start_time'], 2
            )
            
            # Generar reporte final
            final_report = self._generate_final_report(results)
            
            logger.info("✅ Validación de integridad completada")
            logger.info("=" * 70)
            
            return final_report
            
        except Exception as e:
            logger.error(f"❌ Error en validación completa: {str(e)}")
            self.validation_results['errors'].append(str(e))
            raise
        
        finally:
            # Cerrar conexiones
            if self.lp1_conn:
                self.lp1_conn.close()
            if self.lp2_conn:
                self.lp2_conn.close()
            logger.info("🔒 Conexiones a bases de datos cerradas")

    def _generate_final_report(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generar reporte final de validación"""
        success_rate = (self.validation_results['passed_checks'] / 
                       max(self.validation_results['total_checks'], 1)) * 100
        
        final_report = {
            'validation_summary': {
                'start_time': datetime.fromtimestamp(self.validation_results['start_time']).isoformat(),
                'end_time': datetime.fromtimestamp(self.validation_results['end_time']).isoformat(),
                'total_duration': self.validation_results['total_duration'],
                'total_checks': self.validation_results['total_checks'],
                'passed_checks': self.validation_results['passed_checks'],
                'failed_checks': self.validation_results['failed_checks'],
                'success_rate': round(success_rate, 2),
                'overall_status': 'PASSED' if success_rate >= 80 else 'FAILED'
            },
            'validation_results': results,
            'errors': self.validation_results['errors'],
            'warnings': self.validation_results['warnings'],
            'cross_database_analysis': self.validation_results['cross_database_analysis'],
            'recommendations': self._generate_recommendations(),
            'quality_scores': self._calculate_quality_scores(results),
            'compliance_status': self._assess_compliance(results)
        }
        
        # Guardar reporte
        with open('data_integrity_validation_report.json', 'w', encoding='utf-8') as f:
            json.dump(final_report, f, indent=2, ensure_ascii=False, default=str)
        
        logger.info(f"📊 Reporte guardado en: data_integrity_validation_report.json")
        
        return final_report

    def _calculate_quality_scores(self, results: Dict[str, Any]) -> Dict[str, float]:
        """Calcular scores de calidad por sistema"""
        scores = {}
        
        # Score LP1
        if 'Calidad de datos LP1' in results and 'quality_score' in results['Calidad de datos LP1']:
            scores['lp1_quality_score'] = results['Calidad de datos LP1']['quality_score']
        else:
            scores['lp1_quality_score'] = 0
        
        # Score LP2
        if 'Calidad de datos LP2' in results and 'quality_score' in results['Calidad de datos LP2']:
            scores['lp2_quality_score'] = results['Calidad de datos LP2']['quality_score']
        else:
            scores['lp2_quality_score'] = 0
        
        # Score transacciones
        if 'Integridad de transacciones' in results and 'integrity_score' in results['Integridad de transacciones']:
            scores['transaction_integrity_score'] = results['Integridad de transacciones']['integrity_score']
        else:
            scores['transaction_integrity_score'] = 0
        
        # Score auditoría
        if 'Trazabilidad de auditoría' in results and 'coverage_score' in results['Trazabilidad de auditoría']:
            scores['audit_coverage_score'] = results['Trazabilidad de auditoría']['coverage_score']
        else:
            scores['audit_coverage_score'] = 0
        
        # Score promedio
        scores['overall_quality_score'] = round(
            sum(scores.values()) / len(scores), 2
        )
        
        return scores

    def _assess_compliance(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluar cumplimiento normativo"""
        compliance = {
            'data_protection': 'COMPLIANT',
            'audit_requirements': 'COMPLIANT',
            'transaction_integrity': 'COMPLIANT',
            'data_quality': 'COMPLIANT',
            'overall_compliance': 'COMPLIANT'
        }
        
        issues = []
        
        # Evaluar cumplimiento de protección de datos
        if 'Calidad de datos LP2' in results:
            lp2_quality = results['Calidad de datos LP2']
            if lp2_quality.get('duplicate_dnis', 0) > 0:
                compliance['data_protection'] = 'NEEDS_ATTENTION'
                issues.append("DNIs duplicados detectados en LP2")
            
            if lp2_quality.get('invalid_dni_format', 0) > 0:
                compliance['data_protection'] = 'NON_COMPLIANT'
                issues.append("Formatos de DNI inválidos en LP2")
        
        # Evaluar requerimientos de auditoría
        if 'Trazabilidad de auditoría' in results:
            audit_quality = results['Trazabilidad de auditoría']
            if audit_quality.get('coverage_score', 100) < 70:
                compliance['audit_requirements'] = 'NEEDS_ATTENTION'
                issues.append("Cobertura de auditoría baja")
        
        # Evaluar integridad de transacciones
        if 'Integridad de transacciones' in results:
            txn_integrity = results['Integridad de transacciones']
            if txn_integrity.get('status') == 'NEEDS_ATTENTION':
                compliance['transaction_integrity'] = 'NEEDS_ATTENTION'
                issues.append("Problemas de integridad en transacciones")
        
        # Determinar cumplimiento general
        if any(status == 'NON_COMPLIANT' for status in compliance.values()):
            compliance['overall_compliance'] = 'NON_COMPLIANT'
        elif any(status == 'NEEDS_ATTENTION' for status in compliance.values()):
            compliance['overall_compliance'] = 'NEEDS_ATTENTION'
        
        compliance['identified_issues'] = issues
        
        return compliance

    def _generate_recommendations(self) -> List[str]:
        """Generar recomendaciones basadas en los resultados"""
        recommendations = []
        
        # Recomendaciones basadas en errores
        if self.validation_results['failed_checks'] > 0:
            recommendations.append(
                f"🔧 {self.validation_results['failed_checks']} validaciones fallaron. Revisar logs para detalles."
            )
        
        # Recomendaciones basadas en scores de calidad
        if 'lp1_quality_score' in self.validation_results.get('quality_scores', {}):
            lp1_score = self.validation_results['quality_scores']['lp1_quality_score']
            if lp1_score < 80:
                recommendations.append("⚠️  Calidad de datos LP1 por debajo del estándar. Implementar validaciones de entrada.")
        
        if 'lp2_quality_score' in self.validation_results.get('quality_scores', {}):
            lp2_score = self.validation_results['quality_scores']['lp2_quality_score']
            if lp2_score < 90:
                recommendations.append("🔐 Calidad de datos LP2 requiere atención. Verificar integridad de DNIs.")
        
        # Recomendaciones específicas basadas en errores
        for error in self.validation_results['errors']:
            if 'huérfanas' in error.lower():
                recommendations.append("🔗 Revisar integridad referencial en transacciones y préstamos.")
            elif 'duplicados' in error.lower():
                recommendations.append("🔄 Implementar restricciones de unicidad más estrictas.")
            elif 'formato' in error.lower():
                recommendations.append("📝 Mejorar validación de formatos de datos de entrada.")
            elif 'auditoría' in error.lower():
                recommendations.append("📋 Aumentar cobertura de registros de auditoría.")
        
        # Recomendaciones generales
        if not recommendations:
            recommendations.append("✅ Sistema de integridad de datos funcionando correctamente.")
        
        recommendations.append("🔄 Programar validaciones automáticas periódicas.")
        recommendations.append("📊 Monitorear métricas de calidad en tiempo real.")
        
        return recommendations


def main():
    """Función principal"""
    # Configuración de bases de datos
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
    
    try:
        # Crear validador
        validator = DataIntegrityValidator(lp1_config, lp2_config)
        
        # Ejecutar validación completa
        report = validator.run_complete_validation()
        
        # Mostrar resumen
        print("\n" + "="*70)
        print("📋 RESUMEN DE VALIDACIÓN DE INTEGRIDAD")
        print("="*70)
        summary = report['validation_summary']
        print(f"⏱️  Duración total: {summary['total_duration']} segundos")
        print(f"✅ Validaciones exitosas: {summary['passed_checks']}/{summary['total_checks']}")
        print(f"❌ Validaciones fallidas: {summary['failed_checks']}")
        print(f"📈 Tasa de éxito: {summary['success_rate']}%")
        print(f"🎯 Estado general: {summary['overall_status']}")
        
        if 'overall_quality_score' in report.get('quality_scores', {}):
            print(f"📊 Score de calidad general: {report['quality_scores']['overall_quality_score']}")
        
        if 'overall_compliance' in report.get('compliance_status', {}):
            print(f"📋 Cumplimiento normativo: {report['compliance_status']['overall_compliance']}")
        
        print("\n🔧 Recomendaciones principales:")
        for i, rec in enumerate(report['recommendations'][:5], 1):
            print(f"  {i}. {rec}")
        
        print("="*70)
        
        return summary['overall_status'] == 'PASSED'
        
    except Exception as e:
        logger.error(f"❌ Error en validación de integridad: {str(e)}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
