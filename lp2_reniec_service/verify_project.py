#!/usr/bin/env python3
"""
Script de verificación de la estructura del proyecto FastAPI LP2 RENIEC
"""

import os
import sys
from pathlib import Path

def check_file_exists(filepath, description):
    """Verificar si un archivo existe"""
    path = Path(filepath)
    if path.exists():
        size = path.stat().st_size
        print(f"✅ {description}: {filepath} ({size} bytes)")
        return True
    else:
        print(f"❌ {description}: {filepath} NO ENCONTRADO")
        return False

def check_directory_exists(dirpath, description):
    """Verificar si un directorio existe"""
    path = Path(dirpath)
    if path.exists() and path.is_dir():
        print(f"✅ {description}: {dirpath}")
        return True
    else:
        print(f"❌ {description}: {dirpath} NO ENCONTRADO")
        return False

def main():
    """Función principal de verificación"""
    print("=" * 60)
    print("🔍 VERIFICACIÓN DEL PROYECTO FASTAPI LP2 RENIEC SERVICE")
    print("=" * 60)
    print()
    
    all_checks_passed = True
    
    # Verificar archivos principales
    print("📁 ARCHIVOS PRINCIPALES:")
    all_checks_passed &= check_file_exists("main.py", "Aplicación FastAPI")
    all_checks_passed &= check_file_exists("requirements.txt", "Dependencias")
    all_checks_passed &= check_file_exists(".env.example", "Variables de entorno ejemplo")
    all_checks_passed &= check_file_exists("run.sh", "Script de inicio")
    print()
    
    # Verificar configuración
    print("⚙️  CONFIGURACIÓN:")
    all_checks_passed &= check_file_exists("app/__init__.py", "App package")
    all_checks_passed &= check_file_exists("app/config.py", "Configuración principal")
    all_checks_passed &= check_file_exists("app/config/settings.py", "Configuración Pydantic")
    all_checks_passed &= check_file_exists("app/config/database.py", "Configuración DB")
    print()
    
    # Verificar estructura de directorios
    print("📂 ESTRUCTURA DE DIRECTORIOS:")
    all_checks_passed &= check_directory_exists("app/routers", "Routers")
    all_checks_passed &= check_directory_exists("app/middleware", "Middleware")
    all_checks_passed &= check_directory_exists("app/services", "Servicios")
    all_checks_passed &= check_directory_exists("app/models", "Modelos")
    all_checks_passed &= check_directory_exists("app/listeners", "Listeners")
    all_checks_passed &= check_directory_exists("app/utils", "Utilidades")
    print()
    
    # Verificar archivos de configuración adicionales
    print("📄 CONFIGURACIÓN ADICIONAL:")
    check_file_exists("docker-compose.yml", "Docker Compose")
    check_file_exists("Dockerfile", "Dockerfile")
    check_file_exists("PROYECTO_FASTAPI_COMPLETO.md", "Documentación")
    print()
    
    # Verificar sintaxis de archivos Python críticos
    print("🐍 VERIFICACIÓN DE SINTAXIS:")
    python_files = ["main.py", "app/__init__.py", "app/config.py"]
    for py_file in python_files:
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                compile(f.read(), py_file, 'exec')
            print(f"✅ Sintaxis válida: {py_file}")
        except SyntaxError as e:
            print(f"❌ Error de sintaxis en {py_file}: {e}")
            all_checks_passed = False
        except FileNotFoundError:
            print(f"❌ Archivo no encontrado: {py_file}")
            all_checks_passed = False
    print()
    
    # Resumen final
    print("=" * 60)
    if all_checks_passed:
        print("✅ TODOS LOS ARCHIVOS CRÍTICOS VERIFICADOS CORRECTAMENTE")
        print("🚀 El proyecto está listo para ejecutarse")
        print()
        print("📋 Próximos pasos:")
        print("   1. cp .env.example .env")
        print("   2. Editar .env con tus configuraciones")
        print("   3. ./run.sh")
        return 0
    else:
        print("⚠️  SE ENCONTRARON PROBLEMAS EN LA VERIFICACIÓN")
        print("🔧 Revisa los archivos marcados como faltantes")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
