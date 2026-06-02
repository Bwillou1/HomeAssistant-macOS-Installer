#!/bin/bash
# Script de notarisation Apple pour Home Assistant Desktop macOS
# Nécessite un Apple ID et un certificat développeur valide

set -e

# Configuration
PKG_PATH="dist/HomeAssistant-macos.pkg"
APPLE_ID="${APPLE_ID:-}"
APPLE_PASSWORD="${APPLE_PASSWORD:-}"
TEAM_ID="${TEAM_ID:-}"

# Vérification des identifiants
if [ -z "$APPLE_ID" ] || [ -z "$APPLE_PASSWORD" ] || [ -z "$TEAM_ID" ]; then
    echo "❌ Identifiants Apple manquants"
    echo "Usage: APPLE_ID='votre@email.com' APPLE_PASSWORD='app-password' TEAM_ID='ABC123' ./scripts/notarize.sh"
    exit 1
fi

# Vérification du package
if [ ! -f "$PKG_PATH" ]; then
    echo "❌ Package non trouvé: $PKG_PATH"
    echo "Exécutez d'abord: ./scripts/sign.sh"
    exit 1
fi

echo "🔐 Soumission pour notarisation..."

# Soumission pour notarisation
RESULT=$(xcrun altool \
    --notarize-app \
    --primary-bundle-id "org.homeassistant.desktop" \
    --username "$APPLE_ID" \
    --password "$APPLE_PASSWORD" \
    --asc-provider "$TEAM_ID" \
    --file "$PKG_PATH" \
    --output-format json)

# Extraction du UUID de la requête
REQUEST_UUID=$(echo "$RESULT" | jq -r '."notarization-upload".RequestUUID')

if [ "$REQUEST_UUID" = "null" ] || [ -z "$REQUEST_UUID" ]; then
    echo "❌ Échec de la soumission"
    echo "$RESULT"
    exit 1
fi

echo "✅ Soumission réussie - UUID: $REQUEST_UUID"
echo "⏳ Vérification du statut..."

# Attente et vérification du statut
while true; do
    sleep 30
    
    STATUS_RESULT=$(xcrun altool \
        --notarization-info "$REQUEST_UUID" \
        --username "$APPLE_ID" \
        --password "$APPLE_PASSWORD" \
        --output-format json)
    
    STATUS=$(echo "$STATUS_RESULT" | jq -r '."notarization-info".Status')
    
    echo "📊 Statut: $STATUS"
    
    case "$STATUS" in
        "Success")
            echo "✅ Notarisation réussie!"
            
            # Téléchargement du ticket de notarisation
            echo "$STATUS_RESULT" | jq -r '."notarization-info".LogFileURL'
            
            # Stapling du ticket au package
            xcrun stapler staple "$PKG_PATH"
            echo "✅ Ticket de notarisation appliqué au package"
            
            # Vérification finale
            spctl -a -v "$PKG_PATH"
            echo "🎯 Package prêt pour distribution!"
            break
            ;;
        "Invalid")
            echo "❌ Notarisation invalide"
            echo "$STATUS_RESULT"
            exit 1
            ;;
        "in progress")
            echo "⏳ Notarisation en cours..."
            continue
            ;;
        *)
            echo "⚠️ Statut inconnu: $STATUS"
            echo "$STATUS_RESULT"
            sleep 60
            continue
            ;;
    esac
done
