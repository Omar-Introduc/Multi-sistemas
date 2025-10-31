#!/bin/bash

###############################################################################
# Script: generate-validation-report.py
# Descripción: Generador de reportes de validación automática
# Autor: Sistema de Validación Continua
# Fecha: 2025-10-30
###############################################################################

import json
import argparse
import datetime
from pathlib import Path
from typing import Dict, List, Optional
import subprocess
import os

def load_json_file(file_path: str) -> Optional[Dict]:
    """Cargar archivo JSON si existe."""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Warning: No se pudo cargar {file_path}: {e}")
        return None

def generate_html_report(data: Dict, output_file: str):
    """Generar reporte HTML con los datos de validación."""
    
    html_template = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reporte de Validación - {data.get('environment', 'N/A')}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 8px;
        }}
        .status-badge {{
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            color: white;
            font-weight: bold;
            margin: 5px;
        }}
        .status-success {{ background-color: #28a745; }}
        .status-warning {{ background-color: #ffc107; color: #212529; }}
        .status-error {{ background-color: #dc3545; }}
        .status-info {{ background-color: #17a2b8; }}
        
        .section {{
            margin: 30px 0;
            padding: 20px;
            border-left: 4px solid #007bff;
            background: #f8f9fa;
        }}
        .section h3 {{
            margin-top: 0;
            color: #007bff;
        }}
        
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .metric-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            text-align: center;
        }}
        .metric-value {{
            font-size: 2em;
            font-weight: bold;
            color: #007bff;
        }}
        .metric-label {{
            color: #6c757d;
            margin-top: 5px;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #f8f9fa;
            font-weight: bold;
        }}
        .progress-bar {{
            width: 100%;
            height: 20px;
            background-color: #e9ecef;
            border-radius: 10px;
            overflow: hidden;
        }}
        .progress-fill {{
            height: 100%;
            background-color: #007bff;
            transition: width 0.3s ease;
        }}
        .footer {{
            text-align: center;
            margin-top: 40px;
            padding: 20px;
            border-top: 1px solid #ddd;
            color: #6c757d;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏥 Reporte de Validación Continua</h1>
            <p>Entorno: <strong>{data.get('environment', 'N/A')}</strong></p>
            <p>Generado: <strong>{datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</strong></p>
        </div>
        
        <div class="section">
            <h3>📊 Resumen Ejecutivo</h3>
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-value">{data.get('total_checks', 0)}</div>
                    <div class="metric-label">Total de Chequeos</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{data.get('passed_checks', 0)}</div>
                    <div class="metric-label">Chequeos Exitosos</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{data.get('failed_checks', 0)}</div>
                    <div class="metric-label">Chequeos Fallidos</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{data.get('success_rate', 0):.1f}%</div>
                    <div class="metric-label">Tasa de Éxito</div>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h3>🎯 Estado del Sistema</h3>
            <p><strong>Estado General:</strong> 
                <span class="status-badge status-{data.get('overall_status', 'unknown').lower()}">
                    {data.get('overall_status', 'DESCONOCIDO').upper()}
                </span>
            </p>
            <p><strong>Última Actualización:</strong> {data.get('last_update', 'N/A')}</p>
            <p><strong>Tiempo de Validación:</strong> {data.get('duration_seconds', 0)} segundos</p>
            
            <div class="progress-bar">
                <div class="progress-fill" style="width: {data.get('success_rate', 0):.1f}%"></div>
            </div>
        </div>
        
        <div class="section">
            <h3>🏗️ Validaciones por Componente</h3>
            <table>
                <thead>
                    <tr>
                        <th>Componente</th>
                        <th>Estado</th>
                        <th>Tiempo de Respuesta</th>
                        <th>Detalles</th>
                    </tr>
                </thead>
                <tbody>
"""
    
    # Agregar filas de componentes
    for component, status in data.get('components', {}).items():
        status_class = 'success' if status.get('status') == 'healthy' else 'warning' if status.get('status') == 'degraded' else 'error'
        response_time = status.get('response_time_ms', 'N/A')
        details = status.get('details', 'Sin detalles')
        
        html_template += f"""
                    <tr>
                        <td>{component}</td>
                        <td><span class="status-badge status-{status_class}">{status.get('status', 'UNKNOWN').upper()}</span></td>
                        <td>{response_time} ms</td>
                        <td>{details}</td>
                    </tr>
"""
    
    html_template += """
                </tbody>
            </table>
        </div>
        
        <div class="section">
            <h3>📈 Métricas de Performance</h3>
            <table>
                <thead>
                    <tr>
                        <th>Métrica</th>
                        <th>Valor</th>
                        <th>Threshold</th>
                        <th>Estado</th>
                    </tr>
                </thead>
                <tbody>
"""
    
    # Agregar métricas de performance
    for metric, value in data.get('performance_metrics', {}).items():
        threshold = data.get('thresholds', {}).get(metric, 'N/A')
        status = 'success' if value <= threshold else 'warning'
        
        html_template += f"""
                    <tr>
                        <td>{metric.replace('_', ' ').title()}</td>
                        <td>{value}</td>
                        <td>{threshold}</td>
                        <td><span class="status-badge status-{status}">OK</span></td>
                    </tr>
"""
    
    html_template += f"""
                </tbody>
            </table>
        </div>
        
        <div class="section">
            <h3>🔒 Validaciones de Seguridad</h3>
            <table>
                <thead>
                    <tr>
                        <th>Tipo de Validación</th>
                        <th>Estado</th>
                        <th>Vulnerabilidades</th>
                        <th>Recomendaciones</th>
                    </tr>
                </thead>
                <tbody>
"""
    
    # Agregar validaciones de seguridad
    for check, result in data.get('security_checks', {}).items():
        vuln_count = result.get('vulnerabilities', 0)
        status = 'success' if vuln_count == 0 else 'warning'
        
        html_template += f"""
                    <tr>
                        <td>{check.replace('_', ' ').title()}</td>
                        <td><span class="status-badge status-{status}">{'SAFE' if vuln_count == 0 else 'ISSUES'}</span></td>
                        <td>{vuln_count}</td>
                        <td>{', '.join(result.get('recommendations', []))}</td>
                    </tr>
"""
    
    html_template += f"""
                </tbody>
            </table>
        </div>
        
        <div class="section">
            <h3>📝 Logs y Detalles</h3>
            <p><strong>Archivo de Log:</strong> {data.get('log_file', 'N/A')}</p>
            <p><strong>Commit SHA:</strong> {data.get('commit_sha', 'N/A')}</p>
            <p><strong>Branch:</strong> {data.get('branch', 'N/A')}</p>
            <p><strong>Pipeline ID:</strong> {data.get('pipeline_id', 'N/A')}</p>
        </div>
        
        <div class="footer">
            <p>🤖 Generado automáticamente por el Sistema de Validación Continua</p>
            <p>Para más detalles, consultar los logs del sistema y el dashboard de monitoreo.</p>
        </div>
    </div>
</body>
</html>
"""
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_template)
    
    print(f"✅ Reporte HTML generado: {output_file}")

def generate_json_report(data: Dict, output_file: str):
    """Generar reporte JSON con los datos de validación."""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Reporte JSON generado: {output_file}")

def generate_markdown_report(data: Dict, output_file: str):
    """Generar reporte Markdown con los datos de validación."""
    
    markdown_content = f"""# 📋 Reporte de Validación Continua

## Información General
- **Entorno**: {data.get('environment', 'N/A')}
- **Fecha**: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
- **Estado**: {data.get('overall_status', 'DESCONOCIDO')}
- **Duración**: {data.get('duration_seconds', 0)} segundos

## 📊 Resumen de Resultados
- **Total de Chequeos**: {data.get('total_checks', 0)}
- **Chequeos Exitosos**: {data.get('passed_checks', 0)}
- **Chequeos Fallidos**: {data.get('failed_checks', 0)}
- **Tasa de Éxito**: {data.get('success_rate', 0):.1f}%

## 🏗️ Estado de Componentes
"""
    
    for component, status in data.get('components', {}).items():
        status_emoji = "✅" if status.get('status') == 'healthy' else "⚠️" if status.get('status') == 'degraded' else "❌"
        markdown_content += f"- **{component}**: {status_emoji} {status.get('status', 'UNKNOWN')} ({status.get('response_time_ms', 'N/A')} ms)\n"
    
    markdown_content += f"""
## 📈 Métricas de Performance
"""
    
    for metric, value in data.get('performance_metrics', {}).items():
        threshold = data.get('thresholds', {}).get(metric, 'N/A')
        markdown_content += f"- **{metric.replace('_', ' ').title()}**: {value} (Threshold: {threshold})\n"
    
    markdown_content += f"""
## 🔒 Validaciones de Seguridad
"""
    
    for check, result in data.get('security_checks', {}).items():
        vuln_count = result.get('vulnerabilities', 0)
        status_emoji = "✅" if vuln_count == 0 else "⚠️"
        markdown_content += f"- **{check.replace('_', ' ').title()}**: {status_emoji} {vuln_count} vulnerabilidades\n"
    
    markdown_content += f"""
## 📝 Detalles Técnicos
- **Commit SHA**: {data.get('commit_sha', 'N/A')}
- **Branch**: {data.get('branch', 'N/A')}
- **Pipeline ID**: {data.get('pipeline_id', 'N/A')}
- **Archivo de Log**: {data.get('log_file', 'N/A')}

---
*Generado automáticamente por el Sistema de Validación Continua*
"""
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    
    print(f"✅ Reporte Markdown generado: {output_file}")

def main():
    parser = argparse.ArgumentParser(description='Generador de Reportes de Validación')
    parser.add_argument('--pipeline-id', required=True, help='ID del pipeline')
    parser.add_argument('--commit', required=True, help='Commit SHA')
    parser.add_argument('--branch', required=True, help='Nombre del branch')
    parser.add_argument('--environment', required=True, help='Entorno')
    parser.add_argument('--output', required=True, help='Archivo de salida')
    parser.add_argument('--format', choices=['html', 'json', 'markdown', 'all'], default='html', help='Formato del reporte')
    
    args = parser.parse_args()
    
    # Crear datos de ejemplo para el reporte
    report_data = {
        'pipeline_id': args.pipeline_id,
        'commit_sha': args.commit,
        'branch': args.branch,
        'environment': args.environment,
        'timestamp': datetime.datetime.now().isoformat(),
        'last_update': datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
        'duration_seconds': 300,
        'total_checks': 10,
        'passed_checks': 9,
        'failed_checks': 1,
        'success_rate': 90.0,
        'overall_status': 'healthy',
        'log_file': f'validation-{args.pipeline_id}.log',
        'components': {
            'database': {'status': 'healthy', 'response_time_ms': 25, 'details': 'Conexión establecida'},
            'redis': {'status': 'healthy', 'response_time_ms': 2, 'details': 'Cache funcionando'},
            'rabbitmq': {'status': 'healthy', 'response_time_ms': 15, 'details': 'Colas activas'},
            'app': {'status': 'degraded', 'response_time_ms': 2500, 'details': 'Latencia alta detectada'}
        },
        'performance_metrics': {
            'response_time_p95_ms': 1800,
            'response_time_p99_ms': 3200,
            'requests_per_second': 150,
            'error_rate_percent': 0.5,
            'cpu_usage_percent': 65,
            'memory_usage_percent': 72
        },
        'thresholds': {
            'response_time_p95_ms': 2000,
            'response_time_p99_ms': 5000,
            'requests_per_second': 100,
            'error_rate_percent': 1.0,
            'cpu_usage_percent': 80,
            'memory_usage_percent': 85
        },
        'security_checks': {
            'dependency_scan': {'status': 'safe', 'vulnerabilities': 0, 'recommendations': []},
            'static_analysis': {'status': 'warning', 'vulnerabilities': 2, 'recommendations': ['Code review required']},
            'configuration_check': {'status': 'safe', 'vulnerabilities': 0, 'recommendations': []}
        }
    }
    
    # Generar reportes en los formatos solicitados
    base_name = args.output.replace(Path(args.output).suffix, '')
    
    if args.format in ['html', 'all']:
        generate_html_report(report_data, f'{base_name}.html')
    
    if args.format in ['json', 'all']:
        generate_json_report(report_data, f'{base_name}.json')
    
    if args.format in ['markdown', 'all']:
        generate_markdown_report(report_data, f'{base_name}.md')
    
    print(f"🎉 Reportes generados exitosamente para el pipeline {args.pipeline_id}")

if __name__ == '__main__':
    main()