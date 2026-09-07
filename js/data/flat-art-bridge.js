// flat-art-bridge.js — hands the flat-vector override map to the classic-script side of the game.
//
// ── WHY THIS FILE EXISTS ────────────────────────────────────────────────────────
// The world layer (GardenScene) reaches the flat art through `systems/textures.js`, which
// consults `data/flat-assets.js` inside `resolve()`. The DOM half of the UI — the bloom-choice
// cards, the sticker book thumbnails, the celebration card — never goes near the texture loader:
// `game.js` writes a raw `<img src>`. So until this bridge existed the alias layer could not
// reach it, and half the game's surface was still showing claymation portraits in front of a
// flat-vector garden.
//
// `game.js` is a CLASSIC script (deliberately: it must keep running even if the module graph
// fails to load — see the note above `window.GardenGame`), and `flat-assets.js` is an ES module.
// A classic script cannot `import`. So one tiny module publishes the lookup on a namespace and
// `game.js` reads it lazily, at call time.
//
// ── LOAD ORDER ──────────────────────────────────────────────────────────────────
// index.html loads this BEFORE js/main3d.js and AFTER game.js. Module scripts are deferred, so
// this runs after game.js's classic body but before DOMContentLoaded — and every `plantArt()`
// call site in game.js fires on a tap (open the picker, open the book, bloom), all of which are
// gated behind the title screen's Play button. The namespace is therefore always present by the
// time a preview is built.
//
// It is a separate file from main3d.js on purpose. main3d.js `await`s the core texture set and
// bails entirely when WebGL or Three is unavailable; the DOM previews must not inherit either
// risk, because on a locked-down Chromebook with no WebGL the modals are the whole game.
// And it is not a side effect inside flat-assets.js, which stays a pure data module.

import { FLAT_OVERRIDES } from './flat-assets.js';

/** Where the original claymation portraits live — the fallback for an unmapped plant. */
const LEGACY_PLANTS = 'art/assets/plants/';

/**
 * Flat replacement for a logical asset name, or null when that asset is still claymation.
 * Same contract as `flatSrc()` in flat-assets.js, minus the module boundary.
 * @param {string} logicalName e.g. 'plants/s-sunflower.png'
 * @returns {?string}
 */
function flatUrlFor(logicalName) {
  if (!logicalName) return null;
  return FLAT_OVERRIDES[logicalName] || null;
}

/**
 * The `<img src>` for one plant id, flat art where it exists and the original PNG where it does
 * not. All 78 are mapped today; the fallback is what keeps a typo'd or newly added id showing a
 * plant instead of a broken-image icon.
 * @param {string} id e.g. 's-sunflower'
 * @returns {string}
 */
function plantSrc(id) {
  return flatUrlFor('plants/' + id + '.png') || (LEGACY_PLANTS + id + '.png');
}

window.GardenFlatArt = {
  overrides: FLAT_OVERRIDES,
  flatUrlFor: flatUrlFor,
  plantSrc: plantSrc
};
