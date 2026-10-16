# Compatibilité

## État vérifié

Le projet construit un environnement Python `venv` et l'exécutable Home Assistant Core; ce n'est ni une application macOS compilée, ni un binaire universel. Le build doit être effectué sur macOS avec la même architecture que la machine cible. Intel et Apple Silicon doivent donc être validés séparément; Rosetta ne rend pas un environnement Python natif universel.

Le build utilise maintenant un runtime CPython redistribuable `python-build-standalone`, installé par `uv`, et le place dans `/opt/homeassistant/python` à côté du venv relocatable `/opt/homeassistant/venv`. Cela supprime la dépendance au Python de l'ordinateur de build, mais ne prouve pas à lui seul que chaque extension native fonctionne sur tous les Macs. Les builds sont séparés par architecture et doivent être installés/testés sur une machine propre Intel et Apple Silicon avant publication.

La version minimale de Home Assistant est fixée dans `requirements.txt`. Les versions macOS/Python réellement prises en charge dépendent des exigences déclarées par Home Assistant et des dépendances installables sur l'OS ciblé. Le projet ne prétend pas à une validation matérielle ou système qui n'a pas été effectuée.

## Limites connues

- Les intégrations nécessitant des droits système/macOS ou des composants matériels peuvent demander des réglages supplémentaires.
- Le service s'exécute comme utilisateur système restreint; les accès Bluetooth et USB peuvent ne pas être disponibles à cet utilisateur.
- Le paquet n'est pas signé ni notarié par défaut. Gatekeeper peut bloquer son ouverture. Ne contournez les protections que si vous avez vérifié la provenance et l'intégrité du paquet. Pour une distribution publique, configurez une signature Developer ID Installer et la notarisation Apple.
- Un Mac de bureau endormi/éteint ou déconnecté du réseau ne fournit pas un hôte Home Assistant disponible en continu.

## Validation recommandée avant publication

Construire et installer sur macOS 13+ (Intel et Apple Silicon séparément), vérifier le démarrage via `launchctl`, ouvrir l'interface sur le port 8123, puis valider les journaux et la conservation de la configuration après mise à niveau. Aucune de ces plateformes n'est déclarée « testée » sans exécution réelle.