#!/bin/bash
# Script para desplegar la aplicación Spotifice en IceGrid

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
CONFIG_DIR="$PROJECT_DIR/config"

echo "=== Desplegando aplicación Spotifice en IceGrid ==="

# Esperar a que el registry esté listo
sleep 2

# Desplegar la aplicación enviando credenciales vacías con printf
printf '\n\n' | icegridadmin --Ice.Default.Locator="SpotificeGrid/Locator:tcp -h localhost -p 4061" \
  -e "application add '$CONFIG_DIR/application.xml'" 2>&1 | grep -v "user id:" | grep -v "password:" | grep -v "^$"

EXIT_CODE=${PIPESTATUS[1]}

if [ $EXIT_CODE -eq 0 ]; then
    echo "✓ Aplicación desplegada exitosamente"
    echo ""
    
    # Iniciar los servidores manualmente
    echo "Iniciando servidores..."
    printf '\n\n' | icegridadmin --Ice.Default.Locator="SpotificeGrid/Locator:tcp -h localhost -p 4061" \
      -e "server start MediaServer-1" 2>&1 | grep -v "user id:" | grep -v "password:" | grep -v "^$"
    
    printf '\n\n' | icegridadmin --Ice.Default.Locator="SpotificeGrid/Locator:tcp -h localhost -p 4061" \
      -e "server start MediaRender-1" 2>&1 | grep -v "user id:" | grep -v "password:" | grep -v "^$"
    
    sleep 2
    echo "✓ Servidores iniciados"
else
    echo "✗ Error al desplegar la aplicación (código: $EXIT_CODE)"
    exit 1
fi
