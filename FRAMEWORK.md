# Development Framework: 3D Geodetic Planetary Strategy

This document establishes the technical decisions, architecture, methodology, and development standards for the **invassion** project.

---

## 1. Technical Stack & Execution Targets

### 1.1 Engine & Platform
* **Godot 4 Engine (Native & 3D Specialist Focus):** Primary runtime. Leveraging 3D scene rendering, trackball camera transforms, immediate mesh drawing, and low-level shader passes.
* **Pure Python Engine & Test Harness:** Dual implementation of all mathematical, economic, faction, and combat algorithms in pure Python, allowing lightning-fast unit tests (< 60ms) without headless engine boot overhead.
* **Native Desktop Execution:** Optimized for native performance and developer iteration via Godot (`F5`).

### 1.2 Asset & Rendering Pipeline
* **Procedural Icosphere Generation:** No external 3D model files required for the planetary grid; mathematical subdivision of an icosahedron generates 162 or 642 nodes dynamically.
* **Low-Poly Cyber Aesthetic:** High-contrast wireframe geodesics, glowing faction team colors, dynamic billboard badges, and laser beam line renderers.

---

## 2. Programming Paradigm & Code Architecture

Object-Oriented Programming (deep inheritance hierarchies, encapsulated mutable states, coupled class methods) is **strictly avoided** in favor of a **pragmatic data-oriented and pure procedural architecture**.

### 2.1 Hybrid Model: Logic vs. Presentation Decoupling

* **Presentation Layer (Godot - Minimal OOP):** Engine nodes (`Node3D`, `MeshInstance3D`, `Camera3D`, UI Controls) act as **passive views**. They listen to user inputs, trigger state transitions via pure functions, and reflect the world state visually.
* **Game Logic Layer (Pure Functions + Flat Data):** State is held in plain flat dictionaries and arrays. Simulation rules (combat ticks, AI decisions, wave propagation, income generation, technology research) are pure static functions.
* **Testing Suite:** Comprehensive unit tests executed via CLI in milliseconds with zero graphics or scene tree dependencies.

### 2.2 Core Design Principles
1. **Flat Data:** Entity states are represented as simple dictionaries/structs, completely serializable without hidden internal state.
2. **Pure Functions:** Game rules follow the paradigm `calculate_next_state(current_state, parameters) -> updated_state`.
3. **Passive Nodes:** Visual components never compute economic or combat outcomes; they only animate and render the results provided by the logic layer.

---

## 3. AI-Assisted Development Methodology

Development follows a strict closed-loop iterative process:

1. **Define Specification & Contract:** Establish input schemas, output structures, and boundary conditions.
2. **Generate Unit Tests First (TDD):** Full coverage of nominal workflows and extreme edge cases.
3. **Implement Pure Procedural Function:** Simple, concise, algorithmic code with zero OOP bloat.
4. **Validate Test Suite (CLI):** Immediate execution (`./run_tests.sh`) ensuring 100% pass rate in < 70ms.
5. **Bind to Godot View & Scene:** Wire signals, UI consoles, and 3D visual representations.

---

## 4. Testing Strategy (TDD from Day 1)

* **Headless CLI Execution:** Fast unit test runner executing via `python3 -m unittest discover -s tests -v`.
* **Priority Coverage:**
  * Geodetic graph traversal, BFS shortest path, spherical distance.
  * Multi-faction territorial expansion and influence projection.
  * Dynamic economic flow, harvesting rates, and purchase validation.
  * Real-time combat ticks, turret targeting, focus-fire, base batteries, and damage resolution.
  * AI Commander decision tree (expansion, assault thresholds, emergency defense, diplomatic reactions).
  * Savegame serialization and state persistence roundtrips.
