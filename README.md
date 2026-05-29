# Claude & Gemini Agent Skills

A curated repository of custom agent skills and tools designed to extend the capabilities of the **Antigravity IDE** and **Gemini / Claude agentic coding assistants**. 

This repository is structured as a standard plugin, allowing you to load all contained skills at once or install specific skills individually.

---

## 🛠️ Available Skills

| Skill Folder | Description | Key Features & Integrations |
| :--- | :--- | :--- |
| **[`reverse-engineering-skill`](file:///Users/jatinpandey/Antigravity/Claude%20skills/skills/reverse-engineering-skill)** | Binary analysis, firmware extraction, vulnerability research, and CTF solvers. | Ghidra MCP, radare2-mcp, angr symbolic execution, class-dump, jadx, checksec. |

---

## 🚀 Installation Instructions

You can install these skills using one of the two methods below.

### Method 1: Install as a Unified Plugin (Recommended)

Installing the entire repository as a plugin automatically exposes all current and future skills to your agent.

1. **Navigate to the agent's plugins directory:**
   ```bash
   cd ~/.gemini/config/plugins
   ```

2. **Clone this repository:**
   ```bash
   git clone https://github.com/satiricalguru/claude-skills.git
   ```

3. **Restart your IDE / Agent** to load the new plugin.

---

### Method 2: Install as an Individual Skill

If you want to add a specific skill (e.g., `reverse-engineering-skill`) to one of your existing plugins:

1. **Copy the skill folder** into your target plugin's `skills/` directory:
   ```bash
   cp -r skills/reverse-engineering-skill ~/.gemini/config/plugins/<your-plugin-name>/skills/
   ```

2. **Restart your IDE / Agent** to register the new skill.

---

## ⚙️ Skill-Specific Setup

Some skills require additional system dependencies (e.g., specific command-line utilities, Python libraries, or MCP servers). 

* **Reverse Engineering Skill**: Read the detailed [reverse-engineering-skill/SETUP.md](file:///Users/jatinpandey/Antigravity/Claude%20skills/skills/reverse-engineering-skill/SETUP.md) for dependencies setup (like Ghidra, radare2, angr, and fastmcp configuration).

---

## ➕ Adding New Skills in the Future

When adding a new skill to this repository, follow these best practices:

1. **Create a folder** under the `skills/` directory using lowercase and hyphens:
   ```bash
   mkdir -p skills/my-new-skill
   ```
2. **Add a `SKILL.md`** file (required) at the root of your skill folder with YAML frontmatter:
   ```markdown
   ---
   name: my-new-skill
   description: Brief description of the skill.
   ---
   # My New Skill
   ...
   ```
3. **Add helper scripts or references** inside `scripts/` and `references/` subdirectories inside your skill folder if programmatic tools are needed.
4. **Update this root README.md** table to list your new skill!
  
---
## ➕ 📄 License

MIT — free to fork and use for personal or commercial projects.
