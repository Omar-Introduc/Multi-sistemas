# Manual de Instalación - Sistema Shibasito

## 📋 Índice

1. [Requisitos del Sistema](#requisitos-del-sistema)
2. [Preparación del Entorno](#preparación-del-entorno)
3. [Instalación Automática](#instalación-automática)
4. [Instalación Manual](#instalación-manual)
5. [Configuración Post-Instalación](#configuración-post-instalación)
6. [Verificación del Sistema](#verificación-del-sistema)
7. [Configuración de Producción](#configuración-de-producción)
8. [Solución de Problemas](#solución-de-problemas)

---

## Requisitos del Sistema

### Requisitos Mínimos

#### Hardware
| Componente | Mínimo | Recomendado | Producción |
|------------|--------|-------------|------------|
| **CPU** | 2 cores | 4 cores | 8+ cores |
| **RAM** | 4 GB | 8 GB | 16+ GB |
| **Almacenamiento** | 20 GB SSD | 50 GB SSD | 100+ GB SSD |
| **Red** | 100 Mbps | 1 Gbps | 1+ Gbps |

#### Sistemas Operativos Soportados
- **Ubuntu** 20.04 LTS / 22.04 LTS
- **CentOS** 7 / 8 / 9
- **Debian** 10 / 11
- **Red Hat Enterprise Linux** 7 / 8 / 9

### Software Requerido

#### Dependencias Base
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y curl wget git unzip htop vim

# CentOS/RHEL
sudo yum update -y
sudo yum install -y curl wget git unzip htop vim

# Verificar versiones
docker --version      # >= 20.10.0
docker-compose --version  # >= 2.0.0
git --version         # >= 2.20.0
```

### Requisitos de Red

#### Puertos Requeridos
| Puerto | Servicio | Protocolo | Descripción |
|--------|----------|-----------|-------------|
| **80** | HTTP | TCP | API Gateway (opcional) |
| **443** | HTTPS | TCP | API Gateway SSL (producción) |
| **8000** | LP2-RENIEC | TCP | Servicio RENIEC |
| **8080** | LP1-Banco | TCP | Servicio Banco |
| **3000** | Grafana | TCP | Dashboard de monitoreo |
| **5432** | PostgreSQL | TCP | Base de datos Banco |
| **3306** | MySQL | TCP | Base de datos RENIEC |
| **5672** | RabbitMQ | TCP | Message broker |
| **6379** | Redis | TCP | Cache distribuido |
| **9090** | Prometheus | TCP | Métricas del sistema |
| **15672** | RabbitMQ UI | TCP | Interface web RabbitMQ |

#### Reglas de Firewall

##### Ubuntu/Debian (ufw)
```bash
# Permitir puertos básicos
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Permitir puertos de aplicación
sudo ufw allow 8000/tcp
sudo ufw allow 8080/tcp
sudo ufw allow 3000/tcp
sudo ufw allow 9090/tcp

# Permitir puertos de servicios
sudo ufw allow 5432/tcp
sudo ufw allow 3306/tcp
sudo ufw allow 5672/tcp
sudo ufw allow 6379/tcp
sudo ufw allow 15672/tcp

# Habilitar firewall
sudo ufw enable
```

##### CentOS/RHEL (firewalld)
```bash
# Habilitar firewalld
sudo systemctl enable firewalld
sudo systemctl start firewalld

# Agregar servicios
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https

# Agregar puertos
for port in 8000 8080 3000 9090 5432 3306 5672 6379 15672; do
    sudo firewall-cmd --permanent --add-port=$port/tcp
done

# Recargar configuración
sudo firewall-cmd --reload
```

---

## Preparación del Entorno

### 1. Actualización del Sistema

#### Ubuntu/Debian
```bash
# Actualizar paquetes del sistema
sudo apt update && sudo apt upgrade -y

# Instalar herramientas esenciales
sudo apt install -y curl wget git unzip htop vim nano net-tools

# Verificar versiones
docker --version
docker-compose --version
```

#### CentOS/RHEL
```bash
# Actualizar sistema
sudo yum update -y

# Instalar EPEL
sudo yum install -y epel-release

# Instalar herramientas esenciales
sudo yum install -y curl wget git unzip htop vim net-tools

# Habilitar repositorios
sudo yum config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
```

### 2. Instalación de Docker

#### Método 1: Instalación Automática
```bash
# Descargar e instalar Docker automáticamente
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Agregar usuario al grupo docker
sudo usermod -aG docker $USER

# Reiniciar sesión o ejecutar:
newgrp docker

# Verificar instalación
docker --version
docker run hello-world
```

#### Método 2: Instalación Manual Ubuntu
```bash
# Remover versiones antiguas
sudo apt remove -y docker docker-engine docker.io containerd runc

# Instalar dependencias
sudo apt install -y apt-transport-https ca-certificates curl gnupg lsb-release

# Agregar clave GPG oficial de Docker
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Agregar repositorio
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Instalar Docker Engine
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Habilitar servicio
sudo systemctl enable docker
sudo systemctl start docker
```

#### Método 3: Instalación Manual CentOS
```bash
# Instalar yum-utils
sudo yum install -y yum-utils

# Agregar repositorio Docker
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo

# Instalar Docker
sudo yum install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Habilitar servicio
sudo systemctl enable docker
sudo systemctl start docker
```

### 3. Instalación de Docker Compose

#### Opción A: Usar Docker Compose Plugin (Recomendado)
```bash
# Verificar que está disponible
docker compose version

# Si no está disponible, instalarlo
sudo apt install -y docker-compose-plugin
```

#### Opción B: Instalación Binaria
```bash
# Descargar binario
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# Hacer ejecutable
sudo chmod +x /usr/local/bin/docker-compose

# Crear enlace simbólico
sudo ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose

# Verificar instalación
docker-compose --version
```

### 4. Configuración de Docker

#### Configuración de daemon
```bash
# Crear directorio de configuración
sudo mkdir -p /etc/docker

# Crear archivo de configuración
sudo tee /etc/docker/daemon.json << 'EOF'
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  },
  "storage-driver": "overlay2",
  "userland-proxy": false,
  "live-restore": true,
  "default-ulimits": {
    "nofile": {
      "Name": "nofile",
      "Hard": 64000,
      "Soft": 64000
    }
  }
}
EOF

# Reiniciar servicio
sudo systemctl restart docker
```

#### Configuración de límites de recursos
```bash
# Crear archivo de límites
sudo tee /etc/security/limits.d/docker.conf << 'EOF'
* soft nofile 65536
* hard nofile 65536
* soft nproc 65536
* hard nproc 65536
EOF

# Aplicar cambios
sudo sysctl -p
```

---

## Instalación Automática

### 1. Descarga del Sistema

```bash
# Clonar repositorio (o copiar archivos)
git clone <repository-url> shibasito-sistema-distribuido
cd shibasito-sistema-distribuido/

# Verificar estructura
ls -la
```

### 2. Script de Instalación Automática

El sistema incluye un script automatizado que configura todo automáticamente:

```bash
# Hacer ejecutable el script
chmod +x scripts/install.sh

# Ejecutar instalación completa
./scripts/install.sh
```

#### Qué hace el script automático:
1. ✅ Verifica prerrequisitos del sistema
2. ✅ Instala dependencias (Docker, Docker Compose)
3. ✅ Configura variables de entorno
4. ✅ Crea redes Docker
5. ✅ Inicializa bases de datos
6. ✅ Configura RabbitMQ
7. ✅ Inicia servicios principales
8. ✅ Ejecuta health checks
9. ✅ Genera reporte de instalación

### 3. Verificación de la Instalación Automática

```bash
# Verificar estado de todos los servicios
./scripts/health-check.sh

# Ver logs del sistema
./scripts/health-check.sh --detailed

# Generar reporte completo
./scripts/generate-health-report.sh
```

### 4. Salida del Script de Instalación

```
==============================================
  INSTALACIÓN SISTEMA SHIBASITO v1.0
==============================================

[INFO] Verificando prerrequisitos...
[OK] Docker 20.10.0 instalado
[OK] Docker Compose 2.20.0 instalado
[OK] Sistema operativo: Ubuntu 22.04
[OK] RAM disponible: 8.0 GB
[OK] Espacio en disco: 45.2 GB

[INFO] Configurando variables de entorno...
[OK] Archivo .env creado
[OK] Configuración de redes

[INFO] Inicializando bases de datos...
[OK] PostgreSQL configurado
[OK] MySQL configurado
[OK] Datos iniciales cargados

[INFO] Configurando servicios de infraestructura...
[OK] RabbitMQ configurado
[OK] Redis configurado
[OK] Prometheus configurado
[OK] Grafana configurado

[INFO] Iniciando servicios de aplicación...
[OK] Servicio LP1-Banco iniciado
[OK] Servicio LP2-RENIEC iniciado
[OK] Aplicaciones cliente iniciadas

[INFO] Ejecutando verificaciones...
[OK] Health checks completados
[OK] Conectividad de red verificada
[OK] Base de datos accessible
[OK] Message queue operational

==============================================
  INSTALACIÓN COMPLETADA EXITOSAMENTE
==============================================

🌐 Interfaces disponibles:
• Grafana Dashboard: http://localhost:3000
• Prometheus Metrics: http://localhost:9090
• RabbitMQ Management: http://localhost:15672
• API Banco LP1: http://localhost:8080
• API RENIEC LP2: http://localhost:8000

📊 Estado del sistema:
• Servicios activos: 9/9
• Bases de datos: 2/2
• Conexiones de red: 3/3
• Health checks: 100%

🚀 Próximos pasos:
1. Acceder a Grafana: http://localhost:3000
2. Verificar endpoints de API
3. Revisar logs del sistema
4. Configurar alertas (opcional)
```

---

## Instalación Manual

Si prefieres instalar paso a paso, sigue esta guía:

### 1. Preparación de Directorios

```bash
# Crear estructura de directorios
mkdir -p shibasito-sistema-distribuido/{config,data,logs,scripts}
cd shibasito-sistema-distribuido/

# Crear volúmenes persistentes
docker volume create postgres_bd1_data
docker volume create mysql_bd2_data
docker volume create rabbitmq_data
docker volume create redis_data
docker volume create prometheus_data
docker volume create grafana_data
```

### 2. Configuración de Variables de Entorno

```bash
# Crear archivo de configuración
cat > .env << 'EOF'
# ================================
# CONFIGURACIÓN SISTEMA SHIBASITO
# ================================

# Servicios
LP1_HOST=servicio-banco-lp1
LP2_HOST=servicio-reniec-lp2
LP1_PORT=8080
LP2_PORT=8000

# Bases de Datos
POSTGRES_DB=banco_db
POSTGRES_USER=banco_user
POSTGRES_PASSWORD=banco_password_secure_2024
POSTGRES_HOST=bd1_postgresql
POSTGRES_PORT=5432

MYSQL_DB=reniec_db
MYSQL_USER=reniec_user
MYSQL_PASSWORD=reniec_password_secure_2024
MYSQL_HOST=bd2_mysql
MYSQL_PORT=3306

# RabbitMQ
RABBITMQ_HOST=rabbitmq
RABBITMQ_PORT=5672
RABBITMQ_USER=admin
RABBITMQ_PASSWORD=admin123_secure_2024
RABBITMQ_MANAGEMENT_PORT=15672

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=redis_password_2024

# Monitoreo
PROMETHEUS_PORT=9090
GRAFANA_PORT=3000
GRAFANA_USER=admin
GRAFANA_PASSWORD=admin123_secure_2024

# Redes
SHIBASITO_NETWORK=172.20.0.0/16
DATABASE_NETWORK=172.21.0.0/16
MONITORING_NETWORK=172.22.0.0/16

# Configuraciones
DEBUG=false
LOG_LEVEL=INFO
MAX_CONNECTIONS=100
POOL_SIZE=10

# Timeouts (segundos)
DB_TIMEOUT=30
RABBIT_TIMEOUT=30
REDIS_TIMEOUT=10

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=3600

# Backup
BACKUP_RETENTION_DAYS=30
BACKUP_SCHEDULE=0 2 * * *
EOF
```

### 3. Configuración de Docker Compose

```yaml
# docker-compose.main.yml
version: '3.8'

services:
  # ================================
  # SERVICIOS DE APLICACIÓN
  # ================================
  
  servicio-banco-lp1:
    build:
      context: ./lp1-servicio-banco
      dockerfile: Dockerfile
    container_name: servicio-banco-lp1
    ports:
      - "8080:8080"
    environment:
      - SPRING_PROFILES_ACTIVE=prod
      - DATABASE_URL=jdbc:postgresql://bd1_postgresql:5432/banco_db
      - DATABASE_USERNAME=${POSTGRES_USER}
      - DATABASE_PASSWORD=${POSTGRES_PASSWORD}
      - RABBITMQ_HOST=rabbitmq
      - RABBITMQ_USERNAME=${RABBITMQ_USER}
      - RABBITMQ_PASSWORD=${RABBITMQ_PASSWORD}
      - REDIS_HOST=redis
      - REDIS_PASSWORD=${REDIS_PASSWORD}
    volumes:
      - ./logs/banco:/app/logs
    networks:
      - shibasito-network
      - database-network
    depends_on:
      - bd1_postgresql
      - rabbitmq
      - redis
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s

  servicio-reniec-lp2:
    build:
      context: ./lp2_reniec_service
      dockerfile: Dockerfile
    container_name: servicio-reniec-lp2
    ports:
      - "8000:8000"
    environment:
      - DATABASE_HOST=${MYSQL_HOST}
      - DATABASE_NAME=${MYSQL_DB}
      - DATABASE_USER=${MYSQL_USER}
      - DATABASE_PASSWORD=${MYSQL_PASSWORD}
      - RABBITMQ_HOST=${RABBITMQ_HOST}
      - RABBITMQ_USERNAME=${RABBITMQ_USER}
      - RABBITMQ_PASSWORD=${RABBITMQ_PASSWORD}
      - REDIS_HOST=${REDIS_HOST}
      - REDIS_PASSWORD=${REDIS_PASSWORD}
      - LOG_LEVEL=${LOG_LEVEL}
    volumes:
      - ./logs/reniec:/app/logs
    networks:
      - shibasito-network
      - database-network
    depends_on:
      - bd2_mysql
      - rabbitmq
      - redis
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s

  # ================================
  # BASES DE DATOS
  # ================================
  
  bd1_postgresql:
    image: postgres:14-alpine
    container_name: bd1_postgresql
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_DB=${POSTGRES_DB}
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    volumes:
      - postgres_bd1_data:/var/lib/postgresql/data
      - ./init-scripts/schema_lp1_banco.sql:/docker-entrypoint-initdb.d/schema.sql
      - ./init-scripts/seed_data_lp1.sql:/docker-entrypoint-initdb.d/seed.sql
      - ./logs/postgres:/var/log/postgresql
    networks:
      - database-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}"]
      interval: 30s
      timeout: 10s
      retries: 3

  bd2_mysql:
    image: mysql:8.0
    container_name: bd2_mysql
    ports:
      - "3306:3306"
    environment:
      - MYSQL_ROOT_PASSWORD=root_password_secure_2024
      - MYSQL_DATABASE=${MYSQL_DB}
      - MYSQL_USER=${MYSQL_USER}
      - MYSQL_PASSWORD=${MYSQL_PASSWORD}
    volumes:
      - mysql_bd2_data:/var/lib/mysql
      - ./init-scripts/schema_lp2_reniec.sql:/docker-entrypoint-initdb.d/schema.sql
      - ./init-scripts/seed_data_lp2.sql:/docker-entrypoint-initdb.d/seed.sql
      - ./logs/mysql:/var/log/mysql
    networks:
      - database-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost", "-u", "${MYSQL_USER}", "-p${MYSQL_PASSWORD}"]
      interval: 30s
      timeout: 10s
      retries: 3

  # ================================
  # SERVICIOS DE INFRAESTRUCTURA
  # ================================
  
  rabbitmq:
    image: rabbitmq:3.11-management-alpine
    container_name: rabbitmq
    ports:
      - "5672:5672"
      - "15672:15672"
    environment:
      - RABBITMQ_DEFAULT_USER=${RABBITMQ_USER}
      - RABBITMQ_DEFAULT_PASS=${RABBITMQ_PASSWORD}
      - RABBITMQ_SERVER_ADDITIONAL_ERL_ARGS=-rabbit disk_free_limit 1GB
    volumes:
      - rabbitmq_data:/var/lib/rabbitmq
      - ./rabbitmq-config/:/etc/rabbitmq/
      - ./logs/rabbitmq:/var/log/rabbitmq
    networks:
      - shibasito-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "rabbitmq-diagnostics", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3

  redis:
    image: redis:7-alpine
    container_name: redis
    ports:
      - "6379:6379"
    command: redis-server --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data
      - ./redis-config/redis.conf:/etc/redis/redis.conf
      - ./logs/redis:/var/log/redis
    networks:
      - shibasito-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "--raw", "incr", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3

  # ================================
  # SERVICIOS DE MONITOREO
  # ================================
  
  prometheus:
    image: prom/prometheus:latest
    container_name: prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./config/prometheus/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
      - ./logs/prometheus:/var/log/prometheus
    networks:
      - monitoring-network
    restart: unless-stopped
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--storage.tsdb.retention.time=30d'
      - '--web.enable-lifecycle'

  grafana:
    image: grafana/grafana:latest
    container_name: grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
      - GF_SECURITY_ADMIN_USER=${GRAFANA_USER}
      - GF_USERS_ALLOW_SIGN_UP=false
    volumes:
      - grafana_data:/var/lib/grafana
      - ./config/grafana/datasources.yml:/etc/grafana/provisioning/datasources/datasources.yml
      - ./config/grafana/dashboards.yml:/etc/grafana/provisioning/dashboards/dashboards.yml
      - ./config/grafana/dashboards:/var/lib/grafana/dashboards
      - ./logs/grafana:/var/log/grafana
    networks:
      - monitoring-network
    restart: unless-stopped
    depends_on:
      - prometheus

# ================================
# VOLÚMENES
# ================================
volumes:
  postgres_bd1_data:
    driver: local
  mysql_bd2_data:
    driver: local
  rabbitmq_data:
    driver: local
  redis_data:
    driver: local
  prometheus_data:
    driver: local
  grafana_data:
    driver: local

# ================================
# REDES
# ================================
networks:
  shibasito-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
  database-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.21.0.0/16
  monitoring-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.22.0.0/16
```

### 4. Inicialización de Bases de Datos

```bash
# Ejecutar scripts de inicialización
./init-scripts/init-all-databases.sh

# O manualmente:
docker-compose exec bd1_postgresql psql -U banco_user -d banco_db -f /docker-entrypoint-initdb.d/schema.sql
docker-compose exec bd1_postgresql psql -U banco_user -d banco_db -f /docker-entrypoint-initdb.d/seed.sql

docker-compose exec bd2_mysql mysql -u reniec_user -p reniec_db < /docker-entrypoint-initdb.d/schema.sql
docker-compose exec bd2_mysql mysql -u reniec_user -p reniec_db < /docker-entrypoint-initdb.d/seed.sql
```

### 5. Inicio de Servicios

```bash
# Construir imágenes
docker-compose -f docker-compose.main.yml build

# Iniciar servicios en segundo plano
docker-compose -f docker-compose.main.yml up -d

# Ver logs en tiempo real
docker-compose -f docker-compose.main.yml logs -f

# Verificar estado
docker-compose -f docker-compose.main.yml ps
```

---

## Configuración Post-Instalación

### 1. Configuración de Grafana

```bash
# Acceder a Grafana
# URL: http://localhost:3000
# Usuario: admin
# Contraseña: admin123_secure_2024

# Importar dashboards predefinidos
# O crear manualmente:

# Dashboard 1: System Overview
# Dashboard 2: Application Metrics  
# Dashboard 3: Database Performance
# Dashboard 4: Message Queue
# Dashboard 5: Cache Performance
```

### 2. Configuración de RabbitMQ

```bash
# Acceder a RabbitMQ Management
# URL: http://localhost:15672
# Usuario: admin
# Contraseña: admin123_secure_2024

# Verificar exchanges
# - validacion_exchange (topic)
# - error_exchange (fanout)
# - audit_exchange (topic)

# Verificar queues
# - validacion_respuestas
# - banco_respuestas
# - errores_sistema
```

### 3. Configuración de Prometheus

```bash
# Acceder a Prometheus
# URL: http://localhost:9090

# Verificar targets
# - servicio-banco-lp1:8080/metrics
# - servicio-reniec-lp2:8000/metrics
# - rabbitmq:15692/metrics
# - redis:9121/metrics
```

### 4. Configuración de Variables de Entorno de Aplicaciones

```bash
# Para aplicación desktop
cat > aplicaciones-cliente-lp3/desktop-app/.env << 'EOF'
API_BASE_URL=http://localhost:8080/api/v1/banco
RENIEC_BASE_URL=http://localhost:8000/api/v1/reniec
DEBUG=false
LOG_LEVEL=INFO
EOF

# Para aplicación mobile
cat > aplicaciones-cliente-lp3/mobile-app/.env << 'EOF'
API_BASE_URL=http://localhost:8080/api/v1/banco
RENIEC_BASE_URL=http://localhost:8000/api/v1/reniec
ENVIRONMENT=development
EOF
```

---

## Verificación del Sistema

### 1. Health Check Completo

```bash
# Ejecutar verificación completa
./scripts/health-check.sh

# Verificación detallada
./scripts/health-check.sh --detailed

# Generar reporte HTML
./scripts/generate-health-report.sh
```

### 2. Verificación de Servicios

```bash
# Verificar estado de contenedores
docker-compose -f docker-compose.main.yml ps

# Verificar logs de servicios
docker-compose -f docker-compose.main.yml logs servicio-banco-lp1
docker-compose -f docker-compose.main.yml logs servicio-reniec-lp2

# Verificar conectividad de red
docker network inspect shibasito-sistema-distribuido_shibasito-network
```

### 3. Verificación de Bases de Datos

```bash
# PostgreSQL
docker-compose exec bd1_postgresql psql -U banco_user -d banco_db -c "SELECT version();"

# MySQL
docker-compose exec bd2_mysql mysql -u reniec_user -p reniec_db -e "SELECT version();"
```

### 4. Verificación de APIs

```bash
# Health check LP1
curl -f http://localhost:8080/health
curl -f http://localhost:8080/api/v1/banco/health/detailed

# Health check LP2
curl -f http://localhost:8000/health
curl -f http://localhost:8000/api/v1/reniec/health/detailed

# Test de integración
curl -X POST http://localhost:8080/api/v1/banco/health/test-endpoint
```

### 5. Verificación de Conectividad

```bash
# Desde contenedor LP1
docker-compose exec servicio-banco-lp1 curl -f http://servicio-reniec-lp2:8000/health

# Desde contenedor LP2
docker-compose exec servicio-reniec-lp2 psql -h bd1_postgresql -U banco_user -d banco_db -c "SELECT 1;"

# Test de RabbitMQ
docker-compose exec rabbitmq rabbitmqctl status
```

### 6. Resultado de Verificación Exitosa

```
==============================================
  VERIFICACIÓN DEL SISTEMA - REPORTE
==============================================

🟢 SERVICIOS ACTIVOS (9/9)
├── servicio-banco-lp1           UP  100% health
├── servicio-reniec-lp2          UP  100% health
├── bd1_postgresql              UP  database ready
├── bd2_mysql                   UP  database ready
├── rabbitmq                    UP  message broker ready
├── redis                       UP  cache ready
├── prometheus                  UP  metrics ready
├── grafana                     UP  dashboard ready
└── Aplicaciones cliente        UP  frontend ready

🟢 BASES DE DATOS
├── PostgreSQL (Banco)          CONN: 3/100  STATUS: OK
├── MySQL (RENIEC)              CONN: 2/100  STATUS: OK
└── Esquemas                    VERIFIED

🟢 CONECTIVIDAD DE RED
├── shibasito-network           ACTIVE  172.20.0.0/16
├── database-network            ACTIVE  172.21.0.0/16
└── monitoring-network          ACTIVE  172.22.0.0/16

🟢 INTEGRACIÓN DE SERVICIOS
├── LP1 ↔ LP2                   OK  Response: 145ms
├── LP1 ↔ PostgreSQL            OK  Connection pool: 5/10
├── LP2 ↔ MySQL                 OK  Connection pool: 3/10
├── Services ↔ RabbitMQ         OK  Exchanges: 3, Queues: 5
└── Services ↔ Redis            OK  Cache hit rate: 98.2%

🟢 MONITOREO Y MÉTRICAS
├── Prometheus                  UP  Targets: 5/5
├── Grafana                     UP  Dashboards: 8
├── Metrics collection          OK  24h data retention
└── Alerting                    CONFIGURED

🟢 SEGURIDAD
├── Authentication              ENABLED  JWT tokens
├── Database credentials        SECURE  Strong passwords
├── Network isolation           CONFIGURED  3 networks
└── Rate limiting               ENABLED  100 req/hour

📊 PERFORMANCE
├── Response time LP1           245ms   (target: <500ms) ✅
├── Response time LP2           145ms   (target: <500ms) ✅
├── Database connections        5 active (target: <80%) ✅
├── Memory usage                45%     (target: <80%) ✅
└── Disk usage                  32%     (target: <80%) ✅

==============================================
  SISTEMA OPERATIVO Y LISTO PARA PRODUCCIÓN
==============================================

🌐 URLs de acceso:
• Grafana Dashboard: http://localhost:3000
• Prometheus Metrics: http://localhost:9090
• RabbitMQ Management: http://localhost:15672
• API Banco LP1: http://localhost:8080
• API RENIEC LP2: http://localhost:8000

🔧 Próximos pasos:
1. Configurar usuarios de Grafana
2. Personalizar dashboards
3. Configurar alertas
4. Programar backups
5. Configurar SSL/TLS para producción
```

---

## Configuración de Producción

### 1. Seguridad de Producción

#### SSL/TLS Configuration

```bash
# Generar certificados SSL
mkdir -p config/ssl
openssl req -x509 -newkey rsa:4096 -keyout config/ssl/key.pem -out config/ssl/cert.pem -days 365 -nodes

# Configurar nginx como reverse proxy
cat > config/nginx.conf << 'EOF'
server {
    listen 443 ssl;
    server_name shibasito.bank.com;

    ssl_certificate /etc/ssl/cert.pem;
    ssl_certificate_key /etc/ssl/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    location /api/v1/banco/ {
        proxy_pass http://servicio-banco-lp1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api/v1/reniec/ {
        proxy_pass http://servicio-reniec-lp2:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
EOF
```

#### Configuración de Secretos

```bash
# Crear archivo de secretos
cat > .env.production << 'EOF'
# Cambiar todas las contraseñas por defecto
POSTGRES_PASSWORD=postgres_secure_prod_2024_!
MYSQL_PASSWORD=mysql_secure_prod_2024_!
RABBITMQ_PASSWORD=rabbitmq_secure_prod_2024_!
REDIS_PASSWORD=redis_secure_prod_2024_!
GRAFANA_PASSWORD=grafana_secure_prod_2024_!

# Configurar JWT secrets
JWT_SECRET_KEY=jwt_secret_key_very_secure_production_2024
JWT_ALGORITHM=HS256
JWT_EXPIRATION_TIME=3600

# Configurar API keys
ENCRYPTION_KEY=encryption_key_very_secure_32_chars
HASH_SALT=hash_salt_secure_production_2024
EOF

# Permisos seguros para archivos sensibles
chmod 600 .env.production
chown root:root .env.production
```

### 2. Optimización de Performance

#### Configuración de Bases de Datos

```sql
-- PostgreSQL optimizations
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET default_statistics_target = 100;
ALTER SYSTEM SET random_page_cost = 1.1;
ALTER SYSTEM SET effective_io_concurrency = 200;

-- MySQL optimizations
SET GLOBAL innodb_buffer_pool_size = 512 * 1024 * 1024;
SET GLOBAL innodb_log_file_size = 256 * 1024 * 1024;
SET GLOBAL innodb_flush_log_at_trx_commit = 2;
SET GLOBAL innodb_flush_method = 'O_DIRECT';
SET GLOBAL innodb_file_per_table = 1;
```

#### Redis Configuration

```bash
# Configurar redis.conf para producción
cat >> redis-config/redis.conf << 'EOF'
maxmemory 512mb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
stop-writes-on-bgsave-error yes
rdbcompression yes
rdbchecksum yes
tcp-keepalive 300
timeout 0
tcp-backlog 511
EOF
```

### 3. Backup y Recuperación

#### Configuración de Backup Automático

```bash
# Script de backup completo
cat > scripts/backup-system.sh << 'EOF'
#!/bin/bash

BACKUP_DIR="/backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p $BACKUP_DIR

echo "Iniciando backup del sistema Shibasito..."

# Backup PostgreSQL
docker-compose exec -T bd1_postgresql pg_dump -U banco_user banco_db > $BACKUP_DIR/postgres_banco.sql

# Backup MySQL
docker-compose exec -T bd2_mysql mysqldump -u reniec_user -p$MYSQL_PASSWORD reniec_db > $BACKUP_DIR/mysql_reniec.sql

# Backup configuraciones
cp -r ./config $BACKUP_DIR/
cp .env.production $BACKUP_DIR/

# Backup volúmenes
docker run --rm -v postgres_bd1_data:/data -v $BACKUP_DIR:/backup alpine tar czf /backup/postgres_volume.tar.gz -C /data .
docker run --rm -v mysql_bd2_data:/data -v $BACKUP_DIR:/backup alpine tar czf /backup/mysql_volume.tar.gz -C /data .

# Comprimir backup
tar czf $BACKUP_DIR.tar.gz $BACKUP_DIR
rm -rf $BACKUP_DIR

echo "Backup completado: $BACKUP_DIR.tar.gz"
EOF

chmod +x scripts/backup-system.sh

# Programar backup diario
(crontab -l 2>/dev/null; echo "0 2 * * * /path/to/scripts/backup-system.sh >> /var/log/backup.log 2>&1") | crontab -
```

### 4. Monitoreo y Alertas

#### Configuración de Alertas

```yaml
# config/prometheus/alerts.yml
groups:
- name: shibasito-alerts
  rules:
  - alert: ServiceDown
    expr: up == 0
    for: 1m
    labels:
      severity: critical
    annotations:
      summary: "Service {{ $labels.instance }} is down"

  - alert: HighResponseTime
    expr: http_request_duration_seconds{quantile="0.95"} > 2
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High response time for {{ $labels.endpoint }}"

  - alert: DatabaseConnectionsHigh
    expr: database_connections_active / database_connections_max > 0.8
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "Database {{ $labels.database }} high connection usage"
```

### 5. Configuración de Logs

```yaml
# docker-compose.prod.yml - configuración adicional
version: '3.8'
services:
  logging:
    driver: "json-file"
    options:
      max-size: "10m"
      max-file: "5"
  
  logrotate:
    image: alpine:latest
    volumes:
      - ./logs:/var/log/app
    command: |
      sh -c "
        apk add --no-cache logrotate &&
        logrotate -f /etc/logrotate.conf
      "
    restart: "unless-stopped"
```

---

## Solución de Problemas

### Problemas Comunes y Soluciones

#### 1. Servicios no inician

```bash
# Problema: Contenedores fallan al iniciar
# Diagnóstico:
docker-compose -f docker-compose.main.yml logs [servicio]
docker system events --filter 'type=container'

# Solución:
# 1. Verificar puertos disponibles
netstat -tulpn | grep :8080

# 2. Verificar recursos del sistema
docker system df
docker system prune

# 3. Reiniciar servicios problemáticos
docker-compose -f docker-compose.main.yml restart [servicio]

# 4. Verificar variables de entorno
docker-compose -f docker-compose.main.yml config
```

#### 2. Error de conexión a base de datos

```bash
# Problema: Error de conexión a PostgreSQL/MySQL
# Diagnóstico:
docker-compose exec bd1_postgresql psql -U banco_user -d banco_db -c "SELECT 1;"
docker-compose exec bd2_mysql mysql -u reniec_user -p reniec_db -e "SELECT 1;"

# Verificar logs
docker-compose logs bd1_postgresql
docker-compose logs bd2_mysql

# Solución:
# 1. Verificar que el contenedor esté ejecutándose
docker-compose ps bd1_postgresql bd2_mysql

# 2. Verificar variables de entorno
docker-compose exec servicio-banco-lp1 env | grep DATABASE

# 3. Reiniciar bases de datos
docker-compose restart bd1_postgresql bd2_mysql
```

#### 3. Error de RabbitMQ

```bash
# Problema: Message queue no disponible
# Diagnóstico:
docker-compose exec rabbitmq rabbitmqctl status
curl http://localhost:15672/api/overview

# Solución:
# 1. Verificar configuración
docker-compose exec rabbitmq rabbitmq-diagnostics environment

# 2. Verificar exchanges y queues
docker-compose exec rabbitmq rabbitmqctl list_exchanges
docker-compose exec rabbitmq rabbitmqctl list_queues

# 3. Reiniciar RabbitMQ
docker-compose restart rabbitmq
```

#### 4. Problemas de red entre contenedores

```bash
# Problema: Contenedores no pueden comunicarse
# Diagnóstico:
docker network inspect shibasito-sistema-distribuido_shibasito-network
docker-compose exec servicio-banco-lp1 ping servicio-reniec-lp2

# Solución:
# 1. Verificar configuración de red
docker-compose config | grep -A 10 networks

# 2. Recrear red
docker-compose down
docker network prune
docker-compose up -d

# 3. Verificar DNS interno
docker-compose exec servicio-banco-lp1 nslookup servicio-reniec-lp2
```

#### 5. Alto uso de memoria

```bash
# Problema: Sistema usando demasiada memoria
# Diagnóstico:
docker stats --no-stream
free -h
df -h

# Solución:
# 1. Verificar procesos que consumen memoria
docker-compose exec servicio-banco-lp1 ps aux --sort=-%mem

# 2. Ajustar límites de memoria en docker-compose.yml
# Agregar: mem_limit: 1g

# 3. Limpiar Docker
docker system prune -a
docker volume prune
```

#### 6. Errores de validación en APIs

```bash
# Problema: APIs retornando errores 400/500
# Diagnóstico:
curl -v http://localhost:8080/api/v1/banco/health
curl -v http://localhost:8000/api/v1/reniec/health

# Verificar logs detallados
docker-compose logs -f servicio-banco-lp1 | grep ERROR
docker-compose logs -f servicio-reniec-lp2 | grep ERROR

# Solución:
# 1. Verificar configuración de bases de datos
curl http://localhost:8080/api/v1/banco/health/detailed
curl http://localhost:8000/api/v1/reniec/health/detailed

# 2. Verificar conectividad con servicios externos
docker-compose exec servicio-banco-lp1 curl http://servicio-reniec-lp2:8000/health

# 3. Verificar variables de entorno
docker-compose exec servicio-banco-lp1 env | grep -E "(DATABASE|RABBITMQ|REDIS)"
```

### Logs de Diagnóstico

```bash
# Script de diagnóstico completo
cat > scripts/diagnose-system.sh << 'EOF'
#!/bin/bash

echo "=============================================="
echo "  DIAGNÓSTICO COMPLETO SISTEMA SHIBASITO"
echo "=============================================="

echo -e "\n📊 ESTADO DE SERVICIOS:"
docker-compose ps

echo -e "\n📊 RECURSOS DEL SISTEMA:"
docker system df
free -h
df -h

echo -e "\n🌐 ESTADO DE REDES:"
docker network ls
docker network inspect shibasito-sistema-distribuido_shibasito-network | grep -A 10 Containers

echo -e "\n🔌 CONECTIVIDAD ENTRE SERVICIOS:"
echo "LP1 → LP2:"
docker-compose exec -T servicio-banco-lp1 curl -f -s http://servicio-reniec-lp2:8000/health || echo "FAILED"
echo "LP1 → PostgreSQL:"
docker-compose exec -T servicio-banco-lp1 psql -h bd1_postgresql -U banco_user -d banco_db -c "SELECT 1;" || echo "FAILED"
echo "LP2 → MySQL:"
docker-compose exec -T servicio-reniec-lp2 mysql -h bd2_mysql -u reniec_user -p$MYSQL_PASSWORD -e "SELECT 1;" || echo "FAILED"

echo -e "\n💾 ESTADO DE BASES DE DATOS:"
docker-compose exec -T bd1_postgresql psql -U banco_user -d banco_db -c "SELECT version();" 2>/dev/null | head -1
docker-compose exec -T bd2_mysql mysql -u reniec_user -p$MYSQL_PASSWORD -e "SELECT version();" 2>/dev/null | head -1

echo -e "\n🔄 ESTADO DE RABBITMQ:"
docker-compose exec -T rabbitmq rabbitmqctl status | head -5

echo -e "\n⚡ ESTADO DE REDIS:"
docker-compose exec -T redis redis-cli ping

echo -e "\n📈 MÉTRICAS DE APLICACIÓN:"
curl -f -s http://localhost:8080/health | jq . 2>/dev/null || echo "LP1 health check failed"
curl -f -s http://localhost:8000/health | jq . 2>/dev/null || echo "LP2 health check failed"

echo -e "\n🚨 ERRORES RECIENTES (últimas 50 líneas):"
docker-compose logs --tail=50 2>/dev/null | grep -i error | tail -10

echo -e "\n=============================================="
EOF

chmod +x scripts/diagnose-system.sh
./scripts/diagnose-system.sh
```

---

## 📞 Soporte y Mantenimiento

### Contactos de Soporte

- **Documentación**: Revisar archivos en `/docs/`
- **Logs**: Verificar en `/logs/` para diagnósticos
- **Issues**: Crear issue en el repositorio

### Mantenimiento Regular

```bash
# Limpieza semanal de logs
./scripts/cleanup-logs.sh

# Verificación de backups
./scripts/verify-backups.sh

# Actualización de dependencias
./scripts/update-dependencies.sh

# Optimización de bases de datos
./scripts/optimize-databases.sh
```

---

**Manual generado**: 30 de Octubre de 2025  
**Versión**: 1.0  
**Última actualización**: 30 de Octubre de 2025
