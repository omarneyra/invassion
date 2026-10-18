#!/bin/bash
set -e
echo "=========================================="
echo " Compilando 'invassion' a WebAssembly..."
echo "=========================================="
GODOT_BIN="godot"
if ! command -v godot &> /dev/null; then
    if [ -f "./bin/godot" ]; then
        GODOT_BIN="./bin/godot"
    elif [ -f "$HOME/.local/bin/godot" ]; then
        GODOT_BIN="$HOME/.local/bin/godot"
    fi
fi

mkdir -p build/web
$GODOT_BIN --headless --path . --export-release "Web" build/web/index.html
echo "=========================================="
echo " Compilación exitosa en build/web/"
echo " Para probar en tu navegador ejecuta:"
echo " python3 -m http.server -d build/web 8080"
echo " y abre http://localhost:8080"
echo "=========================================="
