#!/usr/bin/env bash
set -euo pipefail
APP_NAME=Mynoh
VERSION=${VERSION:-0.1.0}
python scripts/build.py
mkdir -p packaging
# Portable zip
ditto -c -k --sequesterRsrc --keepParent dist/${APP_NAME} packaging/${APP_NAME}-${VERSION}-macos.zip
# Optional DMG/PKG when host tools are available.
if command -v hdiutil >/dev/null 2>&1; then
  hdiutil create -volname "$APP_NAME" -srcfolder dist/${APP_NAME} -ov -format UDZO packaging/${APP_NAME}-${VERSION}.dmg
fi
if command -v pkgbuild >/dev/null 2>&1; then
  pkgbuild --root dist/${APP_NAME} --identifier ai.arena.mynoh --version "$VERSION" packaging/${APP_NAME}-${VERSION}.pkg || true
fi
