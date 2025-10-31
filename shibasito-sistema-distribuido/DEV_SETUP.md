# Guía de Desarrollo Local - Sistema Shibasito

## 🚀 Configuración para Desarrollo Local

Este archivo contiene las instrucciones para configurar y ejecutar el Sistema Shibasito en modo desarrollo local utilizando Docker Compose con overrides específicos.

## 📋 Prerrequisitos

- Docker Desktop instalado y ejecutándose
- Docker Compose v2.0 o superior
- Al menos 4GB de RAM disponible
- Puertos libres: 5432, 5433, 3306, 3307, 5672, 6379, 6380, 8000, 8001, 8080, 8081, 9090, 9091, 3000, 3001

## 🛠️ Inicio Rápido

### 1. Clonar el repositorio (si es necesario)
```bash
git clone <repository-url>
cd shibasito-sistema-distribuido
```

### 2. Configurar variables de entorno de desarrollo
```bash
cp .env.development .env
# Editar .env si es necesario con tus configuraciones específicas
```

### 3. Levantar todos los servicios en modo desarrollo
```bash
docker-compose -f docker-compose.main.yml -f docker-compose.override.yml up --build
```

### 4. Verificar que todos los servicios están ejecutándose
```bash
docker-compose -f docker-compose.main.yml -f docker-compose.override.yml ps
```

## 🔧 Configuración de Desarrollo

### Servicios Principales

#### 1. Servicio Banco LP1 (Java/Spring Boot)
- **Puerto de aplicación**: 8080
- **Puerto de métricas**: 8081
- **Puerto de debugging**: 5005
- **Hot Reload**: Habilitado con Spring DevTools
- **URL de salud**: http://localhost:8080/actuator/health

#### 2. Servicio RENIEC LP2 (Python/FastAPI)
- **Puerto de API**: 8000
- **Puerto de métricas**: 8001
- **Puerto de debugging**: 5678
- **Hot Reload**: Habilitado con Uvicorn
- **URL de salud**: http://localhost:8000/health

### Servicios de Infraestructura

#### Bases de Datos
- **PostgreSQL (BD1)**: puerto 5432 (principal), 5433 (secundario)
- **MySQL (BD2)**: puerto 3306 (principal), 3307 (secundario)

#### Message Broker y Cache
- **RabbitMQ**: puerto 5672 (AMQP), 15672 (Management UI)
- **Redis**: puerto 6379 (principal), 6380 (secundario)

#### Monitoreo
- **Prometheus**: puerto 9090 (principal), 9091 (secundario)
- **Grafana**: puerto 3000 (principal), 3001 (secundario)

## 🔍 Debugging

### Debugging Java (Servicio Banco)
```bash
# Conectar depurador al puerto 5005
# IntelliJ IDEA:
#   Host: localhost, Puerto: 5005

# VS Code:
#   Configurar launch.json:
{
  "type": "java",
  "name": "Debug Spring Boot",
  "request": "attach",
  "hostName": "localhost",
  "port": 5005
}
```

### Debugging Python (Servicio RENIEC)
```bash
# Conectar depurador al puerto 5678
# VS Code:
#   Configurar launch.json:
{
  "type": "python",
  "name": "Debug FastAPI",
  "request": "attach",
  "connect": {
    "host": "localhost",
    "port": 5678
  },
  "pathMappings": [
    {
      "localRoot": "${workspaceFolder}/lp2_reniec_service",
      "remoteRoot": "/app"
    }
  ]
}
```

## 🔄 Hot Reload

### Servicio Banco LP1
- Los cambios en `./lp1-servicio-banco/src/` se recargan automáticamente
- Spring DevTools está habilitado
- LiveReload está habilitado en el puerto 35729

### Servicio RENIEC LP2
- Los cambios en `./lp2_reniec_service/` se recargan automáticamente
- Uvicorn con `--reload` está habilitado
- Los archivos Python se watchean en tiempo real

## 📊 Monitoreo y Logs

### Ver logs en tiempo real
```bash
# Todos los servicios
docker-compose -f docker-compose.main.yml -f docker-compose.override.yml logs -f

# Servicio específico
docker-compose -f docker-compose.main.yml -f docker-compose.override.yml logs -f servicio-banco-lp1
docker-compose -f docker-compose.main.yml -f docker-compose.override.yml logs -f servicio-reniec-lp2
```

### Dashboards de Monitoreo
- **Grafana**: http://localhost:3000 (admin/admin123_dev)
- **Prometheus**: http://localhost:9090
- **RabbitMQ Management**: http://localhost:15672 (admin/admin123_dev)

### Health Checks
- **Banco**: http://localhost:8080/actuator/health
- **RENIEC**: http://localhost:8000/health

## 🗃️ Gestión de Datos

### Bases de Datos
```bash
# Conectar a PostgreSQL
docker-compose -f docker-compose.main.yml -f docker-compose.override.yml exec bd1_postgresql psql -U banco_user -d banco_db_dev

# Conectar a MySQL
docker-compose -f docker-compose.main.yml -f docker-compose.override.yml exec bd2_mysql mysql -u reniec_user -p reniec_db_dev
```

### Redis
```bash
# Conectar a Redis
docker-compose -f docker-compose.main.yml -f docker-compose.override.yml exec redis redis-cli -a redispass_dev
```

## 🔨 Comandos Útiles

### Desarrollo
```bash
# Iniciar en segundo plano
docker-compose -f docker-compose.main.yml -f docker-compose.override.yml up -d

# Reconstruir servicios específicos
docker-compose -f docker-compose.main.yml -f docker-compose.override.yml up --build servicio-banco-lp1

# Ver logs en tiempo real
docker-compose -f docker-compose.main.yml -f docker-compose.override.yml logs -f --tail=100

# Reiniciar servicio específico
docker-compose -f docker-compose.main.yml -f docker-compose.override.yml restart servicio-banco-lp1

# Parar todos los servicios
docker-compose -f docker-compose.main.yml -f docker-compose.override.yml down

# Parar y eliminar volúmenes (CUIDADO: elimina datos)
docker-compose -f docker-compose.main.yml -f docker-compose.override.yml down -v
```

### Limpieza
```bash
# Limpiar imágenes no utilizadas
docker system prune -a

# Limpiar volúmenes huérfanos
docker volume prune

# Reiniciar completamente (elimina todos los datos)
docker-compose -f docker-compose.main.yml -f docker-compose.override.yml down -v --rmi all
```

## 🚨 Troubleshooting

### Problemas Comunes

#### 1. Puertos ocupados
```bash
# Verificar qué proceso usa el puerto
netstat -tulpn | grep :8080

# O usar lsof en macOS/Linux
lsof -i :8080
```

#### 2. Servicios no inician
```bash
# Verificar logs de servicios específicos
docker-compose -f docker-compose.main.yml -f docker-compose.override.yml logs bd1_postgresql

# Verificar recursos del sistema
docker system df
docker stats
```

#### 3. Problemas de hot reload
```bash
# Verificar volúmenes montados
docker-compose -f docker-compose.main.yml -f docker-compose.override.yml exec servicio-banco-lp1 ls -la /app

# Verificar permisos
docker-compose -f docker-compose.main.yml -f docker-compose.override.yml exec servicio-banco-lp1 whoami
```

#### 4. Problemas de red
```bash
# Verificar conectividad entre servicios
docker-compose -f docker-compose.main.yml -f docker-compose.override.yml exec servicio-banco-lp1 ping redis

# Verificar configuración de red
docker network ls
docker network inspect shibasito-sistema-distribuido_shibasito-network
```

## 📁 Estructura de Volúmenes

```
./lp1-servicio-banco/          -> /app (Hot Reload)
./lp2_reniec_service/          -> /app (Hot Reload)
./logs/banco/                  -> /app/logs
./logs/reniec/                 -> /app/logs
./config/dev/                  -> /app/config/dev (configuración desarrollo)
```

## 🔐 Variables de Entorno

Las variables de entorno específicas de desarrollo están definidas en `.env.development`. Para usar estas variables:

```bash
docker-compose -f docker-compose.main.yml -f docker-compose.override.yml --env-file .env.development up
```

## 🎯 Configuración IDE

### IntelliJ IDEA
1. Configurar debugging remoto en puerto 5005 (Java) y 5678 (Python)
2. Instalar plugins de Spring Boot y FastAPI
3. Configurar run configurations para usar el entorno de Docker

### Visual Studio Code
1. Instalar extensiones: 
   - Docker
   - Spring Boot Extension Pack
   - Python
   - REST Client
2. Configurar launch.json para debugging remoto
3. Usar Remote-Containers para desarrollo dentro de contenedores

## 📞 Soporte

Para problemas específicos del desarrollo:
1. Verificar logs de servicios
2. Revisar configuración de variables de entorno
3. Consultar documentación específica de Spring Boot y FastAPI
4. Verificar configuración de red y puertos