# Git Workflow & Release Standards

This document establishes the official branching model, commit conventions, versioning policy, and language standards for the **invassion** project.

---

## 1. Branching Strategy (Git Flow)

The repository follows a streamlined Git Flow model:

```mermaid
gitGraph
    commit id: "v0.7.0" tag: "v0.7.0"
    branch develop
    checkout develop
    commit id: "develop-init"
    branch feature/rebalance-turrets
    checkout feature/rebalance-turrets
    commit id: "feat: turret stats"
    commit id: "test: focus fire"
    checkout develop
    merge feature/rebalance-turrets id: "merge-feature"
    checkout master
    merge develop id: "v0.8.0" tag: "v0.8.0"
```

### 1.1 Core Branches
* **`master`**: Production-ready, stable releases. Code here is always verified, passes 100% of the unit test suite, and runs natively without regressions. Every release merged into `master` is tagged with a Semantic Version (`vMAJOR.MINOR.PATCH`). Direct commits to `master` are strictly prohibited.
* **`develop`**: Primary integration branch. All completed and verified feature/fix branches are merged here first. Continuous testing takes place against this branch.

### 1.2 Supporting Branches
* **`feature/<feature-name>`**: Branched from `develop`. Used for new gameplay systems, UI improvements, AI logic, or architectural capabilities (e.g., `feature/starcraft-hud`, `feature/turret-focus-fire`).
* **`fix/<fix-name>`**: Branched from `develop` (or `master` for hotfixes). Used for bug resolutions, combat balance tweaks, and edge-case fixes.
* **`chore/<chore-name>`**: Branched from `develop`. Used for tooling, test suite expansion, documentation updates, and repository maintenance.

---

## 2. Commit Policy & Conventional Commits

* **Frequency**: Commits must be made whenever an atomic, coherent unit of work is completed and verified (e.g., test written + implementation passing).
* **Format**: All commit messages must follow the [Conventional Commits](https://www.conventionalcommits.org/) specification strictly in **English**:
  * `feat:` A new feature or gameplay capability.
  * `fix:` A bug fix or balance adjustment.
  * `test:` Adding, updating, or refactoring unit tests.
  * `refactor:` Code restructuring without behavioral changes (e.g., pure procedural refactors).
  * `docs:` Documentation additions or updates (`README.md`, `GDD.md`, etc.).
  * `chore:` Build scripts, configurations, or repository maintenance.
  * `perf:` Performance optimizations (framerate, math calculations).

**Examples:**
* `feat: implement smart RTS focus-fire targeting for defensive turrets`
* `fix: prevent surviving buildings from staying active after base destruction`
* `test: add unit test for base defensive battery engagement`
* `docs: translate game design document and framework specifications to English`

---

## 3. Semantic Versioning (SemVer)

The project adheres to [Semantic Versioning 2.0.0](https://semver.org/) (`MAJOR.MINOR.PATCH`):

1. **`MAJOR`**: Breaking architectural changes, incompatible savegame format overhauls, or complete engine paradigm migrations.
2. **`MINOR`**: Backwards-compatible additions of new gameplay systems, races, technologies, AI capabilities, or full HUD overhauls.
3. **`PATCH`**: Backwards-compatible bug fixes, balance stat tweaks, formula adjustments, and test coverage additions.

* The active version is tracked in the single-source-of-truth file [`VERSION`](file:///home/xor/Proyectos/invassion/VERSION).
* Release tags on `master` match the format `vMAJOR.MINOR.PATCH` (e.g., `v0.7.0`, `v0.7.1`).

---

## 4. Promotion & Pull Request (PR) Lifecycle

1. **Start Feature**: Branch off latest `develop`:
   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b feature/your-feature-name
   ```
2. **Develop & Test**: Implement changes following pure procedural architecture and write unit tests immediately. Validate with `./run_tests.sh`.
3. **Commit**: Make atomic, clean commits in English.
4. **Merge to `develop`**: When feature is verified and tests pass:
   ```bash
   git checkout develop
   git merge --no-ff feature/your-feature-name -m "merge: feature/your-feature-name into develop"
   git branch -d feature/your-feature-name
   ```
5. **Release to `master`**: When a milestone is ready for release:
   - Bump `VERSION` according to SemVer.
   - Merge `develop` into `master`.
   - Tag the release commit: `git tag -a vX.Y.Z -m "Release vX.Y.Z"`.

---

## 5. Strict Language Standard

* **100% English in Git**: Every artifact committed to the repository must be written in English. This includes:
  * Commit titles and descriptions.
  * Branch names.
  * Pull request titles, descriptions, and comments.
  * Documentation (`README.md`, `GDD.md`, `FRAMEWORK.md`, `ROADMAP.md`, `GIT_WORKFLOW.md`).
  * Code comments, docstrings, variable names, and unit test descriptions.
* Interactive pair-programming conversation with the user may remain in Spanish per user preference, but all Git operations and repository files are strictly English.
