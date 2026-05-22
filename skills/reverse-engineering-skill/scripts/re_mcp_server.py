# /// script
# dependencies = [
#     "fastmcp",
# ]
# ///
"""
Reverse Engineering MCP Server
Enhanced for Claude Desktop — autonomous RE of PE, ELF, Mach-O, APK, JAR, .NET
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from fastmcp import FastMCP

mcp = FastMCP("ReverseEngineering")

MAX_TEXT = 16000
MAX_STRINGS = 2000
CHUNK_SIZE = 1024 * 1024


# ─────────────────────────────────────────────
# Utility helpers
# ─────────────────────────────────────────────

def _norm(path: str) -> Path:
    return Path(os.path.expanduser(path)).resolve()

def _exists(path: str) -> Tuple[bool, Optional[Path], str]:
    p = _norm(path)
    if not p.exists():
        return False, None, f"Error: path not found: {path!r}"
    return True, p, ""

def _safe_read_bytes(path: Path, max_bytes: Optional[int] = None) -> bytes:
    with path.open("rb") as f:
        return f.read() if max_bytes is None else f.read(max_bytes)

def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(CHUNK_SIZE), b""):
            h.update(chunk)
    return h.hexdigest()

def _md5(path: Path) -> str:
    h = hashlib.md5()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(CHUNK_SIZE), b""):
            h.update(chunk)
    return h.hexdigest()

def _entropy(path: Path, sample_bytes: int = 8 * 1024 * 1024) -> float:
    data = _safe_read_bytes(path, sample_bytes)
    if not data:
        return 0.0
    counts = [0] * 256
    for b in data:
        counts[b] += 1
    total = len(data)
    ent = 0.0
    for c in counts:
        if c:
            p = c / total
            ent -= p * math.log2(p)
    return round(ent, 4)

def _which(*names: str) -> Optional[str]:
    for name in names:
        p = shutil.which(name)
        if p:
            return p
    return None

def _run(cmd: List[str], timeout: int = 60, cwd: Optional[Path] = None,
         env: Optional[Dict] = None) -> Dict[str, Any]:
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(cwd) if cwd else None,
            env=env,
        )
        return {
            "ok": True,
            "cmd": " ".join(cmd),
            "returncode": proc.returncode,
            "stdout": proc.stdout[:MAX_TEXT],
            "stderr": proc.stderr[:MAX_TEXT],
        }
    except subprocess.TimeoutExpired:
        return {"ok": False, "cmd": " ".join(cmd), "error": "timeout"}
    except Exception as e:
        return {"ok": False, "cmd": " ".join(cmd), "error": str(e)}

def _cap(s: str, limit: int = MAX_TEXT) -> str:
    return s if len(s) <= limit else s[:limit] + "\n...[truncated]..."

def _j(data: Any) -> str:
    return json.dumps(data, indent=2, ensure_ascii=False)

def _magic(path: Path) -> bytes:
    with path.open("rb") as f:
        return f.read(16)


# ─────────────────────────────────────────────
# Format detection
# ─────────────────────────────────────────────

def _file_kind(path: Path) -> Dict[str, Any]:
    m = _magic(path)
    info: Dict[str, Any] = {
        "magic_hex": m[:8].hex(),
        "format": "unknown",
        "platform": "unknown",
        "arch": "unknown",
        "bits": "unknown",
        "endian": "unknown",
    }

    if m.startswith(b"\x7fELF"):
        info["format"] = "ELF"
        info["platform"] = "linux/android"
        info["bits"] = "64" if m[4] == 2 else "32"
        info["endian"] = "little" if m[5] == 1 else "big"
        etype = int.from_bytes(m[16:18], "little" if m[5] == 1 else "big")
        info["elf_type"] = {2: "executable", 3: "shared_lib", 4: "core"}.get(etype, hex(etype))
        emach = int.from_bytes(m[18:20], "little" if m[5] == 1 else "big")
        info["arch"] = {
            0x03: "x86", 0x28: "arm32", 0x3E: "x86_64", 0xB7: "arm64",
            0xF3: "riscv", 0x08: "mips",
        }.get(emach, hex(emach))

    elif m.startswith(b"MZ"):
        info["format"] = "PE"
        info["platform"] = "windows"
        # Try to read PE header for arch
        try:
            with path.open("rb") as f:
                f.seek(0x3C)
                pe_offset = int.from_bytes(f.read(4), "little")
                f.seek(pe_offset + 4)
                machine = int.from_bytes(f.read(2), "little")
                info["arch"] = {
                    0x014C: "x86", 0x8664: "x86_64", 0xAA64: "arm64",
                    0x01C0: "arm32", 0x0200: "ia64",
                }.get(machine, hex(machine))
                f.seek(pe_offset + 4 + 18)
                characteristics = int.from_bytes(f.read(2), "little")
                info["is_dll"] = bool(characteristics & 0x2000)
                info["is_exe"] = bool(characteristics & 0x0002)
                f.seek(pe_offset + 4 + 20)
                opt_magic = int.from_bytes(f.read(2), "little")
                info["bits"] = "64" if opt_magic == 0x20B else "32"
        except Exception:
            pass

    elif m[:4] in {
        b"\xfe\xed\xfa\xce", b"\xce\xfa\xed\xfe",
        b"\xfe\xed\xfa\xcf", b"\xcf\xfa\xed\xfe",
        b"\xca\xfe\xba\xbe",
    }:
        info["format"] = "Mach-O"
        info["platform"] = "macos/ios"
        if m[:4] == b"\xca\xfe\xba\xbe":
            info["arch"] = "universal/fat"
        elif m[:4] in {b"\xfe\xed\xfa\xcf", b"\xcf\xfa\xed\xfe"}:
            info["bits"] = "64"
        else:
            info["bits"] = "32"
        info["endian"] = "big" if m[0] == 0xFE else "little"

    elif m.startswith(b"PK\x03\x04"):
        info["format"] = "ZIP"
        info["platform"] = "multi (jar/apk/zip)"
        info["arch"] = "n/a"

    elif m.startswith(b"\xca\xfe\xba\xbe") and len(m) >= 8:
        # Could be Java .class file too (same magic as fat Mach-O — check by context)
        info["format"] = "Mach-O or Java .class"

    elif m[:4] == b"dex\n":
        info["format"] = "DEX"
        info["platform"] = "android"
        info["arch"] = "dalvik"

    elif m[:2] == b"MZ" or m[:4] == b"BSJB":
        # BSJB = .NET metadata magic
        info["format"] = "PE/.NET"
        info["platform"] = "windows/.net"

    # File command enrichment
    file_exe = _which("file")
    if file_exe:
        res = _run([file_exe, str(path)], timeout=10)
        if res.get("ok"):
            info["file_magic"] = res.get("stdout", "").strip()

    return info


def _is_dotnet(path: Path) -> bool:
    """Check if a PE file is .NET by looking for CLR header."""
    try:
        with path.open("rb") as f:
            f.seek(0x3C)
            pe_off = int.from_bytes(f.read(4), "little")
            f.seek(pe_off + 4 + 20)
            opt_magic = int.from_bytes(f.read(2), "little")
            # Optional header size
            f.seek(pe_off + 4 + 20 + 2)
            if opt_magic == 0x10B:  # PE32
                f.seek(pe_off + 4 + 20 + 208)
            else:  # PE32+
                f.seek(pe_off + 4 + 20 + 224)
            clr_rva = int.from_bytes(f.read(4), "little")
            return clr_rva != 0
    except Exception:
        return False


def _extract_ascii_strings(data: bytes, min_len: int) -> List[str]:
    out = []
    cur: List[str] = []
    for b in data:
        if 32 <= b <= 126:
            cur.append(chr(b))
        else:
            if len(cur) >= min_len:
                out.append("".join(cur))
            cur = []
    if len(cur) >= min_len:
        out.append("".join(cur))
    return out


def _extract_utf16le_strings(data: bytes, min_len: int) -> List[str]:
    out = []
    cur: List[str] = []
    i = 0
    while i + 1 < len(data):
        ch = data[i:i+2]
        if ch[1] == 0 and 32 <= ch[0] <= 126:
            cur.append(chr(ch[0]))
        else:
            if len(cur) >= min_len:
                out.append("".join(cur))
            cur = []
        i += 2
    if len(cur) >= min_len:
        out.append("".join(cur))
    return out


def _tool_inventory() -> Dict[str, Optional[str]]:
    names = [
        "radare2", "rizin", "r2", "strings", "file", "nm",
        "objdump", "readelf", "otool", "lipo", "class-dump",
        "jadx", "apktool", "dex2jar",
        "ilspycmd", "monodis",
        "upx", "java", "dotnet",
        "codesign", "jtool2",
    ]
    return {n: _which(n) for n in names}


# ─────────────────────────────────────────────
# Intelligence patterns
# ─────────────────────────────────────────────

_PATTERNS = {
    "urls": re.compile(r'https?://[^\s\'"<>]{5,}'),
    "ips": re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b'),
    "domains": re.compile(r'\b(?:[a-zA-Z0-9-]{2,63}\.){1,5}(?:com|net|org|io|ru|cn|de|uk|cc|to|onion)\b'),
    "aws_key": re.compile(r'(?:AKIA|ASIA|AROA|AIDA|ANPA|ANVA|APKA)[A-Z0-9]{16}'),
    "jwt": re.compile(r'eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}'),
    "hex_key_32": re.compile(r'\b[0-9a-fA-F]{32}\b'),
    "hex_key_64": re.compile(r'\b[0-9a-fA-F]{64}\b'),
    "pdb_path": re.compile(r'[A-Za-z]:\\.*?\.pdb'),
    "registry": re.compile(r'HKEY_[A-Z_]+\\[^\s"]{5,}'),
    "emails": re.compile(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z]{2,}'),
    "file_paths_win": re.compile(r'[A-Za-z]:\\(?:[^\\/:*?"<>|\r\n]+\\)*[^\\/:*?"<>|\r\n]*'),
    "file_paths_unix": re.compile(r'/(?:usr|home|etc|var|tmp|opt|proc)/[^\s"\'<>]{3,}'),
    "base64_candidate": re.compile(r'[A-Za-z0-9+/]{40,}={0,2}'),
    "crypto_constants": re.compile(r'\b(?:AES|DES|RSA|SHA1|SHA256|SHA512|MD5|RC4|ChaCha|Salsa|Blowfish|ECDH|ECDSA|secp256|curve25519)\b', re.I),
    "suspicious_imports": re.compile(r'\b(?:VirtualAlloc|VirtualProtect|WriteProcessMemory|CreateRemoteThread|NtUnmapViewOfSection|IsDebuggerPresent|CheckRemoteDebuggerPresent|SetWindowsHookEx|GetAsyncKeyState|URLDownloadToFile|ShellExecute|WinExec|CreateProcess|RegSetValue|RegCreateKey|InternetOpen|HttpSendRequest|send|recv|socket|WSAStartup)\b'),
    "packer_sigs": re.compile(r'\b(?:UPX|MPRESS|Themida|VMProtect|Enigma|ASPack|PECompact|netshrink|Confuser|de4dot|ConfuserEx|SmartAssembly)\b', re.I),
}


def _classify_strings(strings: List[str]) -> Dict[str, List[str]]:
    result: Dict[str, List[str]] = {k: [] for k in _PATTERNS}
    combined = "\n".join(strings)
    for category, pattern in _PATTERNS.items():
        found = pattern.findall(combined)
        # Deduplicate
        seen: set = set()
        for item in found:
            if item not in seen:
                seen.add(item)
                result[category].append(item)
    return result


# ─────────────────────────────────────────────
# MCP Tools
# ─────────────────────────────────────────────

@mcp.tool()
def inspect_binary(file_path: str) -> str:
    """
    Triage a binary: format, architecture, platform, entropy, hashes, packer hints.
    This is always the first tool to call on any unknown file.
    """
    ok, p, err = _exists(file_path)
    if not ok:
        return err

    st = p.stat()
    kind = _file_kind(p)
    ent = _entropy(p)

    result = {
        "path": str(p),
        "name": p.name,
        "size_bytes": st.st_size,
        "size_human": f"{st.st_size / 1024:.1f} KB" if st.st_size < 1048576 else f"{st.st_size / 1048576:.1f} MB",
        "sha256": _sha256(p),
        "md5": _md5(p),
        "entropy": ent,
        "entropy_interpretation": (
            "packed/encrypted (>7.2)" if ent > 7.2
            else "elevated (6.5-7.2)" if ent > 6.5
            else "normal"
        ),
        "format": kind,
        "is_dotnet": _is_dotnet(p) if kind.get("format") == "PE" else False,
        "is_dir": p.is_dir(),
        "tools_available": _tool_inventory(),
    }

    # Quick packer scan
    try:
        data = _safe_read_bytes(p, 2 * 1024 * 1024)
        strings_sample = _extract_ascii_strings(data, 4)[:300]
        packer_hits = [s for s in strings_sample if _PATTERNS["packer_sigs"].search(s)]
        result["packer_signatures_found"] = packer_hits
    except Exception:
        result["packer_signatures_found"] = []

    return _j(result)


@mcp.tool()
def extract_strings(file_path: str, min_length: int = 4, include_utf16: bool = True,
                    classify: bool = True) -> str:
    """
    Extract all printable strings from a binary. When classify=True, also buckets
    them into URLs, IPs, secrets, registry keys, crypto constants, suspicious Win32 APIs, etc.
    """
    ok, p, err = _exists(file_path)
    if not ok:
        return err

    strings: List[str] = []

    native = _which("strings")
    if native:
        args = [native, "-n", str(min_length)]
        if include_utf16:
            args += ["-e", "l"]  # little-endian UTF-16
        res1 = _run([native, "-n", str(min_length), str(p)], timeout=30)
        if res1.get("ok") and res1.get("stdout"):
            strings.extend(res1["stdout"].splitlines())
        if include_utf16:
            res2 = _run([native, "-n", str(min_length), "-e", "l", str(p)], timeout=30)
            if res2.get("ok") and res2.get("stdout"):
                strings.extend(res2["stdout"].splitlines())

    if not strings:
        data = _safe_read_bytes(p)
        strings.extend(_extract_ascii_strings(data, min_length))
        if include_utf16:
            strings.extend(_extract_utf16le_strings(data, min_length))

    # Deduplicate preserving order
    seen: set = set()
    cleaned: List[str] = []
    for s in strings:
        s = s.strip()
        if s and s not in seen:
            seen.add(s)
            cleaned.append(s)

    result: Dict[str, Any] = {
        "total_unique_strings": len(cleaned),
        "strings": cleaned[:MAX_STRINGS],
        "truncated": len(cleaned) > MAX_STRINGS,
    }

    if classify:
        result["intelligence"] = _classify_strings(cleaned)

    return _j(result)


@mcp.tool()
def analyze_bundle(root_path: str, max_depth: int = 4) -> str:
    """
    Recursively triage an app bundle, extracted APK, or unpacked directory.
    Returns inventory of all binaries, configs, and interesting files with format hints.
    """
    ok, p, err = _exists(root_path)
    if not ok:
        return err
    if not p.is_dir():
        return "Error: path is not a directory. Use inspect_binary for files."

    interesting_exts = {
        ".exe", ".dll", ".sys", ".ocx", ".msi", ".scr",
        ".dylib", ".so", ".bundle", ".app", ".framework", ".kext",
        ".jar", ".class", ".dex", ".apk", ".aab", ".aar",
        ".plist", ".json", ".xml", ".yaml", ".yml", ".conf", ".cfg", ".ini",
        ".sqlite", ".db", ".key", ".pem", ".cer", ".pfx", ".p12",
    }

    items = []
    base_depth = len(p.parts)

    for item in sorted(p.rglob("*")):
        try:
            depth = len(item.parts) - base_depth
            if depth > max_depth or item.is_dir():
                continue
            suffix = item.suffix.lower()
            kind = _file_kind(item)
            size = item.stat().st_size

            is_interesting = (
                kind["format"] != "unknown"
                or suffix in interesting_exts
                or item.name.lower() in {"macos", "info.plist", "androidmanifest.xml"}
                or (size > 0 and suffix == "")  # no-extension binary
            )

            if is_interesting:
                entry = {
                    "path": str(item.relative_to(p)),
                    "abs_path": str(item),
                    "size_bytes": size,
                    "format": kind["format"],
                    "arch": kind.get("arch", "?"),
                    "platform": kind.get("platform", "?"),
                    "entropy": _entropy(item),
                    "suffix": suffix,
                }
                items.append(entry)
        except Exception:
            continue

    items.sort(key=lambda x: (x["format"] == "unknown", -x["entropy"], -x["size_bytes"]))

    return _j({
        "root": str(p),
        "total_interesting_files": len(items),
        "items": items[:500],
    })


@mcp.tool()
def get_binary_metadata(file_path: str) -> str:
    """
    Deep metadata extraction using native tools:
    - Mach-O: otool (load commands, deps, symbols), codesign entitlements
    - ELF: readelf (headers, sections, dynamic), nm (symbols)
    - PE: objdump (imports, sections), dumpbin if available
    Returns everything — sections, imports, exports, symbols, linked libraries.
    """
    ok, p, err = _exists(file_path)
    if not ok:
        return err

    kind = _file_kind(p)
    fmt = kind.get("format", "unknown")
    out: Dict[str, Any] = {"file": str(p), "format": fmt, "results": {}}

    if fmt == "Mach-O":
        for flag, label in [("-l", "load_commands"), ("-L", "linked_libs"), ("-h", "header")]:
            tool = _which("otool")
            if tool:
                out["results"][label] = _run([tool, flag, str(p)], timeout=20)
        nm = _which("nm")
        if nm:
            out["results"]["symbols"] = _run([nm, "-m", str(p)], timeout=20)
        # Entitlements
        cs = _which("codesign")
        if cs:
            out["results"]["entitlements"] = _run(
                [cs, "-d", "--entitlements", "-", str(p)], timeout=10)
            out["results"]["codesign_info"] = _run(
                [cs, "-dv", "--verbose=4", str(p)], timeout=10)
        # class-dump for ObjC
        cd = _which("class-dump")
        if cd:
            out["results"]["objc_classes"] = _run([cd, str(p)], timeout=30)

    elif fmt == "ELF":
        re_tool = _which("readelf")
        if re_tool:
            for flag, label in [
                ("-h", "elf_header"),
                ("-S", "sections"),
                ("-d", "dynamic"),
                ("-s", "symbols"),
                ("--segments", "segments"),
            ]:
                out["results"][label] = _run([re_tool, flag, str(p)], timeout=20)
        nm = _which("nm")
        if nm:
            out["results"]["nm_symbols"] = _run([nm, "-an", "--demangle", str(p)], timeout=20)
        od = _which("objdump")
        if od:
            out["results"]["imports"] = _run([od, "-p", str(p)], timeout=20)

    elif fmt in ("PE", "PE/.NET"):
        od = _which("objdump")
        if od:
            out["results"]["pe_headers"] = _run([od, "-p", str(p)], timeout=30)
            out["results"]["disasm_entry"] = _run(
                [od, "-d", "--start-address=0", "--stop-address=0x200", str(p)], timeout=30)
        db = _which("dumpbin")
        if db:
            out["results"]["dumpbin_headers"] = _run([db, "/headers", str(p)], timeout=30)
            out["results"]["dumpbin_imports"] = _run([db, "/imports", str(p)], timeout=30)
            out["results"]["dumpbin_exports"] = _run([db, "/exports", str(p)], timeout=30)

    return _j(out)


@mcp.tool()
def run_r2(file_path: str, commands: str, timeout_sec: int = 45) -> str:
    """
    Run radare2/rizin analysis commands on a binary.
    Useful commands:
      aaa          — deep analysis (find all functions)
      iI           — binary info (arch, os, bits, stripped)
      iS           — sections list
      ii           — imports
      iE           — exports
      ie           — entry points
      afl          — list all functions
      pdf @ main   — disassemble main()
      pdf @ sym.FUNCNAME  — disassemble a specific function
      iz           — strings in data sections
      /ad/ pattern — search for byte pattern
      pdc @ func   — decompile function (requires r2ghidra plugin)
    """
    ok, p, err = _exists(file_path)
    if not ok:
        return err

    r2 = _which("radare2") or _which("rizin") or _which("r2")
    if not r2:
        return _j({"error": "radare2/rizin not found. Install with: brew install radare2"})

    # Safety: block shell escapes
    forbidden = ["!sh", "!bash", "!cmd", "!powershell", ";sh ", "; sh", "||", "&&",
                 "open ", "rm ", "del ", "wget ", "curl "]
    lower = commands.lower()
    if any(x in lower for x in forbidden):
        return "Error: blocked dangerous command content."

    result = _run([r2, "-q", "-e", "scr.color=0", "-c", commands, str(p)],
                  timeout=timeout_sec)
    if not result.get("ok"):
        return _j(result)
    return _cap(result.get("stdout", "") + result.get("stderr", ""))


@mcp.tool()
def decompile(file_path: str, output_dir: str = "", tool_hint: str = "auto") -> str:
    """
    Decompile/disassemble compiled code back to readable source:
    - .NET PE → ILSpyCMD (near-perfect C#)
    - APK/JAR/DEX/CLASS → JADX (readable Java + Android resources)
    - Native (PE/ELF/Mach-O) → radare2 with pdc/pdg (Ghidra decompiler if r2ghidra installed)
    tool_hint: "auto" | "jadx" | "ilspy" | "radare2" | "monodis" | "apktool"
    """
    ok, p, err = _exists(file_path)
    if not ok:
        return err

    if not output_dir:
        output_dir = str(p.parent / f"{p.stem}_decompiled")
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    kind = _file_kind(p)
    suffix = p.suffix.lower()
    attempts = []

    def _attempt(tool: str, cmd: List[str], t: int = 300) -> Dict:
        res = _run(cmd, timeout=t)
        return {"tool": tool, "cmd": " ".join(cmd), "result": res}

    # ── .NET / C# ──────────────────────────────
    if (kind.get("format") in ("PE", "PE/.NET") or tool_hint == "ilspy") and tool_hint != "jadx":
        if _is_dotnet(p) or tool_hint == "ilspy":
            ilspy = _which("ilspycmd")
            if ilspy:
                attempts.append(_attempt("ilspycmd",
                    [ilspy, "-p", "-o", str(out), str(p)]))
                return _j({"output_dir": str(out), "method": ".NET→C#", "attempts": attempts,
                            "note": "ILSpyCMD produced C# source in output_dir."})
            mono = _which("monodis")
            if mono:
                attempts.append(_attempt("monodis", [mono, "--output", str(out / "il_output.il"), str(p)]))
                return _j({"output_dir": str(out), "method": ".NET→IL", "attempts": attempts})

    # ── Android APK / Java JAR ─────────────────
    if suffix in {".apk", ".jar", ".aar", ".aab", ".dex", ".class"} or tool_hint in ("jadx", "apktool"):
        jadx = _which("jadx")
        if jadx:
            attempts.append(_attempt("jadx",
                [jadx, "-d", str(out), "--deobf", "--show-bad-code", str(p)], t=600))
            return _j({"output_dir": str(out), "method": "APK/JAR→Java", "attempts": attempts,
                        "note": "JADX decompiled to Java source + resources in output_dir."})
        apktool = _which("apktool")
        if apktool:
            attempts.append(_attempt("apktool", [apktool, "d", str(p), "-o", str(out), "-f"], t=120))

    # ── Native binaries via radare2 ────────────
    r2 = _which("radare2") or _which("rizin")
    if r2:
        cmds = "aaa; iI; iS; ii; iE; afl; s main; pdf"
        # Try r2ghidra decompiler if available
        ghidra_cmds = "aaa; s main; pdg"
        res = _run([r2, "-q", "-e", "scr.color=0", "-c", ghidra_cmds, str(p)], timeout=120)
        if res.get("ok") and "cannot find" not in res.get("stderr", "").lower():
            attempts.append({"tool": "r2+r2ghidra", "result": res})
        else:
            res2 = _run([r2, "-q", "-e", "scr.color=0", "-c", cmds, str(p)], timeout=120)
            attempts.append({"tool": "radare2", "result": res2})
            # Save disasm to file
            disasm_path = out / "radare2_analysis.txt"
            if res2.get("stdout"):
                disasm_path.write_text(res2["stdout"])
        return _j({"output_dir": str(out), "method": "native→disasm", "attempts": attempts})

    return _j({"output_dir": str(out), "attempts": attempts,
               "error": "No decompiler found. Install jadx, ilspycmd, or radare2."})


@mcp.tool()
def read_plist(file_path: str) -> str:
    """
    Read and decode a .plist file (binary or XML). Returns JSON representation.
    Essential for macOS app bundles (Info.plist reveals bundle ID, permissions, version).
    """
    ok, p, err = _exists(file_path)
    if not ok:
        return err

    # Try plutil (macOS native)
    plutil = _which("plutil")
    if plutil:
        res = _run([plutil, "-convert", "json", "-o", "-", str(p)], timeout=10)
        if res.get("ok") and res.get("returncode") == 0:
            return res.get("stdout", "")

    # Try Python plistlib
    try:
        import plistlib
        with p.open("rb") as f:
            data = plistlib.load(f)
        return json.dumps(data, indent=2, default=str)
    except Exception as e:
        return f"Error reading plist: {e}"


@mcp.tool()
def unpack_archive(file_path: str, output_dir: str = "") -> str:
    """
    Extract ZIP, APK, IPA, AAB, JAR, tar.gz, tar.bz2, or other archives.
    Returns the output directory path and a file listing.
    """
    ok, p, err = _exists(file_path)
    if not ok:
        return err

    if not output_dir:
        output_dir = str(p.parent / f"{p.stem}_extracted")
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    suffix = p.suffix.lower()
    name = p.name.lower()

    if suffix in {".zip", ".apk", ".ipa", ".jar", ".aab", ".aar"}:
        res = _run(["unzip", "-o", str(p), "-d", str(out)], timeout=120)
    elif suffix in {".gz"} and ".tar" in name:
        res = _run(["tar", "xzf", str(p), "-C", str(out)], timeout=120)
    elif suffix in {".bz2"} and ".tar" in name:
        res = _run(["tar", "xjf", str(p), "-C", str(out)], timeout=120)
    elif suffix == ".tar":
        res = _run(["tar", "xf", str(p), "-C", str(out)], timeout=120)
    elif suffix == ".gz":
        dest = out / p.stem
        res = _run(["gunzip", "-c", str(p)], timeout=60)
        if res.get("ok"):
            dest.write_bytes(res["stdout"].encode() if isinstance(res["stdout"], str) else res["stdout"])
    else:
        # Try unzip as fallback
        res = _run(["unzip", "-o", str(p), "-d", str(out)], timeout=120)

    # List extracted files
    files = []
    for item in sorted(out.rglob("*"))[:200]:
        if item.is_file():
            files.append({"path": str(item.relative_to(out)), "size": item.stat().st_size})

    return _j({
        "output_dir": str(out),
        "extraction_result": res if 'res' in locals() else {"note": "unknown format"},
        "extracted_files": files,
    })


@mcp.tool()
def scan_decompiled_source(source_dir: str, patterns: Optional[List[str]] = None) -> str:
    """
    Scan a directory of decompiled source code for security-relevant patterns:
    secrets, network endpoints, crypto usage, dangerous APIs, debug artifacts.
    source_dir: path to JADX/ILSpy output directory
    patterns: optional additional regex patterns to search for
    """
    ok, p, err = _exists(source_dir)
    if not ok:
        return err
    if not p.is_dir():
        return "Error: source_dir must be a directory"

    default_patterns = {
        "hardcoded_secrets": re.compile(
            r'(?:password|passwd|secret|apikey|api_key|token|bearer|credentials?|auth)'
            r'\s*[=:]\s*["\']([^"\']{6,})["\']', re.I),
        "urls": re.compile(r'["\'](https?://[^"\']{8,})["\']'),
        "ips": re.compile(r'["\']((?:\d{1,3}\.){3}\d{1,3}(?::\d+)?)["\']'),
        "aws_keys": re.compile(r'((?:AKIA|ASIA)[A-Z0-9]{16})'),
        "file_ops": re.compile(r'\b(?:new\s+File|open\(|fopen|writeFile|readFile|FileOutputStream)\b'),
        "network_calls": re.compile(r'\b(?:HttpURLConnection|OkHttp|fetch\(|axios|requests\.get|urllib|socket\.connect|URLConnection)\b'),
        "crypto_usage": re.compile(r'\b(?:AES|DES|RSA|Cipher\.getInstance|MessageDigest|KeyGenerator|SecretKeySpec|Cipher\.ENCRYPT)\b'),
        "reflection": re.compile(r'\b(?:Class\.forName|getDeclaredMethod|invoke\(|loadClass|ClassLoader)\b'),
        "exec_calls": re.compile(r'\b(?:Runtime\.exec|ProcessBuilder|subprocess|ShellExecute|CreateProcess|os\.system|eval\()\b'),
        "android_permissions": re.compile(r'<uses-permission[^>]+android:name=["\']([^"\']+)["\']'),
        "sql_queries": re.compile(r'(?:SELECT|INSERT|UPDATE|DELETE|DROP|CREATE)\s+.{0,100}', re.I),
    }

    if patterns:
        for i, pat in enumerate(patterns):
            try:
                default_patterns[f"custom_{i}"] = re.compile(pat, re.I)
            except re.error:
                pass

    findings: Dict[str, List[Dict]] = {k: [] for k in default_patterns}
    file_count = 0

    for src_file in p.rglob("*"):
        if not src_file.is_file():
            continue
        if src_file.stat().st_size > 2 * 1024 * 1024:
            continue
        suffix = src_file.suffix.lower()
        if suffix not in {".java", ".kt", ".cs", ".js", ".py", ".xml", ".json",
                          ".yaml", ".yml", ".conf", ".cfg", ".ini", ".properties",
                          ".smali", ".il", ".ts"}:
            continue
        try:
            text = src_file.read_text(errors="replace")
            file_count += 1
            rel = str(src_file.relative_to(p))
            for category, pattern in default_patterns.items():
                for m in pattern.finditer(text):
                    line_no = text[:m.start()].count("\n") + 1
                    snippet = text[max(0, m.start()-40):m.end()+40].strip()
                    findings[category].append({
                        "file": rel,
                        "line": line_no,
                        "match": m.group(0)[:200],
                        "context": snippet[:300],
                    })
        except Exception:
            continue

    # Deduplicate and cap
    summary = {}
    for cat, items in findings.items():
        seen_matches = set()
        deduped = []
        for item in items:
            key = (item["file"], item["match"][:50])
            if key not in seen_matches:
                seen_matches.add(key)
                deduped.append(item)
        summary[cat] = deduped[:50]

    return _j({
        "source_dir": str(p),
        "files_scanned": file_count,
        "findings": summary,
        "total_findings": sum(len(v) for v in summary.values()),
    })


@mcp.tool()
def install_tool(tool_name: str) -> str:
    """
    Auto-install a reverse engineering tool. Detects platform and runs the right command.
    Supported: radare2, jadx, ilspycmd, upx, strings, apktool, class-dump
    """
    system = platform.system()
    tool = tool_name.lower().strip()

    brew = _which("brew")
    apt = _which("apt-get") or _which("apt")

    install_map: Dict[str, Dict[str, Any]] = {
        "radare2": {
            "Darwin": [brew, "install", "radare2"] if brew else None,
            "Linux": [apt, "install", "-y", "radare2"] if apt else None,
        },
        "jadx": {
            "Darwin": [brew, "install", "jadx"] if brew else None,
            "Linux": None,  # handled specially below
        },
        "upx": {
            "Darwin": [brew, "install", "upx"] if brew else None,
            "Linux": [apt, "install", "-y", "upx-ucl"] if apt else None,
        },
        "apktool": {
            "Darwin": [brew, "install", "apktool"] if brew else None,
            "Linux": [apt, "install", "-y", "apktool"] if apt else None,
        },
        "class-dump": {
            "Darwin": [brew, "install", "class-dump"] if brew else None,
            "Linux": None,
        },
    }

    # ilspycmd needs dotnet
    if tool == "ilspycmd":
        dotnet = _which("dotnet")
        if not dotnet:
            return _j({"error": "dotnet SDK required first. Install from https://dotnet.microsoft.com/download"})
        res = _run(["dotnet", "tool", "install", "-g", "ilspycmd"], timeout=120)
        return _j({"tool": "ilspycmd", "result": res})

    cmds = install_map.get(tool, {})
    cmd = cmds.get(system)

    if cmd is None and tool == "jadx" and system == "Linux":
        # Download JADX release
        dl_script = [
            "bash", "-c",
            "LATEST=$(curl -s https://api.github.com/repos/skylot/jadx/releases/latest | "
            "grep tag_name | cut -d'\"' -f4) && "
            "curl -L https://github.com/skylot/jadx/releases/download/$LATEST/jadx-$LATEST.zip "
            "-o /tmp/jadx.zip && unzip -o /tmp/jadx.zip -d /opt/jadx && "
            "ln -sf /opt/jadx/bin/jadx /usr/local/bin/jadx && echo 'DONE'"
        ]
        res = _run(dl_script, timeout=300)
        return _j({"tool": "jadx", "result": res})

    if not cmd:
        return _j({"error": f"No auto-install available for {tool!r} on {system}. "
                            f"See references/tooling.md for manual instructions."})

    res = _run(cmd, timeout=300)
    return _j({"tool": tool, "system": system, "cmd": " ".join(cmd), "result": res})


@mcp.tool()
def generate_report(file_path: str) -> str:
    """
    One-shot full triage report: runs inspect_binary + extract_strings + get_binary_metadata
    and returns everything combined. Use this for a quick first-pass before deeper analysis.
    """
    ok, p, err = _exists(file_path)
    if not ok:
        return err

    report = {
        "target": str(p),
        "inspection": json.loads(inspect_binary(file_path)),
        "metadata": None,
        "strings_intel": None,
    }

    try:
        report["metadata"] = json.loads(get_binary_metadata(file_path))
    except Exception as e:
        report["metadata"] = {"error": str(e)}

    try:
        strings_raw = extract_strings(file_path, min_length=5, classify=True)
        strings_data = json.loads(strings_raw)
        # Keep top strings and all classified intel
        report["strings_intel"] = {
            "total": strings_data.get("total_unique_strings", 0),
            "sample": strings_data.get("strings", [])[:100],
            "intelligence": strings_data.get("intelligence", {}),
        }
    except Exception as e:
        report["strings_intel"] = {"error": str(e)}

    return _j(report)


if __name__ == "__main__":
    mcp.run()


# ─────────────────────────────────────────────
# NEW TOOLS (v2 — merged from plurigrid/asi)
# ─────────────────────────────────────────────

@mcp.tool()
def search_functions(file_path: str, pattern: str) -> str:
    """
    Search functions by name pattern (regex). Use to find:
    - Dangerous APIs: "strcpy|sprintf|gets|memcpy"
    - Crypto routines: "crypt|encode|xor|decrypt|aes|rc4"
    - Network handlers: "recv|send|connect|http|request"
    - Persistence: "persist|startup|install|hook|service"
    - Input handlers: "parse|read|input|handle|process"
    - CTF targets: "win|flag|success|correct|give_shell"
    """
    ok, p, err = _exists(file_path)
    if not ok:
        return err

    r2 = _which("radare2") or _which("rizin")
    if r2:
        cmd = f"aaa; afl~{pattern}"
        res = _run([r2, "-q", "-e", "scr.color=0", "-c", cmd, str(p)], timeout=60)
        if res.get("ok") and res.get("stdout", "").strip():
            lines = res["stdout"].strip().splitlines()
            parsed = []
            for line in lines:
                parts = line.split()
                if len(parts) >= 3:
                    parsed.append({"address": parts[0], "size": parts[1], "name": " ".join(parts[2:])})
                else:
                    parsed.append({"raw": line})
            return _j({"pattern": pattern, "matches": parsed, "count": len(parsed)})

    # Fallback: search in extracted symbols/strings
    strings_raw = extract_strings(file_path, min_length=4, classify=False)
    try:
        data = json.loads(strings_raw)
        all_strings = data.get("strings", [])
    except Exception:
        all_strings = []

    try:
        rx = re.compile(pattern, re.I)
    except re.error:
        return f"Error: invalid regex pattern: {pattern!r}"

    matches = [s for s in all_strings if rx.search(s)]
    return _j({"pattern": pattern, "matches": matches[:100], "count": len(matches),
                "note": "Symbol search via strings (radare2 not available)"})


@mcp.tool()
def xref_analysis(file_path: str, address_or_symbol: str, direction: str = "both") -> str:
    """
    Cross-reference analysis: who calls/references a function or address.
    direction: "to" (callers), "from" (callees), "both"
    address_or_symbol: hex address like "0x401234" or symbol name like "strcpy"
    """
    ok, p, err = _exists(file_path)
    if not ok:
        return err

    r2 = _which("radare2") or _which("rizin")
    if not r2:
        return _j({"error": "radare2 required for xref analysis. Install: brew install radare2"})

    results: Dict[str, Any] = {"target": address_or_symbol, "direction": direction}

    # Resolve symbol to address if needed
    if not address_or_symbol.startswith("0x"):
        resolve_cmd = f"aaa; f~{address_or_symbol}"
        res = _run([r2, "-q", "-e", "scr.color=0", "-c", resolve_cmd, str(p)], timeout=30)
        if res.get("ok") and res.get("stdout", "").strip():
            for line in res["stdout"].strip().splitlines():
                parts = line.split()
                if len(parts) >= 3 and address_or_symbol in parts[2]:
                    address_or_symbol = parts[0]
                    results["resolved_address"] = address_or_symbol
                    break

    if direction in ("to", "both"):
        cmd = f"aaa; axt {address_or_symbol}"
        res = _run([r2, "-q", "-e", "scr.color=0", "-c", cmd, str(p)], timeout=45)
        results["xrefs_to"] = res.get("stdout", "").strip().splitlines()

    if direction in ("from", "both"):
        cmd = f"aaa; axf {address_or_symbol}"
        res = _run([r2, "-q", "-e", "scr.color=0", "-c", cmd, str(p)], timeout=45)
        results["xrefs_from"] = res.get("stdout", "").strip().splitlines()

    return _j(results)


@mcp.tool()
def find_vulnerabilities(file_path: str) -> str:
    """
    Automated vulnerability pattern scanner:
    - Dangerous function usage (strcpy, sprintf, gets, system, memcpy without bounds)
    - Integer overflow patterns
    - Format string risks
    - Buffer handling issues
    - Protection flag check (PIE, canary, NX, RELRO)
    Returns findings with addresses and risk ratings.
    """
    ok, p, err = _exists(file_path)
    if not ok:
        return err

    findings: List[Dict] = []

    # Check binary protections
    kind = _file_kind(p)
    prot: Dict[str, Any] = {}

    if kind.get("format") == "ELF":
        re_tool = _which("readelf")
        if re_tool:
            res = _run([re_tool, "-d", str(p)], timeout=15)
            if res.get("ok"):
                out = res.get("stdout", "")
                prot["has_relro"] = "BIND_NOW" in out or "GNU_RELRO" in out
                prot["has_now"] = "BIND_NOW" in out

            res2 = _run([re_tool, "-l", str(p)], timeout=15)
            if res2.get("ok"):
                out2 = res2.get("stdout", "")
                prot["has_nx"] = "GNU_STACK" in out2 and "RWE" not in out2

    # Check security-relevant imports/symbols
    strings_raw = extract_strings(file_path, classify=False)
    try:
        all_strings = json.loads(strings_raw).get("strings", [])
    except Exception:
        all_strings = []

    dangerous_fns = {
        "strcpy":  ("🔴", "Unbounded string copy — classic stack overflow vector"),
        "strcat":  ("🔴", "Unbounded string concat — stack overflow"),
        "sprintf": ("🟠", "Unbounded format output — potential stack overflow"),
        "vsprintf":("🟠", "Unbounded format output — potential stack overflow"),
        "gets":    ("🔴", "Unbounded stdin read — always vulnerable"),
        "scanf":   ("🟡", "Unbounded input if %s used without width limiter"),
        "system":  ("🟠", "Shell execution — command injection if input reaches here"),
        "popen":   ("🟠", "Shell execution via pipe — command injection risk"),
        "printf":  ("🟡", "Format string vuln if user-controlled first arg"),
        "fprintf": ("🟡", "Format string vuln if user-controlled format arg"),
        "memcpy":  ("🔵", "Safe if size parameter is validated — check callers"),
        "memmove": ("🔵", "Safe if size parameter is validated — check callers"),
        "strncpy": ("🔵", "Safer than strcpy but check null-termination"),
        "malloc":  ("🔵", "Heap alloc — check for integer overflow in size"),
        "alloca":  ("🟡", "Stack alloc of dynamic size — stack overflow if large"),
        "realpath": ("🔵", "Path traversal if user input — check bounds"),
    }

    for fn, (risk, note) in dangerous_fns.items():
        # Check if function is imported
        if any(fn in s for s in all_strings):
            findings.append({
                "type": "dangerous_import",
                "function": fn,
                "risk": risk,
                "description": note,
                "recommendation": f"Use xref_analysis to find all call sites of {fn!r} and verify bounds checking",
            })

    # Radare2 deep scan
    r2 = _which("radare2") or _which("rizin")
    if r2:
        # Get protections
        info_res = _run([r2, "-q", "-e", "scr.color=0", "-c", "aaa; iI", str(p)], timeout=45)
        if info_res.get("ok"):
            info_out = info_res.get("stdout", "")
            prot["canary"] = "canary   true" in info_out.lower()
            prot["pie"] = "pic      true" in info_out.lower() or "pie      true" in info_out.lower()
            prot["nx"] = "nx       true" in info_out.lower()

        if not prot.get("pie"):
            findings.append({
                "type": "missing_protection",
                "protection": "PIE",
                "risk": "🟡",
                "description": "Binary not compiled with Position Independent Executable — fixed addresses aid exploitation",
            })
        if not prot.get("canary"):
            findings.append({
                "type": "missing_protection",
                "protection": "Stack Canary",
                "risk": "🟡",
                "description": "No stack canary — stack overflows may go undetected",
            })
        if not prot.get("nx"):
            findings.append({
                "type": "missing_protection",
                "protection": "NX/DEP",
                "risk": "🟠",
                "description": "Stack/heap may be executable — shellcode injection possible",
            })

    return _j({
        "target": str(p),
        "protection_flags": prot,
        "findings": findings,
        "total": len(findings),
        "note": "Static scan only. Use xref_analysis to trace dangerous function callers.",
    })


@mcp.tool()
def binary_diff(file_path_a: str, file_path_b: str, mode: str = "functions") -> str:
    """
    Compare two binaries to find differences (patch analysis, version comparison).
    mode: "functions" (compare function lists), "bytes" (raw diff), "hashes" (quick change detect)
    Useful for: finding what a patch changed, comparing malware variants, firmware diffing.
    """
    ok1, p1, err1 = _exists(file_path_a)
    if not ok1:
        return err1
    ok2, p2, err2 = _exists(file_path_b)
    if not ok2:
        return err2

    result: Dict[str, Any] = {
        "file_a": str(p1),
        "file_b": str(p2),
        "mode": mode,
    }

    # Hash comparison first
    h1, h2 = _sha256(p1), _sha256(p2)
    result["sha256_a"] = h1
    result["sha256_b"] = h2
    result["identical"] = h1 == h2

    if h1 == h2:
        return _j(result | {"conclusion": "Files are identical."})

    result["size_diff_bytes"] = p2.stat().st_size - p1.stat().st_size
    result["entropy_a"] = _entropy(p1)
    result["entropy_b"] = _entropy(p2)

    if mode == "bytes":
        # Block-level diff
        with p1.open("rb") as fa, p2.open("rb") as fb:
            data_a = fa.read()
            data_b = fb.read()
        diffs = []
        for i in range(min(len(data_a), len(data_b))):
            if data_a[i] != data_b[i]:
                diffs.append({"offset": hex(i), "a": hex(data_a[i]), "b": hex(data_b[i])})
            if len(diffs) >= 500:
                diffs.append({"note": "truncated at 500 diffs"})
                break
        result["byte_differences"] = diffs
        result["total_diff_bytes"] = len(diffs)

    elif mode == "functions":
        r2 = _which("radare2") or _which("rizin")
        if not r2:
            result["note"] = "radare2 required for function diff. Install: brew install radare2"
        else:
            def get_fns(path: Path) -> set:
                res = _run([r2, "-q", "-e", "scr.color=0", "-c", "aaa; afl", str(path)], timeout=60)
                fns = set()
                if res.get("ok"):
                    for line in res.get("stdout", "").splitlines():
                        parts = line.split()
                        if len(parts) >= 3:
                            fns.add(parts[2])  # function name
                return fns

            fns_a = get_fns(p1)
            fns_b = get_fns(p2)
            result["functions_only_in_a"] = sorted(fns_a - fns_b)
            result["functions_only_in_b"] = sorted(fns_b - fns_a)
            result["functions_in_both"] = len(fns_a & fns_b)
            result["total_a"] = len(fns_a)
            result["total_b"] = len(fns_b)

    return _j(result)


@mcp.tool()
def check_protections(file_path: str) -> str:
    """
    Check binary protection flags: PIE, NX/DEP, stack canary, RELRO, ASLR, code signing.
    Equivalent to running checksec. Essential first step for CTF and vuln research.
    """
    ok, p, err = _exists(file_path)
    if not ok:
        return err

    kind = _file_kind(p)
    prot: Dict[str, Any] = {
        "file": str(p),
        "format": kind.get("format"),
        "arch": kind.get("arch"),
        "bits": kind.get("bits"),
    }

    # Try checksec binary first
    checksec = _which("checksec")
    if checksec:
        res = _run([checksec, "--file", str(p), "--output", "json"], timeout=15)
        if res.get("ok") and res.get("stdout", "").strip().startswith("{"):
            return res["stdout"]

    r2 = _which("radare2") or _which("rizin")
    if r2:
        res = _run([r2, "-q", "-e", "scr.color=0", "-c", "iI", str(p)], timeout=30)
        if res.get("ok"):
            out = res.get("stdout", "").lower()
            prot["pie"] = "pic      true" in out or "pie      true" in out
            prot["canary"] = "canary   true" in out
            prot["nx"] = "nx       true" in out
            prot["stripped"] = "stripped true" in out
            prot["raw_iI"] = res.get("stdout", "")

    if kind.get("format") == "ELF":
        re_tool = _which("readelf")
        if re_tool:
            res = _run([re_tool, "-d", str(p)], timeout=15)
            if res.get("ok"):
                out = res.get("stdout", "")
                prot["relro"] = ("BIND_NOW" in out and "GNU_RELRO" in out) and "full" or \
                                ("GNU_RELRO" in out) and "partial" or "none"

    if kind.get("format") == "Mach-O":
        cs = _which("codesign")
        if cs:
            res = _run([cs, "-dv", str(p)], timeout=10)
            prot["code_signed"] = res.get("returncode") == 0
            prot["codesign_info"] = res.get("stderr", "")

    # Risk summary
    risks = []
    if not prot.get("pie"):
        risks.append("🟡 No PIE — fixed base addresses")
    if not prot.get("canary"):
        risks.append("🟡 No stack canary — buffer overflows undetected")
    if not prot.get("nx"):
        risks.append("🟠 No NX — executable stack/heap")
    if prot.get("relro") == "none":
        risks.append("🔵 No RELRO — GOT overwrite possible")
    if prot.get("stripped"):
        risks.append("⚪ Stripped — symbols removed (harder to analyze)")

    prot["risk_summary"] = risks if risks else ["✅ Standard protections appear enabled"]
    return _j(prot)


@mcp.tool()
def analyze_firmware(file_path: str, output_dir: str = "") -> str:
    """
    Firmware-specific analysis: detect format, extract filesystem, find credentials and
    vulnerable binaries. Uses binwalk for extraction when available.
    """
    ok, p, err = _exists(file_path)
    if not ok:
        return err

    if not output_dir:
        output_dir = str(p.parent / f"{p.stem}_firmware")
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    result: Dict[str, Any] = {
        "target": str(p),
        "output_dir": str(out),
        "steps": [],
    }

    # Known firmware magic signatures
    m = _magic(p)
    known_formats = {
        b"hsqs": "SquashFS little-endian",
        b"sqsh": "SquashFS big-endian",
        b"JFFS": "JFFS2 filesystem",
        b"\x1f\x8b": "GZIP compressed",
        b"BZh": "BZIP2 compressed",
        b"\xfd7zXZ": "XZ compressed",
        b"UBI#": "UBIFS",
        bytes.fromhex("27051956"): "U-Boot image",
        b"TRX\x00": "TRX firmware (Broadcom)",
        b"CrAMfs": "CramFS",
    }

    detected_format = "unknown"
    for sig, name in known_formats.items():
        if m.startswith(sig) or sig in m[:16]:
            detected_format = name
            break

    result["detected_format"] = detected_format
    result["steps"].append(f"Detected: {detected_format}")

    # Try binwalk extraction
    binwalk = _which("binwalk")
    if binwalk:
        res = _run([binwalk, "-e", "-M", "-C", str(out), str(p)], timeout=300)
        result["steps"].append("binwalk extraction attempted")
        result["binwalk_result"] = res
    else:
        # Fallback: try common decompressors
        if m.startswith(b"\x1f\x8b"):
            res = _run(["gunzip", "-c", str(p)], timeout=60)
            if res.get("ok"):
                extracted = out / f"{p.stem}.extracted"
                extracted.write_bytes(res.get("stdout", "").encode())
        result["steps"].append("binwalk not available — install with: brew install binwalk")

    # If extraction succeeded, analyze the extracted directory
    extracted_dirs = [d for d in out.iterdir() if d.is_dir()] if out.exists() else []
    if extracted_dirs:
        for d in extracted_dirs[:2]:
            bundle_result = json.loads(analyze_bundle(str(d), max_depth=5))
            result[f"bundle_{d.name}"] = bundle_result

    # Search all files for credentials
    credential_hits: List[Dict] = []
    search_patterns = [
        re.compile(r'(?:password|passwd|secret|apikey)\s*[=:]\s*["\']?([^"\';\s]{4,})', re.I),
        re.compile(r'(?:admin|root|default)\s*[=:]\s*["\']?([^"\';\s]{4,})', re.I),
        re.compile(r'-----BEGIN (?:RSA|EC|OPENSSH) PRIVATE KEY-----'),
        re.compile(r'(?:AKIA|ASIA)[A-Z0-9]{16}'),
    ]

    for src_file in out.rglob("*"):
        if not src_file.is_file() or src_file.stat().st_size > 512 * 1024:
            continue
        try:
            text = src_file.read_text(errors="replace")
            for pat in search_patterns:
                for m_obj in pat.finditer(text):
                    credential_hits.append({
                        "file": str(src_file.relative_to(out)),
                        "match": m_obj.group(0)[:200],
                    })
                    if len(credential_hits) >= 50:
                        break
        except Exception:
            continue

    result["credential_hits"] = credential_hits
    result["total_credential_hits"] = len(credential_hits)
    result["steps"].append(f"Found {len(credential_hits)} potential credential hits")

    return _j(result)


@mcp.tool()
def run_angr_analysis(file_path: str, mode: str = "cfg", find_addr: str = "",
                      avoid_addr: str = "", input_length: int = 32) -> str:
    """
    Symbolic execution with angr for automated analysis:
    mode="cfg"    — build control flow graph, count basic blocks
    mode="find"   — explore to find_addr while avoiding avoid_addr (CTF solver)
    mode="vuln"   — find paths to dangerous functions (system, execve, etc.)
    find_addr, avoid_addr: hex addresses like "0x401234"
    input_length: symbolic input length for find mode (bytes)
    """
    ok, p, err = _exists(file_path)
    if not ok:
        return err

    script_lines: List[str] = [
        "import angr, sys, json",
        f"proj = angr.Project({str(p)!r}, auto_load_libs=False)",
        "result = {'target': " + repr(str(p)) + ", 'mode': " + repr(mode) + "}",
    ]

    if mode == "cfg":
        script_lines += [
            "cfg = proj.analyses.CFGFast()",
            "result['functions'] = [{"
            "   'addr': hex(f.addr),"
            "   'name': f.name,"
            "   'blocks': f.block_count"
            "} for f in cfg.kb.functions.values()][:100]",
            "result['total_functions'] = len(cfg.kb.functions)",
            "result['total_blocks'] = sum(f.block_count for f in cfg.kb.functions.values())",
        ]

    elif mode == "find" and find_addr:
        script_lines += [
            "import claripy",
            f"flag = claripy.BVS('input', 8 * {input_length})",
            "state = proj.factory.entry_state(stdin=claripy.Concat(flag, claripy.BVV(b'\\n')))",
            "simgr = proj.factory.simgr(state)",
            f"find_addr = {find_addr}",
            f"avoid_addr = {avoid_addr or 0}",
            "simgr.explore(find=find_addr, avoid=avoid_addr if avoid_addr else [])",
            "if simgr.found:",
            "    sol = simgr.found[0].solver.eval(flag, cast_to=bytes)",
            "    result['solution'] = sol.hex()",
            "    result['solution_ascii'] = sol.decode('ascii', errors='replace')",
            "    result['found'] = True",
            "else:",
            "    result['found'] = False",
            "    result['deadended'] = len(simgr.deadended)",
        ]

    elif mode == "vuln":
        script_lines += [
            "cfg = proj.analyses.CFGFast()",
            "dangerous = ['system', 'execve', 'execl', 'popen', 'gets', 'strcpy']",
            "vuln_funcs = [f for f in cfg.kb.functions.values() if f.name in dangerous]",
            "result['dangerous_functions_found'] = [{"
            "   'name': f.name, 'addr': hex(f.addr),"
            "   'callers': [hex(c.addr) for c in cfg.kb.functions.callgraph.predecessors(f.addr)]"
            "} for f in vuln_funcs]",
        ]

    script_lines += ["print(json.dumps(result, default=str))"]

    script = "\n".join(script_lines)
    script_path = Path(tempfile.mktemp(suffix=".py"))
    script_path.write_text(script)

    res = _run([sys.executable, str(script_path)], timeout=120)
    script_path.unlink(missing_ok=True)

    if res.get("ok") and res.get("stdout", "").strip():
        return res["stdout"].strip()
    return _j({"error": res.get("error") or res.get("stderr", ""),
               "note": "If angr not installed: pip install angr"})


