# 更新日志

本文件记录本 fork 相对上游的发行版本。上游历史请见
[miru-project/miru-app](https://github.com/miru-project/miru-app/commits/dev)。

## v1.8.1-rune.1 — 2026-10-21

基于上游 `miru-project/miru-app` v1.8.1+39（提交 [`8599d0d`](https://github.com/miru-project/miru-app/commit/8599d0d)）。
这是本 fork 的第一个发行版，目标是让「小说类扩展」在 Miru 里真正可用：修复了客户端层面的搜索限制，
并处理了阅读器、详情页与输入法的若干恼人问题。代码改动集中在 5 个 Dart 文件，逐个提交可单独审视。

### 🚀 功能改进

- **搜索支持「POST → 302」型站点**：不再依赖 `dart:io` 的自动重定向，改为手动跟随 3xx
  （302/303 后转 GET，最多 5 跳），所有扩展共用这条网络路径
  （[`640c92b`](https://github.com/Ceche-Tulip/miru-app/commit/640c92b)）
- 详情页把简介卡片移到章节目录之前，进入详情先看到简介
  （[`c9592e2`](https://github.com/Ceche-Tulip/miru-app/commit/c9592e2)）
- 窄窗口下也显示封面（140px），不再因为宽度不足 600px 直接不渲染
  （[`c9592e2`](https://github.com/Ceche-Tulip/miru-app/commit/c9592e2)）

### 🐛 问题修复

- 阅读器翻到下一章后，正文大标题仍显示进入时那一章的标题
  （[`79c5c17`](https://github.com/Ceche-Tulip/miru-app/commit/79c5c17)）
- 中文输入法在搜索框删除后重新输入，会出现 `da'meng'zhuda'meng'z` 这样的重复上屏
  （[`eac3023`](https://github.com/Ceche-Tulip/miru-app/commit/eac3023)）
- 首页「最近阅读」卡片在封面为空字符串时，会去请求空 URL 并报 `failed to load image`
  （[`c9592e2`](https://github.com/Ceche-Tulip/miru-app/commit/c9592e2)）

### 🏗️ 构建与工程

- 依赖锁定改为镜像地址，避免 `pub get` 把镜像当成换了源、重解析并把 `media_kit_video`
  升到 1.2.5（该版本删除了 `SubtitleViewState` 的 setter，直接编译失败）
  （[`0f20795`](https://github.com/Ceche-Tulip/miru-app/commit/0f20795)）
- 新增一键构建脚本 `build.sh`、构建辅助 `tools/`、构建说明 `BUILD.md`、改动清单 `PATCHES.md`
  （[`0f20795`](https://github.com/Ceche-Tulip/miru-app/commit/0f20795)）

### ⚠️ 已知问题

- 偶发 `0xC0000005` 崩溃（`flutter_windows.dll+0x13481`，空指针读 `0x170`），
  栈上与副窗口（`desktop_multi_window`）相关。属引擎层问题，本版未修复；
  崩溃转储默认写入 `%LOCALAPPDATA%\CrashDumps`，单份约 40MB
- 影视/漫画条目的 TMDB 元数据在部分网络环境下会 401 或连接超时，属上游自带的联网功能，不影响阅读
- 部分站点的作品简介由站方截断，客户端无法补全
- 推荐配合 [miru-extensions](https://github.com/Ceche-Tulip/miru-extensions) 使用

### 📦 安装

本版提供 Windows x64 便携版（解压即用，无需安装）：

1. 下载 `miru-1.8.1-rune.1-win64.zip` 并校验 `SHA256SUMS.txt`
2. 解压到任意目录（建议不要放在 `Program Files` 下）
3. 运行 `miru.exe`；数据目录沿用 `%USERPROFILE%\Documents\miru`

> Windows 可能提示"未知发布者"——本版未做代码签名，属预期行为。

## 版本号约定

`v<上游版本>-rune.<序号>`：上游版本不变，`rune.N` 表示本 fork 的第 N 次发行。
