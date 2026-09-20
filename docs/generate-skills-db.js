const fs = require('fs');
const path = require('path');

let SKILLS_DIR = path.join(__dirname, '..', 'skills');
if (!fs.existsSync(SKILLS_DIR)) {
  SKILLS_DIR = path.join(__dirname, '..', 'Agents-skills', 'skills');
}
const OUTPUT_FILE = path.join(__dirname, 'skills.json');

// Exact mapping from screenshots & core priorities
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
  'uv': { category: 'situational', priority: 11, why: 'If you use Python — fast package manager workflow' },
  'web-scraper': { category: 'situational', priority: 12, why: 'Intelligent adaptive web scraping, traffic interception, anti-blocking, and Apify Actor creation' }
};

// Skill groups classification
const FRONTEND_UI_SKILLS = new Set([
  'agency-grid-layout-minimal', 'beautiful-shadows', 'blue-cloudy-clean-modern',
  'blue-laser-clean-glass-layout', 'book-serif-index', 'bright-green-tech-system-webgl',
  'clean-minimal-beige-light-mode', 'container-lines', 'corner-diagonals', 'corner-lasers',
  'css-alpha-masking', 'css-border-gradient', 'dark-blue-contrasting-clean',
  'dark-glass-clean-layout', 'dither-background', 'dither-laser-dark-mode',
  'documentary-brutalist-agency', 'editorial-portfolio-chapters', 'editorial-service-booking',
  'editorial-tech', 'framed-grid-layout', 'framed-tech-dark-border-gradient',
  'funky-purple-container-tech', 'glass-dark-mode-clock', 'glass-dark-ui',
  'gooey-blob-system', 'ui-ux-pro-max', 'frontend-ui-engineering', 'modern-web-guidance'
]);

const WEBGL_3D_SKILLS = new Set([
  'add-mouse-driven-orbit', 'add-shader-cursor-trail', 'ambient-section-particles',
  'animation-on-scroll', 'animation-systems', 'atmosphere-background',
  'background-grid-webgl', 'beam-glow-states', 'build-awwwards-quality-sites',
  'build-interactive-particle-trail', 'build-threejs-scroll-worlds', 'build-wireframe-scan-reveal',
  'cinematic-gsap-lenis-motion-system', 'cinematic-scroll-storytelling', 'cobejs',
  'falling-leaves', 'globe-gl', 'globe-particles', 'gsap-scrolltrigger-storytelling',
  'optimize-web-animations'
]);

const GAMEDEV_SKILLS = new Set([
  'author-game-levels', 'build-game-audio-feedback', 'build-game-camera-controls',
  'build-game-changelog', 'build-game-inventory', 'build-game-map-editor',
  'build-game-monster-system', 'build-hybrid-game-assets', 'build-isometric-arpg',
  'build-mobile-threejs-games', 'build-rigged-game-assets', 'build-threejs-enemy-systems',
  'build-vesperfall-review-assets', 'create-game-vfx', 'design-action-combat',
  'design-game-encounters', 'implement-fog-of-war', 'optimize-threejs-games',
  'ship-web-games', 'test-playable-web-games', 'tune-enemy-ai'
]);

const AUDIT_QUALITY_SKILLS = new Set([
  'audit-ai-design-slop', 'audit-reference-originality', 'audit-verify-explain-grade-5',
  'no-ai-design-slop', 'iterate-until-verified', 'performance-profiling',
  'stitched-full-page-capture'
]);

const CREATIVE_MEDIA_SKILLS = new Set([
  'aura-asset-images', 'company-logos', 'design-first-ui-prompting', 'elevenlabs-tts',
  'generate-reference-inspired-brand-worlds', 'unsplash-asset-images', 'video-to-superprompt',
  'html-to-interaction-prompts', 'article-prompts-to-skills', 'build-daily-inspiration-sites',
  'daily-ui-inspiration-capture', 'write-like-meng-on-x', 'x-bookmark-quote-posts',
  'browser-video-recording', 'web-technique-to-skill'
]);

const SYSTEM_SKILLS = new Set([
  'agy-customizations', 'antigravity-guide', 'google-antigravity-sdk',
  'permissioned-github', 'hide-agent-reasoning', 'publish-project-to-github',
  'start-teardown', 'using-agent-skills', 'no-excuses-executor'
]);

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

  // Frontmatter Parser (supports quoted values and YAML block scalars: |, >, |-, >-)
  if (content.startsWith('---')) {
    const parts = content.split('---');
    if (parts.length >= 3) {
      const frontmatterText = parts[1];
      rawContent = parts.slice(2).join('---').trim();

      const lines = frontmatterText.split('\n');
      let blockKey = null;
      let blockStyle = null;
      const blockLines = [];

      const commitBlock = () => {
        if (blockKey === null) return;
        let text = blockLines.map(l => l.replace(/^[ \t]+/, '')).join('\n');
        if (blockStyle.startsWith('>')) {
          text = text.replace(/[ \t]*\n[ \t]*/g, ' ');
        }
        if (blockStyle.endsWith('-')) {
          text = text.trim();
        } else if (!blockStyle.endsWith('+')) {
          text = text.replace(/\n+$/, '');
        }
        if (blockKey === 'name') metadata.name = text;
        if (blockKey === 'description') metadata.description = text;
        blockKey = null;
        blockStyle = null;
        blockLines.length = 0;
      };

      lines.forEach(line => {
        if (blockKey !== null) {
          if (/^[ \t]/.test(line) || line.trim() === '') {
            blockLines.push(line);
            return;
          }
          commitBlock();
        }
        const colonIndex = line.indexOf(':');
        if (colonIndex > -1) {
          const key = line.slice(0, colonIndex).trim();
          const val = line.slice(colonIndex + 1).trim();
          if (/^[|>][+-]?$/.test(val)) {
            blockKey = key;
            blockStyle = val;
            return;
          }
          const cleanedVal = val.replace(/^["']|["']$/g, '').trim();
          if (key === 'name') metadata.name = cleanedVal;
          if (key === 'description') metadata.description = cleanedVal;
        }
      });
      commitBlock();
    }
  }

  // Determine Category, Priority, and Description
  const matched = screenshotMapping[filename];
  if (matched) {
    metadata.category = matched.category;
    metadata.priority = matched.priority;
    metadata.why = matched.why;
  } else if (FRONTEND_UI_SKILLS.has(filename)) {
    metadata.category = 'specialized-frontend-ui';
    metadata.priority = 100;
    metadata.why = metadata.description || 'Modern web design, layout systems, and CSS styling architectures';
  } else if (WEBGL_3D_SKILLS.has(filename)) {
    metadata.category = 'specialized-webgl-3d';
    metadata.priority = 100;
    metadata.why = metadata.description || 'Creative web motion, GSAP animations, WebGL shaders & Three.js 3D';
  } else if (GAMEDEV_SKILLS.has(filename)) {
    metadata.category = 'specialized-gamedev';
    metadata.priority = 100;
    metadata.why = metadata.description || 'Web game development, combat systems, 3D asset workflows & level design';
  } else if (AUDIT_QUALITY_SKILLS.has(filename)) {
    metadata.category = 'specialized-audit-quality';
    metadata.priority = 100;
    metadata.why = metadata.description || 'Anti-slop design gates, evidence-based audits & originality verification';
  } else if (CREATIVE_MEDIA_SKILLS.has(filename)) {
    metadata.category = 'specialized-creative-media';
    metadata.priority = 100;
    metadata.why = metadata.description || 'Asset sourcing, daily UI inspiration, TTS narration & superprompts';
  } else if (SYSTEM_SKILLS.has(filename)) {
    metadata.category = 'specialized-system';
    metadata.priority = 100;
    metadata.why = metadata.description || 'Antigravity IDE customizations, agent orchestration & lifecycle hooks';
  } else if (filename.includes('database') || filename.includes('literature') || filename.includes('protein') || ['alphafold-database-fetch-and-analyze', 'chembl-database', 'clinical-trials-database', 'clinvar-database', 'credentials', 'dbsnp-database', 'embl-ebi-ols', 'encode-ccres-database', 'ensembl-database', 'foldseek-structural-search', 'gnomad-database', 'gtex-database', 'human-protein-atlas-database', 'interpro-database', 'jaspar-database', 'ncbi-sequence-fetch', 'opentargets-database', 'pdb-database', 'predictingthepast', 'pubchem-database', 'pubmed-database', 'quickgo-database', 'reactome-database', 'string-database', 'ucsc-conservation-and-tfbs', 'unibind-database', 'uniprot-database'].includes(filename)) {
    metadata.category = 'specialized-science';
    metadata.priority = 100;
    metadata.why = metadata.description || 'Biological and bioinformatics research databases & scientific tools';
  } else if (filename.includes('firebase') || filename === 'supabase' || filename === 'mongodb' || filename === 'chrome-extensions' || filename === 'chrome-devtools') {
    metadata.category = 'specialized-platforms';
    metadata.priority = 100;
    metadata.why = metadata.description || 'Specific database, backend hosting or platform SDK integrations';
  } else {
    metadata.category = 'specialized-utility';
    metadata.priority = 100;
    metadata.why = metadata.description || 'General coding utilities, development patterns, and helper workflows';
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
      const catOrder = {
        'high': 1,
        'medium': 2,
        'situational': 3,
        'specialized-frontend-ui': 4,
        'specialized-webgl-3d': 5,
        'specialized-gamedev': 6,
        'specialized-audit-quality': 7,
        'specialized-creative-media': 8,
        'specialized-platforms': 9,
        'specialized-science': 10,
        'specialized-system': 11,
        'specialized-utility': 12
      };
      return (catOrder[a.category] || 99) - (catOrder[b.category] || 99);
    }
    return a.priority - b.priority;
  });

  fs.writeFileSync(OUTPUT_FILE, JSON.stringify(skills, null, 2));
  console.log(`Successfully compiled ${skills.length} skills to ${OUTPUT_FILE}`);
}

run();
