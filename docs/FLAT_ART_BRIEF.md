# FLAT ART AUTHORING BRIEF
### How to actually build Alphabet Garden's art. Operational companion to `TOCA_STANDARD.md`.

Read `TOCA_STANDARD.md` first — it is the standard. This doc is *how we hit it here*.

---

## 0. Medium: authored SVG → PNG (not generated)

Image generation is **unavailable** on this workspace (`403 insufficient_permissions`,
`image_video_generation`). All art is therefore **hand-authored SVG**, rasterised to
transparent PNG via headless Chrome (see `art/flat/_build_flat.py`).

This is a feature, not a consolation prize. Authored vector gives us what diffusion cannot:
exact hex control (C1), literally zero gradient across a fill (C4), outline weights hit to the
decimal (C3), guaranteed clean alpha, tiny files, resolution independence, and zero
derivative-work risk. Keep the `.svg` source next to every `.png` — the SVG is the master.

---

## 1. THE FOUR FAILURES OF BATCH 1 — do not repeat them

The first authored batch (sun, cloud, hill, grass, dirt, shrub) was measurably flat and
on-palette, and still would have failed review. Every new asset must fix all four:

1. **NO OUTLINES.** Batch 1 had none. `TOCA_STANDARD` C3 scores "no outlines" a **3 — an
   automatic fail.** Outlines are not optional; they are the single loudest signal of the style.
2. **NO FORM BLOCKING.** Every shape was one flat tone. C4 wants a base fill **plus one
   shadow tone** at ΔV 0.08–0.18, hard-edged, occupying roughly the lower/away third.
3. **MATHEMATICAL PERFECTION.** Twelve identical rays at exact 30° intervals reads as clipart.
   C3's 9–10 descriptor demands *"faint hand-made irregularity, not a mathematical stroke."*
4. **NO CHARACTER.** Technically correct and completely forgettable. Charm is the deliverable,
   not a bonus.

---

## 2. Non-negotiable construction rules

### Outlines
- Pure `#000000`. Not dark brown, not 90% black.
- Weight **1.2–1.7% of the object's height**, clamped to **≥2px** at 1024px canvas
  (so a full-canvas object ≈ 13–17px; a 300px-tall prop ≈ 4–5px).
- `stroke-linejoin="round"` and `stroke-linecap="round"` on **everything**. Mitred spikes are
  instant tell #14.
- Outline the silhouette *and* the internal forms that do real work (a petal against a centre,
  a leaf against a stem). Not every internal seam — only the ones that clarify form.
- **Depth-step the weight:** interactive/foreground layer full black at full weight; midground
  thinner and hue-matched (a dark tint of its own fill, not black); far background outlines
  dropped entirely. This is how the scene gets air (C8).

### Fills
- Absolutely flat. **No `linearGradient`, no `radialGradient`, ever, inside an object.**
  (A single very soft gradient is permitted for the *sky backdrop only*.)
- No filters: no `feGaussianBlur` drop shadows, no bevel, no glow. Instant tells #5 and #10.
- Two-tone form: base + shadow at ΔV 0.08–0.18, **hard-edged**, clipped to the parent shape.
- Optional single highlight *chip*: a flat, hard-edged shape — never a soft radial bloom.

### Colour
- 3–4 hue families per scene, one dominant and warm.
- Fills in **V 0.55–0.97, S 0.05–0.55**, with a few small high-sat accents. Nothing above S 0.85.
- Avoid the muddy **V 0.35–0.55** band unless it is a deliberate accent.
- **Never pure `#FFFFFF`** for a field — use cream `#FFF7E6` / `#FFFBF2`.
- **Shadows are hue-derived** from their own surface (a darker, slightly more saturated,
  slightly hue-shifted version), never grey and never black.

### Shape
- Chunky. Nothing thinner than **1.5% of frame height**.
- Corner radii **scale with the shape** — a big soft hill and a small firm button do not share
  a radius. Instant tell #7.
- Must survive the **black-silhouette-at-25% test**: fill the shape solid black, scale to 25%,
  and it should still be identifiable.
- Preserve negative-space gaps at overlaps so forms don't merge into a blob.

### Irregularity (the charm rule)
- Break symmetry deliberately: vary ray lengths ±6–10%, rotate a lobe 3–5°, make one leaf
  bigger, let a cheek sit slightly off-centre.
- Hand-drawn-feeling curves: prefer a path with slightly uneven control points over a perfect
  circle or a perfect rounded-rect.
- Give every asset **one small deliberate oddity** — a nibbled leaf, a crooked pebble, one ray
  stubbier than its neighbours. Instant tell #23 is "a perfectly tidy scene."

### Faces (characters)
- Eyes: solid near-black **almond/oval** shapes, not perfect circles, not outlined rings.
- Mouth: a thick round-capped stroke or a filled shape; round-capped always.
- Flat cheek circles at low opacity of a warm hue — never a soft airbrush.
- Design **≥6 expressions** per character, each reachable by changing **≤3 marks**
  (eye shape, mouth shape, brow). Build them as swappable SVG groups so animation can switch them.

---

## 3. Palette tokens (use these ids, don't invent hexes)

> **REVISED after review.** The original table was measurably too hot: a critic sampling 1.95M
> pixels found median fill **S 0.63 against the standard's 0.27**, with **86.4% above the S 0.55
> ceiling** — the batch read as "loud clip-art" where the reference reads "sunlit and washed."
> These values are the corrected set. **Use these hexes. The old saturated ones are retired.**

> **Drift check.** `_kit.py` is the executable source of truth for every plant-kit hex below;
> this file is kept in sync **by hand**, which is exactly how `sun-shade`, `fruit-deep` and
> `accent-deep` drifted from `_kit.py` and how `steel-dark` went undocumented entirely. Run
> `python3 art/flat/plants/_check_palette.py` after touching a hex on either side — it reads
> `_kit.py` live and diffs every token it finds against this file's tables, and exits non-zero
> on any mismatch, duplicate, or omission.

### Layer 1 — foreground / interactive (full black outlines)

> **BATCH 5 (soil only).** The dirt plot is the game's primary interactive object and must
> carry the frame's focal weight. At `#c2946b` it measured S .448 — indistinguishable from the
> bush (.453) and the grass (.461) — so nothing told a child where to tap. The whole soil
> family was pulled to **S .568 / V .780** (hue held at 25–31°, ΔV spacing preserved), which
> also buys ΔV .079 against the V .859 grass field it sits on. All four tones stay under the
> S 0.60 ceiling; measured on the shipped PNGs, ≤0.11% of pixels sit above S 0.60. **These are
> the current soil hexes; the `#c2946b` family is retired.**


| token | hex | use |
|---|---|---|
| `grass` | `#9ddb76` | meadow base |
| `grass-deep` | `#79b85c` | grass shadow tone |
| `soil` | `#c78956` | dirt base — S .568 / V .780 (batch 5) |
| `soil-deep` | `#a57144` | dirt shadow / packed base band / hollow interior |
| `soil-lite` | `#dd9b68` | lit crumbs on tilled soil |
| `sun` | `#ffe07a` | sun body |
| `sun-deep` | `#f0c665` | sun rays |
| `sun-shade` | `#eebf62` | sun body shadow |
| `ray-shade` | `#dbab58` | ray shadow face |
| `cream` | `#fff7e6` | panels, near-white (never pure `#FFFFFF`) |
| `cloud-shade` | `#c6d8e6` | cloud shadow — hue-rotated cool to 206° |

### Layer 2 — far background (NO black outline; must sit back)

Never share a hex with Layer 1. Target **S ≤ 0.24, V 0.87–0.93**.

| token | hex | use |
|---|---|---|
| `hill-far` | `#d0edbe` | far hill fill |
| `hill-far-deep` | `#badea9` | far hill shadow |
| `sky-hi` | `#8fd3ff` | sky top |
| `sky-lo` | `#cdefff` | sky horizon |

### Accents & ink

Accents are the **only** fills permitted above S 0.55, and must stay under ~10% of frame pixels.

| token | hex | use |
|---|---|---|
| `accent` | `#ffb77e` | warm accent, buttons |
| `berry` | `#c65fd1` | rare high-sat accent — sparingly, never on a background prop |
| `ink` | `#000000` | outlines |
| `ink-soft` | `#3f3026` | eyes |
| `brow` | `#6b5342` | brows — must NOT share the eye hex, or the distinction collapses |

`accent`'s shadow, `accent-deep`, is defined once, in the "Extended tokens" table below (§3,
generated from `_kit.py`) — it used to be duplicated here with a second, drifted value
(`#e08e52`); that row is gone, not just fixed, so it cannot drift again on its own.

### Layer 4 — fixed set dressing (bushes, shrubs)

A depth step **below** the interactive layer (TOCA §3.8: layer 4 sits at S 0.25–0.50,
V 0.55–0.90, layer 5 at V 0.50–0.97). A bush painted in `grass` / `grass-deep` dissolves
into a `grass` ground field. Use these instead — they still take a full black outline.

| token | hex | pair | S / V |
|---|---|---|---|
| `bush` | `#8ac96e` | with `bush-deep` | 0.453 / 0.788 |
| `bush-deep` | `#6ba851` | ΔV 0.129 | 0.518 / 0.659 |
| `bush-b` / `bush-b-deep` | `#96cf7e` / `#76b160` | ΔV 0.118 | variant B |
| `bush-c` / `bush-c-deep` | `#7fc164` / `#61a04a` | ΔV 0.129 | variant C |

### Prop variant bands

Instanced props are an instant tell (#22). Ship **three** of every prop: recolour
*within* the band **and** change at least one shape. These are the sanctioned bands.

| prop | A | B | C |
|---|---|---|---|
| grass | `#9ddb76` / `#79b85c` | `#a8de88` / `#86bd6b` | `#8fd472` / `#6faf55` |
| soil | `#c78956` / `#a57144` / `#dd9b68` / `#885f37` | `#ca8e57` / `#a87745` / `#e0a16a` / `#8b6339` | `#c38254` / `#a26c42` / `#d99467` / `#855936` |
| cloud-shade | `#c6d8e6` | `#cbdae4` | `#c0d5e8` |
| hill / hill-deep | `#d0edbe` / `#badea9` | `#c9ecc6` / `#b4ddb1` | `#d6ecb8` / `#c1dda8` |

### Narrative props

| token | hex | use |
|---|---|---|
| `soil-dark` | `#885f37` | deepest crumbs / the shaded far wall of a planting hollow — ΔV 0.114 from `soil-deep` |
| `ground-contact` | `#93d56c` | contact shadow on a `grass` field — ΔV 0.024, hard edge |
| `stone` | `#b8c2cc` | trowel blade, pebbles — tinted neutral, never `#808080` grey |
| `stone-deep` | `#9aa6b3` | shadow for `stone` (ΔV 0.098) |
| `stone-dark` | `#7f8b99` | ferrules, deep metal (ΔV 0.098 from `stone-deep`) |
| `worm` | `#f0a8a0` | worm body |
| `worm-deep` | `#d98f88` | shadow for `worm` (ΔV 0.090) |

**Contact shadows:** every object that sits on the ground gets one — hue-matched to the ground
green, ~2% value delta, hard edge. Without it everything floats.

**Shadow tones — use these, do not invent your own.** Several base tokens cannot reach the C4
ΔV 0.08–0.18 window on their own (`sun`→`sun-deep` is only ΔV 0.059; `cream` had no shadow at
all), so these were derived by the §3.4 rule — same hue family, slightly more saturated, value
dropped into the band. Coherence across 78 plants by ~10 authors depends on everyone using
the same shadows.

| token | hex | shadow for | ΔV |
|---|---|---|---|
| `grass-deep` | `#79b85c` | `grass` | 0.137 |
| `grass-dark` | `#6c9959` | `grass-deep` — a further/back-layer green, small pattern marks only | 0.122 |
| `soil-deep` | `#a57144` | `soil` | 0.133 |
| `soil-lite` | `#dd9b68` | lit crumbs of tilled soil (its own shadow is `soil`) | 0.087 |
| `sun-shade` | `#eebf62` | `sun` (body) | 0.067 |
| `ray-shade` | `#dbab58` | `sun-deep` (rays) | 0.082 |
| `cloud-shade` | `#c6d8e6` | `cream` — hue-rotated to 206°, because a cloud's shadow must go cool | 0.098 |

*(Note: `sun-shade`'s ΔV against the revised `sun` is only 0.067 — under the C4 0.08 floor, same
known exception as the pre-revision table. Accepted because the alternative is de-saturating `sun`
itself below the brief's own hex, which is fixed. Don't "fix" this by inventing a third yellow.)*

When a fill has no shadow token here, derive one the same way and **add it to this table** so the
next author reuses it rather than inventing a near-miss.

### Extended tokens (added during the Sep 2026 recolour pass)

The six pilot plants (`s-sunflower`, `a-apple-tree`, `m-maple-tree`, `b-butterfly-bush`,
`p-pizza-palm`, `u-ufo-tree`) needed hues the tables above don't cover — a lit canopy-face green,
red/orange accents for fruit and autumn leaves, tinted metal for the UFO saucers, a cool sky
shadow. These were out of band at S 0.60–0.77 under the old palette; all were pulled into S
0.38–0.60 (hue held, value lifted toward 0.85+) by the same §3.4 rule and are now locked. Reuse
these — do not re-derive your own near-miss for "a green," "a red," "a metal grey," etc.

| token | hex | shadow for / role | ΔV |
|---|---|---|---|
| `leaf` | `#c3f598` | lit green canopy face (shadow: `grass`) | 0.101 |
| `accent-deep` | `#e09863` | shadow for `accent` | 0.122 |
| `fruit` | `#d96a62` | red accent — apples, pepperoni (kept punchier: S 0.55, the top of the accent band) | — |
| `fruit-deep` | `#b8544e` | shadow for `fruit` | 0.129 |
| `ember` | `#d9876c` | autumn orange-red (maple canopy) | — |
| `ember-deep` | `#b86a53` | shadow for `ember` | 0.129 |
| `steel` | `#b8bcc8` | tinted metal — saucers, wings (already in band pre-revision, unchanged) | — |
| `steel-deep` | `#969cae` | shadow for `steel` (unchanged) | 0.102 |
| `steel-dark` | `#7f8697` | shadow for `steel-deep` — bolts, grille slots, deep metal | 0.090 |
| `sky-deep` | `#6cacd9` | shadow for `sky-hi` (UFO dome) | 0.150 |
| `cream-deep` | `#e8dcc4` | shadow for `cream` (already in band pre-revision, unchanged) | 0.090 |
| `beam` | `#ffeaa8` | flat light/glow shapes — tractor beams, halos (already in band, unchanged) | — |
| `berry-deep` | `#a44ead` | shadow for `berry` | 0.140 |

---

## 4. Technical gotchas (learned the hard way)

- **Chrome silently renders nothing** for `<use>` pointing at a `<g>` inside a `<clipPath>`.
  It produces a valid-looking file that is empty. **Always verify by decoding actual pixels**,
  never by file size or `hasAlpha`.
- Offset-union shading on a wide flat ellipse reads as an **extruded 3D slab** — exactly the
  look we're avoiding. Use a clipped hard-edged shadow shape instead.
- Rasterise at 2× then downsample for clean outline anti-aliasing.
- Keep the canvas and anchor point identical to the asset being replaced — the game positions
  by existing registration.

---

## 5. Definition of done for any art asset

- [ ] `.svg` master + `.png` raster committed together
- [ ] Pure-black outlines present, correct weight, round joins
- [ ] Two-tone form blocking, hard-edged
- [ ] Zero gradients/filters inside objects (verify by sampling a 100px run — constant RGB)
- [ ] Transparent background verified by decoding corner pixels
- [ ] Passes black-silhouette-at-25%
- [ ] At least one deliberate irregularity
- [ ] Palette drawn only from the token table
- [ ] You opened the PNG and looked at it
