/**
 * Performance optimizations module.
 *
 * - JSON data caching via Cache API (or localStorage fallback)
 * - Virtual scroll helper for large lists
 * - Debounced search with AbortController
 * - Lazy rendering with requestIdleCallback
 *
 * Usage:
 *   import { cachedFetch, VirtualScroller, debouncedSearch, idleRender } from './perf.js';
 */

const CACHE_NAME = 'theographic-data-v1';
const CACHE_TTL = 24 * 60 * 60 * 1000; // 24 hours

// ── Cached Fetch ──────────────────────────────────────────────────────

/**
 * Fetch JSON files with Cache API caching.
 * Falls back to regular fetch if Cache API isn't available.
 *
 * @param {string} url - URL to fetch
 * @returns {Promise<string>} - Response text
 */
export async function cachedFetch(url) {
  // Try Cache API
  if ('caches' in self) {
    try {
      const cache = await caches.open(CACHE_NAME);
      const cached = await cache.match(url);
      if (cached) {
        // Check if cache is fresh
        const cacheDate = cached.headers.get('x-cache-date');
        if (cacheDate && Date.now() - parseInt(cacheDate) < CACHE_TTL) {
          return await cached.text();
        }
      }

      // Fetch fresh
      const response = await fetch(url);
      const text = await response.text();

      // Store in cache with timestamp
      const headers = new Headers(response.headers);
      headers.set('x-cache-date', Date.now().toString());
      const cachedResponse = new Response(text, { headers });
      await cache.put(url, cachedResponse);

      return text;
    } catch {
      // Fall through to regular fetch
    }
  }

  // Fallback: regular fetch
  const resp = await fetch(url);
  return await resp.text();
}

/**
 * Load all 8 JSON files with caching and progress callback.
 *
 * @param {function} onProgress - Called with (filename, index, total)
 * @returns {Promise<object>} - Map of { books, chapters, verses, ... } as text
 */
export async function loadAllJSON(onProgress) {
  const files = ['books', 'chapters', 'verses', 'people', 'places', 'events', 'peopleGroups', 'easton'];
  const jsonData = {};

  // Fetch in parallel for speed
  const promises = files.map(async (name, i) => {
    if (onProgress) onProgress(name, i, files.length);
    jsonData[name] = await cachedFetch(`../JSON/${name}.json`);
  });

  await Promise.all(promises);
  return jsonData;
}

/**
 * Clear the data cache.
 */
export async function clearCache() {
  if ('caches' in self) {
    await caches.delete(CACHE_NAME);
  }
}

// ── Virtual Scroller ──────────────────────────────────────────────────

/**
 * Virtual scroll for large lists.
 * Only renders visible items, dramatically reducing DOM nodes.
 *
 * @example
 * const scroller = new VirtualScroller({
 *   container: document.getElementById('results'),
 *   itemHeight: 32,
 *   renderItem: (item, index) => `<li>${item.label}</li>`,
 * });
 * scroller.setItems(largeArray);
 */
export class VirtualScroller {
  constructor({ container, itemHeight = 32, renderItem, overscan = 5 }) {
    this.container = container;
    this.itemHeight = itemHeight;
    this.renderItem = renderItem;
    this.overscan = overscan;
    this.items = [];
    this.scrollTop = 0;

    // Create inner container for scroll height
    this.inner = document.createElement('div');
    this.inner.style.position = 'relative';
    this.viewport = document.createElement('div');
    this.viewport.style.position = 'absolute';
    this.viewport.style.top = '0';
    this.viewport.style.left = '0';
    this.viewport.style.right = '0';
    this.inner.appendChild(this.viewport);
    this.container.innerHTML = '';
    this.container.appendChild(this.inner);

    this.container.addEventListener('scroll', () => {
      this.scrollTop = this.container.scrollTop;
      this.render();
    });
  }

  setItems(items) {
    this.items = items;
    this.inner.style.height = (items.length * this.itemHeight) + 'px';
    this.render();
  }

  render() {
    const containerHeight = this.container.clientHeight;
    const startIdx = Math.max(0, Math.floor(this.scrollTop / this.itemHeight) - this.overscan);
    const endIdx = Math.min(
      this.items.length,
      Math.ceil((this.scrollTop + containerHeight) / this.itemHeight) + this.overscan
    );

    let html = '';
    for (let i = startIdx; i < endIdx; i++) {
      const top = i * this.itemHeight;
      html += `<div style="position:absolute;top:${top}px;left:0;right:0;height:${this.itemHeight}px">` +
        this.renderItem(this.items[i], i) +
        `</div>`;
    }

    this.viewport.innerHTML = html;
  }

  destroy() {
    this.container.innerHTML = '';
  }
}

// ── Debounced Search ──────────────────────────────────────────────────

/**
 * Create a debounced search function that cancels previous pending searches.
 *
 * @param {function} searchFn - Async function that performs the search
 * @param {number} delay - Debounce delay in ms
 * @returns {{ search: function, cancel: function }}
 */
export function debouncedSearch(searchFn, delay = 200) {
  let timer = null;
  let controller = null;

  function search(...args) {
    // Cancel previous
    if (timer) clearTimeout(timer);
    if (controller) controller.abort();

    return new Promise((resolve) => {
      timer = setTimeout(async () => {
        controller = new AbortController();
        try {
          const result = await searchFn(...args, controller.signal);
          resolve(result);
        } catch (e) {
          if (e.name !== 'AbortError') throw e;
        }
      }, delay);
    });
  }

  function cancel() {
    if (timer) clearTimeout(timer);
    if (controller) controller.abort();
  }

  return { search, cancel };
}

// ── Idle Rendering ────────────────────────────────────────────────────

/**
 * Schedule rendering work during idle periods.
 * Falls back to setTimeout if requestIdleCallback isn't available.
 *
 * @param {function[]} tasks - Array of functions to execute
 * @param {function} onComplete - Called when all tasks are done
 */
export function idleRender(tasks, onComplete) {
  const idle = window.requestIdleCallback || ((cb) => setTimeout(cb, 16));
  let index = 0;

  function processNext(deadline) {
    while (index < tasks.length) {
      // Check if we have time remaining (or use 10ms budget for setTimeout fallback)
      const timeRemaining = deadline?.timeRemaining?.() ?? 10;
      if (timeRemaining < 1) {
        idle(processNext);
        return;
      }
      tasks[index]();
      index++;
    }
    if (onComplete) onComplete();
  }

  idle(processNext);
}

/**
 * Batch DOM updates to minimize reflows.
 *
 * @param {function} updateFn - Function that performs DOM updates
 */
export function batchDOM(updateFn) {
  requestAnimationFrame(() => {
    updateFn();
  });
}

// ── Memoized Graph Queries ────────────────────────────────────────────

/**
 * LRU cache for expensive graph queries.
 */
export class QueryCache {
  constructor(maxSize = 100) {
    this.maxSize = maxSize;
    this.cache = new Map();
  }

  get(key) {
    if (!this.cache.has(key)) return undefined;
    // Move to end (most recently used)
    const val = this.cache.get(key);
    this.cache.delete(key);
    this.cache.set(key, val);
    return val;
  }

  set(key, value) {
    if (this.cache.has(key)) {
      this.cache.delete(key);
    } else if (this.cache.size >= this.maxSize) {
      // Delete oldest
      const firstKey = this.cache.keys().next().value;
      this.cache.delete(firstKey);
    }
    this.cache.set(key, value);
  }

  clear() {
    this.cache.clear();
  }
}
