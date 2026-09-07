# THE TOCA STANDARD
### A judgeable reference for children's-game visual craft, calibrated against Toca Boca's *Toca Life* series

**Version 1.0 — September 2026**
**Audience:** critic agents (scoring), builder agents (target), art direction (arbitration)

---

## 0. LEGAL & ETHICAL FRAME — READ FIRST, APPLIES TO EVERY USE OF THIS DOCUMENT

**We are matching a QUALITY BAR and a general aesthetic vocabulary.** That vocabulary — flat friendly vector art, warm harmonious palettes, expressive faces built from very few marks, chunky readable silhouettes, dense touchable set dressing, and constant playful micro-animation — is not ownable by anyone. It is the shared language of good children's illustration.

**We are NOT copying, tracing, referencing-into, or reproducing Toca Boca's specific characters, assets, logos, typefaces, scenes, UI layouts, or mascots.** Every asset in our game must be original work. No Toca character, no Toca prop, no Toca logo, no Toca colour token lifted verbatim as a "brand" colour, no recreation of a recognisable Toca room.

**Critics must judge CRAFT QUALITY, not similarity.** A critique that says "this doesn't look like Toca's character X" is an invalid critique and must be rewritten. Valid critiques name a craft failure: *value structure is muddy*, *outline weight is inconsistent*, *the idle animation is linear*, *the palette carries seven unrelated hues*. If a builder produced something that scores 10/10 on every category here and looks nothing like any Toca frame, that is a **pass** — and a good outcome.

**The one place similarity IS discussed** is the blind A/B protocol (§7.3), and even there the question is *"which frame is more appealing and more polished?"* — never *"which is closer to Toca?"*

---

## 1. HOW THIS DOCUMENT WAS BUILT — OBSERVED vs INFERRED

Everything in §3 (still-image attributes) is **OBSERVED**. It was measured by loading current *Toca Boca World* store screenshots into a canvas and reading actual pixels: colour histograms, saturation/value percentile distributions, hue-family distribution, run-length scans across characters and props to get outline widths and to test whether fills are flat or gradient. Numbers below are real measurements from those frames, not recollection. Where I estimate rather than measure (e.g. head-to-body ratio measured off a downscaled screenshot), it is marked **≈**.

Everything in §4 (animation) is **INFERRED / PRESCRIPTIVE**. Still frames cannot show timing. The millisecond values and easing curves there are *calibrated targets* — they describe the animation quality that reads as this-tier when built, derived from standard animation principles plus the tactile, never-static character of the reference work as described in design press. They are stated as hard numbers because vague animation advice is useless, **not** because they were extracted from a Toca binary. Builders should treat them as the spec; critics should score against them.

§5 (UI) is mixed: panel/button construction is **OBSERVED**; touch-target and typography guidance is **PRESCRIPTIVE** (partly observed, partly platform best practice).

Design-philosophy statements cited: Toca Boca uses "play designers" rather than game designers; teams run ≈6–8 people with one 2D artist; they deliberately keep things imperfect — *"there is still dirt in the corners, and there is always a weird, quirky element"*; they build animation mood boards to lock the *feel* before animating. (Motionographer, *The design process behind Toca Boca's infectious apps*, 2016.)

---

## 2. THE 10-SECOND GESTALT

Show a person a Toca frame for ten seconds. Four things land, in this order:

1. **It is bright, but it is not loud.** The whole frame lives in the upper value range — nearly every fill sits between 55% and 100% brightness — yet almost nothing is fully saturated. Measured on a classroom frame: median saturation **27%**, 75th percentile **47%**. Pure white is **1.0%** of pixels. The image feels *sunlit and washed*, not neon and not pastel-weak.

2. **Everything is a clean, chunky, closed shape.** No wisps, no thin lines, no gradients on objects, no fuzzy edges. Each thing is a solid flat colour inside a firm black contour. You could name every object in the frame from its silhouette alone at 20% size.

3. **The frame is packed with small stories.** A classroom is not "a classroom asset" — it is a chalkboard with actual half-finished maths on it, a shelf of mismatched binders, a rack of test tubes, a fern, a bin, a mug, a kid asleep on the desk. Density reads as *lived in*, and every single item looks like you could pick it up.

4. **The faces are almost nothing, and they are absolutely readable.** Two black shapes, a dot of a nose, one curve of a mouth, two soft cheeks. From those four marks you get delight, boredom, mischief, panic.

The emotional result is **warm, safe, funny, and touchable**. If a frame reads as *cold*, *slick*, *corporate*, *empty*, or *breakable*, it has already failed the gestalt test regardless of its category scores.

---

## 3. OBSERVABLE ATTRIBUTES

### 3.1 Colour

**Measured value distribution** (classroom interior, art region only, HSV *V* channel):

| percentile | V |
|---|---|
| 5th | 0.04 (outlines) |
| 25th | 0.59 |
| 50th | 0.86 |
| 75th | 0.96 |

**Measured saturation distribution** (HSV *S*):

| percentile | S |
|---|---|
| 25th | 0.06 |
| 50th | 0.27 |
| 75th | 0.47 |
| 95th | 0.80 |

**The rule this implies:** fills live at **V 0.55–0.97, S 0.05–0.55**, with a *small* number of accent shapes allowed up to S 0.80–0.85. Everything below V 0.40 in the frame is either an outline, an eye, or dark hair — **there are no dark mid-tone fills**. This is the single most load-bearing colour fact in the document. Muddy mid-value fills are the fastest way to look amateur.

**Hue count per scene.** Measured hue-family distribution of a classroom frame, 30° bins, as % of the art region:

- Warm (0–60°, red→amber→wood): **41.6%**
- Cyan/teal (150–180°): **9.0%**
- Blue/indigo (210–270°): **8.6%**
- *All other hue families combined: under 6%*

So: **one dominant warm family, two supporting cool families, and a scattering of accents.** That is three hue families doing 95% of the work. Not seven. Not "the rainbow." When a scene needs many colours (a character line-up, a wardrobe grid), the variety comes from **hue rotation inside a fixed S/V band**, so the crowd still reads as one family.

**Measured fills from a real classroom frame** (top of histogram):

| role | hex | note |
|---|---|---|
| wall / negative space | `#E8E8F0`, `#ECEEF2`, `#E6F5FB` | cool near-white, S 3–9%, **never `#FFFFFF`** |
| warm accent | `#F8E080` | soft butter yellow |
| wood / desk | `#F0D0B0` light, `#D08858` edge | 2-tone |
| skin (light) | `#F8BC97` | perfectly flat, measured zero variation across 30px |
| skin (deep) | `#C67C4C` | perfectly flat |
| chalkboard mint | `#78D8D0`, `#A0D0C8` | |
| neutral furniture | `#7D85A0` | desaturated blue-grey, flat across 100+px |
| deep accent | `#983018`, `#E04830` | the only high-sat colours in frame |
| hair | `#5E3512`, `#E14830`, `#282028` | flat |

**Near-white vs pure white.** Backgrounds and panels are *tinted* near-whites: `#E8E8F0` (cool), `#E6F5FB` (cyan-tinted), `#FFF4EF` and `#FEE8E0` (warm UI panels). Pure `#FFFFFF` appears at **1.0% of pixels** and is reserved for: sclera-free eye glints, tiny highlight chips, teeth, and UI icon glyphs. **A large pure-white area is an instant tell.**

**Shadow strategy.** Shadows are **tinted, low-contrast, and flat** — never grey, never black, never a blurred blob at 40% black. A shadow is the local surface colour rotated toward the scene's cool family and dropped ~8–15% in value, at 15–30% opacity, with a *hard or barely-softened* edge. On the pale-cyan character-creator floor, the ground under a figure sits at `#E2F6FD` against `#E6F5FB` — a **~2% value delta**. Contact shadows are a whisper, not a statement. Under-object occlusion (a book on a desk) is stronger but still hue-matched to the desk, not to black.

**Colour do-nots (measurable):**
- No fill with S > 0.85.
- No fill with V < 0.40 that isn't hair, an outline, or a deliberate deep accent covering < 2% of the frame.
- No `#808080`-family neutral greys. Neutrals are tinted: `#7D85A0`, `#B8B8C0`, `#889098`.
- No two adjacent large fills within ΔV 0.05 of each other unless separated by an outline.

---

### 3.2 Shape language

- **Everything is a closed, convex-biased blob.** Objects are built from a small number of large shapes, not many small ones. A backpack is 3 shapes. A microscope is 5. If a prop needs more than ~8 shapes to read, it's over-detailed for this style.
- **Corner radii are proportional, not uniform.** This matters and is routinely botched. A radius is chosen relative to the shape's short side — roughly **r ≈ 0.12–0.30 × short side** for soft objects, **r ≈ 0.05–0.10** for rigid/architectural things (lockers, door frames, tabletops). A 40px pencil case and a 400px wall do **not** share a 16px radius. Rigid things stay crisper; soft/organic things (hair, cushions, clouds, dough, fruit) round hard, often to a full semicircle.
- **Thickness / chunkiness.** No element in the composition should have a load-bearing dimension thinner than **≈1.5% of the frame height**. A chair leg, a lamp stem, a pencil — these get *fattened* well beyond real-world proportion so they survive at thumbnail size and read as grabbable. Measured example: desk legs are `#7D85A0` bars roughly 10px wide in a 739px-tall frame (1.4%), where a realistic leg would be 3px.
- **Silhouette readability.** The hard test: fill every object solid black at 25% scale. Each must still be identifiable and each must not merge with its neighbour. Overlapping objects are separated by a **negative-space gap of ≥ 2× the outline weight**, not by relying on colour difference.
- **Negative space.** Despite the density, there is always a calm band — the upper third of a wall, a run of floor, a plain sky. Density is *clustered*, not uniform. Roughly: 55–70% of the frame is objects, 30–45% is quiet field.
- **Banned:** hairline strokes, single-pixel details, tapering spikes, spindly antennae, engraved/etched texture, drop-shadow-defined edges, anything that disappears below 50% zoom.

---

### 3.3 Line & outline

**Yes — outlines, and they are pure black.** This was tested by run-length pixel scan and it is unambiguous: character contours read as `#000000` with 1–2px of antialiasing on each side. Not charcoal, not dark brown. Pure black.

| element | outline treatment |
|---|---|
| characters, held props, foreground interactables | **pure `#000000`**, uniform weight, no taper |
| mid-ground furniture (desks, shelves) | black, or a very dark hue-matched tone (`#683723` on wood, `#4E5C74` on cool metal) at the same weight |
| background architecture / wallpaper motifs | **outline drops out or becomes a tinted low-contrast line** — measured wallpaper motifs sit at ~4–8% contrast against the wall |
| UI icons | black, slightly lighter weight than character outlines |

**Weight.** Measured: core black run of **3–6px on a ~350px-tall character in a 1600px-wide frame**. That is **≈1.2–1.7% of the character's height**. Scale rule for builders:

> `outline_px = clamp(round(0.014 × object_height_px), 2, 8)`

Never below 2px at any display size — a 1px outline reads as a rendering artifact, not a drawing.

**Uniformity.** Weight is constant around a shape. No calligraphic swell, no line-weight hierarchy inside a single object. What *does* vary is weight **between depth layers** — foreground thicker, background thinner or absent. That is the only legal variation.

**Joins & caps are round.** Every corner of every stroke. There are no mitred spikes anywhere in the reference work.

**Internal contour lines.** Outlines are used *inside* shapes to define form — hair curls, a hoodie's sleeve seam, a jacket's lapel, a shoe's sole line. These are the same weight as the silhouette outline. This is the primary way form is communicated, and it is why gradients are unnecessary.

---

### 3.4 Shading

**Flat. Verified by pixel measurement.** A skin region measured `#F8BC97` for 30 consecutive pixels with zero variation. A furniture leg measured `#7D85A0` for 100+ consecutive pixels with zero variation. There is no gradient, no noise, no ambient occlusion, no bevel on any object.

Form is suggested by, in order of importance:

1. **Internal contour lines** (see above). This does most of the work.
2. **Two-tone flat blocking.** A form gets a *light face* and a *shadow face*, hard-edged, hue-shifted (shadow is cooler and slightly more saturated, not just darker). Value delta between the two is small: **ΔV 0.08–0.18**. Example measured on a UI button: face `#B8C8FF`, body `#989FE9`, rim `#6263D9` — three flat steps, no gradient anywhere.
3. **A single flat highlight chip.** A hard-edged parallelogram or lozenge of near-white on glass, plastic, and polished wood. It is a *shape*, not a gradient, and never uses a radial falloff.
4. **Blush.** Two soft, low-opacity ovals on the cheeks — the *only* place a soft edge is permitted on a character. Measured as a gentle 3–4px ramp from skin tone into a warm rose.

**The one legal gradient:** very broad, very low-contrast environment washes — a sky, a floor plane, a distant wall. Measured example: floor ramping `#E2F6FD → #FFFFFF` across ~70px. Contrast is so low it reads as air, not as rendering. **Rule: an environment gradient may span no less than 25% of the frame and may not exceed ΔV 0.10 end to end.** Any gradient on a discrete object is a failure.

**Absolutely absent:** specular hotspots with radial falloff, rim light, bloom, bevel-and-emboss, inner shadow, glossy plastic reflection, subsurface glow, drop shadows with Gaussian blur on props, "3D render" material response of any kind.

---

### 3.5 Faces & expressions

The construction, read directly off zoomed pixels:

- **Eyes:** solid black shapes, **no sclera, no iris, no pupil separation** in the default construction. Shape is a fat almond / rounded lozenge, slightly wider than tall, often tilted 5–15° inward for wryness or outward for innocence. Each eye is ≈ **8–14% of head width**; spacing between them ≈ 1.0–1.4 eye-widths. Eyes sit at or slightly **below** the vertical midpoint of the head — low eyes read younger.
- **Eye vocabulary (this is the expression engine):**
  | expression | eye form |
  |---|---|
  | neutral | filled almond |
  | happy / laughing | upward arc `^ ^`, stroke only, no fill body |
  | closed / content | downward-bowed line |
  | surprised | tall oval, sometimes with a tiny white glint chip |
  | sly / smug | almond with a flat top edge |
  | sad | almond with a downward-tilted top edge + slight droop of the brow |
  | dizzy / silly | spiral or X (used sparingly, as a gag) |
- **Eyebrows:** short, thick, rounded-rectangle strokes in a **hue-matched brown**, never black, never the hair colour exactly. Their *angle and vertical offset* carry more emotion than the eyes do. Brow can be omitted entirely on some characters.
- **Nose:** a tiny dot, short vertical tick, or small filled oval a few shades deeper than skin, **without an outline**. Frequently omitted. Never a nostril.
- **Mouth vocabulary:**
  - closed smile: a single curved stroke, round caps
  - open laugh: a filled black shape with a **cream/white teeth strip along the upper edge** and a small **coral/rose tongue shape** at the bottom (measured `#E14830`-family)
  - "o" of surprise: small filled oval
  - flat line: bored / deadpan
  - wavy line: unsure
  - one-corner-up: mischief
  That's six. Six is enough for an entire cast.
- **Cheeks:** soft rose ovals at 20–40% opacity. Present on most characters, always.
- **Freckles / marks:** 3–6 dots, one flat tone darker than skin. This is a personality lever that costs almost nothing.

**Expression range per character: minimum 6 distinct states.** A character that only ever wears one face is dead, and a critic must dock heavily for it. The six baseline states are: neutral, happy, laughing, surprised, sad, and mischievous. Add a game-specific seventh (thinking, sleeping, celebrating) if the mechanic needs it.

**Blink:** see §4.2 — non-negotiable.

**Emotion budget:** a full expression change should cost **at most 3 changed marks** (eyes, mouth, brows). If you need to redraw the head to change the mood, the face is over-designed.

---

### 3.6 Proportions & poses

- **Head is huge.** Measured on store frames: head including hair occupies **≈33–45%** of total standing height, i.e. the figure is **≈2.5–3 heads tall**. Never 5, never 7. The bigger the head, the younger and safer the read.
- **Torso is a soft rounded rectangle**, roughly as wide as the head, with almost no waist taper.
- **Limbs are simple tapered tubes with round caps.** No elbows, no knees, no joint articulation drawn.
- **Hands are mittens.** A rounded blob, sometimes with a thumb notch, never five fingers. Feet are a shoe blob.
- **Hair carries the identity.** Since the face is nearly uniform across a cast, silhouette differentiation is 70% hair, 20% clothing shape, 10% accessories (hat, glasses, headphones). Two characters with the same hair silhouette are a design failure.
- **Staging is orthographic-front / flat elevation.** Characters and props face the camera square-on. No 3/4 perspective on characters, no foreshortening. Interiors are drawn as a **dollhouse cutaway** — you look straight into the room, walls removed. Depth comes from layer stacking, never from vanishing-point perspective.
- **Poses are open and readable.** Arms out from the body, silhouette gaps preserved. Nothing crosses in front of the face. A pose that requires the viewer to untangle overlapping limbs is wrong for this style.
- **Diversity is structural, not decorative.** Skin tones span at least 5 distinct values across a cast (measured examples range `#F8BC97` → `#C67C4C` → deeper), and body shapes, hair textures, mobility aids, and glasses appear as ordinary variations, not as "the diverse character."

---

### 3.7 Props & set dressing

- **Density.** A room-scale scene carries **25–60 distinct, individually-authored props**. Not 8. Not a repeated tile. Measured on a classroom half-frame: chalkboard with hand-written equations and a doodle, a projector, a shelf of ~14 differently-coloured binders, a test-tube rack, a DNA model, a stack of exercise books, a plant, a wastebasket, a set of rulers, lockers with individual decals, a fire extinguisher, coats, four desks each with different clutter.
- **Every object is authored, not instanced.** If you can spot the same book asset three times, it fails. Variation is achieved by re-colouring within the palette band *and* changing at least one shape.
- **Objects tell stories.** A half-eaten sandwich. A stack of books with one falling. A drawing pinned crooked. Toca states this deliberately: *"things shouldn't be too perfect, there is still dirt in the corners, and there is always a weird, quirky element."* **Every scene must contain at least one deliberate oddity** — something slightly wrong, slightly funny, unexplained. This is a scoreable requirement, not a flourish.
- **"Everything looks touchable."** Props are sized generously, have real outlines, sit at a scale a child could imagine gripping, and read as separable from their background. Nothing is painted into the backdrop that a child might reasonably want to pick up.
- **Scale is playful, not accurate.** Objects that matter to play are drawn 20–50% larger than realistic proportion. Objects that are pure dressing shrink.

---

### 3.8 Composition & staging

**Layer stack (back to front), with the treatment each layer gets:**

| # | layer | outline | saturation | value |
|---|---|---|---|---|
| 1 | sky / far wall | none | S ≤ 0.12 | V 0.90–0.98 |
| 2 | distant scenery, wallpaper motif | tinted line at 4–8% contrast | S ≤ 0.20 | V 0.85–0.95 |
| 3 | room architecture (walls, floor, doors) | thin, hue-matched | S 0.10–0.30 | V 0.80–0.95 |
| 4 | furniture & fixed set dressing | black or near-black, standard weight | S 0.25–0.50 | V 0.55–0.90 |
| 5 | characters & interactive props | **pure black, full weight** | S 0.30–0.60, accents to 0.85 | V 0.50–0.97 |
| 6 | foreground framing (a plant edge, a desk corner) | pure black, +20% weight | any | often darker for framing |

This **atmospheric-perspective-by-outline** scheme is the mechanism that keeps a dense frame readable. It is the single most commonly missing thing in amateur work, which flattens everything to the same contrast and produces visual noise.

- **Characters sit on the lower 40% of the frame**, feet on a clear ground line, heads well clear of the top edge.
- **Focal hierarchy** comes from: (a) outline contrast, (b) local saturation spike — the most saturated shape in the frame is almost always on or near the focal character, (c) surrounding negative space.
- **Parallax:** in a scrolling or panning scene, layers 1–2 move at 0.15–0.35× camera speed, layer 3 at 0.6–0.8×, layers 4–6 at 1.0×, layer 6 optionally 1.05–1.15×. Static-parallax (all layers locked) is an instant tell.
- **Framing:** the composition is horizontal and stage-like. The reference series consistently uses a wide, side-on "stage" read rather than a dynamic diagonal camera.

---

### 3.9 Texture

**Essentially none, and this is measurable.** Flat fills measured *identical hex values* across 100-pixel runs. There is no film grain, no paper fibre, no halftone, no noise dither, no canvas overlay.

The only surface variation permitted:
- **Pattern as flat shape** — stripes, plaid, polka dots, camo, argyle drawn as discrete filled shapes with the same palette discipline as everything else. Observed extensively on clothing.
- **Hand-drawn irregularity in the linework itself.** Contours are not mathematically perfect; they have a faint hand-made wobble. This is the *only* "texture" in the style and it is what stops the art reading as clip-art.

If a critic sees a grain overlay, a paper texture, or a noise layer, that is a deviation and must be flagged — not because texture is bad, but because it is not this style, and it usually appears as a crutch to hide flat-colour boredom.

---

## 4. ANIMATION & FEEL
*(PRESCRIPTIVE — see §1. These are targets, calibrated to produce this tier of feel.)*

This is where most children's games lose 4 points. Static art of this quality still feels dead if nothing breathes.

### 4.1 The never-static rule

**At any given frame, at least 30% of the on-screen objects are in motion, and no interactive object is ever perfectly still for more than 400ms.** Motion may be almost imperceptible — that is fine, it must simply be non-zero. A frozen screen is the loudest amateur signal there is.

### 4.2 Idle motion

| behaviour | spec |
|---|---|
| **breathing** | `scaleY 1.00 → 1.018 → 1.00`, anchored at the feet; period **1.8–2.6s**, sine in-out. Pair with `scaleX 1.00 → 0.994` to conserve volume. |
| **sway** | rotation ±0.8–1.5°, period **2.4–3.6s**, offset from the breathing phase so they never sync |
| **blink** | close in **60ms**, hold **50–70ms**, open in **80ms**. Interval **randomised 2.4–6.0s**, never fixed. Occasional double-blink (12% chance). Every character in frame must have a **different random phase offset** — synchronised blinking across a crowd is uncanny and is an instant fail. |
| **hair / cloth / ears / plants** | secondary sway at **60–110ms lag** behind the body, amplitude 1.4–2× the body's |
| **ambient props** | anything plausibly loose gets its own loop: a hanging lamp swings 1.2°/4s, a plant leaf ticks, a clock hand steps, a poster corner flutters. Randomise phase per instance. |
| **idle "life beats"** | every **6–12s**, a random character performs a 500–900ms one-off: a head tilt, a look-away, a shoulder shrug, a foot tap. Never on a fixed timer. |

### 4.3 Tap / press response

The full press cycle, in order. Total duration **280–340ms**.

| phase | ms (cumulative) | transform | easing |
|---|---|---|---|
| **press-down (squash)** | 0 → 80 | `scale(1.11, 0.89)` | `cubic-bezier(0.33, 0, 0.67, 1)` |
| **release (stretch/overshoot)** | 80 → 190 | `scale(0.96, 1.05)` | `cubic-bezier(0.34, 1.56, 0.64, 1)` (back-out) |
| **settle** | 190 → 310 | `scale(1.00, 1.00)` | `cubic-bezier(0.22, 1, 0.36, 1)` (expo-out) |

Plus, on the same tap:
- A **rotation kick** of ±1.5–3° that returns over the settle phase.
- A **positional pop** of 2–5px upward on release.
- Volume conservation: squash and stretch must be **reciprocal** (`sx × sy ≈ 1.00 ± 0.02`). Uniform scaling on both axes is a tell — it reads as a zoom, not as a physical squash.
- **Anchor point matters:** press squashes from the *contact* side. Tap the top of an object, it squashes downward from the top.

Small UI buttons use a reduced version: squash to `(1.06, 0.94)` over 60ms, overshoot to `(0.98, 1.02)`, settle by 240ms.

### 4.4 Easing — named, with cubic-bezier

Use these. Nothing else.

| name | cubic-bezier | use |
|---|---|---|
| **backOut (the workhorse)** | `cubic-bezier(0.34, 1.56, 0.64, 1)` | anything appearing, landing, or being released |
| **expoOut** | `cubic-bezier(0.16, 1, 0.30, 1)` | screen transitions, panel slides, camera moves |
| **quintOut** | `cubic-bezier(0.22, 1, 0.36, 1)` | settles, drifts to rest |
| **backIn** | `cubic-bezier(0.36, 0, 0.66, -0.56)` | anticipation before a launch; exits |
| **sineInOut** | `cubic-bezier(0.37, 0, 0.63, 1)` | all looping idles — breathing, sway, bob |
| **elasticOut** | ~0.5s spring, 4–6 oscillations decaying to 0 | celebration pops only; use sparingly |
| **bounceOut** | staged multi-impact | objects landing on a surface |

**`linear` is banned** on every property except: continuous rotation of a genuinely constant-speed object (a fan, a wheel), and a scrolling background loop. Its appearance anywhere else is an automatic deduction.

**Never use `ease` (the CSS default) or `ease-in-out`.** They are symmetric and lifeless. Real motion is asymmetric — fast out, slow in.

### 4.5 Secondary motion & follow-through

- Anything attached to a moving body (hair, ponytail, bag, cape, ears, held object) **lags 60–120ms** and **overshoots by 15–25%** before settling.
- When an object stops, the **last thing to stop is the softest thing** — hair settles ~150ms after the head does.
- Stacked objects: when the bottom of a stack is disturbed, the disturbance propagates upward with **35–60ms per element**.
- When something is picked up, whatever it was resting on gets a **tiny relief bounce** (2–4px, 180ms, backOut).

### 4.6 Anticipation

Every action ≥400ms in duration gets an anticipation beat: a **counter-movement of 8–15% of the main move's amplitude, over 90–140ms, eased with backIn**, immediately before the action.

- Jump: crouch first.
- Throw: wind back first.
- Door opens: a 100ms shudder first.
- A big celebration: everything on screen **compresses slightly for 120ms** before the burst.

Skipping anticipation is the difference between "the object moved" and "the object decided to move."

### 4.7 Screen transitions

- Duration **380–460ms** — long enough to be enjoyed, short enough not to gate play.
- Never a plain crossfade. Use: a masked wipe with a shaped edge, a scale-and-fade where the outgoing screen shrinks to 0.94 while the incoming grows from 1.06, or a physical push with expoOut.
- The incoming screen's elements **stagger in**: 40–70ms between siblings, each with a backOut pop. A screen where all elements arrive on the same frame looks like a slideshow.
- The transition itself carries an animated character or motif — the mascot swipes across, a leaf sweeps past. The transition is content, not plumbing.

### 4.8 Particles & celebration vocabulary

Celebration is **layered**, never a single effect. A "correct answer" moment should stack 4–6 of these:

| element | spec |
|---|---|
| confetti / petals | **10–20** pieces (not 200), each a **flat shape from the scene palette**, 8–18px, initial velocity 300–500px/s upward-biased, gravity 900–1400px/s², rotation 180–540°/s, lifetime **700–1100ms**, fade only in the last 25% |
| sparkle pop | 4–7 four-point star shapes, scale `0 → 1.2 → 0` over 260–380ms, staggered 40ms |
| ring / burst | a single expanding outlined ring, `scale 0.2 → 1.6`, opacity `0.8 → 0`, 320ms expoOut |
| character reaction | expression change to "happy", plus a 2-hop bounce (jump 14px, 220ms each) |
| scale punch on the subject | to 1.14 over 120ms backOut, settle 240ms |
| environment reaction | 2–5 nearby background objects each do a 1-frame wobble, staggered 50ms |

**Particles must not be soft-glow sprites.** They are flat, outlined-or-not, palette-consistent shapes. Additive glow blobs are the #1 particle tell.

### 4.9 The "everything reacts" principle

**Every tap on any pixel produces a visible response within 100ms.** Including taps on things that "aren't interactive" — those get a small acknowledgement wobble (rotate ±2°, 200ms, backOut) rather than nothing. Nothing in the world is inert.

Beyond direct taps:
- Objects near an action react. A character walks past a plant → the plant sways.
- Sound and visual are simultaneous, not sequential.
- Long-press produces a *growing* anticipation (slow scale to 1.05 over 400ms) so the release has weight.
- A drag carries the object with **a 40–70ms follow lag and a 3–7° tilt in the direction of motion**, and it returns to level with backOut on drop.

---

## 5. UI STANDARDS

### 5.1 Buttons — construction (OBSERVED)

Measured from a real in-app circular button: **three flat tones, no gradient.**

| part | measured hex | relationship |
|---|---|---|
| top face | `#B8C8FF` | base |
| lower body / thickness | `#989FE9` | base darkened ~13% V, saturation +8% |
| rim / edge | `#6263D9` | base darkened ~35% V, saturation +40% |
| glyph | `#FFFFFF` | pure white, thick rounded strokes |

This produces a **physically chunky "pressable disc"** — it reads as having thickness because there is a visible lower band, not because of a bevel filter or a gradient.

**Rules:**
- Buttons are **circles or heavily-rounded rects** (`r ≥ 0.4 × height`; a pill is fine).
- The bottom rim is **6–10% of the button height** — this is the affordance. Press animation removes it (button moves down by exactly the rim height) so the button visibly *depresses*.
- No soft drop shadow. If separation from the background is needed, use a **flat offset shape** in a darker tint of the same hue at 100% opacity, offset 3–6px down.
- Minimum diameter **88px @1x** for a primary action; nothing tappable is smaller than **64px**.
- Spacing between adjacent touch targets ≥ **16px**.

### 5.2 Iconography

- Glyphs are **solid white or solid black filled shapes**, not line icons with thin strokes.
- Stroke-based glyphs use a weight of **≥ 8% of the icon's box** with round caps and joins.
- Icons are **objects, not abstractions**, wherever possible: a scissors for cut, an actual paint tube for colour, a real bell for sound. Abstract glyphs (hamburger, gear, chevron) are used only where a child already knows them from other apps.
- Icons in a grid keep their **full art treatment** — observed clothing icons in the wardrobe grid are miniature versions of the actual assets, with outlines and patterns intact, sitting on plain white circles. They are not simplified into monochrome pictograms.

### 5.3 Panels & modals

- Panel grounds are **warm tinted near-whites**: measured `#FFF4EF` (header) over `#FEE8E0` (body). Never `#FFFFFF`, never grey.
- Corner radius on panels: **20–32px** at a 1080p-class layout.
- A modal enters with a **scale from 0.88 with backOut over 320ms** plus the scrim fading in over 200ms. It exits faster (220ms, backIn) — exits are always quicker than entrances.
- Scrim is a **tinted dark of the scene's dominant hue at 35–50% opacity**, never `rgba(0,0,0,0.5)`.
- Content inside a panel staggers in at 45ms intervals.
- Modals are **rare**. The reference work almost never blocks play with a dialog. Prefer in-world feedback.

### 5.4 Typography

- **One display face, heavy and geometric-rounded.** Weight 700–800. Terminals are rounded. Reference frames use a rounded geometric sans in bold — think of the class of faces with circular bowls, generous apertures, and no sharp terminals.
- **Optical size is large:** headline text occupies roughly **5–7% of frame height**. There is no small text anywhere.
- **Letter-spacing is slightly negative** on the display face (−0.5 to −1.5%) so words read as a single chunky shape.
- **Never more than 2 sizes on a screen**, and never more than one face.
- Text colour is a **near-black tinted toward the panel hue** (e.g. `#2B2A33` on a lavender panel), not `#000000`, and not grey.

### 5.5 Avoiding text for pre-readers

This is a hard requirement for the 3–7 audience.

- **All primary affordances are pictorial.** No button relies on a word.
- **Instruction is demonstrated, not stated:** a ghosted hand animates the gesture; a target object pulses; a trail shows the path. Loop the hint after **4–6s of inactivity**, and again every 8s, escalating in obviousness.
- **State is shown by the object itself**, not a label: a plant that is watered looks watered.
- **Numbers are represented as countable objects** (three stars, five seeds), not digits, wherever the mechanic allows.
- **Voice-over may support but never carry** — the visual must work with sound off.
- Where a word is unavoidable (a title, a name), pair it with an icon of the same meaning.

---

## 6. INSTANT TELLS — THE AMATEUR / PRO GAP

A blunt checklist. Each of these, alone, marks a frame as sub-standard. Critics: scan this list first; it is the fastest path to an accurate score.

1. **Anything on screen is perfectly static.** No breathing, no sway, no blink. Dead frame.
2. **`linear` easing** on a scale, position, rotation, or opacity tween.
3. **Symmetric easing** (`ease-in-out`, or the CSS `ease` default) used as the house curve.
4. **Uniform scale on tap** (`scale(1.1)` on both axes) instead of reciprocal squash-and-stretch.
5. **Pure black shadows** — `rgba(0,0,0,0.4)`, grey drop shadows, or blurred black blobs under objects.
6. **Large pure-`#FFFFFF` fields.** Backgrounds and panels must be tinted near-whites.
7. **Uniform corner radius applied globally** — the same 12px on a button, a wall, a fruit, and a card. Radius must scale with the shape.
8. **Gradients on discrete objects.** Any linear or radial gradient inside a prop, a character, or a button.
9. **Gloss / specular highlights with radial falloff** — the "3D render" look. Highlights must be flat hard-edged shapes.
10. **Bevel, emboss, inner shadow, or outer glow** anywhere.
11. **Thin fiddly detail** — 1px lines, hairline chair legs, spindly antennae, tiny sub-shapes that vanish at 50% zoom.
12. **Inconsistent outline weight** within a depth layer, or tapering/calligraphic strokes.
13. **No depth layering** — background, midground, and foreground all at the same outline weight and saturation, producing visual noise.
14. **Mitred stroke joins.** Corners must be round.
15. **Too many hues.** More than ~4 hue families doing meaningful work in one scene.
16. **Muddy mid-values.** Fills sitting at V 0.35–0.55 that aren't a deliberate accent. The palette should be top-heavy.
17. **Over-saturation.** Any fill above S 0.85, or more than ~10% of the frame above S 0.60.
18. **Small heads.** A 4+ head-tall character in a game for under-8s.
19. **Faces with a single expression** across the whole game, or a cast where every character wears the identical face.
20. **Synchronised blinking / synchronised idles** across multiple characters. Every loop needs a random phase offset.
21. **Empty set dressing** — a "classroom" that is a wall, a desk, and a chalkboard. Density is the point.
22. **Instanced props** — the same book, plant, or chair recognisably repeated with no re-colour or shape variation.
23. **A perfectly tidy scene.** No oddity, no dirt in the corners, nothing quirky or slightly wrong.
24. **Soft-glow additive particles**, lens flares, or a 200-particle confetti dump.
25. **A single-effect celebration** — one particle burst with no character reaction, no scale punch, no environment response.
26. **No anticipation** before a large motion.
27. **Text-dependent UI** for a pre-reader audience, or text below ~4% of frame height.
28. **Crossfade screen transitions** with no stagger and no motif.
29. **Locked parallax** — all layers moving at camera speed.
30. **Taps on non-interactive areas produce nothing.** Everything must acknowledge.

---

## 7. THE SCORING RUBRIC

### 7.1 Instrument

Ten categories. Each scored **1–10, integers only**. Score the artefact in front of you, not its intent.

---

#### **C1 — Palette discipline & harmony**
*Are the hues few, the values top-heavy, the saturation restrained, the whites tinted, the shadows coloured?*

- **3** — 6+ unrelated hues; saturation all over the map; large pure-`#FFFFFF` areas; grey or black shadows; muddy mid-value fills. Colours were chosen one at a time.
- **6** — Recognisable palette, mostly harmonious, but 1–2 colours fight the scheme; some fills sit in the muddy V 0.35–0.55 band; whites are pure; shadows are neutral grey.
- **9–10** — 3–4 hue families, one clearly dominant and warm. Fills measurably in V 0.55–0.97 / S 0.05–0.55 with a small number of high-sat accents. All whites tinted. All shadows hue-derived from their surface. The frame could be recoloured from a token file.

#### **C2 — Shape language & silhouette**
*Chunky, closed, readable, proportional radii, no fiddly detail.*

- **3** — Thin elements, spiky joins, one global corner radius, objects that dissolve at 50% zoom, overlapping shapes that merge.
- **6** — Generally chunky and readable, but some elements are too thin, radii are applied mechanically, and a couple of silhouettes are ambiguous.
- **9–10** — Every object passes the black-silhouette-at-25% test. Radii scale with shape size and material. Nothing thinner than 1.5% of frame height. Negative-space gaps preserved at every overlap. Shape count per object is minimal.

#### **C3 — Line quality & outline system**
*Weight, uniformity, round joins, depth-based variation.*

- **3** — No outlines, or 1px outlines, or wildly inconsistent weight, or mitred spikes, or outlines applied uniformly to every depth layer.
- **6** — Consistent outlines present and correctly round-joined, but weight doesn't vary across depth layers, or is slightly off-scale (too thin to read, or so thick it eats the fill).
- **9–10** — Weight ≈1.2–1.7% of object height, clamped ≥2px. Pure black on the interactive layer, hue-matched and thinner on midground, dropped or low-contrast in the background. Internal contour lines do real form work. Faint hand-made irregularity, not a mathematical stroke.

#### **C4 — Shading & material honesty**
*Flat fills, two-tone blocking, flat highlight chips, no render artifacts.*

- **3** — Gradients on objects, gloss with radial falloff, bevels, drop shadows with Gaussian blur, a "3D render" material read.
- **6** — Mostly flat, but a gradient or two sneaks onto props, or the light/shadow value delta is too large (harsh) or too small (invisible), or highlights are soft-edged.
- **9–10** — Object fills measurably flat (identical hex across the fill). Two-tone blocking with ΔV 0.08–0.18 and a cool hue-shift in shadow. Highlights are hard-edged shapes. At most one broad environment wash, ≤ΔV 0.10 across ≥25% of frame.

#### **C5 — Face construction & expression range**
*Minimal marks, maximum emotion, ≥6 states, correct eye/mouth vocabulary.*

- **3** — One expression per character; over-rendered eyes (iris, sclera, gradient, eyelashes) that still convey nothing; identical face across the cast; no blush; no blink.
- **6** — 3–4 expressions exist and read, construction is broadly right, but the range is narrow, the mouth vocabulary is thin, or expressions cost a full head redraw.
- **9–10** — ≥6 distinct, instantly-readable states per character. Each state changes ≤3 marks. Eye and mouth vocabularies are systematic and reusable across the cast. Brow angle carries emotion. Blush present. Blink implemented with randomised, per-character phase.

#### **C6 — Proportion, pose & staging**
*Head ratio, mitten hands, open poses, flat elevation, cast differentiation.*

- **3** — Realistic 5–7 head proportions; articulated fingers; tangled overlapping poses; inconsistent perspective; a cast that reads as one character in different shirts.
- **6** — Correct chunky proportions but stiff, repetitive posing, or a cast whose silhouettes are too similar, or inconsistent camera treatment between assets.
- **9–10** — 2.5–3 heads tall. Mitten hands, tube limbs, soft torso. Poses open and legible with clear negative space. Consistent flat-elevation staging. Every cast member distinguishable by hair/shape silhouette alone. Diversity is structural.

#### **C7 — Set dressing density & storytelling**
*Prop count, authored variety, narrative detail, the deliberate oddity.*

- **3** — Sparse; a handful of generic props; obvious instancing; nothing implies a life happened here.
- **6** — Reasonably furnished, but props are decorative rather than narrative, some assets are visibly repeated, and the scene is too tidy.
- **9–10** — 25–60 individually-authored props at room scale. Multiple items imply an off-screen story (half-eaten food, a knocked-over cup, a crooked drawing). At least one deliberate oddity per scene. Everything reads as pick-up-able.

#### **C8 — Composition, depth & focal hierarchy**
*Layer stack, atmospheric-perspective-by-outline, parallax, where the eye goes.*

- **3** — Flat pile of objects at uniform contrast; no clear layers; focal point ambiguous; character floating or cropped awkwardly.
- **6** — Layers exist and are distinguishable, but background competes with foreground, or the focal hierarchy relies only on centring, or parallax is absent in a scrolling scene.
- **9–10** — Six-layer discipline with outline weight, saturation, and value stepping cleanly back. Focal character carries the frame's saturation peak and its widest negative-space margin. Parallax speeds tiered as specified. A calm band balances the dense clusters.

#### **C9 — Animation: idle life & the never-static rule**
*Breathing, sway, blink cadence, secondary motion, ambient loops, life beats.*

- **3** — Static, or a single looping animation with linear easing, or everything animating in lockstep.
- **6** — Idles exist on the main characters with correct easing, but props and background are static, phases are synchronised, or there is no secondary motion on hair/cloth.
- **9–10** — ≥30% of on-screen objects in motion at any instant. Breathing at 1.8–2.6s sine, sway offset in phase, blinks randomised 2.4–6.0s per character with independent offsets, secondary motion lagging 60–120ms with 15–25% overshoot, ambient prop loops with randomised phase, and periodic one-off life beats.

#### **C10 — Animation: response, timing & juice**
*Tap squash/stretch, easing curves, anticipation, transitions, celebration layering, everything-reacts.*

- **3** — No press feedback, or an instant state swap, or uniform-scale pop with linear/default easing. Celebrations are a single effect or absent. Screen changes are cuts or crossfades.
- **6** — Press feedback exists with a decent curve and some overshoot, but volume isn't conserved, anticipation is missing, transitions are plain, celebrations are one-layered, and non-interactive taps do nothing.
- **9–10** — Full 280–340ms press cycle with reciprocal squash-and-stretch, rotation kick and positional pop. Named easing curves used correctly, `linear` absent. Anticipation on every ≥400ms action. Transitions 380–460ms with staggered entry and a motif. Celebrations stack 4–6 layers with flat palette-consistent particles. Every tap anywhere gets a ≤100ms acknowledgement.

---

### 7.2 Hard rules

> **PASS THRESHOLD: every category must score ≥7.**
>
> **Any category scoring ≤6 fails the piece.** It goes back to the builder. There is no averaging, no "but the total is 78/100," no trading a 9 in colour against a 5 in animation. One weak category is what a player notices.
>
> The critic's return must contain, per failing category: **(a) the score, (b) the specific observable that caused it, quoted in the doc's own vocabulary, (c) the concrete change that would raise it to 8.** "Feels off" is not a finding. "Outline weight on the midground furniture matches the character layer, collapsing depth separation — drop midground outlines to ~60% weight and hue-match them to the wood tone" is a finding.
>
> **Also record:** the highest-scoring category (so the builder doesn't regress it) and the total, for trend tracking only.

**Automatic caps, regardless of other observations:**

| condition | cap |
|---|---|
| any `linear` easing on a visible tween | C10 ≤ 4 |
| any fully static interactive screen | C9 ≤ 2 |
| pure black or grey drop shadows | C1 ≤ 5 |
| gradient on a discrete object | C4 ≤ 5 |
| synchronised blinks across characters | C9 ≤ 5 |
| primary affordance depends on reading a word | C-UI note + overall FAIL for a pre-reader audience |

### 7.3 Blind A/B protocol

Run this **after** the numeric pass, on every review cycle. It catches the failure mode where a piece satisfies every rule and still isn't charming.

1. Render our frame at the target aspect ratio. Place it beside **one genuine reference frame** from the *Toca Life* series, at identical size, on a neutral `#F2F2F0` ground, unlabelled and in randomised left/right order.
2. Look at the pair for **five seconds only**. Then answer one question:

   > **Which frame is more appealing and more polished?**

   Not "which is more Toca." Not "which is more original." Appeal and polish only.
3. **If ours wins or it's a genuine tie:** record the result, note what carried it, ship the review.
4. **If ours loses:** you must name **the single biggest gap in exactly one sentence**, in this form:

   > `BIGGEST GAP: <the one observable difference that decided it>.`

   One sentence. One gap. Not a list. The discipline of choosing forces you to identify what actually decided the comparison rather than cataloguing everything. Examples of well-formed answers:
   - *BIGGEST GAP: their frame has three depth layers stepping back in outline weight and saturation while ours renders every object at identical contrast, so ours reads as noise.*
   - *BIGGEST GAP: their characters' faces change shape between marks while ours wear one fixed expression, so ours reads as a sticker sheet.*
   - *BIGGEST GAP: their scene is full of small authored oddities and ours is a tidy inventory of correct objects.*
5. Feed that one sentence to the builder as the headline task for the next cycle, above the numeric findings.

**Reference-frame handling note:** reference frames are for side-by-side *judgement* only. They are never handed to a builder as source material, never traced, never sampled for assets. The output of the A/B is one sentence of English, not an image.

---

## 8. BUILDER QUICK CARD

Pin this. Everything below is derived from the sections above.

**Colour**
- Fills: `V 0.55–0.97`, `S 0.05–0.55`; accents to `S 0.85` on <10% of frame
- 3–4 hue families max; one dominant, warm
- Whites are tinted (`#E8E8F0`, `#E6F5FB`, `#FFF4EF`) — never `#FFFFFF` at scale
- Shadows = surface hue, cooler, −8–15% V, 15–30% opacity, hard edge
- No fill in `V 0.35–0.55` unless it's a deliberate accent

**Shape & line**
- `outline_px = clamp(round(0.014 × object_height_px), 2, 8)`, round joins, no taper
- Pure `#000000` on the interactive layer; hue-matched + thinner on midground; dropped in background
- Nothing thinner than 1.5% of frame height
- `radius ≈ 0.12–0.30 × short side` (soft) / `0.05–0.10` (rigid)

**Shading**
- Object fills 100% flat
- Two-tone blocking at ΔV 0.08–0.18, shadow hue-shifted cooler
- Highlights are hard-edged shapes
- One environment wash max, ≤ΔV 0.10, ≥25% of frame

**Character**
- 2.5–3 heads tall; mitten hands; tube limbs
- Eyes: solid black almond, 8–14% of head width, at/below head midline
- ≥6 expressions, each ≤3 changed marks
- Blush always; brows hue-matched brown, never black

**Motion**
- Breathe: `scaleY 1.00↔1.018`, 1.8–2.6s, sineInOut, foot-anchored
- Blink: 60ms close / 60ms hold / 80ms open, interval random 2.4–6.0s, per-character phase
- Tap: squash `(1.11, 0.89)` @80ms → overshoot `(0.96, 1.05)` @190ms → settle @310ms
- Default curve: `cubic-bezier(0.34, 1.56, 0.64, 1)`
- Transitions 380–460ms with 40–70ms sibling stagger
- Celebration = 4–6 stacked layers, 10–20 flat palette-consistent particles
- `linear` is banned
- Every tap anywhere gets a response within 100ms

**Scene**
- 25–60 authored props at room scale, no visible instancing
- ≥1 deliberate oddity per scene
- Six-layer depth stack with outline/saturation/value stepping
- Characters in the lower 40%, feet on a ground line

---

## 9. SOURCES

Visual measurements taken from current *Toca Boca World* store imagery (Google Play listing, `com.tocaboca.tocalifeworld`), September 2026 — including classroom, retail, outdoor, character-creator, and outfit-designer frames — analysed by pixel sampling (colour histograms, HSV percentile distributions, hue-family binning, run-length scans for outline weight and fill flatness).

Design-philosophy context:
- [The design process behind Toca Boca's infectious apps — Motionographer](https://motionographer.com/2016/04/27/the-design-process-behind-toca-bocas-infectious-apps/)
- [Toca Boca dishes on gender-neutrality and design — Kidscreen](https://kidscreen.com/2014/10/30/toca-boca-dishes-on-gender-neutrality-and-design/)
- [Defining Diversity at Toca Boca — Designing for Children's Rights](https://d4cr.org/cases/toca-boca)
- [Toca Life: School — Common Sense Media review](https://www.commonsensemedia.org/app-reviews/toca-life-school)
- [Toca Boca World — Google Play listing](https://play.google.com/store/apps/details?id=com.tocaboca.tocalifeworld)

*Toca Boca and Toca Life are trademarks of Toca Boca AB. This document references them for comparative quality benchmarking only. No assets, characters, or protected expression are reproduced, derived from, or intended to be imitated.*
