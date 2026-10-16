#!/bin/bash
# Submit the signed installer with Apple's current notarytool workflow.
set -euo pipefail

VERSION=$(cat VERSION)
PKG_PATH="${PKG_PATH:-dist/HomeAssistant-macOS-${VERSION}.pkg}"
KEYCHAIN_PROFILE="${NOTARY_PROFILE:-}"

if [[ -z "$KEYCHAIN_PROFILE" ]]; then
  echo "Create a notarytool keychain profile, then set NOTARY_PROFILE to its name." >&2
  echo "Example: xcrun notarytool store-credentials <profile> --apple-id … --team-id … --password …" >&2
  exit 2
fi
if [[ ! -f "$PKG_PATH" ]]; then
  echo "Package not found: $PKG_PATH (run make package first)." >&2
  exit 1
fi

xcrun notarytool submit "$PKG_PATH" --keychain-profile "$KEYCHAIN_PROFILE" --wait
xcrun stapler staple "$PKG_PATH"
xcrun stapler validate "$PKG_PATH"
spctl --assess --type install --verbose "$PKG_PATH"
echo "Notarized package: $PKG_PATH"
