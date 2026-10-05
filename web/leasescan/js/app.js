// LeaseScan — Main Application Logic

import { scanLease } from './scanner.js';
import { isAIAvailable, aiEnhance } from './ai.js';

// ── State ──────────────────────────────────────────────────────────────────────
let currentProvince = 'ontario';
let aiAvailable = false;

// ── Init ───────────────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', async () => {
  setupProvinceSelector();
  setupTextarea();
  setupScanButton();
  setupResultActions();

  aiAvailable = await isAIAvailable();
  if (aiAvailable) {
    document.getElementById('ai-badge').hidden = false;
  }
});

// ── Province Selector ─────────────────────────────────────────────────────────
function setupProvinceSelector() {
  const buttons = document.querySelectorAll('.province-btn');
  buttons.forEach((btn) => {
    btn.addEventListener('click', () => {
      buttons.forEach((b) => { b.classList.remove('active'); b.setAttribute('aria-pressed', 'false'); });
      btn.classList.add('active');
      btn.setAttribute('aria-pressed', 'true');
      currentProvince = btn.dataset.province;
      updateProvinceHint();
      hideResults();
    });
  });
  updateProvinceHint();
}

function updateProvinceHint() {
  const hints = {
    ontario:
      'Ontario rules loaded — includes Bill 60 (2025) updates. Covers the Residential Tenancies Act, 2006.',
    bc: 'BC rules loaded — covers the Residential Tenancy Act (RSBC 2002).',
    alberta: 'Alberta rules loaded — covers the Residential Tenancies Act (RSA 2000). Note: no rent control in AB.',
  };
  const el = document.getElementById('province-hint');
  if (el) el.textContent = hints[currentProvince] ?? '';
}

// ── Textarea ──────────────────────────────────────────────────────────────────
function setupTextarea() {
  const textarea = document.getElementById('lease-input');
  const counter = document.getElementById('word-count');

  textarea.addEventListener('input', () => {
    const words = textarea.value.trim().split(/\s+/).filter(Boolean).length;
    counter.textContent = words > 0 ? `${words.toLocaleString()} words` : '';
    hideResults();
  });

  // Allow pasting via the paste button
  const pasteBtn = document.getElementById('paste-btn');
  if (pasteBtn && navigator.clipboard?.readText) {
    pasteBtn.hidden = false;
    pasteBtn.addEventListener('click', async () => {
      try {
        const text = await navigator.clipboard.readText();
        textarea.value = text;
        textarea.dispatchEvent(new Event('input'));
      } catch {
        pasteBtn.textContent = 'Paste not available — use Ctrl+V';
      }
    });
  }

  // Clear button
  document.getElementById('clear-btn').addEventListener('click', () => {
    textarea.value = '';
    counter.textContent = '';
    hideResults();
    textarea.focus();
  });
}

// ── Scan Button ────────────────────────────────────────────────────────────────
function setupScanButton() {
  document.getElementById('scan-btn').addEventListener('click', runScan);
}

async function runScan() {
  const textarea = document.getElementById('lease-input');
  const text = textarea.value.trim();

  if (text.length < 100) {
    showError('Please paste your lease text (at least a few paragraphs) before scanning.');
    return;
  }

  setLoading(true);
  hideResults();
  clearError();

  try {
    // Small async tick so the loading UI paints before the (sync) scan runs
    await tick();
    const result = scanLease(text, currentProvince);

    renderResults(result);

    // AI enhancement (non-blocking, appended when ready)
    if (aiAvailable) {
      renderAILoading();
      const aiText = await aiEnhance(text, result);
      renderAIResult(aiText);
    }
  } catch (err) {
    console.error('[LeaseScan] Scan error:', err);
    showError('Something went wrong during the scan. Please try again.');
  } finally {
    setLoading(false);
  }
}

// ── Rendering ─────────────────────────────────────────────────────────────────
function renderResults(result) {
  const section = document.getElementById('results-section');
  section.hidden = false;
  section.scrollIntoView({ behavior: 'smooth', block: 'start' });

  // Summary card
  renderSummary(result);

  // Flag cards
  const container = document.getElementById('flags-container');
  container.innerHTML = '';

  if (result.flags.length === 0) {
    container.innerHTML = `
      <div class="clean-card">
        <div class="clean-icon">✓</div>
        <h3>No red flags detected</h3>
        <p>Our rules-based scan found no common problematic clauses in your lease.
        This doesn't mean every clause is fair — always read the full lease carefully
        and consider consulting a tenant rights clinic before signing.</p>
      </div>`;
    return;
  }

  // Group by category for display
  const byCategory = {};
  for (const flag of result.flags) {
    (byCategory[flag.category] ??= []).push(flag);
  }

  for (const [category, flags] of Object.entries(byCategory)) {
    const section = document.createElement('div');
    section.className = 'flag-category';
    section.innerHTML = `<h3 class="category-heading">${escHtml(category)}</h3>`;

    for (const flag of flags) {
      section.appendChild(buildFlagCard(flag));
    }

    container.appendChild(section);
  }

  // Store result for export
  window.__leaseScanResult = result;
}

function renderSummary(result) {
  const { summary, province, legislation, legalAidUrl, wordCount } = result;

  const verdictClass = {
    serious: 'verdict-serious',
    concerns: 'verdict-concerns',
    minor: 'verdict-minor',
    clean: 'verdict-clean',
  }[summary.verdict];

  document.getElementById('summary-card').innerHTML = `
    <div class="summary-header ${verdictClass}">
      <div class="summary-verdict">
        <span class="verdict-icon">${verdictIcon(summary.verdict)}</span>
        <span class="verdict-label">${verdictLabel(summary.verdict)}</span>
      </div>
      <p class="verdict-text">${escHtml(summary.verdictText)}</p>
    </div>
    <div class="summary-stats">
      <div class="stat-item">
        <span class="stat-number stat-total">${summary.total}</span>
        <span class="stat-label">Total Flags</span>
      </div>
      <div class="stat-item">
        <span class="stat-number stat-high">${summary.high}</span>
        <span class="stat-label">High Risk</span>
      </div>
      <div class="stat-item">
        <span class="stat-number stat-medium">${summary.medium}</span>
        <span class="stat-label">Medium Risk</span>
      </div>
      <div class="stat-item">
        <span class="stat-number stat-low">${summary.low}</span>
        <span class="stat-label">Notes</span>
      </div>
      <div class="stat-item">
        <span class="stat-number stat-words">${wordCount.toLocaleString()}</span>
        <span class="stat-label">Words Scanned</span>
      </div>
    </div>
    <div class="summary-meta">
      <span>Province: <strong>${escHtml(province)}</strong></span>
      <span>Legislation: <strong>${escHtml(legislation)}</strong></span>
      <a href="${escHtml(legalAidUrl)}" target="_blank" rel="noopener noreferrer" class="ltb-link">
        Official Tenancy Board ↗
      </a>
    </div>`;
}

function buildFlagCard(flag) {
  const card = document.createElement('div');
  card.className = `flag-card flag-${flag.severity}`;

  const matchHtml = flag.matches
    .map(
      (m) => `
      <blockquote class="match-quote">
        <span class="match-highlight">${escHtml(m.matchedText)}</span>
        <span class="match-context">${escHtml(m.context)}</span>
      </blockquote>`
    )
    .join('');

  const bill60Badge = flag.isBill60
    ? `<span class="bill60-badge">Bill 60 (2025)</span>`
    : '';

  card.innerHTML = `
    <div class="flag-header">
      <div class="flag-title-row">
        <span class="severity-badge severity-${flag.severity}">${severityLabel(flag.severity)}</span>
        ${bill60Badge}
        <h4 class="flag-title">${escHtml(flag.title)}</h4>
      </div>
    </div>
    <div class="flag-body">
      <div class="flag-description">
        <strong>What this means:</strong> ${escHtml(flag.description)}
      </div>
      ${matchHtml}
      <div class="flag-legislation">
        <span class="legislation-icon">⚖</span>
        <strong>Legal reference:</strong> ${escHtml(flag.legislation)}
      </div>
      <div class="flag-recommendation">
        <span class="rec-icon">→</span>
        <strong>What to do:</strong> ${escHtml(flag.recommendation)}
      </div>
    </div>`;

  return card;
}

function renderAILoading() {
  const container = document.getElementById('ai-section');
  container.hidden = false;
  container.innerHTML = `
    <div class="ai-loading">
      <div class="ai-spinner"></div>
      <span>AI is reviewing additional clauses\u2026</span>
    </div>`;
}

function renderAIResult(text) {
  const container = document.getElementById('ai-section');
  if (!text) {
    container.hidden = true;
    return;
  }
  container.innerHTML = `
    <div class="ai-result">
      <h3 class="ai-heading">
        <span class="ai-chip">AI Enhanced</span>
        Additional Findings
      </h3>
      <div class="ai-content">${formatAIText(text)}</div>
      <p class="ai-disclaimer">AI analysis uses Chrome's on-device Gemini Nano model. Results are additional context only — verify against official sources.</p>
    </div>`;
}

// ── Result Actions ─────────────────────────────────────────────────────────────
function setupResultActions() {
  document.getElementById('copy-btn').addEventListener('click', copyReport);
  document.getElementById('print-btn').addEventListener('click', () => window.print());
}

async function copyReport() {
  const result = window.__leaseScanResult;
  if (!result) return;

  const lines = [
    `LEASESCAN REPORT`,
    `Province: ${result.province}`,
    `Scanned: ${new Date(result.scannedAt).toLocaleString()}`,
    `Words: ${result.wordCount.toLocaleString()}`,
    ``,
    `SUMMARY: ${result.summary.verdictText}`,
    `Total flags: ${result.summary.total} (${result.summary.high} high, ${result.summary.medium} medium, ${result.summary.low} notes)`,
    ``,
    ...result.flags.map(
      (f, i) =>
        `${i + 1}. [${f.severity.toUpperCase()}] ${f.title}\n   ${f.description}\n   Law: ${f.legislation}\n   Action: ${f.recommendation}`
    ),
    ``,
    `Legislation: ${result.legislation}`,
    `LeaseScan — leasescan.ca | Not legal advice.`,
  ];

  try {
    await navigator.clipboard.writeText(lines.join('\n'));
    const btn = document.getElementById('copy-btn');
    btn.textContent = 'Copied!';
    setTimeout(() => (btn.textContent = 'Copy Report'), 2000);
  } catch {
    alert('Copy failed. Please select the results manually.');
  }
}

// ── Utilities ──────────────────────────────────────────────────────────────────
function setLoading(on) {
  const btn = document.getElementById('scan-btn');
  const spinner = document.getElementById('scan-spinner');
  btn.disabled = on;
  btn.querySelector('.btn-text').textContent = on ? 'Scanning\u2026' : 'Scan My Lease';
  if (spinner) spinner.hidden = !on;
}

function hideResults() {
  document.getElementById('results-section').hidden = true;
  const ai = document.getElementById('ai-section');
  if (ai) ai.hidden = true;
}

function showError(msg) {
  const el = document.getElementById('error-msg');
  el.textContent = msg;
  el.hidden = false;
}

function clearError() {
  const el = document.getElementById('error-msg');
  el.hidden = true;
  el.textContent = '';
}

function escHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function formatAIText(text) {
  // Convert numbered list to HTML
  const lines = text
    .split('\n')
    .map((l) => l.trim())
    .filter(Boolean);
  const items = lines
    .map((l) => {
      if (/^\d+\./.test(l)) return `<li>${escHtml(l.replace(/^\d+\.\s*/, ''))}</li>`;
      return `<p>${escHtml(l)}</p>`;
    })
    .join('');

  if (items.includes('<li>')) {
    return `<ol>${items}</ol>`;
  }
  return items;
}

function verdictIcon(verdict) {
  return { serious: '🔴', concerns: '🟠', minor: '🟡', clean: '🟢' }[verdict] ?? '⚪';
}

function verdictLabel(verdict) {
  return (
    { serious: 'Serious Concerns', concerns: 'Concerns Found', minor: 'Minor Issues', clean: 'Looks Clean' }[
      verdict
    ] ?? 'Reviewed'
  );
}

function severityLabel(severity) {
  return { high: 'High Risk', medium: 'Medium Risk', low: 'Note' }[severity] ?? severity;
}

function tick() {
  return new Promise((r) => setTimeout(r, 0));
}
