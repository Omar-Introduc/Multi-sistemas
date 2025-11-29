# Planeación del Proyecto

Este documento detalla la estructura y los archivos necesarios para la documentación del sistema de vigilancia y entrenamiento distribuido.

## Documentación Requerida

De acuerdo con la auditoría y los requisitos, se deben crear/actualizar los siguientes archivos:

1.  **README.md**: Visión general del proyecto, requisitos y ejecución (ya existente, pero requiere actualización de enlaces).
2.  **docs/THEORY.md**: Explicación teórica del modelo de IA (XGBoost), justificación y resultados oficiales.
3.  **docs/ARCHITECTURE.md**: Descripción detallada de la arquitectura distribuida (Servidores y Clientes).
4.  **docs/PROTOCOL.md**: Especificación del protocolo de comunicación (Sockets, Headers, Payloads).
5.  **docs/AUDIT.md**: Registro de la auditoría realizada y cumplimiento de requisitos.

## Estado del Modelo Principal

El modelo principal ha sido migrado de **KNN** a **XGBoost** para mejorar la precisión y robustez en la clasificación de características extraídas.

## Próximos Pasos

1.  Generar los documentos listados arriba.
2.  Verificar que el código coincida con la documentación.
