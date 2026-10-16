# Home Assistant Core macOS community installer

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Platform](https://img.shields.io/badge/Platform-macOS-lightgrey.svg)](#)
[![Installer version](https://img.shields.io/badge/Installer-3.1.0-green.svg)](#)

A community-maintained macOS `.pkg` wrapper that installs Home Assistant Core in a Python virtual environment and runs it with `launchd`. **It is not an official Home Assistant installation method and is not suitable to describe as production-supported.** It does not include Supervisor or add-ons.

## Important support and reliability notice

Home Assistant ended official support for the Core and Supervised installation methods after the 2025.12 release. They may still run and receive releases, but upstream no longer supports issues for these installation types. Home Assistant OS and Home Assistant Container are the officially supported methods. See the [official announcement](https://www.home-assistant.io/blog/2025/05/22/deprecating-core-and-supervised-installation-methods-and-32-bit-systems/).

The forum discussion that prompted this project also reports Gatekeeper refusing the unsigned package and notes that desktop Macs may not be available 24/7. Community replies suggest testing/development as a more appropriate use case. See [the discussion](https://community.home-assistant.io/t/native-macos-standalone-installer-pkg-for-home-assistant-no-docker-no-vms/1009745). These are user reports, not a successful test certification of this installer.

Use a supported HA OS/Container host for a primary home-automation server. If experimenting with this installer, keep off-device backups and test restore, upgrade, and reboot recovery before relying on it. Bluetooth/USB access from a system LaunchDaemon is not guaranteed; macOS privacy permissions may prevent it.

## Current target and limitations

- Installer package version: `3.1.0` (`VERSION`).
- New installs pin Home Assistant Core `2026.10.2` (`requirements.txt`). After installation, a root LaunchDaemon checks PyPI once daily at 04:30 and transactionally updates to the newest stable Core release when available.
- Home Assistant 2026.10.2 requires Python `3.14.2+`. The build currently bundles CPython `3.14.8` from Astral's `python-build-standalone` via `uv`, beside a relocatable virtual environment.
- Builds are architecture-specific for macOS 13+. Build/test on Intel and Apple Silicon separately; each package contains its own architecture's Python runtime, and Installer rejects the wrong OS version or architecture. The first full install must be tested on a clean Mac for each architecture before release.
- The package is unsigned and not notarized by default. Gatekeeper may block it. Do not disable Gatekeeper or remove quarantine for an artifact unless you have independently verified its origin and integrity.
- `ffmpeg` is not bundled. Install it on the target Mac with Homebrew (`brew install ffmpeg`) for integrations that need transcoding; the LaunchDaemon PATH includes Apple Silicon and Intel Homebrew locations.
- Core is backed up before each update to `/Library/Application Support/HomeAssistant-Backups` (retained for 30 days). The updater builds and checks a separate environment, swaps it in only after validation, and rolls back if the running service does not respond. Updates require network access and compatible bundled Python; if a future Core requires a newer Python, the updater safely leaves the existing version running and a new installer release is needed.
- This is **Home Assistant Core only**, not Home Assistant OS (HAOS), Supervisor, or add-ons. The daily updater cannot turn a native macOS installation into HAOS.

## Build

On a Mac with Xcode Command Line Tools, `pkgbuild`, `productbuild`, Homebrew and `uv` (`brew install uv ffmpeg autoconf cmake`):

```sh
make all
```

Output: `dist/HomeAssistant-macOS-3.1.0-<architecture>.pkg` (`arm64` or `x86_64`). Build/test separately on each target architecture. Signing and notarization are optional, require an Apple Developer ID and configured notarytool profile; see `scripts/sign.sh` and `scripts/notarize.sh`.

## Install and manage

Install the package using macOS Installer, then open `http://localhost:8123`. Initial startup can take a few minutes. Paths:

- Runtime: `/opt/homeassistant`
- Configuration: `/Library/Application Support/HomeAssistant/config`
- Logs: `/Library/Logs/HomeAssistant`
- LaunchDaemon: `/Library/LaunchDaemons/org.homeassistant.daemon.plist`

Service status and restart:

```sh
sudo launchctl print system/org.homeassistant.daemon
sudo launchctl kickstart -k system/org.homeassistant.daemon
```

Core checks for the newest stable release daily at 04:30 when the Mac is awake and online. To trigger an update now, run `sudo /opt/homeassistant/update`; to inspect the updater logs, use `sudo tail -n 100 /Library/Logs/HomeAssistant-Installer/updater.log` and `updater.error.log`. Each update writes a private config/database snapshot first. The updater retains snapshots for 30 days; keep an additional off-device backup for disaster recovery. To disable scheduled updates: `sudo launchctl disable system/org.homeassistant.updater && sudo launchctl bootout system/org.homeassistant.updater`. Re-enable with `sudo launchctl enable system/org.homeassistant.updater && sudo launchctl bootstrap system /Library/LaunchDaemons/org.homeassistant.updater.plist`.

Uninstall while preserving configuration:

```sh
sudo /opt/homeassistant/uninstall --keep-config
```

To delete data, pass `--remove-config` instead. Read the script's prompts/options carefully.

## Documentation

- [Build](docs/BUILD.md)
- [Installation and troubleshooting](docs/INSTALLATION.md)
- [Compatibility and validation limits](docs/COMPATIBILITY.md)
- [Why Core is no longer an upstream-supported install method](docs/OFFICIAL_MACOS_GUIDE.md)

## License

Apache-2.0. Home Assistant Core is a separate project with its own license.