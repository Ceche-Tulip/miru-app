# Android 构建说明

和 Windows 一样，先有能通的环境再谈编译。分四步走，每一步都能单独验证。

## 阶段 0 · 环境

| 组件 | 路径 | 版本 |
| --- | --- | --- |
| JDK | `D:\Tools\Language\Java\jdk-17` | 17.0.12 |
| cmdline-tools | `D:\Tools\Android\cmdline-tools\latest` | 13114758（19.0） |
| SDK | `D:\Tools\Android\sdk` | platform-tools / android-34 / build-tools 34.0.0 / ndk 26.1.10909125 |
| Gradle 缓存 | `D:\Tools\Android\gradle-home` | Gradle 7.5（wrapper 自动下载） |
| 签名密钥 | `D:\Keys\miru\miru-release.jks` | 密码见同目录 `password.txt`（**不要入库**） |

项目本身：Gradle 7.5、AGP 7.2.0、Kotlin 1.7.10、`compileSdk 34` / `minSdk 21` / `targetSdk 28`。

装 SDK 组件（一次性）：

```bash
export JAVA_HOME="D:/Tools/Language/Java/jdk-17"
cd D:/Tools/Android/cmdline-tools/latest/bin
yes | ./sdkmanager.bat --sdk_root="D:\Tools\Android\sdk" --licenses
./sdkmanager.bat --sdk_root="D:\Tools\Android\sdk" \
  "platform-tools" "platforms;android-34" "build-tools;34.0.0" "ndk;26.1.10909125"
```

> 环境变量**没有写进系统**，全部由 `build-android.sh` 临时注入，换机器只需改脚本顶部几行。

## 阶段 1 · 构建

```bash
cd D:/SoftWare/Miru/client/src
bash build-android.sh                # 分 ABI，出 3 个 APK
bash build-android.sh --universal    # 单个通用 APK（37MB，四 ABI 全含）
```

产物：`build/app/outputs/flutter-apk/app-<abi>-release.apk`

| ABI | 大小 | 适用 |
| --- | --- | --- |
| arm64-v8a | 17.6 MB | 绝大多数现代手机 |
| armeabi-v7a | 17.1 MB | 老机器 |
| x86_64 | 18.6 MB | 模拟器 |

首次构建约 20 分钟（下 Gradle 发行包 + 全量依赖 + 若干 SDK 平台），之后约 2 分钟。

## 阶段 2 · 验签

```bash
D:/Tools/Android/sdk/build-tools/34.0.0/apksigner.bat verify --print-certs \
  build/app/outputs/flutter-apk/app-arm64-v8a-release.apk
```

应看到 `CN=Ceche-Tulip, OU=Miru Fork`。证书 SHA-256：

```
61be97a0c579c29eed13173fff72d4b0a88756e842978fe1a2a593cb38623362
```

**换密钥等于换应用身份**，旧版本无法覆盖安装。密钥丢了就只能卸载重装，务必备份
`D:\Keys\miru\`（jks + 密码）。

## 阶段 3 · 真机验证

```bash
# 手机开 USB 调试后
adb devices
adb install -r dist/app-arm64-v8a-release.apk
```

要验证的点：扩展能装、搜索可用（依赖本 fork 对 POST 重定向的修复）、正文能翻页、
动态/视频不崩。Android 端的 JS 引擎是 QuickJS、数据库是 isar，与 Windows 是两条独立链，
Windows 上过了不代表这里也过。

## 踩过的坑

1. **`Access is denied.` 且伴随 `wsl.exe` 被安全策略拦截**
   真正原因是 `flutter` 的 bash 脚本缺 `git`：PATH 里没有 PortableGit 时会立刻失败。
   把 `PortableGit/versions/<ver>/bin` 放到 PATH 最前面即可（`build-android.sh` 已处理）。
2. **Gradle 下载依赖报 TLS 握手失败**
   `dl.google.com` 走代理时 Java 的 TLS 可能被中断。不要用 `JAVA_TOOL_OPTIONS` 设代理，
   改用阿里云镜像：`GRADLE_USER_HOME/init.d/aliyun.gradle` 里给 `buildscript` 与 `allprojects`
   注入 `maven.aliyun.com/repository/{google,public,gradle-plugin}`。
3. **Gradle 会自己装 SDK 平台**
   老插件声明了 `compileSdk 28/29/30`，首次构建时 AGP 会自动下载这些 platform。
   日志里看到 `Install Android SDK Platform 30 ... complete` 属正常，不是卡住。
4. **默认产物是未签名的**
   `app/build.gradle` 只在 `storePassword` 非空时才配 `signingConfig`，否则 release 包**没有签名**，
   装上去会报「解析包出错」。签名走环境变量（脚本已设）：
   `KEYSTORE` / `KEYSTORE_PASSWORD` / `KEY_ALIAS` / `KEY_PASSWORD`。
5. **Kotlin 元数据版本告警**
   `Module was compiled with an incompatible version of Kotlin ... 1.8.0, expected 1.6.0`
   是 kotlin-stdlib 1.8.22 与 AGP 7.2 的已知不匹配，**只告警不阻断**，产物正常。
