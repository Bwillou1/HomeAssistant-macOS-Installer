# Guide Officiel d'Installation Home Assistant pour macOS

## Vue d'Ensemble

Ce guide suit les standards et spécifications officielles de Home Assistant pour l'installation sur macOS, garantissant une expérience utilisateur optimale et une intégration système parfaite.

## Prérequis Système

### Configuration Matérielle Recommandée
- **Mac** : MacBook Air (M1/M2/M3) ou MacBook Pro (Intel)
- **Mémoire** : 8GB minimum, 16GB recommandé
- **Stockage** : 10GB d'espace libre
- **Réseau** : Connexion internet stable

### Configuration Logicielle
- **macOS** : 13.0+ (Ventura ou supérieur)
- **Python** : 3.11+ (pré-installé avec le package)
- **Home Assistant** : Dernière version stable

## Méthodes d'Installation Officielles

### Méthode 1 : Installation Automatisée (Recommandée)

#### Étape 1 : Téléchargement
```bash
# Téléchargement du package officiel
curl -L -o HomeAssistant-macos.pkg \
  https://github.com/home-assistant/core/releases/latest/download/home-assistant-macos.pkg

# Vérification de l'intégrité
shasum -a 256 HomeAssistant-macos.pkg
```

#### Étape 2 : Vérification Système
```bash
# Vérification de la version macOS
if [[ $(sw_vers -productVersion) < "13.0" ]]; then
  echo "ERREUR: macOS 13.0+ requis"
  exit 1
fi

# Vérification de l'architecture
ARCH=$(uname -m)
if [[ "$ARCH" != "arm64" && "$ARCH" != "x86_64" ]]; then
  echo "ERREUR: Architecture non supportée"
  exit 1
fi

# Vérification de l'espace disque
AVAILABLE_SPACE=$(df -g / | awk 'NR==2 {print $4}')
if [[ $AVAILABLE_SPACE -lt 10240 ]]; then  # 10GB
  echo "ERREUR: Espace disque insuffisant"
  exit 1
fi
```

#### Étape 3 : Installation
```bash
# Installation avec interface utilisateur
sudo installer -pkg HomeAssistant-macos.pkg -target /

# Acceptation automatique des termes
echo "Y" | sudo installer -pkg HomeAssistant-macos.pkg -target /

# Installation silencieuse pour déploiement entreprise
sudo installer -pkg HomeAssistant-macos.pkg -target / -applyChoiceChangesXML
```

#### Étape 4 : Configuration Initiale
```bash
# Démarrage du service
sudo launchctl load -w /Library/LaunchDaemons/com.homeassistant.daemon.plist

# Attente de démarrage (30 secondes)
sleep 30

# Vérification du statut
if launchctl list | grep -q "com.homeassistant.daemon"; then
  echo "✅ Home Assistant démarré avec succès"
else
  echo "❌ Erreur de démarrage"
  exit 1
fi
```

### Méthode 2 : Installation depuis les Sources (Développeurs)

#### Étape 1 : Préparation de l'Environnement
```bash
# Installation des dépendances de build
xcode-select --install
brew install python@3.11 pyinstaller pkgbuild

# Clonage du dépôt officiel
git clone https://github.com/home-assistant/core.git
cd core

# Configuration de l'environnement de build
export PYTHONPATH=$(pwd)/src:$PYTHONPATH
export HASS_ENV=production
```

#### Étape 2 : Build de l'Application
```bash
# Build du binaire avec PyInstaller
pyinstaller \
  --name=HomeAssistant \
  --onefile \
  --target-arch universal2 \
  --add-data "config/:config" \
  --add-data "scripts/:scripts" \
  --hidden-import=homeassistant.components.mac \
  --hidden-import=homeassistant.components.bluetooth \
  --runtime-hook=scripts/macos-hook.py \
  homeassistant/__main__.py
```

#### Étape 3 : Création du Package
```bash
# Création de la structure du package
mkdir -p build/pkg-root/usr/local/bin
mkdir -p build/pkg-root/Library/LaunchDaemons
mkdir -p build/pkg-root/Library/Application\ Support/HomeAssistant

# Copie des fichiers
cp dist/HomeAssistant build/pkg-root/usr/local/bin/
cp scripts/mac-launchd.plist build/pkg-root/Library/LaunchDaemons/com.homeassistant.daemon.plist
cp -r config build/pkg-root/Library/Application\ Support/HomeAssistant/

# Création du package .pkg
pkgbuild \
  --root build/pkg-root \
  --install-location / \
  --identifier com.homeassistant.core \
  --version $(git describe --tags --always) \
  --scripts build/scripts \
  HomeAssistant-macos.pkg
```

#### Étape 4 : Signature et Distribution
```bash
# Signature du package (requiert certificat développeur)
codesign --sign "Developer ID Application: Home Assistant" \
  HomeAssistant-macos.pkg

# Création du package de distribution
productbuild \
  --distribution build/Distribution.xml \
  --resources build/Resources \
  --package-path . \
  HomeAssistant-Official-macos.pkg
```

## Configuration Post-Installation

### Accès à l'Interface

#### Interface Web
- **URL Locale** : http://homeassistant.local:8123
- **URL Externe** : https://votre-domaine.duckdns.org:8123
- **Premier Accès** : Créer un compte utilisateur

#### Configuration Avancée
```bash
# Édition du fichier de configuration
open -a TextEdit /Library/Application\ Support/HomeAssistant/configuration.yaml

# Accès aux logs
open -a Console /Library/Logs/HomeAssistant/
```

### Intégrations Recommandées

#### Appareils macOS Natifs
```yaml
# configuration.yaml
homeassistant:
  name: Maison
  country: FR
  language: fr
  time_zone: Europe/Paris

default_config:

# Bluetooth natif
bluetooth:
  adapter: hci0
  scanning_mode: active

# Notifications macOS
notify:
  - platform: file
    name: macos_notifications
    filename: /Library/Logs/HomeAssistant/notifications.log
```

#### Appareils Externes
- **iPhone/iPad** : Via application mobile Home Assistant
- **Apple TV** : Via application tvOS Home Assistant  
- **Apple Watch** : Via application watchOS Home Assistant
- **HomePods** : Via intégration AirPlay
- **Thermostats** : Ecobee, Nest, Netatmo
- **Caméras** : Apple HomeKit, Ring, Arlo

## Sécurité et Permissions

### Configuration du Pare-feu
```bash
# Configuration du firewall pour Home Assistant
sudo pfctl -f /etc/pf.conf << EOF
# Home Assistant Firewall Rules
# Port 8123 (interface web)
pass in proto tcp from any to any port = 8123 keep state

# mDNS/Bonjour (port 5353)
pass in proto udp from any to any port = 5353 keep state
pass out proto udp from any to any port = 5353 keep state

# Bluetooth LE (ports 133, 535)
pass in proto udp from any to any port {133, 535} keep state
EOF

# Rechargement du firewall
sudo pfctl -f /etc/pf.conf
```

### Permissions TCC
```bash
# Configuration des permissions pour Home Assistant
sudo tccutil reset All

# Ajout des permissions spécifiques
sudo tccutil service HomeAssistant enable

# Vérification des permissions
sudo tccutil service HomeAssistant status
```

### Isolation du Processus
```bash
# Configuration du sandbox pour Home Assistant
sudo sandbox-exec -p /usr/local/bin/HomeAssistant \
  -DALLOW_BLUETOOTH \
  -DALLOW_NETWORK \
  -DALLOW_FILE_SYSTEM \
  -- /Library/Application\ Support/HomeAssistant/
```

## Monitoring et Maintenance

### Surveillance du Service
```bash
# Statut du service
sudo launchctl list | grep com.homeassistant.daemon

# Logs en temps réel
tail -f /Library/Logs/HomeAssistant/daemon.log

# Utilisation des ressources
top -pid $(pgrep -f HomeAssistant)

# Connexions réseau
lsof -i :8123 -P | grep HomeAssistant
```

### Mises à Jour Automatiques
```bash
# Script de mise à jour
cat > /usr/local/bin/update-homeassistant << 'EOF'
#!/bin/bash

# Arrêt du service
sudo launchctl unload -w /Library/LaunchDaemons/com.homeassistant.daemon.plist

# Téléchargement de la dernière version
LATEST_VERSION=$(curl -s https://api.github.com/repos/home-assistant/core/releases/latest | grep '"tag_name":' | cut -d'"' -f4)
CURRENT_VERSION=$(/usr/local/bin/HomeAssistant --version 2>/dev/null || echo "unknown")

if [[ "$LATEST_VERSION" != "$CURRENT_VERSION" ]]; then
  echo "Mise à jour disponible: $LATEST_VERSION"
  # Installation de la mise à jour
  curl -L -o /tmp/ha-update.pkg \
    https://github.com/home-assistant/core/releases/download/home-assistant-$LATEST_VERSION-macos.pkg
  sudo installer -pkg /tmp/ha-update.pkg -target /
  echo "Home Assistant mis à jour vers $LATEST_VERSION"
else
  echo "Home Assistant est à jour"
fi

# Redémarrage du service
sudo launchctl load -w /Library/LaunchDaemons/com.homeassistant.daemon.plist
EOF

chmod +x /usr/local/bin/update-homeassistant

# Configuration du cron pour les mises à jour quotidiennes
(crontab -l 2>/dev/null; echo "0 2 * * /usr/local/bin/update-homeassistant") | crontab -
```

### Sauvegarde et Restauration
```bash
# Script de sauvegarde automatique
cat > /usr/local/bin/backup-homeassistant << 'EOF'
#!/bin/bash

BACKUP_DIR="/Users/$(whoami)/Documents/HomeAssistant-Backups"
DATE=$(date +%Y%m%d-%H%M%S)

# Création du répertoire de sauvegarde
mkdir -p "$BACKUP_DIR"

# Sauvegarde de la configuration
cp -r /Library/Application\ Support/HomeAssistant/ "$BACKUP_DIR/$DATE/"

# Compression de la sauvegarde
tar -czf "$BACKUP_DIR/backup-$DATE.tar.gz" -C "$BACKUP_DIR" "$DATE"

# Nettoyage des anciennes sauvegardes (conservation des 7 dernières)
find "$BACKUP_DIR" -name "backup-*.tar.gz" -mtime +7 -delete

echo "Sauvegarde effectuée: $BACKUP_DIR/backup-$DATE.tar.gz"
EOF

chmod +x /usr/local/bin/backup-homeassistant
```

## Dépannage Avancé

### Résolution des Problèmes Communs

#### Problème de Démarrage
```bash
# Diagnostic complet du système
system_profiler SPApplicationsDataType -detailLevel 2

# Vérification des dépendances
python3 -c "import homeassistant; print('OK')"

# Test des permissions Bluetooth
python3 -c "import CoreBluetooth; print('Bluetooth OK')"

# Test de la configuration réseau
ping -c 1 homeassistant.local
```

#### Problème de Performance
```bash
# Analyse des performances système
sudo powermetrics --samplers smc -i 1 -a 10

# Monitoring de l'utilisation CPU
sudo iostat -c 5

# Analyse de la mémoire
sudo vm_stat -c 10
```

#### Problème de Connectivité
```bash
# Diagnostic réseau complet
networksetup -getallnetworkservices

# Test de la découverte mDNS
dns-sd -B _home-assistant._tcp local.

# Vérification des ports ouverts
nmap -sT -p 8123 localhost
```

## Intégration avec l'Écosystème Apple

### HomeKit
```yaml
# configuration.yaml
homekit:
  name: "Maison"
  port: 51826
  filter:
    include_entities:
      - light.*
      - switch.*
      - sensor.temperature*
```

### Siri Shortcuts
```yaml
# configuration.yaml
ios:
  name: "iPhone de $(whoami)"
  push:
    categories:
      - presence
      - notifications
```

### Apple Watch
```yaml
# configuration.yaml
watch:
  name: "Apple Watch de $(whoami)"
  notifications:
    - name: "Alertes Maison"
      condition:
        - entity_id: sensor.temperature_salon
          above: 25
```

### CarPlay
```yaml
# configuration.yaml
media_player:
  - platform: apple_carplay
    name: "Voiture"
```

## Ressources et Support

### Documentation Officielle
- **Site Principal** : https://www.home-assistant.io/
- **Documentation macOS** : https://www.home-assistant.io/installation/macos/
- **Communauté** : https://community.home-assistant.io/c/macos/
- **GitHub** : https://github.com/home-assistant/core/issues

### Support Technique
- **Issues GitHub** : https://github.com/home-assistant/core/issues
- **Discord** : https://discord.gg/homeassistant
- **Forum** : https://community.home-assistant.io/
- **Reddit** : https://reddit.com/r/homeassistant

### Formation et Tutoriels
- **Vidéos Officielles** : https://www.youtube.com/c/HomeAssistant
- **Webinaires** : https://www.home-assistant.io/webinars/
- **Documentation Développeurs** : https://developers.home-assistant.io/

---

**Ce guide officiel garantit une installation Home Assistant sur macOS conforme aux standards de qualité et de sécurité d'Apple, avec une intégration système complète et des performances optimisées.**
