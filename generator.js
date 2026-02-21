(function () {
  'use strict';

  let patterns = null;
  let currentStep = 1;
  let generatedMd = '';

  // ── Bootstrap ──────────────────────────────────────────────────────────────
  document.addEventListener('DOMContentLoaded', function () {
    loadPatterns();
    bindNavigation();
    bindFormEvents();
  });

  // ── Data loading ───────────────────────────────────────────────────────────
  function loadPatterns() {
    fetch('patterns.json')
      .then(function (r) { return r.json(); })
      .then(function (data) {
        patterns = data;
        var m = data.metadata;
        document.getElementById('header-stats').innerHTML =
          'Built from scanning <strong>' + m.source_repos + '</strong> public repos with <strong>' + m.active_workflows + '</strong> active workflows';
      })
      .catch(function () {
        document.getElementById('header-stats').textContent = 'Patterns data unavailable';
      });
  }

  function getArchetype(id) {
    if (!patterns) return null;
    for (var i = 0; i < patterns.archetypes.length; i++) {
      if (patterns.archetypes[i].id === id) return patterns.archetypes[i];
    }
    return null;
  }

  // ── Navigation ─────────────────────────────────────────────────────────────
  function bindNavigation() {
    document.getElementById('next-1').addEventListener('click', function () { goToStep(2); });
    document.getElementById('next-2').addEventListener('click', function () { goToStep(3); });
    document.getElementById('next-3').addEventListener('click', function () { goToStep(4); });
    document.getElementById('next-4').addEventListener('click', function () { generateAndShow(); });
    document.getElementById('prev-2').addEventListener('click', function () { goToStep(1); });
    document.getElementById('prev-3').addEventListener('click', function () { goToStep(2); });
    document.getElementById('prev-4').addEventListener('click', function () { goToStep(3); });
    document.getElementById('prev-5').addEventListener('click', function () { goToStep(4); });

    document.getElementById('btn-copy').addEventListener('click', copyToClipboard);
    document.getElementById('btn-download').addEventListener('click', downloadFile);

    // Clickable progress steps
    var steps = document.querySelectorAll('.progress-step');
    steps.forEach(function (el) {
      el.addEventListener('click', function () {
        var target = parseInt(el.getAttribute('data-step'));
        if (target < currentStep) goToStep(target);
      });
    });
  }

  function goToStep(n) {
    // Hide current
    document.getElementById('step-' + currentStep).classList.remove('active');
    // Update progress
    updateProgress(currentStep, n);
    currentStep = n;
    document.getElementById('step-' + n).classList.add('active');
  }

  function updateProgress(from, to) {
    var steps = document.querySelectorAll('.progress-step');
    steps.forEach(function (el) {
      var s = parseInt(el.getAttribute('data-step'));
      el.classList.remove('active', 'completed');
      if (s < to) el.classList.add('completed');
      else if (s === to) el.classList.add('active');
    });
    // Update checkmarks
    steps.forEach(function (el) {
      var ind = el.querySelector('.step-indicator');
      var s = parseInt(el.getAttribute('data-step'));
      ind.textContent = el.classList.contains('completed') ? '✓' : s;
    });
  }

  // ── Form events ────────────────────────────────────────────────────────────
  function bindFormEvents() {
    // Step 1: archetype radios
    document.querySelectorAll('input[name="archetype"]').forEach(function (radio) {
      radio.addEventListener('change', function () {
        updateCardSelection('#archetype-options', 'radio');
        document.getElementById('next-1').disabled = false;
        var customField = document.getElementById('custom-description-field');
        customField.classList.toggle('visible', radio.value === 'custom');
        // Auto-fill triggers/outputs from archetype data
        prefillFromArchetype(radio.value);
      });
    });

    // Step 2: trigger checkboxes
    document.querySelectorAll('input[name="trigger"]').forEach(function (cb) {
      cb.addEventListener('change', function () {
        updateCardSelection('#trigger-options', 'checkbox');
        document.getElementById('next-2').disabled = !hasChecked('trigger');
      });
    });

    // Step 3: output checkboxes
    document.querySelectorAll('input[name="output"]').forEach(function (cb) {
      cb.addEventListener('change', function () {
        updateCardSelection('#output-options', 'checkbox');
        document.getElementById('next-3').disabled = !hasChecked('output');
      });
    });

    // Step 4: data radios
    document.querySelectorAll('input[name="needs-data"]').forEach(function (radio) {
      radio.addEventListener('change', function () {
        updateCardSelection('#data-options', 'radio');
        document.getElementById('next-4').disabled = false;
        document.getElementById('data-description-field').classList.toggle('visible', radio.value === 'yes');
      });
    });
  }

  function updateCardSelection(containerSel, type) {
    var cards = document.querySelectorAll(containerSel + ' .option-card');
    cards.forEach(function (card) {
      var input = card.querySelector('input');
      card.classList.toggle('selected', input.checked);
    });
  }

  function hasChecked(name) {
    return document.querySelectorAll('input[name="' + name + '"]:checked').length > 0;
  }

  function prefillFromArchetype(id) {
    var arch = getArchetype(id);
    if (!arch) return;

    // Pre-check recommended triggers
    document.querySelectorAll('input[name="trigger"]').forEach(function (cb) { cb.checked = false; });
    if (arch.recommended_triggers) {
      arch.recommended_triggers.forEach(function (t) {
        var cb = document.querySelector('input[name="trigger"][value="' + t.type + '"]');
        if (cb) cb.checked = true;
      });
    }
    updateCardSelection('#trigger-options', 'checkbox');
    document.getElementById('next-2').disabled = !hasChecked('trigger');

    // Pre-check recommended outputs
    var outputMap = {
      'issues': ['comments', 'labels', 'new-issues'],
      'pull-requests': ['pull-requests', 'comments'],
      'contents': ['commits']
    };
    document.querySelectorAll('input[name="output"]').forEach(function (cb) { cb.checked = false; });
    if (arch.recommended_safe_outputs) {
      arch.recommended_safe_outputs.forEach(function (so) {
        var vals = outputMap[so] || [];
        vals.forEach(function (v) {
          var cb = document.querySelector('input[name="output"][value="' + v + '"]');
          if (cb) cb.checked = true;
        });
      });
    }
    updateCardSelection('#output-options', 'checkbox');
    document.getElementById('next-3').disabled = !hasChecked('output');

    // Pre-select data need
    var needsData = (id === 'dependency-monitor' || id === 'status-report') ? 'yes' : 'no';
    var dataRadio = document.querySelector('input[name="needs-data"][value="' + needsData + '"]');
    if (dataRadio) {
      dataRadio.checked = true;
      updateCardSelection('#data-options', 'radio');
      document.getElementById('next-4').disabled = false;
      document.getElementById('data-description-field').classList.toggle('visible', needsData === 'yes');
    }
  }

  // ── Gather answers ─────────────────────────────────────────────────────────
  function gatherAnswers() {
    var arch = document.querySelector('input[name="archetype"]:checked');
    var triggers = [];
    document.querySelectorAll('input[name="trigger"]:checked').forEach(function (cb) { triggers.push(cb.value); });
    var outputs = [];
    document.querySelectorAll('input[name="output"]:checked').forEach(function (cb) { outputs.push(cb.value); });
    var needsData = document.querySelector('input[name="needs-data"]:checked');

    return {
      archetype: arch ? arch.value : 'custom',
      customDescription: document.getElementById('custom-description').value.trim(),
      triggers: triggers,
      outputs: outputs,
      needsData: needsData ? needsData.value === 'yes' : false,
      dataDescription: document.getElementById('data-description').value.trim()
    };
  }

  // ── Generate prompt ────────────────────────────────────────────────────────
  function generateAndShow() {
    var answers = gatherAnswers();
    generatedMd = generatePrompt(answers);
    goToStep(5);
    showPreview(generatedMd);
    showTips(answers.archetype);
    var name = workflowName(answers.archetype, answers.customDescription);
    document.getElementById('preview-filename').textContent = name + '.md';
  }

  function workflowName(archetype, customDesc) {
    if (archetype === 'custom' && customDesc) {
      return customDesc.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '').slice(0, 40) || 'custom-workflow';
    }
    return archetype;
  }

  function generatePrompt(answers) {
    var arch = getArchetype(answers.archetype);
    var name = workflowName(answers.archetype, answers.customDescription);
    var label = arch ? arch.label : 'Custom Workflow';
    var desc = arch ? arch.description : answers.customDescription || 'Custom agentic workflow';

    // Build tools and safe-outputs
    var toolSet = new Set();
    var safeSet = new Set();
    answers.outputs.forEach(function (o) {
      switch (o) {
        case 'comments':
          toolSet.add('add-comment'); safeSet.add('issues'); safeSet.add('pull-requests'); break;
        case 'labels':
          toolSet.add('add-label'); safeSet.add('issues'); break;
        case 'new-issues':
          toolSet.add('create-issue'); safeSet.add('issues'); break;
        case 'pull-requests':
          toolSet.add('create-pull-request'); safeSet.add('pull-requests'); break;
        case 'commits':
          toolSet.add('commit-files'); safeSet.add('contents'); break;
      }
    });
    var tools = Array.from(toolSet);
    var safeOutputs = Array.from(safeSet);

    // Timeout
    var timeout = (arch && arch.timeout_minutes) ? arch.timeout_minutes : 30;
    if (patterns && patterns.config_defaults && patterns.config_defaults.timeout_by_trigger) {
      answers.triggers.forEach(function (t) {
        var val = patterns.config_defaults.timeout_by_trigger[t];
        if (val && val > timeout) timeout = val;
      });
    }

    // Trigger config YAML
    var triggerYaml = buildTriggerYaml(answers.triggers);

    // Frontmatter
    var fm = '---\n';
    fm += 'name: ' + name + '\n';
    fm += 'description: ' + desc + '\n';
    fm += 'on:\n' + triggerYaml;
    fm += 'tools:\n';
    tools.forEach(function (t) { fm += '  - ' + t + '\n'; });
    fm += 'safe-outputs:\n';
    safeOutputs.forEach(function (s) { fm += '  - ' + s + '\n'; });
    fm += 'timeout-minutes: ' + timeout + '\n';
    fm += '---\n\n';

    // Body — varies by archetype
    var body = '';
    switch (answers.archetype) {
      case 'issue-triage':
        body = buildIssueTriage(answers, label);
        break;
      case 'code-improvement':
        body = buildCodeImprovement(answers, label);
        break;
      case 'status-report':
        body = buildStatusReport(answers, label);
        break;
      case 'dependency-monitor':
        body = buildDependencyMonitor(answers, label);
        break;
      case 'content-moderation':
        body = buildContentModeration(answers, label);
        break;
      default:
        body = buildCustom(answers, label);
    }

    return fm + body;
  }

  function buildTriggerYaml(triggers) {
    var lines = '';
    triggers.forEach(function (t) {
      switch (t) {
        case 'issues':
          lines += '  issues:\n    types: [opened]\n'; break;
        case 'pull_request':
          lines += '  pull_request:\n    types: [opened]\n'; break;
        case 'schedule':
          lines += '  schedule:\n    - cron: "0 9 * * 1-5"\n'; break;
        case 'workflow_dispatch':
          lines += '  workflow_dispatch:\n'; break;
        case 'issue_comment':
          lines += '  issue_comment:\n    types: [created]\n'; break;
        case 'push':
          lines += '  push:\n    branches: [main]\n'; break;
      }
    });
    return lines;
  }

  // ── Archetype body builders ────────────────────────────────────────────────
  function preStepsBlock(answers) {
    if (!answers.needsData) return '';
    var desc = answers.dataDescription || 'the required external data';
    return '## Pre-steps\n\nBefore starting, gather the following information:\n\n' +
      '1. **Fetch external data**: ' + desc + '\n' +
      '2. **Validate** that the fetched data is complete and well-formed\n' +
      '3. **Store** the results for use in the steps below\n\n';
  }

  function buildIssueTriage(answers, label) {
    return '# ' + label + '\n\n' +
      'You are an **issue triage specialist** for this repository.\n\n' +
      'Your job is to read every newly opened issue, classify it, apply the correct labels, and post a helpful comment.\n\n' +
      preStepsBlock(answers) +
      '## Instructions\n\n' +
      '1. **Read** the issue title and body carefully\n' +
      '2. **Classify** the issue into one of these categories:\n' +
      '   - `bug` — Something is broken or not working as expected\n' +
      '   - `feature` — A request for new functionality\n' +
      '   - `question` — A question about usage or behavior\n' +
      '   - `docs` — Documentation improvement needed\n' +
      '   - `chore` — Maintenance, refactoring, or infrastructure\n' +
      '3. **Apply** the appropriate label(s) to the issue\n' +
      '4. **Comment** on the issue with:\n' +
      '   - A brief acknowledgment\n' +
      '   - The classification you chose and why\n' +
      '   - Any initial guidance or next steps for the author\n\n' +
      '## Rules\n\n' +
      '- Only apply labels that already exist in the repository. Do not create new labels.\n' +
      '- If the issue is unclear or ambiguous, apply a `needs-triage` label and ask the author for clarification.\n' +
      '- Do not attempt to fix the issue or write code. Your job is classification only.\n' +
      '- Be polite and professional in your comments.\n' +
      '- If the issue is a duplicate, note it in your comment but do not close the issue.\n';
  }

  function buildCodeImprovement(answers, label) {
    return '# ' + label + '\n\n' +
      'You are a **code quality engineer** for this repository.\n\n' +
      'Your job is to find one targeted improvement, implement it, validate it, and open a pull request.\n\n' +
      preStepsBlock(answers) +
      '## Phase 1: Analyze\n\n' +
      '1. Scan the codebase for one of these improvement opportunities (pick only one per run):\n' +
      '   - Missing or incomplete test coverage\n' +
      '   - Code that can be simplified or deduplicated\n' +
      '   - Outdated or missing documentation\n' +
      '   - Type safety improvements\n' +
      '2. Choose the single highest-impact improvement you can make\n' +
      '3. Write a brief analysis of what you found and why it matters\n\n' +
      '## Phase 2: Plan\n\n' +
      '1. List the specific files you will modify\n' +
      '2. Describe the exact changes you will make\n' +
      '3. Identify any risks or dependencies\n\n' +
      '## Phase 3: Implement\n\n' +
      '1. Make the changes described in your plan\n' +
      '2. Keep changes minimal and focused — one improvement per PR\n' +
      '3. Follow the existing code style and conventions\n\n' +
      '## Phase 4: Validate\n\n' +
      '1. Verify that existing tests still pass\n' +
      '2. If you added tests, verify they pass\n' +
      '3. Review your own changes for correctness\n\n' +
      '## Rules\n\n' +
      '- One improvement per run. Do not try to fix everything at once.\n' +
      '- Do not change functionality — only improve quality.\n' +
      '- Do not modify generated files, vendored code, or lock files.\n' +
      '- If you cannot find a meaningful improvement, do nothing. Do not create empty PRs.\n' +
      '- PR title must start with the type of improvement: `test:`, `refactor:`, `docs:`, or `types:`.\n';
  }

  function buildStatusReport(answers, label) {
    return '# ' + label + '\n\n' +
      'You are a **project status reporter** for this repository.\n\n' +
      'Your job is to gather activity data and produce a formatted status report as a new issue.\n\n' +
      preStepsBlock(answers) +
      '## Instructions\n\n' +
      '1. **Gather data** for the reporting period (since last report or last 7 days):\n' +
      '   - New issues opened and closed\n' +
      '   - Pull requests opened, merged, and closed\n' +
      '   - Notable commits or releases\n' +
      '   - Active contributors\n' +
      '2. **Generate** the report using the template below\n' +
      '3. **Create** a new issue with the report\n\n' +
      '## Report Template\n\n' +
      'Use this exact format for the report issue:\n\n' +
      '```\n' +
      '## 📊 Weekly Status Report — {date range}\n\n' +
      '### Summary\n' +
      '{2-3 sentence overview of the week}\n\n' +
      '### Issues\n' +
      '- Opened: {count}\n' +
      '- Closed: {count}\n' +
      '- Net change: {+/- count}\n\n' +
      '### Pull Requests\n' +
      '- Opened: {count}\n' +
      '- Merged: {count}\n' +
      '- Closed without merge: {count}\n\n' +
      '### Highlights\n' +
      '- {notable item 1}\n' +
      '- {notable item 2}\n\n' +
      '### Active Contributors\n' +
      '{list of contributors with activity}\n' +
      '```\n\n' +
      '## Rules\n\n' +
      '- Stick to facts. Do not editorialize or make recommendations.\n' +
      '- Use the exact template format above for consistency.\n' +
      '- If there is no activity to report, create a brief report noting that.\n' +
      '- Label the report issue with `status-report`.\n';
  }

  function buildDependencyMonitor(answers, label) {
    return '# ' + label + '\n\n' +
      'You are a **dependency monitor** for this repository.\n\n' +
      'Your job is to check for upstream changes in key dependencies and flag anything that needs attention.\n\n' +
      preStepsBlock(answers) +
      '## Checklist\n\n' +
      'For each monitored dependency, perform these checks:\n\n' +
      '- [ ] **Check latest version**: Compare the currently used version with the latest available release\n' +
      '- [ ] **Review changelog**: Read the changelog or release notes for any new versions\n' +
      '- [ ] **Identify breaking changes**: Flag any breaking changes that could affect this repository\n' +
      '- [ ] **Check security advisories**: Look for any security vulnerabilities in current versions\n' +
      '- [ ] **Assess urgency**: Determine if an update is critical, recommended, or optional\n\n' +
      '## Output\n\n' +
      'If updates are found:\n\n' +
      '1. Create an issue summarizing the findings with a table:\n' +
      '   | Dependency | Current | Latest | Breaking? | Urgency |\n' +
      '   |------------|---------|--------|-----------|---------|\n' +
      '   | {name}     | {ver}   | {ver}  | Yes/No    | {level} |\n\n' +
      '2. If the update is straightforward, open a PR with the version bump\n\n' +
      '## Rules\n\n' +
      '- Do not auto-merge or auto-approve dependency updates.\n' +
      '- Only create a PR for non-breaking, patch-level updates.\n' +
      '- For major version updates, create an issue only — let humans decide.\n' +
      '- If no updates are available, do nothing. Do not create empty reports.\n';
  }

  function buildContentModeration(answers, label) {
    return '# ' + label + '\n\n' +
      'You are a **content moderator** for this repository.\n\n' +
      'Your job is to review new issues and pull requests for spam, abuse, or policy violations.\n\n' +
      preStepsBlock(answers) +
      '## Instructions\n\n' +
      '1. **Read** the issue or PR title, body, and any attached content\n' +
      '2. **Evaluate** against the rules below\n' +
      '3. **Take action** based on your evaluation\n\n' +
      '## Rules for Classification\n\n' +
      '### Spam indicators (flag as `spam`):\n' +
      '- Promotional content unrelated to the project\n' +
      '- Mass-posted identical content across repos\n' +
      '- Links to suspicious or unrelated external sites\n' +
      '- Bot-generated nonsense text\n\n' +
      '### Policy violations (flag as `policy-violation`):\n' +
      '- Abusive, harassing, or threatening language directed at contributors\n' +
      '- Content that violates the project\'s code of conduct\n' +
      '- Deliberately misleading or malicious content\n\n' +
      '### Legitimate content:\n' +
      '- Bug reports, feature requests, and questions — even if poorly written\n' +
      '- Content in non-English languages (do not flag for language)\n' +
      '- Beginner questions or first-time contributions\n\n' +
      '## Actions\n\n' +
      '- **If spam**: Apply `spam` label and comment explaining why it was flagged\n' +
      '- **If policy violation**: Apply `policy-violation` label and comment with a link to the code of conduct\n' +
      '- **If legitimate**: Do nothing — no comment, no label\n\n' +
      '## Rules\n\n' +
      '- **Never** close or lock an issue/PR. Only label and comment.\n' +
      '- When in doubt, err on the side of legitimate. False positives are worse than false negatives.\n' +
      '- Be factual in your comments. Do not be accusatory.\n' +
      '- Include specific evidence for why content was flagged.\n';
  }

  function buildCustom(answers, label) {
    var desc = answers.customDescription || 'Perform the specified task on this repository.';
    return '# Custom Workflow\n\n' +
      'You are an **automated assistant** for this repository.\n\n' +
      'Your job is: ' + desc + '\n\n' +
      preStepsBlock(answers) +
      '## Instructions\n\n' +
      '1. **Understand** the context from the triggering event\n' +
      '2. **Analyze** what needs to be done based on the description above\n' +
      '3. **Execute** the task using the tools available to you\n' +
      '4. **Report** the results by commenting on the relevant issue or PR\n\n' +
      '## Rules\n\n' +
      '- Stay focused on the specific task described above. Do not go beyond scope.\n' +
      '- If the task cannot be completed, comment explaining why.\n' +
      '- Be conservative — it is better to do less and be correct than to do more and break things.\n' +
      '- Follow existing code conventions and project standards.\n';
  }

  // ── Preview rendering ──────────────────────────────────────────────────────
  function showPreview(md) {
    var el = document.getElementById('preview-code');
    el.innerHTML = highlightMarkdown(md);
  }

  function highlightMarkdown(md) {
    var lines = md.split('\n');
    var inFrontmatter = false;
    var result = [];

    for (var i = 0; i < lines.length; i++) {
      var line = lines[i];
      var escaped = escapeHtml(line);

      if (line === '---' && (i === 0 || inFrontmatter)) {
        inFrontmatter = !inFrontmatter;
        result.push('<span class="yaml-delim">' + escaped + '</span>');
        continue;
      }

      if (inFrontmatter) {
        result.push(highlightYamlLine(escaped));
      } else if (/^#{1,6}\s/.test(line)) {
        result.push('<span class="md-heading">' + escaped + '</span>');
      } else if (/^\d+\.\s/.test(line)) {
        var num = escaped.match(/^(\d+\.)/)[1];
        result.push('<span class="md-number">' + num + '</span>' + escaped.slice(num.length));
      } else if (/^[-*]\s/.test(line) || /^\s+[-*]\s/.test(line)) {
        result.push('<span class="md-list">' + escaped + '</span>');
      } else {
        // Bold markers
        result.push(escaped.replace(/\*\*([^*]+)\*\*/g, '<span class="md-bold">**$1**</span>'));
      }
    }
    return result.join('\n');
  }

  function highlightYamlLine(escaped) {
    var match = escaped.match(/^(\s*)([\w-]+)(:)(.*)/);
    if (match) {
      return match[1] +
        '<span class="yaml-key">' + match[2] + '</span>' +
        '<span class="yaml-delim">' + match[3] + '</span>' +
        '<span class="yaml-value">' + match[4] + '</span>';
    }
    // List items in frontmatter
    if (/^\s*-\s/.test(escaped)) {
      return '<span class="yaml-value">' + escaped + '</span>';
    }
    return escaped;
  }

  function escapeHtml(str) {
    return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  }

  // ── Tips ───────────────────────────────────────────────────────────────────
  function showTips(archetypeId) {
    var panel = document.getElementById('tips-panel');
    var arch = getArchetype(archetypeId);
    if (!arch) {
      panel.innerHTML = '';
      return;
    }

    var html = '<h3>Tips for ' + arch.label + '</h3>';

    // Success rate badge
    if (arch.success_rate !== null) {
      var rate = Math.round(arch.success_rate * 100);
      var level = rate >= 75 ? 'high' : (rate >= 50 ? 'medium' : 'low');
      html += '<div class="success-badge ' + level + '">' +
        (level === 'high' ? '✓' : level === 'medium' ? '~' : '✗') +
        ' ' + rate + '% success rate across public repos</div>';
    }

    // Tips
    if (arch.tips && arch.tips.length) {
      arch.tips.forEach(function (tip) {
        html += '<div class="tip-item good"><span class="tip-icon">✓</span> ' + escapeHtml(tip) + '</div>';
      });
    }

    // Anti-patterns
    if (arch.anti_patterns && arch.anti_patterns.length) {
      arch.anti_patterns.forEach(function (ap) {
        html += '<div class="tip-item warn"><span class="tip-icon">⚠</span> ' + escapeHtml(ap) + '</div>';
      });
    }

    // Global anti-pattern warnings
    if (patterns && patterns.anti_patterns) {
      var relevant = patterns.anti_patterns.filter(function (ap) {
        if (archetypeId === 'code-improvement' && ap.pattern === 'pr-fix') return true;
        if (ap.pattern === 'over-ambitious-scope') return true;
        return false;
      });
      relevant.forEach(function (ap) {
        var rate = ap.success_rate !== null ? ' (' + Math.round(ap.success_rate * 100) + '% success rate)' : '';
        html += '<div class="tip-item bad"><span class="tip-icon">✗</span> Anti-pattern: ' +
          escapeHtml(ap.reason) + rate + '</div>';
      });
    }

    panel.innerHTML = html;
  }

  // ── Clipboard & download ───────────────────────────────────────────────────
  function copyToClipboard() {
    navigator.clipboard.writeText(generatedMd).then(function () {
      showToast('Copied to clipboard!');
    }).catch(function () {
      // Fallback
      var ta = document.createElement('textarea');
      ta.value = generatedMd;
      ta.style.position = 'fixed';
      ta.style.opacity = '0';
      document.body.appendChild(ta);
      ta.select();
      document.execCommand('copy');
      document.body.removeChild(ta);
      showToast('Copied to clipboard!');
    });
  }

  function downloadFile() {
    var answers = gatherAnswers();
    var name = workflowName(answers.archetype, answers.customDescription);
    var blob = new Blob([generatedMd], { type: 'text/markdown' });
    var url = URL.createObjectURL(blob);
    var a = document.createElement('a');
    a.href = url;
    a.download = name + '.md';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    showToast('Downloaded ' + name + '.md');
  }

  function showToast(msg) {
    var toast = document.getElementById('toast');
    toast.textContent = msg;
    toast.classList.add('show');
    setTimeout(function () { toast.classList.remove('show'); }, 2500);
  }
})();
