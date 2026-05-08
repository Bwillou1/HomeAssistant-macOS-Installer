# Home Assistant Desktop for macOS - Guide d'Installation

## Vue d'ensemble

Home Assistant Desktop for macOS est une application native qui transforme votre Mac en un hôte Home Assistant de niveau production, avec une intégration système complète et des performances optimisées.

## Configuration Requise

### Système
- **macOS** : 12.0+ (Monterey ou supérieur)
- **Architecture** : Intel x86_64 ou Apple Silicon M1/M2/M3
- **Mémoire** : 4GB minimum (8GB recommandés)
- **Stockage** : 2GB espace disponible
- **Permissions** : Administrateur requis

### Réseau
- Accès réseau local pour la découverte d'appareils
- Port 8123 disponible pour l'interface web
- Accès Bluetooth pour les appareils IoT

## Méthodes d'Installation

### 1. Installation via Package .pkg (Recommandé)

```bash
# Téléchargement du package
wget https://github.com/homeassistant/homeassistant-macos/releases/latest/download/HomeAssistant-macOS.pkg

# Installation
sudo installer -pkg HomeAssistant-macOS.pkg -target /
```

### 2. Installation depuis les Sources

```bash
# Clonage du dépôt
git clone https://github.com/homeassistant/homeassistant-macos.git
cd homeassistant-macos

# Build et installation
make all
sudo make install
```

### 3. Installation Manuelle

```bash
# Installation dépendances
pip3 install -r requirements.txt

# Build binaire
pyinstaller --onefile --target-arch universal2 src/main.py

# Copie des fichiers
sudo cp dist/main /usr/local/bin/homeassistant-macos
sudo cp launchd/org.homeassistant.daemon.plist /Library/LaunchDaemons/
sudo launchctl load -w /Library/LaunchDaemons/org.homeassistant.daemon.plist
```

## Processus d'Installation

### 1. Vérification Système
L'installateur vérifie automatiquement :
- Version de macOS (12.0+ requis)
- Architecture supportée (Intel/Apple Silicon)
- Espace disque disponible (2GB+)
- Permissions administrateur

### 2. Installation des Composants
- **Binaire Universal 2** : `/usr/local/bin/homeassistant-macos`
- **LaunchDaemon** : `/Library/LaunchDaemons/org.homeassistant.daemon.plist`
- **Configuration** : `/Library/Application Support/HomeAssistant/`
- **Logs** : `/Library/Logs/HomeAssistant/`

### 3. Configuration des Permissions
L'installateur configure automatiquement :
- **Permissions TCC** : Bluetooth et LocalNetwork
- **Firewall** : Règles pour mDNS (port 5353 UDP)
- **Sandbox** : Profil de sécurité restrictif
- **Bonjour** : Service de découverte réseau

### 4. Démarrage du Service
Le service démarre automatiquement après l'installation :
- **Interface Web** : http://localhost:8123
- **Découverte** : homeassistant.local (Bonjour)
- **Logs** : `/Library/Logs/HomeAssistant/daemon.log`

## Configuration Post-Installation

### Accès à l'Interface

1. Ouvrez votre navigateur web
2. Naviguez vers `http://localhost:8123`
3. Créez votre compte utilisateur
4. Configurez vos intégrations

### Fichiers de Configuration

- **Configuration principale** : `/Library/Application Support/HomeAssistant/config/configuration.yaml`
- **Personnalisation** : `/Library/Application Support/HomeAssistant/config/custom_components/`
- **Automatisations** : `/Library/Application Support/HomeAssistant/config/automations.yaml`
- **Scènes** : `/Library/Application Support/HomeAssistant/config/scenes.yaml`

### Intégrations macOS

L'installation inclut les intégrations natives :
- **Capteurs système** : CPU, mémoire, disque, réseau
- **Bluetooth** : Appareils IoT Bluetooth
- **Bonjour** : Découverte automatique réseau
- **Notifications** : Notifications système macOS

## Gestion du Service

### Démarrage/Arrêt

```bash
# Démarrer le service
sudo launchctl load -w /Library/LaunchDaemons/org.homeassistant.daemon.plist

# Arrêter le service
sudo launchctl unload -w /Library/LaunchDaemons/org.homeassistant.daemon.plist

# Redémarrer le service
sudo launchctl unload -w /Library/LaunchDaemons/org.homeassistant.daemon.plist
sudo launchctl load -w /Library/LaunchDaemons/org.homeassistant.daemon.plist
```

### Vérification du Statut

```bash
# Vérifier si le service tourne
sudo launchctl list | grep homeassistant

# Vérifier les processus
ps aux | grep homeassistant

# Vérifier les ports
lsof -i :8123
```

### Logs

```bash
# Logs en temps réel
tail -f /Library/Logs/HomeAssistant/daemon.log

# Logs d'erreurs
tail -f /Library/Logs/HomeAssistant/daemon.error.log

# Logs Home Assistant
tail -f /Library/Logs/HomeAssistant/home-assistant.log
```

## Dépannage

### Problèmes Communs

#### Service ne démarre pas
```bash
# Vérifier les logs
sudo cat /Library/Logs/HomeAssistant/daemon.log

# Vérifier les permissions
sudo launchctl list | grep homeassistant

# Redémarrer manuellement
sudo /usr/local/bin/homeassistant-macos --debug
```

#### Permissions refusées
```bash
# Réinitialiser les permissions TCC
sudo tccutil reset All

# Redémarrer pour appliquer les changements
sudo reboot
```

#### Accès réseau impossible
```bash
# Vérifier le firewall
sudo pfctl -sr | grep 8123

# Vérifier Bonjour
dns-sd -B _home-assistant._tcp local.
```

#### Interface web inaccessible
```bash
# Vérifier le port
netstat -an | grep 8123

# Vérifier la configuration
cat /Library/Application\ Support/HomeAssistant/config/configuration.yaml
```

### Mode Debug

```bash
# Démarrage en mode debug
sudo /usr/local/bin/homeassistant-macos --debug --log-level debug

# Logs détaillés
export HASS_DEBUG=1
sudo /usr/local/bin/homeassistant-macos
```

## Mise à Jour

### Automatique
Home Assistant Desktop se met à jour automatiquement :
- Vérification quotidienne des mises à jour
- Téléchargement et installation silencieuse
- Redémarrage automatique du service

### Manuelle
```bash
# Arrêt du service
sudo launchctl unload -w /Library/LaunchDaemons/org.homeassistant.daemon.plist

# Téléchargement et installation du nouveau package
sudo installer -pkg HomeAssistant-macOS-new.pkg -target /

# Redémarrage
sudo launchctl load -w /Library/LaunchDaemons/org.homeassistant.daemon.plist
```

## Désinstallation

### Automatique
```bash
# Script de désinstallation inclus
sudo /Library/Application\ Support/HomeAssistant/scripts/uninstall
```

### Manuelle
```bash
# Arrêt du service
sudo launchctl unload -w /Library/LaunchDaemons/org.homeassistant.daemon.plist

# Suppression des fichiers
sudo rm -f /usr/local/bin/homeassistant-macos
sudo rm -f /Library/LaunchDaemons/org.homeassistant.daemon.plist
sudo rm -rf /Library/Application\ Support/HomeAssistant
sudo rm -rf /Library/Logs/HomeAssistant
```

## Sécurité

### Signatures et Notarisation
- **Signature Code** : Certificat développeur Apple
- **Notarisation** : Vérification par Apple
- **Sandbox** : Isolation des processus
- **Permissions** : Contrôle d'accès granulaire

### Réseau
- **mDNS** : Découverte locale sécurisée
- **HTTPS** : Support SSL/TLS
- **Firewall** : Règles restrictives
- **VPN** : Compatible avec les VPN

## Support

### Documentation Complète
- [Documentation officielle](https://www.home-assistant.io)
- [Intégrations macOS](https://www.home-assistant.io/integrations/)
- [Communauté](https://community.home-assistant.io/)

### Rapports de Bugs
- [Issues GitHub](https://github.com/homeassistant/homeassistant-macos/issues)
- Logs requis : `/Library/Logs/HomeAssistant/`
- Informations système : `sw_vers && uname -a`

### Communauté
- [Discord Home Assistant](https://discord.gg/homeassistant)
- [Forum](https://community.home-assistant.io/)
- [Reddit](https://reddit.com/r/homeassistant)
