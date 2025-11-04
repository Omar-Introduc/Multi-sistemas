Basado en los archivos que proporcionaste, aquí tienes un análisis de los pasos para ejecutar el código y las funcionalidades actuales del sistema.

### Pasos para Ejecutar el Código

Para correr este proyecto, el método principal es usando Docker y Docker Compose, gestionado a través del `Makefile`.

1.  **Requisitos Previos**: Debes tener **Docker** y **Docker Compose** instalados en tu máquina.
2.  **Crear Archivo de Entorno**: El archivo `docker-compose.main.yml` depende de variables de entorno (como `${POSTGRES_DB}`, `${MYSQL_USER}`, `${RABBITMQ_USER}`, etc.) que no están definidas. Necesitarás crear un archivo llamado `.env` en la raíz del proyecto (junto al `Makefile` y `docker-compose.main.yml`) y definir valores para estas variables. El archivo `.gitignore` confirma que este archivo es esperado.
3.  **Construir las Imágenes**: Antes de levantar los servicios, es recomendable construir las imágenes de Docker.
    * Ejecuta el comando: `make build`
4.  **Levantar los Servicios**: Este comando iniciará todos los contenedores definidos en el `docker-compose.main.yml` en segundo plano (`-d`).
    * Ejecuta el comando: `make up`
5.  **Verificar Logs (Opcional)**: Para ver la salida de los contenedores mientras se inician y funcionan.
    * Ejecuta el comando: `make logs`
6.  **Detener los Servicios**: Cuando quieras detener todo el sistema.
    * Ejecuta el comando: `make down`

---

### Funcionalidades Actuales del Sistema

El proyecto es un **sistema distribuido** compuesto por múltiples microservicios, bases de datos y herramientas de monitoreo, todos orquestados por Docker Compose.

#### Componentes Principales

1.  **`servicio-banco-lp1` (Sistema Bancario)**
    * **Tecnología**: Es una aplicación **Java 17** usando el framework **Spring Boot**.
    * **Base de Datos**: Utiliza **PostgreSQL**.
    * **Funcionalidad (Basada en Schema)**: El archivo `schema.sql` de este servicio define la estructura para gestionar:
        * `cuentas` (Cuentas de ahorro o corriente).
        * `prestamos` (Préstamos a clientes).
        * `transacciones` (Depósitos, retiros, pagos, etc.).
    * **Comunicación**: Está configurado para conectarse a **RabbitMQ** (usando `spring-boot-starter-amqp`), lo que sugiere que participa en mensajería o eventos con otros servicios.

2.  **`servicio-reniec-lp2` (Sistema RENIEC)**
    * **Tecnología**: Es una aplicación **Python 3.11** usando el framework **FastAPI**.
    * **Base de Datos**: Utiliza **MySQL**.
    * **Funcionalidad (Basada en Schema y Código)**:
        * El `schema.sql` define una tabla `personas` para almacenar datos personales (DNI, nombres, apellidos, etc.).
        * Al iniciar, el script `start.sh` ejecuta `seed.py`, que puebla la base de datos con dos registros de ejemplo si la tabla está vacía.
        * Expone un único endpoint web en `/` que devuelve `{"message": "Servicio RENIEC LP2"}`.
    * **Comunicación**: Incluye la librería `pika`, indicando que también se conecta a **RabbitMQ**.

3.  **`rabbitmq` (Middleware)**
    * Es el bus de mensajería (Message Broker) que permite la comunicación asíncrona entre el servicio de banco y el servicio de RENIEC.

4.  **Monitoreo (`prometheus` y `grafana`)**
    * **Prometheus** está configurado para recolectar métricas de los servicios (`servicio-banco-lp1` y `servicio-reniec-lp2`).
    * **Grafana** se incluye para visualizar los datos recolectados por Prometheus.

#### Funcionalidades Adicionales

* **Pruebas**: El `Makefile` define un comando `make test` que ejecuta pruebas para ambos servicios (usando `mvn test` para el banco y `pytest` para RENIEC).
* **Build de Imágenes**: Los `Dockerfile` de cada servicio definen cómo construir sus respectivas imágenes de contenedor, usando builds multi-etapa para optimización.