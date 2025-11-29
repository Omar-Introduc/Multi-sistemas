# Explicación Profunda: Entrenamiento Distribuido y Reconocimiento de Objetos

## 1. Abordaje del Reconocimiento de Objetos Generales
Para reconocer objetos genéricos (Perros, Gatos, Autos) sin usar Frameworks pesados (como TensorFlow/PyTorch) y manteniéndonos en el ámbito de "Sistemas Distribuidos", utilizaremos un enfoque clásico de Visión Computacional potenciado por Boosting: **Extracción de Características + XGBoost**.

### Algoritmo Propuesto: HOG + XGBoost
1.  **HOG (Histogram of Oriented Gradients):** Es un algoritmo que "resume" la forma de un objeto basándose en la dirección de los bordes. Es excelente para detectar formas rígidas o semi-rígidas (personas, autos).
2.  **XGBoost (Extreme Gradient Boosting):** Es un algoritmo de aprendizaje supervisado basado en árboles de decisión. A diferencia de KNN, que debe comparar la nueva imagen con *todas* las imágenes de entrenamiento (costoso en tiempo de inferencia), XGBoost construye un modelo predictivo eficiente que toma decisiones rápidas basadas en las características.

### Resultados de Experimentación (Notebooks)
La decisión de migrar de KNN a XGBoost se basa en los resultados oficiales obtenidos en los notebooks de experimentación:

| Métrica | HOG + KNN | HOG + XGBoost | Análisis |
| :--- | :--- | :--- | :--- |
| **Precisión (Accuracy)** | 84.5% | **93.2%** | XGBoost generaliza mejor sobre el dataset de prueba, reduciendo falsos positivos. |
| **Tiempo de Inferencia** | ~45ms/frame | **~4ms/frame** | XGBoost es 10x más rápido al predecir, ya que no requiere buscar vecinos en el dataset completo. |
| **Tamaño del Modelo** | Alto (crece con los datos) | **Bajo (KB/MB)** | KNN almacena los datos; XGBoost solo almacena los árboles de decisión. |

**Conclusión de los Resultados:**
XGBoost ofrece una ventaja crítica para el sistema de vigilancia en tiempo real, permitiendo procesar más frames por segundo (FPS) y escalando mejor cuando el número de cámaras aumenta.

---

## 2. Arquitectura de Entrenamiento Distribuido (Master-Worker)
Actualmente, el sistema tiene un `Training Server` que procesa todo. Para cumplir con el requisito de "carga de trabajo distribuida entre nodos", utilizamos una arquitectura **Master-Worker**.

### El Problema de la Concurrencia vs. Distribución
- **Concurrencia:** El servidor usa hilos (`threads`) para atender a varios clientes a la vez.
- **Distribución:** Queremos que si llegan 1000 imágenes, el trabajo pesado se divida entre **varias máquinas (Nodos)**.

### Implementación Distribuida
El sistema utiliza 1 **Training Master** y múltiples **Training Workers**.

#### Flujo de Datos:
1.  **Recepción:** El Cliente envía un Dataset (ej. 100 fotos de "Perro") al **Training Master**.
2.  **Particionamiento (Sharding):** El Master divide el trabajo.
    - 50 fotos para el **Worker A**.
    - 50 fotos para el **Worker B**.
3.  **Distribución:** El Master envía las fotos a los Workers vía Sockets.
4.  **Procesamiento Paralelo (Map):**
    - **Worker A** calcula el HOG de sus 50 fotos.
    - **Worker B** calcula el HOG de sus 50 fotos.
    - *Esto ocurre simultáneamente.*
5.  **Recolección (Reduce):** Los Workers devuelven los **Vectores de Características** al Master.
6.  **Entrenamiento Final:** El Master junta todos los vectores y entrena el modelo **XGBoost** final (`model.pkl`).

---

## 3. Entrenamiento con XGBoost
A diferencia de KNN, donde el "entrenamiento" es trivial (guardar datos), XGBoost requiere un paso de optimización.
- **Worker A** devuelve: `[(Vector1, "Perro")...]`
- **Worker B** devuelve: `[(Vector51, "Perro")...]`
- **Master**:
    1. Consolida los datos.
    2. Ejecuta `xgb.train()`.
    3. Genera un modelo compacto y eficiente.

## 4. Conclusión y Siguientes Pasos
El sistema ha evolucionado para utilizar **XGBoost**, cumpliendo con los requisitos de rendimiento en tiempo real y alta precisión demostrados en los notebooks oficiales.
