# Usar imagen base Python 3.11 Alpine para menor tamaño
FROM python:3.11-alpine

# Configurar directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema necesarias (solo las esenciales)
RUN apk add --no-cache \
    gcc \
    musl-dev \
    libffi-dev \
    && rm -rf /var/cache/apk/*

# Copiar archivo de requirements primero para aprovechar caché de Docker
COPY requirements.txt .

# Instalar dependencias Python (sin archivos dev)
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && pip cache purge

# Copiar código fuente de la aplicación
COPY . .

# Crear usuario no-root para seguridad
RUN adduser -D -s /bin/sh appuser && \
    chown -R appuser:appuser /app
USER appuser

# Exponer puerto 8000 para FastAPI
EXPOSE 8000

# Health check para verificar que el servicio está funcionando
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Comando de entrada usando run.sh
CMD ["./run.sh"]