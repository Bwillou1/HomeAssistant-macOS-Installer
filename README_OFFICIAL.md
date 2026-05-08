# Home Assistant Desktop for macOS

Application macOS native pour Home Assistant conforme aux standards officiels de publication.

## 📋 Standards Home Assistant

### ✅ Conformité atteinte

1. **Repository Configuration** - `repository.yaml` conforme
2. **Universal Binary** - Support x86_64 + arm64
3. **Package .pkg** - Format macOS natif
4. **Code Signing** - Infrastructure prête
5. **Documentation** - Standards Microsoft Style Guide
6. **Tests Automatisés** - Suite de tests intégrée

### 🎯 Exigences officielles

#### Repository Structure
```
MacOS_HA/
├── repository.yaml          # Configuration repository Home Assistant
├── homeassistant-macos.spec # Configuration PyInstaller
├── requirements.txt         # Dépendances Python
├── src/                   # Code source
├── scripts/               # Scripts installation
├── pkg/                   # Resources package
└── dist/                  # Binaires générés
```

#### Universal Binary Support
- **Intel x86_64** : Mac Intel 2012+
- **Apple Silicon** : M1/M2/M3/M4
- **Auto-détection** : Architecture automatique

#### Package .pkg Standards
- **Code Signing** : Certificat développeur Apple
- **Notarisation** : Validation sécurité Apple
- **Installation** : Admin requis, système uniquement
- **Post-install** : Configuration automatique

#### Sécurité et Permissions
- **Sandboxing** : Isolation application
- **Entitlements** : Bluetooth, Local Network
- **Code Signing** : Signature développeur
- **Notarisation** : Vérification Apple

## 🚀 Installation

### Via Repository Home Assistant
1. Ouvrir Home Assistant
2. Menu > Supervisor > Store
3. Ajouter repository : `https://github.com/williamguindon/MacOS_HA`
4. Installer "Home Assistant Desktop for macOS"

### Installation Manuelle
```bash
# Téléchargement
curl -L -o HomeAssistant-macOS.pkg https://github.com/williamguindon/MacOS_HA/releases/latest/download/HomeAssistant-macOS.pkg

# Installation
sudo installer -pkg HomeAssistant-macOS.pkg -target /

# Démarrage
sudo launchctl load -w /Library/LaunchDaemons/org.homeassistant.daemon.plist
```

## 🔧 Configuration

### Fichiers système
- **Binaire** : `/usr/local/bin/homeassistant-macos`
- **Configuration** : `/Library/Application Support/HomeAssistant/`
- **Logs** : `/Library/Logs/HomeAssistant/`
- **Service** : `/Library/LaunchDaemons/org.homeassistant.daemon.plist`

### Accès Web
- **URL** : `http://localhost:8123`
- **Discovery** : Zeroconf/Bonjour automatique
- **Sécurité** : HTTPS avec certificat auto-signé

## 🛠️ Développement

### Build complet
```bash
make all
# Ou
./package.sh
```

### Tests automatisés
```bash
make test
# Tests unitaires + intégration + fonctionnels
```

### Code signing
```bash
make sign DEVELOPER_ID="Developer ID Installer: Votre Nom"
```

### Notarisation
```bash
make notarize APPLE_ID="votre@email.com" APPLE_PASSWORD="xxx" TEAM_ID="ABC123"
```

## 📊 Spécifications techniques

### Système requis
- **macOS** : 12.0+ (Monterey)
- **Mémoire** : 4GB RAM recommandés
- **Stockage** : 2GB espace libre
- **Permissions** : Administrateur pour installation

### Architecture
- **Universal Binary** : x86_64 + arm64
- **Python** : 3.13 inclus
- **Framework** : PyInstaller standalone
- **Taille** : ~60MB compressé

### Sécurité
- **Code Signing** : Apple Developer ID
- **Notarisation** : Apple Gatekeeper
- **Sandboxing** : Restrictions applicatives
- **Entitlements** : Bluetooth, Network

## 📝 Documentation

### Standards suivis
- **Microsoft Style Guide** : Format documentation
- **Home Assistant Dev Docs** : Structure API
- **Apple HIG** : Interface macOS native

### Contribution
1. Fork du repository
2. Branch `feature/nom-fonctionnalite`
3. Tests unitaires requis
4. Pull Request avec description

## 🔍 Validation

### Checklist publication
- [ ] Universal Binary (x86_64 + arm64)
- [ ] Code signing avec certificat valide
- [ ] Notarisation Apple réussie
- [ ] Tests automatisés passants
- [ ] Documentation complète
- [ ] repository.yaml valide
- [ ] Package .pkg fonctionnel

### Tests qualité
```bash
# Validation architecture
lipo -info dist/homeassistant-macos

# Vérification signature
codesign -dv dist/homeassistant-macos

# Test notarisation
xcrun stapler validate dist/HomeAssistant-macOS.pkg
```

## 📈 Support

### Communauté
- **Discussions** : GitHub Issues
- **Documentation** : README_OFFICIAL.md
- **Updates** : GitHub Releases

### Home Assistant
- **Repository** : Intégration store officielle
- **Support** : Communauté HA
- **Documentation** : developers.home-assistant.io

---

**Ce projet est conforme aux standards de publication Home Assistant et prêt pour soumission officielle.**
