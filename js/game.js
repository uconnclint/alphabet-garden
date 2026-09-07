/* ═══════════════════════════════════════════════════════════
   game.js — ALPHABET GARDEN game logic (the authoritative model).
   Plant seed letters → choose what they bloom into →
   water them, watch them grow — even while you are away.

   THIS FILE OWNS STATE, NOT PIXELS. The living world (sky, plots,
   plants, critters, weather) is drawn by the Three.js view in
   js/scenes/GardenScene.js, which subscribes to the events fired
   below via `window.GardenGame.on(...)`. Text UI — modals, HUD,
   toasts, the title screen — deliberately stays DOM, because a
   pre-reader's screen reader and a teacher's zoom both work there
   and neither works inside a canvas.
   ═══════════════════════════════════════════════════════════ */
(function () {
'use strict';

/* ---------- constants ---------- */
const SAVE_KEY = 'alphabet-garden-v1';
const LETTERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'.split('');
const TOTAL_PLOTS = 16;
const WATERS_PER_STAGE = 2;          // waters to advance one stage
const STAGE_MAX = 3;                 // 0 seed, 1 sprout, 2 growing, 3 grown
const OFFLINE_MS_PER_STAGE = 3 * 60 * 1000;   // grows 1 stage per 3 min away
const SUNSHINE_MS = 75 * 1000;       // passive water tick while playing
const WATER_COOLDOWN = 850;          // ms between waters on one plot
const PLOT_UNLOCKS = [[0, 8], [3, 12], [7, 16]]; // [plantsGrown, plotsOpen]
const RAIN_COOLDOWN = 30 * 1000;

const DB = window.PLANT_DB || {};
const TOTAL_PLANTS = LETTERS.length * 3;

/* ---------- generic art ---------- */
const ART = 'art/assets/';
// Custom AAA art assets; the inline SVG in each plant record is kept only as a fallback.
function plantArt(info, cls) {
  return '<img class="asset plant-img ' + (cls || '') + '" src="' + ART + 'plants/' + info.id + '.png" ' +
         'draggable="false" alt="' + info.name + '">';
}
function fallbackPlant(letter) {
  const hue = (LETTERS.indexOf(letter) * 137) % 360;
  return {
    id: 'x-mystery-' + letter.toLowerCase(),
    name: letter + ' Mystery Flower',
    style: 'wacky', emoji: '🌈',
    fact: 'This magical mystery flower loves the letter ' + letter + '!',
    svg: '<svg viewBox="0 0 100 120" xmlns="http://www.w3.org/2000/svg"><ellipse cx="50" cy="113" rx="22" ry="5" fill="rgba(0,0,0,0.15)"/><path d="M50 112 V60" stroke="#4d8b3f" stroke-width="6" stroke-linecap="round"/><path d="M50 88 Q30 84 26 68 Q46 72 50 82 Z" fill="#6fbe4f"/><g>' +
      [0,60,120,180,240,300].map(a => '<ellipse cx="50" cy="30" rx="12" ry="20" fill="hsl(' + ((hue + a/3)|0) + ',85%,62%)" transform="rotate(' + a + ' 50 45)"/>').join('') +
      '</g><circle cx="50" cy="45" r="13" fill="#ffd23f"/><circle cx="45" cy="42" r="2.2" fill="#4a3628"/><circle cx="55" cy="42" r="2.2" fill="#4a3628"/><path d="M44 49 Q50 54 56 49" stroke="#4a3628" stroke-width="2.5" fill="none" stroke-linecap="round"/></svg>'
  };
}

function optionsFor(letter) {
  const opts = DB[letter];
  if (Array.isArray(opts) && opts.length) return opts;
  return [fallbackPlant(letter)];
}
function getPlant(letter, id) {
  return optionsFor(letter).find(p => p.id === id) || fallbackPlant(letter);
}

/* ---------- state ---------- */
let state = loadState();
function freshState() {
  return {
    v: 1,
    plots: Array(TOTAL_PLOTS).fill(null),
    stickers: {},
    grownTotal: 0,
    muted: false,
    lastVisit: Date.now()
  };
}
function loadState() {
  try {
    const raw = localStorage.getItem(SAVE_KEY);
    if (!raw) return freshState();
    const s = JSON.parse(raw);
    if (!s || s.v !== 1 || !Array.isArray(s.plots)) return freshState();
    while (s.plots.length < TOTAL_PLOTS) s.plots.push(null);
    s.stickers = s.stickers || {};
    s.muted = false;   // always start unmuted; mute is per-session, never remembered
    return s;
  } catch (e) { return freshState(); }
}
function save() {
  state.lastVisit = Date.now();
  try { localStorage.setItem(SAVE_KEY, JSON.stringify(state)); } catch (e) {}
}

function plotsOpen() {
  let open = 8;
  for (const [need, n] of PLOT_UNLOCKS) if (state.grownTotal >= need) open = n;
  return open;
}
function nextUnlock() {
  for (const [need, n] of PLOT_UNLOCKS) if (state.grownTotal < need) return { need, n };
  return null;
}
function stickerCount() { return Object.keys(state.stickers).length; }

/* ---------- audio ---------- */
let actx = null;
function audio() {
  if (!actx) { try { actx = new (window.AudioContext || window.webkitAudioContext)(); } catch (e) {} }
  // Only wake the context when sound is allowed, so a muted context stays silent.
  if (actx && actx.state === 'suspended' && !state.muted) actx.resume();
  return actx;
}
function tone(freq, dur, type, vol, when, slideTo) {
  if (state.muted) return;
  const ac = audio(); if (!ac) return;
  const t = ac.currentTime + (when || 0);
  const o = ac.createOscillator(), g = ac.createGain();
  o.type = type || 'sine'; o.frequency.setValueAtTime(freq, t);
  if (slideTo) o.frequency.exponentialRampToValueAtTime(slideTo, t + dur);
  g.gain.setValueAtTime(0.0001, t);
  g.gain.exponentialRampToValueAtTime(vol || 0.15, t + 0.02);
  g.gain.exponentialRampToValueAtTime(0.0001, t + dur);
  o.connect(g).connect(ac.destination);
  o.start(t); o.stop(t + dur + 0.05);
}
function noise(dur, filterFreq, vol, when) {
  if (state.muted) return;
  const ac = audio(); if (!ac) return;
  const t = ac.currentTime + (when || 0);
  const len = Math.max(1, (dur * ac.sampleRate) | 0);
  const buf = ac.createBuffer(1, len, ac.sampleRate);
  const d = buf.getChannelData(0);
  for (let i = 0; i < len; i++) d[i] = Math.random() * 2 - 1;
  const src = ac.createBufferSource(); src.buffer = buf;
  const f = ac.createBiquadFilter(); f.type = 'bandpass'; f.frequency.value = filterFreq;
  const g = ac.createGain();
  g.gain.setValueAtTime(vol || 0.12, t);
  g.gain.exponentialRampToValueAtTime(0.0001, t + dur);
  src.connect(f).connect(g).connect(ac.destination);
  src.start(t);
}
const sfx = {
  click:  () => tone(650, 0.08, 'square', 0.06),
  plop:   () => { tone(180, 0.15, 'sine', 0.2, 0, 90); tone(320, 0.1, 'sine', 0.1, 0.08, 500); },
  water:  () => { noise(0.35, 2400, 0.1); tone(900, 0.12, 'sine', 0.05, 0.05, 1400); },
  grow:   () => { tone(523, 0.15, 'triangle', 0.14); tone(659, 0.15, 'triangle', 0.14, 0.12); tone(784, 0.22, 'triangle', 0.16, 0.24); },
  fanfare:() => { [523, 659, 784, 1047].forEach((f, i) => tone(f, 0.22, 'triangle', 0.16, i * 0.14));
                  [523, 659, 784, 1047].forEach((f, i) => tone(f * 2, 0.18, 'sine', 0.05, i * 0.14));
                  tone(1319, 0.5, 'triangle', 0.14, 0.6); },
  poof:   () => { noise(0.3, 600, 0.14); tone(300, 0.25, 'triangle', 0.12, 0, 80); },
  buzz:   () => tone(140, 0.2, 'sawtooth', 0.07),
  rain:   () => noise(1.6, 3000, 0.06),
  page:   () => noise(0.15, 1800, 0.06)
};

/* ---------- voice (pre-rendered Chatterbox clips, voice: Jade) ----------
   Plays a real narration clip (art/audio/<key>.m4a) when present.
   If a clip is missing, it gracefully falls back to the browser's speech
   synthesis using the same words — so the game is always fully narrated,
   and each clip added later replaces its fallback with no code changes. */
const ART_AUDIO = 'art/audio/';
const ART_AUDIO_EXT = '.m4a';
let currentVoice = null;
const voiceCache = {};       // key -> HTMLAudioElement, or 'missing'
const VOICE_UI_TEXT = {
  'ui-plant': 'Yay! You planted a seed! Now tap it with water to help it grow!',
  'ui-rain': 'Rain, rain, water the garden!',
  'ui-offline': 'Wow! Your garden grew while you were away!',
  'ui-sound-on': 'Sound is on!',
  'ui-welcome': 'Welcome to Alphabet Garden! Tap the dirt to plant a seed letter!',
  'ui-welcome-back': 'Welcome back to your Alphabet Garden!'
};
function voiceText(key) {
  if (key in VOICE_UI_TEXT) return VOICE_UI_TEXT[key];
  if (key.slice(0, 7) === 'letter-') return key.slice(7).toUpperCase() + '!';
  if (key.slice(0, 6) === 'plant-') {
    const id = key.slice(6);
    const info = getPlant(id.charAt(0).toUpperCase(), id);
    return info ? info.name + '! ' + info.fact : null;
  }
  return null;
}
function speakFallback(key) {
  if (state.muted || !('speechSynthesis' in window)) return;
  const text = voiceText(key);
  if (!text) return;
  try {
    speechSynthesis.cancel();
    const u = new SpeechSynthesisUtterance(text);
    u.rate = 0.95; u.pitch = 1.1;
    speechSynthesis.speak(u);
  } catch (e) {}
}
// Play a narration clip by key (e.g. "plant-b-butterfly-bush", "letter-a", "ui-rain").
function voice(key) {
  if (state.muted || !key) return;
  stopVoice();
  const cached = voiceCache[key];
  if (cached === 'missing') { speakFallback(key); return; }
  let a = cached;
  if (!a) {
    a = new Audio(ART_AUDIO + key + ART_AUDIO_EXT);
    a.preload = 'auto';
    a.addEventListener('error', function () {
      voiceCache[key] = 'missing';
      if (currentVoice === a) { currentVoice = null; speakFallback(key); }
    });
    voiceCache[key] = a;
  }
  try { a.currentTime = 0; } catch (e) {}
  currentVoice = a;
  const p = a.play();
  if (p && p.catch) p.catch(function () {});
}
function stopVoice() {
  if (currentVoice) {
    try { currentVoice.pause(); currentVoice.currentTime = 0; } catch (e) {}
    currentVoice = null;
  }
  try { speechSynthesis.cancel(); } catch (e) {}
}

/* ---------- dom helpers ---------- */
const $ = s => document.querySelector(s);
function el(tag, cls, html) {
  const n = document.createElement(tag);
  if (cls) n.className = cls;
  if (html != null) n.innerHTML = html;
  return n;
}
let toastTimer = null;
function toast(msg, ms) {
  const t = $('#toast');
  t.textContent = msg; t.classList.add('show');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => t.classList.remove('show'), ms || 2600);
}

/* ---------- view events ----------
   A tiny emitter is all the coupling the view needs: game.js never learns what a
   sprite is, and GardenScene never learns what a save file is. */
const listeners = Object.create(null);
function on(evt, fn) {
  (listeners[evt] || (listeners[evt] = [])).push(fn);
  return function () { off(evt, fn); };
}
function off(evt, fn) {
  const a = listeners[evt]; if (!a) return;
  const i = a.indexOf(fn); if (i >= 0) a.splice(i, 1);
}
function emit(evt, data) {
  const a = listeners[evt]; if (!a || !a.length) return;
  // Copy first: a handler that unsubscribes mid-dispatch must not shift the array we walk.
  const copy = a.slice();
  for (let i = 0; i < copy.length; i++) {
    // One broken listener must never take the game logic down with it — a kid whose
    // GPU dropped the canvas still needs planting and saving to work.
    try { copy[i](data); } catch (e) { console.error('[garden] "' + evt + '" listener failed', e); }
  }
}

/* ---------- garden rendering (delegated to the view) ---------- */
function renderPlot(i, fx) { emit('plot', { i: i, pop: !!(fx && fx.pop) }); }
function renderAll() {
  emit('plots', { open: plotsOpen() });
  updateHud();
}
function updateHud() {
  $('#stat-grown b').textContent = state.grownTotal;
  $('#stat-stickers b').textContent = stickerCount();
  $('#btn-sound').classList.toggle('muted', state.muted);
}

/* ---------- particles ----------
   Plot-local effects live in WebGL now; the confetti layer stays DOM because it has to
   rain down OVER the celebration modal, which is DOM. */
function dropletFX(i) { emit('water', { i: i }); }
function sparkleFX(i, n) { emit('sparkle', { i: i, n: n || 6 }); }
function confetti(n) {
  const layer = $('#confetti-layer');
  const emo = ['🎉', '⭐', '🌸', '🌼', '💛', '🦋'];
  const colors = ['#ff6b6b', '#ffd23f', '#6ec6ff', '#8ed46a', '#c65fd1', '#ff8a3d'];
  for (let k = 0; k < (n || 50); k++) {
    const paper = Math.random() < 0.6;
    const c = el('div', 'confetto' + (paper ? ' paper' : ''), paper ? '' : emo[(Math.random() * emo.length) | 0]);
    if (paper) c.style.background = colors[(Math.random() * colors.length) | 0];
    c.style.left = (Math.random() * 100) + 'vw';
    c.style.animationDuration = (1.8 + Math.random() * 1.8) + 's';
    c.style.animationDelay = (Math.random() * 0.5) + 's';
    layer.appendChild(c);
    setTimeout(() => c.remove(), 4200);
  }
}

/* ---------- planting flow ---------- */
let pendingPlot = -1;
let shovelMode = false;
let shovelArm = { i: -1, until: 0 };
const waterCooldowns = {};

function onPlotTap(i) {
  const open = plotsOpen();
  if (i >= open) {
    sfx.buzz();
    const nu = nextUnlock();
    if (nu) toast('🔒 Grow ' + (nu.need - state.grownTotal) + ' more plants to open this plot!');
    emit('nope', { i: i });
    return;
  }
  const plant = state.plots[i];

  if (shovelMode) {
    if (!plant) { toast('Nothing to dig here!'); sfx.click(); return; }
    const now = Date.now();
    if (shovelArm.i === i && now < shovelArm.until) {
      digUp(i);
    } else {
      shovelArm = { i, until: now + 2500 };
      emit('nope', { i: i });
      sfx.click();
      toast('Tap again to dig it up! 🪏');
    }
    return;
  }

  if (!plant) {
    pendingPlot = i;
    openLetterPicker();
    return;
  }
  if (plant.stage < STAGE_MAX) {
    waterPlot(i);
  } else {
    celebrate(i, plant.seen);
  }
}

function digUp(i) {
  const plant = state.plots[i];
  const info = getPlant(plant.letter, plant.plantId);
  state.plots[i] = null;
  save();
  sfx.poof();
  emit('dug', { i: i });
  renderPlot(i);
  toast('Bye-bye, ' + info.name + '! 👋');
  setShovel(false);
}

function waterPlot(i) {
  const now = Date.now();
  if (waterCooldowns[i] && now - waterCooldowns[i] < WATER_COOLDOWN) return;
  waterCooldowns[i] = now;
  const plant = state.plots[i];
  plant.water++;
  plant.ts = now;
  sfx.water();
  dropletFX(i);
  if (plant.water >= WATERS_PER_STAGE) {
    plant.water = 0;
    setTimeout(() => advanceStage(i, true), 500);
  } else {
    renderPlot(i);
  }
  save();
}

function advanceStage(i, interactive) {
  const plant = state.plots[i]; if (!plant || plant.stage >= STAGE_MAX) return;
  const from = plant.stage;
  plant.stage++;
  plant.ts = Date.now();
  // Fired BEFORE the save/render bookkeeping so the view can start its anticipation dip on the
  // same frame the stage flips — a late animation reads as a snap, which is the whole thing
  // we are trying to avoid.
  emit('stage', { i: i, from: from, to: plant.stage, full: plant.stage === STAGE_MAX, interactive: !!interactive });
  if (plant.stage === STAGE_MAX) {
    state.grownTotal++;
    const info = getPlant(plant.letter, plant.plantId);
    const isNewSticker = !state.stickers[info.id];
    state.stickers[info.id] = true;
    plant.newSticker = isNewSticker;
    if (interactive) {
      plant.seen = true;
      save();
      renderAll();                       // may unlock plots
      sfx.fanfare();
      confetti(60);
      // Let the bloom actually play before the modal covers it. The bloom is the payoff for
      // every tap the child has spent on this plot; opening the card on the same frame threw
      // it away. Everything else about the flow is unchanged.
      setTimeout(function () { celebrate(i, false); }, 900);
    } else {
      plant.seen = false;
      save();
      renderAll();
      if (started) {
        sfx.grow();
        sparkleFX(i, 8);
        toast('✨ ' + info.name + ' is fully grown! Tap it! ✨');
      }
    }
  } else {
    save();
    sfx.grow();
    sparkleFX(i, 5);
    renderPlot(i, { pop: true });
    updateHud();
  }
}

/* ---------- celebration ---------- */
function celebrate(i, replay) {
  const plant = state.plots[i];
  const info = getPlant(plant.letter, plant.plantId);
  const firstLook = !plant.seen;
  plant.seen = true;
  save();
  renderPlot(i);
  $('#grown-svg').innerHTML = plantArt(info);
  $('#grown-name').textContent = info.emoji + ' ' + info.name;
  $('#grown-fact').textContent = info.fact;
  $('#grown-sticker').style.display = (firstLook && plant.newSticker) ? '' : 'none';
  openModal('#modal-grown');
  if (firstLook) { sfx.fanfare(); confetti(60); } else { sfx.grow(); confetti(18); }
  voice('plant-' + info.id);
}

/* ---------- letter picker ---------- */
function openLetterPicker() {
  const grid = $('#letter-grid');
  grid.innerHTML = '';
  LETTERS.forEach((L, idx) => {
    const found = optionsFor(L).filter(p => state.stickers[p.id]).length;
    const b = el('button', 'letter-btn', L + '<span class="mini-count">' + (found ? '⭐' + found + '/3' : '&nbsp;') + '</span>');
    b.style.background = 'hsl(' + ((idx * 137) % 360) + ', 75%, 58%)';
    b.addEventListener('click', () => {
      sfx.click();
      voice('letter-' + L.toLowerCase());
      openChoice(L);
    });
    grid.appendChild(b);
  });
  openModal('#modal-letters');
}

function openChoice(L) {
  closeModal('#modal-letters');
  $('#choice-title').textContent = 'What will your ' + L + ' seed become?';
  const wrap = $('#choice-cards');
  wrap.innerHTML = '';
  const badges = { realistic: '🌿 Real!', silly: '😄 Silly!', wacky: '🤪 Wacky!' };
  optionsFor(L).forEach(p => {
    const card = el('div', 'choice-card',
      '<div class="preview">' + plantArt(p) + '</div>' +
      '<h3>' + p.emoji + ' ' + p.name + '</h3>' +
      '<span class="badge ' + p.style + '">' + (badges[p.style] || '🌱') + '</span>');
    card.addEventListener('click', () => plantSeed(L, p));
    wrap.appendChild(card);
  });
  openModal('#modal-choice');
}

function plantSeed(L, p) {
  closeModal('#modal-choice');
  if (pendingPlot < 0 || state.plots[pendingPlot]) return;
  state.plots[pendingPlot] = {
    letter: L, plantId: p.id, stage: 0, water: 0,
    ts: Date.now(), seen: true, newSticker: false
  };
  save();
  sfx.plop();
  emit('planted', { i: pendingPlot, letter: L, plantId: p.id });
  sparkleFX(pendingPlot, 4);
  voice('ui-plant');
  toast('🌱 ' + p.name + ' seed planted! Tap it to water it! 💧');
  pendingPlot = -1;
}

/* ---------- sticker book ---------- */
function openBook() {
  sfx.page();
  const pages = $('#book-pages');
  pages.innerHTML = '';
  let found = 0;
  LETTERS.forEach(L => {
    const row = el('div', 'book-row');
    row.appendChild(el('div', 'book-letter', L));
    const slots = el('div', 'book-slots');
    optionsFor(L).forEach(p => {
      const has = !!state.stickers[p.id];
      if (has) found++;
      const slot = el('div', 'book-slot ' + (has ? 'unlocked' : 'locked'),
        '<div class="thumb">' + (has ? plantArt(p) : '?') + '</div>' + (has ? p.emoji + ' ' + p.name : '? ? ?'));
      if (has) slot.addEventListener('click', () => voice('plant-' + p.id));
      slots.appendChild(slot);
    });
    row.appendChild(slots);
    pages.appendChild(row);
  });
  const pct = Math.round((found / TOTAL_PLANTS) * 100);
  $('#book-progress-fill').style.width = pct + '%';
  $('#book-progress-label').textContent = found + ' of ' + TOTAL_PLANTS + ' plants discovered!';
  openModal('#modal-book');
}

/* ---------- rain ---------- */
let lastRain = 0;
function makeItRain() {
  const now = Date.now();
  if (now - lastRain < RAIN_COOLDOWN) {
    toast('☁️ The rain cloud is resting! Try again soon.');
    sfx.buzz();
    return;
  }
  lastRain = now;
  const btn = $('#btn-rain');
  btn.disabled = true;
  setTimeout(() => { btn.disabled = false; }, RAIN_COOLDOWN);

  sfx.rain();
  voice('ui-rain');
  // The view owns the clouds, the drops and the rainbow; the timings below stay here because
  // they are gameplay (when the watering lands), not decoration.
  emit('rain', { cloudsMs: 3400, rainbowMs: 5000 });

  setTimeout(() => {
    state.plots.forEach((p, i) => {
      if (p && p.stage < STAGE_MAX && i < plotsOpen()) {
        p.water++;
        p.ts = Date.now();
        dropletFX(i);
        if (p.water >= WATERS_PER_STAGE) {
          p.water = 0;
          setTimeout(() => advanceStage(i, false), 600 + Math.random() * 600);
        } else renderPlot(i);
      }
    });
    save();
  }, 1400);
}

/* ---------- offline growth ---------- */
function applyOfflineGrowth() {
  const now = Date.now();
  let grewCount = 0;
  state.plots.forEach((p, i) => {
    if (!p || p.stage >= STAGE_MAX) return;
    const elapsed = now - (p.ts || now);
    const gained = Math.floor(elapsed / OFFLINE_MS_PER_STAGE);
    if (gained <= 0) return;
    const target = Math.min(STAGE_MAX, p.stage + gained);
    while (p.stage < target) {
      p.stage++;
      if (p.stage === STAGE_MAX) {
        state.grownTotal++;
        const info = getPlant(p.letter, p.plantId);
        p.newSticker = !state.stickers[info.id];
        state.stickers[info.id] = true;
        p.seen = false;
      }
    }
    p.ts = now; p.water = 0;
    grewCount++;
  });
  if (grewCount > 0) {
    save();
    setTimeout(() => {
      toast('✨ Your garden grew while you were away! ✨', 3500);
      voice('ui-offline');
      confetti(25);
    }, 1200);
  }
  return grewCount;
}

/* ---------- passive sunshine growth ---------- */
setInterval(() => {
  if (!started) return;
  let changed = false;
  state.plots.forEach((p, i) => {
    if (p && p.stage < STAGE_MAX && i < plotsOpen()) {
      p.water++;
      p.ts = Date.now();
      changed = true;
      if (p.water >= WATERS_PER_STAGE) {
        p.water = 0;
        advanceStage(i, false);
      } else renderPlot(i);
      sparkleFX(i, 1);
    }
  });
  if (changed) save();
}, SUNSHINE_MS);

/* ---------- sky clock ----------
   Same rule as before (night from 7pm to 6am); the view cross-fades to it. Sky, stars,
   clouds and critters are all drawn by GardenScene now. */
function isNight() {
  const h = new Date().getHours();
  return h < 6 || h >= 19;
}
function applyDayNight() {
  const night = isNight();
  // body.night still drives the DOM chrome (title screen, toast tint) — the world reads the event.
  document.body.classList.toggle('night', night);
  emit('daynight', { night: night });
}
function startClock() {
  applyDayNight();
  setInterval(applyDayNight, 60 * 1000);
}

/* ---------- modals ---------- */
function openModal(sel) { $(sel).classList.remove('hidden'); }
function closeModal(sel) { $(sel).classList.add('hidden'); }
document.querySelectorAll('.modal').forEach(m => {
  m.addEventListener('pointerdown', e => { if (e.target === m) { m.classList.add('hidden'); sfx.click(); } });
  const x = m.querySelector('.modal-close');
  if (x) x.addEventListener('click', () => { m.classList.add('hidden'); sfx.click(); });
});
$('#grown-ok').addEventListener('click', () => { closeModal('#modal-grown'); sfx.click(); });

/* ---------- hud buttons ---------- */
function setShovel(on) {
  shovelMode = on;
  shovelArm = { i: -1, until: 0 };
  $('#btn-shovel').classList.toggle('active', on);
  if (on) toast('🪏 Shovel time! Tap a plant twice to dig it up.');
}
$('#btn-shovel').addEventListener('click', () => { sfx.click(); setShovel(!shovelMode); });
$('#btn-book').addEventListener('click', openBook);
$('#btn-rain').addEventListener('click', makeItRain);
$('#btn-sound').addEventListener('click', () => {
  state.muted = !state.muted;
  save(); updateHud();
  if (state.muted) {
    // Kill everything already in flight: scheduled tones/noise, clip playback, and any narration.
    stopVoice();
    if (actx && actx.suspend) { try { actx.suspend(); } catch (e) {} }
  } else {
    if (actx && actx.resume) { try { actx.resume(); } catch (e) {} }
    sfx.grow(); voice('ui-sound-on');
  }
});

/* ---------- title screen ---------- */
let started = false;
function buildTitle() {
  const hasSave = state.plots.some(Boolean);
  $('#title-hint').textContent = hasSave
    ? '🌼 Welcome back! Your garden was waiting for you!'
    : '🌱 Tap an empty dirt patch to plant your first seed!';
}
$('#btn-play').addEventListener('click', () => {
  started = true;
  audio();
  sfx.fanfare();
  $('#title-screen').classList.add('gone');
  const grew = applyOfflineGrowth();
  renderAll();
  emit('start', { grew: grew });
  const hasSave = state.plots.some(Boolean);
  if (!grew) {
    voice(hasSave ? 'ui-welcome-back' : 'ui-welcome');
  }
});

/* ---------- public model, for the view ----------
   Read-only by contract: the view asks questions and reports taps; every mutation still
   happens in here. Exposed on `window` (not as an ES export) because game.js is a classic
   script that has to keep running even if the module graph fails to load. */
window.GardenGame = {
  TOTAL_PLOTS: TOTAL_PLOTS,
  STAGE_MAX: STAGE_MAX,
  WATERS_PER_STAGE: WATERS_PER_STAGE,
  on: on,
  off: off,
  plot: function (i) { return state.plots[i] || null; },
  plotsOpen: plotsOpen,
  nextUnlock: nextUnlock,
  grownTotal: function () { return state.grownTotal; },
  getPlant: getPlant,
  isNight: isNight,
  isStarted: function () { return started; },
  isMuted: function () { return state.muted; },
  isShovelMode: function () { return shovelMode; },
  tapPlot: onPlotTap
};

/* ---------- boot ---------- */
startClock();
buildTitle();
updateHud();
window.addEventListener('beforeunload', save);
document.addEventListener('visibilitychange', () => { if (document.hidden) save(); });

})();
