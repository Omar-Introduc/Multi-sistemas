# Proyecto Banco Shibasito

Este proyecto implementa un sistema bancario distribuido utilizando Docker para orquestar los diferentes servicios.

## Arquitectura

El sistema consta de los siguientes servicios:

- `servicio-banco-lp1`: Un servicio en Java (Spring Boot) que gestiona las operaciones bancarias.
- `servicio-reniec-lp2`: Un servicio en Python que simula la validación de identidad con RENIEC.
- `aplicaciones-cliente-lp3`: Aplicaciones cliente (móvil y de escritorio) para interactuar con el sistema.
- `bd1`: Base de datos PostgreSQL para el servicio bancario.
- `bd2`: Base de datos MySQL para el servicio de RENIEC.
- `rabbitmq`: Middleware para la comunicación asíncrona entre servicios.

## Cómo ejecutar el proyecto

1. Clona este repositorio.
2. Asegúrate de tener Docker y Docker Compose instalados.
3. Ejecuta `docker-compose up --build` en la raíz del proyecto.
