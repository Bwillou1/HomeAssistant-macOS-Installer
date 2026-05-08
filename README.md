# Home Assistant Desktop for macOS

Transformation native de macOS en hôte Home Assistant de niveau production.

## Architecture

- **LaunchDaemon système** : Exécution au boot sans session utilisateur
- **Binaire Universal 2** : Support x86_64 et arm64 natif  
- **Gestion TCC** : Permissions Bluetooth et LocalNetwork automatisées
- **Intégration Bonjour** : Découverte mDNS zeroconf
- **Package .pkg** : Installation silencieuse enterprise-ready

## Installation

```bash
# Installation via package
sudo installer -pkg HomeAssistant-macOS.pkg -target /

# Démarrage manuel
sudo launchctl load -w /Library/LaunchDaemons/org.homeassistant.daemon.plist
```

## Configuration

- Données : `/Library/Application Support/HomeAssistant/`
- Logs : `/Library/Logs/HomeAssistant/`
- Configuration : `http://localhost:8123`

## Build

```bash
make all          # Build complet
make package      # Package .pkg uniquement
make clean        # Nettoyage build
```

## Sécurité

- Signature code avec certificat développeur Apple
- Notarisation pour distribution sécurisée
- Sandbox avec entitlements spécifiques
- Gestion automatique permissions TCC

## Support

- macOS 12.0+ (Monterey)
- Intel x86_64 et Apple Silicon M1/M2/M3
- Python 3.11+ inclus dans binaire
