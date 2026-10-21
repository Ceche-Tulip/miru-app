"""创建 / 删除 Windows 目录联接（junction），不需要管理员权限，也不需要 cmd.exe。

用法:
    python mkjunction.py create <link_dir> <target_dir>
    python mkjunction.py delete <link_dir>
    python mkjunction.py check  <link_dir>
"""
import ctypes
import os
import struct
import sys
from ctypes import wintypes

GENERIC_WRITE = 0x40000000
FILE_SHARE_READ = 0x1
FILE_SHARE_WRITE = 0x2
FILE_SHARE_DELETE = 0x4
OPEN_EXISTING = 3
FILE_FLAG_BACKUP_SEMANTICS = 0x02000000
FILE_FLAG_OPEN_REPARSE_POINT = 0x00200000
FSCTL_SET_REPARSE_POINT = 0x000900A4
FSCTL_DELETE_REPARSE_POINT = 0x000900AC
IO_REPARSE_TAG_MOUNT_POINT = 0xA0000003
INVALID_HANDLE_VALUE = ctypes.c_void_p(-1).value

kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
kernel32.CreateFileW.restype = wintypes.HANDLE
kernel32.CreateFileW.argtypes = [
    wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD, wintypes.LPVOID,
    wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE,
]
kernel32.DeviceIoControl.restype = wintypes.BOOL
kernel32.DeviceIoControl.argtypes = [
    wintypes.HANDLE, wintypes.DWORD, wintypes.LPVOID, wintypes.DWORD,
    wintypes.LPVOID, wintypes.DWORD, ctypes.POINTER(wintypes.DWORD), wintypes.LPVOID,
]
kernel32.CloseHandle.argtypes = [wintypes.HANDLE]


def _open(path, access=GENERIC_WRITE):
    h = kernel32.CreateFileW(
        path, access,
        FILE_SHARE_READ | FILE_SHARE_WRITE | FILE_SHARE_DELETE,
        None, OPEN_EXISTING,
        FILE_FLAG_OPEN_REPARSE_POINT | FILE_FLAG_BACKUP_SEMANTICS,
        None,
    )
    if h == INVALID_HANDLE_VALUE or h is None:
        raise OSError(ctypes.get_last_error(), f"CreateFileW 失败: {path}")
    return h


def create(link, target):
    link = os.path.abspath(link)
    target = os.path.abspath(target)
    if not os.path.isdir(target):
        os.makedirs(target, exist_ok=True)
    if os.path.exists(link) and os.listdir(link):
        raise SystemExit(f"链接目录非空，拒绝覆盖: {link}")
    os.makedirs(link, exist_ok=True)

    sub = "\\??\\" + target
    sub_b = sub.encode("utf-16-le")
    print_b = target.encode("utf-16-le")

    data = struct.pack("<IHH", IO_REPARSE_TAG_MOUNT_POINT, 0, 0)
    data += struct.pack("<HHHH", 0, len(sub_b), len(sub_b) + 2, len(print_b))
    data += sub_b + b"\x00\x00" + print_b + b"\x00\x00"
    # 回填 ReparseDataLength（不含 8 字节头部）
    data = data[:4] + struct.pack("<H", len(data) - 8) + data[6:]

    h = _open(link)
    try:
        returned = wintypes.DWORD(0)
        ok = kernel32.DeviceIoControl(
            h, FSCTL_SET_REPARSE_POINT, data, len(data), None, 0,
            ctypes.byref(returned), None,
        )
        if not ok:
            raise OSError(ctypes.get_last_error(), "FSCTL_SET_REPARSE_POINT 失败")
    finally:
        kernel32.CloseHandle(h)
    print(f"[OK] {link}  ==>  {target}")


def delete(link):
    link = os.path.abspath(link)
    h = _open(link)
    try:
        # REPARSE_DATA_BUFFER: tag + 数据长度 0 + Reserved + 四个偏移/长度字段全 0
        data = struct.pack("<IHH", IO_REPARSE_TAG_MOUNT_POINT, 0, 0)
        data += struct.pack("<HHHH", 0, 0, 0, 0)
        returned = wintypes.DWORD(0)
        ok = kernel32.DeviceIoControl(
            h, FSCTL_DELETE_REPARSE_POINT, data, len(data), None, 0,
            ctypes.byref(returned), None,
        )
        if not ok:
            raise OSError(ctypes.get_last_error(), "FSCTL_DELETE_REPARSE_POINT 失败")
    finally:
        kernel32.CloseHandle(h)
    print(f"[OK] 已移除联接: {link}")


def check(link):
    link = os.path.abspath(link)
    print("存在:", os.path.exists(link))
    print("是目录:", os.path.isdir(link))
    try:
        print("真实路径:", os.path.realpath(link))
    except OSError as e:
        print("realpath 失败:", e)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__)
        raise SystemExit(1)
    cmd = sys.argv[1]
    if cmd == "create" and len(sys.argv) == 4:
        create(sys.argv[2], sys.argv[3])
    elif cmd == "delete" and len(sys.argv) == 3:
        delete(sys.argv[2])
    elif cmd == "check" and len(sys.argv) == 3:
        check(sys.argv[2])
    else:
        print(__doc__)
        raise SystemExit(1)
