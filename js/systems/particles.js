// particles.js — pooled 2D particle system: one instanced draw call per texture, zero per-frame allocation.
//
// Sparkles when a seed sprouts, confetti when a plant blooms, droplets when you water, a poof of
// dust when you dig, and slow pollen motes drifting across the garden all the time.
//
// ── HOW IT WORKS ────────────────────────────────────────────────────────────────
// Particles are instanced quads (InstancedBufferGeometry + a tiny ShaderMaterial), batched by
// texture+blend mode. That means N particles cost one draw call, and the pool is preallocated so
// a burst never triggers GC mid-animation — the thing that makes Chromebooks stutter.
//
// ── USE ─────────────────────────────────────────────────────────────────────────
//   import { createParticles } from './systems/particles.js';
//   const fx = createParticles(stage);              // auto-attaches to stage.onUpdate
//   fx.emit('sparkle', x, y);                       // x/y in WORLD units (same space as sprites)
//   fx.emit('confetti', 0, 200, { count: 60 });
//   const motes = fx.ambient('pollen');             // handle.cancel() to stop
//
// Presets: sparkle, confetti, waterDroplets, poof, pollen.
// Add your own with fx.definePreset('name', {...}) — see PRESETS below for every field.
//
// ── LIMITS & REDUCED MOTION ─────────────────────────────────────────────────────
// A hard `max` (default 700) caps live particles; emits past it are silently trimmed, never
// dropped entirely, so feedback still happens. Under reduced motion counts are cut to ~30%
// (minimum 1, so an action still reads as "something happened") and ambient emitters are off.
//
// ── API ─────────────────────────────────────────────────────────────────────────
//   createParticles(stage, opts) -> fx
//   fx.emit(preset, x, y, overrides) -> number spawned
//   fx.ambient(preset, opts) -> { cancel(), setRate(n) }
//   fx.definePreset(name, cfg) / fx.presets
//   fx.update(dt) / fx.clear() / fx.dispose() / fx.count / fx.max

import * as THREE from '../../vendor/three.module.js';
import * as Textures from './textures.js';
import { isReducedMotion } from './tween.js';

/* ═══════════════════════ shaders ═══════════════════════ */

const VERT = `
attribute vec3 iOffset;
attribute vec2 iScale;
attribute float iRot;
attribute vec3 iColor;
attribute float iAlpha;
varying vec2 vUv;
varying vec3 vColor;
varying float vAlpha;
void main() {
  vUv = uv;
  vColor = iColor;
  vAlpha = iAlpha;
  float c = cos(iRot), s = sin(iRot);
  vec2 p = position.xy * iScale;
  vec2 r = vec2(p.x * c - p.y * s, p.x * s + p.y * c);
  gl_Position = projectionMatrix * modelViewMatrix * vec4(iOffset + vec3(r, 0.0), 1.0);
}`;

// The renderer's fragment prefix always supplies linearToOutputTexel (via <colorspace_fragment>),
// but nothing decodes an sRGB *input* texture inside a custom shader — so we do it by hand.
const FRAG = `
uniform sampler2D map;
varying vec2 vUv;
varying vec3 vColor;
varying float vAlpha;
vec3 srgbToLinear(vec3 v) {
  return mix(pow((v + 0.055) / 1.055, vec3(2.4)), v / 12.92, vec3(lessThanEqual(v, vec3(0.04045))));
}
void main() {
  vec4 t = texture2D(map, vUv);
  if (t.a <= 0.001) discard;
  gl_FragColor = vec4(srgbToLinear(t.rgb) * vColor, t.a * vAlpha);
  #include <colorspace_fragment>
}`;

/* ═══════════════════════ presets ═══════════════════════ */

/**
 * Every field is optional. Ranges are [min, max] and picked uniformly per particle.
 *
 *  texture   {string}  url passed to textures.js (404 → procedural fallback, game still boots)
 *  fallback  {object}  procedural spec used if the texture is missing ({shape,color,soft,size})
 *  additive  {boolean} additive blending (glows, sparkles)
 *  count     {[n,n]}   particles per emit()
 *  life      {[ms,ms]}
 *  size      {[u,u]}   world units
 *  aspect    {[n,n]}   width/height ratio (confetti strips)
 *  angle     {[r,r]}   emission direction, radians, 0 = +X, PI/2 = up
 *  speed     {[u,u]}   world units per second
 *  spread    {number}  extra random position offset at spawn, world units
 *  gravity   {number}  world units/s² (negative pulls down; +Y is up)
 *  drag      {number}  velocity retained per second (1 = none, 0.2 = heavy air)
 *  spin      {[r,r]}   radians per second
 *  spinMag   {[r,r]}   radians per second as a MAGNITUDE, sign randomised per particle
 *                      (use instead of `spin` when every particle must actually tumble)
 *  scale     {[n,n]}   size multiplier at birth → death
 *  fadeIn    {number}  fraction of life spent fading in (0..1)
 *  fadeOut   {number}  fraction of life spent fading out (0..1)
 *  alpha     {number}  peak alpha
 *  colors    {string[]} birth colour choices (hex)
 *  colorTo   {string}  colour at death (defaults to the birth colour)
 *  drift     {[u,u]}   sideways sine drift amplitude (pollen, floaty things)
 *  driftHz   {[n,n]}   drift frequency
 *  rate      {number}  default particles/second for ambient()
 */
const PRESETS = {
  sparkle: {
    texture: 'fx/sparkle.png',
    fallback: { shape: 'star', color: '#fff6c2', soft: false },
    additive: true,
    count: [10, 16], life: [420, 820], size: [22, 46],
    angle: [0, Math.PI * 2], speed: [90, 260], spread: 12,
    gravity: -60, drag: 0.25, spin: [-3, 3],
    scale: [1, 0.15], fadeIn: 0.08, fadeOut: 0.55, alpha: 1,
    colors: ['#fff8d0', '#ffe680', '#fffbe9', '#bff0ff']
  },

  // Straight off the house spec sheet: 10–20 pieces (NOT 60 — a 200-piece dump is an instant
  // tell), each a flat chip in a scene-palette colour, launched 300–500 u/s upward-biased,
  // pulled down at 900–1400 u/s², spinning 180–540°/s, alive 700–1100ms and fading only in the
  // last 25%. Flat and opaque on purpose: additive glow blobs are the #1 particle tell.
  confetti: {
    texture: null, // procedural: a plain rounded chip is cheaper and crisper than a PNG
    fallback: { shape: 'roundrect', color: '#ffffff', radius: 0.3, size: 64 },
    additive: false,
    count: [12, 18], life: [700, 1100], size: [16, 30], aspect: [0.35, 0.75],
    angle: [Math.PI * 0.22, Math.PI * 0.78], speed: [300, 500], spread: 20,
    gravity: -1150, drag: 0.72,
    // 180–540°/s, sign picked per particle — a plain [-9.4, 9.4] range would hand half the
    // chips a spin near zero, and a chip that does not tumble reads as a falling brick.
    spinMag: [Math.PI, Math.PI * 3],
    scale: [1, 1], fadeIn: 0.02, fadeOut: 0.25, alpha: 1,
    colors: ['#ff8a3d', '#ffd23f', '#7ecbf2', '#8fd15b', '#f2a3c7', '#fff0c2']
  },

  waterDroplets: {
    texture: 'fx/water_splash.png',
    fallback: { shape: 'circle', color: '#7fd4ff', soft: true },
    additive: false,
    count: [12, 20], life: [420, 760], size: [16, 34],
    angle: [Math.PI * 0.18, Math.PI * 0.82], speed: [160, 380], spread: 14,
    gravity: -1400, drag: 0.85, spin: [-1.5, 1.5],
    scale: [1, 0.55], fadeIn: 0, fadeOut: 0.4, alpha: 0.95,
    colors: ['#9fe2ff', '#6cc6f5', '#d6f4ff']
  },

  poof: {
    texture: 'fx/poof_cloud.png',
    fallback: { shape: 'circle', color: '#e6dcc8', soft: true },
    additive: false,
    count: [7, 11], life: [520, 900], size: [50, 96],
    angle: [0, Math.PI * 2], speed: [40, 140], spread: 16,
    gravity: 30, drag: 0.2, spin: [-1.2, 1.2],
    scale: [0.6, 1.9], fadeIn: 0.1, fadeOut: 0.7, alpha: 0.75,
    colors: ['#efe6d4', '#ded1b8', '#fffaf0']
  },

  // Ambient motes. Emitted continuously by fx.ambient('pollen'), not in bursts.
  pollen: {
    texture: null,
    fallback: { shape: 'circle', color: '#fff3b0', soft: true, size: 64 },
    additive: true,
    count: [1, 1], life: [6000, 11000], size: [7, 16],
    angle: [Math.PI * 0.35, Math.PI * 0.65], speed: [8, 26], spread: 0,
    gravity: 4, drag: 0.9, spin: [-0.5, 0.5],
    scale: [1, 1], fadeIn: 0.18, fadeOut: 0.35, alpha: 0.6,
    colors: ['#fff3b0', '#ffe9d0', '#eaffc9'],
    drift: [18, 46], driftHz: [0.12, 0.35],
    rate: 5
  }
};

/* ═══════════════════════ helpers ═══════════════════════ */

function rng(range, fallback) {
  if (!range) return fallback;
  if (typeof range === 'number') return range;
  return range[0] + Math.random() * (range[1] - range[0]);
}
function pick(arr) { return arr[(Math.random() * arr.length) | 0]; }

const _c = new THREE.Color();
function hexToLinearRGB(hex, out) {
  _c.set(hex).convertSRGBToLinear();
  out[0] = _c.r; out[1] = _c.g; out[2] = _c.b;
  return out;
}

/* ═══════════════════════ system ═══════════════════════ */

/**
 * @param {object} stage from stage.js
 * @param {object} [opts]
 * @param {number} [opts.max=700] hard cap on live particles
 * @param {string} [opts.layer='fx'] which stage layer to draw into
 * @param {boolean} [opts.autoUpdate=true] register with stage.onUpdate automatically
 * @param {number} [opts.reducedScale=0.3] count multiplier under reduced motion
 * @returns {object} fx
 */
export function createParticles(stage, opts = {}) {
  const max = opts.max || 700;
  const layer = stage.layers[opts.layer || 'fx'] || stage.layers.fx;
  const reducedScale = opts.reducedScale != null ? opts.reducedScale : 0.3;

  const presets = Object.assign({}, PRESETS);

  /* ── pooled particle records (preallocated; never resized) ────────────── */
  const pool = new Array(max);
  const free = new Array(max);
  for (let i = 0; i < max; i++) {
    pool[i] = {
      alive: false, batch: null,
      x: 0, y: 0, vx: 0, vy: 0,
      age: 0, life: 1,
      size: 1, aspect: 1, rot: 0, spin: 0,
      s0: 1, s1: 1, fadeIn: 0, fadeOut: 0.4, alpha: 1,
      c0: [1, 1, 1], c1: [1, 1, 1],
      gravity: 0, drag: 1,
      driftAmp: 0, driftHz: 0, driftPhase: 0, baseX: 0
    };
    free[i] = i;
  }
  let freeTop = max; // free[0..freeTop-1] are available indices
  let live = 0;

  /* ── batches: one instanced mesh per texture+blend ────────────────────── */
  const batches = new Map();

  function batchFor(cfg) {
    const key = (cfg.texture || 'proc:' + JSON.stringify(cfg.fallback || {})) +
                (cfg.additive ? '|add' : '|norm');
    let b = batches.get(key);
    if (b) return b;

    const geo = new THREE.InstancedBufferGeometry();
    // A unit quad centred on the origin; instances scale/rotate/translate it in the vertex shader.
    geo.setAttribute('position', new THREE.Float32BufferAttribute(
      [-0.5, -0.5, 0, 0.5, -0.5, 0, 0.5, 0.5, 0, -0.5, 0.5, 0], 3));
    geo.setAttribute('uv', new THREE.Float32BufferAttribute([0, 0, 1, 0, 1, 1, 0, 1], 2));
    geo.setIndex([0, 1, 2, 0, 2, 3]);

    const mk = (name, size) => {
      const a = new THREE.InstancedBufferAttribute(new Float32Array(max * size), size);
      a.setUsage(THREE.DynamicDrawUsage);
      geo.setAttribute(name, a);
      return a;
    };
    const attrs = {
      iOffset: mk('iOffset', 3),
      iScale: mk('iScale', 2),
      iRot: mk('iRot', 1),
      iColor: mk('iColor', 3),
      iAlpha: mk('iAlpha', 1)
    };
    geo.instanceCount = 0;

    // Start with procedural art so the first frame after boot already draws something;
    // the real PNG (if any) swaps in when it arrives.
    const placeholder = Textures.makeProcedural(
      Object.assign({ shape: 'circle', color: '#ffffff', size: 64 }, cfg.fallback || {}));

    const mat = new THREE.ShaderMaterial({
      uniforms: { map: { value: placeholder } },
      vertexShader: VERT,
      fragmentShader: FRAG,
      transparent: true,
      depthTest: false,
      depthWrite: false,
      blending: cfg.additive ? THREE.AdditiveBlending : THREE.NormalBlending
    });

    if (cfg.texture) {
      Textures.load(cfg.texture, { fallback: cfg.fallback }).then(t => { mat.uniforms.map.value = t; });
    }

    const mesh = new THREE.Mesh(geo, mat);
    mesh.frustumCulled = false; // particles live all over the screen; the bounding quad lies
    mesh.renderOrder = cfg.additive ? 2 : 1;
    layer.add(mesh);

    b = { key, geo, mat, mesh, attrs, count: 0, placeholder };
    batches.set(key, b);
    return b;
  }

  /* ── emitting ─────────────────────────────────────────────────────────── */

  function spawnOne(cfg, batch, x, y) {
    if (freeTop === 0) return false;
    const p = pool[free[--freeTop]];
    live++;

    const spread = cfg.spread || 0;
    p.alive = true;
    p.batch = batch;
    p.x = x + (Math.random() - 0.5) * 2 * spread;
    p.y = y + (Math.random() - 0.5) * 2 * spread;
    p.baseX = p.x;

    const ang = rng(cfg.angle, Math.random() * Math.PI * 2);
    const spd = rng(cfg.speed, 100);
    p.vx = Math.cos(ang) * spd;
    p.vy = Math.sin(ang) * spd;

    p.age = 0;
    p.life = rng(cfg.life, 800);
    p.size = rng(cfg.size, 24);
    p.aspect = rng(cfg.aspect, 1);
    p.rot = Math.random() * Math.PI * 2;
    p.spin = cfg.spinMag
      ? rng(cfg.spinMag, 0) * (Math.random() < 0.5 ? -1 : 1)
      : rng(cfg.spin, 0);
    p.s0 = cfg.scale ? cfg.scale[0] : 1;
    p.s1 = cfg.scale ? cfg.scale[1] : 1;
    p.fadeIn = cfg.fadeIn != null ? cfg.fadeIn : 0.05;
    p.fadeOut = cfg.fadeOut != null ? cfg.fadeOut : 0.4;
    p.alpha = cfg.alpha != null ? cfg.alpha : 1;
    p.gravity = cfg.gravity || 0;
    p.drag = cfg.drag != null ? cfg.drag : 1;
    p.driftAmp = rng(cfg.drift, 0);
    p.driftHz = rng(cfg.driftHz, 0);
    p.driftPhase = Math.random() * Math.PI * 2;

    const from = cfg.colors ? pick(cfg.colors) : '#ffffff';
    hexToLinearRGB(from, p.c0);
    hexToLinearRGB(cfg.colorTo || from, p.c1);
    return true;
  }

  /**
   * Burst particles at a world position.
   * @param {string|object} preset preset name, or an inline config object
   * @param {number} x world units
   * @param {number} y world units
   * @param {object} [overrides] any preset field, plus `count` as a plain number
   * @returns {number} how many actually spawned (0 if the cap was already reached)
   */
  function emit(preset, x, y, overrides) {
    const base = typeof preset === 'string' ? presets[preset] : preset;
    if (!base) { console.warn('[particles] unknown preset "' + preset + '"'); return 0; }
    const cfg = overrides ? Object.assign({}, base, overrides) : base;

    let n = Math.round(rng(cfg.count, 10));
    if (isReducedMotion()) n = Math.max(1, Math.round(n * reducedScale));
    n = Math.min(n, max - live);
    if (n <= 0) return 0;

    const batch = batchFor(cfg);
    let spawned = 0;
    for (let i = 0; i < n; i++) if (spawnOne(cfg, batch, x, y)) spawned++;
    return spawned;
  }

  /* ── ambient (continuous) emitters ────────────────────────────────────── */

  const ambients = [];

  /**
   * Continuous emitter, e.g. pollen drifting across the whole garden.
   * Disabled entirely under reduced motion — ambient drift is precisely what motion-sensitive
   * players ask us to turn off.
   *
   * @param {string|object} preset
   * @param {object} [o] { rate=preset.rate, area:{x,y,w,h} (default: the whole screen) }
   * @returns {object} { cancel(), setRate(n) }
   */
  function ambient(preset, o) {
    o = o || {};
    const base = typeof preset === 'string' ? presets[preset] : preset;
    if (!base) { console.warn('[particles] unknown preset "' + preset + '"'); return { cancel() {}, setRate() {} }; }
    const cfg = o.overrides ? Object.assign({}, base, o.overrides) : base;

    const handle = {
      cfg,
      rate: o.rate != null ? o.rate : (cfg.rate || 4),
      area: o.area || null,
      acc: 0,
      dead: false,
      cancel() { this.dead = true; },
      setRate(n) { this.rate = n; }
    };
    ambients.push(handle);
    return handle;
  }

  /* ── update ───────────────────────────────────────────────────────────── */

  function update(dt) {
    // Spawn from ambient emitters first so new motes get a frame of motion this tick.
    if (!isReducedMotion()) {
      for (let i = ambients.length - 1; i >= 0; i--) {
        const a = ambients[i];
        if (a.dead) { ambients.splice(i, 1); continue; }
        a.acc += a.rate * dt;
        while (a.acc >= 1) {
          a.acc -= 1;
          const area = a.area || {
            x: stage.bounds.left, y: stage.bounds.bottom,
            w: stage.worldWidth, h: stage.worldHeight
          };
          emit(a.cfg, area.x + Math.random() * area.w, area.y + Math.random() * area.h, { count: 1 });
        }
      }
    }

    // Integrate, then write straight into the instance buffers. One pass, no allocation.
    batches.forEach(b => { b.count = 0; });

    const dtms = dt * 1000;
    for (let i = 0; i < max; i++) {
      const p = pool[i];
      if (!p.alive) continue;

      p.age += dtms;
      if (p.age >= p.life) {
        p.alive = false;
        p.batch = null;
        free[freeTop++] = i;
        live--;
        continue;
      }

      const t = p.age / p.life;

      p.vy += p.gravity * dt;
      if (p.drag !== 1) {
        const k = Math.pow(p.drag, dt);
        p.vx *= k; p.vy *= k;
      }
      p.x += p.vx * dt;
      p.y += p.vy * dt;
      p.rot += p.spin * dt;

      let px = p.x;
      if (p.driftAmp) {
        px += Math.sin(p.age / 1000 * p.driftHz * Math.PI * 2 + p.driftPhase) * p.driftAmp;
      }

      // alpha envelope: fade in, hold, fade out
      let a = p.alpha;
      if (p.fadeIn > 0 && t < p.fadeIn) a *= t / p.fadeIn;
      const outStart = 1 - p.fadeOut;
      if (p.fadeOut > 0 && t > outStart) a *= 1 - (t - outStart) / p.fadeOut;

      const s = p.size * (p.s0 + (p.s1 - p.s0) * t);

      const b = p.batch;
      const n = b.count++;
      const off = b.attrs.iOffset.array;
      off[n * 3] = px; off[n * 3 + 1] = p.y; off[n * 3 + 2] = 0;
      const sc = b.attrs.iScale.array;
      sc[n * 2] = s * p.aspect; sc[n * 2 + 1] = s;
      b.attrs.iRot.array[n] = p.rot;
      const col = b.attrs.iColor.array;
      col[n * 3] = p.c0[0] + (p.c1[0] - p.c0[0]) * t;
      col[n * 3 + 1] = p.c0[1] + (p.c1[1] - p.c0[1]) * t;
      col[n * 3 + 2] = p.c0[2] + (p.c1[2] - p.c0[2]) * t;
      b.attrs.iAlpha.array[n] = a;
    }

    batches.forEach(b => {
      b.geo.instanceCount = b.count;
      if (b.count > 0) {
        b.attrs.iOffset.needsUpdate = true;
        b.attrs.iScale.needsUpdate = true;
        b.attrs.iRot.needsUpdate = true;
        b.attrs.iColor.needsUpdate = true;
        b.attrs.iAlpha.needsUpdate = true;
      }
      b.mesh.visible = b.count > 0;
    });
  }

  /** Kill every live particle immediately. */
  function clear() {
    for (let i = 0; i < max; i++) {
      if (pool[i].alive) { pool[i].alive = false; pool[i].batch = null; }
    }
    freeTop = max;
    for (let i = 0; i < max; i++) free[i] = i;
    live = 0;
    batches.forEach(b => { b.count = 0; b.geo.instanceCount = 0; b.mesh.visible = false; });
  }

  let detach = null;
  if (opts.autoUpdate !== false) detach = stage.onUpdate(update);

  function dispose() {
    if (detach) detach();
    ambients.length = 0;
    batches.forEach(b => {
      layer.remove(b.mesh);
      b.geo.dispose();
      b.mat.dispose();
      b.placeholder.dispose();
    });
    batches.clear();
  }

  /** Register a custom preset (or override a built-in one). */
  function definePreset(name, cfg) { presets[name] = cfg; return cfg; }

  return {
    emit, ambient, update, clear, dispose, definePreset,
    presets,
    max,
    get count() { return live; },
    get batchCount() { return batches.size; }
  };
}

/** The built-in preset table, for reference or cloning. */
export { PRESETS };
