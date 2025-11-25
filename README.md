# Escuela de Ciencias de la Computación
## Practica 04 2025-11
### CC4P1 Programación Concurrente y Distribuida

### Implementación de un Sistema Distribuido para el entrenamiento de IAs de reconocimiento de objetos, animales o personas que requiera entrenamiento.

**El objetivo de esta evaluación** es diseñar e implementar un sistema distribuido que permita el entrenamiento y consumo de modelos de inteligencia artificial (IA) de manera paralela, distribuida y concurrente.

---

### Componentes del Sistema

#### 1. Entrenamiento Distribuido de Modelos de IA (Servidor de Entrenamiento)
Se debe desarrollar un sistema distribuido en el cual un cliente envíe datos de entrada (inputs) y salida (outputs) a un conjunto de servidores (nodos).

Estos servidores pueden ser de manera secuencial (se considerará si se procesa en paralelo distribuido tipo cpu), gestionando los recursos de manera distribuida y concurrente.

**Requisitos:**
* La parte del entrenamiento es de acuerdo al modelo del grupo.
* La carga de trabajo puede ser secuencial, en caso que sea paralelo distribuido la carga de trabajo debe distribuirse entre los nodos del sistema para optimizar el proceso de entrenamiento.
* Se debe garantizar la persistencia y accesibilidad de los modelos entrenados para su posterior consumo.
* Se tiene que entrenar con un grupo "n" de objetos, animales o personas que se pueda reconocer, se tomará en cuenta si mayor es el $n$ para la evaluación, por ejemplo, $n=2$ puede reconocer perros y gatos.

*(Componentes de arquitectura: Servidor de video, Cliente vigilante de objetos, Servidor de testeo de objetos, Servidor de entrenamiento de objetos)*

#### 2. Consumo de Modelos de IA (Servidor de Testeo)
El sistema debe permitir que la cámara enésima use un modelo de IA previamente entrenado y según identifique los objetos y guarde una imagen (objetos, animales o personas) en un archivo y agregue en un registro que objeto se acercó y su imagen.

**Requisitos:**
* El servidor de testeo de objeto debe poder usar su modelo de IA y autónomamente reconocer los objetos entrenados.
* El modelo debe procesar la entrada de los frames del video y devolver la salida esperada de manera eficiente por cada camara.
* Para un numero "c" de cámaras, mientras más cámaras se considerará.

*(Ejemplos de detección: Detecto un Carro, Detecto Maria, Detecto Naranja)*

#### 3. Vigilante de objetos (Cliente Vigilante)
El cliente vigilante de objetos puede ver visualmente el registro que objetos identificados, su foto, la fecha, hora de la captura y la cámara enésima que lo proceso el servidor de testeo de manera continua.

**Ejemplo de Registro:**

| Encontro Tipo | Encontro | Fecha | Hora |
| :--- | :--- | :--- | :--- |
| Mujer | [Foto] | 01/11/2025 | 03:25 |
| Naranja | [Foto] | 01/11/2025 | 15:20 |
| Loro | [Foto] | 03/11/2025 | 2:30 |
| Carro | [Foto] | 05/11/2025 | 14:00 |

---

### Requisitos de Implementación y Técnicos

* **Lenguajes:** Se pide escribir un código en $\{LP1,...\}$, puede ser con uno o más de un lenguaje de programación, exponer y redactar un informe, se tomará en cuenta si usa más lenguajes de programación.
* **Ejecución:** Se iniciará los nodos servidor de video, servidor de testeo de objetos y servidor de entrenamiento de objetos, luego se inician los clientes y recibirá las peticiones de Clientes.
* El módulo del entrenamiento de IA puede estar en el lenguaje de programación que decida. Tomar como base las explicaciones.
* **Despliegue:**
    * Exponer y Ejecutar en cluster, con $\{LP1,...\}$ u otro según sea el caso, ya sea virtual local o en las pcs de su grupo.
    * Desplegar el programa en redes LAN y WIFI.
* **Documentación:**
    * Graficar la arquitectura diseñada.
    * Graficar el diagrama de protocolo.
    * Explicar el desarrollo del programa puntualmente.
* **Restricciones (IMPORTANTE):**
    * Usar solo **Sockets** y el protocolo **RTSP** o similar de acuerdo su cámara ip.
    * **No usar:** websocket, socketio, frameworks, RabbitMQ, MQ, Librerías de Comunicación, etc.
* **Rendimiento:** Usar hilos para mejorar el desempeño y evitar corrupción de registros.

### Entregables
Subir en Univirtual un comprimido que consta de:
1. Códigos fuente de extensión en el LP1, LP2, LP3.
2. PDF Informe.
3. PDF Presentación.

### Evaluación
* Los grupos mayores a 2 alumnos pueden mejorar el "n" (número de objetos a reconocer) o "c" (número de cámaras) 