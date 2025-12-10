#!/bin/bash
# Script para iniciar el Nodo 1 de IceGrid (MediaServer)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
CONFIG_DIR="$PROJECT_DIR/config"

echo "=== Iniciando IceGrid Node 1 (MediaServer) ==="
echo "Directorio de configuración: $CONFIG_DIR"

# Crear directorios necesarios
mkdir -p "$PROJECT_DIR/node1_data"
mkdir -p "$PROJECT_DIR/node1_output"

# Iniciar el nodo
icegridnode --Ice.Config="$CONFIG_DIR/node1.config"
