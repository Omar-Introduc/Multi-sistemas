# Manual de Pruebas y Ejecución (Actualizado)

Este documento describe los pasos para ejecutar el sistema con **Inteligencia Real (HOG+KNN)** y **Entrenamiento Distribuido**.

## Requisitos Previos
- Python 3.8+
- Librerías: `opencv-python`, `numpy`
- Dataset de imágenes (carpeta con subcarpetas por clase).

## Orden de Ejecución

### 1. Iniciar el Worker Server (Nodo de Procesamiento)
Este nodo realizará el cálculo pesado (HOG) de las imágenes que le envíe el Master.
```bash
cd src/training
python worker_server.py 6000
```
*Salida esperada:* `Server listening on 0.0.0.0:6000`

### 2. Iniciar el Training Server (Master)
Este servidor orquesta el entrenamiento y distribuye la carga.
```bash
cd src/training
python training_server.py
```
*Salida esperada:* `Server listening on 0.0.0.0:5002`

### 3. Entrenar con Imágenes Reales
Ejecuta el cliente de entrenamiento apuntando a tu carpeta de imágenes.
```bash
cd src/training
python train_client.py "C:/Ruta/A/Tu/Dataset"
```
*Estructura del Dataset:*
```
Dataset/
  ├── Perro/
  │   ├── img1.jpg
  │   └── img2.jpg
  └── Auto/
      ├── img1.jpg
      └── img2.jpg
```
*Salida esperada:* `Distributing X samples to 1 workers...` -> `Aggregation complete` -> `TRAIN_COMPLETE`.

### 4. Iniciar Video Server y Testing Server
Igual que antes:
```bash
# Terminal 3
cd src/video_server
python video_server.py 0

# Terminal 4
cd src/testing
python testing_server.py
```

### 5. Iniciar Vigilante
```bash
# Terminal 5
cd src/monitoring
python vigilante_client.py
```

## Verificación de Inteligencia
1.  Apunta la cámara a un objeto que hayas entrenado (ej. una foto de un perro si entrenaste con perros).
2.  El `Testing Server` debería imprimir: `Frame X: Detected Perro`.
3.  El `Vigilante` debería mostrar la alerta con la foto.

## Solución de Problemas
- **Worker no conecta:** Verifica que el puerto 6000 esté libre.
- **Predicciones "Unknown":** El algoritmo HOG+KNN requiere buenas imágenes de entrenamiento. Si las imágenes son muy diferentes a lo que ve la cámara (iluminación, ángulo), puede fallar. Intenta entrenar con fotos tomadas con la misma cámara.
