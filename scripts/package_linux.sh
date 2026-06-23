#!/usr/bin/env bash
set -euo pipefail
APP_NAME=Mynoh
VERSION=${VERSION:-0.1.0}
python scripts/build.py
mkdir -p packaging
# Portable tarball
tar -czf packaging/${APP_NAME}-${VERSION}-linux-x86_64.tar.gz -C dist ${APP_NAME}
# Optional native formats when tools are installed in CI/host.
if command -v appimagetool >/dev/null 2>&1; then
  echo "appimagetool detected; create an AppDir before enabling AppImage packaging."
fi
if command -v fpm >/dev/null 2>&1; then
  fpm -s dir -t deb -n mynoh -v "$VERSION" --prefix /opt/mynoh dist/${APP_NAME}/
  fpm -s dir -t rpm -n mynoh -v "$VERSION" --prefix /opt/mynoh dist/${APP_NAME}/
  mv ./*.deb ./*.rpm packaging/ 2>/dev/null || true
else
  echo "Install fpm to produce .deb and .rpm packages."
fi
