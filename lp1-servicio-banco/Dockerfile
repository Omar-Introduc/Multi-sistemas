# Multistage Dockerfile para LP1 - Servicio Banco
# Etapa 1: Build stage con Maven y Java 17
FROM openjdk:17-jdk-slim as builder

# Instalar Maven
RUN apt-get update && \
    apt-get install -y maven && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /app

# Copiar pom.xml primero para aprovechar cache de Docker
COPY pom.xml .

# Descargar dependencias (esto se cachea si pom.xml no cambia)
RUN mvn dependency:go-offline -B

# Copiar código fuente
COPY src ./src

# Compilar y crear JAR
RUN mvn clean package -DskipTests && \
    mv target/*.jar app.jar

# Etapa 2: Runtime stage
FROM openjdk:17-jdk-slim

# Crear usuario no-root para seguridad
RUN groupadd -r appgroup && useradd -r -g appgroup appuser

# Instalar curl para health check
RUN apt-get update && \
    apt-get install -y curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Crear directorio para la aplicación
WORKDIR /app

# Copiar JAR desde el stage anterior
COPY --from=builder /app/app.jar app.jar

# Crear directorio para logs
RUN mkdir -p /app/logs && \
    chown -R appuser:appgroup /app

# Cambiar a usuario no-root
USER appuser

# Exponer puerto 8080
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8080/actuator/health || exit 1

# Variables de entorno por defecto
ENV JAVA_OPTS="-Xms512m -Xmx1024m -XX:+UseG1GC"
ENV SPRING_PROFILES_ACTIVE=prod

# Comando por defecto
CMD ["sh", "-c", "java $JAVA_OPTS -jar app.jar"]
