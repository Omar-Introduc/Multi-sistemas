# Explicación Profunda: Entrenamiento Distribuido y Reconocimiento de Objetos

## 1. Abordaje del Reconocimiento de Objetos Generales
Para reconocer objetos genéricos (Perros, Gatos, Autos) sin usar Frameworks pesados (como TensorFlow/PyTorch) y manteniéndonos en el ámbito de "Sistemas Distribuidos", utilizaremos un enfoque clásico de Visión Computacional: **Extracción de Características + Clasificador**.

### Algoritmo Propuesto: HOG + KNN
1.  **HOG (Histogram of Oriented Gradients):** Es un algoritmo que "resume" la forma de un objeto basándose en la dirección de los bordes. Es excelente para detectar formas rígidas o semi-rígidas (personas, autos).
2.  **KNN (K-Nearest Neighbors):** Es un clasificador simple. Guarda "ejemplos" (vectores de características) y cuando llega una imagen nueva, busca a los "vecinos" más cercanos matemáticamente.

**¿Por qué este enfoque?**
- **Computacionalmente Intenso:** Calcular HOG requiere CPU, lo cual justifica el uso de múltiples nodos (distribución).
- **Sin "Caja Negra":** Podemos implementar la lógica de distribución manualmente.

---

## 2. Arquitectura de Entrenamiento Distribuido (Master-Worker)
Actualmente, el sistema tiene un `Training Server` que procesa todo. Para cumplir con el requisito de "carga de trabajo distribuida entre nodos", debemos refactorizar la arquitectura a un modelo **Master-Worker**.

### El Problema de la Concurrencia vs. Distribución
- **Concurrencia (Actual):** El servidor usa hilos (`threads`) para atender a varios clientes a la vez. Si 3 clientes envían datos, el servidor los atiende "al mismo tiempo" (Time Slicing), pero todo corre en la **misma máquina/CPU**.
- **Distribución (Objetivo):** Queremos que si llegan 1000 imágenes, el trabajo pesado se divida entre **varias máquinas (Nodos)**.

### Nueva Arquitectura Propuesta
Imagina que tenemos 1 **Training Master** y 2 **Training Workers**.

#### Flujo de Datos:
1.  **Recepción:** El Cliente envía un Dataset (ej. 100 fotos de "Perro") al **Training Master**.
2.  **Particionamiento (Sharding):** El Master divide el trabajo.
    - 50 fotos para el **Worker A**.
    - 50 fotos para el **Worker B**.
3.  **Distribución:** El Master envía las fotos a los Workers vía Sockets.
4.  **Procesamiento Paralelo (Map):**
    - **Worker A** calcula el HOG de sus 50 fotos.
    - **Worker B** calcula el HOG de sus 50 fotos.
    - *Esto ocurre simultáneamente en procesos o máquinas distintas.*
5.  **Recolección (Reduce):** Los Workers devuelven los **Vectores de Características** al Master.
6.  **Agregación:** El Master junta todos los vectores y guarda el Modelo Final (`model.pkl`).

---

## 3. ¿Cómo se "Promedia" o Entrena?
En el caso de **KNN**, el "entrenamiento" es simplemente almacenar los vectores de características etiquetados.
- **Worker A** devuelve: `[(Vector1, "Perro"), (Vector2, "Perro")...]`
- **Worker B** devuelve: `[(Vector51, "Perro"), (Vector52, "Perro")...]`
- **Master** concatena: `Lista_Final = Lista_A + Lista_B`

Si usáramos **Redes Neuronales** (más complejo), los Workers calcularían "Gradientes" (la dirección en la que debe aprender la red) y el Master promediaría esos gradientes para actualizar los pesos globales (Federated Averaging). Para este proyecto, el enfoque de **Características (HOG/KNN)** es mucho más viable y demostrable.

## 4. Conclusión y Siguientes Pasos
Para llevar el proyecto al nivel "Experto" y cumplir cabalmente con la distribución de carga, deberíamos:
1.  Crear el componente **Worker**.
2.  Modificar el **Training Server** para que actúe como **Master** (repartidor de tareas).
3.  Implementar **HOG** real en lugar del mock.
