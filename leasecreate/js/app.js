// LeaseCreate — Main Application (with all features integrated)
import { provinces, provinceList } from './provinces/index.js';
import { generateLease } from './generator.js';
import { checkClause, renderClauseWarnings } from './clause-checker.js';
import { SignaturePad, createSignatureSection } from './signature-pad.js';
import { renderRightsSidebar } from './rights-sidebar.js';
import { generateTimeline } from './timeline.js';
import { setLanguage, getLanguage, t } from './i18n.js';
import { saveDraft, loadDraft, deleteDraft, getDraftList, renderDraftManager, startAutoSave, hasAutoSave, getAutoSave } from './drafts.js';
import { renderTemplateSelector, getTemplate } from './templates.js';
import { renderImportSection, parseLeaseText, hasLeaseScanData, getLeaseScanData } from './leasescan-import.js';

const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => document.querySelectorAll(sel);

let currentProvince = null;
let selectedSchedules = [];
let sigPadLandlord = null;
let sigPadTenant = null;

// ── Init ──
document.addEventListener('DOMContentLoaded', () => {
  // Core features — must work
  populateProvinceDropdown();
  setupEventListeners();
  showStep(1);

  // Enhanced features — wrapped so a failure in one doesn't break the rest
  const safeInit = (name, fn) => {
    try { fn(); } catch (e) { console.warn(`[LeaseCreate] ${name} init failed:`, e); }
  };

  safeInit('ClauseChecker', setupClauseChecker);
  safeInit('Drafts', setupDrafts);
  safeInit('Templates', setupTemplates);
  safeInit('Import', setupImport);
  safeInit('AutoSave', () => startAutoSave(collectFormData));

  // Check for auto-save recovery
  try {
    if (hasAutoSave()) {
      const banner = document.createElement('div');
      banner.className = 'autosave-banner';
      banner.innerHTML = `
        <span>You have an unsaved draft from a previous session.</span>
        <button class="btn btn-sm btn-primary" id="btn-restore-autosave">Restore</button>
        <button class="btn btn-sm btn-secondary" id="btn-dismiss-autosave">Dismiss</button>
      `;
      $('main .container').prepend(banner);

      $('#btn-restore-autosave')?.addEventListener('click', () => {
        const data = getAutoSave();
        if (data) restoreDraftProgress(data);
        banner.remove();
      });
      $('#btn-dismiss-autosave')?.addEventListener('click', () => banner.remove());
    }
  } catch (e) { console.warn('[LeaseCreate] AutoSave recovery failed:', e); }
});


// ── Province Dropdown ──
function populateProvinceDropdown() {
  const select = $('#province');
  provinceList.forEach(p => {
    const opt = document.createElement('option');
    opt.value = p.code;
    opt.textContent = p.name;
    select.appendChild(opt);
  });
}


// ── Steps Navigation ──
function showStep(step) {
  $$('.form-step').forEach(s => s.classList.remove('active'));
  $(`.form-step[data-step="${step}"]`).classList.add('active');

  $$('.step-indicator .step').forEach((s, i) => {
    s.classList.toggle('active', i + 1 === step);
    s.classList.toggle('completed', i + 1 < step);
  });

  window.scrollTo({ top: 0, behavior: 'smooth' });
}

function getActiveStep() {
  return Number($('.form-step.active')?.dataset.step || 1);
}

function getSelectedScheduleIds() {
  return Array.from($$('#schedule-list input[type="checkbox"]:checked')).map(cb => cb.value);
}

function normalizeSelectedScheduleIds(selectedIds) {
  return Array.isArray(selectedIds) ? selectedIds.filter(Boolean) : [];
}

function isStepOneComplete(data) {
  return !!(data?.province && data?.landlordName && data?.tenantName);
}

function isStepTwoComplete(data) {
  return !!(data?.unitAddress && data?.city && data?.postalCode);
}

function isStepThreeComplete(data) {
  return !!(data?.startDate && data?.rentAmount && (data?.termType !== 'fixed' || data?.endDate));
}

function hasStepFourProgress(data) {
  return !!(
    data?.guestPolicy ||
    data?.noisePolicy ||
    data?.maintenanceNotes ||
    data?.additionalTerms ||
    data?.parkingIncluded ||
    data?.storageIncluded ||
    data?.smokingAllowed ||
    data?.petsAllowed ||
    data?.tenantInsuranceRequired
  );
}

function getResumeStep(data) {
  const explicitStep = Number(data?.currentStep);
  if (Number.isFinite(explicitStep) && explicitStep >= 1) {
    return Math.min(6, Math.max(1, explicitStep));
  }

  if (!isStepOneComplete(data)) return 1;
  if (!isStepTwoComplete(data)) return 2;
  if (!isStepThreeComplete(data)) return 3;
  if (normalizeSelectedScheduleIds(data?.selectedScheduleIds).length) return 5;
  return hasStepFourProgress(data) ? 5 : 4;
}

function applySelectedScheduleIds(selectedIds) {
  const selectedSet = new Set(normalizeSelectedScheduleIds(selectedIds));
  $$('#schedule-list input[type="checkbox"]').forEach(cb => {
    cb.checked = selectedSet.has(cb.value);
  });
}

function restoreDraftProgress(data) {
  if (!data) return;

  applyFormData(data);

  const resumeStep = getResumeStep(data);
  const selectedScheduleIds = normalizeSelectedScheduleIds(data.selectedScheduleIds);

  if (currentProvince && (resumeStep >= 5 || selectedScheduleIds.length)) {
    buildScheduleSelector();
    applySelectedScheduleIds(selectedScheduleIds);
  }

  if (resumeStep >= 6) {
    generatePreview();
  }

  showStep(resumeStep);
}

function nextStep(current) {
  if (!validateStep(current)) return;
  if (current === 1) {
    onProvinceSelected();
  }
  if (current === 4) {
    buildScheduleSelector();
  }
  if (current === 5) {
    generatePreview();
  }
  showStep(current + 1);
}

function prevStep(current) {
  showStep(current - 1);
}


// ── Province Selection ──
function onProvinceSelected() {
  const code = $('#province').value;
  currentProvince = provinces[code];
  if (!currentProvince) return;

  // Show province info banner
  const info = $('#province-info');
  info.innerHTML = `
    <strong>${currentProvince.name}</strong> — ${currentProvince.legislationShort}
    ${currentProvince.standardLeaseRequired ? `<br><span class="info-warning">This province requires the official <strong>${currentProvince.standardLeaseForm}</strong>. This tool generates a supplemental agreement.</span>` : ''}
    <br>Regulator: ${currentProvince.regulator}
    <br>Deposit rules: ${currentProvince.rentRules.maxDeposit}
  `;
  info.hidden = false;

  // Update deposit fields
  updateDepositFields();

  // Update rights sidebar
  updateRightsSidebar();

  // Switch to French if Quebec selected
  if (code === 'QC' && getLanguage() !== 'fr') {
    showLanguagePrompt();
  }
}

function showLanguagePrompt() {
  const existing = $('#lang-prompt');
  if (existing) existing.remove();

  const prompt = document.createElement('div');
  prompt.id = 'lang-prompt';
  prompt.className = 'lang-prompt';
  prompt.innerHTML = `
    <span>Quebec selected — switch to French?</span>
    <button class="btn btn-sm btn-primary" id="btn-lang-fr">Oui, en francais</button>
    <button class="btn btn-sm btn-secondary" id="btn-lang-en">No, keep English</button>
  `;
  $('#province-info').after(prompt);

  $('#btn-lang-fr').addEventListener('click', () => {
    setLanguage('fr');
    const langBtn = $('#lang-switch');
    if (langBtn) langBtn.textContent = 'EN';
    prompt.remove();
  });
  $('#btn-lang-en').addEventListener('click', () => prompt.remove());
}

function updateDepositFields() {
  if (!currentProvince) return;

  const depositSection = $('#deposit-fields');
  let html = '';

  if (currentProvince.code === 'ON') {
    html = `
      <div class="form-group">
        <label for="lastMonthDeposit">Last Month's Rent Deposit ($)</label>
        <input type="number" id="lastMonthDeposit" step="0.01" placeholder="Same as rent amount">
        <span class="field-help">Ontario only allows a last month's rent deposit (RTA s.106)</span>
      </div>
    `;
  } else if (currentProvince.code === 'QC') {
    html = `<p class="form-notice">Security deposits are <strong>prohibited</strong> in Quebec. Only first month's rent may be collected.</p>`;
  } else {
    html = `
      <div class="form-group">
        <label for="securityDeposit">Security Deposit ($)</label>
        <input type="number" id="securityDeposit" step="0.01" placeholder="0.00">
        <span class="field-help">Maximum: ${currentProvince.rentRules.maxDeposit}</span>
      </div>
    `;
    if (currentProvince.code === 'BC') {
      html += `
        <div class="form-group">
          <label for="petDeposit">Pet Damage Deposit ($)</label>
          <input type="number" id="petDeposit" step="0.01" placeholder="0.00">
          <span class="field-help">Max half month's rent, separate from security deposit</span>
        </div>
      `;
    }
  }

  depositSection.innerHTML = html;

  const petNotice = $('#pet-notice');
  if (currentProvince.code === 'ON') {
    petNotice.textContent = 'Note: No-pet clauses are void and unenforceable in Ontario (RTA s.14)';
    petNotice.hidden = false;
  } else {
    petNotice.hidden = true;
  }
}


// ── Feature 5: Rights Sidebar ──
function updateRightsSidebar() {
  if (!currentProvince) return;
  const sidebar = $('#rights-sidebar');
  sidebar.innerHTML = renderRightsSidebar(currentProvince.code);
  sidebar.classList.add('has-content');
}


// ── Feature 1: Clause Checker ──
function setupClauseChecker() {
  const textarea = $('#additionalTerms');
  const resultsEl = $('#clause-check-results');
  let debounce = null;

  textarea.addEventListener('input', () => {
    clearTimeout(debounce);
    debounce = setTimeout(() => {
      if (!currentProvince) return;
      const warnings = checkClause(textarea.value, currentProvince.code);
      resultsEl.innerHTML = renderClauseWarnings(warnings);
      resultsEl.hidden = warnings.length === 0;
    }, 400);
  });
}


// ── Feature 9: Drafts ──
function setupDrafts() {
  const container = $('#drafts-container');
  container.innerHTML = renderDraftManager();

  // Save button
  container.addEventListener('click', (e) => {
    if (e.target.id === 'btn-save-draft') {
      const nameInput = $('#draftName');
      const name = nameInput.value.trim() || `Draft ${new Date().toLocaleDateString()}`;
      saveDraft(name, collectFormData());
      nameInput.value = '';
      container.innerHTML = renderDraftManager();
      showToast('Draft saved!');
    }

    if (e.target.classList.contains('draft-load')) {
      const name = e.target.dataset.draft;
      const data = loadDraft(name);
      if (data) {
        restoreDraftProgress(data);
        showToast(`Loaded: ${name}`);
      }
    }

    if (e.target.classList.contains('draft-delete')) {
      const name = e.target.dataset.draft;
      deleteDraft(name);
      container.innerHTML = renderDraftManager();
      showToast('Draft deleted');
    }
  });
}


// ── Feature 10: Templates ──
function setupTemplates() {
  const container = $('#template-container');
  container.innerHTML = renderTemplateSelector();

  container.addEventListener('click', (e) => {
    const card = e.target.closest('.template-card');
    if (!card) return;

    const template = getTemplate(card.dataset.template);
    if (!template) return;

    applyFormData(template.data);
    showToast(`Template applied: ${template.name}`);
  });
}


// ── Feature 6: LeaseScan Import ──
function setupImport() {
  const container = $('#import-container');
  container.innerHTML = renderImportSection();

  // Import from LeaseScan localStorage
  $('#btn-import-leasescan')?.addEventListener('click', () => {
    const data = getLeaseScanData();
    if (data && data.text) {
      const parsed = parseLeaseText(data.text);
      applyFormData(parsed);
      showToast('Imported from LeaseScan');
    }
  });

  // File upload
  $('#import-file')?.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => {
      const parsed = parseLeaseText(reader.result);
      applyFormData(parsed);
      showToast('Imported from file');
    };
    reader.readAsText(file);
  });

  // Paste text
  $('#btn-import-paste')?.addEventListener('click', () => {
    const modal = document.createElement('div');
    modal.className = 'modal-overlay';
    modal.innerHTML = `
      <div class="modal-content">
        <h3>Paste Lease Text</h3>
        <p>Paste the text of an existing lease below. We'll extract key fields automatically.</p>
        <textarea id="import-paste-text" rows="12" placeholder="Paste your lease text here..."></textarea>
        <div class="modal-actions">
          <button class="btn btn-primary" id="btn-import-paste-go">Import</button>
          <button class="btn btn-secondary" id="btn-import-paste-cancel">Cancel</button>
        </div>
      </div>
    `;
    document.body.appendChild(modal);

    $('#btn-import-paste-go').addEventListener('click', () => {
      const text = $('#import-paste-text').value;
      if (text) {
        const parsed = parseLeaseText(text);
        applyFormData(parsed);
        showToast('Imported from pasted text');
      }
      modal.remove();
    });

    $('#btn-import-paste-cancel').addEventListener('click', () => modal.remove());
    modal.addEventListener('click', (e) => { if (e.target === modal) modal.remove(); });
  });
}


// ── Schedule Selector ──
function buildScheduleSelector() {
  if (!currentProvince) return;
  const container = $('#schedule-list');
  container.innerHTML = '';

  currentProvince.schedules.forEach(s => {
    const div = document.createElement('div');
    div.className = 'schedule-option';
    div.innerHTML = `
      <label>
        <input type="checkbox" value="${s.id}" data-name="${s.name}" data-desc="${s.description}">
        <div class="schedule-info">
          <strong>${s.name}</strong>
          <span>${s.description}</span>
        </div>
      </label>
    `;
    container.appendChild(div);
  });
}


// ── Form Data Collection ──
function collectFormData() {
  const utilities = {};
  $$('.utility-toggle').forEach(el => {
    utilities[el.dataset.utility] = el.checked ? 'included' : 'tenant';
  });

  return {
    province: $('#province').value,
    landlordName: $('#landlordName').value.trim(),
    landlordAddress: $('#landlordAddress').value.trim(),
    landlordPhone: $('#landlordPhone').value.trim(),
    landlordEmail: $('#landlordEmail').value.trim(),
    tenantName: $('#tenantName').value.trim(),
    tenantPhone: $('#tenantPhone').value.trim(),
    tenantEmail: $('#tenantEmail').value.trim(),
    additionalTenants: $('#additionalTenants').value.trim(),
    unitAddress: $('#unitAddress').value.trim(),
    unitNumber: $('#unitNumber').value.trim(),
    city: $('#city').value.trim(),
    postalCode: $('#postalCode').value.trim(),
    unitType: $('#unitType').value,
    isFurnished: $('#isFurnished').checked,
    parkingIncluded: $('#parkingIncluded').checked,
    parkingDetails: $('#parkingDetails')?.value.trim() || '',
    storageIncluded: $('#storageIncluded').checked,
    termType: $('input[name="termType"]:checked')?.value || 'fixed',
    startDate: $('#startDate').value,
    endDate: $('#endDate').value,
    rentAmount: $('#rentAmount').value,
    rentDueDay: $('#rentDueDay').value || '1st',
    paymentMethod: $('#paymentMethod').value,
    lastMonthDeposit: $('#lastMonthDeposit')?.value || '',
    securityDeposit: $('#securityDeposit')?.value || '',
    petDeposit: $('#petDeposit')?.value || '',
    utilities,
    smokingAllowed: $('#smokingAllowed').checked,
    petsAllowed: $('#petsAllowed').checked,
    guestPolicy: $('#guestPolicy').value.trim(),
    noisePolicy: $('#noisePolicy').value.trim(),
    tenantInsuranceRequired: $('#tenantInsurance').checked,
    maintenanceNotes: $('#maintenanceNotes').value.trim(),
    additionalTerms: $('#additionalTerms').value.trim(),
    currentStep: getActiveStep(),
    selectedScheduleIds: getSelectedScheduleIds(),
  };
}

// ── Apply form data (from template, draft, or import) ──
function applyFormData(data) {
  if (!data) return;

  if (data.province) {
    $('#province').value = data.province;
    currentProvince = provinces[data.province];
    if (currentProvince) onProvinceSelected();
  }

  const textFields = [
    'landlordName', 'landlordAddress', 'landlordPhone', 'landlordEmail',
    'tenantName', 'tenantPhone', 'tenantEmail', 'additionalTenants',
    'unitAddress', 'unitNumber', 'city', 'postalCode',
    'startDate', 'endDate', 'rentAmount',
    'guestPolicy', 'noisePolicy', 'maintenanceNotes', 'additionalTerms',
    'parkingDetails',
  ];
  textFields.forEach(field => {
    const el = $(`#${field}`);
    if (el && data[field] !== undefined) el.value = data[field];
  });

  const selectFields = ['unitType', 'rentDueDay', 'paymentMethod'];
  selectFields.forEach(field => {
    const el = $(`#${field}`);
    if (el && data[field]) el.value = data[field];
  });

  const checkFields = ['isFurnished', 'parkingIncluded', 'storageIncluded', 'smokingAllowed', 'petsAllowed'];
  checkFields.forEach(field => {
    const el = $(`#${field}`);
    if (el && data[field] !== undefined) el.checked = !!data[field];
  });

  if (data.tenantInsuranceRequired !== undefined) {
    $('#tenantInsurance').checked = data.tenantInsuranceRequired;
  }

  if (data.termType) {
    const radio = $(`input[name="termType"][value="${data.termType}"]`);
    if (radio) {
      radio.checked = true;
      $('#endDateGroup').style.display = data.termType === 'fixed' ? '' : 'none';
    }
  }

  if (data.utilities) {
    $$('.utility-toggle').forEach(el => {
      const key = el.dataset.utility;
      if (data.utilities[key] !== undefined) {
        el.checked = data.utilities[key] === 'included';
      }
    });
  }

  // Deposit fields (may need province selected first)
  setTimeout(() => {
    if (data.lastMonthDeposit) {
      const el = $('#lastMonthDeposit');
      if (el) el.value = data.lastMonthDeposit;
    }
    if (data.securityDeposit) {
      const el = $('#securityDeposit');
      if (el) el.value = data.securityDeposit;
    }
    if (data.petDeposit) {
      const el = $('#petDeposit');
      if (el) el.value = data.petDeposit;
    }
  }, 100);
}


// ── Preview ──
function generatePreview() {
  selectedSchedules = [];
  $$('#schedule-list input[type="checkbox"]:checked').forEach(cb => {
    const pSchedule = currentProvince.schedules.find(s => s.id === cb.value);
    if (pSchedule) selectedSchedules.push(pSchedule);
  });

  const formData = collectFormData();
  const leaseHtml = generateLease(formData, selectedSchedules);

  // Feature 7: Timeline
  const timelineHtml = currentProvince ? generateTimeline(formData, currentProvince) : '';

  // Feature 3: Signature section
  const sigHtml = createSignatureSection();

  window.clearPrintPagination?.(document);
  $('#lease-preview').innerHTML = composeLeasePreviewHtml(leaseHtml, sigHtml, timelineHtml);

  // Init signature pads
  setTimeout(() => {
    const landlordCanvas = $('#sig-landlord');
    const tenantCanvas = $('#sig-tenant');
    if (landlordCanvas) sigPadLandlord = new SignaturePad(landlordCanvas);
    if (tenantCanvas) sigPadTenant = new SignaturePad(tenantCanvas);

    // Clear buttons
    $$('[data-clear]').forEach(btn => {
      btn.addEventListener('click', () => {
        const id = btn.dataset.clear;
        if (id === 'sig-landlord' && sigPadLandlord) sigPadLandlord.clear();
        if (id === 'sig-tenant' && sigPadTenant) sigPadTenant.clear();
      });
    });
  }, 100);
}

function composeLeasePreviewHtml(leaseHtml, sigHtml, timelineHtml) {
  const signaturePattern = /<div class="lease-section lease-signatures[^"]*">/;
  const match = leaseHtml.match(signaturePattern);

  if (!match) {
    return leaseHtml + timelineHtml + sigHtml;
  }

  return leaseHtml.replace(
    signaturePattern,
    `${timelineHtml}<div class="agreement-signature-stack print-page-group">${match[0]}`
  ) + sigHtml + '</div>';
}


// ── PDF Export ──
async function exportPDF() {
  const preview = $('#lease-preview');

  // Replace canvas signatures with images for print
  let printContent = preview.innerHTML;

  if (sigPadLandlord && !sigPadLandlord.isEmpty()) {
    const img = sigPadLandlord.toDataURL();
    printContent = printContent.replace(
      /<canvas id="sig-landlord"[^>]*><\/canvas>/,
      `<img src="${img}" style="width:100%;height:120px;object-fit:contain;" alt="Landlord Signature">`
    );
  }
  if (sigPadTenant && !sigPadTenant.isEmpty()) {
    const img = sigPadTenant.toDataURL();
    printContent = printContent.replace(
      /<canvas id="sig-tenant"[^>]*><\/canvas>/,
      `<img src="${img}" style="width:100%;height:120px;object-fit:contain;" alt="Tenant Signature">`
    );
  }

  // Also embed typed signatures
  const typedLandlord = $('#sig-landlord-typed')?.value.trim();
  const typedTenant = $('#sig-tenant-typed')?.value.trim();
  if (typedLandlord && (!sigPadLandlord || sigPadLandlord.isEmpty())) {
    printContent = printContent.replace(
      /<canvas id="sig-landlord"[^>]*><\/canvas>/,
      `<div style="font-family:'Brush Script MT',cursive;font-size:28px;padding:20px 0;border-bottom:1px solid #333;">${esc(typedLandlord)}</div>`
    );
  }
  if (typedTenant && (!sigPadTenant || sigPadTenant.isEmpty())) {
    printContent = printContent.replace(
      /<canvas id="sig-tenant"[^>]*><\/canvas>/,
      `<div style="font-family:'Brush Script MT',cursive;font-size:28px;padding:20px 0;border-bottom:1px solid #333;">${esc(typedTenant)}</div>`
    );
  }

  // Remove interactive elements from print
  printContent = printContent.replace(/<button[^>]*>.*?<\/button>/gs, '');
  printContent = printContent.replace(/<input[^>]*class="sig-typed-input"[^>]*>/g, '');
  printContent = printContent.replace(/<div class="sig-pad-actions">[\s\S]*?<\/div>/g, '');
  printContent = printContent.replace(/<p class="sig-instructions">[\s\S]*?<\/p>/g, '');

  const stylesheetHref = new URL('./css/styles.css', window.location.href).href;
  const printWindow = window.open('', '_blank');
  printWindow.document.write(`
    <!DOCTYPE html>
    <html>
    <head>
      <title>Residential Tenancy Agreement</title>
      <link rel="stylesheet" href="${stylesheetHref}">
      <style>${getPrintStyles()}</style>
    </head>
    <body>
      <div class="print-document" id="lease-preview">${printContent}</div>
    </body>
    </html>
  `);
  printWindow.document.close();
  printWindow.onload = async () => {
    try {
      printWindow.history.replaceState({}, '', '/leasecreate/print-preview');
    } catch (error) {
      // Ignore browsers that don't allow history updates in the popup.
    }

    await waitForPrintWindowReady(printWindow);

    const printRoot = printWindow.document.querySelector('#lease-preview');
    if (window.preparePrintPagination && printRoot) {
      window.preparePrintPagination(printWindow.document, printRoot);
    }

    printWindow.focus();
    printWindow.print();
  };
}

function waitForPrintWindowReady(printWindow) {
  const { document } = printWindow;
  const stylesheetLoads = Array.from(document.querySelectorAll('link[rel="stylesheet"]')).map((link) => (
    new Promise((resolve) => {
      if (link.sheet) {
        resolve();
        return;
      }

      const done = () => resolve();
      link.addEventListener('load', done, { once: true });
      link.addEventListener('error', done, { once: true });
      printWindow.setTimeout(done, 1200);
    })
  ));

  const fontsReady = document.fonts?.ready?.catch(() => undefined) ?? Promise.resolve();

  return Promise.all([...stylesheetLoads, fontsReady]).then(() => (
    new Promise((resolve) => {
      printWindow.requestAnimationFrame(() => {
        printWindow.requestAnimationFrame(resolve);
      });
    })
  ));
}

function esc(str) {
  return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}


function getPrintStyles() {
  return `
    @page {
      size: Letter;
      margin: 20mm 15mm;
    }

    html {
      -webkit-print-color-adjust: exact;
      print-color-adjust: exact;
    }

    body {
      margin: 0;
      padding: 20mm 15mm;
      background: #fff;
      font-family: 'Georgia', 'Times New Roman', serif;
      font-size: 11pt;
      line-height: 1.5;
      color: #1a1a1a;
    }

    #lease-preview.print-document {
      max-width: 8in;
      margin: 0 auto;
    }

    .print-page-break {
      display: none;
    }

    @media print {
      body {
        padding: 0;
      }

      #lease-preview.print-document {
        max-width: none;
        margin: 0;
      }
    }
  `;
}


// ── Validation ──
function validateStep(step) {
  let valid = true;
  const stepEl = $(`.form-step[data-step="${step}"]`);
  const required = stepEl.querySelectorAll('[required]');

  required.forEach(input => {
    const group = input.closest('.form-group');
    if (!input.value.trim()) {
      if (group) group.classList.add('error');
      valid = false;
    } else {
      if (group) group.classList.remove('error');
    }
  });

  if (!valid) {
    const firstError = stepEl.querySelector('.form-group.error');
    if (firstError) firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
  }

  return valid;
}


// ── Toast Notifications ──
function showToast(message) {
  const existing = $('.toast');
  if (existing) existing.remove();

  const toast = document.createElement('div');
  toast.className = 'toast';
  toast.textContent = message;
  document.body.appendChild(toast);
  requestAnimationFrame(() => toast.classList.add('show'));
  setTimeout(() => {
    toast.classList.remove('show');
    setTimeout(() => toast.remove(), 300);
  }, 2500);
}


// ── Event Listeners ──
function setupEventListeners() {
  // Next/Prev buttons
  $$('.btn-next').forEach(btn => {
    btn.addEventListener('click', () => {
      const step = parseInt(btn.closest('.form-step').dataset.step);
      nextStep(step);
    });
  });

  $$('.btn-prev').forEach(btn => {
    btn.addEventListener('click', () => {
      const step = parseInt(btn.closest('.form-step').dataset.step);
      prevStep(step);
    });
  });

  // Province change
  $('#province').addEventListener('change', () => {
    const code = $('#province').value;
    if (code) {
      currentProvince = provinces[code];
      onProvinceSelected();
    }
  });

  // Term type toggle
  $$('input[name="termType"]').forEach(radio => {
    radio.addEventListener('change', () => {
      $('#endDateGroup').style.display = radio.value === 'fixed' ? '' : 'none';
    });
  });

  // Export PDF
  $('#btn-export').addEventListener('click', exportPDF);

  // Edit button
  $('#btn-edit').addEventListener('click', () => showStep(1));

  // Regenerate preview
  $('#btn-regenerate').addEventListener('click', () => generatePreview());

  // Rights sidebar toggle
  $('#rights-toggle')?.addEventListener('click', () => {
    const sidebar = $('#rights-sidebar');
    sidebar.classList.toggle('open');
  });

  // Language switcher — button label shows what you'll switch TO
  $('#lang-switch')?.addEventListener('click', () => {
    const newLang = getLanguage() === 'en' ? 'fr' : 'en';
    setLanguage(newLang);
    // After switching, button shows the OTHER language (what you'd switch to next)
    $('#lang-switch').textContent = newLang === 'fr' ? 'EN' : 'FR';
  });
}
