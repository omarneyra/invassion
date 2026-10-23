# Visual Compendium of Galactic Factions — Invassion

This document establishes the **canonical visual identity**, color palettes, architectural language, and asset kits for the 8 galactic factions of **Invassion**. All images serve as official design references for procedural 3D modeling (`.obj`/`.mtl`) and in-engine rendering in Godot 4.x.

---

## Faction Flagship Bases (Command Cores)

| Faction | Theme | Command Base (`base`) |
| :--- | :--- | :---: |
| **Solarian Hegemony** | Industrial Titanium & Cyan Plasma | ![Solarian Base](../assets/concept_art/solarian_base.jpg) |
| **Krynn Swarm** | Biological Chitin & Acid Sacs | ![Krynn Base](../assets/concept_art/krynn_flagship.jpg) |
| **Nexus Protocol** | Quantum Ceramic & Levitating Rings | ![Nexus Base](../assets/concept_art/nexus_flagship.jpg) |
| **Aethelian Enclave** | Psionic Alabaster & Solar Gold | ![Aethelian Base](../assets/concept_art/aethelian_flagship.jpg) |
| **Vorash Scavengers** | Welded Scrap, Rust & Diesel | ![Vorash Base](../assets/concept_art/vorash_flagship.jpg) |
| **Titanforge Lithoids** | Volcanic Basalt & Magma Channels | ![Titanforge Base](../assets/concept_art/titanforge_flagship.jpg) |
| **Zephyrian Nomads** | Aerodynamic Composite & Solar Sails | ![Zephyrian Base](../assets/concept_art/zephyrian_flagship.jpg) |
| **Umbral Parasites** | Obsidian Shards & Void Matter | ![Umbral Base](../assets/concept_art/umbral_flagship.jpg) |

---

## 1. Solarian Hegemony (`solarian`)
* **Archetype:** Heavy Industrial / Ballistic Engineering
* **Base Color:** `#22c55e` (Military Green / Tactical Cyan)
* **Materials:** Matte dark titanium, copper induction coils, riveted armor plates, cyan plasma conduits (`#00e5ff`).
* **In-Engine Status:** **100% Implemented in 3D & In-Engine (`assets/models/`)**
* **Gameplay Trait:** 20% turret cooldown reduction, +25% harvester energy yield.

### Complete Solarian Kit:
| Base | Turret | Harvester | Wall | Purifier | Vanguard Mech |
| :---: | :---: | :---: | :---: | :---: | :---: |
| ![Base](../assets/concept_art/solarian_base.jpg) | ![Turret](../assets/concept_art/solarian_turret.jpg) | ![Harvester](../assets/concept_art/solarian_harvester.jpg) | ![Wall](../assets/concept_art/solarian_wall.jpg) | ![Purifier](../assets/concept_art/solarian_purifier.jpg) | ![Vanguard](../assets/concept_art/solarian_vanguard.jpg) |

1. **Base (`base`)**: *Planetary Command Core* — Hexagonal bunker with perimeter forcefield emitter and telemetry array.
2. **Turret (`turret`)**: *Pulse Defense Cannon* — Dual-barrel rapid-fire ballistic turret with copper induction rings.
3. **Harvester (`harvester`)**: *Geothermal Mining Rig* — Vertical laser drill and hydraulic magma extraction pump.
4. **Wall (`wall`)**: *Barrier Shield Pylon* — Heavy interlocking alloy pylon with localized kinetic shielding.
5. **Purifier (`purifier`)**: *Orbital Purification Array* — Triangular Tesla coil array directing an ionizing cleansing beam at infected planetary craters.
6. **Doctrinal Units**:
   - *Vanguard Mech* (Heavy, 110 HP): Armored bipedal walker with dual autocannons.
   - *Infantry Marine* (Light, 45 HP): Rapid-response mechanized rifle squads.

---

## 2. Krynn Swarm (`krynn`)
* **Archetype:** Biological Insectoid / Swarm Growth
* **Base Color:** `#a855f7` (Biological Purple & Toxic Lime Green)
* **Materials:** Segmented purple-black chitin carapaces, translucent bioluminescent acid sacs, organic bone barbs.
* **In-Engine Status:** Concept Art 100% Complete; 3D generation pending.
* **Gameplay Trait:** Buildings 20% cheaper, units 25% faster with 1.5 HP/s passive regeneration.

### Complete Krynn Kit:
| Base | Turret | Harvester | Wall | Purifier | Ravager Beast |
| :---: | :---: | :---: | :---: | :---: | :---: |
| ![Base](../assets/concept_art/krynn_flagship.jpg) | ![Turret](../assets/concept_art/krynn_turret.jpg) | ![Harvester](../assets/concept_art/krynn_harvester.jpg) | ![Wall](../assets/concept_art/krynn_wall.jpg) | ![Purifier](../assets/concept_art/krynn_purifier.jpg) | ![Ravager](../assets/concept_art/krynn_ravager.jpg) |

1. **Base (`base`)**: *Swarm Matrix Spire* — Living organic hive spire with central pulsating venom heart and rooting tendrils.
2. **Turret (`turret`)**: *Acid Spore Cannon* — Predatory insectoid maw spitting pressurized caustic acid globs.
3. **Harvester (`harvester`)**: *Biomass Digestive Rhizome* — Parasitic root tendrils siphoning planetary mantle heat.
4. **Wall (`wall`)**: *Chitin Bone Crest* — Interlocking plates of calcified carapace reinforced with venomous ribs.
5. **Purifier (`purifier`)**: *Void-Neutralizing Bloom* — Bioluminescent flower releasing cleansing airborne mycelium spores.
6. **Doctrinal Units**:
   - *Krynn Ravager* (Heavy, 100 HP): Armored quadrupedal assault beast with scythe forelimbs.
   - *Broodling* (Light, 55 HP): Fast-swarming predatory hatchlings.

---

## 3. Nexus Protocol (`nexus`)
* **Archetype:** Quantum Synthetic / Autonomous AI Network
* **Base Color:** `#06b6d4` (Quantum Cyan, White Ceramic & Chrome)
* **Materials:** Glossy white ceramic armor, black graphene composites, levitating concentric chrome rings, cyan crystalline cores.
* **In-Engine Status:** Concept Art 100% Complete; 3D generation pending.
* **Gameplay Trait:** +1 turret range hop (range 3), +3 E/s constant passive energy income.

### Complete Nexus Kit:
| Base | Turret | Harvester | Wall | Purifier | Railgun Automaton |
| :---: | :---: | :---: | :---: | :---: | :---: |
| ![Base](../assets/concept_art/nexus_flagship.jpg) | ![Turret](../assets/concept_art/nexus_turret.jpg) | ![Harvester](../assets/concept_art/nexus_harvester.jpg) | ![Wall](../assets/concept_art/nexus_wall.jpg) | ![Purifier](../assets/concept_art/nexus_purifier.jpg) | ![Railgun Mech](../assets/concept_art/nexus_railgun_mech.jpg) |

1. **Base (`base`)**: *Quantum Core Matrix* — White ceramic pylon surrounded by rotating levitation rings and holographic processing core.
2. **Turret (`turret`)**: *Electromagnetic Railgun Accelerator* — Long-range precision magnetic accelerator cannon.
3. **Harvester (`harvester`)**: *Quantum Flux Siphon* — Resonance ring array extracting subsurface quantum particles.
4. **Wall (`wall`)**: *Holographic Link Barrier* — Hexagonal ceramic pylon projecting solid-light cyan forcefield lattices.
5. **Purifier (`purifier`)**: *Molecular Orbital Reconfigurator* — Concentrated vertical deconstruction laser beam.
6. **Doctrinal Units**:
   - *Railgun Automaton* (Heavy, 110 HP): Bipedal sniper mech with shoulder-mounted magnetic cannon.
   - *Pulse Drone* (Light, 48 HP): Floating discoidal scout drones emitting guided micro-pulses.

---

## 4. Aethelian Enclave (`aethelian`)
* **Archetype:** Ancient Psionic Templars / Solar Plasma
* **Base Color:** `#eab308` (Solar Gold, Alabaster Marble & Amber)
* **Materials:** Fluted white alabaster marble, polished gold filigree, suspended sun halos, radiant amber crystals.
* **In-Engine Status:** Concept Art 100% Complete; 3D generation pending.
* **Gameplay Trait:** Double purification rate (30 pts/s), starts with 3 influence hops.

### Complete Aethelian Kit:
| Base | Turret | Harvester | Wall | Purifier | Archon Strider |
| :---: | :---: | :---: | :---: | :---: | :---: |
| ![Base](../assets/concept_art/aethelian_flagship.jpg) | ![Turret](../assets/concept_art/aethelian_turret.jpg) | ![Harvester](../assets/concept_art/aethelian_harvester.jpg) | ![Wall](../assets/concept_art/aethelian_wall.jpg) | ![Purifier](../assets/concept_art/aethelian_purifier.jpg) | ![Archon Strider](../assets/concept_art/aethelian_archon_strider.jpg) |

1. **Base (`base`)**: *Solar Temple Monolith* — Sacred alabaster spire with levitating sun-disc halo channeling planetary psionic energy.
2. **Turret (`turret`)**: *Solar Ray Prism Obelisk* — Suspended amber crystal discharging focused beams of searing solar plasma.
3. **Harvester (`harvester`)**: *Telluric Communion Pylon* — Marble sanctuary transmuting thermal currents into liquid light.
4. **Wall (`wall`)**: *Sacred Alabaster Screen* — Carved stone barrier projecting amber psionic kinetic deflection grids.
5. **Purifier (`purifier`)**: *Beacon of Transcendence* — Massive tiered temple channeling a celestial flame pillar.
6. **Doctrinal Units**:
   - *Archon Strider* (Heavy, 120 HP): Tall psionic titan enclosed in a radiant golden spherical aura.
   - *Psionic Disciple* (Light, 50 HP): Levitate disciples with guided plasma staves.

---

## 5. Vorash Scavengers (`vorash`)
* **Archetype:** Nomadic Space Pirates / Orbital Scrappers
* **Base Color:** `#f97316` (Rust Orange, Corrugated Iron & Welded Steel)
* **Materials:** Salvaged armor plates, diesel exhausts, barbed wire, hazard stripes, improvised hydraulics.
* **In-Engine Status:** Concept Art 100% Complete; 3D generation pending.
* **Gameplay Trait:** +35 E bounty per destroyed enemy, double damage to walls and enemy structures.

### Complete Vorash Kit:
| Base | Turret | Harvester | Wall | Purifier | Scrap Tank |
| :---: | :---: | :---: | :---: | :---: | :---: |
| ![Base](../assets/concept_art/vorash_flagship.jpg) | ![Turret](../assets/concept_art/vorash_turret.jpg) | ![Harvester](../assets/concept_art/vorash_harvester.jpg) | ![Wall](../assets/concept_art/vorash_wall.jpg) | ![Purifier](../assets/concept_art/vorash_purifier.jpg) | ![Scrap Tank](../assets/concept_art/vorash_scrap_tank.jpg) |

1. **Base (`base`)**: *Fortified Scrap Bastion* — Irregular multi-level junk fortress with watchtowers and diesel smoke stacks.
2. **Turret (`turret`)**: *Twin Recycled Flak Cannon* — Heavy dual-barrel cannon mounted on vehicle axle swivel.
3. **Harvester (`harvester`)**: *Steam Hammer & Pump Rig* — Industrial cable crane driving a heavy percussion mining drill.
4. **Wall (`wall`)**: *Welded Armor Barricade* — Crow's nest watch pylon built from tank tracks and barbed wire.
5. **Purifier (`purifier`)**: *Chemical Plasma Flare* — Incinerator tower built of welded fuel drums launching cleansing fireballs.
6. **Doctrinal Units**:
   - *Scrap Tank* (Heavy, 120 HP): Heavily armored tread vehicle with bulldozer ram and demolition mortar.
   - *Raider Scout* (Light, 55 HP): Fast off-road buggy with roof-mounted machine gun.

---

## 6. Titanforge Lithoids (`titanforge`)
* **Archetype:** Mineral Lithoids / Fortification Masters
* **Base Color:** `#78716c` (Basalt Gray, Obsidian & Glowing Magma)
* **Materials:** Chiseled basalt megaliths, granite blocks, obsidian slabs, glowing molten lava channels.
* **In-Engine Status:** Concept Art: Base, Turret, Harvester generated; Wall, Purifier, Unit in progress.
* **Gameplay Trait:** Walls cost 52% less (12 E instead of 25 E), 20% passive global damage reduction.

### Titanforge Kit (In Progress):
| Base | Turret | Harvester | Wall | Purifier | Juggernaut Colossus |
| :---: | :---: | :---: | :---: | :---: | :---: |
| ![Base](../assets/concept_art/titanforge_flagship.jpg) | ![Turret](../assets/concept_art/titanforge_turret.jpg) | ![Harvester](../assets/concept_art/titanforge_harvester.jpg) | *(Generating)* | *(Generating)* | *(Generating)* |

1. **Base (`base`)**: *Cyclopean Basalt Citadel* — Colossal stepped ziggurat with magma melting crucibles.
2. **Turret (`turret`)**: *Volcanic Magma Mortar* — Wide-bore stone mortar lobbing burning lava bombs.
3. **Extractor (`harvester`)**: *Geothermal Stone Forge* — Massive stone counterweight pump harnessing volcanic veins.
4. **Wall (`wall`)**: *Cyclopean Megalith Rampart* — Interlocking mortise-and-tenon granite blocks.
5. **Purifier (`purifier`)**: *Seismic Crystallization Spire* — Low-frequency harmonic resonator vitrifying corrupt terrain.
6. **Doctrinal Units**:
   - *Juggernaut Colossus* (Heavy, 260 HP): Walking granite megalith with molten core that shrugs off crossfire.

---

## 7. Zephyrian Nomads (`zephyrian`)
* **Archetype:** Sky Nomads / Atmospheric Agility
* **Base Color:** `#38bdf8` (Sky Blue, White Composite & Carbon Fiber)
* **Materials:** Aerodynamic composite fairings, woven carbon-fiber hydrofoils, cyan repulsor rings, holographic solar sails.
* **In-Engine Status:** Base Concept Art Complete; Kit specifications ready.
* **Gameplay Trait:** 30% complete attack evasion chance, units move 15% faster.

### Zephyrian Kit:
| Base | Turret | Harvester | Wall | Purifier | Storm Skimmer |
| :---: | :---: | :---: | :---: | :---: | :---: |
| ![Base](../assets/concept_art/zephyrian_flagship.jpg) | *(Generating)* | *(Generating)* | *(Generating)* | *(Generating)* | *(Generating)* |

1. **Base (`base`)**: *Aerodynamic Sky Spire* — Arrowhead composite tower with solar hydrofoil masts and air docking bays.
2. **Turret (`turret`)**: *Sonic Vortex Cannon* — Fluid acceleration turbine firing focused atmospheric shockwaves.
3. **Extractor (`harvester`)**: *Ionic Atmospheric Condenser* — Inverted funnel collecting charged stratospheric ion streams.
4. **Wall (`wall`)**: *Kinetic Flow Deflector* — Aerodynamic winglet panels deflecting incoming projectiles with compressed wind curtains.
5. **Purifier (`purifier`)**: *Ozone Tempest Disperser* — High-velocity fan dispersing ozone micro-cyclones.
6. **Doctrinal Units**:
   - *Storm Skimmer* (Light, 70 HP): High-speed atmospheric skimmer bypassing ground terrain obstacles.

---

## 8. Umbral Parasites (`umbral`)
* **Archetype:** Void Entities / Cosmic Corruption
* **Base Color:** `#831843` (Deep Burgundy, Glassy Obsidian & Crimson)
* **Materials:** Razor-sharp obsidian crystals, weeping viscous dark matter, necrotic tentacles, pulsing eldritch eye cores.
* **In-Engine Status:** Base Concept Art Complete; Kit specifications ready.
* **Gameplay Trait:** +0.5 E/s per controlled corrupt node, 30% chance to reanimate fallen enemy units as void parasites.

### Umbral Kit:
| Base | Turret | Harvester | Wall | Purifier | Void Infestor |
| :---: | :---: | :---: | :---: | :---: | :---: |
| ![Base](../assets/concept_art/umbral_flagship.jpg) | *(Generating)* | *(Generating)* | *(Generating)* | *(Generating)* | *(Generating)* |

1. **Base (`base`)**: *Void Eye Obelisk* — Levitation obelisk of obsidian shards surrounding a colossal dark cosmic eye core.
2. **Turret (`turret`)**: *Umbral Spine Tentacle* — Retractable biomechanical tendril bursting from the earth to impale targets.
3. **Extractor (`harvester`)**: *Parasitic Drain Node* — Fleshy pustule rooted into the core consuming planetary energy into corruption.
4. **Wall (`wall`)**: *Void Cyst Barrier* — Interconnected dark pustules weeping caustic necrotic filaments.
5. **Purifier (`purifier`)**: *Entropic Reality Sink* — Sub-spatial singularity absorbing anomalies into sterile void.
6. **Doctrinal Units**:
   - *Void Infestor* (Heavy, 110 HP): Tentacled horror spreading corruption along its path and reanimating the fallen.
