# Guía de Despliegue - Sistema Shibasito

## Tabla de Contenidos
1. [Estrategias de Despliegue](#estrategias-de-despliegue)
2. [Configuración de Ambientes](#configuración-de-ambientes)
3. [Procedimientos de Despliegue](#procedimientos-de-despliegue)
4. [Consideraciones de Seguridad](#consideraciones-de-seguridad)
5. [Procedimientos de Rollback](#procedimientos-de-rollback)
6. [Monitoreo Post-Despliegue](#monitoreo-post-despliegue)
7. [Troubleshooting](#troubleshooting)

---

## Estrategias de Despliegue

### Desarrollo (Development)
```yaml
# docker-compose.dev.yml
version: '3.8'
services:
  lp1-banco:
    build: ./lp1-servicio-banco
    environment:
      - SPRING_PROFILES_ACTIVE=dev
      - SPRING_DATASOURCE_URL=jdbc:postgresql://db-lp1:5432/shibasito_lp1_dev
    ports:
      - "8081:8080"
    
  lp2-reniec:
    build: ./lp2_reniec_service
    environment:
      - DATABASE_URL=mysql://user:password@db-lp2:3306/shibasito_lp2_dev
      - ENVIRONMENT=development
    ports:
      - "8001:8000"
    
  rabbitmq:
    image: rabbitmq:3-management
    environment:
      - RABBITMQ_DEFAULT_USER=devuser
      - RABBITMQ_DEFAULT_PASS=devpass
    ports:
      - "5672:5672"
      - "15672:15672"
      
  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
```

### Staging (Pre-producción)
```yaml
# docker-compose.staging.yml
version: '3.8'
services:
  lp1-banco:
    image: shibasito/lp1-banco:staging
    environment:
      - SPRING_PROFILES_ACTIVE=staging
      - SPRING_DATASOURCE_URL=jdbc:postgresql://db-lp1:5432/shibasito_lp1_staging
      - SPRING_SECURITY_OAUTH2_CLIENT_REGISTRATION_KEYCLOAK_CLIENTSECRET=${KEYCLOAK_CLIENT_SECRET}
    deploy:
      replicas: 2
      resources:
        limits:
          memory: 1G
          cpus: '0.5'
          
  lp2-reniec:
    image: shibasito/lp2-reniec:staging
    environment:
      - DATABASE_URL=mysql://user:${STAGING_DB_PASSWORD}@db-lp2:3306/shibasito_lp2_staging
      - ENVIRONMENT=staging
      - LOG_LEVEL=INFO
    deploy:
      replicas: 2
      resources:
        limits:
          memory: 512M
          cpus: '0.3'
```

### Producción (Production)
```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  lp1-banco:
    image: shibasito/lp1-banco:${IMAGE_TAG}
    environment:
      - SPRING_PROFILES_ACTIVE=prod
      - SPRING_DATASOURCE_URL=jdbc:postgresql://db-lp1:5432/shibasito_lp1_prod
      - SPRING_SECURITY_OAUTH2_CLIENT_REGISTRATION_KEYCLOAK_CLIENTSECRET=${KEYCLOAK_CLIENT_SECRET}
      - SPRING_JPA_HIBERNATE_DDL_AUTO=validate
      - SERVER_SHUTDOWN=graceful
    deploy:
      replicas: 3
      resources:
        limits:
          memory: 2G
          cpus: '1.0'
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
        
  lp2-reniec:
    image: shibasito/lp2-reniec:${IMAGE_TAG}
    environment:
      - DATABASE_URL=mysql://user:${PROD_DB_PASSWORD}@db-lp2:3306/shibasito_lp2_prod
      - ENVIRONMENT=production
      - LOG_LEVEL=WARNING
      - WORKERS=4
    deploy:
      replicas: 3
      resources:
        limits:
          memory: 1G
          cpus: '0.5'
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
```

---

## Configuración de Ambientes

### Variables de Entorno por Ambiente

#### Desarrollo (.env.development)
```bash
# Base URLs
LP1_API_URL=http://localhost:8081/api/v1
LP2_API_URL=http://localhost:8001/api/v1

# Database Configuration
DEV_DB_PASSWORD=devpassword123

# Security
JWT_SECRET=development-jwt-secret-key
KEYCLOAK_CLIENT_SECRET=dev-client-secret

# Message Queue
RABBITMQ_USER=devuser
RABBITMQ_PASSWORD=devpass
RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672

# Redis
REDIS_PASSWORD=
REDIS_HOST=localhost
REDIS_PORT=6379

# Monitoring
ENABLE_METRICS=true
ENABLE_TRACING=true
LOG_LEVEL=DEBUG
```

#### Staging (.env.staging)
```bash
# Base URLs
LP1_API_URL=https://lp1.staging.shibasito.com/api/v1
LP2_API_URL=https://lp2.staging.shibasito.com/api/v1

# Database Configuration
STAGING_DB_PASSWORD=${STAGING_DB_SECRET}

# Security
JWT_SECRET=${STAGING_JWT_SECRET}
KEYCLOAK_CLIENT_SECRET=${STAGING_KEYCLOAK_SECRET}

# Message Queue
RABBITMQ_USER=${RABBITMQ_USER}
RABBITMQ_PASSWORD=${RABBITMQ_PASSWORD}
RABBITMQ_HOST=rabbitmq.staging
RABBITMQ_PORT=5672

# Redis
REDIS_PASSWORD=${REDIS_PASSWORD}
REDIS_HOST=redis.staging
REDIS_PORT=6379

# Monitoring
ENABLE_METRICS=true
ENABLE_TRACING=true
LOG_LEVEL=INFO
PROMETHEUS_ENABLED=true
```

#### Producción (.env.production)
```bash
# Base URLs
LP1_API_URL=https://lp1.shibasito.com/api/v1
LP2_API_URL=https://lp2.shibasito.com/api/v1

# Database Configuration
PROD_DB_PASSWORD=${PROD_DB_SECRET}

# Security
JWT_SECRET=${PROD_JWT_SECRET}
KEYCLOAK_CLIENT_SECRET=${PROD_KEYCLOAK_SECRET}
ENCRYPTION_KEY=${ENCRYPTION_KEY}

# Message Queue
RABBITMQ_USER=${RABBITMQ_USER}
RABBITMQ_PASSWORD=${RABBITMQ_PASSWORD}
RABBITMQ_HOST=rabbitmq.prod
RABBITMQ_PORT=5672

# Redis
REDIS_PASSWORD=${REDIS_PASSWORD}
REDIS_HOST=redis.prod
REDIS_PORT=6379

# Monitoring
ENABLE_METRICS=true
ENABLE_TRACING=true
LOG_LEVEL=WARNING
PROMETHEUS_ENABLED=true
GRAFANA_ENABLED=true
ALERTING_ENABLED=true
```

### Configuración de Red

#### Docker Network para Producción
```yaml
# networks.yml
networks:
  frontend:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
  backend:
    driver: bridge
    ipam:
      config:
        - subnet: 172.21.0.0/16
  database:
    driver: bridge
    internal: true
    ipam:
      config:
        - subnet: 172.22.0.0/16
```

#### Configuración de SSL/TLS
```nginx
# nginx/prod/nginx.conf
upstream lp1_backend {
    server lp1-banco-1:8080;
    server lp1-banco-2:8080;
    server lp1-banco-3:8080;
    keepalive 32;
}

upstream lp2_backend {
    server lp2-reniec-1:8000;
    server lp2-reniec-2:8000;
    server lp2-reniec-3:8000;
    keepalive 32;
}

server {
    listen 443 ssl http2;
    server_name lp1.shibasito.com;
    
    ssl_certificate /etc/ssl/certs/shibasito.com.crt;
    ssl_certificate_key /etc/ssl/private/shibasito.com.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    
    location /api/v1/ {
        proxy_pass http://lp1_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }
}
```

---

## Procedimientos de Despliegue

### Despliegue en Desarrollo

#### Paso 1: Verificar Prerrequisitos
```bash
#!/bin/bash
# check-dev-prerequisites.sh

echo "Verificando prerrequisitos para desarrollo..."

# Verificar Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker no está instalado"
    exit 1
fi
echo "✅ Docker instalado: $(docker --version)"

# Verificar Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose no está instalado"
    exit 1
fi
echo "✅ Docker Compose instalado: $(docker-compose --version)"

# Verificar variables de entorno
if [ ! -f .env.development ]; then
    echo "⚠️ Archivo .env.development no encontrado"
    echo "Copiando template..."
    cp .env.development.template .env.development
fi

# Verificar puertos disponibles
ports=(8081 8001 5672 6379 5432 3306)
for port in "${ports[@]}"; do
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo "⚠️ Puerto $port está en uso"
    else
        echo "✅ Puerto $port disponible"
    fi
done

echo "✅ Verificación completada"
```

#### Paso 2: Construir y Desplegar Servicios
```bash
#!/bin/bash
# deploy-dev.sh

echo "Iniciando despliegue en desarrollo..."

# Cargar variables de entorno
set -a
source .env.development
set +a

# Limpiar containers anteriores
echo "🧹 Limpiando containers anteriores..."
docker-compose -f docker-compose.dev.yml down -v --remove-orphans

# Construir imágenes
echo "🔨 Construyendo imágenes..."
docker-compose -f docker-compose.dev.yml build --no-cache

# Iniciar servicios base
echo "🚀 Iniciando servicios base..."
docker-compose -f docker-compose.dev.yml up -d rabbitmq redis db-lp1 db-lp2

# Esperar a que los servicios base estén listos
echo "⏳ Esperando servicios base..."
sleep 30

# Verificar RabbitMQ
until docker exec $(docker ps -qf "name=rabbitmq") rabbitmqctl status; do
    echo "⏳ Esperando RabbitMQ..."
    sleep 5
done

# Verificar PostgreSQL
until docker exec $(docker ps -qf "name=db-lp1") pg_isready -U postgres; do
    echo "⏳ Esperando PostgreSQL..."
    sleep 5
done

# Verificar MySQL
until docker exec $(docker ps -qf "name=db-lp2") mysqladmin ping -h localhost -uroot -p${DEV_DB_PASSWORD}; do
    echo "⏳ Esperando MySQL..."
    sleep 5
done

# Ejecutar migraciones de base de datos
echo "📊 Ejecutando migraciones..."
docker-compose -f docker-compose.dev.yml exec -T db-lp1 psql -U postgres -c "CREATE DATABASE shibasito_lp1_dev;" 2>/dev/null || true
docker-compose -f docker-compose.dev.yml exec -T db-lp2 mysql -u root -p${DEV_DB_PASSWORD} -e "CREATE DATABASE IF NOT EXISTS shibasito_lp2_dev;" 2>/dev/null || true

# Iniciar servicios de aplicación
echo "🚀 Iniciando servicios de aplicación..."
docker-compose -f docker-compose.dev.yml up -d lp1-banco lp2-reniec

# Verificar estado de servicios
echo "🔍 Verificando estado de servicios..."
docker-compose -f docker-compose.dev.yml ps

echo "✅ Despliegue en desarrollo completado"
```

#### Paso 3: Verificar Funcionamiento
```bash
#!/bin/bash
# verify-dev-deployment.sh

echo "Verificando despliegue en desarrollo..."

# Verificar LP1
echo "🔍 Verificando LP1 Banking Service..."
if curl -f http://localhost:8081/actuator/health > /dev/null 2>&1; then
    echo "✅ LP1 responde correctamente"
    curl -s http://localhost:8081/actuator/health | jq .
else
    echo "❌ LP1 no responde"
fi

# Verificar LP2
echo "🔍 Verificando LP2 RENIEC Service..."
if curl -f http://localhost:8001/health > /dev/null 2>&1; then
    echo "✅ LP2 responde correctamente"
    curl -s http://localhost:8001/health | jq .
else
    echo "❌ LP2 no responde"
fi

# Verificar RabbitMQ
echo "🔍 Verificando RabbitMQ..."
if curl -f http://localhost:15672/api/overview > /dev/null 2>&1; then
    echo "✅ RabbitMQ Management Interface disponible"
    echo "   URL: http://localhost:15672 (devuser/devpass)"
else
    echo "❌ RabbitMQ Management Interface no disponible"
fi

# Verificar Redis
echo "🔍 Verificando Redis..."
if docker exec $(docker ps -qf "name=redis") redis-cli ping > /dev/null 2>&1; then
    echo "✅ Redis responde correctamente"
else
    echo "❌ Redis no responde"
fi

echo "✅ Verificación completada"
```

### Despliegue en Staging

#### Paso 1: Preparar Imagen Docker
```dockerfile
# Dockerfile.staging
FROM openjdk:17-jdk-slim as builder
WORKDIR /app
COPY . .
RUN ./gradlew clean build -x test

FROM openjdk:17-jre-slim
COPY --from=builder /app/build/libs/*.jar app.jar
COPY --chown=www-data:www-data docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8080
ENTRYPOINT ["/entrypoint.sh"]
```

```bash
#!/bin/bash
# build-staging-images.sh

echo "Construyendo imágenes para staging..."

# Variables
IMAGE_TAG="staging"
REGISTRY="registry.shibasito.com"

# Construir LP1
echo "🔨 Construyendo imagen LP1..."
cd lp1-servicio-banco
docker build -f Dockerfile.staging -t ${REGISTRY}/shibasito/lp1-banco:${IMAGE_TAG} .
docker tag ${REGISTRY}/shibasito/lp1-banco:${IMAGE_TAG} ${REGISTRY}/shibasito/lp1-banco:latest-staging

# Construir LP2
echo "🔨 Construyendo imagen LP2..."
cd ../lp2_reniec_service
docker build -f Dockerfile.staging -t ${REGISTRY}/shibasito/lp2-reniec:${IMAGE_TAG} .
docker tag ${REGISTRY}/shibasito/lp2-reniec:${IMAGE_TAG} ${REGISTRY}/shibasito/lp2-reniec:latest-staging

# Subir imágenes al registry
echo "📤 Subiendo imágenes al registry..."
docker push ${REGISTRY}/shibasito/lp1-banco:${IMAGE_TAG}
docker push ${REGISTRY}/shibasito/lp2-reniec:${IMAGE_TAG}

echo "✅ Imágenes construidas y subidas exitosamente"
```

#### Paso 2: Desplegar en Staging
```bash
#!/bin/bash
# deploy-staging.sh

echo "Iniciando despliegue en staging..."

# Variables
ENVIRONMENT="staging"
IMAGE_TAG="staging"
DEPLOYMENT_ID=$(date +%Y%m%d-%H%M%S)

# Verificar prerrequisitos
if [ ! -f .env.staging ]; then
    echo "❌ Archivo .env.staging no encontrado"
    exit 1
fi

# Cargar configuración
set -a
source .env.staging
set +a

# Crear backup de la versión actual
echo "💾 Creando backup de versión actual..."
docker-compose -f docker-compose.staging.yml exec -T lp1-banco curl -X POST http://localhost:8080/actuator/shutdown 2>/dev/null || true

# Desplegar servicios
echo "🚀 Desplegando servicios en staging..."
docker-compose -f docker-compose.staging.yml pull
docker-compose -f docker-compose.staging.yml up -d

# Esperar inicialización
echo "⏳ Esperando inicialización de servicios..."
sleep 60

# Verificar despliegue
echo "🔍 Verificando despliegue..."
./verify-staging-deployment.sh

if [ $? -eq 0 ]; then
    echo "✅ Despliegue en staging exitoso"
    
    # Ejecutar tests de integración
    echo "🧪 Ejecutando tests de integración..."
    ./run-staging-tests.sh
    
    if [ $? -eq 0 ]; then
        echo "✅ Tests de integración pasados"
        echo "✅ Despliegue en staging completado exitosamente"
    else
        echo "❌ Tests de integración fallaron"
        ./rollback-staging.sh
        exit 1
    fi
else
    echo "❌ Despliegue en staging falló"
    ./rollback-staging.sh
    exit 1
fi
```

### Despliegue en Producción

#### Paso 1: Preparar Despliegue
```bash
#!/bin/bash
# prepare-production-deployment.sh

echo "Preparando despliegue en producción..."

# Variables
IMAGE_TAG=${1:-"latest"}
DEPLOYMENT_ID=$(date +%Y%m%d-%H%M%S)
BACKUP_DIR="/opt/shibasito/backups/${DEPLOYMENT_ID}"

# Crear directorio de backup
mkdir -p ${BACKUP_DIR}

# Verificar que el tag de imagen existe
if ! docker manifest inspect registry.shibasito.com/shibasito/lp1-banco:${IMAGE_TAG} > /dev/null; then
    echo "❌ Imagen LP1 ${IMAGE_TAG} no encontrada en registry"
    exit 1
fi

if ! docker manifest inspect registry.shibasito.com/shibasito/lp2-reniec:${IMAGE_TAG} > /dev/null; then
    echo "❌ Imagen LP2 ${IMAGE_TAG} no encontrada en registry"
    exit 1
fi

# Crear backup de bases de datos
echo "💾 Creando backup de bases de datos..."
./backup-databases.sh ${BACKUP_DIR}

# Crear backup de configuraciones
echo "💾 Creando backup de configuraciones..."
cp docker-compose.prod.yml ${BACKUP_DIR}/
cp -r nginx/ ${BACKUP_DIR}/ 2>/dev/null || true
cp .env.production ${BACKUP_DIR}/

# Verificar espacio en disco
DISK_USAGE=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
if [ ${DISK_USAGE} -gt 80 ]; then
    echo "⚠️ Advertencia: Uso de disco ${DISK_USAGE}%"
fi

echo "✅ Preparación completada"
echo "Deployment ID: ${DEPLOYMENT_ID}"
echo "Backup directory: ${BACKUP_DIR}"
```

#### Paso 2: Ejecutar Despliegue Blue-Green
```bash
#!/bin/bash
# blue-green-deployment.sh

echo "Iniciando despliegue Blue-Green en producción..."

# Variables
IMAGE_TAG=${1:-"latest"}
CURRENT_ENV="green" # o "blue"
NEW_ENV="blue" # o "green"

# Determinar entorno actual
if docker-compose -f docker-compose.prod.yml ps | grep -q "${CURRENT_ENV}_lp1-banco"; then
    NEW_ENV="blue"
    CURRENT_ENV="green"
else
    NEW_ENV="green" 
    CURRENT_ENV="blue"
fi

echo "🔄 Transicionando de ${CURRENT_ENV} a ${NEW_ENV}"

# Configurar nuevas variables de entorno
cp .env.production .env.production.${NEW_ENV}
sed -i "s/ENVIRONMENT_LABEL=.*/ENVIRONMENT_LABEL=${NEW_ENV}/g" .env.production.${NEW_ENV}
sed -i "s/IMAGE_TAG=.*/IMAGE_TAG=${IMAGE_TAG}/g" .env.production.${NEW_ENV}

# Iniciar nuevos servicios
echo "🚀 Iniciando servicios ${NEW_ENV}..."
docker-compose -f docker-compose.blue-green.yml --env-file .env.production.${NEW_ENV} up -d ${NEW_ENV}_lp1-banco ${NEW_ENV}_lp2-reniec

# Esperar inicialización
echo "⏳ Esperando inicialización de servicios..."
sleep 120

# Ejecutar health checks
echo "🔍 Ejecutando health checks..."
./health-check-production.sh ${NEW_ENV}

if [ $? -eq 0 ]; then
    echo "✅ Health checks pasados para ${NEW_ENV}"
    
    # Ejecutar tests de humo
    echo "🧪 Ejecutando tests de humo..."
    ./run-production-smoke-tests.sh ${NEW_ENV}
    
    if [ $? -eq 0 ]; then
        echo "✅ Tests de humo pasados"
        
        # Cambiar tráfico al nuevo entorno
        echo "🔀 Cambiando tráfico a ${NEW_ENV}..."
        ./switch-traffic.sh ${NEW_ENV}
        
        # Mantener entorno anterior en standby por 30 minutos
        echo "⏰ Manteniendo ${CURRENT_ENV} en standby por 30 minutos..."
        sleep 1800
        
        # Si todo está bien, limpiar entorno anterior
        echo "🧹 Limpiando entorno ${CURRENT_ENV}..."
        docker-compose -f docker-compose.blue-green.yml stop ${CURRENT_ENV}_lp1-banco ${CURRENT_ENV}_lp2-reniec
        docker-compose -f docker-compose.blue-green.yml rm -f ${CURRENT_ENV}_lp1-banco ${CURRENT_ENV}_lp2-reniec
        
        echo "✅ Despliegue Blue-Green completado exitosamente"
        
        # Actualizar DNS
        ./update-dns.sh ${NEW_ENV}
        
    else
        echo "❌ Tests de humo fallaron"
        ./rollback-blue-green.sh ${NEW_ENV} ${CURRENT_ENV}
        exit 1
    fi
else
    echo "❌ Health checks fallaron para ${NEW_ENV}"
    ./rollback-blue-green.sh ${NEW_ENV} ${CURRENT_ENV}
    exit 1
fi
```

#### Paso 3: Health Checks de Producción
```bash
#!/bin/bash
# health-check-production.sh

ENV=${1:-"blue"}
TIMEOUT=300
INTERVAL=10

echo "Ejecutando health checks para entorno ${ENV}..."

# URLs de servicios
LP1_URL="https://lp1.shibasito.com/actuator/health"
LP2_URL="https://lp2.shibasito.com/health"

# Verificar LP1
echo "🔍 Verificando LP1 Banking Service..."
start_time=$(date +%s)
while [ $(( $(date +%s) - start_time )) -lt ${TIMEOUT} ]; do
    response=$(curl -s -w "%{http_code}" -o /dev/null ${LP1_URL})
    if [ "${response}" = "200" ]; then
        echo "✅ LP1 responde correctamente (${response})"
        break
    fi
    echo "⏳ Esperando LP1... (${response})"
    sleep ${INTERVAL}
done

if [ "${response}" != "200" ]; then
    echo "❌ LP1 no responde después de ${TIMEOUT} segundos"
    exit 1
fi

# Verificar LP2
echo "🔍 Verificando LP2 RENIEC Service..."
start_time=$(date +%s)
while [ $(( $(date +%s) - start_time )) -lt ${TIMEOUT} ]; do
    response=$(curl -s -w "%{http_code}" -o /dev/null ${LP2_URL})
    if [ "${response}" = "200" ]; then
        echo "✅ LP2 responde correctamente (${response})"
        break
    fi
    echo "⏳ Esperando LP2... (${response})"
    sleep ${INTERVAL}
done

if [ "${response}" != "200" ]; then
    echo "❌ LP2 no responde después de ${TIMEOUT} segundos"
    exit 1
fi

# Verificar conectividad entre servicios
echo "🔍 Verificando conectividad entre servicios..."
./test-service-connectivity.sh

if [ $? -eq 0 ]; then
    echo "✅ Todos los health checks pasaron"
    exit 0
else
    echo "❌ Algunos health checks fallaron"
    exit 1
fi
```

---

## Consideraciones de Seguridad

### Configuración de Seguridad en Producción

#### Variables de Entorno Seguras
```bash
# Generar secretos seguros
JWT_SECRET=$(openssl rand -base64 64)
ENCRYPTION_KEY=$(openssl rand -base64 32)
DB_PASSWORD=$(openssl rand -base64 24)

# Almacenar en vault seguro
vault kv put secret/shibasito/production \
    jwt_secret="${JWT_SECRET}" \
    encryption_key="${ENCRYPTION_KEY}" \
    db_password="${DB_PASSWORD}"
```

#### Configuración de Firewall
```bash
#!/bin/bash
# configure-firewall.sh

echo "Configurando firewall para producción..."

# Resetear reglas
iptables -F
iptables -X
iptables -t nat -F
iptables -t nat -X

# Políticas por defecto
iptables -P INPUT DROP
iptables -P FORWARD DROP
iptables -P OUTPUT ACCEPT

# Permitir loopback
iptables -A INPUT -i lo -j ACCEPT

# Permitir conexiones establecidas
iptables -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT

# Permitir SSH (solo desde IPs autorizadas)
iptables -A INPUT -p tcp --dport 22 -s 10.0.0.0/8 -j ACCEPT
iptables -A INPUT -p tcp --dport 22 -s 192.168.0.0/16 -j ACCEPT

# Permitir HTTP/HTTPS
iptables -A INPUT -p tcp --dport 80 -j ACCEPT
iptables -A INPUT -p tcp --dport 443 -j ACCEPT

# Permitir comunicación interna entre contenedores
iptables -A INPUT -i docker0 -j ACCEPT
iptables -A INPUT -i br-* -j ACCEPT

# Rate limiting para prevención DoS
iptables -A INPUT -p tcp --dport 80 -m limit --limit 25/minute --limit-burst 100 -j ACCEPT
iptables -A INPUT -p tcp --dport 443 -m limit --limit 25/minute --limit-burst 100 -j ACCEPT

# Logging de paquetes sospechosos
iptables -A INPUT -m limit --limit 5/min -j LOG --log-prefix "iptables denied: " --log-level 7

echo "✅ Firewall configurado"
```

#### Configuración de SSL/TLS
```bash
#!/bin/bash
# setup-ssl.sh

echo "Configurando certificados SSL/TLS..."

# Usar Let's Encrypt para certificados automáticos
certbot --nginx \
    --non-interactive \
    --agree-tos \
    --email admin@shibasito.com \
    -d lp1.shibasito.com \
    -d lp2.shibasito.com \
    --expand

# Verificar renovación automática
echo "0 12 * * * /usr/bin/certbot renew --quiet" | crontab -

# Configurar cipher suites seguros
cat > /etc/nginx/ssl-config.conf << 'EOF'
# SSL Configuration
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;
ssl_prefer_server_ciphers off;
ssl_session_cache shared:SSL:10m;
ssl_session_timeout 10m;
ssl_stapling on;
ssl_stapling_verify on;
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
add_header X-Frame-Options DENY always;
add_header X-Content-Type-Options nosniff always;
add_header X-XSS-Protection "1; mode=block" always;
EOF

echo "✅ SSL/TLS configurado"
```

### Auditoría y Monitoreo de Seguridad

#### Configuración de Logs de Seguridad
```yaml
# logging-security.yml
version: '3.8'
services:
  audit-logger:
    image: fluent/fluent-bit:latest
    volumes:
      - ./fluent-bit.conf:/fluent-bit/etc/fluent-bit.conf
      - /var/log:/var/log:ro
    environment:
      - ES_HOST=elasticsearch.prod
      - ES_PORT=9200
    networks:
      - backend
```

```
# fluent-bit.conf
[SERVICE]
    Flush         1
    Log_Level     info
    Daemon        off
    Parsers_File  parsers.conf

[INPUT]
    Name              tail
    Path              /var/log/shibasito/*.log
    Parser            json
    Tag               shibasito.*
    Refresh_Interval  5

[FILTER]
    Name    grep
    Match   shibasito.*
    Regex   level (ERROR|WARN)

[OUTPUT]
    Name  es
    Match shibasito.*
    Host  elasticsearch.prod
    Port  9200
    Index shibasito-security
    Type  _doc
```

---

## Procedimientos de Rollback

### Rollback Automático

#### Script de Rollback Automático
```bash
#!/bin/bash
# auto-rollback.sh

echo "Iniciando rollback automático..."

# Variables
CURRENT_ENV=${1:-"blue"}
PREVIOUS_ENV=${2:-"green"}
TIMESTAMP=$(date +%Y%m%d-%H%M%S)

# Detectar problemas automáticamente
ALERT_COUNT=$(curl -s "http://localhost:9090/api/v1/query?query=ALERTS{alertstate='firing'}" | jq -r '.data.result | length')

if [ ${ALERT_COUNT} -gt 5 ]; then
    echo "🚨 Detectados ${ALERT_COUNT} alertas activas - Iniciando rollback automático"
    
    # Cambiar tráfico inmediatamente
    ./switch-traffic.sh ${PREVIOUS_ENV}
    
    # Detener servicios problemáticos
    docker-compose -f docker-compose.blue-green.yml stop ${CURRENT_ENV}_lp1-banco ${CURRENT_ENV}_lp2-reniec
    
    # Notificar equipo
    ./notify-rollback.sh "Rollback automático ejecutado debido a ${ALERT_COUNT} alertas" ${TIMESTAMP}
    
    # Ejecutar investigación post-rollback
    ./post-mortem.sh ${TIMESTAMP} &
    
    echo "✅ Rollback automático completado"
else
    echo "ℹ️ Alertas dentro de rango normal (${ALERT_COUNT}) - No se requiere rollback"
fi
```

### Rollback Manual

#### Procedimiento de Rollback Manual
```bash
#!/bin/bash
# manual-rollback.sh

echo "Iniciando rollback manual..."

# Variables
ROLLBACK_ENV=${1:-"green"}  # Entorno al que hacer rollback
TIMESTAMP=$(date +%Y%m%d-%H%M%S)

echo "Rollback hacia: ${ROLLBACK_ENV}"
echo "Timestamp: ${TIMESTAMP}"

read -p "¿Confirmar rollback? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Rollback cancelado"
    exit 1
fi

# Paso 1: Cambiar tráfico
echo "🔀 Cambiando tráfico a ${ROLLBACK_ENV}..."
./switch-traffic.sh ${ROLLBACK_ENV}

# Paso 2: Verificar que el tráfico se cambió correctamente
echo "🔍 Verificando cambio de tráfico..."
sleep 30

# Verificar logs de nginx para confirmar el cambio
if nginx -t && nginx -s reload; then
    echo "✅ Tráfico cambiado exitosamente"
else
    echo "❌ Error al cambiar tráfico"
    exit 1
fi

# Paso 3: Verificar funcionamiento del sistema
echo "🔍 Verificando funcionamiento post-rollback..."
./verify-rollback.sh

if [ $? -eq 0 ]; then
    echo "✅ Rollback manual completado exitosamente"
    
    # Notificar equipo
    ./notify-rollback.sh "Rollback manual completado exitosamente" ${TIMESTAMP}
else
    echo "❌ Problemas detectados post-rollback"
    exit 1
fi
```

#### Script de Verificación Post-Rollback
```bash
#!/bin/bash
# verify-rollback.sh

echo "Verificando funcionamiento post-rollback..."

# Verificar endpoints críticos
ENDPOINTS=(
    "https://lp1.shibasito.com/api/v1/health"
    "https://lp2.shibasito.com/api/v1/health"
)

FAILED=0

for endpoint in "${ENDPOINTS[@]}"; do
    echo "🔍 Verificando ${endpoint}..."
    
    response=$(curl -s -w "%{http_code}" -o /dev/null --max-time 30 "${endpoint}")
    if [ "${response}" = "200" ]; then
        echo "✅ ${endpoint} responde correctamente"
    else
        echo "❌ ${endpoint} responde con código ${response}"
        FAILED=$((FAILED + 1))
    fi
done

# Verificar métricas críticas
echo "📊 Verificando métricas críticas..."

# Latencia promedio debe ser < 200ms
LATENCY=$(curl -s "http://localhost:9090/api/v1/query?query=avg(rate(http_request_duration_seconds_sum[5m]))" | jq -r '.data.result[0].value[1]')
if [ $(echo "${LATENCY} < 0.2" | bc) -eq 1 ]; then
    echo "✅ Latencia promedio OK: ${LATENCY}s"
else
    echo "⚠️ Latencia alta: ${LATENCY}s"
    FAILED=$((FAILED + 1))
fi

# Tasa de errores debe ser < 1%
ERROR_RATE=$(curl -s "http://localhost:9090/api/v1/query?query=rate(http_requests_total{status=~'5..'}[5m])" | jq -r '.data.result[0].value[1]')
if [ $(echo "${ERROR_RATE} < 0.01" | bc) -eq 1 ]; then
    echo "✅ Tasa de errores OK: ${ERROR_RATE}"
else
    echo "⚠️ Tasa de errores alta: ${ERROR_RATE}"
    FAILED=$((FAILED + 1))
fi

if [ ${FAILED} -eq 0 ]; then
    echo "✅ Verificación post-rollback exitosa"
    exit 0
else
    echo "❌ ${FAILED} verificaciones fallaron"
    exit 1
fi
```

### Recuperación de Base de Datos

#### Script de Recuperación de BD
```bash
#!/bin/bash
# restore-database.sh

echo "Iniciando recuperación de base de datos..."

# Variables
BACKUP_DIR=${1:-"/opt/shibasito/backups"}
TARGET_ENV=${2:-"production"}

# Listar backups disponibles
echo "📁 Backups disponibles:"
ls -la ${BACKUP_DIR}/*/database-*.sql 2>/dev/null || echo "No hay backups de BD disponibles"

read -p "Seleccionar backup a restaurar (nombre completo): " BACKUP_FILE

if [ ! -f "${BACKUP_DIR}/${BACKUP_FILE}" ]; then
    echo "❌ Archivo de backup no encontrado"
    exit 1
fi

echo "📦 Restaurando backup: ${BACKUP_FILE}"

# Para PostgreSQL (LP1)
if [[ ${BACKUP_FILE} == *"lp1"* ]]; then
    echo "🗄️ Restaurando PostgreSQL (LP1)..."
    docker exec -i $(docker ps -qf "name=db-lp1") psql -U postgres -c "DROP DATABASE IF EXISTS shibasito_lp1_prod;"
    docker exec -i $(docker ps -qf "name=db-lp1") psql -U postgres -c "CREATE DATABASE shibasito_lp1_prod;"
    docker exec -i $(docker ps -qf "name=db-lp1") psql -U postgres shibasito_lp1_prod < "${BACKUP_DIR}/${BACKUP_FILE}"
fi

# Para MySQL (LP2)
if [[ ${BACKUP_FILE} == *"lp2"* ]]; then
    echo "🗄️ Restaurando MySQL (LP2)..."
    docker exec -i $(docker ps -qf "name=db-lp2") mysql -u root -p${PROD_DB_PASSWORD} -e "DROP DATABASE IF EXISTS shibasito_lp2_prod;"
    docker exec -i $(docker ps -qf "name=db-lp2") mysql -u root -p${PROD_DB_PASSWORD} -e "CREATE DATABASE shibasito_lp2_prod;"
    docker exec -i $(docker ps -qf "name=db-lp2") mysql -u root -p${PROD_DB_PASSWORD} shibasito_lp2_prod < "${BACKUP_DIR}/${BACKUP_FILE}"
fi

echo "✅ Recuperación de base de datos completada"
```

---

## Monitoreo Post-Despliegue

### Configuración de Alertas

#### Alertas Críticas
```yaml
# prometheus/alerts.yml
groups:
  - name: shibasito.critical
    rules:
      - alert: ServiceDown
        expr: up == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Servicio {{ $labels.job }} está caído"
          description: "El servicio {{ $labels.instance }} ha estado caído por más de 1 minuto"
      
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Alta tasa de errores en {{ $labels.job }}"
          description: "Tasa de errores 5xx: {{ $value }} por segundo"
      
      - alert: DatabaseConnectionFailure
        expr: database_connections_failed > 0
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Fallo de conexión a base de datos"
          description: "Servicio {{ $labels.job }} no puede conectar a la base de datos"
      
      - alert: MessageQueueDown
        expr: rabbitmq_queue_messages == -1
        for: 3m
        labels:
          severity: critical
        annotations:
          summary: "RabbitMQ no disponible"
          description: "La cola de mensajes no está disponible"
```

#### Alertas de Advertencia
```yaml
  - name: shibasito.warning
    rules:
      - alert: HighLatency
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 1
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Latencia alta detectada"
          description: "P95 de latencia: {{ $value }}s"
      
      - alert: HighMemoryUsage
        expr: (node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes > 0.85
        for: 15m
        labels:
          severity: warning
        annotations:
          summary: "Uso alto de memoria"
          description: "Uso de memoria: {{ $value | humanizePercentage }}"
      
      - alert: DiskSpaceLow
        expr: (node_filesystem_avail_bytes{mountpoint="/"} / node_filesystem_size_bytes{mountpoint="/"}) < 0.15
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Espacio en disco bajo"
          description: "Espacio disponible: {{ $value | humanizePercentage }}"
```

### Dashboard de Monitoreo

#### Configuración de Grafana
```json
{
  "dashboard": {
    "title": "Shibasito - Post Deployment Monitoring",
    "panels": [
      {
        "title": "Service Health",
        "type": "stat",
        "targets": [
          {
            "expr": "up{job=~\"lp1.*|lp2.*\"}",
            "legendFormat": "{{job}}"
          }
        ]
      },
      {
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])",
            "legendFormat": "{{job}} - {{method}} {{status}}"
          }
        ]
      },
      {
        "title": "Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "P95"
          },
          {
            "expr": "histogram_quantile(0.50, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "P50"
          }
        ]
      },
      {
        "title": "Error Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total{status=~\"4..|5..\"}[5m])",
            "legendFormat": "{{job}} - {{status}}"
          }
        ]
      }
    ]
  }
}
```

### Métricas de Desempeño

#### Script de Métricas Post-Despliegue
```bash
#!/bin/bash
# generate-deployment-metrics.sh

DEPLOYMENT_ID=${1:-$(date +%Y%m%d-%H%M%S)}
OUTPUT_FILE="/opt/shibasito/metrics/deployment-${DEPLOYMENT_ID}.json"

echo "Generando métricas de despliegue: ${DEPLOYMENT_ID}"

# Recopilar métricas
METRICS=$(cat << EOF
{
  "deployment_id": "${DEPLOYMENT_ID}",
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "services": {
    "lp1_banco": {
      "status": "$(curl -s -w "%{http_code}" -o /dev/null https://lp1.shibasito.com/api/v1/health)",
      "response_time_ms": $(curl -s -w "%{time_total}" -o /dev/null https://lp1.shibasito.com/api/v1/health | awk '{print int($1 * 1000)}'),
      "memory_usage_mb": $(docker stats --no-stream --format "{{.MemUsage}}" lp1-banco-1 | awk '{print int($1)}'),
      "cpu_usage_percent": $(docker stats --no-stream --format "{{.CPUPerc}}" lp1-banco-1 | awk '{print int($1)}')
    },
    "lp2_reniec": {
      "status": "$(curl -s -w "%{http_code}" -o /dev/null https://lp2.shibasito.com/api/v1/health)",
      "response_time_ms": $(curl -s -w "%{time_total}" -o /dev/null https://lp2.shibasito.com/api/v1/health | awk '{print int($1 * 1000)}'),
      "memory_usage_mb": $(docker stats --no-stream --format "{{.MemUsage}}" lp2-reniec-1 | awk '{print int($1)}'),
      "cpu_usage_percent": $(docker stats --no-stream --format "{{.CPUPerc}}" lp2-reniec-1 | awk '{print int($1)}')
    }
  },
  "infrastructure": {
    "rabbitmq_status": "$(docker ps --filter "name=rabbitmq" --format "{{.Status}}" | wc -l)",
    "redis_status": "$(docker ps --filter "name=redis" --format "{{.Status}}" | wc -l)",
    "disk_usage_percent": $(df / | tail -1 | awk '{print $5}' | sed 's/%//'),
    "memory_usage_percent": $(free | grep Mem | awk '{printf("%.1f", $3/$2 * 100.0)}')
  }
}
EOF
)

echo ${METRICS} | jq '.' > ${OUTPUT_FILE}
echo "✅ Métricas guardadas en: ${OUTPUT_FILE}"
```

---

## Troubleshooting

### Diagnóstico de Problemas Comunes

#### Problemas de Conectividad

##### Servicios No Responden
```bash
#!/bin/bash
# diagnose-service-connectivity.sh

echo "🔍 Diagnosticando conectividad de servicios..."

# Verificar DNS
echo "🔍 Verificando resolución DNS..."
nslookup lp1.shibasito.com
nslookup lp2.shibasito.com

# Verificar conectividad de red
echo "🔍 Verificando conectividad de red..."
ping -c 3 lp1.shibasito.com
ping -c 3 lp2.shibasito.com

# Verificar puertos
echo "🔍 Verificando puertos..."
nc -zv lp1.shibasito.com 443
nc -zv lp2.shibasito.com 443

# Verificar certificados SSL
echo "🔍 Verificando certificados SSL..."
openssl s_client -connect lp1.shibasito.com:443 -servername lp1.shibasito.com < /dev/null 2>/dev/null | openssl x509 -noout -dates
openssl s_client -connect lp2.shibasito.com:443 -servername lp2.shibasito.com < /dev/null 2>/dev/null | openssl x509 -noout -dates

# Verificar configuración de nginx
echo "🔍 Verificando configuración de nginx..."
nginx -t

echo "✅ Diagnóstico de conectividad completado"
```

##### Problemas de Base de Datos
```bash
#!/bin/bash
# diagnose-database.sh

echo "🔍 Diagnosticando base de datos..."

# Verificar PostgreSQL (LP1)
echo "🔍 Verificando PostgreSQL..."
docker exec $(docker ps -qf "name=db-lp1") pg_isready -U postgres
docker exec $(docker ps -qf "name=db-lp1") psql -U postgres -c "SELECT version();"

# Verificar MySQL (LP2)
echo "🔍 Verificando MySQL..."
docker exec $(docker ps -qf "name=db-lp2") mysqladmin ping -h localhost -uroot -p${PROD_DB_PASSWORD}
docker exec $(docker ps -qf "name=db-lp2") mysql -u root -p${PROD_DB_PASSWORD} -e "SELECT VERSION();"

# Verificar conexiones activas
echo "🔍 Verificando conexiones activas..."
docker exec $(docker ps -qf "name=db-lp1") psql -U postgres -c "SELECT count(*) FROM pg_stat_activity;"
docker exec $(docker ps -qf "name=db-lp2") mysql -u root -p${PROD_DB_PASSWORD} -e "SHOW PROCESSLIST;"

# Verificar tamaño de bases de datos
echo "🔍 Verificando tamaño de bases de datos..."
docker exec $(docker ps -qf "name=db-lp1") psql -U postgres -c "SELECT pg_size_pretty(pg_database_size('shibasito_lp1_prod'));"
docker exec $(docker ps -qf "name=db-lp2") mysql -u root -p${PROD_DB_PASSWORD} -e "SELECT ROUND(SUM(data_length + index_length) / 1024 / 1024, 1) AS 'DB Size in MB' FROM information_schema.tables WHERE table_schema='shibasito_lp2_prod';"

echo "✅ Diagnóstico de base de datos completado"
```

#### Problemas de Performance

##### Análisis de Rendimiento
```bash
#!/bin/bash
# performance-analysis.sh

echo "📊 Analizando rendimiento del sistema..."

# CPU Usage
echo "🔍 CPU Usage:"
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}"

# Memory Usage
echo "🔍 Memory Usage:"
free -h

# Disk I/O
echo "🔍 Disk I/O:"
iostat -x 1 3

# Network Connections
echo "🔍 Network Connections:"
netstat -tuln | grep -E ':(8080|8000|443|80|5672|6379|5432|3306) '

# Top Processes
echo "🔍 Top Processes:"
top -b -n1 | head -20

# Docker System Info
echo "🔍 Docker System:"
docker system df
docker system info | grep -E "(Server Version|Storage Driver|Operating System)"

echo "✅ Análisis de rendimiento completado"
```

#### Problemas de Mensajes

##### Análisis de RabbitMQ
```bash
#!/bin/bash
# diagnose-rabbitmq.sh

echo "🔍 Diagnosticando RabbitMQ..."

# Estado general
echo "🔍 Estado de RabbitMQ:"
curl -s -u ${RABBITMQ_USER}:${RABBITMQ_PASSWORD} http://rabbitmq.shibasito.com:15672/api/overview | jq '.'

# Colas
echo "🔍 Estado de colas:"
curl -s -u ${RABBITMQ_USER}:${RABBITMQ_PASSWORD} http://rabbitmq.shibasito.com:15672/api/queues | jq '.[] | {name: .name, messages: .messages, consumers: .consumers}'

# Exchanges
echo "🔍 Estado de exchanges:"
curl -s -u ${RABBITMQ_USER}:${RABBITMQ_PASSWORD} http://rabbitmq.shibasito.com:15672/api/exchanges | jq '.[] | {name: .name, type: .type, durable: .durable}'

# Conexiones
echo "🔍 Conexiones activas:"
curl -s -u ${RABBITMQ_USER}:${RABBITMQ_PASSWORD} http://rabbitmq.shibasito.com:15672/api/connections | jq '.[] | {client_properties: .client_properties, state: .state}'

# Logs
echo "🔍 Logs recientes de RabbitMQ:"
docker logs $(docker ps -qf "name=rabbitmq") --tail 50

echo "✅ Diagnóstico de RabbitMQ completado"
```

### Scripts de Recuperación

#### Recuperación de Servicios Caídos
```bash
#!/bin/bash
# recover-failed-services.sh

echo "🔧 Iniciando recuperación de servicios..."

# Detectar servicios caídos
FAILED_SERVICES=()

# Verificar LP1
if ! curl -f -s https://lp1.shibasito.com/api/v1/health > /dev/null; then
    echo "❌ LP1 detectado como caído"
    FAILED_SERVICES+=("lp1-banco")
fi

# Verificar LP2
if ! curl -f -s https://lp2.shibasito.com/api/v1/health > /dev/null; then
    echo "❌ LP2 detectado como caído"
    FAILED_SERVICES+=("lp2-reniec")
fi

if [ ${#FAILED_SERVICES[@]} -eq 0 ]; then
    echo "✅ Todos los servicios están funcionando"
    exit 0
fi

echo "🔧 Recuperando servicios: ${FAILED_SERVICES[@]}"

# Reiniciar contenedores
for service in "${FAILED_SERVICES[@]}"; do
    echo "🔄 Reiniciando ${service}..."
    docker-compose -f docker-compose.prod.yml restart ${service}
    
    # Esperar inicialización
    sleep 30
    
    # Verificar que el servicio responde
    retries=0
    max_retries=10
    while [ ${retries} -lt ${max_retries} ]; do
        if curl -f -s https://${service}.shibasito.com/api/v1/health > /dev/null; then
            echo "✅ ${service} recuperado exitosamente"
            break
        fi
        echo "⏳ Esperando ${service}... (intento $((retries + 1))/${max_retries})"
        sleep 10
        retries=$((retries + 1))
    done
    
    if [ ${retries} -eq ${max_retries} ]; then
        echo "❌ No se pudo recuperar ${service}"
        exit 1
    fi
done

echo "✅ Recuperación completada"
```

#### Limpieza de Recursos
```bash
#!/bin/bash
# cleanup-resources.sh

echo "🧹 Limpiando recursos del sistema..."

# Limpiar imágenes no utilizadas
echo "🧹 Limpiando imágenes Docker no utilizadas..."
docker image prune -f

# Limpiar volúmenes huérfanos
echo "🧹 Limpiando volúmenes huérfanos..."
docker volume prune -f

# Limpiar redes no utilizadas
echo "🧹 Limpiando redes no utilizadas..."
docker network prune -f

# Rotar logs antiguos
echo "🧹 Rotando logs..."
find /var/log/shibasito -name "*.log" -mtime +7 -delete
find /opt/shibasito/logs -name "*.log" -mtime +7 -delete

# Limpiar backups antiguos (mantener últimos 30 días)
echo "🧹 Limpiando backups antiguos..."
find /opt/shibasito/backups -type d -mtime +30 -exec rm -rf {} +

# Limpiar métricas antiguas
echo "🧹 Limpiando métricas antiguas..."
find /opt/shibasito/metrics -name "*.json" -mtime +30 -delete

# Limpiar cache de Redis
echo "🧹 Limpiando cache de Redis..."
docker exec $(docker ps -qf "name=redis") redis-cli FLUSHDB

echo "✅ Limpieza de recursos completada"
```

### Contactos de Soporte

#### Lista de Contactos de Emergencia
```bash
# Contactos de emergencia
INFRASTRUCTURE_TEAM="infraestructura@shibasito.com"
DEVELOPMENT_TEAM="desarrollo@shibasito.com"
ONCALL_ENGINEER="+51-999-888-777"
MANAGER_EMAIL="gerencia@shibasito.com"

# SLAs de respuesta
CRITICAL_SLA="15 minutos"
HIGH_SLA="1 hora"
MEDIUM_SLA="4 horas"
LOW_SLA="24 horas"
```

#### Escalamiento de Problemas
```bash
#!/bin/bash
# escalate-issue.sh

SEVERITY=${1:-"medium"}
ISSUE_DESCRIPTION=${2:-"Problema detectado automáticamente"}

echo "📢 Escalando problema..."

case ${SEVERITY} in
    "critical")
        echo "🚨 Problema crítico detectado"
        # Enviar SMS, email y notificación Slack
        ./send-notification.sh "critical" "${ISSUE_DESCRIPTION}" "${ONCALL_ENGINEER}"
        ;;
    "high")
        echo "⚠️ Problema de alta prioridad detectado"
        # Enviar email y notificación Slack
        ./send-notification.sh "high" "${ISSUE_DESCRIPTION}" "${INFRASTRUCTURE_TEAM}"
        ;;
    "medium")
        echo "⚠️ Problema de prioridad media detectado"
        # Enviar email
        ./send-notification.sh "medium" "${ISSUE_DESCRIPTION}" "${DEVELOPMENT_TEAM}"
        ;;
    "low")
        echo "ℹ️ Problema de baja prioridad detectado"
        # Solo log
        echo "$(date): ${ISSUE_DESCRIPTION}" >> /var/log/shibasito/escalations.log
        ;;
esac
```

---

## Checklist de Despliegue

### Pre-Despliegue
- [ ] Backup de bases de datos creado
- [ ] Backup de configuraciones guardado
- [ ] Imágenes Docker construidas y verificadas
- [ ] Variables de entorno configuradas
- [ ] Certificados SSL válidos
- [ ] Puertos disponibles verificados
- [ ] Espacio en disco suficiente (>20% libre)
- [ ] Alertas configuradas y probadas
- [ ] Equipo notificado del despliegue programado

### Durante el Despliegue
- [ ] Servicios desplegados sin errores
- [ ] Health checks pasando
- [ ] Migraciones de BD ejecutadas exitosamente
- [ ] Conectividad entre servicios verificada
- [ ] Logs monitoreados para errores
- [ ] Métricas de performance dentro de rangos normales

### Post-Despliegue
- [ ] Funcionalidad básica probada
- [ ] Tests de integración ejecutados
- [ ] Monitoreo activo y alertas configuradas
- [ ] Métricas de performance recolectadas
- [ ] Documentación actualizada
- [ ] Equipo notificado del éxito del despliegue
- [ ] Rollback plan documentado y disponible

### Rollback (si es necesario)
- [ ] Problema identificado y documentado
- [ ] Decisión de rollback comunicada al equipo
- [ ] Tráfico desviado a versión anterior
- [ ] Servicios problemáticos detenidos
- [ ] Sistema verificado funcionando correctamente
- [ ] Post-mortem programado para análisis

---

*Documento actualizado: $(date +%Y-%m-%d)*  
*Versión: 1.0*  
*Autor: Equipo de Infraestructura Shibasito*