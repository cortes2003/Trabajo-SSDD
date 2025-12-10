#!/bin/bash
# Script para detener todos los componentes de IceGrid

echo "=== Deteniendo IceGrid ==="

# Detener la aplicación
echo "Deteniendo aplicación Spotifice..."
icegridadmin --Ice.Default.Locator="SpotificeGrid/Locator:tcp -h localhost -p 4061" \
  -e "application remove SpotificeApp" 2>/dev/null

# Apagar los nodos
echo "Apagando nodos..."
icegridadmin --Ice.Default.Locator="SpotificeGrid/Locator:tcp -h localhost -p 4061" \
  -e "node shutdown node1" 2>/dev/null
icegridadmin --Ice.Default.Locator="SpotificeGrid/Locator:tcp -h localhost -p 4061" \
  -e "node shutdown node2" 2>/dev/null

# Apagar el registry
echo "Apagando registry..."
icegridadmin --Ice.Default.Locator="SpotificeGrid/Locator:tcp -h localhost -p 4061" \
  -e "registry shutdown SpotificeGrid" 2>/dev/null

sleep 2
echo "✓ IceGrid detenido"
