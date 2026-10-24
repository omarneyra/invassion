# Pipeline de Generación 3D Industrial (Concept Art a Modelos PBR en AWS SageMaker)

Este documento detalla el procedimiento técnico completo y reproducible para convertir ilustraciones 2D de arte conceptual en modelos 3D reales optimizados (`.glb` / glTF 2.0) con texturas PBR completas (Albedo, Normal Map, Roughness) utilizando inteligencia artificial generativa sobre hardware acelerado en AWS.

---

## 1. Arquitectura y Stack Tecnológico

* **Motor Base de Generación 3D:** [Stable Fast 3D (SF3D)](https://github.com/Stability-AI/stable-fast-3d) de Stability AI.
* **Infraestructura Cloud:** AWS SageMaker (Notebook / Studio).
* **Instancia Recomendada:** `ml.g5.xlarge`
  * **GPU:** 1x NVIDIA A10G (24 GB VRAM Ampere).
  * **vCPU / RAM:** 4 vCPUs / 16 GB RAM.
  * **Almacenamiento Scratch:** Disco NVMe efímero de alta velocidad (~232 GB) montado en `/mnt/sagemaker-nvme`.
  * **Costo por Hora:** ~\$1.408 USD/hora (en `us-east-1`).
  * **Rendimiento:** ~1.08 a 2.10 segundos por modelo 3D (lote completo de 100 piezas en ~3 minutos).
* **Motor de Destino:** Godot 4.3 (soporte nativo glTF con compresión de texturas VRAM).

---

## 2. Preparación de las Imágenes de Entrada

Las imágenes deben ser ilustraciones 2D en formato `.jpg` o `.png` organizadas por facción/raza:

```text
assets/concept_art/
├── solarian/
├── krynn/
├── nexus/
├── titanforge/
├── umbral/
├── zephyrian/
├── vorash/
└── aethelian/
```

Para transferirlas a SageMaker en un solo archivo comprimido:

```bash
python3 -c "
import zipfile, glob, os
factions = ['solarian', 'krynn', 'nexus', 'titanforge', 'umbral', 'zephyrian', 'vorash', 'aethelian']
with zipfile.ZipFile('all_factions_concept_art.zip', 'w', zipfile.ZIP_DEFLATED) as zf:
    for f in factions:
        for img in glob.glob(f'assets/concept_art/{f}/*.jpg'):
            zf.write(img, f'{f}/{os.path.basename(img)}')
"
```

---

## 3. Configuración del Entorno en AWS SageMaker

### 3.1. Clonar el Repositorio e Instalar Dependencias

Abre una **Terminal** en JupyterLab / SageMaker Studio y ejecuta:

```bash
cd ~
git clone https://github.com/Stability-AI/stable-fast-3d.git
cd stable-fast-3d

# Dependencias Python de IA y geometría
python -m pip install torch torchvision transformers open_clip_torch huggingface-hub \
    einops jaxtyping omegaconf trimesh gpytoolbox rembg onnxruntime-gpu pynanoinstantmeshes

# Compilación de extensiones CUDA locales (OBLIGATORIO: usar --no-build-isolation)
python -m pip install ./texture_baker/ --no-build-isolation
python -m pip install ./uv_unwrapper/ --no-build-isolation
```

> [!IMPORTANT]
> Los módulos `./texture_baker/` y `./uv_unwrapper/` son extensiones nativas en C++/CUDA. Si no se usa la bandera `--no-build-isolation`, `pip` intentará compilar en un entorno aislado sin PyTorch y fallará con `ModuleNotFoundError: torch`.

---

## 4. Gestión de Almacenamiento y Autenticación

### 4.1. Solución al Límite de Disco en SageMaker (EBS 5GB)
Por defecto, la carpeta `/home/sagemaker-user` en SageMaker tiene una cuota pequeña (~5 GB). Los pesos del modelo ocupan ~5.8 GB combinados, lo que provoca `RuntimeError: No space left on device (os error 28)`.

Para solucionarlo, se redirige el directorio de caché de Hugging Face al disco NVMe efímero de 232 GB:

```bash
# Limpiar descargas parciales y redirigir
rm -rf ~/.cache/huggingface/hub
export HF_HOME=/mnt/sagemaker-nvme/huggingface
```

### 4.2. Autenticación en Hugging Face (Licencia Gated)
El modelo `stabilityai/stable-fast-3d` requiere aceptar la licencia comunitaria de Stability AI:

1. Iniciar sesión en [Hugging Face](https://huggingface.co/) y acceder a [huggingface.co/stabilityai/stable-fast-3d](https://huggingface.co/stabilityai/stable-fast-3d).
2. Hacer clic en **"Agree and access repository"** (gratuito).
3. Crear un Access Token de tipo **Read** en [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens).
4. Autenticar en la terminal de SageMaker:
   ```bash
   huggingface-cli login --token TU_TOKEN_AQUI
   ```

---

## 5. Script de Validación Técnica Pre-Inferencia

Antes de lanzar generación por lote, ejecuta este script para validar que el 100% de los subsistemas y CUDA estén operativos:

```bash
python -c "
modules = [
    ('PyTorch (CUDA)', lambda: __import__('torch').cuda.is_available()),
    ('Trimesh (Geometría)', lambda: __import__('trimesh')),
    ('Rembg (Segmentación)', lambda: __import__('rembg')),
    ('Transformers & Clip', lambda: __import__('transformers') and __import__('open_clip')),
    ('Gpytoolbox', lambda: __import__('gpytoolbox')),
    ('Texture Baker (CUDA)', lambda: __import__('texture_baker')),
    ('UV Unwrapper', lambda: __import__('uv_unwrapper')),
    ('Pynanoinstantmeshes', lambda: __import__('pynanoinstantmeshes')),
    ('SF3D Core Engine', lambda: getattr(__import__('sf3d.system', fromlist=['SF3D']), 'SF3D')),
]

all_ok = True
for name, check in modules:
    try:
        res = check()
        if name == 'PyTorch (CUDA)' and not res:
            print(f'[-] {name:<25} ERROR: CUDA no detectado')
            all_ok = False
        else:
            print(f'[+] {name:<25} OK')
    except Exception as e:
        print(f'[-] {name:<25} FALLÓ: {e}')
        all_ok = False

if all_ok:
    print('>>> ENTORNO 100% OPERATIVO <<<')
else:
    print('>>> FALTAN COMPONENTES <<<')
"
```

---

## 6. Generación Automatizada por Lote (`batch_generate.py`)

Crea y ejecuta el siguiente script en la carpeta `~/stable-fast-3d` de SageMaker para procesar todas las facciones y empaquetar los modelos `.glb` finales:

```python
import os
import glob
import subprocess
import zipfile

# 1. Descomprimir lote si existe el zip
zip_name = "all_factions_concept_art.zip"
for possible_path in [f"../{zip_name}", f"./{zip_name}"]:
    if os.path.exists(possible_path) and not os.path.exists("./input_factions"):
        print(f"Descomprimiendo {possible_path}...")
        subprocess.run(["unzip", "-q", "-o", possible_path, "-d", "./input_factions"])
        break

factions = ['solarian', 'krynn', 'nexus', 'titanforge', 'umbral', 'zephyrian', 'vorash', 'aethelian']
os.makedirs("./output_all", exist_ok=True)

all_images = []
for f in factions:
    imgs = glob.glob(f"./input_factions/{f}/*.jpg") or glob.glob(f"./input_factions/*/{f}/*.jpg")
    for img in sorted(imgs):
        all_images.append((f, img))

print(f"Total de imágenes encontradas: {len(all_images)}")

for idx, (faction, img_path) in enumerate(all_images, 1):
    base_name = os.path.splitext(os.path.basename(img_path))[0]
    out_dir = f"./output_all/{faction}"
    os.makedirs(out_dir, exist_ok=True)
    target_glb = f"{out_dir}/{base_name}.glb"
    
    if os.path.exists(target_glb):
        print(f"[{idx}/{len(all_images)}] Omitiendo (ya existe): {faction}/{base_name}")
        continue
        
    print(f"[{idx}/{len(all_images)}] Procesando: {faction} -> {base_name}...")
    temp_dir = f"./output_temp_{idx}"
    subprocess.run(["python", "run.py", img_path, "--output-dir", temp_dir])
    
    src_glb = f"{temp_dir}/0/mesh.glb"
    if os.path.exists(src_glb):
        os.rename(src_glb, target_glb)
        subprocess.run(["rm", "-rf", temp_dir])

print("\nEmpaquetando todos los modelos en output_models_all.zip...")
with zipfile.ZipFile("output_models_all.zip", "w", zipfile.ZIP_DEFLATED) as zf:
    for root, _, files in os.walk("./output_all"):
        for file in files:
            if file.endswith(".glb"):
                full_p = os.path.join(root, file)
                rel_p = os.path.relpath(full_p, "./output_all")
                zf.write(full_p, rel_p)

print("\n>>> PROCESO FINALIZADO CON ÉXITO <<<")
```

Ejecución:
```bash
python batch_generate.py
```

---

## 7. Despliegue en el Proyecto Godot

1. Descargar `output_models_all.zip` desde SageMaker a tu equipo local.
2. Descomprimir directamente sobre la carpeta de modelos de Godot:
   ```bash
   unzip -o ~/Downloads/output_models_all.zip -d /home/xor/Proyectos/invassion/assets/models/
   ```
3. Estructura resultante en Godot:
   ```text
   assets/models/
   ├── solarian/
   ├── krynn/
   ├── nexus/
   ├── titanforge/
   ├── umbral/
   ├── zephyrian/
   ├── vorash/
   └── aethelian/
   ```
4. Godot 4.3 detectará automáticamente los nuevos archivos `.glb`, comprimirá las texturas a VRAM (`S3TC/ETC/BPTC`) y asignará los mapas de normales y rugosidad sin requerir configuración manual adicional.

---

## 8. Control de Costos

* **Tiempo de Cómputo Total:** ~3 minutos de GPU para ~100 assets.
* **Costo Estimado de Ejecución:** ~\$0.07 USD.
* **Buenas Prácticas:** Detener la instancia (`Actions -> Stop`) inmediatamente después de descargar el archivo comprimido para evitar cobros de tiempo inactivo.
