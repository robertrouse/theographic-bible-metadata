/**
 * Theographic Theme System
 *
 * Provides dark, light, sepia, and high-contrast themes via CSS custom properties.
 * Import this module and call `initTheme()` to set up the theme switcher.
 *
 * Usage:
 *   import { initTheme, getTypeColors, getGenderColor } from './theme.js';
 *   initTheme();  // injects CSS vars, renders theme picker in <header>
 */

// ── Theme Definitions ─────────────────────────────────────────────────

const THEMES = {
  dark: {
    label: 'Dark',
    vars: {
      '--bg-primary':     '#0a0a0f',
      '--bg-secondary':   '#111118',
      '--bg-tertiary':    '#1a1a24',
      '--bg-hover':       '#1a1a24',
      '--border':         '#2a2a35',
      '--edge-color':     '#1a2a35',
      '--text-primary':   '#e0e0e0',
      '--text-secondary': '#aaaaaa',
      '--text-muted':     '#888888',
      '--text-subtle':    '#555555',
      '--text-inverse':   '#000000',
      '--text-on-color':  '#ffffff',
      '--tooltip-bg':     '#1a1a24ee',
      '--accent':         '#c4a55a',
      '--accent-bg':      '#c4a55a22',
      '--link':           '#5a9ec4',
      '--node-stroke':    '#1a1a24',
      '--highlight':      '#c4a55a',
      '--brush-fill':     '#c4a55a33',
      '--graticule':      '#1a1a24',
      '--region-text':    '#222222',
      '--ref-text':       '#333333',
      '--color-book':     '#c4a55a',
      '--color-person':   '#5a9ec4',
      '--color-place':    '#5ac47a',
      '--color-event':    '#c45a7a',
      '--color-group':    '#a55ac4',
      '--color-easton':   '#c49a5a',
      '--color-chapter':  '#666666',
      '--color-verse':    '#888888',
      '--color-male':     '#5a9ec4',
      '--color-female':   '#c45a7a',
      '--color-unknown':  '#888888',
      '--color-person-bg':'#5a9ec422',
      '--color-place-bg': '#5ac47a22',
      '--color-place-fade':'#5ac47a44',
      '--svg-bg':         '#0a0a0f',
    },
  },
  light: {
    label: 'Light',
    vars: {
      '--bg-primary':     '#f5f5f0',
      '--bg-secondary':   '#ffffff',
      '--bg-tertiary':    '#eeeee8',
      '--bg-hover':       '#e8e8e2',
      '--border':         '#d0d0c8',
      '--edge-color':     '#c8c8c0',
      '--text-primary':   '#1a1a1a',
      '--text-secondary': '#555555',
      '--text-muted':     '#777777',
      '--text-subtle':    '#999999',
      '--text-inverse':   '#ffffff',
      '--text-on-color':  '#ffffff',
      '--tooltip-bg':     '#ffffffee',
      '--accent':         '#8b6914',
      '--accent-bg':      '#8b691422',
      '--link':           '#2a6496',
      '--node-stroke':    '#ffffff',
      '--highlight':      '#8b6914',
      '--brush-fill':     '#8b691433',
      '--graticule':      '#d0d0c8',
      '--region-text':    '#bbbbbb',
      '--ref-text':       '#cccccc',
      '--color-book':     '#8b6914',
      '--color-person':   '#2a6496',
      '--color-place':    '#1a7a3a',
      '--color-event':    '#a02050',
      '--color-group':    '#7030a0',
      '--color-easton':   '#9a6a1a',
      '--color-chapter':  '#999999',
      '--color-verse':    '#aaaaaa',
      '--color-male':     '#2a6496',
      '--color-female':   '#a02050',
      '--color-unknown':  '#999999',
      '--color-person-bg':'#2a649622',
      '--color-place-bg': '#1a7a3a22',
      '--color-place-fade':'#1a7a3a44',
      '--svg-bg':         '#f5f5f0',
    },
  },
  sepia: {
    label: 'Sepia',
    vars: {
      '--bg-primary':     '#1c1710',
      '--bg-secondary':   '#241e15',
      '--bg-tertiary':    '#2e261b',
      '--bg-hover':       '#2e261b',
      '--border':         '#3e3428',
      '--edge-color':     '#2e2820',
      '--text-primary':   '#d4c5a9',
      '--text-secondary': '#a89878',
      '--text-muted':     '#7a6e58',
      '--text-subtle':    '#5a5040',
      '--text-inverse':   '#1c1710',
      '--text-on-color':  '#ffffff',
      '--tooltip-bg':     '#241e15ee',
      '--accent':         '#c4a55a',
      '--accent-bg':      '#c4a55a22',
      '--link':           '#7aaa9a',
      '--node-stroke':    '#241e15',
      '--highlight':      '#c4a55a',
      '--brush-fill':     '#c4a55a33',
      '--graticule':      '#2e261b',
      '--region-text':    '#3a3225',
      '--ref-text':       '#4a4030',
      '--color-book':     '#c4a55a',
      '--color-person':   '#7aaa9a',
      '--color-place':    '#8ab47a',
      '--color-event':    '#c47a6a',
      '--color-group':    '#a07ac4',
      '--color-easton':   '#c4a05a',
      '--color-chapter':  '#6a5e48',
      '--color-verse':    '#7a6e58',
      '--color-male':     '#7aaa9a',
      '--color-female':   '#c47a6a',
      '--color-unknown':  '#7a6e58',
      '--color-person-bg':'#7aaa9a22',
      '--color-place-bg': '#8ab47a22',
      '--color-place-fade':'#8ab47a44',
      '--svg-bg':         '#1c1710',
    },
  },
  'high-contrast': {
    label: 'High Contrast',
    vars: {
      '--bg-primary':     '#000000',
      '--bg-secondary':   '#0a0a0a',
      '--bg-tertiary':    '#141414',
      '--bg-hover':       '#1e1e1e',
      '--border':         '#444444',
      '--edge-color':     '#333333',
      '--text-primary':   '#ffffff',
      '--text-secondary': '#dddddd',
      '--text-muted':     '#bbbbbb',
      '--text-subtle':    '#999999',
      '--text-inverse':   '#000000',
      '--text-on-color':  '#ffffff',
      '--tooltip-bg':     '#000000ee',
      '--accent':         '#ffd700',
      '--accent-bg':      '#ffd70033',
      '--link':           '#66bbff',
      '--node-stroke':    '#000000',
      '--highlight':      '#ffd700',
      '--brush-fill':     '#ffd70044',
      '--graticule':      '#222222',
      '--region-text':    '#333333',
      '--ref-text':       '#444444',
      '--color-book':     '#ffd700',
      '--color-person':   '#66bbff',
      '--color-place':    '#66ff66',
      '--color-event':    '#ff6688',
      '--color-group':    '#cc77ff',
      '--color-easton':   '#ffaa33',
      '--color-chapter':  '#888888',
      '--color-verse':    '#aaaaaa',
      '--color-male':     '#66bbff',
      '--color-female':   '#ff6688',
      '--color-unknown':  '#aaaaaa',
      '--color-person-bg':'#66bbff22',
      '--color-place-bg': '#66ff6622',
      '--color-place-fade':'#66ff6644',
      '--svg-bg':         '#000000',
    },
  },
};

// ── State ─────────────────────────────────────────────────────────────

let currentTheme = 'dark';

// ── Apply theme ───────────────────────────────────────────────────────

function applyTheme(name) {
  const theme = THEMES[name];
  if (!theme) return;
  currentTheme = name;

  const root = document.documentElement;
  for (const [prop, value] of Object.entries(theme.vars)) {
    root.style.setProperty(prop, value);
  }

  // Persist
  try { localStorage.setItem('theographic-theme', name); } catch {}

  // Update picker UI
  document.querySelectorAll('.theme-btn').forEach(btn => {
    const isActive = btn.dataset.theme === name;
    btn.classList.toggle('active', isActive);
    btn.setAttribute('aria-checked', isActive);
  });
}

// ── Theme Picker UI ───────────────────────────────────────────────────

function renderThemePicker(headerEl) {
  const picker = document.createElement('div');
  picker.className = 'theme-picker';
  picker.setAttribute('role', 'radiogroup');
  picker.setAttribute('aria-label', 'Color theme');
  picker.innerHTML = Object.entries(THEMES).map(([key, theme]) =>
    `<button class="theme-btn ${key === currentTheme ? 'active' : ''}" data-theme="${key}" title="${theme.label}" role="radio" aria-checked="${key === currentTheme}">${theme.label}</button>`
  ).join('');

  picker.querySelectorAll('.theme-btn').forEach(btn => {
    btn.addEventListener('click', () => applyTheme(btn.dataset.theme));
  });

  headerEl.appendChild(picker);
}

// ── Inject base CSS for theme picker ──────────────────────────────────

function injectPickerStyles() {
  const style = document.createElement('style');
  style.textContent = `
    *, *::before, *::after {
      transition: background-color 0.25s ease, color 0.25s ease, border-color 0.25s ease, fill 0.25s ease, stroke 0.25s ease;
    }
    .theme-picker {
      display: flex;
      gap: 4px;
      margin-left: auto;
    }
    .theme-btn {
      padding: 3px 8px;
      font-size: 11px;
      border: 1px solid var(--border);
      border-radius: 10px;
      background: transparent;
      color: var(--text-muted);
      cursor: pointer;
      transition: all 0.15s;
      white-space: nowrap;
    }
    .theme-btn:hover { border-color: var(--accent); color: var(--text-primary); }
    .theme-btn.active {
      background: var(--accent-bg);
      border-color: var(--accent);
      color: var(--accent);
    }

    /* ── Sidebar toggle ── */
    .sidebar-toggle {
      position: fixed;
      top: 50%;
      left: 0;
      transform: translateY(-50%);
      z-index: 50;
      width: 20px;
      height: 48px;
      border: 1px solid var(--border);
      border-left: none;
      border-radius: 0 6px 6px 0;
      background: var(--bg-secondary);
      color: var(--text-muted);
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 12px;
      transition: left 0.3s ease, background 0.15s;
    }
    .sidebar-toggle:hover { background: var(--bg-hover); color: var(--accent); }
    #app.sidebar-collapsed aside { display: none; }
    #app.sidebar-collapsed { grid-template-columns: 1fr !important; }
    #app.sidebar-collapsed .sidebar-toggle { left: 0; }

    /* ── Global search overlay (Ctrl+K) ── */
    .global-search-overlay {
      position: fixed;
      inset: 0;
      background: rgba(0,0,0,0.6);
      z-index: 200;
      display: none;
      align-items: flex-start;
      justify-content: center;
      padding-top: 15vh;
    }
    .global-search-overlay.open { display: flex; }
    .global-search-box {
      width: 500px;
      max-width: 90vw;
      background: var(--bg-secondary);
      border: 1px solid var(--border);
      border-radius: 12px;
      box-shadow: 0 20px 60px rgba(0,0,0,0.5);
      overflow: hidden;
    }
    .global-search-input {
      width: 100%;
      padding: 14px 16px;
      background: transparent;
      border: none;
      border-bottom: 1px solid var(--border);
      color: var(--text-primary);
      font-size: 16px;
      outline: none;
    }
    .global-search-input::placeholder { color: var(--text-subtle); }
    .global-search-hint {
      padding: 6px 16px;
      font-size: 11px;
      color: var(--text-subtle);
      display: flex;
      justify-content: space-between;
    }
    .global-search-results {
      list-style: none;
      max-height: 300px;
      overflow-y: auto;
    }
    .global-search-results li {
      padding: 10px 16px;
      cursor: pointer;
      font-size: 14px;
      display: flex;
      align-items: center;
      gap: 8px;
      border-bottom: 1px solid var(--border);
    }
    .global-search-results li:hover,
    .global-search-results li.focused { background: var(--bg-hover); }
    .global-search-results .gs-type {
      font-size: 10px;
      padding: 1px 6px;
      border-radius: 6px;
      white-space: nowrap;
    }
    .global-search-results .gs-page {
      margin-left: auto;
      font-size: 11px;
      color: var(--text-subtle);
    }

    /* ── Export button ── */
    .export-btn {
      padding: 3px 8px;
      font-size: 11px;
      border: 1px solid var(--border);
      border-radius: 10px;
      background: transparent;
      color: var(--text-muted);
      cursor: pointer;
      white-space: nowrap;
    }
    .export-btn:hover { border-color: var(--accent); color: var(--accent); }
    .export-menu {
      position: absolute;
      top: 100%;
      right: 0;
      background: var(--bg-secondary);
      border: 1px solid var(--border);
      border-radius: 8px;
      box-shadow: 0 8px 24px rgba(0,0,0,0.3);
      padding: 4px 0;
      display: none;
      z-index: 60;
      min-width: 160px;
    }
    .export-menu.open { display: block; }
    .export-menu button {
      display: block;
      width: 100%;
      padding: 8px 14px;
      border: none;
      background: transparent;
      color: var(--text-primary);
      font-size: 12px;
      text-align: left;
      cursor: pointer;
    }
    .export-menu button:hover { background: var(--bg-hover); }

    /* ── Loading skeleton ── */
    .skeleton-pulse {
      background: linear-gradient(90deg, var(--bg-tertiary) 25%, var(--bg-hover) 50%, var(--bg-tertiary) 75%);
      background-size: 200% 100%;
      animation: skeleton-shimmer 1.5s infinite;
      border-radius: 4px;
    }
    @keyframes skeleton-shimmer {
      0% { background-position: 200% 0; }
      100% { background-position: -200% 0; }
    }

    /* ── Responsive: collapse sidebar on narrow screens ── */
    @media (max-width: 768px) {
      #app {
        grid-template-columns: 1fr !important;
        grid-template-rows: auto auto 1fr !important;
      }
      header {
        flex-wrap: wrap;
        padding: 8px 12px !important;
        gap: 8px !important;
      }
      header h1 { font-size: 15px !important; }
      aside {
        border-right: none !important;
        border-bottom: 1px solid var(--border);
        max-height: 35vh;
        overflow-y: auto;
      }
      .theme-picker { margin-left: 0; }
      .theme-btn { font-size: 10px; padding: 2px 6px; }
      nav { order: 2; width: 100%; }
      nav a { font-size: 12px; }
    }

    @media (max-width: 480px) {
      header h1 { font-size: 13px !important; }
      aside { max-height: 25vh; padding: 10px !important; }
      .theme-btn { font-size: 9px; padding: 2px 5px; }
    }

    /* ── Skip link for keyboard users ── */
    .skip-link {
      position: absolute;
      top: -40px;
      left: 0;
      background: var(--accent);
      color: var(--text-inverse);
      padding: 8px 16px;
      z-index: 100;
      font-size: 14px;
      text-decoration: none;
      border-radius: 0 0 6px 0;
      transition: top 0.2s;
    }
    .skip-link:focus { top: 0; }

    /* ── Focus visible outlines ── */
    :focus-visible {
      outline: 2px solid var(--accent);
      outline-offset: 2px;
    }
    button:focus-visible, a:focus-visible, input:focus-visible, select:focus-visible {
      outline: 2px solid var(--accent);
      outline-offset: 2px;
    }
  `;
  document.head.appendChild(style);
}

// ── Public API ────────────────────────────────────────────────────────

/**
 * Initialize the theme system. Call once after DOM is ready.
 * Injects CSS variables, renders theme picker in <header>, restores saved preference.
 */
export function initTheme() {
  // Restore saved theme, or detect OS preference
  let hasSaved = false;
  try {
    const saved = localStorage.getItem('theographic-theme');
    if (saved && THEMES[saved]) {
      currentTheme = saved;
      hasSaved = true;
    }
  } catch {}

  if (!hasSaved && window.matchMedia) {
    if (window.matchMedia('(prefers-color-scheme: light)').matches) {
      currentTheme = 'light';
    } else if (window.matchMedia('(prefers-contrast: more)').matches) {
      currentTheme = 'high-contrast';
    }
  }

  injectPickerStyles();
  applyTheme(currentTheme);

  // Add skip link for keyboard accessibility
  const skip = document.createElement('a');
  skip.href = '#main-content';
  skip.className = 'skip-link';
  skip.textContent = 'Skip to content';
  document.body.insertBefore(skip, document.body.firstChild);

  // Mark main content area
  const mainArea = document.querySelector('#graph-container, #sigma-container, #tree-container, #map-container, #timeline-container');
  if (mainArea) mainArea.id = mainArea.id || 'main-content';
  if (mainArea && !mainArea.getAttribute('role')) mainArea.setAttribute('role', 'main');

  const header = document.querySelector('header');
  if (header) renderThemePicker(header);

  // Sidebar toggle
  setupSidebarToggle();

  // Global search (Ctrl/Cmd+K)
  setupGlobalSearch();

  // Export button
  setupExportButton(header);

  // Loading skeleton
  setupLoadingSkeleton();
}

// ── Sidebar Toggle ─────────────────────────────────────────────────────

function setupSidebarToggle() {
  const app = document.getElementById('app');
  const aside = document.querySelector('aside');
  if (!app || !aside) return;

  const btn = document.createElement('button');
  btn.className = 'sidebar-toggle';
  btn.innerHTML = '&#9664;';
  btn.title = 'Toggle sidebar';
  btn.setAttribute('aria-label', 'Toggle sidebar');
  document.body.appendChild(btn);

  // Restore state
  try {
    if (localStorage.getItem('theographic-sidebar') === 'collapsed') {
      app.classList.add('sidebar-collapsed');
      btn.innerHTML = '&#9654;';
    }
  } catch {}

  btn.addEventListener('click', () => {
    const collapsed = app.classList.toggle('sidebar-collapsed');
    btn.innerHTML = collapsed ? '&#9654;' : '&#9664;';
    try { localStorage.setItem('theographic-sidebar', collapsed ? 'collapsed' : 'open'); } catch {}
  });
}

// ── Global Search (Ctrl/Cmd+K) ────────────────────────────────────────

function setupGlobalSearch() {
  const overlay = document.createElement('div');
  overlay.className = 'global-search-overlay';
  overlay.innerHTML = `
    <div class="global-search-box">
      <input class="global-search-input" type="text" placeholder="Search across all views..." autofocus>
      <div class="global-search-hint">
        <span>Type to search people, places, events...</span>
        <span>ESC to close</span>
      </div>
      <ul class="global-search-results"></ul>
    </div>
  `;
  document.body.appendChild(overlay);

  const input = overlay.querySelector('.global-search-input');
  const results = overlay.querySelector('.global-search-results');
  let focusedIdx = -1;

  // Pages for navigation
  const PAGES = {
    Person:      { url: 'tree-view.html',    label: 'Trees' },
    Place:       { url: 'map-view.html',     label: 'Map' },
    Event:       { url: 'timeline-view.html', label: 'Timeline' },
    Book:        { url: 'index.html',        label: 'Explorer' },
    PeopleGroup: { url: 'sigma-graph.html',  label: 'Graph' },
    Easton:      { url: 'sigma-graph.html',  label: 'Graph' },
  };

  function open() {
    overlay.classList.add('open');
    input.value = '';
    results.innerHTML = '';
    focusedIdx = -1;
    setTimeout(() => input.focus(), 50);
  }

  function close() {
    overlay.classList.remove('open');
  }

  function navigate(id, nodeType) {
    const page = PAGES[nodeType] || { url: 'index.html' };
    // Store selection for the target page
    try { localStorage.setItem('theographic-navigate', JSON.stringify({ id, nodeType })); } catch {}
    close();
    // If we're already on the right page, trigger the local search
    const currentPage = window.location.pathname.split('/').pop();
    if (currentPage === page.url) {
      // Find the local search box and fill it
      const localSearch = document.getElementById('search');
      if (localSearch) {
        localSearch.value = '';
        localSearch.dispatchEvent(new Event('input'));
      }
      // Try to call page-specific selection
      if (window.selectResult) window.selectResult(id);
      if (window.selectPerson) window.selectPerson(id);
      if (window.focusNode) window.focusNode(id);
    } else {
      window.location.href = page.url;
    }
  }

  // Keyboard shortcut
  document.addEventListener('keydown', (e) => {
    if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
      e.preventDefault();
      if (overlay.classList.contains('open')) close();
      else open();
    }
    if (e.key === 'Escape' && overlay.classList.contains('open')) {
      close();
    }
  });

  // Close on backdrop click
  overlay.addEventListener('click', (e) => {
    if (e.target === overlay) close();
  });

  // Search input
  let searchTimeout;
  input.addEventListener('input', () => {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => {
      const q = input.value.trim();
      if (q.length < 2) { results.innerHTML = ''; focusedIdx = -1; return; }

      // Use the page's existing search if available via local search box
      const localSearch = document.getElementById('search');
      if (localSearch) {
        // Trigger the same search logic
        localSearch.value = q;
        localSearch.dispatchEvent(new Event('input'));
      }

      // Also show results in global overlay by reading from the local results
      setTimeout(() => {
        const localResults = document.querySelectorAll('#results li');
        const items = [];
        localResults.forEach(li => {
          const onclick = li.getAttribute('onclick') || '';
          const idMatch = onclick.match(/'([^']+)'/);
          const typeTag = li.querySelector('.type-tag');
          if (idMatch) {
            items.push({
              id: idMatch[1],
              label: li.textContent.trim(),
              type: typeTag ? typeTag.textContent.trim() : '',
              color: typeTag ? typeTag.style.color : '',
            });
          }
        });

        results.innerHTML = items.slice(0, 10).map((item, i) =>
          `<li data-id="${item.id}" data-type="${item.type}" class="${i === 0 ? 'focused' : ''}">` +
          `<span class="gs-type" style="background:${item.color}22;color:${item.color}">${item.type}</span>` +
          `${item.label.replace(item.type, '').trim()}` +
          `<span class="gs-page">${PAGES[item.type]?.label || 'Explorer'}</span></li>`
        ).join('');
        focusedIdx = items.length > 0 ? 0 : -1;
      }, 300);
    }, 150);
  });

  // Keyboard navigation in results
  input.addEventListener('keydown', (e) => {
    const items = results.querySelectorAll('li');
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      focusedIdx = Math.min(focusedIdx + 1, items.length - 1);
      items.forEach((li, i) => li.classList.toggle('focused', i === focusedIdx));
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      focusedIdx = Math.max(focusedIdx - 1, 0);
      items.forEach((li, i) => li.classList.toggle('focused', i === focusedIdx));
    } else if (e.key === 'Enter') {
      e.preventDefault();
      const focused = items[focusedIdx];
      if (focused) navigate(focused.dataset.id, focused.dataset.type);
    }
  });

  // Click on result
  results.addEventListener('click', (e) => {
    const li = e.target.closest('li');
    if (li) navigate(li.dataset.id, li.dataset.type);
  });
}

// ── Export Button ──────────────────────────────────────────────────────

function setupExportButton(headerEl) {
  if (!headerEl) return;

  const wrapper = document.createElement('div');
  wrapper.style.cssText = 'position:relative;display:inline-block';

  const btn = document.createElement('button');
  btn.className = 'export-btn';
  btn.textContent = 'Export';
  btn.title = 'Export visualization';

  const menu = document.createElement('div');
  menu.className = 'export-menu';
  menu.innerHTML = `
    <button data-action="png">Save as PNG</button>
    <button data-action="svg">Save as SVG</button>
    <button data-action="json">Export data as JSON</button>
  `;

  wrapper.appendChild(btn);
  wrapper.appendChild(menu);

  // Insert before theme picker
  const picker = headerEl.querySelector('.theme-picker');
  if (picker) headerEl.insertBefore(wrapper, picker);
  else headerEl.appendChild(wrapper);

  btn.addEventListener('click', (e) => {
    e.stopPropagation();
    menu.classList.toggle('open');
  });

  document.addEventListener('click', () => menu.classList.remove('open'));

  menu.addEventListener('click', (e) => {
    const action = e.target.dataset.action;
    if (!action) return;
    menu.classList.remove('open');

    const svgEl = document.querySelector('svg');
    if (!svgEl) return;

    if (action === 'png') {
      exportAsPng(svgEl);
    } else if (action === 'svg') {
      exportAsSvg(svgEl);
    } else if (action === 'json') {
      exportAsJson();
    }
  });
}

function exportAsPng(svgEl) {
  const svgData = new XMLSerializer().serializeToString(svgEl);
  const canvas = document.createElement('canvas');
  const rect = svgEl.getBoundingClientRect();
  canvas.width = rect.width * 2;
  canvas.height = rect.height * 2;
  const ctx = canvas.getContext('2d');
  ctx.scale(2, 2);

  const img = new Image();
  img.onload = () => {
    ctx.fillStyle = themeVar('--bg-primary');
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.drawImage(img, 0, 0, rect.width, rect.height);
    const a = document.createElement('a');
    a.download = 'theographic-export.png';
    a.href = canvas.toDataURL('image/png');
    a.click();
  };
  img.src = 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(svgData);
}

function exportAsSvg(svgEl) {
  const svgData = new XMLSerializer().serializeToString(svgEl);
  const blob = new Blob([svgData], { type: 'image/svg+xml' });
  const a = document.createElement('a');
  a.download = 'theographic-export.svg';
  a.href = URL.createObjectURL(blob);
  a.click();
  URL.revokeObjectURL(a.href);
}

function exportAsJson() {
  // Collect visible data from the page
  const data = {
    page: document.title,
    theme: currentTheme,
    exportedAt: new Date().toISOString(),
    nodes: [],
  };

  // Try to read from local graph state
  document.querySelectorAll('#results li').forEach(li => {
    data.nodes.push({ text: li.textContent.trim() });
  });

  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
  const a = document.createElement('a');
  a.download = 'theographic-export.json';
  a.href = URL.createObjectURL(blob);
  a.click();
  URL.revokeObjectURL(a.href);
}

// ── Loading Skeleton ──────────────────────────────────────────────────

function setupLoadingSkeleton() {
  const aside = document.querySelector('aside');
  if (!aside) return;

  // Show skeleton until #loading is hidden
  const loadingEl = document.getElementById('loading');
  if (!loadingEl || loadingEl.style.display === 'none') return;

  const skeleton = document.createElement('div');
  skeleton.className = 'loading-skeleton';
  skeleton.innerHTML = `
    <div class="skeleton-pulse" style="height:36px;margin-bottom:12px"></div>
    <div style="display:flex;gap:6px;margin-bottom:16px">
      <div class="skeleton-pulse" style="height:24px;flex:1"></div>
      <div class="skeleton-pulse" style="height:24px;flex:1"></div>
      <div class="skeleton-pulse" style="height:24px;flex:1"></div>
    </div>
    <div class="skeleton-pulse" style="height:16px;width:60%;margin-bottom:8px"></div>
    <div class="skeleton-pulse" style="height:16px;width:80%;margin-bottom:8px"></div>
    <div class="skeleton-pulse" style="height:16px;width:45%;margin-bottom:8px"></div>
    <div class="skeleton-pulse" style="height:16px;width:70%;margin-bottom:16px"></div>
    <div class="skeleton-pulse" style="height:100px;margin-bottom:12px"></div>
  `;
  aside.prepend(skeleton);

  // Remove skeleton when loading finishes
  const observer = new MutationObserver(() => {
    if (loadingEl.style.display === 'none') {
      skeleton.remove();
      observer.disconnect();
    }
  });
  observer.observe(loadingEl, { attributes: true, attributeFilter: ['style'] });
}

/**
 * Get TYPE_COLORS object matching the current theme's CSS variables.
 */
export function getTypeColors() {
  const s = getComputedStyle(document.documentElement);
  return {
    Book:        s.getPropertyValue('--color-book').trim(),
    Chapter:     s.getPropertyValue('--color-chapter').trim(),
    Verse:       s.getPropertyValue('--color-verse').trim(),
    Person:      s.getPropertyValue('--color-person').trim(),
    Place:       s.getPropertyValue('--color-place').trim(),
    Event:       s.getPropertyValue('--color-event').trim(),
    PeopleGroup: s.getPropertyValue('--color-group').trim(),
    Easton:      s.getPropertyValue('--color-easton').trim(),
  };
}

/**
 * Get the color for a gender string.
 */
export function getGenderColor(gender) {
  const s = getComputedStyle(document.documentElement);
  if (gender === 'Male') return s.getPropertyValue('--color-male').trim();
  if (gender === 'Female') return s.getPropertyValue('--color-female').trim();
  return s.getPropertyValue('--color-unknown').trim();
}

/**
 * Get a single CSS variable value from the current theme.
 */
export function themeVar(name) {
  return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
}

/**
 * Get the current theme name.
 */
export function getCurrentTheme() {
  return currentTheme;
}

/**
 * Available theme names.
 */
export const themeNames = Object.keys(THEMES);
