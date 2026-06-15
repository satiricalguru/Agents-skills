document.addEventListener('DOMContentLoaded', () => {
  // Application State
  let skillsData = [];
  const selectedSkills = new Set();
  let currentOpenSkill = null;
  let wizardAnswers = {};
  let currentWizardStep = 1;

  // DOM Elements
  const highContainer = document.getElementById('highSkillsContainer');
  const mediumContainer = document.getElementById('mediumSkillsContainer');
  const situationalContainer = document.getElementById('situationalSkillsContainer');
  const specializedContainer = document.getElementById('specializedSkillsContainer');
  
  const searchInput = document.getElementById('searchInput');
  const btnSelectAll = document.getElementById('btnSelectAll');
  const btnClearSelection = document.getElementById('btnClearSelection');
  const btnQuiz = document.getElementById('btnQuiz');
  
  const exportFormat = document.getElementById('exportFormat');
  const codePreview = document.getElementById('codePreview');
  const previewTitle = document.getElementById('previewTitle');
  const selectedCountBadge = document.getElementById('selectedCountBadge');
  const compilerSummary = document.getElementById('compilerSummary');
  
  const btnCopy = document.getElementById('btnCopy');
  const btnDownload = document.getElementById('btnDownload');
  const btnPowerShell = document.getElementById('btnPowerShell');

  // Drawer Elements
  const drawer = document.getElementById('drawer');
  const drawerBackdrop = document.getElementById('drawerBackdrop');
  const drawerTitle = document.getElementById('drawerTitle');
  const drawerBadge = document.getElementById('drawerBadge');
  const drawerMarkdown = document.getElementById('drawerMarkdown');
  const btnDrawerClose = document.getElementById('btnDrawerClose');
  const btnDrawerCancel = document.getElementById('btnDrawerCancel');
  const btnDrawerToggleSelect = document.getElementById('btnDrawerToggleSelect');

  // Wizard Elements
  const wizardBackdrop = document.getElementById('wizardBackdrop');
  const btnWizardClose = document.getElementById('btnWizardClose');
  const btnWizardNext = document.getElementById('btnWizardNext');
  const btnWizardBack = document.getElementById('btnWizardBack');
  const wizardSteps = document.querySelectorAll('.wizard-step');

  // Load Skills Database
  async function loadSkills() {
    try {
      const response = await fetch('skills.json');
      if (!response.ok) throw new Error('Failed to load skills database');
      skillsData = await response.json();
      
      // Select High priority skills by default
      skillsData.forEach(skill => {
        if (skill.category === 'high') {
          selectedSkills.add(skill.id);
        }
      });

      renderSkills();
      updateCompilation();
    } catch (err) {
      console.error(err);
      alert('Error loading skills database. Make sure generate-skills-db.js has run.');
    }
  }

  // Render Skill Cards in their respective columns
  function renderSkills() {
    // Clear containers
    highContainer.innerHTML = '';
    mediumContainer.innerHTML = '';
    situationalContainer.innerHTML = '';
    specializedContainer.innerHTML = '';

    skillsData.forEach(skill => {
      const card = createSkillCard(skill);

      if (skill.category === 'high') {
        highContainer.appendChild(card);
      } else if (skill.category === 'medium') {
        mediumContainer.appendChild(card);
      } else if (skill.category === 'situational') {
        situationalContainer.appendChild(card);
      } else {
        specializedContainer.appendChild(card);
      }
    });
  }

  // Helper to create card element
  function createSkillCard(skill) {
    const card = document.createElement('div');
    card.className = `skill-card ${selectedSkills.has(skill.id) ? 'selected' : ''}`;
    card.setAttribute('data-id', skill.id);

    const isSelected = selectedSkills.has(skill.id);

    card.innerHTML = `
      <div class="card-top">
        <div class="skill-name">${skill.name}</div>
        <div class="skill-checkbox">
          <i class="fa-solid fa-check"></i>
        </div>
      </div>
      <div class="skill-why">${skill.why || skill.description || 'Custom developer workflow directive.'}</div>
    `;

    // Click on checkbox/top section toggles selection
    const checkbox = card.querySelector('.skill-checkbox');
    checkbox.addEventListener('click', (e) => {
      e.stopPropagation();
      toggleSkillSelection(skill.id);
    });

    // Click card body opens details in drawer
    card.addEventListener('click', () => {
      openSkillDetails(skill);
    });

    return card;
  }

  // Toggle selection
  function toggleSkillSelection(id) {
    if (selectedSkills.has(id)) {
      selectedSkills.delete(id);
    } else {
      selectedSkills.add(id);
    }

    // Update UI Card
    const cards = document.querySelectorAll(`[data-id="${id}"]`);
    cards.forEach(card => {
      if (selectedSkills.has(id)) {
        card.classList.add('selected');
      } else {
        card.classList.remove('selected');
      }
    });

    updateCompilation();
  }

  // Open Skill Inspector Drawer
  function openSkillDetails(skill) {
    currentOpenSkill = skill;
    drawerTitle.textContent = skill.name;
    
    // Setup badge class and text
    drawerBadge.className = 'drawer-badge';
    if (skill.category === 'high') {
      drawerBadge.classList.add('high');
      drawerBadge.textContent = 'High Priority (Core)';
    } else if (skill.category === 'medium') {
      drawerBadge.classList.add('medium');
      drawerBadge.textContent = 'Medium Priority';
    } else if (skill.category === 'situational') {
      drawerBadge.classList.add('situational');
      drawerBadge.textContent = 'Situational';
    } else {
      drawerBadge.classList.add('specialized');
      drawerBadge.textContent = 'Specialized / Platform';
    }

    // Render markdown content
    if (window.marked) {
      drawerMarkdown.innerHTML = marked.parse(skill.content || '# ' + skill.name + '\nNo guidelines content.');
    } else {
      drawerMarkdown.textContent = skill.content;
    }

    // Update Drawer Button State
    updateDrawerButtonState();

    // Show drawer
    drawer.classList.add('open');
    drawerBackdrop.classList.add('open');
  }

  function updateDrawerButtonState() {
    if (!currentOpenSkill) return;
    const isSelected = selectedSkills.has(currentOpenSkill.id);
    if (isSelected) {
      btnDrawerToggleSelect.innerHTML = '<i class="fa-solid fa-minus"></i> <span>Remove from Bundle</span>';
      btnDrawerToggleSelect.classList.remove('btn-primary');
      btnDrawerToggleSelect.style.backgroundColor = 'hsl(354, 85%, 25%)';
      btnDrawerToggleSelect.style.borderColor = 'hsl(354, 85%, 45%)';
    } else {
      btnDrawerToggleSelect.innerHTML = '<i class="fa-solid fa-plus"></i> <span>Add to Bundle</span>';
      btnDrawerToggleSelect.classList.add('btn-primary');
      btnDrawerToggleSelect.style.backgroundColor = '';
      btnDrawerToggleSelect.style.borderColor = '';
    }
  }

  function closeDrawer() {
    drawer.classList.remove('open');
    drawerBackdrop.classList.remove('open');
    currentOpenSkill = null;
  }

  // Update Compiled Prompt Preview
  function updateCompilation() {
    const count = selectedSkills.size;
    selectedCountBadge.textContent = `${count} selected`;

    // Reset Copy button text to match standard state
    btnCopy.innerHTML = '<i class="fa-solid fa-copy"></i> <span>Copy System rules</span>';

    if (count === 0) {
      codePreview.textContent = '# No Skills Selected\n\nPlease select one or more developer skills in the workspace columns to compile system rules.';
      compilerSummary.textContent = '0 skills selected. Bundle is empty.';
      return;
    }

    compilerSummary.textContent = `${count} skills bundled in prompt.`;

    const targetFormat = exportFormat.value;
    const compiled = compilePrompt(targetFormat);
    codePreview.textContent = compiled;
  }

  // Core Prompt Compiler Logic
  function compilePrompt(format) {
    const selectedList = skillsData.filter(s => selectedSkills.has(s.id));
    
    let result = '';

    if (format === 'cursor' || format === 'windsurf') {
      const filename = format === 'cursor' ? '.cursorrules' : '.windsurfrules';
      previewTitle.textContent = `${filename} Preview`;
      
      result += `# AI Coding Assistant Directives (${filename})\n\n`;
      result += `You are operating in a workspace configured with active developer skill workflows. Adhere strictly to the guidelines and workflows defined below for each active skill.\n\n`;
      
      result += `## Active Core Workflows\n`;
      selectedList.forEach(s => {
        result += `- **${s.name}**: ${s.why || s.description}\n`;
      });
      result += `\n`;

      result += `## Core Directives & Standards\n\n`;
      
      selectedList.forEach(s => {
        result += `### === Workflow: ${s.name} ===\n`;
        result += `${cleanMarkdownContent(s.content)}\n\n`;
      });

    } else if (format === 'claudecode') {
      previewTitle.textContent = `.clauderc Instructions`;
      
      result += `You are Claude Code, operating under specific developer engineering skills. Follow these active workflows:\n\n`;
      
      selectedList.forEach(s => {
        result += `[Skill Workflow: ${s.name}]\n`;
        result += `${cleanMarkdownContent(s.content)}\n\n`;
      });

    } else if (format === 'antigravity' || format === 'gemini') {
      previewTitle.textContent = `Unified System Instructions`;
      
      result += `You are Antigravity, a powerful agentic AI coding assistant designed by Google DeepMind.\n`;
      result += `You operate with the following core developer skills activated:\n\n`;

      selectedList.forEach(s => {
        result += `### SKILL: ${s.name}\n`;
        result += `Description: ${s.description}\n\n`;
        result += `Guidelines:\n`;
        result += `${cleanMarkdownContent(s.content)}\n\n`;
      });

    } else if (format === 'chatgpt') {
      previewTitle.textContent = `Custom Instructions Preview`;
      
      result += `Use the following guidelines for all code generation, analysis, and architecture decisions:\n\n`;
      
      selectedList.forEach(s => {
        result += `[Core Skill: ${s.name}]\n`;
        result += `${cleanMarkdownContent(s.content)}\n\n`;
      });
    }

    return result;
  }

  // Strips frontmatter, large duplicate titles, and cleans layout
  function cleanMarkdownContent(content) {
    if (!content) return '';
    let cleaned = content.trim();
    
    // Double safeguard to strip leading yaml frontmatter
    if (cleaned.startsWith('---')) {
      const parts = cleaned.split('---');
      if (parts.length >= 3) {
        cleaned = parts.slice(2).join('---').trim();
      }
    }
    
    // Remove duplicate title heading if it exists at the start
    cleaned = cleaned.replace(/^#\s+.+$/m, '').trim();
    
    return cleaned;
  }

  // Clipboard Copier
  btnCopy.addEventListener('click', async () => {
    const content = codePreview.textContent;
    if (!content || content.startsWith('# No Skills Selected')) return;
    
    try {
      await navigator.clipboard.writeText(content);
      const originalHTML = btnCopy.innerHTML;
      const isPowerShell = previewTitle.textContent.includes('PowerShell');
      const successText = isPowerShell ? 'Script Copied!' : 'Rules Copied!';
      btnCopy.innerHTML = `<i class="fa-solid fa-circle-check text-green-400"></i> <span>${successText}</span>`;
      btnCopy.style.backgroundColor = 'var(--color-success)';
      btnCopy.style.borderColor = 'var(--color-success)';
      setTimeout(() => {
        btnCopy.innerHTML = originalHTML;
        btnCopy.style.backgroundColor = '';
        btnCopy.style.borderColor = '';
      }, 2000);
    } catch (err) {
      alert('Failed to copy to clipboard. Please select the text manually.');
    }
  });

  // Download compiled rules file
  btnDownload.addEventListener('click', () => {
    const content = codePreview.textContent;
    if (!content || content.startsWith('# No Skills Selected')) return;
    
    const isPowerShell = previewTitle.textContent.includes('PowerShell');
    let filename = '';
    
    if (isPowerShell) {
      filename = 'install-skills.ps1';
    } else {
      const format = exportFormat.value;
      if (format === 'windsurf') filename = '.windsurfrules';
      else if (format === 'claudecode') filename = '.clauderc';
      else if (format === 'antigravity' || format === 'gemini') filename = 'antigravity.instructions.md';
      else if (format === 'chatgpt') filename = 'chatgpt-custom-instructions.txt';
      else filename = '.cursorrules';
    }

    const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  });

  // PowerShell Local Setup Script Generator
  btnPowerShell.addEventListener('click', () => {
    const activeList = Array.from(selectedSkills).map(id => `'${id}'`).join(', ');
    
    const psScript = `# PowerShell Skill Deployment Script for Antigravity & Gemini
# Automatically configures active plugins

$PluginDir = "$Home\\.gemini\\config\\plugins"
$SkillsTarget = "$Home\\.gemini\\config\\skills"
$ActiveSkills = @(${activeList})

Write-Host "=== AI Agent Skills local deployer ===" -ForegroundColor Green

# 1. Ensure plugin structure exists
if (!(Test-Path $PluginDir)) {
    Write-Host "Creating local plugins folder: $PluginDir"
    New-Item -ItemType Directory -Force -Path $PluginDir | Out-Null
}
if (!(Test-Path $SkillsTarget)) {
    Write-Host "Creating local skills folder: $SkillsTarget"
    New-Item -ItemType Directory -Force -Path $SkillsTarget | Out-Null
}

# 2. Sync files from current dashboard workspace
# Resolves source skills directory dynamically
$SourceSkills = "C:\\Projects\\Agentic Skills\\Agents-skills\\skills"
if (!(Test-Path $SourceSkills)) {
    $SourceSkills = Join-Path $pwd.Path "Agents-skills\\skills"
}
if (!(Test-Path $SourceSkills)) {
    $SourceSkills = Join-Path $pwd.Path "..\\Agents-skills\\skills"
}

if (!(Test-Path $SourceSkills)) {
    Write-Host "Error: Could not locate source skills folder." -ForegroundColor Red
    Write-Host "Please edit the '$SourceSkills' variable in this script to point to your cloned repository skills directory."
    Exit
}

Write-Host "Deploying selected skills to '$SkillsTarget'..." -ForegroundColor Cyan
foreach ($skill in $ActiveSkills) {
    $src = Join-Path $SourceSkills "$skill.md"
    $dest = Join-Path $SkillsTarget "$skill.md"
    if (Test-Path $src) {
        Copy-Item -Path $src -Destination $dest -Force
        Write-Host " [+] Installed skill: $skill"
    } else {
        Write-Host " [-] Warning: Skill not found in source: $skill" -ForegroundColor Yellow
    }
}

# 3. Complete
Write-Host "Active skills deployed! Please restart your IDE agent." -ForegroundColor Green
`;

    // Open ps script in a new modal or code preview
    codePreview.textContent = psScript;
    previewTitle.textContent = `PowerShell Deployer script`;
    compilerSummary.textContent = 'Copy the PowerShell script and run it in your Windows shell.';
    
    // Highlight Copy Button
    btnCopy.innerHTML = '<i class="fa-solid fa-copy"></i> <span>Copy PowerShell Script</span>';
  });

  // Select / Deselect actions
  btnSelectAll.addEventListener('click', () => {
    skillsData.forEach(s => {
      if (s.category === 'high' || s.category === 'medium') {
        selectedSkills.add(s.id);
      }
    });
    renderSkills();
    updateCompilation();
  });

  btnClearSelection.addEventListener('click', () => {
    selectedSkills.clear();
    renderSkills();
    updateCompilation();
  });

  exportFormat.addEventListener('change', () => {
    updateCompilation();
  });

  // Drawer events
  btnDrawerClose.addEventListener('click', closeDrawer);
  btnDrawerCancel.addEventListener('click', closeDrawer);
  drawerBackdrop.addEventListener('click', closeDrawer);
  
  btnDrawerToggleSelect.addEventListener('click', () => {
    if (currentOpenSkill) {
      toggleSkillSelection(currentOpenSkill.id);
      updateDrawerButtonState();
    }
  });

  // Search Input Handler
  searchInput.addEventListener('input', (e) => {
    const query = e.target.value.toLowerCase().trim();
    const cards = document.querySelectorAll('.skill-card');

    cards.forEach(card => {
      const id = card.getAttribute('data-id');
      const skill = skillsData.find(s => s.id === id);
      if (!skill) return;

      const matched = skill.name.toLowerCase().includes(query) || 
                      (skill.why && skill.why.toLowerCase().includes(query)) ||
                      (skill.content && skill.content.toLowerCase().includes(query)) ||
                      (skill.category && skill.category.toLowerCase().includes(query));

      if (matched || query === '') {
        card.style.display = 'flex';
      } else {
        card.style.display = 'none';
      }
    });
  });

  // Recommender Wizard Logic
  btnQuiz.addEventListener('click', () => {
    wizardAnswers = {};
    currentWizardStep = 1;
    document.querySelectorAll('.wizard-option').forEach(o => o.classList.remove('selected'));
    showWizardStep(1);
    wizardBackdrop.classList.add('open');
  });

  btnWizardClose.addEventListener('click', closeWizard);

  function closeWizard() {
    wizardBackdrop.classList.remove('open');
  }

  function showWizardStep(step) {
    currentWizardStep = step;
    wizardSteps.forEach(s => s.classList.remove('active'));
    document.querySelector(`.wizard-step[data-step="${step}"]`).classList.add('active');

    // Button states
    btnWizardBack.disabled = (step === 1);
    if (step === 3) {
      btnWizardNext.innerHTML = '<span>Apply Recommendations</span> <i class="fa-solid fa-circle-check text-green-400"></i>';
    } else {
      btnWizardNext.innerHTML = '<span>Next</span> <i class="fa-solid fa-arrow-right"></i>';
    }

    // Highlight selected options
    const options = document.querySelectorAll(`.wizard-step[data-step="${step}"] .wizard-option`);
    options.forEach(opt => {
      const val = opt.getAttribute('data-value');
      if (wizardAnswers[step] === val) {
        opt.classList.add('selected');
      } else {
        opt.classList.remove('selected');
      }
    });
  }

  // Handle option select inside wizard
  document.querySelectorAll('.wizard-option').forEach(opt => {
    opt.addEventListener('click', () => {
      const parentStep = opt.closest('.wizard-step');
      const stepNum = parseInt(parentStep.getAttribute('data-step'));
      const val = opt.getAttribute('data-value');

      wizardAnswers[stepNum] = val;

      // Unselect others on this step
      parentStep.querySelectorAll('.wizard-option').forEach(o => o.classList.remove('selected'));
      opt.classList.add('selected');
    });
  });

  btnWizardNext.addEventListener('click', () => {
    // Validate that option is selected
    if (!wizardAnswers[currentWizardStep]) {
      alert('Please select an option to proceed.');
      return;
    }

    if (currentWizardStep < 3) {
      showWizardStep(currentWizardStep + 1);
    } else {
      // Compile & Apply recommended skills!
      applyWizardRecommendations();
      closeWizard();
    }
  });

  btnWizardBack.addEventListener('click', () => {
    if (currentWizardStep > 1) {
      showWizardStep(currentWizardStep - 1);
    }
  });

  function applyWizardRecommendations() {
    selectedSkills.clear();
    
    // Core foundational skills are always added
    selectedSkills.add('git-workflow-and-versioning');
    selectedSkills.add('debugging-and-error-recovery');

    const projectType = wizardAnswers[1];
    const techStack = wizardAnswers[2];
    const challenge = wizardAnswers[3];

    // Recommendations based on Project Type
    if (projectType === 'production') {
      selectedSkills.add('security-and-hardening');
      selectedSkills.add('doubt-driven-development');
      selectedSkills.add('observability-and-instrumentation');
      selectedSkills.add('shipping-and-launch');
      selectedSkills.add('ci-cd-and-automation');
    } else if (projectType === 'standard') {
      selectedSkills.add('test-driven-development');
      selectedSkills.add('code-review-and-quality');
      selectedSkills.add('spec-driven-development');
    } else if (projectType === 'prototype') {
      selectedSkills.add('incremental-implementation');
      selectedSkills.add('no-excuses-executor');
    }

    // Recommendations based on Tech Stack
    if (techStack === 'web') {
      selectedSkills.add('browser-testing-with-devtools');
      selectedSkills.add('a11y-debugging');
      selectedSkills.add('frontend-ui-engineering');
      selectedSkills.add('performance-optimization');
    } else if (techStack === 'backend') {
      selectedSkills.add('api-and-interface-design');
      selectedSkills.add('observability-and-instrumentation');
      // Suggest databases
      selectedSkills.add('supabase');
      selectedSkills.add('mongodb');
    } else if (techStack === 'mobile') {
      selectedSkills.add('android-cli');
      selectedSkills.add('xcode-project-setup');
    }

    // Recommendations based on challenges
    if (challenge === 'quality') {
      selectedSkills.add('doubt-driven-development');
      selectedSkills.add('test-driven-development');
      selectedSkills.add('code-review-and-quality');
      selectedSkills.add('source-driven-development');
    } else if (challenge === 'planning') {
      selectedSkills.add('spec-driven-development');
      selectedSkills.add('planning-and-task-breakdown');
      selectedSkills.add('context-engineering');
    } else if (challenge === 'speed') {
      selectedSkills.add('incremental-implementation');
      selectedSkills.add('no-excuses-executor');
      selectedSkills.add('uv');
    }

    renderSkills();
    updateCompilation();
    
    // Highlight panel
    const count = selectedSkills.size;
    alert(`Recommended ${count} skills optimized for your workspace! Review the preview on the right side of the dashboard.`);
  }

  // Run initialization
  loadSkills();
});
