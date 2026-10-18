# Game Design Document & Technical Specification: invassion

## 1. Game Overview
* **Genre:** Real-Time Geodetic Planetary Strategy & Territory Defense (Hybrid combining tactical lane placement from *Plants vs. Zombies* with base expansion and macro-economy from *Age of Empires* / *StarCraft*).
* **Target Platform:** Native Godot 4 Desktop Execution.
* **Camera & Navigation:** Full 3D trackball orbital camera with momentum/inertia, drag threshold filtering, smooth zoom, and tactical auto-focus shortcuts (`Base [Space]`, `Threat [F]`, `Enemy Base [C]`).
* **Blind Hemisphere Radar:** Screen-edge dynamic indicator badges projecting threats advancing on the occluded side of the planet.

---

## 2. The Board: Geodetic Icosphere Grid

### 2.1 Mathematical Topology
* **Standard Resolution:** Dual-subdivision icosahedron (162 vertices / nodes) scalable to 642 vertices.
* Each node $v \in V$ contains:
  * 3D Cartesian position on the sphere: $\vec{p} = (x, y, z)$ where $|\vec{p}| = R$.
  * Adjacency list of topological neighbors (valence 5 or 6).
  * Structure status: `building` (or `null`).
  * Faction controller: `controller` (Faction ID or `neutral`).
  * Special flags: `is_base`, `is_crater`.

### 2.2 Multi-Faction Territorial Influence
* **Structures project influence hops ($R$):**
  * **Command Base:** 2 to 3 influence hops depending on faction race.
  * **Extractor / Quantum Harvester:** 1 to 2 influence hops.
  * **Defensive Turret:** 1 to 2 influence hops.
  * **Containment Wall:** 0 influence hops (pure barrier).
* **Contested Nodes:** When influence zones overlap, ownership resolves in favor of existing structures or remains disputed neutral.
* **Victory Condition:** Eradicate hostile faction command bases across the globe.
* **Defeat Condition:** Total collapse of the player's primary Command Base.

---

## 3. Economy & Installations (Age of Empires Style)

| Installation | Cost | Influence | Integrity | Primary Function |
| :--- | :--- | :--- | :--- | :--- |
| **Command Base** | Initial | 2-3 hops | 500 HP | Generates +5.0 E/s base energy. Armed with active 20 DMG perimeter defense battery. |
| **Quantum Harvester** | 50 E | 1-2 hops | 100 HP | Generates +1.0 E/s to +1.5 E/s per controlled node in radius. |
| **Defensive Turret** | 75 E | 1-2 hops | 280 HP | Heavy defensive fortification. 35 DMG, 0.8s cooldown, 2-3 hops range. Smart focus-fire on lowest HP threats. |
| **Containment Wall** | 25 E | 0 hops | 350 HP | High-durability structural barrier blocking physical invader transit. |
| **Atmospheric Purifier**| 120 E | 1-2 hops | 200 HP | Radiates cleansing field (4 hops) sealing alien spawn craters. |

---

## 4. Combat Dynamics & Invasion Mechanics

* **Geodesic Lanes:** Invaders navigate along shortest geodesic paths (BFS) from alien craters or rival bases toward target objectives.
* **Flank & Pincer Attacks:** Wave progression introduces divergent flank lanes circumventing player fortifications.
* **Tactical Prioritization (RTS Focus Fire):**
  * Defensive turrets evaluate all hostile targets in range and prioritize direct attackers first, followed by lowest HP units to eliminate enemy damage output rapidly.
* **Symmetrical Planetary AI:** Procedural AI commanders manage macro-economies, expand territory, reinforce borders with turrets and walls, research technologies, and launch military assault squads.
* **Emergency Defense:** When bases or defensive perimeters take damage, AI commanders scramble emergency counter-assault units immediately.

---

## 5. Architecture & Code Structure

* **Style:** Pure procedural programming, simple standalone functions, flat dictionaries and arrays. No object-oriented class hierarchies or mutable stateful models.
* **Codebase Directory Layout:**
  ```
  invassion/
  ├── logic/                # Pure algorithmic Python modules (shared logic specification)
  │   ├── icosphere.py      # Geodetic mesh generation and BFS graph traversal
  │   ├── territory.py      # Influence projection and conquest algorithms
  │   ├── economy.py        # Income calculations and purchase validation
  │   ├── combat.py         # Range detection, turret targeting, focus-fire, damage ticks
  │   ├── factions.py       # Multi-faction diplomacy, teams, and victory evaluation
  │   ├── ai_commander.py   # Procedural AI decision tree and assault logic
  │   ├── races.py          # 8 distinct galactic factions with economic/combat traits
  │   ├── tech_tree.py      # Tech research tree and stat modifiers
  │   ├── threat_radar.py   # Blind hemisphere screen projection and clamping
  │   └── save_system.py    # Serialization and state persistence
  ├── scripts/logic/        # Identical GDScript procedural equivalents for Godot 4
  ├── scenes/               # Passive visual Godot 4 scenes (StarCraft RTS HUD, 3D Planet)
  ├── tests/                # Comprehensive unit test suite (execution < 60ms)
  ├── VERSION               # Single source of truth for SemVer
  ├── GIT_WORKFLOW.md       # Git Flow, commit conventions, and release policies
  ├── GDD.md                # Game Design Document
  └── FRAMEWORK.md          # Technical framework and architectural guidelines
  ```
