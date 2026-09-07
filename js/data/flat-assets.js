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
  'plants/a-airplane-tree.png':             'art/flat/plants/a-airplane-tree.png',
  'plants/a-ant-arch.png':                  'art/flat/plants/a-ant-arch.png',
  'plants/a-apple-tree.png':                'art/flat/plants/a-apple-tree.png',
  'plants/b-banana-tree.png':               'art/flat/plants/b-banana-tree.png',
  'plants/b-burger-bush.png':               'art/flat/plants/b-burger-bush.png',
  'plants/b-butterfly-bush.png':            'art/flat/plants/b-butterfly-bush.png',
  'plants/c-carrot-plant.png':              'art/flat/plants/c-carrot-plant.png',
  'plants/c-caterpillar-vine.png':          'art/flat/plants/c-caterpillar-vine.png',
  'plants/c-cupcake-tree.png':              'art/flat/plants/c-cupcake-tree.png',
  'plants/d-daffodil.png':                  'art/flat/plants/d-daffodil.png',
  'plants/d-donut-tree.png':                'art/flat/plants/d-donut-tree.png',
  'plants/d-duck-bloom.png':                'art/flat/plants/d-duck-bloom.png',
  'plants/e-eggplant.png':                  'art/flat/plants/e-eggplant.png',
  'plants/e-elephant-ear.png':              'art/flat/plants/e-elephant-ear.png',
  'plants/e-escalator-plant.png':           'art/flat/plants/e-escalator-plant.png',
  'plants/f-fern.png':                      'art/flat/plants/f-fern.png',
  'plants/f-firefly-flower.png':            'art/flat/plants/f-firefly-flower.png',
  'plants/f-firetruck-flower.png':          'art/flat/plants/f-firetruck-flower.png',
  'plants/g-giraffe-grass.png':             'art/flat/plants/g-giraffe-grass.png',
  'plants/g-grape-vine.png':                'art/flat/plants/g-grape-vine.png',
  'plants/g-gumball-tree.png':              'art/flat/plants/g-gumball-tree.png',
  'plants/h-hedgehog-herb.png':             'art/flat/plants/h-hedgehog-herb.png',
  'plants/h-hibiscus.png':                  'art/flat/plants/h-hibiscus.png',
  'plants/h-hotdog-hedge.png':              'art/flat/plants/h-hotdog-hedge.png',
  'plants/i-icecream-iris.png':             'art/flat/plants/i-icecream-iris.png',
  'plants/i-inchworm-ivy.png':              'art/flat/plants/i-inchworm-ivy.png',
  'plants/i-iris.png':                      'art/flat/plants/i-iris.png',
  'plants/j-jaguar-jade.png':               'art/flat/plants/j-jaguar-jade.png',
  'plants/j-jasmine.png':                   'art/flat/plants/j-jasmine.png',
  'plants/j-jellybean-jungle.png':          'art/flat/plants/j-jellybean-jungle.png',
  'plants/k-kale.png':                      'art/flat/plants/k-kale.png',
  'plants/k-kangaroo-kelp.png':             'art/flat/plants/k-kangaroo-kelp.png',
  'plants/k-ketchup-cactus.png':            'art/flat/plants/k-ketchup-cactus.png',
  'plants/l-ladybug-lettuce.png':           'art/flat/plants/l-ladybug-lettuce.png',
  'plants/l-lavender.png':                  'art/flat/plants/l-lavender.png',
  'plants/l-lollipop-lily.png':             'art/flat/plants/l-lollipop-lily.png',
  'plants/m-maple-tree.png':                'art/flat/plants/m-maple-tree.png',
  'plants/m-marshmallow-tree.png':          'art/flat/plants/m-marshmallow-tree.png',
  'plants/m-monkey-marigold.png':           'art/flat/plants/m-monkey-marigold.png',
  'plants/n-narwhal-nettle.png':            'art/flat/plants/n-narwhal-nettle.png',
  'plants/n-noodle-nutbush.png':            'art/flat/plants/n-noodle-nutbush.png',
  'plants/n-norway-spruce.png':             'art/flat/plants/n-norway-spruce.png',
  'plants/o-octopus-oakleaf.png':           'art/flat/plants/o-octopus-oakleaf.png',
  'plants/o-orange-tree.png':               'art/flat/plants/o-orange-tree.png',
  'plants/o-owl-orchid.png':                'art/flat/plants/o-owl-orchid.png',
  'plants/p-palm-tree.png':                 'art/flat/plants/p-palm-tree.png',
  'plants/p-panda-pansy.png':               'art/flat/plants/p-panda-pansy.png',
  'plants/p-pizza-palm.png':                'art/flat/plants/p-pizza-palm.png',
  'plants/q-quackers-duckbloom.png':        'art/flat/plants/q-quackers-duckbloom.png',
  'plants/q-quail-quillplant.png':          'art/flat/plants/q-quail-quillplant.png',
  'plants/q-quaking-aspen.png':             'art/flat/plants/q-quaking-aspen.png',
  'plants/r-rabbit-radish.png':             'art/flat/plants/r-rabbit-radish.png',
  'plants/r-red-rose.png':                  'art/flat/plants/r-red-rose.png',
  'plants/r-robot-rosebush.png':            'art/flat/plants/r-robot-rosebush.png',
  'plants/s-snail-snapdragon.png':          'art/flat/plants/s-snail-snapdragon.png',
  'plants/s-sock-sprout.png':               'art/flat/plants/s-sock-sprout.png',
  'plants/s-sunflower.png':                 'art/flat/plants/s-sunflower.png',
  'plants/t-taco-tree.png':                 'art/flat/plants/t-taco-tree.png',
  'plants/t-tomato.png':                    'art/flat/plants/t-tomato.png',
  'plants/t-turtle-tulip.png':              'art/flat/plants/t-turtle-tulip.png',
  'plants/u-ufo-tree.png':                  'art/flat/plants/u-ufo-tree.png',
  'plants/u-umbrella-plant.png':            'art/flat/plants/u-umbrella-plant.png',
  'plants/u-unicorn-flower.png':            'art/flat/plants/u-unicorn-flower.png',
  'plants/v-violet.png':                    'art/flat/plants/v-violet.png',
  'plants/v-volcano-tree.png':              'art/flat/plants/v-volcano-tree.png',
  'plants/v-vole-vine.png':                 'art/flat/plants/v-vole-vine.png',
  'plants/w-waffle-willow.png':             'art/flat/plants/w-waffle-willow.png',
  'plants/w-watermelon.png':                'art/flat/plants/w-watermelon.png',
  'plants/w-whale-wisteria.png':            'art/flat/plants/w-whale-wisteria.png',
  'plants/x-fox-xerophyte.png':             'art/flat/plants/x-fox-xerophyte.png',
  'plants/x-xanthosoma.png':                'art/flat/plants/x-xanthosoma.png',
  'plants/x-xylophone-tree.png':            'art/flat/plants/x-xylophone-tree.png',
  'plants/y-yak-yarrow.png':                'art/flat/plants/y-yak-yarrow.png',
  'plants/y-yoyo-tree.png':                 'art/flat/plants/y-yoyo-tree.png',
  'plants/y-yucca.png':                     'art/flat/plants/y-yucca.png',
  'plants/z-zebra-zinnia.png':              'art/flat/plants/z-zebra-zinnia.png',
  'plants/z-zinnia.png':                    'art/flat/plants/z-zinnia.png',
  'plants/z-zombie-tree.png':               'art/flat/plants/z-zombie-tree.png'
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
  'art/flat/plants/a-airplane-tree.png':               { u: [0.082, 0.947], v: [0.084, 0.98], ax: 0.5, ay: 0.98 },
  'art/flat/plants/a-ant-arch.png':                    { u: [0.229, 0.723], v: [0.062, 0.981], ax: 0.488, ay: 0.981 },
  'art/flat/plants/a-apple-tree.png':                  { u: [0.037, 0.988], v: [0.049, 0.98], ax: 0.475, ay: 0.98 },
  'art/flat/plants/b-banana-tree.png':                 { u: [0.037, 0.927], v: [0.106, 0.984], ax: 0.477, ay: 0.984 },
  'art/flat/plants/b-burger-bush.png':                 { u: [0.082, 0.907], v: [0.147, 0.981], ax: 0.473, ay: 0.981 },
  'art/flat/plants/b-butterfly-bush.png':              { u: [0.038, 0.969], v: [0.062, 0.981], ax: 0.474, ay: 0.981 },
  'art/flat/plants/c-carrot-plant.png':                { u: [0.111, 0.928], v: [0.071, 0.985], ax: 0.486, ay: 0.985 },
  'art/flat/plants/c-caterpillar-vine.png':            { u: [0.139, 0.818], v: [0.14, 0.981], ax: 0.477, ay: 0.981 },
  'art/flat/plants/c-cupcake-tree.png':                { u: [0.226, 0.741], v: [0.1, 0.98], ax: 0.494, ay: 0.98 },
  'art/flat/plants/d-daffodil.png':                    { u: [0.274, 0.755], v: [0.063, 0.983], ax: 0.49, ay: 0.983 },
  'art/flat/plants/d-donut-tree.png':                  { u: [0.045, 0.929], v: [0.125, 0.98], ax: 0.467, ay: 0.98 },
  'art/flat/plants/d-duck-bloom.png':                  { u: [0.268, 0.801], v: [0.125, 0.978], ax: 0.569, ay: 0.978 },
  'art/flat/plants/e-eggplant.png':                    { u: [0.041, 0.93], v: [0.12, 0.981], ax: 0.558, ay: 0.981 },
  'art/flat/plants/e-elephant-ear.png':                { u: [0.029, 0.945], v: [0.056, 0.981], ax: 0.485, ay: 0.981 },
  'art/flat/plants/e-escalator-plant.png':             { u: [0.0, 0.943], v: [0.104, 0.981], ax: 0.475, ay: 0.981 },
  'art/flat/plants/f-fern.png':                        { u: [0.041, 0.95], v: [0.077, 0.981], ax: 0.498, ay: 0.981 },
  'art/flat/plants/f-firefly-flower.png':              { u: [0.021, 0.935], v: [0.123, 0.981], ax: 0.474, ay: 0.981 },
  'art/flat/plants/f-firetruck-flower.png':            { u: [0.182, 0.924], v: [0.053, 0.981], ax: 0.496, ay: 0.981 },
  'art/flat/plants/g-giraffe-grass.png':               { u: [0.147, 0.853], v: [0.063, 0.985], ax: 0.498, ay: 0.985 },
  'art/flat/plants/g-grape-vine.png':                  { u: [0.066, 0.947], v: [0.065, 0.981], ax: 0.551, ay: 0.981 },
  'art/flat/plants/g-gumball-tree.png':                { u: [0.143, 0.97], v: [0.095, 0.981], ax: 0.472, ay: 0.981 },
  'art/flat/plants/h-hedgehog-herb.png':               { u: [0.071, 0.966], v: [0.044, 0.985], ax: 0.518, ay: 0.985 },
  'art/flat/plants/h-hibiscus.png':                    { u: [0.142, 0.852], v: [0.06, 0.981], ax: 0.579, ay: 0.981 },
  'art/flat/plants/h-hotdog-hedge.png':                { u: [0.036, 0.954], v: [0.088, 0.984], ax: 0.447, ay: 0.984 },
  'art/flat/plants/i-icecream-iris.png':               { u: [0.196, 0.764], v: [0.071, 0.981], ax: 0.488, ay: 0.981 },
  'art/flat/plants/i-inchworm-ivy.png':                { u: [0.195, 0.811], v: [0.07, 0.981], ax: 0.484, ay: 0.981 },
  'art/flat/plants/i-iris.png':                        { u: [0.137, 0.859], v: [0.093, 0.985], ax: 0.503, ay: 0.985 },
  'art/flat/plants/j-jaguar-jade.png':                 { u: [0.043, 0.917], v: [0.096, 0.981], ax: 0.488, ay: 0.981 },
  'art/flat/plants/j-jasmine.png':                     { u: [0.049, 0.866], v: [0.055, 0.981], ax: 0.51, ay: 0.981 },
  'art/flat/plants/j-jellybean-jungle.png':            { u: [0.236, 0.854], v: [0.054, 0.988], ax: 0.661, ay: 0.988 },
  'art/flat/plants/k-kale.png':                        { u: [0.014, 0.985], v: [0.033, 0.998], ax: 0.675, ay: 0.998 },
  'art/flat/plants/k-kangaroo-kelp.png':               { u: [0.163, 0.862], v: [0.126, 0.981], ax: 0.361, ay: 0.981 },
  'art/flat/plants/k-ketchup-cactus.png':              { u: [0.128, 0.913], v: [0.055, 0.985], ax: 0.477, ay: 0.985 },
  'art/flat/plants/l-ladybug-lettuce.png':             { u: [0.067, 0.932], v: [0.038, 0.978], ax: 0.481, ay: 0.978 },
  'art/flat/plants/l-lavender.png':                    { u: [0.18, 0.861], v: [0.075, 0.986], ax: 0.447, ay: 0.986 },
  'art/flat/plants/l-lollipop-lily.png':               { u: [0.195, 0.728], v: [0.049, 0.981], ax: 0.484, ay: 0.981 },
  'art/flat/plants/m-maple-tree.png':                  { u: [0.052, 0.979], v: [0.086, 0.994], ax: 0.312, ay: 0.994 },
  'art/flat/plants/m-marshmallow-tree.png':            { u: [0.169, 0.887], v: [0.061, 0.99], ax: 0.66, ay: 0.99 },
  'art/flat/plants/m-monkey-marigold.png':             { u: [0.075, 0.877], v: [0.054, 0.981], ax: 0.515, ay: 0.981 },
  'art/flat/plants/n-narwhal-nettle.png':              { u: [0.083, 0.897], v: [0.047, 0.981], ax: 0.514, ay: 0.981 },
  'art/flat/plants/n-noodle-nutbush.png':              { u: [0.074, 0.922], v: [0.034, 0.981], ax: 0.5, ay: 0.981 },
  'art/flat/plants/n-norway-spruce.png':               { u: [0.052, 0.956], v: [0.045, 0.981], ax: 0.499, ay: 0.981 },
  'art/flat/plants/o-octopus-oakleaf.png':             { u: [0.01, 0.96], v: [0.086, 0.981], ax: 0.501, ay: 0.981 },
  'art/flat/plants/o-orange-tree.png':                 { u: [0.085, 0.909], v: [0.11, 0.981], ax: 0.557, ay: 0.981 },
  'art/flat/plants/o-owl-orchid.png':                  { u: [0.109, 0.868], v: [0.094, 0.981], ax: 0.497, ay: 0.981 },
  'art/flat/plants/p-palm-tree.png':                   { u: [0.055, 0.73], v: [0.088, 0.981], ax: 0.591, ay: 0.981 },
  'art/flat/plants/p-panda-pansy.png':                 { u: [0.118, 0.936], v: [0.068, 0.99], ax: 0.731, ay: 0.99 },
  'art/flat/plants/p-pizza-palm.png':                  { u: [0.124, 0.868], v: [0.04, 0.989], ax: 0.506, ay: 0.989 },
  'art/flat/plants/q-quackers-duckbloom.png':          { u: [0.117, 0.869], v: [0.062, 0.985], ax: 0.529, ay: 0.985 },
  'art/flat/plants/q-quail-quillplant.png':            { u: [0.102, 0.979], v: [0.077, 0.98], ax: 0.49, ay: 0.98 },
  'art/flat/plants/q-quaking-aspen.png':               { u: [0.169, 0.828], v: [0.076, 0.981], ax: 0.497, ay: 0.981 },
  'art/flat/plants/r-rabbit-radish.png':               { u: [0.193, 0.743], v: [0.062, 0.985], ax: 0.545, ay: 0.985 },
  'art/flat/plants/r-red-rose.png':                    { u: [0.135, 0.972], v: [0.086, 0.981], ax: 0.471, ay: 0.981 },
  'art/flat/plants/r-robot-rosebush.png':              { u: [0.031, 0.967], v: [0.04, 0.985], ax: 0.502, ay: 0.985 },
  'art/flat/plants/s-snail-snapdragon.png':            { u: [0.264, 0.902], v: [0.056, 0.981], ax: 0.493, ay: 0.981 },
  'art/flat/plants/s-sock-sprout.png':                 { u: [0.037, 0.978], v: [0.107, 0.975], ax: 0.501, ay: 0.975 },
  'art/flat/plants/s-sunflower.png':                   { u: [0.183, 0.789], v: [0.11, 0.981], ax: 0.491, ay: 0.981 },
  'art/flat/plants/t-taco-tree.png':                   { u: [0.075, 0.953], v: [0.153, 1.0], ax: 0.197, ay: 1.0 },
  'art/flat/plants/t-tomato.png':                      { u: [0.0, 0.97], v: [0.104, 0.981], ax: 0.621, ay: 0.981 },
  'art/flat/plants/t-turtle-tulip.png':                { u: [0.106, 0.835], v: [0.137, 0.995], ax: 0.523, ay: 0.995 },
  'art/flat/plants/u-ufo-tree.png':                    { u: [0.011, 0.993], v: [0.044, 0.981], ax: 0.496, ay: 0.981 },
  'art/flat/plants/u-umbrella-plant.png':              { u: [0.188, 0.971], v: [0.071, 0.985], ax: 0.497, ay: 0.985 },
  'art/flat/plants/u-unicorn-flower.png':              { u: [0.087, 0.89], v: [0.073, 0.981], ax: 0.483, ay: 0.981 },
  'art/flat/plants/v-violet.png':                      { u: [0.002, 0.975], v: [0.061, 0.966], ax: 0.578, ay: 0.966 },
  'art/flat/plants/v-volcano-tree.png':                { u: [0.103, 0.908], v: [0.069, 0.997], ax: 0.497, ay: 0.997 },
  'art/flat/plants/v-vole-vine.png':                   { u: [0.147, 0.858], v: [0.074, 0.991], ax: 0.51, ay: 0.991 },
  'art/flat/plants/w-waffle-willow.png':               { u: [0.08, 0.925], v: [0.129, 0.978], ax: 0.572, ay: 0.978 },
  'art/flat/plants/w-watermelon.png':                  { u: [0.08, 0.959], v: [0.088, 0.989], ax: 0.68, ay: 0.989 },
  'art/flat/plants/w-whale-wisteria.png':              { u: [0.016, 0.999], v: [0.133, 0.982], ax: 0.557, ay: 0.982 },
  'art/flat/plants/x-fox-xerophyte.png':               { u: [0.186, 0.959], v: [0.096, 0.961], ax: 0.504, ay: 0.961 },
  'art/flat/plants/x-xanthosoma.png':                  { u: [0.052, 0.953], v: [0.085, 0.989], ax: 0.495, ay: 0.989 },
  'art/flat/plants/x-xylophone-tree.png':              { u: [0.041, 0.961], v: [0.051, 0.979], ax: 0.484, ay: 0.979 },
  'art/flat/plants/y-yak-yarrow.png':                  { u: [0.022, 0.968], v: [0.089, 0.981], ax: 0.483, ay: 0.981 },
  'art/flat/plants/y-yoyo-tree.png':                   { u: [0.093, 0.914], v: [0.116, 0.98], ax: 0.595, ay: 0.98 },
  'art/flat/plants/y-yucca.png':                       { u: [0.009, 0.942], v: [0.14, 0.981], ax: 0.481, ay: 0.981 },
  'art/flat/plants/z-zebra-zinnia.png':                { u: [0.202, 0.862], v: [0.058, 0.998], ax: 0.609, ay: 0.998 },
  'art/flat/plants/z-zinnia.png':                      { u: [0.113, 0.992], v: [0.057, 0.981], ax: 0.48, ay: 0.981 },
  'art/flat/plants/z-zombie-tree.png':                 { u: [0.121, 0.928], v: [0.074, 0.975], ax: 0.478, ay: 0.975 }
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
