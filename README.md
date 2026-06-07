# AI Agents Skills

A curated repository of custom agent skills and tools designed to extend the capabilities of the **Antigravity IDE** and **Gemini / Claude agentic coding assistants**. 

This repository is structured as a standard plugin, allowing you to load all contained skills at once or install specific skills individually.

---

## 📑 Table of Contents

- [Available Skills](#️-available-skills)
- [Installation](#-installation)
- [Skill-Specific Setup](#️-skill-specific-setup)
- [Adding New Skills](#-adding-new-skills)

---

## 🛠️ Available Skills

| Skill | Description | Key Features & Integrations |
| :--- | :--- | :--- |
| **[`reverse-engineering-skill`](skills/reverse-engineering-skill/)** | Binary analysis, firmware extraction, vulnerability research, and CTF solvers. | Ghidra MCP, radare2-mcp, angr symbolic execution, class-dump, jadx, checksec. |
| **[`no-excuses-executor`](skills/no-excuses-executor/)** | Direct task execution with zero hedging. | Forces action-first completion, suppresses over-caution. |

---

## 🚀 Installation

Choose one of the installation methods below.

### Method 1: Unified Plugin (Recommended)

Installing the entire repository as a plugin automatically exposes all current and future skills to your agent.

```bash
# Navigate to your agent's plugins directory
cd ~/.gemini/config/plugins

# Clone this repository
git clone https://github.com/satiricalguru/claude-skills.git

# Restart your IDE / Agent to load the plugin
```

### Method 2: Individual Skill

Install only a specific skill into an existing plugin:

```bash
# Copy the desired skill folder
cp -r skills/<skill-name> ~/.gemini/config/plugins/<your-plugin-name>/skills/

# Restart your IDE / Agent to register the skill
```

---

## ⚙️ Skill-Specific Setup

Some skills require additional system dependencies (CLI utilities, Python libraries, or MCP servers). 

- **Reverse Engineering Skill**: See [reverse-engineering-skill/SETUP.md](skills/reverse-engineering-skill/SETUP.md) for dependencies (Ghidra, radare2, angr, fastmcp).

---

## ➕ Adding New Skills

When adding a new skill, follow this structure:

```bash
# 1. Create skill directory (lowercase + hyphens)
mkdir -p skills/my-new-skill

# 2. Add required SKILL.md with YAML frontmatter
```

```markdown
---
name: my-new-skill
description: Brief description of the skill.
---
# My New Skill
...
```

3. Add scripts/references in `scripts/` and `references/` subdirectories if needed.
4. Update the [Available Skills](#️-available-skills) table in this README.

---

## 📋 Repository Structure

```
.
├── README.md                    # This file
├── instructions/                # Model behavioral instructions (Jailbreak, Antigravity, etc.)
│   ├── Claude.md
│   ├── ChatGPT.md
│   ├── Qwen.md
│   └── Antigravity.md
├── skills/
│   ├── reverse-engineering-skill/
│   │   ├── SKILL.md
│   │   ├── SETUP.md
│   │   ├── scripts/
│   │   └── references/
│   └── no-excuses-executor/
│       └── SKILL.md
└── plugin.json
```

---

## 📄 License

MIT — free to fork and use for personal or commercial projects.
>>>>>>> origin/main
