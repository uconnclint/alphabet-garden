#!/usr/bin/env python3
"""ALPHABET GARDEN — SHARED PLANT KIT (the style bible, in code).

Import this from every plant-builder script:

    import sys, os
    sys.path.insert(0, os.path.dirname(__file__))
    from _kit import *

Everything here is the *vocabulary* 78 plants are drawn from: palette tokens,
leaf silhouettes, trunk/stem treatments, the ground anchor, the face system,
the outline ladder and the two-tone shading recipe.  Read `KIT.md` for the
prose version and the rules you must not break.

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
# --- core (FLAT_ART_BRIEF Sec 3) -------------------------------------
GRASS       = "#7ec850"   # grass
GRASS_DEEP  = "#5da23c"   # grass-deep
GRASS_DARK  = "#4a8531"   # grass-dark
SKY_HI      = "#8fd3ff"   # sky-hi
SKY_LO      = "#cdefff"   # sky-lo
SOIL        = "#a9713f"   # soil
SOIL_DEEP   = "#8a5a33"   # soil-deep
CREAM       = "#fff7e6"   # cream
SUN         = "#ffd23f"   # sun
SUN_DEEP    = "#f0b429"   # sun-deep
ACCENT      = "#ff9d52"   # accent
BERRY       = "#c65fd1"   # berry
INK         = "#000000"   # ink
INK_SOFT    = "#3f3026"   # ink-soft

# --- extended (derived; see KIT.md Sec 2) ----------------------------
LEAF        = "#b0e070"   # leaf         lit green face   (shadow: GRASS)
SUN_SHADE   = "#e8a52a"   # sun-shade    shadow for SUN        dV 0.090
ACCENT_DEEP = "#e0813c"   # accent-deep  shadow for ACCENT     dV 0.122
FRUIT       = "#e8493c"   # fruit        red accent (apples, pepperoni)
FRUIT_DEEP  = "#c73a30"   # fruit-deep   shadow for FRUIT      dV 0.130
EMBER       = "#ef6a3c"   # ember        autumn orange-red
EMBER_DEEP  = "#cf5530"   # ember-deep   shadow for EMBER      dV 0.125
STEEL       = "#b8bcc8"   # steel        tinted metal (saucers, wings)
STEEL_DEEP  = "#969cae"   # steel-deep   shadow for STEEL      dV 0.102
SKY_DEEP    = "#62b0e6"   # sky-deep     shadow for SKY_HI     dV 0.098
BARK_LITE   = "#c2884e"   # bark-lite    lit bark face    (shadow: SOIL)
CREAM_DEEP  = "#e8dcc4"   # cream-deep   shadow for CREAM      dV 0.090
BEAM        = "#ffeaa8"   # beam         light/glow shapes, flat

# base -> shadow pairing table.  ALWAYS take a shadow from here.
SHADE = {
    GRASS: GRASS_DEEP, GRASS_DEEP: GRASS_DARK, LEAF: GRASS,
    SOIL: SOIL_DEEP, BARK_LITE: SOIL,
    SUN: SUN_SHADE, SUN_DEEP: "#d69526",
    ACCENT: ACCENT_DEEP, FRUIT: FRUIT_DEEP, EMBER: EMBER_DEEP,
    STEEL: STEEL_DEEP, SKY_HI: SKY_DEEP, CREAM: CREAM_DEEP,
    BERRY: "#a94bb3", BEAM: SUN,
}

# =====================================================================
# OUTLINE LADDER  (TOCA 3.3; object height ~880px on a 1024 canvas)
# One weight per role, NOT per shape.  13 / 880 = 1.48%.
# =====================================================================
OL_MAIN = 13   # silhouette + primary masses (canopy, trunk, petals, slices)
OL_PROP = 10   # attached props 90-190px tall (apples, butterflies, saucers)
OL_FINE = 7    # props under 90px + internal detail (pepperoni, stars, veins)
OL_BG   = 8    # background/atmospheric layer, hue-matched not black

RJ = 'stroke-linejoin="round" stroke-linecap="round"'


def ol_for(short_side):
    """Outline weight for a prop, capped so it can never eat its own shape."""
    return max(OL_FINE, min(OL_MAIN, int(round(0.16 * short_side))))


# =====================================================================
# GEOMETRY HELPERS
# =====================================================================
def smooth_closed(pts):
    """Catmull-Rom -> closed cubic bezier through pts. Hand-drawn wobble."""
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


def bite(cx, cy, r):
    """Sub-path circle; with fill-rule=evenodd it removes a nibble.
    Always place it STRADDLING an edge so it reads as a bite, not a hole."""
    return ("M%.1f,%.1f A%.1f,%.1f 0 1 0 %.1f,%.1f "
            "A%.1f,%.1f 0 1 0 %.1f,%.1f Z"
            % (cx - r, cy, r, r, cx + r, cy, r, r, cx - r, cy))


# =====================================================================
# SHADING RECIPE  (TOCA 3.4 / BRIEF Sec 2)
# Light is ALWAYS from the upper-left, on every one of the 78 plants.
# The shadow face is therefore the lower-right ~35% of every mass.
# `sweep()` returns a hard-edged, hand-wavy region to clip into a shape.
# =====================================================================
def sweep(cx, cy, rx, ry, lo=0.34, hi=-0.36, wob=0.07, seed=0.0):
    """Region below a wavy line that RISES left->right (light upper-left).

    lo/hi: the line's y at the left/right edge, as a fraction of ry
    (positive = below centre).  Defaults put ~35% of a round mass in shade.
    """
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

    Lobes are given SHOULDER points at +-15 deg so each tip stays fat: a
    maple leaf drawn from tips alone becomes a spiky asterisk that vanishes
    at game size.  Notches are shallow (0.38-0.46 of L) for the same reason.
    """
    tips = [(-101, .64), (-50, .88), (0, 1.00), (52, .86), (100, .62)]
    notch = [(-77, .42), (-26, .46), (26, .44), (77, .40)]
    seq = [(-153, .16)]
    for i, (a, r) in enumerate(tips):
        k = jit[i % len(jit)]
        seq += [(a - 15, r * k * .86), (a, r * k), (a + 15, r * k * .86)]
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
    """Grass blade: fat base, round tip, one-sided bend. (from batch 2)"""
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


def canopy_blob(cx, cy, rx, ry, n=9, jit=(1.0, .93, 1.07, .96, 1.04, .91,
                                          1.05, .98, 1.02),
                bul=(46, 62, 38, 70, 44, 58, 34, 66, 50), start=-96,
                notch=None):
    """A lobed foliage mass: n unequal scallops around an ellipse.

    This is the house canopy primitive -- clump masses, bushes, shrubs.
    Stack 3-6 of them, back to front, each independently outlined; the
    crossing outlines are what make a canopy read as clumps and not a blob.
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
# TRUNK / STEM VOCABULARY  (3 treatments) + THE GROUND ANCHOR
# Every one of them ends in `root_flare()` so all 78 meet the soil the
# same way: the shaft splays into 3 unequal rounded root lobes spanning
# 1.6-2.2x the shaft width, the lowest touching BASE_Y.
# =====================================================================
def _root_pts(cx, wb, y_base):
    """3 unequal root lobes, deliberately not mirrored. Left->right.

    Notches are SHALLOW (18-30px) on purpose: deeper ones read as claws or
    trouser legs at game size, which was the loudest defect of pilot v1.
    """
    return [(cx - wb * 1.06, y_base - 28),
            (cx - wb * 0.70, y_base - 4),
            (cx - wb * 0.34, y_base - 17),
            (cx + wb * 0.02, y_base - 2),
            (cx + wb * 0.40, y_base - 20),
            (cx + wb * 0.74, y_base - 3),
            (cx + wb * 1.02, y_base - 24)]


def stem_slim(cx, y_top, y_base, w, lean=18.0, w_base=None):
    """Treatment 1 -- slim stem. Flowers, small plants. w >= 40px (3.9%)."""
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
    return smooth_closed(left + _root_pts(cx, wb, y_base) + right)


def trunk_chunky(cx, y_top, y_base, w_top, w_base, lean=0.0):
    """Treatment 2 -- chunky flared trunk. Trees. Buttressed, not a cylinder."""
    ht, hb = w_top * 0.5, w_base * 0.5
    hgt = y_base - y_top
    left = [(cx - ht + lean, y_top),
            (cx - ht * 1.10 + lean * 0.6, y_top + hgt * 0.26),
            (cx - ht * 1.34, y_top + hgt * 0.55),
            (cx - hb * 0.84, y_base - 76)]
    right = [(cx + hb * 0.88, y_base - 70),
             (cx + ht * 1.28, y_top + hgt * 0.58),
             (cx + ht * 1.16 + lean * 0.5, y_top + hgt * 0.28),
             (cx + ht + lean, y_top)]
    return smooth_closed(left + _root_pts(cx, hb, y_base) + right)


def lozenge(cx, cy, hw, hh, deg=0.0):
    """One squat segment. Building block of the palm trunk."""
    p = [(-hw * 0.97, -hh * 0.50), (-hw * 0.70, -hh), (0, -hh * 0.93),
         (hw * 0.72, -hh * 0.98), (hw * 0.99, -hh * 0.46),
         (hw * 0.95, hh * 0.52), (hw * 0.64, hh), (0, hh * 0.97),
         (-hw * 0.68, hh * 0.99), (-hw * 0.98, hh * 0.48)]
    return smooth_closed(place(p, cx, cy, deg))


def trunk_palm(cx, y_top, y_base, hw_top, hw_base, n=7, wob=(0, 5, -4, 6, -3, 4, -6, 3)):
    """Treatment 3 -- segmented palm. Returns [(path, hw, cy)] TOP FIRST so
    the caller paints top->bottom and each lower ring overlaps the one above.
    The bottom ring IS the ground anchor: it is the widest and sits on
    BASE_Y with a flat-ish rounded underside."""
    out = []
    span = y_base - y_top
    hh = span / (n * 1.72)
    for i in range(n):
        t = i / float(n - 1)
        cy = y_top + hh + (span - 2 * hh) * t
        hw = hw_top + (hw_base - hw_top) * (t ** 1.25)
        out.append((lozenge(cx + wob[i % len(wob)], cy, hw, hh * 1.16,
                            deg=(-1.6 if i % 2 else 1.4)), hw, cy))
    return out


# =====================================================================
# THE FACE SYSTEM
# Designed in a 200-unit-wide box, origin at the face centre, then
# translate+scale onto the plant.  s ~= face_width_px / 200.
# Every expression = eyes(1 mark) + mouth(1 mark) [+ brows(1 mark)] <= 3.
# Blush lives OUTSIDE the swappable group -- it is always on.
# Emitted ids are stable: face-neutral, face-happy, face-delighted,
# face-sleepy, face-surprised, face-mischief.  Only the default is
# visible; the rest carry display="none" so runtime can hot-swap them.
# =====================================================================
EXPRESSIONS = ("neutral", "happy", "delighted", "sleepy", "surprised",
               "mischief")

_EL, _ER = (-46, -14), (48, -18)      # eye anchors -- deliberately unequal
_MO = (2, 44)                          # mouth anchor


def _eye_marks(kind):
    lx, ly = _EL
    rx, ry = _ER
    if kind == "neutral":
        return ('<ellipse cx="%d" cy="%d" rx="19" ry="26" fill="%s" '
                'transform="rotate(-7 %d %d)"/>'
                '<ellipse cx="%d" cy="%d" rx="18" ry="24" fill="%s" '
                'transform="rotate(6 %d %d)"/>'
                % (lx, ly, INK_SOFT, lx, ly, rx, ry, INK_SOFT, rx, ry))
    if kind in ("happy", "delighted"):
        return ('<path d="M%d,%d Q%d,%d %d,%d" fill="none" stroke="%s" '
                'stroke-width="15" %s/>'
                '<path d="M%d,%d Q%d,%d %d,%d" fill="none" stroke="%s" '
                'stroke-width="15" %s/>'
                % (lx - 24, ly + 8, lx, ly - 30, lx + 23, ly + 6, INK_SOFT, RJ,
                   rx - 23, ry + 7, rx + 1, ry - 32, rx + 24, ry + 5,
                   INK_SOFT, RJ))
    if kind == "sleepy":
        return ('<path d="M%d,%d Q%d,%d %d,%d" fill="none" stroke="%s" '
                'stroke-width="15" %s/>'
                '<path d="M%d,%d Q%d,%d %d,%d" fill="none" stroke="%s" '
                'stroke-width="15" %s/>'
                % (lx - 24, ly - 8, lx, ly + 18, lx + 23, ly - 10, INK_SOFT, RJ,
                   rx - 23, ry - 9, rx + 1, ry + 17, rx + 24, ry - 11,
                   INK_SOFT, RJ))
    if kind == "surprised":
        return ('<ellipse cx="%d" cy="%d" rx="22" ry="31" fill="%s"/>'
                '<ellipse cx="%d" cy="%d" rx="21" ry="29" fill="%s"/>'
                '<ellipse cx="%d" cy="%d" rx="7" ry="9" fill="%s"/>'
                '<ellipse cx="%d" cy="%d" rx="6" ry="8" fill="%s"/>'
                % (lx, ly, INK_SOFT, rx, ry, INK_SOFT,
                   lx - 7, ly - 12, CREAM, rx - 6, ry - 11, CREAM))
    if kind == "mischief":
        def flat(ex, ey, w, h):
            return ('<path d="M%d,%d L%d,%d Q%d,%d %d,%d Q%d,%d %d,%d Z" '
                    'fill="%s"/>' % (ex - w, ey - h, ex + w, ey - h,
                                     ex + w, ey + h, ex, ey + h,
                                     ex - w, ey + h, ex - w, ey - h, INK_SOFT))
        return flat(lx, ly, 21, 17) + flat(rx, ry, 20, 16)
    raise ValueError(kind)


def _mouth_marks(kind):
    mx, my = _MO
    if kind == "neutral":
        return ('<path d="M%d,%d Q%d,%d %d,%d" fill="none" stroke="%s" '
                'stroke-width="15" %s/>'
                % (mx - 28, my - 4, mx, my + 14, mx + 30, my - 7, INK_SOFT, RJ))
    if kind == "happy":
        return ('<path d="M%d,%d Q%d,%d %d,%d" fill="none" stroke="%s" '
                'stroke-width="16" %s/>'
                % (mx - 42, my - 12, mx, my + 32, mx + 44, my - 15,
                   INK_SOFT, RJ))
    if kind == "delighted":
        cav = ("M{a},{b} Q{x},{c} {d},{e} Q{f},{g} {x},{h} Q{i},{j} {a},{b} Z"
               .format(a=mx - 48, b=my - 18, x=mx, c=my - 10, d=mx + 48,
                       e=my - 24, f=mx + 47, g=my + 50, h=my + 54,
                       i=mx - 47, j=my + 48))
        teeth = ("M{a},{b} Q{x},{c} {d},{e} L{d2},{f} Q{x},{g} {a2},{h} Z"
                 .format(a=mx - 43, b=my - 13, x=mx, c=my - 6, d=mx + 43,
                         e=my - 19, d2=mx + 41, f=my + 1, g=my + 12,
                         a2=mx - 41, h=my + 5))
        tongue = '<ellipse cx="%d" cy="%d" rx="20" ry="13" fill="%s"/>' % (
            mx + 2, my + 34, FRUIT)
        return ('<path d="%s" fill="%s"/><path d="%s" fill="%s"/>%s'
                % (cav, INK_SOFT, teeth, CREAM, tongue))
    if kind == "sleepy":
        return '<ellipse cx="%d" cy="%d" rx="15" ry="18" fill="%s"/>' % (
            mx, my + 4, INK_SOFT)
    if kind == "surprised":
        return '<ellipse cx="%d" cy="%d" rx="20" ry="27" fill="%s"/>' % (
            mx + 1, my + 8, INK_SOFT)
    if kind == "mischief":
        return ('<path d="M%d,%d Q%d,%d %d,%d" fill="none" stroke="%s" '
                'stroke-width="15" %s/>'
                % (mx - 40, my + 4, mx - 2, my + 4, mx + 44, my - 26,
                   INK_SOFT, RJ))
    raise ValueError(kind)


def _brow_marks(kind):
    """Brows are hue-matched brown, never black, and often omitted."""
    lx, ly = _EL
    rx, ry = _ER
    if kind == "surprised":
        return ('<path d="M%d,%d Q%d,%d %d,%d" fill="none" stroke="%s" '
                'stroke-width="13" %s/>'
                '<path d="M%d,%d Q%d,%d %d,%d" fill="none" stroke="%s" '
                'stroke-width="13" %s/>'
                % (lx - 22, ly - 56, lx, ly - 76, lx + 22, ly - 58,
                   SOIL_DEEP, RJ,
                   rx - 21, ry - 58, rx + 1, ry - 79, rx + 23, ry - 60,
                   SOIL_DEEP, RJ))
    if kind == "mischief":
        return ('<path d="M%d,%d L%d,%d" fill="none" stroke="%s" '
                'stroke-width="13" %s/>'
                '<path d="M%d,%d L%d,%d" fill="none" stroke="%s" '
                'stroke-width="13" %s/>'
                % (lx - 24, ly - 52, lx + 22, ly - 36, SOIL_DEEP, RJ,
                   rx + 23, ry - 54, rx - 21, ry - 38, SOIL_DEEP, RJ))
    if kind == "sleepy":
        return ('<path d="M%d,%d Q%d,%d %d,%d" fill="none" stroke="%s" '
                'stroke-width="12" %s/>'
                % (lx - 22, ly - 48, lx, ly - 40, lx + 22, ly - 50,
                   SOIL_DEEP, RJ))
    return ""


def blush(scale_note=""):
    """Always-on cheek marks. Unequal, off-centre. Flat, low opacity."""
    return ('<ellipse cx="-86" cy="30" rx="31" ry="23" fill="%s" '
            'opacity="0.45"/>'
            '<ellipse cx="88" cy="26" rx="27" ry="20" fill="%s" '
            'opacity="0.45"/>' % (ACCENT, ACCENT))


def face(cx, cy, width_px, default="happy", tilt=0.0, with_blush=True):
    """Emit the whole swappable face rig at (cx, cy).

    All six expression groups are written out with stable ids; every one
    except `default` carries display="none" so the runtime can hot-swap by
    toggling visibility.  Only the default rasterises into the PNG.
    """
    s = width_px / 200.0
    parts = ['<g id="face" transform="translate(%.1f,%.1f) rotate(%.1f) '
             'scale(%.4f)">' % (cx, cy, tilt, s)]
    if with_blush:
        parts.append('<g id="face-blush">%s</g>' % blush())
    for kind in EXPRESSIONS:
        hide = "" if kind == default else ' display="none"'
        parts.append('<g id="face-%s"%s>%s%s%s</g>'
                     % (kind, hide, _brow_marks(kind), _eye_marks(kind),
                        _mouth_marks(kind)))
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

    def svg(self):
        return ('<svg xmlns="http://www.w3.org/2000/svg" width="%d" '
                'height="%d" viewBox="0 0 %d %d">\n  <defs>%s</defs>\n  %s\n'
                '</svg>' % (self.w, self.h, self.w, self.h,
                            "".join(self.defs), "\n  ".join(self.body)))
