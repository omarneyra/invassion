# invassion: 3D Geodetic Planetary Strategy (RTS)

![Version](https://img.shields.io/badge/version-0.7.0-blue.svg)
![Godot](https://img.shields.io/badge/engine-Godot%204.x-478cbf.svg)
![Python](https://img.shields.io/badge/tests-67%20passing%20(<0.06s)-success.svg)
![Architecture](https://img.shields.io/badge/style-pure%20procedural%20%7C%20no%20OOP-orange.svg)

**invassion** is a 3D real-time strategy and planetary defense game played across a continuous geodetic spherical grid (icosphere). Combining macro-economic expansion and base management (*Age of Empires*, *StarCraft*) with geodesic lane defense and tactical positioning (*Plants vs. Zombies*), the game challenges players to command planetary empires, expand territorial influence, research technological advancements, and orchestrate military invasions across a living 3D world.

---

## Key Features

* **3D Geodetic Spherical Battlefield**: Navigate a seamless 162-node icosphere topology with an inertial trackball camera and analytical raycasting (no heavy physics colliders needed).
* **StarCraft / AoE Cyber RTS Interface**:
  * **Top Console**: Live resource status (`⚡ Energy`), wave countdowns, objective tracking, and management panels.
  * **Tactical Nav Bay**: Rapid camera shortcuts (`🎯 Base [Space]`, `⚠️ Threat [F]`, `🏛️ Enemy Base [C]`, `🔍 Zoom`).
  * **Sector & Unit Inspector**: Detailed real-time HUD card displaying building integrity, faction affiliation, and tactical combat stats.
  * **Command Matrix**: Instant construction orders (`Shield Wall`, `Quantum Harvester`, `Defensive Turret`, `Military Assault [R]`).
* **Tactical RTS Combat & Defensive Fortifications**:
  * **Smart Focus-Fire Targeting**: Defensive turrets intelligently engage direct attackers and prioritize low-HP enemies to suppress hostile damage output quickly.
  * **Base Defensive Batteries**: Primary command bases feature automated perimeter defense fire to prevent premature rush victories.
  * **Clean Grid Collapse**: Defeated faction bases immediately decommission their peripheral installations, eliminating ghost structures.
* **Symmetrical AI Commander**: Autonomous procedural AI managing harvesting operations, fortified perimeters, tech research, and strategic counter-assaults.
* **8 Distinct Galactic Factions**: Asymmetrical economic, combat, and unit traits (Solarian Hegemony, Krynn Swarm, Nexus Protocol, Titanforge Lithoids, and more).
* **Planetary Tech Tree & Diplomacy**: Upgrade offensive firepower, deploy shields, trade planetary tributes, and negotiate alliances.
* **Blind Hemisphere Radar**: Screen-edge dynamic threat badges tracking off-screen enemies navigating the occluded hemisphere.

---

## Architectural Principles (Pure Procedural / No OOP)

The codebase strictly adheres to a **data-oriented, pure procedural architecture**:
* **Zero OOP Bloat**: No class inheritance hierarchies, no stateful object instances, and no hidden mutation.
* **Flat Data Schemas**: All game state lives in plain dictionaries and arrays, ensuring 100% serializability and simple debugging.
* **Dual Python & GDScript Parity**: All mathematical, territorial, combat, and AI algorithms are implemented in pure Python (`logic/`) and mirrored in GDScript (`scripts/logic/`).
* **Instant TDD Unit Tests**: 67 unit tests execute in under **55 milliseconds** (`./run_tests.sh`) without requiring engine or graphics initialization.

---

## Quickstart

### Running Unit Tests
```bash
./run_tests.sh
```
Executes all 67 unit tests across graph mathematics, territorial influence, economic cycles, combat resolution, AI decisions, and save systems.

### Running the Game
Open the project directory in **Godot 4.x** and press **F5** (or open `scenes/main.tscn`).

---

## Git Workflow & Development Standard

This repository follows a strict Git Flow model with Semantic Versioning:
* `master`: Stable, tagged production releases (`vMAJOR.MINOR.PATCH`).
* `develop`: Main integration branch.
* `feature/<name>`: Scoped gameplay features and improvements.
* `fix/<name>`: Balance tweaks and bug fixes.

For detailed rules on branching, commit conventions, SemVer, and English documentation policies, see [GIT_WORKFLOW.md](file:///home/xor/Proyectos/invassion/GIT_WORKFLOW.md).

---

## License

All rights reserved. Developed by xor & Antigravity.
