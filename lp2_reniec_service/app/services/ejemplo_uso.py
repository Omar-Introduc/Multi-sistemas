"""
Ejemplo de uso de los servicios de validación RENIEC

Este archivo muestra cómo utilizar los servicios de validación
"""

import os
import sys
from datetime import datetime

# Agregar el directorio del proyecto al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services import crear_servicios, EstadoValidacion

def ejemplo_validacion_completa():
    """Ejemplo de un flujo completo de validación"""
    
    print("=== EJEMPLO DE VALIDACIÓN RENIEC ===")
    print()
    
    # Crear servicios
    print("1. Inicializando servicios...")
    reniec_service, database_service, rabbit_service, log_service = crear_servicios()
    
    # Inicializar servicios
    print("2. Conectando servicios...")
    
    # Inicializar base de datos
    if database_service.inicializar():
        print("   ✓ Base de datos conectada")
        
        # Crear tablas de auditoría si no existen
        if log_service.crear_tablas_auditoria():
            print("   ✓ Tablas de auditoría creadas")
    else:
        print("   ✗ Error conectando base de datos")
        return
    
    # Inicializar RabbitMQ
    if rabbit_service.inicializar():
        print("   ✓ RabbitMQ conectado")
    else:
        print("   ✗ Error conectando RabbitMQ")
    
    print()
    
    # Ejemplo de validación de identidad
    print("3. Realizando validación de identidad...")
    
    numero_dni = "12345678"
    nombres = "JUAN CARLOS"
    apellido_paterno = "PEREZ"
    apellido_materno = "GARCIA"
    id_solicitud = "SOL-2024-001"
    
    resultado = reniec_service.validarIdentidad(
        numero_dni=numero_dni,
        nombres=nombres,
        apellido_paterno=apellido_paterno,
        apellido_materno=apellido_materno,
        id_solicitud=id_solicitud
    )
    
    print(f"   Estado: {resultado.estado.value}")
    print(f"   Mensaje: {resultado.mensaje}")
    print(f"   Score de confianza: {resultado.score_confianza}")
    
    if resultado.datos_ciudadano:
        print(f"   Ciudadano encontrado: {resultado.datos_ciudadano.nombres} {resultado.datos_ciudadano.apellido_paterno}")
    
    print()
    
    # Ejemplo de consulta de ciudadano
    print("4. Consultando ciudadano...")
    
    datos_ciudadano = reniec_service.consultarCiudadano("87654321")
    
    if datos_ciudadano:
        print(f"   ✓ Ciudadano encontrado:")
        print(f"     DNI: {datos_ciudadano.numero_documento}")
        print(f"     Nombres: {datos_ciudadano.nombres}")
        print(f"     Apellidos: {datos_ciudadano.apellido_paterno} {datos_ciudadano.apellido_materno}")
    else:
        print("   ✗ Ciudadano no encontrado")
    
    print()
    
    # Ejemplo de validación simple de DNI
    print("5. Validando DNI...")
    
    validacion_dni = reniec_service.validarDni("12345678")
    
    print(f"   Válido: {validacion_dni['valido']}")
    print(f"   Mensaje: {validacion_dni['mensaje']}")
    print(f"   Existe: {validacion_dni['existe']}")
    
    if validacion_dni.get('datos'):
        datos = validacion_dni['datos']
        print(f"   Datos: {datos['nombres']} {datos['apellido_paterno']} {datos['apellido_materno']}")
    
    print()
    
    # Ejemplo de envío de respuesta al banco
    print("6. Enviando respuesta al banco...")
    
    # Preparar respuesta para el banco
    respuesta_banco = {
        "id_solicitud": id_solicitud,
        "estado": "exitoso",
        "datos_ciudadano": {
            "numero_documento": numero_dni,
            "nombres": nombres,
            "apellido_paterno": apellido_paterno,
            "apellido_materno": apellido_materno
        },
        "timestamp": datetime.now().isoformat()
    }
    
    id_banco = "BANCO_001"
    enviado = rabbit_service.enviarRespuestaValidacion(id_banco, respuesta_banco)
    
    if enviado:
        print("   ✓ Respuesta enviada al banco exitosamente")
    else:
        print("   ✗ Error enviando respuesta al banco")
    
    print()
    
    # Mostrar estadísticas
    print("7. Estadísticas del sistema...")
    
    estadisticas = log_service.obtenerEstadisticas(periodo_horas=1)
    
    if estadisticas:
        print(f"   Eventos totales: {estadisticas.get('eventos_total', 0)}")
        print(f"   Errores totales: {estadisticas.get('errores_total', 0)}")
        print(f"   Eventos por tipo: {estadisticas.get('eventos_por_tipo', {})}")
        print(f"   Errores por tipo: {estadisticas.get('errores_por_tipo', {})}")
    
    print()
    
    # Limpiar recursos
    print("8. Cerrando conexiones...")
    
    rabbit_service.cerrarConexion()
    database_service.cerrarPool()
    
    print("   ✓ Conexiones cerradas")
    print()
    print("=== EJEMPLO COMPLETADO ===")

def ejemplo_manejo_errores():
    """Ejemplo de manejo de errores"""
    
    print("=== EJEMPLO DE MANEJO DE ERRORES ===")
    print()
    
    try:
        # Crear servicios
        reniec_service, database_service, rabbit_service, log_service = crear_servicios()
        
        # Intentar validar con datos incorrectos
        print("1. Probando validación con DNI inválido...")
        
        resultado = reniec_service.validarIdentidad(
            numero_dni="123",  # DNI inválido
            nombres="Juan",
            apellido_paterno="Pérez",
            apellido_materno="García",
            id_solicitud="SOL-ERR-001"
        )
        
        print(f"   Resultado esperado (fallido): {resultado.estado.value}")
        print()
        
        # Probar consulta con DNI que no existe
        print("2. Probando consulta de ciudadano inexistente...")
        
        datos_ciudadano = reniec_service.consultarCiudadano("00000000")
        
        if datos_ciudadano:
            print("   ✗ Se encontró un ciudadano (inesperado)")
        else:
            print("   ✓ No se encontró ciudadano (esperado)")
        
        print()
        
        # Mostrar errores registrados
        print("3. Errores registrados...")
        
        errores = log_service.obtenerErrores(limite=10)
        
        if errores:
            for error in errores:
                print(f"   - {error.get('tipo_error', 'Desconocido')}: {error.get('mensaje', 'Sin mensaje')}")
        else:
            print("   No se registraron errores")
        
    except Exception as e:
        print(f"Error en ejemplo: {str(e)}")
    
    print("=== EJEMPLO COMPLETADO ===")

def ejemplo_auditoria():
    """Ejemplo de auditoría y logging"""
    
    print("=== EJEMPLO DE AUDITORÍA ===")
    print()
    
    try:
        # Crear servicios
        reniec_service, database_service, rabbit_service, log_service = crear_servicios()
        
        # Inicializar base de datos
        if database_service.inicializar():
            log_service.database_service = database_service
            
            # Crear tablas de auditoría
            if log_service.crear_tablas_auditoria():
                print("1. Tablas de auditoría creadas")
            else:
                print("1. Error creando tablas de auditoría")
                return
        
        # Registrar algunos eventos manualmente
        print("2. Registrando eventos de auditoría...")
        
        evento_id = log_service.registrarEvento(
            tipo_evento="AUDITORIA_INICIO",
            mensaje="Inicio del ejemplo de auditoría",
            datos_adicios={"proceso": "ejemplo", "version": "1.0"},
            usuario="sistema"
        )
        
        print(f"   Evento registrado: {evento_id}")
        
        # Simular un error
        print("3. Registrando un error...")
        
        error_id = log_service.registrarError(
            tipo_error="EJEMPLO_ERROR",
            mensaje="Este es un error de ejemplo para demostrar el logging",
            contexto={"proceso": "ejemplo", "paso": "simulacion"},
            severidad="WARNING"
        )
        
        print(f"   Error registrado: {error_id}")
        
        # Registrar métricas
        print("4. Registrando métricas...")
        
        metrica_id = log_service.registrarMetrica(
            nombre_metrica="validaciones_procesadas",
            valor=100,
            unidad="count",
            etiquetas={"servicio": "reniec", "tipo": "ejemplo"}
        )
        
        print(f"   Métrica registrada: {metrica_id}")
        
        # Mostrar estadísticas
        print("5. Estadísticas del sistema...")
        
        estadisticas = log_service.obtenerEstadisticas(periodo_horas=24)
        
        if estadisticas:
            print(f"   Período: {estadisticas.get('periodo_horas', 0)} horas")
            print(f"   Eventos totales: {estadisticas.get('eventos_total', 0)}")
            print(f"   Errores totales: {estadisticas.get('errores_total', 0)}")
            
            eventos_por_tipo = estadisticas.get('eventos_por_tipo', {})
            if eventos_por_tipo:
                print("   Top 3 tipos de eventos:")
                for tipo, cantidad in sorted(eventos_por_tipo.items(), key=lambda x: x[1], reverse=True)[:3]:
                    print(f"     - {tipo}: {cantidad}")
        
        # Cerrar conexiones
        database_service.cerrarPool()
        
    except Exception as e:
        print(f"Error en auditoría: {str(e)}")
    
    print("=== EJEMPLO COMPLETADO ===")

if __name__ == "__main__":
    print("EJEMPLOS DE USO - SERVICIOS DE VALIDACIÓN RENIEC")
    print("=" * 60)
    print()
    
    # Ejecutar ejemplos
    try:
        ejemplo_validacion_completa()
        print()
        
        ejemplo_manejo_errores()
        print()
        
        ejemplo_auditoria()
        
    except KeyboardInterrupt:
        print("\nEjemplos interrumpidos por el usuario")
    except Exception as e:
        print(f"\nError ejecutando ejemplos: {str(e)}")
        import traceback
        traceback.print_exc()