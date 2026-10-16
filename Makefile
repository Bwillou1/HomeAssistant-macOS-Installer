# Build a relocatable, architecture-specific Home Assistant Core installer.
.PHONY: all clean build package install uninstall help
.NOTPARALLEL: all

VERSION := $(shell cat VERSION)
PYTHON ?= python3
UV ?= uv
UV_MIN_VERSION := 0.10.8
PYTHON_VERSION := 3.14.8
BUILD_DIR := build
DIST_DIR := dist
PKG_NAME := HomeAssistant-macOS
ARCH := $(shell uname -m)
PKG_FILE := $(DIST_DIR)/$(PKG_NAME)-$(VERSION)-$(ARCH).pkg
HA_ROOT := $(BUILD_DIR)/opt/homeassistant
HA_PYTHON_DIR := $(HA_ROOT)/python
HA_VENV_DIR := $(HA_ROOT)/venv

all: clean package

clean:
	@echo "Cleaning build directories..."
	rm -rf "$(BUILD_DIR)" "$(DIST_DIR)"

build:
	@echo "Building relocatable Home Assistant runtime..."
	@$(PYTHON) -c 'import platform,sys; assert sys.platform == "darwin", "The installer package must be built on macOS"; assert platform.machine() in ("arm64", "x86_64"), "Only Apple Silicon and Intel Macs are supported"'
	@command -v "$(UV)" >/dev/null || { echo "uv $(UV_MIN_VERSION)+ is required (install with Homebrew: brew install uv)" >&2; exit 1; }
	@$(PYTHON) -c 'import re,subprocess,sys; v=re.search(r"(\d+\.\d+\.\d+)", subprocess.check_output(["$(UV)","--version"], text=True)).group(1); assert tuple(map(int,v.split("."))) >= tuple(map(int,"$(UV_MIN_VERSION)".split("."))), "uv $(UV_MIN_VERSION)+ required; found "+v'
	mkdir -p "$(HA_ROOT)"
	UV_PYTHON_INSTALL_DIR="$(CURDIR)/$(HA_PYTHON_DIR)" "$(UV)" python install --managed-python --no-bin "$(PYTHON_VERSION)"
	BASE_PYTHON="$$(UV_PYTHON_INSTALL_DIR="$(CURDIR)/$(HA_PYTHON_DIR)" "$(UV)" python find --managed-python "$(PYTHON_VERSION)")"; \
	  "$(UV)" venv --relocatable --python "$$BASE_PYTHON" "$(HA_VENV_DIR)"
	UV_PYTHON_INSTALL_DIR="$(CURDIR)/$(HA_PYTHON_DIR)" "$(UV)" pip install --python "$(HA_VENV_DIR)/bin/python" --requirement requirements.txt
	"$(HA_VENV_DIR)/bin/python" -c 'import sys,homeassistant; assert sys.version_info >= (3,14,2); print("Home Assistant",homeassistant.__version__,"on Python",sys.version.split()[0])'
	$(PYTHON) scripts/relocate_venv.py "$(HA_ROOT)" --prefix /opt/homeassistant

package: build
	@echo "Creating and inspecting .pkg package..."
	@set -euo pipefail; \
	PKG_TEMP=$$(mktemp -d); \
	trap 'rm -rf "$$PKG_TEMP"' EXIT; \
	mkdir -p "$$PKG_TEMP/pkg_root/opt" "$$PKG_TEMP/pkg_root/Library/LaunchDaemons" "$$PKG_TEMP/scripts" "$$PKG_TEMP/resources"; \
	cp -a "$(HA_ROOT)" "$$PKG_TEMP/pkg_root/opt/"; \
	install -m 644 pkg/Distribution.xml "$$PKG_TEMP/Distribution.xml"; \
	install -m 755 scripts/uninstall "$$PKG_TEMP/pkg_root/opt/homeassistant/uninstall"; \
	install -m 755 scripts/update "$$PKG_TEMP/pkg_root/opt/homeassistant/update"; \
	install -m 755 scripts/relocate_venv.py "$$PKG_TEMP/pkg_root/opt/homeassistant/relocate_venv.py"; \
	install -m 644 THIRD_PARTY_NOTICES.md "$$PKG_TEMP/pkg_root/opt/homeassistant/THIRD_PARTY_NOTICES.md"; \
	install -m 644 launchd/org.homeassistant.daemon.plist "$$PKG_TEMP/pkg_root/Library/LaunchDaemons/org.homeassistant.daemon.plist"; \
	install -m 644 launchd/org.homeassistant.updater.plist "$$PKG_TEMP/pkg_root/Library/LaunchDaemons/org.homeassistant.updater.plist"; \
	install -m 755 scripts/preinstall "$$PKG_TEMP/scripts/preinstall"; \
	install -m 755 scripts/postinstall "$$PKG_TEMP/scripts/postinstall"; \
	for f in "$$PKG_TEMP/scripts/preinstall" "$$PKG_TEMP/scripts/postinstall" "$$PKG_TEMP/pkg_root/opt/homeassistant/uninstall" "$$PKG_TEMP/pkg_root/opt/homeassistant/update" "$$PKG_TEMP/Distribution.xml"; do \
	  sed -i '' 's/VERSION_PLACEHOLDER/$(VERSION)/g' "$$f"; \
	done; \
	sed -i '' 's/ARCH_PLACEHOLDER/$(ARCH)/g' "$$PKG_TEMP/Distribution.xml"; \
	cp pkg/welcome.html pkg/conclusion.html pkg/license.txt pkg/background.png "$$PKG_TEMP/resources/"; \
	pkgbuild --root "$$PKG_TEMP/pkg_root" --install-location / \
	  --scripts "$$PKG_TEMP/scripts" --identifier org.homeassistant.desktop \
	  --version "$(VERSION)" --ownership preserve "$(DIST_DIR)/homeassistant-core.pkg"; \
	productbuild --distribution "$$PKG_TEMP/Distribution.xml" --resources "$$PKG_TEMP/resources" \
	  --package-path "$(DIST_DIR)" "$(PKG_FILE)"; \
	rm -f "$(DIST_DIR)/homeassistant-core.pkg"; \
	pkgutil --expand-full "$(PKG_FILE)" "$$PKG_TEMP/expanded"; \
	find "$$PKG_TEMP/expanded" -path '*/opt/homeassistant/python/*/bin/python3.14' -print -quit | grep -q .; \
	find "$$PKG_TEMP/expanded" -path '*/opt/homeassistant/venv/bin/hass' -print -quit | grep -q .; \
	find "$$PKG_TEMP/expanded" -path '*/opt/homeassistant/update' -print -quit | grep -q .; \
	find "$$PKG_TEMP/expanded" -path '*/opt/homeassistant/relocate_venv.py' -print -quit | grep -q .; \
	find "$$PKG_TEMP/expanded" -path '*/Library/LaunchDaemons/org.homeassistant.daemon.plist' -print -quit | grep -q .; \
	find "$$PKG_TEMP/expanded" -path '*/Library/LaunchDaemons/org.homeassistant.updater.plist' -print -quit | grep -q .; \
	echo "Package created and payload verified: $(PKG_FILE)"

install: package
	@echo "Installing Home Assistant..."
	sudo installer -pkg "$(PKG_FILE)" -target /

uninstall:
	@echo "Uninstalling Home Assistant while preserving configuration..."
	sudo /opt/homeassistant/uninstall --keep-config

help:
	@echo "Home Assistant Core macOS community installer"
	@echo "  make all       - Build portable runtime and .pkg (macOS + uv)"
	@echo "  make build     - Build relocatable Python + Home Assistant"
	@echo "  make package   - Build and inspect the .pkg"
	@echo "  make install   - Install locally (administrator access required)"
	@echo "  make uninstall - Uninstall but preserve configuration"
