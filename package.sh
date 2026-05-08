#!/bin/bash
set -e

echo "Création package .pkg pour Home Assistant Desktop..."

# Configuration
VERSION="1.0.0"
DIST_DIR="dist"
BUILD_DIR="build"
PKG_NAME="HomeAssistant-macOS"
PKG_FILE="${DIST_DIR}/${PKG_NAME}-${VERSION}.pkg"

# Nettoyage
rm -rf "${DIST_DIR}"
mkdir -p "${DIST_DIR}"

# Build binaire complet avec PyInstaller
echo "Build binaire complet avec PyInstaller..."
python3 -m PyInstaller main.spec --clean --noconfirm

# Création répertoire temporaire
PKG_TEMP=$(mktemp -d)
echo "Répertoire temporaire: ${PKG_TEMP}"

# Structure package
mkdir -p "${PKG_TEMP}/pkg_root/usr/local/bin"
mkdir -p "${PKG_TEMP}/pkg_root/Library/LaunchDaemons"
mkdir -p "${PKG_TEMP}/pkg_root/Library/Application Support/HomeAssistant"
mkdir -p "${PKG_TEMP}/scripts"
mkdir -p "${PKG_TEMP}/resources"

# Copie fichiers
echo "Copie fichiers..."
cp "dist/homeassistant-macos" "${PKG_TEMP}/pkg_root/usr/local/bin/"
cp launchd/org.homeassistant.daemon.plist "${PKG_TEMP}/pkg_root/Library/LaunchDaemons/"
cp scripts/preinstall "${PKG_TEMP}/scripts/preinstall"
cp scripts/postinstall "${PKG_TEMP}/scripts/postinstall"
chmod 755 "${PKG_TEMP}/scripts/preinstall" "${PKG_TEMP}/scripts/postinstall"

# Création package
echo "Création package .pkg..."
pkgbuild \
    --root "${PKG_TEMP}/pkg_root" \
    --install-location / \
    --scripts "${PKG_TEMP}/scripts" \
    --identifier org.homeassistant.desktop \
    --version "${VERSION}" \
    --ownership preserve \
    "${DIST_DIR}/homeassistant-core.pkg"

# Package final (simple)
echo "Création package final..."
mv "${DIST_DIR}/homeassistant-core.pkg" "${PKG_FILE}"

# Nettoyage
rm -rf "${PKG_TEMP}"
rm -f "${DIST_DIR}/homeassistant-core.pkg"

echo "Package créé: ${PKG_FILE}"
ls -la "${PKG_FILE}"
