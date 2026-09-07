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

| token | hex | use |
|---|---|---|
| `grass` | `#7ec850` | meadow base |
| `grass-deep` | `#5da23c` | grass shadow tone |
| `grass-dark` | `#4a8531` | far grass / deep shadow |
| `sky-hi` | `#8fd3ff` | sky top |
| `sky-lo` | `#cdefff` | sky horizon |
| `soil` | `#a9713f` | dirt base |
| `soil-deep` | `#8a5a33` | dirt shadow |
| `cream` | `#fff7e6` | panels, near-white |
| `sun` | `#ffd23f` | sun, highlights |
| `sun-deep` | `#f0b429` | sun shadow tone |
| `accent` | `#ff9d52` | warm accent, buttons |
| `berry` | `#c65fd1` | rare high-sat accent |
| `ink` | `#000000` | outlines |
| `ink-soft` | `#3f3026` | eyes, text |

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
