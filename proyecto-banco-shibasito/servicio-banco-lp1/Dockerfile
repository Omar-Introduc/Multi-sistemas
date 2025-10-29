# Stage 1: Build with Maven
FROM maven:3.8.5-openjdk-17 AS build
WORKDIR /app
COPY . .
RUN mvn clean package -DskipTests

# Stage 2: Create final image
FROM openjdk:17-jdk-slim
WORKDIR /app
COPY --from=build /app/target/banco-0.0.1-SNAPSHOT.jar app.jar
CMD ["java", "-jar", "app.jar"]
