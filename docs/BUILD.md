# Home Assistant Desktop for macOS - Guide de Build

## Vue d'ensemble

Ce document décrit comment compiler et packager Home Assistant Desktop for macOS depuis les sources.

## Prérequis

### Système de Build
- **macOS** : 12.0+ (Monterey ou supérieur)
- **Python** : 3.11+ (recommandé 3.13)
- **Xcode** : Outils de développement ligne de commande
- **Git** : Pour la gestion des sources

### Outils Requis
```bash
# Installation via Homebrew (recommandé)
brew install python3 pyinstaller pkgbuild

# Vérification des versions
python3 --version  # 3.11+
pyinstaller --version  # 6.0+
```

## Processus de Build

### 1. Clonage des Sources
```bash
git clone https://github.com/homeassistant/homeassistant-macos.git
cd homeassistant-macos
```

### 2. Installation des Dépendances
```bash
# Installation automatique via Makefile
make deps

# Installation manuelle
python3 -m pip install -r requirements.txt
```

### 3. Configuration de l'Environnement
```bash
# Vérification de l'architecture
export ARCH=$(uname -m)
echo "Architecture: $ARCH"

# Configuration pour PyInstaller
export PYTHONPATH=$(pwd)/src:$PYTHONPATH
```

### 4. Build du Binaire
```bash
# Build complet
make all

# Build uniquement
make build

# Build avec debug
make DEBUG=1 build
```

### 5. Création du Package
```bash
# Package .pkg
make package

# Package avec signature
make sign DEVELOPER_ID="Developer ID Installer: Votre Nom"

# Package complet avec notarisation
make notarize APPLE_ID="votre@email.com" APPLE_PASSWORD="app-password" TEAM_ID="ABC123DEF"
```

## Architecture du Build

### Structure des Répertoires
```
homeassistant-macos/
├── src/                    # Code source
│   ├── main.py           # Point d'entrée principal
│   ├── bonjour_manager.py # Gestionnaire Bonjour
│   └── hooks/            # Hooks PyInstaller
├── launchd/               # Configuration système
│   └── org.homeassistant.daemon.plist
├── scripts/               # Scripts d'installation
│   ├── postinstall       # Post-installation
│   ├── preinstall        # Pré-installation
│   └── uninstall         # Désinstallation
├── pkg/                  # Ressources package
│   ├── Distribution.xml   # Configuration installateur
│   └── resources/        # Fichiers ressources
├── config/               # Configuration par défaut
│   └── default_config.yaml
├── build/                # Fichiers build temporaires
└── dist/                 # Binaires finaux
```

### Étapes du Build

#### Phase 1: Préparation
1. **Nettoyage** : Suppression des builds précédents
2. **Dépendances** : Installation des packages Python
3. **Configuration** : Préparation de l'environnement

#### Phase 2: Compilation
1. **Analyse** : PyInstaller analyse le code
2. **Collecte** : Rassemblement des dépendances
3. **Empaquetage** : Création du binaire

#### Phase 3: Packaging
1. **Préparation** : Création de la structure package
2. **Assemblage** : Génération du .pkg
3. **Signature** : Code signing et notarisation

## Configuration PyInstaller

### Fichier Spec
Le fichier `homeassistant-macos.spec` configure :

- **Analyse** : Dépendances et imports cachés
- **Données** : Fichiers de configuration et ressources
- **Hooks** : Personnalisation pour macOS
- **Architecture** : Support Intel et Apple Silicon

### Hooks Personnalisés
- `macos-hook.py` : Configuration environnement macOS
- `hook-cryptography.py` : Bibliothèques OpenSSL
- `hook-pillow.py` : Support images
- `hook-sqlalchemy.py` : Base de données

## Gestion des Architectures

### Universal 2
Le build crée un binaire compatible :
- **Intel x86_64** : Mac Intel et Rosetta 2
- **Apple Silicon** : Mac M1/M2/M3 natif

### Vérification
```bash
# Vérification architecture
file dist/homeassistant-macos
# Sortie attendue: Mach-O universal binary with 2 architectures

# Test sur les deux architectures
arch -x86_64 dist/homeassistant-macos --version
arch -arm64 dist/homeassistant-macos --version
```

## Dépannage du Build

### Problèmes Communs

#### Dépendances Manquantes
```bash
# Erreur: ModuleNotFoundError
make deps  # Réinstaller les dépendances

# Vérification manuelle
python3 -c "import homeassistant; print('OK')"
```

#### Erreurs PyInstaller
```bash
# Nettoyage complet
make clean
make build

# Build détaillé
pyinstaller --log-level DEBUG src/main.py
```

#### Problèmes d'Architecture
```bash
# Vérification architecture système
uname -m
arch

# Build forcé pour architecture
make build ARCH=x86_64
make build ARCH=arm64
```

#### Permissions Build
```bash
# Permissions sur les scripts
chmod +x scripts/*.sh

# Permissions sur les binaires
chmod +x dist/homeassistant-macos
```

## Tests Automatisés

### Tests Unitaires
```bash
# Tests du code source
python3 -m pytest tests/

# Tests du binaire
make test
```

### Tests d'Intégration
```bash
# Installation test
sudo installer -pkg dist/HomeAssistant-macos.pkg -target /tmp/test

# Vérification installation
/tmp/test/usr/local/bin/homeassistant-macos --version
```

### Tests de Performance
```bash
# Benchmark démarrage
time /tmp/test/usr/local/bin/homeassistant-macos --start

# Test mémoire
memory_pressure --level warning /tmp/test/usr/local/bin/homeassistant-macos &
```

## Optimisations

### Build Rapide
```bash
# Build parallèle
make -j$(sysctl -n hw.ncpu) build

# Cache pip
export PIP_CACHE_DIR=/tmp/pip-cache
make deps
```

### Taille Optimisée
```bash
# Compression UPX
export UPX=1
make build

# Strip symbols
export STRIP=1
make build
```

### Débogage
```bash
# Mode debug
export DEBUG=1
export HASS_DEBUG=1
make build

# Logs détaillés
make build 2>&1 | tee build.log
```

## Publication

### Versioning
```bash
# Configuration version
export VERSION=$(git describe --tags --always)
export BUILD_NUMBER=$(git rev-list --count HEAD)

# Génération numéro de version
echo "${VERSION}-${BUILD_NUMBER}"
```

### Release Automation
```bash
# Build release complet
make clean all

# Création archive sources
git archive --format zip --output homeassistant-macos-${VERSION}.zip HEAD

# Génération checksums
shasum -a 256 dist/HomeAssistant-macos.pkg > checksums.txt
```

## Intégration CI/CD

### GitHub Actions
```yaml
name: Build and Release
on: [push, pull_request]
jobs:
  build:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        run: |
          python3 -m pip install --upgrade pip
          python3 -m pip install -r requirements.txt
      - name: Build
        run: make all
      - name: Test
        run: make test
      - name: Package
        run: make package
```

### Variables d'Environnement
```bash
# Développement
export HASS_ENV=development
export HASS_DEBUG=1

# Production
export HASS_ENV=production
export HASS_CONFIG_PATH=/config
```

## Ressources Supplémentaires

### Documentation
- [PyInstaller Documentation](https://pyinstaller.readthedocs.io/)
- [macOS LaunchDaemons](https://developer.apple.com/library/archive/documentation/NetworkingInternet/Conceptual/Bonjour_and_IP_Networking_Prog_Guide/Chapters/Chapter_5_Network_Service_Discovery.html)
- [Apple Package Maker](https://developer.apple.com/documentation/technologies/packaging-apps-for-the-mac-app-store/)

### Outils Utiles
```bash
# Analyse de binaires
otool -L dist/homeassistant-macos

# Vérification signatures
codesign -dv dist/homeassistant-macos

# Analyse package
pkgutil --expand dist/HomeAssistant-macos.pkg /tmp/expanded
```

## Support

Pour toute question sur le processus de build :
- Issues GitHub : https://github.com/homeassistant/homeassistant-macos/issues
- Documentation : https://github.com/homeassistant/homeassistant-macos/wiki
- Communauté : https://community.home-assistant.io/
