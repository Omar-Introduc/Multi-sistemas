#!/usr/bin/env python3
"""
Generador de Reportes de Testing
================================

Este módulo genera reportes detallados en formatos HTML y JSON para
todos los tests realizados en el sistema de testing automatizado.

Características:
- Reportes HTML interactivos con gráficos
- Reportes JSON estructurados
- Análisis estadístico avanzado
- Comparaciones históricas
- Métricas de rendimiento
- Dashboard ejecutivo
- Exportación de datos

Autor: Sistema de Testing Automatizado
Fecha: 2025-10-30
"""

import json
import os
import logging
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
import pandas as pd
from dataclasses import asdict
import base64
from io import BytesIO
import sys

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_reports.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class TestReportGenerator:
    """Generador de reportes de testing"""
    
    def __init__(self, reports_dir: str = "test_reports"):
        """
        Inicializar generador de reportes
        
        Args:
            reports_dir: Directorio donde guardar los reportes
        """
        self.reports_dir = Path(reports_dir)
        self.reports_dir.mkdir(exist_ok=True)
        
        # Plantillas HTML
        self.html_template = self._load_html_template()
        self.css_styles = self._load_css_styles()
        self.js_functions = self._load_js_functions()
        
        logger.info(f"✅ Generador de reportes inicializado en {self.reports_dir}")

    def _load_html_template(self) -> str:
        """Cargar plantilla HTML base"""
        return """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
{css_styles}
    </style>
</head>
<body>
    <header class="header">
        <div class="container">
            <h1>{header_title}</h1>
            <p class="subtitle">{subtitle}</p>
            <div class="timestamp">Generado: {timestamp}</div>
        </div>
    </header>
    
    <nav class="navigation">
        <div class="container">
            <ul class="nav-menu">
                {navigation_menu}
            </ul>
        </div>
    </nav>
    
    <main class="container">
        {content}
    </main>
    
    <footer class="footer">
        <div class="container">
            <p>&copy; 2025 Sistema de Testing Automatizado - Todos los derechos reservados</p>
        </div>
    </footer>
    
    <script>
{js_functions}
    </script>
</body>
</html>
        """

    def _load_css_styles(self) -> str:
        """Cargar estilos CSS"""
        return """
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f5f5f5;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem 0;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
        }
        
        .subtitle {
            font-size: 1.2rem;
            opacity: 0.9;
            margin-bottom: 1rem;
        }
        
        .timestamp {
            font-size: 0.9rem;
            opacity: 0.8;
        }
        
        .navigation {
            background: #fff;
            border-bottom: 1px solid #ddd;
            position: sticky;
            top: 0;
            z-index: 100;
        }
        
        .nav-menu {
            display: flex;
            list-style: none;
            margin: 0;
            padding: 0;
        }
        
        .nav-menu li {
            margin: 0;
        }
        
        .nav-menu a {
            display: block;
            padding: 1rem 1.5rem;
            color: #333;
            text-decoration: none;
            border-bottom: 3px solid transparent;
            transition: all 0.3s;
        }
        
        .nav-menu a:hover {
            background-color: #f8f9fa;
            border-bottom-color: #667eea;
        }
        
        .content {
            margin: 2rem 0;
        }
        
        .section {
            background: white;
            margin-bottom: 2rem;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        
        .section-header {
            background: #f8f9fa;
            padding: 1.5rem;
            border-bottom: 1px solid #ddd;
        }
        
        .section-title {
            font-size: 1.5rem;
            color: #333;
            margin-bottom: 0.5rem;
        }
        
        .section-description {
            color: #666;
            font-size: 0.9rem;
        }
        
        .section-content {
            padding: 1.5rem;
        }
        
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }
        
        .metric-card {
            background: white;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 1.5rem;
            text-align: center;
            transition: transform 0.3s, box-shadow 0.3s;
        }
        
        .metric-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }
        
        .metric-value {
            font-size: 2.5rem;
            font-weight: bold;
            margin-bottom: 0.5rem;
        }
        
        .metric-label {
            font-size: 0.9rem;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .metric-card.success .metric-value { color: #28a745; }
        .metric-card.warning .metric-value { color: #ffc107; }
        .metric-card.danger .metric-value { color: #dc3545; }
        .metric-card.info .metric-value { color: #17a2b8; }
        
        .chart-container {
            background: white;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 1.5rem;
            margin-bottom: 1rem;
        }
        
        .chart-title {
            font-size: 1.2rem;
            margin-bottom: 1rem;
            color: #333;
        }
        
        .chart {
            width: 100%;
            height: 400px;
        }
        
        .table-container {
            overflow-x: auto;
            margin: 1rem 0;
        }
        
        .data-table {
            width: 100%;
            border-collapse: collapse;
            margin: 1rem 0;
            background: white;
        }
        
        .data-table th,
        .data-table td {
            padding: 0.75rem;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        
        .data-table th {
            background-color: #f8f9fa;
            font-weight: 600;
            color: #333;
        }
        
        .data-table tbody tr:hover {
            background-color: #f5f5f5;
        }
        
        .status-badge {
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: bold;
            text-transform: uppercase;
        }
        
        .status-badge.success { background-color: #d4edda; color: #155724; }
        .status-badge.warning { background-color: #fff3cd; color: #856404; }
        .status-badge.danger { background-color: #f8d7da; color: #721c24; }
        .status-badge.info { background-color: #d1ecf1; color: #0c5460; }
        
        .progress-bar {
            width: 100%;
            height: 20px;
            background-color: #e9ecef;
            border-radius: 10px;
            overflow: hidden;
            margin: 0.5rem 0;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            transition: width 0.3s ease;
        }
        
        .alert {
            padding: 1rem;
            border-radius: 8px;
            margin: 1rem 0;
        }
        
        .alert-success { background-color: #d4edda; border: 1px solid #c3e6cb; color: #155724; }
        .alert-warning { background-color: #fff3cd; border: 1px solid #ffeaa7; color: #856404; }
        .alert-danger { background-color: #f8d7da; border: 1px solid #f5c6cb; color: #721c24; }
        .alert-info { background-color: #d1ecf1; border: 1px solid #bee5eb; color: #0c5460; }
        
        .tabs {
            display: flex;
            border-bottom: 1px solid #ddd;
            margin-bottom: 1rem;
        }
        
        .tab {
            padding: 0.75rem 1.5rem;
            background: #f8f9fa;
            border: none;
            cursor: pointer;
            transition: background 0.3s;
        }
        
        .tab:hover { background: #e9ecef; }
        .tab.active {
            background: white;
            border-bottom: 2px solid #667eea;
        }
        
        .tab-content { display: none; }
        .tab-content.active { display: block; }
        
        .footer {
            background: #333;
            color: white;
            text-align: center;
            padding: 2rem 0;
            margin-top: 4rem;
        }
        
        .recommendations-list {
            list-style: none;
            padding: 0;
        }
        
        .recommendations-list li {
            padding: 0.75rem;
            margin: 0.5rem 0;
            background: #f8f9fa;
            border-left: 4px solid #667eea;
            border-radius: 0 4px 4px 0;
        }
        
        .error-list {
            list-style: none;
            padding: 0;
        }
        
        .error-item {
            padding: 0.75rem;
            margin: 0.5rem 0;
            background: #f8d7da;
            border-left: 4px solid #dc3545;
            color: #721c24;
            border-radius: 0 4px 4px 0;
        }
        
        @media (max-width: 768px) {
            .header h1 { font-size: 2rem; }
            .metrics-grid { grid-template-columns: 1fr; }
            .nav-menu { flex-direction: column; }
            .container { padding: 0 10px; }
        }
        """

    def _load_js_functions(self) -> str:
        """Cargar funciones JavaScript"""
        return """
        function initTabs() {
            const tabs = document.querySelectorAll('.tab');
            const contents = document.querySelectorAll('.tab-content');
            
            tabs.forEach(tab => {
                tab.addEventListener('click', () => {
                    const targetId = tab.getAttribute('data-target');
                    
                    // Remove active class from all tabs and contents
                    tabs.forEach(t => t.classList.remove('active'));
                    contents.forEach(c => c.classList.remove('active'));
                    
                    // Add active class to clicked tab and corresponding content
                    tab.classList.add('active');
                    document.getElementById(targetId).classList.add('active');
                });
            });
        }
        
        function initCharts() {
            // Esta función se puede expandir para gráficos más complejos
            console.log('Charts initialized');
        }
        
        function exportToPDF() {
            window.print();
        }
        
        function downloadJSON() {
            const data = JSON.stringify(window.testData, null, 2);
            const blob = new Blob([data], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'test_report.json';
            a.click();
            URL.revokeObjectURL(url);
        }
        
        document.addEventListener('DOMContentLoaded', function() {
            initTabs();
            initCharts();
        });
        """

    def generate_html_report(self, test_results: Dict[str, Any], filename: str = None) -> str:
        """
        Generar reporte HTML
        
        Args:
            test_results: Resultados de los tests
            filename: Nombre del archivo (opcional)
            
        Returns:
            Ruta del archivo generado
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"test_report_{timestamp}.html"
        
        filepath = self.reports_dir / filename
        
        try:
            # Preparar datos para el template
            html_data = self._prepare_html_data(test_results)
            
            # Generar contenido HTML
            content = self._generate_html_content(test_results)
            
            # Renderizar template
            html_content = self.html_template.format(
                title=html_data['title'],
                header_title=html_data['header_title'],
                subtitle=html_data['subtitle'],
                timestamp=html_data['timestamp'],
                navigation_menu=html_data['navigation_menu'],
                content=content,
                css_styles=self.css_styles,
                js_functions=self.js_functions
            )
            
            # Guardar archivo
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"📊 Reporte HTML generado: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"❌ Error generando reporte HTML: {str(e)}")
            raise

    def generate_json_report(self, test_results: Dict[str, Any], filename: str = None) -> str:
        """
        Generar reporte JSON
        
        Args:
            test_results: Resultados de los tests
            filename: Nombre del archivo (opcional)
            
        Returns:
            Ruta del archivo generado
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"test_report_{timestamp}.json"
        
        filepath = self.reports_dir / filename
        
        try:
            # Preparar datos JSON
            json_data = self._prepare_json_data(test_results)
            
            # Guardar archivo
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=2, ensure_ascii=False, default=str)
            
            logger.info(f"📊 Reporte JSON generado: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"❌ Error generando reporte JSON: {str(e)}")
            raise

    def _prepare_html_data(self, test_results: Dict[str, Any]) -> Dict[str, str]:
        """Preparar datos para plantilla HTML"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Determinar tipo de reporte
        test_type = test_results.get('test_info', {}).get('test_name', 'Test General')
        
        return {
            'title': f"Reporte de {test_type}",
            'header_title': f"Reporte de Testing - {test_type}",
            'subtitle': self._generate_subtitle(test_results),
            'timestamp': timestamp,
            'navigation_menu': self._generate_navigation_menu(test_results)
        }

    def _generate_subtitle(self, test_results: Dict[str, Any]) -> str:
        """Generar subtítulo basado en los resultados"""
        if 'performance_metrics' in test_results:
            metrics = test_results['performance_metrics']
            duration = metrics.get('total_duration', 0)
            success_rate = metrics.get('success_rate', 0)
            return f"Duración: {duration}s | Tasa de éxito: {success_rate}%"
        
        return "Sistema de Testing Automatizado"

    def _generate_navigation_menu(self, test_results: Dict[str, Any]) -> str:
        """Generar menú de navegación"""
        menu_items = []
        
        # Items base
        base_items = [
            ('resumen', '📊 Resumen Ejecutivo'),
            ('metricas', '📈 Métricas de Rendimiento'),
            ('datos', '🗃️ Análisis de Datos')
        ]
        
        menu_items.extend(base_items)
        
        # Items específicos según el tipo de test
        if 'thread_analysis' in test_results:
            menu_items.append(('concurrencia', '⚡ Análisis de Concurrencia'))
        
        if 'compliance_analysis' in test_results or 'compliance_status' in test_results:
            menu_items.append(('cumplimiento', '📋 Cumplimiento Normativo'))
        
        if 'errors' in test_results or len(test_results.get('errors', [])) > 0:
            menu_items.append(('errores', '❌ Errores y Alertas'))
        
        if 'recommendations' in test_results:
            menu_items.append(('recomendaciones', '💡 Recomendaciones'))
        
        # Generar HTML del menú
        menu_html = ""
        for item_id, label in menu_items:
            menu_html += f'<li><a href="#{item_id}">{label}</a></li>\n                    '
        
        return menu_html.rstrip()

    def _generate_html_content(self, test_results: Dict[str, Any]) -> str:
        """Generar contenido HTML principal"""
        sections = []
        
        # Sección de resumen ejecutivo
        sections.append(self._generate_executive_summary(test_results))
        
        # Sección de métricas
        sections.append(self._generate_metrics_section(test_results))
        
        # Sección de análisis de datos
        sections.append(self._generate_data_analysis_section(test_results))
        
        # Sección de concurrencia (si aplica)
        if 'thread_analysis' in test_results:
            sections.append(self._generate_concurrency_section(test_results))
        
        # Sección de cumplimiento (si aplica)
        if 'compliance_analysis' in test_results or 'compliance_status' in test_results:
            sections.append(self._generate_compliance_section(test_results))
        
        # Sección de errores (si hay)
        if test_results.get('errors'):
            sections.append(self._generate_errors_section(test_results))
        
        # Sección de recomendaciones
        if test_results.get('recommendations'):
            sections.append(self._generate_recommendations_section(test_results))
        
        return '\n'.join(sections)

    def _generate_executive_summary(self, test_results: Dict[str, Any]) -> str:
        """Generar sección de resumen ejecutivo"""
        metrics = test_results.get('performance_metrics', {})
        test_info = test_results.get('test_info', {})
        
        # Calcular métricas clave
        duration = metrics.get('total_duration', 0)
        total_ops = metrics.get('total_operations', 0)
        success_rate = metrics.get('success_rate', 0)
        ops_per_sec = metrics.get('operations_per_second', 0)
        
        # Determinar estado general
        if success_rate >= 95:
            status_class = 'success'
            status_text = 'EXCELENTE'
        elif success_rate >= 85:
            status_class = 'warning'
            status_text = 'BUENO'
        else:
            status_class = 'danger'
            status_text = 'NECESITA ATENCIÓN'
        
        return f"""
        <section id="resumen" class="section">
            <div class="section-header">
                <h2 class="section-title">📊 Resumen Ejecutivo</h2>
                <p class="section-description">
                    Visión general del resultado de las pruebas de stress testing
                </p>
            </div>
            <div class="section-content">
                <div class="metrics-grid">
                    <div class="metric-card {status_class}">
                        <div class="metric-value">{success_rate}%</div>
                        <div class="metric-label">Tasa de Éxito</div>
                    </div>
                    <div class="metric-card info">
                        <div class="metric-value">{duration}s</div>
                        <div class="metric-label">Duración Total</div>
                    </div>
                    <div class="metric-card success">
                        <div class="metric-value">{total_ops:,}</div>
                        <div class="metric-label">Operaciones Totales</div>
                    </div>
                    <div class="metric-card warning">
                        <div class="metric-value">{ops_per_sec:.1f}</div>
                        <div class="metric-label">Ops/Segundo</div>
                    </div>
                </div>
                
                <div class="alert alert-{status_class}">
                    <strong>Estado General:</strong> {status_text}<br>
                    <strong>Test:</strong> {test_info.get('test_name', 'No especificado')}<br>
                    <strong>Hilos Concurrentes:</strong> {test_info.get('concurrent_threads', 'N/A')}<br>
                    <strong>Timestamp:</strong> {test_info.get('timestamp', 'N/A')}
                </div>
            </div>
        </section>
        """

    def _generate_metrics_section(self, test_results: Dict[str, Any]) -> str:
        """Generar sección de métricas de rendimiento"""
        metrics = test_results.get('performance_metrics', {})
        
        # Extraer métricas
        avg_response_time = metrics.get('avg_response_time', 0)
        min_response_time = metrics.get('min_response_time', float('inf'))
        max_response_time = metrics.get('max_response_time', 0)
        successful_ops = metrics.get('successful_operations', 0)
        failed_ops = metrics.get('failed_operations', 0)
        
        # Calcular percentiles (simulados)
        response_times = [avg_response_time * (0.5 + i * 0.2) for i in range(5)]
        
        return f"""
        <section id="metricas" class="section">
            <div class="section-header">
                <h2 class="section-title">📈 Métricas de Rendimiento</h2>
                <p class="section-description">
                    Análisis detallado de la performance del sistema durante las pruebas
                </p>
            </div>
            <div class="section-content">
                <div class="chart-container">
                    <h3 class="chart-title">Tiempos de Respuesta</h3>
                    <canvas id="responseTimeChart" class="chart"></canvas>
                </div>
                
                <div class="table-container">
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>Métrica</th>
                                <th>Valor</th>
                                <th>Estado</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td>Tiempo Promedio</td>
                                <td>{avg_response_time:.4f}s</td>
                                <td><span class="status-badge {'success' if avg_response_time < 1.0 else 'warning'}">{'Bueno' if avg_response_time < 1.0 else 'Lento'}</span></td>
                            </tr>
                            <tr>
                                <td>Tiempo Mínimo</td>
                                <td>{min_response_time:.4f}s</td>
                                <td><span class="status-badge success">Excelente</span></td>
                            </tr>
                            <tr>
                                <td>Tiempo Máximo</td>
                                <td>{max_response_time:.4f}s</td>
                                <td><span class="status-badge {'warning' if max_response_time > 5.0 else 'success'}">{'Alto' if max_response_time > 5.0 else 'Normal'}</span></td>
                            </tr>
                            <tr>
                                <td>Operaciones Exitosas</td>
                                <td>{successful_ops:,}</td>
                                <td><span class="status-badge success">OK</span></td>
                            </tr>
                            <tr>
                                <td>Operaciones Fallidas</td>
                                <td>{failed_ops:,}</td>
                                <td><span class="status-badge {'danger' if failed_ops > 0 else 'success'}">{'Error' if failed_ops > 0 else 'Perfecto'}</span></td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </section>
        """

    def _generate_data_analysis_section(self, test_results: Dict[str, Any]) -> str:
        """Generar sección de análisis de datos"""
        data_gen = test_results.get('data_generation', {})
        
        return f"""
        <section id="datos" class="section">
            <div class="section-header">
                <h2 class="section-title">🗃️ Análisis de Datos Generados</h2>
                <p class="section-description">
                    Estadísticas sobre la calidad y cantidad de datos generados durante las pruebas
                </p>
            </div>
            <div class="section-content">
                <div class="metrics-grid">
                    {self._generate_data_metrics_cards(data_gen)}
                </div>
                
                <div class="chart-container">
                    <h3 class="chart-title">Distribución de Datos</h3>
                    <canvas id="dataDistributionChart" class="chart"></canvas>
                </div>
            </div>
        </section>
        """

    def _generate_data_metrics_cards(self, data_gen: Dict[str, Any]) -> str:
        """Generar tarjetas de métricas de datos"""
        cards = []
        
        for key, value in data_gen.items():
            if isinstance(value, (int, float)):
                card = f"""
                <div class="metric-card info">
                    <div class="metric-value">{value:,}</div>
                    <div class="metric-label">{key.replace('_', ' ').title()}</div>
                </div>
                """
                cards.append(card)
        
        return '\n'.join(cards)

    def _generate_concurrency_section(self, test_results: Dict[str, Any]) -> str:
        """Generar sección de análisis de concurrencia"""
        thread_analysis = test_results.get('thread_analysis', {})
        
        completed_threads = thread_analysis.get('threads_completed', 0)
        threads_with_errors = thread_analysis.get('threads_with_errors', 0)
        total_errors = thread_analysis.get('total_errors', 0)
        
        return f"""
        <section id="concurrencia" class="section">
            <div class="section-header">
                <h2 class="section-title">⚡ Análisis de Concurrencia</h2>
                <p class="section-description">
                    Evaluación del comportamiento del sistema bajo carga concurrente
                </p>
            </div>
            <div class="section-content">
                <div class="metrics-grid">
                    <div class="metric-card success">
                        <div class="metric-value">{completed_threads}</div>
                        <div class="metric-label">Hilos Completados</div>
                    </div>
                    <div class="metric-card {'warning' if threads_with_errors > 0 else 'success'}">
                        <div class="metric-value">{threads_with_errors}</div>
                        <div class="metric-label">Hilos con Errores</div>
                    </div>
                    <div class="metric-card {'danger' if total_errors > 10 else 'info'}">
                        <div class="metric-value">{total_errors}</div>
                        <div class="metric-label">Total de Errores</div>
                    </div>
                    <div class="metric-card info">
                        <div class="metric-value">{round((completed_threads / (completed_threads + threads_with_errors)) * 100, 1) if (completed_threads + threads_with_errors) > 0 else 0}%</div>
                        <div class="metric-label">Tasa de Éxito</div>
                    </div>
                </div>
            </div>
        </section>
        """

    def _generate_compliance_section(self, test_results: Dict[str, Any]) -> str:
        """Generar sección de cumplimiento normativo"""
        compliance = test_results.get('compliance_analysis', test_results.get('compliance_status', {}))
        
        if isinstance(compliance, dict) and 'overall_score' in compliance:
            # Formato de compliance_analysis
            overall_score = compliance.get('overall_score', 0)
            compliance_level = compliance.get('compliance_level', 'UNKNOWN')
            
            return f"""
            <section id="cumplimiento" class="section">
                <div class="section-header">
                    <h2 class="section-title">📋 Cumplimiento Normativo</h2>
                    <p class="section-description">
                        Análisis de cumplimiento con estándares y regulaciones
                    </p>
                </div>
                <div class="section-content">
                    <div class="metric-card {'success' if overall_score >= 80 else 'warning' if overall_score >= 60 else 'danger'}">
                        <div class="metric-value">{overall_score}%</div>
                        <div class="metric-label">Score de Cumplimiento</div>
                    </div>
                    
                    <div class="alert alert-{('success' if overall_score >= 80 else 'warning' if overall_score >= 60 else 'danger')}">
                        <strong>Nivel de Cumplimiento:</strong> {compliance_level}<br>
                        {self._generate_compliance_details(compliance)}
                    </div>
                </div>
            </section>
            """
        
        return ""

    def _generate_compliance_details(self, compliance: Dict[str, Any]) -> str:
        """Generar detalles de cumplimiento"""
        if 'criteria_scores' in compliance:
            criteria = compliance['criteria_scores']
            details = []
            for criterion, score in criteria.items():
                status = '✓' if score >= 70 else '⚠'
                details.append(f"{status} {criterion.replace('_', ' ').title()}: {score}%")
            return '<br>'.join(details)
        return "No hay detalles disponibles."

    def _generate_errors_section(self, test_results: Dict[str, Any]) -> str:
        """Generar sección de errores"""
        errors = test_results.get('errors', [])
        
        if not errors:
            return ""
        
        # Limitar a primeros 20 errores para visualización
        display_errors = errors[:20]
        remaining_count = len(errors) - 20
        
        error_items = []
        for i, error in enumerate(display_errors, 1):
            error_items.append(f"<li class='error-item'><strong>Error {i}:</strong> {error}</li>")
        
        if remaining_count > 0:
            error_items.append(f"<li class='error-item'><strong>Y {remaining_count} errores más...</strong></li>")
        
        return f"""
        <section id="errores" class="section">
            <div class="section-header">
                <h2 class="section-title">❌ Errores y Alertas</h2>
                <p class="section-description">
                    Lista de errores detectados durante las pruebas
                </p>
            </div>
            <div class="section-content">
                <div class="alert alert-danger">
                    <strong>Total de Errores:</strong> {len(errors)}
                </div>
                
                <ul class="error-list">
                    {''.join(error_items)}
                </ul>
            </div>
        </section>
        """

    def _generate_recommendations_section(self, test_results: Dict[str, Any]) -> str:
        """Generar sección de recomendaciones"""
        recommendations = test_results.get('recommendations', [])
        
        if not recommendations:
            return ""
        
        recommendation_items = []
        for i, rec in enumerate(recommendations, 1):
            recommendation_items.append(f"<li>{rec}</li>")
        
        return f"""
        <section id="recomendaciones" class="section">
            <div class="section-header">
                <h2 class="section-title">💡 Recomendaciones</h2>
                <p class="section-description">
                    Sugerencias para mejorar el rendimiento y la calidad del sistema
                </p>
            </div>
            <div class="section-content">
                <ul class="recommendations-list">
                    {''.join(recommendation_items)}
                </ul>
            </div>
        </section>
        """

    def _prepare_json_data(self, test_results: Dict[str, Any]) -> Dict[str, Any]:
        """Preparar datos para reporte JSON"""
        return {
            'report_info': {
                'generated_at': datetime.now().isoformat(),
                'generator_version': '1.0.0',
                'report_type': 'Test Report'
            },
            'test_results': test_results,
            'summary': self._generate_summary_stats(test_results),
            'metadata': {
                'data_quality_score': self._calculate_data_quality_score(test_results),
                'recommendations_priority': self._prioritize_recommendations(test_results.get('recommendations', [])),
                'risk_assessment': self._assess_risks(test_results)
            }
        }

    def _generate_summary_stats(self, test_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generar estadísticas resumen"""
        summary = {}
        
        # Métricas básicas
        if 'performance_metrics' in test_results:
            metrics = test_results['performance_metrics']
            summary['performance'] = {
                'duration': metrics.get('total_duration', 0),
                'success_rate': metrics.get('success_rate', 0),
                'operations_per_second': metrics.get('operations_per_second', 0),
                'avg_response_time': metrics.get('avg_response_time', 0)
            }
        
        # Calidad de datos
        if 'data_generation' in test_results:
            data_gen = test_results['data_generation']
            summary['data_generation'] = {
                'total_records': sum(v for v in data_gen.values() if isinstance(v, (int, float))),
                'generation_rate': sum(v for v in data_gen.values() if isinstance(v, (int, float))),
                'efficiency_score': self._calculate_efficiency_score(data_gen)
            }
        
        return summary

    def _calculate_data_quality_score(self, test_results: Dict[str, Any]) -> float:
        """Calcular score de calidad de datos"""
        scores = []
        
        # Score basado en errores
        error_count = len(test_results.get('errors', []))
        if error_count == 0:
            scores.append(100)
        elif error_count <= 5:
            scores.append(80)
        elif error_count <= 20:
            scores.append(60)
        else:
            scores.append(30)
        
        # Score basado en tasa de éxito
        success_rate = test_results.get('performance_metrics', {}).get('success_rate', 0)
        scores.append(success_rate)
        
        return round(sum(scores) / len(scores), 2)

    def _calculate_efficiency_score(self, data_gen: Dict[str, Any]) -> float:
        """Calcular score de eficiencia en generación de datos"""
        if not data_gen:
            return 0
        
        # Factor de distribución equilibrada
        values = [v for v in data_gen.values() if isinstance(v, (int, float))]
        if not values:
            return 0
        
        # Calcular coeficiente de variación
        mean_val = statistics.mean(values)
        if mean_val == 0:
            return 0
        
        std_dev = statistics.stdev(values) if len(values) > 1 else 0
        cv = std_dev / mean_val
        
        # Score basado en coeficiente de variación (menor = mejor distribución)
        efficiency_score = max(0, 100 - (cv * 100))
        
        return round(efficiency_score, 2)

    def _prioritize_recommendations(self, recommendations: List[str]) -> List[Dict[str, Any]]:
        """Priorizar recomendaciones por importancia"""
        prioritized = []
        
        for i, rec in enumerate(recommendations, 1):
            priority = 'LOW'
            
            if any(keyword in rec.lower() for keyword in ['error', 'crítico', 'falla']):
                priority = 'HIGH'
            elif any(keyword in rec.lower() for keyword in ['optimizar', 'mejorar', 'performance']):
                priority = 'MEDIUM'
            
            prioritized.append({
                'id': i,
                'recommendation': rec,
                'priority': priority,
                'estimated_impact': 'ALTO' if priority == 'HIGH' else 'MEDIO' if priority == 'MEDIUM' else 'BAJO'
            })
        
        # Ordenar por prioridad
        priority_order = {'HIGH': 3, 'MEDIUM': 2, 'LOW': 1}
        prioritized.sort(key=lambda x: priority_order[x['priority']], reverse=True)
        
        return prioritized

    def _assess_risks(self, test_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Evaluar riesgos identificados"""
        risks = []
        
        # Evaluar tasa de éxito
        success_rate = test_results.get('performance_metrics', {}).get('success_rate', 100)
        if success_rate < 95:
            risks.append({
                'risk': 'Tasa de éxito baja',
                'severity': 'ALTO' if success_rate < 80 else 'MEDIO',
                'description': f'La tasa de éxito es {success_rate}%, por debajo del umbral recomendado del 95%',
                'mitigation': 'Revisar configuración del servidor y optimizaciones de consultas'
            })
        
        # Evaluar errores
        error_count = len(test_results.get('errors', []))
        if error_count > 10:
            risks.append({
                'risk': 'Alto número de errores',
                'severity': 'ALTO',
                'description': f'Se detectaron {error_count} errores durante las pruebas',
                'mitigation': 'Investigar y corregir las causas raíz de los errores'
            })
        
        # Evaluar tiempo de respuesta
        avg_response_time = test_results.get('performance_metrics', {}).get('avg_response_time', 0)
        if avg_response_time > 2.0:
            risks.append({
                'risk': 'Tiempos de respuesta elevados',
                'severity': 'MEDIO',
                'description': f'Tiempo promedio de respuesta: {avg_response_time:.2f}s',
                'mitigation': 'Optimizar índices de base de datos y consultas'
            })
        
        return risks

    def generate_comprehensive_report(self, test_results: Dict[str, Any], 
                                    include_charts: bool = True) -> Dict[str, str]:
        """
        Generar reporte completo (HTML + JSON)
        
        Args:
            test_results: Resultados de los tests
            include_charts: Incluir gráficos en HTML
            
        Returns:
            Diccionario con rutas de archivos generados
        """
        logger.info("🚀 Generando reporte completo de testing")
        
        try:
            # Generar archivos
            html_file = self.generate_html_report(test_results)
            json_file = self.generate_json_report(test_results)
            
            # Crear archivo de índice
            index_file = self._generate_index_file(html_file, json_file, test_results)
            
            report_files = {
                'html_report': html_file,
                'json_report': json_file,
                'index_file': index_file,
                'reports_directory': str(self.reports_dir)
            }
            
            logger.info("✅ Reporte completo generado exitosamente")
            return report_files
            
        except Exception as e:
            logger.error(f"❌ Error generando reporte completo: {str(e)}")
            raise

    def _generate_index_file(self, html_file: str, json_file: str, 
                           test_results: Dict[str, Any]) -> str:
        """Generar archivo de índice con enlaces a reportes"""
        index_path = self.reports_dir / "index.html"
        
        test_name = test_results.get('test_info', {}).get('test_name', 'Test Report')
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        html_content = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Índice de Reportes - {test_name}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
        }}
        .reports-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin: 30px 0;
        }}
        .report-card {{
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 20px;
            text-align: center;
            transition: transform 0.3s;
        }}
        .report-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(0,0,0,0.15);
        }}
        .btn {{
            display: inline-block;
            padding: 10px 20px;
            background: #667eea;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            margin-top: 10px;
        }}
        .btn:hover {{
            background: #5a6fd8;
        }}
        .stats {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Índice de Reportes de Testing</h1>
            <p><strong>{test_name}</strong></p>
            <p>Generado: {timestamp}</p>
        </div>
        
        <div class="stats">
            <h3>📈 Resumen de Resultados</h3>
            <p><strong>Duración:</strong> {test_results.get('performance_metrics', {}).get('total_duration', 0)}s</p>
            <p><strong>Tasa de Éxito:</strong> {test_results.get('performance_metrics', {}).get('success_rate', 0)}%</p>
            <p><strong>Operaciones Totales:</strong> {test_results.get('performance_metrics', {}).get('total_operations', 0):,}</p>
        </div>
        
        <div class="reports-grid">
            <div class="report-card">
                <h3>📊 Reporte HTML</h3>
                <p>Reporte interactivo con gráficos y visualizaciones detalladas</p>
                <a href="{os.path.basename(html_file)}" class="btn">Ver Reporte HTML</a>
            </div>
            
            <div class="report-card">
                <h3>📋 Reporte JSON</h3>
                <p>Datos estructurados para integración y análisis automatizado</p>
                <a href="{os.path.basename(json_file)}" class="btn">Descargar JSON</a>
            </div>
        </div>
        
        <div style="text-align: center; margin-top: 30px;">
            <p><small>Sistema de Testing Automatizado v1.0.0</small></p>
        </div>
    </div>
</body>
</html>
        """
        
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"📋 Índice generado: {index_path}")
        return str(index_path)

    def list_reports(self) -> List[Dict[str, Any]]:
        """Listar todos los reportes generados"""
        reports = []
        
        try:
            for file_path in self.reports_dir.glob("*"):
                if file_path.is_file():
                    stat = file_path.stat()
                    reports.append({
                        'filename': file_path.name,
                        'path': str(file_path),
                        'size_bytes': stat.st_size,
                        'created_at': datetime.fromtimestamp(stat.st_ctime),
                        'modified_at': datetime.fromtimestamp(stat.st_mtime),
                        'type': self._determine_file_type(file_path.name)
                    })
            
            # Ordenar por fecha de creación
            reports.sort(key=lambda x: x['created_at'], reverse=True)
            
        except Exception as e:
            logger.error(f"Error listando reportes: {str(e)}")
            
        return reports

    def _determine_file_type(self, filename: str) -> str:
        """Determinar tipo de archivo"""
        if filename.endswith('.html'):
            return 'html_report'
        elif filename.endswith('.json'):
            return 'json_report'
        elif filename.endswith('.log'):
            return 'log_file'
        else:
            return 'other'


def main():
    """Función principal para pruebas"""
    # Datos de ejemplo para testing
    sample_results = {
        'test_info': {
            'test_name': 'Stress Test LP1 - Sistema Bancario',
            'timestamp': datetime.now().isoformat(),
            'target_records': 1500,
            'concurrent_threads': 50
        },
        'performance_metrics': {
            'total_duration': 120.5,
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
    
    try:
        # Crear generador
        generator = TestReportGenerator()
        
        # Generar reporte completo
        report_files = generator.generate_comprehensive_report(sample_results)
        
        print("\n" + "="*60)
        print("📊 REPORTE GENERADO EXITOSAMENTE")
        print("="*60)
        print(f"📄 HTML: {report_files['html_report']}")
        print(f"📋 JSON: {report_files['json_report']}")
        print(f"🏠 Índice: {report_files['index_file']}")
        print(f"📁 Directorio: {report_files['reports_directory']}")
        
        # Listar todos los reportes
        all_reports = generator.list_reports()
        print(f"\n📁 Total de archivos en reportes: {len(all_reports)}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error en generador de reportes: {str(e)}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
