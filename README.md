<h1 align="center">HomeAssistant-macOS-Installer</h1>

<div align="center">

<p><i>Relocatable, native Home Assistant Core installer and launchd background daemon for modern macOS.</i></p>

[![macOS](https://img.shields.io/badge/macOS-13.0%2B%20%7C%20Sonoma%20%7C%20Sequoia-000000?style=for-the-badge&logo=apple&logoColor=white)](https://apple.com)
[![Apple Silicon](https://img.shields.io/badge/Apple%20Silicon-M1--M4%20Native-grey?style=for-the-badge&logo=apple&logoColor=white)](https://apple.com)
[![Intel](https://img.shields.io/badge/Intel-x86__64-informational?style=for-the-badge&logo=apple&logoColor=white)](https://apple.com)
[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-Core%202026.10-41BDF5?style=for-the-badge&logo=home-assistant&logoColor=white)](https://home-assistant.io)
[![Python](https://img.shields.io/badge/Python-3.14-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Release](https://img.shields.io/badge/Release-v3.1.0-success?style=for-the-badge)](https://github.com/rhythmcreative/HomeAssistant-macOS-Installer/releases)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue?style=for-the-badge)](LICENSE)

</div>

___

[![Typing SVG](https://readme-typing-svg.herokuapp.com?font=Fira+Code&size=23&pause=1000&color=F7F7F7&vCenter=true&width=435&height=30&lines=ABOUT)](https://git.io/typing-svg)

A modernized, standalone macOS installer package (`.pkg`) for **Home Assistant Core**. It packages a completely self-contained Python runtime and deploys Home Assistant as a native Darwin background daemon (`launchd`) without Docker, virtual machines, or modifying your system Python installation.

Includes a fully redesigned, human-crafted installer interface complying with Apple's Human Interface Guidelines (SF Pro typography and adaptive Light/Dark mode).

___

[![Typing SVG](https://readme-typing-svg.herokuapp.com?font=Fira+Code&size=23&pause=1000&color=F7F7F7&vCenter=true&width=435&height=30&lines=FEATURES)](https://git.io/typing-svg)

- **Zero External Dependencies**: Bundles isolated CPython 3.14 runtime via `uv` beside a relocatable virtual environment.
- **Native macOS Installer UI**: Clean, authentic Apple Installer panes with adaptive light and dark mode, replacing tacky AI-generated templates.
- **Unprivileged Dedicated Service**: Runs strictly under a sandboxed `_homeassistant` system user (`UserShell: /usr/bin/false`, `IsHidden: 1`, disabled password auth).
- **Apple Silicon & Intel Universal Support**: Native builds optimized for Apple Silicon (M1/M2/M3/M4, `arm64`) and Intel (`x86_64`) Macs on macOS 13+ (Ventura, Sonoma, Sequoia).
- **Transactional Core Updates**: Automated daily checks at 04:30. Staged in an isolated virtual environment, validated with pre-flight configuration checks, and safely rolled back if startup validation fails.
- **Hardware Acceleration Ready**: Configured with Apple VideoToolbox hardware acceleration flags for camera and video streaming integrations.
- **Automated Configuration Backups**: Automatic rolling 30-day snapshot backups in `/Library/Application Support/HomeAssistant-Backups` created before every update.

___

[![Typing SVG](https://readme-typing-svg.herokuapp.com?font=Fira+Code&size=23&pause=1000&color=F7F7F7&vCenter=true&width=435&height=30&lines=SECURITY)](https://git.io/typing-svg)

- **Least Privilege Execution**: The `launchd` daemon executes under a dedicated unprivileged daemon account (`_homeassistant`) with `Umask 027` (files never world-readable).
- **Immutable Code Directory**: `/opt/homeassistant` is strictly owned by `root:wheel` (`chmod -R go-w`). The service account cannot modify binary or application files, mitigating privilege escalation.
- **Protected Configuration & Secrets**: Configuration files (`/Library/Application Support/HomeAssistant`) and log outputs are restricted to `_homeassistant` (`chmod 750` / `640`), preventing other local macOS user accounts from reading tokens or databases.
- **Disabled Interactive Login**: The `_homeassistant` service account is provisioned with a disabled password (`Password: *`) and disabled authentication authority tags.

___

[![Typing SVG](https://readme-typing-svg.herokuapp.com?font=Fira+Code&size=23&pause=1000&color=F7F7F7&vCenter=true&width=435&height=30&lines=INSTALLATION)](https://git.io/typing-svg)

1. Download the latest **`HomeAssistant-macOS-3.1.0-arm64.pkg`** (or `x86_64.pkg`) from [Releases](https://github.com/rhythmcreative/HomeAssistant-macOS-Installer/releases/tag/v3.1.0).
2. Double-click the `.pkg` file and follow the standard macOS installation wizard.
3. If macOS Gatekeeper presents an unsigned developer warning:
   - **Finder**: Right-click (or Control + Click) the `.pkg` file and choose **Open**.
   - **Terminal**: Remove the quarantine flag:
     ```bash
     xattr -d com.apple.quarantine ~/Downloads/HomeAssistant-macOS-*.pkg
     ```
   - **Direct Terminal Install**:
     ```bash
     sudo installer -pkg ~/Downloads/HomeAssistant-macOS-*.pkg -target /
     ```
4. Once completed, navigate to **`http://localhost:8123`** in Safari or Chrome to complete initial onboarding (allow 30-60 seconds for initial bootstrap).

___

[![Typing SVG](https://readme-typing-svg.herokuapp.com?font=Fira+Code&size=23&pause=1000&color=F7F7F7&vCenter=true&width=435&height=30&lines=MANAGEMENT)](https://git.io/typing-svg)

### System Paths

| Component | Filesystem Location |
| :--- | :--- |
| **Runtime & Venv** | `/opt/homeassistant` |
| **Configuration & SQLite DB** | `/Library/Application Support/HomeAssistant/config` |
| **Daemon Logs** | `/Library/Logs/HomeAssistant/home-assistant.log` |
| **LaunchDaemon Plist** | `/Library/LaunchDaemons/org.homeassistant.daemon.plist` |
| **Snapshot Backups** | `/Library/Application Support/HomeAssistant-Backups` |

### Service Control

```bash
# Check service status
sudo launchctl print system/org.homeassistant.daemon

# Restart Home Assistant daemon
sudo launchctl kickstart -k system/org.homeassistant.daemon

# Follow live logs
tail -f "/Library/Logs/HomeAssistant/home-assistant.log"
```

### Manual Update & Rollback

```bash
# Trigger an immediate transactional update to latest stable Core
sudo /opt/homeassistant/update

# Inspect updater log
tail -n 100 /Library/Logs/HomeAssistant-Installer/updater.log
```

### Uninstallation

```bash
# Remove runtime & LaunchDaemon while preserving your configuration & database
sudo /opt/homeassistant/uninstall --keep-config

# Or completely remove all files including configurations and history
sudo /opt/homeassistant/uninstall --remove-config
```

___

[![Typing SVG](https://readme-typing-svg.herokuapp.com?font=Fira+Code&size=23&pause=1000&color=F7F7F7&vCenter=true&width=435&height=30&lines=BUILD+FROM+SOURCE)](https://git.io/typing-svg)

```bash
# Install build prerequisites
brew install uv ffmpeg

# Clone repository
git clone https://github.com/rhythmcreative/HomeAssistant-macOS-Installer.git
cd HomeAssistant-macOS-Installer

# Build relocatable runtime and generate .pkg
make package
```

___

<div align="center">

<p>Made with ❤️ from rhythmcreative.</p>

</div>
