// Feature 9: Save/Load Drafts via localStorage

const STORAGE_KEY = 'leaseCreate_drafts';

export function saveDraft(name, formData) {
  const drafts = getAllDrafts();
  drafts[name] = {
    data: formData,
    savedAt: new Date().toISOString(),
  };
  localStorage.setItem(STORAGE_KEY, JSON.stringify(drafts));
}

export function loadDraft(name) {
  const drafts = getAllDrafts();
  return drafts[name]?.data || null;
}

export function deleteDraft(name) {
  const drafts = getAllDrafts();
  delete drafts[name];
  localStorage.setItem(STORAGE_KEY, JSON.stringify(drafts));
}

export function getAllDrafts() {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}');
  } catch {
    return {};
  }
}

export function getDraftList() {
  const drafts = getAllDrafts();
  return Object.entries(drafts)
    .map(([name, { savedAt }]) => ({ name, savedAt }))
    .sort((a, b) => new Date(b.savedAt) - new Date(a.savedAt));
}

export function renderDraftManager() {
  const drafts = getDraftList();
  const listHtml = drafts.length === 0
    ? '<p class="drafts-empty">No saved drafts yet. Your progress is saved locally in your browser.</p>'
    : drafts.map(d => `
        <div class="draft-item" data-draft="${esc(d.name)}">
          <div class="draft-info">
            <strong>${esc(d.name)}</strong>
            <span>${new Date(d.savedAt).toLocaleString()}</span>
          </div>
          <div class="draft-actions">
            <button class="btn btn-sm btn-primary draft-load" data-draft="${esc(d.name)}">Load</button>
            <button class="btn btn-sm btn-danger draft-delete" data-draft="${esc(d.name)}">Delete</button>
          </div>
        </div>
      `).join('');

  return `
    <div class="drafts-panel">
      <div class="drafts-save">
        <input type="text" id="draftName" class="draft-name-input" placeholder="Name this draft...">
        <button class="btn btn-sm btn-primary" id="btn-save-draft">Save Draft</button>
      </div>
      <div class="drafts-list" id="drafts-list">
        ${listHtml}
      </div>
    </div>
  `;
}

function esc(str) {
  return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

// Auto-save to a special "__autosave__" key every 30 seconds
let autoSaveInterval = null;
export function startAutoSave(collectFn) {
  if (autoSaveInterval) clearInterval(autoSaveInterval);
  autoSaveInterval = setInterval(() => {
    try {
      const data = collectFn();
      if (data && data.province) {
        saveDraft('__autosave__', data);
      }
    } catch { /* ignore */ }
  }, 30000);
}

export function getAutoSave() {
  return loadDraft('__autosave__');
}

export function hasAutoSave() {
  const drafts = getAllDrafts();
  return !!drafts['__autosave__'];
}
