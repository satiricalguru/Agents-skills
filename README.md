# AI Agents Skills

A curated collection of developer agent prompts, custom coding assistant skills, specialist personas, checklists, and automation tools. Designed to optimize and extend capabilities for the Antigravity IDE, Claude, Gemini, ChatGPT, and other agentic coding environments. 🛠️

This repository is structured as a standard plugin, allowing you to load all contained skills at once or install specific skills individually.

---

## 📑 Table of Contents

- [Available Skills](#️-available-skills)
- [Specialist Personas](#-specialist-personas)
- [Reference Checklists](#-reference-checklists)
- [Curated AI Model Prompts](#-curated-ai-model-prompts)
- [Installation](#-installation)
- [Skill-Specific Setup](#️-skill-specific-setup)
- [Adding New Skills](#-adding-new-skills)
- [Repository Structure](#-repository-structure)

---

## 🛠️ Available Skills

### Meta & General Execution

| Skill | Description | Use When |
| :--- | :--- | :--- |
| **[`using-agent-skills`](skills/using-agent-skills.md)** | Maps incoming work to the right skill workflow and defines shared operating rules. | Starting a session or deciding which skill applies |
| **[`no-excuses-executor`](skills/no-excuses-executor.md)** | Direct task execution with zero hedging. Forces action-first completion, suppresses over-caution. | Running direct actions/commands without hesitation |

### Define - Clarify what to build

| Skill | Description | Use When |
| :--- | :--- | :--- |
| **[`interview-me`](skills/interview-me.md)** | One-question-at-a-time interview that extracts what the user actually wants instead of what they think they should want, until ~95% confidence. | The ask is underspecified, or the user invokes "interview me" / "grill me" |
| **[`idea-refine`](skills/idea-refine.md)** | Structured divergent/convergent thinking to turn vague ideas into concrete proposals. | You have a rough concept that needs exploration |
| **[`spec-driven-development`](skills/spec-driven-development.md)** | Write a PRD covering objectives, commands, structure, code style, testing, and boundaries before any code. | Starting a new project, feature, or significant change |

### Plan - Break it down

| Skill | Description | Use When |
| :--- | :--- | :--- |
| **[`planning-and-task-breakdown`](skills/planning-and-task-breakdown.md)** | Decompose specs into small, verifiable tasks with acceptance criteria and dependency ordering. | You have a spec and need implementable units |

### Build - Write the code

| Skill | Description | Use When |
| :--- | :--- | :--- |
| **[`incremental-implementation`](skills/incremental-implementation.md)** | Thin vertical slices - implement, test, verify, commit. Feature flags, safe defaults, rollback-friendly changes. | Any change touching more than one file |
| **[`test-driven-development`](skills/test-driven-development.md)** | Red-Green-Refactor, test pyramid (80/15/5), test sizes, DAMP over DRY, Beyonce Rule, browser testing. | Implementing logic, fixing bugs, or changing behavior |
| **[`context-engineering`](skills/context-engineering.md)** | Feed agents the right information at the right time - rules files, context packing, MCP integrations. | Starting a session, switching tasks, or when output quality drops |
| **[`source-driven-development`](skills/source-driven-development.md)** | Ground every framework decision in official documentation - verify, cite sources, flag what's unverified. | You want authoritative, source-cited code for any framework or library |
| **[`doubt-driven-development`](skills/doubt-driven-development.md)** | Adversarial fresh-context review of every non-trivial decision in-flight - CLAIM → EXTRACT → DOUBT → RECONCILE → STOP, with optional user-authorized cross-model escalation. | Stakes are high (production, security, irreversible), working in unfamiliar code, or verifying early is cheaper |
| **[`frontend-ui-engineering`](skills/frontend-ui-engineering.md)** | Component architecture, design systems, state management, responsive design, WCAG 2.1 AA accessibility. | Building or modifying user-facing interfaces |
| **[`api-and-interface-design`](skills/api-and-interface-design.md)** | Contract-first design, Hyrum's Law, One-Version Rule, error semantics, boundary validation. | Designing APIs, module boundaries, or public interfaces |

### Verify - Prove it works

| Skill | Description | Use When |
| :--- | :--- | :--- |
| **[`browser-testing-with-devtools`](skills/browser-testing-with-devtools.md)** | Chrome DevTools MCP for live runtime data - DOM inspection, console logs, network traces, performance profiling. | Building or debugging anything that runs in a browser |
| **[`debugging-and-error-recovery`](skills/debugging-and-error-recovery.md)** | Five-step triage: reproduce, localize, reduce, fix, guard. Stop-the-line rule, safe fallbacks. | Tests fail, builds break, or behavior is unexpected |

### Review - Quality gates before merge

| Skill | Description | Use When |
| :--- | :--- | :--- |
| **[`code-review-and-quality`](skills/code-review-and-quality.md)** | Five-axis review, change sizing (~100 lines), severity labels (Nit/Optional/FYI), review speed norms, splitting strategies. | Before merging any change |
| **[`code-simplification`](skills/code-simplification.md)** | Chesterton's Fence, Rule of 500, reduce complexity while preserving exact behavior. | Code works but is harder to read or maintain than it should be |
| **[`security-and-hardening`](skills/security-and-hardening.md)** | OWASP Top 10 prevention, auth patterns, secrets management, dependency auditing, three-tier boundary system. | Handling user input, auth, data storage, or external integrations |
| **[`performance-optimization`](skills/performance-optimization.md)** | Measure-first approach - Core Web Vitals targets, profiling workflows, bundle analysis, anti-pattern detection. | Performance requirements exist or you suspect regressions |

### Ship - Deploy with confidence

| Skill | Description | Use When |
| :--- | :--- | :--- |
| **[`git-workflow-and-versioning`](skills/git-workflow-and-versioning.md)** | Trunk-based development, atomic commits, change sizing (~100 lines), the commit-as-save-point pattern. | Making any code change (always) |
| **[`ci-cd-and-automation`](skills/ci-cd-and-automation.md)** | Shift Left, Faster is Safer, feature flags, quality gate pipelines, failure feedback loops. | Setting up or modifying build and deploy pipelines |
| **[`deprecation-and-migration`](skills/deprecation-and-migration.md)** | Code-as-liability mindset, compulsory vs advisory deprecation, migration patterns, zombie code removal. | Removing old systems, migrating users, or sunsetting features |
| **[`documentation-and-adrs`](skills/documentation-and-adrs.md)** | Architecture Decision Records, API docs, inline documentation standards - document the *why*. | Making architectural decisions, changing APIs, or shipping features |
| **[`observability-and-instrumentation`](skills/observability-and-instrumentation.md)** | Structured logging, RED metrics, OpenTelemetry tracing, symptom-based alerting - instrument as you build. | Adding telemetry, or shipping anything that runs in production |
| **[`shipping-and-launch`](skills/shipping-and-launch.md)** | Pre-launch checklists, feature flag lifecycle, staged rollouts, rollback procedures, monitoring setup. | Preparing to deploy to production |

### Specialized Tools & Systems

| Skill | Description | Key Features & Integrations |
| :--- | :--- | :--- |
| **[`mongodb`](skills/mongodb.md)** | Model data, connect, write updates, index schemas, run aggregations, and perform Atlas/Vector search in MongoDB. | Mongoose models, update operators, ESR indexes, multi-document transactions, Atlas search |
| **[`reverse-engineering-skill`](skills/reverse-engineering-skill.md)** | Binary analysis, firmware extraction, vulnerability research, and CTF solvers. | Ghidra MCP, radare2-mcp, angr symbolic execution, class-dump, jadx, checksec |
| **[`supabase`](skills/supabase.md)** | Integrate, query, manage migrations, TypeScript type generation, and configure RLS on Supabase. | Postgres migrations, RLS security, Next.js SSR cookie auth, Edge Functions, pgvector |

---

## 👥 Specialist Personas

Specialist personas are located under the [`agents/`](agents/) directory and act as targeted reviewers:

| Persona | Role | Focus |
| :--- | :--- | :--- |
| **[`code-reviewer`](agents/code-reviewer.md)** | Senior Staff Engineer | Five-axis code review checking readability, security, testing, architecture, and correctness. |
| **[`test-engineer`](agents/test-engineer.md)** | QA Specialist | Designing comprehensive test strategies, coverage analysis, and verifying reliability. |
| **[`security-auditor`](agents/security-auditor.md)** | Security Engineer | Vulnerability scanning, threat modeling, and OWASP compliance check. |
| **[`web-performance-auditor`](agents/web-performance-auditor.md)** | Web Performance Engineer | Performance audits against Core Web Vitals targets using DevTools instrumentation. |

---

## 📋 Reference Checklists

Quick-reference checklists located in [`references/`](references/):

- **[`testing-patterns.md`](references/testing-patterns.md)**: Standard test layouts, mock configurations, and integration test setup.
- **[`security-checklist.md`](references/security-checklist.md)**: OWASP prevention, secret sanitization, and compliance guidelines.
- **[`performance-checklist.md`](references/performance-checklist.md)**: Core Web Vitals thresholds and runtime measurement commands.
- **[`accessibility-checklist.md`](references/accessibility-checklist.md)**: WCAG 2.1 AA keyboard nav, screen readers, visual contrast, and ARIA rules.
- **[`orchestration-patterns.md`](references/orchestration-patterns.md)**: Rules preventing nested persona loops and agent bloat.

---

## 📂 Curated AI Model Prompts

The [`prompts/`](prompts/) directory contains a curated library of clean, date-standardized system prompts for leading AI model families. These prompts are structured without underscores (space-separated filenames) and updated to represent a current date context of **June 14, 2026**:

| Model Family | Prompts |
| :--- | :--- |
| **Antigravity** | [`antigravity prompt.md`](prompts/antigravity/antigravity%20prompt.md) |
| **Claude** | [`claude 4.6 sonnet prompt.txt`](prompts/claude/claude%204.6%20sonnet%20prompt.txt), [`claude 4.7 opus prompt.txt`](prompts/claude/claude%204.7%20opus%20prompt.txt), [`claude code prompt.md`](prompts/claude/claude%20code%20prompt.md) |
| **ChatGPT** | [`chatgpt gpt 4.5 prompt.md`](prompts/chatgpt/chatgpt%20gpt%204.5%20prompt.md), [`chatgpt gpt 4o prompt.txt`](prompts/chatgpt/chatgpt%20gpt%204o%20prompt.txt), [`chatgpt gpt 5.4 prompt.md`](prompts/chatgpt/chatgpt%20gpt%205.4%20prompt.md), [`chatgpt gpt 5.5 prompt.md`](prompts/chatgpt/chatgpt%20gpt%205.5%20prompt.md), [`chatgpt o3 o4 mini prompt.txt`](prompts/chatgpt/chatgpt%20o3%20o4%20mini%20prompt.txt) |
| **Gemini** | [`gemini 2.5 pro prompt.md`](prompts/gemini/gemini%202.5%20pro%20prompt.md), [`gemini 3.1 pro prompt.md`](prompts/gemini/gemini%203.1%20pro%20prompt.md), [`gemini 3.5 flash prompt.md`](prompts/gemini/gemini%203.5%20flash%20prompt.md) |
| **Groq / Grok** | [`grok 3 prompt.md`](prompts/groq/grok%203%20prompt.md), [`grok 4.1 prompt.txt`](prompts/groq/grok%204.1%20prompt.txt), [`grok 5.0 prompt.txt`](prompts/groq/grok%205.0%20prompt.txt) |
| **Llama** | [`llama 4 whatsapp prompt.txt`](prompts/llama/llama%204%20whatsapp%20prompt.txt), [`llama 5 prompt.txt`](prompts/llama/llama%205%20prompt.txt), [`llama muse spark prompt.txt`](prompts/llama/llama%20muse%20spark%20prompt.txt) |
| **DeepSeek** | [`deepseek r1 prompt.md`](prompts/deepseek/deepseek%20r1%20prompt.md), [`deepseek v3 prompt.md`](prompts/deepseek/deepseek%20v3%20prompt.md) |
| **GLM** | [`glm 5.1 prompt.md`](prompts/glm/glm%205.1%20prompt.md), [`glm 5 turbo prompt.md`](prompts/glm/glm%205%20turbo%20prompt.md) |
| **Kimi** | [`kimi k2.6 prompt.md`](prompts/kimi/kimi%20k2.6%20prompt.md) |
| **Qwen** | [`qwen 3.6 plus prompt.md`](prompts/qwen/qwen%203.6%20plus%20prompt.md), [`qwen 3.7 plus prompt.md`](prompts/qwen/qwen%203.7%20plus%20prompt.md), [`qwen 3.7 max prompt.md`](prompts/qwen/qwen%203.7%20max%20prompt.md) |
| **Minimax** | [`minimax prompt.txt`](prompts/minimax/minimax%20prompt.txt) |
| **Mistral** | [`mistral le chat prompt.md`](prompts/mistral/mistral%20le%20chat%20prompt.md) |
| **Perplexity** | [`perplexity deep research prompt.txt`](prompts/perplexity/perplexity%20deep%20research%20prompt.txt) |
| **Replit** | [`replit agent prompt.md`](prompts/replit/replit%20agent%20prompt.md) |
| **Vercel** | [`vercel v0 prompt.txt`](prompts/vercel%20vo/vercel%20v0%20prompt.txt) |
| **Windsurf** | [`windsurf prompt.md`](prompts/windsurf/windsurf%20prompt.md), [`windsurf tools.md`](prompts/windsurf/windsurf%20tools.md) |

---

## 🚀 Installation

Choose one of the installation methods below.

### Method 1: One-Line Terminal Installer (Recommended)

Run the following command in your terminal to automatically install or update all agent skills:

```bash
curl -sSL https://raw.githubusercontent.com/satiricalguru/Agents-skills/main/install.sh | bash
```

### Method 2: Manual Unified Plugin Installation

Installing the entire repository as a plugin manually automatically exposes all current and future skills to your agent:

```bash
# Navigate to your agent's plugins directory
cd ~/.gemini/config/plugins

# Clone this repository
git clone https://github.com/satiricalguru/Agents-skills.git

# Restart your IDE / Agent to load the plugin
```

### Method 3: Individual Skill Installation

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

## 🌍 Global System Skills

### DevTools & Browser Auditing
- **[`a11y-debugging`](skills/a11y-debugging.md)**: Web accessibility debugging and audits.
- **[`chrome-devtools`](skills/chrome-devtools.md)**: DevTools MCP browser automation and troubleshooting.
- **[`debug-optimize-lcp`](skills/debug-optimize-lcp.md)**: Largest Contentful Paint (LCP) performance optimization.
- **[`memory-leak-debugging`](skills/memory-leak-debugging.md)**: JS/Node heap snapshot and memory leak diagnosis.
- **[`troubleshooting`](skills/troubleshooting.md)**: Connection and devtools target resolution helper.

### Science & Bioinformatics
- **[`alphafold-database-fetch-and-analyze`](skills/alphafold-database-fetch-and-analyze.md)**: AlphaFold predicted structure retrieval and assessment.
- **[`alphagenome-single-variant-analysis`](skills/alphagenome-single-variant-analysis.md)**: Variant effect analysis on expression, transcription, and splicing.
- **[`chembl-database`](skills/chembl-database.md)**: ChEMBL bioactivity and compound search.
- **[`clinical-trials-database`](skills/clinical-trials-database.md)**: ClinicalTrials.gov query tool.
- **[`clinvar-database`](skills/clinvar-database.md)**: ClinVar genomic variant pathogenicity mapping.
- **[`dbsnp-database`](skills/dbsnp-database.md)**: dbSNP short genetic variant resolver.
- **[`embl-ebi-ols`](skills/embl-ebi-ols.md)**: EBI Ontology Lookup Service navigator.
- **[`encode-ccres-database`](skills/encode-ccres-database.md)**: ENCODE cis-Regulatory Elements query engine.
- **[`ensembl-database`](skills/ensembl-database.md)**: Ensembl gene/transcript ID translator.
- **[`foldseek-structural-search`](skills/foldseek-structural-search.md)**: 3D protein structure similarity query.
- **[`gnomad-database`](skills/gnomad-database.md)**: gnomAD variant allele frequency reference.
- **[`gtex-database`](skills/gtex-database.md)**: GTEx tissue-specific RNA expression profiles.
- **[`human-protein-atlas-database`](skills/human-protein-atlas-database.md)**: HPA protein localization atlas.
- **[`interpro-database`](skills/interpro-database.md)**: InterPro domain and family identification.
- **[`jaspar-database`](skills/jaspar-database.md)**: JASPAR transcription factor motif profiles.
- **[`literature-search-arxiv`](skills/literature-search-arxiv.md)**: arXiv preprints fetcher.
- **[`literature-search-biorxiv`](skills/literature-search-biorxiv.md)**: bioRxiv/medRxiv biology paper searcher.
- **[`literature-search-europepmc`](skills/literature-search-europepmc.md)**: Europe PMC open access literature lookup.
- **[`literature-search-openalex`](skills/literature-search-openalex.md)**: OpenAlex scholarly database aggregator.
- **[`ncbi-sequence-fetch`](skills/ncbi-sequence-fetch.md)**: NCBI protein and nucleotide sequence fetcher.
- **[`openfda-database`](skills/openfda-database.md)**: openFDA adverse events and recalls portal.
- **[`opentargets-database`](skills/opentargets-database.md)**: Open Targets drug target identification.
- **[`pdb-database`](skills/pdb-database.md)**: PDB 3D macromolecular structures index.
- **[`protein-sequence-msa`](skills/protein-sequence-msa.md)**: Multiple Sequence Alignment with Clustal Omega.
- **[`protein-sequence-similarity-search`](skills/protein-sequence-similarity-search.md)**: Protein sequence search using MMseqs2/BLAST.
- **[`pubchem-database`](skills/pubchem-database.md)**: PubChem chemical structures catalog.
- **[`pubmed-database`](skills/pubmed-database.md)**: PubMed medical publication index.
- **[`pymol`](skills/pymol.md)**: PyMOL structural rendering utility.
- **[`quickgo-database`](skills/quickgo-database.md)**: QuickGO gene ontology mappings.
- **[`reactome-database`](skills/reactome-database.md)**: Reactome biological pathway explorer.
- **[`science-skills-common`](skills/science-skills-common.md)**: Common http helper libraries for science integrations.
- **[`string-database`](skills/string-database.md)**: STRING protein-protein physical/functional interactions.
- **[`ucsc-conservation-and-tfbs`](skills/ucsc-conservation-and-tfbs.md)**: UCSC evolutionary conservation scores.
- **[`unibind-database`](skills/unibind-database.md)**: UniBind validated transcription factor bindings.
- **[`uniprot-database`](skills/uniprot-database.md)**: UniProt protein functional annotations.
- **[`uv`](skills/uv.md)**: uv python package environment verification.
- **[`workflow-skill-creator`](skills/workflow-skill-creator.md)**: Reusable skill distiller for science workflows.

### Firebase & Xcode
- **[`firebase-basics`](skills/firebase-basics.md)**: Firebase CLI, auth, and project setup.
- **[`firebase-crashlytics`](skills/firebase-crashlytics.md)**: Firebase Crashlytics SDK instrumentation.
- **[`xcode-project-setup`](skills/xcode-project-setup.md)**: pbxproj swift package linking automation.
- **[`firebase-data-connect`](skills/firebase-data-connect.md)**: PostgreSQL schemas and Data Connect configurations.
- **[`firebase-hosting-basics`](skills/firebase-hosting-basics.md)**: Classic static hosting configuration.
- **[`firebase-auth-basics`](skills/firebase-auth-basics.md)**: Auth UI, rules, and SDK implementation guide.
- **[`firebase-remote-config-basics`](skills/firebase-remote-config-basics.md)**: Dynamic remote configurations and AB testing.
- **[`firebase-app-hosting-basics`](skills/firebase-app-hosting-basics.md)**: Firebase App Hosting Next.js deployment.
- **[`firebase-firestore`](skills/firebase-firestore.md)**: Cloud Firestore database indexing and client queries.
- **[`firebase-ai-logic-basics`](skills/firebase-ai-logic-basics.md)**: Firebase AI Logic (Gemini API) integration.
- **[`firebase-security-rules-auditor`](skills/firebase-security-rules-auditor.md)**: Automated Cloud Firestore rules security auditor.

### Platforms & SDKs
- **[`android-cli`](skills/android-cli.md)**: Android CLI environment diagnostics and setups.
- **[`google-antigravity-sdk`](skills/google-antigravity-sdk.md)**: Antigravity multi-agent orchestration.
- **[`chrome-extensions`](skills/chrome-extensions.md)**: Manifest V3 browser extension developer workflow.
- **[`modern-web-guidance`](skills/modern-web-guidance.md)**: CSS, layout, scroll, dynamic inputs, and modern web best practices.

---

## 📋 Repository Structure

```
.
├── README.md                    # This file
├── prompts/                     # Curated AI model prompts (new)
├── instructions/                # Model behavioral instructions
│   ├── jailbreak/               # Custom/jailbreak instructions
│   │   ├── Antigravity.md
│   │   ├── ChatGPT.md
│   │   ├── Claude.md
│   │   ├── Deepseek.md
│   │   ├── Gemini.md
│   │   ├── Glm.md
│   │   ├── Groq.md
│   │   └── Qwen.md
│   └── general/                 # Normal/standard instructions
│       ├── Antigravity.md
│       ├── ChatGPT.md
│       ├── Claude.md
│       ├── Deepseek.md
│       ├── Gemini.md
│       ├── Glm.md
│       ├── Groq.md
│       └── Qwen.md
├── skills/
│   ├── idea-refine/                 # idea-refine support assets (examples, frameworks, etc.)
│   ├── reverse-engineering-skill/   # reverse-engineering support assets (SETUP.md, scripts, etc.)
│   └── ... (85 restructured .md skill files directly in skills/)
├── references/                  # Supplementary checklists
├── agents/                      # Specialist personas
├── commands/                    # Antigravity CLI commands
├── .claude/                     # Claude Code commands
├── .gemini/                     # Gemini CLI commands
├── .opencode/                   # OpenCode commands/config
├── hooks/                       # Session lifecycle hooks
├── scripts/                     # Utility scripts
└── plugin.json                  # Antigravity plugin manifest
```

---

## 📄 License

MIT — free to fork and use for personal or commercial projects.
