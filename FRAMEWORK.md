# Marco de Trabajo: Desarrollo de Juego 3D en Navegador

Este documento establece las decisiones técnicas, arquitectura, metodología y estándares de desarrollo para el proyecto de juego 3D en navegador.

---

## 1. Pila Tecnológica y Plataforma Web

### 1.1 Ejecución en Navegador (Estado del Arte)
* **WebAssembly (Wasm):** Núcleo de ejecución de CPU. Compilación nativa desde C++/Rust o el motor (Godot), permitiendo velocidad cercana al código nativo sin recolección de basura de JS.
* **WebGPU / WebGL 2:**
  * **WebGPU:** Estándar moderno de bajo nivel (Vulkan/Metal/D3D12) con soporte de *Compute Shaders* y reducción drástica de overhead de *draw calls*.
  * **WebGL 2 (Fallback):** Renderer *Compatibility* de Godot para compatibilidad universal con navegadores antiguos o móviles.
* **Wasm Threads & SharedArrayBuffer:** Permite ejecución multihilo real en Web Workers (requiere configuración de headers `COOP` y `COEP` en el servidor).
* **OPFS (Origin Private File System):** Almacenamiento local de alta velocidad para cachear assets binarios (mallas, texturas, audio) sin requerir re-descargas.

### 1.2 Pipeline de Assets para Web
* **Texturas:** Compresión GPU universal **Basis Universal (KTX2)** para reducir uso de RAM y VRAM.
* **Geometría 3D:** Formato `glTF` / `GLB` optimizado con **Meshoptimizer** o compresión **Draco**.

---

## 2. Paradigma de Programación y Arquitectura de Código

Se rechaza el OOP clásico profundo (árboles de herencia, estado mutable encapsulado y métodos acoplados) en favor de un **enfoque pragmático orientado a datos y funciones puras**.

### 2.1 Modelo Híbrido: Desacoplamiento Lógica vs. Presentación

* **Capa de Presentación (Godot - Mínimo OOP):** Nodos (`Node3D`, `MeshInstance3D`, `Camera3D`) y controladores de inputs/colisiones físicas del motor. Actúan como vistas pasivas.
* **Capa de Lógica del Juego (Funciones Puras + Datos Planos):** Estados planos en diccionarios/structs y módulos de cálculo puro (combate, movimiento, spawn, economía).
* **Suite de Testing:** Unit tests ejecutados en milisegundos en modo *headless* sin necesidad de inicializar gráficos o escenas.

### 2.2 Principios de Diseño
1. **Datos Planos:** Estados de entidades representados como estructuras simples (`Dictionary` o estructuras tipo struct), serializables y sin métodos internos ocultos.
2. **Funciones Puras:** Las reglas del juego se definen como `static func calcular_x(estado, parametros) -> nuevo_estado`.
3. **Nodos Pasivos:** Los nodos de Godot (`Node3D`, `CharacterBody3D`) reciben inputs, consultan la lógica y reflejan la posición/animación en pantalla.

---

## 3. Metodología de Desarrollo Asistida por IA

El flujo de trabajo aprovecha la IA como copiloto y generador de pruebas bajo un ciclo iterativo cerrado:

1. **Definir Contrato / Firma:** Especificar datos de entrada y salida esperados.
2. **Generar Casos y Unit Tests (IA):** Cobertura de casos nominales y casos límite (*edge cases*).
3. **Implementar Función Pura:** Código procedimental simple.
4. **Validar Suite de Tests (CLI/Headless):** Ejecución inmediata hasta pase al 100%.
5. **Vincular a Escena de Godot:** Conexión con los nodos visuales.

### 3.1 Prácticas Clave
* **Spec-First:** Cada mecánica o sistema complejo se define primero en un documento Markdown conciso.
* **IA para Edge Cases:** Solicitar a la IA que genere los casos límite y tests antes o en paralelo con la lógica.
* **Cero Alucinaciones:** Limitar la IA a funciones puras sin dependencias profundas de la API gráfica.

---

## 4. Estrategia de Testing (TDD desde el Día 1)

* **Ejecución Headless:** Pruebas de lógica pura corriendo por línea de comandos o scripts de test rápidos.
* **Cobertura Prioritaria:**
  * Fórmulas matemáticas y cálculos de combate/daño.
  * Transiciones de estado (vida, muerte, cambios de fase).
  * Reglas de inventario, economía y spawn procedural.
  * Protocolos de serialización de estado para guardado o red.
