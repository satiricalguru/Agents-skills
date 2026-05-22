# Tooling Reference

Platform detection: run `uname -s` (Linux/Darwin) or check `platform.system()` in Python.

---

## radare2

Universal disassembler/debugger. The most important tool — install first.

**macOS:**
```bash
brew install radare2
```

**Linux (Debian/Ubuntu):**
```bash
sudo apt-get install -y radare2
```

**Linux (manual, latest):**
```bash
git clone https://github.com/radareorg/radare2 /tmp/radare2
cd /tmp/radare2 && sys/install.sh
```

**Windows (in PATH check):**
```
winget install radare2
# or download from https://github.com/radareorg/radare2/releases
```

**Verify:** `radare2 -v`

---

## jadx (Android/Java decompiler)

Required for APK decompilation. Produces readable Java source + Android resources.

**macOS:**
```bash
brew install jadx
```

**Linux:**
```bash
# Download latest release
JADX_VERSION=$(curl -s https://api.github.com/repos/skylot/jadx/releases/latest | grep tag_name | cut -d'"' -f4)
curl -L "https://github.com/skylot/jadx/releases/download/${JADX_VERSION}/jadx-${JADX_VERSION}.zip" -o /tmp/jadx.zip
unzip /tmp/jadx.zip -d /opt/jadx
ln -sf /opt/jadx/bin/jadx /usr/local/bin/jadx
```

**Requires:** Java 11+ (`java -version`). If missing:
```bash
# macOS
brew install openjdk@17
# Linux
sudo apt-get install -y openjdk-17-jre
```

**Verify:** `jadx --version`

---

## ilspycmd (.NET decompiler)

Required for .NET/C# assembly decompilation. Produces near-perfect C# source.

**All platforms (requires .NET SDK):**
```bash
dotnet tool install -g ilspycmd
```

**Install .NET SDK if missing:**

macOS:
```bash
brew install dotnet
```

Linux:
```bash
sudo apt-get install -y dotnet-sdk-8.0
```

**Verify:** `ilspycmd --version`

---

## monodis (Mono IL disassembler, fallback for .NET)

**macOS:**
```bash
brew install mono
```

**Linux:**
```bash
sudo apt-get install -y mono-complete
```

---

## strings

Usually pre-installed. Extract printable strings from binaries.

**macOS:** Pre-installed with Xcode Command Line Tools
```bash
xcode-select --install  # if missing
```

**Linux:**
```bash
sudo apt-get install -y binutils
```

---

## file

Magic-based file type detection. Usually pre-installed.

**Linux (if missing):**
```bash
sudo apt-get install -y file
```

---

## upx (unpacker for UPX-packed binaries)

**macOS:**
```bash
brew install upx
```

**Linux:**
```bash
sudo apt-get install -y upx-ucl
```

**Usage:** `upx -d packed_binary -o unpacked_binary`

---

## readelf / objdump / nm (ELF/PE inspection)

Usually included in `binutils`.

**Linux:**
```bash
sudo apt-get install -y binutils
```

**macOS:** Use `otool`, `lipo`, `nm` (included with Xcode CLI tools)

---

## otool / lipo / codesign (macOS-only Mach-O tools)

Pre-installed on macOS with Xcode Command Line Tools:
```bash
xcode-select --install
```

**codesign inspection:**
```bash
codesign -dv --verbose=4 /path/to/binary
codesign -d --entitlements - /path/to/binary
```

---

## apktool (alternative APK unpacker)

**macOS/Linux:**
```bash
brew install apktool        # macOS
sudo apt-get install apktool # Linux
```

**Usage:** `apktool d TARGET.apk -o /tmp/apktool_out`
Better than `unzip` for APKs — decodes resources and AndroidManifest properly.

---

## class-dump / class-dump-z (Objective-C header dumping)

For Objective-C Mach-O binaries — dumps class interfaces.

**macOS:**
```bash
brew install class-dump
```

**Usage:** `class-dump -H /path/to/binary -o /tmp/headers/`

---

## frida-tools (dynamic instrumentation, optional)

For tracing at runtime if static analysis is insufficient.

```bash
pip3 install frida-tools
```

**Note:** Dynamic analysis — only suggest to user, don't run automatically.

---

## Quick Platform Detection Script

```python
import platform, shutil

system = platform.system()  # 'Darwin', 'Linux', 'Windows'
arch = platform.machine()   # 'x86_64', 'arm64', 'AMD64'

tools = {name: shutil.which(name) for name in
         ['radare2', 'rizin', 'jadx', 'ilspycmd', 'monodis',
          'strings', 'file', 'upx', 'readelf', 'objdump',
          'nm', 'otool', 'lipo', 'class-dump', 'apktool']}

missing = [k for k, v in tools.items() if not v]
print(f"System: {system} {arch}")
print(f"Available: {[k for k, v in tools.items() if v]}")
print(f"Missing: {missing}")
```

---

## angr (Symbolic Execution)

```bash
pip3 install angr
# Verify
python3 -c "import angr; print(angr.__version__)"
```

---

## binwalk (Firmware extraction)

**macOS:**
```bash
brew install binwalk
```

**Linux:**
```bash
sudo apt-get install -y binwalk
```

**Usage:**
```bash
binwalk -e firmware.bin          # extract
binwalk -Me firmware.bin         # recursive extract
binwalk -A firmware.bin          # scan for CPU arch opcodes
```

---

## checksec (Binary protection flags)

```bash
pip3 install checksec
# or
sudo apt-get install checksec
```

**Usage:** `checksec --file=binary` → shows PIE, ASLR, canary, NX, RELRO status

---

## Ghidra (Free NSA decompiler)

**macOS/Linux:**
```bash
brew install ghidra         # macOS (Java required)
# or download from: https://ghidra-sre.org
```

**Requires Java 17+:**
```bash
brew install openjdk@17     # macOS
sudo apt-get install openjdk-17-jdk  # Linux
```

---

## r2ghidra (Ghidra decompiler inside radare2)

Adds `pdc` and `pdg` commands to radare2 — gives Ghidra-quality decompilation without opening the GUI.

```bash
r2pm -ci r2ghidra
```

**Usage in r2:** `aaa; s main; pdc`

---

## x64dbg / WinDbg (Windows dynamic analysis — user suggests, don't auto-run)

Only mention to users for dynamic analysis recommendations:
- x64dbg: https://x64dbg.com (free, best Windows debugger for RE)
- WinDbg: `winget install Microsoft.WinDbg`

---

## frida-tools (Dynamic instrumentation — suggest only, don't run on analyzed binary)

```bash
pip3 install frida-tools
```

Useful for tracing function calls at runtime when static analysis is blocked by heavy obfuscation.
