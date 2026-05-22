# Setup — Reverse Engineering Skill v2 for Claude Desktop

## What Changed in v2

- **Ghidra MCP integration** (GhidrAssistMCP — 31 tools: xrefs, struct recovery, annotations)
- **IDA Pro MCP** support (mrexodia/ida-pro-mcp, MxIris-Reverse-Engineering/ida-mcp-server)
- **Official radare2-mcp** (from radareorg) as dedicated backend
- **angr symbolic execution** (`run_angr_analysis` — OEP finding, CTF constraint solving)
- **7 new MCP tools**: `search_functions`, `xref_analysis`, `find_vulnerabilities`,
  `binary_diff`, `check_protections`, `analyze_firmware`, `run_angr_analysis`
- **5 new workflows**: Malware, Vulnerability Research, CTF, Firmware, Binary Diff
- **Firmware extraction** with binwalk + credential scanning
- **CTF workflow** with protection check + win-function hunting + ROP hints

---

## Step 1: Install Python Dependency

```bash
pip install fastmcp
# Optional but recommended
pip install angr
```

---

## Step 2: Register Built-in MCP Server

Add to Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "reverse-engineering": {
      "command": "uv",
      "args": ["run", "/ABSOLUTE/PATH/reverse-engineering-skill/scripts/re_mcp_server.py"]
    }
  }
}
```

---

## Step 3 (Optional): Connect Ghidra for Best Decompilation

1. Install Ghidra: `brew install ghidra`
2. Download GhidrAssistMCP from https://github.com/jtang613/GhidrAssistMCP/releases
3. Install extension: Ghidra → File → Install Extensions → Add Extension
4. Enable: Ghidra → File → Configure → Experimental → GhidrAssistMCP
5. Add to Claude Desktop config:

```json
{
  "mcpServers": {
    "ghidra": {
      "command": "npx",
      "args": ["-y", "@ghidra-assist/mcp-client"],
      "env": { "GHIDRA_MCP_URL": "http://localhost:8080" }
    },
    "reverse-engineering": { ... }
  }
}
```

---

## Step 4 (Optional): Connect radare2-mcp

```bash
pip install radare2-mcp
```

```json
{
  "mcpServers": {
    "radare2": { "command": "r2-mcp", "args": [] }
  }
}
```

---

## Step 5: Install RE Tools

```bash
# macOS — core tools
brew install radare2 jadx upx binwalk class-dump checksec

# r2ghidra (Ghidra decompiler inside r2 — no GUI needed)
r2pm -ci r2ghidra

# .NET decompilation
dotnet tool install -g ilspycmd

# Symbolic execution
pip install angr
```

---

## Step 6: Install Skill

```bash
mkdir -p ~/.claude/skills
cp -r reverse-engineering-skill ~/.claude/skills/
```

Restart Claude Desktop.

---

## All 18 MCP Tools

| Tool | Purpose |
|------|---------|
| `inspect_binary` | Format, arch, entropy, hashes, packer hints |
| `extract_strings` | ASCII + UTF-16LE with 13-category classification |
| `analyze_bundle` | Recursive app bundle / directory inventory |
| `get_binary_metadata` | Sections, imports, exports via otool/readelf/objdump |
| `run_r2` | radare2/rizin command runner (safe wrapper) |
| `decompile` | Source reconstruction: ILSpy/.NET, JADX/APK, r2/native |
| `read_plist` | macOS binary/XML plist decoder |
| `unpack_archive` | ZIP/APK/IPA/tar extraction |
| `scan_decompiled_source` | Scan JADX/ILSpy output for secrets and dangerous patterns |
| `install_tool` | Auto-install missing RE tools |
| `generate_report` | One-shot full triage combining all tools |
| `search_functions` | Search functions by regex pattern |
| `xref_analysis` | Cross-reference tracing (xrefs_to, xrefs_from) |
| `find_vulnerabilities` | Automated vuln pattern scanner + protection flags |
| `binary_diff` | Compare two binaries (function diff, byte diff) |
| `check_protections` | PIE, NX, canary, RELRO, ASLR, code signing |
| `analyze_firmware` | Firmware extraction, credential scan, filesystem triage |
| `run_angr_analysis` | Symbolic execution: CFG, CTF constraint solving, vuln paths |

---

## Usage Examples

- `"Reverse engineer /Downloads/malware.exe"`
- `"Decompile this .NET DLL and show me the source"`
- `"What does this APK do? /tmp/suspicious.apk"`
- `"Find buffer overflows in this binary"`
- `"Solve this CTF crackme: /ctf/crackme64"`
- `"Diff these two firmware versions"`
- `"Extract and analyze this router firmware.bin"`
- `"Find all callers of VirtualAlloc in this malware"`
