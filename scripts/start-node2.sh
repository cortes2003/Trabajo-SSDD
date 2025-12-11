#!/bin/bash
# Script para iniciar el Nodo 2 de IceGrid (MediaRender)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
CONFIG_DIR="$PROJECT_DIR/config"

echo "=== Iniciando IceGrid Node 2 (MediaRender) ==="
echo "Directorio de configuración: $CONFIG_DIR"

# Crear directorios necesarios
mkdir -p "$PROJECT_DIR/node2_data"
mkdir -p "$PROJECT_DIR/node2_output"

# Iniciar el nodo en background
icegridnode --Ice.Config="$CONFIG_DIR/node2.config" > /dev/null 2>&1 &

# Guardar PID y esperar
NODE_PID=$!
sleep 2

# Verificar que esté corriendo
if pgrep -f "icegridnode.*node2" > /dev/null; then
    echo "✓ Node 2 iniciado (PID: $NODE_PID)"
else
    echo "✗ Error: Node 2 no se inició"
    exit 1
fi
