// tween.js — animation core: tweens, timelines, springs, easings and game-feel helpers.
//
// This is what makes the garden feel alive. Everything that moves should move through here so
// that (a) reduced motion is honoured in one place and (b) nothing fights over the same property.
//
// ── DRIVING IT ──────────────────────────────────────────────────────────────────
// The manager does not own a rAF loop; the stage does. Wire it once at boot:
//
//   import { attachTweensTo } from './systems/tween.js';
//   attachTweensTo(stage);      // stage.onUpdate(dt => tweens.update(dt))
//
// `update(dt)` takes SECONDS (what stage.onUpdate delivers). Every duration/delay in the
// public API is in MILLISECONDS, because that is how designers talk about timing.
//
// ── TWEENING ────────────────────────────────────────────────────────────────────
//   tweens.to(sprite, { 'position.y': 320, 'material.opacity': 0 },
//             { duration: 420, ease: 'backOut', delay: 100, onComplete });
//
// Property keys are dot paths on the target ('position.x', 'scale.y', 'material.opacity',
// 'material.rotation'). Starting a tween cancels any other tween/driver on the SAME target
// touching the SAME properties, so a re-tap never produces two animations fighting.
//
// ── TIMELINES ───────────────────────────────────────────────────────────────────
//   tweens.timeline()
//     .to(a, { 'scale.y': 120 }, { duration: 300 })
//     .wait(120)
//     .parallel([ t => t.to(b, {...}), t => t.to(c, {...}) ])
//     .call(() => sfx('bloom'))
//     .start();
//
// ── SPRINGS ─────────────────────────────────────────────────────────────────────
//   tweens.spring(sprite, { 'position.x': 0 }, { stiffness: 200, damping: 16 });
// A real integrator, not an eased curve: interrupting it keeps the current velocity.
//
// ── GAME FEEL HELPERS ───────────────────────────────────────────────────────────
//   pop(obj)                    scale punch-in (planting, appearing)
//   squashStretch(obj, amt, ms) squash then elastic recovery (landing, watering)
//   wobble(obj, opts)           damped rotational wobble (bumped, wrong answer)
//   nudge(obj, opts)            ONE out-and-back tilt (±2°/200ms) — the "everything reacts" ack
//   press(obj, opts)            the full §4.3 press cycle; handle.release() on pointer-up
//   shake(obj, opts)            damped positional shake (impact)
//   breathe(obj, opts)          LOOPING gentle scale idle — returns { cancel() }
//   swayLoop(obj, opts)         LOOPING gentle rotation idle — returns { cancel() }
//
// ── REDUCED MOTION ──────────────────────────────────────────────────────────────
// Honoured at two layers, per house style: the OS `prefers-reduced-motion` media query AND a
// teacher-settable in-game toggle. When on, tweens snap to their end state on the next update
// (onComplete STILL fires, so game logic never stalls) and idle loops hold their base pose.
//   setReducedMotion(true|false|'auto')   'auto' = follow the OS only
//   isReducedMotion()  prefersReducedMotion()  onReducedMotionChange(cb)
//
// ── API ─────────────────────────────────────────────────────────────────────────
//   tweens (singleton), createTweenManager(), attachTweensTo(stage), Easing,
//   setReducedMotion, isReducedMotion, prefersReducedMotion, onReducedMotionChange,
//   pop, squashStretch, wobble, shake, breathe, swayLoop

/* ═══════════════════════════ reduced motion ═══════════════════════════ */

let _osQuery = null;
try {
  _osQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
} catch (e) { _osQuery = null; }

let _toggle = 'auto'; // 'auto' | true | false
const _rmCbs = [];

/** True if the OS asks for reduced motion. */
export function prefersReducedMotion() {
  return !!(_osQuery && _osQuery.matches);
}

/** Effective state: the in-game toggle wins; 'auto' defers to the OS. */
export function isReducedMotion() {
  if (_toggle === true) return true;
  if (_toggle === false) return false;
  return prefersReducedMotion();
}

/** @param {boolean|'auto'} v */
export function setReducedMotion(v) {
  const before = isReducedMotion();
  _toggle = (v === 'auto') ? 'auto' : !!v;
  const after = isReducedMotion();
  if (before !== after) _rmCbs.forEach(cb => cb(after));
}

/** @returns {function} unsubscribe */
export function onReducedMotionChange(cb) {
  _rmCbs.push(cb);
  return () => { const i = _rmCbs.indexOf(cb); if (i >= 0) _rmCbs.splice(i, 1); };
}

if (_osQuery && _osQuery.addEventListener) {
  _osQuery.addEventListener('change', () => {
    if (_toggle === 'auto') _rmCbs.forEach(cb => cb(isReducedMotion()));
  });
}

/* ═══════════════════════════ easing ═══════════════════════════ */

const c1 = 1.70158;        // classic "back" overshoot constant
const c2 = c1 * 1.525;
const c3 = c1 + 1;
const c4 = (2 * Math.PI) / 3;
const c5 = (2 * Math.PI) / 4.5;

function bounceOut(t) {
  const n1 = 7.5625, d1 = 2.75;
  if (t < 1 / d1) return n1 * t * t;
  if (t < 2 / d1) return n1 * (t -= 1.5 / d1) * t + 0.75;
  if (t < 2.5 / d1) return n1 * (t -= 2.25 / d1) * t + 0.9375;
  return n1 * (t -= 2.625 / d1) * t + 0.984375;
}

/** Named easing curves. All take and return 0..1 (back/elastic overshoot outside that range). */
export const Easing = {
  linear: t => t,

  quadIn: t => t * t,
  quadOut: t => 1 - (1 - t) * (1 - t),
  quadInOut: t => (t < 0.5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2),

  cubicIn: t => t * t * t,
  cubicOut: t => 1 - Math.pow(1 - t, 3),
  cubicInOut: t => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2),

  quartOut: t => 1 - Math.pow(1 - t, 4),
  quartInOut: t => (t < 0.5 ? 8 * t * t * t * t : 1 - Math.pow(-2 * t + 2, 4) / 2),

  // The house "settle" curve — cubic-bezier(0.22, 1, 0.36, 1) in the standard's table.
  quintOut: t => 1 - Math.pow(1 - t, 5),

  sineIn: t => 1 - Math.cos((t * Math.PI) / 2),
  sineOut: t => Math.sin((t * Math.PI) / 2),
  sineInOut: t => -(Math.cos(Math.PI * t) - 1) / 2,

  expoOut: t => (t >= 1 ? 1 : 1 - Math.pow(2, -10 * t)),
  expoInOut: t => (t === 0 ? 0 : t === 1 ? 1 :
    t < 0.5 ? Math.pow(2, 20 * t - 10) / 2 : (2 - Math.pow(2, -20 * t + 10)) / 2),

  backIn: t => c3 * t * t * t - c1 * t * t,
  backOut: t => 1 + c3 * Math.pow(t - 1, 3) + c1 * Math.pow(t - 1, 2),
  backInOut: t => (t < 0.5
    ? (Math.pow(2 * t, 2) * ((c2 + 1) * 2 * t - c2)) / 2
    : (Math.pow(2 * t - 2, 2) * ((c2 + 1) * (t * 2 - 2) + c2) + 2) / 2),

  elasticIn: t => (t === 0 ? 0 : t === 1 ? 1
    : -Math.pow(2, 10 * t - 10) * Math.sin((t * 10 - 10.75) * c4)),
  elasticOut: t => (t === 0 ? 0 : t === 1 ? 1
    : Math.pow(2, -10 * t) * Math.sin((t * 10 - 0.75) * c4) + 1),
  elasticInOut: t => (t === 0 ? 0 : t === 1 ? 1 : t < 0.5
    ? -(Math.pow(2, 20 * t - 10) * Math.sin((20 * t - 11.125) * c5)) / 2
    : (Math.pow(2, -20 * t + 10) * Math.sin((20 * t - 11.125) * c5)) / 2 + 1),

  bounceOut,
  bounceIn: t => 1 - bounceOut(1 - t),
  bounceInOut: t => (t < 0.5 ? (1 - bounceOut(1 - 2 * t)) / 2 : (1 + bounceOut(2 * t - 1)) / 2)
};

function resolveEase(ease) {
  if (typeof ease === 'function') return ease;
  if (typeof ease === 'string' && Easing[ease]) return Easing[ease];
  return Easing.cubicOut; // the safe, friendly default
}

/* ═══════════════════════════ property paths ═══════════════════════════ */

function getPath(obj, path) {
  if (path.indexOf('.') < 0) return obj[path];
  const parts = path.split('.');
  let o = obj;
  for (let i = 0; i < parts.length - 1; i++) {
    o = o[parts[i]];
    if (o == null) return undefined;
  }
  return o[parts[parts.length - 1]];
}

function setPath(obj, path, value) {
  if (path.indexOf('.') < 0) { obj[path] = value; return; }
  const parts = path.split('.');
  let o = obj;
  for (let i = 0; i < parts.length - 1; i++) {
    o = o[parts[i]];
    if (o == null) return;
  }
  o[parts[parts.length - 1]] = value;
}

/** Sprites rotate through their material; everything else through rotation.z. */
export function rotationPath(obj) {
  return (obj && obj.isSprite) ? 'material.rotation' : 'rotation.z';
}

/** Base (unanimated) scale of a sprite made by createSprite, or its current scale. */
export function baseScaleOf(obj) {
  const b = obj && obj.userData && obj.userData.baseScale;
  if (b) return { x: b.x, y: b.y };
  return { x: obj.scale.x, y: obj.scale.y };
}

/* ═══════════════════════════ manager ═══════════════════════════ */

let _uid = 0;

/**
 * Create an independent tween manager. Most code should use the `tweens` singleton;
 * a separate manager is useful for e.g. a modal that must pause the world's tweens.
 */
export function createTweenManager() {
  /** @type {Array<object>} live items: tweens, springs, drivers, timelines */
  const items = [];
  const adds = [];   // added during update() — applied after the pass, so no mutation mid-loop
  let updating = false;

  function push(item) {
    if (updating) adds.push(item);
    else items.push(item);
    return item;
  }

  /**
   * Resolve conflicts when something starts animating properties another item already owns.
   *
   * One-off animations KILL each other (a second tap should restart the pop, not blend two).
   * Idle LOOPS (breathe/swayLoop) are only SUSPENDED — they snap back to their base pose, wait
   * for the interrupting animation to finish, then pick up again. Without this, watering a plant
   * once would silently stop it breathing for the rest of the session.
   */
  function claim(item) {
    if (!item.target || !item.keys || !item.keys.length) return;
    for (let i = 0; i < items.length; i++) {
      const o = items[i];
      if (o === item || o.dead || o.target !== item.target || !o.keys) continue;
      let overlaps = false;
      for (let k = 0; k < item.keys.length; k++) {
        if (o.keys.indexOf(item.keys[k]) >= 0) { overlaps = true; break; }
      }
      if (!overlaps) continue;
      if (o.isLoop && !item.isLoop) {
        o.suspended = true;
        o.blockedBy = item;
        if (o.onKilled) o.onKilled(); // restore base pose so the interrupter measures it correctly
      } else {
        o.dead = true;
        if (o.onKilled) o.onKilled();
      }
    }
  }

  const mgr = {
    /** Number of live animations — handy for debug readouts. */
    get count() { return items.length; },

    /**
     * Advance every animation.
     * @param {number} dt seconds (as delivered by stage.onUpdate)
     */
    update(dt) {
      const ms = dt * 1000;
      updating = true;
      for (let i = 0; i < items.length; i++) {
        const it = items[i];
        if (it.dead) continue;
        if (it.suspended) {
          if (it.blockedBy && !it.blockedBy.dead) continue;
          it.suspended = false;
          it.blockedBy = null;
        }
        if (it.tick(ms) === true) it.dead = true;
      }
      updating = false;
      // Compact in place; no allocation.
      let w = 0;
      for (let i = 0; i < items.length; i++) if (!items[i].dead) items[w++] = items[i];
      items.length = w;
      for (let i = 0; i < adds.length; i++) items.push(adds[i]);
      adds.length = 0;
    },

    /**
     * Tween dot-path properties on a target.
     * @param {object} target
     * @param {Object<string,number>} props end values keyed by dot path
     * @param {object} [o]
     * @param {number} [o.duration=300] ms
     * @param {number} [o.delay=0] ms
     * @param {string|function} [o.ease='cubicOut']
     * @param {Object<string,number>} [o.from] explicit start values
     * @param {number} [o.repeat=0] extra repetitions (-1 = forever)
     * @param {boolean} [o.yoyo=false] reverse on alternate repetitions
     * @param {function} [o.onUpdate] (t01, target)
     * @param {function} [o.onComplete] (target)
     * @param {boolean} [o.ignoreReducedMotion=false] animate even in reduced motion
     * @returns {object} handle { cancel(), finish(), promise(), id }
     */
    to(target, props, o) {
      o = o || {};
      const keys = Object.keys(props);
      const reduced = isReducedMotion() && !o.ignoreReducedMotion;
      const item = {
        id: ++_uid,
        target, keys,
        dead: false,
        started: false,
        elapsed: 0,
        delay: reduced ? 0 : (o.delay || 0),
        duration: reduced ? 0 : Math.max(0, o.duration != null ? o.duration : 300),
        ease: resolveEase(o.ease),
        from: null,
        to: props,
        fromOpt: o.from || null,
        repeatsLeft: reduced ? 0 : (o.repeat || 0),
        yoyo: !!o.yoyo,
        reversed: false,
        onUpdate: o.onUpdate || null,
        onComplete: o.onComplete || null,

        tick(ms) {
          if (this.delay > 0) {
            this.delay -= ms;
            if (this.delay > 0) return false;
            ms = -this.delay;
            this.delay = 0;
          }
          if (!this.started) {
            this.started = true;
            claim(this);
            this.from = {};
            for (let i = 0; i < keys.length; i++) {
              const k = keys[i];
              const startVal = this.fromOpt && this.fromOpt[k] != null
                ? this.fromOpt[k] : getPath(target, k);
              this.from[k] = Number(startVal) || 0;
              if (this.fromOpt && this.fromOpt[k] != null) setPath(target, k, this.from[k]);
            }
          }
          this.elapsed += ms;
          let t = this.duration <= 0 ? 1 : Math.min(1, this.elapsed / this.duration);
          const e = this.ease(this.reversed ? 1 - t : t);
          for (let i = 0; i < keys.length; i++) {
            const k = keys[i];
            setPath(target, k, this.from[k] + (this.to[k] - this.from[k]) * e);
          }
          if (this.onUpdate) this.onUpdate(t, target);
          if (t < 1) return false;

          if (this.repeatsLeft !== 0) {
            if (this.repeatsLeft > 0) this.repeatsLeft--;
            this.elapsed = 0;
            if (this.yoyo) this.reversed = !this.reversed;
            return false;
          }
          if (this.onComplete) this.onComplete(target);
          return true;
        },

        cancel() { this.dead = true; },
        /** Jump to the end state and fire onComplete. */
        finish() {
          if (this.dead) return;
          for (let i = 0; i < keys.length; i++) setPath(target, keys[i], this.to[keys[i]]);
          if (this.onComplete) this.onComplete(target);
          this.dead = true;
        },
        promise() {
          return new Promise(res => {
            const prev = this.onComplete;
            this.onComplete = tgt => { if (prev) prev(tgt); res(tgt); };
          });
        }
      };
      return push(item);
    },

    /**
     * Physical spring toward end values. Survives interruption with velocity intact.
     * @param {object} target
     * @param {Object<string,number>} props end values by dot path
     * @param {object} [o] { stiffness=180, damping=18, mass=1, velocity=0, restDelta=0.02,
     *                       onComplete, ignoreReducedMotion }
     * @returns {object} handle { cancel(), finish(), promise() }
     */
    spring(target, props, o) {
      o = o || {};
      const keys = Object.keys(props);
      const reduced = isReducedMotion() && !o.ignoreReducedMotion;
      const k = o.stiffness != null ? o.stiffness : 180;
      const d = o.damping != null ? o.damping : 18;
      const m = o.mass != null ? o.mass : 1;
      const rest = o.restDelta != null ? o.restDelta : 0.02;
      const vel = {};
      const item = {
        id: ++_uid,
        target, keys, dead: false, started: false,
        onComplete: o.onComplete || null,

        tick(ms) {
          if (!this.started) {
            this.started = true;
            claim(this);
            for (let i = 0; i < keys.length; i++) vel[keys[i]] = o.velocity || 0;
            if (reduced) {
              for (let i = 0; i < keys.length; i++) setPath(target, keys[i], props[keys[i]]);
              if (this.onComplete) this.onComplete(target);
              return true;
            }
          }
          // Fixed 1/240s substeps: a stiff spring integrated at frame rate explodes on a
          // 30fps Chromebook, and we would rather burn a few extra sub-steps than diverge.
          let remain = Math.min(ms, 100) / 1000;
          const h = 1 / 240;
          let settled = true;
          while (remain > 0) {
            const step = Math.min(h, remain);
            remain -= step;
            settled = true;
            for (let i = 0; i < keys.length; i++) {
              const key = keys[i];
              const x = Number(getPath(target, key)) || 0;
              const dx = x - props[key];
              const a = (-k * dx - d * vel[key]) / m;
              vel[key] += a * step;
              const nx = x + vel[key] * step;
              setPath(target, key, nx);
              if (Math.abs(nx - props[key]) > rest || Math.abs(vel[key]) > rest * 10) settled = false;
            }
          }
          if (!settled) return false;
          for (let i = 0; i < keys.length; i++) setPath(target, keys[i], props[keys[i]]);
          if (this.onComplete) this.onComplete(target);
          return true;
        },
        cancel() { this.dead = true; },
        finish() {
          if (this.dead) return;
          for (let i = 0; i < keys.length; i++) setPath(target, keys[i], props[keys[i]]);
          if (this.onComplete) this.onComplete(target);
          this.dead = true;
        },
        promise() {
          return new Promise(res => {
            const prev = this.onComplete;
            this.onComplete = t => { if (prev) prev(t); res(t); };
          });
        }
      };
      return push(item);
    },

    /**
     * Raw per-frame driver — the escape hatch used by breathe/sway/shake.
     * @param {function} fn (elapsedMs, dtMs) => true to finish
     * @param {object} [o] { target, keys, onKilled, loop }  target+keys join conflict resolution;
     *                     `loop:true` marks a permanent idle animation, which is suspended (not
     *                     killed) while a one-off animation touches the same properties.
     * @returns {object} handle { cancel() }
     */
    driver(fn, o) {
      o = o || {};
      const item = {
        id: ++_uid,
        target: o.target || null,
        keys: o.keys || null,
        isLoop: !!o.loop,
        suspended: false, blockedBy: null,
        dead: false, started: false, elapsed: 0,
        onKilled: o.onKilled || null,
        tick(ms) {
          if (!this.started) { this.started = true; claim(this); }
          this.elapsed += ms;
          return fn(this.elapsed, ms) === true;
        },
        cancel() { if (!this.dead) { this.dead = true; if (this.onKilled) this.onKilled(); } },
        finish() { this.cancel(); }
      };
      return push(item);
    },

    /** Run a callback after `ms`. @returns {object} handle */
    delay(ms, fn) {
      return mgr.driver(elapsed => {
        if (elapsed >= ms) { fn(); return true; }
        return false;
      });
    },

    /** Cancel every animation on a target (or everything if omitted). */
    cancel(target) {
      for (let i = 0; i < items.length; i++) {
        if (!target || items[i].target === target) {
          items[i].dead = true;
          if (items[i].onKilled) items[i].onKilled();
        }
      }
      for (let i = 0; i < adds.length; i++) {
        if (!target || adds[i].target === target) adds[i].dead = true;
      }
    },

    /** Cancel everything. */
    clear() { mgr.cancel(null); },

    /** @returns {Timeline} a new, unstarted timeline */
    timeline(o) { return new Timeline(mgr, o); }
  };

  /* ── game-feel helpers (manager-bound) ────────────────────────────────── */

  /**
   * Scale punch-in. Good for "a thing just appeared".
   * @param {THREE.Object3D} obj
   * @param {object} [o] { from=0.4, ms=420, ease='backOut', overshoot, onComplete }
   */
  mgr.pop = function (obj, o) {
    o = o || {};
    const base = baseScaleOf(obj);
    const from = o.from != null ? o.from : 0.4;
    if (isReducedMotion()) {
      obj.scale.set(base.x, base.y, 1);
      if (o.onComplete) o.onComplete(obj);
      return { cancel() {}, finish() {} };
    }
    obj.scale.set(base.x * from, base.y * from, 1);
    // `from` is re-applied on the tween's first tick, AFTER any idle loop has been suspended —
    // otherwise a running breathe() would overwrite the start pose before we ever read it.
    return mgr.to(obj, { 'scale.x': base.x, 'scale.y': base.y }, {
      from: { 'scale.x': base.x * from, 'scale.y': base.y * from },
      duration: o.ms != null ? o.ms : 420,
      ease: o.ease || 'backOut',
      onComplete: o.onComplete
    });
  };

  /**
   * Squash on one axis, stretch on the other, then spring back. The bread-and-butter
   * "something happened to this object" cue.
   * @param {THREE.Object3D} obj
   * @param {number} [amount=0.22] 0..1
   * @param {number} [ms=520]
   */
  mgr.squashStretch = function (obj, amount, ms) {
    const a = amount != null ? amount : 0.22;
    const base = baseScaleOf(obj);
    if (isReducedMotion()) { obj.scale.set(base.x, base.y, 1); return { cancel() {}, finish() {} }; }
    obj.scale.set(base.x * (1 + a), base.y * (1 - a), 1);
    return mgr.to(obj, { 'scale.x': base.x, 'scale.y': base.y }, {
      from: { 'scale.x': base.x * (1 + a), 'scale.y': base.y * (1 - a) },
      duration: ms != null ? ms : 520,
      ease: 'elasticOut'
    });
  };

  /**
   * Damped rotational wobble.
   * @param {object} [o] { angle=0.22 rad, ms=600, cycles=3, onComplete }
   */
  mgr.wobble = function (obj, o) {
    o = o || {};
    const path = rotationPath(obj);
    if (isReducedMotion()) { if (o.onComplete) o.onComplete(obj); return { cancel() {}, finish() {} }; }
    const angle = o.angle != null ? o.angle : 0.22;
    const ms = o.ms != null ? o.ms : 600;
    const cycles = o.cycles != null ? o.cycles : 3;
    // Base is read on the FIRST TICK, not at call time: by then any idle swayLoop has been
    // suspended and snapped back, so we wobble around the true rest angle.
    let base = null;
    return mgr.driver((elapsed) => {
      if (base === null) base = Number(getPath(obj, path)) || 0;
      const t = Math.min(1, elapsed / ms);
      const decay = 1 - t;
      setPath(obj, path, base + Math.sin(t * Math.PI * 2 * cycles) * angle * decay * decay);
      if (t >= 1) { setPath(obj, path, base); if (o.onComplete) o.onComplete(obj); return true; }
      return false;
    }, { target: obj, keys: [path], onKilled: () => { if (base !== null) setPath(obj, path, base); } });
  };

  /**
   * A single out-and-back rotational tick — the "I noticed you" acknowledgement the house style
   * owes every tap that lands on nothing in particular (§4.9), and what a neighbouring prop does
   * when something happens next door (§4.8).
   *
   * Distinct from wobble(): this is one shaped move on a backOut envelope, not a damped ring-down.
   * @param {object} [o] { angle=0.035 rad (±2°), ms=200, dir=±1, onComplete }
   */
  mgr.nudge = function (obj, o) {
    o = o || {};
    const path = rotationPath(obj);
    if (isReducedMotion()) { if (o.onComplete) o.onComplete(obj); return { cancel() {}, finish() {} }; }
    const angle = o.angle != null ? o.angle : 0.035;
    const ms = o.ms != null ? o.ms : 200;
    const dir = o.dir != null ? o.dir : (Math.random() < 0.5 ? -1 : 1);
    // Base is read on the first tick, once any idle sway has stood down — same reason as wobble().
    let base = null;
    return mgr.driver(elapsed => {
      if (base === null) base = Number(getPath(obj, path)) || 0;
      const t = Math.min(1, elapsed / ms);
      // Out fast on backOut, back to level on backOut: asymmetric, never a symmetric sine.
      const e = t < 0.38 ? Easing.backOut(t / 0.38) : 1 - Easing.backOut((t - 0.38) / 0.62);
      setPath(obj, path, base + e * angle * dir);
      if (t >= 1) { setPath(obj, path, base); if (o.onComplete) o.onComplete(obj); return true; }
      return false;
    }, { target: obj, keys: [path], onKilled: () => { if (base !== null) setPath(obj, path, base); } });
  };

  /**
   * THE PRESS CYCLE (§4.3), start to finish, in one driver.
   *
   *   press-down   0 → 80ms     eased to scale(1+a, 1-a) + a rotation kick + a push INTO the surface
   *   long-press   80ms → …     a slow load-up to (1.02, 1.05) so a held finger has weight (§4.9)
   *   release      → +110ms     backOut overshoot to (1-o, 1+o) plus a 2–5 unit upward pop
   *   settle       → +120ms     quintOut back to rest, the rotation kick unwinding with it
   *
   * Call on pointer-down, call the handle's release() on pointer-up. A flick therefore reads at
   * ~290ms end to end and a held press at up to ~630ms — the two are measurably different curves,
   * which is the whole point of anticipation.
   *
   * ONE driver owns scale.x, scale.y, position.y AND rotation for the entire cycle, so the idle
   * loops are suspended exactly once and there is no frame where breathe() sneaks the base pose
   * back in between phases.
   *
   * @param {THREE.Object3D} obj
   * @param {object} [o] { squash=0.10, stretch=0.045, rotate=0.038 rad, pop=3.5 units,
   *                       holdMs=400, dir=±1, onAcknowledge(down), onComplete }
   * @returns {object} handle { release(), cancel() }
   */
  mgr.press = function (obj, o) {
    o = o || {};
    const base = baseScaleOf(obj);
    const path = rotationPath(obj);
    const baseY = obj.position.y;
    const amt = o.squash != null ? o.squash : 0.10;      // (1.10, 0.90) → sx·sy = 0.99
    const over = o.stretch != null ? o.stretch : 0.045;  // (0.955, 1.045) → sx·sy = 0.998
    const kick = (o.rotate != null ? o.rotate : 0.038) * (o.dir || (Math.random() < 0.5 ? -1 : 1));
    const pop = o.pop != null ? o.pop : 3.5;
    const DOWN = 80, UP = 110, SETTLE = 130;
    const HOLD = o.holdMs != null ? o.holdMs : 400;
    // Even the fastest flick gets a press-down long enough to SEE, which also puts the shortest
    // possible cycle at 72 + 110 + 130 = 312ms — inside the 280–340ms window. Without this floor
    // a 17ms tap released from an almost-unsquashed pose, which is the "1-frame snap" failure.
    const MIN_DOWN = 72;

    // Reduced motion must still CONFIRM the press — it just does it without moving anything.
    // The caller supplies an instant, non-animated acknowledgement (a tint or opacity step).
    if (isReducedMotion()) {
      if (o.onAcknowledge) o.onAcknowledge(true);
      let spent = false;
      return {
        release() {
          if (spent) return; spent = true;
          if (o.onAcknowledge) o.onAcknowledge(false);
          if (o.onComplete) o.onComplete(obj);
        },
        cancel() { this.release(); }
      };
    }

    let baseRot = null;          // read on the first tick, after any sway loop has stood down
    let wantRelease = false, releasedAt = -1, done = false;
    let relSX = 0, relSY = 0, relRot = 0, relY = 0;

    function restore() {
      const b = baseScaleOf(obj);
      obj.scale.set(b.x, b.y, 1);
      if (baseRot !== null) setPath(obj, path, baseRot);
      obj.position.y = baseY;
    }

    const drv = mgr.driver(elapsed => {
      if (baseRot === null) baseRot = Number(getPath(obj, path)) || 0;

      if (releasedAt < 0) {
        if (wantRelease && elapsed >= MIN_DOWN) {
          releasedAt = elapsed;
          relSX = obj.scale.x; relSY = obj.scale.y;
          relRot = Number(getPath(obj, path)) || 0;
          relY = obj.position.y;
        } else if (elapsed <= DOWN) {
          const t = Easing.sineInOut(elapsed / DOWN);
          obj.scale.x = base.x * (1 + amt * t);
          obj.scale.y = base.y * (1 - amt * t);
          setPath(obj, path, baseRot + kick * t);
          obj.position.y = baseY - pop * 0.4 * t;     // pressed INTO the ground, not floating
          return false;
        } else {
          const t = Easing.sineInOut(Math.min(1, (elapsed - DOWN) / HOLD));
          obj.scale.x = base.x * ((1 + amt) + (1.02 - (1 + amt)) * t);
          obj.scale.y = base.y * ((1 - amt) + (1.05 - (1 - amt)) * t);
          setPath(obj, path, baseRot + kick * (1 + 0.6 * t));
          obj.position.y = baseY - pop * 0.4 * (1 - t);
          return false;
        }
      }

      const e = elapsed - releasedAt;
      if (e <= UP) {
        const t = Easing.backOut(e / UP);
        obj.scale.x = relSX + (base.x * (1 - over) - relSX) * t;
        obj.scale.y = relSY + (base.y * (1 + over) - relSY) * t;
        setPath(obj, path, relRot);                    // the kick holds through the release…
        obj.position.y = relY + (baseY + pop - relY) * t;
        return false;
      }
      const t = Easing.quintOut(Math.min(1, (e - UP) / SETTLE));
      obj.scale.x = base.x * ((1 - over) + over * t);
      obj.scale.y = base.y * ((1 + over) - over * t);
      setPath(obj, path, relRot + (baseRot - relRot) * t);   // …and unwinds through the settle
      obj.position.y = (baseY + pop) + (baseY - (baseY + pop)) * t;
      if (e >= UP + SETTLE) {
        restore(); done = true;
        if (o.onComplete) o.onComplete(obj);
        return true;
      }
      return false;
    }, { target: obj, keys: ['scale.x', 'scale.y', 'position.y', path], onKilled: restore });

    return {
      release() {
        if (done || wantRelease) return;
        wantRelease = true;
        // A release that lands before the driver's very first tick still gets its MIN_DOWN.
        if (drv.started && drv.elapsed >= MIN_DOWN) {
          releasedAt = drv.elapsed;
          relSX = obj.scale.x; relSY = obj.scale.y;
          relRot = Number(getPath(obj, path)) || 0;
          relY = obj.position.y;
        }
      },
      cancel() { done = true; drv.cancel(); }
    };
  };

  /**
   * Damped positional shake around the object's current position.
   * @param {object} [o] { amount=14 world units, ms=380, freq=26, axis='both'|'x'|'y', onComplete }
   */
  mgr.shake = function (obj, o) {
    o = o || {};
    if (isReducedMotion()) { if (o.onComplete) o.onComplete(obj); return { cancel() {}, finish() {} }; }
    const amount = o.amount != null ? o.amount : 14;
    const ms = o.ms != null ? o.ms : 380;
    const freq = o.freq != null ? o.freq : 26;
    const axis = o.axis || 'both';
    const phase = Math.random() * 6.28;
    let bx = null, by = 0;
    return mgr.driver((elapsed) => {
      if (bx === null) { bx = obj.position.x; by = obj.position.y; }
      const t = Math.min(1, elapsed / ms);
      const decay = (1 - t) * (1 - t);
      const s = elapsed / 1000 * freq;
      if (axis !== 'y') obj.position.x = bx + Math.sin(s * 6.28 + phase) * amount * decay;
      if (axis !== 'x') obj.position.y = by + Math.cos(s * 5.13 + phase) * amount * 0.7 * decay;
      if (t >= 1) {
        obj.position.x = bx; obj.position.y = by;
        if (o.onComplete) o.onComplete(obj);
        return true;
      }
      return false;
    }, {
      target: obj, keys: ['position.x', 'position.y'],
      onKilled: () => { if (bx !== null) { obj.position.x = bx; obj.position.y = by; } }
    });
  };

  /**
   * LOOPING idle: breathing, exactly as the house style specs it —
   * `scaleY 1.00 → 1.018 → 1.00` paired with `scaleX 1.00 → 0.994`, sine in-out.
   *
   * The pairing is the point: equal deltas on both axes is a ZOOM, and a zoom is an instant tell.
   * `amount` is the Y amplitude; X gets a third of it in the opposite direction, which is what
   * conserves volume (1.018 × 0.994 ≈ 1.012).
   *
   * The base pose is re-read every tick from `userData.baseScale`, so a resize (which rewrites
   * every sprite's base) is picked up without having to tear the loop down and restart it.
   *
   * @param {object} [o] { amount=0.018, ms=2200, phase=random 0..1 }
   * @returns {object} handle { cancel() } — keep it, cancel it when the object dies
   */
  mgr.breathe = function (obj, o) {
    o = o || {};
    if (isReducedMotion()) {
      const b = baseScaleOf(obj);
      obj.scale.set(b.x, b.y, 1);
      return { cancel() {} };
    }
    const amount = o.amount != null ? o.amount : 0.018;
    const ms = o.ms != null ? o.ms : 2200;
    const phase = (o.phase != null ? o.phase : Math.random()) * ms;
    return mgr.driver((elapsed) => {
      const b = baseScaleOf(obj);
      // Unipolar 0..1, so the loop runs 1.00 ↔ 1+amount rather than straddling the base pose.
      const u = 0.5 + 0.5 * Math.sin(((elapsed + phase) / ms) * Math.PI * 2);
      obj.scale.y = b.y * (1 + amount * u);
      obj.scale.x = b.x * (1 - amount * u / 3);
      return false;
    }, {
      loop: true,
      target: obj, keys: ['scale.x', 'scale.y'],
      onKilled: () => { const b = baseScaleOf(obj); obj.scale.set(b.x, b.y, 1); }
    });
  };

  /**
   * LOOPING idle: a lazy rotational sway, like a plant in a breeze.
   * House spec is ±0.8–1.5° (0.014–0.026 rad) over 2.4–3.6s — small enough to read as air moving,
   * not as a toy wobbling.
   * @param {object} [o] { angle=0.021 rad ≈ 1.2°, ms=3000, phase=random 0..1 }
   * @returns {object} handle { cancel() }
   */
  mgr.swayLoop = function (obj, o) {
    o = o || {};
    const path = rotationPath(obj);
    const base = Number(getPath(obj, path)) || 0;
    if (isReducedMotion()) { setPath(obj, path, base); return { cancel() {} }; }
    const angle = o.angle != null ? o.angle : 0.021;
    const ms = o.ms != null ? o.ms : 3000;
    const phase = (o.phase != null ? o.phase : Math.random()) * ms;
    return mgr.driver((elapsed) => {
      setPath(obj, path, base + Math.sin(((elapsed + phase) / ms) * Math.PI * 2) * angle);
      return false;
    }, { loop: true, target: obj, keys: [path], onKilled: () => setPath(obj, path, base) });
  };

  return mgr;
}

/* ═══════════════════════════ timeline ═══════════════════════════ */

/**
 * A sequence of steps. Nothing runs until `.start()`.
 * Chainable: .to() .from() .wait() .call() .parallel() .add() .start()
 */
class Timeline {
  constructor(mgr, o) {
    this._mgr = mgr;
    this._steps = [];
    this._i = -1;
    this._driver = null;
    this._done = (o && o.onComplete) || null;
    this._repeat = (o && o.repeat) || 0;
    this._cancelled = false;
  }

  /** @see tweens.to — queued sequentially. */
  to(target, props, opts) {
    this._steps.push({ kind: 'tween', target, props, opts: opts || {} });
    return this;
  }

  /** Tween FROM the given values to wherever the target currently sits. */
  from(target, props, opts) {
    const o = Object.assign({}, opts || {});
    const end = {};
    this._steps.push({
      kind: 'fn',
      run: next => {
        Object.keys(props).forEach(k => { end[k] = Number(getPath(target, k)) || 0; });
        this._driver = this._mgr.to(target, end, Object.assign({}, o, { from: props, onComplete: next }));
      }
    });
    return this;
  }

  /** Pause for `ms`. */
  wait(ms) { this._steps.push({ kind: 'wait', ms }); return this; }

  /** Run a synchronous callback, then continue immediately. */
  call(fn) { this._steps.push({ kind: 'call', fn }); return this; }

  /**
   * Run several branches at once and continue when the slowest finishes.
   * @param {Array<function>} builders each receives a fresh Timeline to fill in
   */
  parallel(builders) {
    this._steps.push({ kind: 'parallel', builders });
    return this;
  }

  /** Append another timeline's steps. */
  add(tl) { this._steps.push({ kind: 'timeline', tl }); return this; }

  /** Begin. @returns {Timeline} this */
  start() {
    if (this._i >= 0) return this;
    this._advance();
    return this;
  }

  /** @returns {Promise} resolves when the whole timeline finishes (or is cancelled). */
  promise() {
    return new Promise(res => {
      const prev = this._done;
      this._done = () => { if (prev) prev(); res(); };
    });
  }

  cancel() {
    this._cancelled = true;
    if (this._driver && this._driver.cancel) this._driver.cancel();
    this._driver = null;
  }

  _advance() {
    if (this._cancelled) return;
    this._i++;
    if (this._i >= this._steps.length) {
      if (this._repeat !== 0) {
        if (this._repeat > 0) this._repeat--;
        this._i = -1;
        this._advance();
        return;
      }
      if (this._done) this._done();
      return;
    }
    const step = this._steps[this._i];
    const next = () => this._advance();

    switch (step.kind) {
      case 'tween': {
        const opts = Object.assign({}, step.opts);
        const userDone = opts.onComplete;
        opts.onComplete = t => { if (userDone) userDone(t); next(); };
        this._driver = this._mgr.to(step.target, step.props, opts);
        break;
      }
      case 'wait':
        // Reduced motion should not make the child sit through dead air either.
        this._driver = isReducedMotion() ? this._mgr.delay(0, next) : this._mgr.delay(step.ms, next);
        break;
      case 'call':
        step.fn();
        next();
        break;
      case 'fn':
        step.run(next);
        break;
      case 'timeline': {
        this._driver = step.tl;
        step.tl.promise().then(next);
        step.tl.start();
        break;
      }
      case 'parallel': {
        let left = step.builders.length;
        if (!left) { next(); break; }
        step.builders.forEach(b => {
          const sub = new Timeline(this._mgr);
          b(sub);
          sub.promise().then(() => { if (--left === 0) next(); });
          sub.start();
        });
        break;
      }
      default:
        next();
    }
  }
}

/* ═══════════════════════════ singleton + wiring ═══════════════════════════ */

/** The shared manager. Drive it with attachTweensTo(stage). */
export const tweens = createTweenManager();

/**
 * Wire the shared manager into a stage's fixed-timestep loop. Call once at boot.
 * @returns {function} unsubscribe
 */
export function attachTweensTo(stage, manager) {
  const m = manager || tweens;
  return stage.onUpdate(dt => m.update(dt));
}

/* Convenience re-exports bound to the singleton, so game code can just import the verb. */
export const pop = (obj, o) => tweens.pop(obj, o);
export const squashStretch = (obj, amount, ms) => tweens.squashStretch(obj, amount, ms);
export const wobble = (obj, o) => tweens.wobble(obj, o);
export const nudge = (obj, o) => tweens.nudge(obj, o);
export const press = (obj, o) => tweens.press(obj, o);
export const shake = (obj, o) => tweens.shake(obj, o);
export const breathe = (obj, o) => tweens.breathe(obj, o);
export const swayLoop = (obj, o) => tweens.swayLoop(obj, o);
