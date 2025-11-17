# Sprint 5: La Progresión (Pilares 4 y 6)

**Objetivo:** Darle sentido al combate y a las decisiones. Implementar el crecimiento del jugador a través de niveles y habilidades, y definir las consecuencias de la derrota a través del sistema de vidas.

---

### **Issue S5I1: Sistema de XP y Niveles**

**Descripción Técnica Detallada:**

*   **Objetivo:** Implementar la lógica para ganar experiencia (XP), subir de nivel y mejorar los atributos del jugador.
*   **Archivos a Modificar:** `PlayerManager.cs`, `CombatManager.cs`, `EnemigoData.cs`, `UIManager.cs`.
*   **Modificaciones en `EnemigoData.cs`:**
    *   Añadir el campo: `public int xpRecompensa = 10;`
*   **Modificaciones en `PlayerManager.cs`:**
    *   **Nuevos Campos:**
        *   `public int Nivel { get; private set; } = 1;`
        *   `public int XpActual { get; private set; } = 0;`
        *   `public int XpSiguienteNivel { get; private set; }`
        *   `public int puntosDeAtributoSinAsignar = 0;`
    *   **Métodos:**
        *   `void Start()`: Al final, llamar a `CalcularXpSiguienteNivel();`.
        *   `private void CalcularXpSiguienteNivel()`: Define la curva de progresión.
            *   Ejemplo: `XpSiguienteNivel = Nivel * Nivel * 100;`
        *   `public void AnadirXp(int cantidad)`:
            1.  `XpActual += cantidad;`
            2.  `while (XpActual >= XpSiguienteNivel)`: (Usa `while` para soportar múltiples subidas de nivel con una gran cantidad de XP).
                *   `XpActual -= XpSiguienteNivel;`
                *   `Nivel++;`
                *   `puntosDeAtributoSinAsignar += 5;` (O la cantidad deseada).
                *   `CalcularXpSiguienteNivel();`
                *   `// Pausar el juego y notificar a la UI.`
                *   `Time.timeScale = 0; // Pausa el juego`
                *   `UIManager.Instance.MostrarPantallaSubirNivel();`
        *   `public void AsignarPuntoDeAtributo(string atributo)`:
            *   Llamado por los botones de la UI de subida de nivel.
            *   Usa un `switch` para incrementar el atributo base correspondiente.
            *   `puntosDeAtributoSinAsignar--;`
*   **Integración con `CombatManager.cs`:**
    *   En `EndCombat(bool victoria)`: si `victoria` es `true`, calcular el total de XP de los enemigos derrotados y llamar a `PlayerManager.Instance.AnadirXp(totalXp);`.
*   **Nueva UI: Pantalla de "Subir de Nivel"**
    *   **Jerarquía:** `Panel_SubirNivel` con texto mostrando "¡Nivel X alcanzado!", puntos disponibles y botones "+" para cada atributo (Encanto, Perspicacia, etc.). Un botón "Confirmar" para cerrar la pantalla.
    *   **`UIManager.cs`**: Añadir la referencia al panel y los métodos `MostrarPantallaSubirNivel()` y `OcultarPantallaSubirNivel()`.
    *   **Flujo:** El botón "Confirmar" llama a `UIManager.Instance.OcultarPantallaSubirNivel()` y reanuda el juego (`Time.timeScale = 1;`).

---

### **Issue S5I2: Sistema de Habilidades**

**Descripción Técnica Detallada:**

*   **Objetivo:** Implementar un sistema flexible para habilidades activas y pasivas.
*   **Archivos Nuevos:**
    *   `Assets/Scripts/Data/Combate/HabilidadData.cs` (`ScriptableObject` base, abstracto).
    *   `Assets/Scripts/Data/Combate/HabilidadActivaData.cs` (Hereda de `HabilidadData`).
    *   `Assets/Scripts/Data/Combate/HabilidadPasivaData.cs` (Hereda de `HabilidadData`).
*   **`HabilidadData.cs` (Base):**
    *   **Campos:** `public string nombre;`, `public string descripcion;`, `public Sprite icono;`
*   **`HabilidadActivaData.cs`:**
    *   **Campos:**
        *   `public int costeMana;`
        *   `public enum TipoObjetivo { UnoMismo, UnEnemigo, TodosEnemigos }`
        *   `public TipoObjetivo objetivo;`
        *   `public float multiplicadorDano = 1.5f;` (Respecto al ataque del lanzador).
        *   `public StatusEffect efectoAAplicar;` (Opcional, para habilidades que aplican estados).
*   **`HabilidadPasivaData.cs`:**
    *   **Campos:**
        *   `public enum TipoModificador { Ataque, Defensa, Velocidad }`
        *   `public TipoModificador atributoModificado;`
        *   `public int valorAdicional;` (Ej. +10 de Ataque).
        *   `public float multiplicador;` (Ej. +10% de Velocidad).
*   **Modificaciones en `PlayerManager.cs`:**
    *   Añadir listas:
        *   `public List<HabilidadActivaData> habilidadesActivas = new List<HabilidadActivaData>();`
        *   `public List<HabilidadPasivaData> habilidadesPasivas = new List<HabilidadPasivaData>();`
    *   Modificar las propiedades de stats para que incluyan los bonus de las pasivas.
*   **Integración en `CombatManager.cs` y UI:**
    *   El `Panel_Acciones` de combate ahora necesita un botón "Habilidad".
    *   Al pulsarlo, se muestra un `Panel_ListaHabilidades` que se popula dinámicamente con las `habilidadesActivas` del jugador.
    *   Al seleccionar una habilidad, se sigue un flujo similar al de atacar, seleccionando un objetivo si es necesario.
    *   `CombatManager` necesita un método `EjecutarHabilidad(HabilidadActivaData habilidad, CombatEntity lanzador, CombatEntity objetivo)`.

---

### **Issue S5I3: Sistema de Vidas y Muerte**

**Descripción Técnica Detallada:**

*   **Objetivo:** Implementar el sistema de "vidas" del pilar 6, donde la muerte en combate no significa el fin de la partida, sino la pérdida de una oportunidad.
*   **Archivo a Modificar:** `PlayerManager.cs`, `CombatManager.cs`.
*   **Modificaciones en `PlayerManager.cs`:**
    *   **Nuevos Campos:**
        *   `public int VidasActuales { get; private set; } = 3;`
        *   `public int VidasMaximas { get; private set; } = 3;`
    *   **Nuevo Método:**
        *   `public void PerderVida()`:
            *   `if (VidasActuales > 0) VidasActuales--;`
*   **Modificaciones en `CombatManager.cs`:**
    *   Cuando la vida de la `CombatEntity` del jugador llega a 0, se debe reescribir la lógica de derrota.
    *   **Nuevo Flujo de Derrota del Jugador:**
        1.  Comprobar `PlayerManager.Instance.VidasActuales`.
        2.  **Si `VidasActuales > 1`:**
            *   Llamar a `PlayerManager.Instance.PerderVida()`.
            *   El combate termina inmediatamente. Considerarlo una "victoria" para el propósito de salir del combate, pero sin recompensas (`EndCombat(true, false)` donde el segundo bool es `otorgarRecompensas`).
            *   El `GameManager` debe recibir esta información y cargar un evento de "respawn" o punto de control, donde se restaura la vida del jugador.
        3.  **Si `VidasActuales <= 1` (será la última vida):**
            *   La próxima derrota es permanente. Cuando la vida llegue a 0, proceder como antes: llamar a `EndCombat(false, false)`.
*   **Consideración de Diseño:** ¿Qué pasa con los enemigos? ¿Se recuperan? Lo más simple es que el combate termina y el jugador "escapa", volviendo a un punto seguro, y los enemigos desaparecen o se resetean.

---

### **Issue S5I4: Pantalla de "Game Over"**

**Descripción Técnica Detallada:**

*   **Objetivo:** Crear la pantalla que se muestra cuando el jugador pierde su última vida, finalizando la "Run".
*   **Archivos:** `GameManager.cs`, `UIManager.cs`.
*   **Nueva UI: Pantalla de "Game Over"**
    *   **Jerarquía:** `Panel_GameOver` (desactivado por defecto).
    *   **Contenido:** Un texto grande ("FIN DE LA PARTIDA"), un resumen de la "Run" (ej. "Nivel alcanzado: X", "Oro conseguido: Y") y un botón "Continuar" o "Volver al Refugio".
*   **Modificaciones en `GameManager.cs`:**
    *   El método `HandleCombatFinished(bool victoria)` (o como se llame el callback de `CombatManager`) debe manejar el caso de la derrota final.
    *   **Lógica:**
        ```csharp
        private void HandleCombatFinished(bool victoria, bool conRecompensas)
        {
            if (victoria)
            {
                // ... cargar evento de victoria
            }
            else // Derrota
            {
                // El jugador ya ha perdido su última vida en este punto.
                UIManager.Instance.MostrarPantallaGameOver();
                // Aquí se calcularían y guardarían las meta-monedas (Sprint 6).
            }
        }
        ```
*   **Flujo Final:**
    1.  El jugador muere en combate con su última vida.
    2.  `CombatManager` notifica al `GameManager` de la derrota (`victoria = false`).
    3.  `GameManager` llama a `UIManager` para mostrar la pantalla de Game Over.
    4.  El botón en la pantalla de Game Over se encargará de cargar la escena del menú principal o "Refugio".
