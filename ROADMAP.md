# Project Roadmap & Implementation Status: invassion

This document records the engineering progress and milestone roadmap in accordance with [FRAMEWORK.md](file:///home/xor/Proyectos/invassion/FRAMEWORK.md), [GDD.md](file:///home/xor/Proyectos/invassion/GDD.md), and [GIT_WORKFLOW.md](file:///home/xor/Proyectos/invassion/GIT_WORKFLOW.md).

---

## Global Progress Overview

```mermaid
flowchart LR
	M1["Milestone 1: Core Geodetic MVP"] --> M2["Milestone 2: Symmetrical Factions & AI"]
	M2 --> M3["Milestone 3: StarCraft RTS HUD & Rebalance"]
	M3 --> M4["Milestone 4: Polish & Audio/VFX"]

	style M1 fill:#22c55e,stroke:#15803d,color:#ffffff
	style M2 fill:#22c55e,stroke:#15803d,color:#ffffff
	style M3 fill:#22c55e,stroke:#15803d,color:#ffffff
	style M4 fill:#3b82f6,stroke:#1d4ed8,color:#ffffff
```

---

## Detailed Milestone Breakdown

### [x] Milestone 1: Geodetic Engine & Basic Loop (Completed)
- [x] Mathematical generation of 162-node icosphere topology with BFS geodesic pathfinding ([`logic/icosphere.py`](file:///home/xor/Proyectos/invassion/logic/icosphere.py)).
- [x] Territorial influence projection, building placement, and containment mechanics ([`logic/territory.py`](file:///home/xor/Proyectos/invassion/logic/territory.py)).
- [x] Economic harvesting loops and purchase validation ([`logic/economy.py`](file:///home/xor/Proyectos/invassion/logic/economy.py)).
- [x] Geodesic wave navigation and combat damage ticks ([`logic/combat.py`](file:///home/xor/Proyectos/invassion/logic/combat.py)).
- [x] Procedural 3D planetary rendering with inertia trackball camera ([`scenes/camera_orbit.gd`](file:///home/xor/Proyectos/invassion/scenes/camera_orbit.gd)).
- [x] Full Python-to-GDScript parity.

### [x] Milestone 2: Symmetrical Multi-Faction Engine & AI Commander (Completed)
- [x] Dynamic multi-faction territory calculation ([`logic/factions.py`](file:///home/xor/Proyectos/invassion/logic/factions.py)).
- [x] Dynamic diplomacy matrix (Ally, Neutral, Enemy stances, tribute system).
- [x] Procedural AI Commander executing macro-economic expansions and military assaults ([`logic/ai_commander.py`](file:///home/xor/Proyectos/invassion/logic/ai_commander.py)).
- [x] 8 Distinct Galactic Factions catalog with asymmetric economic and combat traits ([`logic/races.py`](file:///home/xor/Proyectos/invassion/logic/races.py)).
- [x] Interactive planetary Tech Tree with retroactive upgrades ([`logic/tech_tree.py`](file:///home/xor/Proyectos/invassion/logic/tech_tree.py)).
- [x] State serialization and save/load persistence system ([`logic/save_system.py`](file:///home/xor/Proyectos/invassion/logic/save_system.py)).

### [x] Milestone 3: StarCraft / AoE RTS HUD & Combat Rebalance (Completed)
- [x] StarCraft II / Age of Empires style RTS command console ([`scenes/main.tscn`](file:///home/xor/Proyectos/invassion/scenes/main.tscn)):
  - Top Resource & Objective Bar.
  - Tactical Camera Navigation Bay.
  - Sector & Structure Inspector Bay with real-time stats and faction colors.
  - Cyber Command Bay for instant building & assault orders.
- [x] Base Defensive Battery to prevent premature rush victories.
- [x] Defeated faction cleanup (collapsing structures upon base destruction).
- [x] Fortified Turret rebalance: 280 HP, 35 DMG, 0.8s cooldown (43.75 DPS).
- [x] RTS smart focus-fire targeting (lowest HP threats targeted first).
- [x] AI emergency defense mobilization when base or perimeter is attacked.
- [x] Interactive Victory/Defeat modal with Free Spectate mode and quick Rematch.
- [x] Comprehensive test suite: **67 unit tests running in ~50ms**.

### [ ] Milestone 4: VFX, Audio & Visual Polish (Next Up)
- [ ] Shader enhancements for planetary atmosphere, node glow, and laser projectile trails.
- [ ] Positional sound effects for construction, laser discharges, alerts, and building collapse.
- [ ] Faction visual distinctions in 3D buildings and custom unit models.
