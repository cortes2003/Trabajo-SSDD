#!/bin/bash
# Script maestro para iniciar toda la infraestructura IceGrid

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "==================================="
echo "  Iniciando Spotifice con IceGrid"
echo "==================================="

# Función para verificar si un proceso está corriendo
check_process() {
    pgrep -f "$1" > /dev/null
    return $?
}

# Limpiar procesos anteriores
echo "Limpiando procesos anteriores..."
pkill -f icegridregistry 2>/dev/null
pkill -f icegridnode 2>/dev/null
sleep 2

# 1. Iniciar Registry
echo ""
echo "[1/4] Iniciando Registry..."
"$SCRIPT_DIR/start-registry.sh" &
REGISTRY_PID=$!
sleep 3

if check_process "icegridregistry"; then
    echo "✓ Registry iniciado (PID: $REGISTRY_PID)"
else
    echo "✗ Error: Registry no pudo iniciarse"
    exit 1
fi

# 2. Iniciar Node 1
echo ""
echo "[2/4] Iniciando Node 1..."
"$SCRIPT_DIR/start-node1.sh" &
NODE1_PID=$!
sleep 2

if check_process "icegridnode.*node1"; then
    echo "✓ Node 1 iniciado (PID: $NODE1_PID)"
else
    echo "✗ Error: Node 1 no pudo iniciarse"
    exit 1
fi

# 3. Iniciar Node 2
echo ""
echo "[3/4] Iniciando Node 2..."
"$SCRIPT_DIR/start-node2.sh" &
NODE2_PID=$!
sleep 2

if check_process "icegridnode.*node2"; then
    echo "✓ Node 2 iniciado (PID: $NODE2_PID)"
else
    echo "✗ Error: Node 2 no pudo iniciarse"
    exit 1
fi

# 4. Desplegar aplicación
echo ""
echo "[4/4] Desplegando aplicación..."
"$SCRIPT_DIR/deploy-app.sh"

if [ $? -eq 0 ]; then
    echo ""
    echo "==================================="
    echo "  ✓ IceGrid iniciado correctamente"
    echo "==================================="
    echo ""
    echo "PIDs de procesos:"
    echo "  Registry: $REGISTRY_PID"
    echo "  Node 1:   $NODE1_PID"
    echo "  Node 2:   $NODE2_PID"
    echo ""
    echo "Para detener todo: ./scripts/stop-all.sh"
    echo "Para monitorear: tail -f node*_output/*.log"
else
    echo "✗ Error al desplegar la aplicación"
    exit 1
fi
