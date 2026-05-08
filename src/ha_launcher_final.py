#!/usr/bin/env python3
"""
Home Assistant Desktop for macOS - Launcher final optimisé
Utilise Python système avec Home Assistant installé.
"""

import subprocess
import sys
from pathlib import Path

def main():
    """Lance Home Assistant avec Python système."""
    
    # Configuration
    config_dir = Path("/Library/Application Support/HomeAssistant/config")
    log_dir = Path("/Library/Logs/HomeAssistant")
    
    # Créer les répertoires avec permissions correctes
    try:
        config_dir.mkdir(parents=True, exist_ok=True)
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # Configuration par défaut si elle n'existe pas
        config_file = config_dir / "configuration.yaml"
        if not config_file.exists():
            default_config = """# Home Assistant Configuration
homeassistant:
  name: Maison
  country: FR
  language: fr
  time_zone: Europe/Paris

default_config:

logger:
  default: info
"""
            config_file.write_text(default_config, encoding='utf-8')
        
        print("✓ Répertoires et configuration prêts")
    except PermissionError:
        # Fallback utilisateur
        config_dir = Path.home() / "Library/Application Support/HomeAssistant/config"
        log_dir = Path.home() / "Library/Logs/HomeAssistant"
        config_dir.mkdir(parents=True, exist_ok=True)
        log_dir.mkdir(parents=True, exist_ok=True)
        print("✓ Répertoires utilisateur créés")
    
    # Lancer Home Assistant avec module Python
    cmd = [
        sys.executable, "-m", "homeassistant",
        "--config", str(config_dir),
        "--log-file", str(log_dir / "home-assistant.log"),
        "--log-rotate-days", "7",
        "--open-ui",  # Ouvrir l'interface
    ]
    
    print(f"Lancement Home Assistant: {' '.join(cmd)}")
    
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Erreur lancement Home Assistant: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("Arrêt demandé par l'utilisateur")
        sys.exit(0)

if __name__ == "__main__":
    main()
