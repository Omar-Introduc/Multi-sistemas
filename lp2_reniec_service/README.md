# LP2 RENIEC Service

Servicio de consultas al Registro Nacional de Identificación y Estado Civil (RENIEC) desarrollado con FastAPI.

## Características

- **Framework**: FastAPI con Python 3.11
- **Puerto**: 8000 (configurable)
- **Health Check**: Incluido en `/health`
- **Documentación**: Swagger UI en `/docs` y ReDoc en `/redoc`
- **Optimización**: Imagen Docker Alpine para menor tamaño
- **Seguridad**: Usuario no-root en el contenedor

## Construcción de la Imagen

```bash
# Construir imagen Docker
docker build -t lp2-reniec-service .

# Verificar imagen creada
docker images lp2-reniec-service
```

## Ejecución del Contenedor

```bash
# Ejecutar en primer plano
docker run -p 8000:8000 lp2-reniec-service

# Ejecutar en segundo plano con variables de entorno
docker run -d \
  --name lp2-reniec \
  -p 8000:8000 \
  -e HOST=0.0.0.0 \
  -e PORT=8000 \
  lp2-reniec-service

# Ver logs
docker logs lp2-reniec

# Seguir logs en tiempo real
docker logs -f lp2-reniec
```

## Variables de Entorno

| Variable | Descripción | Valor por Defecto |
|----------|-------------|-------------------|
| `HOST` | Host de escucha | `0.0.0.0` |
| `PORT` | Puerto de escucha | `8000` |

## Endpoints Disponibles

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/` | GET | Información del servicio |
| `/health` | GET | Health check |
| `/consulta/dni/{dni}` | GET | Consulta datos por DNI |
| `/buscar/nombre` | POST | Búsqueda alternativa |
| `/info` | GET | Información del sistema |
| `/docs` | GET | Documentación Swagger |
| `/redoc` | GET | Documentación ReDoc |

## Ejemplos de Uso

### Health Check
```bash
curl http://localhost:8000/health
```

### Consulta por DNI
```bash
curl http://localhost:8000/consulta/dni/12345678
```

### Consulta POST
```bash
curl -X POST "http://localhost:8000/buscar/nombre" \
  -H "Content-Type: application/json" \
  -d '{"dni": "12345678"}'
```

## Base de Datos de Prueba

El servicio incluye datos de prueba en memoria:

| DNI | Nombre Completo |
|-----|-----------------|
| 12345678 | JUAN CARLOS PEREZ GARCIA |
| 87654321 | MARIA ELENA LOPEZ RODRIGUEZ |

## Desarrollo

### Estructura del Proyecto
```
lp2_reniec_service/
├── Dockerfile          # Imagen Docker optimizada
├── requirements.txt    # Dependencias Python
├── run.sh             # Script de entrada
├── main.py            # Aplicación FastAPI
├── .dockerignore      # Archivos a ignorar
└── README.md          # Esta documentación
```

### Instalación Local
```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar servidor
python main.py

# O usando uvicorn directamente
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## Optimizaciones Aplicadas

1. **Imagen base**: Python 3.11 Alpine (menor tamaño)
2. **Cache de Docker**: Instalación de requirements antes del código
3. **Multi-stage**: No utilizado (aplicación simple)
4. **Usuario no-root**: Ejecución como usuario appuser
5. **Caching**: Pip cache purge después de instalaciones
6. **Limpieza**: Eliminación de cache de apk

## Monitoreo

El servicio incluye health checks automáticos que verifican:
- Estado del proceso
- Respuesta del endpoint `/health`
- Disponibilidad cada 30 segundos

## Seguridad

- Usuario no-root en el contenedor
- CORS configurado (ajustar según necesidades)
- Validación de entrada de datos
- Logging de consultas para auditoría

## Contribución

1. Fork del proyecto
2. Crear rama feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

## Licencia

Este proyecto es parte del sistema distribuido LP2.