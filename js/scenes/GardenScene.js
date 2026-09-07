// GardenScene.js — the living world: sky, meadow, plots, plants, critters and weather, in WebGL.
//
// This is the VIEW. `js/game.js` owns every byte of state and fires events; nothing in here
// mutates a plot, writes a save, or decides when a plant grows. We are told, and we perform.
//
// ── LAYERS (from stage.js, back to front) ───────────────────────────────────────
//   sky          gradient plate (day + night), stars, sun, moon
//   farParallax  hills, slow clouds
//   midParallax  fast clouds, rain clouds, rainbow
//   ground       meadow plate + grass fringe
//   plots        dirt patches, lock signs, invisible tap pads
//   plants       the plants themselves
//   critters     bees, butterflies, owls
//   fx           particles (owned by particles.js)
//   ui           letter tags, water meters — in-world chrome that must never hide behind a plant
//
// ── DEPTH ───────────────────────────────────────────────────────────────────────
// Rows overlap on purpose (a real garden is dense), so every per-plot sprite carries
// `z = row * ROW_Z` INSIDE its layer. The layer z-step is 10, so with at most 6 rows the
// offsets can never leak into the next layer.

import { createSprite, THREE } from '../systems/stage.js';
import { tweens, isReducedMotion, onReducedMotionChange } from '../systems/tween.js';
import * as Textures from '../systems/textures.js';

const ROW_Z = 1.2;

const DAY_CRITTERS = ['critters/butterfly_pink.png', 'critters/bee.png', 'critters/ladybug.png',
                      'critters/butterfly_blue.png', 'critters/bluebird.png'];
const NIGHT_CRITTERS = ['critters/owl.png', 'sky/firefly.png', 'critters/bat.png', 'sky/firefly.png'];

const KID_FONT = '"Comic Sans MS", "Chalkboard SE", "Marker Felt", "Segoe Print", cursive, sans-serif';

/* ═══════════════════════ canvas texture helpers ═══════════════════════ */

/** Vertical gradient plate. Four pixels wide is plenty — it is stretched across the world. */
function gradientTexture(stops) {
  const cv = document.createElement('canvas');
  cv.width = 4; cv.height = 256;
  const ctx = cv.getContext('2d');
  const g = ctx.createLinearGradient(0, 0, 0, 256);
  stops.forEach(s => g.addColorStop(s[0], s[1]));
  ctx.fillStyle = g;
  ctx.fillRect(0, 0, 4, 256);
  return Textures.canvasTexture(cv, { mipmaps: false });
}

const letterCache = new Map();
/** The little orange-ringed letter badge that sits beside each planted seed. */
function letterTexture(L) {
  if (letterCache.has(L)) return letterCache.get(L);
  const S = 128;
  const cv = document.createElement('canvas');
  cv.width = cv.height = S;
  const ctx = cv.getContext('2d');
  ctx.beginPath(); ctx.arc(S / 2, S / 2, S * 0.44, 0, Math.PI * 2);
  ctx.fillStyle = '#ffffff'; ctx.fill();
  ctx.lineWidth = S * 0.09; ctx.strokeStyle = '#ff8a3d'; ctx.stroke();
  ctx.fillStyle = '#ff8a3d';
  ctx.font = 'bold ' + Math.round(S * 0.54) + 'px ' + KID_FONT;
  ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
  ctx.fillText(L, S / 2, S * 0.55);
  const t = Textures.canvasTexture(cv);
  letterCache.set(L, t);
  return t;
}

const labelCache = new Map();
/** Wooden-sign label under a locked plot ("Grow 3 more!"). */
function labelTexture(text) {
  if (labelCache.has(text)) return labelCache.get(text);
  const W = 320, H = 110;
  const cv = document.createElement('canvas');
  cv.width = W; cv.height = H;
  const ctx = cv.getContext('2d');
  const r = 26;
  ctx.beginPath();
  ctx.moveTo(r, 4); ctx.arcTo(W - 4, 4, W - 4, H - 4, r);
  ctx.arcTo(W - 4, H - 4, 4, H - 4, r); ctx.arcTo(4, H - 4, 4, 4, r); ctx.arcTo(4, 4, W - 4, 4, r);
  ctx.closePath();
  ctx.fillStyle = '#f6d98a'; ctx.fill();
  ctx.lineWidth = 8; ctx.strokeStyle = '#c99b4c'; ctx.stroke();
  ctx.fillStyle = '#7a5b1e';
  ctx.font = 'bold 40px ' + KID_FONT;
  ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
  ctx.fillText(text, W / 2, H / 2 + 3);
  const t = Textures.canvasTexture(cv);
  labelCache.set(text, t);
  return t;
}

/** A soft pill used for the water meter track and its fill. */
function pillTexture(color) {
  return Textures.makeProcedural({ shape: 'roundrect', color: color, radius: 0.5, size: 64 });
}

let plusTex = null;
/** "Tap here" cue on an empty, unlocked plot — the DOM build drew a ＋ and pre-readers rely on it. */
function plusTexture() {
  if (plusTex) return plusTex;
  const S = 128, t = S * 0.17, r = S * 0.34;
  const cv = document.createElement('canvas');
  cv.width = cv.height = S;
  const ctx = cv.getContext('2d');
  ctx.lineCap = 'round';
  ctx.strokeStyle = 'rgba(0,0,0,0.22)'; ctx.lineWidth = t * 1.5;
  ctx.beginPath(); ctx.moveTo(S / 2 - r, S / 2 + 4); ctx.lineTo(S / 2 + r, S / 2 + 4);
  ctx.moveTo(S / 2, S / 2 - r + 4); ctx.lineTo(S / 2, S / 2 + r + 4); ctx.stroke();
  ctx.strokeStyle = 'rgba(255,255,255,0.92)'; ctx.lineWidth = t;
  ctx.beginPath(); ctx.moveTo(S / 2 - r, S / 2); ctx.lineTo(S / 2 + r, S / 2);
  ctx.moveTo(S / 2, S / 2 - r); ctx.lineTo(S / 2, S / 2 + r); ctx.stroke();
  plusTex = Textures.canvasTexture(cv);
  return plusTex;
}

/* ═══════════════════════ scene ═══════════════════════ */

/**
 * @param {object} o
 * @param {object} o.stage  from stage.js
 * @param {object} o.fx     from particles.js
 * @param {object} o.input  from input.js
 * @param {object} o.game   window.GardenGame
 * @returns {object} { dispose }
 */
export function createGardenScene(o) {
  const stage = o.stage, fx = o.fx, input = o.input, game = o.game;
  const L = stage.layers;
  const TOTAL = game.TOTAL_PLOTS;
  const STAGE_MAX = game.STAGE_MAX;

  /* ── layout state, rewritten on every resize ────────────────────────── */
  const lay = {
    cols: 4, rows: 4, colW: 300, rowH: 130, dirtW: 260, plantH: 220,
    left: -600, top: 80, horizonY: 100
  };

  /* ── sky ────────────────────────────────────────────────────────────── */
  const skyDay = createSprite(gradientTexture([[0, '#57bcf7'], [0.55, '#a9e3ff'], [1, '#dcf4ff']]),
    { width: 100, height: 100 });
  const skyNight = createSprite(gradientTexture([[0, '#0e1540'], [0.55, '#28316d'], [1, '#4a5590']]),
    { width: 100, height: 100, opacity: 0 });
  L.sky.add(skyDay); L.sky.add(skyNight);
  skyNight.position.z = 0.1;

  // A single object holds the animated 0..1 day→night mix so one tween drives everything
  // that has to change colour together (stars, hills, meadow tint).
  const sky = { night: game.isNight() ? 1 : 0, stars: game.isNight() ? 1 : 0 };

  const stars = [];
  const starTex = Textures.get('sky/star.png');
  for (let i = 0; i < 26; i++) {
    const s = createSprite(starTex, { height: 12 + Math.random() * 16, opacity: 0 });
    s.userData.phase = Math.random() * Math.PI * 2;
    s.userData.period = 1400 + Math.random() * 2200;   // never a shared twinkle rhythm
    s.userData.rx = Math.random();
    s.userData.ry = Math.random();
    s.position.z = 0.2;
    L.sky.add(s);
    stars.push(s);
  }
  // Late-arriving art: the sync peek above may return null on the very first frame.
  Textures.load('sky/star.png').then(t => stars.forEach(s => sizeTo(s, t, s.userData.baseScale.y)));

  const sun = createSprite(Textures.get('sky/sun.png'), { height: 180 });
  const moon = createSprite(Textures.get('sky/moon.png'), { height: 150, opacity: 0 });
  L.sky.add(sun); L.sky.add(moon);
  sun.position.z = 0.3; moon.position.z = 0.3;
  Textures.load('sky/sun.png').then(t => sizeTo(sun, t, 180));
  Textures.load('sky/moon.png').then(t => sizeTo(moon, t, 150));

  /* ── parallax: hills + clouds ───────────────────────────────────────── */
  const hills = createSprite(Textures.get('garden/hills_backdrop.png'), { height: 300, opacity: 0.6 });
  L.farParallax.add(hills);
  Textures.load('garden/hills_backdrop.png').then(t => {
    hills.material.map = t; hills.material.needsUpdate = true; relayout();
  });

  const clouds = [];
  for (let i = 0; i < 5; i++) {
    const url = Math.random() < 0.5 ? 'sky/cloud_puffy.png' : 'sky/cloud_wisp.png';
    const c = createSprite(Textures.get(url), { height: 100, opacity: 0.95 });
    // Different speeds per cloud AND per layer — parallax is the whole point, and identical
    // drift rates read as a single flat sheet sliding past.
    c.userData.speed = 9 + Math.random() * 26;
    c.userData.ry = 0.04 + Math.random() * 0.24;
    c.userData.sizeK = 0.75 + Math.random() * 0.5;
    (i % 2 ? L.midParallax : L.farParallax).add(c);
    Textures.load(url).then(t => { c.material.map = t; c.material.needsUpdate = true; relayout(); });
    clouds.push(c);
  }

  /* ── ground ─────────────────────────────────────────────────────────── */
  const meadow = createSprite(gradientTexture([[0, '#8ad35c'], [0.35, '#6fbf46'], [1, '#4f9536']]),
    { width: 100, height: 100 });
  L.ground.add(meadow);

  const fringe = createSprite(Textures.get('garden/grass_foreground.png'), { height: 70 });
  fringe.position.z = 0.4;
  L.ground.add(fringe);
  Textures.load('garden/grass_foreground.png').then(t => {
    // Clone before tiling: textures.js hands back one shared, clamped instance and other
    // sprites (none today, but tomorrow) would inherit the repeat.
    const rep = t.clone();
    rep.wrapS = THREE.RepeatWrapping;
    rep.needsUpdate = true;
    fringe.material.map = rep;
    fringe.material.needsUpdate = true;
    fringe.userData.tile = rep;
    relayout();
  });

  const rainbow = createSprite(Textures.get('sky/rainbow.png'), { height: 260, opacity: 0 });
  L.midParallax.add(rainbow);
  Textures.load('sky/rainbow.png').then(t => sizeTo(rainbow, t, 260));

  /* ── plots ──────────────────────────────────────────────────────────── */
  // The track needs enough contrast to read against both dark soil and bright grass.
  const trackTex = pillTexture('#e7f2f7');
  const fillTex = pillTexture('#3f9ff0');
  const plots = [];

  for (let i = 0; i < TOTAL; i++) {
    const dirt = createSprite(Textures.get('garden/dirt_plot_empty.png'), { width: 200 });
    L.plots.add(dirt);

    const plant = createSprite(null, { width: 10, height: 10, opacity: 0 });
    plant.center.set(0.5, 0);          // grows from the soil line, per the "anchor at the feet" rule
    L.plants.add(plant);

    const tag = createSprite(letterTexture('A'), { height: 46, opacity: 0 });
    L.ui.add(tag);

    const track = createSprite(trackTex, { width: 90, height: 14, opacity: 0 });
    const fill = createSprite(fillTex, { width: 90, height: 10, opacity: 0 });
    fill.center.set(0, 0.5);           // grows rightward from the left end of the track
    L.ui.add(track); L.ui.add(fill);

    const plus = createSprite(plusTexture(), { height: 34, opacity: 0 });
    plus.position.z = 0.3;
    L.plots.add(plus);

    const lock = createSprite(Textures.get('garden/lock_sign.png'), { height: 70, opacity: 0 });
    const label = createSprite(labelTexture('Grow 1 more!'), { height: 40, opacity: 0 });
    L.plots.add(lock); L.plots.add(label);

    // A bare Object3D, not a sprite: input.js takes `hitSize` straight from the config, so this
    // costs zero draw calls while still giving the whole cell (plant included) a tap target.
    const pad = new THREE.Object3D();
    L.plots.add(pad);

    const cell = {
      i: i, dirt: dirt, plant: plant, tag: tag, track: track, fill: fill,
      lock: lock, label: label, pad: pad, plus: plus,
      col: 0, row: 0, cx: 0, soilY: 0, dirtTint: 0xffffff,
      texUrl: null, texStage: -1, texToken: 0, plantBase: { x: 10, y: 10 },
      idle: null, propIdle: null, busy: false, locked: false, pressing: null,
      // Fixed-at-birth randomness: this is what stops sixteen plants breathing in lockstep.
      r1: Math.random(), r2: Math.random(), r3: Math.random()
    };
    plots.push(cell);
    // The tap target itself is registered in layout(), because its size is the cell size.
  }

  Textures.loadAll(['garden/dirt_plot_empty.png', 'garden/dirt_plot_seeded.png', 'garden/lock_sign.png'])
    .then(() => { plots.forEach(c => syncPlot(c.i)); relayout(); });

  /* ── helpers ────────────────────────────────────────────────────────── */

  function sizeTo(spr, tex, height) {
    const img = tex && tex.image;
    const ratio = (img && img.width && img.height) ? img.width / img.height : 1;
    const w = height * ratio;
    spr.material.map = tex;
    spr.material.needsUpdate = true;
    spr.scale.set(w, height, 1);
    spr.userData.baseScale.x = w;
    spr.userData.baseScale.y = height;
    return { x: w, y: height };
  }

  function stageTexUrl(p) {
    if (!p) return null;
    if (p.stage === 0) return 'garden/seed.png';
    if (p.stage === 1) return 'garden/sprout.png';
    return 'plants/' + p.plantId + '.png';
  }

  function stageHeight(st) {
    if (st === 0) return lay.rowH * 0.30;
    if (st === 1) return lay.rowH * 0.58;
    if (st === 2) return lay.plantH * 0.60;
    return lay.plantH;
  }

  function stopIdle(cell) {
    if (!cell.idle) return;
    cell.idle.forEach(h => h && h.cancel && h.cancel());
    cell.idle = null;
  }

  function startIdle(cell) {
    stopIdle(cell);
    const p = game.plot(cell.i);
    if (!p || cell.busy) return;
    const big = p.stage >= 2;
    cell.plant.material.rotation = 0;
    cell.idle = [
      // Breathe: scaleY 1.00↔1.018 with scaleX 1.00↔0.994, period 1.85–2.55s. Every amount and
      // period here is drawn from the cell's fixed-at-birth randomness, which is what keeps
      // sixteen plants from inhaling together.
      tweens.breathe(cell.plant, {
        amount: (big ? 0.016 : 0.022) * (0.85 + cell.r2 * 0.4),
        ms: 1850 + cell.r1 * 700,
        phase: cell.r2
      }),
      // Sway: the house spec is ±0.8–1.5°, i.e. 0.014–0.026 rad. It used to run to ±4°, which
      // reads as a toy being shaken rather than a plant standing in moving air.
      tweens.swayLoop(cell.plant, {
        angle: (big ? 0.016 : 0.020) * (0.8 + cell.r3 * 0.5),
        ms: 2450 + cell.r3 * 1100,
        phase: cell.r1
      })
    ];
  }

  /**
   * The plot furniture breathes too — all eight dirt mounds, both sign pieces and the letter tag.
   *
   * These are the biggest objects on screen AND the main interactive ones, and §4.1 gives no
   * interactive object leave to sit perfectly still for more than 400ms. Amplitudes are tiny
   * (a mound is heavy; it should look heavy) and every phase and period is derived from the
   * cell's own r1/r2/r3, so no two plots ever share a rhythm.
   *
   * Started once per cell at birth and never restarted: breathe() re-reads `userData.baseScale`
   * every tick, so a resize or an art swap is picked up without tearing the loop down.
   */
  function startPropIdle(cell) {
    if (cell.propIdle) return;
    const r1 = cell.r1, r2 = cell.r2, r3 = cell.r3;
    cell.propIdle = [
      // Soil: a slow, shallow settle — 1.0% on Y, 2.05–2.75s.
      tweens.breathe(cell.dirt, { amount: 0.010 + r1 * 0.004, ms: 2050 + r3 * 700, phase: r2 }),
      tweens.swayLoop(cell.dirt, { angle: 0.011 + r2 * 0.007, ms: 2900 + r1 * 900, phase: r3 }),
      // Sign post: it is on a stick in the ground, so it gets the freest sway in the scene —
      // still inside the ±1.5° ceiling.
      tweens.breathe(cell.lock, { amount: 0.014 + r3 * 0.005, ms: 1900 + r2 * 700, phase: r1 }),
      tweens.swayLoop(cell.lock, { angle: 0.017 + r1 * 0.009, ms: 2500 + r3 * 1000, phase: r2 }),
      tweens.breathe(cell.label, { amount: 0.012 + r2 * 0.006, ms: 2200 + r1 * 600, phase: r3 }),
      tweens.swayLoop(cell.label, { angle: 0.015 + r3 * 0.010, ms: 2750 + r2 * 850, phase: r1 }),
      // Letter badge: a light bob, offset from everything else on the plot.
      tweens.breathe(cell.tag, { amount: 0.016 + r1 * 0.006, ms: 1950 + r3 * 650, phase: r2 }),
      tweens.swayLoop(cell.tag, { angle: 0.014 + r2 * 0.008, ms: 3050 + r1 * 500, phase: r3 }),
      // Even the water meter's track breathes. Its FILL cannot go through breathe() — scale.x is
      // the water level and belongs to setMeter — so the ripple below only touches scale.y.
      tweens.breathe(cell.track, { amount: 0.020 + r2 * 0.008, ms: 2300 + r1 * 800, phase: r1 })
    ];
  }

  function stopPropIdle(cell) {
    if (!cell.propIdle) return;
    cell.propIdle.forEach(h => h && h.cancel && h.cancel());
    cell.propIdle = null;
  }

  /** Point the plant sprite at the art for its current stage. Async, and re-entrant-safe. */
  function setPlantArt(cell, opts) {
    const p = game.plot(cell.i);
    const url = stageTexUrl(p);
    const token = ++cell.texToken;

    if (!url) {
      stopIdle(cell);
      cell.plant.material.opacity = 0;
      cell.texUrl = null;
      cell.texStage = -1;
      return Promise.resolve(null);
    }

    const h = stageHeight(p.stage);
    return Textures.load(url).then(tex => {
      if (cell.texToken !== token) return null;   // a newer stage/plant won the race
      cell.plantBase = sizeTo(cell.plant, tex, h);
      cell.plant.material.opacity = 1;
      cell.texUrl = url;
      cell.texStage = p.stage;
      if (!opts || opts.idle !== false) startIdle(cell);
      return tex;
    });
  }

  /* ── plot sync (state → sprites, no animation) ──────────────────────── */

  function syncPlot(i) {
    const cell = plots[i];
    if (!cell || cell.busy) return;   // never stomp a running growth performance
    const p = game.plot(i);
    const open = game.plotsOpen();
    const locked = i >= open;
    cell.locked = locked;

    if (locked) {
      const nu = game.nextUnlock();
      const left = nu ? Math.max(1, nu.need - game.grownTotal()) : 0;
      cell.lock.material.opacity = 1;
      cell.label.material.opacity = 1;
      sizeTo(cell.label, labelTexture('Grow ' + left + ' more!'), lay.rowH * 0.30);
      // Desaturated but still clearly SOIL. A heavier grey at low opacity let the plot melt
      // into the meadow behind it, so a locked plot stopped reading as a plot at all.
      cell.dirt.material.opacity = 0.62;
      setDirtTint(cell, 0xd2c8bc);
      cell.tag.material.opacity = 0;
      cell.track.material.opacity = 0;
      cell.fill.material.opacity = 0;
      cell.plant.material.opacity = 0;
      cell.plus.material.opacity = 0;
      stopIdle(cell);
      return;
    }

    cell.lock.material.opacity = 0;
    cell.label.material.opacity = 0;
    cell.dirt.material.opacity = 1;
    setDirtTint(cell, 0xffffff);

    const seeded = !!p && p.stage <= 1;
    const dirtTex = Textures.get(seeded ? 'garden/dirt_plot_seeded.png' : 'garden/dirt_plot_empty.png');
    if (dirtTex && cell.dirt.material.map !== dirtTex) {
      const w = lay.dirtW;
      const img = dirtTex.image;
      const ratio = (img && img.width && img.height) ? img.width / img.height : 2;
      cell.dirt.material.map = dirtTex;
      cell.dirt.material.needsUpdate = true;
      cell.dirt.scale.set(w, w / ratio, 1);
      cell.dirt.userData.baseScale = { x: w, y: w / ratio };
    }

    if (!p) {
      cell.tag.material.opacity = 0;
      cell.track.material.opacity = 0;
      cell.fill.material.opacity = 0;
      cell.plant.material.opacity = 0;
      cell.plus.material.opacity = 0.9;
      cell.texUrl = null;
      cell.texStage = -1;
      stopIdle(cell);
      return;
    }
    cell.plus.material.opacity = 0;

    sizeTo(cell.tag, letterTexture(p.letter), lay.rowH * 0.32);
    cell.tag.material.opacity = 1;

    const showMeter = p.stage < STAGE_MAX;
    cell.track.material.opacity = showMeter ? 0.95 : 0;
    cell.fill.material.opacity = showMeter ? 1 : 0;
    setMeter(cell, p.water / game.WATERS_PER_STAGE, false);

    // Compare the STAGE as well as the url: stages 2 and 3 share one plant PNG and differ only
    // in height, so a url-only check would leave a full bloom drawn at its half-grown size.
    if (stageTexUrl(p) !== cell.texUrl || cell.texStage !== p.stage) setPlantArt(cell);
    else if (!cell.idle) startIdle(cell);
  }

  /**
   * Set the soil's base tint (normal / locked / finger-down) and re-apply the night wash on top.
   * Kept in one place because three different code paths write this colour, and any of them
   * writing it raw would knock the plot back into daylight in the middle of the night.
   */
  function setDirtTint(cell, hex) {
    cell.dirtTint = hex;
    // NOTE the steep factor: material.color multiplies in LINEAR space but the renderer outputs
    // sRGB, so a 0.6 multiplier only looks like ~0.8 on screen. Night needs to go this low to
    // read as night at all.
    const k = 1 - 0.62 * sky.night;
    const c = cell.dirt.material.color;
    c.setHex(hex);
    c.setRGB(c.r * k * 0.94, c.g * k * 0.97, c.b * Math.min(1, k * 1.06));
  }

  function setMeter(cell, pct, animate) {
    const w = Math.max(0.0001, Math.min(1, pct)) * lay.dirtW * 0.62;
    if (animate && !isReducedMotion()) {
      tweens.to(cell.fill, { 'scale.x': w }, { duration: 320, ease: 'quartOut' });
    } else {
      cell.fill.scale.x = w;
    }
  }

  function syncAll() {
    for (let i = 0; i < TOTAL; i++) syncPlot(i);
  }

  /* ── the signature moment: a stage change ───────────────────────────── */

  function animateStage(i, full) {
    const cell = plots[i];
    const p = game.plot(i);
    if (!cell || !p) return;

    const url = stageTexUrl(p);
    const token = ++cell.texToken;

    // Claim the plot SYNCHRONOUSLY. game.js fires this event and then immediately re-renders
    // (unlocking plots can change every cell); if `busy` were only set inside the promise
    // below, that re-render would already have snapped the new art into place and there would
    // be nothing left to animate.
    stopIdle(cell);
    cell.busy = true;

    // A timeline is fire-and-forget, and tween.js resolves conflicts by KILLING the loser —
    // so any other animation that grabbed this plant's scale mid-performance would strand the
    // timeline half-finished and leave `busy` stuck true forever (the plot would never react
    // again). Everything that ends the performance funnels through here, and a watchdog fires
    // it even if the timeline dies. syncPlot then repairs whatever art we did not reach.
    let finished = false;
    function finishGrowth() {
      if (finished) return;
      finished = true;
      if (cell.texToken !== token) return;   // a newer growth owns this plot now
      cell.busy = false;
      cell.plant.material.rotation = 0;
      syncPlot(cell.i);
      startIdle(cell);
    }

    // Pre-load BEFORE the curtain goes up. A texture that arrives mid-timeline turns the
    // anticipation dip into a stutter, which is exactly the snap we are avoiding.
    Textures.load(url).then(tex => {
      if (cell.texToken !== token) { cell.busy = false; return; }
      const spr = cell.plant;
      const from = { x: spr.scale.x || 1, y: spr.scale.y || 1 };
      const newH = stageHeight(p.stage);
      const img = tex.image;
      const ratio = (img && img.width && img.height) ? img.width / img.height : 1;
      const base = { x: newH * ratio, y: newH };

      if (isReducedMotion()) {
        cell.plantBase = sizeTo(spr, tex, newH);
        spr.material.opacity = 1;
        cell.texUrl = url;
        cell.texStage = p.stage;
        fx.emit('sparkle', cell.cx, cell.soilY + base.y * 0.5, { count: 4 });
        finishGrowth();
        return;
      }

      const sparkleY = cell.soilY + base.y * 0.55;

      // The growth performance OWNS this plant for the next 710ms. Clearing first is not
      // belt-and-braces: tween.js claims properties on an animation's FIRST TICK, so a squash
      // queued by the watering tap a moment ago — which has not ticked yet if the tab was
      // throttled — would tick first, claim the scale, and kill our timeline before frame one.
      tweens.cancel(cell.plant);

      // 130 + 280 + 300 of animation, plus slack for the frame the .call steps land on.
      tweens.delay(900, finishGrowth);

      tweens.timeline({ onComplete: finishGrowth })
        // 1. ANTICIPATION — the plant gathers itself: a squat, reciprocal, eased backIn.
        .to(spr, { 'scale.x': from.x * 1.16, 'scale.y': from.y * 0.80 },
            { duration: 130, ease: 'backIn', from: { 'scale.x': from.x, 'scale.y': from.y } })
        // 2. THE SWAP, hidden inside a puff of soil.
        .call(() => {
          cell.plantBase = sizeTo(spr, tex, newH);
          cell.texUrl = url;
          cell.texStage = p.stage;
          spr.material.opacity = 1;
          spr.scale.set(base.x * 0.46, base.y * 0.30, 1);
          spr.material.rotation = (cell.r1 - 0.5) * 0.18;
          tweens.squashStretch(cell.dirt, 0.16, 420);          // the soil takes the shove
          fx.emit('poof', cell.cx, cell.soilY + 6, { count: full ? 8 : 5, size: [36, 74] });
          fx.emit('sparkle', cell.cx, sparkleY, { count: full ? 22 : 12 });
        })
        // 3. THE SPRING UP — overshoot tall and thin (sx × sy ≈ 1: a stretch, never a zoom).
        .to(spr, { 'scale.x': base.x * 0.90, 'scale.y': base.y * 1.12 },
            { duration: 280, ease: 'backOut',
              from: { 'scale.x': base.x * 0.46, 'scale.y': base.y * 0.30 } })
        // 4. SETTLE — quintOut-ish drift to rest, with the rotation kick unwinding with it.
        .to(spr, { 'scale.x': base.x, 'scale.y': base.y, 'material.rotation': 0 },
            { duration: 300, ease: 'quartOut' })
        .call(() => {
          if (!full) return;
          // Full bloom gets the layered celebration: 10–20 flat confetti chips (never a
          // 60-piece dump), a second sparkle wave, and the neighbours noticing
          // (§4.8 "environment reaction").
          fx.emit('confetti', cell.cx, sparkleY, { count: 16 });
          fx.emit('sparkle', cell.cx, sparkleY, { count: 16, size: [26, 54] });
          nudgeNeighbours(i);
        })
        .start();
    });
  }

  /**
   * §4.8 "environment reaction": 2–5 nearby background objects each take a one-off wobble,
   * staggered 50ms apart. Not just the neighbouring PLANTS — the mounds and the sign posts
   * too, because they are the things actually next to the bloom, and a celebration that only
   * moves its own plot reads as a sticker being applied rather than as an event in a world.
   */
  function nudgeNeighbours(i) {
    const cell = plots[i];
    const near = plots
      .filter(o => o !== cell && !o.busy)
      .map(o => ({ o: o, d: Math.hypot(o.cx - cell.cx, o.soilY - cell.soilY) }))
      .filter(e => e.d <= lay.colW * 1.6)
      .sort((a, b) => a.d - b.d)
      .slice(0, 5);                       // 2–5 objects, never the whole garden

    near.forEach((e, k) => {
      const other = e.o;
      tweens.delay(50 + k * 50, () => {   // staggered 50ms, per the spec
        if (other.busy) return;
        tweens.nudge(other.dirt, { angle: 0.026, ms: 220 });
        if (other.locked) {
          tweens.nudge(other.lock, { angle: 0.05, ms: 260 });
          tweens.nudge(other.label, { angle: 0.042, ms: 240 });
        } else if (game.plot(other.i)) {
          tweens.nudge(other.plant, { angle: 0.055, ms: 260 });
          tweens.nudge(other.tag, { angle: 0.05, ms: 220 });
        }
      });
    });

    // The wider world notices too — the grass fringe and the nearest cloud both take a beat.
    tweens.delay(90, () => tweens.nudge(fringe, { angle: 0.006, ms: 320 }));
    let best = null, bd = Infinity;
    clouds.forEach(c => {
      const d = Math.abs(c.position.x - cell.cx);
      if (d < bd) { bd = d; best = c; }
    });
    if (best) tweens.delay(140, () => tweens.nudge(best, { angle: 0.05, ms: 300 }));
  }

  /* ── layout ─────────────────────────────────────────────────────────── */

  function relayout() { layout(stage); }

  function layout(s) {
    const b = s.bounds, W = s.worldWidth, H = s.worldHeight;
    const landscape = (W / H) >= 1.0;

    // Portrait phones get three columns and six rows; anything landscape-ish gets the
    // familiar four-wide grid. The DOM version scrolled on phones — a canvas cannot, so the
    // meadow claims more of the screen in portrait instead.
    lay.cols = landscape ? 4 : 3;
    lay.rows = Math.ceil(TOTAL / lay.cols);
    lay.horizonY = b.top - H * (landscape ? 0.40 : 0.30);

    // The DOM HUD floats over the canvas; keep the top row clear of it.
    const hudReserve = 100 * s.unitsPerPx;
    lay.top = Math.min(lay.horizonY - 16, b.top - hudReserve - 16);
    const bottom = b.bottom + 52;
    lay.rowH = (lay.top - bottom) / lay.rows;
    lay.colW = Math.min(W / (lay.cols + 0.25), 330);
    lay.left = -lay.colW * lay.cols / 2;
    lay.dirtW = Math.min(lay.colW * 0.92, lay.rowH * 2.2);
    // Plants deliberately overrun their row (a garden is dense, not a spreadsheet) — but on a
    // phone six tight rows meant the front row swallowed the one behind it, so portrait gets a
    // shorter plant.
    lay.plantH = Math.min(lay.rowH * (landscape ? 1.75 : 1.28), lay.dirtW * 1.4);

    // sky + ground plates
    skyDay.scale.set(W, H, 1); skyDay.userData.baseScale = { x: W, y: H };
    skyNight.scale.set(W, H, 1); skyNight.userData.baseScale = { x: W, y: H };

    const groundH = lay.horizonY - b.bottom;
    meadow.scale.set(W, groundH, 1);
    meadow.userData.baseScale = { x: W, y: groundH };
    meadow.position.set(0, b.bottom + groundH / 2, 0);

    const fringeH = Math.max(46, H * 0.06);
    fringe.scale.set(W, fringeH, 1);
    fringe.userData.baseScale = { x: W, y: fringeH };
    fringe.position.set(0, lay.horizonY - fringeH * 0.25, 0.4);
    if (fringe.userData.tile) {
      // Tile horizontally rather than stretching, or the blades smear on a wide screen.
      fringe.userData.tile.repeat.set(Math.max(2, Math.round(W / (fringeH * 3))), 1);
    }

    // Hills are deliberately stretched to the full width — they are a silhouette band, not art
    // whose aspect anyone can read, and letterboxed hills would show the sky plate behind them.
    const hillH = H * 0.30;
    hills.scale.set(W * 1.06, hillH, 1);
    hills.userData.baseScale = { x: W * 1.06, y: hillH };
    hills.position.set(0, lay.horizonY + hillH * 0.30, 0);

    // Sun and moon key off the SHORTER axis too, and sit below the HUD reserve: on a phone the
    // four DOM tool buttons live exactly where a height-only sun would be.
    const sunH = Math.min(H * 0.19, W * 0.24);
    if (sun.material.map) sizeTo(sun, sun.material.map, sunH);
    if (moon.material.map) sizeTo(moon, moon.material.map, sunH * 0.82);
    const skyY = b.top - hudReserve * (landscape ? 0.35 : 1) - sunH * 0.55;
    sun.position.set(b.right - sun.scale.x * 0.58, skyY, 0.3);
    moon.position.set(b.right - moon.scale.x * 0.58, skyY, 0.3);

    stars.forEach(s2 => {
      s2.position.set(b.left + s2.userData.rx * W, b.top - s2.userData.ry * H * 0.5, 0.2);
    });

    // Clouds are sized against the SHORTER axis too. Keying purely off world height made them
    // swallow a portrait phone's sky, because a portrait world is only ~380 units wide.
    const cloudH = Math.min(H * 0.125, W * 0.28);
    clouds.forEach(c => {
      if (c.material.map) sizeTo(c, c.material.map, cloudH * c.userData.sizeK);
      c.position.y = b.top - c.userData.ry * H;
      if (c.position.x === 0) c.position.x = b.left + Math.random() * W;
    });

    rainbow.position.set(b.left + W * 0.26, lay.horizonY + rainbow.scale.y * 0.25, 0);

    for (let i = 0; i < TOTAL; i++) {
      const cell = plots[i];
      cell.col = i % lay.cols;
      cell.row = (i / lay.cols) | 0;
      cell.cx = lay.left + (cell.col + 0.5) * lay.colW;
      cell.soilY = lay.top - (cell.row + 1) * lay.rowH + lay.rowH * 0.24;
      const z = cell.row * ROW_Z;

      const dw = lay.dirtW;
      const dratio = cell.dirt.userData.baseScale.x / (cell.dirt.userData.baseScale.y || 1);
      cell.dirt.scale.set(dw, dw / dratio, 1);
      cell.dirt.userData.baseScale = { x: dw, y: dw / dratio };
      cell.dirt.position.set(cell.cx, cell.soilY, z);

      cell.plant.position.set(cell.cx, cell.soilY - cell.dirt.scale.y * 0.12, z);

      cell.tag.position.set(cell.cx - dw * 0.40, cell.soilY + lay.rowH * 0.18, z);
      cell.track.position.set(cell.cx, cell.soilY - cell.dirt.scale.y * 0.30, z);
      const tw = dw * 0.62, th = Math.max(11, lay.rowH * 0.11);
      cell.track.scale.set(tw, th, 1);
      cell.track.userData.baseScale = { x: tw, y: th };
      cell.fillH = th * 0.72;
      cell.fill.scale.y = cell.fillH;
      cell.fill.position.set(cell.cx - tw / 2, cell.track.position.y, z + 0.1);

      sizeTo(cell.plus, plusTexture(), Math.max(24, lay.rowH * 0.26));
      cell.plus.position.set(cell.cx, cell.soilY + cell.dirt.scale.y * 0.06, z + 0.3);

      cell.lock.position.set(cell.cx, cell.soilY + lay.rowH * 0.36, z + 0.2);
      if (cell.lock.material.map) sizeTo(cell.lock, cell.lock.material.map, lay.rowH * 0.42);
      cell.label.position.set(cell.cx, cell.soilY + lay.rowH * 0.02, z + 0.2);

      cell.pad.position.set(cell.cx, cell.soilY + lay.rowH * 0.28, z);
      input.register(cell.pad, Object.assign({}, padHandlers(i), {
        hitSize: { w: lay.colW * 0.96, h: lay.rowH * 0.98 }
      }));
    }

    // Sprite sizes changed, so every base scale the idle loops captured at their old size is
    // stale — restart them or the plants breathe around a pose that no longer exists.
    syncAll();
    plots.forEach(c => { if (!c.busy && !c.locked && game.plot(c.i)) startIdle(c); });
  }

  // input.register replaces the whole config, so layout has to hand the handlers back in.
  const padHandlerCache = [];
  function padHandlers(i) {
    if (padHandlerCache[i]) return padHandlerCache[i];
    const cell = plots[i];

    /**
     * Reduced motion must REDUCE motion, not delete the feedback. When the press cycle is off we
     * still owe the child a confirmation, so the plot takes an instant, non-animated tint step —
     * one frame, no tween — and steps back on release.
     */
    function tintAck(down) {
      setDirtTint(cell, down ? 0xffe9b0 : 0xffffff);
      cell.plantBoost = down ? 1.32 : 1;
      setPlantShade(cell);
    }

    function endPress() {
      if (!cell.pressing) return;
      cell.pressing.forEach(h => h.release());
      cell.pressing = null;
    }

    padHandlerCache[i] = {
      onPressStart: () => {
        if (cell.locked) return;
        endPress();
        // The whole cycle is driven from here: an eased press-down now, the overshoot + settle
        // when the finger lifts. tintAck fires only in reduced motion (tween.press calls it),
        // so the two feedback paths never double up.
        setDirtTint(cell, 0xffe9b0);
        const dir = cell.r3 < 0.5 ? -1 : 1;
        const h = [tweens.press(cell.dirt, {
          squash: 0.085, stretch: 0.038, rotate: 0.028, pop: Math.max(2, lay.rowH * 0.022),
          dir: dir, onAcknowledge: tintAck
        })];
        // Never touch a plant that is mid-growth: a competing scale tween would kill the
        // growth timeline outright (tween.js resolves conflicts by killing the loser).
        if (game.plot(i) && !cell.busy) {
          h.push(tweens.press(cell.plant, {
            squash: 0.10, stretch: 0.045, rotate: 0.042,
            pop: Math.max(2, lay.rowH * 0.028), dir: -dir
          }));
        }
        cell.pressing = h;
      },
      onPressEnd: () => {
        // endPress() runs even if the plot locked or unlocked under the finger — otherwise a
        // press whose release was skipped would sit in its long-press anticipation forever.
        endPress();
        if (!cell.locked) setDirtTint(cell, 0xffffff);
      },
      onTap: info => {
        fx.emit('sparkle', info.x, info.y, { count: 5, size: [16, 30] });
        game.tapPlot(i);
      }
    };
    return padHandlerCache[i];
  }

  stage.onResize(layout);

  /* ── day / night ────────────────────────────────────────────────────── */

  function applyDayNight(night, instant) {
    const ms = instant ? 0 : 2600;
    const target = night ? 1 : 0;
    if (instant) {
      sky.night = target; sky.stars = target;
      paintDayNight();
    } else {
      // ignoreReducedMotion: this is a slow colour wash, not a motion effect, and without it
      // a reduced-motion player would be stuck in whichever sky they booted into.
      tweens.to(sky, { night: target, stars: target },
        { duration: ms, ease: 'sineInOut', ignoreReducedMotion: true, onUpdate: paintDayNight });
    }
    tweens.to(sun.material, { opacity: night ? 0 : 1 },
      { duration: ms, ease: 'sineInOut', ignoreReducedMotion: true });
    tweens.to(moon.material, { opacity: night ? 1 : 0 },
      { duration: ms, ease: 'sineInOut', ignoreReducedMotion: true });
  }

  function paintDayNight() {
    const n = sky.night;
    skyNight.material.opacity = n;
    hills.material.opacity = 0.6 - 0.28 * n;
    // Meadow, plants and soil all dim toward a cool blue-green after dark rather than going
    // grey. Without the soil in here the plots stayed in broad daylight under a starry sky.
    const g = 1 - 0.74 * n;
    meadow.material.color.setRGB(g * 0.80, g * 0.98, g * 1.05);
    fringe.material.color.setRGB(g * 0.80, g * 0.98, g * 1.05);
    plots.forEach(c => {
      setPlantShade(c);
      setDirtTint(c, c.dirtTint != null ? c.dirtTint : 0xffffff);
    });
  }

  /**
   * The plant's colour, combining the night wash with the plot's own brightness boost.
   *
   * Same discipline as setDirtTint, and for the same reason: two code paths write this colour
   * (the day/night wash and the reduced-motion press acknowledgement) and whichever wrote last
   * used to win. The press ack was silently erased on the very next frame the sky repainted.
   */
  function setPlantShade(cell) {
    const pl = 1 - 0.55 * sky.night;
    const k = cell.plantBoost || 1;
    cell.plant.material.color.setRGB(
      Math.min(1, pl * 0.90 * k), Math.min(1, pl * 0.98 * k), Math.min(1, pl * 1.06 * k));
  }

  applyDayNight(game.isNight(), true);

  // Twinkle: one driver for all 26 stars, each with its own phase and period.
  tweens.driver(elapsed => {
    if (sky.stars <= 0.001) {
      for (let i = 0; i < stars.length; i++) stars[i].material.opacity = 0;
      return false;
    }
    for (let i = 0; i < stars.length; i++) {
      const s = stars[i];
      const k = 0.35 + 0.65 * (0.5 + 0.5 * Math.sin(elapsed / s.userData.period + s.userData.phase));
      s.material.opacity = k * sky.stars;
    }
    return false;
  });

  /* ── ambient life ───────────────────────────────────────────────────── */

  // Amounts are now Y-amplitudes with a reciprocal X, so these read smaller than the old numbers
  // even where the number is unchanged. The sun is allowed a touch more than a plant: it is the
  // one openly cartoon object in the sky.
  tweens.breathe(sun, { amount: 0.026, ms: 3300 });
  tweens.swayLoop(sun, { angle: 0.030, ms: 5200 });
  tweens.breathe(moon, { amount: 0.020, ms: 4100 });
  tweens.swayLoop(moon, { angle: 0.018, ms: 6100 });
  // Clouds are soft things in moving air: each gets its own slow deform on its own period.
  clouds.forEach((c, k) => {
    tweens.breathe(c, { amount: 0.014 + (k % 3) * 0.004, ms: 3400 + k * 520, phase: Math.random() });
    tweens.swayLoop(c, { angle: 0.010 + (k % 2) * 0.006, ms: 4700 + k * 610, phase: Math.random() });
  });

  // Cloud drift: each cloud on its own speed, wrapping across the world.
  tweens.driver((elapsed, dtms) => {
    if (isReducedMotion()) return false;
    const b = stage.bounds;
    for (let i = 0; i < clouds.length; i++) {
      const c = clouds[i];
      c.position.x += (dtms / 1000) * c.userData.speed;
      if (c.position.x > b.right + c.scale.x) c.position.x = b.left - c.scale.x;
    }
    return false;
  });

  // Empty plots breathe their ＋ so no part of the garden is ever perfectly still (§4.1). One
  // driver for all of them, each on its own phase and period.
  //
  // This used to multiply BOTH axes by the same number at ±11%, which is not a breath at all —
  // equal deltas on x and y are a zoom, and a 22% peak-to-peak zoom on a hint badge is a pulse
  // you cannot look away from. It is now the house breathe: scaleY 1.00↔1.018 against
  // scaleX 1.00↔0.994, one tenth the amplitude, and volume-conserving.
  tweens.driver(elapsed => {
    if (isReducedMotion()) return false;
    for (let i = 0; i < plots.length; i++) {
      const c = plots[i];
      if (c.plus.material.opacity <= 0.01) continue;
      const b2 = c.plus.userData.baseScale;
      const u = 0.5 + 0.5 * Math.sin(elapsed / (1900 + c.r1 * 700) + c.r2 * 6.28);
      c.plus.scale.set(b2.x * (1 - 0.006 * u), b2.y * (1 + 0.018 * u), 1);
    }
    return false;
  });

  // The far scenery is not a painted backdrop either. The hills drift a hair against the
  // parallax and the grass fringe leans in the same breeze the plants do — both far enough
  // below the plant amplitudes to stay atmospheric rather than distracting.
  tweens.breathe(hills, { amount: 0.006, ms: 5200, phase: 0.2 });
  tweens.driver(elapsed => {
    if (isReducedMotion()) return false;
    hills.position.x = Math.sin(elapsed / 9000) * (stage.worldWidth * 0.008);
    return false;
  }, { target: hills, keys: ['position.x'] });
  tweens.swayLoop(fringe, { angle: 0.005, ms: 4300, phase: 0.55 });
  tweens.breathe(fringe, { amount: 0.010, ms: 3100, phase: 0.15 });

  // The water in each meter ripples. scale.x is the level and is off limits, so this only ever
  // writes scale.y — which is why it is a hand-rolled driver rather than a breathe().
  tweens.driver(elapsed => {
    if (isReducedMotion()) return false;
    for (let i = 0; i < plots.length; i++) {
      const c = plots[i];
      if (!c.fillH || c.fill.material.opacity <= 0.02) continue;
      const u = 0.5 + 0.5 * Math.sin(elapsed / (1700 + c.r2 * 900) + c.r3 * 6.28);
      c.fill.scale.y = c.fillH * (1 + 0.07 * u);
    }
    return false;
  });

  const pollen = fx.ambient('pollen', { rate: 3.5 });

  // Reduced motion is checked when an animation STARTS, so a mid-session toggle would leave
  // sixteen plants breathing at a player who just asked them to stop. Restart the idles on
  // every change: they turn into no-ops (and reset the pose) while it is on.
  const offReduced = onReducedMotionChange(() => {
    plots.forEach(cell => {
      stopIdle(cell);
      stopPropIdle(cell);
      startPropIdle(cell);
      if (!cell.busy && !cell.locked && game.plot(cell.i)) startIdle(cell);
    });
    if (isReducedMotion()) clearCritters(); else ensureCritters();
  });

  /**
   * The nearest DISCRETE prop to a world point — clouds, critters, the sun or moon, a mound, a
   * plant, a sign. Deliberately excludes the full-bleed plates (sky, meadow, hills, grass fringe):
   * tilting a band that spans the whole world by 2° swings its corners off screen and shows the
   * sky behind, so those get their own idle motion instead and never take the tap ack.
   *
   * There are always sixteen mounds on screen, so this never comes back empty.
   */
  function nearestProp(x, y) {
    let best = null, bd = Infinity;
    function consider(obj, wx, wy, weight) {
      if (!obj || obj.material.opacity <= 0.02) return;
      const d = Math.hypot(wx - x, wy - y) * (weight || 1);
      if (d < bd) { bd = d; best = obj; }
    }
    clouds.forEach(c => consider(c, c.position.x, c.position.y));
    critters.forEach(c => consider(c, c.position.x, c.position.y));
    consider(sun, sun.position.x, sun.position.y);
    consider(moon, moon.position.x, moon.position.y);
    plots.forEach(c => {
      consider(c.dirt, c.cx, c.soilY);
      if (c.locked) consider(c.lock, c.cx, c.lock.position.y);
      else if (game.plot(c.i)) consider(c.plant, c.cx, c.soilY + c.plantBase.y * 0.5);
    });
    return best;
  }

  input.onTapAnywhere(p => {
    // §4.9 / Instant Tell #30: nothing in the world is inert. A tap that hits no interactive
    // object still gets an acknowledgement inside 100ms — a small poof of dust where the finger
    // landed, and a 200ms ±2° backOut tilt on whatever was nearest to it.
    if (p.hit) return;
    fx.emit('poof', p.x, p.y, { count: 4, size: [22, 44], life: [340, 560], alpha: 0.5 });
    fx.emit('sparkle', p.x, p.y, { count: 5, size: [14, 28] });
    const prop = nearestProp(p.x, p.y);
    if (prop) tweens.nudge(prop, { angle: 0.035, ms: 200 });
  });

  input.register(sun, {
    hitPadding: 20,
    onTap: info => {
      tweens.wobble(sun, { angle: 0.35, ms: 720, cycles: 3 });
      fx.emit('sparkle', info.x, info.y, { count: 20, size: [28, 56] });
    }
  });

  /* ── critters ───────────────────────────────────────────────────────── */

  const critters = [];

  /**
   * Keep the critter layer populated. It is not decoration: two or three butterflies and a bee
   * crossing the meadow on desynced curved paths carry a big slice of the never-static rule by
   * themselves, and the layer sitting empty is what made the garden read as a painted backdrop.
   *
   * Note what is NOT a gate here any more: `document.hidden`. Bailing on a hidden document meant
   * that anything sampling the game with the tab backgrounded — including an automated pass —
   * found a permanently empty layer, and a real player returning from another tab waited up to
   * nine seconds for the first one.
   */
  const CRITTER_TARGET = 3;
  function ensureCritters() {
    if (isReducedMotion()) return;
    for (let n = critters.length; n < CRITTER_TARGET; n++) spawnCritter();
  }

  /** Retire every flier at once — what turning reduced motion ON has to do. */
  function clearCritters() {
    critters.slice().forEach(spr => {
      if (spr.userData.driver && spr.userData.driver.cancel) spr.userData.driver.cancel();
      input.unregister(spr);
      L.critters.remove(spr);
      if (spr.material) spr.material.dispose();
    });
    critters.length = 0;
  }

  /**
   * @param {number} [startT] 0..1 — begin this critter part-way along its flight path. Used for
   *        the ones seeded at boot, so the layer is populated with critters already IN the
   *        frame instead of three sprites queued up off the left edge.
   */
  function spawnCritter(startT) {
    if (isReducedMotion()) return;
    if (critters.length >= 5) return;
    const pool = game.isNight() ? NIGHT_CRITTERS : DAY_CRITTERS;
    const url = pool[(Math.random() * pool.length) | 0];
    const b = stage.bounds;
    const h = 52 + Math.random() * 34;
    const spr = createSprite(Textures.get(url), { height: h, opacity: 0 });
    L.critters.add(spr);
    critters.push(spr);

    Textures.load(url).then(t => {
      const base = sizeTo(spr, t, h);
      spr.material.opacity = 1;

      const dir = Math.random() < 0.5 ? 1 : -1;
      const fromX = dir > 0 ? b.left - base.x : b.right + base.x;
      const toX = dir > 0 ? b.right + base.x : b.left - base.x;
      const baseY = b.top - stage.worldHeight * (0.12 + Math.random() * 0.4);
      const dur = (12 + Math.random() * 12) * 1000;
      const waves = 1.4 + Math.random() * 1.8;
      const amp = 40 + Math.random() * 80;
      // Wing flutter at 3.5–7Hz. Each critter also carries its own phase offset, so two
      // butterflies in frame never beat their wings on the same frame.
      const flap = 22 + Math.random() * 23;
      const flapPhase = Math.random() * Math.PI * 2;
      const t0 = startT ? Math.min(0.92, startT) : 0;

      spr.userData.kick = 0;
      const drv = tweens.driver((elapsed, dtms) => {
        const t2 = t0 + elapsed / dur;
        if (t2 >= 1) {
          input.unregister(spr);
          L.critters.remove(spr);
          spr.material.dispose();
          const k = critters.indexOf(spr);
          if (k >= 0) critters.splice(k, 1);
          return true;
        }
        spr.position.x = fromX + (toX - fromX) * t2;
        spr.position.y = baseY + Math.sin(t2 * Math.PI * 2 * waves) * amp;
        // Wing flutter is a scale pulse, not a sprite swap — cheap, and it reads at any size.
        const w = Math.sin(elapsed / flap + flapPhase);
        // A tapped critter startles: the reaction has to live INSIDE this driver, because the
        // driver rewrites rotation and scale every frame and would erase an outside tween.
        const kick = spr.userData.kick;
        if (kick > 0) spr.userData.kick = Math.max(0, kick - dtms / 700);
        const boost = 1 + kick * 0.3;
        spr.scale.x = base.x * dir * (1 + w * 0.13) * boost;
        spr.scale.y = base.y * (1 - w * 0.06) * boost;
        // Tilt into the curve: the body follows the path, per the follow-through rule.
        spr.material.rotation = Math.cos(t2 * Math.PI * 2 * waves) * 0.26 * dir
          + Math.sin(elapsed / 45) * 0.5 * kick;
        return false;
      }, { target: spr, keys: ['position.x', 'position.y'] });

      input.register(spr, {
        hitPadding: 18,
        onTap: info => {
          fx.emit('sparkle', info.x, info.y, { count: 14 });
          spr.userData.kick = 1;
        }
      });
      spr.userData.driver = drv;
    });
  }

  /* ── weather ────────────────────────────────────────────────────────── */

  fx.definePreset('rain', {
    texture: null,
    // Procedural round drops on purpose: the raindrop PNG would spin, because the pool gives
    // every particle a random birth rotation.
    fallback: { shape: 'circle', color: '#bfeeff', soft: true, size: 64 },
    additive: false,
    count: [1, 1], life: [1400, 2000], size: [12, 22],
    angle: [-Math.PI * 0.54, -Math.PI * 0.46], speed: [420, 560], spread: 0,
    gravity: -320, drag: 1, spin: [0, 0],
    scale: [1, 1], fadeIn: 0.06, fadeOut: 0.22, alpha: 0.85,
    colors: ['#cdf1ff', '#9adcff', '#eaf9ff'],
    rate: 42
  });

  const rainClouds = [];
  function doRain(info) {
    const b = stage.bounds;
    const cloudsMs = (info && info.cloudsMs) || 3400;
    const rainbowMs = (info && info.rainbowMs) || 5000;

    for (let c = 0; c < 3; c++) {
      const cl = createSprite(Textures.get('sky/rain_cloud.png'), { height: 150, opacity: 0 });
      L.midParallax.add(cl);
      rainClouds.push(cl);
      Textures.load('sky/rain_cloud.png').then(t => {
        sizeTo(cl, t, Math.max(120, stage.worldHeight * 0.16));
        cl.material.opacity = 1;
        const x = b.left + stage.worldWidth * (0.2 + c * 0.3 + Math.random() * 0.06);
        const y = b.top - cl.scale.y * 0.55;
        cl.position.set(x, y + 200, 0.5);
        tweens.to(cl, { 'position.y': y }, { duration: 520, ease: 'backOut', delay: c * 90 });
        // Rumble: a low, per-cloud sway so the three never bob together.
        tweens.breathe(cl, { amount: 0.03, ms: 900 + c * 220 });
      });
    }

    const shower = fx.ambient('rain', {
      rate: 46,
      area: { x: b.left, y: b.top - 20, w: stage.worldWidth, h: 30 }
    });
    tweens.delay(2600, () => shower.cancel());

    tweens.delay(cloudsMs, () => {
      rainClouds.forEach((cl, k) => {
        tweens.to(cl, { 'material.opacity': 0, 'position.y': cl.position.y + 160 },
          { duration: 620, ease: 'quadIn', delay: k * 70, onComplete: () => L.midParallax.remove(cl) });
      });
      rainClouds.length = 0;
      const rb = stage.bounds;
      rainbow.position.set(rb.left + stage.worldWidth * 0.28, lay.horizonY + rainbow.scale.y * 0.22, 0);
      tweens.to(rainbow.material, { opacity: 0.92 }, { duration: 900, ease: 'sineOut' });
      tweens.delay(rainbowMs, () => tweens.to(rainbow.material, { opacity: 0 }, { duration: 1200 }));
    });
  }

  /* ── event wiring ───────────────────────────────────────────────────── */

  const offs = [
    game.on('plot', d => syncPlot(d.i)),
    game.on('plots', () => syncAll()),

    game.on('planted', d => {
      const cell = plots[d.i];
      syncPlot(d.i);
      setPlantArt(cell, { idle: false }).then(() => {
        tweens.pop(cell.plant, { from: 0.15, ms: 560, onComplete: () => startIdle(cell) });
        tweens.squashStretch(cell.dirt, 0.2, 520);
        fx.emit('poof', cell.cx, cell.soilY + 4, { count: 6 });
      });
    }),

    game.on('water', d => {
      const cell = plots[d.i];
      const p = game.plot(d.i);
      // Droplets fall from above the plant and burst on it.
      fx.emit('waterDroplets', cell.cx, cell.soilY + cell.plantBase.y * 0.85,
        { count: 14, angle: [-Math.PI * 0.7, -Math.PI * 0.3], speed: [60, 170], gravity: -900 });
      if (p) {
        if (!cell.busy) tweens.squashStretch(cell.plant, 0.15, 520);
        setMeter(cell, p.water / game.WATERS_PER_STAGE, true);
      }
    }),

    game.on('sparkle', d => {
      const cell = plots[d.i];
      fx.emit('sparkle', cell.cx, cell.soilY + Math.max(30, cell.plantBase.y * 0.6),
        { count: d.n, spread: lay.dirtW * 0.3 });
    }),

    game.on('stage', d => animateStage(d.i, d.full)),

    game.on('nope', d => {
      const cell = plots[d.i];
      tweens.shake(cell.dirt, { amount: lay.dirtW * 0.05, ms: 420, axis: 'x' });
      if (game.plot(d.i) && !cell.busy) tweens.wobble(cell.plant, { angle: 0.14, ms: 480, cycles: 3 });
    }),

    game.on('dug', d => {
      const cell = plots[d.i];
      // Invalidate any growth still in flight for this plot — the plant it was growing is gone.
      cell.texToken++;
      cell.busy = false;
      fx.emit('poof', cell.cx, cell.soilY + 20, { count: 12, size: [56, 110] });
      stopIdle(cell);
      tweens.squashStretch(cell.dirt, 0.22, 520);
    }),

    game.on('rain', doRain),

    game.on('daynight', d => applyDayNight(d.night, false)),

    game.on('start', () => {
      syncAll();
      // Staggered entrance, per §4.7 — a garden that arrives all on one frame is a slideshow.
      plots.forEach((cell, k) => {
        if (cell.locked || !game.plot(cell.i)) return;
        tweens.delay(k * 45, () => {
          if (cell.busy) return;
          stopIdle(cell);
          tweens.pop(cell.plant, { from: 0.55, ms: 460, onComplete: () => startIdle(cell) });
        });
      });
      ensureCritters();
    })
  ];

  /* ── timers: critters and idle "life beats" ─────────────────────────── */

  // These live on the tween manager's clock rather than on stage.onUpdate. Same cadence — the
  // stage drives the manager — but it keeps every piece of scheduled life in one place, and it
  // means a harness that steps tweens deterministically also steps the critter population and
  // the life beats instead of watching a frozen garden.
  let critterAcc = 0, beatAcc = 0, beatNext = 7000;
  const timers = tweens.driver((elapsed, dtms) => {
    critterAcc += dtms;
    // Top the population back up quickly — the layer must never be empty, and one spawn every
    // nine seconds against a 12–24s flight meant it regularly was.
    if (critterAcc >= 3000) { critterAcc = 0; ensureCritters(); }

    beatAcc += dtms;
    if (beatAcc >= beatNext) {
      beatAcc = 0;
      beatNext = 6000 + Math.random() * 6000;   // never a fixed timer
      const live = plots.filter(c => !c.busy && !c.locked && game.plot(c.i));
      if (live.length) {
        const c = live[(Math.random() * live.length) | 0];
        // A one-off "life beat" (§4.2): small, and well under the ±1.5° idle ceiling's cousin —
        // a beat is allowed to be bigger than an idle, but not by much.
        tweens.wobble(c.plant, { angle: 0.055 + Math.random() * 0.03, ms: 620, cycles: 2 });
      }
    }
    return false;
  });
  const offUpdate = () => timers.cancel();

  /* ── boot ───────────────────────────────────────────────────────────── */
  syncAll();
  // Every mound, sign and badge starts breathing at birth, on its own phase. These loops read
  // their base pose live, so nothing here needs restarting on a resize or an art swap.
  plots.forEach(startPropIdle);
  // Seed the critter layer already mid-flight, so the first frame of the garden has life in it
  // rather than three sprites waiting off the left edge.
  spawnCritter(0.18); spawnCritter(0.46); spawnCritter(0.72);

  /**
   * A world-wide confetti burst, for the celebration beats game.js owns (a bloom, a sticker,
   * a garden that grew overnight).
   *
   * This used to be a DOM layer of 60 emoji divs falling on a `linear` CSS keyframe — a `linear`
   * tween on a visible property is an automatic cap on the whole response category, and 60 pieces
   * is its own instant tell. It is now the WebGL `confetti` preset: 10–20 flat palette chips per
   * launch point, real gravity, real tumble, fading only in the last quarter of their life.
   *
   * @param {number} [n] a rough total; split across 1–3 launch points so it reads as a spray
   *                     rather than a single fountain.
   */
  function burstConfetti(n) {
    const b = stage.bounds;
    const total = Math.max(8, Math.min(48, n || 16));
    const points = total > 34 ? 3 : (total > 18 ? 2 : 1);
    const per = Math.round(total / points);
    for (let k = 0; k < points; k++) {
      const x = b.left + stage.worldWidth * ((k + 0.5) / points + (Math.random() - 0.5) * 0.12);
      const y = lay.horizonY + stage.worldHeight * 0.06;
      tweens.delay(k * 90, () => {
        fx.emit('confetti', x, y, { count: per });
        fx.emit('sparkle', x, y, { count: Math.max(4, (per / 3) | 0), size: [22, 44] });
      });
    }
  }

  return {
    plots: plots,
    relayout: relayout,
    burstConfetti: burstConfetti,
    // The clock lives in game.js and only ticks once a minute; this is how a dev (or a future
    // teacher toggle) previews the other half of the day without waiting for it.
    setNight: applyDayNight,
    dispose() {
      offs.forEach(f => f());
      offUpdate();
      offReduced();
      pollen.cancel();
      plots.forEach(stopIdle);
      plots.forEach(stopPropIdle);
    }
  };
}
