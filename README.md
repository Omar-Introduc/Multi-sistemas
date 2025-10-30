🏛️ Shibasito - Sistema Distribuido de Pagos y Préstamos con RabbitMQ

Estado: ✅ Completado y Operativo (Versión 1.0.0)
Este repositorio contiene la implementación completa del sistema distribuido "Shibasito", desarrollado como parte de la Práctica 03 de CC4P1 - Programación Concurrente y Distribuida. El sistema simula operaciones bancarias (cuentas, préstamos, transacciones) y validación de identidad (RENIEC) utilizando una arquitectura heterogénea, microservicios y RabbitMQ como middleware central.


🎯 Descripción General

Shibasito es un sistema diseñado para demostrar principios de programación distribuida y concurrente. Se compone de servicios independientes que se comunican de forma asíncrona a través de colas de mensajes, garantizando desacoplamiento, escalabilidad y tolerancia a fallos. El proyecto cumple con todos los requisitos especificados, incluyendo la heterogeneidad tecnológica, la arquitectura de nodos simulada con Docker, la comunicación exclusiva vía RabbitMQ (sin WebSockets/Socket.IO) , pruebas de estrés concurrentes y validación de datos entre bases de datos.


✨ Características Principales y Requisitos Cumplidos


🏗️ Arquitectura Distribuida: Múltiples nodos (simulados con contenedores Docker) para cada componente principal (LP1, LP2, LP3, Middleware).

🌐 Sistema Heterogéneo:

Lenguajes: Java 17/Spring Boot (LP1 - Banco) , Python 3.11/FastAPI (LP2 - RENIEC) , y un tercer lenguaje (LP3 - Clientes, ej. JavaScript con React Native/Electron).


Bases de Datos: PostgreSQL (BD1 - Banco) y MySQL (BD2 - RENIEC).


Sistemas Operativos: Múltiples SOs simulados mediante imágenes Docker base (ej. Linux para backend, potencialmente diferente para clientes o si se usan imágenes base distintas).


🔄 Middleware RabbitMQ: Toda la comunicación entre servicios (Banco ↔ RENIEC, Clientes ↔ Banco) se realiza exclusivamente a través de RabbitMQ.


📱 Cliente Móvil (LP3): Aplicación funcional con transacciones QR , consulta de estados y solicitud de préstamos , comunicándose vía RabbitMQ.


💻 Cliente Desktop (LP3): Aplicación funcional con GUI , consulta detallada de estados , historial y solicitud de préstamos (sin QR ), comunicándose vía RabbitMQ.

🧪 Testing Completo (testing_system/):
Pruebas unitarias para LP1 y LP2.
Stress testing con 1500+ registros y 50 hilos concurrentes.
Validación de integridad de datos entre BD1 y BD2 post-stress.
Verificación de persistencia.
Métricas de rendimiento.
🐳 Orquestación con Docker Compose: Definición completa de la infraestructura y servicios para fácil despliegue local.
⚙️ Automatización CI/CD: Makefile robusto para construir, ejecutar, probar, validar y limpiar el entorno.
📈 Monitoreo (Bonus): Stack de Prometheus y Grafana preconfigurado para observabilidad.

📝 Documentación: Incluye diagramas de arquitectura y protocolo requeridos, además de documentación técnica detallada.


🏗️ Arquitectura del Sistema

El sistema se compone de los siguientes servicios orquestados por Docker Compose:

Fuente: docs/architecture.png (Referencia al diagrama requerido )


servicio-banco-lp1 (Java/Spring Boot): Gestiona la lógica de negocio bancaria y la base de datos BD1 (PostgreSQL). Escucha solicitudes de clientes vía RabbitMQ y se comunica con RENIEC.


servicio-reniec-lp2 (Python/FastAPI): Simula el servicio RENIEC, gestionando la base de datos BD2 (MySQL). Responde a solicitudes de validación de identidad desde el banco vía RabbitMQ.


bd1_postgresql: Contenedor de base de datos PostgreSQL para el servicio bancario.


bd2_mysql: Contenedor de base de datos MySQL para el servicio RENIEC.


rabbitmq: Contenedor del message broker RabbitMQ, núcleo de comunicación.

redis: Contenedor de Redis para caché (opcional, mejora de rendimiento).
prometheus / grafana: Contenedores para el stack de monitoreo (opcional).
aplicaciones-cliente-lp3 (Móvil y Desktop): Estas no se ejecutan en Docker, sino en sus plataformas nativas (móvil, PC), conectándose a RabbitMQ expuesto por el host.
El flujo de comunicación principal se realiza mediante mensajes estructurados (JSON) a través de colas específicas en RabbitMQ para cada tipo de operación (transacciones, préstamos, validaciones).


Fuente: docs/protocol.png (Referencia al diagrama requerido )


🛠️ Stack Tecnológico

Backend LP1: Java 17, Spring Boot 3.x, Spring Data JPA, Spring AMQP
Backend LP2: Python 3.11, FastAPI, SQLAlchemy, Pika (cliente RabbitMQ)

Frontend LP3 (Ejemplo): JavaScript, React Native (Móvil), Electron (Desktop)


Bases de Datos: PostgreSQL 15 , MySQL 8.0


Middleware: RabbitMQ 3.13 (con Management UI)

Cache: Redis 7
Containerización: Docker, Docker Compose v2+
Testing: Pytest, JUnit 5, Scripting Python (para stress/validation)
Monitoreo: Prometheus, Grafana
Automatización: Make

📁 Estructura del Repositorio


⚙️ Requisitos Previos

Git
Docker (versión 20.10+)
Docker Compose (v2.0+)
make (opcional, pero recomendado para usar el Makefile)
Conexión a internet (para descargar imágenes Docker)
Recursos Recomendados: 16GB RAM, 10GB+ Espacio en Disco

🚀 Instalación y Configuración

Clonar el Repositorio:
Configurar Variables de Entorno:
Copia el archivo de ejemplo:
IMPORTANTE: Edita el archivo .env y configura contraseñas seguras para las bases de datos y RabbitMQ.
Construir las Imágenes Docker:
Puedes usar el script de inicio o el Makefile:

⚡ Ejecución del Sistema


Iniciar Todos los Servicios:

El sistema puede tardar unos minutos en iniciar completamente, especialmente la primera vez mientras se crean las bases de datos y se aplican las inicializaciones. El script start-shibasito.sh incluye verificaciones de salud básicas.

Verificar Estado:


Ver Logs:


Detener el Sistema:


Limpieza Completa (Elimina Contenedores, Volúmenes y Redes):

¡ADVERTENCIA! Esto borrará todos los datos persistentes.

🧪 Ejecución de Pruebas

La suite de pruebas completa se encuentra en el directorio testing_system/. Puedes ejecutarla usando el Makefile:
Asegúrate que el sistema esté corriendo: make up
Ejecutar Pruebas Unitarias:
Ejecutar Stress Test (+1500 registros, 50 hilos):
(Esto generará las bases de datos stress_test_lp1.db y stress_test_lp2.db dentro de testing_system/)
Ejecutar Validación de Integridad Post-Stress:
Ejecutar Pipeline Completo de Pruebas (Unit + Stress + Validation):
Los reportes detallados de las pruebas se guardarán en /workspace/testing_system/reports/.

🌐 Acceso a Servicios

API Banco (LP1): http://localhost:8080/api/...
API RENIEC (LP2): http://localhost:8000/api/...
API RENIEC Docs (Swagger): http://localhost:8000/docs
RabbitMQ Management UI: http://localhost:15672 (Usuario/Contraseña definidos en .env)
Grafana Dashboard: http://localhost:3000 (Usuario: admin, Contraseña definida en .env o por defecto admin)
Prometheus: http://localhost:9090
PostgreSQL (BD1): Host: localhost, Puerto: 5432
MySQL (BD2): Host: localhost, Puerto: 3306
Redis: Host: localhost, Puerto: 6379

📚 Documentación Adicional

Documentación Técnica Completa: docs/SHIBASITO_DOCUMENTACION_COMPLETA.md

Diagrama de Arquitectura: docs/architecture.png (o similar)


Diagrama de Protocolo: docs/protocol.png (o similar)

Documentación del Makefile: README_MAKEFILE.md
Documentación Sistema de Pruebas: testing_system/README.md
