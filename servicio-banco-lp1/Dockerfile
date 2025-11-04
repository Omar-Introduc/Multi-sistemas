# Stage 1: Build
# Se utiliza una versión estable de Maven.
FROM maven:3.9.6-eclipse-temurin-17 AS build
WORKDIR /app
COPY pom.xml .
COPY src ./src
RUN mvn clean install -DskipTests

# Stage 2: Run
# Se usa la imagen de Semeru JRE, anclada a una versión específica
FROM eclipse-temurin:17-jre-noble

# Se crea un usuario no-root para seguridad
RUN addgroup --system appgroup && adduser --system appuser --ingroup appgroup
USER appuser
WORKDIR /app
COPY --from=build /app/target/*.jar app.jar
EXPOSE 8080

ENTRYPOINT ["java", "-jar", "app.jar"]