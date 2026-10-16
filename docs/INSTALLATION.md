# Installation macOS

## Téléchargement et Gatekeeper

Téléchargez le fichier `.pkg` correspondant à l'architecture de votre Mac (`arm64` pour Apple Silicon ou `x86_64` pour Intel) depuis les [releases de ce dépôt](https://github.com/Bwillou1/HomeAssistant-macOS-Installer/releases). Le paquet refuse l'installation sur la mauvaise architecture ou une version de macOS antérieure à 13.0. Le paquet actuel n'est pas signé/notarié par défaut; macOS peut le refuser. Ne désactivez pas Gatekeeper globalement. N'installez le paquet que si vous faites confiance à sa source et, idéalement, vérifiez son empreinte publiée. Une distribution signée requiert un certificat Apple Developer ID Installer et une notarisation.

Installez ensuite le paquet avec l'installateur macOS (ou `sudo installer -pkg HomeAssistant-macOS-*.pkg -target /`). Le service utilise `/opt/homeassistant`, la configuration `/Library/Application Support/HomeAssistant/config` et les journaux `/Library/Logs/HomeAssistant`.

Ouvrez `http://localhost:8123` pour terminer la configuration initiale. Le premier démarrage peut prendre plusieurs minutes. Pour les intégrations qui utilisent le transcodage, installez aussi FFmpeg sur le Mac hôte (`brew install ffmpeg`); FFmpeg n'est pas inclus dans le paquet.

## Service et journaux

```sh
sudo launchctl print system/org.homeassistant.daemon
sudo launchctl kickstart -k system/org.homeassistant.daemon
sudo launchctl bootout system /Library/LaunchDaemons/org.homeassistant.daemon.plist
 tail -f /Library/Logs/HomeAssistant/daemon.error.log
```

Le LaunchDaemon est chargé automatiquement à l'installation. La configuration existante n'est pas remplacée lors d'une mise à niveau.

## Désinstallation

```sh
sudo /opt/homeassistant/uninstall --keep-config
```

Par défaut, le script préserve configuration et journaux. Pour les supprimer, utilisez `--remove-config` et confirmez en saisissant `REMOVE`. En mode automatisé, `--remove-config --non-interactive` rend cette suppression explicite sans prompt. Le compte système restreint est conservé pour éviter de supprimer un compte préexistant portant le même nom.

## Mise à jour de Core

Un LaunchDaemon vérifie chaque jour à 04 h 30 (heure locale, Mac éveillé et connecté) la dernière version stable de Home Assistant Core publiée sur PyPI. Il prépare une nouvelle venv séparée, vérifie la configuration, sauvegarde `config` (y compris `.storage` et la base SQLite), puis bascule le service; si le service ne répond pas, l'ancienne venv est restaurée. Les sauvegardes locales sont stockées dans `/Library/Application Support/HomeAssistant-Backups` et conservées 30 jours. Elles ne remplacent pas une sauvegarde hors du Mac.

Pour lancer la mise à jour immédiatement: `sudo /opt/homeassistant/update`. Journaux: `/Library/Logs/HomeAssistant-Installer/updater.log` et `updater.error.log`. Pour désactiver l'automatisation: `sudo launchctl disable system/org.homeassistant.updater && sudo launchctl bootout system/org.homeassistant.updater`; pour la réactiver: `sudo launchctl enable system/org.homeassistant.updater && sudo launchctl bootstrap system /Library/LaunchDaemons/org.homeassistant.updater.plist`.

La mise à jour nécessite Internet et le Python embarqué. Si une future version exige une version de Python plus récente, le processus échoue sans remplacer la version installée; il faudra installer une nouvelle version du paquet. Les mises à jour dynamiques depuis PyPI comportent un risque résiduel malgré le contrôle de configuration, la sauvegarde et le retour arrière. Home Assistant Core natif n'est pas une méthode officiellement prise en charge.

Pour mettre à jour le runtime Python ou le contenu du paquet lui-même, installez un nouveau `.pkg` par-dessus l'installation existante; les données dans `/Library/Application Support/HomeAssistant` sont conservées.

## Dépannage

- Statut: `sudo launchctl print system/org.homeassistant.daemon`
- Sortie du service: `/Library/Logs/HomeAssistant/daemon.log` et `daemon.error.log`
- Journal Home Assistant: `/Library/Logs/HomeAssistant/home-assistant.log`
- Si le service ne démarre pas, vérifiez la configuration YAML et les permissions, puis redémarrez avec `launchctl kickstart`.

Le service limité à un compte système peut ne pas avoir accès aux périphériques Bluetooth/USB ou aux autorisations TCC d'une session utilisateur macOS. Ce n'est pas automatiquement résolu par l'installation.