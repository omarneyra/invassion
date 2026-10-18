#!/bin/bash
set -e
echo "=========================================="
echo " Ejecutando Suite de Unit Tests (invassion)"
echo "=========================================="
python3 -m unittest discover -s tests -v
echo "=========================================="
echo " Todos los tests pasaron exitosamente."
echo "=========================================="
