#!/usr/bin/env bash
# 构建 Android 版（默认出三种 ABI 的已签名 APK）
# 用法：
#   bash build-android.sh              # 分 ABI，出 3 个 APK
#   bash build-android.sh --universal  # 单个通用 APK
#
# 签名信息从下面的 KEYSTORE 读取；密码放在 D:/Keys/miru/password.txt（不入库）。
# 没有密钥时也能编过，但产物是未签名的，装不上。
set -e

# 本机路径（换机器需改）
FLUTTER_DIR="/d/Tools/Language/Flutter/3.22.3"
GIT_BIN="/c/Users/Herwin/.workbuddy/binaries/PortableGit/versions/1.3.0/bin"
export PATH="$GIT_BIN:$FLUTTER_DIR/bin:/c/Windows/System32:$PATH"

# 这里必须包含 PortableGit：flutter 的 bash 启动脚本依赖 git 等工具，
# 缺了会报 "Access is denied."（而不是明说找不到 git）
export JAVA_HOME="D:/Tools/Language/Java/jdk-17"
export ANDROID_HOME="D:\\Tools\\Android\\sdk"
export ANDROID_SDK_ROOT="$ANDROID_HOME"
export GRADLE_USER_HOME="D:\\Tools\\Android\\gradle-home"
export PUB_CACHE="D:/Tools/Language/Flutter/pub-cache"
export PUB_HOSTED_URL=https://pub.flutter-io.cn
export FLUTTER_STORAGE_BASE_URL=https://storage.flutter-io.cn

KEYSTORE_PATH="D:\\Keys\\miru\\miru-release.jks"
if [ -f "D:/Keys/miru/password.txt" ]; then
  export KEYSTORE="$KEYSTORE_PATH"
  export KEYSTORE_PASSWORD="$(cat D:/Keys/miru/password.txt)"
  export KEY_ALIAS=miru
  export KEY_PASSWORD="$KEYSTORE_PASSWORD"
  echo "[sign] 使用 $KEYSTORE_PATH 签名"
else
  echo "[sign] 未找到密码文件，产物将是未签名 APK（装不上）"
fi

cd "$(dirname "$0")"

if [ "$1" = "--universal" ]; then
  flutter build apk --release
else
  flutter build apk --release --split-per-abi
fi

echo "[done] 产物在 build/app/outputs/flutter-apk/"
ls -la build/app/outputs/flutter-apk/*.apk | awk '{print "  ", $NF, $5"B"}'
