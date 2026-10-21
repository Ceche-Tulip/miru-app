# 本 fork 相对上游的改动

上游：[`miru-project/miru-app`](https://github.com/miru-project/miru-app) v1.8.1+39（2024-04-16，AGPL-3.0）
基线提交：`8599d0d`

改动集中在 5 个 Dart 文件 + 构建工具，`git log` 里每个提交对应一个问题。
上游若继续更新，用 `git diff 8599d0d..HEAD -- lib/ pubspec.lock` 取补丁再 rebase 即可。

| 提交主题 | 文件 | 解决的问题 |
| --- | --- | --- |
| `fix(network): 手动跟随重定向` | `lib/data/services/extension_service.dart` | 扩展的 `POST → 302` 搜索永远失败 |
| `fix(reader): 章节标题不刷新` | `lib/views/pages/watch/reader/novel/novel_reader_content.dart` | 翻到下一章，正文大标题还是旧章名 |
| `fix(search): 修复中文输入法重复上屏` | `lib/views/pages/search/search_page.dart` | 删字重打出现 `da'meng'zhuda'meng'z` |
| `fix(detail): 简介前置 / 封面 / 空封面兜底` | `lib/views/pages/detail_page.dart`、`lib/views/widgets/home/home_resent_card.dart` | 简介在目录之后、窄窗口无封面、历史记录空封面报错 |
| `build: 固定依赖源与工具链` | `pubspec.lock`、`build.sh`、`tools/`、`BUILD.md` | 国内网络下可重复构建 |

## 1. 手动跟随重定向（核心）

`dart:io` 的自动重定向**只对 GET / HEAD 生效**（见 [Dart 文档](https://api.dart.dev/stable/dart-io/HttpClientRequest/followRedirects.html)），
POST 收到 302 时 dio 会把它当异常抛出。而大量中文小说站的搜索就是「POST 表单 → 302 跳到结果页」。

改法：`jsRequest` 里关掉自动跟随，自己读 `Location` 重发（302/303 之后改 GET，最多 5 跳），对齐浏览器行为。
对**所有扩展**生效，不只是书海阁。

## 2. 阅读器标题

`novel_reader_content.dart` 用 `_c.playIndex`（构造时固定的 `final` 值）拼标题，永远不会变。
改成 `Obx + _c.index.value`。

## 3. 中文输入法

`search_page.dart` 里输入框的 `TextEditingController` 是在 `build()` 里 `new` 的，
每次重建都会重置输入法的组合状态，于是候选词被反复上屏。改成 `State` 里只创建一次并 `dispose`。

## 4. 详情页

- 简介从「目录之后」移到「目录之前」；
- 封面原本要求窗口宽度 > 600 才渲染，改为窄窗口画 140 宽小图；
- 首页历史卡片原来只判断 `cover == null`，而数据库里存的是空字符串 `""`，
  于是去加载空 URL 并报 `failed to load image`；改为 `== null || isEmpty`。

## 5. 构建（仅影响本机/国内网络，不影响功能）

- `pubspec.lock` 的 `url` 从 `pub.dev` 换成 `pub.flutter-io.cn`：否则 `pub get` 会把镜像当成"换了源"，
  重新解析依赖并把 `media_kit_video` 升到 1.2.5（该版本删了 `SubtitleViewState` 的 setter，直接编译失败）；
- `build.sh` 一键构建，绕开五个坑（详见 `BUILD.md`）；
- `tools/` 里是构建辅助（插件 junction 兜底、符号检查）。

## 构建

```bash
bash build.sh
# 产物：../dist/miru-1.8.1-rune-<时间戳>/miru.exe
```

需要 Flutter 3.22.x（Dart 3.4）、VS2022 C++ 工具链。详细步骤与坑位见 `BUILD.md`。

## 许可

上游是 **AGPL-3.0**，本 fork 沿用。分发编译产物时需同时提供对应源码（本仓库即为源码）。
