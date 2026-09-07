# Flattening the claymation plants — pipeline, results, verdict

Date: 2026-09-07
Tool: `tools/flatten_plants.py`
Interpreter: a venv at
`/private/tmp/claude-501/-Users-clintonmcleod-AI-letter-garden/ce761231-.../scratchpad/venv/bin/python`
(Python 3.9, numpy 2.0.2, Pillow 11.3.0, opencv-python-headless 5.0.0, scikit-image 0.24.0).
System python3 was **not** modified. `scikit-image` (for `skeletonize`) and `opencv` are hard
requirements of the script; numpy/Pillow alone are not enough.

Originals in `art/assets/plants/` were **never written to**. Outputs are 1024x1024 RGBA in
`art/flat/plants/`. `_compare/` holds `original | flat | flat-at-game-size` sheets.

---

## VERDICT: **NOT VIABLE** for a blanket roll-out to all 78.

1 of the 8 validation samples passes the standard outright. 1 more is a single-category
near-miss. 6 fail, most of them badly. The plants must be **regenerated as native flat
vector** (image-to-image restyle or authored art) rather than derived from the existing
renders by image processing.

The important nuance: **the two problems the task was aimed at are actually solved.**
Instant tells #8 (gradients on discrete objects) and #9 (specular with radial falloff) are
gone, measurably and completely — C4 scores 7–9 on all eight samples, up from the reported 3.
What kills it is a *different* pair of categories: **C2 (shape language) and C3 (line
quality)**, and those fail for a reason that is structural, not a tuning problem.

---

## 1. The approach

Ten stages, in `flatten_plants.py`:

1. **Alpha mask + outside-RGB nearest-fill** so the black matte can't bleed into any filter.
2. **Specular kill.** Connected components of `V > 0.86 & S < 0.32` that are smaller than 1%
   of the object are dilated and Telea-inpainted back into their surrounding fill. Large
   bright areas (eyes, teeth, cream petals) are deliberately spared. 3–308 blobs removed per
   plant.
3. **Crease extraction.** A difference-of-gaussians valley detector on the *original*
   luminance finds the shading grooves the render uses to separate petals / slices / panels.
   Dense texture meshes are rejected by a bbox-fill-ratio test, the survivors are
   **skeletonised to 1px**, and short orphan strokes are pruned (a real contour line either
   runs >15% of object height or terminates on the silhouette). This is the stage that
   re-authors soft AO as §3.3 internal contour lines.
4. **Edge-preserving smoothing** — `pyrMeanShiftFiltering` + 3 bilateral passes at a reduced
   560px working resolution, which forces large shapes.
5. **k-means quantisation in Lab** (k=16), then merge any two centres closer than ΔE 12.
6. **Region hygiene** — per-label morphological open(r4)/close(r5), removal of components
   under 0.16% of object area, nearest-label refill of the holes.
7. **Palette discipline.** Tiered families: `ink` (V<0.30 **and** area<3.5%), `neutral`
   (S<0.16), and chroma buckets agglomerated at 40° of hue, capped at 5 families. Then per
   colour: neutrals tinted to `#7D85A0`-family or cream (never grey, never `#FFFFFF`),
   S ≤ 0.82 (0.70 on fills over 12% area), V lifted out of the muddy 0.35–0.55 band to a
   0.60 floor and capped at 0.965, then a gentle pull toward the locked game palette.
8. **Two-tone form.** Per family: one base (largest area), one shadow at ΔV 0.12 hue-rotated
   10° cooler with S+0.05, and at most one flat highlight chip at ΔV +0.10 (only if it
   covers under 18% of its family). A hue lock forbids the collapse from shifting any
   region's hue by more than 25°.
9. **Smooth label upscale** — per-label masks blurred (σ 2.2) and bilinear-resized to 1024,
   then argmax. Gives organic boundaries instead of blocky nearest-neighbour.
10. **Outlines.** Pure `#000000`, built from distance transforms, so **joins and caps are
    round by construction — there are no mitred spikes anywhere.** Weight is computed **per
    connected component** as `0.014 x that component's height`, floored at 2px and capped at
    16% of the component's short side so a small prop (a star, a floating saucer) can never
    be eaten by its own outline. The silhouette outline is drawn **inward**, so the canvas
    footprint and registration are untouched. Internal lines are the crease skeleton plus
    region boundaries where the two fills differ by ΔE ≥ 36 — deliberately *not* every
    quantiser boundary, because outlining every boundary traces lighting level-sets and is
    the single loudest "flattened 3D render" tell.

### Final parameters

```
work=560   k=16   merge_lab=12   open_r=4  close_r=5  min_area_frac=0.0016  label_smooth=2.2
spec_v=0.86  spec_s=0.32  spec_max_frac=0.010
ink_v=0.30  ink_max_frac=0.035  neutral_s=0.16  hue_bucket=40  max_chroma_fams=5
s_cap=0.82  s_large_cap=0.70  v_floor=0.60  v_ceil=0.965  ink_v_set=0.14
shadow_dv=0.12  shadow_cool=10  shadow_ds=0.05  hi_dv=0.10  hi_max_frac=0.18
fam_hue_lock=25  house_pull=0.45  house_tol=0.70
crease_sigma=0.016  crease_t=0.070  crease_min_len=0.055  crease_long_len=0.150
crease_density=0.26  crease_max_frac=0.045
sil_smooth=0.007  outline_pct=0.014  outline_min=2  outline_max_rel=0.16  internal_scale=0.72
internal_de_min=36
```

Runtime ≈ 1 s/plant; all 78 would take under two minutes.

---

## 2. Numeric validation

Measured on the eight outputs (opaque pixels only):

| plant | canvas | longest identical-RGB run | flat colours >0.2% | max S | fills in V 0.35–0.55 | pure `#FFFFFF` | untinted grey | bbox drift vs original |
|---|---|---|---|---|---|---|---|---|
| b-butterfly-bush | 1024² | **359 px** | 11 | 0.80 | 0.0% | 0.00% | 0.0% | 3 px |
| s-sunflower | 1024² | **323 px** | 10 | 0.82 | 0.0% | 0.00% | 0.0% | 0 px |
| p-pizza-palm | 1024² | **514 px** | 15 | 0.80 | 0.6% | 0.00% | 0.0% | 0 px |
| u-ufo-tree | 1024² | **240 px** | 12 | 0.82 | 0.0% | 0.00% | 0.0% | 1 px |
| a-apple-tree | 1024² | **418 px** | 10 | 0.81 | 0.0% | 0.00% | 0.0% | 0 px |
| z-zombie-tree | 1024² | **450 px** | 13 | 0.82 | 0.0% | 0.00% | 0.0% | 1 px |
| m-maple-tree | 1024² | **370 px** | 10 | 0.82 | 0.0% | 0.00% | 0.0% | 0 px |
| r-robot-rosebush | 1024² | **319 px** | 10 | 0.82 | 0.0% | 0.00% | 0.0% | 0 px |

The standard measures flatness over 100px runs. Every sample clears that by 2.4–5.1x, with
**literally identical RGB** across the run — the pipeline emits a fixed palette, so a fill is
bit-exact flat by construction, not merely low-variance.

Outlines: ink core is exactly `#000000` (81,704 exact-black opaque pixels on the pizza palm,
73,633 on the zombie) with only a 24–848 px anti-aliased fringe. Median horizontal black run
11 px on the pizza palm (computed weight 11.1) and 14 px on the zombie (12.7) — the weight
field is being honoured. The zombie's 90th percentile of 31 px is the mouth blob described
below, i.e. the measurement catches the same defect the eye does.

Registration is preserved: the alpha bounding box moves 0–3 px, and the 3 px case is the
optional silhouette-smoothing pass, not a translation.

---

## 3. Per-sample scores (C1–C4). Every output PNG below was opened and looked at.

**Pass threshold is ≥7 in every category.**

| plant | C1 palette | C2 shape/silhouette | C3 line/outline | C4 shading | result |
|---|---|---|---|---|---|
| **p-pizza-palm** | **9** | **7** | **7** | **9** | **PASS** |
| a-apple-tree | 9 | 7 | **5** | 8 | FAIL (C3) |
| r-robot-rosebush | 8 | **6** | 7 | 8 | FAIL (C2) |
| z-zombie-tree | 8 | **5** | **6** | 8 | FAIL |
| s-sunflower | 9 | **5** | **5** | 8 | FAIL |
| u-ufo-tree | 7 | **5** | **5** | 8 | FAIL |
| m-maple-tree | 8 | **4** | **5** | 8 | FAIL |
| b-butterfly-bush | **6** | **3** | **4** | 7 | FAIL |

Detail, in the doc's vocabulary:

- **p-pizza-palm — PASS.** Clean chunky slices, crust as a genuine second flat tone, thirteen
  outlined pepperoni, three hue families (butter/orange/coral) plus a brown trunk. Its 514px
  constant run is the best in the set. Nits that keep C2/C3 at 7: the trunk's stacked-ring
  design is gone, replaced by an arbitrary wobbly vertical two-tone split; a ~20px orphan
  black tick floats on the trunk; a black spur hangs under the right slice.
- **a-apple-tree — near miss.** Genuinely good chunky lobed canopy, five clean two-tone
  apples, correct outline weight. **C3=5** because a large meaningless black smear sits at
  the trunk/canopy junction (a deep-AO region that survived the ink-tier size gate) and a
  hooked squiggle floats free in the canopy. Both are artifact-hugging, not form-describing.
  This one is plausibly fixable.
- **r-robot-rosebush — C2=6.** Head, cyan eyes, yellow bulb, body, arms, leaves and base all
  survive and read; the chrome material is completely gone, which is the point. But the two
  roses are unreadable red blobs with a random squiggle, the chest grille and panel lines are
  gone, and the neck spring is a stub. "Which object is this?" is answerable; "what shape is
  each part?" is not.
- **z-zombie-tree — C2=5, C3=6.** Face survives, which was the surprise of the exercise: two
  eyes with pupils and a mouth are legible. But the eyes are asymmetric and lumpy, only one
  brow survived, the stitches and teeth are gone, and the mouth is a lumpy black *spill*
  rather than a drawn shape. Head and trunk are covered in olive/green camouflage blotches
  with no form logic.
- **s-sunflower — C2=5, C3=5.** The petals have **no separation at all** after orphan-stroke
  pruning, so the head reads as a cog or a gear, not a sunflower. The seed disc is an
  amorphous brown blob ringed by a doubled, scribbly outline that is visibly a trace of the
  render's disc edge.
- **u-ufo-tree — C2=5, C3=5.** The tree itself is decent. The three flying saucers are not:
  their hulls become knobbly irregular black-and-grey bands rather than discs, the alien is a
  green blob, and the sparkle stars got hue-dragged off yellow into yellow-green — a colour
  lie introduced by global (whole-image) family grouping.
- **m-maple-tree — C2=4.** The canopy is camouflage blotching. The maple leaves — the entire
  identity of the asset — are reduced to two surviving star shapes out of eleven. A stray
  white dot sits on the trunk. This is a posterised photograph, not authored art.
- **b-butterfly-bush — C1=6, C2=3, C3=4.** The worst. Both butterflies collapse into grey /
  mustard / blue blobs, one carrying a large near-white oval left by the specular inpaint.
  The bush's face is two grey dots and no mouth. Dark green holes are scattered through the
  canopy and loose grey dots float outside the silhouette.

---

## 4. The honest finding — why it cannot be tuned into a pass

**The failures are not parameter failures. They are an information problem.**

In these renders, the boundary between two *design* shapes (two petals, two pizza slices, a
saucer hull and its rim) and the boundary produced by *lighting* on a single smooth shape (a
lump on a canopy, an ambient-occlusion pocket, a sphere's terminator) have **identical pixel
signatures**: both are a soft dark valley or a soft value ramp. Nothing in the image says
which is which. So every threshold trades one failure directly against the other:

- **Sensitive settings** (low working res, many colours, low crease threshold) recover petal
  grooves and faces — and simultaneously trace hundreds of lighting level-sets, giving
  outlined amoebas, scribbly doubled contours and black dashes scattered across fills.
  Verified: this is what the first three iterations produced.
- **Conservative settings** (the ones shipped) delete the artifacts — and delete the petal
  separations, the maple leaves, the saucer hulls and the stitches with them. Verified: the
  sunflower lost every petal groove at exactly the setting that stopped the maple from
  showing dashes.

I ran four full parameter regimes across the eight samples. The pass count never exceeded
1/8. The categories that fail are stable across all four regimes.

A second, related failure: **quantiser regions are not design shapes.** Even unoutlined, a
canopy split into three iso-luminance blobs reads as camouflage, because the shadow lands
where the renderer's AO was, not where an illustrator would put a shadow face. §3.4 asks for
a *light face and a shadow face*. A level set of a lighting field is neither.

Third: **global, whole-image colour families produce cross-object colour lies** (green saucer
rims, yellow-green stars). Per-component families would fix that specific bug but not C2/C3.

### Where the pipeline succeeds

It succeeds exactly where the source object is already built from **large, hard-edged,
chromatically distinct design shapes** — the pizza palm (slices/crust/pepperoni), and to a
lesser degree the apple tree and the robot. It fails on **many small same-hue repeated forms
separated only by soft AO** — canopies of spheres, broccoli lobes, petal fans, chrome. Most
of the 78 are in the second group.

---

## 5. Recommendation

**Regenerate the plants as native flat vector via image-to-image restyle**, not by processing.
A generative pass sees "sunflower" and draws petals; a filter sees a luminance field and
cannot.

The work here is still worth keeping, for three reasons:

1. `tools/flatten_plants.py` is a working, parameterised, documented reference implementation
   of the standard's *measurable* rules — palette bands, tinted neutrals, two-tone ΔV,
   round-join outlines at 1.4% of object height, no pure white, no muddy mid-values. Point a
   critic agent at its `discipline()` / `two_tone()` / outline code for the numbers.
2. The outputs are a **proof that the flat direction reads at game size**. `.plot .plant-art`
   is 128x150 css px, so a 1024px source is shown at ~8:1. The third panel of each
   `_compare/*.png` sheet renders that exact size. At 150px the flat versions read *better*
   than the glossy originals — silhouettes are crisper and the black contour survives the
   downscale where soft AO turns to mush. The 13px outline at 1024 lands at ~1.6px at 1x /
   3.2px at 2x DPR, which is the spec's target.
3. The outputs are usable as **structure references for the restyle** (palette, silhouette,
   composition), and the extracted per-plant hex palettes are printed by the tool.

If a partial roll-out is ever wanted, the tool is safe to run — it never touches the
originals — but it should be applied **per asset with a human look**, not in batch. On current
evidence roughly 1 in 8 will pass and about 1 in 8 more will be close.

---

## 6. Reproducing

```
python3 tools/flatten_plants.py                       # all 78
python3 tools/flatten_plants.py s-sunflower           # one
python3 tools/flatten_plants.py --contact --measure   # sheets + flatness runs
python3 tools/flatten_plants.py --set crease_t=0.05 --set work=384   # override any parameter
```

Requires numpy, Pillow, opencv-python(-headless) and scikit-image. Writes only to
`art/flat/plants/`.
