# syntax=docker/dockerfile:1.4
# Stage 1: Build
# Se utiliza una versión estable de Maven.
FROM maven:3.9.6-eclipse-temurin-17 AS build
WORKDIR /app
# Copy only pom first to leverage Docker cache for dependency resolution
COPY pom.xml ./

# Use BuildKit cache for Maven local repository so dependencies aren't downloaded every build.
# Also pass a property to skip the fabric8 docker plugin during the image build to avoid
# attempts to talk to the Docker daemon from inside the builder.
RUN --mount=type=cache,id=maven,target=/root/.m2 \ 
	mvn -B -DskipTests -Dfabric8.skip=true -Ddocker.skip=true dependency:go-offline

# Now copy source and build (this keeps dependency downloads cached when pom.xml doesn't change)
COPY src ./src
RUN --mount=type=cache,id=maven,target=/root/.m2 mvn -B -DskipTests -Dfabric8.skip=true -Ddocker.skip=true clean install

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