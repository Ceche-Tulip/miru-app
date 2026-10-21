"""最小化 Minidump 解析：取异常码 / 异常地址 / 所属模块 / 线程栈顶部。
用途：定位 miru.exe 崩溃发生在哪个 native 模块。
"""
import struct, sys, os

def parse(path):
    with open(path, "rb") as f:
        data = f.read()

    sig, ver, nstreams, dir_rva = struct.unpack_from("<IIII", data, 0)
    if data[:4] != b"MDMP":
        print("不是 minidump"); return

    streams = {}
    for i in range(nstreams):
        stype, size, rva = struct.unpack_from("<III", data, dir_rva + i * 12)
        streams.setdefault(stype, []).append((size, rva))

    def u32(off): return struct.unpack_from("<I", data, off)[0]
    def u64(off): return struct.unpack_from("<Q", data, off)[0]
    def u16(off): return struct.unpack_from("<H", data, off)[0]

    def read_minidump_string(rva):
        n = u32(rva)  # 字节数（含结尾 \0 的宽字符）
        raw = data[rva + 4: rva + 4 + n]
        return raw.decode("utf-16-le", "replace").rstrip("\x00")

    # --- 模块表 ---
    modules = []  # (base, size, name)
    if 4 in streams:
        size, rva = streams[4][0]
        count = u32(rva)
        for i in range(count):
            m_off = rva + 4 + i * 108
            base = u64(m_off)
            msize = u32(m_off + 8)
            name_rva = u32(m_off + 20)
            modules.append((base, msize, read_minidump_string(name_rva)))
    modules.sort()

    def module_of(addr):
        for base, size, name in modules:
            if base <= addr < base + size:
                return name, addr - base
        return None, None

    # --- 异常流 ---
    code = flags = addr = None
    if 6 in streams:
        size, rva = streams[6][0]
        code = u32(rva + 8)
        flags = u32(rva + 12)
        addr = u64(rva + 24)
        nparams = u32(rva + 32)
        params = [u64(rva + 40 + 8 * k) for k in range(min(nparams, 15))]
        name, off = module_of(addr)
        print(f"异常码: 0x{code:08X}  flags=0x{flags:X}")
        print(f"异常地址: 0x{addr:X} -> {name} + 0x{off:X}" if name else f"异常地址: 0x{addr:X} -> <未知模块>")
        print(f"参数: {[hex(p) for p in params]}")
        if code == 0xC0000005 and len(params) >= 2:
            kind = {0: "读", 1: "写", 8: "执行"}.get(params[0], params[0])
            print(f"访问违规类型: {kind}  访问地址: 0x{params[1]:X}")
            n2, o2 = module_of(params[1])
            print(f"  目标地址归属: {n2} + 0x{o2:X}" if n2 else "  目标地址归属: <未知/野指针>")

    # --- 线程栈（只取前几个线程，并做伪回溯） ---
    if 3 in streams:
        size, rva = streams[3][0]
        nth = u32(rva)
        print(f"\n线程数: {nth}")
        for i in range(min(nth, 8)):
            t_off = rva + 4 + i * 48
            tid = u32(t_off)
            stack_start = u64(t_off + 24)
            stack_size = u32(t_off + 32)
            stack_rva = u32(t_off + 36)
            ctx_size = u32(t_off + 40)
            ctx_rva = u32(t_off + 44)
            rip = rsp = None
            if ctx_size >= 0x100:
                rip = u64(ctx_rva + 0xF8)
                rsp = u64(ctx_rva + 0x98)
            name, off = module_of(rip) if rip else (None, None)
            tag = "  <-- 崩溃线程" if i == 0 else ""
            if name:
                print(f"  线程 {i} tid={tid} rip=0x{rip:X} ({os.path.basename(name)}+0x{off:X}){tag}")
            else:
                print(f"  线程 {i} tid={tid} rip={hex(rip) if rip else '?'}{tag}")
            # 伪回溯：在栈内存里扫描落在模块内的指针
            if stack_size and stack_rva:
                stack = data[stack_rva: stack_rva + min(stack_size, 0x4000)]
                hits = []
                for k in range(0, len(stack) - 8, 8):
                    v = struct.unpack_from("<Q", stack, k)[0]
                    mn, mo = module_of(v)
                    if mn and not mn.lower().endswith(("ntdll.dll", "kernel32.dll", "kernelbase.dll")):
                        hits.append(f"{os.path.basename(mn)}+0x{mo:X}")
                if hits:
                    seen = []
                    for h in hits:
                        if not seen or seen[-1] != h:
                            seen.append(h)
                    print("      栈上代码指针:", " | ".join(seen[:14]))

    # --- 内存中的可疑字符串（判断崩溃前在干嘛） ---
    print("\n模块清单（按地址）:")
    for base, size, name in modules:
        if any(k in name.lower() for k in ("miru", "flutter", "quickjs", "mpv", "media_kit", "webview", "isar", "d3d", "opengl")):
            print(f"  0x{base:012X} {name}")

if __name__ == "__main__":
    for p in sys.argv[1:]:
        print("=" * 70)
        print(p, f"({os.path.getsize(p)/1048576:.1f} MB)")
        parse(p)
