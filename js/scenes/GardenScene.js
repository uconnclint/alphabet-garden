// GardenScene.js — the living world: sky, meadow, plots, plants, critters and weather, in WebGL.
//
// This is the VIEW. `js/game.js` owns every byte of state and fires events; nothing in here
// mutates a plot, writes a save, or decides when a plant grows. We are told, and we perform.
//
// ── LAYERS (from stage.js, back to front) ───────────────────────────────────────
//   sky          gradient plate (day + night), stars
//   farParallax  hills, slow clouds
//   midParallax  fast clouds, rain clouds, rainbow, THE SUN AND MOON (in front of both
//                cloud bands — see SUN_Z)
//   ground       meadow plate, horizon shrubs, grass tufts
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
import { variantUrl, metricsFor } from '../data/flat-assets.js';

const ROW_Z = 1.2;

/* ── content fitting ─────────────────────────────────────────────────────────────
 * The flat-vector art is authored inside a generous canvas — the dirt bed lives in the
 * lower half of a square, a plant's leaves stop 5% short of the top — so "make this sprite
 * 200 units tall" is no longer the same instruction as "make this OBJECT 200 units tall".
 * Everything below sizes and anchors against the asset's measured content box
 * (js/data/flat-assets.js) instead of its canvas.
 *
 * These three defaults are what an asset that has NOT been re-authored gets. Each one
 * reproduces exactly where that sprite used to sit, so the claymation fallback path is
 * pixel-identical to before. */
const DEF_CENTER = { u: [0, 1], v: [0, 1], ax: 0.5, ay: 0.5 };            // floats: sun, clouds
const DEF_GROUND = { u: [0, 1], v: [0, 1], ax: 0.5, ay: 1 };              // stands on the ground
// 0.62 reproduces the old `soilY - dirt.scale.y * 0.12` plant offset for claymation soil.
const DEF_DIRT = { u: [0, 1], v: [0, 1], ax: 0.5, ay: 0.5, plant: 0.62 };

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

  const SUN_URL = 'sky/sun.png';

  // The sun and moon live in midParallax, NOT in the sky layer, and they sit in front of
  // everything else in it. They used to be sky-layer sprites, which put them behind BOTH
  // parallax cloud bands: a drifting cloud slid straight over the sun's face. That was
  // survivable when the sun was a featureless disc and is not now that it is a character with
  // six authored expressions — a cloud parked on its eyes reads as a z-order bug, because it is.
  //
  // Note what this does NOT do: the clouds keep their own two-band split (far and mid,
  // different speeds), so the parallax depth between them is untouched. Only the two sky
  // characters moved. 6 is inside the layer's 10-unit z budget, so it cannot leak into `ground`.
  const SUN_Z = 6;
  const sun = createSprite(Textures.get(SUN_URL), { height: 180 });
  const moon = createSprite(Textures.get('sky/moon.png'), { height: 150, opacity: 0 });
  L.midParallax.add(sun); L.midParallax.add(moon);
  sun.position.z = SUN_Z; moon.position.z = SUN_Z;
  Textures.load(SUN_URL).then(t => { applyFit(sun, t, SUN_URL, 180, DEF_CENTER); relayout(); });
  Textures.load('sky/moon.png').then(t => sizeTo(moon, t, 150));

  /* ── the sun's face ───────────────────────────────────────────────────
   * art/flat/ ships six authored expressions on one rig — identical rays, identical alpha box,
   * only the face group differs — so a reaction is a MAP SWAP and never a re-fit. `relayout()`
   * deliberately keeps measuring against SUN_URL for exactly that reason: whatever face is
   * showing, the geometry is the neutral sun's.
   *
   * The logical names carry an '@' suffix, which means textures.js strips it and falls back to
   * plain 'sky/sun.png' for any expression that is missing — a 404 here costs a reaction, never
   * a green placeholder blob in the sky.
   */
  const SUN_FACES = {
    neutral:     SUN_URL,
    happy:       'sky/sun@happy.png',        // eyes closed — this is the blink
    laughing:    'sky/sun@laughing.png',
    surprised:   'sky/sun@surprised.png',
    mischievous: 'sky/sun@mischievous.png',
    sad:         'sky/sun@sad.png'
  };
  const sunTex = Object.create(null);        // name -> Texture, filled once the art lands
  let sunHold = 0;                           // ms left on a non-neutral face
  let sunBlinkIn = 2200 + Math.random() * 3600;

  // Lazy, and deliberately NOT in main3d's CORE set: five more 150KB PNGs are not worth
  // delaying the first frame for, and until they arrive the sun simply does not blink.
  Object.keys(SUN_FACES).forEach(name => {
    Textures.load(SUN_FACES[name]).then(t => { sunTex[name] = t; });
  });

  /**
   * Show one expression. `holdMs` is how long before the face falls back to neutral; 0 holds
   * until something else changes it.
   */
  function setSunFace(name, holdMs) {
    const t = sunTex[name] || sunTex.neutral;
    if (t && sun.material.map !== t) { sun.material.map = t; sun.material.needsUpdate = true; }
    sunHold = holdMs || 0;
    // A reaction resets the blink clock, so the sun never blinks on top of its own laugh.
    if (holdMs) sunBlinkIn = holdMs + 1400 + Math.random() * 3000;
  }

  let wasNight = game.isNight();

  /** Never a fixed cadence: a metronome blink is worse than no blink at all. */
  function nextBlink() { return 3400 + Math.random() * 6400; }

  tweens.driver((elapsed, dtms) => {
    if (sunHold > 0) {
      sunHold -= dtms;
      if (sunHold <= 0) setSunFace('neutral', 0);
      return false;
    }
    // Nothing to perform to while the sun is under the horizon, and blinking is ambience, so
    // it is one of the things `prefers-reduced-motion` switches off. Tap and bloom REACTIONS
    // still fire — those are feedback, not decoration.
    if (isReducedMotion() || sun.material.opacity < 0.35) return false;
    sunBlinkIn -= dtms;
    if (sunBlinkIn <= 0) {
      setSunFace('happy', 150);
      sunBlinkIn = nextBlink();
    }
    return false;
  });

  /* ── parallax: hills + clouds ───────────────────────────────────────── */
  // Two bands, not one. The flat hill is a low tileable ridge with no outline, so a single
  // band left a lot of bare sky between the ridge line and the clouds; a second, paler,
  // taller band behind it gives the backdrop the depth the old dome silhouette had.
  const HILL_URL = variantUrl('garden/hills_backdrop.png', 0);
  const HILL_FAR_URL = variantUrl('garden/hills_backdrop.png', 1);
  const hillsFar = createSprite(Textures.get(HILL_FAR_URL), { height: 300, opacity: 0.55 });
  const hills = createSprite(Textures.get(HILL_URL), { height: 300, opacity: 0.6 });
  L.farParallax.add(hillsFar); L.farParallax.add(hills);
  hills.position.z = 0.1;
  Textures.load(HILL_FAR_URL).then(t => {
    hillsFar.material.map = t; hillsFar.material.needsUpdate = true; relayout();
  });
  Textures.load(HILL_URL).then(t => {
    hills.material.map = t; hills.material.needsUpdate = true; relayout();
  });

  const clouds = [];
  for (let i = 0; i < 5; i++) {
    // Deterministic variant per cloud rather than a coin flip between two files: three
    // different puffy shapes, and cloud 0 never has to be the same one as cloud 3.
    const url = variantUrl('sky/cloud_puffy.png', i * 2 + 1);
    const c = createSprite(Textures.get(url), { height: 100, opacity: 0.95 });
    c.userData.url = url;
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

  // The old grass fringe was ONE sprite stretched across the world with the texture set to
  // repeat. The flat art is a TUFT, not a strip — tiling it would stamp the identical clump
  // every 100 units, which is instant tell #23 with extra steps. So the fringe is now a row of
  // discrete tufts, cycling three authored variants, each with its own size and lean.
  const TUFT_MAX = 18;
  const tufts = [];
  for (let i = 0; i < TUFT_MAX; i++) {
    const url = variantUrl('garden/grass_foreground.png', i);
    const t = createSprite(Textures.get(url), { height: 70, opacity: 0 });
    t.position.z = 0.4;
    t.userData.url = url;
    // Index-derived, not Math.random(): the meadow must not reshuffle itself on a resize.
    t.userData.jitterX = ((i * 37) % 13) / 13 - 0.5;
    t.userData.sizeK = 0.80 + ((i * 29) % 11) / 11 * 0.44;
    t.userData.lift = ((i * 17) % 7) / 7;
    L.ground.add(t);
    tufts.push(t);
    Textures.load(url).then(tex => {
      t.material.map = tex; t.material.needsUpdate = true; relayout();
    });
  }

  // Set dressing with no claymation ancestor: three shrubs sitting on the horizon, behind the
  // grass and behind every plot. They give the meadow a skyline, which is what the flat hill
  // band (deliberately outline-free and low-contrast) cannot do on its own.
  const bushes = [];
  for (let i = 0; i < 3; i++) {
    const url = variantUrl('garden/bush.png', i);
    const b2 = createSprite(Textures.get(url), { height: 120, opacity: 0 });
    b2.position.z = 0.2;
    b2.userData.url = url;
    b2.userData.at = [0.08, 0.40, 0.86][i];
    b2.userData.sizeK = [1, 0.84, 0.92][i];
    L.ground.add(b2);
    bushes.push(b2);
    Textures.load(url).then(tex => {
      b2.material.map = tex; b2.material.needsUpdate = true; relayout();
    });
  }

  const rainbow = createSprite(Textures.get('sky/rainbow.png'), { height: 260, opacity: 0 });
  L.midParallax.add(rainbow);
  Textures.load('sky/rainbow.png').then(t => sizeTo(rainbow, t, 260));

  /* ── plots ──────────────────────────────────────────────────────────── */
  // The track needs enough contrast to read against both dark soil and bright grass.
  const trackTex = pillTexture('#e7f2f7');
  const fillTex = pillTexture('#3f9ff0');
  const plots = [];

  for (let i = 0; i < TOTAL; i++) {
    // One of three authored beds per plot, chosen from the PLOT INDEX so a plot looks the same
    // on every re-render, every resize and every reload. Empty and seeded share the variant.
    const emptyUrl = variantUrl('garden/dirt_plot_empty.png', i);
    const seededUrl = variantUrl('garden/dirt_plot_seeded.png', i);
    const dirt = createSprite(Textures.get(emptyUrl), { width: 200 });
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
      emptyUrl: emptyUrl, seededUrl: seededUrl, dirtUrl: emptyUrl,
      // bedH: the VISIBLE height of the bed (the sprite is taller — the flat plot is drawn in
      // the lower half of its canvas). plantY: where a plant's base meets the dug hollow.
      bedH: 0, plantY: 0,
      col: 0, row: 0, cx: 0, soilY: 0, dirtTint: 0xffffff,
      texUrl: null, texStage: -1, texToken: 0, plantBase: { x: 10, y: 10 },
      idle: null, propIdle: null, busy: false, locked: false, pressing: null,
      // Fixed-at-birth randomness: this is what stops sixteen plants breathing in lockstep.
      r1: Math.random(), r2: Math.random(), r3: Math.random()
    };
    plots.push(cell);
    // The tap target itself is registered in layout(), because its size is the cell size.
  }

  // Every bed variant actually in play, plus the sign — the first frame must not show a
  // procedural blob where the primary tap target belongs.
  const bedUrls = ['garden/lock_sign.png'];
  plots.forEach(c => {
    if (bedUrls.indexOf(c.emptyUrl) < 0) bedUrls.push(c.emptyUrl);
    if (bedUrls.indexOf(c.seededUrl) < 0) bedUrls.push(c.seededUrl);
  });
  Textures.loadAll(bedUrls)
    .then(() => { plots.forEach(c => syncPlot(c.i)); relayout(); });

  /* ── helpers ────────────────────────────────────────────────────────── */

  function texRatio(tex, fallback) {
    const img = tex && tex.image;
    return (img && img.width && img.height) ? img.width / img.height : (fallback || 1);
  }

  /** Canvas-height sizing. Still correct for everything we draw ourselves (badges, meters). */
  function sizeTo(spr, tex, height) {
    const w = height * texRatio(tex);
    spr.material.map = tex;
    spr.material.needsUpdate = true;
    spr.scale.set(w, height, 1);
    spr.userData.baseScale.x = w;
    spr.userData.baseScale.y = height;
    return { x: w, y: height };
  }

  /**
   * The SPRITE scale needed to make `url`'s visible content exactly `contentH` tall.
   * Split out from applyFit because the growth timeline has to know the final pose before
   * it swaps the art in (it animates *toward* it).
   */
  function fitScale(tex, url, contentH, def) {
    const m = metricsFor(url, def) || DEF_CENTER;
    const y = contentH / Math.max(0.05, m.v[1] - m.v[0]);
    return { x: y * texRatio(tex), y: y, m: m };
  }

  /** Point a sprite at `url`'s art, sized by content height and pivoted on its anchor. */
  function applyFit(spr, tex, url, contentH, def) {
    const f = fitScale(tex, url, contentH, def);
    spr.material.map = tex;
    spr.material.needsUpdate = true;
    spr.scale.set(f.x, f.y, 1);
    spr.userData.baseScale = { x: f.x, y: f.y };
    // `center` is the pivot AND the meaning of `position` — an object anchored on its contact
    // point squashes into the ground instead of swinging about the middle of an empty quad.
    // input.js already accounts for center when it measures a hit box.
    spr.center.set(f.m.ax, 1 - f.m.ay);
    return { x: f.x, y: f.y };
  }

  /**
   * Size and place one plot's bed, and derive everything anchored to it.
   *
   * The flat bed is a wide shallow trough drawn in the lower half of a square canvas, with
   * loose clods flung outside its main mass and a baked contact shadow. Three consequences,
   * all handled here:
   *   • WIDTH is fitted to the bed's own span, not the alpha box — otherwise a variant that
   *     happens to throw its clods further would draw a visibly smaller plot.
   *   • The sprite is pivoted on the bed's CONTACT LINE, so `position` means "where the plot
   *     touches the meadow" and the press-squash compresses into the ground.
   *   • `plantY` is the dug hollow, which is well ABOVE the contact line in this 3/4 view.
   *     A plant anchored to soilY would stand in front of the plot instead of in it.
   */
  function placeDirt(cell) {
    const tex = cell.dirt.material.map;
    const m = metricsFor(cell.dirtUrl, DEF_DIRT) || DEF_DIRT;
    const w = lay.dirtW / Math.max(0.05, m.u[1] - m.u[0]);
    const h = w / texRatio(tex, 2);
    cell.dirt.scale.set(w, h, 1);
    cell.dirt.userData.baseScale = { x: w, y: h };
    cell.dirt.center.set(m.ax, 1 - m.ay);
    cell.bedH = h * (m.v[1] - m.v[0]);
    cell.plantY = cell.soilY + h * (m.ay - (m.plant != null ? m.plant : m.ay));

    const z = cell.row * ROW_Z;
    cell.dirt.position.set(cell.cx, cell.soilY, z);
    cell.plant.position.set(cell.cx, cell.plantY, z);
    // The ＋ marks where to tap, so it belongs in the hollow, not on the front rim.
    cell.plus.position.set(cell.cx, cell.plantY + Math.max(8, lay.rowH * 0.08), z + 0.3);
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
      // Content-fitted: `h` is how tall the PLANT is, not how tall its canvas is, so a flat
      // plant with 5% of headroom baked in does not draw 5% short of an unauthored one.
      cell.plantBase = applyFit(cell.plant, tex, url, h, DEF_GROUND);
      cell.plant.material.opacity = 1;
      cell.texUrl = url;
      cell.texStage = p.stage;
      if (!opts || opts.idle !== false) startIdle(cell);
      return tex;
    });
  }

  /**
   * Re-fit an already-loaded plant to the CURRENT layout.
   *
   * syncPlot only touches the plant art when the stage or the plant changed, so before this
   * existed a resize moved every plant to its new plot but left it drawn at the size the old
   * viewport asked for — rotate a tablet to portrait and a full-grown tree stayed desktop-sized
   * and overflowed its cell. Synchronous and token-free on purpose: it reuses the texture that
   * is already on the sprite, so it can never race a growth performance (which it skips anyway).
   */
  function refitPlant(cell) {
    const p = game.plot(cell.i);
    const tex = cell.plant.material.map;
    if (!p || cell.busy || !cell.texUrl || !tex) return;
    cell.plantBase = applyFit(cell.plant, tex, cell.texUrl, stageHeight(p.stage), DEF_GROUND);
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
    const dirtUrl = seeded ? cell.seededUrl : cell.emptyUrl;
    const dirtTex = Textures.get(dirtUrl);
    if (dirtTex && cell.dirt.material.map !== dirtTex) {
      cell.dirt.material.map = dirtTex;
      cell.dirt.material.needsUpdate = true;
      cell.dirtUrl = dirtUrl;
      // Proportions and anchor can differ between the two beds, so re-derive rather than
      // reusing the old scale — this is also what keeps the plant sitting in the hollow.
      placeDirt(cell);
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
      // The target pose has to be known BEFORE the swap (the timeline animates toward it),
      // and it must be the same content-fitted pose applyFit will install.
      const fitted = fitScale(tex, url, newH, DEF_GROUND);
      const base = { x: fitted.x, y: fitted.y };

      if (isReducedMotion()) {
        cell.plantBase = applyFit(spr, tex, url, newH, DEF_GROUND);
        spr.material.opacity = 1;
        cell.texUrl = url;
        cell.texStage = p.stage;
        fx.emit('sparkle', cell.cx, cell.plantY + base.y * 0.5, { count: 4 });
        finishGrowth();
        return;
      }

      const sparkleY = cell.plantY + base.y * 0.55;

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
          cell.plantBase = applyFit(spr, tex, url, newH, DEF_GROUND);
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

    // The wider world notices too — the nearest grass tuft and the nearest cloud take a beat.
    let tuft = null, td = Infinity;
    tufts.forEach(t => {
      if (t.material.opacity <= 0.02) return;
      const d = Math.abs(t.position.x - cell.cx);
      if (d < td) { td = d; tuft = t; }
    });
    if (tuft) tweens.delay(90, () => tweens.nudge(tuft, { angle: 0.05, ms: 320 }));
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
    // The bed is the game's primary tap target and has to READ as the focal object. The flat
    // plot is a wide shallow trough (~2.4:1 visible), where the claymation art was a tall
    // dome, so the old 0.92/2.2 pair left it the shortest thing on screen. Widening it to
    // nearly the full cell buys back the height the new proportions cost.
    lay.dirtW = Math.min(lay.colW * 0.98, lay.rowH * 2.5);
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

    // Grass fringe: a ROW of tufts standing on the horizon, spaced so they read as clumps in
    // a meadow rather than as a cut-out strip. Count follows the width; the rest are parked
    // invisible rather than destroyed, so a rotate back to landscape is free.
    const tuftH = Math.max(50, Math.min(H * 0.075, W * 0.10));
    const tuftN = Math.max(5, Math.min(TUFT_MAX, Math.round(W / (tuftH * 1.15))));
    tufts.forEach((t, i) => {
      if (i >= tuftN) { t.material.opacity = 0; return; }
      t.material.opacity = 1;
      const h = tuftH * t.userData.sizeK;
      if (t.material.map) applyFit(t, t.material.map, t.userData.url, h, DEF_GROUND);
      const step = W / tuftN;
      t.position.set(b.left + (i + 0.5) * step + t.userData.jitterX * step * 0.45,
        lay.horizonY + h * (0.10 + t.userData.lift * 0.16), 0.4);
    });

    const bushH = Math.min(H * 0.115, W * 0.17);
    bushes.forEach(b2 => {
      const h = bushH * b2.userData.sizeK;
      if (b2.material.map) {
        applyFit(b2, b2.material.map, b2.userData.url, h, DEF_GROUND);
        b2.material.opacity = 1;
      }
      b2.position.set(b.left + W * b2.userData.at, lay.horizonY + h * 0.16, 0.2);
    });

    // Hills are deliberately stretched to the full width — they are a silhouette band, not art
    // whose aspect anyone can read, and letterboxed hills would show the sky plate behind them.
    // The flat band is bottom-anchored (its ridge sits in the lower half of its canvas), so
    // pinning it just under the horizon is what stops a strip of sky showing beneath it.
    function bandTo(spr, url, bandH, y) {
      const m = metricsFor(url, DEF_CENTER) || DEF_CENTER;
      const h = bandH / Math.max(0.05, m.v[1] - m.v[0]);
      spr.scale.set(W * 1.06, h, 1);
      spr.userData.baseScale = { x: W * 1.06, y: h };
      spr.center.set(m.ax, 1 - m.ay);
      spr.position.set(0, y, spr.position.z);
    }
    bandTo(hillsFar, HILL_FAR_URL, H * 0.20, lay.horizonY + H * 0.055);
    bandTo(hills, HILL_URL, H * 0.17, lay.horizonY - 4);

    // Sun and moon key off the SHORTER axis too, and sit below the HUD reserve: on a phone the
    // four DOM tool buttons live exactly where a height-only sun would be.
    const sunH = Math.min(H * 0.19, W * 0.24);
    if (sun.material.map) applyFit(sun, sun.material.map, SUN_URL, sunH, DEF_CENTER);
    if (moon.material.map) sizeTo(moon, moon.material.map, sunH * 0.82);
    const skyY = b.top - hudReserve * (landscape ? 0.35 : 1) - sunH * 0.55;
    // Inset by the VISIBLE half-width: the flat sun carries ~11% of transparent margin on
    // each side, and insetting by the raw sprite width would push it off toward the middle.
    sun.position.set(b.right - sunH * 0.52, skyY, SUN_Z);
    moon.position.set(b.right - moon.scale.x * 0.58, skyY, SUN_Z);

    stars.forEach(s2 => {
      s2.position.set(b.left + s2.userData.rx * W, b.top - s2.userData.ry * H * 0.5, 0.2);
    });

    // Clouds are sized against the SHORTER axis too. Keying purely off world height made them
    // swallow a portrait phone's sky, because a portrait world is only ~380 units wide.
    // Retuned for content fitting: the old numbers were SPRITE heights, and the claymation
    // cloud only filled about two thirds of its canvas. Asking for the same figure as a
    // CONTENT height made every cloud half again as big — on a phone they swallowed the sky.
    // (They can no longer hide the sun whatever their size: it renders in front of both cloud
    // bands now. This cap is still here because a cloud the size of the sky is its own bug.)
    const cloudH = Math.min(H * 0.085, W * 0.19);
    clouds.forEach(c => {
      if (c.material.map) applyFit(c, c.material.map, c.userData.url, cloudH * c.userData.sizeK, DEF_CENTER);
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
      // Bed, plant anchor and the ＋ all come out of one measurement of the bed art.
      sizeTo(cell.plus, plusTexture(), Math.max(24, lay.rowH * 0.26));
      placeDirt(cell);

      // The badge rides on the bed's left shoulder, and the meter hangs just below its
      // contact line — both keyed off the bed's VISIBLE height, not the sprite's.
      cell.tag.position.set(cell.cx - dw * 0.44, cell.soilY + Math.max(lay.rowH * 0.16, cell.bedH * 0.46), z);
      // The meter moved ONTO the bed's front rim. Below the contact line it landed on the bed
      // of the row in front (the flat beds are wide and the rows overlap by design), and a
      // pale pill on dark soil reads better than a pale pill on grass anyway.
      cell.track.position.set(cell.cx, cell.soilY + Math.max(8, cell.bedH * 0.13), z);
      const tw = dw * 0.62, th = Math.max(11, lay.rowH * 0.11);
      cell.track.scale.set(tw, th, 1);
      cell.track.userData.baseScale = { x: tw, y: th };
      cell.fillH = th * 0.72;
      cell.fill.scale.y = cell.fillH;
      cell.fill.position.set(cell.cx - tw / 2, cell.track.position.y, z + 0.1);

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
    plots.forEach(c => {
      refitPlant(c);
      if (!c.busy && !c.locked && game.plot(c.i)) startIdle(c);
    });
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
    // The flat hill band is a pale, outline-free layer-2 colour that is MEANT to sit almost
    // opaque — the old 0.6 was compensating for a much darker painted silhouette, and at that
    // value the new band all but vanished into the sky.
    hills.material.opacity = 0.95 - 0.22 * n;
    hillsFar.material.opacity = 0.68 - 0.18 * n;
    // Meadow, plants and soil all dim toward a cool blue-green after dark rather than going
    // grey. Without the soil in here the plots stayed in broad daylight under a starry sky.
    const g = 1 - 0.74 * n;
    meadow.material.color.setRGB(g * 0.80, g * 0.98, g * 1.05);
    tufts.forEach(t => t.material.color.setRGB(g * 0.80, g * 0.98, g * 1.05));
    // Distance buys the far scenery a lighter wash, or the horizon goes black before the
    // foreground has finished dimming. Written per-channel so the multiplier is EXACTLY 1 in
    // daylight: the flat hill and shrub palettes are authored to sit against the meadow as
    // they are, and a permanent blue shift on them (which the meadow's own wash carries, for
    // its own historical reasons) turned the ridge line teal at noon.
    const hr = 1 - 0.62 * n, hgc = 1 - 0.50 * n, hb = 1 - 0.34 * n;
    // The flat cloud is a near-cream field where the claymation one was a soft grey, so an
    // untinted cloud now reads as a hole punched in the night sky. Washed more gently than
    // the ground — a cloud still catches the moon.
    clouds.forEach(c => c.material.color.setRGB(1 - 0.50 * n, 1 - 0.44 * n, 1 - 0.26 * n));
    bushes.forEach(b2 => b2.material.color.setRGB(hr, hgc, hb));
    hills.material.color.setRGB(hr, hgc, hb);
    hillsFar.material.color.setRGB(hr, hgc, hb);
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
  // parallax and the grass tufts lean in the same breeze the plants do — both far enough
  // below the plant amplitudes to stay atmospheric rather than distracting.
  tweens.breathe(hills, { amount: 0.006, ms: 5200, phase: 0.2 });
  tweens.driver(elapsed => {
    if (isReducedMotion()) return false;
    hills.position.x = Math.sin(elapsed / 9000) * (stage.worldWidth * 0.008);
    return false;
  }, { target: hills, keys: ['position.x'] });
  // Each tuft leans on its own phase — a row of clumps nodding in unison would be worse than
  // the stretched strip it replaced. Anchored on their contact shadows, so they pivot at the
  // ground like real grass rather than swinging from the middle.
  tufts.forEach((t, k) => {
    tweens.swayLoop(t, { angle: 0.030 + (k % 3) * 0.009, ms: 3600 + k * 190, phase: (k * 0.37) % 1 });
    tweens.breathe(t, { amount: 0.014 + (k % 4) * 0.004, ms: 2900 + k * 150, phase: (k * 0.61) % 1 });
  });
  bushes.forEach((b2, k) => {
    tweens.swayLoop(b2, { angle: 0.014 + k * 0.004, ms: 4600 + k * 480, phase: (k * 0.41) % 1 });
    tweens.breathe(b2, { amount: 0.010 + k * 0.003, ms: 3800 + k * 360, phase: (k * 0.73) % 1 });
  });

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
   * plant, a sign, and now the horizon tufts and shrubs (they used to be one stretched fringe
   * sprite and could not be considered; as discrete flat props they can).
   * Deliberately still excludes the full-bleed plates (sky, meadow, hill bands): tilting a band
   * that spans the whole world by 2° swings its corners off screen and shows the sky behind, so
   * those get their own idle motion instead and never take the tap ack.
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
    tufts.forEach(t => consider(t, t.position.x, t.position.y));
    bushes.forEach(b2 => consider(b2, b2.position.x, b2.position.y));
    consider(sun, sun.position.x, sun.position.y);
    consider(moon, moon.position.x, moon.position.y);
    plots.forEach(c => {
      consider(c.dirt, c.cx, c.soilY);
      if (c.locked) consider(c.lock, c.cx, c.lock.position.y);
      else if (game.plot(c.i)) consider(c.plant, c.cx, c.plantY + c.plantBase.y * 0.5);
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
      setSunFace('laughing', 1250);
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
        // Above SUN_Z: ordinary drifting clouds must never cover the sun's face, but a
        // rain cloud rolling across it is the whole point of a shower.
        cl.position.set(x, y + 200, SUN_Z + 1);
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
      fx.emit('waterDroplets', cell.cx, cell.plantY + cell.plantBase.y * 0.85,
        { count: 14, angle: [-Math.PI * 0.7, -Math.PI * 0.3], speed: [60, 170], gravity: -900 });
      if (p) {
        if (!cell.busy) tweens.squashStretch(cell.plant, 0.15, 520);
        setMeter(cell, p.water / game.WATERS_PER_STAGE, true);
      }
    }),

    game.on('sparkle', d => {
      const cell = plots[d.i];
      fx.emit('sparkle', cell.cx, cell.plantY + Math.max(30, cell.plantBase.y * 0.6),
        { count: d.n, spread: lay.dirtW * 0.3 });
    }),

    game.on('stage', d => {
      animateStage(d.i, d.full);
      // A bloom is the biggest thing that happens in this game; the sun is allowed to notice.
      // Surprised first, then a long laugh — long enough to still be running when a child
      // closes the celebration card.
      if (d.full) {
        setSunFace('surprised', 620);
        tweens.delay(620, () => setSunFace('laughing', 2400));
      }
    }),

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

    game.on('rain', d => {
      doRain(d);
      setSunFace('mischievous', 1500);   // it knows perfectly well what it just let in
    }),

    game.on('daynight', d => {
      applyDayNight(d.night, false);
      // game.js re-emits this every 60s whether or not anything changed, so the face reacts to
      // the TRANSITION only. Without the guard the sun pulls a face once a minute, forever.
      if (d.night !== wasNight) {
        wasNight = d.night;
        setSunFace(d.night ? 'sad' : 'happy', 1800);   // sunset on the way out, sunrise on the way in
      }
    }),

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
