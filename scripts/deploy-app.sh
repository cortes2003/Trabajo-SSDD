#!/bin/bash
# Script para desplegar la aplicación Spotifice en IceGrid

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
CONFIG_DIR="$PROJECT_DIR/config"

echo "=== Desplegando aplicación Spotifice en IceGrid ==="

# Esperar a que el registry esté listo
sleep 2

# Desplegar la aplicación usando icegridadmin
icegridadmin --Ice.Default.Locator="SpotificeGrid/Locator:tcp -h localhost -p 4061" \
  -e "application add '$CONFIG_DIR/application.xml'"

if [ $? -eq 0 ]; then
    echo "✓ Aplicación desplegada exitosamente"
    echo ""
    echo "Para ver el estado de la aplicación:"
    echo "  icegridadmin --Ice.Default.Locator='SpotificeGrid/Locator:tcp -h localhost -p 4061' -e 'application describe SpotificeApp'"
else
    echo "✗ Error al desplegar la aplicación"
    exit 1
fi
