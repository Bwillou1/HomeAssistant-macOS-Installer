import sys
import subprocess
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest

# Ensure src is in sys.path
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.ha_launcher_final import main

@patch("src.ha_launcher_final.subprocess.run")
@patch("src.ha_launcher_final.print")
def test_successful_system_install(mock_print, mock_run):
    """Test successful installation in system directories."""
    with patch("src.ha_launcher_final.Path.mkdir") as mock_mkdir, \
         patch("src.ha_launcher_final.Path.exists") as mock_exists, \
         patch("src.ha_launcher_final.Path.write_text") as mock_write_text:

        mock_exists.return_value = False
        # We want to make sure it doesn't raise PermissionError
        mock_mkdir.return_value = None

        main()

        # Verify system paths were used
        expected_system_config = "/Library/Application Support/HomeAssistant/config"

        args, _ = mock_run.call_args
        cmd = args[0]
        assert "--config" in cmd
        config_index = cmd.index("--config")
        assert cmd[config_index + 1] == expected_system_config

        mock_print.assert_any_call("✓ Répertoires et configuration prêts")
        assert mock_mkdir.call_count == 2
        mock_write_text.assert_called_once()

@patch("src.ha_launcher_final.subprocess.run")
@patch("src.ha_launcher_final.print")
def test_permission_error_fallback(mock_print, mock_run):
    """Test fallback to user directories when system directories are not writable."""
    with patch("src.ha_launcher_final.Path.mkdir") as mock_mkdir, \
         patch("src.ha_launcher_final.Path.home") as mock_home:

        # Mock home directory
        fake_home = Path("/tmp/fakehome")
        mock_home.return_value = fake_home

        # First call to mkdir (system config) raises PermissionError
        mock_mkdir.side_effect = [PermissionError(), None, None]

        main()

        # Verify fallback paths were used in subprocess.run
        expected_user_config = str(fake_home / "Library/Application Support/HomeAssistant/config")
        expected_user_log = str(fake_home / "Library/Logs/HomeAssistant" / "home-assistant.log")

        args, _ = mock_run.call_args
        cmd = args[0]

        assert "--config" in cmd
        config_index = cmd.index("--config")
        assert cmd[config_index + 1] == expected_user_config

        assert "--log-file" in cmd
        log_index = cmd.index("--log-file")
        assert cmd[log_index + 1] == expected_user_log

        mock_print.assert_any_call("✓ Répertoires utilisateur créés")
        # 1 call for system config (fails), then 2 calls for user config and user log
        assert mock_mkdir.call_count == 3

@patch("src.ha_launcher_final.subprocess.run")
@patch("src.ha_launcher_final.print")
@patch("src.ha_launcher_final.sys.exit")
def test_subprocess_error(mock_exit, mock_print, mock_run):
    """Test handling of subprocess error."""
    with patch("src.ha_launcher_final.Path.mkdir") as mock_mkdir, \
         patch("src.ha_launcher_final.Path.exists") as mock_exists:

        mock_exists.return_value = True
        mock_run.side_effect = subprocess.CalledProcessError(1, 'cmd')

        main()

        mock_print.assert_any_call("Erreur lancement Home Assistant: Command 'cmd' returned non-zero exit status 1.")
        mock_exit.assert_called_once_with(1)
