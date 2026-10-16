# Home Assistant sur macOS : statut et options

> **Ce projet est communautaire et non officiel.** Il ne s'agit pas d'une méthode d'installation prise en charge par Home Assistant.

Depuis Home Assistant 2025.12, les méthodes Core (application Python/venv) et Supervised ne sont plus officiellement prises en charge. Elles peuvent encore fonctionner et recevoir des versions, mais l'équipe Home Assistant n'accepte plus les rapports de problèmes propres à ces méthodes. Les méthodes officiellement prises en charge sont Home Assistant OS et Home Assistant Container. Référence : [annonce officielle](https://www.home-assistant.io/blog/2025/05/22/deprecating-core-and-supervised-installation-methods-and-32-bit-systems/).

## Ce que propose ce dépôt

Ce projet est un emballage communautaire de Home Assistant Core dans un environnement Python macOS, lancé par `launchd`. Il peut servir à l'expérimentation ou au développement sur Mac, mais ne transforme pas Core en méthode officiellement supportée, ne fournit pas Supervisor/Add-ons, et ne garantit pas une disponibilité 24/7. La mise en veille, les redémarrages, les changements de Python/macOS, les autorisations matérielles, ou les dépendances natives peuvent interrompre le service.

Home Assistant 2026.10.2 exige Python 3.14.2 ou supérieur selon ses métadonnées de version. Le build utilise désormais `uv` et un runtime CPython redistribuable `python-build-standalone`, au lieu du Python système du Mac. Les dépendances natives et l'exécution finale restent à valider sur du matériel macOS réel pour chaque architecture.

## Retour de la communauté sur le fil lié

Le fil du [forum Home Assistant](https://community.home-assistant.io/t/native-macos-standalone-installer-pkg-for-home-assistant-no-docker-no-vms/1009745) signale notamment le blocage Gatekeeper dû à l'absence de signature/notarisation. Les réponses rappellent aussi qu'un Mac de bureau n'est pas toujours un hôte disponible en permanence. Les participants évoquent comme usages plus adaptés un environnement d'essai ou de développement. Ce sont des retours d'utilisateurs, pas une validation technique du paquet.

## Recommandations

- Pour une instance principale et durable, choisissez Home Assistant OS ou Container sur un hôte pris en charge.
- Pour essayer ce paquet, sauvegardez régulièrement toute la configuration et testez restauration/mise à niveau avant de vous y fier.
- Ne contournez jamais Gatekeeper pour un paquet dont la provenance et l'intégrité ne sont pas vérifiées. Les scripts de signature/notarisation de ce dépôt nécessitent des certificats Apple et doivent être testés avant distribution.
- Validez les versions macOS, architectures Intel/Apple Silicon, Bluetooth, réseau, upgrades et désinstallation sur de vrais Macs. Le projet ne publie pas de matrice de tests tant que ces essais n'ont pas été exécutés.