#!/usr/bin/env bash
# 一键构建 Windows 版 Miru（Rune 补丁版）
# 用法：bash build.sh
# 注意：下面三行是本机路径（Flutter 版本、Python、pub 缓存），换机器需要改
set -e

FLUTTER_DIR="/d/Tools/Language/Flutter/3.22.3"
export PATH="/c/Users/Herwin/.workbuddy/binaries/PortableGit/versions/1.3.0/bin:$FLUTTER_DIR/bin:/c/Windows/System32:$PATH"
export FLUTTER_STORAGE_BASE_URL=https://storage.flutter-io.cn
export PUB_HOSTED_URL=https://pub.flutter-io.cn
export PUB_CACHE=D:/Tools/Language/Flutter/pub-cache
export HTTP_PROXY=http://127.0.0.1:7897
export HTTPS_PROXY=http://127.0.0.1:7897

cd "$(dirname "$0")"
PY="C:/Users/Herwin/.workbuddy/binaries/python/versions/3.13.12/python.exe"

echo "[1/5] 依赖"
flutter pub get

echo "[2/5] 修复插件链接（没开开发者模式时的 junction 兜底）"
PUB_CACHE="$PUB_CACHE" "$PY" tools/fix_plugin_symlinks.py
# flutter_windows_webview 是 git 依赖，脚本找不到，单独补
LINK=windows/flutter/ephemeral/.plugin_symlinks/flutter_windows_webview
if [ -d "$LINK" ] && [ ! -L "$LINK" ]; then
  rm -rf "$LINK"
  "$PY" tools/mkjunction.py create "$LINK" \
    "$PUB_CACHE/git/flutter_windows_webview-096d24d88454819b9f8a94af14a130cb372fa5ae/"
fi

echo "[3/5] 检查 media_kit 预编译依赖（mpv / ANGLE）"
mkdir -p build/windows/x64
[ -f build/windows/x64/mpv-dev-x86_64-20230924-git-652a1dd.7z ] || \
  curl -sL "https://gh-proxy.com/https://github.com/media-kit/libmpv-win32-video-build/releases/download/2023-09-24/mpv-dev-x86_64-20230924-git-652a1dd.7z" \
    -o build/windows/x64/mpv-dev-x86_64-20230924-git-652a1dd.7z
[ -f build/windows/x64/ANGLE.7z ] || \
  curl -sL "https://gh-proxy.com/https://github.com/alexmercerind/flutter-windows-ANGLE-OpenGL-ES/releases/download/v1.0.1/ANGLE.7z" \
    -o build/windows/x64/ANGLE.7z

echo "[4/5] 编译"
flutter build windows --release

echo "[5/5] 归档"
# 旧的 dist 里 exe 可能正在运行，不能被覆盖，所以按时间戳出新目录
STAMP=$(date +%m%d-%H%M)
DEST="../dist/miru-1.8.1-rune-$STAMP"
cp -r build/windows/x64/runner/Release "$DEST"
echo "完成：$DEST/miru.exe"
