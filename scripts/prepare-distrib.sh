#!/bin/bash
# Script para preparar el directorio de distribución de IcePatch2

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(dirname "$SCRIPT_DIR")"
DISTRIB_DIR="$BASE_DIR/distrib"
ICEPATCH_DIR="$BASE_DIR/icepatch"

echo "=== Preparando distribución IcePatch2 ==="

# Limpiar directorio de distribución
rm -rf "$DISTRIB_DIR"
mkdir -p "$DISTRIB_DIR"

# Copiar archivos Python necesarios
echo "Copiando archivos de aplicación..."
cp "$BASE_DIR/media_server.py" "$DISTRIB_DIR/"
cp "$BASE_DIR/media_render.py" "$DISTRIB_DIR/"
cp "$BASE_DIR/gst_player.py" "$DISTRIB_DIR/"
cp "$BASE_DIR/spotifice_v1.ice" "$DISTRIB_DIR/"

# Copiar directorios necesarios
echo "Copiando recursos..."
cp -r "$BASE_DIR/media" "$DISTRIB_DIR/" 2>/dev/null || echo "  (media no copiado - demasiado grande)"
cp -r "$BASE_DIR/playlists" "$DISTRIB_DIR/"

# Crear estructura de directorios en icepatch
echo "Preparando IcePatch2..."
rm -rf "$ICEPATCH_DIR"
mkdir -p "$ICEPATCH_DIR"

# Copiar archivos a icepatch (excluyendo media por tamaño)
rsync -av --exclude='media/' "$DISTRIB_DIR/" "$ICEPATCH_DIR/"

# Generar checksums de IcePatch2
echo "Generando checksums..."
cd "$ICEPATCH_DIR"
icepatch2calc .

echo ""
echo "✓ Distribución preparada en: $DISTRIB_DIR"
echo "✓ IcePatch2 preparado en: $ICEPATCH_DIR"
echo ""
echo "Archivos en distribución:"
find "$ICEPATCH_DIR" -type f ! -name ".*" | head -20
