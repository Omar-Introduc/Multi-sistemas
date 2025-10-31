# Dockerfile para Health Checks
# Imagen base con todas las herramientas necesarias

FROM ubuntu:20.04

# Evitar prompts durante la instalación
ENV DEBIAN_FRONTEND=noninteractive

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    bash \
    curl \
    wget \
    gnupg \
    ca-certificates \
    lsb-release \
    software-properties-common \
    apt-transport-https \
    bc \
    jq \
    python3 \
    python3-pip \
    vim \
    less \
    netcat-openbsd \
    dnsutils \
    iputils-ping \
    telnet \
    htop \
    sysstat \
    logrotate \
    cron \
    && rm -rf /var/lib/apt/lists/*

# Instalar PostgreSQL client
RUN echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list \
    && wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add - \
    && apt-get update \
    && apt-get install -y postgresql-client-13 \
    && rm -rf /var/lib/apt/lists/*

# Instalar MySQL client
RUN apt-get install -y default-mysql-client \
    && rm -rf /var/lib/apt/lists/*

# Instalar Redis tools
RUN apt-get install -y redis-tools \
    && rm -rf /var/lib/apt/lists/*

# Instalar RabbitMQ tools
RUN curl -fsSL https://keys.openpgp.org/vks/v1/by-fingerprint/0A9AF2115F4687BD29803A206B73A36E6026DFCA | gpg --dearmor | tee /usr/share/keyrings/com.rabbitmq.team.gpg > /dev/null \
    && curl -fsSL https://dl.cloudsmith.io/public/rabbitmq-erlang/gpg.E495BB49CC4BBE5B.key | gpg --dearmor | tee /usr/share/keyrings/io.cloudsmith.rabbitmq.E495BB49CC4BBE5B.gpg > /dev/null \
    && curl -fsSL https://dl.cloudsmith.io/public/rabbitmq/rabbitmq-erlang/gpg.9F4587F226208342.key | gpg --dearmor | tee /usr/share/keyrings/io.cloudsmith.rabbitmq.9F4587F226208342.gpg > /dev/null \
    && curl -fsSL https://dl.cloudsmith.io/public/rabbitmq/rabbitmq-server/gpg.9F4587F226208342.key | gpg --dearmor | tee /usr/share/keyrings/io.cloudsmith.rabbitmq.9F4587F226208342.gpg > /dev/null \
    && tee /etc/apt/sources.list.d/rabbitmq-team.list <<EOF
deb [signed-by=/usr/share/keyrings/io.cloudsmith.rabbitmq.E495BB49CC4BBE5B.gpg] https://dl.cloudsmith.io/public/rabbitmq/rabbitmq-erlang/gpg.E495BB49CC4BBE5B.key
deb [signed-by=/usr/share/keyrings/io.cloudsmith.rabbitmq.9F4587F226208342.gpg] https://dl.cloudsmith.io/public/rabbitmq/rabbitmq-server/gpg.9F4587F226208342.key
deb-src [signed-by=/usr/share/keyrings/io.cloudsmith.rabbitmq.9F4587F226208342.gpg] https://dl.cloudsmith.io/public/rabbitmq/rabbitmq-erlang/gpg.E495BB49CC4BBE5B.key
deb-src [signed-by=/usr/share/keyrings/io.cloudsmith.rabbitmq.9F4587F226208342.gpg] https://dl.cloudsmith.io/public/rabbitmq/rabbitmq-server/gpg.9F4587F226208342.key
EOF \
    && apt-get update \
    && apt-get install -y erlang-base \
                        erlang-asn1 erlang-crypto erlang-eldap erlang-ftp erlang-inets \
                        erlang-mnesia erlang-os-mon erlang-parsetools erlang-public-key \
                        erlang-runtime-tools erlang-snmp erlang-ssl \
                        erlang-syntax-tools erlang-tftp erlang-tools erlang-xmerl \
                        rabbitmq-server \
    && rm -rf /var/lib/apt/lists/*

# Instalar herramientas de monitoreo adicionales
RUN apt-get install -y \
    iotop \
    nethogs \
    tcpdump \
    strace \
    lsof \
    tree \
    && rm -rf /var/lib/apt/lists/*

# Crear usuario no root para ejecutar health checks
RUN useradd -m -s /bin/bash healthcheck \
    && usermod -aG sudo healthcheck \
    && echo "healthcheck ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# Crear directorios necesarios
RUN mkdir -p /app/logs \
    /app/reports \
    /app/config \
    && chown -R healthcheck:healthcheck /app

# Configurar directorio de trabajo
WORKDIR /app

# Copiar scripts de health checks
COPY scripts/ /app/
RUN chmod +x /app/*.sh

# Copiar archivos de configuración
COPY config.env.example /app/config/config.env.example

# Copiar script de entrada
COPY docker-entrypoint.sh /app/docker-entrypoint.sh
RUN chmod +x /app/docker-entrypoint.sh

# Configurar cron (opcional)
COPY crontab /etc/cron.d/health-checks
RUN chmod 0644 /etc/cron.d/health-checks

# Configurar timezone
RUN ln -sf /usr/share/zoneinfo/America/Mexico_City /etc/localtime \
    && echo "America/Mexico_City" > /etc/timezone

# Configurar variables de entorno por defecto
ENV SCRIPT_DIR=/app
ENV LOG_LEVEL=INFO
ENV ENVIRONMENT=docker

# Exponer puertos (si se necesitan para servicios web)
EXPOSE 8080 9090 3000

# Health check del contenedor
HEALTHCHECK --interval=5m --timeout=30s --start-period=1m --retries=3 \
    CMD /app/health-check.sh || exit 1

# Usuario no root
USER healthcheck

# Script de entrada
ENTRYPOINT ["/app/docker-entrypoint.sh"]

# Comando por defecto
CMD ["/bin/bash"]
