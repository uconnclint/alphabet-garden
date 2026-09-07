# Flat-Vector Art — Alphabet Garden

**Batch 3 — 2026-09-07. Rebuild after batch 2 failed review (C1 5, C2 6, C4 6, C5 5, C7 4, C8 4).**

Source of truth is `_build_flat.py`; it writes both the `.svg` masters and the `.png`
rasters into this directory. Edit the script, re-run it:

```
python3 "/Users/clintonmcleod/AI/letter garden/art/flat/_build_flat.py"
```

Medium is hand-authored SVG (image generation is still `403 insufficient_permissions`
for `image_video_generation`). Rasterised at 2× via headless Chrome, then LANCZOS
downsampled to 1× for clean outline anti-aliasing.

---

## What the batch-2 review found GOOD — carried forward untouched

Flat fills, zero gradients/filters/blur, no bevel/glow/gloss, no black or grey drop
shadows, round joins and caps on everything, internal contours at 82–100% of silhouette
weight, tinted whites, clean alpha, disciplined hue count. **C3 (line quality) scored 7,
the highest in the batch** — the outline system is unchanged in kind, only re-weighted so
every asset lands inside the measured 1.29–1.76% band.

## What failed, and what changed

| Batch 2 failure | Batch 3 fix |
|---|---|
| **Every object a full saturation step hotter than the reference.** Median fill S 0.63 vs 0.27, 86.4% above the S 0.55 ceiling — "loud vector clip-art". | Whole batch repainted on the **revised** `FLAT_ART_BRIEF` §3 tokens. Core six now median **S 0.420**, 6.4% above 0.55, **1.5% above 0.60**. |
| **`hill_layer` shared its two exact hexes with the foreground bush and grass**, so the layers vanished into each other. | Hill moved to the layer-2 band (`#d0edbe` / `#badea9`). Bushes moved to a new layer-4 band (`#8ac96e` / `#6ba851`) so they read against a `grass` field. Hill now shares **zero** hexes with bush or grass. |
| **HARD BUG — 744px enclosed transparent hole** in the tall grass blade (the `bite()` evenodd oddity). Sky showed through the grass. | `bite()` deleted. Blades are now built as an explicit outline (left edge, round cap, right edge) that is **simply connected by construction**. Scan across all 24 PNGs: 0 enclosed transparent regions. |
| **HARD BUG — 18,862px off-palette `#6AB543` hairline** on the hill's left, right and bottom edges (a `stroke-width="6"` whose outer half the viewBox clipped). Would have tiled as a seam. | Stroke removed entirely — a layer-1/2 background carries no outline. Ridges also re-cut so `y(0) == y(2048)` with **horizontal tangents at both ends**, so the band now tiles without a step. Verified 0px of `#6ab543`. |
| **One wavy horizontal band reused as the shadow on sun, cloud, bush AND dirt** — a decorative gesture describing no form. Sun terminator read as a waterline; rays implied a different light direction than the disc. | Single honest construction, `twotone()`: fill the shape with its shadow tone, then lay **the same path** back down shifted toward the light and clipped to itself. The lit/shade boundary is therefore always concentric with the form that owns it — a crescent on the sun disc, per-lobe crescents on the cloud, a scalloped rim on the bush, a ring on the dirt lip, a flank on each blade, a crest band on the hill. Rays use the same offset as the body, so they agree. |
| **`dirt_plot` read as a rock or a loaf sitting on the grass**, not a hole to plant into. | Redrawn as an excavated hole: dug rim whose back bank **dips into a saddle** (so the 25% silhouette carries a visible depression), slightly elliptical opening, interior a full step darker than the lip, lit far wall concentric with the opening, flat ground line, **round-capped** scrape marks (the tapered furrow strokes are gone). Cream pebble removed. |
| **Grass read as a sea anemone / cactus** at 25% black. | Rebuilt: 6 blades, full widths 60–124px (no two within 12px), heights 118–626, fanned apart, bends capped so nothing curls into a shepherd's crook. Left pair separated by ≥19px of sky (≥2× the 10px outline) everywhere they are visible. Painter's order corrected to tall-behind / short-in-front. |
| **Nothing sat in the world** — everything floated. | Contact shadow on plot, bush, grass and all three props: `ground-contact` `#93d56c`, hue-matched to `grass`, **ΔV 0.024**, hard edge, no blur. |
| **C7 = 4, instanced props.** Same shape every time; the cream pebble was an every-plot constant that read as a hole or an eye at game size. | **Three variants of every prop** (grass, dirt, bush, cloud, hill) — recoloured within band *and* reshaped. Pebble deleted. Three narrative props added: `prop_seed` (half-buried), `prop_trowel`, `prop_worm`. |
| **C5 = 5, one face.** Eyes w/h 0.77 (taller than wide), sitting ~35px above the disc midline; brows shared the eye hex. | Eyes now **w/h 1.153** (rx 34 / ry 29.5), sitting at y 528/534 — **below** the midline (516) and not level with each other. Brows on the `brow` token `#6b5342`. **Six** expressions shipped as swappable `<g id="face-*">` groups plus one PNG each. |

---

## Files

| file | canvas | notes |
|---|---|---|
| `sun_character.png` + `_happy`, `_laughing`, `_surprised`, `_sad`, `_mischievous` | 1024² | one SVG holds all six `face-*` groups; the PNGs are pre-rendered frames |
| `cloud_puffy{,_b,_c}` | 1024² | 6 lobes / 6 / 6 in different arrangements |
| `hill_layer{,_b,_c}` | 2048×700 | horizontally tileable, no outline |
| `grass_tuft{,_b,_c}` | 1024² | |
| `dirt_plot{,_b,_c}` | 1024² | |
| `bush_shrub{,_b,_c}` | 1024² | A berries, B orange blossom, C one berry |
| `prop_seed`, `prop_trowel`, `prop_worm` | 512² | scatter dressing |

## Verification (measured, not assumed)

**Saturation, non-outline opaque pixels (V > 0.25, alpha > 0.9):**

| set | median S | mean S | > 0.55 | > 0.60 |
|---|---|---|---|---|
| batch 2 (core six) | 0.630 | 0.574 | 86.4% | 63.7% |
| **batch 3 (core six)** | **0.420** | **0.348** | **6.4%** | **1.5%** |
| batch 3 (+ variants + props) | 0.240 | 0.320 | 2.5% | 0.6% |

Per asset (batch 3): sun 0.522, cloud 0.098, hill 0.239, grass 0.461, dirt 0.448,
bush 0.453. The sun is the only asset with pixels above S 0.60 (10.8% of its own area,
1.5% of the batch) — that is `sun-deep` 0.579 / `ray-shade` 0.598 / `sun-shade` 0.613,
all three fixed by the brief's revised table.

**Other checks, all re-run after the final build:**

- Enclosed transparent regions across every PNG: **0**.
- `#6ab543` pixels in the three hill layers: **0**.
- `hill ∩ (bush ∪ grass)` hex sets: **empty**.
- Longest constant-RGB run: 1024px (2048 on the hill) — fills are perfectly flat.
- `linearGradient` / `radialGradient` / `filter` / `feGaussianBlur` in any SVG: **0**.
- Pure `#FFFFFF` anywhere: **0** (the laughing mouth's teeth are `cream` `#fff7e6`).
- Alpha at all four corners of every PNG: **0**.
- Outline weight as % of object height: sun 1.60, cloud 1.58, grass 1.41, dirt 1.47,
  bush 1.55, seed 1.59, trowel 1.45, worm 1.60. Hill: none, by design.
- Internal contours at 83–100% of their silhouette weight.
- Hue families over the core six: green 57.5%, amber 31.6%, warm-red 9.1%, cool 1.6%
  — three families doing 98% of the work.
- Two-tone ΔV: grass 0.137, soil 0.122, soil lip 0.098, hole floor 0.098, cloud 0.098,
  sun rays 0.082. Two sit under the C4 0.08 floor and are **deliberate**: `sun` →
  `sun-shade` at 0.067 (both hexes fixed by the brief, documented there as a known
  exception) and `hill` → `hill-deep` at 0.059 (a layer-2 background *should* be
  low-contrast — TOCA §3.8 gives layer 2 a 4–8% contrast line).

## The deliberate oddity in each asset

- **sun** — ray index 6 is stubby (322 vs ~400); the eyes are different sizes and not level.
- **cloud** — one small low puff hanging off the left underside.
- **hill** — the ridge is asymmetric; the second summit is a shoulder, not a peak.
- **grass** — a shallow nibble bitten out of the tall blade's left edge (open to the
  silhouette; it is **not** a hole).
- **dirt** — one clod on the back bank is rotated ~36° out of true.
- **bush** — one leaf scallop points *inward* (a bitten leaf) instead of bulging out.

## Technique notes for later batches

- `twotone(cid, d, over, under, dx, dy)` fills the shape with `under`, then draws the
  same path filled `over` at `(dx, dy)` clipped to itself. Sign convention: offset the
  overlay **toward** the light and the uncovered crescent lands on the shaded side. On a
  hill or a mound, offset *down* instead and the uncovered strip becomes the lit crest.
  A small `rotate` about a far point makes the band breathe in thickness.
- Never put a stroke on a path that runs along the viewBox edge — half the stroke is
  clipped and what survives is a hairline in an off-palette colour. That was the hill seam.
- `fill-rule="evenodd"` with a second subpath punches a genuine **alpha hole**, not a
  painted mark. Only use it when you want to see through the asset.
- Chrome silently renders nothing for `<use>` pointing at a `<g>` inside a `<clipPath>`.
  Always verify by decoding pixels.
- `capsule()` and `blade_path()` sample their outlines rather than using SVG arc flags,
  which both avoids flag bugs and gives a hand-drawn wobble for free.
