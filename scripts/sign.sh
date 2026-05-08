#!/bin/bash
# Script de signature code pour Home Assistant Desktop macOS
# Nécessite un certificat développeur Apple valide

set -e

# Configuration
PKG_PATH="dist/HomeAssistant-macos.pkg"
SIGNED_PKG_PATH="dist/HomeAssistant-macos-signed.pkg"
DEVELOPER_ID="${DEVELOPER_ID:-}"

# Vérification du certificat
if [ -z "$DEVELOPER_ID" ]; then
    echo "❌ Aucun certificat développeur spécifié"
    echo "Usage: DEVELOPER_ID='Developer ID Installer: Votre Nom' ./scripts/sign.sh"
    exit 1
fi

# Vérification du package
if [ ! -f "$PKG_PATH" ]; then
    echo "❌ Package non trouvé: $PKG_PATH"
    echo "Exécutez d'abord: python3 create_web_pkg.py"
    exit 1
fi

echo "🔐 Signature du package avec: $DEVELOPER_ID"

# Signature du package
productsign \
    --sign "$DEVELOPER_ID" \
    "$PKG_PATH" \
    "$SIGNED_PKG_PATH"

if [ $? -eq 0 ]; then
    echo "✅ Package signé avec succès: $SIGNED_PKG_PATH"
    
    # Vérification de la signature
    echo "🔍 Vérification de la signature..."
    spctl -a -v "$SIGNED_PKG_PATH"
    
    # Remplacement du package original
    mv "$SIGNED_PKG_PATH" "$PKG_PATH"
    echo "✅ Package signé et prêt pour la notarisation"
else
    echo "❌ Échec de la signature"
    exit 1
fi
