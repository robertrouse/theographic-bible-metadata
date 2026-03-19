/**
 * UX enhancements: breadcrumb history, bookmarks/favorites, undo/redo navigation.
 *
 * Usage:
 *   import { initUX, pushBreadcrumb, getBookmarks, toggleBookmark } from './ux.js';
 *   initUX();
 */

// ── Navigation History (Breadcrumbs + Undo/Redo) ──────────────────────

const MAX_HISTORY = 50;
let history = [];
let historyIndex = -1;
let onNavigate = null;

/**
 * Push a navigation entry. Called whenever the user navigates to a new entity.
 * @param {{ id: string, label: string, nodeType: string, page: string }} entry
 */
export function pushBreadcrumb(entry) {
  // Trim any forward history when we branch
  if (historyIndex < history.length - 1) {
    history = history.slice(0, historyIndex + 1);
  }
  // Don't duplicate the current entry
  if (history.length > 0 && history[history.length - 1].id === entry.id) return;

  history.push(entry);
  if (history.length > MAX_HISTORY) history.shift();
  historyIndex = history.length - 1;

  saveHistory();
  renderBreadcrumbs();
  updateUndoRedoButtons();
}

export function canUndo() { return historyIndex > 0; }
export function canRedo() { return historyIndex < history.length - 1; }

export function undo() {
  if (!canUndo()) return null;
  historyIndex--;
  const entry = history[historyIndex];
  renderBreadcrumbs();
  updateUndoRedoButtons();
  return entry;
}

export function redo() {
  if (!canRedo()) return null;
  historyIndex++;
  const entry = history[historyIndex];
  renderBreadcrumbs();
  updateUndoRedoButtons();
  return entry;
}

function saveHistory() {
  try {
    localStorage.setItem('theographic-history', JSON.stringify(history.slice(-20)));
  } catch {}
}

function loadHistory() {
  try {
    const saved = localStorage.getItem('theographic-history');
    if (saved) {
      history = JSON.parse(saved);
      historyIndex = history.length - 1;
    }
  } catch {}
}

// ── Bookmarks / Favorites ─────────────────────────────────────────────

let bookmarks = [];

export function getBookmarks() { return [...bookmarks]; }

export function toggleBookmark(entry) {
  const idx = bookmarks.findIndex(b => b.id === entry.id);
  if (idx >= 0) {
    bookmarks.splice(idx, 1);
  } else {
    bookmarks.push({ ...entry, savedAt: new Date().toISOString() });
  }
  saveBookmarks();
  renderBookmarks();
  return idx < 0; // true if added, false if removed
}

export function isBookmarked(id) {
  return bookmarks.some(b => b.id === id);
}

export function removeBookmark(id) {
  bookmarks = bookmarks.filter(b => b.id !== id);
  saveBookmarks();
  renderBookmarks();
}

function saveBookmarks() {
  try {
    localStorage.setItem('theographic-bookmarks', JSON.stringify(bookmarks));
  } catch {}
}

function loadBookmarks() {
  try {
    const saved = localStorage.getItem('theographic-bookmarks');
    if (saved) bookmarks = JSON.parse(saved);
  } catch {}
}

// ── UI Rendering ──────────────────────────────────────────────────────

function renderBreadcrumbs() {
  const el = document.getElementById('ux-breadcrumbs');
  if (!el) return;

  // Show last 5 entries
  const visible = history.slice(Math.max(0, historyIndex - 4), historyIndex + 1);
  const startIdx = Math.max(0, historyIndex - 4);

  el.innerHTML = visible.map((entry, i) => {
    const isActive = startIdx + i === historyIndex;
    const color = getTypeColor(entry.nodeType);
    return `<span class="breadcrumb-item ${isActive ? 'active' : ''}" ` +
      `data-idx="${startIdx + i}" ` +
      `style="color:${isActive ? 'var(--accent)' : 'var(--text-muted)'}">` +
      `<span class="breadcrumb-type" style="color:${color}">${entry.nodeType?.[0] || '?'}</span>` +
      `${entry.label.length > 15 ? entry.label.slice(0, 15) + '…' : entry.label}` +
      `</span>`;
  }).join('<span class="breadcrumb-sep">›</span>');

  // Click to navigate to any breadcrumb
  el.querySelectorAll('.breadcrumb-item').forEach(item => {
    item.addEventListener('click', () => {
      const idx = parseInt(item.dataset.idx);
      historyIndex = idx;
      const entry = history[historyIndex];
      renderBreadcrumbs();
      updateUndoRedoButtons();
      if (onNavigate) onNavigate(entry);
    });
  });
}

function renderBookmarks() {
  const el = document.getElementById('ux-bookmarks-list');
  if (!el) return;

  if (bookmarks.length === 0) {
    el.innerHTML = '<div style="font-size:11px;color:var(--text-subtle);padding:4px 0">No bookmarks yet. Click ★ on any entity to save it.</div>';
    return;
  }

  el.innerHTML = bookmarks.map(b => {
    const color = getTypeColor(b.nodeType);
    return `<div class="bookmark-item" data-id="${b.id}">` +
      `<span class="breadcrumb-type" style="color:${color}">${b.nodeType?.[0] || '?'}</span>` +
      `<span class="bookmark-label">${b.label}</span>` +
      `<button class="bookmark-remove" data-id="${b.id}" title="Remove bookmark">&times;</button>` +
      `</div>`;
  }).join('');

  el.querySelectorAll('.bookmark-item').forEach(item => {
    item.addEventListener('click', (e) => {
      if (e.target.classList.contains('bookmark-remove')) return;
      const id = item.dataset.id;
      const bookmark = bookmarks.find(b => b.id === id);
      if (bookmark && onNavigate) onNavigate(bookmark);
    });
  });

  el.querySelectorAll('.bookmark-remove').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      removeBookmark(btn.dataset.id);
    });
  });
}

function updateUndoRedoButtons() {
  const undoBtn = document.getElementById('ux-undo');
  const redoBtn = document.getElementById('ux-redo');
  if (undoBtn) undoBtn.disabled = !canUndo();
  if (redoBtn) redoBtn.disabled = !canRedo();
}

function getTypeColor(nodeType) {
  const s = getComputedStyle(document.documentElement);
  const map = {
    Book: '--color-book', Person: '--color-person', Place: '--color-place',
    Event: '--color-event', PeopleGroup: '--color-group', Easton: '--color-easton',
    Chapter: '--color-chapter', Verse: '--color-verse',
  };
  return s.getPropertyValue(map[nodeType] || '--text-muted').trim();
}

// ── Inject UX bar into the page ───────────────────────────────────────

function injectUXBar() {
  const style = document.createElement('style');
  style.textContent = `
    #ux-bar {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 4px 12px;
      background: var(--bg-tertiary);
      border-bottom: 1px solid var(--border);
      font-size: 12px;
      grid-column: 1 / -1;
      overflow-x: auto;
      white-space: nowrap;
    }
    #ux-breadcrumbs {
      display: flex;
      align-items: center;
      gap: 2px;
      flex: 1;
      overflow: hidden;
    }
    .breadcrumb-item {
      cursor: pointer;
      padding: 2px 4px;
      border-radius: 3px;
      font-size: 11px;
      transition: background 0.15s;
    }
    .breadcrumb-item:hover { background: var(--bg-hover); }
    .breadcrumb-item.active { font-weight: 600; }
    .breadcrumb-type {
      font-size: 9px;
      font-weight: 700;
      margin-right: 2px;
    }
    .breadcrumb-sep {
      color: var(--text-subtle);
      font-size: 10px;
      margin: 0 1px;
    }
    .ux-btn {
      padding: 2px 6px;
      font-size: 11px;
      border: 1px solid var(--border);
      border-radius: 4px;
      background: transparent;
      color: var(--text-muted);
      cursor: pointer;
      white-space: nowrap;
    }
    .ux-btn:hover:not(:disabled) { border-color: var(--accent); color: var(--accent); }
    .ux-btn:disabled { opacity: 0.3; cursor: default; }
    .ux-btn.bookmarked { color: var(--accent); border-color: var(--accent); }

    /* Bookmarks panel (dropdown) */
    .bookmarks-panel {
      position: absolute;
      top: 100%;
      right: 0;
      width: 250px;
      max-height: 300px;
      overflow-y: auto;
      background: var(--bg-secondary);
      border: 1px solid var(--border);
      border-radius: 8px;
      box-shadow: 0 8px 24px rgba(0,0,0,0.3);
      padding: 8px;
      display: none;
      z-index: 100;
    }
    .bookmarks-panel.open { display: block; }
    .bookmark-item {
      display: flex;
      align-items: center;
      gap: 6px;
      padding: 5px 6px;
      border-radius: 4px;
      cursor: pointer;
      font-size: 12px;
      margin-bottom: 2px;
    }
    .bookmark-item:hover { background: var(--bg-hover); }
    .bookmark-label { flex: 1; overflow: hidden; text-overflow: ellipsis; }
    .bookmark-remove {
      border: none;
      background: transparent;
      color: var(--text-subtle);
      cursor: pointer;
      font-size: 14px;
      padding: 0 2px;
    }
    .bookmark-remove:hover { color: var(--accent); }
  `;
  document.head.appendChild(style);

  // Insert bar after header
  const header = document.querySelector('header');
  if (!header) return;

  const bar = document.createElement('div');
  bar.id = 'ux-bar';
  bar.innerHTML = `
    <button class="ux-btn" id="ux-undo" title="Back (Alt+←)" disabled>← Back</button>
    <button class="ux-btn" id="ux-redo" title="Forward (Alt+→)" disabled>Forward →</button>
    <div id="ux-breadcrumbs"></div>
    <div style="position:relative">
      <button class="ux-btn" id="ux-bookmarks-btn">★ Bookmarks</button>
      <div class="bookmarks-panel" id="ux-bookmarks-panel">
        <div style="font-size:11px;color:var(--text-muted);margin-bottom:6px;text-transform:uppercase;letter-spacing:0.5px">Saved Bookmarks</div>
        <div id="ux-bookmarks-list"></div>
      </div>
    </div>
  `;
  header.after(bar);

  // Wire undo/redo buttons
  document.getElementById('ux-undo').addEventListener('click', () => {
    const entry = undo();
    if (entry && onNavigate) onNavigate(entry);
  });

  document.getElementById('ux-redo').addEventListener('click', () => {
    const entry = redo();
    if (entry && onNavigate) onNavigate(entry);
  });

  // Keyboard shortcuts
  document.addEventListener('keydown', (e) => {
    if (e.altKey && e.key === 'ArrowLeft') {
      e.preventDefault();
      const entry = undo();
      if (entry && onNavigate) onNavigate(entry);
    }
    if (e.altKey && e.key === 'ArrowRight') {
      e.preventDefault();
      const entry = redo();
      if (entry && onNavigate) onNavigate(entry);
    }
  });

  // Bookmarks panel toggle
  const bmBtn = document.getElementById('ux-bookmarks-btn');
  const bmPanel = document.getElementById('ux-bookmarks-panel');
  bmBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    bmPanel.classList.toggle('open');
  });
  document.addEventListener('click', () => bmPanel.classList.remove('open'));
  bmPanel.addEventListener('click', (e) => e.stopPropagation());
}

// ── Public: Initialize UX system ──────────────────────────────────────

/**
 * Initialize UX enhancements. Call after DOM is ready.
 * @param {function} navigateCallback - Called when user clicks a breadcrumb/bookmark.
 *   Receives { id, label, nodeType, page }.
 */
export function initUX(navigateCallback) {
  onNavigate = navigateCallback || null;
  loadHistory();
  loadBookmarks();
  injectUXBar();
  renderBreadcrumbs();
  renderBookmarks();
  updateUndoRedoButtons();
}
