# Sprint 4: El Combate Real (Pilares 3, 4 y 5)

**Objetivo:** Reemplazar el "combate falso" (de S3I3) por el sistema de combate real que diseñamos, implementando la lógica de ATB (Active Time Battle), las estructuras de datos de entidades y los efectos de estado.

---

### **Issue S4I1: Estructura de Datos (Oponentes y Equipo)**

**Descripción Técnica Detallada:**

*   **Objetivo:** Crear los `ScriptableObjects` que definirán las estadísticas y propiedades de los enemigos y el equipo del jugador.
*   **`EnemigoData.cs`:**
    *   **Archivo:** `Assets/Scripts/Data/Combate/EnemigoData.cs`
    *   **Tipo:** `ScriptableObject`.
    *   **Campos:**
        *   `public string nombre;`
        *   `public Sprite sprite;` (Para la UI de combate).
        *   `public int vidaMaxima;`
        *   `public int ataqueBase;`
        *   `public int defensaBase;`
        *   `public float velocidadBase;` (Float para más granularidad en el llenado de la barra ATB).
        *   `public List<Habilidad> habilidades;` (La `Habilidad` se definirá en S5, por ahora puede ser una lista de strings).
    *   **Sugerencia de Implementación:**
        ```csharp
        // EnemigoData.cs
        using UnityEngine;

        [CreateAssetMenu(fileName = "Nuevo Enemigo", menuName = "Juego/Combate/Enemigo")]
        public class EnemigoData : ScriptableObject
        {
            public string nombre;
            public Sprite sprite;
            public int vidaMaxima = 50;
            public int ataqueBase = 10;
            public int defensaBase = 5;
            public float velocidadBase = 10f;
            // public List<HabilidadData> habilidades;
        }
        ```
*   **`ItemData.cs` (Base para Equipo):**
    *   **Archivo:** `Assets/Scripts/Data/Items/ItemData.cs`
    *   **Tipo:** `ScriptableObject` (clase base).
    *   **Campos:** `public string nombre;`, `public string descripcion;`, `public Sprite icono;`
*   **`ArmaData.cs`:**
    *   **Archivo:** `Assets/Scripts/Data/Items/ArmaData.cs`
    *   **Tipo:** `ScriptableObject`, hereda de `ItemData`.
    *   **Campos Adicionales:** `public int ataqueAdicional;`, `public float velocidadAdicional;`
*   **`ArmaduraData.cs`:**
    *   **Archivo:** `Assets/Scripts/Data/Items/ArmaduraData.cs`
    *   **Tipo:** `ScriptableObject`, hereda de `ItemData`.
    *   **Campos Adicionales:** `public int defensaAdicional;`, `public int vidaAdicional;`
*   **Modificación a `PlayerManager.cs`:**
    *   Añadir campos para el equipo: `public ArmaData armaEquipada;`, `public ArmaduraData armaduraEquipada;`
    *   Añadir propiedades que calculen las estadísticas totales:
        ```csharp
        public int AtaqueTotal => (statsBase.ataque + (armaEquipada != null ? armaEquipada.ataqueAdicional : 0));
        public int DefensaTotal => (statsBase.defensa + (armaduraEquipada != null ? armaduraEquipada.defensaAdicional : 0));
        ```

---

### **Issue S4I2: Lógica del Bucle de Combate (ATB)**

**Descripción Técnica Detallada:**

*   **Archivo Principal:** `Assets/Scripts/Core/CombatManager.cs`
*   **Tipo:** `MonoBehaviour` Singleton.
*   **Clase Auxiliar:** `CombatEntity.cs` (clase C# normal, no `MonoBehaviour`).
    *   **Propósito:** Representa a un participante en el combate (jugador o enemigo) y mantiene su estado en tiempo real.
    *   **Campos:**
        *   `public bool esJugador;`
        *   `public object data;` (Referencia a `PlayerManager` o `EnemigoData`).
        *   `public int vidaActual;`
        *   `public float barraATB; // 0 a 100`
        *   `public int Ataque { get; ... }`, `public int Defensa { get; ... }`, `public float Velocidad { get; ... }` (Propiedades que obtienen los stats del `data`).
*   **`CombatManager.cs` Lógica:**
    *   **Campos:**
        *   `public static CombatManager Instance { get; private set; }`
        *   `private List<CombatEntity> entidadesEnCombate = new List<CombatEntity>();`
        *   `private EventoDeCombate eventoCombateActual;`
        *   `private bool combateActivo = false;`
    *   **Métodos:**
        *   `public void StartCombat(EventoDeCombate evento)`:
            1.  Guarda `evento` en `eventoCombateActual`.
            2.  Limpia la lista `entidadesEnCombate`.
            3.  Crea una `CombatEntity` para el jugador (leyendo de `PlayerManager`).
            4.  Crea una `CombatEntity` para cada `EnemigoData` en `evento.enemigos`.
            5.  `combateActivo = true;`
        *   `void Update()`:
            1.  `if (!combateActivo) return;`
            2.  Itera sobre `entidadesEnCombate`.
            3.  Si la entidad no tiene la barra ATB llena:
                *   `entidad.barraATB += entidad.Velocidad * Time.deltaTime;`
            4.  Si la barra de una entidad se llena (`>= 100`):
                *   `entidad.barraATB = 100;`
                *   Si es un enemigo, llama a `EjecutarTurnoEnemigo(entidad)`.
                *   Si es el jugador, pausa el llenado de barras y activa la UI de acciones del jugador.
        *   `private void EjecutarTurnoEnemigo(CombatEntity enemigo)`:
            1.  Lógica de IA simple: ataca al jugador.
            2.  Calcula el daño (ej. `enemigo.Ataque - jugador.Defensa`).
            3.  Aplica el daño.
            4.  Resetea la barra ATB del enemigo: `enemigo.barraATB = 0;`
            5.  Comprueba si el jugador ha sido derrotado.
        *   `public void EjecutarTurnoJugador(Accion accion, CombatEntity objetivo)`:
            1.  Llamado desde la UI.
            2.  Ejecuta la acción (atacar, usar habilidad).
            3.  Resetea la barra ATB del jugador.
            4.  Comprueba si el objetivo (enemigo) ha sido derrotado.
            5.  Si todos los enemigos están derrotados, termina el combate con victoria.
        *   `private void EndCombat(bool victoria)`:
            1.  `combateActivo = false;`
            2.  Llama a `GameManager.Instance.EndCombat(victoria)`.

---

### **Issue S4I3: Sistema de Estados (Buffs/Debuffs)**

**Descripción Técnica Detallada:**

*   **Archivo Base:** `Assets/Scripts/Data/Combate/StatusEffect.cs`
    *   **Tipo:** `ScriptableObject` (clase base, `abstract`).
    *   **Campos:** `public string nombre;`, `public float duracion;`, `public Sprite icono;`
    *   **Métodos Abstractos:**
        *   `public abstract void OnApply(CombatEntity target);`
        *   `public abstract void OnTick(CombatEntity target);` (Llamado cada segundo, por ejemplo).
        *   `public abstract void OnRemove(CombatEntity target);`
*   **Ejemplos de Implementación:**
    *   `VenenoEffect.cs`: `OnTick` reduce `target.vidaActual`.
    *   `LentoEffect.cs`: `OnApply` modifica un multiplicador de velocidad en `CombatEntity` (ej. `target.modificadorVelocidad = 0.5f;`). `OnRemove` lo resetea a `1f`.
*   **Clase Auxiliar `AppliedStatusEffect`:**
    *   `public StatusEffect effectData;`
    *   `public float tiempoRestante;`
    *   `public CombatEntity portador;`
*   **Modificación a `CombatEntity.cs`:**
    *   Añadir `public List<AppliedStatusEffect> efectosActivos = new List<AppliedStatusEffect>();`
    *   Añadir `public float modificadorVelocidad = 1f;` (y otros para ataque/defensa).
*   **Integración en `CombatManager.cs`:**
    *   En `Update`, añadir un `TickEfectos()` que itera sobre todos los efectos de todas las entidades, llama a `OnTick` y reduce su `tiempoRestante`. Si el tiempo llega a 0, llama a `OnRemove` y elimina el efecto de la lista.

---

### **Issue S4I4: Integración del Combate Real**

**Descripción Técnica Detallada:**

*   **Objetivo:** Reemplazar el `Panel_Combate` falso con una UI funcional conectada al `CombatManager`.
*   **Jerarquía de la UI (`Panel_Combate`):**
    *   `Contenedor_Enemigos` (Horizontal Layout Group)
        *   `Prefab_EnemigoUI` (Instanciado por cada enemigo)
            *   `Imagen_Enemigo`
            *   `BarraVida_Enemigo` (Slider)
            *   `BarraATB_Enemigo` (Slider)
            *   `Contenedor_Efectos` (Iconos de buffs/debuffs)
    *   `Contenedor_Jugador`
        *   `BarraVida_Jugador`
        *   `BarraATB_Jugador`
        *   `Contenedor_Efectos_Jugador`
    *   `Panel_Acciones` (Desactivado hasta que sea el turno del jugador)
        *   `Boton_Atacar`
        *   `Boton_Habilidad`
        *   `Boton_Objeto`
    *   `Panel_SeleccionObjetivo` (Se activa al pulsar "Atacar", por ejemplo)
*   **Flujo de Conexión:**
    1.  **`CombatManager.StartCombat`**: Además de crear las `CombatEntity`, instancia los `Prefab_EnemigoUI` y guarda referencias a todos los elementos de la UI.
    2.  **`CombatManager.Update`**: Actualiza constantemente los `value` de los Sliders (barras de vida y ATB) para reflejar el estado de cada `CombatEntity`.
    3.  **Turno del Jugador**: Cuando `jugador.barraATB >= 100`, el `CombatManager` activa el `Panel_Acciones`.
    4.  **`Boton_Atacar.onClick`**:
        *   Llama a un método en `CombatManager` como `PrepararAtaque()`.
        *   Este método activa un modo de "selección de objetivo", quizás haciendo que los enemigos sean clickeables.
    5.  **Click en Enemigo**:
        *   El script del `EnemigoUI` notifica al `CombatManager` que ha sido seleccionado.
        *   `CombatManager` llama a `EjecutarTurnoJugador(ataque, enemigoSeleccionado)`.
        *   Desactiva el `Panel_Acciones` y reanuda el llenado de barras ATB.
*   **Refactorización de `GameManager` y `CombatManager`:**
    *   El `CombatManager` debe ser completamente autónomo una vez que empieza el combate.
    *   Añadir un evento C# en `CombatManager`: `public static event System.Action<bool> OnCombatFinished;`
    *   En `CombatManager.EndCombat(bool victoria)`, invocar el evento: `OnCombatFinished?.Invoke(victoria);`
    *   En `GameManager`, suscribirse al evento: `CombatManager.OnCombatFinished += HandleCombatFinished;`
    *   El método `HandleCombatFinished(bool victoria)` contendrá la lógica que antes estaba en `EndCombat`, cargando el siguiente evento. Esto desacopla elegantemente los dos sistemas.
