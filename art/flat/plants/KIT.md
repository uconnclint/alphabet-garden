# THE ALPHABET GARDEN PLANT KIT
### The shared vocabulary for all 78 hand-authored flat-vector plants

**Read `docs/TOCA_STANDARD.md` and `docs/FLAT_ART_BRIEF.md` first — they are binding.
This document is the *house dialect* of those rules, so that 78 plants by ~10 authors
look like one game.**

Three files make up the kit:

| file | what it is |
|---|---|
| `art/flat/plants/_kit.py` | the kit **in code** — palette, geometry, leaf/trunk/face generators, the two-tone emitter. Import it; do not re-implement it. |
| `art/flat/plants/_kit.svg` / `.png` | the kit **as a picture** — open the PNG and look at it before you draw anything |
| `art/flat/plants/_build_plants.py` | the six pilot plants, and the working example of how to use the kit |

```python
import sys, os
sys.path.insert(0, "art/flat/plants")
from _kit import *

d = Doc()                       # 1024x1024
d.form(trunk_chunky(508, 400, BASE_Y, 170, 320), SOIL,
       sweep(520, 760, 160, 250, lo=.18, hi=-.14), SOIL_DEEP)
open("my-plant.svg", "w").write(d.svg())
```

Rasterise with the shared renderer (2× headless Chrome → LANCZOS to 1×):

```python
from _build_plants import render
render("my-plant", svg, 1024, 1024, "art/flat/plants/my-plant.png")
```

---

## 1. CANVAS CONTRACT

Non-negotiable, because the game positions plants by their registration.

| | |
|---|---|
| canvas | **1024 × 1024**, transparent RGBA PNG + the `.svg` master beside it |
| ground line | base of trunk/stem touches **y = 1000** (±6px for the outline) |
| top of subject | **y ≈ 60–130** → object height ≈ 880–940 px = **86–92 % of frame** |
| horizontal | subject roughly centred but **never exactly** — put the mass at x 500–520 and let props break the symmetry |
| upright | the plant stands up. No 3/4 view, no perspective, flat elevation only |
| in-game size | `.plot .plant-art` is **128 × 150 css px** — an 8:1 downscale. Everything below exists to survive that. |

Verified against the existing renders: their alpha boxes bottom out at y 921–1024, so
y = 1000 is inside the established registration for all 78.

---

## 2. PALETTE

> **REVISED (Sep 2026 recolour pass).** A critic measured the first six pilots at median fill
> S 0.63 against the standard's 0.27, 86% of pixels above the S 0.55 ceiling. The hexes below
> are the corrected set that replaced them across all six pilots and `_kit.py` — the old
> saturated hexes are retired, do not use them. `_kit.py` is still the source of truth; this
> table is kept in sync with it and with `FLAT_ART_BRIEF` §3.

### 2.1 Core tokens — verbatim from `FLAT_ART_BRIEF` §3

`grass #9ddb76` · `grass-deep #79b85c` · `grass-dark #6c9959` · `sky-hi #8fd3ff` ·
`sky-lo #cdefff` · `soil #c2946b` · `soil-deep #a37855` · `cream #fff7e6` ·
`sun #ffe07a` · `sun-deep #f0c665` · `accent #ffb77e` · `berry #c65fd1` ·
`ink #000000` · `ink-soft #3f3026` · `brow #6b5342` (new — brows must not share the eye hex)

### 2.2 Extended tokens — added by the pilot, now locked

Fifteen tokens cannot dress 78 plants (there is no red for an apple, no metal for a
saucer, no second green for a canopy). These are derived by the rule in §2.3 and are
now **part of the locked palette**:

| token | hex | role |
|---|---|---|
| `leaf` | `#c3f598` | lit green face — the canopy's light tone (shadow: `grass`) |
| `sun-shade` | `#eebf5c` | shadow for `sun` (ΔV 0.067) |
| `ray-shade` | `#dbab58` | shadow for `sun-deep` (ΔV 0.082) |
| `accent-deep` | `#e09863` | shadow for `accent` (ΔV 0.122) |
| `fruit` | `#d96a62` | red accent — apples, pepperoni, berries (S 0.55, top of the accent band) |
| `fruit-deep` | `#b85149` | shadow for `fruit` (ΔV 0.129) |
| `ember` | `#d9876c` | autumn orange-red |
| `ember-deep` | `#b86a53` | shadow for `ember` (ΔV 0.129) |
| `steel` | `#b8bcc8` | tinted metal — saucers, wings, tools (unchanged, already in band) |
| `steel-deep` | `#969cae` | shadow for `steel` (ΔV 0.102, unchanged) |
| `sky-deep` | `#6cacd9` | shadow for `sky-hi` (ΔV 0.150) |
| `bark-lite` | `#dbad7f` | lit bark face / soil-lite (shadow: `soil`) |
| `cream-deep` | `#e8dcc4` | shadow for `cream` (ΔV 0.090, unchanged) |
| `beam` | `#ffeaa8` | flat light shapes — tractor beams, glows, halos (unchanged) |
| `berry-deep` | `#a44ead` | shadow for `berry` (ΔV 0.140) |

`_kit.SHADE` is a dict: **always take a shadow from it**, never eyeball one.

### 2.3 If you genuinely need a hue that does not exist

Adding one is allowed *once* and must be added to `_kit.py`, not to your own file.
Derive it so it lands inside the standard:

1. base fill: **V 0.55–0.97, S 0.05–0.55**, accents to **S 0.80** on small areas only;
2. shadow: same hue **rotated 8–14° cooler**, **S +0.03–0.08**, **V −0.09 to −0.14**;
3. never `#FFFFFF` for a field (use `cream`), never an untinted grey (use `steel`),
4. keep the whole plant inside **3–4 hue families, one dominant and warm**.

### 2.4 Known tension, deliberately accepted

Pre-revision, `soil-deep #8a5a33` (V 0.541) and `grass-dark #4a8531` (V 0.521) sat at the top
edge of TOCA §3.1's "muddy" V 0.35–0.55 band; the Sep 2026 recolour lifted both clear of it
(`soil-deep` is now V 0.639, `grass-dark` V 0.600). The rule that made that tension survivable
still applies and is worth keeping: these are shadow tokens, and they only ever appear as the
*shadow face* of a trunk or a far clump — never as a base fill. If a trunk's shadow ever
exceeds ~12 % of the frame, the trunk is too big, not the token wrong.

---

## 3. THE OUTLINE LADDER

Pure `#000000`, `stroke-linejoin="round"` and `stroke-linecap="round"` on **everything**.
One weight per *role*, not per shape — that is what stops ten authors drifting.

| constant | px @1024 | % of an 880px object | use |
|---|---|---|---|
| `OL_MAIN` | **13** | 1.48 % | silhouette, canopy clumps, trunk, petals, slices, internal contour lines |
| `OL_PROP` | **10** | 1.14 % | attached props 90–190 px tall — apples, butterflies, saucers, maple leaves |
| `OL_FINE` | **7** | 0.80 % | props under 90 px + fine detail — pepperoni, stars, rim lights, veins |
| `OL_BG` | **8**, hue-matched | — | atmospheric/background layer only. **Not black** — use a dark tint of its own fill. |

`ol_for(short_side)` gives `clamp(0.16 × short_side, 7, 13)` for anything awkward, so a
prop can never be eaten by its own outline.

**Depth-stepping (TOCA §3.8) is done by weight *and* colour**: interactive/foreground art
gets full-weight black; a background element like a tractor beam gets `OL_BG` in a
hue-matched tint. That is how the frame gets air.

Do **not** give every sub-shape its own computed weight. A plant is one object at game
size; a per-shape weight ladder reads as noise.

---

## 4. THE TWO-TONE SHADING RECIPE

> **Light comes from the UPPER-LEFT on every one of the 78 plants.** No exceptions.
> The shadow face is the lower-right ~35 % of every mass.

Every mass is built the same way, and `Doc.form()` does it for you:

1. flat **base** fill — one hex, no gradient, no filter, ever;
2. a **hard-edged shadow** shape from `sweep()`, **clipped to the parent** — same hue,
   ~10° cooler, S +0.05, **ΔV 0.09–0.14**;
3. **internal contour lines** at `OL_MAIN` where they do real form work (a lobe seam, a
   bark groove, a leaf midrib) — this does more than the shadow does;
4. the **outline** last, on top;
5. optionally **one** flat highlight `chip()` — a hard-edged lozenge, never a radial bloom.

```python
d.form(canopy_blob(512, 430, 244, 188), LEAF,
       sweep(512, 430, 244, 188, lo=.30, hi=-.42, wob=.09, seed=5.1),
       inner=seam_paths)          # seams are strokes, drawn inside the clip
```

`sweep(cx, cy, rx, ry, lo, hi, wob, seed)` returns the region below a hand-wavy line that
**rises left→right**. Vary `seed` and nudge `lo`/`hi` per clump — identical sweeps across
neighbouring clumps line up into one long stripe and read as a lighting pass, not as form.

**Never** use `linearGradient`, `radialGradient`, `filter`, `feGaussianBlur`, bevel or glow.
Verified absent from all six pilot SVGs.

---

## 5. LEAF VOCABULARY

Five silhouettes. Pick one; do not invent a sixth without adding it to `_kit.py`.

| generator | shape | use |
|---|---|---|
| `leaf_round(cx, cy, L, W, deg, curl)` | broad ovate, soft tip | bushes, canopy leaf marks, generic foliage |
| `leaf_pointed(cx, cy, L, W, deg, curl)` | lance/almond, pointed both ends | flower leaves, stem leaves |
| `leaf_lobed(cx, cy, L, deg, jit)` | 5-lobe maple | maple, sycamore, anything autumnal |
| `leaf_frond(cx, cy, L, W, deg, bend)` | fat curved paddle | palms, ferns, banana |
| `leaf_blade(bx, by, tx, ty, hw, tw, bend)` | grass blade, round tip | grasses, reeds, corn |

`vein(cx, cy, L, deg)` gives a midrib contour line — stroke it at the leaf's own weight.

Two treatments, and mixing them is the point:

* **Prop leaves** — outlined at `OL_PROP`, two-toned. They are objects.
* **Leaf marks** — flat unoutlined shapes in `grass-deep` / `grass-dark` scattered across a
  canopy. They are *pattern*, which TOCA §3.9 explicitly permits and which is how a green
  mass stops being a blob. **Never outline a leaf mark** — that is how a canopy turns into
  camouflage.

**Chunkiness rule that bites people:** lobed leaves need *shoulder* points beside each tip
(`leaf_lobed` puts them at ±13°) or the leaf renders as a spiky asterisk that vanishes at
128 px. Pilot v1 failed exactly this way.

---

## 6. TRUNK / STEM VOCABULARY + THE GROUND ANCHOR

| generator | use | minimum shaft width |
|---|---|---|
| `stem_slim(cx, y_top, y_base, w, lean, w_base)` | flowers, small plants | **≥ 40 px** (3.9 % of frame) |
| `trunk_chunky(cx, y_top, y_base, w_top, w_base, lean)` | trees | ≥ 130 px at the top |
| `trunk_palm(cx, y_top, y_base, hw_top, hw_base, n)` | palms, segmented stalks | returns rings **top-first** — paint in order so each lower ring overlaps the one above |

### The ground anchor — how every plant meets the soil

All three end in the same move, so 78 plants sit in the dirt plot identically:

* the shaft splays to **1.6–2.2 ×** its width over the last ~80 px;
* the bottom edge is **three unequal, deliberately un-mirrored root lobes**, the lowest
  touching **y = 1000**;
* **notches between the lobes stay 15–30 px deep.** Deeper reads as claws or trouser legs
  at game size — the single loudest defect of the first pilot pass;
* no contact shadow is drawn. The `dirt_plot` asset supplies the ground.

Draw the trunk **behind** the canopy. Trunk-in-front reads as claymation, not as flat art,
and it costs you the clean scalloped canopy edge.

---

## 7. THE FACE SYSTEM

**Realistic plants get NO face. Silly and wacky plants do.** That split is the game's
whole tonal signal — do not soften it.

```python
d.add(face(cx, cy, width_px, default="happy", tilt=-2.0))
```

`face()` emits the **entire rig**: an always-on `face-blush` group plus all six expression
groups, each with a stable id, all but the default carrying `display="none"`. The runtime
hot-swaps by toggling visibility — nothing has to be re-authored to animate.

```
face-neutral   face-happy   face-delighted   face-sleepy   face-surprised   face-mischief
```

Construction, in a 200-unit box scaled to `width_px`:

* eye anchors `(-46,-14)` and `(48,-18)` — **unequal on purpose**, and below the mass's
  vertical midline (low eyes read younger)
* mouth anchor `(2, 44)`
* blush: two `accent` ovals at opacity 0.45, unequal, off-centre, **always present**
* brows: `soil-deep`, **never black**, and only on `surprised` / `mischief` / `sleepy`

| state | eyes | mouth | brows |
|---|---|---|---|
| neutral | filled almonds, tilted −7° / +6° | small curve | — |
| happy | upward arcs `^ ^` | wide curve | — |
| delighted | upward arcs `^ ^` | open shape + cream teeth strip + `fruit` tongue | — |
| sleepy | down-bowed lines | small "o" | one soft arc |
| surprised | tall ovals + cream glint chips | tall oval | raised arcs |
| mischief | almonds with a **flat top edge** | one-corner-up curve | inward slants |

**Emotion budget: ≤ 3 changed marks** (eyes = 1, mouth = 1, brows = 1). `happy` →
`delighted` is one mark. If you need to redraw the head, the face is over-designed.

Face width should be **45–60 % of the mass it sits on**, placed slightly off-centre.

---

## 8. IRREGULARITY — THE CHARM RULE

Mathematical symmetry is instant tell #23 and killed the first authored batch.

* jitter every radius **±5–10 %** (`canopy_blob`'s `jit`), every angle **±2–5°**
* never mirror left/right — root lobes, eyes, cheeks and clumps are all asymmetric
* **every plant carries exactly one deliberate oddity**, and it should tell a small story:
  a nibbled leaf, one stubby petal, a crooked pepperoni, a fallen leaf on the ground, a
  saucer flying upside-down

### `bite()` — read this before you use it

`bite(cx, cy, r)` appends a circle sub-path removed with `fill-rule="evenodd"`. **It must
sit FULLY INSIDE the parent shape.** A circle that straddles the edge does *not* make a
bite: under evenodd the part outside the parent has winding 1 and renders as a **solid
filled lune stuck to the silhouette**. That artifact appeared on the pilot's apple, its
sunflower leaf and its pizza crust before it was caught.

For a true *edge* bite, push a point of the shape's own outline inward instead —
`canopy_blob(..., notch=i)` does exactly that.

---

## 9. CHECKLIST BEFORE YOU CALL A PLANT DONE

- [ ] `.svg` master and `.png` raster committed together in `art/flat/plants/`
- [ ] rasterised at **2× then downsampled** (use the shared `render()`)
- [ ] **You opened the PNG and looked at it**, and you looked at the original render beside it
- [ ] corner pixels decoded and actually transparent (a Chrome clipPath bug renders empty
      files that pass every other check)
- [ ] a 100-px run inside a fill is **bit-identical RGB** — run `_verify.py`
- [ ] zero `linearGradient` / `radialGradient` / `filter` / `<use>`-inside-`<clipPath>`
- [ ] outlines pure `#000000`, weight from the ladder, round joins **and** caps everywhere
- [ ] two-tone on every mass, light from the upper-left, ΔV 0.09–0.14
- [ ] palette only from §2; no pure white field, no untinted grey
- [ ] nothing load-bearing thinner than **15 px** (1.5 % of frame)
- [ ] survives the **black silhouette at 25 %** — and its props don't merge into the mass
- [ ] **survives 128 × 150 px.** Look at it at that size. This is the size players see.
- [ ] exactly one deliberate oddity
- [ ] faced plants: all six `face-*` groups present, only the default visible

`python3 art/flat/plants/_verify.py <id>` does the numeric half and writes a contact sheet
(original | flat | silhouette@25 % | game size) to `_compare/<id>-flat.png`.
