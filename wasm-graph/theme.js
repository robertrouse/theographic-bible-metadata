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
