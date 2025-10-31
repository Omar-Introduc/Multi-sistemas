# 🚀 Redis Configuration - Sistema Distribuido Shibasito

Configuración completa y optimizada para Redis en el sistema distribuido Shibasito, incluyendo configuraciones de performance, memoria, backup automático, clustering y monitoreo avanzado.

## 📋 Índice

- [Características](#-características)
- [Estructura de Archivos](#-estructura-de-archivos)
- [Instalación](#-instalación)
- [Configuración](#-configuración)
- [Uso](#-uso)
- [Monitoreo](#-monitoreo)
- [Cluster](#-cluster)
- [Backup](#-backup)
- [Performance](#-performance)
- [Troubleshooting](#-troubleshooting)
- [API y Referencias](#-api-y-referencias)

## 🌟 Características

### ✅ Configuración Completa
- **redis.conf**: Configuración principal optimizada para producción
- **redis-cluster.conf**: Configuración específica para clustering
- **setup-redis.sh**: Script automatizado de instalación y configuración
- **monitoring-redis.py**: Sistema completo de monitoreo y métricas

### 📊 Monitoreo Avanzado
- Dashboard web en tiempo real (`http://localhost:8080`)
- Métricas de memoria, CPU, conexiones y latencia
- Sistema de alertas por email
- Exportación compatible con Prometheus/Grafana
- Health checks automáticos

### 🔒 Seguridad
- Contraseñas configuradas por defecto
- Comandos peligrosos deshabilitados
- Renombrado de comandos sensibles
- Configuración de firewall automática

### 💾 Backup Automático
- Backup diario automático a las 2:00 AM
- Compresión automática de backups
- Retención configurable (30 días por defecto)
- Backup manual bajo demanda

### ⚡ Performance
- Optimización de memoria con políticas LRU
- Configuración de threads I/O
- Lazy freeing para operaciones pesadas
- Buffer de cliente configurable

### 🏗️ Clustering
- Configuración para Redis Cluster
- Soporte para failover automático
- Gestión de réplicas
- Balanceador de carga automático

## 📁 Estructura de Archivos

```
redis-config/
├── redis.conf                 # Configuración principal de Redis
├── redis-cluster.conf         # Configuración para cluster
├── setup-redis.sh            # Script de instalación automática
├── monitoring-redis.py       # Monitor completo con dashboard
├── docker-compose.redis.yml  # Configuración Docker Compose
└── README.md                 # Esta documentación
```

## 🚀 Instalación

### Opción 1: Instalación Automática (Recomendado)

```bash
# Clonar o navegar al directorio del proyecto
cd shibasito-sistema-distribuido/redis-config/

# Ejecutar setup automático (requiere permisos root)
sudo ./setup-redis.sh
```

### Opción 2: Instalación Manual

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install redis-server

# RHEL/CentOS
sudo yum install redis

# Configurar Redis
sudo cp redis.conf /etc/redis/
sudo systemctl enable redis
sudo systemctl start redis
```

### Opción 3: Docker Compose (Recomendado para desarrollo)

```bash
# Crear directorios necesarios
mkdir -p data/redis logs/redis backups/redis

# Iniciar Redis con monitoreo
docker-compose -f docker-compose.redis.yml up redis redis-monitor

# Solo Redis básico
docker-compose -f docker-compose.redis.yml up redis
```

## ⚙️ Configuración

### Configuración Principal (redis.conf)

```bash
# Configuración de red
bind 0.0.0.0
port 6379
protected-mode yes
requirepass redispass123_secure_2024

# Configuración de memoria
maxmemory 512mb
maxmemory-policy allkeys-lru

# Persistencia
appendonly yes
save 900 1
save 300 10
save 60 10000

# Seguridad
rename-command FLUSHDB ""
rename-command FLUSHALL ""
rename-command DEBUG ""
```

### Variables de Entorno

```bash
# Configuración de Redis
export REDIS_PASSWORD="redispass123_secure_2024"
export REDIS_MAXMEMORY="512mb"
export REDIS_MAXMEMORY_POLICY="allkeys-lru"

# Configuración de Monitoreo
export REDIS_MONITOR_EMAIL="admin@shibasito.com"
export REDIS_ALERT_MEMORY_PERCENT="85"
export REDIS_ALERT_LATENCY_MS="100"
```

## 🔧 Uso

### Comandos Básicos de Redis

```bash
# Conectar a Redis
redis-cli -h localhost -p 6379 -a redispass123_secure_2024

# Test de conectividad
redis-cli -h localhost -p 6379 -a redispass123_secure_2024 ping

# Ver información del servidor
redis-cli -h localhost -p 6379 -a redispass123_secure_2024 info

# Ver uso de memoria
redis-cli -h localhost -p 6379 -a redispass123_secure_2024 info memory

# Ver clientes conectados
redis-cli -h localhost -p 6379 -a redispass123_secure_2024 client list
```

### Operaciones Comunes

```bash
# Set/Get de datos
SET user:123 '{"name":"Juan","age":30}'
GET user:123

# Contadores
INCR page_views:home
GET page_views:home

# Listas
LPUSH notifications "Nuevo mensaje"
LRANGE notifications 0 -1

# Sets
SADD online_users user123 user456
SMEMBERS online_users

# Hashes
HSET user:123 name "Juan" age 30
HGETALL user:123

# Expiración
SET session:abc "data" EX 3600  # Expira en 1 hora
TTL session:abc  # Ver tiempo restante
```

### Scripts Personalizados

```bash
# Script de backup manual
./backup-redis.sh

# Health check
./health-check.sh

# Crear cluster (si está habilitado)
./create-cluster.sh 3
```

## 📊 Monitoreo

### Dashboard Web

Accede al dashboard en: **http://localhost:8080**

#### Funcionalidades:
- **Métricas en tiempo real**: Memoria, CPU, conexiones, operaciones/seg
- **Estado del sistema**: Health checks automáticos
- **Alertas visuales**: Indicadores de estado
- **Enlaces rápidos**: Métricas JSON y health checks

### Monitoreo por Línea de Comandos

```bash
# Ejecutar monitor completo
python monitoring-redis.py

# Solo test de conectividad
python monitoring-redis.py --test

# Health check completo
python monitoring-redis.py --health-check

# Métricas para Prometheus
python monitoring-redis.py --prometheus

# Configurar intervalo personalizado
python monitoring-redis.py --interval 60
```

### Configuración de Alertas

```python
# Configuración en Python
alert_config = AlertConfig(
    max_memory_percent=85.0,      # Alerta si memoria > 85%
    max_latency_ms=100.0,         # Alerta si latencia > 100ms
    max_connections=8000,         # Alerta si conexiones > 8000
    min_disk_space_mb=1000,       # Alerta si disco < 1GB
    alert_email="admin@example.com"  # Email para alertas
)
```

### Logs de Monitoreo

```bash
# Ver logs del monitor
tail -f /var/log/redis/monitoring.log

# Ver alertas
tail -f /var/log/redis/alerts.log

# Ver métricas actuales
cat /var/log/redis/metrics.json

# Ver health checks
tail -f /var/log/redis/health.log
```

## 🏗️ Cluster

### Habilitar Redis Cluster

```bash
# 1. Editar configuración
cp redis-cluster.conf redis.conf

# 2. Habilitar cluster en configuración
sed -i 's/# cluster-enabled yes/cluster-enabled yes/' redis.conf

# 3. Reiniciar Redis
sudo systemctl restart redis

# 4. Crear cluster (requiere múltiples nodos)
redis-cli --cluster create node1:6379 node2:6379 node3:6379
```

### Operaciones de Cluster

```bash
# Ver información del cluster
redis-cli -h localhost -p 6379 -a redispass123_secure_2024 cluster info

# Ver nodos del cluster
redis-cli -h localhost -p 6379 -a redispass123_secure_2024 cluster nodes

# Ver distribución de slots
redis-cli -h localhost -p 6379 -a redispass123_secure_2024 cluster slots

# Añadir nodo al cluster
redis-cli --cluster add-node new_node:6379 existing_node:6379

# Balancear slots
redis-cli --cluster rebalance existing_node:6379
```

### Docker Compose con Cluster

```bash
# Iniciar con perfil de cluster
docker-compose -f docker-compose.redis.yml --profile cluster up redis-cluster

# Ver logs del cluster
docker-compose -f docker-compose.redis.yml --profile cluster logs -f redis-cluster
```

## 💾 Backup

### Backup Automático

```bash
# El backup automático se ejecuta diariamente a las 2:00 AM
# Configuración en crontab:
0 2 * * * /path/to/redis-config/backup-redis.sh >> /var/log/redis/backup.log 2>&1
```

### Backup Manual

```bash
# Método 1: Usando el script incluido
./backup-redis.sh

# Método 2: Con Docker Compose
docker-compose -f docker-compose.redis.yml --profile backup up redis-backup

# Método 3: Desde Redis CLI
redis-cli -h localhost -p 6379 -a redispass123_secure_2024 BGSAVE
cp /data/dump.rdb /backups/redis_backup_$(date +%Y%m%d_%H%M%S).rdb

# Método 4: Comando directo en contenedor
docker exec shibasito-redis redis-cli -a redispass123_secure_2024 BGSAVE
docker cp shibasito-redis:/data/dump.rdb ./backup_$(date +%Y%m%d).rdb
```

### Restaurar desde Backup

```bash
# 1. Parar Redis
sudo systemctl stop redis

# 2. Hacer backup del archivo actual
sudo mv /data/dump.rdb /data/dump.rdb.backup

# 3. Copiar backup deseado
sudo cp /backups/redis_backup_YYYYMMDD_HHMMSS.rdb /data/dump.rdb

# 4. Configurar permisos
sudo chown redis:redis /data/dump.rdb
sudo chmod 644 /data/dump.rdb

# 5. Reiniciar Redis
sudo systemctl start redis

# 6. Verificar
redis-cli -h localhost -p 6379 -a redispass123_secure_2024 ping
```

### Gestión de Backups

```bash
# Ver backups disponibles
ls -la /data/backups/

# Limpiar backups antiguos (más de 30 días)
find /data/backups -name "redis_backup_*.rdb.gz" -mtime +30 -delete

# Ver tamaño de backups
du -sh /data/backups/*

# Verificar integridad de backup
redis-check-rdb /backups/redis_backup_20231201_020000.rdb
```

## ⚡ Performance

### Optimizaciones Incluidas

```bash
# Configuración de memoria optimizada
maxmemory 512mb                    # 75% de RAM disponible
maxmemory-policy allkeys-lru      # Política de eviction

# Optimización de estructuras de datos
hash-max-ziplist-entries 512
hash-max-ziplist-value 64
list-max-ziplist-size -2
set-max-intset-entries 512
zset-max-ziplist-entries 128
zset-max-ziplist-value 64

# Configuración de I/O
io-threads 4                      # 4 threads de I/O
io-threads-do-reads yes           # Habilitar lecturas en threads

# Buffer de clientes optimizado
client-output-buffer-limit normal 0 0 0
client-output-buffer-limit replica 256mb 64mb 60
client-output-buffer-limit pubsub 32mb 8mb 60
```

### Tuning para Alto Rendimiento

```bash
# 1. Ajustar límites del sistema
echo 'vm.overcommit_memory = 1' >> /etc/sysctl.conf
echo 'net.core.somaxconn = 65535' >> /etc/sysctl.conf
sysctl -p

# 2. Configurar límites de archivos
echo '* soft nofile 65536' >> /etc/security/limits.conf
echo '* hard nofile 65536' >> /etc/security/limits.conf

# 3. Ajustar configuración de memoria del kernel
echo 'vm.swappiness = 1' >> /etc/sysctl.conf
```

### Benchmarks de Performance

```bash
# Benchmark básico
redis-benchmark -h localhost -p 6379 -a redispass123_secure_2024

# Benchmark con datos específicos
redis-benchmark -h localhost -p 6379 -a redispass123_secure_2024 -t set,get -n 100000 -r 100000

# Benchmark de latencia
redis-benchmark -h localhost -p 6379 -a redispass123_secure_2024 --latency

# Test de throughput específico
redis-benchmark -h localhost -p 6379 -a redispass123_secure_2024 -t set,get -c 50 -n 10000 -d 1024
```

## 🔍 Troubleshooting

### Problemas Comunes

#### 1. Redis no inicia

```bash
# Verificar configuración
redis-server /path/to/redis.conf --test-memory

# Ver logs de error
journalctl -u redis -f
tail -f /var/log/redis/redis-server.log

# Verificar puertos
netstat -tlnp | grep 6379
ss -tlnp | grep 6379

# Verificar permisos
ls -la /data/
ls -la /var/log/redis/
```

#### 2. Problemas de memoria

```bash
# Ver uso actual de memoria
redis-cli -h localhost -p 6379 -a redispass123_secure_2024 info memory

# Ver claves grandes
redis-cli -h localhost -p 6379 -a redispass123_secure_2024 --bigkeys

# Ver distribución de tipos de datos
redis-cli -h localhost -p 6379 -a redispass123_secure_2024 --scan --pattern '*' | head -100 | xargs redis-cli -h localhost -p 6379 -a redispass123_secure_2024 debug object
```

#### 3. Conexiones lentas

```bash
# Ver clientes conectados
redis-cli -h localhost -p 6379 -a redispass123_secure_2024 client list

# Ver conexiones de red
netstat -an | grep 6379 | wc -l

# Test de latencia
redis-cli -h localhost -p 6379 -a redispass123_secure_2024 --latency-history
```

#### 4. Problemas de persistencia

```bash
# Verificar estado de AOF
redis-cli -h localhost -p 6379 -a redispass123_secure_2024 info persistence

# Verificar último dump RDB
ls -la /data/dump.rdb
stat /data/dump.rdb

# Verificar integridad del dump
redis-check-rdb /data/dump.rdb

# Verificar integridad del AOF
redis-check-aof /data/appendonly.aof
```

#### 5. Problemas de cluster

```bash
# Ver estado del cluster
redis-cli -h localhost -p 6379 -a redispass123_secure_2024 cluster info

# Ver información detallada de nodos
redis-cli -h localhost -p 6379 -a redispass123_secure_2024 cluster nodes

# Reparar cluster
redis-cli --cluster check any_node:6379
redis-cli --cluster fix any_node:6379
```

### Herramientas de Diagnóstico

```bash
# Monitor en tiempo real
redis-cli -h localhost -p 6379 -a redispass123_secure_2024 monitor

# Info detallada
redis-cli -h localhost -p 6379 -a redispass123_secure_2024 info all

# Configuración actual
redis-cli -h localhost -p 6379 -a redispass123_secure_2024 config get '*'

# Comandos lentos
redis-cli -h localhost -p 6379 -a redispass123_secure_2024 slowlog get 10

# Estadísticas de red
redis-cli -h localhost -p 6379 -a redispass123_secure_2024 info stats
```

## 📚 API y Referencias

### Monitoreo Programático

```python
import redis
import json

# Conectar a Redis
r = redis.Redis(
    host='localhost',
    port=6379,
    password='redispass123_secure_2024',
    decode_responses=True
)

# Obtener información básica
info = r.info()
print(f"Versión: {info['redis_version']}")
print(f"Memoria usada: {info['used_memory_human']}")
print(f"Conexiones: {info['connected_clients']}")

# Obtener métricas específicas
memory_info = r.info('memory')
performance_info = r.info('persistence')

# Health check programático
def check_redis_health():
    try:
        # Test de conectividad
        if r.ping():
            print("✅ Redis está funcionando")
            
            # Test de memoria
            memory_percent = (memory_info['used_memory'] / memory_info['maxmemory']) * 100
            if memory_percent > 85:
                print(f"⚠️  Uso de memoria alto: {memory_percent:.1f}%")
            
            # Test de latencia
            start_time = time.time()
            r.ping()
            latency = (time.time() - start_time) * 1000
            
            if latency > 100:
                print(f"⚠️  Latencia alta: {latency:.1f}ms")
            else:
                print(f"✅ Latencia normal: {latency:.1f}ms")
                
        return True
    except redis.ConnectionError:
        print("❌ Error de conexión a Redis")
        return False
```

### Integración con Prometheus

```python
# En monitoring-redis.py
from prometheus_client import start_http_server, Gauge, Counter

# Crear métricas
redis_memory = Gauge('redis_memory_bytes', 'Redis memory usage', ['type'])
redis_connections = Gauge('redis_connected_clients', 'Redis connected clients')
redis_ops = Counter('redis_operations_total', 'Redis operations', ['command'])

# Iniciar servidor de métricas
start_http_server(8000)

# Exportar métricas en loop
while True:
    info = r.info()
    
    redis_memory.labels(type='used').set(info['used_memory'])
    redis_memory.labels(type='rss').set(info['used_memory_rss'])
    redis_memory.labels(type='peak').set(info['used_memory_peak'])
    
    redis_connections.set(info['connected_clients'])
    
    time.sleep(30)
```

### Configuración de Docker Avanzada

```yaml
# docker-compose.override.yml
version: '3.8'
services:
  redis:
    # Configuración para producción
    deploy:
      replicas: 2
      update_config:
        parallelism: 1
        delay: 10s
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
    
    # Variables de entorno para producción
    environment:
      - REDIS_MAXMEMORY=1gb
      - REDIS_MAXMEMORY_POLICY=allkeys-lru
      - REDIS_APPENDONLY=yes
    
    # Volumes adicionales para producción
    volumes:
      - redis_prod_data:/data
      - redis_prod_logs:/var/log/redis
    
    # Network específica
    networks:
      - production-network
```

## 🤝 Contribución

Para contribuir al proyecto:

1. Fork el repositorio
2. Crear branch para nueva funcionalidad: `git checkout -b feature/nueva-funcionalidad`
3. Commit de cambios: `git commit -am 'Agregar nueva funcionalidad'`
4. Push al branch: `git push origin feature/nueva-funcionalidad`
5. Crear Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver archivo `LICENSE` para más detalles.

## 🆘 Soporte

- **Documentación oficial**: [Redis Documentation](https://redis.io/documentation)
- **Issues**: Reportar problemas en el repositorio
- **Email**: admin@shibasito.com
- **Wiki**: Ver documentación adicional en el wiki del proyecto

---

**Sistema Distribuido Shibasito - Redis Configuration** 🚀

*Configuración completa, optimizada y lista para producción*