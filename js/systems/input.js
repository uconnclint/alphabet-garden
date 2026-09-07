// input.js — Pointer Events → world-space hit testing for 2D sprites, with a guaranteed 44px minimum target.
//
// Touch-first by construction: Pointer Events only (no mouse/touch pairs, no HTML5 drag API,
// no hover-only behaviour). Five-year-olds on an iPad are the design target.
//
// ── WHY AABB AND NOT A RAYCASTER ────────────────────────────────────────────────
// Everything here is an axis-aligned sprite in an orthographic camera, so a raycast would do
// strictly more work for strictly less control — we could not grow the hit rect past the art.
// A world-space rectangle test lets us guarantee the house-style ≥44 CSS px minimum target even
// when the art is a 30px seed, and it stays correct while a squash/stretch tween is running
// (we measure `userData.baseScale`, not the animated scale, so targets never wobble away).
//
// ── USE ─────────────────────────────────────────────────────────────────────────
//   import { createInput } from './systems/input.js';
//   const input = createInput(stage);
//
//   const off = input.register(seedSprite, {
//     onTap:        (info) => plant(info),      // finger lifted on the target
//     onPressStart: (info) => squash(seed),     // finger went down on it
//     onPressEnd:   (info) => release(seed),    // lifted or cancelled — ALWAYS pairs with start
//     hitPadding:   12                          // extra world units around the art
//   });
//   off();                                      // unregister
//
// Handlers receive: { object, x, y, clientX, clientY, event, cancelled }
// (x/y are world units.)
//
// ── API ─────────────────────────────────────────────────────────────────────────
//   createInput(stage, opts) -> input
//   input.register(obj3d, handlers) -> unregister()
//   input.unregister(obj3d)
//   input.setEnabled(obj3d, bool) / input.enabled = bool   (whole-system gate)
//   input.onTapAnywhere(cb) -> unsubscribe                  (background taps, ambient fx)
//   input.hitTest(clientX, clientY) -> obj3d|null
//   input.toWorld(clientX, clientY) -> {x,y}
//   input.dispose()

import * as THREE from '../../vendor/three.module.js';

const _v = new THREE.Vector3();
const _s = new THREE.Vector3();
const _box = new THREE.Box3();

/** House-style minimum effective target, in CSS pixels. */
const MIN_HIT_PX = 44;

/** How far a finger may slide and still count as a tap (CSS px). Kids are not precise. */
const TAP_SLOP_PX = 20;

/**
 * @param {object} stage from stage.js
 * @param {object} [opts]
 * @param {number} [opts.minHitPx=44]
 * @param {number} [opts.tapSlopPx=20]
 * @param {Element} [opts.element=stage.canvas]
 * @returns {object} input
 */
export function createInput(stage, opts = {}) {
  const el = opts.element || stage.canvas;
  const minHitPx = opts.minHitPx != null ? opts.minHitPx : MIN_HIT_PX;
  const tapSlopPx = opts.tapSlopPx != null ? opts.tapSlopPx : TAP_SLOP_PX;

  /** @type {Map<THREE.Object3D, object>} */
  const entries = new Map();
  const anywhereCbs = [];

  const api = {
    enabled: true,
    /** Last known pointer position in world units. */
    world: { x: 0, y: 0 }
  };

  /* ── hit rectangles ───────────────────────────────────────────────────── */

  const rect = { cx: 0, cy: 0, hw: 0, hh: 0, z: 0 };

  function rectOf(obj, cfg, out) {
    obj.updateWorldMatrix(true, false);
    _v.setFromMatrixPosition(obj.matrixWorld);
    out.z = _v.z;

    let w, h, cx = _v.x, cy = _v.y;

    if (cfg.hitSize) {
      w = cfg.hitSize.w; h = cfg.hitSize.h;
    } else if (obj.isSprite) {
      // Measure the *base* scale so a running squash/stretch does not move the target.
      const base = obj.userData && obj.userData.baseScale;
      if (base) { w = Math.abs(base.x); h = Math.abs(base.y); }
      else { _s.setFromMatrixScale(obj.matrixWorld); w = Math.abs(_s.x); h = Math.abs(_s.y); }
      // Sprite.center moves the quad relative to its position.
      cx += (0.5 - obj.center.x) * w;
      cy += (0.5 - obj.center.y) * h;
    } else {
      _box.setFromObject(obj);
      if (_box.isEmpty()) { w = 0; h = 0; }
      else {
        w = _box.max.x - _box.min.x;
        h = _box.max.y - _box.min.y;
        cx = (_box.min.x + _box.max.x) / 2;
        cy = (_box.min.y + _box.max.y) / 2;
      }
    }

    const pad = cfg.hitPadding || 0;
    let hw = w / 2 + pad;
    let hh = h / 2 + pad;

    // Enforce the minimum effective target in *screen* terms, whatever the world scale is.
    const minHalf = (minHitPx * stage.unitsPerPx) / 2;
    if (hw < minHalf) hw = minHalf;
    if (hh < minHalf) hh = minHalf;

    out.cx = cx; out.cy = cy; out.hw = hw; out.hh = hh;
    return out;
  }

  /**
   * Topmost registered object under a client point, or null.
   * "Topmost" = greatest world z, i.e. the frontmost layer wins.
   */
  function hitTest(clientX, clientY) {
    const p = stage.toWorld(clientX, clientY);
    let best = null, bestZ = -Infinity;
    entries.forEach((cfg, obj) => {
      if (!cfg.enabled) return;
      if (!obj.visible || !isChainVisible(obj)) return;
      rectOf(obj, cfg, rect);
      if (Math.abs(p.x - rect.cx) <= rect.hw && Math.abs(p.y - rect.cy) <= rect.hh) {
        if (rect.z >= bestZ) { bestZ = rect.z; best = obj; }
      }
    });
    return best;
  }

  function isChainVisible(obj) {
    let o = obj.parent;
    while (o) { if (!o.visible) return false; o = o.parent; }
    return true;
  }

  /* ── pointer state ────────────────────────────────────────────────────── */

  // Only one pointer at a time. Extra fingers during a drag are ignored outright, which is what
  // a kid resting a palm on the screen produces.
  let activeId = null;
  let downTarget = null;
  let downX = 0, downY = 0;
  let moved = false;

  function info(obj, e, cancelled) {
    const p = stage.toWorld(e.clientX, e.clientY);
    api.world.x = p.x; api.world.y = p.y;
    return {
      object: obj, x: p.x, y: p.y,
      clientX: e.clientX, clientY: e.clientY,
      event: e, cancelled: !!cancelled
    };
  }

  function onPointerDown(e) {
    if (!api.enabled) return;
    if (activeId !== null) return; // ignore extra fingers
    activeId = e.pointerId;
    downX = e.clientX; downY = e.clientY;
    moved = false;

    downTarget = hitTest(e.clientX, e.clientY);
    if (downTarget) {
      const cfg = entries.get(downTarget);
      // Capture so a finger sliding off the canvas still delivers pointerup to us.
      try { el.setPointerCapture(e.pointerId); } catch (err) { /* not fatal */ }
      if (cfg && cfg.onPressStart) cfg.onPressStart(info(downTarget, e));
    }
  }

  function onPointerMove(e) {
    if (e.pointerId !== activeId) return;
    if (!moved) {
      const dx = e.clientX - downX, dy = e.clientY - downY;
      if (dx * dx + dy * dy > tapSlopPx * tapSlopPx) moved = true;
    }
    if (downTarget) {
      const cfg = entries.get(downTarget);
      if (cfg && cfg.onPressMove) cfg.onPressMove(info(downTarget, e));
    }
  }

  function finish(e, cancelled) {
    if (e.pointerId !== activeId) return;
    try { el.releasePointerCapture(e.pointerId); } catch (err) { /* already gone */ }

    const target = downTarget;
    activeId = null;
    downTarget = null;

    if (target) {
      const cfg = entries.get(target);
      // onPressEnd always pairs with onPressStart, cancelled or not — visual state must recover.
      if (cfg && cfg.onPressEnd) cfg.onPressEnd(info(target, e, cancelled));
      if (!cancelled && !moved && cfg && cfg.onTap && cfg.enabled) {
        // Still over the target? Kids drift; slop already allowed for that, but a finger that
        // ended somewhere else entirely should not fire the tap.
        if (hitTest(e.clientX, e.clientY) === target) cfg.onTap(info(target, e));
      }
    }

    if (!cancelled && !moved) {
      const p = stage.toWorld(e.clientX, e.clientY);
      for (let i = 0; i < anywhereCbs.length; i++) {
        anywhereCbs[i]({ x: p.x, y: p.y, clientX: e.clientX, clientY: e.clientY, hit: target, event: e });
      }
    }
  }

  const onPointerUp = e => finish(e, false);
  // pointercancel fires on iOS when the system takes over (notification, gesture, call).
  const onPointerCancel = e => finish(e, true);

  el.addEventListener('pointerdown', onPointerDown);
  el.addEventListener('pointermove', onPointerMove);
  el.addEventListener('pointerup', onPointerUp);
  el.addEventListener('pointercancel', onPointerCancel);
  // A pointer whose capture is stolen never sends pointerup; treat it as a cancel.
  el.addEventListener('lostpointercapture', e => { if (e.pointerId === activeId) finish(e, true); });

  /* ── registration ─────────────────────────────────────────────────────── */

  /**
   * Make an object tappable.
   * @param {THREE.Object3D} obj
   * @param {object} handlers
   * @param {function} [handlers.onTap]
   * @param {function} [handlers.onPressStart]
   * @param {function} [handlers.onPressEnd]
   * @param {function} [handlers.onPressMove]
   * @param {number} [handlers.hitPadding=0] extra world units on every side
   * @param {{w:number,h:number}} [handlers.hitSize] explicit world-unit hit box (overrides art size)
   * @param {boolean} [handlers.enabled=true]
   * @returns {function} unregister
   */
  function register(obj, handlers) {
    const cfg = Object.assign({ enabled: true, hitPadding: 0 }, handlers || {});
    entries.set(obj, cfg);
    return () => unregister(obj);
  }

  function unregister(obj) {
    if (downTarget === obj) downTarget = null;
    entries.delete(obj);
  }

  function setEnabled(obj, on) {
    const cfg = entries.get(obj);
    if (cfg) cfg.enabled = !!on;
  }

  /** Fires on every tap on the canvas (hit or not). @returns {function} unsubscribe */
  function onTapAnywhere(cb) {
    anywhereCbs.push(cb);
    return () => { const i = anywhereCbs.indexOf(cb); if (i >= 0) anywhereCbs.splice(i, 1); };
  }

  function dispose() {
    el.removeEventListener('pointerdown', onPointerDown);
    el.removeEventListener('pointermove', onPointerMove);
    el.removeEventListener('pointerup', onPointerUp);
    el.removeEventListener('pointercancel', onPointerCancel);
    entries.clear();
    anywhereCbs.length = 0;
    activeId = null;
    downTarget = null;
  }

  return Object.assign(api, {
    register, unregister, setEnabled, onTapAnywhere, hitTest, dispose,
    toWorld: (x, y) => stage.toWorld(x, y),
    get registeredCount() { return entries.size; }
  });
}
