#!/usr/bin/env bash
# Builds the Windows installer from Linux (or WSL). Needs: python3 with pip, curl, makensis.
# Output: dist/IDA-Live-Setup-<version>.exe
set -euo pipefail
cd "$(dirname "$0")/.."
VERSION=$(python3 -c "import ida_live; print(ida_live.__version__)")
PY_URL="https://github.com/astral-sh/python-build-standalone/releases/download/20260901/cpython-3.12.14%2B20260901-x86_64-pc-windows-msvc-install_only_stripped.tar.gz"
WORK=build/win; STAGE=$WORK/stage; SP=$STAGE/python/Lib/site-packages
rm -rf "$WORK" && mkdir -p "$STAGE/app" dist
curl -sL "$PY_URL" -o "$WORK/python.tar.gz"
tar xzf "$WORK/python.tar.gz" -C "$STAGE"
PIP="python3 -m pip install -q --target $SP --platform win_amd64 --python-version 3.12 --implementation cp --only-binary=:all:"
# versions tested under Windows Python; bleak's Windows (WinRT) dependencies listed explicitly
$PIP "numpy==1.26.4" "aiohttp==3.14.3" "pyserial==3.5" \
  winrt-runtime==3.2.1 winrt-windows-devices-bluetooth==3.2.1 winrt-windows-devices-bluetooth-advertisement==3.2.1 \
  winrt-windows-devices-bluetooth-genericattributeprofile==3.2.1 winrt-windows-devices-enumeration==3.2.1 \
  winrt-windows-devices-radios==3.2.1 winrt-windows-foundation==3.2.1 winrt-windows-foundation-collections==3.2.1 \
  winrt-windows-storage-streams==3.2.1
$PIP --no-deps "bleak==3.0.2"
find "$SP" -type d \( -name tests -o -name test -o -name __pycache__ \) -prune -exec rm -rf {} +
rm -rf "$SP/bin"
echo "../../../app" > "$SP/ida_live_app.pth"
cp -r ida_live web maps recipes hardware docs README.md LICENSE NOTICE.md "$STAGE/app/"
cp packaging/ida-live.ico "$STAGE/app/"
find "$STAGE/app" -type d -name __pycache__ -prune -exec rm -rf {} +
touch "$STAGE/app/installed.flag"
makensis -V2 -DVERSION="$VERSION" -DSTAGE="$(realpath $STAGE)" -DOUTFILE="$(realpath dist)/IDA-Live-Setup-$VERSION.exe" packaging/installer.nsi
ls -la dist
