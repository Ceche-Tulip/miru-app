"""把 windows/flutter/ephemeral/.plugin_symlinks 下的「复制目录」换成 junction。

背景：这台机器没开 Windows 开发者模式，`flutter pub get` 建不了符号链接，
于是把插件目录整个复制过来；紧接着 `flutter build windows` 又要 `Link.createSync`，
就会报 `PathExistsException ... errno = 183`。

junction 不需要管理员权限，而 Dart 的 Link.existsSync() 对 junction 返回 true，
所以换成 junction 之后 flutter 会跳过创建，CMake 也能正常找到插件目录。
"""
import os
import re
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mkjunction as mj


def pick_version(cache_root, name):
    cands = []
    for entry in os.listdir(cache_root):
        if entry == name or entry.startswith(name + "-"):
            cands.append(entry)

    def ver(e):
        m = re.search(r"-([\d.]+)(?:[+-].*)?$", e)
        return tuple(int(x) for x in m.group(1).split(".")) if m else (0,)

    cands.sort(key=ver)
    return os.path.join(cache_root, cands[-1]) if cands else None


def main():
    project = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    links_dir = os.path.join(project, "windows", "flutter", "ephemeral", ".plugin_symlinks")
    cache_root = os.path.join(
        os.environ.get("PUB_CACHE", os.path.expanduser("~/AppData/Local/Pub/Cache")),
        "hosted", "pub.flutter-io.cn",
    )
    if not os.path.isdir(links_dir):
        print("没有 .plugin_symlinks，先跑 flutter pub get")
        return
    if not os.path.isdir(cache_root):
        print("找不到 pub cache:", cache_root)
        return

    fixed = skipped = failed = 0
    for name in sorted(os.listdir(links_dir)):
        path = os.path.join(links_dir, name)
        attrs = os.stat(path).st_file_attributes if hasattr(os.stat(path), "st_file_attributes") else 0
        if attrs & 0x400:  # FILE_ATTRIBUTE_REPARSE_POINT
            skipped += 1
            continue
        target = pick_version(cache_root, name)
        if not target:
            print(f"  [skip] {name} 在 cache 里找不到对应版本")
            failed += 1
            continue
        try:
            shutil.rmtree(path)
            mj.create(path, target)
            fixed += 1
        except Exception as e:
            print(f"  [fail] {name}: {e}")
            failed += 1

    print(f"完成：替换 {fixed} 个，已是链接 {skipped} 个，失败 {failed} 个")


if __name__ == "__main__":
    main()
