// stage.js — the Three.js rendering core: orthographic 2D stage, named layers, resize, fixed-step loop.
//
// This is a 2D game drawn with WebGL. There is no perspective, no lighting, no depth buffer —
// just layered sprites in a resolution-independent "design space".
//
// ── DESIGN SPACE ────────────────────────────────────────────────────────────────
// The camera always shows exactly `designHeight` world units vertically (default 1000).
// Width is derived from the viewport aspect, so it changes between phone/tablet/desktop.
// Origin (0,0) is the centre of the screen, +X right, +Y UP (Three convention, not DOM).
// Layout math should therefore key off `stage.bounds` / `stage.worldWidth`, never off pixels.
//
//   const s = createStage({ container: document.body });
//   sprite.position.set(0, s.bounds.top - 120, 0);   // 120 units below the top edge
//   s.layers.sky.add(sprite);
//
// ── LAYERS ──────────────────────────────────────────────────────────────────────
// Back-to-front: sky, farParallax, midParallax, ground, plots, plants, critters, fx, ui.
// Each is a THREE.Group at a stepped z. Add to a layer, never to `stage.scene` directly —
// transparent sprites are sorted by distance, so the z step is what guarantees draw order.
//
// ── LOOP ────────────────────────────────────────────────────────────────────────
//   stage.onUpdate(dt => ...)   fixed timestep, dt is ALWAYS the same (default 1/60 s)
//   stage.onDraw((alpha, dt) => ...)  once per rendered frame; alpha = 0..1 interpolation
//   stage.onResize(({ worldWidth, worldHeight, bounds }) => ...)  fires immediately too
//
// ── API ─────────────────────────────────────────────────────────────────────────
//   createStage(opts) -> stage
//   createSprite(texture, opts) -> THREE.Sprite       // aspect-correct 2D sprite helper
//   LAYER_NAMES, DESIGN_HEIGHT
//
// stage: { THREE, renderer, scene, camera, canvas, layers, worldWidth, worldHeight, bounds,
//          designHeight, pxPerUnit, unitsPerPx, dpr, elapsed, frames,
//          onUpdate, onDraw, onResize, refresh, toWorld, start, stop, dispose,
//          isContextLost, setBackground }

import * as THREE from '../../vendor/three.module.js';

export { THREE };

/** Vertical size of the world in design units. Everything lays out against this. */
export const DESIGN_HEIGHT = 1000;

/** Back-to-front layer names. Index * LAYER_Z_STEP is each group's z. */
export const LAYER_NAMES = [
  'sky',          // flat background gradient / sky colour plate
  'farParallax',  // distant hills, far clouds
  'midParallax',  // nearer hills, fence line
  'ground',       // the dirt/grass plate the garden sits on
  'plots',        // plot tiles, seed holes, plot UI chrome
  'plants',       // the growing plants themselves
  'critters',     // bees, butterflies, birds
  'fx',           // particles, splashes, celebration bursts
  'ui'            // in-world HUD, buttons, modal scrims
];

const LAYER_Z_STEP = 10;

/** Hard cap from the house style: retina above this buys nothing and costs Chromebook framerate. */
const MAX_DPR = 1.75;

/** A tab that was backgrounded for 30s must not deliver a 30s dt. */
const MAX_DELTA = 0.25;

/** Never run more than this many logic steps in one frame — prevents the spiral of death. */
const MAX_STEPS_PER_FRAME = 5;

/**
 * Create the stage. Call once.
 *
 * @param {object}  [opts]
 * @param {Element} [opts.container=document.body] element the canvas is appended to
 * @param {number}  [opts.designHeight=1000] world units visible vertically
 * @param {number|string} [opts.background=null] clear colour, or null for transparent
 * @param {number}  [opts.fixedStep=1/60] seconds per logic step
 * @param {number}  [opts.maxDPR=1.75]
 * @param {boolean} [opts.antialias=true]
 * @param {boolean} [opts.autoStart=true]
 * @returns {object} stage
 */
export function createStage(opts = {}) {
  const container = opts.container || document.body;
  const designHeight = opts.designHeight || DESIGN_HEIGHT;
  const fixedStep = opts.fixedStep || 1 / 60;
  const maxDPR = opts.maxDPR || MAX_DPR;

  // ── renderer ──────────────────────────────────────────────────────────────
  const renderer = new THREE.WebGLRenderer({
    antialias: opts.antialias !== false,
    alpha: true,
    powerPreference: 'high-performance',
    // Chromebooks lose contexts on tab switch; without this the restore path never fires cleanly.
    preserveDrawingBuffer: false
  });
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.setClearColor(0x000000, 0);
  renderer.autoClear = true;

  const canvas = renderer.domElement;
  canvas.style.display = 'block';
  canvas.style.width = '100%';
  canvas.style.height = '100%';
  // Pointer Events only — without this iOS steals drags for scroll/zoom before we see them.
  canvas.style.touchAction = 'none';
  container.appendChild(canvas);

  // ── scene + camera ────────────────────────────────────────────────────────
  const scene = new THREE.Scene();
  // Frustum is rewritten on every resize; these are placeholders.
  const camera = new THREE.OrthographicCamera(-1, 1, 1, -1, 0.1, 2000);
  camera.position.set(0, 0, 1000);

  const layers = Object.create(null);
  LAYER_NAMES.forEach((name, i) => {
    const g = new THREE.Group();
    g.name = name;
    g.position.z = i * LAYER_Z_STEP;
    scene.add(g);
    layers[name] = g;
  });

  // ── public size state ─────────────────────────────────────────────────────
  const stage = {
    THREE,
    renderer, scene, camera, canvas, layers, container,
    designHeight,
    worldWidth: designHeight,
    worldHeight: designHeight,
    bounds: { left: 0, right: 0, top: 0, bottom: 0 },
    cssWidth: 1, cssHeight: 1,
    pxPerUnit: 1,   // CSS pixels per world unit
    unitsPerPx: 1,  // world units per CSS pixel  (use for min-hit-area math)
    dpr: 1,
    elapsed: 0,     // seconds of simulated time
    frames: 0,
    running: false,
    isContextLost: false,
    hasLayout: false // false until the container has produced a real (non-zero) box
  };

  if (opts.background != null) setBackground(opts.background);

  function setBackground(color) {
    if (color == null) { scene.background = null; renderer.setClearColor(0x000000, 0); return; }
    scene.background = new THREE.Color(color);
  }

  // ── resize ────────────────────────────────────────────────────────────────
  const resizeCbs = [];
  let layoutDirty = true;
  let hasLayout = false; // true once the container has produced a real (non-zero) box

  function measure() {
    // Prefer the container box; fall back to the viewport when the container is unsized.
    const rect = container.getBoundingClientRect();
    const w = Math.round(rect.width || window.innerWidth || 0);
    const h = Math.round(rect.height || window.innerHeight || 0);
    return { w, h };
  }

  let retryRaf = 0;
  function refresh() {
    const { w, h } = measure();

    // A hidden or not-yet-laid-out container measures 0. Publishing a 1×1 box here would give
    // every onResize listener a bogus square world to lay out against — and some of them only
    // run their expensive layout once. Wait for a real box instead; the ResizeObserver or this
    // rAF retry will call us back the moment there is one.
    if (w <= 0 || h <= 0) {
      layoutDirty = true;
      if (!retryRaf) retryRaf = requestAnimationFrame(() => { retryRaf = 0; refresh(); });
      return;
    }

    layoutDirty = false;
    const dpr = Math.min(window.devicePixelRatio || 1, maxDPR);

    stage.cssWidth = w;
    stage.cssHeight = h;
    stage.dpr = dpr;

    renderer.setPixelRatio(dpr);
    renderer.setSize(w, h, false);
    canvas.style.width = w + 'px';
    canvas.style.height = h + 'px';

    const aspect = w / h;
    const worldHeight = designHeight;
    const worldWidth = designHeight * aspect;

    camera.left = -worldWidth / 2;
    camera.right = worldWidth / 2;
    camera.top = worldHeight / 2;
    camera.bottom = -worldHeight / 2;
    camera.updateProjectionMatrix();

    stage.worldWidth = worldWidth;
    stage.worldHeight = worldHeight;
    stage.bounds.left = -worldWidth / 2;
    stage.bounds.right = worldWidth / 2;
    stage.bounds.top = worldHeight / 2;
    stage.bounds.bottom = -worldHeight / 2;
    stage.pxPerUnit = h / worldHeight;
    stage.unitsPerPx = worldHeight / h;
    stage.hasLayout = hasLayout = true;

    for (let i = 0; i < resizeCbs.length; i++) resizeCbs[i](stage);
  }

  /**
   * Subscribe to resize. The callback fires IMMEDIATELY AND SYNCHRONOUSLY with the current size
   * (once a real box exists) so layout code has exactly one code path.
   *
   * Gotcha: because that first call happens inside `onResize` itself, the returned unsubscribe
   * handle does not exist yet during it — `const off = onResize(() => off())` throws a TDZ error.
   * Use a flag inside the callback if you need to run only once.
   *
   * @returns {function} unsubscribe
   */
  function onResize(cb) {
    resizeCbs.push(cb);
    // Only fire immediately once we actually have a measured box; otherwise the first real
    // refresh will call it, so listeners never see a placeholder size.
    if (hasLayout) cb(stage);
    return () => {
      const i = resizeCbs.indexOf(cb);
      if (i >= 0) resizeCbs.splice(i, 1);
    };
  }

  function markDirty() { layoutDirty = true; }

  // FIT/viewport bounds go stale after split-view, rotation and tab-restore on iPad and
  // Chromebooks, and the resize event does not always fire. Belt and braces: four triggers,
  // plus a check on the first pointerdown after any of them.
  const onWinResize = () => { markDirty(); refresh(); };
  const onOrientation = () => { markDirty(); setTimeout(refresh, 120); }; // Safari reports old size immediately
  const onVisibility = () => { if (!document.hidden) { markDirty(); refresh(); } };
  const onFirstPointer = () => { if (layoutDirty) refresh(); };

  window.addEventListener('resize', onWinResize, { passive: true });
  window.addEventListener('orientationchange', onOrientation, { passive: true });
  document.addEventListener('visibilitychange', onVisibility);
  window.addEventListener('pointerdown', onFirstPointer, { capture: true, passive: true });

  let resizeObserver = null;
  if (typeof ResizeObserver !== 'undefined') {
    resizeObserver = new ResizeObserver(() => { markDirty(); refresh(); });
    resizeObserver.observe(container);
  }

  refresh();

  // ── context loss ──────────────────────────────────────────────────────────
  // A black canvas reads as "the game is broken" to a five-year-old. Show a friendly
  // sleepy-garden overlay instead and recover silently when the GPU comes back.
  let overlay = null;
  function showWakeOverlay() {
    if (overlay) return;
    overlay = document.createElement('div');
    overlay.setAttribute('role', 'status');
    overlay.style.cssText =
      'position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;' +
      'justify-content:center;gap:12px;z-index:9999;text-align:center;padding:24px;' +
      'font:700 clamp(20px,4vw,34px)/1.35 "Baloo 2",system-ui,-apple-system,sans-serif;' +
      'color:#3b5d2b;background:linear-gradient(#cdeffd,#e9f8d6);';
    overlay.innerHTML =
      '<div style="font-size:2em">🌙</div>' +
      '<div>The garden dozed off!</div>' +
      '<div style="font-weight:600;font-size:.62em;opacity:.8">Waking it back up…</div>';
    // The container must be a positioning context for inset:0 to land correctly.
    const cs = getComputedStyle(container);
    if (cs.position === 'static') container.style.position = 'relative';
    container.appendChild(overlay);
  }
  function hideWakeOverlay() {
    if (overlay && overlay.parentNode) overlay.parentNode.removeChild(overlay);
    overlay = null;
  }

  function onContextLost(e) {
    e.preventDefault(); // required, or the browser never fires contextrestored
    stage.isContextLost = true;
    showWakeOverlay();
  }
  function onContextRestored() {
    stage.isContextLost = false;
    hideWakeOverlay();
    markDirty();
    refresh();
  }
  canvas.addEventListener('webglcontextlost', onContextLost, false);
  canvas.addEventListener('webglcontextrestored', onContextRestored, false);

  // ── loop ──────────────────────────────────────────────────────────────────
  const updateCbs = [];
  const drawCbs = [];
  let raf = 0;
  let last = 0;
  let acc = 0;

  /** Fixed-timestep logic. dt is always `fixedStep` seconds. @returns {function} unsubscribe */
  function onUpdate(cb) {
    updateCbs.push(cb);
    return () => { const i = updateCbs.indexOf(cb); if (i >= 0) updateCbs.splice(i, 1); };
  }

  /** Per-frame draw. (alpha, frameDt) — alpha is the 0..1 leftover for interpolation. */
  function onDraw(cb) {
    drawCbs.push(cb);
    return () => { const i = drawCbs.indexOf(cb); if (i >= 0) drawCbs.splice(i, 1); };
  }

  function frame(now) {
    raf = requestAnimationFrame(frame);
    if (last === 0) last = now;
    let dt = (now - last) / 1000;
    last = now;
    if (dt > MAX_DELTA) dt = MAX_DELTA; // tab-switch / long GC pause safety
    if (dt < 0) dt = 0;

    acc += dt;
    let steps = 0;
    while (acc >= fixedStep && steps < MAX_STEPS_PER_FRAME) {
      for (let i = 0; i < updateCbs.length; i++) updateCbs[i](fixedStep);
      acc -= fixedStep;
      steps++;
      stage.elapsed += fixedStep;
    }
    if (steps === MAX_STEPS_PER_FRAME) acc = 0; // give up on catching up rather than spiral

    const alpha = acc / fixedStep;
    for (let i = 0; i < drawCbs.length; i++) drawCbs[i](alpha, dt);

    stage.frames++;
    if (!stage.isContextLost) renderer.render(scene, camera);
  }

  function start() {
    if (stage.running) return;
    stage.running = true;
    last = 0;
    acc = 0;
    raf = requestAnimationFrame(frame);
  }

  function stop() {
    stage.running = false;
    if (raf) cancelAnimationFrame(raf);
    raf = 0;
  }

  function dispose() {
    stop();
    window.removeEventListener('resize', onWinResize);
    window.removeEventListener('orientationchange', onOrientation);
    document.removeEventListener('visibilitychange', onVisibility);
    window.removeEventListener('pointerdown', onFirstPointer, { capture: true });
    canvas.removeEventListener('webglcontextlost', onContextLost);
    canvas.removeEventListener('webglcontextrestored', onContextRestored);
    if (resizeObserver) resizeObserver.disconnect();
    if (retryRaf) { cancelAnimationFrame(retryRaf); retryRaf = 0; }
    hideWakeOverlay();
    resizeCbs.length = updateCbs.length = drawCbs.length = 0;

    // Geometries/materials are ours; textures belong to textures.js and are disposed there.
    scene.traverse(obj => {
      if (obj.geometry && obj.geometry.dispose) obj.geometry.dispose();
      const m = obj.material;
      if (Array.isArray(m)) m.forEach(x => x && x.dispose && x.dispose());
      else if (m && m.dispose) m.dispose();
    });
    scene.clear();
    renderer.dispose();
    if (canvas.parentNode) canvas.parentNode.removeChild(canvas);
  }

  /**
   * Convert a DOM/pointer client coordinate to world units.
   * @param {number} clientX @param {number} clientY @param {THREE.Vector2} [out]
   */
  function toWorld(clientX, clientY, out) {
    const r = canvas.getBoundingClientRect();
    const nx = (clientX - r.left) / (r.width || 1);
    const ny = (clientY - r.top) / (r.height || 1);
    const v = out || new THREE.Vector2();
    v.x = stage.bounds.left + nx * stage.worldWidth;
    v.y = stage.bounds.top - ny * stage.worldHeight; // DOM y is down, world y is up
    return v;
  }

  Object.assign(stage, {
    onResize, onUpdate, onDraw, refresh, toWorld, start, stop, dispose, setBackground
  });

  if (opts.autoStart !== false) start();
  return stage;
}

/**
 * Aspect-correct 2D sprite. Give it ONE of `width` or `height` in world units and the
 * other is derived from the texture, so art swaps never distort.
 *
 * @param {THREE.Texture} texture
 * @param {object} [opts]
 * @param {number} [opts.width]  world units
 * @param {number} [opts.height] world units (default 100 if neither given)
 * @param {number} [opts.x=0] @param {number} [opts.y=0] @param {number} [opts.z=0]
 * @param {[number,number]} [opts.anchor=[0.5,0.5]] 0,0 = bottom-left of the sprite
 * @param {number} [opts.opacity=1] @param {number|string} [opts.color=0xffffff]
 * @param {boolean} [opts.additive=false]
 * @returns {THREE.Sprite} with `userData.baseScale` {x,y} for the tween helpers
 */
export function createSprite(texture, opts = {}) {
  const mat = new THREE.SpriteMaterial({
    map: texture || null,
    transparent: true,
    opacity: opts.opacity != null ? opts.opacity : 1,
    color: opts.color != null ? new THREE.Color(opts.color) : 0xffffff,
    // 2D painter's order: layer z + transparent sorting decides who wins, never the depth buffer.
    depthTest: false,
    depthWrite: false,
    blending: opts.additive ? THREE.AdditiveBlending : THREE.NormalBlending
  });

  const sprite = new THREE.Sprite(mat);

  const img = texture && texture.image;
  const iw = (img && (img.width || img.videoWidth)) || 1;
  const ih = (img && (img.height || img.videoHeight)) || 1;
  const ratio = iw / ih;

  let w, h;
  if (opts.width != null && opts.height != null) { w = opts.width; h = opts.height; }
  else if (opts.width != null) { w = opts.width; h = opts.width / ratio; }
  else if (opts.height != null) { h = opts.height; w = opts.height * ratio; }
  else { h = 100; w = 100 * ratio; }

  sprite.scale.set(w, h, 1);
  sprite.position.set(opts.x || 0, opts.y || 0, opts.z || 0);
  if (opts.anchor) sprite.center.set(opts.anchor[0], opts.anchor[1]);
  sprite.userData.baseScale = { x: w, y: h };
  return sprite;
}
