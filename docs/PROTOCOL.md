# Protocolo de Comunicación

Este documento define el protocolo de capa de aplicación personalizado utilizado sobre TCP/IP para la comunicación entre los nodos del sistema.

## Estructura del Mensaje

Todos los mensajes intercambiados en el sistema siguen una estructura binaria TLV (Type-Length-Value) simplificada, donde el "Type" está implícito en el contenido JSON.

### Encabezado (Header)
*   **Longitud**: 4 bytes.
*   **Formato**: Entero Big-Endian (`>I` en `struct` de Python).
*   **Contenido**: Indica el tamaño en bytes del cuerpo del mensaje (Payload JSON).

### Cuerpo (Payload)
*   **Formato**: JSON codificado en UTF-8.
*   **Contenido Mínimo**: Debe contener al menos un campo `type` o `action` que identifique el propósito del mensaje.

### Transmisión de Datos Binarios (Imágenes)
Cuando un mensaje incluye datos binarios grandes (como una imagen), el flujo es:
1.  Se envía el **Encabezado** (4 bytes) con el tamaño del JSON de metadatos.
2.  Se envía el **JSON de Metadatos**. Este JSON debe incluir un campo (ej. `image_size`) que indique el tamaño de los datos binarios que siguen.
3.  Se envían los **Datos Binarios** (Raw Bytes) inmediatamente después del JSON.

## Tipos de Mensajes Definidos

### 1. `IMAGE_SEND` (Video Server -> Testing Server)
Enviado por una cámara para procesar un frame.

*   **JSON Payload**:
    ```json
    {
        "type": "image",
        "cam_id": "cam_1",
        "timestamp": 1678888.123,
        "size": <tamaño_imagen_bytes>
    }
    ```
*   **Binary**: `<bytes de la imagen>`

### 2. `DETECTION_EVENT` (Testing Server -> Watchman Client)
Enviado cuando se detecta un objeto.

*   **JSON Payload**:
    ```json
    {
        "type": "detection",
        "label": "Persona",
        "cam_id": "cam_1",
        "timestamp": "2025-11-01 14:00:00",
        "has_image": true,
        "image_size": <tamaño_imagen_bytes>
    }
    ```
*   **Binary**: `<bytes de la imagen>` (Opcional, si `has_image` es true)

### 3. `TRAIN_REQUEST` (Client -> Training Server)
Enviado para iniciar el entrenamiento con un lote de imágenes.

*   **JSON Payload**:
    ```json
    {
        "action": "train",
        "label": "perro",
        "image_size": <tamaño_imagen_bytes>
    }
    ```
*   **Binary**: `<bytes de la imagen>` (Repetido por cada imagen o en un bloque, dependiendo de la implementación específica).

## Manejo de Conexiones
*   Las conexiones son persistentes (Keep-Alive implícito de TCP).
*   El cierre de un socket por un extremo se detecta al recibir 0 bytes o una excepción, procediendo a la limpieza de recursos.
