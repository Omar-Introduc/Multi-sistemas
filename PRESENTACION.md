# Presentación del Proyecto: Sistema Distribuido de IA

## Diapositiva 1: Título
**Sistema Distribuido para Entrenamiento y Consumo de IA**
*Curso: Programación Concurrente y Distribuida*
*Integrantes: [Tu Nombre]*

---

## Diapositiva 2: El Problema
- Necesidad de entrenar y consumir modelos de IA de forma escalable.
- Requerimiento de procesar video en tiempo real.
- Restricciones: No usar frameworks de alto nivel (Solo Sockets).

---

## Diapositiva 3: La Solución
- Arquitectura de Microservicios (Nodos).
- Comunicación asíncrona vía TCP/IP Sockets.
- Desacoplamiento de Captura, Entrenamiento y Testeo.

---

## Diapositiva 4: Arquitectura
1. **Video Server:** Captura y streaming de frames.
2. **Training Server:** Gestión de modelos y datasets.
3. **Testing Server:** Inferencia y lógica de negocio.
4. **Vigilante Client:** Monitoreo y alertas.

---

## Diapositiva 5: Detalles Técnicos
- **Lenguaje:** Python.
- **Librerías:** OpenCV (Visión), Socket (Red), Threading (Concurrencia).
- **Protocolo:** JSON sobre TCP con headers de longitud fija.

---

## Diapositiva 6: Demostración
- Flujo completo funcionando: Cámara -> Detección -> Alerta.
- Persistencia de modelos.
- Configuración flexible mediante `config.json`.

---

## Diapositiva 7: Conclusiones
- Sistema robusto y modular.
- Cumplimiento total de los requisitos del curso.
- Base sólida para futuras mejoras (IA real, más nodos).
