# RE Quick-Reference Cheatsheet

Fast lookup during analysis sessions — tool commands, patterns, and decision trees.

---

## Tool Command Reference

### radare2 (r2) — Core Commands

```bash
# Open
r2 binary                        # open for analysis
r2 -d binary                     # open for dynamic (debug mode)
r2 -A binary                     # open + auto-analyze (equiv to: r2; aaa)

# Analysis
aaa                              # full analysis (find all functions, xrefs, etc.)
aaaa                             # even deeper analysis (slower)
afl                              # list all functions
afl~<name>                       # filter functions by name
afl | grep -i crypt              # find crypto-related functions

# Inspection
iI                               # binary info (arch, bits, os, stripped, nx, canary, pic)
iS                               # sections list
ii                               # imports (linked symbols)
iE                               # exports
iz                               # strings in data section
izz                              # strings anywhere in binary

# Navigation + Disasm
s main                           # seek to main
pdf                              # disassemble current function
pdf @ main                       # disassemble main
pdf @ 0x401234                   # disassemble at address
pdc @ main                       # decompile to C (requires r2ghidra)
pdg @ main                       # decompile with Ghidra backend

# Cross-references
axt @ sym.strcpy                 # who calls strcpy
axf @ main                       # what main calls
axt @ 0x402010                   # xrefs TO an address
axf @ 0x401234                   # xrefs FROM a function

# Search
/ UPX                            # search string in binary
/b 90 90 90                      # search byte pattern (NOPs)
/ad jmp eax                      # search assembly instruction

# Struct recovery (via r2ghidra or rizin)
ta struct_name 0x401234          # apply struct type at address

# Patching
wa nop                           # write NOP at current address
wao nop                          # patch current instruction with NOP
```

### Ghidra — Scripting & Headless

```bash
# Headless analysis (no GUI)
analyzeHeadless /tmp/proj MyProject \
  -import /path/to/binary \
  -postScript PrintDecompilation.java \
  -deleteProject

# Useful built-in scripts (via Script Manager)
# FindReferences.java      — xrefs to a function
# DecompileFunction.java   — dump decompiled C
# ExportProgram.java       — export to various formats
```

### JADX — Android/Java

```bash
jadx app.apk -d output/               # decompile APK to Java source
jadx app.apk -d output/ --deobf       # with deobfuscation
jadx-gui app.apk                      # open in GUI (if available)

# After decompile, important files:
# output/sources/        → Java source
# output/resources/      → res/values/strings.xml, AndroidManifest.xml
```

### ILSpyCMD — .NET

```bash
ilspycmd assembly.dll                  # decompile to stdout
ilspycmd assembly.dll -p -o output/   # decompile to project directory
ilspycmd assembly.dll -t ClassName    # decompile specific class
```

### upx — Unpacker

```bash
upx -d packed.exe -o unpacked.exe     # decompress UPX-packed binary
upx -l binary                          # check if UPX packed (list mode)
upx --best -o packed.exe orig.exe     # pack a binary (for testing)
```

### binwalk — Firmware

```bash
binwalk firmware.bin                   # scan and identify embedded files
binwalk -e firmware.bin                # extract all found filesystems
binwalk -Me firmware.bin              # recursive extraction
binwalk -A firmware.bin               # scan for CPU opcodes (arch detection)
binwalk -E firmware.bin               # entropy graph
```

### checksec — Protections

```bash
checksec --file=binary                 # check all protections
checksec --file=binary --output=json  # JSON output for scripting
```

### strings

```bash
strings binary                         # ASCII strings (default min 4)
strings -n 8 binary                    # min 8 chars
strings -e l binary                    # UTF-16LE strings (Windows)
strings -e b binary                    # UTF-16BE strings
strings binary | grep -iE "http|api|key|pass|token"
```

### otool (macOS)

```bash
otool -L binary                        # linked libraries
otool -l binary                        # load commands (full header)
otool -h binary                        # mach-o header
otool -d binary                        # data section
codesign -dv --verbose=4 binary       # code signing info
codesign -d --entitlements - binary   # entitlements plist
```

### class-dump (macOS ObjC)

```bash
class-dump binary                      # dump ObjC class interfaces
class-dump -H binary -o headers/      # save headers to directory
```

---

## Pattern Recognition — What Imports Mean

### Windows (PE) Suspicious API Clusters

| Cluster | APIs | Meaning |
|---------|------|---------|
| **Process Injection** | `VirtualAllocEx` + `WriteProcessMemory` + `CreateRemoteThread` | Classic DLL/shellcode injection |
| **Hollow Process** | `CreateProcessA` (suspended) + `NtUnmapViewOfSection` + `VirtualAllocEx` | Process hollowing |
| **Reflective Loader** | `VirtualAlloc` + `VirtualProtect` + self-referencing PE parse | Reflective DLL injection |
| **Network C2** | `InternetOpenA/W` + `InternetConnectA` + `HttpSendRequestA` | WinInet-based C2 |
| **Socket C2** | `WSAStartup` + `socket` + `connect` + `send`/`recv` | Raw socket C2 |
| **Keylogger** | `SetWindowsHookExA` + `GetAsyncKeyState` | Keyboard hook |
| **Persistence** | `RegCreateKeyEx` + `RegSetValueEx` (Run key) | Registry persistence |
| **Download & Exec** | `URLDownloadToFileA` + `ShellExecuteA`/`CreateProcessA` | Dropper pattern |
| **Anti-Debug** | `IsDebuggerPresent` + `CheckRemoteDebuggerPresent` + `NtQueryInformationProcess` | Debugger evasion |
| **VM Detection** | strings: `VMware`, `VBox`, `QEMU`, `Sandbox`, `Wireshark` | Sandbox evasion |
| **Crypto** | `CryptAcquireContext` + `CryptEncrypt`/`CryptDecrypt` | WinCrypt encryption |

### Linux (ELF) Suspicious Patterns

| Pattern | Meaning |
|---------|---------|
| `ptrace(PTRACE_TRACEME)` | Anti-debug (fails if already traced) |
| `/proc/self/status` + `TracerPid` check | Debugger detection via procfs |
| `mprotect(PROT_EXEC)` on heap/stack | JIT or shellcode execution |
| `memfd_create` + `fexecve` | Fileless execution |
| `LD_PRELOAD` manipulation | Library hijacking |
| `dlopen` + `dlsym` | Dynamic loading (obfuscation or plugin) |

### Android (APK) Danger Signs

| Pattern | Risk |
|---------|------|
| `SEND_SMS` + `READ_CONTACTS` + `INTERNET` | SMS stealer |
| `READ_CALL_LOG` + `RECORD_AUDIO` | Spyware |
| `BIND_DEVICE_ADMIN` | Device admin — ransomware or lock |
| `DexClassLoader` in code | Dynamic code loading |
| `Runtime.exec()` in code | Shell command execution |
| `android.os.Build` checks | Emulator detection |
| Native lib + `System.loadLibrary` | Native code bypass |

---

## Entropy Reference

| Entropy | Interpretation |
|---------|---------------|
| 0.0 – 3.0 | Highly repetitive data (padding, zeroes) |
| 3.0 – 5.0 | Plain text, config, structured data |
| 5.0 – 6.5 | Normal compiled code |
| 6.5 – 7.2 | Elevated — compressed resources, encryption likely present in some sections |
| 7.2 – 7.9 | High — likely packed or encrypted binary |
| 7.9 – 8.0 | Near-maximum — strong encryption or random data |

---

## Decision Tree: What Tool for What Format?

```
Binary received
│
├─ .apk / .jar / .dex / .class  ──→  JADX (decompile to Java)
│
├─ .exe / .dll  (PE format)
│   ├─ .NET detected (CLR header)  ──→  ILSpyCMD (decompile to C#)
│   ├─ High entropy (>7.2)  ────────→  UPX unpack → then PE analysis
│   └─ Regular PE  ─────────────────→  Ghidra / IDA / radare2
│
├─ No extension / Mach-O
│   ├─ macOS .app bundle  ──────────→  analyze_bundle + otool + class-dump
│   ├─ iOS .ipa  ───────────────────→  unzip + Mach-O analysis + plist
│   └─ Raw Mach-O  ─────────────────→  otool + radare2 / Ghidra
│
├─ ELF (Linux/Android native)
│   ├─ .so shared lib  ─────────────→  readelf + nm + radare2
│   └─ Executable  ─────────────────→  checksec + radare2 / Ghidra
│
├─ Firmware blob
│   ├─ Known magic (SquashFS etc.)  →  binwalk -e + analyze extracted
│   └─ Unknown  ────────────────────→  binwalk -A (arch scan) + strings
│
└─ Unknown format
    └─ file + strings + inspect_binary  →  identify then route above
```

---

## CTF Quick Checklist

```
□ checksec — note PIE/canary/NX/RELRO
□ strings — find flag format hint (CTF{, FLAG{, picoCTF{)
□ ltrace/strace (dynamic) — see library calls at runtime
□ list_functions — find win/flag/success/correct/give_shell
□ decompile main — understand input flow
□ find comparison function — strcmp/memcmp/custom check
□ if strcmp: check both arguments in decompiler
□ if custom algorithm: try angr constraint solving
□ if overflow: find offset with pattern (cyclic/de bruijn)
□ if ROP needed: list segments for gadget hunt
```

---

## Common String Patterns → What They Indicate

| String found | Likely meaning |
|-------------|---------------|
| `C:\Users\dev\...\*.pdb` | Developer PDB path — reveals internal build paths |
| `AKIA[A-Z0-9]{16}` | AWS IAM Access Key — hardcoded credential |
| `ghp_[A-Za-z0-9]{36}` | GitHub Personal Access Token |
| `eyJ[base64]` | JWT token |
| `-----BEGIN RSA PRIVATE KEY-----` | Hardcoded private key |
| `http://[IP]/gate.php` | Classic C2 beacon URL |
| `cmd.exe /c` | Windows shell execution |
| `/bin/sh` or `/bin/bash` | Unix shell spawn |
| `SELECT * FROM users` | SQL query — check for injection |
| `VBoxGuestAdditions` | VM detection (VirtualBox) |
| `vmware` / `VMWARE` | VM detection (VMware) |
| `SbieDll.dll` | Sandboxie detection |
| `wireshark` (in lowercase) | Analyst tool detection |
| `UPX0` / `UPX1` | UPX packing signature |
| `This program cannot be run in DOS mode` | Normal PE stub (not suspicious) |
| `Themida` / `VMProtect` | Commercial protector — expect high entropy |
