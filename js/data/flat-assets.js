// flat-assets.js — the flat-vector art OVERRIDE LAYER.
//
// The game asks the texture loader for logical names ('garden/dirt_plot_empty.png',
// 'plants/s-sunflower.png'). Those names are stable and every call site in GardenScene.js
// still uses them. This file is the single place that says "…but draw the flat-vector one
// instead", and `systems/textures.js` consults it inside `resolve()` — so a mapping added
// here lights up everywhere at once, with no scene edits.
//
// ── HOW TO ADD A NEWLY AUTHORED PLANT ───────────────────────────────────────────
// One line in FLAT_OVERRIDES:
//     'plants/t-taco-tree.png': 'art/flat/plants/t-taco-tree.png',
// plus one line in FLAT_METRICS with its measured content box (see below). Nothing else.
// The other 69 plants keep resolving to art/assets/plants/<id>.png until their line exists.
//
// ── VARIANTS ────────────────────────────────────────────────────────────────────
// Set dressing must not be sixteen identical stamps. `variantUrl(url, seed)` turns a logical
// name into a VIRTUAL logical name carrying a variant suffix:
//     variantUrl('garden/dirt_plot_empty.png', 5)  ->  'garden/dirt_plot_empty@c.png'
// If that key has an override it loads the `_c` flat art; if it does not, textures.js strips
// the suffix and falls back to the original claymation file. So a half-authored variant set
// degrades to "all the same" rather than to a 404.
//
// The seed is the PLOT INDEX, never a random number: a plot must look identical on every
// re-render and every reload.
//
// ── METRICS: why a path is not enough ───────────────────────────────────────────
// The flat art has different proportions and different anchors from the claymation it
// replaces. The flat dirt plot, for instance, is a wide shallow bed drawn in the LOWER HALF
// of a square canvas, with loose clods shed outside the main mass and a baked contact shadow.
// Sizing it by canvas height (what `sizeTo` used to do) makes it a third of its intended size
// and floats it half a bed above the soil line.
//
// So every flat asset carries a measured content box, in 0..1 of its own canvas:
//   u  [left, right]   horizontal span used for WIDTH fitting. For the dirt this is the main
//                      BED only — fitting to the full alpha box would shrink the bed by
//                      however far that variant's loose clods happen to fly.
//   v  [top, bottom]   vertical span of the alpha box, used for HEIGHT fitting.
//   ax, ay             the sprite's pivot, in canvas coords. For anything standing on the
//                      ground this is its CONTACT POINT, so `position` means "where it
//                      touches", and squash/sway pivot there instead of swinging the object
//                      about the middle of a mostly-empty quad.
//   plant              (dirt only) the v of the planting hollow — where a plant's base goes.
//
// Numbers are measured off the shipped PNGs (alpha bounding boxes and per-row runs), not
// eyeballed. Re-measure if the art is rebuilt.

/* ═══════════════════════ overrides ═══════════════════════ */

/**
 * Logical asset name → flat replacement, as a path relative to index.html.
 * A name that is absent here silently keeps its original `art/assets/` file.
 * @type {Object<string,string>}
 */
export const FLAT_OVERRIDES = {
  /* ── sky ─────────────────────────────────────────────── */
  'sky/sun.png':                  'art/flat/sun_character.png',
  'sky/cloud_puffy.png':          'art/flat/cloud_puffy.png',
  'sky/cloud_puffy@b.png':        'art/flat/cloud_puffy_b.png',
  'sky/cloud_puffy@c.png':        'art/flat/cloud_puffy_c.png',
  'sky/cloud_wisp.png':           'art/flat/cloud_puffy_c.png',

  /* ── garden furniture ────────────────────────────────── */
  // Empty and seeded share a variant on purpose: planting a seed must not restyle the bed.
  'garden/dirt_plot_empty.png':   'art/flat/dirt_plot.png',
  'garden/dirt_plot_empty@b.png': 'art/flat/dirt_plot_b.png',
  'garden/dirt_plot_empty@c.png': 'art/flat/dirt_plot_c.png',
  'garden/dirt_plot_seeded.png':  'art/flat/dirt_plot.png',
  'garden/dirt_plot_seeded@b.png':'art/flat/dirt_plot_b.png',
  'garden/dirt_plot_seeded@c.png':'art/flat/dirt_plot_c.png',

  'garden/hills_backdrop.png':    'art/flat/hill_layer.png',
  'garden/hills_backdrop@b.png':  'art/flat/hill_layer_b.png',
  'garden/hills_backdrop@c.png':  'art/flat/hill_layer_c.png',

  'garden/grass_foreground.png':  'art/flat/grass_tuft.png',
  'garden/grass_foreground@b.png':'art/flat/grass_tuft_b.png',
  'garden/grass_foreground@c.png':'art/flat/grass_tuft_c.png',

  // Set dressing with no claymation ancestor — a purely flat logical name.
  'garden/bush.png':              'art/flat/bush_shrub.png',
  'garden/bush@b.png':            'art/flat/bush_shrub_b.png',
  'garden/bush@c.png':            'art/flat/bush_shrub_c.png',

  'garden/seed.png':              'art/flat/prop_seed.png',

  /* ── plants: the 9 authored so far ───────────────────── */
  'plants/s-sunflower.png':       'art/flat/plants/s-sunflower.png',
  'plants/a-apple-tree.png':      'art/flat/plants/a-apple-tree.png',
  'plants/m-maple-tree.png':      'art/flat/plants/m-maple-tree.png',
  'plants/b-butterfly-bush.png':  'art/flat/plants/b-butterfly-bush.png',
  'plants/p-pizza-palm.png':      'art/flat/plants/p-pizza-palm.png',
  'plants/u-ufo-tree.png':        'art/flat/plants/u-ufo-tree.png',
  'plants/r-robot-rosebush.png':  'art/flat/plants/r-robot-rosebush.png',
  'plants/x-xylophone-tree.png':  'art/flat/plants/x-xylophone-tree.png',
  'plants/b-banana-tree.png':     'art/flat/plants/b-banana-tree.png'
};

/* ═══════════════════════ metrics ═══════════════════════ */

/**
 * Measured geometry for each flat file. Keyed by the flat path so there is exactly one
 * entry per PNG, however many logical names point at it.
 * @type {Object<string,{u:number[],v:number[],ax:number,ay:number,plant?:number}>}
 */
export const FLAT_METRICS = {
  // Sun: a near-square disc-plus-rays, pivoting at its own centre.
  'art/flat/sun_character.png':   { u: [0.116, 0.891], v: [0.094, 0.892], ax: 0.504, ay: 0.493 },

  // Clouds: lobes sitting high in the canvas, so the pivot is well above canvas centre.
  'art/flat/cloud_puffy.png':     { u: [0.130, 0.933], v: [0.196, 0.696], ax: 0.531, ay: 0.446 },
  'art/flat/cloud_puffy_b.png':   { u: [0.157, 0.923], v: [0.235, 0.676], ax: 0.540, ay: 0.455 },
  'art/flat/cloud_puffy_c.png':   { u: [0.149, 0.862], v: [0.237, 0.677], ax: 0.506, ay: 0.457 },

  // Hills: full-bleed tileable bands, no outline, ridge in the lower half. Bottom-anchored so
  // the band's base can be pinned to the horizon whatever height it is stretched to.
  'art/flat/hill_layer.png':      { u: [0, 1], v: [0.430, 1], ax: 0.5, ay: 1 },
  'art/flat/hill_layer_b.png':    { u: [0, 1], v: [0.486, 1], ax: 0.5, ay: 1 },
  'art/flat/hill_layer_c.png':    { u: [0, 1], v: [0.444, 1], ax: 0.5, ay: 1 },

  // Grass: a TUFT, not a strip. Anchored on its own contact shadow.
  'art/flat/grass_tuft.png':      { u: [0.178, 0.835], v: [0.229, 0.927], ax: 0.507, ay: 0.921 },
  'art/flat/grass_tuft_b.png':    { u: [0.172, 0.835], v: [0.260, 0.927], ax: 0.503, ay: 0.921 },
  'art/flat/grass_tuft_c.png':    { u: [0.199, 0.835], v: [0.290, 0.927], ax: 0.517, ay: 0.921 },

  'art/flat/bush_shrub.png':      { u: [0.146, 0.851], v: [0.255, 0.827], ax: 0.498, ay: 0.821 },
  'art/flat/bush_shrub_b.png':    { u: [0.178, 0.820], v: [0.230, 0.827], ax: 0.499, ay: 0.821 },
  'art/flat/bush_shrub_c.png':    { u: [0.223, 0.773], v: [0.205, 0.827], ax: 0.498, ay: 0.821 },

  'art/flat/prop_seed.png':       { u: [0.139, 0.846], v: [0.318, 0.822], ax: 0.492, ay: 0.811 },

  // Dirt: `u` is the BED's widest contiguous run — the detached clods are deliberately
  // outside it, so all three variants fit to the same bed width. `ay` is the front rim's
  // contact line; `plant` is the middle of the dug hollow.
  'art/flat/dirt_plot.png':       { u: [0.088, 0.922], v: [0.496, 0.893], ax: 0.505, ay: 0.855, plant: 0.700 },
  'art/flat/dirt_plot_b.png':     { u: [0.098, 0.910], v: [0.529, 0.896], ax: 0.504, ay: 0.858, plant: 0.690 },
  'art/flat/dirt_plot_c.png':     { u: [0.054, 0.954], v: [0.522, 0.900], ax: 0.504, ay: 0.862, plant: 0.705 },

  // Plants: each stands on its own baked contact shadow at the bottom of the canvas.
  'art/flat/plants/a-apple-tree.png':     { u: [0.037, 0.988], v: [0.049, 0.980], ax: 0.513, ay: 0.980 },
  'art/flat/plants/b-banana-tree.png':    { u: [0.037, 0.927], v: [0.106, 0.984], ax: 0.482, ay: 0.984 },
  'art/flat/plants/b-butterfly-bush.png': { u: [0.038, 0.969], v: [0.062, 0.981], ax: 0.503, ay: 0.981 },
  'art/flat/plants/m-maple-tree.png':     { u: [0.052, 0.979], v: [0.086, 0.994], ax: 0.516, ay: 0.994 },
  'art/flat/plants/p-pizza-palm.png':     { u: [0.124, 0.868], v: [0.040, 0.989], ax: 0.496, ay: 0.989 },
  'art/flat/plants/r-robot-rosebush.png': { u: [0.031, 0.967], v: [0.040, 0.985], ax: 0.499, ay: 0.985 },
  'art/flat/plants/s-sunflower.png':      { u: [0.183, 0.789], v: [0.110, 0.981], ax: 0.486, ay: 0.981 },
  'art/flat/plants/u-ufo-tree.png':       { u: [0.011, 0.993], v: [0.044, 0.981], ax: 0.502, ay: 0.981 },
  'art/flat/plants/x-xylophone-tree.png': { u: [0.041, 0.961], v: [0.051, 0.979], ax: 0.501, ay: 0.979 }
};

/* ═══════════════════════ api ═══════════════════════ */

const VARIANTS = ['', 'b', 'c'];

// Period 7 against a 3- or 4-wide grid, so variants never line up into columns or stripes.
const VARIANT_ORDER = [0, 2, 1, 1, 0, 2, 2];

/** Which of the three variants plot/tuft/cloud `seed` gets. Deterministic — never random. */
export function variantIndex(seed) {
  const i = Math.abs(seed | 0);
  return VARIANT_ORDER[i % VARIANT_ORDER.length];
}

/**
 * Virtual logical name for one variant of an asset.
 * `variantUrl('garden/bush.png', 4)` -> 'garden/bush.png' (variant 0 has no suffix).
 * A suffix with no override is stripped again by textures.js, so this always resolves.
 */
export function variantUrl(url, seed) {
  const v = VARIANTS[variantIndex(seed)];
  if (!v) return url;
  const dot = url.lastIndexOf('.');
  return dot < 0 ? url + '@' + v : url.slice(0, dot) + '@' + v + url.slice(dot);
}

/** Remove any '@x' variant suffix: 'a/b@c.png' -> 'a/b.png'. */
export function stripVariant(url) {
  return typeof url === 'string' ? url.replace(/@[a-z0-9]+(\.[a-z0-9]+)$/i, '$1') : url;
}

/** The flat file for a logical name, or null if this asset has not been re-authored yet. */
export function flatSrc(url) {
  if (!url) return null;
  return FLAT_OVERRIDES[url] || null;
}

/** True if `url` currently resolves to flat art. */
export function isFlat(url) { return !!flatSrc(url); }

/**
 * Measured geometry for a logical name, or `def` when the asset is still claymation.
 * Callers pass the default whose pivot matches how they used to place the sprite, so an
 * un-authored asset lands exactly where it always did.
 */
export function metricsFor(url, def) {
  const src = flatSrc(url);
  return (src && FLAT_METRICS[src]) || def || null;
}
