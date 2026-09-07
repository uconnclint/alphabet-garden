# Flat-Vector Art — Alphabet Garden

**Batch 2 — 2026-09-07. Rebuild of all six assets after batch 1 failed review.**

Source of truth is `_build_flat.py`; it writes both the `.svg` masters and the `.png`
rasters into this directory. Edit the script, re-run it:

```
python3 "/Users/clintonmcleod/AI/letter garden/art/flat/_build_flat.py"
```

Medium is hand-authored SVG (image generation is still `403 insufficient_permissions`
for `image_video_generation`). Rasterised at 2x via headless Chrome, then LANCZOS
downsampled to 1x for clean outline anti-aliasing.

---

## Why batch 1 failed, and what changed

| Batch 1 failure | Batch 2 fix |
|---|---|
| **No outlines at all** (C3 = automatic 3) | Every asset now carries pure `#000000` outlines at **1.4–1.7% of object height**, `stroke-linejoin="round"` + `stroke-linecap="round"` on everything. |
| **No two-tone form blocking** (C4) | Every asset has a base fill plus **one hard-edged shadow tone clipped inside the parent shape**, ΔV 0.09–0.15. Zero gradients, zero filters. |
| **Mathematically perfect symmetry** (12 rays at exactly 30°) | The sun now has **11 rays at irregular angles** (30–36° apart), lengths varied ±9%, widths varied, and one deliberately stubby. Nothing in the batch is on a grid. |
| **No charm** | Every asset has at least one authored oddity, listed below. The sun has a real face: eyes at different heights and sizes, mismatched brows, a lopsided grin. |

### Outline depth-step (C8 / §3.3)

- **Foreground props** — sun, cloud, grass, dirt, bush: pure `#000000`, full weight.
- **Far background** — `hill_layer`: **zero pure black** (verified: 0 px). It carries only a
  6px hue-matched `#6ab543` line at **7.4% contrast** against its own fill, which is the
  §3.3 background-architecture treatment. This is what makes the hill sit back.

### Per-asset fixes called out in the previous review

- **`dirt_plot`** (was the weakest — read as a cookie / pie tin / pit). Rebuilt as a wide
  **2.3:1 tilled patch**, not a dome: crumbly lumpy back edge against a settled front edge,
  three **tilled rows** (a `soil-deep` groove with a `soil-lite` lit crest riding above it),
  chunky **clods seated on the rim so the silhouette is broken open**, and **loose crumbs
  spilled fully outside the outline**. The gotcha was respected — no offset-union on the
  ellipse; the shading is a clipped hard-edged wavy band.
- **`cloud_puffy`** (slab-like straight bottom, ~3 lobes). Now **5 genuinely unequal lobes**
  plus a small dangling sixth puff, and the whole bottom edge is an **undulating hand-authored
  curve** (y 620–668), never a rect.
- **`bush_shrub`** (shared the cloud's silhouette language). Now built from **15 small unequal
  leaf scallops** wrapped all the way round *including the base*, versus the cloud's 5 big
  smooth lobes. Verified side-by-side as black silhouettes — they no longer read as siblings.
- **`grass_tuft`** (pointed tips). Blade tips are now explicit **arc caps at ~50% of the base
  half-width** (22–29px radius), so every tip is a rounded strap end.
- **`hill_layer`** (crest rim almost invisible). Crest contrast raised from ΔV 0.047 to
  **ΔV 0.149**, band deepened from 34px to 66px, and offset sideways by 16px so the lit band
  varies in thickness along the ridge instead of being a uniform rim.

### The deliberate oddity in each asset

| asset | oddity |
|---|---|
| `sun_character` | one ray is stubby (322px vs ~400px); eyes are different sizes and not level; the brows disagree with each other |
| `cloud_puffy` | a small sixth puff dangles below the bottom-left edge |
| `hill_layer` | a small extra knoll interrupts the right-hand descent |
| `grass_tuft` | one blade has flopped over completely; another has an insect-nibbled hole |
| `dirt_plot` | one clod is rotated 34° off-axis; a cream stone has been turned up near the left edge |
| `bush_shrub` | scallop #11 is an inward notch (a bitten leaf) instead of a bump; the three berries are all different sizes |

---

## Palette

Tokens from `FLAT_ART_BRIEF` §3, unchanged: `grass` `#7ec850`, `grass-deep` `#5da23c`,
`soil` `#a9713f`, `soil-deep` `#8a5a33`, `cream` `#fff7e6`, `sun` `#ffd23f`,
`sun-deep` `#f0b429`, `accent` `#ff9d52`, `berry` `#c65fd1`, `ink` `#000000`,
`ink-soft` `#3f3026`.

**Four shadow tones had to be derived**, because two token pairs do not reach the C4 range
of ΔV 0.08–0.18 on their own. `grass`→`grass-deep` is ΔV 0.149 and `soil`→`soil-deep` is
ΔV 0.122 (both in spec, used as-is), but `sun`→`sun-deep` is only **ΔV 0.059** and `cream`
has no shadow token at all. Derived by the §3.4 rule — surface hue, slightly more
saturated, value dropped into the band:

| derived | hex | from | ΔV | note |
|---|---|---|---|---|
| `sun-shade` | `#e8a52a` | `sun` | 0.090 | body shadow face |
| `ray-shade` | `#d69526` | `sun-deep` | 0.102 | ray shadow face |
| `cloud-shade` | `#c6d8e6` | `cream` | 0.098 | hue-rotated to 206° — a cloud's shadow must go cool |
| `soil-lite` | `#c2884e` | `soil` | 0.098 | lit crest of a tilled row; raised clods |

No pure `#FFFFFF` anywhere. No neutral grey anywhere. Every shadow is derived from its own
surface hue.

---

## Verification (measured, not assumed)

Every PNG below was opened and looked at. Numbers are from decoded pixels.

| asset | canvas | longest constant RGB run | corner alpha | pure `#000000` |
|---|---|---|---|---|
| `sun_character` | 1024×1024 | **439 px** `#ffd23f` | all 4 = 0 | 17.1% of opaque |
| `cloud_puffy` | 1024×1024 | **635 px** `#fff7e6` | all 4 = 0 | 5.9% |
| `hill_layer` | 2048×700 | **2048 px** `#6ab543` | top 2 = 0 (bottom is ground) | **0%** — correct, it is layer 1 |
| `grass_tuft` | 1024×1024 | **526 px** `#5da23c` | all 4 = 0 | 18.9% |
| `dirt_plot` | 1024×1024 | **695 px** `#a9713f` | all 4 = 0 | 6.6% |
| `bush_shrub` | 1024×1024 | **568 px** `#7ec850` | all 4 = 0 | 8.9% |

Explicit 100px horizontal probes placed inside a fill returned **`unique_rgb = 1`, `alpha = {255}`
on all six**. There is literally no gradient, noise, or filter anywhere in the batch.

Transparency was confirmed by **decoding actual corner pixel values**, not by file size — the
Chrome `<use>`-inside-`<clipPath>` bug renders a valid-looking empty file, so `clipPath`
children here are always literal shapes.

**Black-silhouette-at-25% test** run on sun, bush, dirt and grass, and rendered to disk:
all four are identifiable from silhouette alone, and the irregularities survive (the sun's
stubby ray, the grass's flopped blade and nibble hole are all visible at 256px).
`cloud_puffy` and `bush_shrub` were silhouetted side by side on a neutral ground to confirm
they no longer share a shape language.

---

## Self-scores (1–10; anything ≤6 is a fail)

| asset | C1 palette | C2 shape | C3 line | C4 shading |
|---|---|---|---|---|
| `sun_character` | 9 | 9 | 9 | 8 |
| `cloud_puffy` | 9 | 9 | 9 | 9 |
| `hill_layer` | 8 | 8 | 9 | 9 |
| `grass_tuft` | 8 | 8 | 9 | 9 |
| `dirt_plot` | 8 | 8 | 8 | 9 |
| `bush_shrub` | 9 | 9 | 9 | 9 |

Where the points were withheld, honestly:

- **`sun_character` C4 = 8** — the body's shadow tone goes *warmer*, not cooler, as it darkens.
  §3.4 asks for a cool hue-shift; on a sun a cool shadow reads wrong, so this is a deliberate
  deviation rather than an oversight, and it costs a point.
- **`grass_tuft` C2 = 8** — the blades are chunky and correctly round-tipped, but at
  ~50% tip-to-base taper they read slightly more succulent than soft grass.
- **`dirt_plot` C2 = 8, C3 = 8** — the crumbly ridge, tilled rows, rim clods and spilled
  crumbs have decisively killed the cookie read, but the core mass is still a lozenge, and
  its 7px outline is thin next to the sun's 13px when the two sit at the same on-screen size.
- **`hill_layer` C1/C2 = 8** — deliberately the simplest thing in the batch. It is a
  background plate; a higher score would mean it was competing for attention.

---

## Technique notes for later batches

- **Union silhouettes without internal seams** (cloud): draw the whole shape group once as a
  black underlay with `fill="#000" stroke="#000" stroke-width="2 × outline"`, then draw the
  colour fills on top. Only the outer rim of black survives. Add internal contour lines as
  short open arcs clipped to the union.
- **Overlapping separate objects** (grass blades, sun rays): use painter's algorithm instead
  — back to front, each object filled *and* stroked. Every overlap then reads as a real
  drawn edge at consistent weight. Do not mix the two techniques in one asset.
- **Three-pass order is mandatory** when a shape has a clipped shadow: fill → clipped shadow →
  stroke. Stroking before the shadow lets the clipped shadow eat the inner half of the outline.
- **Nibbled holes**: append a second closed subpath and set `fill-rule="evenodd"` on the fill
  and `clip-rule="evenodd"` on its `clipPath`. Keep the hole entirely *inside* the shape — a
  subpath straddling the edge leaves the stroke tracing a full circle floating in empty space.
- **Scalloped organic edges**: walk a list of perimeter points, and between each pair emit a
  `Q` with the control point pushed along the outward normal `(dy, -dx)` by roughly
  2 × the bump height. Jitter the bulge per segment; a negative bulge gives an inward notch.
- **Hand-drawn wobble**: `smooth_closed()` converts a jittered point list into Catmull-Rom
  cubics. Perturbing radii ±6% around a circle gives a blob that reads as drawn rather than
  constructed. Note that dense point lists get smoothed *flatter* — for a crumbly edge, use
  fewer points with larger alternating amplitude.
- **Chrome bug (still live):** `<use href="#g"/>` inside a `<clipPath>` where `#g` is a `<g>`
  silently renders **nothing**. `clipPath` children must be literal shapes. Always verify by
  decoding pixels.
- **Transparent PNG from headless Chrome:**
  `--headless --default-background-color=00000000 --force-device-scale-factor=2
  --window-size=W,H --screenshot=out.png`, then downsample to W×H.
