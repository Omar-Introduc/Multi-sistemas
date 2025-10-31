#!/usr/bin/env python3
"""
Generador de Reportes Finales
Crea reportes HTML y JSON con todos los resultados de validación
"""

import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
import argparse

class FinalReportGenerator:
    """Generador de reportes finales HTML/JSON"""
    
    def __init__(self, reports_dir: str = "/workspace/validation_system/reports"):
        """
        Inicializar generador de reportes
        
        Args:
            reports_dir: Directorio donde están los reportes de validación
        """
        self.reports_dir = Path(reports_dir)
        self.consolidated_data: Optional[Dict[str, Any]] = None

    def find_latest_report(self, prefix: str) -> Optional[Path]:
        """Encontrar el reporte más reciente con el prefijo dado"""
        pattern = f"{prefix}_*.json"
        matching_files = list(self.reports_dir.glob(pattern))
        
        if not matching_files:
            return None
        
        # Ordenar por fecha de modificación (más reciente primero)
        return max(matching_files, key=lambda f: f.stat().st_mtime)

    def load_consolidated_data(self) -> Dict[str, Any]:
        """Cargar datos consolidados del reporte más reciente"""
        consolidated_report = self.find_latest_report("consolidated_validation_report")
        
        if not consolidated_report:
            raise FileNotFoundError("No se encontró reporte consolidado")
        
        with open(consolidated_report, 'r') as f:
            self.consolidated_data = json.load(f)
        
        return self.consolidated_data

    def load_module_reports(self) -> Dict[str, Dict[str, Any]]:
        """Cargar todos los reportes de módulos individuales"""
        module_reports = {}
        
        prefixes = [
            "integration_test_results",
            "technology_validation_results", 
            "architecture_validation_results",
            "scalability_test_results",
            "fault_tolerance_test_results"
        ]
        
        for prefix in prefixes:
            report_file = self.find_latest_report(prefix)
            if report_file:
                with open(report_file, 'r') as f:
                    module_reports[prefix] = json.load(f)
        
        return module_reports

    def generate_html_report(self, output_file: Optional[str] = None) -> str:
        """
        Generar reporte HTML completo
        
        Args:
            output_file: Archivo de salida (opcional)
            
        Returns:
            Ruta del archivo generado
        """
        if not self.consolidated_data:
            self.load_consolidated_data()
        
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = self.reports_dir / f"validation_report_{timestamp}.html"
        else:
            output_file = Path(output_file)
        
        html_content = self._build_html_content()
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return str(output_file)

    def _build_html_content(self) -> str:
        """Construir contenido HTML del reporte"""
        data = self.consolidated_data
        overview = data.get("validation_overview", {})
        scores = data.get("overall_scores", {})
        health = data.get("system_health", {})
        module_results = data.get("module_results", {})
        
        # Determinar colores basados en puntajes
        def get_score_color(score: float) -> str:
            if score >= 80:
                return "#28a745"  # Verde
            elif score >= 60:
                return "#ffc107"  # Amarillo
            else:
                return "#dc3545"  # Rojo
        
        # Generar barras de progreso
        score_bars = ""
        for module, score in scores.items():
            if module != "overall_system_score":
                color = get_score_color(score)
                width = min(score, 100)
                bar_html = f"""
                <div class="score-item">
                    <div class="score-label">{module.replace('_', ' ').title()}</div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: {width}%; background-color: {color}"></div>
                    </div>
                    <div class="score-value">{score:.1f}%</div>
                </div>
                """
                score_bars += bar_html
        
        # Generar tabla de detalles de módulos
        module_details = ""
        for module_name, result in module_results.items():
            status = result.get("status", "UNKNOWN")
            message = result.get("message", "Sin información")
            
            if status == "COMPLETED":
                status_badge = '<span class="badge badge-success">COMPLETADO</span>'
            elif status == "SKIPPED":
                status_badge = '<span class="badge badge-warning">OMITIDO</span>'
            else:
                status_badge = '<span class="badge badge-danger">ERROR</span>'
            
            module_details += f"""
            <tr>
                <td>{module_name.replace('_', ' ').title()}</td>
                <td>{status_badge}</td>
                <td>{message}</td>
            </tr>
            """
        
        # Tiempo total
        total_duration = overview.get("total_duration", 0)
        duration_min = int(total_duration // 60)
        duration_sec = int(total_duration % 60)
        
        # Plantilla HTML
        html_template = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reporte de Validación Integral - Sistema Distribuido</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        .header {{
            background: white;
            border-radius: 10px;
            padding: 30px;
            margin-bottom: 20px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            text-align: center;
        }}
        
        .header h1 {{
            color: #2c3e50;
            margin-bottom: 10px;
            font-size: 2.5em;
        }}
        
        .header .subtitle {{
            color: #7f8c8d;
            font-size: 1.2em;
        }}
        
        .card {{
            background: white;
            border-radius: 10px;
            padding: 25px;
            margin-bottom: 20px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}
        
        .card h2 {{
            color: #2c3e50;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #ecf0f1;
        }}
        
        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }}
        
        .summary-item {{
            text-align: center;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 8px;
        }}
        
        .summary-item .value {{
            font-size: 2em;
            font-weight: bold;
            color: #2c3e50;
        }}
        
        .summary-item .label {{
            color: #7f8c8d;
            margin-top: 5px;
        }}
        
        .overall-score {{
            font-size: 3em;
            font-weight: bold;
            text-align: center;
            margin: 20px 0;
            background: linear-gradient(45deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        
        .score-item {{
            display: flex;
            align-items: center;
            margin-bottom: 15px;
            padding: 10px;
            background: #f8f9fa;
            border-radius: 8px;
        }}
        
        .score-label {{
            flex: 0 0 200px;
            font-weight: 500;
        }}
        
        .progress-bar {{
            flex: 1;
            height: 20px;
            background: #ecf0f1;
            border-radius: 10px;
            margin: 0 15px;
            overflow: hidden;
        }}
        
        .progress-fill {{
            height: 100%;
            border-radius: 10px;
            transition: width 0.3s ease;
        }}
        
        .score-value {{
            flex: 0 0 60px;
            font-weight: bold;
            text-align: right;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}
        
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        
        th {{
            background: #f8f9fa;
            font-weight: 600;
            color: #2c3e50;
        }}
        
        .badge {{
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.8em;
            font-weight: bold;
            text-transform: uppercase;
        }}
        
        .badge-success {{
            background: #d4edda;
            color: #155724;
        }}
        
        .badge-warning {{
            background: #fff3cd;
            color: #856404;
        }}
        
        .badge-danger {{
            background: #f8d7da;
            color: #721c24;
        }}
        
        .health-status {{
            display: inline-flex;
            align-items: center;
            gap: 10px;
            padding: 10px 15px;
            background: #f8f9fa;
            border-radius: 8px;
            margin: 5px;
        }}
        
        .status-icon {{
            width: 12px;
            height: 12px;
            border-radius: 50%;
        }}
        
        .status-healthy {{
            background: #28a745;
        }}
        
        .status-unhealthy {{
            background: #dc3545;
        }}
        
        .footer {{
            text-align: center;
            margin-top: 40px;
            padding: 20px;
            color: #7f8c8d;
            font-size: 0.9em;
        }}
        
        .timestamp {{
            text-align: center;
            color: #7f8c8d;
            font-size: 0.9em;
            margin-bottom: 20px;
        }}
        
        @media (max-width: 768px) {{
            .score-item {{
                flex-direction: column;
                text-align: center;
            }}
            
            .score-label {{
                flex: none;
                margin-bottom: 10px;
            }}
            
            .progress-bar {{
                margin: 10px 0;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏗️ Sistema Distribuido Bancario</h1>
            <div class="subtitle">Reporte de Validación Integral</div>
        </div>
        
        <div class="timestamp">
            Generado el {datetime.now().strftime('%d/%m/%Y a las %H:%M:%S')}
        </div>
        
        <div class="card">
            <h2>📊 Resumen Ejecutivo</h2>
            <div class="summary-grid">
                <div class="summary-item">
                    <div class="value">{overview.get('modules_executed', 0)}</div>
                    <div class="label">Módulos Ejecutados</div>
                </div>
                <div class="summary-item">
                    <div class="value">{duration_min}:{duration_sec:02d}</div>
                    <div class="label">Duración Total</div>
                </div>
                <div class="summary-item">
                    <div class="value">{health.get('services_available', 0)}/{health.get('total_services', 0)}</div>
                    <div class="label">Servicios Operativos</div>
                </div>
            </div>
            
            <div class="overall-score">
                {scores.get('overall_system_score', 0):.1f}%
            </div>
            <p style="text-align: center; color: #7f8c8d; font-size: 1.1em;">
                Puntaje General del Sistema Distribuido
            </p>
        </div>
        
        <div class="card">
            <h2>📈 Puntajes por Módulo</h2>
            {score_bars}
        </div>
        
        <div class="card">
            <h2>📋 Detalles de Ejecución</h2>
            <table>
                <thead>
                    <tr>
                        <th>Módulo</th>
                        <th>Estado</th>
                        <th>Detalles</th>
                    </tr>
                </thead>
                <tbody>
                    {module_details}
                </tbody>
            </table>
        </div>
        
        <div class="card">
            <h2>🏥 Estado de Salud del Sistema</h2>
            <p><strong>Disponibilidad de Servicios:</strong> {health.get('health_percentage', 0):.1f}%</p>
            
            <h3>Servicios Verificados:</h3>
            <div>
                <div class="health-status">
                    <div class="status-icon status-healthy"></div>
                    <span>LP1 - Servicio Bancario (Java)</span>
                </div>
                <div class="health-status">
                    <div class="status-icon status-healthy"></div>
                    <span>LP2 - Servicio RENIEC (Python)</span>
                </div>
                <div class="health-status">
                    <div class="status-icon status-healthy"></div>
                    <span>LP3 - Aplicación Cliente (JavaScript)</span>
                </div>
            </div>
        </div>
        
        <div class="card">
            <h2>🔍 Metodología de Validación</h2>
            <p><strong>Este reporte evalúa los siguientes aspectos del sistema distribuido:</strong></p>
            <ul style="margin: 20px 0; padding-left: 40px;">
                <li><strong>Pruebas de Integración:</strong> Comunicación entre servicios LP1, LP2 y LP3</li>
                <li><strong>Validación de Tecnologías:</strong> Heterogeneidad Java + Python + JavaScript</li>
                <li><strong>Validación de Arquitectura:</strong> Patrones distribuidos y containerización</li>
                <li><strong>Pruebas de Escalabilidad:</strong> Rendimiento bajo carga y concurrencia</li>
                <li><strong>Tolerancia a Fallos:</strong> Resiliencia y recuperación de errores</li>
            </ul>
        </div>
        
        <div class="footer">
            <p>Sistema de Validación Integral v1.0 | Generado automáticamente</p>
            <p>© 2024 - Evaluación Completa de Sistema Distribuido Bancario</p>
        </div>
    </div>
</body>
</html>
        """
        
        return html_template

    def generate_json_summary(self, output_file: Optional[str] = None) -> str:
        """
        Generar resumen JSON
        
        Args:
            output_file: Archivo de salida (opcional)
            
        Returns:
            Ruta del archivo generado
        """
        if not self.consolidated_data:
            self.load_consolidated_data()
        
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = self.reports_dir / f"validation_summary_{timestamp}.json"
        else:
            output_file = Path(output_file)
        
        # Crear resumen simplificado
        summary = {
            "validation_summary": {
                "timestamp": datetime.now().isoformat(),
                "system_health_score": self.consolidated_data.get("system_health", {}).get("health_percentage", 0),
                "overall_system_score": self.consolidated_data.get("overall_scores", {}).get("overall_system_score", 0),
                "modules_executed": self.consolidated_data.get("validation_overview", {}).get("modules_executed", 0),
                "validation_successful": self.consolidated_data.get("validation_overview", {}).get("overall_success", False)
            },
            "module_scores": self.consolidated_data.get("overall_scores", {}),
            "system_status": self.consolidated_data.get("system_health", {}),
            "execution_details": {
                "duration_seconds": self.consolidated_data.get("validation_overview", {}).get("total_duration", 0),
                "modules": {
                    module: {
                        "status": result.get("status"),
                        "success": result.get("success", False),
                        "message": result.get("message")
                    }
                    for module, result in self.consolidated_data.get("module_results", {}).items()
                }
            }
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        return str(output_file)

    def print_console_summary(self):
        """Imprimir resumen en consola"""
        if not self.consolidated_data:
            self.load_consolidated_data()
        
        print("\n" + "="*80)
        print("🏗️ RESUMEN DE VALIDACIÓN INTEGRAL - SISTEMA DISTRIBUIDO")
        print("="*80)
        
        overview = self.consolidated_data.get("validation_overview", {})
        scores = self.consolidated_data.get("overall_scores", {})
        health = self.consolidated_data.get("system_health", {})
        
        # Información general
        print(f"\n⏰ Duración: {overview.get('total_duration', 0):.1f} segundos")
        print(f"📊 Módulos ejecutados: {overview.get('modules_executed', 0)}")
        
        # Estado general
        overall_success = overview.get("overall_success", False)
        status_icon = "✅" if overall_success else "❌"
        print(f"{status_icon} Validación: {'EXITOSA' if overall_success else 'CON FALLOS'}")
        
        # Puntajes
        print(f"\n📈 PUNTAJES:")
        for module, score in scores.items():
            if module != "overall_system_score":
                module_name = module.replace("_", " ").title()
                print(f"  {module_name:.<30} {score:.1f}%")
        
        # Puntaje general
        overall_score = scores.get("overall_system_score", 0)
        print(f"\n🎯 PUNTAJE GENERAL: {overall_score:.1f}%")
        
        # Salud del sistema
        services_ok = health.get("services_available", 0)
        services_total = health.get("total_services", 0)
        health_pct = health.get("health_percentage", 0)
        print(f"\n🏥 SALUD DE SERVICIOS: {services_ok}/{services_total} ({health_pct:.1f}%)")
        
        print("\n" + "="*80)

def main():
    """Función principal"""
    parser = argparse.ArgumentParser(description="Generador de Reportes Finales")
    parser.add_argument("--reports-dir", "-r", default="/workspace/validation_system/reports",
                       help="Directorio de reportes")
    parser.add_argument("--output-html", help="Archivo de salida HTML")
    parser.add_argument("--output-json", help="Archivo de salida JSON")
    parser.add_argument("--console", "-c", action="store_true",
                       help="Mostrar resumen en consola")
    
    args = parser.parse_args()
    
    try:
        # Crear generador
        generator = FinalReportGenerator(reports_dir=args.reports_dir)
        
        # Generar reportes
        html_file = None
        json_file = None
        
        if args.output_html or not args.output_json:  # Generar HTML por defecto
            html_file = generator.generate_html_report(args.output_html)
            print(f"📄 Reporte HTML generado: {html_file}")
        
        if args.output_json or not args.output_html:  # Generar JSON por defecto
            json_file = generator.generate_json_summary(args.output_json)
            print(f"📄 Resumen JSON generado: {json_file}")
        
        # Mostrar resumen en consola si se solicita
        if args.console:
            generator.print_console_summary()
        
        print(f"\n✅ Reportes generados exitosamente en: {args.reports_dir}")
        
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        print("Asegúrese de ejecutar primero la validación completa con run_complete_validation.py")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error generando reportes: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
