# MCP Backends Reference

This skill can orchestrate four different RE backends via MCP. Use the best available one.

---

## 1. GhidrAssistMCP (Recommended — Free)

**Repo:** https://github.com/jtang613/GhidrAssistMCP  
**Transport:** HTTP/SSE on `http://localhost:8080`  
**Quality:** Best free decompiler. 31 built-in tools.

### Installation
```bash
# 1. Install Ghidra (if not already)
brew install ghidra          # macOS
# or download from https://ghidra-sre.org

# 2. Download GhidrAssistMCP plugin
# Go to: https://github.com/jtang613/GhidrAssistMCP/releases
# Download the latest .zip extension

# 3. Install in Ghidra
# File → Install Extensions → Add Extension → select .zip → restart

# 4. Enable in Ghidra
# File → Configure → Experimental → check GhidrAssistMCP → restart
```

### Claude Desktop Config
```json
{
  "mcpServers": {
    "ghidra": {
      "command": "npx",
      "args": ["-y", "@ghidra-assist/mcp-client"],
      "env": { "GHIDRA_MCP_URL": "http://localhost:8080" }
    }
  }
}
```

### All 31 Tools

**Program Analysis:**
| Tool | Description |
|------|-------------|
| `get_program_info` | Architecture, OS, compiler, entry point, protection flags |
| `list_functions` | All functions with addresses and sizes |
| `list_data` | Global data and their types |
| `list_strings` | All strings in data sections |
| `list_imports` | Imported symbols and libraries |
| `list_exports` | Exported symbols (for DLLs/dylibs) |
| `list_segments` | Memory segments/sections |

**Function Analysis:**
| Tool | Description |
|------|-------------|
| `get_function_info` | Info about a specific function by name or address |
| `decompile_function` | High-level decompiled C from a function |
| `disassemble_function` | Raw assembly listing |
| `function_xrefs` | All xrefs to/from a function |
| `search_functions` | Search functions by name regex (e.g., `"crypt\|encode"`) |

**Navigation:**
| Tool | Description |
|------|-------------|
| `get_current_address` | Current cursor address in Ghidra |
| `get_current_function` | Function at current cursor |
| `xrefs_to` | All references TO an address |
| `xrefs_from` | All references FROM an address |

**Modification (annotations persist in project):**
| Tool | Description |
|------|-------------|
| `rename_function` | Give meaningful name to a function |
| `rename_variable` | Rename a local variable in decompiler view |
| `set_function_prototype` | Set parameter types for better decompilation |
| `set_local_variable_type` | Set type of a local variable |
| `set_disassembly_comment` | Add comment at an address |
| `set_decompiler_comment` | Add comment in decompiler view |

**Advanced:**
| Tool | Description |
|------|-------------|
| `auto_create_struct` | Recover data structure layout from usage |

### Alternative: LaurieWired/GhidraMCP
```bash
git clone https://github.com/LaurieWired/GhidraMCP
# Follow README — Python bridge to Ghidra HTTP server
```

---

## 2. IDA Pro MCP (Commercial — Best Quality)

Only available if user has an IDA Pro license. Three MCP server options:

### mrexodia/ida-pro-mcp (Most Active)
```bash
git clone https://github.com/mrexodia/ida-pro-mcp
cd ida-pro-mcp
pip install -e .
# Run from IDA Pro plugin menu after installing
```

### MxIris-Reverse-Engineering/ida-mcp-server (473 stars)
```bash
git clone https://github.com/MxIris-Reverse-Engineering/ida-mcp-server
pip install -e .
```

### Claude Desktop Config (IDA)
```json
{
  "mcpServers": {
    "ida-pro": {
      "command": "python",
      "args": ["-m", "ida_mcp_server"],
      "env": { "IDA_PORT": "9090" }
    }
  }
}
```

**IDA MCP tools mirror Ghidra's API:** `list_functions`, `decompile_function`,
`xrefs_to`, `xrefs_from`, `rename_function`, `list_imports`, `get_program_info`.

---

## 3. radare2-mcp (Official CLI Backend)

**Repo:** https://github.com/radareorg/radare2-mcp  
**Best for:** headless/automated workflows, no GUI needed.

### Installation
```bash
pip install radare2-mcp
# or
git clone https://github.com/radareorg/radare2-mcp
cd radare2-mcp && pip install -e .
```

### Claude Desktop Config
```json
{
  "mcpServers": {
    "radare2": {
      "command": "r2-mcp",
      "args": []
    }
  }
}
```

### Key radare2-mcp Tools
Maps r2 commands to MCP calls. Equivalent commands:

| MCP Tool | r2 Command | Description |
|----------|-----------|-------------|
| `analyze` | `aaa` | Full analysis |
| `list_functions` | `afl` | All functions |
| `disassemble` | `pdf @ <addr>` | Disassemble function |
| `decompile` | `pdc @ <addr>` | Decompile (r2ghidra) |
| `get_info` | `iI` | Binary info |
| `get_imports` | `ii` | Imports |
| `get_exports` | `iE` | Exports |
| `get_strings` | `iz` | Strings |
| `get_sections` | `iS` | Sections |
| `xrefs_to` | `axt @ <addr>` | Cross-refs to |
| `xrefs_from` | `axf @ <addr>` | Cross-refs from |
| `search` | `/` | Search bytes/strings |

### Ghidra Headless (No GUI)
For fully automated analysis without opening Ghidra GUI:
```bash
analyzeHeadless /tmp/ghidra_project ProjectName \
  -import /path/to/binary \
  -postScript DecompileAllFunctions.java \
  -deleteProject \
  -scriptPath /path/to/scripts
```

---

## 4. rand-tech/pcm (Multi-Tool Bridge)

**Repo:** https://github.com/rand-tech/pcm  
Wraps multiple RE backends behind a single MCP interface.

```bash
git clone https://github.com/rand-tech/pcm
cd pcm && pip install -e .
```

---

## 5. Built-in FastMCP Server (Always Available)

`scripts/re_mcp_server.py` — no external tools required (except optional radare2/jadx/ilspy).

### Claude Desktop Config
```json
{
  "mcpServers": {
    "reverse-engineering": {
      "command": "uv",
      "args": ["run", "/path/to/reverse-engineering-skill/scripts/re_mcp_server.py"]
    }
  }
}
```

**Tools:** `inspect_binary`, `extract_strings`, `analyze_bundle`, `get_binary_metadata`,
`run_r2`, `decompile`, `read_plist`, `unpack_archive`, `scan_decompiled_source`,
`install_tool`, `generate_report`.

---

## Angr (Symbolic Execution)

For packed binaries, path-constraint solving, or automated exploit finding:

```bash
pip install angr
```

### Common angr Patterns

**Find OEP (unpacking loop):**
```python
import angr
proj = angr.Project('packed_binary', auto_load_libs=False)
cfg = proj.analyses.CFGFast()
entry = proj.entry
simgr = proj.factory.simgr()
# Find state that reaches .text after unpacking
simgr.explore(find=0x401000, avoid=0x000000)
print(simgr.found[0].posix.dumps(0))
```

**Solve input constraint (CTF):**
```python
import angr, claripy
proj = angr.Project('./crackme', auto_load_libs=False)
flag = claripy.BVS('flag', 8 * 32)
state = proj.factory.entry_state(stdin=flag)
simgr = proj.factory.simgr(state)
simgr.explore(find=0x401234,   # "Correct!" branch
              avoid=0x401256)  # "Wrong!" branch
if simgr.found:
    print(simgr.found[0].solver.eval(flag, cast_to=bytes))
```

**Taint analysis / data flow:**
```python
from angr.analyses.reaching_definitions import ReachingDefinitionsAnalysis
rda = proj.analyses.ReachingDefinitions(subject=proj.kb.functions['vulnerable_func'])
```

---

## Choosing the Right Backend

| Scenario | Best Backend |
|----------|-------------|
| Deep malware analysis, needs best decompiler | Ghidra + GhidrAssistMCP |
| Stripped commercial binary, max quality | IDA Pro MCP |
| Headless/automated pipeline | radare2-mcp |
| No external tools, quick triage | Built-in FastMCP |
| Packed binary, need OEP | angr symbolic exec |
| APK / Android | Built-in (JADX) |
| .NET assembly | Built-in (ILSpyCMD) |
| CTF with constraints | angr |
| Firmware blob | Built-in + binwalk |
