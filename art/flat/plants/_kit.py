#!/usr/bin/env python3
"""ALPHABET GARDEN — SHARED PLANT KIT (the style bible, in code).

Import this from every plant-builder script:

    import sys, os
    sys.path.insert(0, os.path.dirname(__file__))
    from _kit import *

Everything here is the *vocabulary* 78 plants are drawn from: palette tokens,
leaf silhouettes, trunk/stem treatments, branches, a rectilinear/mechanical
set, the parameterised ground anchor, the face rig, the outline ladder and
the two-tone shading recipe.  Read `KIT.md` for the prose version.

DESIGN RULE OF THIS FILE (added after the fan-out gate failed):
    A primitive with a baked-in default *shape* profile is a plant-cloning
    machine.  `canopy_blob` used to carry module-level `jit`/`bul` defaults
    and `_root_pts` was a fixed 7-point foot; apple and maple therefore
    measured 0.929 silhouette IoU.  Every shape-defining knob below is now a
    REQUIRED per-plant argument.  If a call fails with a TypeError, that is
    the kit refusing to let you ship the same plant twice.

Binding docs: ../../../docs/TOCA_STANDARD.md, ../../../docs/FLAT_ART_BRIEF.md
"""
import math

# =====================================================================
# CANVAS CONTRACT
# =====================================================================
W = H = 1024                # every plant is 1024x1024 transparent PNG
BASE_Y = 1000               # trunk/stem meets the soil here (+-6px)
TOP_Y = 120                 # top of the subject (=> object height ~880 = 86%)
OBJ_H = BASE_Y - TOP_Y      # 880
CX = 512                    # nominal centre; DO NOT centre everything exactly

# =====================================================================
# PALETTE
# Core tokens are verbatim from FLAT_ART_BRIEF Sec 3.  The EXTENDED block
# is derived by the documented rule in KIT.md Sec 2 and is now part of the
# locked palette -- do not invent hexes outside these two blocks.
# =====================================================================
# --- core (FLAT_ART_BRIEF Sec 3 -- REVISED palette, post S-0.63 audit) -
GRASS       = "#9ddb76"   # grass            (was #7ec850)
GRASS_DEEP  = "#79b85c"   # grass-deep       (was #5da23c)
GRASS_DARK  = "#6c9959"   # grass-dark       (was #4a8531; derived back-layer green)
SKY_HI      = "#8fd3ff"   # sky-hi           (unchanged -- already in band)
SKY_LO      = "#cdefff"   # sky-lo           (unchanged -- already in band)
SOIL        = "#c2946b"   # soil             (was #a9713f)
SOIL_DEEP   = "#a37855"   # soil-deep        (was #8a5a33)
CREAM       = "#fff7e6"   # cream            (unchanged)
SUN         = "#ffe07a"   # sun              (was #ffd23f)
SUN_DEEP    = "#f0c665"   # sun-deep         (was #f0b429)
ACCENT      = "#ffb77e"   # accent           (was #ff9d52; brief's revised value)
BERRY       = "#c65fd1"   # berry            (unchanged -- rare high-sat accent)
INK         = "#000000"   # ink
INK_SOFT    = "#3f3026"   # ink-soft         (eyes)
BROW        = "#6b5342"   # brow             (brows must not share the eye hex)

# --- extended (derived; see KIT.md Sec 2 / FLAT_ART_BRIEF Sec 3) -----
LEAF        = "#c3f598"   # leaf         lit green face   (shadow: GRASS)
SUN_SHADE   = "#eebf62"   # sun-shade    shadow for SUN        dV 0.067
                          #   (was #eebf5c, S 0.613 -- desaturated to S 0.588
                          #    so a sunflower alone does not breach S0.60/10%)
RAY_SHADE   = "#dbab58"   # ray-shade    shadow for SUN_DEEP   dV 0.082
ACCENT_DEEP = "#e09863"   # accent-deep  shadow for ACCENT     dV 0.122
FRUIT       = "#d96a62"   # fruit        red accent (apples, pepperoni)
FRUIT_DEEP  = "#b8544e"   # fruit-deep   shadow for FRUIT      dV 0.129
                          #   (was #b85149, S 0.603 -- desaturated to S 0.576)
EMBER       = "#d9876c"   # ember        autumn orange-red
EMBER_DEEP  = "#b86a53"   # ember-deep   shadow for EMBER      dV 0.130
STEEL       = "#b8bcc8"   # steel        tinted metal (saucers, panels, wings)
STEEL_DEEP  = "#969cae"   # steel-deep   shadow for STEEL      dV 0.102
STEEL_DARK  = "#7f8697"   # steel-dark   bolts, grille slots, deep metal dV 0.098
SKY_DEEP    = "#6cacd9"   # sky-deep     shadow for SKY_HI     dV 0.150
BARK_LITE   = "#dbad7f"   # bark-lite / soil-lite  lit bark face (shadow: SOIL)
CREAM_DEEP  = "#e8dcc4"   # cream-deep   shadow for CREAM      dV 0.090
BEAM        = "#ffeaa8"   # beam         light/glow shapes, flat
BERRY_DEEP  = "#a44ead"   # berry-deep   shadow for BERRY      dV 0.140

# base -> shadow pairing table.  ALWAYS take a shadow from here.
SHADE = {
    GRASS: GRASS_DEEP, GRASS_DEEP: GRASS_DARK, LEAF: GRASS,
    SOIL: SOIL_DEEP, BARK_LITE: SOIL,
    SUN: SUN_SHADE, SUN_DEEP: RAY_SHADE,
    ACCENT: ACCENT_DEEP, FRUIT: FRUIT_DEEP, EMBER: EMBER_DEEP,
    STEEL: STEEL_DEEP, STEEL_DEEP: STEEL_DARK,
    SKY_HI: SKY_DEEP, CREAM: CREAM_DEEP,
    BERRY: BERRY_DEEP, BEAM: SUN,
}

# =====================================================================
# OUTLINE LADDER  (TOCA 3.3; object height ~880px on a 1024 canvas)
# One weight per role, NOT per shape.
#
# The ladder is DELIBERATELY COMPRESSED.  The game renders a plant at
# 128x150 css px -- an 8:1 downscale -- so a 7px stroke lands at 0.87px and
# ghosts out.  11px is the floor at which a line still survives that
# downscale (1.37px), and 1.7% of an 880px object is the ceiling from
# FLAT_ART_BRIEF Sec 2.  That leaves exactly 11..15; we use 11/12/13, which
# keeps every weight inside 1.25%-1.48%.  There is no thinner rung, and
# there must never be one: "make it thinner" is not available as a way to
# de-emphasise, only colour and layer order are.
# =====================================================================
OL_MAIN = 13   # 1.48% -- silhouette + primary masses (canopy, trunk, slabs)
OL_PROP = 12   # 1.36% -- attached props 90-190px (apples, butterflies, bars)
OL_FINE = 11   # 1.25% -- props under 90px + internal detail. THE FLOOR.
OL_BG   = 10   # background/atmospheric layer ONLY, hue-matched not black

OL_FLOOR = 11  # nothing a player must see may be stroked thinner than this

RJ = 'stroke-linejoin="round" stroke-linecap="round"'


def ol_for(short_side):
    """Outline weight for a prop, capped so it can never eat its own shape."""
    return max(OL_FINE, min(OL_MAIN, int(round(0.16 * short_side))))


# =====================================================================
# GEOMETRY HELPERS
# =====================================================================
def smooth_closed(pts):
    """Catmull-Rom -> closed cubic bezier through pts. Hand-drawn wobble.

    ORGANIC ONLY.  If the thing you are drawing has a machined edge, use
    `poly()` / `hard_poly()` / `slab()` instead -- see Sec 'RECTILINEAR'.
    """
    n = len(pts)
    d = "M%.1f,%.1f" % pts[0]
    for i in range(n):
        p0, p1 = pts[(i - 1) % n], pts[i]
        p2, p3 = pts[(i + 1) % n], pts[(i + 2) % n]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6.0, p1[1] + (p2[1] - p0[1]) / 6.0)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6.0, p2[1] - (p3[1] - p1[1]) / 6.0)
        d += " C%.1f,%.1f %.1f,%.1f %.1f,%.1f" % (c1 + c2 + p2)
    return d + " Z"


def smooth_open(pts):
    """Catmull-Rom bezier chain (no leading M, no Z)."""
    n = len(pts)
    d = ""
    for i in range(n - 1):
        p0 = pts[max(i - 1, 0)]
        p1, p2 = pts[i], pts[i + 1]
        p3 = pts[min(i + 2, n - 1)]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6.0, p1[1] + (p2[1] - p0[1]) / 6.0)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6.0, p2[1] - (p3[1] - p1[1]) / 6.0)
        d += " C%.1f,%.1f %.1f,%.1f %.1f,%.1f" % (c1 + c2 + p2)
    return d


def rot(px, py, cx, cy, deg):
    a = math.radians(deg)
    dx, dy = px - cx, py - cy
    return (cx + dx * math.cos(a) - dy * math.sin(a),
            cy + dx * math.sin(a) + dy * math.cos(a))


def place(pts, cx, cy, deg=0.0, sx=1.0, sy=None):
    """Scale about origin, rotate, translate a local point list."""
    sy = sx if sy is None else sy
    out = []
    a = math.radians(deg)
    for x, y in pts:
        x, y = x * sx, y * sy
        out.append((cx + x * math.cos(a) - y * math.sin(a),
                    cy + x * math.sin(a) + y * math.cos(a)))
    return out


def jitter(seed, n, amp=0.08, base=1.0):
    """n deterministic values around `base`, +-amp. The house wobble source.

    Deterministic per seed so a plant renders identically every build, but
    different for every seed -- which is the whole point: pass a different
    seed per plant and the shapes stop being the same shape.
    """
    out = []
    for i in range(n):
        t = math.sin((i + 1) * 12.9898 + seed * 78.233) * 43758.5453
        out.append(base + amp * (2.0 * (t - math.floor(t)) - 1.0))
    return tuple(out)


def spread(seed, n, lo, hi):
    """n deterministic values in [lo, hi]. Bulge depths, slot widths, etc."""
    return tuple(lo + (hi - lo) * v for v in jitter(seed, n, 0.5, 0.5))


def bite(cx, cy, r):
    """Caterpillar nibble: a sub-path circle removed with fill-rule=evenodd.

    MUST sit FULLY INSIDE the parent shape.  A circle that straddles the
    edge does NOT produce a bite -- under evenodd the part lying outside the
    parent has winding 1 and renders as a solid filled lune stuck to the
    silhouette.  For a true edge bite, push a point of the shape's own
    outline inward instead (canopy_blob(notch=i) does exactly that).
    """
    return ("M%.1f,%.1f A%.1f,%.1f 0 1 0 %.1f,%.1f "
            "A%.1f,%.1f 0 1 0 %.1f,%.1f Z"
            % (cx - r, cy, r, r, cx + r, cy, r, r, cx - r, cy))


# =====================================================================
# SHADING RECIPE  (TOCA 3.4 / BRIEF Sec 2)
# Light is ALWAYS from the upper-left, on every one of the 78 plants.
# The shadow face is therefore the lower-right ~35% of every mass.
# =====================================================================
def sweep(cx, cy, rx, ry, lo=0.34, hi=-0.36, wob=0.07, seed=0.0):
    """Region below a wavy line that RISES left->right (light upper-left)."""
    x0, x1 = cx - rx * 1.7, cx + rx * 1.7
    pts, n = [], 7
    for i in range(n + 1):
        t = i / float(n)
        pts.append((x0 + (x1 - x0) * t,
                    cy + ry * (lo + (hi - lo) * t)
                    + ry * wob * math.sin(t * 6.3 + seed)))
    d = "M%.1f,%.1f" % pts[0] + smooth_open(pts)
    d += " L%.1f,%.1f L%.1f,%.1f Z" % (x1, cy + ry * 3.0, x0, cy + ry * 3.0)
    return d


def sweep_hard(cx, cy, rx, ry, lo=0.30, hi=-0.34):
    """The MACHINED shadow: a straight-edged sweep, no wobble at all.

    Use on slabs, panels, bars, hulls -- anything with a manufactured edge.
    A hand-wavy shadow line inside a crisp rectangle is the tell that the
    author only had organic tools.
    """
    x0, x1 = cx - rx * 1.7, cx + rx * 1.7
    return ("M%.1f,%.1f L%.1f,%.1f L%.1f,%.1f L%.1f,%.1f Z"
            % (x0, cy + ry * lo, x1, cy + ry * hi,
               x1, cy + ry * 3.0, x0, cy + ry * 3.0))


def chip(cx, cy, r, deg=-28):
    """The one legal highlight: a flat, hard-edged lozenge. Never a radial."""
    pts = [(-r, -r * 0.42), (-r * 0.3, -r * 0.62), (r * 0.72, -r * 0.30),
           (r, r * 0.30), (r * 0.24, r * 0.60), (-r * 0.74, r * 0.34)]
    return smooth_closed(place(pts, cx, cy, deg))


# =====================================================================
# LEAF VOCABULARY  (5 silhouettes; all return a path `d`)
# Local design space: leaf points UP, base at origin, length L, width Wd.
# =====================================================================
def leaf_round(cx, cy, L, Wd, deg=0.0, curl=0.10):
    """Broad ovate leaf with a soft tip. Bushes, canopies, generic foliage."""
    k = curl * Wd
    p = [(0, 0), (-Wd * 0.46 + k, -L * 0.22), (-Wd * 0.50 + k, -L * 0.58),
         (-Wd * 0.22 + k, -L * 0.93), (0 + k * 1.3, -L),
         (Wd * 0.26 + k, -L * 0.92), (Wd * 0.50 + k, -L * 0.56),
         (Wd * 0.44 + k, -L * 0.20)]
    return smooth_closed(place(p, cx, cy, deg))


def leaf_pointed(cx, cy, L, Wd, deg=0.0, curl=0.16):
    """Lance / almond leaf, pointed both ends. Sunflower, stem leaves."""
    k = curl * Wd
    p = [(0, 0), (-Wd * 0.34 + k * 0.4, -L * 0.20),
         (-Wd * 0.50 + k, -L * 0.52), (-Wd * 0.28 + k * 1.5, -L * 0.86),
         (k * 2.0, -L), (Wd * 0.30 + k * 1.4, -L * 0.84),
         (Wd * 0.50 + k, -L * 0.50), (Wd * 0.32 + k * 0.4, -L * 0.18)]
    return smooth_closed(place(p, cx, cy, deg))


def leaf_lobed(cx, cy, L, deg=0.0, jit=(1.0, 0.94, 1.06, 0.97, 1.02)):
    """5-lobe maple leaf, centred on (cx, cy), L = radius to the top lobe.

    Lobes are given SHOULDER points at +-13 deg so each tip stays fat: a
    maple leaf drawn from tips alone becomes a spiky asterisk that vanishes
    at game size.  Notches are shallow (0.36-0.42 of L) for the same reason.
    """
    tips = [(-103, .64), (-50, .90), (0, 1.00), (52, .88), (102, .62)]
    notch = [(-78, .38), (-26, .42), (26, .40), (78, .36)]
    seq = [(-153, .16)]
    for i, (a, r) in enumerate(tips):
        k = jit[i % len(jit)]
        seq += [(a - 13, r * k * .82), (a, r * k), (a + 13, r * k * .82)]
        if i < len(notch):
            seq.append(notch[i])
    seq += [(153, .16), (180, .30)]                 # petiole nub
    pts = []
    for a, r in seq:
        rad = math.radians(a - 90.0)                # 0 deg == straight up
        pts.append((L * r * math.cos(rad), L * r * math.sin(rad)))
    return smooth_closed(place(pts, cx, cy, deg))


def leaf_frond(cx, cy, L, Wd, deg=0.0, bend=0.34):
    """Palm frond: a fat curved paddle with a scalloped trailing edge."""
    b = bend * L
    p = [(0, 0), (-Wd * 0.30, -L * 0.26), (-Wd * 0.52 + b * 0.3, -L * 0.56),
         (-Wd * 0.44 + b * 0.7, -L * 0.84), (b * 0.95, -L),
         (Wd * 0.30 + b * 0.9, -L * 0.86), (Wd * 0.56 + b * 0.5, -L * 0.60),
         (Wd * 0.46 + b * 0.15, -L * 0.30), (Wd * 0.22, -L * 0.06)]
    return smooth_closed(place(p, cx, cy, deg))


def leaf_blade(bx, by, tx, ty, hw, tw, bend):
    """Grass blade: fat base, round tip, one-sided bend."""
    h = by - ty
    return ("M%.1f,%.1f C%.1f,%.1f %.1f,%.1f %.1f,%.1f "
            "A%.1f,%.1f 0 0 1 %.1f,%.1f "
            "C%.1f,%.1f %.1f,%.1f %.1f,%.1f Z") % (
        bx - hw, by,
        bx - hw + bend * 0.30, by - h * 0.46,
        tx - tw - bend * 0.10, ty + h * 0.34, tx - tw, ty,
        tw, tw, tx + tw, ty,
        tx + tw + bend * 0.10, ty + h * 0.34,
        bx + hw + bend * 0.30, by - h * 0.46, bx + hw, by)


def canopy_blob(cx, cy, rx, ry, n, jit, bul, start=-96, notch=None):
    """A lobed foliage mass: n unequal scallops around an ellipse.

    `n`, `jit` and `bul` are REQUIRED.  They used to be module-level
    defaults, which is exactly why apple / maple / butterfly-bush measured
    0.93 / 0.78 / 0.76 silhouette IoU -- three plants wearing one mass.
    Get them from `lobe_profile(seed, n, ...)`, one seed per plant.

    `notch` = index of one edge pushed INWARD (a bitten leaf / oddity).
    """
    pts = []
    for i in range(n):
        a = math.radians(start + 360.0 * i / n)
        k = jit[i % len(jit)]
        pts.append((cx + rx * k * math.cos(a), cy + ry * k * math.sin(a)))
    d = "M%.1f,%.1f" % pts[0]
    for i in range(n):
        p1, p2 = pts[i], pts[(i + 1) % n]
        dx, dy = p2[0] - p1[0], p2[1] - p1[1]
        L = math.hypot(dx, dy) or 1.0
        nx, ny = dy / L, -dx / L
        mx, my = (p1[0] + p2[0]) / 2.0, (p1[1] + p2[1]) / 2.0
        if (mx - cx) * nx + (my - cy) * ny < 0:
            nx, ny = -nx, -ny
        b = bul[i % len(bul)]
        if notch is not None and i == notch:
            b = -abs(b) * 0.42
        d += " Q%.1f,%.1f %.1f,%.1f" % (mx + nx * b, my + ny * b, p2[0], p2[1])
    return d + " Z"


def lobe_profile(seed, n, jit=0.08, bul=(34, 72)):
    """(jit, bul) for `canopy_blob`, derived from ONE per-plant seed.

        JIT, BUL = lobe_profile(seed=41.7, n=11, jit=0.09, bul=(30, 78))
        canopy_blob(cx, cy, rx, ry, 11, JIT, BUL)

    Raise `jit` for a raggedy mass, lower it for a tight ball; widen `bul`
    for deep, uneven scallops.  Two plants with different seeds cannot
    produce the same silhouette by accident.
    """
    j = jitter(seed, n, jit, 1.0)
    b = spread(seed * 1.618 + 3.0, n, bul[0], bul[1])
    return j, b


def star4(cx, cy, r, deg=0.0, waist=0.30):
    """Four-point sparkle. Chunky waist so it survives the 25% silhouette."""
    p = []
    for i in range(4):
        a = math.radians(90 * i)
        b = math.radians(90 * i + 45)
        k = 1.0 if i != 1 else 0.88          # never a perfect star
        p.append((r * k * math.cos(a), r * k * math.sin(a)))
        p.append((r * waist * math.cos(b), r * waist * math.sin(b)))
    return smooth_closed(place(p, cx, cy, deg))


def fruit_blob(cx, cy, r, deg=0.0):
    """Apple/berry silhouette: round with a dimpled crown and a fat cheek."""
    p = [(0, -r * 0.66), (r * 0.54, -r * 0.92), (r * 1.00, -r * 0.26),
         (r * 0.84, r * 0.62), (r * 0.28, r * 1.00), (-r * 0.36, r * 0.96),
         (-r * 0.90, r * 0.54), (-r * 1.02, -r * 0.24), (-r * 0.50, -r * 0.94)]
    return smooth_closed(place(p, cx, cy, deg))


def vein(cx, cy, L, deg=0.0, frac=0.72):
    """Midrib contour line for a leaf. Same weight as its parent's outline."""
    p = [(0, -L * 0.06), (0, -L * frac)]
    q = place(p, cx, cy, deg)
    return "M%.1f,%.1f L%.1f,%.1f" % (q[0] + q[1])


# =====================================================================
# RIBBON / BRANCH / LIMB VOCABULARY
# The kit's answer to "every tree is a column plus a blob".  A ribbon is a
# tapered band swept along a spine; a branch, a horn, a crescent tube and a
# segmented arm are all the same primitive with different width profiles.
# =====================================================================
def bow(x0, y0, x1, y1, k=0.22, n=6):
    """A spine polyline from A to B, bowed sideways by k*length.

    Positive k bows to the LEFT of the A->B direction. Use a different k per
    limb so a fork never looks like a mirrored Y.
    """
    dx, dy = x1 - x0, y1 - y0
    L = math.hypot(dx, dy) or 1.0
    nx, ny = -dy / L, dx / L
    pts = []
    for i in range(n):
        t = i / float(n - 1)
        s = math.sin(math.pi * t)           # 0 at both ends, 1 in the middle
        pts.append((x0 + dx * t + nx * k * L * s,
                    y0 + dy * t + ny * k * L * s))
    return pts


def ribbon(spine, widths, cap0="flat", cap1="round"):
    """Closed path: a band along `spine` whose full width is `widths[i]`.

    `widths` may be a list (one per spine point) or a single number.
    Caps: "flat" (square-ish butt), "round" (semicircular), "point" (tapers
    to a single point -- use for horns, thorns, spikes).
    """
    n = len(spine)
    if not isinstance(widths, (list, tuple)):
        widths = [widths] * n
    nor = []
    for i in range(n):
        a = spine[max(i - 1, 0)]
        b = spine[min(i + 1, n - 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy) or 1.0
        nor.append((-dy / L, dx / L))
    left, right = [], []
    for i, (px, py) in enumerate(spine):
        h = widths[i] * 0.5
        nx, ny = nor[i]
        left.append((px + nx * h, py + ny * h))
        right.append((px - nx * h, py - ny * h))
    if cap1 == "point":
        left, right = left[:-1], right[:-1]
        tip = spine[-1]
    d = "M%.1f,%.1f" % left[0] + smooth_open(left)
    if cap1 == "point":
        d += " L%.1f,%.1f" % tip
    elif cap1 == "round":
        # sweep-flag 0: the cap must bulge FORWARD along the spine. With
        # flag 1 the arc doubles back and bites a notch out of every tip --
        # it showed up on maple limbs, mallet handles and banana leaves.
        r = widths[-1] * 0.5
        d += " A%.1f,%.1f 0 0 0 %.1f,%.1f" % (r, r, right[-1][0], right[-1][1])
    else:
        d += " L%.1f,%.1f" % right[-1]
    rr = list(reversed(right))
    d += smooth_open(rr)
    if cap0 == "round":
        r = widths[0] * 0.5
        d += " A%.1f,%.1f 0 0 0 %.1f,%.1f" % (r, r, left[0][0], left[0][1])
    return d + " Z"


def branch(x0, y0, x1, y1, w0, w1, k=0.20, n=6, cap="round"):
    """A tapered limb from the trunk (w0) out to a tip (w1). THE branch.

    A tree without this is a column with a blob on top, forever.  Draw the
    limbs BEFORE the foliage clusters so the clusters cover the tips, and
    give each limb its own `k` so the fork is never mirrored.
    """
    sp = bow(x0, y0, x1, y1, k, n)
    ws = [w0 + (w1 - w0) * (i / float(n - 1)) ** 0.85 for i in range(n)]
    return ribbon(sp, ws, cap0="flat", cap1=cap)


def horn(cx, cy, L, w, deg=0.0, k=0.16):
    """Tapered horn / thorn / tusk / spike. Fat rounded base, real point."""
    a = math.radians(deg - 90.0)
    sp = bow(cx, cy, cx + L * math.cos(a), cy + L * math.sin(a), k, 6)
    ws = [w * (1.0 - (i / 5.0) ** 1.35) for i in range(6)]
    return ribbon(sp, ws, cap0="round", cap1="point")


def crescent(cx, cy, L, w, deg=0.0, arc=0.34, waist=0.55):
    """Curved tube, fat in the middle, rounded at both ends. A BANANA.

    Not a leaf, not a blob: the one shape a foliage kit cannot make.  `arc`
    is how far it bends; `waist` how thin the ends get relative to `w`.
    """
    a = math.radians(deg - 90.0)
    sp = bow(cx, cy, cx + L * math.cos(a), cy + L * math.sin(a), arc, 7)
    ws = [w * (waist + (1.0 - waist) * math.sin(math.pi * (i / 6.0)) ** 0.6)
          for i in range(7)]
    return ribbon(sp, ws, cap0="round", cap1="round")


# =====================================================================
# RECTILINEAR / MECHANICAL VOCABULARY
# The opt-out of `smooth_closed`.  Robots, xylophones, burgers, saucers,
# escalators, firetrucks -- roughly a fifth of the 78 -- are unbuildable
# out of scallops.  Corner radii here follow TOCA 3.2: r = 0.05-0.10 of the
# SHORT SIDE for rigid things (soft things round to 0.12-0.30).
# =====================================================================
def poly(pts, close=True):
    """Exact straight-line path. No smoothing, no wobble. Hard edges."""
    d = "M%.1f,%.1f" % pts[0]
    for p in pts[1:]:
        d += " L%.1f,%.1f" % p
    return d + (" Z" if close else "")


def hard_poly(pts, r):
    """Polygon with ROUNDED CORNERS but perfectly straight edges.

    `r` is a scalar or one radius per vertex; each is clamped to half the
    shorter adjacent edge so a corner can never swallow its own side.  This
    is the machined counterpart of `smooth_closed` -- edges stay dead
    straight, only the corners soften, which is what makes a panel read as
    manufactured rather than grown.
    """
    n = len(pts)
    if not isinstance(r, (list, tuple)):
        r = [r] * n
    d = ""
    for i in range(n):
        p0, p1, p2 = pts[(i - 1) % n], pts[i], pts[(i + 1) % n]
        v0 = (p0[0] - p1[0], p0[1] - p1[1])
        v1 = (p2[0] - p1[0], p2[1] - p1[1])
        l0 = math.hypot(*v0) or 1.0
        l1 = math.hypot(*v1) or 1.0
        rr = min(r[i], l0 * 0.5, l1 * 0.5)
        a = (p1[0] + v0[0] / l0 * rr, p1[1] + v0[1] / l0 * rr)
        b = (p1[0] + v1[0] / l1 * rr, p1[1] + v1[1] / l1 * rr)
        d += ("M%.1f,%.1f" % a) if i == 0 else (" L%.1f,%.1f" % a)
        d += " Q%.1f,%.1f %.1f,%.1f" % (p1[0], p1[1], b[0], b[1])
    return d + " Z"


def slab(cx, cy, w, h, r=0.08, deg=0.0, skew=0.0):
    """Rigid rounded rectangle. THE mechanical mass primitive.

    `r` is a FRACTION of the short side (0.05-0.10 rigid, up to 0.30 soft).
    `skew` tapers the top edge in by that fraction of w -- a slab with a
    slightly narrower top reads as a moulded part, not as clip-art.
    """
    hw, hh = w * 0.5, h * 0.5
    t = hw * (1.0 - skew)
    p = place([(-t, -hh), (t, -hh), (hw, hh), (-hw, hh)], cx, cy, deg)
    return hard_poly(p, r * min(w, h))


def panel(cx, cy, w, h, r=0.08, deg=0.0, inset=0.16, skew=0.0):
    """(outer, inner) -- a slab with a recessed face plate inside it.

    Draw `outer` with `Doc.form`, then stroke `inner` as a contour line.
    Two lines of code, and a mass stops being a blob and becomes a machine.
    """
    return (slab(cx, cy, w, h, r, deg, skew),
            slab(cx, cy, w * (1 - inset), h * (1 - inset * 1.25),
                 r * 1.2, deg))


def bolt(cx, cy, r, deg=0.0):
    """(head, slot) -- a rivet/bolt head plus its screw slot.

    Fill `head` in the panel's own shadow tone, stroke `slot` at OL_FINE.
    Bolts are how a flat panel gets a scale reference.  Never fewer than 2,
    never in a perfect square -- offset one.
    """
    head = hard_poly(place([(-r, -r * .72), (-r * .18, -r), (r * .78, -r * .62),
                            (r, r * .22), (r * .34, r), (-r * .66, r * .78)],
                           cx, cy, deg), r * 0.34)
    q = place([(-r * .52, 0), (r * .52, 0)], cx, cy, deg + 24)
    return head, "M%.1f,%.1f L%.1f,%.1f" % (q[0] + q[1])


def grille(cx, cy, w, h, n, deg=0.0, gap=0.42):
    """n vertical slots in a face plate -- a speaker/vent grille.

    Returns a list of slot paths.  Slot width is derived so the slots never
    fall under the 11px floor; if they would, `n` is reduced.
    """
    while n > 1 and (w / float(n)) * (1 - gap) < OL_FLOOR + 4:
        n -= 1
    pitch = w / float(n)
    sw = pitch * (1 - gap)
    out = []
    for i in range(n):
        x = cx - w * 0.5 + pitch * (i + 0.5)
        kh = h * (1.0 - 0.10 * abs(i - (n - 1) / 2.0) / max(n, 1))
        p = place([(x - cx, -kh * .5), (x - cx + sw, -kh * .5),
                   (x - cx + sw, kh * .5), (x - cx, kh * .5)], cx, cy, deg)
        out.append(hard_poly(p, sw * 0.42))
    return out


def graduated(n, a, b, curve=1.0):
    """n values from a to b. `curve`>1 back-loads, <1 front-loads.

    The non-organic repetition primitive: xylophone bar lengths, escalator
    steps, ladder rungs, gumball rows, a row of windows.
    """
    return [a + (b - a) * ((i / float(n - 1)) ** curve) for i in range(n)]


def plinth(cx, y_base, w, h, r=0.06, feet=2):
    """A machined base plate -- the RECTILINEAR ground anchor.

    Root lobes are wrong on a robot.  This is what a manufactured plant
    stands on: a wide slab with `feet` square pads under it, bottom edge on
    y_base.  Returns (plate, [pad, ...]).
    """
    plate = hard_poly([(cx - w * .5, y_base - h), (cx + w * .5, y_base - h),
                       (cx + w * .46, y_base - h * .18),
                       (cx - w * .48, y_base - h * .18)], r * w)
    pads = []
    for i in range(feet):
        t = (i + .5) / feet
        px = cx - w * .40 + w * .80 * t
        pw = w * (0.22 if i % 2 else 0.26)
        pads.append(hard_poly([(px - pw * .5, y_base - h * .34),
                               (px + pw * .5, y_base - h * .34),
                               (px + pw * .44, y_base),
                               (px - pw * .46, y_base)], pw * 0.16))
    return plate, pads


# =====================================================================
# TRUNK / STEM VOCABULARY + THE GROUND ANCHOR
# `root_seed` is REQUIRED on both organic trunks.  One fixed 7-point foot
# across 78 plants is Instant Tell #22 by construction; five of the six
# pilots shared it verbatim before this change.
# =====================================================================
def root_pts(cx, wb, y_base, seed, lobes=3, spread_k=1.06, depth=(16, 30)):
    """`lobes` unequal root lobes, deliberately not mirrored. Left->right.

    Notches stay SHALLOW (16-30px by default) -- deeper reads as claws or
    trouser legs at game size, the loudest defect of pilot v1.  A plant that
    WANTS claws (a xylophone tree's splayed foot) passes depth=(40, 80) and
    lobes=4, and owns that decision.
    """
    n = lobes * 2 + 1
    xs = jitter(seed, n, 0.10, 1.0)
    ds = spread(seed + 5.0, n, depth[0], depth[1])
    pts = []
    for i in range(n):
        t = -1.0 + 2.0 * i / float(n - 1)
        x = cx + wb * spread_k * t * xs[i]
        y = y_base - (ds[i] if i % 2 == 0 else 2 + ds[i] * 0.12)
        pts.append((x, y))
    return pts


_root_pts = root_pts          # legacy alias; new code should use root_pts


def stem_slim(cx, y_top, y_base, w, *, root_seed, lean=18.0, w_base=None,
              root_lobes=3, root_depth=(16, 30)):
    """Treatment 1 -- slim stem. Flowers, small plants. w >= 40px (3.9%).

    `root_seed` is KEYWORD-ONLY on purpose. It used to be the 5th positional
    argument, one slot after `lean` -- an author writing `stem_slim(cx, top,
    base, w, 0)` meaning "lean=0" was silently setting the foot seed instead,
    and `lean` fell back to its 18.0 default unnoticed. Two plants written
    that way emit a byte-identical foot path. Passing it positionally now
    raises TypeError instead of shipping a shared-ground-foot regression.
    """
    wb = (w_base or w * 1.9) * 0.5
    hw = w * 0.5
    hgt = y_base - y_top
    left = [(cx - hw + lean, y_top),
            (cx - hw * 1.06 + lean * 0.55, y_top + hgt * 0.34),
            (cx - hw * 1.14, y_top + hgt * 0.66),
            (cx - wb * 0.86, y_base - 62)]
    right = [(cx + wb * 0.90, y_base - 58),
             (cx + hw * 1.16, y_top + hgt * 0.64),
             (cx + hw * 1.02 + lean * 0.5, y_top + hgt * 0.32),
             (cx + hw + lean, y_top)]
    return smooth_closed(left
                         + root_pts(cx, wb, y_base, root_seed, root_lobes,
                                    depth=root_depth)
                         + right)


def trunk_chunky(cx, y_top, y_base, w_top, w_base, *, root_seed, lean=0.0,
                 root_lobes=3, root_depth=(16, 30), flare=1.0):
    """Treatment 2 -- chunky flared trunk. Trees. Buttressed, not a cylinder.

    `flare` scales how hard the shaft splays into the foot: 0.8 = a slim
    upright pole, 1.4 = a broad buttressed base.

    `root_seed` is KEYWORD-ONLY -- see `stem_slim`'s docstring for why. It
    used to be the 6th positional argument, the slot right after `lean`;
    a positional `lean=0.0` silently became the foot seed instead. Two
    plants both written `trunk_chunky(..., 0)` produced a byte-identical
    root path before this guard existed.
    """
    ht, hb = w_top * 0.5, w_base * 0.5
    hgt = y_base - y_top
    left = [(cx - ht + lean, y_top),
            (cx - ht * 1.10 + lean * 0.6, y_top + hgt * 0.26),
            (cx - ht * 1.34 * flare, y_top + hgt * 0.55),
            (cx - hb * 0.84 * flare, y_base - 76)]
    right = [(cx + hb * 0.88 * flare, y_base - 70),
             (cx + ht * 1.28 * flare, y_top + hgt * 0.58),
             (cx + ht * 1.16 + lean * 0.5, y_top + hgt * 0.28),
             (cx + ht + lean, y_top)]
    return smooth_closed(left
                         + root_pts(cx, hb, y_base, root_seed, root_lobes,
                                    depth=root_depth)
                         + right)


def lozenge(cx, cy, hw, hh, deg=0.0):
    """One squat segment. Building block of the palm trunk."""
    p = [(-hw * 0.97, -hh * 0.50), (-hw * 0.70, -hh), (0, -hh * 0.93),
         (hw * 0.72, -hh * 0.98), (hw * 0.99, -hh * 0.46),
         (hw * 0.95, hh * 0.52), (hw * 0.64, hh), (0, hh * 0.97),
         (-hw * 0.68, hh * 0.99), (-hw * 0.98, hh * 0.48)]
    return smooth_closed(place(p, cx, cy, deg))


def trunk_palm(cx, y_top, y_base, hw_top, hw_base, n=7,
               wob=(0, 5, -4, 6, -3, 4, -6, 3)):
    """Treatment 3 -- segmented palm. Returns [(path, hw, cy)] TOP FIRST so
    the caller paints top->bottom and each lower ring overlaps the one above.
    The bottom ring IS the ground anchor."""
    out = []
    span = y_base - y_top
    hh = span / (n * 1.72)
    for i in range(n):
        t = i / float(n - 1)
        cy = y_top + hh * 1.16 + (span - 2 * hh * 1.16) * t
        hw = hw_top + (hw_base - hw_top) * (t ** 1.25)
        out.append((lozenge(cx + wob[i % len(wob)], cy, hw, hh * 1.16,
                            deg=(-1.6 if i % 2 else 1.4)), hw, cy))
    return out


def trunk_stack(cx, y_top, y_base, w_top, w_base, n, r=0.10, seed=0.0):
    """Treatment 4 -- a MACHINED segmented column (robot spine, drainpipe).

    Rigid counterpart of `trunk_palm`: hard-cornered slabs with collar rings
    between them, so a mechanical plant does not have to borrow a palm.
    Returns [(slab_d, w, cy, h)] TOP FIRST.
    """
    out = []
    span = y_base - y_top
    seg = span / float(n)
    wob = jitter(seed, n, 0.05, 1.0)
    for i in range(n):
        t = i / float(max(n - 1, 1))
        cy = y_top + seg * (i + 0.5)
        w = (w_top + (w_base - w_top) * (t ** 1.15)) * wob[i]
        h = seg * (1.02 if i % 2 else 0.96)
        out.append((slab(cx, cy, w, h, r, 0.0, 0.06 if i % 2 else 0.0),
                    w, cy, h))
    return out


# =====================================================================
# THE FACE SYSTEM
# Designed in a 200-unit-wide box, origin at the face centre, then
# translate+scale onto the plant.  s ~= face_width_px / 200.
# Every expression = eyes(1 mark) + mouth(1 mark) [+ brows(1 mark)] <= 3.
# Blush lives OUTSIDE the swappable group -- it is always on.
#
# Emitted ids are stable and NESTED:
#   face-<kind>  ->  face-<kind>-eyes , face-<kind>-mouth [, -brows]
# plus a standalone `face-blink` lid group, so the runtime can either swap
# whole expressions OR blink on top of the current one.
# =====================================================================
EXPRESSIONS = ("neutral", "happy", "delighted", "sleepy", "surprised",
               "mischief", "blink")

EYES_DEFAULT = ((-46, -14), (48, -18))    # deliberately unequal
EYE_R_DEFAULT = (19, 26)
MOUTH_DEFAULT = (2, 44)

# ~30 of the 78 plants wear a face.  If they all wear THIS face, that is
# Instant Tell #19.  Move the anchors, change the eye radius, shift the
# mouth -- the rig is parameterised so you have no excuse not to.
FACE_MIN, FACE_MAX = 0.45, 0.60      # face width as a fraction of its mass


def _eye(kind, kx, ky, side):
    """One eye, drawn about the origin, pre-scaled by (kx, ky).

    `side` = -1 left / +1 right; the two are never identical.
    """
    k = 1.0 if side < 0 else 0.95
    tilt = -7 if side < 0 else 6

    def S(x, y):
        return (x * kx * k, y * ky * k)
    if kind == "neutral":
        rx, ry = S(19, 26)
        return ('<ellipse cx="0" cy="0" rx="%.1f" ry="%.1f" fill="%s" '
                'transform="rotate(%d)"/>' % (rx, ry, INK_SOFT, tilt))
    if kind in ("happy", "delighted"):
        a, b, c = S(-24, 8), S(0, -30), S(23, 6)
        return ('<path d="M%.1f,%.1f Q%.1f,%.1f %.1f,%.1f" fill="none" '
                'stroke="%s" stroke-width="%.1f" %s/>'
                % (a[0], a[1], b[0], b[1], c[0], c[1], INK_SOFT,
                   15 * ky * k, RJ))
    if kind == "sleepy":
        a, b, c = S(-24, -8), S(0, 18), S(23, -10)
        return ('<path d="M%.1f,%.1f Q%.1f,%.1f %.1f,%.1f" fill="none" '
                'stroke="%s" stroke-width="%.1f" %s/>'
                % (a[0], a[1], b[0], b[1], c[0], c[1], INK_SOFT,
                   15 * ky * k, RJ))
    if kind == "blink":
        # A CLOSED LID: near-flat, a hair of upward bow, no brow. Reads as a
        # blink, not as the droopy sleepy lid.
        a, b, c = S(-26, 2), S(0, -6), S(25, 1)
        return ('<path d="M%.1f,%.1f Q%.1f,%.1f %.1f,%.1f" fill="none" '
                'stroke="%s" stroke-width="%.1f" %s/>'
                % (a[0], a[1], b[0], b[1], c[0], c[1], INK_SOFT,
                   16 * ky * k, RJ))
    if kind == "surprised":
        rx, ry = S(22, 31)
        gx, gy = S(-7, -12)
        return ('<ellipse cx="0" cy="0" rx="%.1f" ry="%.1f" fill="%s"/>'
                '<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="%s"/>'
                % (rx, ry, INK_SOFT, gx, gy, rx * .32, ry * .29, CREAM))
    if kind == "mischief":
        w, h = S(21, 17)
        return ('<path d="M%.1f,%.1f L%.1f,%.1f Q%.1f,%.1f %.1f,%.1f '
                'Q%.1f,%.1f %.1f,%.1f Z" fill="%s"/>'
                % (-w, -h, w, -h, w, h, 0, h, -w, h, -w, -h, INK_SOFT))
    raise ValueError(kind)


def _eye_marks(kind, G):
    (lx, ly), (rx, ry) = G["eyes"]
    kx = G["eye_r"][0] / 19.0
    ky = G["eye_r"][1] / 26.0
    return ('<g transform="translate(%.1f,%.1f)">%s</g>'
            '<g transform="translate(%.1f,%.1f)">%s</g>'
            % (lx, ly, _eye(kind, kx, ky, -1),
               rx, ry, _eye(kind, kx, ky, 1)))


def _mouth_marks(kind, G):
    mx, my = G["mouth"]
    mk = G["mouth_k"]

    def S(x, y):
        return (mx + x * mk, my + y * mk)
    if kind in ("neutral", "blink"):
        a, b, c = S(-28, -4), S(0, 14), S(30, -7)
        return ('<path d="M%.1f,%.1f Q%.1f,%.1f %.1f,%.1f" fill="none" '
                'stroke="%s" stroke-width="%.1f" %s/>'
                % (a[0], a[1], b[0], b[1], c[0], c[1], INK_SOFT, 15 * mk, RJ))
    if kind == "happy":
        a, b, c = S(-42, -12), S(0, 32), S(44, -15)
        return ('<path d="M%.1f,%.1f Q%.1f,%.1f %.1f,%.1f" fill="none" '
                'stroke="%s" stroke-width="%.1f" %s/>'
                % (a[0], a[1], b[0], b[1], c[0], c[1], INK_SOFT, 16 * mk, RJ))
    if kind == "delighted":
        p = [S(-48, -18), S(0, -10), S(48, -24), S(47, 50), S(0, 54),
             S(-47, 48)]
        cav = ("M%.1f,%.1f Q%.1f,%.1f %.1f,%.1f Q%.1f,%.1f %.1f,%.1f "
               "Q%.1f,%.1f %.1f,%.1f Z"
               % (p[0] + p[1] + p[2] + p[3] + p[4] + p[5] + p[0]))
        q = [S(-43, -13), S(0, -6), S(43, -19), S(41, 1), S(0, 12), S(-41, 5)]
        teeth = ("M%.1f,%.1f Q%.1f,%.1f %.1f,%.1f L%.1f,%.1f Q%.1f,%.1f "
                 "%.1f,%.1f Z" % (q[0] + q[1] + q[2] + q[3] + q[4] + q[5]))
        t = S(2, 34)
        tongue = ('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" '
                  'fill="%s"/>' % (t[0], t[1], 20 * mk, 13 * mk, FRUIT))
        return ('<path d="%s" fill="%s"/><path d="%s" fill="%s"/>%s'
                % (cav, INK_SOFT, teeth, CREAM, tongue))
    if kind == "sleepy":
        t = S(0, 4)
        return ('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="%s"/>'
                % (t[0], t[1], 15 * mk, 18 * mk, INK_SOFT))
    if kind == "surprised":
        t = S(1, 8)
        return ('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="%s"/>'
                % (t[0], t[1], 20 * mk, 27 * mk, INK_SOFT))
    if kind == "mischief":
        a, b, c = S(-40, 4), S(-2, 4), S(44, -26)
        return ('<path d="M%.1f,%.1f Q%.1f,%.1f %.1f,%.1f" fill="none" '
                'stroke="%s" stroke-width="%.1f" %s/>'
                % (a[0], a[1], b[0], b[1], c[0], c[1], INK_SOFT, 15 * mk, RJ))
    raise ValueError(kind)


def _brow_marks(kind, G):
    """Brows are hue-matched brown (BROW, never SOIL_DEEP or the eye hex)."""
    (lx, ly), (rx, ry) = G["eyes"]
    lift = G["brow_lift"]
    if kind == "surprised":
        return ('<path d="M%d,%d Q%d,%d %d,%d" fill="none" stroke="%s" '
                'stroke-width="13" %s/>'
                '<path d="M%d,%d Q%d,%d %d,%d" fill="none" stroke="%s" '
                'stroke-width="13" %s/>'
                % (lx - 22, ly - 56 - lift, lx, ly - 76 - lift,
                   lx + 22, ly - 58 - lift, BROW, RJ,
                   rx - 21, ry - 58 - lift, rx + 1, ry - 79 - lift,
                   rx + 23, ry - 60 - lift, BROW, RJ))
    if kind == "mischief":
        return ('<path d="M%d,%d L%d,%d" fill="none" stroke="%s" '
                'stroke-width="13" %s/>'
                '<path d="M%d,%d L%d,%d" fill="none" stroke="%s" '
                'stroke-width="13" %s/>'
                % (lx - 24, ly - 52 - lift, lx + 22, ly - 36 - lift, BROW, RJ,
                   rx + 23, ry - 54 - lift, rx - 21, ry - 38 - lift,
                   BROW, RJ))
    if kind == "sleepy":
        return ('<path d="M%d,%d Q%d,%d %d,%d" fill="none" stroke="%s" '
                'stroke-width="12" %s/>'
                % (lx - 22, ly - 48 - lift, lx, ly - 40 - lift,
                   lx + 22, ly - 50 - lift, BROW, RJ))
    return ""


def blush(G):
    """Always-on cheek marks. Unequal, off-centre, flat, low opacity.

    Anchored to the EYES, not to a hard-coded +-86: a face with narrow eye
    anchors gets narrow cheeks instead of blush hanging off the mass.
    """
    (lx, ly), (rx, ry) = G["eyes"]
    return ('<ellipse cx="%.1f" cy="%.1f" rx="31" ry="23" fill="%s" '
            'opacity="0.45"/>'
            '<ellipse cx="%.1f" cy="%.1f" rx="27" ry="20" fill="%s" '
            'opacity="0.45"/>'
            % (lx * 1.87, ly + 44, ACCENT, rx * 1.83, ry + 44, ACCENT))


def face(cx, cy, width_px, *, mass_w, default="happy", tilt=0.0,
         with_blush=True, eyes=None, eye_r=None, mouth=None, mouth_k=1.0,
         brow_lift=0):
    """Emit the whole swappable face rig at (cx, cy).

    `mass_w` is the width of the mass the face sits on, and is REQUIRED and
    KEYWORD-ONLY: the kit asserts the TOCA/KIT rule that a face is 45-60% of
    its mass. Pass the full mass width by mistake and the blush used to
    slide off the silhouette; now a positional 4th argument raises TypeError
    instead of being silently accepted as `mass_w`.

    Parameterise `eyes` / `eye_r` / `mouth` per plant.  Same six states on
    thirty plants is Instant Tell #19; the rig will not stop you, but the
    critic will.
    """
    ratio = width_px / float(mass_w)
    if not (FACE_MIN - 1e-9 <= ratio <= FACE_MAX + 1e-9):
        raise AssertionError(
            "face width %.0f is %.1f%% of its %.0f-wide mass; the rule is "
            "%.0f-%.0f%% (KIT.md Sec 7). Widen the mass or shrink the face."
            % (width_px, ratio * 100, mass_w, FACE_MIN * 100, FACE_MAX * 100))
    G = {"eyes": eyes or EYES_DEFAULT,
         "eye_r": eye_r or EYE_R_DEFAULT,
         "mouth": mouth or MOUTH_DEFAULT,
         "mouth_k": mouth_k,
         "brow_lift": brow_lift}
    s = width_px / 200.0
    parts = ['<g id="face" transform="translate(%.1f,%.1f) rotate(%.1f) '
             'scale(%.4f)">' % (cx, cy, tilt, s)]
    if with_blush:
        parts.append('<g id="face-blush">%s</g>' % blush(G))
    for kind in EXPRESSIONS:
        hide = "" if kind == default else ' display="none"'
        br = _brow_marks(kind, G)
        parts.append('<g id="face-%s"%s>%s<g id="face-%s-eyes">%s</g>'
                     '<g id="face-%s-mouth">%s</g></g>'
                     % (kind, hide,
                        ('<g id="face-%s-brows">%s</g>' % (kind, br))
                        if br else "",
                        kind, _eye_marks(kind, G),
                        kind, _mouth_marks(kind, G)))
    parts.append("</g>")
    return "".join(parts)


# =====================================================================
# DOCUMENT BUILDER
# `form()` is the two-tone recipe: flat base -> hard-edged shadow clipped
# to the shape -> outline on top.  Use it for EVERY mass.  Never use a
# gradient, never use a filter.  Never put <use> inside a <clipPath>
# (Chrome silently renders an empty file).
# =====================================================================
class Doc(object):
    def __init__(self, w=W, h=H):
        self.w, self.h = w, h
        self.defs, self.body, self._n = [], [], 0

    def _cid(self):
        self._n += 1
        return "k%d" % self._n

    def add(self, s):
        self.body.append(s)
        return self

    def form(self, d, base, shadow_d=None, shade=None, ol=OL_MAIN,
             inner="", evenodd=False, stroke=INK):
        """base fill + clipped hard-edged shadow + outline. The house move."""
        shade = shade or SHADE.get(base, base)
        fr = ' fill-rule="evenodd"' if evenodd else ""
        cr = ' clip-rule="evenodd"' if evenodd else ""
        cid = self._cid()
        self.defs.append('<clipPath id="%s"><path d="%s"%s/></clipPath>'
                         % (cid, d, cr))
        self.body.append('<path d="%s" fill="%s"%s/>' % (d, base, fr))
        guts = ""
        if shadow_d:
            guts += '<path d="%s" fill="%s"/>' % (shadow_d, shade)
        guts += inner
        if guts:
            self.body.append('<g clip-path="url(#%s)">%s</g>' % (cid, guts))
        self.body.append('<path d="%s" fill="none" stroke="%s" '
                         'stroke-width="%s" %s%s/>' % (d, stroke, ol, RJ, fr))
        return self

    def line(self, d, ol=OL_MAIN, col=INK):
        """An internal contour line -- same weight as its parent's outline."""
        self.body.append('<path d="%s" fill="none" stroke="%s" '
                         'stroke-width="%s" %s/>' % (d, col, ol, RJ))
        return self

    def fill(self, d, col, evenodd=False):
        """A flat unoutlined pattern mark (leaf marks, decals). No outline."""
        self.body.append('<path d="%s" fill="%s"%s/>'
                         % (d, col, ' fill-rule="evenodd"' if evenodd else ""))
        return self

    def svg(self):
        return ('<svg xmlns="http://www.w3.org/2000/svg" width="%d" '
                'height="%d" viewBox="0 0 %d %d">\n  <defs>%s</defs>\n  %s\n'
                '</svg>' % (self.w, self.h, self.w, self.h,
                            "".join(self.defs), "\n  ".join(self.body)))
