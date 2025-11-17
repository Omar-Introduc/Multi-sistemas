# Sprint 1: El Esqueleto Jugable (Pilar 1)

**Objetivo:** Probar el bucle de decisión más básico. Crear el esqueleto del juego para tener una base sólida sobre la cual construir las demás mecánicas.

---

### **Issue S1I1: Estructura de Datos del Evento**

**Historia de Usuario:** Como jugador, quiero que un evento de historia tenga texto y opciones, para poder entender qué está pasando y tomar una decisión.

**Descripción Técnica Detallada:**

*   **Archivo:** `Assets/Scripts/Data/EventoDeJuego.cs`
*   **Tipo:** `ScriptableObject`
*   **Propósito:** Representará un nodo individual en la narrativa del juego. Será un asset de Unity que se puede crear y configurar desde el editor, facilitando la creación de contenido por parte de los diseñadores.
*   **Campos:**
    *   `[TextArea(10, 14)] public string textoDeHistoria;`
        *   **Uso:** Almacenará el texto principal que se le mostrará al jugador cuando este evento esté activo. El atributo `TextArea` mejora la legibilidad y edición en el Inspector de Unity.
        *   **Consideración:** Pensar en el futuro soporte para localización. Podríamos reemplazar `string` por una clave a un archivo de localización. Por ahora, `string` es suficiente.
    *   `public List<OpcionDeJuego> opciones;`
        *   **Uso:** Contendrá una lista de las posibles decisiones que el jugador puede tomar en este evento.
        *   **Implementación:** Debe ser inicializada en el constructor o directamente (`= new List<OpcionDeJuego>();`) para evitar `NullReferenceException`.
*   **Sugerencia de Implementación:**
    ```csharp
    // EventoDeJuego.cs
    using UnityEngine;
    using System.Collections.Generic;

    [CreateAssetMenu(fileName = "Nuevo Evento", menuName = "Juego/Evento de Juego")]
    public class EventoDeJuego : ScriptableObject
    {
        [TextArea(10, 14)]
        public string textoDeHistoria;
        public List<OpcionDeJuego> opciones = new List<OpcionDeJuego>();
    }
    ```

---

### **Issue S1I2: Estructura de Datos de la Opción**

**Historia de Usuario:** Como desarrollador, quiero una estructura de datos dedicada para las opciones, para que cada opción pueda tener su propio texto y un enlace claro al siguiente evento.

**Descripción Técnica Detallada:**

*   **Archivo:** `Assets/Scripts/Data/OpcionDeJuego.cs`
*   **Tipo:** `Clase serializable` (no `MonoBehaviour` ni `ScriptableObject`).
*   **Propósito:** Representará una única elección disponible dentro de un `EventoDeJuego`. Al ser una clase serializable, sus instancias podrán ser editadas directamente en el Inspector de Unity, dentro de la lista de opciones del `EventoDeJuego` que la contiene.
*   **Campos:**
    *   `public string textoDeOpcion;`
        *   **Uso:** El texto que se mostrará en el botón de la UI correspondiente a esta opción.
    *   `public EventoDeJuego siguienteEvento;`
        *   **Uso:** Referencia directa al `EventoDeJuego` que se cargará si el jugador elige esta opción. Esto crea el enlace entre nodos de la historia.
*   **Sugerencia de Implementación:**
    ```csharp
    // OpcionDeJuego.cs
    using UnityEngine;

    [System.Serializable]
    public class OpcionDeJuego
    {
        public string textoDeOpcion;
        public EventoDeJuego siguienteEvento;
    }
    ```
    *   **Nota:** El atributo `[System.Serializable]` es crucial para que Unity pueda mostrar y guardar los datos de esta clase en el Inspector.

---

### **Issue S1I3: Implementación del GameManager (Flujo)**

**Historia de Usuario:** Como jugador, quiero que al hacer clic en una opción, la historia avance al siguiente evento, para que mi decisión tenga un resultado inmediato.

**Descripción Técnica Detallada:**

*   **Archivo:** `Assets/Scripts/Core/GameManager.cs`
*   **Tipo:** `MonoBehaviour` (Singleton).
*   **Propósito:** Será el cerebro del flujo del juego. Gestionará el estado actual de la narrativa, actualizará la UI y procesará las elecciones del jugador.
*   **Campos:**
    *   `public static GameManager Instance { get; private set; }`
        *   **Uso:** Implementación del patrón Singleton para asegurar que solo exista una instancia del GameManager y que sea fácilmente accesible desde otros scripts (ej. los botones de la UI).
    *   `public EventoDeJuego eventoActual;`
        *   **Uso:** Almacena la referencia al `EventoDeJuego` que se está mostrando en este momento.
    *   `public TextMeshProUGUI textoHistoriaUI;`
        *   **Uso:** Referencia al componente de texto de la UI donde se mostrará la historia.
    *   `public List<Button> botonesOpcionUI;`
        *   **Uso:** Referencias a los botones de la UI que representarán las opciones.
*   **Métodos:**
    *   `void Awake()`: Implementación del Singleton.
        ```csharp
        if (Instance == null) {
            Instance = this;
            DontDestroyOnLoad(gameObject);
        } else {
            Destroy(gameObject);
        }
        ```
    *   `void Start()`: Carga el primer evento del juego.
        ```csharp
        CargarEvento(eventoActual);
        ```
    *   `public void CargarEvento(EventoDeJuego nuevoEvento)`:
        *   **Lógica:**
            1.  Asigna `nuevoEvento` a `eventoActual`.
            2.  Actualiza `textoHistoriaUI.text` con `eventoActual.textoDeHistoria`.
            3.  Itera sobre los `botonesOpcionUI`.
            4.  Para cada botón, si hay una opción correspondiente en `eventoActual.opciones`, lo activa, le asigna el texto (`opcion.textoDeOpcion`) y configura su `onClick` listener. Si no hay opción, desactiva el botón.
            *   **Importante:** Limpiar los listeners anteriores antes de añadir uno nuevo para evitar llamadas múltiples (`boton.onClick.RemoveAllListeners();`).
    *   `public void ElegirOpcion(int indiceOpcion)`:
        *   **Lógica:**
            1.  Valida que el índice esté dentro del rango de `eventoActual.opciones`.
            2.  Obtiene la `OpcionDeJuego` seleccionada.
            3.  Si `siguienteEvento` no es nulo, llama a `CargarEvento(opcion.siguienteEvento)`.
            4.  Si es nulo, podría ser el final de una rama (por ahora no hace nada, en el futuro podría mostrar un mensaje de "Continuará...").
*   **Diagrama de Flujo Lógico:**
    `Start` -> `CargarEvento(eventoInicial)` -> `UI Muestra Historia y Opciones` -> `Jugador Clickea Botón` -> `Botón Llama a ElegirOpcion(indice)` -> `GameManager Procesa Elección` -> `CargarEvento(siguienteEvento)` -> (Bucle)

---

### **Issue S1I4: Creación de UI Básica**

**Historia de Usuario:** Como desarrollador, quiero una interfaz de usuario básica con un área de texto y botones, para poder presentar la historia y las opciones al jugador de forma clara.

**Descripción Técnica Detallada:**

*   **Escena:** `Assets/Scenes/GameScene.unity`
*   **Jerarquía de Objetos:**
    *   `Canvas` (Render Mode: Screen Space - Overlay)
        *   `Panel_Historia` (Vertical Layout Group)
            *   `Texto_Historia (TextMeshProUGUI)`: Ocupará la parte superior. Configurado para auto-ajustar el texto.
            *   `Panel_Opciones` (Vertical Layout Group, con padding)
                *   `Boton_Opcion_1 (Button)` con un hijo `Texto_Boton (TextMeshProUGUI)`
                *   `Boton_Opcion_2 (Button)`
                *   `Boton_Opcion_3 (Button)`
                *   `Boton_Opcion_4 (Button)`
    *   `GameManager (GameObject Vacío)`
        *   Con el script `GameManager.cs` adjunto.
*   **Configuración:**
    1.  Importar `TextMeshPro` Essentials si es la primera vez que se usa.
    2.  Arrastrar el componente `Texto_Historia` al campo `textoHistoriaUI` del `GameManager` en el Inspector.
    3.  Arrastrar los 4 botones al campo `botonesOpcionUI` del `GameManager`.
    4.  En cada `Button`, el `onClick` no se configurará en el editor. Se hará dinámicamente desde el código del `GameManager` para mantener la flexibilidad.

---

### **Issue S1I5: Contenido de Prueba (Demo)**

**Historia de Usuario:** Como jugador, quiero poder navegar por una pequeña historia de 3 a 5 pasos, para confirmar que el bucle de juego principal funciona.

**Descripción Técnica Detallada:**

*   **Ubicación:** `Assets/GameData/Eventos/`
*   **Proceso de Creación:**
    1.  Click derecho en la ventana de Proyecto -> `Create` -> `Juego/Evento de Juego`.
    2.  Crear 5 assets de `EventoDeJuego` y nombrarlos descriptivamente.
*   **Ejemplo de Contenido:**
    *   **`E001_Inicio.asset`**
        *   `textoDeHistoria`: "Te encuentras en una encrucijada. Un camino va a la izquierda, hacia un oscuro bosque. El otro va a la derecha, hacia una bulliciosa ciudad."
        *   `opciones`:
            *   `Opcion 1`: `textoDeOpcion`: "Ir a la izquierda.", `siguienteEvento`: (arrastrar `E002_Bosque.asset` aquí)
            *   `Opcion 2`: `textoDeOpcion`: "Ir a la derecha.", `siguienteEvento`: (arrastrar `E003_Ciudad.asset` aquí)
    *   **`E002_Bosque.asset`**
        *   `textoDeHistoria`: "El bosque es silencioso y un poco aterrador. No parece haber nada de interés."
        *   `opciones`:
            *   `Opcion 1`: `textoDeOpcion`: "Volver a la encrucijada.", `siguienteEvento`: (arrastrar `E001_Inicio.asset` aquí)
    *   **`E003_Ciudad.asset`**
        *   `textoDeHistoria`: "La ciudad es vibrante, pero un guardia te detiene. '¿A dónde crees que vas?'"
        *   `opciones`:
            *   `Opcion 1`: `textoDeOpcion`: "Intentar sobornarlo.", `siguienteEvento`: (arrastrar `E004_Soborno.asset` aquí)
            *   `Opcion 2`: `textoDeOpcion`: "Dar media vuelta.", `siguienteEvento`: (arrastrar `E001_Inicio.asset` aquí)
    *   **`E004_Soborno.asset`**
        *   `textoDeHistoria`: "El guardia se ríe y se guarda tu oro. 'Sigue adelante', dice."
        *   `opciones`:
            *   `Opcion 1`: `textoDeOpcion`: "Explorar la ciudad.", `siguienteEvento`: (arrastrar `E005_Explorar.asset` aquí)
    *   **`E005_Explorar.asset`**
        *   `textoDeHistoria`: "Encuentras un tesoro. ¡Has ganado! (Fin de la demo)"
        *   `opciones`: (Lista vacía o con una opción para reiniciar)
*   **Prueba Final del Sprint:**
    1.  Asignar `E001_Inicio.asset` al campo `eventoActual` del `GameManager` en la escena.
    2.  Darle a "Play".
    3.  Verificar que el texto inicial se muestra.
    4.  Verificar que los dos primeros botones están activos con el texto correcto.
    5.  Hacer clic en las opciones y navegar por el flujo de eventos creado para asegurar que todos los enlaces funcionan como se espera.
