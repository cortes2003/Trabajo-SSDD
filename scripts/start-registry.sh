#!/bin/bash
# Script para iniciar el IceGrid Registry

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
CONFIG_DIR="$PROJECT_DIR/config"

echo "=== Iniciando IceGrid Registry ==="
echo "Directorio de configuración: $CONFIG_DIR"

# Crear directorio de datos si no existe
mkdir -p "$PROJECT_DIR/registry_data"

# Iniciar el registry
icegridregistry --Ice.Config="$CONFIG_DIR/registry.config"
