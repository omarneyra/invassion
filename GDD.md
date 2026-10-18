# GDD & Especificación Técnica: invassion (Defensa Planetaria 3D)

## 1. Visión General del Juego
* **Género:** Estrategia / Defensa de Territorio en Tiempo Real sobre superficie esférica (Fusión de colocación táctica estilo *Plants vs. Zombies* y progresión de instalaciones estilo *Age of Empires*).
* **Plataforma Objetivo:** Navegador Web (WebAssembly + WebGPU/WebGL 2) vía Godot Engine.
* **Cámara & Navegación:** Vista orbital superior en 3D. Control mediante arrastre con umbral de filtrado (drag threshold) para rotar la esfera planetaria en cualquier eje y rueda del ratón/gesto táctil para zoom in/out.
* **Manejo de Hemisferio Ciego:** Indicadores visuales de amenaza en la periferia de pantalla (flechas de alerta) cuando hay invasores activos en el lado no visible del planeta.

---

## 2. El Tablero: Malla Geodésica (Icosfera)

### 2.1 Estructura Matemática del Grafo
* **Resolución Estándar:** Icosfera con **Subdivisión 2** (162 nodos / vértices uniformemente distribuidos).
* Cada nodo $v \in V$ posee:
  * Coordenada tridimensional normalizada en la esfera: $\vec{p} = (x, y, z)$ donde $|\vec{p}| = R$.
  * Lista de nodos vecinos adyacentes conectados por aristas $E$ (5 o 6 vecinos por nodo).
  * Estado de ocupación: `vacio`, `edificio_id`, `invasor_id`.
  * Bando controlador actual: `neutro`, `jugador`, `corrupto_enemigo`.
  * Tipo de terreno especial: `normal`, `crater_spawn`, `base_jugador`.

### 2.2 Sistema de Influencia Territorial y Conquista
* **Instalaciones del Jugador:** Cada edificio proyecta un radio de influencia ($R$ saltos de arista):
  * **Base:** Radio 2 saltos (~19 nodos iniciales).
  * **Torreta / Recolector:** Radio 1 salto (~5 a 6 nodos contiguos).
* **Zonas de Infección / Corrupción (Cráteres de Invasión):**
  * Los cráteres enemigos proyectan una zona corrupta donde el jugador no puede construir de forma directa.
  * Para conquistar el planeta, el jugador debe expandir su perímetro hasta rodear o neutralizar el cráter.
* **Condición de Victoria:** Controlar el 100% de los nodos libres de corrupción y erradicar las fuentes de invasión.
* **Condición de Derrota:** Destrucción de la Base del jugador o reducción del territorio a cero nodos.

---

## 3. Economía e Instalaciones (Estilo Age of Empires)

| Instalación | Costo | Radio Influencia | Salud | Función Principal |
| :--- | :--- | :--- | :--- | :--- |
| **Puesto de Comando (Base)** | Inicial | 2 saltos | 500 HP | Genera +5 energía/seg. Si cae, derrota. |
| **Extractor / Recolector** | 50 E | 1 salto | 100 HP | Genera +2 energía/seg por cada nodo dominado en su radio. |
| **Torreta Defensiva** | 75 E | 1 salto | 150 HP | Ataca enemigos a 2 saltos de distancia. Cadencia: 1 disparo/seg. Daño: 25. |
| **Muro Defensivo** | 25 E | 0 saltos | 300 HP | Bloquea el avance físico de invasores en el nodo. |

---

## 4. Dinámica de Invasión (Carriles Geodésicos estilo PvZ)

* **Rutas Geodésicas de Invasión:** En lugar de dispersarse al azar por el grafo, cada cráter genera **carriles geodésicos principales** hacia el territorio del jugador.
* **Avance de la Horda:** Los invasores marchan por las aristas de estos carriles predefinidos.
* **Combate en Ruta:**
  * Si la torreta detecta un invasor dentro de su radio de alcance angular, dispara un proyectil balístico.
  * Si un invasor llega a un nodo ocupado por un edificio, se detiene y ataca hasta demolerlo, reduciendo el territorio del jugador si el edificio cae.

---

## 5. Arquitectura de Código & Desacoplamiento (Reglas del Proyecto)

* **Estilo:** Procedimental puro, funciones simples sin OOP, datos planos (diccionarios y listas).
* **Estructura del Proyecto:**
  ```
  invassion/
  ├── logic/                # Módulos de funciones puras (Python y GDScript)
  │   ├── icosphere.py      # Generación del grafo geodésico de 162 nodos y distancias
  │   ├── territory.py      # Radios de influencia, conquista y zonas de corrupción
  │   ├── economy.py        # Generación de energía, validación y costos de edificios
  │   └── combat.py         # Detección de rango, disparo, rutas de invasión y daño
  ├── tests/                # Suite de Unit Tests inmediatos (ejecución < 50ms)
  │   ├── test_icosphere.py
  │   ├── test_territory.py
  │   ├── test_economy.py
  │   └── test_combat.py
  ├── scenes/               # Capa visual pasiva de Godot
  ├── GDD.md
  └── FRAMEWORK.md
  ```
