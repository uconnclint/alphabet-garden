// textures.js — async texture loading with a cache and a procedural fallback that never lets the game fail to boot.
//
// House rule: **the game must always boot.** School wifi filters, half-deployed asset folders and
// typo'd filenames are facts of life, so a 404 here produces a friendly procedural blob rather
// than an exception. Every failure is warned about exactly once, so the console stays readable.
//
// ── USE ─────────────────────────────────────────────────────────────────────────
//   import * as Textures from './systems/textures.js';
//   Textures.setRenderer(stage.renderer);            // once, for anisotropy support
//   Textures.setBasePath('art/assets/');             // optional; prefixes relative urls
//
//   const tex = await Textures.load('sky/sun.png');           // never rejects
//   const all = await Textures.loadAll(['a.png','b.png']);    // { url: Texture }
//   const now = Textures.get('sky/sun.png');                  // sync: cached, or a placeholder
//
// ── API ─────────────────────────────────────────────────────────────────────────
//   setRenderer(renderer)            enable max anisotropy for downscaled art
//   setBasePath(path)                prefix for relative urls
//   load(url, opts) -> Promise<Texture>       cached, never rejects
//   loadAll(urls, opts) -> Promise<Object>    { url: Texture }
//   get(url) -> Texture|null                  sync cache peek (loads in the background)
//   has(url) -> boolean
//   makeProcedural(opts) -> Texture           roundrect | circle | star | dot | square
//   canvasTexture(canvas) -> Texture          wrap your own canvas with the right settings
//   failures() -> string[]                    urls that fell back (for a debug overlay)
//   dispose(url) / disposeAll()

import * as THREE from '../../vendor/three.module.js';

const cache = new Map();      // url -> THREE.Texture
const inflight = new Map();   // url -> Promise<THREE.Texture>
const warned = new Set();     // urls we have already complained about
const failed = new Set();     // urls that fell back to procedural art

let renderer = null;
let maxAnisotropy = 1;
let basePath = '';

/** Give the loader the renderer so textures can use the GPU's max anisotropy. */
export function setRenderer(r) {
  renderer = r;
  try { maxAnisotropy = r.capabilities.getMaxAnisotropy(); } catch (e) { maxAnisotropy = 1; }
  // Re-apply to anything already loaded so load order does not matter.
  cache.forEach(t => { t.anisotropy = Math.min(8, maxAnisotropy); t.needsUpdate = true; });
}

/** Prefix for relative urls, e.g. 'art/assets/'. Absolute/'./'-prefixed urls are left alone. */
export function setBasePath(p) {
  basePath = p || '';
}

function resolve(url) {
  if (!url) return url;
  if (/^([a-z]+:)?\/\//i.test(url) || url.startsWith('/') || url.startsWith('./') ||
      url.startsWith('../') || url.startsWith('data:')) return url;
  return basePath + url;
}

/**
 * Apply the house filtering setup. Our art is authored large and drawn small, so mipmaps plus
 * anisotropy are what keep leaf edges from crawling on a Chromebook.
 */
function configure(tex, opts) {
  opts = opts || {};
  tex.colorSpace = THREE.SRGBColorSpace;
  tex.magFilter = THREE.LinearFilter;
  const mip = opts.mipmaps !== false;
  tex.generateMipmaps = mip;
  tex.minFilter = mip ? THREE.LinearMipmapLinearFilter : THREE.LinearFilter;
  tex.anisotropy = Math.min(opts.anisotropy || 8, maxAnisotropy);
  tex.wrapS = opts.wrapS || THREE.ClampToEdgeWrapping;
  tex.wrapT = opts.wrapT || THREE.ClampToEdgeWrapping;
  tex.needsUpdate = true;
  return tex;
}

/* ═══════════════════════ procedural fallback art ═══════════════════════ */

function roundRectPath(ctx, x, y, w, h, r) {
  const rr = Math.min(r, w / 2, h / 2);
  ctx.beginPath();
  ctx.moveTo(x + rr, y);
  ctx.arcTo(x + w, y, x + w, y + h, rr);
  ctx.arcTo(x + w, y + h, x, y + h, rr);
  ctx.arcTo(x, y + h, x, y, rr);
  ctx.arcTo(x, y, x + w, y, rr);
  ctx.closePath();
}

/**
 * Draw a simple shape into a canvas texture. Used both as the 404 fallback and as real art
 * for generic particles (dots, squares) so we never ship a file for a white square.
 *
 * @param {object} [o]
 * @param {'roundrect'|'circle'|'star'|'dot'|'square'} [o.shape='roundrect']
 * @param {string} [o.color='#8fd15b'] fill
 * @param {string} [o.stroke] outline colour
 * @param {number} [o.size=128] px (square canvas)
 * @param {number} [o.radius=0.22] corner radius as a fraction of size (roundrect)
 * @param {boolean} [o.soft=false] radial alpha falloff (good for glows / pollen)
 * @param {string} [o.label] a single character drawn in the middle (debug placeholders)
 * @returns {THREE.CanvasTexture}
 */
export function makeProcedural(o) {
  o = o || {};
  const size = o.size || 128;
  const color = o.color || '#8fd15b';
  const shape = o.shape || 'roundrect';

  const cv = document.createElement('canvas');
  cv.width = cv.height = size;
  const ctx = cv.getContext('2d');
  const pad = size * 0.06;
  const inner = size - pad * 2;

  if (o.soft) {
    const g = ctx.createRadialGradient(size / 2, size / 2, 0, size / 2, size / 2, size / 2);
    g.addColorStop(0, color);
    g.addColorStop(0.55, color);
    g.addColorStop(1, 'rgba(255,255,255,0)');
    ctx.fillStyle = g;
    ctx.beginPath();
    ctx.arc(size / 2, size / 2, size / 2, 0, Math.PI * 2);
    ctx.fill();
  } else {
    ctx.fillStyle = color;
    if (shape === 'circle' || shape === 'dot') {
      ctx.beginPath();
      ctx.arc(size / 2, size / 2, inner / 2, 0, Math.PI * 2);
      ctx.fill();
    } else if (shape === 'square') {
      ctx.fillRect(pad, pad, inner, inner);
    } else if (shape === 'star') {
      const spikes = 5, R = inner / 2, r = R * 0.45;
      ctx.beginPath();
      for (let i = 0; i < spikes * 2; i++) {
        const rad = (i % 2 === 0) ? R : r;
        const a = (Math.PI / spikes) * i - Math.PI / 2;
        const px = size / 2 + Math.cos(a) * rad;
        const py = size / 2 + Math.sin(a) * rad;
        i === 0 ? ctx.moveTo(px, py) : ctx.lineTo(px, py);
      }
      ctx.closePath();
      ctx.fill();
    } else {
      roundRectPath(ctx, pad, pad, inner, inner, size * (o.radius != null ? o.radius : 0.22));
      ctx.fill();
    }
    if (o.stroke) {
      ctx.strokeStyle = o.stroke;
      ctx.lineWidth = Math.max(2, size * 0.035);
      ctx.stroke();
    }
  }

  if (o.label) {
    ctx.fillStyle = 'rgba(255,255,255,0.92)';
    ctx.font = 'bold ' + Math.round(size * 0.42) + 'px system-ui, sans-serif';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(String(o.label).slice(0, 2), size / 2, size * 0.54);
  }

  const tex = new THREE.CanvasTexture(cv);
  return configure(tex, o);
}

/** Wrap a canvas you drew yourself with the house texture settings. */
export function canvasTexture(canvas, opts) {
  return configure(new THREE.CanvasTexture(canvas), opts);
}

/**
 * Deterministic-ish placeholder for a missing asset: hue derived from the filename so the same
 * missing file always looks the same across reloads (easier to spot and report).
 */
function placeholderFor(url, opts) {
  let hash = 0;
  const s = String(url);
  for (let i = 0; i < s.length; i++) hash = (hash * 31 + s.charCodeAt(i)) | 0;
  const hue = Math.abs(hash) % 360;
  return makeProcedural(Object.assign({
    shape: 'roundrect',
    color: 'hsl(' + hue + ',68%,62%)',
    stroke: 'hsl(' + hue + ',60%,38%)',
    size: 128
  }, (opts && opts.fallback) || {}));
}

function warnOnce(url, err) {
  if (warned.has(url)) return;
  warned.add(url);
  console.warn('[textures] "' + url + '" failed to load — using procedural fallback art.',
    err && err.message ? err.message : '');
}

/* ═══════════════════════ loading ═══════════════════════ */

const loader = new THREE.TextureLoader();

/**
 * Load a texture. Resolves with a usable texture in every case: real art if the file loads,
 * procedural art if it does not. Never rejects, never throws.
 *
 * @param {string} url relative to basePath, or absolute
 * @param {object} [opts] { mipmaps, anisotropy, wrapS, wrapT, fallback:{shape,color,size} }
 * @returns {Promise<THREE.Texture>}
 */
export function load(url, opts) {
  if (cache.has(url)) return Promise.resolve(cache.get(url));
  if (inflight.has(url)) return inflight.get(url);

  const p = new Promise(res => {
    loader.load(
      resolve(url),
      tex => {
        configure(tex, opts);
        cache.set(url, tex);
        inflight.delete(url);
        res(tex);
      },
      undefined,
      err => {
        warnOnce(url, err);
        failed.add(url);
        const tex = placeholderFor(url, opts);
        cache.set(url, tex);
        inflight.delete(url);
        res(tex);
      }
    );
  });

  inflight.set(url, p);
  return p;
}

/**
 * Load many at once.
 * @param {string[]} urls
 * @returns {Promise<Object<string,THREE.Texture>>} keyed by the url you passed in
 */
export function loadAll(urls, opts) {
  return Promise.all(urls.map(u => load(u, opts))).then(list => {
    const out = {};
    urls.forEach((u, i) => { out[u] = list[i]; });
    return out;
  });
}

/**
 * Synchronous peek. Returns the cached texture, or null if it has not loaded yet
 * (and kicks off the load so a later frame will have it).
 */
export function get(url, opts) {
  if (cache.has(url)) return cache.get(url);
  load(url, opts);
  return null;
}

export function has(url) { return cache.has(url); }

/** Urls that fell back to procedural art — useful for a dev overlay. */
export function failures() { return Array.from(failed); }

export function dispose(url) {
  const t = cache.get(url);
  if (t) { t.dispose(); cache.delete(url); }
}

export function disposeAll() {
  cache.forEach(t => t.dispose());
  cache.clear();
  inflight.clear();
}
