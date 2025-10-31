# Scripts SQL para Sistema RENIEC LP2

Este directorio contiene los scripts SQL necesarios para inicializar y gestionar la base de datos del Sistema RENIEC (Registro Nacional de Identificación y Estado Civil) - Proyecto LP2.

## Archivos Incluidos

### 1. `schema_lp2_reniec.sql`
**Descripción**: Esquema completo de la base de datos con todas las tablas, relaciones, procedimientos almacenados y triggers.

**Contenido Principal**:
- **Tabla `ciudadanos`**: Información completa de ciudadanos peruanos
- **Tabla `validadores`**: Usuarios autorizados para validar documentos
- **Tabla `reniec_sessions`**: Gestión de sesiones de usuarios
- **Tabla `auditoria`**: Registro detallado de todas las operaciones
- Procedimientos almacenados para operaciones frecuentes
- Triggers de auditoría automática
- Vistas optimizadas para consultas

**Uso**:
```bash
mysql -u root -p < schema_lp2_reniec.sql
```

### 2. `seed_data_lp2.sql`
**Descripción**: Datos de prueba realistas para el sistema RENIEC.

**Contenido**:
- 12 validadores de diferentes oficinas del Perú
- 25+ ciudadanos de diversos departamentos
- Sesiones de ejemplo (activas y expiradas)
- Registros de auditoría de muestra
- Verificaciones de integridad

**Uso**:
```bash
mysql -u root -p reniec_lp2 < seed_data_lp2.sql
```

### 3. `indexes_lp2.sql`
**Descripción**: Índices optimizados para mejorar el rendimiento de las consultas más frecuentes.

**Características**:
- Índices primarios y secundarios
- Índices compuestos para búsquedas complejas
- Índices para funciones de geolocalización
- Optimizaciones para joins frecuentes
- Procedimientos para análisis de uso

**Uso**:
```bash
mysql -u root -p reniec_lp2 < indexes_lp2.sql
```

### 4. `backup_reniec.sql`
**Descripción**: Scripts completos para backup, restauración y mantenimiento de la base de datos.

**Funcionalidades**:
- Backup completo de la base de datos
- Backup selectivo por tablas
- Backup especializado para datos críticos
- Verificación de integridad
- Limpieza de datos obsoletos
- Procedimientos de monitoreo

**Uso**:
```sql
-- Ejecutar procedimientos de backup
CALL backup_completo();
CALL backup_solo_ciudadanos();
CALL backup_solo_auditoria();
CALL backup_sesiones_inactivas();
```

## Estructura de la Base de Datos

### Tabla `ciudadanos`
| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | INT AUTO_INCREMENT | Identificador único |
| dni | VARCHAR(8) | Documento Nacional de Identidad (único) |
| nombre | VARCHAR(100) | Nombres del ciudadano |
| apellido_paterno | VARCHAR(100) | Apellido paterno |
| apellido_materno | VARCHAR(100) | Apellido materno |
| fecha_nacimiento | DATE | Fecha de nacimiento |
| lugar_nacimiento | VARCHAR(200) | Lugar de nacimiento |
| genero | ENUM('M', 'F') | Género |
| estado_civil | ENUM(...) | Estado civil |
| direccion | VARCHAR(300) | Dirección domiciliaria |
| distrito | VARCHAR(100) | Distrito |
| provincia | VARCHAR(100) | Provincia |
| departamento | VARCHAR(100) | Departamento |
| es_verificado | BOOLEAN | Estado de verificación |
| activo | BOOLEAN | Estado activo |

### Tabla `validadores`
| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | INT AUTO_INCREMENT | Identificador único |
| usuario | VARCHAR(50) | Nombre de usuario (único) |
| password_hash | VARCHAR(255) | Hash de la contraseña |
| nombre_completo | VARCHAR(200) | Nombre completo |
| cargo | VARCHAR(100) | Cargo que desempeña |
| oficina | VARCHAR(100) | Oficina donde labora |
| nivel_acceso | ENUM(...) | Nivel de acceso al sistema |
| ultimo_acceso | TIMESTAMP | Último acceso al sistema |
| intentos_fallidos | INT | Intentos de login fallidos |
| bloqueado | BOOLEAN | Estado de bloqueo |
| activo | BOOLEAN | Estado activo |

### Tabla `reniec_sessions`
| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | INT AUTO_INCREMENT | Identificador único |
| validador_id | INT | FK a validadores |
| token_sesion | VARCHAR(255) | Token único de sesión |
| ip_address | VARCHAR(45) | Dirección IP del cliente |
| user_agent | TEXT | Agente de usuario del navegador |
| fecha_inicio | TIMESTAMP | Inicio de la sesión |
| fecha_ultimo_uso | TIMESTAMP | Último uso de la sesión |
| fecha_expiracion | TIMESTAMP | Fecha de expiración |
| activa | BOOLEAN | Estado de la sesión |
| operaciones_realizadas | INT | Número de operaciones |

### Tabla `auditoria`
| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | BIGINT AUTO_INCREMENT | Identificador único |
| tabla_afectada | VARCHAR(50) | Tabla afectada |
| registro_id | INT | ID del registro afectado |
| accion | ENUM(...) | Tipo de operación |
| validador_id | INT | FK a validadores |
| session_id | INT | FK a sesiones |
| datos_anteriores | JSON | Datos anteriores (UPDATE/DELETE) |
| datos_nuevos | JSON | Datos nuevos (INSERT/UPDATE) |
| ip_address | VARCHAR(45) | IP del usuario |
| timestamp_operacion | TIMESTAMP | Timestamp de la operación |
| observaciones | TEXT | Observaciones adicionales |

## Procedimientos Almacenados

### `crear_ciudadano()`
Crea un nuevo registro de ciudadano con validación de datos.

### `iniciar_sesion_validador()`
Inicia sesión de un validador y genera token de sesión.

### `verificar_integridad_ciudadanos()`
Verifica la integridad de los datos en la tabla ciudadanos.

### `verificar_sesiones_validas()`
Valida el estado de las sesiones activas.

## Vistas Disponibles

### `vista_ciudadanos_completa`
Vista con información completa de ciudadanos para consultas frecuentes.

### `vista_sesiones_activas`
Vista para monitoreo de sesiones activas del sistema.

### `vista_estadisticas_backup`
Vista con estadísticas generales para monitoreo.

## Secuencia de Instalación

1. **Crear la base de datos y estructura**:
   ```bash
   mysql -u root -p < schema_lp2_reniec.sql
   ```

2. **Cargar datos de prueba**:
   ```bash
   mysql -u root -p reniec_lp2 < seed_data_lp2.sql
   ```

3. **Aplicar optimizaciones**:
   ```bash
   mysql -u root -p reniec_lp2 < indexes_lp2.sql
   ```

4. **Configurar procedimientos de backup**:
   ```bash
   mysql -u root -p reniec_lp2 < backup_reniec.sql
   ```

## Comandos de Backup Externos

### Backup Completo
```bash
mysqldump -u root -p reniec_lp2 > backup_completo_$(date +%Y%m%d_%H%M%S).sql
```

### Backup Comprimido
```bash
mysqldump -u root -p reniec_lp2 | gzip > backup_completo_$(date +%Y%m%d_%H%M%S).sql.gz
```

### Backup Selectivo
```bash
mysqldump -u root -p reniec_lp2 ciudadanos validadores auditoria > backup_critico_$(date +%Y%m%d_%H%M%S).sql
```

### Restaurar Backup
```bash
mysql -u root -p reniec_lp2 < backup_completo_YYYYMMDD_HHMMSS.sql
```

## Automatización con Cron

```bash
# Backup diario a las 2:00 AM
0 2 * * * mysqldump -u root -p[CONTRASEÑA] reniec_lp2 | gzip > /backups/daily_$(date +\%Y\%m\%d).sql.gz

# Backup semanal completo los domingos
0 1 * * 0 mysqldump -u root -p[CONTRASEÑA] --single-transaction --routines --triggers reniec_lp2 | gzip > /backups/weekly_$(date +\%Y\%m\%d).sql.gz

# Limpiar backups antiguos (mantener últimos 30 días)
0 3 * * * find /backups/reniec_lp2/ -name "*.sql.gz" -mtime +30 -delete
```

## Monitoreo y Mantenimiento

### Verificar Estado de la Base de Datos
```sql
SELECT * FROM vista_estadisticas_backup;
SELECT verificar_integridad_ciudadanos();
SELECT verificar_sesiones_validas();
```

### Optimización Regular
```sql
OPTIMIZE TABLE ciudadanos, validadores, reniec_sessions, auditoria;
ANALYZE TABLE ciudadanos, validadores, reniec_sessions, auditoria;
```

### Análisis de Rendimiento
```sql
CALL analizar_uso_indices();
CALL verificar_consultas_lentas();
```

## Consideraciones de Seguridad

1. **Contraseñas**: Los validadores tienen contraseñas hasheadas (usar hash real en producción)
2. **Acceso**: Control de acceso por niveles (BASICO, INTERMEDIO, AVANZADO, ADMINISTRADOR)
3. **Auditoría**: Todas las operaciones quedan registradas automáticamente
4. **Sesiones**: Control de sesiones con expiración automática
5. **IP Tracking**: Registro de direcciones IP para auditoría de seguridad

## Soporte Técnico

Para soporte técnico o consultas sobre estos scripts:
- Revisar logs de la base de datos
- Verificar configuración de MySQL/MariaDB
- Consultar documentación oficial de MySQL
- Contactar al equipo de desarrollo del proyecto RENIEC LP2

## Versión
**Versión**: 1.0  
**Fecha**: Enero 2025  
**Compatibilidad**: MySQL 8.0+ / MariaDB 10.5+
