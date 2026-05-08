#!/usr/bin/env python3
"""
Home Assistant Desktop for macOS - Version simplifiée
Lancement direct de Home Assistant sans wrapper complexe.
"""

import os
import sys
from pathlib import Path

def main():
    """Lance Home Assistant directement avec configuration minimale."""
    
    # Configuration de base
    config_dir = Path("/Library/Application Support/HomeAssistant/config")
    log_dir = Path("/Library/Logs/HomeAssistant")
    
    # Créer les répertoires si nécessaire
    try:
        config_dir.mkdir(parents=True, exist_ok=True)
        log_dir.mkdir(parents=True, exist_ok=True)
        print(f"✓ Répertoires créés: {config_dir}, {log_dir}")
    except Exception as e:
        # Fallback vers les répertoires utilisateur
        config_dir = Path.home() / "Library/Application Support/HomeAssistant/config"
        log_dir = Path.home() / "Library/Logs/HomeAssistant"
        config_dir.mkdir(parents=True, exist_ok=True)
        log_dir.mkdir(parents=True, exist_ok=True)
        print(f"✓ Répertoires utilisateur créés: {config_dir}, {log_dir}")
    
    # Configuration environnement Home Assistant
    os.environ["HA_CONFIG"] = str(config_dir)
    os.environ["HA_LOG_FILE"] = str(log_dir / "home-assistant.log")
    
    print(f"Configuration Home Assistant:")
    print(f"  Config: {config_dir}")
    print(f"  Log: {log_dir / 'home-assistant.log'}")
    
    # Lancement de Home Assistant
    try:
        from homeassistant.__main__ import main as ha_main
        
        # Arguments pour Home Assistant
        sys.argv = [
            "homeassistant",
            "--config", str(config_dir),
            "--log-file", str(log_dir / "home-assistant.log"),
            "--log-rotate-days", "7",
            "--debug",
        ]
        
        print("Démarrage Home Assistant...")
        ha_main()
        
    except ImportError as e:
        print(f"Erreur import Home Assistant: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Erreur démarrage Home Assistant: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
