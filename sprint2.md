# Sprint 2: El Cerebro (Pilares 2 y 4)

**Objetivo:** Hacer que las decisiones importen. Integrar los atributos del jugador y la memoria del mundo para que las elecciones tengan requisitos y consecuencias tangibles.

---

### **Issue S2I1: Sistema de Atributos del Jugador**

**Descripción Técnica Detallada:**

*   **Archivos:**
    *   `Assets/Scripts/Player/PlayerStatsData.cs` (`ScriptableObject`)
    *   `Assets/Scripts/Player/PlayerManager.cs` (`MonoBehaviour` Singleton)
*   **Propósito:** Se utilizará un enfoque híbrido. `PlayerStatsData` definirá la estructura y los valores *iniciales* de los atributos, permitiendo crear diferentes "clases" o "arquetipos" como assets. `PlayerManager` será un Singleton que mantendrá el estado *actual* de los atributos durante una partida.
*   **`PlayerStatsData.cs`:**
    *   **Tipo:** `ScriptableObject`
    *   **Campos:**
        *   `public int encantoInicial;`
        *   `public int perspicaciaInicial;`
        *   `public int vidaMaximaInicial;`
        *   `public int oroInicial;`
    *   **Sugerencia de Implementación:**
        ```csharp
        // PlayerStatsData.cs
        using UnityEngine;

        [CreateAssetMenu(fileName = "Nuevas Stats Jugador", menuName = "Juego/Stats de Jugador")]
        public class PlayerStatsData : ScriptableObject
        {
            public int encanto = 5;
            public int perspicacia = 5;
            public int vidaMaxima = 100;
            public int oro = 10;
        }
        ```
*   **`PlayerManager.cs`:**
    *   **Tipo:** `MonoBehaviour` Singleton.
    *   **Campos:**
        *   `public static PlayerManager Instance { get; private set; }`
        *   `public PlayerStatsData statsBase;` (Para asignar el arquetipo inicial en el editor).
        *   `// Atributos en tiempo de ejecución`
        *   `public int Encanto { get; private set; }`
        *   `public int Perspicacia { get; private set; }`
        *   `public int VidaActual { get; private set; }`
        *   `public int VidaMaxima { get; private set; }`
        *   `public int Oro { get; private set; }`
    *   **Métodos:**
        *   `void Awake()`: Implementación del Singleton e inicialización de stats.
            ```csharp
            if (Instance == null) { Instance = this; DontDestroyOnLoad(gameObject); }
            else { Destroy(gameObject); return; }

            if (statsBase != null)
            {
                Encanto = statsBase.encanto;
                Perspicacia = statsBase.perspicacia;
                VidaMaxima = statsBase.vidaMaxima;
                VidaActual = VidaMaxima;
                Oro = statsBase.oro;
            }
            ```
        *   `public void ModificarOro(int cantidad)`: `Oro += cantidad;`
        *   `public void ModificarEncanto(int cantidad)`: `Encanto += cantidad;`
        *   `(Y así para los demás atributos...)`

---

### **Issue S2I2: Sistema de "Memoria" (Banderas/Misiones)**

**Descripción Técnica Detallada:**

*   **Archivo:** `Assets/Scripts/Core/WorldState.cs`
*   **Tipo:** `MonoBehaviour` Singleton.
*   **Propósito:** Servirá como la memoria central del juego, rastreando eventos clave y el progreso de misiones que persisten a lo largo de la partida.
*   **Campos:**
    *   `public static WorldState Instance { get; private set; }`
    *   `private HashSet<string> flags = new HashSet<string>();`
        *   **Uso:** Un `HashSet` es ideal para las banderas (flags) porque es muy eficiente para comprobar si una bandera existe (`Contains`) y no permite duplicados. Una bandera existe o no existe (ej. "mato_al_lobo").
*   **Métodos:**
    *   `void Awake()`: Implementación del Singleton.
    *   `public void SetFlag(string flag)`: `flags.Add(flag);`
    *   `public void RemoveFlag(string flag)`: `flags.Remove(flag);`
    *   `public bool HasFlag(string flag)`: `return flags.Contains(flag);`
    *   `public void ResetState()`: `flags.Clear();` (Para empezar una nueva partida).
*   **Consideración a Futuro (Misiones):** Para un sistema de misiones más complejo, se podría añadir un `Dictionary<string, QuestStatus> questLog;` donde `QuestStatus` es un `enum` (`NoIniciada`, `EnProgreso`, `Completada`, `Fallida`). Por ahora, el sistema de banderas es suficiente y puede emular misiones simples.

---

### **Issue S2I3: Lógica de Opciones Condicionales**

**Descripción Técnica Detallada:**

*   **Objetivo:** Extender la clase `OpcionDeJuego` para que pueda definir requisitos que el jugador debe cumplir para que la opción sea visible o interactuable.
*   **Archivos a Modificar:** `OpcionDeJuego.cs`, `GameManager.cs`
*   **Nuevo Archivo:** `Assets/Scripts/Data/RequisitoOpcion.cs`
*   **`RequisitoOpcion.cs`:**
    *   **Tipo:** `Clase serializable`.
    *   **Campos:**
        *   `public enum TipoRequisito { Atributo, Flag }`
        *   `public TipoRequisito tipo;`
        *   `public string clave;` (Ej. "Encanto", "mato_al_lobo")
        *   `public int valorRequerido;` (Solo para `Atributo`)
        *   `public bool debeTenerFlag = true;` (Solo para `Flag`)
    *   **Sugerencia de Implementación:**
        ```csharp
        // RequisitoOpcion.cs
        [System.Serializable]
        public class RequisitoOpcion
        {
            public enum TipoRequisito { Atributo, Flag }
            public TipoRequisito tipo;
            public string clave; // "Encanto", "Perspicacia", "Oro", o el nombre del flag

            // Para Atributo
            public int valorMinimo;

            // Para Flag
            public bool debeExistir = true;
        }
        ```
*   **Modificación a `OpcionDeJuego.cs`:**
    *   Añadir el campo: `public List<RequisitoOpcion> requisitos = new List<RequisitoOpcion>();`
*   **Modificación a `GameManager.cs` (método `CargarEvento`)**
    *   La lógica de actualización de botones ahora debe incluir una comprobación de requisitos.
    *   **Diagrama de Flujo Lógico:**
        `Para cada opción en eventoActual.opciones:`
        1.  `bool requisitosCumplidos = ComprobarRequisitos(opcion);`
        2.  `if (requisitosCumplidos)`
            *   `Activar y configurar el botón normalmente.`
            *   `botón.interactable = true;`
        3.  `else`
            *   **Opción A (Ocultar):** `botón.gameObject.SetActive(false);`
            *   **Opción B (Deshabilitar y Mostrar):**
                *   `Activar y configurar el botón.`
                *   `botón.interactable = false;`
                *   `Añadir el texto del requisito al botón:` (ej. `"[Encanto 10] Hablar con el guardia"`) - Esto da mejor feedback al jugador.
    *   **Nuevo método `bool ComprobarRequisitos(OpcionDeJuego opcion)`:**
        *   Itera sobre `opcion.requisitos`.
        *   Usa un `switch` sobre `requisito.tipo`.
        *   **Caso `Atributo`:** Llama a `PlayerManager.Instance` para obtener el valor del atributo y lo compara con `requisito.valorMinimo`. Si no cumple, `return false`.
        *   **Caso `Flag`:** Llama a `WorldState.Instance.HasFlag(requisito.clave)` y lo compara con `requisito.debeExistir`. Si no cumple, `return false`.
        *   Si pasa todos los requisitos, `return true`.

---

### **Issue S2I4: Lógica de Opciones con Consecuencia**

**Descripción Técnica Detallada:**

*   **Objetivo:** Extender `OpcionDeJuego` para que, al ser elegida, pueda modificar el estado del jugador o del mundo.
*   **Archivos a Modificar:** `OpcionDeJuego.cs`, `GameManager.cs`
*   **Nuevo Archivo:** `Assets/Scripts/Data/ConsecuenciaOpcion.cs`
*   **`ConsecuenciaOpcion.cs`:**
    *   **Tipo:** `Clase serializable`.
    *   **Campos:**
        *   `public enum TipoConsecuencia { ModificarAtributo, SetFlag }`
        *   `public TipoConsecuencia tipo;`
        *   `public string clave;` (Ej. "Oro", "robo_al_mercader")
        *   `public int valor;` (Para `ModificarAtributo`, puede ser positivo o negativo)
        *   `public bool setFlag = true;` (Para `SetFlag`)
    *   **Sugerencia de Implementación:**
        ```csharp
        // ConsecuenciaOpcion.cs
        [System.Serializable]
        public class ConsecuenciaOpcion
        {
            public enum TipoConsecuencia { ModificarAtributo, SetFlag }
            public TipoConsecuencia tipo;
            public string clave; // "Oro", "VidaActual", o nombre del flag

            // Para ModificarAtributo
            public int cantidad; // Ej. -10 para restar 10 de oro

            // Para SetFlag
            public bool establecer = true; // true para añadir, false para quitar
        }
        ```
*   **Modificación a `OpcionDeJuego.cs`:**
    *   Añadir el campo: `public List<ConsecuenciaOpcion> consecuencias = new List<ConsecuenciaOpcion>();`
*   **Modificación a `GameManager.cs` (método `ElegirOpcion`)**
    *   Antes de cargar el `siguienteEvento`, se deben procesar las consecuencias.
    *   **Diagrama de Flujo Lógico:**
        `Al elegir una opción:`
        1.  `OpcionDeJuego opcionElegida = eventoActual.opciones[indiceOpcion];`
        2.  `AplicarConsecuencias(opcionElegida);`
        3.  `CargarEvento(opcionElegida.siguienteEvento);`
    *   **Nuevo método `void AplicarConsecuencias(OpcionDeJuego opcion)`:**
        *   Itera sobre `opcion.consecuencias`.
        *   Usa un `switch` sobre `consecuencia.tipo`.
        *   **Caso `ModificarAtributo`:** Llama al método correspondiente en `PlayerManager.Instance` (ej. `PlayerManager.Instance.ModificarOro(consecuencia.cantidad)`).
        *   **Caso `SetFlag`:** Llama a `WorldState.Instance.SetFlag(consecuencia.clave)` o `RemoveFlag` según `consecuencia.establecer`.
*   **Prueba Final del Sprint:**
    1.  Crear un `PlayerStatsData.asset` y asignarlo al `PlayerManager`.
    2.  Modificar el contenido de prueba del Sprint 1.
    3.  Ejemplo: Una opción "Robar al mercader" que requiere `Perspicacia > 8`.
    4.  Si se elige, tiene como consecuencias: `ModificarAtributo("Oro", +50)` y `SetFlag("robo_exitoso")`.
    5.  Crear otro evento posterior cuya opción requiera `HasFlag("robo_exitoso")`.
    6.  Jugar la secuencia y verificar que los requisitos ocultan/deshabilitan opciones y que las consecuencias modifican los stats y flags correctamente.
