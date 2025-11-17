# Sprint 3: El Prototipo de Combate (Pilares 1 y 5)

**Objetivo:** Probar la transición de la historia al combate. No se construye el combate real, solo el flujo de estados y la gestión de la UI, sentando las bases para el sistema de combate del Sprint 4.

---

### **Issue S3I1: Tipos de Evento (Polimorfismo)**

**Historia de Usuario:** Como desarrollador, quiero que el sistema de eventos pueda manejar diferentes tipos (historia vs. combate), para poder expandir el juego fácilmente.

**Descripción Técnica Detallada:**

*   **Objetivo:** Refactorizar `EventoDeJuego` para que sea una clase base que permita diferentes tipos de eventos, como historia y combate, utilizando herencia.
*   **Archivos:**
    *   `Assets/Scripts/Data/Eventos/EventoDeJuego.cs` (Clase base)
    *   `Assets/Scripts/Data/Eventos/EventoDeHistoria.cs` (Clase hija)
    *   `Assets/Scripts/Data/Eventos/EventoDeCombate.cs` (Clase hija)
*   **Refactorización de `EventoDeJuego.cs`:**
    *   **Tipo:** Seguirá siendo un `ScriptableObject`, pero ahora funcionará como una clase base. No es necesario que sea `abstract` para que podamos tener eventos genéricos si es necesario, pero su propósito principal es ser heredada.
    *   **Contenido:** Se mantendrá simple. Podemos mover el contenido específico de la historia a su clase hija.
        ```csharp
        // EventoDeJuego.cs
        using UnityEngine;

        // La clase base es muy simple, actúa como un marcador de tipo.
        public class EventoDeJuego : ScriptableObject
        {
            [Header("Info del Evento")]
            public string idDesarrollador = "Escribir un ID único";
        }
        ```
*   **Implementación de `EventoDeHistoria.cs`:**
    *   **Tipo:** `ScriptableObject` que hereda de `EventoDeJuego`.
    *   **Propósito:** Contendrá toda la lógica que antes estaba en `EventoDeJuego`.
    *   **Campos:** `textoDeHistoria` y `opciones`.
    *   **Sugerencia de Implementación:**
        ```csharp
        // EventoDeHistoria.cs
        using UnityEngine;
        using System.Collections.Generic;

        [CreateAssetMenu(fileName = "Nuevo Evento de Historia", menuName = "Juego/Eventos/Evento de Historia")]
        public class EventoDeHistoria : EventoDeJuego
        {
            [TextArea(10, 14)]
            public string textoDeHistoria;
            public List<OpcionDeJuego> opciones = new List<OpcionDeJuego>();
        }
        ```
*   **Implementación de `EventoDeCombate.cs`:**
    *   **Tipo:** `ScriptableObject` que hereda de `EventoDeJuego`.
    *   **Propósito:** Define un encuentro de combate, especificando los enemigos y los posibles resultados (victoria/derrota).
    *   **Campos:**
        *   `public List<EnemigoData> enemigos;` (Aunque `EnemigoData` se define en Sprint 4, podemos usar un placeholder o un simple `string` por ahora).
        *   `public EventoDeJuego eventoVictoria;` (El evento a cargar si el jugador gana).
        *   `public EventoDeJuego eventoDerrota;` (El evento a cargar si el jugador pierde).
    *   **Sugerencia de Implementación:**
        ```csharp
        // EventoDeCombate.cs
        using UnityEngine;
        using System.Collections.Generic;

        [CreateAssetMenu(fileName = "Nuevo Evento de Combate", menuName = "Juego/Eventos/Evento de Combate")]
        public class EventoDeCombate : EventoDeJuego
        {
            [Header("Configuración de Combate")]
            // Por ahora, una lista de strings para saber contra qué se pelea.
            public List<string> nombresEnemigos;

            [Header("Resultados")]
            public EventoDeJuego eventoVictoria;
            public EventoDeJuego eventoDerrota;
        }
        ```
*   **Acción Requerida:** Tras crear estos scripts, los `EventoDeJuego` existentes en el proyecto deben ser actualizados. El editor de Unity debería permitir cambiar el script de los assets a `EventoDeHistoria` para conservar los datos.

---

### **Issue S3I2: Gestor de Estados del Juego (UI)**

**Historia de Usuario:** Como jugador, quiero que la UI cambie claramente entre el modo 'Historia' y el modo 'Combate', para no confundirme sobre qué está pasando.

**Descripción Técnica Detallada:**

*   **Archivo:** `Assets/Scripts/UI/UIManager.cs`
*   **Tipo:** `MonoBehaviour` Singleton.
*   **Propósito:** Centralizar el control de la visibilidad de los diferentes paneles de la UI para reflejar el estado actual del juego (ej. explorando la historia vs. en combate).
*   **Campos:**
    *   `public static UIManager Instance { get; private set; }`
    *   `public GameObject panelHistoria;`
    *   `public GameObject panelCombate;`
    //  `public GameObject panelMapa;` (Ejemplo futuro)
    //  `public GameObject panelInventario;` (Ejemplo futuro)
*   **`enum GameState`:**
    *   `public enum GameUIState { Historia, Combate, Mapa, Inventario }`
*   **Métodos:**
    *   `void Awake()`: Implementación del Singleton.
    *   `void Start()`: Configurar el estado inicial. `SwitchState(GameUIState.Historia);`
    *   `public void SwitchState(GameUIState newState)`:
        *   **Lógica:** Oculta todos los paneles y luego activa solo el correspondiente al `newState`.
        ```csharp
        panelHistoria.SetActive(false);
        panelCombate.SetActive(false);

        switch (newState)
        {
            case GameUIState.Historia:
                panelHistoria.SetActive(true);
                break;
            case GameUIState.Combate:
                panelCombate.SetActive(true);
                break;
            // Otros casos...
        }
        ```
*   **Alternativa a `SetActive`:** Usar `CanvasGroup` en cada panel. Controlar `alpha` (para fade in/out), `interactable` y `blocksRaycasts` ofrece más flexibilidad y evita problemas con componentes que se desactivan.

---

### **Issue S3I3: Prototipo de "Combate Falso"**

**Historia de Usuario:** Como desarrollador, quiero una pantalla de combate de prueba con botones para "Ganar" o "Perder", para poder probar el flujo de transición sin necesidad de un sistema de combate completo.

**Descripción Técnica Detallada:**

*   **Escena:** `Assets/Scenes/GameScene.unity`
*   **Jerarquía de Objetos (dentro del `Canvas`):**
    *   `Panel_Combate` (GameObject vacío, desactivado por defecto)
        *   `Imagen_Fondo` (Opcional)
        *   `Texto_Titulo (TextMeshProUGUI)`: Con el texto "¡COMBATE!".
        *   `Boton_Ganar (Button)`
            *   `Texto_Boton (TextMeshProUGUI)`: Con el texto "Ganar (Prueba)".
        *   `Boton_Perder (Button)` (Opcional, para pruebas)
            *   `Texto_Boton (TextMeshProUGUI)`: Con el texto "Perder (Prueba)".
*   **Configuración:**
    1.  Crear este panel y asegurarse de que está desactivado por defecto.
    2.  Asignarlo al campo `panelCombate` del `UIManager`.
    3.  El `onClick` de los botones se conectará con el `GameManager`. En el Inspector del botón:
        *   Arrastrar el `GameObject` del `GameManager`.
        *   Seleccionar la función `GameManager.EndCombat(bool)`.
        *   Para `Boton_Ganar`, marcar el checkbox del parámetro booleano (`true`).
        *   Para `Boton_Perder`, dejar el checkbox sin marcar (`false`).

---

### **Issue S3I4: Flujo de Transición de Combate**

**Historia de Usuario:** Como jugador, quiero que un evento de historia me lleve a una pantalla de combate y, al terminar, me devuelva a la historia, para que el flujo del juego sea fluido.

**Descripción Técnica Detallada:**

*   **Archivo a Modificar:** `Assets/Scripts/Core/GameManager.cs`
*   **Objetivo:** Modificar el `GameManager` para que pueda interpretar los diferentes tipos de evento y delegar el cambio de UI al `UIManager`.
*   **Modificaciones en `GameManager.cs`:**
    *   **Método `CargarEvento(EventoDeJuego nuevoEvento)`:**
        *   Esta es la modificación clave. Debe detectar el tipo de evento y actuar en consecuencia.
        ```csharp
        public void CargarEvento(EventoDeJuego nuevoEvento)
        {
            if (nuevoEvento == null) return;
            eventoActual = nuevoEvento;

            // Type Pattern Matching (C# 7.0+)
            switch (eventoActual)
            {
                case EventoDeHistoria eh:
                    UIManager.Instance.SwitchState(UIManager.GameUIState.Historia);
                    // Lógica para mostrar texto y opciones (ya existente)
                    ActualizarUIHistoria(eh);
                    break;
                case EventoDeCombate ec:
                    UIManager.Instance.SwitchState(UIManager.GameUIState.Combate);
                    // Lógica para iniciar el combate (en S4 será más complejo)
                    // Por ahora, solo se muestra la UI de combate falso.
                    break;
                default:
                    Debug.LogError($"Tipo de evento no reconocido: {eventoActual.GetType()}");
                    break;
            }
        }
        ```
        *   Será necesario refactorizar la lógica de carga de historia a un nuevo método `ActualizarUIHistoria(EventoDeHistoria evento)` para mantener `CargarEvento` limpio.
    *   **Nuevo método `public void EndCombat(bool playerWon)`:**
        *   Este método será llamado por los botones de la UI de combate falso.
        *   **Lógica:**
            1.  Asegurarse de que el `eventoActual` es un `EventoDeCombate`.
            2.  Cargar el evento de victoria o derrota correspondiente.
            ```csharp
            public void EndCombat(bool playerWon)
            {
                if (eventoActual is EventoDeCombate ec)
                {
                    if (playerWon)
                    {
                        CargarEvento(ec.eventoVictoria);
                    }
                    else
                    {
                        CargarEvento(ec.eventoDerrota);
                    }
                }
                else
                {
                    Debug.LogWarning("EndCombat llamado fuera de un evento de combate.");
                }
            }
            ```
*   **Prueba Final del Sprint:**
    1.  Crear un `EventoDeHistoria` que tenga una opción que lleve a un `EventoDeCombate`.
    2.  Configurar el `EventoDeCombate` con un `eventoVictoria` y un `eventoDerrota` (que pueden ser otros `EventoDeHistoria`).
    3.  Darle a "Play".
    4.  Navegar hasta el evento de combate.
    5.  Verificar que la UI cambia de `panelHistoria` a `panelCombate`.
    6.  Hacer clic en "Ganar (Prueba)".
    7.  Verificar que la UI vuelve a ser la de historia y que se ha cargado el `eventoVictoria` correcto.
