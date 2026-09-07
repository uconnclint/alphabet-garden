# PILOT BATCH — six authored flat-vector plants

Date: 2026-09-07 · branch `toca-polish`
Deliverables: `_kit.py` + `_kit.svg`/`.png` + `KIT.md`, and six `.svg`/`.png` pairs.
Build: `python3 art/flat/plants/_build_plants.py` · Verify: `python3 art/flat/plants/_verify.py`

These six set the visual language for the remaining 72. **Read `KIT.md` before you draw
anything.** This file is what the pilot *measured*, what it *got wrong first*, and what
the next ten authors must not repeat.

---

## 1. Context: why these are authored, not derived

`FLATTEN_NOTES.md` established that image-processing the glossy 3D renders cannot work,
because in a render a *design* edge and a *lighting* edge have identical pixel signatures.
Everything here is hand-authored SVG. The six plants keep the originals' character,
silhouette and personality; not one pixel is derived from them.

Two notes for whoever reads `FLATTEN_NOTES.md` next: its `art/flat/plants/*.png` outputs
for these six ids have been **replaced** by the authored versions (recoverable from git),
and `r-robot-rosebush.png` / `z-zombie-tree.png` are still flatten-pipeline leftovers with
no `.svg` beside them — they must be re-authored, not shipped.

---

## 2. Measured results

Every number below was produced by decoding actual pixels, not by inspection.

| plant | canvas | alpha bbox | corners transparent | **longest bit-identical RGB run** | colours >0.2 % | max S | pure `#FFFFFF` | untinted grey | median black run |
|---|---|---|---|---|---|---|---|---|---|
| `s-sunflower` | 1024² | 187,113 → 808,1007 | ✅ all 4 = α0 | **163 px** `#7ec850` | 16 | 0.82 | 0.000 % | 0.000 % | 14 px |
| `a-apple-tree` | 1024² | 38,64 → 1019,1007 | ✅ | **364 px** `#7ec850` | 15 | 0.76 | 0.000 % | 0.000 % | 13 px |
| `m-maple-tree` | 1024² | 38,65 → 1006,1007 | ✅ | **337 px** `#ff9d52` | 18 | 0.82 | 0.000 % | 0.000 % | 13 px |
| `b-butterfly-bush` | 1024² | 22,61 → 1018,1007 | ✅ | **532 px** `#b0e070` | 17 | 0.82 | 0.000 % | 0.060 %* | 14 px |
| `p-pizza-palm` | 1024² | 131,45 → 886,1013 | ✅ | **329 px** `#a9713f` | 19 | 0.82 | 0.001 %* | 0.000 % | 13 px |
| `u-ufo-tree` | 1024² | 12,48 → 1016,1007 | ✅ | **410 px** `#b0e070` | 18 | 0.83 | 0.000 % | 0.000 % | 13 px |

\* Both starred figures are **LANCZOS ringing on the 2×→1× downsample**, not fills: the
grey is antialiasing between `steel #b8bcc8` and black, the white is overshoot on the
`cream` teeth strip. Neither exists in the SVG masters.

**Flatness.** The standard measures over 100 px. The worst of the six clears it by 1.6×
and the best by 5.3×, and the runs are *bit-identical*, not low-variance — vector fills are
flat by construction. The sunflower is lowest because it is the most line-dense asset in
the set (26 outlined petals chop every horizontal span).

**Outline weight.** Median black run 13–14 px against object heights of 894–975 px →
**1.34 %–1.57 %**, inside the 1.2–1.7 % target and never below 2 px. Verified pure
`#000000` core with only an antialiased fringe.

**Structural checks.**
`grep` across all six SVGs: **zero** `linearGradient`, `radialGradient`, `filter`,
`feGaussianBlur`, and **zero** `<use>` anywhere (so the Chrome `<use>`-inside-`<clipPath>`
empty-file bug cannot bite). `stroke-linejoin="round"` present on **227 of 227** strokes.

**Silhouette at 25 %** rendered for all six (right panel of each `_compare/*-flat.png`).
All six are identifiable from the black shape alone. Two honest nits, scored below: the
butterfly bush's butterflies merge into the bush mass (only the antennae read clear), and
the UFO tree's two small saucers are the thinnest silhouette elements in the batch.

**Game size.** All six downscaled to the real in-game `128 × 150 css px` and inspected
(and again at 3× nearest-neighbour). All six read; see §4 for the blunt per-plant verdict.

---

## 3. Self-scores, C1–C4

Pass threshold is ≥7 in every category. **All six pass.**

| plant | C1 palette | C2 shape/silhouette | C3 line/outline | C4 shading | result |
|---|---|---|---|---|---|
| `s-sunflower` | 9 | 8 | 9 | 9 | PASS |
| `a-apple-tree` | 8 | 9 | 9 | 9 | PASS |
| `m-maple-tree` | 9 | 8 | 9 | 9 | PASS |
| `b-butterfly-bush` | 9 | 8 | 9 | 9 | PASS |
| `p-pizza-palm` | 9 | 9 | 9 | 9 | PASS |
| `u-ufo-tree` | 8 | 8 | 9 | 9 | PASS |

Where the points went, in the standard's own vocabulary:

* **`a-apple-tree` C1 = 8.** 10.8 % of the frame sits in the muddy V 0.35–0.55 band — 9.2 %
  of it is `soil-deep #8a5a33` (V 0.541), the trunk's shadow face. It is a sanctioned token
  used only as a shadow, but it is the largest muddy share in the batch and it is the
  trunk being generous rather than the token being wrong.
* **`u-ufo-tree` C1 = 8.** Five hue families do meaningful work (green, steel, sky-blue,
  sun/beam, soil). That is at the very top of the 3–4 budget; the subject demands it, but
  no later plant should exceed it.
* **`s-sunflower` C2 = 8.** Ink is 25.3 % of opaque pixels — the highest in the set, from
  two full outlined petal rings. At 128 px the head reads very slightly line-heavy.
* **`m-maple-tree` C2 = 8.** The maple leaves are deliberately fattened (shoulder points at
  ±13°, notches at 0.36–0.42 of L) so they survive 8:1 downscale. They read as maple at
  game size but as chunky five-fingered hands at full resolution. That trade is correct
  for this game; it is still a compromise.
* **`b-butterfly-bush` C2 = 8.** The butterflies sit *on* the bush, as in the original
  design, so at 25 % black-silhouette they merge with the foliage mass. Colour and outline
  separate them completely at every real display size.
* **`u-ufo-tree` C2 = 8.** The two small saucers (hull ~70 px including dome) are the
  batch's thinnest props and sit at the frame edges; readable at 128 px but the weakest
  element in the set.
* **C3 = 9 everywhere**, not 10, because the outlines are mathematically smooth Catmull-Rom
  curves with jittered *control points*. The wobble is in the geometry, not in the stroke
  itself; a true hand-made line quality would need per-point noise along the path.

---

## 4. Charm at 128 px — blunt, one line each

* **`s-sunflower`** — reads instantly and is pleasant, but it is the least *characterful* of
  the six; its charm is entirely craft (the caterpillar hole, the one stubby petal) rather
  than personality, which is the right answer for a face-free realistic plant but means it
  will never be the one a child points at.
* **`a-apple-tree`** — genuinely lovable: five fat two-tone apples with cream highlight chips
  popping off a clumped canopy, and the wormholed apple is a real small story.
* **`m-maple-tree`** — the strongest pure-colour piece in the batch; the all-warm canopy and
  the single leaf that has fallen beside the trunk give it more warmth than a realistic
  tree has any right to.
* **`b-butterfly-bush`** — the face plus two butterflies land completely at 128 px and it is
  the most immediately affectionate asset in the set.
* **`p-pizza-palm`** — yes, this one will make a five-year-old laugh: an open-mouthed
  delighted grin at the centre of five pepperoni slices, one pepperoni sliding off the
  crust, on a stack of segmented rings.
* **`u-ufo-tree`** — the tree looking straight up in alarm while a saucer beams a leaf off
  its head is the funniest *idea* in the batch and it survives the downscale, though the
  frame is the busiest and the two small saucers do the least work.

---

## 5. What the pilot got wrong first — do not repeat these

Six things were caught only by rendering, downscaling and **looking**. Every one of them
passed the numeric checks.

1. **`bite()` straddling an edge produces a solid blob, not a bite.** Under
   `fill-rule="evenodd"` the part of the circle *outside* the parent has winding 1 and
   fills. It put a floating orange disc on the pizza crust and a phantom ring on an apple.
   Keep the circle **fully inside**; for an edge bite use `canopy_blob(notch=i)`.
   `_kit.bite()`'s docstring now says so.
2. **Deep root notches read as claws.** The first ground anchor used 50–60 px notches; at
   128 px every plant looked like it was standing on two feet in trousers. Notches are now
   15–30 px and the flare is wider. This is `_root_pts()` and it is shared by all three
   trunk treatments — do not hand-roll a base.
3. **A lobed leaf drawn from tips alone is a spiky asterisk.** The first `leaf_lobed` had no
   shoulder points; eleven maple leaves rendered as black scribbles. Shoulders at ±13° and
   shallow notches fixed it.
4. **A tractor beam behind a canopy is an invisible tractor beam.** The UFO tree had to be
   recomposed twice to leave ~135 px of visible beam between the saucer and the foliage.
   Compose for the 128 px view, then check at 1024 — not the other way round.
5. **Slices at exactly half-pitch merge into one disc.** The pizza's five wedges were drawn
   at half-angle 20.5° on a 43° pitch, so they touched and the fan silhouetted as a solid
   dome. Half-angle is now 16–18°, leaving real negative-space gaps (TOCA §3.2 wants
   ≥ 2× outline weight).
6. **Identical `sweep()` parameters on neighbouring clumps line up into one long stripe**
   that reads as a lighting pass across the whole canopy rather than as per-clump form.
   Vary `seed`, `lo`, `hi` and `wob` per clump.

---

## 6. Guidance for the other 72

**Do this:**

* Import `_kit.py`. If a shape you need does not exist there, **add it to `_kit.py`**, with
  a docstring, so the next author inherits it. Do not keep private geometry.
* Look at the original render in `art/assets/plants/<id>.png` *first*, and keep its
  silhouette, its colour story and its personality. You are re-authoring a character, not
  illustrating a species.
* Build a plant as **4–8 large masses**, back to front, each independently `form()`ed. The
  crossing outlines are what makes a canopy read as clumps. More than ~8 masses is
  over-detailed for this style.
* Use unoutlined **leaf marks** (`grass-deep` / `grass-dark`) to keep green mass from being
  a blob. Never outline them.
* Give each plant exactly **one oddity that tells a story**.
* Realistic ⇒ **no face.** Silly / wacky ⇒ `face()` with a default expression that suits the
  gag. Do not put a face on a realistic plant to make it cuter.

**Do not do this:**

* Do not invent a hex. Do not use pure white, untinted grey, or a fill below V 0.55 as a
  *base*.
* Do not change the light direction. Upper-left, all 78.
* Do not compute a per-shape outline weight. Use the ladder.
* Do not use `<use>` inside `<clipPath>` — Chrome renders a valid-looking empty file.
* Do not trust "it built OK". Decode the corners, run `_verify.py`, **and open the PNG**.

**Suggested batching.** The kit covers: flowers (`stem_slim` + `leaf_pointed` + petal ring),
broadleaf trees (`trunk_chunky` + `canopy_blob` + `leaf_round` marks), palms
(`trunk_palm` + `leaf_frond`), grasses (`leaf_blade`), and object-plants (any of the above
plus authored props). Group the 72 that way rather than alphabetically — an author who
builds five flowers in a row will make them more consistent than one who builds a flower,
a robot and a banana.

**Reference sheet:** open `art/flat/plants/_kit.png`. It shows the five leaves, the three
trunks with the soil line, all twelve base/shadow pairs with hexes, and all six faces.
