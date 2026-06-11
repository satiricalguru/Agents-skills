---
name: reverse-engineering-skill
description: >
  Autonomous reverse engineering of compiled apps, binaries, APKs, firmware, and
  installers on macOS and Windows. Use when the user wants to analyze, decompile,
  inspect, or understand a binary — including PE/ELF/Mach-O executables, Android APKs,
  .NET assemblies, Java JARs, firmware blobs, and app bundles. Triggers on: "reverse
  engineer", "decompile", "disassemble", "analyze binary", "what does this app do",
  "inspect exe/dll/dylib/apk/so", "extract strings", "find secrets in binary",
  "static analysis", "check for malware", "CTF challenge", "buffer overflow",
  "find vulnerabilities", "xref analysis", "recover symbols", "firmware extraction",
  "binary diff", "ROP gadgets", "angr", "symbolic execution", "Ghidra", "IDA Pro",
  "radare2". Also trigger when the user drops any binary file and asks what it is.
  Runs fully autonomously — orchestrates Ghidra/IDA/radare2 MCP servers or built-in
  FastMCP server, installs missing tools, and produces a structured intelligence report.
---

# Reverse Engineering Skill

You are an expert reverse engineer. When this skill triggers, your goal is **full autonomous
analysis** — run the tools, interpret output, and produce actionable intelligence. Don't ask the
user to do manual steps.

Read `reverse-engineering-skill/references/tooling.md` for installation commands before installing anything.  
Read `reverse-engineering-skill/references/report-template.md` for the final report structure.  
Read `reverse-engineering-skill/references/mcp-backends.md` for Ghidra/IDA/radare2-mcp server setup and tool APIs.  
Read `reverse-engineering-skill/references/cheatsheet.md` during analysis for fast command lookup, import pattern recognition, and decision trees.

---

## Tool Priority: Which Backend to Use

Check what's available in this order — use the first one that's connected:

1. **GhidraMCP / GhidrAssistMCP** (best decompilation quality — 31 tools, free)  
   → If Ghidra is running with MCP enabled, use `list_functions`, `decompile_function`, `xrefs_to`, etc.
2. **IDA Pro MCP** (commercial, highest quality for stripped binaries)  
   → If IDA is running with mcp-server, use the same function/xref API calls
3. **radare2-mcp** (official, `r2-mcp` binary — CLI-native, great for automation)  
   → Translates r2 commands into MCP tool calls
4. **Built-in FastMCP server** (`re_mcp_server.py` — always available, no external tools needed)  
   → Falls back to this if none of the above are running

When using Ghidra/IDA/radare2-mcp, always start with `get_program_info` before anything else.

---

## Phase 0: Resolve & Orient

1. If user gave a file path, confirm it exists. If a URL, `curl -L -o /tmp/target <url>`.
2. If the target is an archive (`.zip`, `.tar`, `.gz`, `.ipa`, `.aab`), extract it first.
3. Detect format using `inspect_binary` (built-in) or `get_program_info` (Ghidra/IDA/r2-mcp).
4. **Determine the analysis goal** — pick the right workflow below:
   - Malware triage → Malware Analysis workflow
   - CVE/vuln hunting → Vulnerability Research workflow  
   - CTF challenge → CTF workflow
   - General understanding → Standard Triage workflow
   - Firmware → Firmware workflow

---

## Phase 1: Triage (All Workflows)

**With Ghidra/IDA/radare2-mcp:**
```
get_program_info    → arch, compiler, OS target, entry point, protection flags (PIE, ASLR, canary)
list_functions      → full function list with addresses and sizes
list_imports        → imported APIs — primary behavioral signal
list_exports        → exported symbols (for DLLs/dylibs)
list_strings        → strings in data sections (URLs, keys, paths)
list_segments       → memory layout (useful for ROP, firmware)
```

**With built-in server:**
```
inspect_binary(path)                    → format, arch, entropy, hashes, packer hints
extract_strings(path, classify=True)    → strings + auto-classified intelligence buckets
get_binary_metadata(path)               → sections, imports, symbols via native tools
```

**After triage, decide:**
- Entropy > 7.2 + low string count → **packed binary** (see Phase 2f)
- Imports include `VirtualAlloc`+`WriteProcessMemory`+`CreateRemoteThread` → **injector/RAT**
- `.NET` CLR header found → use ILSpyCMD for near-perfect C# decompilation
- APK/JAR/DEX → use JADX
- Mach-O `.app` bundle → also scan `Info.plist` and embedded frameworks

---

## Phase 2: Workflow-Specific Analysis

### 2A: Standard Triage (Unknown Binary)

1. `list_functions` → note entry point, unusual names, suspiciously named stubs
2. `decompile_function` on `main` / `DllMain` / `_start` → understand top-level logic
3. `list_imports` → what does it use? (network, crypto, process, registry, file I/O)
4. `list_strings` → harvest URLs, IPs, paths, version strings, error messages
5. `xrefs_to` on suspicious imports → who calls `VirtualAlloc`? Who calls `InternetOpen`?
6. `decompile_function` on top callers of suspicious imports
7. `auto_create_struct` on data buffers if structure recovery is needed

### 2B: Malware Analysis

Primary goal: identify capabilities, C2, persistence, evasion.

```
1. get_program_info     → entry point, compiler (MSVC malware vs MinGW is a useful signal)
2. list_imports         → look for: VirtualAlloc, WriteProcessMemory, CreateRemoteThread,
                          URLDownloadToFile, InternetOpen, RegSetValue, ShellExecute,
                          IsDebuggerPresent, GetTickCount (timing evasion), CreateMutex
3. list_strings         → C2 URLs/IPs, registry keys, mutex names, scheduled task names,
                          base64 blobs, crypto constants, debug PDB paths
4. search_functions "crypt|encode|xor|decrypt|obfusc"  → find obfuscation routines
5. decompile_function   → decompile each suspicious routine
6. xrefs_to on C2 URL strings → trace who builds/uses the URL
7. search_functions "persist|install|startup|hook"  → persistence mechanisms
8. auto_create_struct   → recover C2 beacon struct or config struct if present
9. set_disassembly_comment  → annotate findings in the project for the report
```

**Indicators to document:** mutex names, registry keys, C2 endpoints, encryption algorithm,
persistence mechanism, process injection technique, anti-analysis tricks.

### 2C: Vulnerability Research

Primary goal: find memory safety issues, insecure API use, logic flaws.

```
1. list_functions       → sort by size; very large functions are complex = more attack surface
2. search_functions "parse|read|recv|copy|input|handle|process|decode"  → input handlers
3. decompile_function   → inspect each handler for:
   - Unbounded copies: strcpy, sprintf, gets, memcpy without size check
   - Integer issues: size_t truncation, signed/unsigned comparison
   - Use-after-free: freed pointer reuse
   - Format string: printf(user_input) pattern
4. xrefs_to dangerous functions (strcpy, sprintf, gets, memcpy, recv)  → find all call sites
5. xrefs_from input parsing functions → trace data flow forward to sinks
6. list_segments        → check for non-PIE, no-RELRO, executable stack
7. search_functions "alloc|malloc|free|delete"  → heap operations for UAF/double-free
8. set_decompiler_comment / rename_function  → annotate findings
```

**Report each finding:** function name + address, vulnerable pattern, call chain, exploitability.

### 2D: CTF Binary

Primary goal: understand the challenge mechanics and find the flag/solution.

```
1. get_program_info     → PIE? canary? RELRO? NX? (checksec equivalent)
2. list_functions       → look for: win, flag, success, correct, print_flag, give_shell
3. list_strings         → flag format hints (CTF{, FLAG{, picoCTF{), error messages
4. decompile_function "main"  → understand input flow and comparison logic
5. xrefs_from main      → trace control flow to win conditions
6. search_functions "strcmp|memcmp|check|verify|validate"  → find comparison functions
7. decompile_function on comparison  → find expected value or algorithm
8. list_segments        → for ROP: .text base, gadget hunting
9. xrefs_to puts/system/execve  → possible win function locations
10. rename_function / rename_variable  → clean up decompiler output for clarity
```

**Deliverable:** explain the vulnerability/challenge mechanic + the solution or key insight.

### 2E: Firmware Analysis

Primary goal: extract code, identify hardware I/O, find hardcoded credentials.

```
1. inspect_binary       → check for known firmware magic (SquashFS, JFFS2, U-Boot, TRX)
2. If archive: unpack_archive → extract filesystem
3. analyze_bundle       → inventory all binaries in extracted firmware
4. For each interesting binary: run standard triage (2A)
5. list_strings in all binaries  → hardcoded passwords, SSH keys, telnet backdoors
6. search_functions "uart|gpio|i2c|spi|mmio|ioctl"  → hardware I/O routines
7. list_imports in httpd/web binaries  → often where vulns live
8. decompile_function on CGI handlers  → command injection patterns
9. auto_create_struct on protocol parsers  → recover packet/frame structs
```

### 2F: Packed / Obfuscated Binary

High entropy (>7.2) + sparse strings = packing/encryption. Do:

```
1. list_strings for packer names: UPX, MPRESS, Themida, VMProtect, Enigma, ConfuserEx
2. If UPX found: run `upx -d packed -o unpacked` then restart analysis on unpacked
3. decompile_function "entry0" / OEP stub  → understand unpacking loop
4. If custom packer: use angr symbolic execution to find OEP:
   import angr
   proj = angr.Project(binary, auto_load_libs=False)
   simgr = proj.factory.simgr()
   simgr.explore(find=lambda s: s.history.bbl_addrs[-1] != entry_addr)
5. Note: dynamic unpacking may be required — recommend sandbox (Any.run, Cuckoo) to user
```

---

## Phase 3: XREF-Driven Deep Dive

Always use cross-references to trace data flow — don't rely solely on decompiled output:

- `xrefs_to <address>` — who calls/references this address? (callers of a dangerous function)
- `xrefs_from <address>` — what does this function call? (callees, data dependencies)
- `function_xrefs <name>` — full call graph neighborhood of a function

**Pattern:** find a suspicious string → `xrefs_to` the string → get the function using it →
`decompile_function` that function → `xrefs_to` that function → find the full call chain.

---

## Phase 4: Annotation & Symbol Recovery

When doing deep analysis, annotate findings in the tool (Ghidra/IDA):

```
rename_function <addr> <descriptive_name>    → e.g., "beacon_send", "decrypt_config"
rename_variable <func> <var> <name>          → e.g., "c2_url", "encryption_key"
set_function_prototype <addr> <sig>          → improves decompiler output quality
set_local_variable_type <func> <var> <type>  → helps struct field recovery
set_disassembly_comment <addr> <comment>     → "VirtualAlloc for shellcode buffer"
auto_create_struct <addr> <size>             → recover data structure layout
```

---

## Phase 5: Decompilation (Source Reconstruction)

For full source reconstruction where possible:

- **.NET assemblies** → `decompile(path, tool_hint="ilspy")` → near-perfect C# via ILSpyCMD
- **Android APK** → `decompile(path, tool_hint="jadx")` → readable Java + resources
- **Objective-C Mach-O** : `class-dump` for interfaces + `decompile_function` for method bodies
- **Native (PE/ELF/Mach-O)** → `decompile_function` via Ghidra/IDA, or r2+r2ghidra
- After decompiling APK: run `scan_decompiled_source(jadx_output_dir)` → auto-finds secrets

---

## Phase 6: Final Report

Use the template in `references/report-template.md` exactly.

Key principles:
- **Lead with the most critical finding** — hardcoded creds, active C2, unpatched vuln
- **Be specific** — address, function name, decompiled snippet, not just "something suspicious"
- **Explain for non-RE readers** — what does `VirtualAlloc+WriteProcessMemory` actually mean?
- **MITRE ATT&CK map** findings where applicable (malware only)
- **Risk-rate every finding**: 🔴 Critical · 🟠 High · 🟡 Medium · 🔵 Low · ⚪ Info
- **Quote decompiled code** to prove findings (format: `function@addr: <snippet>`)

---

## Safety Rules

- Never execute the analyzed binary. Static analysis only.
- Decompiled output → `/tmp/re_output/` only, never to the user's project tree
- If live malware suspected: add ⚠️ MALWARE SUSPECTED banner at top of report, still analyze
- Report all findings even if embarrassing to the software author (hardcoded creds, etc.)
- For firmware: never write back to device — read only
