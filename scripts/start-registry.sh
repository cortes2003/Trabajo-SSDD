#!/bin/bash
# Script para iniciar el IceGrid Registry

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
CONFIG_DIR="$PROJECT_DIR/config"

echo "=== Iniciando IceGrid Registry ==="
echo "Directorio de configuración: $CONFIG_DIR"

# Crear directorio de datos si no existe
mkdir -p "$PROJECT_DIR/registry_data"

# Iniciar el registry en background
icegridregistry --Ice.Config="$CONFIG_DIR/registry.config" > /dev/null 2>&1 &

# Guardar PID
REGISTRY_PID=$!
sleep 2

# Verificar que esté corriendo
if pgrep -f "icegridregistry" > /dev/null; then
    echo "✓ Registry iniciado correctamente (PID: $REGISTRY_PID)"
else
    echo "✗ Error: El Registry no se inició"
    exit 1
fi
