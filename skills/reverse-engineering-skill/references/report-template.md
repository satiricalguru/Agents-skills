# Reverse Engineering Report Template

Use this exact structure. Fill every section — write "None found" if a section is empty.
Use emoji risk indicators: 🔴 Critical · 🟠 High · 🟡 Medium · 🔵 Low · ⚪ Informational

---

# 🔬 Reverse Engineering Report: `<filename>`

**Analyzed:** `<full path>`  
**Date:** `<today>`  
**Analyst:** Claude (Autonomous RE)

---

## ⚡ Executive Summary

> 2–4 sentences. What is this binary? What does it do? What are the most important findings?
> Non-technical language. If malware is suspected, say so here with ⚠️.

---

## 📋 File Identity

| Field | Value |
|-------|-------|
| File name | `<name>` |
| File size | `<size>` |
| SHA-256 | `<hash>` |
| MD5 | `<hash>` |
| Format | `<PE/ELF/Mach-O/APK/JAR/…>` |
| Architecture | `<x86/x86_64/arm64/…>` |
| Platform target | `<Windows/Linux/macOS/Android/…>` |
| Entropy | `<value>` (`<interpretation: normal/elevated/packed>`) |
| Compiler/Runtime hints | `<MSVC/GCC/Clang/.NET/Dalvik/…>` |
| Packed/Obfuscated | `<Yes/No/Suspected — reason>` |

---

## 🔍 Key Findings

List findings by severity. Each finding = one bullet. Format:

**🔴 [CRITICAL] Hardcoded AWS Access Key**  
Found string `AKIA...XXXX` at offset 0x1A4C in `.data` section. This is an AWS IAM key that
grants API access. Decompiled code in `Config.java:42` assigns it to `AwsClient`.

**🟠 [HIGH] C2 Communication**  
Binary connects to `http://185.220.x.x/gate.php` — a known Tor exit node IP. Import of
`URLDownloadToFile` + `ShellExecuteA` suggests download-and-execute behavior.

*(Continue for all findings, descending severity)*

---

## 🧩 Binary Structure

### Sections / Segments
*(Table of sections with name, size, entropy, permissions)*

| Section | Size | Entropy | Permissions | Notes |
|---------|------|---------|-------------|-------|
| `.text` | 0x1A000 | 6.1 | r-x | code |
| `.data` | 0x2000 | 4.3 | rw- | globals |
| … | | | | |

### Dependencies / Imports
*(Libraries the binary links against)*

- `<library>` — `<what it provides>`
- …

### Exports / Symbols
*(For libraries/plugins — what functions are exposed)*

---

## 📡 Network Indicators

| Indicator | Type | Context | Risk |
|-----------|------|---------|------|
| `https://api.example.com/v2/report` | URL | Found in strings, called in `sendData()` | 🟡 |
| `185.220.101.x` | IP | Hardcoded C2 candidate | 🔴 |
| `8443` | Port | Non-standard HTTPS | 🔵 |

---

## 🔑 Secrets & Credentials

| Secret | Value (redacted) | Location | Risk |
|--------|-----------------|---------|------|
| AWS Key | `AKIA...XXXX` | `.data` offset 0x1A4C | 🔴 |
| JWT secret | `"mysecretkey123"` | `Config.class:18` | 🔴 |

*(If none: "No hardcoded secrets found.")*

---

## 🧠 Behavioral Analysis (Static)

Based on imports, strings, and decompiled code, this binary likely:

1. **Starts up** → does X (evidence: imports/strings)
2. **Checks environment** → VM detection / anti-debug (evidence: string `"VBoxGuestAdditions"`)
3. **Communicates** → sends beacon to C2 (evidence: import `InternetOpenA`, URL found)
4. **Persists** → writes to `HKCU\Software\Microsoft\Windows\CurrentVersion\Run` (evidence: registry key string)

*(Use numbered steps to describe the execution flow. Be specific. Cite evidence.)*

---

## 💻 Decompiled Code Highlights

*(Only if decompilation succeeded — paste most relevant reconstructed functions)*

### `<ClassName>.<methodName>()` (`<file>:<line>`)
```java
// JADX-decompiled — approximate reconstruction
public void sendBeacon(String c2url) {
    String data = collectSystemInfo();
    HttpClient.post(c2url + "/gate.php", data);
}
```
**What this does:** Collects system information and POSTs it to the C2 endpoint.

*(Repeat for 3–5 most important functions)*

---

## 🛡️ Anti-Analysis Techniques

| Technique | Evidence | Bypass |
|-----------|---------|--------|
| Debugger detection | `IsDebuggerPresent` import | Patch NOP or use ScyllaHide |
| VM detection | String `"VMware"` / `"VBox"` | Use bare metal or patch check |
| High entropy sections | `.packed` section entropy 7.8 | Run UPX -d or use dynamic unpacking |

*(If none: "No anti-analysis techniques detected.")*

---

## 📦 Android-Specific (APK only)

### Permissions Requested
*(From AndroidManifest.xml)*

| Permission | Risk | Purpose |
|-----------|------|---------|
| `READ_CONTACTS` | 🟠 | Reads device contacts |
| `INTERNET` | 🔵 | Network access |

### Components
- **Activities:** `<list>`
- **Services:** `<list>`
- **Receivers:** `<list>`
- **Providers:** `<list>`

### Native Libraries
*(`.so` files bundled in APK)*

---

## 🗺️ MITRE ATT&CK Mapping (if applicable)

| Technique ID | Name | Evidence |
|-------------|------|---------|
| T1055 | Process Injection | VirtualAlloc + WriteProcessMemory imports |
| T1082 | System Information Discovery | `GetComputerNameA` / `uname` calls |

*(Skip if the binary is benign software — only include if suspicious behavior found)*

---

## 📝 Recommendations

1. **<Specific action>** — reason
2. **<Specific action>** — reason
3. …

---

## 🔧 Analysis Artifacts

| Artifact | Location |
|---------|---------|
| Decompiled source | `/tmp/re_output/` |
| Extracted strings | *(included inline above)* |
| Unpacked binary | `/tmp/unpacked` *(if applicable)* |

---

*Report generated by Claude Autonomous RE Skill. Static analysis only — no binary was executed.*

---

## 🏴 CTF-Specific Section (CTF binaries only)

### Binary Protections (checksec)
| Protection | Status | Impact |
|-----------|--------|--------|
| PIE | ✅ Enabled / ❌ Disabled | Fixed base = easier ROP |
| Stack Canary | ✅ / ❌ | No canary = overflow unchecked |
| NX/DEP | ✅ / ❌ | Executable stack = shellcode possible |
| RELRO | Full / Partial / None | GOT overwrite possible if none |
| ASLR | System-level | Assume enabled on modern OS |

### Challenge Mechanic
*(Explain what the binary does, what input it takes, what constitutes "winning")*

### Vulnerability / Solution Path
```
1. <What the bug is>
2. <How to trigger it>
3. <What it gives you>
```

### Key Addresses
| Symbol | Address | Notes |
|--------|---------|-------|
| `main` | `0x401234` | Entry point |
| `win` / `flag` | `0x401500` | Target function |
| `dangerous_call` | `0x401340` | Overflow site |

### Exploit Approach
*(Describe the exploitation strategy: ret2win, ROP chain, format string, angr solve, etc.)*

---

## 🔩 Firmware-Specific Section (firmware only)

### Firmware Identity
| Field | Value |
|-------|-------|
| Format | SquashFS / JFFS2 / TRX / U-Boot / … |
| Compression | gzip / lzma / xz / none |
| Architecture | MIPS / ARM / x86 / … |
| Extracted size | … |
| Extraction tool | binwalk / unzip / manual |

### Filesystem Contents
*(High-level summary: what directories, which binaries, what web server)*

### Hardcoded Credentials Found
| File | Credential | Risk |
|------|-----------|------|
| `/etc/passwd` | `root:admin123` | 🔴 |
| `/usr/bin/httpd` string | `"password=default"` | 🔴 |

### Vulnerable Components
*(List outdated software versions, known CVEs, unsafe config)*

### Network Attack Surface
*(Web interfaces, telnet daemons, UART ports, JTAG)*

---

## 🔀 Binary Diff Section (patch/diff analysis only)

### Change Summary
| Metric | Value |
|--------|-------|
| Functions added | N |
| Functions removed | N |
| Total changed bytes | N |
| Entropy change | ±N |

### Functions Added in B
*(List new functions — may indicate added features or patched code)*

### Functions Removed in A→B
*(List deleted functions — may indicate removed backdoors or deprecated code)*

### Patch Analysis
*(What does the diff suggest? Security fix? Feature addition? Suspicious change?)*

---

*Report generated by Claude Autonomous RE Skill v2 · Ghidra/IDA/radare2/angr backends · Static analysis only*
