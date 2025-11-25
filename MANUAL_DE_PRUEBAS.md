# Manual de Pruebas y Ejecución

Este documento describe los pasos necesarios para poner en marcha el sistema distribuido y verificar su funcionamiento.

## Requisitos Previos
- Python 3.8+ instalado.
- Librerías necesarias: `opencv-python`, `numpy`.
  ```bash
  pip install opencv-python numpy
  ```
- Una cámara web conectada (ID 0) o un archivo de video.

## Orden de Ejecución

El sistema consta de 4 componentes que deben iniciarse en orden (preferiblemente en terminales separadas).

### 1. Iniciar el Servidor de Entrenamiento (Training Server)
Este servidor espera datos para entrenar el modelo y sirve el modelo entrenado a quien lo pida.

```bash
cd src/training
python training_server.py
```
*Salida esperada:* `Server listening on 0.0.0.0:5002`

### 2. Entrenar el Modelo (Simulación)
Para que el sistema funcione, primero debe existir un modelo "entrenado". Ejecuta este script para enviar datos de prueba al servidor de entrenamiento.

```bash
cd src/training
python train_client.py
```
*Salida esperada:* `Server Response: TRAIN_COMPLETE - {'status': 'success'}`

### 3. Iniciar el Servidor de Video (Video Server)
Este servidor captura video de tu cámara web.

```bash
cd src/video_server
python video_server.py 0
```
*(Si tienes una cámara IP, reemplaza `0` por la URL RTSP)*
*Salida esperada:* `Server listening on 0.0.0.0:5001` y `Video capture started...`

### 4. Iniciar el Servidor de Testeo (Testing Server)
Este es el cerebro que consulta al Video Server y al Training Server.

```bash
cd src/testing
python testing_server.py
```
*Salida esperada:* 
- `Server listening on 0.0.0.0:5003`
- `Model updated successfully` (Si se conectó bien al Training Server)
- Logs de detección: `Frame X: Detected ...`

### 5. Iniciar el Cliente Vigilante (Monitoring)
Para ver las alertas en tiempo real.

```bash
cd src/monitoring
python vigilante_client.py
```
*Salida esperada:* Tabla esperando alertas.

---

## Verificación de Funcionalidad

1. **Entrenamiento:** Verifica que `train_client.py` reciba un `success`. Esto creará un archivo `model.pkl` en `src/training`.
2. **Actualización de Modelo:** Al iniciar `testing_server.py`, debería descargar `model.pkl` y guardarlo localmente como `downloaded_model.pkl`.
3. **Detección:**
    - Si el modelo Mock devuelve "Unknown", no verás alertas.
    - **Nota:** Como el modelo es un Mock (simulado), actualmente devuelve "Unknown" por defecto en `src/training/model.py`.
    - **Para probar alertas:** Puedes modificar temporalmente `src/training/model.py` línea 35 para que devuelva "Person" aleatoriamente, o simplemente observar que los frames se procesan en la consola del Testing Server.

### Tip para Pruebas (Forzar Alertas)
Edita `src/training/model.py`:
```python
    def predict(self, image_data):
        # ...
        import random
        return random.choice(["Person", "Car", "Unknown"])
```
Reinicia `training_server.py`, ejecuta `train_client.py` nuevamente, y luego reinicia `testing_server.py`. ¡Verás alertas llegar al Vigilante!

## Solución de Problemas
- **Connection Refused:** Asegúrate de que los servidores estén corriendo en los puertos por defecto (5001, 5002, 5003).
- **OpenCV Error:** Verifica que tu cámara web no esté siendo usada por otra aplicación (Zoom, Teams, etc.).
