#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
BUILD_DIR="$REPO_ROOT/build"

APP_NAME="VisiCore_App_for_AI_Observability"

# Get version from app.conf
version=$(grep -m1 '^version' "$REPO_ROOT/default/app.conf" | awk -F' = ' '{print $2}')

# Clean build directory
rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR"

# Create tarball with proper root directory name
echo "Packaging $APP_NAME v${version}..."
tar -czf "$BUILD_DIR/${APP_NAME}-${version}.tar.gz" \
    --transform "s,^\.,$APP_NAME," \
    -C "$REPO_ROOT" \
    --exclude='.git' \
    --exclude='build' \
    --exclude='.direnv' \
    --exclude='scripts' \
    --exclude='CLAUDE.md' \
    --exclude='README.md' \
    --exclude='.gitignore' \
    --exclude='.DS_Store' \
    .

echo "  -> ${APP_NAME}-${version}.tar.gz"
echo ""
echo "Build artifact:"
ls -lh "$BUILD_DIR"/*.tar.gz
