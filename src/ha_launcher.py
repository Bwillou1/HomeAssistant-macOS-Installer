#!/usr/bin/env python3
"""
Home Assistant Desktop for macOS - Launcher léger
Utilise Python système avec Home Assistant installé.
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """Lance Home Assistant avec Python système."""
    
    # Configuration
    config_dir = Path("/Library/Application Support/HomeAssistant/config")
    log_dir = Path("/Library/Logs/HomeAssistant")
    
    # Créer les répertoires
    try:
        config_dir.mkdir(parents=True, exist_ok=True)
        log_dir.mkdir(parents=True, exist_ok=True)
        print(f"✓ Répertoires système créés")
    except PermissionError:
        # Fallback utilisateur
        config_dir = Path.home() / "Library/Application Support/HomeAssistant/config"
        log_dir = Path.home() / "Library/Logs/HomeAssistant"
        config_dir.mkdir(parents=True, exist_ok=True)
        log_dir.mkdir(parents=True, exist_ok=True)
        print(f"✓ Répertoires utilisateur créés")
    
    # Lancer Home Assistant avec module Python
    cmd = [
        sys.executable, "-m", "homeassistant",
        "--config", str(config_dir),
        "--log-file", str(log_dir / "home-assistant.log"),
        "--log-rotate-days", "7",
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
