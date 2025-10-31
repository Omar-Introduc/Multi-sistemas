#!/usr/bin/env python3
"""
=============================================================================
MONITOR DE REDIS - SISTEMA DISTRIBUIDO SHIBASITO
Monitoreo completo de métricas, performance y alertas para Redis
=============================================================================

Funcionalidades:
- Métricas en tiempo real de Redis
- Monitoreo de memoria y performance
- Alertas automáticas por umbral
- Dashboard web para visualización
- Reportes de salud del sistema
- Exportación de métricas para Prometheus/Grafana
"""

import redis
import psutil
import time
import json
import logging
import threading
from datetime import datetime, timedelta
from collections import deque
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
import argparse
import sys
import os
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional
import socket
import subprocess

# =============================================================================
# CONFIGURACIÓN
# =============================================================================

@dataclass
class RedisConfig:
    """Configuración de conexión a Redis"""
    host: str = 'localhost'
    port: int = 6379
    password: str = 'redispass123_secure_2024'
    db: int = 0
    socket_timeout: float = 5.0
    socket_connect_timeout: float = 5.0

@dataclass
class AlertConfig:
    """Configuración de alertas"""
    max_memory_percent: float = 85.0
    max_latency_ms: float = 100.0
    max_connections: int = 8000
    min_disk_space_mb: int = 1000
    alert_email: str = ""
    smtp_server: str = "localhost"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""

@dataclass
class MonitoringConfig:
    """Configuración general del monitoreo"""
    update_interval: int = 30  # segundos
    history_size: int = 100   # número de puntos de historial
    log_file: str = "/var/log/redis/monitoring.log"
    metrics_file: str = "/var/log/redis/metrics.json"
    alert_file: str = "/var/log/redis/alerts.log"
    web_port: int = 8080

# =============================================================================
# CLASE PRINCIPAL DE MONITOREO
# =============================================================================

class RedisMonitor:
    """Monitor completo de Redis con métricas avanzadas"""
    
    def __init__(self, redis_config: RedisConfig, alert_config: AlertConfig, 
                 monitoring_config: MonitoringConfig):
        self.redis_config = redis_config
        self.alert_config = alert_config
        self.monitoring_config = monitoring_config
        
        # Conexión a Redis
        self.r = redis.Redis(
            host=redis_config.host,
            port=redis_config.port,
            password=redis_config.password,
            db=redis_config.db,
            socket_timeout=redis_config.socket_timeout,
            socket_connect_timeout=redis_config.socket_connect_timeout,
            decode_responses=True
        )
        
        # Historiales de métricas
        self.memory_history = deque(maxlen=monitoring_config.history_size)
        self.cpu_history = deque(maxlen=monitoring_config.history_size)
        self.connection_history = deque(maxlen=monitoring_config.history_size)
        self.latency_history = deque(maxlen=monitoring_config.history_size)
        
        # Estado de alertas
        self.alert_state = {}
        self.alerts_log = []
        
        # Control de hilos
        self.running = False
        self.threads = []
        
        # Configurar logging
        self._setup_logging()
        
    def _setup_logging(self):
        """Configurar sistema de logging"""
        log_format = '%(asctime)s - %(levelname)s - %(message)s'
        
        # Crear directorio de logs si no existe
        os.makedirs(os.path.dirname(self.monitoring_config.log_file), exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format=log_format,
            handlers=[
                logging.FileHandler(self.monitoring_config.log_file),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger(__name__)
    
    # =============================================================================
    # MÉTRICAS DE REDIS
    # =============================================================================
    
    def get_redis_info(self) -> Dict:
        """Obtener información completa de Redis"""
        try:
            info = self.r.info()
            return info
        except redis.ConnectionError as e:
            self.logger.error(f"Error conectando a Redis: {e}")
            return {}
        except Exception as e:
            self.logger.error(f"Error obteniendo info de Redis: {e}")
            return {}
    
    def get_memory_metrics(self) -> Dict:
        """Obtener métricas de memoria específicas"""
        info = self.get_redis_info()
        if not info:
            return {}
        
        return {
            'used_memory': info.get('used_memory', 0),
            'used_memory_human': info.get('used_memory_human', '0B'),
            'used_memory_rss': info.get('used_memory_rss', 0),
            'used_memory_peak': info.get('used_memory_peak', 0),
            'mem_fragmentation_ratio': info.get('mem_fragmentation_ratio', 0),
            'maxmemory': info.get('maxmemory', 0),
            'maxmemory_policy': info.get('maxmemory_policy', 'unknown')
        }
    
    def get_performance_metrics(self) -> Dict:
        """Obtener métricas de performance"""
        info = self.get_redis_info()
        if not info:
            return {}
        
        return {
            'instantaneous_ops_per_sec': info.get('instantaneous_ops_per_sec', 0),
            'total_commands_processed': info.get('total_commands_processed', 0),
            'total_connections_received': info.get('total_connections_received', 0),
            'connected_clients': info.get('connected_clients', 0),
            'keyspace_hits': info.get('keyspace_hits', 0),
            'keyspace_misses': info.get('keyspace_misses', 0),
            'expired_keys': info.get('expired_keys', 0),
            'evicted_keys': info.get('evicted_keys', 0)
        }
    
    def get_persistence_metrics(self) -> Dict:
        """Obtener métricas de persistencia"""
        info = self.get_redis_info()
        if not info:
            return {}
        
        # Métricas RDB
        rdb_info = info.get('rdb_bgsave_in_progress', {})
        
        return {
            'rdb_bgsave_in_progress': info.get('rdb_bgsave_in_progress', 0),
            'rdb_last_save_time': info.get('rdb_last_save_time', 0),
            'rdb_last_bgsave_status': info.get('rdb_last_bgsave_status', 'unknown'),
            'rdb_changes_since_last_save': info.get('rdb_changes_since_last_save', 0),
            'aof_rewrite_in_progress': info.get('aof_rewrite_in_progress', 0),
            'aof_last_rewrite_status': info.get('aof_last_rewrite_status', 'unknown'),
            'aof_last_write_status': info.get('aof_last_write_status', 'unknown')
        }
    
    # =============================================================================
    # MÉTRICAS DEL SISTEMA
    # =============================================================================
    
    def get_system_metrics(self) -> Dict:
        """Obtener métricas del sistema operativo"""
        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            
            # Memoria del sistema
            memory = psutil.virtual_memory()
            
            # Disco
            disk = psutil.disk_usage('/')
            
            # Red
            network = psutil.net_io_counters()
            
            # Proceso Redis específico (si existe)
            redis_processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                if 'redis' in proc.info['name'].lower():
                    redis_processes.append({
                        'pid': proc.info['pid'],
                        'name': proc.info['name'],
                        'cpu_percent': proc.info['cpu_percent'],
                        'memory_percent': proc.info['memory_percent']
                    })
            
            return {
                'cpu': {
                    'percent': cpu_percent,
                    'count': cpu_count
                },
                'memory': {
                    'total': memory.total,
                    'available': memory.available,
                    'percent': memory.percent,
                    'used': memory.used,
                    'free': memory.free
                },
                'disk': {
                    'total': disk.total,
                    'used': disk.used,
                    'free': disk.free,
                    'percent': (disk.used / disk.total) * 100
                },
                'network': {
                    'bytes_sent': network.bytes_sent,
                    'bytes_recv': network.bytes_recv,
                    'packets_sent': network.packets_sent,
                    'packets_recv': network.packets_recv
                },
                'redis_processes': redis_processes
            }
        except Exception as e:
            self.logger.error(f"Error obteniendo métricas del sistema: {e}")
            return {}
    
    # =============================================================================
    # TEST DE LATENCIA
    # =============================================================================
    
    def test_latency(self, iterations: int = 100) -> Dict:
        """Probar latencia de Redis"""
        latencies = []
        
        try:
            start_time = time.time()
            
            for _ in range(iterations):
                ping_start = time.time()
                result = self.r.ping()
                ping_end = time.time()
                
                if result:
                    latency_ms = (ping_end - ping_start) * 1000
                    latencies.append(latency_ms)
            
            end_time = time.time()
            
            if latencies:
                return {
                    'test_duration_ms': (end_time - start_time) * 1000,
                    'iterations': iterations,
                    'success_count': len(latencies),
                    'min_latency_ms': min(latencies),
                    'max_latency_ms': max(latencies),
                    'avg_latency_ms': sum(latencies) / len(latencies),
                    'latencies': latencies
                }
            else:
                return {
                    'error': 'No se pudieron obtener mediciones de latencia'
                }
                
        except Exception as e:
            self.logger.error(f"Error probando latencia: {e}")
            return {'error': str(e)}
    
    # =============================================================================
    # VERIFICACIÓN DE SALUD
    # =============================================================================
    
    def health_check(self) -> Dict:
        """Verificar salud general de Redis"""
        health_status = {
            'timestamp': datetime.now().isoformat(),
            'overall_status': 'unknown',
            'checks': {}
        }
        
        try:
            # Test básico de conectividad
            try:
                ping_result = self.r.ping()
                health_status['checks']['connectivity'] = {
                    'status': 'ok' if ping_result else 'fail',
                    'message': 'Redis responde al ping'
                }
            except Exception as e:
                health_status['checks']['connectivity'] = {
                    'status': 'fail',
                    'message': f'Error de conectividad: {e}'
                }
                health_status['overall_status'] = 'critical'
                return health_status
            
            # Test de escritura/lectura
            try:
                test_key = 'monitor_test_key'
                self.r.set(test_key, 'test_value', ex=10)
                test_value = self.r.get(test_key)
                self.r.delete(test_key)
                
                health_status['checks']['read_write'] = {
                    'status': 'ok' if test_value == 'test_value' else 'fail',
                    'message': 'Operaciones de lectura/escritura funcionando'
                }
            except Exception as e:
                health_status['checks']['read_write'] = {
                    'status': 'fail',
                    'message': f'Error en operaciones de lectura/escritura: {e}'
                }
                health_status['overall_status'] = 'critical'
            
            # Verificar memoria
            memory_metrics = self.get_memory_metrics()
            if memory_metrics:
                used_memory_percent = (memory_metrics['used_memory'] / memory_metrics['maxmemory']) * 100 if memory_metrics['maxmemory'] > 0 else 0
                if used_memory_percent > self.alert_config.max_memory_percent:
                    health_status['checks']['memory'] = {
                        'status': 'warning',
                        'message': f'Uso de memoria alto: {used_memory_percent:.1f}%'
                    }
                else:
                    health_status['checks']['memory'] = {
                        'status': 'ok',
                        'message': f'Uso de memoria normal: {used_memory_percent:.1f}%'
                    }
            
            # Verificar conexiones
            performance_metrics = self.get_performance_metrics()
            if performance_metrics and performance_metrics.get('connected_clients', 0) > self.alert_config.max_connections:
                health_status['checks']['connections'] = {
                    'status': 'warning',
                    'message': f'Muchas conexiones: {performance_metrics["connected_clients"]}'
                }
            else:
                health_status['checks']['connections'] = {
                    'status': 'ok',
                    'message': 'Número de conexiones normal'
                }
            
            # Determinar estado general
            critical_failures = [check for check in health_status['checks'].values() 
                               if check['status'] == 'fail']
            warnings = [check for check in health_status['checks'].values() 
                       if check['status'] == 'warning']
            
            if critical_failures:
                health_status['overall_status'] = 'critical'
            elif warnings:
                health_status['overall_status'] = 'warning'
            else:
                health_status['overall_status'] = 'ok'
                
        except Exception as e:
            health_status['overall_status'] = 'error'
            health_status['error'] = str(e)
            self.logger.error(f"Error en health check: {e}")
        
        return health_status
    
    # =============================================================================
    # SISTEMA DE ALERTAS
    # =============================================================================
    
    def check_alerts(self) -> List[Dict]:
        """Verificar condiciones de alerta"""
        alerts = []
        current_time = datetime.now()
        
        # Verificar uso de memoria
        memory_metrics = self.get_memory_metrics()
        if memory_metrics and memory_metrics.get('maxmemory', 0) > 0:
            memory_percent = (memory_metrics['used_memory'] / memory_metrics['maxmemory']) * 100
            
            if memory_percent > self.alert_config.max_memory_percent:
                alert_key = 'high_memory'
                alert = {
                    'timestamp': current_time.isoformat(),
                    'type': 'memory',
                    'severity': 'high' if memory_percent > 95 else 'medium',
                    'message': f'Uso de memoria alto: {memory_percent:.1f}%',
                    'value': memory_percent,
                    'threshold': self.alert_config.max_memory_percent
                }
                
                if alert_key not in self.alert_state or self.alert_state[alert_key] != 'active':
                    alerts.append(alert)
                    self.alert_state[alert_key] = 'active'
                else:
                    self.alert_state[alert_key] = 'active'
        
        # Verificar latencia
        latency_test = self.test_latency(10)
        if 'avg_latency_ms' in latency_test:
            if latency_test['avg_latency_ms'] > self.alert_config.max_latency_ms:
                alert_key = 'high_latency'
                alert = {
                    'timestamp': current_time.isoformat(),
                    'type': 'performance',
                    'severity': 'medium' if latency_test['avg_latency_ms'] < 500 else 'high',
                    'message': f'Latencia alta: {latency_test["avg_latency_ms"]:.1f}ms',
                    'value': latency_test['avg_latency_ms'],
                    'threshold': self.alert_config.max_latency_ms
                }
                
                if alert_key not in self.alert_state or self.alert_state[alert_key] != 'active':
                    alerts.append(alert)
                    self.alert_state[alert_key] = 'active'
                else:
                    self.alert_state[alert_key] = 'active'
        
        # Verificar conexiones
        performance_metrics = self.get_performance_metrics()
        if performance_metrics:
            connected_clients = performance_metrics.get('connected_clients', 0)
            if connected_clients > self.alert_config.max_connections:
                alert_key = 'high_connections'
                alert = {
                    'timestamp': current_time.isoformat(),
                    'type': 'connections',
                    'severity': 'medium',
                    'message': f'Muchas conexiones: {connected_clients}',
                    'value': connected_clients,
                    'threshold': self.alert_config.max_connections
                }
                
                if alert_key not in self.alert_state or self.alert_state[alert_key] != 'active':
                    alerts.append(alert)
                    self.alert_state[alert_key] = 'active'
                else:
                    self.alert_state[alert_key] = 'active'
        
        # Verificar espacio en disco
        system_metrics = self.get_system_metrics()
        if system_metrics:
            disk_free_mb = system_metrics.get('disk', {}).get('free', 0) / (1024 * 1024)
            if disk_free_mb < self.alert_config.min_disk_space_mb:
                alert_key = 'low_disk_space'
                alert = {
                    'timestamp': current_time.isoformat(),
                    'type': 'system',
                    'severity': 'high',
                    'message': f'Espacio en disco bajo: {disk_free_mb:.0f}MB disponibles',
                    'value': disk_free_mb,
                    'threshold': self.alert_config.min_disk_space_mb
                }
                
                if alert_key not in self.alert_state or self.alert_state[alert_key] != 'active':
                    alerts.append(alert)
                    self.alert_state[alert_key] = 'active'
                else:
                    self.alert_state[alert_key] = 'active'
        
        return alerts
    
    def send_email_alert(self, alert: Dict):
        """Enviar alerta por email"""
        if not self.alert_config.alert_email:
            return
        
        try:
            msg = MimeMultipart()
            msg['From'] = self.alert_config.smtp_user
            msg['To'] = self.alert_config.alert_email
            msg['Subject'] = f"ALERTA REDIS - {alert['severity'].upper()}: {alert['type']}"
            
            body = f"""
Alerta del Sistema de Monitoreo de Redis
            
Tipo: {alert['type']}
Severidad: {alert['severity']}
Mensaje: {alert['message']}
Timestamp: {alert['timestamp']}
Valor actual: {alert['value']}
Umbral configurado: {alert['threshold']}

Sistema Distribuido Shibasito
Monitoreo Redis
"""
            
            msg.attach(MimeText(body, 'plain'))
            
            server = smtplib.SMTP(self.alert_config.smtp_server, self.alert_config.smtp_port)
            server.starttls()
            server.login(self.alert_config.smtp_user, self.alert_config.smtp_password)
            server.send_message(msg)
            server.quit()
            
            self.logger.info(f"Alerta enviada por email: {alert['message']}")
            
        except Exception as e:
            self.logger.error(f"Error enviando email de alerta: {e}")
    
    def process_alerts(self):
        """Procesar y enviar alertas"""
        alerts = self.check_alerts()
        
        for alert in alerts:
            self.logger.warning(f"ALERTA: {alert['message']}")
            self.alerts_log.append(alert)
            
            # Enviar por email si está configurado
            if self.alert_config.alert_email:
                self.send_email_alert(alert)
            
            # Log de alertas
            with open(self.monitoring_config.alert_file, 'a') as f:
                f.write(f"{alert['timestamp']} - {alert['type']}: {alert['message']}\n")
    
    # =============================================================================
    # COLECCIÓN DE MÉTRICAS
    # =============================================================================
    
    def collect_metrics(self) -> Dict:
        """Recopilar todas las métricas actuales"""
        timestamp = datetime.now()
        
        # Métricas de Redis
        redis_info = self.get_redis_info()
        memory_metrics = self.get_memory_metrics()
        performance_metrics = self.get_performance_metrics()
        persistence_metrics = self.get_persistence_metrics()
        
        # Métricas del sistema
        system_metrics = self.get_system_metrics()
        
        # Test de latencia
        latency_metrics = self.test_latency(5)
        
        # Compilar métricas
        metrics = {
            'timestamp': timestamp.isoformat(),
            'redis': {
                'info': redis_info,
                'memory': memory_metrics,
                'performance': performance_metrics,
                'persistence': persistence_metrics,
                'latency': latency_metrics
            },
            'system': system_metrics
        }
        
        # Actualizar historiales
        if memory_metrics:
            self.memory_history.append({
                'timestamp': timestamp.isoformat(),
                'used_memory': memory_metrics.get('used_memory', 0),
                'max_memory': memory_metrics.get('maxmemory', 0)
            })
        
        if performance_metrics:
            self.connection_history.append({
                'timestamp': timestamp.isoformat(),
                'connected_clients': performance_metrics.get('connected_clients', 0),
                'ops_per_sec': performance_metrics.get('instantaneous_ops_per_sec', 0)
            })
        
        if 'avg_latency_ms' in latency_metrics:
            self.latency_history.append({
                'timestamp': timestamp.isoformat(),
                'avg_latency_ms': latency_metrics['avg_latency_ms']
            })
        
        if system_metrics:
            self.cpu_history.append({
                'timestamp': timestamp.isoformat(),
                'cpu_percent': system_metrics.get('cpu', {}).get('percent', 0),
                'memory_percent': system_metrics.get('memory', {}).get('percent', 0)
            })
        
        return metrics
    
    def save_metrics(self, metrics: Dict):
        """Guardar métricas en archivo"""
        try:
            with open(self.monitoring_config.metrics_file, 'w') as f:
                json.dump(metrics, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error guardando métricas: {e}")
    
    # =============================================================================
    # DASHBOARD WEB
    # =============================================================================
    
    def start_web_dashboard(self):
        """Iniciar dashboard web básico"""
        try:
            from http.server import HTTPServer, BaseHTTPRequestHandler
            import urllib.parse
            
            class DashboardHandler(BaseHTTPRequestHandler):
                def do_GET(self):
                    if self.path == '/':
                        self.serve_dashboard()
                    elif self.path == '/metrics':
                        self.serve_metrics_json()
                    elif self.path == '/health':
                        self.serve_health_json()
                    else:
                        self.send_error(404)
                
                def serve_dashboard(self):
                    """Servir página principal del dashboard"""
                    html = self.generate_dashboard_html()
                    
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write(html.encode())
                
                def serve_metrics_json(self):
                    """Servir métricas en formato JSON"""
                    metrics = self.server.monitor.collect_metrics()
                    
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps(metrics, indent=2).encode())
                
                def serve_health_json(self):
                    """Servir health check en formato JSON"""
                    health = self.server.monitor.health_check()
                    
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps(health, indent=2).encode())
                
                def generate_dashboard_html(self):
                    """Generar HTML del dashboard"""
                    return """
<!DOCTYPE html>
<html>
<head>
    <title>Redis Monitor - Shibasito</title>
    <meta charset="utf-8">
    <meta http-equiv="refresh" content="30">
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { background: #d32f2f; color: white; padding: 20px; border-radius: 5px; margin-bottom: 20px; }
        .metrics { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
        .metric-card { background: white; padding: 20px; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .metric-title { font-weight: bold; color: #333; margin-bottom: 10px; }
        .metric-value { font-size: 24px; font-weight: bold; color: #d32f2f; }
        .status-ok { color: #4caf50; }
        .status-warning { color: #ff9800; }
        .status-error { color: #f44336; }
        .health-status { padding: 15px; border-radius: 5px; margin: 20px 0; }
        .health-ok { background: #e8f5e8; border: 1px solid #4caf50; }
        .health-warning { background: #fff3e0; border: 1px solid #ff9800; }
        .health-error { background: #ffebee; border: 1px solid #f44336; }
        .timestamp { color: #666; font-size: 12px; margin-top: 10px; }
    </style>
    <script>
        function refreshMetrics() {
            fetch('/metrics')
                .then(response => response.json())
                .then(data => updateDashboard(data))
                .catch(error => console.error('Error:', error));
        }
        
        function updateDashboard(data) {
            // Actualizar métricas en tiempo real
            document.getElementById('memory-usage').textContent = 
                data.redis.memory.used_memory_human || 'N/A';
            document.getElementById('connections').textContent = 
                data.redis.performance.connected_clients || 'N/A';
            document.getElementById('ops-per-sec').textContent = 
                data.redis.performance.instantaneous_ops_per_sec || 'N/A';
            document.getElementById('cpu-usage').textContent = 
                (data.system.cpu?.percent || 0).toFixed(1) + '%';
            
            const timestamp = new Date(data.timestamp).toLocaleString();
            document.getElementById('last-update').textContent = timestamp;
        }
        
        // Actualizar cada 30 segundos
        setInterval(refreshMetrics, 30000);
        window.onload = refreshMetrics;
    </script>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Redis Monitor - Sistema Distribuido Shibasito</h1>
            <p>Monitoreo en tiempo real de Redis</p>
        </div>
        
        <div class="health-status" id="health-status">
            <h3>Estado del Sistema</h3>
            <p id="health-message">Verificando...</p>
        </div>
        
        <div class="metrics">
            <div class="metric-card">
                <div class="metric-title">💾 Memoria Usada</div>
                <div class="metric-value" id="memory-usage">Cargando...</div>
            </div>
            
            <div class="metric-card">
                <div class="metric-title">🔗 Conexiones Activas</div>
                <div class="metric-value" id="connections">Cargando...</div>
            </div>
            
            <div class="metric-card">
                <div class="metric-title">⚡ Operaciones/seg</div>
                <div class="metric-value" id="ops-per-sec">Cargando...</div>
            </div>
            
            <div class="metric-card">
                <div class="metric-title">🖥️ CPU del Sistema</div>
                <div class="metric-value" id="cpu-usage">Cargando...</div>
            </div>
        </div>
        
        <div class="timestamp">
            Última actualización: <span id="last-update">Cargando...</span>
        </div>
        
        <div class="metric-card" style="margin-top: 20px;">
            <h3>🔗 Enlaces Útiles</h3>
            <p><a href="/metrics">📊 Métricas JSON</a> | <a href="/health">🏥 Health Check</a></p>
        </div>
    </div>
</body>
</html>
"""
            
            # Configurar servidor HTTP
            httpd = HTTPServer(('0.0.0.0', self.monitoring_config.web_port), DashboardHandler)
            httpd.monitor = self  # Pasar referencia al monitor
            
            self.logger.info(f"Dashboard web disponible en http://localhost:{self.monitoring_config.web_port}")
            httpd.serve_forever()
            
        except ImportError:
            self.logger.warning("Módulo HTTP no disponible, dashboard web deshabilitado")
        except Exception as e:
            self.logger.error(f"Error iniciando dashboard web: {e}")
    
    # =============================================================================
    # EXPORTACIÓN PARA PROMHEUS
    # =============================================================================
    
    def generate_prometheus_metrics(self) -> str:
        """Generar métricas en formato Prometheus"""
        metrics = self.collect_metrics()
        prometheus_output = []
        
        # Métricas de Redis
        redis_info = metrics.get('redis', {})
        
        if redis_info.get('performance'):
            perf = redis_info['performance']
            prometheus_output.append(f'redis_connected_clients {perf.get("connected_clients", 0)}')
            prometheus_output.append(f'redis_ops_per_second {perf.get("instantaneous_ops_per_sec", 0)}')
            prometheus_output.append(f'redis_total_commands_processed {perf.get("total_commands_processed", 0)}')
        
        if redis_info.get('memory'):
            mem = redis_info['memory']
            prometheus_output.append(f'redis_used_memory_bytes {mem.get("used_memory", 0)}')
            prometheus_output.append(f'redis_used_memory_rss_bytes {mem.get("used_memory_rss", 0)}')
            prometheus_output.append(f'redis_maxmemory_bytes {mem.get("maxmemory", 0)}')
        
        # Métricas del sistema
        system_metrics = metrics.get('system', {})
        
        if system_metrics.get('cpu'):
            prometheus_output.append(f'system_cpu_percent {system_metrics["cpu"].get("percent", 0)}')
        
        if system_metrics.get('memory'):
            prometheus_output.append(f'system_memory_percent {system_metrics["memory"].get("percent", 0)}')
            prometheus_output.append(f'system_memory_available_bytes {system_metrics["memory"].get("available", 0)}')
        
        return '\n'.join(prometheus_output) + '\n'
    
    # =============================================================================
    # LOOP PRINCIPAL DE MONITOREO
    # =============================================================================
    
    def start_monitoring(self):
        """Iniciar monitoreo continuo"""
        self.running = True
        self.logger.info("=== INICIANDO MONITOREO DE REDIS ===")
        
        # Hilo para dashboard web
        dashboard_thread = threading.Thread(target=self.start_web_dashboard, daemon=True)
        dashboard_thread.start()
        self.threads.append(dashboard_thread)
        
        try:
            while self.running:
                # Recopilar métricas
                metrics = self.collect_metrics()
                
                # Guardar métricas
                self.save_metrics(metrics)
                
                # Procesar alertas
                self.process_alerts()
                
                # Log de métricas importantes
                if metrics.get('redis', {}).get('performance'):
                    perf = metrics['redis']['performance']
                    self.logger.info(
                        f"Ops/sec: {perf.get('instantaneous_ops_per_sec', 0)}, "
                        f"Conexiones: {perf.get('connected_clients', 0)}"
                    )
                
                # Esperar siguiente iteración
                time.sleep(self.monitoring_config.update_interval)
                
        except KeyboardInterrupt:
            self.logger.info("Deteniendo monitoreo por interrupción de usuario")
        except Exception as e:
            self.logger.error(f"Error en monitoreo: {e}")
        finally:
            self.stop_monitoring()
    
    def stop_monitoring(self):
        """Detener monitoreo"""
        self.running = False
        self.logger.info("=== DETENIENDO MONITOREO ===")
        
        # Esperar a que terminen los hilos
        for thread in self.threads:
            if thread.is_alive():
                thread.join(timeout=5)

# =============================================================================
# FUNCIONES DE UTILIDAD
# =============================================================================

def create_default_config():
    """Crear configuración por defecto"""
    redis_config = RedisConfig()
    alert_config = AlertConfig()
    monitoring_config = MonitoringConfig()
    
    return redis_config, alert_config, monitoring_config

def load_config_from_file(config_file: str):
    """Cargar configuración desde archivo JSON"""
    try:
        with open(config_file, 'r') as f:
            config_data = json.load(f)
        
        redis_config = RedisConfig(**config_data.get('redis', {}))
        alert_config = AlertConfig(**config_data.get('alerts', {}))
        monitoring_config = MonitoringConfig(**config_data.get('monitoring', {}))
        
        return redis_config, alert_config, monitoring_config
    except Exception as e:
        logging.error(f"Error cargando configuración: {e}")
        return create_default_config()

def main():
    """Función principal"""
    parser = argparse.ArgumentParser(description='Monitor de Redis para Sistema Shibasito')
    parser.add_argument('--config', '-c', help='Archivo de configuración JSON')
    parser.add_argument('--host', default='localhost', help='Host de Redis')
    parser.add_argument('--port', type=int, default=6379, help='Puerto de Redis')
    parser.add_argument('--password', help='Contraseña de Redis')
    parser.add_argument('--web-port', type=int, default=8080, help='Puerto del dashboard web')
    parser.add_argument('--interval', type=int, default=30, help='Intervalo de monitoreo en segundos')
    parser.add_argument('--test', action='store_true', help='Ejecutar solo test de conectividad')
    parser.add_argument('--prometheus', action='store_true', help='Generar métricas para Prometheus')
    parser.add_argument('--health-check', action='store_true', help='Ejecutar health check y salir')
    
    args = parser.parse_args()
    
    # Cargar o crear configuración
    if args.config and os.path.exists(args.config):
        redis_config, alert_config, monitoring_config = load_config_from_file(args.config)
    else:
        redis_config, alert_config, monitoring_config = create_default_config()
        
        # Aplicar argumentos de línea de comandos
        redis_config.host = args.host
        redis_config.port = args.port
        if args.password:
            redis_config.password = args.password
        monitoring_config.web_port = args.web_port
        monitoring_config.update_interval = args.interval
    
    # Crear monitor
    monitor = RedisMonitor(redis_config, alert_config, monitoring_config)
    
    if args.test:
        # Solo test de conectividad
        health = monitor.health_check()
        print(json.dumps(health, indent=2))
        return
    
    if args.health_check:
        # Solo health check
        health = monitor.health_check()
        print(json.dumps(health, indent=2))
        return
    
    if args.prometheus:
        # Generar métricas para Prometheus
        metrics = monitor.generate_prometheus_metrics()
        print(metrics)
        return
    
    # Iniciar monitoreo completo
    try:
        monitor.start_monitoring()
    except KeyboardInterrupt:
        print("\nMonitoreo detenido por el usuario")
    except Exception as e:
        print(f"Error fatal: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()