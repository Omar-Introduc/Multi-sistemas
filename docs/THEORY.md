# Teoría del Modelo de IA

## Introducción

Este documento describe el componente de Inteligencia Artificial utilizado en el sistema de vigilancia distribuida. El objetivo del modelo es clasificar objetos detectados en las transmisiones de video en tiempo real.

## Selección del Modelo: XGBoost

El modelo principal seleccionado para este sistema es **XGBoost (Extreme Gradient Boosting)**.

### ¿Por qué XGBoost?

Anteriormente, el sistema utilizaba un clasificador K-Nearest Neighbors (KNN). Sin embargo, se migró a XGBoost por las siguientes razones:

1.  **Rendimiento en Inferencia**: Una vez entrenado, XGBoost es extremadamente rápido para predecir, lo cual es crucial para un sistema de vigilancia en tiempo real que procesa múltiples frames por segundo. KNN, por el contrario, requiere buscar en todo el dataset de entrenamiento para cada predicción (Lazy Learning), lo cual se vuelve lento a medida que crece el dataset.
2.  **Precisión**: XGBoost es un algoritmo de ensamble basado en árboles de decisión que captura relaciones no lineales complejas mejor que un simple KNN basado en distancia euclidiana.
3.  **Manejo de Features**: XGBoost es robusto al manejo de características crudas de píxeles, aunque se beneficia del preprocesamiento.

## Preprocesamiento de Datos

Antes de alimentar las imágenes al modelo, se realiza el siguiente preprocesamiento:

1.  **Redimensionamiento**: Las imágenes de entrada (frames de video o recortes de objetos) se redimensionan a una resolución fija de **32x32 píxeles**. Esto estandariza la entrada y reduce la dimensionalidad.
2.  **Aplanamiento (Flattening)**: La imagen 2D (o 3D con canales de color) se convierte en un vector unidimensional (array 1D).
3.  **Normalización (Implícita)**: Los valores de píxeles (0-255) se utilizan como características numéricas.

## Resultados Oficiales

Basado en las pruebas realizadas con el conjunto de datos sintético de validación (Círculos, Cuadrados, Triángulos), el modelo ha demostrado un rendimiento excepcional.

**Resultados de la prueba de validación (`verify_xgboost.py`):**

*   **Precisión (Accuracy)**: 100.00%
*   **Muestras de Entrenamiento**: 240 imágenes
*   **Muestras de Test**: 60 imágenes
*   **Clases**: circle, square, triangle

> Nota: Los resultados perfectos (100%) se deben a la naturaleza sintética y controlada del dataset de prueba. En escenarios del mundo real con ruido de cámara e iluminación variable, se espera una precisión menor pero superior a la de modelos simples como KNN.

## Flujo de Entrenamiento

1.  El **Servidor de Entrenamiento** recibe imágenes etiquetadas de los clientes.
2.  Las imágenes se acumulan en memoria/disco.
3.  Se invoca el proceso de entrenamiento (`model.fit`).
4.  El modelo entrenado se serializa (formato JSON de XGBoost + mapa de etiquetas en Pickle) y se guarda en disco.
5.  El **Servidor de Testeo** carga este modelo para realizar inferencias.
