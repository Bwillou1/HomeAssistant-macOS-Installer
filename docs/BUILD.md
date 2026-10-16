# Construire le paquet macOS

Le build nécessite macOS, les outils Xcode Command Line Tools (`pkgbuild`, `productbuild`) et `uv` 0.10.8 ou ultérieur. La CI installe également FFmpeg et les outils de compilation natifs utilisés par les dépendances Home Assistant.

```sh
xcode-select --install
brew install uv ffmpeg autoconf cmake
make all
```

`uv` télécharge depuis Astral `python-build-standalone` le runtime CPython 3.14.8 redistribuable correspondant à l'architecture du Mac, l'installe dans l'arborescence du paquet, construit un venv relocatable et y installe les dépendances épinglées. Le script `scripts/relocate_venv.py` corrige le chemin de base du venv vers le chemin final `/opt/homeassistant` et vérifie ses liens Python. Ne construisez pas un paquet sur une architecture en supposant qu'il fonctionnera sur l'autre.

Le fichier `.pkg` est généré dans `dist/` avec l'architecture dans son nom. Le choix de la mauvaise architecture et macOS < 13 sont refusés par l'installateur. Le build inspecte son payload avec `pkgutil`. La CI effectue les builds macOS sur Intel et Apple Silicon et tente une installation de bout en bout; un test réussi sur les runners n'élimine pas la nécessité d'un test sur un Mac physique propre.

Pour distribution publique, signer avec Developer ID Installer et notariser le paquet. Voir `scripts/sign.sh` et `scripts/notarize.sh`; ces opérations nécessitent des identifiants Apple Developer configurés localement. Vérifier la signature, le ticket et le Gatekeeper avant de publier.
