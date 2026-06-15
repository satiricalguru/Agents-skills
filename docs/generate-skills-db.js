const fs = require('fs');
const path = require('path');

let SKILLS_DIR = path.join(__dirname, '..', 'skills');
if (!fs.existsSync(SKILLS_DIR)) {
  SKILLS_DIR = path.join(__dirname, '..', 'Agents-skills', 'skills');
}
const OUTPUT_FILE = path.join(__dirname, 'skills.json');

// Exact mapping from screenshots
const screenshotMapping = {
  // High Priority
  'security-and-hardening': { category: 'high', priority: 1, why: 'OWASP Top 10, auth patterns, secrets management — should be active on every project touching user data' },
  'test-driven-development': { category: 'high', priority: 2, why: 'Red-Green-Refactor discipline, full test pyramid (80/15/5), Beyonce Rule — enforces proof over "seems right"' },
  'debugging-and-error-recovery': { category: 'high', priority: 3, why: 'Structured 5-step triage (reproduce → localize → reduce → fix → guard) — stops the guessing loop' },
  'git-workflow-and-versioning': { category: 'high', priority: 4, why: 'Trunk-based dev, atomic commits, commit-as-save-point — especially important when Claude generates code at speed' },
  'ci-cd-and-automation': { category: 'high', priority: 5, why: 'Automated quality gates, feature flags, deployment pipelines — catches what Claude misses' },
  'observability-and-instrumentation': { category: 'high', priority: 6, why: 'Structured logging, RED metrics, OpenTelemetry — without this, production bugs become archaeology' },

  // Medium Priority
  'code-review-and-quality': { category: 'medium', priority: 1, why: '5-axis review with severity labels (Nit/Optional/FYI), change sizing norms — adds a review conscience' },
  'spec-driven-development': { category: 'medium', priority: 2, why: 'Write a PRD before writing code — prevents vague-to-broken builds' },
  'planning-and-task-breakdown': { category: 'medium', priority: 3, why: 'Decomposes specs into verifiable atomic tasks with dependency ordering' },
  'api-and-interface-design': { category: 'medium', priority: 4, why: 'Contract-first design, Hyrum\'s Law, error semantics — critical for any API work' },
  'documentation-and-adrs': { category: 'medium', priority: 5, why: 'Architecture Decision Records — documents why, not just what' },
  'performance-optimization': { category: 'medium', priority: 6, why: 'Core Web Vitals targets, measure-first approach, bundle analysis' },
  'shipping-and-launch': { category: 'medium', priority: 7, why: 'Pre-launch checklists, staged rollouts, rollback procedures' },
  'deprecation-and-migration': { category: 'medium', priority: 8, why: 'Code-as-liability mindset, safe migration patterns — prevents zombie code accumulation' },

  // Situational
  'browser-testing-with-devtools': { category: 'situational', priority: 1, why: 'If you do any web development — live DOM inspection, network traces' },
  'a11y-debugging': { category: 'situational', priority: 2, why: 'If building user-facing UIs (WCAG 2.1 AA enforcement)' },
  'context-engineering': { category: 'situational', priority: 3, why: 'If you do long multi-session agentic work — prevents context drift and quality degradation' },
  'interview-me': { category: 'situational', priority: 4, why: 'Great for clarifying underspecified requests — extracts what you actually want' },
  'idea-refine': { category: 'situational', priority: 5, why: 'Divergent/convergent thinking to solidify vague concepts' },
  'reverse-engineering-skill': { category: 'situational', priority: 6, why: 'If you do security research, CTFs, or binary analysis (Ghidra MCP, radare2, angr)' },
  'incremental-implementation': { category: 'situational', priority: 7, why: 'Enforces thin vertical slices — good discipline for large features' },
  'doubt-driven-development': { category: 'situational', priority: 8, why: 'Adversarial review of in-flight decisions — use on high-stakes/production changes' },
  'xcode-project-setup': { category: 'situational', priority: 9, why: 'iOS/macOS development only' },
  'android-cli': { category: 'situational', priority: 10, why: 'Android development only' },
  'uv': { category: 'situational', priority: 11, why: 'If you use Python — fast package manager workflow' }
};

// Parse a single Markdown file with frontmatter
function parseMarkdownFile(filePath) {
  const content = fs.readFileSync(filePath, 'utf-8');
  const filename = path.basename(filePath, '.md');

  let metadata = {
    id: filename,
    name: filename.split('-').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' '),
    description: '',
    tags: []
  };

  let rawContent = content;

  // Simple Frontmatter Parser
  if (content.startsWith('---')) {
    const parts = content.split('---');
    if (parts.length >= 3) {
      const frontmatterText = parts[1];
      rawContent = parts.slice(2).join('---').trim();

      const lines = frontmatterText.split('\n');
      lines.forEach(line => {
        const colonIndex = line.indexOf(':');
        if (colonIndex > -1) {
          const key = line.slice(0, colonIndex).trim();
          const val = line.slice(colonIndex + 1).trim();
          // Clean quotes if present
          const cleanedVal = val.replace(/^["']|["']$/g, '').trim();
          if (key === 'name') metadata.name = cleanedVal;
          if (key === 'description') metadata.description = cleanedVal;
        }
      });
    }
  }

  // Determine Category, Priority, and Screenshot Description
  const matched = screenshotMapping[filename];
  if (matched) {
    metadata.category = matched.category;
    metadata.priority = matched.priority;
    metadata.why = matched.why;
  } else {
    // If not in screenshots, categorize based on directories or name
    if (filename.includes('database') || filename.includes('literature') || filename.includes('protein') || ['alphafold-database-fetch-and-analyze', 'chembl-database', 'clinical-trials-database', 'clinvar-database', 'dbsnp-database', 'embl-ebi-ols', 'encode-ccres-database', 'ensembl-database', 'foldseek-structural-search', 'gnomad-database', 'gtex-database', 'human-protein-atlas-database', 'interpro-database', 'jaspar-database', 'ncbi-sequence-fetch', 'opentargets-database', 'pdb-database', 'pubchem-database', 'pubmed-database', 'quickgo-database', 'reactome-database', 'string-database', 'ucsc-conservation-and-tfbs', 'unibind-database', 'uniprot-database'].includes(filename)) {
      metadata.category = 'specialized-science';
      metadata.priority = 100;
      metadata.why = 'Biological and bioinformatics research databases & tools';
    } else if (filename.includes('firebase') || filename === 'supabase' || filename === 'mongodb') {
      metadata.category = 'specialized-platforms';
      metadata.priority = 100;
      metadata.why = 'Specific database or backend hosting platforms';
    } else {
      metadata.category = 'specialized-utility';
      metadata.priority = 100;
      metadata.why = 'General coding utilities and helper scripts';
    }
  }

  metadata.content = rawContent;
  return metadata;
}

function run() {
  console.log(`Scanning skills from: ${SKILLS_DIR}`);
  if (!fs.existsSync(SKILLS_DIR)) {
    console.error(`Error: Skills directory does not exist at ${SKILLS_DIR}`);
    process.exit(1);
  }

  const files = fs.readdirSync(SKILLS_DIR);
  const skills = [];

  files.forEach(file => {
    if (path.extname(file) === '.md') {
      const filePath = path.join(SKILLS_DIR, file);
      try {
        const skill = parseMarkdownFile(filePath);
        skills.push(skill);
      } catch (err) {
        console.error(`Error parsing ${file}:`, err);
      }
    }
  });

  // Sort by category and priority
  skills.sort((a, b) => {
    if (a.category !== b.category) {
      const catOrder = { 'high': 1, 'medium': 2, 'situational': 3, 'specialized-platforms': 4, 'specialized-science': 5, 'specialized-utility': 6 };
      return (catOrder[a.category] || 99) - (catOrder[b.category] || 99);
    }
    return a.priority - b.priority;
  });

  fs.writeFileSync(OUTPUT_FILE, JSON.stringify(skills, null, 2));
  console.log(`Successfully compiled ${skills.length} skills to ${OUTPUT_FILE}`);
}

run();
