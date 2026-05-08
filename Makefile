# Home Assistant Desktop for macOS - Makefile
# Build automation pour package .pkg natif (Architecture Standalone Venv)

.PHONY: all clean build package install uninstall help

# Configuration
VERSION = 2.0.0
BUILD_DIR = build
DIST_DIR = dist
PKG_NAME = HomeAssistant-macOS
PKG_FILE = $(DIST_DIR)/$(PKG_NAME)-$(VERSION).pkg

# Target directories inside package
HA_OPT_DIR = $(BUILD_DIR)/opt/homeassistant

# Répertoires
SCRIPTS_DIR = scripts
LAUNCHD_DIR = launchd
PKG_DIR = pkg

# Par défaut
all: clean build package

clean:
	@echo "Nettoyage build..."
	rm -rf $(BUILD_DIR) $(DIST_DIR)
	@echo "Nettoyage terminé"

build:
	@echo "Build de l'environnement Home Assistant..."
	mkdir -p $(HA_OPT_DIR)
	
	# Création du virtualenv standalone avec le python système
	python3 -m venv $(HA_OPT_DIR)
	
	# Installation de Home Assistant
	$(HA_OPT_DIR)/bin/pip install --upgrade pip
	$(HA_OPT_DIR)/bin/pip install -r requirements.txt
	
	# Fixes applied during packaging step to avoid breaking local venv
	@echo "Build terminé: $(HA_OPT_DIR)"

package: build
	@echo "Création package .pkg..."
	mkdir -p $(DIST_DIR)
	
	@PKG_TEMP=$$(mktemp -d); \
	echo "Répertoire temporaire: $$PKG_TEMP"; \
	\
	mkdir -p "$$PKG_TEMP/pkg_root/opt"; \
	mkdir -p "$$PKG_TEMP/pkg_root/Library/LaunchDaemons"; \
	mkdir -p "$$PKG_TEMP/pkg_root/Library/Application Support/HomeAssistant"; \
	mkdir -p "$$PKG_TEMP/scripts"; \
	mkdir -p "$$PKG_TEMP/resources"; \
	\
	cp -a "$(HA_OPT_DIR)" "$$PKG_TEMP/pkg_root/opt/"; \
	\
	echo "Ajustement des chemins absolus dans le package..."; \
	for f in $$(find "$$PKG_TEMP/pkg_root/opt/homeassistant/bin" -type f); do \
		if file "$$f" | grep -q "text"; then \
			sed -i '' 's|$(PWD)/$(HA_OPT_DIR)|/opt/homeassistant|g' "$$f"; \
		fi; \
	done; \
	\
	if [ -f "$(LAUNCHD_DIR)/org.homeassistant.daemon.plist" ]; then \
		cp "$(LAUNCHD_DIR)/org.homeassistant.daemon.plist" "$$PKG_TEMP/pkg_root/Library/LaunchDaemons/"; \
	fi; \
	if [ -d "$(SCRIPTS_DIR)" ]; then \
		cp -r "$(SCRIPTS_DIR)"/* "$$PKG_TEMP/scripts/"; \
	fi; \
	if [ -d "$(PKG_DIR)" ]; then \
		cp -r "$(PKG_DIR)"/* "$$PKG_TEMP/resources/" 2>/dev/null || true; \
	fi; \
	\
	pkgbuild \
		--root "$$PKG_TEMP/pkg_root" \
		--install-location / \
		--scripts "$$PKG_TEMP/scripts" \
		--identifier org.homeassistant.desktop \
		--version $(VERSION) \
		--ownership preserve \
		"$(DIST_DIR)/homeassistant-core.pkg"; \
	\
	if [ -f "$(PKG_DIR)/Distribution.xml" ]; then \
		productbuild \
			--distribution "$(PKG_DIR)/Distribution.xml" \
			--resources "$$PKG_TEMP/resources" \
			--package-path "$(DIST_DIR)" \
			"$(PKG_FILE)"; \
	else \
		mv "$(DIST_DIR)/homeassistant-core.pkg" "$(PKG_FILE)"; \
	fi; \
	\
	rm -rf "$$PKG_TEMP"; \
	rm -f "$(DIST_DIR)/homeassistant-core.pkg"; \
	echo "Package créé: $(PKG_FILE)"

install: package
	@echo "Installation locale..."
	sudo installer -pkg $(PKG_FILE) -target /

uninstall:
	@echo "Désinstallation Home Assistant Desktop..."
	sudo launchctl bootout system /Library/LaunchDaemons/org.homeassistant.daemon.plist 2>/dev/null || true
	sudo rm -f /Library/LaunchDaemons/org.homeassistant.daemon.plist
	sudo rm -rf /opt/homeassistant
	sudo dscl . -delete /Users/_homeassistant 2>/dev/null || true
	sudo dscl . -delete /Groups/_homeassistant 2>/dev/null || true
	@echo "Désinstallation terminée"

help:
	@echo "Home Assistant Desktop for macOS - Makefile"
	@echo "  make build    - Créer l'environnement virtuel"
	@echo "  make package  - Construire le .pkg"
	@echo "  make install  - Installer localement"
	@echo "  make uninstall- Nettoyer le système"
