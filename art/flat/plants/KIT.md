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

Sixteen tokens cannot dress 78 plants (there is no red for an apple, no metal for a
saucer, no second green for a canopy). These are derived by the rule in §2.3 and are
now **part of the locked palette**. This table is generated from `_kit.py`, not hand-typed —
run `python3 art/flat/plants/_check_palette.py` (§2.5) if you touch a hex on either side and
want proof they still agree:

| token | hex | role |
|---|---|---|
| `leaf` | `#c3f598` | lit green face — the canopy's light tone (shadow: `grass`) |
| `sun-shade` | `#eebf62` | shadow for `sun` (ΔV 0.067) |
| `ray-shade` | `#dbab58` | shadow for `sun-deep` (ΔV 0.082) |
| `accent-deep` | `#e09863` | shadow for `accent` (ΔV 0.122) |
| `fruit` | `#d96a62` | red accent — apples, pepperoni, berries (S 0.55, top of the accent band) |
| `fruit-deep` | `#b8544e` | shadow for `fruit` (ΔV 0.129) |
| `ember` | `#d9876c` | autumn orange-red |
| `ember-deep` | `#b86a53` | shadow for `ember` (ΔV 0.129) |
| `steel` | `#b8bcc8` | tinted metal — saucers, wings, tools (unchanged, already in band) |
| `steel-deep` | `#969cae` | shadow for `steel` (ΔV 0.102, unchanged) |
| `steel-dark` | `#7f8697` | shadow for `steel-deep` — bolts, grille slots, deep metal (ΔV 0.090) |
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

### 2.5 Palette drift is a solved problem — use the checker

Three hexes above (`sun-shade`, `fruit-deep`, `accent-deep`) once drifted between this file,
`FLAT_ART_BRIEF.md`, and `_kit.py` itself, and `steel-dark` went undocumented in both places —
that is exactly the class of bug a hand-maintained table cannot catch itself.
`art/flat/plants/_check_palette.py` reads `_kit.py`'s live palette (`vars(_kit)`, not a
retyped list) and diffs it against `FLAT_ART_BRIEF.md`'s tables, failing on any mismatch,
duplicate, or omission:

```
python3 art/flat/plants/_check_palette.py
```

It does not check *this* file's tables mechanically (KIT.md's prose format varies too much
section to section), so when you touch a hex here, touch it in `_kit.py` and
`FLAT_ART_BRIEF.md` too and run the checker — `_kit.py` is the one true source either way.

---

## 3. THE OUTLINE LADDER

> **REVISED (fan-out gate fix).** The ladder used to run `13 / 10 / 7 / 8` — anything
> documented here with a `7` or an `8` for a foreground weight is the FAILED, already-rejected
> version. The game renders a plant at **128×150 css px**, an **8:1 downscale**: a 7px stroke
> lands at 0.87px and ghosts out completely. The ladder below is what `_kit.py` actually
> ships, and it is deliberately compressed to stay above that downscale floor. There is no
> thinner rung, and there must never be one — "make it thinner" is not an available way to
> de-emphasise something; only colour and layer order are.

Pure `#000000`, `stroke-linejoin="round"` and `stroke-linecap="round"` on **everything**.
One weight per *role*, not per shape — that is what stops ten authors drifting.

| constant | px @1024 | % of an 880px object | use |
|---|---|---|---|
| `OL_MAIN` | **13** | 1.48 % | silhouette + primary masses — canopy, trunk, slabs, petals, internal contour lines |
| `OL_PROP` | **12** | 1.36 % | attached props 90–190 px tall — apples, butterflies, saucers, maple leaves, xylophone bars |
| `OL_FINE` | **11** | 1.25 % | props under 90 px + fine internal detail — pepperoni, stars, rim lights, veins, bolts, grille slots. **`OL_FLOOR` — the floor. Nothing a player must see may be stroked thinner than this.** |
| `OL_BG` | **10**, hue-matched | 1.14 % | atmospheric/background layer only. **Not black** — use a dark tint of its own fill. |

`ol_for(short_side)` gives `clamp(round(0.16 × short_side), OL_FINE, OL_MAIN)` — i.e. **11 to
13**, never lower — for anything awkward, so a prop can never be eaten by its own outline and
can never sink below the downscale floor either.

**Depth-stepping (TOCA §3.8) is done by weight *and* colour**: interactive/foreground art
gets full-weight black at `OL_MAIN`/`OL_PROP`/`OL_FINE`; a background element like a tractor
beam gets `OL_BG` in a hue-matched tint. That is how the frame gets air — never by thinning a
foreground stroke past `OL_FLOOR`.

Do **not** give every sub-shape its own computed weight. A plant is one object at game
size; a per-shape weight ladder reads as noise.

**This is a different rule from §9's "nothing load-bearing thinner than 15 px."** That
checklist item is about *shape width* — how fat a stem, bar, or leg is drawn — not stroke
weight. A shaft can be 15 px+ wide and still outlined at `OL_FINE` (11 px); the two numbers
are independent and neither substitutes for the other.

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

`vein(cx, cy, L, deg=0.0, frac=0.72)` gives a midrib contour line — stroke it at the leaf's
own weight. `frac` is how far down the leaf the vein reaches (0.72 by default).

Two treatments, and mixing them is the point:

* **Prop leaves** — outlined at `OL_PROP`, two-toned. They are objects.
* **Leaf marks** — flat unoutlined shapes in `grass-deep` / `grass-dark` scattered across a
  canopy. They are *pattern*, which TOCA §3.9 explicitly permits and which is how a green
  mass stops being a blob. **Never outline a leaf mark** — that is how a canopy turns into
  camouflage.

**Chunkiness rule that bites people:** lobed leaves need *shoulder* points beside each tip
(`leaf_lobed` puts them at ±13°) or the leaf renders as a spiky asterisk that vanishes at
128 px. Pilot v1 failed exactly this way.

### 5.1 The canopy mass — `canopy_blob` / `lobe_profile`

A tree or bush is not one leaf blown up; it is a lobed **mass** with leaf marks scattered on
top. `canopy_blob` is that mass:

```
canopy_blob(cx, cy, rx, ry, n, jit, bul, start=-96, notch=None)
```

`n`, `jit` and `bul` are **required positional arguments, with no defaults** — that is
deliberate and load-bearing. They used to be module-level defaults, which is exactly why the
apple / maple / butterfly-bush pilots measured 0.93 / 0.78 / 0.76 silhouette IoU against each
other: three plants wearing one mass. Get `jit`/`bul` from `lobe_profile`, one seed per plant:

```python
JIT, BUL = lobe_profile(seed=41.7, n=11, jit=0.09, bul=(30, 78))
canopy_blob(512, 430, 244, 188, 11, JIT, BUL)
```

`lobe_profile(seed, n, jit=0.08, bul=(34, 72))` derives `(jit, bul)` from one per-plant
`seed` — raise `jit` for a raggedy mass, lower it for a tight ball; widen `bul` for deep,
uneven scallops. Two plants with different seeds cannot produce the same silhouette by
accident. `notch=i` on `canopy_blob` pushes lobe `i` inward — the sanctioned way to give a
canopy a bitten-leaf oddity (see §8's `bite()` warning for why a stray circle is not).

Two more small shape helpers live beside the leaf set: `star4(cx, cy, r, deg=0.0, waist=0.30)`
(a chunky four-point sparkle — never a perfect star, one arm is always shorter) and
`fruit_blob(cx, cy, r, deg=0.0)` (a round, dimpled-crown silhouette for apples, berries, any
round fruit prop).

---

## 6. TRUNK / STEM VOCABULARY + THE GROUND ANCHOR

> **REVISED (fan-out gate fix).** The signatures below are **wrong in the previous revision
> of this doc** in the single most dangerous way a signature can be wrong: `root_seed` is
> documented as the treatments' 5th/6th *positional* argument, but it is a required argument
> with no visual meaning of its own — get its position wrong and Python does not complain, it
> just silently uses whatever you passed as the plant's foot seed. An author writing
> `trunk_chunky(cx, top, base, w0, w1, lean=0)` positionally was actually calling
> `trunk_chunky(cx, top, base, w0, w1, root_seed=0)` and getting `lean`'s *default* — two
> plants both written that way emitted a **byte-identical foot path**. `_kit.py` now makes
> `root_seed` (and `face()`'s `mass_w`, §7) **keyword-only**: get the call wrong today and you
> get an immediate `TypeError`, not a shared silhouette 40 plants later.

| generator | use | minimum shaft width |
|---|---|---|
| `stem_slim(cx, y_top, y_base, w, *, root_seed, lean=18.0, w_base=None, root_lobes=3, root_depth=(16, 30))` | flowers, small plants | **≥ 40 px** (3.9 % of frame) |
| `trunk_chunky(cx, y_top, y_base, w_top, w_base, *, root_seed, lean=0.0, root_lobes=3, root_depth=(16, 30), flare=1.0)` | trees | ≥ 130 px at the top |
| `trunk_palm(cx, y_top, y_base, hw_top, hw_base, n=7, wob=(...))` | palms, segmented stalks | returns `[(path, hw, cy), ...]` **top-first** — paint in order so each lower ring overlaps the one above |

The `*` is not decorative — it means everything after it, including `root_seed`, **must** be
passed by keyword. `stem_slim(cx, top, base, 60, 5.0)` now raises `TypeError: stem_slim()
takes 4 positional arguments but 5 were given` instead of silently seeding the foot with
`5.0`. Always write the call as `stem_slim(cx, top, base, w, root_seed=5.0, lean=12)`.

`flare` (trunk_chunky only) scales how hard the shaft splays into the foot: 0.8 = a slim
upright pole, 1.4 = a broad buttressed base.

### 6.1 The ground anchor — `root_pts`, and how every plant meets the soil

`stem_slim` and `trunk_chunky` both delegate their foot to one shared generator:

```
root_pts(cx, wb, y_base, seed, lobes=3, spread_k=1.06, depth=(16, 30))
```

`lobes` unequal root lobes, deliberately not mirrored, left to right. This — not a fixed
7-point shape — is why 78 plants can all stand in the dirt the same way without standing on
the *same foot*: a different `seed` reshuffles the lobe positions and depths. All three trunk
treatments end in the same move:

* the shaft splays to **1.6–2.2 ×** its width over the last ~80 px;
* the bottom edge is **unequal, deliberately un-mirrored root lobes** (3 by default —
  `root_lobes` / `lobes`), the lowest touching **y = 1000**;
* **notches between the lobes stay 15–30 px deep** (`root_depth` / `depth`). Deeper reads as
  claws or trouser legs at game size — the single loudest defect of the first pilot pass. A
  plant that *wants* claws (a xylophone tree's splayed foot) passes `depth=(40, 80)` and
  `lobes=4` deliberately, and owns that decision;
* no contact shadow is drawn. The `dirt_plot` asset supplies the ground.

Draw the trunk **behind** the canopy. Trunk-in-front reads as claymation, not as flat art,
and it costs you the clean scalloped canopy edge.

---

### 6.2 RIBBON / BRANCH / LIMB VOCABULARY (organic, non-foliage)

The kit's answer to "every tree is a column plus a blob." A **ribbon** is a tapered band swept
along a spine; a branch, a horn, and a crescent tube are the same primitive with different
width profiles laid over it. All of these are smooth/organic — for a machined equivalent, see
§6.3.

| generator | shape | use |
|---|---|---|
| `bow(x0, y0, x1, y1, k=0.22, n=6)` | a spine polyline from A to B, bowed sideways by `k × length` | the spine every ribbon/branch/horn/crescent is built on; give each limb its own `k` so a fork is never mirrored |
| `ribbon(spine, widths, cap0="flat", cap1="round")` | a closed band along `spine`, full width `widths[i]` at each point | the underlying primitive — `branch`/`horn`/`crescent` are all `ribbon` with a different `bow` + width profile. Caps: `"flat"` (square butt), `"round"` (semicircular), `"point"` (tapers to nothing — horns, thorns, spikes) |
| `branch(x0, y0, x1, y1, w0, w1, k=0.20, n=6, cap="round")` | a tapered limb from the trunk (`w0`) out to a tip (`w1`) | **THE branch.** A tree without this is a column with a blob on top, forever. Draw limbs *before* the foliage clusters so the clusters cover the tips |
| `horn(cx, cy, L, w, deg=0.0, k=0.16)` | fat rounded base tapering to a real point | horns, thorns, tusks, spikes |
| `crescent(cx, cy, L, w, deg=0.0, arc=0.34, waist=0.55)` | curved tube, fat in the middle, rounded at both ends | **a banana.** Not a leaf, not a blob — the one shape a foliage-only kit cannot make. `arc` is how far it bends; `waist` how thin the ends get relative to `w` |

---

### 6.3 RECTILINEAR / MECHANICAL VOCABULARY

The opt-out of `smooth_closed`. Robots, xylophones, saucers, escalators, firetrucks — roughly
a fifth of the 78 — are unbuildable out of scallops. Corner radii here follow TOCA §3.2:
`r = 0.05–0.10` of the **short side** for rigid things (soft things round to 0.12–0.30).

| generator | shape | use |
|---|---|---|
| `poly(pts, close=True)` | exact straight-line path, no smoothing, no wobble | any hard edge that isn't rounded |
| `hard_poly(pts, r)` | a polygon with **rounded corners but dead-straight edges** — `r` is a scalar or one radius per vertex, each clamped to half the shorter adjacent edge | the machined counterpart of `smooth_closed`; what makes a panel read as manufactured rather than grown |
| `slab(cx, cy, w, h, r=0.08, deg=0.0, skew=0.0)` | rigid rounded rectangle | **THE mechanical mass primitive.** `r` is a *fraction* of the short side (0.05–0.10 rigid, up to 0.30 soft); `skew` tapers the top edge in so the slab reads as a moulded part, not clip-art |
| `panel(cx, cy, w, h, r=0.08, deg=0.0, inset=0.16, skew=0.0)` | returns `(outer, inner)` — a slab with a recessed face plate inside it | draw `outer` with `Doc.form`, stroke `inner` as a contour line — two lines of code turn a blob into a machine |
| `grille(cx, cy, w, h, n, deg=0.0, gap=0.42)` | returns a list of `n` vertical slot paths | speaker/vent grille; slot width is derived so slots never fall under `OL_FLOOR` — if they would, `n` is reduced automatically |
| `bolt(cx, cy, r, deg=0.0)` | returns `(head, slot)` — a rivet/bolt head plus its screw-slot line | fill `head` in the panel's own shadow tone, stroke `slot` at `OL_FINE`. Never fewer than 2 bolts, never in a perfect square — offset one |
| `graduated(n, a, b, curve=1.0)` | `n` values from `a` to `b`; `curve` > 1 back-loads, < 1 front-loads | the non-organic repetition primitive — xylophone bar lengths, escalator steps, ladder rungs, a row of windows |
| `plinth(cx, y_base, w, h, r=0.06, feet=2)` | returns `(plate, [pad, ...])` — a wide slab with `feet` square pads under it | the RECTILINEAR ground anchor. Root lobes are wrong on a robot — this is what a manufactured plant stands on instead of `root_pts` |
| `trunk_stack(cx, y_top, y_base, w_top, w_base, n, r=0.10, seed=0.0)` | returns `[(slab_d, w, cy, h), ...]` **top-first** | a MACHINED segmented column (robot spine, drainpipe) — the rigid counterpart of `trunk_palm`, so a mechanical plant does not have to borrow a palm's soft lozenges |
| `sweep_hard(cx, cy, rx, ry, lo=0.30, hi=-0.34)` | the machined shadow: a **straight-edged** sweep, no wobble | use on slabs, panels, bars, hulls — anything with a manufactured edge. A hand-wavy shadow line inside a crisp rectangle is the tell that the author only had organic tools |

---

## 7. THE FACE SYSTEM

**Realistic plants get NO face. Silly and wacky plants do.** That split is the game's
whole tonal signal — do not soften it.

### 7.1 Signature — `mass_w` is required and keyword-only

```
face(cx, cy, width_px, *, mass_w, default="happy", tilt=0.0, with_blush=True,
     eyes=None, eye_r=None, mouth=None, mouth_k=1.0, brow_lift=0)
```

`face(cx, cy, width_px, default="happy", tilt=-2.0)` — the call as this doc previously showed
it — **raises `TypeError: face() missing 1 required keyword-only argument: 'mass_w'`.**
`mass_w` is the width of the mass the face sits on (a canopy, a head, a saucer), and it is
required so the kit can assert the 45–60 % rule below instead of letting a face silently slide
off a silhouette. It is keyword-only for the same reason `root_seed` is (§6): the kit will not
let a shape-defining number hide in an unlabelled argument slot. Call it like this:

```python
d.add(face(cx, cy, width_px, mass_w=canopy_width, default="happy", tilt=-2.0))
```

`width_px / mass_w` must land in **45–60 %** (`FACE_MIN`/`FACE_MAX`) or `face()` raises
`AssertionError` naming the actual percentage and the 45–60 % rule — widen the mass or shrink
the face, don't relax the check.

### 7.2 What it emits

`face()` emits the **entire rig**: an always-on `face-blush` group (unless
`with_blush=False`) plus all **seven** expression groups, each with a stable id, all but
`default` carrying `display="none"`. The runtime hot-swaps by toggling visibility — nothing
has to be re-authored to animate.

```
face-neutral   face-happy   face-delighted   face-sleepy   face-surprised   face-mischief   face-blink
```

`blink` is the 7th state — previous revisions of this doc listed only six. It is a near-flat,
barely-upward-bowed lid with **no brow**, distinct from the droopy `sleepy` lid, meant to be
toggled on top of whatever expression is current rather than swapped in as a mood of its own.
Ids nest as `face-<kind>` → `face-<kind>-eyes`, `face-<kind>-mouth` [, `face-<kind>-brows`], so
the runtime can swap a whole expression or just blink over it.

### 7.3 The anchors — why ~30 faced plants don't have to share one face

Construction happens in a 200-unit box, origin at the face centre, scaled to `width_px`
(`s = width_px / 200`). Every anchor is a **parameter**, not a constant — this is exactly what
stops "same six states on thirty plants" (Instant Tell #19):

| param | default | controls |
|---|---|---|
| `eyes` | `((-46, -14), (48, -18))` | the two eye centres — **deliberately unequal**, and below the mass's vertical midline (low eyes read younger) |
| `eye_r` | `(19, 26)` | eye (x, y) radius — scales every eye shape, not just `neutral`'s ellipse |
| `mouth` | `(2, 44)` | the mouth anchor |
| `mouth_k` | `1.0` | uniform scale on every mouth mark and its stroke weight |
| `brow_lift` | `0` | vertical offset raising/lowering the brow arcs, independent of the eyes they sit above |

`with_blush=True` toggles the always-on cheek group; blush is anchored to `eyes` (at
`(lx*1.87, ly+44)`), so narrow eye anchors also narrow the cheeks instead of leaving blush
stranded off the silhouette.

Brows are **`BROW` (`#6b5342`)** — a previous revision of this doc said "soil-deep." Brows
must not share the eye hex (`ink-soft`, `#3f3026`) or the two marks collapse into one shape at
game size; `soil-deep` is a different token again and was simply wrong. Brows only draw on
`surprised` / `mischief` / `sleepy`.

**Worked example — moving all three anchors, not just picking a `default`:**

```python
d.add(face(cx, cy, 220, mass_w=440, default="happy", tilt=3.0,
           eyes=((-58, -6), (54, -10)),   # wider-set, higher on the mass than default
           eye_r=(24, 20),                # rounder and shorter than default (19, 26)
           mouth=(-6, 30),                # shifted left and up
           mouth_k=1.25,                  # bigger mouth marks
           brow_lift=8))                  # brows sit higher above the (raised) eyes
```

This produces a visibly different face from the copy-paste default — wider eyes, a
higher/left mouth, bigger mouth marks — from the same `default="happy"` state. Changing
`default` alone is not enough; move at least `eyes` and `mouth` per plant.

### 7.4 The seven states

| state | eyes | mouth | brows |
|---|---|---|---|
| neutral | filled almonds, tilted −7° / +6° | small curve | — |
| happy | upward arcs `^ ^` | wide curve | — |
| delighted | upward arcs `^ ^` | open shape + cream teeth strip + `fruit` tongue | — |
| sleepy | down-bowed lines | small "o" | one soft arc |
| surprised | tall ovals + cream glint chips | tall oval | raised arcs |
| mischief | almonds with a **flat top edge** | one-corner-up curve | inward slants |
| blink | near-flat lid, hair of upward bow | *(mouth unchanged from neutral)* | — |

**Emotion budget: ≤ 3 changed marks** (eyes = 1, mouth = 1, brows = 1). `happy` →
`delighted` is one mark. If you need to redraw the head, the face is over-designed.

Face width should be **45–60 % of the mass it sits on** (enforced, §7.1), placed slightly
off-centre.

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
- [ ] nothing load-bearing thinner than **15 px** (1.5 % of frame) — this is *shape width*
      (a stem, a bar, a leg), not outline stroke weight; strokes follow the §3 ladder (11–13 px)
- [ ] survives the **black silhouette at 25 %** — and its props don't merge into the mass
- [ ] **survives 128 × 150 px.** Look at it at that size. This is the size players see.
- [ ] exactly one deliberate oddity
- [ ] faced plants: all six `face-*` groups present, only the default visible

`python3 art/flat/plants/_verify.py <id>` does the numeric half and writes a contact sheet
(original | flat | silhouette@25 % | game size) to `_compare/<id>-flat.png`.
