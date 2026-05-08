#!/bin/bash
# Script pour créer un package Universal 2 (Apple Silicon + Intel)

set -e

echo "🏗️  Construction du package Universal 2 pour Home Assistant Desktop"

# Configuration
VERSION="1.0.0"
BUILD_DIR="build"
DIST_DIR="dist"
PKG_NAME="HomeAssistant-macos-Universal"

# Nettoyage
echo "🧹 Nettoyage des builds précédents..."
rm -rf "$BUILD_DIR" "$DIST_DIR"

# Build ARM64 (Apple Silicon)
echo "🍎 Build ARM64 (Apple Silicon)..."
# Créer une copie du spec pour ARM64
sed 's/target_arch=None/target_arch="arm64"/' homeassistant-macos.spec > homeassistant-macos-arm64.spec
python3 -m PyInstaller --clean --noconfirm homeassistant-macos-arm64.spec
mv dist/homeassistant-macos "$BUILD_DIR/homeassistant-macos-arm64"

# Build x86_64 (Intel)
echo "💻 Build x86_64 (Intel)..."
# Créer une copie du spec pour Intel
sed 's/target_arch=None/target_arch="x86_64"/' homeassistant-macos.spec > homeassistant-macos-x86_64.spec
python3 -m PyInstaller --clean --noconfirm homeassistant-macos-x86_64.spec
mv dist/homeassistant-macos "$BUILD_DIR/homeassistant-macos-x86_64"

# Création du binaire Universal 2
echo "🔗 Création du binaire Universal 2..."
lipo \
    "$BUILD_DIR/homeassistant-macos-arm64" \
    "$BUILD_DIR/homeassistant-macos-x86_64" \
    -create \
    -output "$BUILD_DIR/homeassistant-macos-universal"

# Vérification
echo "🔍 Vérification de l'architecture..."
file "$BUILD_DIR/homeassistant-macos-universal"

# Copie du binaire universel
cp "$BUILD_DIR/homeassistant-macos-universal" "dist/homeassistant-macos"

# Nettoyage
rm -rf "$BUILD_DIR"

echo "✅ Build Universal 2 terminé: dist/homeassistant-macos"
