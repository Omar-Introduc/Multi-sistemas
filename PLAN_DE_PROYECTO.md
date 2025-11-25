# Planeación de Sprints y Issues - Proyecto Multi-sistemas

Este documento detalla la planeación del proyecto dividido en Sprints, con sus respectivos Issues para el desarrollo del Sistema Distribuido de Entrenamiento y Consumo de IA.

## Resumen del Proyecto
Sistema distribuido para entrenamiento y reconocimiento de objetos/personas utilizando modelos de IA, comunicación vía Sockets, y despliegue en cluster.

---

## Sprint 1: Arquitectura Base y Comunicación
**Objetivo:** Establecer la infraestructura básica de comunicación y la captura de video.

### Issues
#### 1.1. Inicialización del Proyecto y Repositorio
- **Descripción:** Crear la estructura de directorios para los 3 componentes principales (Entrenamiento, Testeo, Vigilante) y configurar el control de versiones.
- **Tareas:**
    - Crear repositorio y ramas base.
    - Definir estructura de carpetas (e.g., `/src/training`, `/src/testing`, `/src/monitoring`).
    - Crear `Makefile` o scripts de compilación iniciales.

#### 1.2. Implementación de Módulo de Comunicación (Sockets)
- **Descripción:** Desarrollar una librería o módulo compartido para manejar la comunicación por Sockets TCP/IP, ya que no se permiten frameworks de alto nivel.
- **Tareas:**
    - Implementar clase `SocketServer` (Manejo de hilos por conexión).
    - Implementar clase `SocketClient`.
    - Definir protocolo de mensajes (e.g., Estructura JSON o binaria personalizada: `Header | Payload`).

#### 1.3. Servidor de Video (Captura RTSP)
- **Descripción:** Implementar el componente que se conecta a las cámaras IP vía RTSP y extrae frames.
- **Tareas:**
    - Conexión a stream RTSP (usando OpenCV o similar).
    - Extracción de frames en un buffer circular o cola.
    - Servir frames a petición o por stream a los nodos de procesamiento.

---

## Sprint 2: Servidor de Entrenamiento (Training Server)
**Objetivo:** Desarrollar el núcleo de entrenamiento de IA y la distribución de carga.

### Issues
#### 2.1. Diseño del Modelo de IA
- **Descripción:** Definir y programar el modelo de IA a utilizar (e.g., Red Neuronal Convolucional, SVM, etc.) compatible con el problema (reconocimiento de n objetos).
- **Tareas:**
    - Seleccionar algoritmo/librería base (respetando restricciones).
    - Implementar pipeline de pre-procesamiento de datos (imágenes).
    - Definir arquitectura del modelo.

#### 2.2. Lógica de Entrenamiento Distribuido/Secuencial
- **Descripción:** Implementar la lógica para recibir datasets y entrenar el modelo.
- **Tareas:**
    - Recibir datos de entrada (imágenes + etiquetas) vía Sockets.
    - Implementar bucle de entrenamiento.
    - (Opcional) Implementar paralelismo en el entrenamiento (distribución de batches entre hilos/nodos).

#### 2.3. Persistencia de Modelos
- **Descripción:** Guardar y cargar los modelos entrenados en disco para que puedan ser consumidos por el Servidor de Testeo.
- **Tareas:**
    - Serialización del modelo entrenado (pesos/parámetros).
    - Mecanismo de versionado de modelos (timestamp o ID).

---

## Sprint 3: Servidor de Testeo (Testing Server)
**Objetivo:** Implementar la inferencia y detección de objetos en tiempo real.

### Issues
#### 3.1. Carga y Actualización de Modelos
- **Descripción:** El servidor debe ser capaz de cargar el último modelo entrenado disponible.
- **Tareas:**
    - Monitorizar directorio de modelos o recibir notificación de nuevo modelo.
    - Carga dinámica del modelo en memoria.

#### 3.2. Motor de Inferencia (Detección)
- **Descripción:** Procesar frames provenientes del Servidor de Video usando el modelo cargado.
- **Tareas:**
    - Recibir frame del Servidor de Video.
    - Ejecutar inferencia (Forward pass).
    - Filtrar resultados por umbral de confianza.

#### 3.3. Generación de Alertas y Registro
- **Descripción:** Cuando se detecta un objeto de interés, generar un registro y guardar la evidencia.
- **Tareas:**
    - Guardar imagen con bounding box o la imagen original en disco.
    - Generar estructura de log: `{Tipo, Fecha, Hora, ID_Camara, Path_Imagen}`.
    - Enviar alerta al Cliente Vigilante vía Sockets.

---

## Sprint 4: Cliente Vigilante y Monitoreo
**Objetivo:** Visualización de resultados y gestión del sistema.

### Issues
#### 4.1. Interfaz de Usuario (Vigilante)
- **Descripción:** Aplicación cliente para ver los registros en tiempo real.
- **Tareas:**
    - Diseño de UI (Consola avanzada o GUI simple).
    - Conexión persistente con el Servidor de Testeo.

#### 4.2. Visualización de Registros
- **Descripción:** Mostrar tabla de detecciones y permitir ver la imagen capturada.
- **Tareas:**
    - Renderizar tabla con datos (Objeto, Hora, Cámara).
    - Visualizar imagen asociada al registro (descarga bajo demanda o push).

#### 4.3. Pruebas de Integración Sistema Completo
- **Descripción:** Verificar flujo completo: Cámara -> Video Server -> Testeo -> Alerta -> Vigilante.
- **Tareas:**
    - Debugging de comunicación entre módulos.
    - Validación de latencia y consistencia de datos.

---

## Sprint 5: Despliegue, Optimización y Entrega
**Objetivo:** Puesta en producción (simulada), optimización y documentación final.

### Issues
#### 5.1. Despliegue en Cluster/LAN
- **Descripción:** Configurar el sistema para correr en múltiples máquinas (o VMs).
- **Tareas:**
    - Configuración de IPs y Puertos en archivos de configuración.
    - Scripts de lanzamiento remoto o manual de despliegue.

#### 5.2. Optimización y Concurrencia
- **Descripción:** Asegurar el uso correcto de hilos y evitar condiciones de carrera.
- **Tareas:**
    - Profiling de uso de CPU/Memoria.
    - Revisión de locks y semáforos en colas compartidas.

#### 5.3. Documentación y Presentación
- **Descripción:** Elaborar los entregables finales.
- **Tareas:**
    - Redactar Informe PDF (Arquitectura, Protocolos, Manual de Usuario).
    - Crear Diapositivas de Presentación.
    - Diagramas de Arquitectura y Protocolo.

## Verificación del Plan
- **Revisión con el Usuario:** Confirmar que el alcance cubre todos los requisitos del README.
- **Validación Técnica:** Asegurar que las restricciones (No Frameworks, Solo Sockets) se respetan en cada issue.
