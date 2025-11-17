# Sprint 6: El Meta-Juego y Contenido (Pilar 6)

**Objetivo:** Construir el bucle exterior (la progresión entre partidas), asegurar que el progreso persista, y establecer un flujo de trabajo claro para empezar a añadir el contenido real del juego a gran escala.

---

### **Issue S6I1: Sistema de Moneda Persistente ("Ecos")**

**Historia de Usuario:** Como jugador, quiero ganar una 'moneda persistente' (Ecos) en cada partida, para sentir que progresé algo incluso si muero.

**Descripción Técnica Detallada:**

*   **Objetivo:** Diseñar e implementar la "meta-moneda" que el jugador conserva después de una "Run" para comprar mejoras permanentes.
*   **Archivo Principal:** `Assets/Scripts/Core/MetaProgressionManager.cs`
*   **Tipo:** `MonoBehaviour` Singleton que persiste entre escenas (`DontDestroyOnLoad`).
*   **Campos:**
    *   `public static MetaProgressionManager Instance { get; private set; }`
    *   `public int EcosTotales { get; private set; }`
*   **Métodos:**
    *   `void Awake()`: Implementación del Singleton persistente. Al despertar, debe llamar al sistema de guardado para cargar los datos existentes. `LoadProgress();`
    *   `public void AñadirEcos(int cantidad)`:
        *   `if (cantidad > 0) EcosTotales += cantidad;`
        *   `SaveProgress();` // Guardar inmediatamente para asegurar que no se pierdan.
    *   `public bool GastarEcos(int cantidad)`:
        *   `if (EcosTotales >= cantidad)`:
            *   `EcosTotales -= cantidad;`
            *   `SaveProgress();`
            *   `return true;`
        *   `return false;`
*   **Integración (Cálculo de Recompensa):**
    *   En el script que maneja la pantalla de "Game Over" (probablemente `UIManager` o `GameManager`).
    *   **Función `CalcularRecompensaDeEcos()`:**
        *   Se llama cuando la partida termina.
        *   **Lógica de Ejemplo:** `int ecosGanados = (PlayerManager.Instance.Nivel * 10) + (PlayerManager.Instance.Oro / 100);`
        *   Esta lógica puede ser tan compleja como se desee, incluyendo bonificaciones por jefes derrotados, misiones completadas, etc.
    *   Una vez calculados, se llama a: `MetaProgressionManager.Instance.AñadirEcos(ecosGanados);`
    *   La UI de Game Over debe mostrar tanto los ecos ganados en esa run como el total acumulado.

---

### **Issue S6I2: UI de Meta-Progreso (El Refugio)**

**Historia de Usuario:** Como jugador, quiero poder gastar mis 'Ecos' en un menú principal para desbloquear mejoras permanentes (como nuevas clases o más vidas), para que mis futuras partidas sean diferentes y más fáciles.

**Descripción Técnica Detallada:**

*   **Objetivo:** Crear la escena del "Refugio" (menú principal) donde el jugador gasta "Ecos" en mejoras permanentes.
*   **Nueva Escena:** `Assets/Scenes/RefugioScene.unity`.
*   **`MetaUpgradeData.cs`:**
    *   **Archivo:** `Assets/Scripts/Data/Meta/MetaUpgradeData.cs`
    *   **Tipo:** `ScriptableObject`.
    *   **Campos:**
        *   `public string idMejora;` (Un identificador único, ej. "aumentar_vidas_max_1").
        *   `public string nombre;`
        *   `[TextArea] public string descripcion;`
        *   `public int costeEcos;`
        *   `public MetaUpgradeData mejoraRequerida;` (Opcional, para crear árboles de mejoras).
*   **Modificaciones en `MetaProgressionManager.cs`:**
    *   **Nuevo Campo:** `private HashSet<string> mejorasDesbloqueadas = new HashSet<string>();`
    *   **Nuevos Métodos:**
        *   `public bool DesbloquearMejora(MetaUpgradeData mejora)`:
            1.  Comprueba si ya está desbloqueada.
            2.  Comprueba si `mejoraRequerida` está desbloqueada (si no es nula).
            3.  Llama a `GastarEcos(mejora.costeEcos)`.
            4.  Si todo es exitoso, `mejorasDesbloqueadas.Add(mejora.idMejora);` y `SaveProgress();`.
        *   `public bool HaDesbloqueado(string idMejora)`: `return mejorasDesbloqueadas.Contains(idMejora);`
*   **`RefugioUI.cs` (Script para la escena):**
    *   Obtiene la lista de todos los `MetaUpgradeData.asset` del proyecto.
    *   Por cada uno, instancia un prefab de botón en la UI.
    *   El script del botón lee el `MetaUpgradeData` y configura su texto (nombre, coste).
    *   Comprueba con `MetaProgressionManager.Instance.HaDesbloqueado()` si la mejora ya fue comprada (para mostrarla como "Adquirida") o si los requisitos se cumplen (para habilitar o deshabilitar el botón de compra).
*   **Ejemplos de Mejoras:**
    *   "Aumentar Vidas Máximas +1": El `PlayerManager` en su `Start()` comprobaría `MetaProgressionManager.Instance.HaDesbloqueado("aumentar_vidas_max_1")` para ajustar las `VidasMaximas` iniciales.
    *   "Desbloquear Clase: Mago": Habilitaría un nuevo `PlayerStatsData.asset` para elegir al empezar una nueva partida.

---

### **Issue S6I3: Sistema de Guardado/Carga (Persistencia)**

**Historia de Usuario:** Como jugador, quiero que mis desbloqueos y 'Ecos' se guarden automáticamente, para poder cerrar el juego y continuar mi progreso más tarde.

**Descripción Técnica Detallada:**

*   **Objetivo:** Implementar un sistema robusto para guardar y cargar el meta-progreso entre sesiones.
*   **`MetaSaveData.cs`:**
    *   **Archivo:** `Assets/Scripts/Core/MetaSaveData.cs`
    *   **Tipo:** Clase C# normal, serializable. No hereda de nada.
    *   **Campos:** Deben coincidir con lo que se quiere guardar.
        ```csharp
        [System.Serializable]
        public class MetaSaveData
        {
            public int ecosTotales;
            public List<string> idsMejorasDesbloqueadas = new List<string>();
        }
        ```
*   **`SaveSystem.cs`:**
    *   **Archivo:** `Assets/Scripts/Core/SaveSystem.cs`
    *   **Tipo:** Clase estática.
    *   **Lógica:**
        ```csharp
        using UnityEngine;
        using System.IO;

        public static class SaveSystem
        {
            private static string savePath = Path.Combine(Application.persistentDataPath, "meta.json");

            public static void Save(MetaSaveData data)
            {
                string json = JsonUtility.ToJson(data, true); // true para formateo legible
                File.WriteAllText(savePath, json);
            }

            public static MetaSaveData Load()
            {
                if (File.Exists(savePath))
                {
                    string json = File.ReadAllText(savePath);
                    return JsonUtility.FromJson<MetaSaveData>(json);
                }
                return new MetaSaveData(); // Devuelve datos por defecto si no hay guardado.
            }
        }
        ```
*   **Integración Final en `MetaProgressionManager.cs`:**
    *   **Crear los métodos `SaveProgress()` y `LoadProgress()`:**
        ```csharp
        private void SaveProgress()
        {
            MetaSaveData data = new MetaSaveData
            {
                ecosTotales = this.EcosTotales,
                idsMejorasDesbloqueadas = new List<string>(this.mejorasDesbloqueadas)
            };
            SaveSystem.Save(data);
        }

        private void LoadProgress()
        {
            MetaSaveData data = SaveSystem.Load();
            this.EcosTotales = data.ecosTotales;
            this.mejorasDesbloqueadas = new HashSet<string>(data.idsMejorasDesbloqueadas);
        }
        ```

---

### **Issue S6I4: Integración de Contenido (El Juego Real)**

**Historia de Usuario:** Como desarrollador, quiero un flujo de trabajo claro y eficiente para crear y conectar eventos de historia, combate y recompensas, para poder construir el juego a gran escala.

**Descripción Técnica Detallada:**

*   **Objetivo:** Establecer un flujo de trabajo y buenas prácticas para la creación masiva de contenido utilizando los sistemas ya construidos. Esta es una guía para el equipo.
*   **Flujo de Trabajo para Diseñadores:**
    1.  **Planificación Externa:** Diseñar arcos narrativos, árboles de decisiones y encuentros en una herramienta externa (ej. Miro, Trello, Google Sheets). Esto permite tener una visión global antes de crear assets.
    2.  **Creación de Assets Base:**
        *   Crear los `ScriptableObjects` para nuevos enemigos, armas, armaduras y habilidades en sus respectivas carpetas (`Assets/GameData/Enemigos`, etc.).
    3.  **Construcción de la Narrativa en Unity:**
        *   Dentro de `Assets/GameData/Eventos/`, crear carpetas por capítulo o zona (ej. `Capitulo1/BosqueOscuro`).
        *   Crear los `EventoDeHistoria` y `EventoDeCombate` necesarios.
        *   **Nomenclatura:** Usar un prefijo claro. `EH_Bosque_01` (Evento de Historia), `EC_Bosque_01` (Evento de Combate).
        *   **Enlace:** Arrastrar y soltar los assets de eventos en los campos `siguienteEvento` de las opciones para conectar la historia.
    4.  **Implementación de Lógica:**
        *   Usar los `Requisitos` en las opciones para crear ramas condicionales (ej. se requiere el flag "llave_encontrada").
        *   Usar las `Consecuencias` para otorgar recompensas, cambiar stats y establecer flags que afectarán eventos futuros.
    5.  **Pruebas Modulares:** Probar cada arco narrativo de forma aislada. Se puede hacer que el `GameManager` empiece directamente desde un evento específico para no tener que jugar todo el juego cada vez.
*   **Recomendaciones Técnicas:**
    *   **Prefabricación:** Si ciertos patrones de UI o de objetos de juego se repiten, crear prefabs para acelerar el desarrollo.
    *   **Gestión de Escenas:** Mantener la escena de juego principal (`GameScene`) limpia. El contenido específico (eventos, enemigos) se define en los `ScriptableObjects`, no en la escena misma.
    *   **Control de Versiones:** Utilizar `git` o similar y asegurarse de que los archivos `.meta` de Unity se versionen correctamente. Trabajar en ramas separadas para diferentes arcos de contenido.
