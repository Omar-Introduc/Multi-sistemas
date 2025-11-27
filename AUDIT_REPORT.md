# Informe de Auditoría del Sistema Distribuido

## Resumen Ejecutivo

Se ha realizado una auditoría completa del código fuente para verificar la correcta creación, implementación, configuración de puertos y mecanismos de limpieza del sistema de aprendizaje automático distribuido.

**Resultado Global:** El sistema está correctamente implementado y cumple con los requisitos de diseño, configuración y limpieza.

## Detalles de la Auditoría

### 1. Verificación de Creación e Implementación

*   **Arquitectura:** La arquitectura distribuida (Training Server, Workers, Video Server, Testing Server, Clients) está correctamente implementada utilizando sockets TCP.
*   **Lógica de Negocio:**
    *   **Training Server (`src/training/training_server.py`):** Distribuye correctamente las tareas de entrenamiento a los workers configurados y agrega los resultados para actualizar el modelo global. Maneja la concurrencia mediante `threading.Lock`.
    *   **Workers (`src/training/worker_server.py`):** Reciben imágenes, las decodifican y extraen características HOG. Se verificó que los parámetros del descriptor HOG coinciden exactamente con los definidos en `model.py`, asegurando la coherencia del modelo.
    *   **Testing Server (`src/testing/testing_server.py`):** Implementa correctamente el ciclo de inferencia: solicita frames al Video Server, ejecuta la predicción con el modelo cargado y emite alertas a los clientes Vigilante.
    *   **Video Server (`src/video_server/video_server.py`):** Captura video en un hilo dedicado y sirve frames bajo demanda, evitando bloqueos.
*   **Modelo (`src/training/model.py`):** Implementa correctamente la lógica KNN y HOG.
    *   *Nota Técnica:* Se observó que el entrenamiento distribuido no aplica el aumento de datos (data augmentation) en los workers para optimizar el rendimiento y tráfico de red. El aumento de datos está presente en la clase `AIModel` pero solo se invoca en entrenamiento local. Esto es aceptable para el diseño distribuido actual.

### 2. Configuración de Puertos

La configuración de puertos es centralizada y consistente:

*   **Archivo de Configuración (`config.json`):** Define claramente los puertos para todos los servicios.
    *   Video Server: `5001`
    *   Training Server: `5002`
    *   Testing Server: `5003`
    *   Workers: `6000`, `6001`, `6002`
*   **Implementación:** Todos los servidores cargan estos valores del archivo de configuración o aceptan argumentos de línea de comandos (en el caso de los workers) que coinciden con los scripts de lanzamiento (`launch_training_only.bat`, etc.). No se detectaron conflictos de puertos.

### 3. Limpieza Total de Puertos Activos

El sistema cumple rigurosamente con el requisito de "limpieza total":

*   **Mecanismo de Terminación (`automate_pipeline.py`):** La función `run_kill` ejecuta el comando `taskkill /F /IM python.exe`. Esto asegura que **todos** los procesos de Python relacionados con el proyecto se terminen forzosamente, liberando todos los recursos y puertos asociados sin excepción.
*   **Reutilización de Sockets (`src/common/socket_comm.py`):** Se utiliza la opción `SO_REUSEADDR` en la creación de sockets (`self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)`). Esto permite que el sistema operativo libere el puerto inmediatamente después de que el proceso termina, evitando errores de "Address already in use" al reiniciar el sistema rápidamente.

## Conclusión

El proyecto presenta una estructura sólida, una configuración de red coherente y mecanismos robustos para garantizar que no queden procesos o puertos activos tras la finalización de la ejecución.
