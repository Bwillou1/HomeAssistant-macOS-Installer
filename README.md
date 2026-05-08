# Home Assistant Native macOS Installer 🍏🏡

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Platform](https://img.shields.io/badge/Platform-macOS-lightgrey.svg)](#)
[![Architecture](https://img.shields.io/badge/Architecture-Universal%202-purple.svg)](#)

A production-ready, enterprise-grade standalone macOS installer (`.pkg`) for the Home Assistant Server. 

This project aims to eliminate the need for Virtual Machines (VMs) or Docker containers on macOS by providing a native, highly stable, and fully integrated server environment for Mac users.

## 🌟 Why this Installer?

Running Home Assistant on macOS usually requires complex virtualization. This introduces significant overhead and complicates access to native hardware interfaces such as Bluetooth, USB devices, and local networking (Bonjour/mDNS). 

This native macOS package solves these issues by deploying a **Self-Contained Python Virtual Environment**.

### Key Features
- **Zero VM Overhead:** Runs natively on both Intel (x86_64) and Apple Silicon (ARM64) via Universal 2 support.
- **True System Daemon:** Integrates seamlessly with macOS `launchd` for automatic startup at boot, running independently of user sessions.
- **Enhanced Security:** Abides by macOS Server best practices. It runs under a dedicated, restricted background system user (`_homeassistant`) rather than `root`.
- **Ultimate Stability:** Unlike PyInstaller wrappers that frequently break on dynamic dependency loading, this installer bundles a complete, isolated Python virtual environment.
- **Enterprise Packaging:** Distributed as a standard Apple Flat Package (`.pkg`) with proper `preinstall` and `postinstall` scripts.

## 🚀 Installation

1. Go to the [Releases](../../releases) page.
2. Download the latest `HomeAssistant-macOS-*.pkg`.
3. Double-click the downloaded file and follow the standard macOS installer instructions.
4. Once installed, open your web browser and navigate to `http://localhost:8123`.

*The server will automatically start in the background and will restart automatically whenever your Mac reboots.*

## 🛠️ Build it yourself

If you want to build the `.pkg` from source:

```bash
# Clone the repository
git clone https://github.com/Bwillou1/HomeAssistant-macOS-Installer.git
cd HomeAssistant-macOS-Installer

# Build the virtual environment and package the .pkg
make all
```
The compiled package will be available in the `dist/` folder.

## 📂 System Paths

- **Installation Directory:** `/opt/homeassistant`
- **Configuration Directory:** `/Library/Application Support/HomeAssistant`
- **Logs:** `/Library/Logs/HomeAssistant`
- **LaunchDaemon:** `/Library/LaunchDaemons/org.homeassistant.daemon.plist`

## 🧹 Uninstallation

To completely remove the Home Assistant server from your Mac, you can run the uninstall target:

```bash
sudo make uninstall
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request if you have ideas on how to improve the macOS integration further.

## 📄 License

This project is licensed under the Apache 2.0 License - see the [LICENSE](LICENSE) file for details. This matches the official Home Assistant core license.
