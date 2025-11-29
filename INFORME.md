# Informe Final - Sistema Distribuido de Entrenamiento y Consumo de IA

## 1. Introducción
Este proyecto implementa un sistema distribuido para el entrenamiento y consumo de modelos de Inteligencia Artificial, diseñado para el reconocimiento de objetos, animales o personas. El sistema permite la captura de video, el entrenamiento de modelos y la detección en tiempo real, todo comunicado a través de una arquitectura basada en Sockets TCP/IP.

## 2. Arquitectura del Sistema
El sistema se compone de cuatro módulos principales:

### 2.1 Servidor de Video (Video Server)
- **Función:** Captura frames de una fuente de video (Cámara Web o RTSP).
- **Comunicación:** Actúa como servidor, esperando peticiones de frames.
- **Tecnología:** OpenCV para captura, Sockets para transmisión.

### 2.2 Servidor de Entrenamiento (Training Server)
- **Función:** Recibe datasets para entrenar modelos de IA y persiste los modelos entrenados. Implementa una arquitectura Master-Worker para distribuir el cálculo de características.
- **Comunicación:** Recibe datos de entrenamiento y sirve el archivo del modelo serializado.
- **Tecnología:** XGBoost (Extreme Gradient Boosting) sobre características HOG. Persistencia vía Pickle.

### 2.3 Servidor de Testeo (Testing Server)
- **Función:** Orquesta el proceso de detección. Consume frames del Video Server y utiliza el modelo del Training Server.
- **Comunicación:** Cliente de Video y Training; Servidor para el Cliente Vigilante.
- **Tecnología:** Inferencia de IA optimizada con XGBoost, gestión de hilos.

### 2.4 Cliente Vigilante (Monitoring)
- **Función:** Interfaz para el usuario final que muestra alertas de detecciones en tiempo real.
- **Comunicación:** Cliente del Testing Server.
- **Tecnología:** Consola/UI.

## 3. Protocolos de Comunicación
Se diseñó un protocolo personalizado sobre TCP/IP:
- **Header:** 4 bytes (Big Endian) indicando la longitud del payload.
- **Payload:** JSON codificado en UTF-8.
- **Datos Binarios:** Imágenes y Modelos se codifican en Base64 dentro del JSON para simplificar el parsing.

## 4. Resultados y Selección del Modelo
Basado en los resultados experimentales detallados en la documentación técnica, se seleccionó **XGBoost** sobre KNN debido a su superioridad en:
1.  **Velocidad de Inferencia:** Crítica para procesamiento de video en tiempo real.
2.  **Precisión:** Mejor generalización ante variaciones de iluminación y postura.
3.  **Eficiencia:** Menor consumo de memoria al no requerir almacenar todo el dataset de entrenamiento.

## 5. Diagrama de Despliegue
```mermaid
graph TD
    Camara[Cámara / RTSP] -->|Video| VideoServer
    VideoServer -->|Frames (Socket)| TestingServer
    TrainingClient -->|Dataset (Socket)| TrainingServer
    TrainingServer -->|Modelo (Socket)| TestingServer
    TestingServer -->|Alertas (Socket)| VigilanteClient
```

## 6. Conclusiones
- Se logró una arquitectura totalmente desacoplada y distribuida.
- La implementación de XGBoost permite un rendimiento apto para producción.
- El uso de Sockets puros permite un control total sobre el flujo de datos y cumple con las restricciones del proyecto.
- El sistema es escalable, permitiendo múltiples cámaras o clientes vigilantes.
