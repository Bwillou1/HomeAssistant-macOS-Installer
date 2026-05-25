# Home Assistant Native macOS Installer 🍏🏡
[![DOI](https://zenodo.org/badge/8475.svg)](https://zenodo.org/badge/latestdoi/8475)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Platform](https://img.shields.io/badge/Platform-macOS-lightgrey.svg)](#)
[![Version](https://img.shields.io/badge/Version-3.0.0-green.svg)](#)

A robust standalone macOS installer (`.pkg`) for the Home Assistant Server.

This project eliminates the need for Virtual Machines (VMs) or Docker containers on macOS by providing a native, stable, and fully integrated server environment.

## 🌟 Why this Installer?

Running Home Assistant on macOS usually requires complex virtualization. This introduces significant overhead and complicates access to native hardware interfaces such as Bluetooth, USB devices, and local networking (Bonjour/mDNS).

This native macOS package deploys a **Self-Contained Python Virtual Environment** directly to your system.

### Key Features
- **Zero VM Overhead:** Runs natively on your Mac.
- **True System Daemon:** Integrates with macOS `launchd` for automatic startup at boot.
- **Enhanced Security:** Runs under a dedicated, restricted background system user (`_homeassistant`) rather than `root`.
- **Isolated Environment:** Bundles a complete, isolated Python virtual environment in `/opt/homeassistant`.
- **Native Packaging:** Standard Apple Flat Package (`.pkg`) for easy installation and removal.

## 🚀 Installation

1. Download the latest `HomeAssistant-macOS-*.pkg` from the [Releases](../../releases) page.
2. **Gatekeeper Bypass:** Since this package is community-built and not yet signed by an Apple Developer ID, you may need to bypass macOS security:
   - Right-click (or Control-click) the `.pkg` file and select **Open**.
   - Alternatively, run the following in Terminal before opening:
     ```bash
     xattr -d com.apple.quarantine HomeAssistant-macOS-3.0.0.pkg
     ```
3. Follow the installer instructions.
4. Once installed, navigate to `http://localhost:8123`.

## 🛠️ Build from Source

```bash
# Clone the repository
git clone https://github.com/Bwillou1/HomeAssistant-macOS-Installer.git
cd HomeAssistant-macOS-Installer

# Ensure Python 3.12 is installed (Home Assistant 2024.x requirement)
python3 --version

# Build the virtual environment and package the .pkg
make all
```
The package will be in the `dist/` folder.

## 📂 System Paths

- **Installation:** `/opt/homeassistant`
- **Configuration:** `/Library/Application Support/HomeAssistant`
- **Logs:** `/Library/Logs/HomeAssistant`
- **LaunchDaemon:** `/Library/LaunchDaemons/org.homeassistant.daemon.plist`

## 🧹 Uninstallation

Run the included uninstall script with administrative privileges:
```bash
sudo /opt/homeassistant/bin/uninstall
```
Options:
- `--keep-config`: Preserves your configuration in `/Library/Application Support/HomeAssistant`.
- `--remove-config`: Deletes all data.
- `--non-interactive`: Headless mode (defaults to keeping config).

## 🤝 Contributing

Contributions are welcome! Pull Requests are appreciated.

## 📄 License

Licensed under the Apache 2.0 License. Matches the official Home Assistant core license.
