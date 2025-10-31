# Sistema Distribuido Shibasito - Docker Compose

## Descripción

Este archivo `docker-compose.main.yml` proporciona una configuración completa para ejecutar el sistema distribuido Shibasito con todos sus componentes y servicios de infraestructura.

## Servicios Incluidos

### Servicios de Aplicación
- **servicio-banco-lp1**: Servicio Java/Spring Boot para operaciones bancarias (Puerto 8080)
- **servicio-reniec-lp2**: Servicio Python/FastAPI para consultas RENIEC (Puerto 8000)

### Bases de Datos
- **bd1_postgresql**: Base de datos PostgreSQL para el servicio banco (Puerto 5432)
- **bd2_mysql**: Base de datos MySQL para el servicio RENIEC (Puerto 3306)

### Servicios de Mensajería e Infraestructura
- **rabbitmq**: Message broker con interfaz de gestión (Puertos: 5672 AMQP, 15672 Management UI)
- **redis**: Cache y almacenamiento de sesiones (Puerto 6379)

### Servicios de Monitoreo
- **prometheus**: Sistema de monitoreo y métricas (Puerto 9090)
- **grafana**: Dashboard y visualización de métricas (Puerto 3000)

## Redes Configuradas

- **shibasito-network** (172.20.0.0/16): Red principal para comunicación entre servicios
- **database-network** (172.21.0.0/16): Red dedicada para servicios de base de datos
- **monitoring-network** (172.22.0.0/16): Red para servicios de monitoreo

## Volúmenes Persistentes

- `postgres_bd1_data`: Datos de PostgreSQL
- `mysql_bd2_data`: Datos de MySQL
- `rabbitmq_data`: Datos de RabbitMQ
- `redis_data`: Datos de Redis
- `prometheus_data`: Métricas de Prometheus
- `grafana_data`: Configuración y dashboards de Grafana

## Instalación y Uso

### Prerrequisitos

- Docker Engine 20.10+
- Docker Compose v2.0+

### Pasos de Instalación

1. **Clonar y navegar al directorio del proyecto**
   ```bash
   cd shibasito-sistema-distribuido/
   ```

2. **Iniciar todos los servicios**
   ```bash
   docker-compose -f docker-compose.main.yml up -d
   ```

3. **Verificar el estado de los servicios**
   ```bash
   docker-compose -f docker-compose.main.yml ps
   ```

4. **Ver logs en tiempo real**
   ```bash
   docker-compose -f docker-compose.main.yml logs -f
   ```

### Comandos Útiles

```bash
# Iniciar servicios específicos
docker-compose -f docker-compose.main.yml up -d servicio-banco-lp1 servicio-reniec-lp2

# Detener todos los servicios
docker-compose -f docker-compose.main.yml down

# Detener y eliminar volúmenes (⚠️ CUIDADO: Elimina todos los datos)
docker-compose -f docker-compose.main.yml down -v

# Reiniciar un servicio específico
docker-compose -f docker-compose.main.yml restart servicio-banco-lp1

# Ver logs de un servicio específico
docker-compose -f docker-compose.main.yml logs -f servicio-banco-lp1

# Ejecutar comando en un contenedor
docker-compose -f docker-compose.main.yml exec servicio-banco-lp1 bash
```

## Configuración de Variables de Entorno

Las variables de entorno se configuran en el archivo `.env`. Las principales incluyen:

- Credenciales de bases de datos
- Configuración de RabbitMQ
- Configuración de Redis
- Credenciales de Grafana
- Configuración de aplicaciones

## Acceso a Interfaces Web

| Servicio | URL | Credenciales |
|----------|-----|--------------|
| Grafana | http://localhost:3000 | admin / admin123_secure_2024 |
| RabbitMQ Management | http://localhost:15672 | admin / admin123_secure_2024 |
| Prometheus | http://localhost:9090 | No requiere autenticación |
| API Banco LP1 | http://localhost:8080 | N/A |
| API RENIEC LP2 | http://localhost:8000 | N/A |

## Health Checks

Todos los servicios incluyen health checks configurados para:
- Verificar disponibilidad del servicio
- Validar conexiones a bases de datos
- Monitorear recursos del sistema

## Dependencias entre Servicios

Las dependencias están configuradas para garantizar que:
- Los servicios de aplicación esperan a que las bases de datos estén listas
- Los servicios de monitoreo se inician después de los servicios principales
- Las dependencias se resuelven automáticamente

## Monitoreo y Métricas

### Prometheus
- Recolecta métricas de todos los servicios
- Configurado con intervalos de scraping optimizados
- Retención de datos configurada a 30 días

### Grafana
- Dashboards pre-configurados para visualización
- Fuentes de datos auto-provisionadas
- Plugins adicionales instalados

### Logs
- Todos los servicios están configurados para logging estructurado
- Los logs se almacenan en volúmenes persistentes
- Configuración de rotación automática

## Configuración de Producción

Para un entorno de producción, se recomienda:

1. **Seguridad**:
   - Cambiar todas las credenciales por defecto
   - Configurar SSL/TLS para todas las comunicaciones
   - Restringir acceso a redes internas únicamente

2. **Rendimiento**:
   - Ajustar límites de memoria para cada servicio
   - Configurar pools de conexiones apropiados
   - Optimizar configuraciones de bases de datos

3. **Monitoreo**:
   - Configurar alertas en Prometheus
   - Implementar dashboards específicos para el negocio
   - Configurar backup automático de datos

## Solución de Problemas

### Servicios no inician
```bash
# Verificar logs detallados
docker-compose -f docker-compose.main.yml logs [servicio]

# Verificar conectividad de red
docker network ls
docker network inspect shibasito-sistema-distribuido_shibasito-network
```

### Problemas de base de datos
```bash
# Conectar a PostgreSQL
docker-compose -f docker-compose.main.yml exec bd1_postgresql psql -U banco_user -d banco_db

# Conectar a MySQL
docker-compose -f docker-compose.main.yml exec bd2_mysql mysql -u reniec_user -p
```

### Problemas de red
```bash
# Verificar conectividad entre servicios
docker-compose -f docker-compose.main.yml exec servicio-banco-lp1 ping bd1_postgresql
```

## Contribución

Para contribuir al proyecto:

1. Asegúrate de que todos los health checks pasen
2. Verifica que no haya conflictos de puertos
3. Actualiza la documentación según sea necesario
4. Prueba en un entorno limpio antes de hacer commit

## Licencia

Este proyecto está bajo licencia MIT. Ver archivo LICENSE para más detalles.