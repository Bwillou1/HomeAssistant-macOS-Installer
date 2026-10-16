#!/bin/bash
# Sign the generated installer package. Run on macOS with an Installer certificate.
set -euo pipefail

VERSION=$(cat VERSION)
PKG_PATH="${PKG_PATH:-dist/HomeAssistant-macOS-${VERSION}.pkg}"
SIGNED_PKG_PATH="${PKG_PATH%.pkg}-signed.pkg"
DEVELOPER_ID="${DEVELOPER_ID:-}"

if [[ -z "$DEVELOPER_ID" ]]; then
  echo "Set DEVELOPER_ID to the exact 'Developer ID Installer: …' certificate name." >&2
  exit 2
fi
if [[ ! -f "$PKG_PATH" ]]; then
  echo "Package not found: $PKG_PATH (run make package first)." >&2
  exit 1
fi

productsign --sign "$DEVELOPER_ID" "$PKG_PATH" "$SIGNED_PKG_PATH"
pkgutil --check-signature "$SIGNED_PKG_PATH"
mv -f "$SIGNED_PKG_PATH" "$PKG_PATH"
echo "Signed package: $PKG_PATH"
