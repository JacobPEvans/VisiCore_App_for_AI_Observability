#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
BUILD_DIR="$REPO_ROOT/build"

# Get version from app.conf
get_version() {
    local app_conf="$1/default/app.conf"
    grep -m1 '^version' "$app_conf" | awk -F' = ' '{print $2}'
}

# Clean build directory
rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR"

# Package each app
for app_dir in VisiCore_App_for_AI_Observability VisiCore_TA_AI_Observability; do
    if [ ! -d "$REPO_ROOT/$app_dir" ]; then
        echo "ERROR: $app_dir not found" >&2
        exit 1
    fi

    version=$(get_version "$REPO_ROOT/$app_dir")
    tarball="$BUILD_DIR/${app_dir}-${version}.tar.gz"

    echo "Packaging $app_dir v${version}..."
    tar -czf "$tarball" -C "$REPO_ROOT" "$app_dir"
    echo "  -> $(basename "$tarball")"
done

echo ""
echo "Build artifacts:"
ls -lh "$BUILD_DIR"/*.tar.gz
