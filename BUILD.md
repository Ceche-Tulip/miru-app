# Miru 客户端 fork（Rune 补丁版）

上游：`miru-project/miru-app` v1.8.1+39（HEAD 8599d0d，2024-04-16）
本目录：`src/` 源码、`dist/` 产物、`tools/` 构建辅助、`rune-patches.diff` 补丁总diff

## 为什么要 fork

扩展运行在 App 里，有两件事扩展改不了，只能改客户端：

1. **搜索**：`dart:io` 的自动重定向只对 GET/HEAD 生效，站点返回「POST → 302」时
   dio 直接把 302 当异常抛出。书海阁、以及一大批同类站点都这么实现，于是搜索必崩。
2. **阅读器大标题不刷新**：`novel_reader_content.dart` 里用的是 `_c.playIndex`（构造时固定的死值），
   翻到下一章标题不会变。

## 改了什么（4 处）

| 文件 | 改动 |
| --- | --- |
| `lib/data/services/extension_service.dart` | `jsRequest` 手动跟随重定向（3xx + Location → 改用 GET 重发，最多 5 跳）；`hide Response` 消除与 get 的重名 |
| `lib/views/pages/watch/reader/novel/novel_reader_content.dart` | 大标题改用 `Obx + index.value`，翻章即时刷新 |
| `lib/views/pages/detail_page.dart` | 简介 CardTile 移到章节目录**之前**；封面不再要求窗口宽度 > 600（窄窗画 140 宽小图） |
| `pubspec.lock` | `url` 批量换成 `pub.flutter-io.cn` 镜像地址（版本号不动，否则会被重新解析） |

## 构建

```bash
cd D:/SoftWare/Miru/client
bash build.sh
# 产物：dist/miru-1.8.1-rune-win64/miru.exe
```

工具链：

| 项 | 路径 / 版本 |
| --- | --- |
| Flutter | `D:\Tools\Language\Flutter\3.22.3`（Dart 3.4.4） |
| PUB_CACHE | `D:\Tools\Language\Flutter\pub-cache` |
| 镜像 | `PUB_HOSTED_URL=https://pub.flutter-io.cn`、`FLUTTER_STORAGE_BASE_URL=https://storage.flutter-io.cn` |
| 编译器 | VS2022 BuildTools 14.44（MSVC + Windows SDK 10.0.26100 + CMake + Ninja） |

### 五个必须知道的坑

1. **没开 Windows 开发者模式** → `pub get` 只能复制插件目录，flutter 随后重复建链接报 `PathExistsException`。
   已做两件事：`tools/fix_plugin_symlinks.py` 把复制目录换成 junction；并给 Flutter SDK 的
   `packages/flutter_tools/lib/src/flutter_plugins.dart` 打了补丁（`errno 183` 跳过）。
   **改完 SDK 要删 `bin/cache/flutter_tools.snapshot` 和 `.stamp`**，否则用的还是旧快照。
2. **media_kit 的两份预编译包**（`mpv-dev-...7z`、`ANGLE.7z`）走 GitHub 直连必失败，
   要用 `gh-proxy.com` 下好放进 `build/windows/x64/`，脚本已自动处理。
3. **`pub get` 会重解析依赖**：只要 lock 里的 url 和当前 `PUB_HOSTED_URL` 不一致，pub 就认为换了源，
   于是把 `media_kit_video` 升到 1.2.5，而 1.2.5 的 `SubtitleViewState` 去掉了 `textAlign/style` setter → 编译失败。
   所以 lock 的 url 必须先改成镜像地址，版本必须锁在 1.2.4。
4. `easy_refresh 3.3.4` 用了 Flutter 3.22 已删除的 `TextTheme.subtitle1/caption`，
   已直接改 pub cache 里该文件（换 Flutter 3.19 则不需要）。
5. `flutter clean` 之后插件链接会退回复制目录，**每次 clean 后要重跑 `build.sh`**。

## 待办

- APK：需要装 Android SDK + BuildTools + Gradle（约 1.5GB），`flutter build apk --release`。
- 上游跟进：补丁集中在 4 个文件，upstream 更新时可 `git diff rune-patches.diff` 重新应用。
