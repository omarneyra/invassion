# Hoja de Ruta y Estado del Proyecto: invassion

Este documento registra el progreso riguroso del desarrollo según la metodología y arquitectura establecidas en [FRAMEWORK.md](file:///home/xor/Proyectos/invassion/FRAMEWORK.md) y [GDD.md](file:///home/xor/Proyectos/invassion/GDD.md).

---

## Estado Global del Proyecto: Hito 1 (MVP WebAssembly) Completado al 100%

```mermaid
flowchart LR
	F1["Fase 1: Especificación & GDD"] --> F2["Fase 2: TDD & Lógica Pura"]
	F2 --> F3["Fase 3: Módulos GDScript"]
	F3 --> F4["Fase 4: 3D Greybox & Cámara"]
	F4 --> F5["Fase 5: Input & Raycast"]
	F5 --> F6["Fase 6: Bucle Jugable MVP"]
	F6 --> F7["Fase 7: Build WebAssembly"]

	style F1 fill:#22c55e,stroke:#15803d,color:#ffffff
	style F2 fill:#22c55e,stroke:#15803d,color:#ffffff
	style F3 fill:#22c55e,stroke:#15803d,color:#ffffff
	style F4 fill:#22c55e,stroke:#15803d,color:#ffffff
	style F5 fill:#22c55e,stroke:#15803d,color:#ffffff
	style F6 fill:#22c55e,stroke:#15803d,color:#ffffff
	style F7 fill:#22c55e,stroke:#15803d,color:#ffffff
```

---

## Desglose de Fases y Tareas

### [x] Fase 1: Especificación y Resolución de Inconsistencias (Completada)
- [x] Definición del concepto: Defensa planetaria sobre icosfera 3D (PvZ + Age of Empires).
- [x] Auditoría técnica y resolución de 5 inconsistencias críticas (carriles geodésicos, corrupción en cráteres, alertas hemisferio ciego, escala 162 nodos, umbral de arrastre 6px).
- [x] Documentación aprobada en [GDD.md](file:///home/xor/Proyectos/invassion/GDD.md) y [FRAMEWORK.md](file:///home/xor/Proyectos/invassion/FRAMEWORK.md).

### [x] Fase 2: Lógica Pura y Suite de Unit Tests Inmediata (Completada)
- [x] Módulo geométrico [`logic/icosphere.py`](file:///home/xor/Proyectos/invassion/logic/icosphere.py).
- [x] Módulo territorial [`logic/territory.py`](file:///home/xor/Proyectos/invassion/logic/territory.py).
- [x] Módulo económico [`logic/economy.py`](file:///home/xor/Proyectos/invassion/logic/economy.py).
- [x] Módulo de combate [`logic/combat.py`](file:///home/xor/Proyectos/invassion/logic/combat.py).
- [x] Suite de pruebas automatizadas: **18 unit tests pasando en 0.012 segundos** vía [`run_tests.sh`](file:///home/xor/Proyectos/invassion/run_tests.sh).

### [x] Fase 3: Equivalentes en GDScript para Godot Engine (Completada)
- [x] [`scripts/logic/icosphere.gd`](file:///home/xor/Proyectos/invassion/scripts/logic/icosphere.gd): funciones estáticas puras para grafo icosférico y navegación BFS.
- [x] [`scripts/logic/territory.gd`](file:///home/xor/Proyectos/invassion/scripts/logic/territory.gd): cálculo de dominio territorial, zonas corruptas y victoria/derrota.
- [x] [`scripts/logic/economy.gd`](file:///home/xor/Proyectos/invassion/scripts/logic/economy.gd): acumulación de energía y compras.
- [x] [`scripts/logic/combat.gd`](file:///home/xor/Proyectos/invassion/scripts/logic/combat.gd): disparo de torretas, avance por carriles geodésicos y daño.

### [x] Fase 4: Prototipado Visual 3D (Greybox) y Cámara Orbital (Completada)
- [x] [`scenes/planet_view.gd`](file:///home/xor/Proyectos/invassion/scenes/planet_view.gd) y [`scenes/planet_view.tscn`](file:///home/xor/Proyectos/invassion/scenes/planet_view.tscn): Generación procedural del planeta de 162 nodos, núcleo oscuro y aristas en wireframe.
- [x] [`scenes/camera_orbit.gd`](file:///home/xor/Proyectos/invassion/scenes/camera_orbit.gd) y [`scenes/camera_orbit.tscn`](file:///home/xor/Proyectos/invassion/scenes/camera_orbit.tscn): Rotación 3D por arrastre (clic izquierdo con filtro de umbral o clic derecho libre) y zoom suave por rueda del ratón.

### [x] Fase 5: Raycasting, Selección y Feedback Visual (Completada)
- [x] Intersección matemática analítica rayo-esfera en `PlanetView.get_closest_node_from_ray()` sin necesidad de colliders de física pesados.
- [x] Feedback visual por materiales (Verde: jugador, Rojo: corrupto, Gris: neutral, Celeste: seleccionado).
- [x] Filtro de eventos de ratón `mouse_filter = 2 (IGNORE)` en toda la interfaz para evitar bloqueo de clics 3D.

### [x] Fase 6: Bucle Jugable Completo - MVP (Completada)
- [x] [`scenes/main.gd`](file:///home/xor/Proyectos/invassion/scenes/main.gd) y [`scenes/main.tscn`](file:///home/xor/Proyectos/invassion/scenes/main.tscn):
  - HUD integrado con contador de energía en tiempo real.
  - Selección y compra de Extractores y Torretas con validación de territorio.
  - Spawner de invasores por carril geodésico ("Lanzar Invasión").
  - Combate activo y detección de condiciones de victoria o derrota con banner.

### [x] Fase 7: Empaquetado y Exportación Web (Completada - v0.1.0)
- [x] Plantilla de exportación configurada en [`export_presets.cfg`](file:///home/xor/Proyectos/invassion/export_presets.cfg) optimizada para WebGL2/Compatibility single-threaded (sin dependencia de headers de servidor COOP/COEP).
- [x] Compilación exitosa de binario WebAssembly (`build/web/index.wasm`, `index.pck`, `index.html`, `index.js`).
- [x] Script de compilación automática [`export_web.sh`](file:///home/xor/Proyectos/invassion/export_web.sh).

---

## Hito 2 (v0.2.0): Densidad, Zoom y Radar Periférico de Amenazas (Completado)
- [x] **Expansión a Subdivisión 3 (642 nodos)**: Malla icosférica densa de 1280 caras triangulares con radio planetario 6.2.
- [x] **Cálculo de Cráter Antipodal Dinámico**: Localización geométrica exacta del polo opuesto para cualquier nivel de subdivisión ([`logic/icosphere.py`](file:///home/xor/Proyectos/invassion/logic/icosphere.py), [`scripts/logic/icosphere.gd`](file:///home/xor/Proyectos/invassion/scripts/logic/icosphere.gd)).
- [x] **Zoom Orbital Mejorado**: Rango expandido [7.2 a 34.0] con paso de 2.5 unidades y controles múltiples (rueda, teclas PgUp/PgDn, botones HUD).
- [x] **Radar de Hemisferio Ciego**:
  - Detección analítica de oclusión esférica sin colliders físicos ni ray tracing ([`logic/threat_radar.py`](file:///home/xor/Proyectos/invassion/logic/threat_radar.py), [`scripts/logic/threat_radar.gd`](file:///home/xor/Proyectos/invassion/scripts/logic/threat_radar.gd)).
  - Proyección y clampeo de vectores de dirección a los bordes de la pantalla con flechas cardinales (`➡`, `↘`, `⬇`, `↙`, `⬅`, `↖`, `⬆`, `↗`).
  - Badges interactivos en el HUD con código de color por arquetipo (Crawler, Scout, Brute) y distancia restante en saltos.
  - Clic interactivo en cualquier badge para enfocar inmediatamente la cámara en la amenaza oculta.
- [x] **Suite de Tests Automatizada**: 25 unit tests pasando en 0.020s.

---

## Hito 3 (v0.3.0): Purificación de Cráteres & Victoria Ofensiva (Completado)
- [x] **Módulo de Purificación Procedimental**:
  - Lógica matemática en [`logic/purification.py`](file:///home/xor/Proyectos/invassion/logic/purification.py) y [`scripts/logic/purification.gd`](file:///home/xor/Proyectos/invassion/scripts/logic/purification.gd).
  - Especificaciones de la instalación: `"purifier"` (Costo: 120 E, Salud: 200 HP, Alcance: 2 saltos, Tasa: 15.0 pts/segundo).
  - Canalización de haz purificador continuo hacia cráteres alienígenas dentro del radio geodésico.
  - Sellado de nidos: al agotar la corrupción (100 HP), el cráter se sella, la zona de corrupción colapsa y cesa la generación de oleadas desde ese foco.
- [x] **Condición de Victoria Ofensiva**:
  - [`logic/territory.py`](file:///home/xor/Proyectos/invassion/logic/territory.py) y [`scripts/logic/territory.gd`](file:///home/xor/Proyectos/invassion/scripts/logic/territory.gd): victoria inmediata declarada cuando todos los cráteres del planeta han sido neutralizados.
- [x] **Presentación Visual 3D**:
  - Modelo procedimental de aguja/obelisco cian con prisma y núcleo de energía flotante en [`scenes/planet_view.gd`](file:///home/xor/Proyectos/invassion/scenes/planet_view.gd).
  - Efecto de haz continuo de descontaminación (`fire_purification_beam`) conectando la torre con la caldera alienígena.
  - Botón táctico en HUD: `✨ Purificador (120 E)` con visualización del % de corrupción restante en tiempo real.
- [x] **Suite de Tests Automatizada**: **28 unit tests** pasando en 0.021s vía [`run_tests.sh`](file:///home/xor/Proyectos/invassion/run_tests.sh).

---

## Hito 4 (v0.4.0): Múltiples Carriles de Invasión & Ataque en Pinza (Completado)
- [x] **Algoritmo Geodésico de Rutas Divergentes**:
  - `find_shortest_path` ampliado con soporte de `excluded_nodes` en [`logic/icosphere.py`](file:///home/xor/Proyectos/invassion/logic/icosphere.py) y [`scripts/logic/icosphere.gd`](file:///home/xor/Proyectos/invassion/scripts/logic/icosphere.gd).
  - `generate_multiple_invasion_lanes` en [`logic/combat.py`](file:///home/xor/Proyectos/invassion/logic/combat.py) y [`scripts/logic/combat.gd`](file:///home/xor/Proyectos/invassion/scripts/logic/combat.gd): calcula una ruta de flanqueo divergente seleccionando el vecino del cráter más opuesto angularmente y excluyendo el sector intermedio de la ruta 1.
- [x] **Despliegue Táctico Multi-Frente en Oleadas 3+**:
  - A partir de la oleada 3, la horda se bifurca en **2 carriles geodésicos simultáneos** envolviendo el planeta por ambos costados (pinza Este/Oeste).
  - Los enemigos se intercalan entre ambas rutas obligando al jugador a proteger ambos flancos de su territorio.
- [x] **Integración con Radar Periférico y HUD**:
  - El sistema de radar en borde de pantalla proyecta alertas independientes a ambos lados del visor.
  - Anuncio en barra de estado: `"¡OLEADA #X ¡ATAQUE EN PINZA (2 FRENTES)! DESATADA!"`.
- [x] **Suite de Tests Automatizada**: **29 unit tests** pasando en 0.022s vía [`run_tests.sh`](file:///home/xor/Proyectos/invassion/run_tests.sh).

---

## Hito 5 (v0.5.0): Sistema Procedimental de Guardado y Carga de Estado (Save / Load State) (Completado)
- [x] **Módulo Procedimental de Serialización Pura**:
  - Implementación en [`logic/save_system.py`](file:///home/xor/Proyectos/invassion/logic/save_system.py) y [`scripts/logic/save_system.gd`](file:///home/xor/Proyectos/invassion/scripts/logic/save_system.gd).
  - Serialización 100% compatible con JSON estándar para grafos icosféricos con claves enteras/string.
  - Almacenamiento desacoplado de:
	- Estado territorial (`nodes`, `base_node_id`, `crater_node_ids`, `craters`, `game_status`).
	- Estado de recursos y economía (`energy`, `base_income_rate`).
	- Estado de combate y oleadas (`current_wave`, `wave_countdown`, `is_wave_active`, `invader_counter`, `active_invaders`).
- [x] **Persistencia en Disco**:
  - Manejo de archivos JSON persistentes en la ruta estándar `user://quicksave.json` en Godot Engine.
  - Validación de esquema en carga para prevenir deserialización de datos corruptos o incompletos.
- [x] **Controles de Guardado y Carga Rápida**:
  - Atajos de teclado dedicados: `F6` (Guardar partida) y `F7` (Cargar partida).
  - Botones tácticos en HUD TopBar: `💾 Guardar [F6]` y `📂 Cargar [F7]`.
  - Reconstrucción visual 3D completa e instantánea de la icosfera, torres, invasores y radar tras la carga.
- [x] **Suite de Tests Automatizada**:
  - Pruebas exhaustivas en [`tests/test_save_system.py`](file:///home/xor/Proyectos/invassion/tests/test_save_system.py): roundtrip completo de serialización/deserialización, persistencia en archivos temporales, validación de errores.
  - **32 unit tests pasando en 0.027s** vía [`run_tests.sh`](file:///home/xor/Proyectos/invassion/run_tests.sh).

---

## Hito 6 (v0.6.0): RTS Planetario Simétrico: 8 Razas, Diplomacia Dinámica & IA Comandante (Completado)
- [x] **Catálogo Completo de las 8 Razas Planetarias**:
  - Implementado en [`logic/races.py`](file:///home/xor/Proyectos/invassion/logic/races.py) y [`scripts/logic/races.gd`](file:///home/xor/Proyectos/invassion/scripts/logic/races.gd).
  - Razas con identidad única: Solarian, Krynn, Nexus, Aethelian, Vorash, Titanforge, Zephyrian, Umbral.
  - Modificadores planos de economía (descuentos, rendimientos, influencia inicial) y de combate (cadencia, armaduras, evasión, asedio x2).
- [x] **Múltiples Facciones, Diplomacia Dinámica y Alianzas**:
  - Implementado en [`logic/factions.py`](file:///home/xor/Proyectos/invassion/logic/factions.py) y [`scripts/logic/factions.gd`](file:///home/xor/Proyectos/invassion/scripts/logic/factions.gd).
  - Algoritmo de muestreo de punto más lejano (*farthest-point sampling*) para ubicar bases equidistantes en la icosfera.
  - Matriz diplomática en tiempo real (`diplomacy_matrix[f1][f2] -> "ally" | "neutral" | "enemy"`).
  - Sistema de cambio de postura unilateral y treguas.
  - Sistema de tributos de energía con arancel de transporte opcional.
  - Condición de victoria dinámica (alcanzada cuando no quedan enemigos hostiles con vida).
- [x] **Comandante de IA Simétrica**:
  - Implementado en [`logic/ai_commander.py`](file:///home/xor/Proyectos/invassion/logic/ai_commander.py) y [`scripts/logic/ai_commander.gd`](file:///home/xor/Proyectos/invassion/scripts/logic/ai_commander.gd).
  - Clasificación de territorio en nodos interiores seguros vs nodos de contacto enemigo.
  - Decisiones de construcción económicas (Extractores) y defensivas (Muros y Torretas en la frontera).
  - Despliegue de asaltos militares geodésicos marchando hacia la base enemiga más cercana.
  - Respuestas diplomáticas reactivas a tributos (paz/alianza) y a traiciones (guerra inmediata).
- [x] **Suite de Tests Automatizada**:
  - Tests en [`tests/test_races.py`](file:///home/xor/Proyectos/invassion/tests/test_races.py), [`tests/test_factions.py`](file:///home/xor/Proyectos/invassion/tests/test_factions.py) y [`tests/test_ai_commander.py`](file:///home/xor/Proyectos/invassion/tests/test_ai_commander.py).
  - **55 unit tests pasando en 0.039s** vía [`run_tests.sh`](file:///home/xor/Proyectos/invassion/run_tests.sh).

---

## Hito 7 (v0.7.0): Integración Total del RTS Planetario 3D Simétrico en Godot Engine (Completado)
- [x] **Bucle de Simulación Multi-Facción en Godot**:
  - Integrado en [`scenes/main.gd`](file:///home/xor/Proyectos/invassion/scenes/main.gd):
	- Inicialización de facción del Jugador (*Imperio Solar*) y de la IA (*Enclave Krynn*) en nodos equidistantes.
	- Proyección y renderizado de fronteras y colores de cada civilización sobre la icosfera 3D.
	- Bucle de economía simétrica por facciones en tiempo real.
	- Ejecución periódica del Comandante de IA (cada 1.5s): construcción de bases, extractores y muros en el hemisferio opuesto, y lanzamiento de asaltos geodésicos.
- [x] **Combate Geodésico Multi-Facción**:
  - En [`logic/combat.py`](file:///home/xor/Proyectos/invassion/logic/combat.py) y [`scripts/logic/combat.gd`](file:///home/xor/Proyectos/invassion/scripts/logic/combat.gd):
	- Priorización de objetivos hostiles por torretas y libre tránsito entre aliados.
	- Asaltos militares con eventos de daño que alertan diplomáticamente a las facciones agredidas.
- [x] **Panel HUD Interactivo de Diplomacia & Tributos**:
  - Panel modal accesible mediante tecla `[D]` o botón `📜 Diplomacia [D]`.
  - Visualización del estado en tiempo real de cada facción, posturas mutuas y reserva energética.
  - Botones dinámicos para cambiar postura bilateral: `🤝 Aliado`, `⚖️ Neutral`, `⚔️ Hostil`.
  - Botones de transferencia de tributos energéticos (`+25 E`, `+50 E`, `+100 E`) con reacción diplomática inmediata de la IA.
- [x] **Suite de Tests y Rendimiento Inmediato**:
  - Pruebas unitarias de combate multi-facción en [`tests/test_combat.py`](file:///home/xor/Proyectos/invassion/tests/test_combat.py).
  - **55 unit tests pasando en 0.039s** vía [`run_tests.sh`](file:///home/xor/Proyectos/invassion/run_tests.sh).
