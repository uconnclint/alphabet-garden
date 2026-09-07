#!/usr/bin/env python3
"""Build wave-3 flat-vector plants (ids P-Z, 28 plants).

    python3 art/flat/plants/_build_w3.py             # all 28
    python3 art/flat/plants/_build_w3.py z-zombie-tree

Authored entirely from `_kit.py`.  Rasteriser reused from `_build_plants.py`
(2x headless Chrome -> LANCZOS to 1x).

DO NOT edit `_build_plants.py`, `_build_w1.py`, `_build_w2.py`, `_kit.py`,
`KIT.md` or `_verify.py` from here -- they are shared with other authors
working concurrently.
"""
import os
import sys
import math

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _kit import *                                     # noqa: F401,F403
from _build_plants import render                       # noqa: E402

OUT = HERE


# =====================================================================
# LOCAL HELPERS  (built ON the kit, never replacing it)
# =====================================================================
def circ(cx, cy, r, seed=0.0, n=12, amp=0.030, ry=None, deg=0.0):
    """A hand-drawn circle/ellipse -- the kit has no primitive for a ball."""
    ry = r if ry is None else ry
    j = jitter(seed, n, amp, 1.0)
    p = [(r * j[i] * math.cos(2 * math.pi * i / n - 1.25),
          ry * j[i] * math.sin(2 * math.pi * i / n - 1.25)) for i in range(n)]
    return smooth_closed(place(p, cx, cy, deg))


def ball(d, cx, cy, r, base, seed=0.0, ol=OL_PROP, ry=None, deg=0.0,
         shade=None, gloss=0.0, amp=0.030):
    """A two-tone sphere with an optional flat cream gloss chip."""
    ry = r if ry is None else ry
    p = circ(cx, cy, r, seed, 12, amp, ry, deg)
    inner = ""
    if gloss:
        inner = ('<path d="%s" fill="%s" opacity="0.80"/>'
                 % (chip(cx - r * .40, cy - ry * .44, r * gloss), CREAM))
    d.form(p, base, sweep(cx, cy, r, ry, lo=.30, hi=-.44, seed=seed),
           shade, ol=ol, inner=inner)
    return p


def marks(d, items):
    """Flat, UNOUTLINED leaf-marks scattered over a canopy (KIT Sec 5)."""
    for (mx, my, L, Wd, dg, col) in items:
        d.fill(leaf_round(mx, my, L, Wd, dg), col)


def clump(d, items):
    """Canopy clumps, each with its OWN lobe profile from its own seed."""
    for it in items:
        cx, cy, rx, ry, col, n, st, notch, sd = it
        J, B = lobe_profile(sd, n, jit=0.085, bul=(28, 76))
        d.form(canopy_blob(cx, cy, rx, ry, n, J, B, start=st, notch=notch),
               col, sweep(cx, cy, rx, ry, lo=.26 + (int(cx) % 6) * .013,
                          hi=-.38 - (int(cy) % 5) * .014, wob=.09,
                          seed=sd * .83))


def stroke(d, pts, col=INK, ol=OL_MAIN):
    """A smoothed open contour line through a point list."""
    d.add('<path d="M%.1f,%.1f%s" fill="none" stroke="%s" stroke-width="%d" '
          '%s/>' % (pts[0][0], pts[0][1], smooth_open(pts), col, ol, RJ))


def qline(d, ax, ay, bx, by, cx, cy, col=INK, ol=OL_MAIN):
    """One quadratic contour line."""
    d.add('<path d="M%.1f,%.1f Q%.1f,%.1f %.1f,%.1f" fill="none" '
          'stroke="%s" stroke-width="%d" %s/>'
          % (ax, ay, bx, by, cx, cy, col, ol, RJ))


def swoosh(d, x0, y0, x1, y1, k, col, ol=OL_BG):
    """A hue-matched motion/background arc. Never black."""
    sp = bow(x0, y0, x1, y1, k, 6)
    d.add('<path d="M%.1f,%.1f%s" fill="none" stroke="%s" stroke-width="%d" '
          '%s/>' % (sp[0][0], sp[0][1], smooth_open(sp), col, ol, RJ))


def tube(d, pts, w0, w1, base, shade=None, ol=OL_MAIN, cap0="flat",
         cap1="round", inner=""):
    """A tapered organic limb along an explicit spine (vines, tentacles)."""
    n = len(pts)
    ws = [w0 + (w1 - w0) * (i / float(n - 1)) ** 0.9 for i in range(n)]
    p = ribbon(pts, ws, cap0=cap0, cap1=cap1)
    xs = [q[0] for q in pts]
    ys = [q[1] for q in pts]
    cx, cy = (min(xs) + max(xs)) / 2., (min(ys) + max(ys)) / 2.
    rx = max((max(xs) - min(xs)) / 2., 30)
    ry = max((max(ys) - min(ys)) / 2., 30)
    d.form(p, base, sweep(cx, cy, rx, ry, lo=.22, hi=-.34, wob=.05,
                          seed=cx * .01), shade, ol=ol, inner=inner)
    return p


def spiral_pts(cx, cy, r0, turns, seed_ang, n=16, shrink=0.82):
    """Points along an inward spiral -- tendrils, shells, curls."""
    pts = []
    for i in range(n):
        t = i / float(n - 1)
        a = math.radians(seed_ang) + turns * 2 * math.pi * t
        r = r0 * (1.0 - shrink * t)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def petal_ring(d, cx, cy, n, r_in, r_out, wd, base, shade, seed,
               ol=OL_PROP, start=-90, kind="round", curl=0.10, sq=1.0):
    """A ring of leaf-shaped petals around (cx, cy). Angles are jittered.

    `sq` < 1 squashes the ring vertically, so a bloom can be a WIDE ellipse
    instead of yet another disc -- the single cheapest way to keep two
    flower heads off each other's silhouette.
    """
    j = jitter(seed, n, 0.09, 1.0)
    k = jitter(seed + 4.0, n, 3.6, 0.0)
    for i in range(n):
        a = start + 360.0 * i / n + k[i]
        rad = math.radians(a)
        bx = cx + r_in * math.cos(rad)
        by = cy + r_in * sq * math.sin(rad)
        L = (r_out - r_in) * j[i] * (abs(math.cos(rad))
                                     + sq * abs(math.sin(rad)))
        fn = leaf_round if kind == "round" else leaf_pointed
        p = fn(bx, by, L, wd * j[i], a + 90, curl)
        d.form(p, base, sweep(bx + (L * .3) * math.cos(rad),
                              by + (L * .3) * math.sin(rad),
                              wd * .55, L * .45, lo=.26, hi=-.42,
                              seed=seed + i), shade, ol=ol)


def blade_fan(d, items):
    """Sword/strap leaves radiating from a crown point."""
    for (bx, by, tx, ty, hw, tw, bend, col, sh, ol) in items:
        p = leaf_blade(bx, by, tx, ty, hw, tw, bend)
        d.form(p, col, sweep((bx + tx) / 2., (by + ty) / 2.,
                             abs(tx - bx) * .5 + 40, abs(by - ty) * .5 + 20,
                             lo=.22, hi=-.36, seed=tx * .01), sh, ol=ol)


def gnarl(d, pts, w0, w1, base, shade, ol=OL_MAIN):
    """A crooked woody limb (zombie / willow branches)."""
    return tube(d, pts, w0, w1, base, shade, ol=ol, cap1="round")


def palm_rings(cx0, y_top, cx1, y_base, hw_top, hw_base, n=9, k=0.16):
    """A LEANING segmented palm column. Returns [(path, hw, cy)] TOP FIRST."""
    sp = bow(cx0, y_top, cx1, y_base, k, n)
    hh = (y_base - y_top) / float(n * 1.42)
    out = []
    for i, (x, y) in enumerate(sp):
        t = i / float(n - 1)
        hw = hw_top + (hw_base - hw_top) * (t ** 1.30)
        out.append((lozenge(x, y, hw, hh, deg=(-2.4 if i % 2 else 2.0)),
                    hw, y))
    return out


# =====================================================================
# 1. p-palm-tree   REALISTIC -- no face
#    A LEANING segmented column with a drooping frond fan. Deliberately
#    off-centre and asymmetric so it cannot sit on p-pizza-palm's upright
#    trunk-plus-fan silhouette.
# =====================================================================
def palm_tree():
    d = Doc()
    CX0, CY0 = 404, 404                      # the crown
    # ---- back rank fronds: hue-matched, unoutlined (depth step) ----
    for (dg, L, Wd, bd) in ((-162, 288, 118, 0.34), (156, 284, 116, -0.34),
                            (-118, 300, 120, 0.26), (118, 292, 118, -0.26)):
        d.fill(leaf_frond(CX0, CY0, L, Wd, dg, bd), GRASS_DARK)
    # ---- the trunk, drawn before the crown so fronds cover the top ----
    rings = palm_rings(CX0 + 16, CY0 + 44, 596, 942, 46, 96, 9, 0.19)
    for i, (p, hw, cy) in enumerate(rings):
        d.form(p, BARK_LITE if i % 2 else BARK,
               sweep(0, cy, hw * 2.0, hw * 0.62, lo=.24, hi=-.30, wob=.05,
                     seed=cy * .01), None, ol=OL_MAIN)
    # a splayed foot under the bottom ring
    bx = 596
    d.form(smooth_closed(root_pts(bx, 106, BASE_Y, 61.3, 3, 1.08, (18, 30))
                         + [(bx + 108, 914), (bx, 898), (bx - 112, 916)]),
           BARK, sweep(bx, 956, 110, 46, lo=.22, hi=-.28), BARK_DEEP)
    # ---- the frond fan: LONG, NARROW, and drooping past the horizontal ----
    for (dg, L, Wd, bd, col, sd) in (
            (-152, 306, 126, 0.36, GRASS_DEEP, 1.1),
            (146, 300, 124, -0.36, GRASS_DEEP, 2.2),
            (-112, 328, 132, 0.28, GRASS, 3.3),
            (108, 322, 130, -0.30, GRASS, 4.4),
            (-72, 336, 134, 0.20, GRASS, 5.5),
            (68, 330, 132, -0.22, LEAF, 6.6),
            (-30, 318, 126, 0.12, LEAF, 7.7),
            (24, 314, 124, -0.14, LEAF, 8.8)):
        a = math.radians(dg)
        tipx = CX0 + L * math.sin(a) * .58
        tipy = CY0 - L * math.cos(a) * .58
        d.form(leaf_frond(CX0, CY0, L, Wd, dg, bd), col,
               sweep(tipx, tipy, Wd * .74, L * .34, lo=.24, hi=-.40,
                     seed=sd), None, ol=OL_MAIN)
        d.line(vein(CX0, CY0, L * .88, dg, .82), OL_FINE)
    # ODDITY: one frond has snapped at the midrib and hangs straight down
    d.form(leaf_frond(462, 478, 262, 116, 176, -0.44), GRASS_DEEP,
           sweep(486, 646, 84, 116, lo=.22, hi=-.36), GRASS_DARK, ol=OL_MAIN)
    d.line("M462,478 C476,552 480,614 470,686", OL_FINE)
    # ---- coconuts under the crown ----
    for (kx, ky, r, sd) in ((338, 470, 54, 7.1), (432, 486, 50, 8.2),
                            (396, 418, 46, 9.3)):
        ball(d, kx, ky, r, BARK_DEEP, sd, OL_PROP, shade=INK_SOFT, gloss=0.30)
    return d.svg()


# =====================================================================
# 2. p-panda-pansy   SILLY -- face
#    A pansy whose bloom IS a panda head: cream scalloped petals, two dark
#    ears breaking the top edge, big patches around the eyes.
# =====================================================================
def panda_pansy():
    d = Doc()
    # ---- stem + two leaves ----
    d.form(leaf_pointed(448, 856, 322, 158, -86, .16), GRASS,
           sweep(292, 792, 146, 108, lo=.20, hi=-.36), GRASS_DEEP, ol=OL_MAIN)
    d.line(vein(448, 856, 282, -86, .78), OL_FINE)
    d.form(leaf_pointed(560, 918, 296, 148, 84, -.16), GRASS_DEEP,
           sweep(706, 866, 134, 100, lo=.18, hi=-.34), GRASS_DARK, ol=OL_MAIN)
    d.line(vein(560, 918, 258, 84, .78), OL_FINE)
    # a second, unopened pansy bud on its own short stalk
    d.form(branch(500, 700, 774, 596, 40, 28, -0.18, 6), GRASS,
           sweep(636, 648, 140, 60, lo=.16, hi=-.26), GRASS_DEEP, ol=OL_PROP)
    d.form(circ(792, 560, 84, 15.1, 11, .07, 96, 14), CREAM,
           sweep(792, 560, 84, 96, lo=.28, hi=-.42), CREAM_DEEP, ol=OL_PROP)
    d.line("M792,466 C812,506 810,556 796,600", OL_FINE)
    for (dg, L, Wd) in ((-150, 128, 56), (-6, 122, 52), (152, 118, 50)):
        d.form(leaf_pointed(788, 630, L, Wd, dg, .12), GRASS_DEEP,
               sweep(788, 590, Wd * .6, L * .34, lo=.24, hi=-.38, seed=dg),
               GRASS_DARK, ol=OL_FINE)
    d.form(stem_slim(504, 566, BASE_Y, 76, root_seed=27.6, lean=-12,
                     w_base=210, root_lobes=3, root_depth=(18, 30)),
           GRASS, sweep(518, 800, 62, 216, lo=.06, hi=-.12, wob=.03),
           GRASS_DEEP)
    # ---- the two dark ears, behind the bloom ----
    for (ex, ey, r, sd) in ((286, 194, 98, 2.4), (734, 178, 92, 5.8)):
        d.form(circ(ex, ey, r, sd, 10, .05, r * .94), INK_SOFT,
               sweep(ex, ey, r, r, lo=.30, hi=-.44), INK_SOFT, ol=OL_MAIN)
    # ---- the bloom: broad pansy scallops ----
    J, B = lobe_profile(38.2, 8, jit=0.11, bul=(62, 124))
    head = canopy_blob(508, 332, 236, 220, 8, J, B, start=-104)
    d.form(head, CREAM, sweep(508, 332, 254, 236, lo=.30, hi=-.44, wob=.07),
           CREAM_DEEP)
    # ---- eye patches: dark oval, cream well inside it ----
    for (px, py, rx, ry, dg) in ((390, 292, 100, 116, -12),
                                 (628, 284, 96, 112, 10)):
        d.form(circ(px, py, rx, 0.0, 10, .04, ry, dg),
               INK_SOFT, None, INK_SOFT, ol=OL_PROP)
        d.fill(circ(px, py + 4, rx * .60, 1.7, 10, .05, ry * .60, dg), CREAM)
    # muzzle + nose
    d.fill(circ(508, 412, 96, 3.1, 10, .05, 62, 2), CREAM_DEEP)
    d.form(smooth_closed([(508, 356), (546, 372), (534, 402), (508, 412),
                          (482, 400), (470, 370)]), INK_SOFT, None, INK_SOFT,
           ol=OL_FINE)
    # ODDITY: one bloom-petal is nibbled -- a bee-bitten notch, plus a
    # single stray petal lying on the soil
    d.form(leaf_round(846, 946, 106, 80, 100, .12), CREAM,
           sweep(796, 936, 50, 34, lo=.24, hi=-.38), CREAM_DEEP, ol=OL_PROP)
    d.line(vein(846, 946, 92, 100, .74), OL_FINE)
    d.add(face(508, 332, 280, mass_w=508, default="happy", tilt=-2.0,
               eyes=((-84, -28), (86, -34)), eye_r=(19, 21), mouth=(2, 62),
               mouth_k=1.10))
    return d.svg()


# =====================================================================
# 3. q-quaking-aspen   REALISTIC -- no face
#    THREE pale trunks under a TALL, NARROW shimmering column of coin
#    leaves.  Deliberately the tallest/thinnest tree mass in the game so it
#    cannot land on the spruce's triangle or the UFO tree's wide dome.
# =====================================================================
def quaking_aspen():
    d = Doc()
    def _pale_trunk(cx, top, wt, wb, sd, lean, flare, marks_at):
        d.form(trunk_chunky(cx, top, BASE_Y, wt, wb, root_seed=sd, lean=lean,
                            root_lobes=3, root_depth=(16, 28), flare=flare),
               CREAM, sweep(cx + 22, (top + BASE_Y) / 2, wb * .52,
                            (BASE_Y - top) * .5, lo=.10, hi=-.16, wob=.04),
               CREAM_DEEP)
        for (my, mw, mh, dg) in marks_at:
            d.fill(slab(cx + (mw * .10), my, mw, mh, 0.42, dg), INK_SOFT)

    _pale_trunk(344, 486, 44, 72, 23.9, -12, 0.82,
                [(602, 54, 20, -4), (722, 42, 17, 6), (852, 48, 18, -7)])
    _pale_trunk(676, 458, 40, 66, 41.1, 14, 0.82,
                [(572, 48, 18, 5), (694, 56, 20, -6), (834, 40, 16, 8)])
    _pale_trunk(508, 402, 62, 100, 17.3, 4, 0.88,
                [(500, 72, 24, -5), (628, 62, 21, 7), (766, 78, 25, -4),
                 (890, 56, 19, 6)])
    # ---- the tall narrow canopy column ----
    clump(d, [(354, 402, 128, 110, GRASS_DEEP, 9, -104, None, 1.4),
              (660, 388, 126, 108, GRASS_DEEP, 9, -86, None, 2.8),
              (330, 296, 134, 116, GRASS, 10, -100, None, 4.2),
              (686, 280, 130, 114, GRASS, 10, -88, 4, 5.6),
              (426, 322, 146, 126, LEAF, 10, -96, None, 7.0),
              (600, 306, 142, 124, LEAF, 10, -92, None, 8.4),
              (508, 234, 152, 128, LEAF, 11, -97, None, 9.8),
              (508, 424, 152, 110, GRASS, 10, -95, None, 11.2)])
    # coin leaves -- the quake. Flat, unoutlined pattern (KIT Sec 5).
    for (mx, my, r, col, sd) in (
            (352, 246, 30, SUN, 1.1), (438, 190, 27, SUN_DEEP, 2.2),
            (566, 166, 29, SUN, 3.3), (648, 232, 26, SUN_DEEP, 4.4),
            (392, 350, 28, SUN, 5.5), (612, 366, 25, SUN_DEEP, 6.6),
            (498, 254, 31, SUN, 7.7), (532, 388, 26, SUN, 8.8),
            (444, 424, 24, SUN_DEEP, 9.9), (596, 436, 27, SUN, 11.0)):
        d.fill(circ(mx, my, r, sd, 9, .09, r * .88, sd * 7), col)
    marks(d, [(330, 322, 74, 42, -30, GRASS_DARK),
              (664, 306, 70, 40, 26, GRASS_DARK),
              (470, 148, 68, 40, -16, GRASS_DEEP),
              (556, 442, 66, 38, 32, GRASS_DEEP)])
    # ODDITY: one golden coin leaf has let go and is falling past the trunks
    d.form(circ(760, 712, 44, 12.1, 10, .07, 38, 24), SUN,
           sweep(760, 712, 44, 38, lo=.26, hi=-.42), SUN_DEEP, ol=OL_PROP)
    d.line("M744,678 C756,662 774,656 792,660", OL_FINE)
    return d.svg()


# =====================================================================
# 4. q-quail-quillplant   SILLY -- face
#    A plump three-quarter quail perched on a stem: fat egg body, round
#    head, beak jutting LEFT out of the silhouette, and the topknot quill
#    curling forward over the forehead.
# =====================================================================
def quail_quillplant():
    d = Doc()
    # ---- stem + leaves ----
    d.form(leaf_pointed(448, 876, 268, 138, -80, .16), GRASS,
           sweep(320, 806, 128, 98, lo=.20, hi=-.36), GRASS_DEEP, ol=OL_MAIN)
    d.line(vein(448, 876, 232, -80, .78), OL_FINE)
    d.form(leaf_pointed(556, 936, 232, 124, 76, -.16), GRASS_DEEP,
           sweep(676, 884, 112, 90, lo=.18, hi=-.34), GRASS_DARK, ol=OL_MAIN)
    d.line(vein(556, 936, 198, 76, .78), OL_FINE)
    d.form(stem_slim(506, 620, BASE_Y, 72, root_seed=13.7, lean=-18,
                     w_base=196, root_lobes=3, root_depth=(18, 30)),
           GRASS, sweep(518, 830, 60, 190, lo=.06, hi=-.12, wob=.03),
           GRASS_DEEP)
    # ---- the quill, behind the head ----
    qs = bow(486, 236, 322, 128, 0.46, 8)
    d.form(ribbon(qs, [46, 42, 36, 30, 24, 18, 13, 9], cap0="flat",
                  cap1="point"), BARK_DEEP,
           sweep(400, 176, 92, 62, lo=.24, hi=-.38), INK_SOFT, ol=OL_MAIN)
    # ---- body ----
    d.form(circ(488, 544, 214, 3.4, 13, .035, 218, -5), BARK_LITE,
           sweep(488, 544, 214, 218, lo=.30, hi=-.44, wob=.07), BARK)
    # wings: one fat paddle over each flank, the near one bigger
    d.form(leaf_round(348, 520, 244, 152, -116, .12), BARK,
           sweep(240, 476, 106, 88, lo=.24, hi=-.40), BARK_DEEP, ol=OL_MAIN)
    d.line(vein(348, 520, 210, -116, .74), OL_FINE)
    d.form(leaf_round(626, 506, 198, 132, 112, -.12), BARK,
           sweep(710, 470, 92, 76, lo=.22, hi=-.38), BARK_DEEP, ol=OL_MAIN)
    d.line(vein(626, 506, 168, 112, .70), OL_FINE)
    # tail, poking out low right
    d.form(leaf_pointed(646, 636, 348, 126, 106, -.18), BARK_LITE,
           sweep(818, 690, 140, 84, lo=.22, hi=-.36), BARK, ol=OL_MAIN)
    # quail speckles: flat, unoutlined pattern
    for (sx, sy, dg) in ((398, 594, -22), (462, 654, 14), (540, 606, -8),
                         (580, 668, 26), (424, 706, -30), (516, 720, 6),
                         (594, 552, 18), (356, 630, -14)):
        d.fill(slab(sx, sy, 62, 27, 0.50, dg), BARK_DEEP)
    # ---- head ----
    d.form(circ(504, 320, 154, 8.1, 12, .035, 146, 3), BARK_LITE,
           sweep(504, 320, 154, 146, lo=.30, hi=-.44, wob=.07), BARK)
    # beak, jutting LEFT clear of the mass
    d.form(hard_poly([(372, 300), (262, 336), (372, 372)], 16), SUN_DEEP,
           sweep_hard(334, 338, 46, 30, lo=.24, hi=-.30), RAY_SHADE,
           ol=OL_PROP)
    d.line("M368,336 L286,338", OL_FINE)
    # a pale cheek stripe -- the quail's field mark
    d.fill(leaf_pointed(566, 404, 128, 58, 26, .10), CREAM)
    # chin line: keeps the head from melting into the body at game size
    d.line("M382,394 C436,452 566,458 626,388", OL_MAIN)
    # ODDITY: the quill has one loose barb sticking out sideways
    d.form(ribbon(bow(392, 178, 470, 106, -0.32, 5), [22, 17, 12, 8, 5],
                  cap0="flat", cap1="point"), BARK_DEEP,
           sweep(430, 142, 44, 34, lo=.24, hi=-.38), INK_SOFT, ol=OL_FINE)
    d.add(face(516, 322, 160, mass_w=308, default="mischief", tilt=-3.0,
               eyes=((-48, -18), (44, -24)), eye_r=(17, 20), mouth=(-2, 56),
               mouth_k=0.78, brow_lift=6))
    return d.svg()


# =====================================================================
# 5. q-quackers-duckbloom   WACKY -- face
#    Five fat petals, a broad orange bill across the disc, and two webbed
#    feet standing in the soil instead of root lobes.
# =====================================================================
def quackers_duckbloom():
    d = Doc()
    # ---- one long leaf, behind ----
    d.form(leaf_pointed(448, 800, 262, 138, -76, .18), GRASS,
           sweep(320, 720, 128, 100, lo=.20, hi=-.36), GRASS_DEEP, ol=OL_MAIN)
    d.line(vein(448, 800, 226, -76, .78), OL_FINE)
    d.form(leaf_pointed(566, 862, 222, 122, 72, -.16), GRASS_DEEP,
           sweep(680, 800, 108, 88, lo=.18, hi=-.34), GRASS_DARK, ol=OL_MAIN)
    d.line(vein(566, 862, 190, 72, .78), OL_FINE)
    # ---- stem ----
    d.form(stem_slim(506, 566, 946, 86, root_seed=44.2, lean=12,
                     w_base=180, root_lobes=2, root_depth=(14, 24)),
           GRASS, sweep(520, 780, 70, 200, lo=.06, hi=-.12, wob=.03),
           GRASS_DEEP)
    # ---- webbed feet: the ground anchor, and the joke ----
    for (fx, sgn, sd) in ((338, -1, 2.2), (692, 1, 5.5)):
        d.form(smooth_closed([(fx - 92 * 1, 946), (fx + 86, 950),
                              (fx + 96 * sgn * .4 + 74, 1000),
                              (fx + 26, 978), (fx + 2, 1000),
                              (fx - 42, 976), (fx - 78, 998)]),
               ACCENT, sweep(fx, 972, 92, 30, lo=.24, hi=-.34), ACCENT_DEEP,
               ol=OL_PROP)
    # ---- five fat petals ----
    petal_ring(d, 508, 336, 6, 112, 358, 224, SUN_DEEP, RAY_SHADE, 21.4,
               ol=OL_MAIN, start=-104, curl=0.08, sq=0.60)
    # ---- the disc the face sits on ----
    d.form(circ(508, 330, 192, 6.2, 12, .035, 144, -3), SUN,
           sweep(508, 330, 192, 144, lo=.30, hi=-.44, wob=.06), SUN_SHADE)
    # ---- the bill ----
    d.form(smooth_closed([(356, 372), (508, 348), (660, 374), (684, 424),
                          (622, 476), (508, 492), (394, 474), (334, 422)]),
           ACCENT, sweep(508, 420, 172, 66, lo=.26, hi=-.38), ACCENT_DEEP,
           ol=OL_MAIN)
    d.line("M362,392 C462,368 556,368 656,394", OL_FINE)
    # ODDITY: one petal has flopped right forward, hanging over the bill
    d.form(leaf_round(756, 268, 196, 128, 156, -.16), SUN_DEEP,
           sweep(778, 372, 74, 74, lo=.24, hi=-.40), RAY_SHADE, ol=OL_MAIN)
    d.line(vein(756, 268, 168, 156, .74), OL_FINE)
    d.add(face(508, 330, 250, mass_w=480, default="surprised", tilt=-2.0,
               eyes=((-58, -46), (60, -52)), eye_r=(22, 25), mouth=(0, 72),
               mouth_k=1.10, brow_lift=10))
    return d.svg()


# =====================================================================
# 6. r-red-rose   REALISTIC -- no face
#    One spiralled bloom, a thorned stem and two compound leaf sprays.
# =====================================================================
def red_rose():
    d = Doc()
    # ---- stem ----
    d.form(stem_slim(500, 508, BASE_Y, 68, root_seed=52.8, lean=14,
                     w_base=188, root_lobes=3, root_depth=(16, 28)),
           GRASS_DEEP, sweep(516, 760, 58, 236, lo=.06, hi=-.12, wob=.03),
           GRASS_DARK)
    # thorns
    for (tx, ty, dg) in ((452, 640, -104), (556, 742, 96), (462, 848, -100)):
        d.form(horn(tx, ty, 74, 44, dg, .18), GRASS_DEEP,
               sweep(tx, ty, 38, 30, lo=.24, hi=-.38), GRASS_DARK, ol=OL_FINE)
    # ---- two compound leaf sprays ----
    for (bx, by, sgn, sd) in ((360, 706, -1, 3.3), (696, 792, 1, 6.6),
                              (790, 836, 1, 9.9)):
        for (dx, dy, L, dg) in ((0, 0, 200, -66 * -sgn if sgn < 0 else 66),
                                (-58 * sgn, -78, 168, -34 if sgn < 0 else 34),
                                (-70 * sgn, 66, 160, -96 if sgn < 0 else 96)):
            d.form(leaf_pointed(bx + dx, by + dy, L, L * .58, dg, .14 * sgn),
                   GRASS, sweep(bx + dx, by + dy - L * .4, L * .32, L * .34,
                                lo=.22, hi=-.38, seed=sd + L), GRASS_DEEP,
                   ol=OL_PROP)
            d.line(vein(bx + dx, by + dy, L * .88, dg, .76), OL_FINE)
    # ---- the bloom ----
    petal_ring(d, 496, 368, 6, 132, 268, 214, FRUIT, FRUIT_DEEP, 9.4,
               ol=OL_MAIN, start=-86, curl=0.12)
    J, B = lobe_profile(58.1, 9, jit=0.075, bul=(38, 84))
    coil = ("".join('<path d="M%.1f,%.1f%s" fill="none" stroke="%s" '
                    'stroke-width="%d" %s/>'
                    % (p[0][0], p[0][1], smooth_open(p), INK, OL_MAIN, RJ)
                    for p in [spiral_pts(496, 368, 164, 1.55, -52, 16, .86),
                              spiral_pts(486, 382, 114, 1.20, 118, 12, .80)]))
    cres = ('<path d="%s" fill="%s"/>'
            % (leaf_round(548, 460, 156, 120, 158, .10), FRUIT_DEEP))
    d.form(canopy_blob(496, 368, 190, 178, 9, J, B, start=-96), FRUIT,
           sweep(496, 368, 190, 178, lo=.30, hi=-.44, wob=.07), FRUIT_DEEP,
           inner=cres + coil)
    # a third stem carries a tight bud out to the right
    d.form(branch(520, 620, 830, 424, 40, 26, -0.18, 6), GRASS_DEEP,
           sweep(674, 520, 160, 110, lo=.16, hi=-.26), GRASS_DARK,
           ol=OL_PROP)
    d.form(circ(852, 372, 72, 26.4, 11, .06, 92, 12), FRUIT,
           sweep(852, 372, 72, 92, lo=.28, hi=-.42), FRUIT_DEEP, ol=OL_PROP)
    for (dg, L, Wd) in ((-146, 128, 54), (-16, 120, 50), (156, 116, 48)):
        d.form(leaf_pointed(852, 430, L, Wd, dg, .12), GRASS_DEEP,
               sweep(852, 384, Wd * .6, L * .34, lo=.24, hi=-.38, seed=dg),
               GRASS_DARK, ol=OL_FINE)
    # a second bloom, still a bud, on its own stem to the left
    d.form(branch(486, 660, 250, 486, 44, 30, 0.16, 6), GRASS_DEEP,
           sweep(368, 574, 130, 100, lo=.16, hi=-.26), GRASS_DARK,
           ol=OL_PROP)
    d.form(circ(238, 428, 92, 18.3, 11, .06, 116, -10), FRUIT,
           sweep(238, 428, 92, 116, lo=.28, hi=-.42), FRUIT_DEEP)
    for (dg, L, Wd) in ((-152, 158, 66), (-24, 148, 62), (150, 142, 60)):
        d.form(leaf_pointed(238, 500, L, Wd, dg, .12), GRASS_DEEP,
               sweep(238, 440, Wd * .6, L * .34, lo=.24, hi=-.38, seed=dg),
               GRASS_DARK, ol=OL_FINE)
    # ODDITY: one petal has dropped and lies on the soil
    d.form(leaf_round(316, 916, 118, 90, 106, .12), FRUIT,
           sweep(266, 906, 54, 38, lo=.24, hi=-.38), FRUIT_DEEP, ol=OL_PROP)
    d.line(vein(316, 916, 100, 106, .72), OL_FINE)
    return d.svg()


# =====================================================================
# 7. r-rabbit-radish   SILLY -- face
#    A round red radish with two tall cream ears, a leafy tuft between
#    them and a pale taproot that IS the ground anchor.
# =====================================================================
def rabbit_radish():
    d = Doc()
    # ---- the taproot: the ground anchor ----
    d.form(ribbon(bow(516, 792, 556, BASE_Y, -0.22, 7),
                  [78, 66, 54, 44, 34, 24, 15], cap0="flat", cap1="point"),
           CREAM, sweep(536, 900, 44, 106, lo=.20, hi=-.30), CREAM_DEEP)
    # ---- ears, behind the body ----
    for (ex, ey, L, Wd, dg, sd) in ((392, 452, 384, 158, -13, 2.1),
                                    (620, 440, 372, 150, 12, 4.2)):
        d.form(leaf_pointed(ex, ey, L, Wd, dg, .06), CREAM,
               sweep(ex, ey - L * .5, Wd * .62, L * .40, lo=.26, hi=-.42,
                     seed=sd), CREAM_DEEP)
        d.fill(leaf_pointed(ex, ey - 34, L * .64, Wd * .52, dg, .06), ACCENT)
    # ---- the leafy tuft ----
    for (dg, L, Wd, col) in ((-40, 214, 132, GRASS_DEEP), (38, 206, 128,
                                                           GRASS_DEEP),
                             (-14, 244, 142, GRASS), (16, 236, 138, LEAF)):
        d.form(leaf_round(506, 456, L, Wd, dg, .10), col,
               sweep(506 + L * .3 * math.sin(math.radians(dg)),
                     456 - L * .5, Wd * .6, L * .34, lo=.24, hi=-.40,
                     seed=dg), None, ol=OL_MAIN)
        d.line(vein(506, 456, L * .86, dg, .78), OL_FINE)
    # ---- the radish body ----
    d.form(circ(504, 626, 246, 7.3, 13, .035, 224, -4), FRUIT,
           sweep(504, 626, 246, 224, lo=.30, hi=-.44, wob=.07), FRUIT_DEEP)
    # a pale shoulder band where the leaves emerge
    d.fill(leaf_round(504, 452, 118, 300, 0, .0), CREAM_DEEP)
    # ODDITY: the left ear is folded over at the tip
    d.form(leaf_round(352, 214, 156, 118, -128, .16), CREAM,
           sweep(286, 200, 66, 52, lo=.26, hi=-.42), CREAM_DEEP, ol=OL_PROP)
    d.add(face(506, 626, 256, mass_w=492, default="delighted", tilt=-2.0,
               eyes=((-58, -6), (60, -12)), eye_r=(23, 27), mouth=(0, 52),
               mouth_k=1.05))
    return d.svg()


# =====================================================================
# 8. s-snail-snapdragon   SILLY -- face on the SNAIL
#    A TALL alternating spike of pouch blooms, with a big snail riding a
#    side leaf low-right so the mass is L-shaped, not a disc on a stick.
# =====================================================================
def _pouch(d, cx, cy, w, h, dg, base, shade):
    """One snapdragon pouch bloom: fat lower lip, small upper hood."""
    p = smooth_closed(place([(-w * .50, -h * .10), (-w * .40, -h * .48),
                             (0, -h * .58), (w * .44, -h * .40),
                             (w * .58, h * .04), (w * .40, h * .46),
                             (0, h * .58), (-w * .44, h * .42)],
                            cx, cy, dg))
    d.form(p, base, sweep(cx, cy, w * .5, h * .5, lo=.28, hi=-.42, wob=.08,
                          seed=cx * .02), shade, ol=OL_MAIN)
    q = place([(-w * .46, h * .06), (w * .10, h * .16), (w * .50, h * .00)],
              cx, cy, dg)
    d.line("M%.1f,%.1f Q%.1f,%.1f %.1f,%.1f" % (q[0] + q[1] + q[2]), OL_FINE)
    t = place([(w * .16, -h * .06)], cx, cy, dg)[0]
    d.fill(circ(t[0], t[1], w * .17, cx * .01, 9, .08, h * .17), SUN)


def snail_snapdragon():
    d = Doc()
    # ---- the spike ----
    d.form(stem_slim(512, 232, BASE_Y, 78, root_seed=66.3, lean=8,
                     w_base=214, root_lobes=3, root_depth=(18, 30)),
           GRASS, sweep(526, 640, 64, 380, lo=.06, hi=-.12, wob=.03),
           GRASS_DEEP)
    # side leaves off the spike
    for (bx, by, L, Wd, dg, col, sh) in (
            (486, 546, 224, 118, -74, GRASS, GRASS_DEEP),
            (536, 700, 206, 112, 76, GRASS_DEEP, GRASS_DARK),
            (486, 862, 188, 104, -80, GRASS, GRASS_DEEP)):
        d.form(leaf_pointed(bx, by, L, Wd, dg, .14), col,
               sweep(bx, by - L * .4, Wd * .6, L * .34, lo=.22, hi=-.36,
                     seed=by * .02), sh, ol=OL_PROP)
        d.line(vein(bx, by, L * .86, dg, .76), OL_FINE)
    # ---- pouch blooms, alternating left/right up the spike ----
    for (bx, by, w, h, dg, col, sh) in (
            (440, 486, 214, 168, -16, FRUIT, FRUIT_DEEP),
            (586, 398, 208, 162, 14, EMBER, EMBER_DEEP),
            (438, 306, 200, 156, -13, FRUIT, FRUIT_DEEP),
            (574, 224, 190, 148, 12, EMBER, EMBER_DEEP),
            (486, 146, 176, 138, -6, FRUIT, FRUIT_DEEP)):
        _pouch(d, bx, by, w, h, dg, col, sh)
    # ---- the snail's leaf platform ----
    d.form(leaf_round(556, 782, 350, 190, 96, -.10), GRASS_DEEP,
           sweep(730, 800, 150, 84, lo=.22, hi=-.36), GRASS_DARK)
    d.line(vein(556, 782, 300, 96, .80), OL_FINE)
    # ---- the snail ----
    d.form(smooth_closed([(556, 776), (620, 736), (742, 726), (836, 742),
                          (872, 776), (838, 800), (700, 806), (594, 802)]),
           BARK_LITE, sweep(716, 776, 158, 40, lo=.22, hi=-.34), BARK)
    d.form(circ(620, 704, 128, 11.2, 12, .035, 118, -6), BARK_LITE,
           sweep(620, 704, 128, 118, lo=.28, hi=-.42), BARK)
    # shell
    sh = circ(776, 664, 138, 14.4, 13, .030, 130, 5)
    d.form(sh, SUN_DEEP, sweep(776, 664, 138, 130, lo=.30, hi=-.44),
           RAY_SHADE,
           inner=('<path d="M%.1f,%.1f%s" fill="none" stroke="%s" '
                  'stroke-width="%d" %s/>'
                  % (spiral_pts(776, 664, 112, 1.7, -40, 16, .88)[0][0],
                     spiral_pts(776, 664, 112, 1.7, -40, 16, .88)[0][1],
                     smooth_open(spiral_pts(776, 664, 112, 1.7, -40, 16,
                                            .88)), INK, OL_MAIN, RJ)))
    # eye stalks
    for (sx, sy, tx, ty, k) in ((586, 626, 528, 542, 0.26),
                                (646, 616, 622, 518, -0.22)):
        st = bow(sx, sy, tx, ty, k, 5)
        d.form(ribbon(st, [30, 27, 24, 22, 21], cap0="flat", cap1="round"),
               BARK_LITE, sweep((sx + tx) / 2, (sy + ty) / 2, 30, 60,
                                lo=.22, hi=-.34), BARK, ol=OL_FINE)
        ball(d, tx, ty, 30, CREAM, tx * .01, OL_FINE, shade=CREAM_DEEP)
        d.fill(circ(tx - 4, ty - 3, 13, tx * .02, 8, .06, 15), INK_SOFT)
    # ODDITY: a glistening slime trail behind the snail, hue-matched
    swoosh(d, 906, 792, 596, 812, 0.10, CREAM_DEEP, OL_BG)
    d.add(face(614, 706, 128, mass_w=252, default="happy", tilt=-4.0,
               eyes=((-52, 4), (50, -2)), eye_r=(20, 22), mouth=(-4, 60),
               mouth_k=1.15))
    return d.svg()


# =====================================================================
# 9. s-sock-sprout   "Stinky Sock Sprout"   WACKY -- face on the red sock
#    A bare clothesline of a plant: three splayed legs, two arching arms
#    and a sock swinging off each. The silhouette is an ARCH with holes.
# =====================================================================
def _sock(d, cx, cy, w, h, dg, base, shade, flip=1):
    p = [(-.46, -.52), (.46, -.52), (.50, .06), (.34, .40), (-.16, .54),
         (-.86, .50), (-1.06, .22), (-.90, -.04), (-.44, -.06)]
    p = [(x * flip * w, y * h) for x, y in p]
    body = smooth_closed(place(p, cx, cy, dg))
    d.form(body, base, sweep(cx, cy, w * .62, h * .52, lo=.28, hi=-.42,
                             wob=.08, seed=cx * .02), shade)
    # cuff
    cw, ch = w * .96, h * .26
    d.form(slab(cx - flip * w * .02, cy - h * .50, cw, ch, 0.30, dg), CREAM,
           sweep_hard(cx, cy - h * .50, cw * .30, ch * .5, lo=.22, hi=-.30),
           CREAM_DEEP, ol=OL_PROP)
    # heel seam
    q = place([(-.40 * flip * w, .10 * h), (-.62 * flip * w, .44 * h)],
              cx, cy, dg)
    d.line("M%.1f,%.1f Q%.1f,%.1f %.1f,%.1f"
           % (q[0][0], q[0][1], q[0][0] - flip * w * .22, q[1][1] - h * .12,
              q[1][0], q[1][1]), OL_FINE)
    return body


def sock_sprout():
    d = Doc()
    # ---- the splayed three-legged stalk ----
    d.form(trunk_chunky(508, 288, BASE_Y, 96, 214, root_seed=71.9, lean=-6,
                        root_lobes=3, root_depth=(64, 132), flare=1.34),
           GRASS, sweep(526, 700, 96, 340, lo=.10, hi=-.14, wob=.05),
           GRASS_DEEP,
           inner=('<path d="M446,470 C462,610 452,760 466,900" fill="none" '
                  'stroke="%s" stroke-width="%d" %s/>' % (INK, OL_MAIN, RJ)))
    # ---- two arching arms ----
    for (x1, y1, k, w0, w1) in ((286, 404, 0.36, 76, 46),
                                (742, 388, -0.32, 72, 44)):
        d.form(branch(508, 316, x1, y1, w0, w1, k, 7), GRASS,
               sweep((508 + x1) / 2, (316 + y1) / 2, 130, 70, lo=.20,
                     hi=-.32, seed=x1 * .01), GRASS_DEEP)
    # a stub arm with nothing on it
    d.form(branch(512, 306, 596, 214, 52, 30, -0.24, 6), GRASS_DEEP,
           sweep(556, 260, 60, 50, lo=.20, hi=-.34), GRASS_DARK, ol=OL_MAIN)
    # ---- stink squiggles: background weight, hue-matched, never black ----
    swoosh(d, 252, 372, 208, 176, 0.42, GRASS_DARK)
    swoosh(d, 320, 356, 356, 168, -0.44, GRASS_DARK)
    swoosh(d, 286, 348, 274, 118, 0.30, GRASS_DARK)
    # ---- the socks ----
    _sock(d, 288, 606, 236, 348, -7, FRUIT, FRUIT_DEEP, 1)
    # ODDITY: the blue sock hangs upside-down, toe in the air, with a hole
    _sock(d, 748, 596, 224, 332, 186, SKY_HI, SKY_DEEP, 1)
    d.form(circ(690, 508, 44, 4.4, 9, .08, 36, 12), CREAM,
           sweep(690, 508, 44, 36, lo=.26, hi=-.40), CREAM_DEEP, ol=OL_FINE)
    d.add(face(292, 636, 128, mass_w=246, default="mischief", tilt=-5.0,
               eyes=((-50, -10), (46, -16)), eye_r=(21, 24), mouth=(-4, 54),
               mouth_k=1.10, brow_lift=4))
    return d.svg()


# =====================================================================
# 10. t-tomato   REALISTIC -- no face
#     One big low-slung fruit under a five-point calyx, two broad leaves
#     and a little green truss fruit off to the right.
# =====================================================================
def tomato():
    d = Doc()
    # ---- stem, behind ----
    d.form(stem_slim(496, 330, BASE_Y, 70, root_seed=83.4, lean=10,
                     w_base=192, root_lobes=3, root_depth=(16, 28)),
           GRASS_DEEP, sweep(510, 700, 60, 300, lo=.06, hi=-.12, wob=.03),
           GRASS_DARK)
    # ---- two broad leaves, low and wide ----
    for (bx, by, L, Wd, dg, col, sh, sd) in (
            (352, 848, 342, 196, -94, GRASS, GRASS_DEEP, 2.5),
            (662, 872, 322, 188, 92, GRASS_DEEP, GRASS_DARK, 5.0)):
        d.form(leaf_round(bx, by, L, Wd, dg, .10), col,
               sweep(bx + (L * .5 if dg > 0 else -L * .5), by - 40,
                     Wd * .62, L * .30, lo=.22, hi=-.36, seed=sd), sh)
        d.line(vein(bx, by, L * .88, dg, .80), OL_FINE)
    # a side truss with one green tomato -- and the ODDITY, it is unripe
    d.form(branch(500, 520, 826, 570, 34, 26, -0.22, 6), GRASS_DEEP,
           sweep(660, 546, 160, 40, lo=.20, hi=-.32), GRASS_DARK, ol=OL_PROP)
    ball(d, 866, 632, 92, LEAF, 9.1, OL_PROP, ry=86, shade=GRASS, gloss=0.30)
    d.form(circ(838, 800, 74, 12.3, 11, .04, 70, 4), FRUIT,
           sweep(838, 800, 74, 70, lo=.28, hi=-.42), FRUIT_DEEP, ol=OL_PROP)
    d.line("M844,732 C860,750 866,772 862,796", OL_FINE)
    # ---- the fruit ----
    d.form(circ(430, 654, 262, 6.8, 14, .028, 242, -3), FRUIT,
           sweep(430, 654, 262, 242, lo=.30, hi=-.44, wob=.06), FRUIT_DEEP,
           inner=('<path d="M208,594 C272,544 358,516 444,518" fill="none" '
                  'stroke="%s" stroke-width="%d" %s/>' % (INK, OL_MAIN, RJ)))
    # ---- the calyx ----
    for (dg, L, Wd) in ((-154, 258, 124), (-112, 274, 128), (-58, 246, 118),
                        (16, 268, 124), (72, 254, 120), (136, 234, 112)):
        d.form(leaf_pointed(432, 428, L, Wd, dg, .12), GRASS_DEEP,
               sweep(432, 372, Wd * .6, L * .34, lo=.24, hi=-.38, seed=dg),
               GRASS_DARK, ol=OL_PROP)
    d.form(slab(438, 328, 48, 132, 0.36, -4), GRASS_DEEP,
           sweep_hard(438, 328, 18, 56, lo=.22, hi=-.30), GRASS_DARK,
           ol=OL_PROP)
    d.form(leaf_pointed(438, 278, 176, 100, -34, .14), GRASS,
           sweep(394, 216, 60, 60, lo=.22, hi=-.36), GRASS_DEEP, ol=OL_PROP)
    return d.svg()


# =====================================================================
# 11. t-turtle-tulip   SILLY -- face on the TURTLE
#     A wide low shell at the soil line with a single tall tulip growing
#     out of it: the mass is a T, not a disc on a stick.
# =====================================================================
def turtle_tulip():
    d = Doc()
    # ---- two long leaves flanking the stem ----
    d.form(leaf_blade(556, 800, 320, 288, 46, 20, 74), GRASS,
           sweep(440, 540, 130, 250, lo=.20, hi=-.34), GRASS_DEEP)
    d.form(leaf_blade(576, 812, 780, 316, 44, 19, -68), GRASS_DEEP,
           sweep(680, 560, 120, 244, lo=.18, hi=-.32), GRASS_DARK)
    # ---- the tulip stem ----
    d.form(ribbon(bow(566, 322, 572, 812, -0.05, 7),
                  [56, 58, 60, 62, 64, 66, 70], cap0="round", cap1="flat"),
           GRASS, sweep(570, 560, 40, 250, lo=.08, hi=-.14), GRASS_DEEP)
    # ---- the tulip cup: three petals ----
    for (px, py, L, Wd, dg, col, sh) in (
            (566, 386, 226, 178, -26, FRUIT, FRUIT_DEEP),
            (566, 390, 222, 174, 24, FRUIT, FRUIT_DEEP),
            (566, 394, 244, 186, -2, EMBER, EMBER_DEEP)):
        d.form(leaf_pointed(px, py, L, Wd, dg, .10), col,
               sweep(px, py - L * .5, Wd * .6, L * .36, lo=.26, hi=-.42,
                     seed=dg), sh)
    d.line("M566,372 C560,300 566,238 570,186", OL_FINE)
    # ---- the turtle: four stubby legs, then the shell ----
    for (lx, ly, lw, lh, dg) in ((316, 942, 118, 96, -8), (472, 954, 112, 92,
                                                           4),
                                 (654, 946, 116, 94, -5), (786, 936, 104, 88,
                                                           7)):
        d.form(slab(lx, ly, lw, lh, 0.34, dg), GRASS_DEEP,
               sweep_hard(lx, ly, lw * .3, lh * .4, lo=.22, hi=-.30),
               GRASS_DARK, ol=OL_PROP)
    # head
    d.form(circ(238, 828, 124, 3.7, 12, .035, 114, -6), LEAF,
           sweep(238, 828, 124, 114, lo=.28, hi=-.42), GRASS)
    d.form(ribbon(bow(300, 856, 392, 878, 0.10, 5), [104, 108, 112, 116, 120],
                  cap0="flat", cap1="flat"), LEAF,
           sweep(346, 866, 60, 60, lo=.24, hi=-.36), GRASS, ol=OL_MAIN)
    # shell
    J, B = lobe_profile(64.5, 11, jit=0.055, bul=(16, 40))
    d.form(canopy_blob(556, 830, 292, 176, 11, J, B, start=-172), GRASS_DEEP,
           sweep(556, 830, 292, 176, lo=.28, hi=-.42, wob=.05), GRASS_DARK)
    for (sx, sy, r, dg) in ((430, 782, 74, -8), (566, 758, 82, 5),
                            (700, 786, 70, 10), (490, 872, 66, -4),
                            (636, 878, 62, 6)):
        d.fill(slab(sx, sy, r * 1.7, r * 1.3, 0.28, dg), GRASS)
    # ODDITY: a tiny second sprout has pushed up through one shell scute
    d.form(leaf_round(756, 736, 96, 62, 34, .12), LEAF,
           sweep(786, 700, 40, 30, lo=.24, hi=-.38), GRASS, ol=OL_FINE)
    d.add(face(238, 832, 124, mass_w=248, default="sleepy", tilt=-3.0,
               eyes=((-46, -6), (48, -12)), eye_r=(20, 22), mouth=(0, 52),
               mouth_k=0.95, brow_lift=4))
    return d.svg()


# =====================================================================
# 12. t-taco-tree   WACKY -- face on the SHELL
#     A hard taco shell as the canopy on a stubby armed trunk. The mass is
#     a DOME WITH A FLAT BOTTOM and a fringe of filling hanging under it.
# =====================================================================
def taco_tree():
    d = Doc()
    # ---- the stubby trunk ----
    d.form(trunk_chunky(508, 560, BASE_Y, 250, 356, root_seed=88.6, lean=4,
                        root_lobes=4, root_depth=(26, 48), flare=1.08),
           BARK, sweep(534, 780, 168, 226, lo=.14, hi=-.14, wob=.06),
           BARK_DEEP,
           inner=('<path d="M424,634 C440,730 430,850 448,960" fill="none" '
                  'stroke="%s" stroke-width="%d" %s/>'
                  '<path d="M636,660 C650,760 642,860 656,952" fill="none" '
                  'stroke="%s" stroke-width="%d" %s/>'
                  % (INK, OL_MAIN, RJ, INK, OL_MAIN, RJ)))
    # two stubby arms
    for (x1, y1, k, w0, w1, bx0, by0) in (
            (146, 848, 0.28, 84, 60, 380, 690),
            (908, 332, -0.26, 80, 56, 640, 646)):
        d.form(branch(bx0, by0, x1, y1, w0, w1, k, 7),
               BARK, sweep((bx0 + x1) / 2, (by0 + y1) / 2, 150, 130, lo=.20,
                           hi=-.32, seed=x1 * .01), BARK_DEEP)
        ball(d, x1, y1, 54, BARK, x1 * .01, OL_MAIN, ry=48, shade=BARK_DEEP)
    # ---- the filling, hanging under the shell ----
    J, B = lobe_profile(29.7, 15, jit=0.11, bul=(22, 52))
    d.form(canopy_blob(496, 534, 350, 96, 15, J, B, start=-6), LEAF,
           sweep(496, 534, 350, 96, lo=.26, hi=-.40, wob=.10), GRASS)
    for (fx, fy, r, col, sh, sd) in ((236, 568, 50, FRUIT, FRUIT_DEEP, 1.2),
                                     (428, 590, 46, FRUIT, FRUIT_DEEP, 2.4),
                                     (644, 584, 48, FRUIT, FRUIT_DEEP, 3.6),
                                     (800, 556, 44, FRUIT, FRUIT_DEEP, 4.8)):
        d.form(slab(fx, fy, r * 1.8, r * 1.5, 0.22, sd * 7), col,
               sweep_hard(fx, fy, r * .6, r * .5), sh, ol=OL_FINE)
    for (cx2, cy2, dg) in ((330, 592, 14), (536, 602, -10), (720, 590, 20)):
        d.fill(slab(cx2, cy2, 92, 30, 0.44, dg), SUN)
    # ---- the shell ----
    shell = smooth_closed(place(
        [(-322, 130), (-306, -40), (-208, -160), (-48, -212), (114, -198),
         (246, -122), (312, 8), (324, 130), (162, 142), (0, 148),
         (-166, 142)], 508, 386, 13))
    d.form(shell, SUN_DEEP, sweep(508, 404, 372, 200, lo=.30, hi=-.44,
                                  wob=.06), RAY_SHADE)
    # the folded front edge of the shell -- the taco tell
    d.line("M196,468 C372,424 646,462 812,554", OL_MAIN)
    d.line("M232,340 C290,278 368,238 442,220", OL_FINE)
    # ODDITY: one tomato cube has escaped and sits on the left arm
    # ...one cube held up in the raised right hand
    d.form(slab(916, 246, 92, 78, 0.22, 16), FRUIT,
           sweep_hard(916, 246, 32, 28), FRUIT_DEEP, ol=OL_PROP)
    # ...and a whole spill of filling has landed on the soil
    d.form(canopy_blob(226, 950, 148, 56, 11,
                       *lobe_profile(44.1, 11, jit=0.12, bul=(12, 34))),
           LEAF, sweep(226, 950, 148, 56, lo=.26, hi=-.40, wob=.10), GRASS,
           ol=OL_PROP)
    d.form(slab(178, 966, 74, 60, 0.22, -12), FRUIT,
           sweep_hard(178, 966, 26, 22), FRUIT_DEEP, ol=OL_FINE)
    d.fill(slab(286, 970, 84, 28, 0.44, 8), SUN)
    d.add(face(504, 358, 288, mass_w=580, default="delighted", tilt=5.0,
               eyes=((-62, -12), (64, -18)), eye_r=(23, 26), mouth=(2, 48),
               mouth_k=1.25))
    return d.svg()


# =====================================================================
# 13. u-umbrella-plant   REALISTIC -- no face
#     A potted schefflera: the ONLY pot in the alphabet, with whorls of
#     finger leaflets on long radiating stalks.
# =====================================================================
def _whorl(d, cx, cy, n, L, Wd, col, sh, sd, lo=-150, hi=150, ol=OL_PROP):
    j = jitter(sd, n, 0.12, 1.0)
    for i in range(n):
        dg = lo + (hi - lo) * i / float(n - 1) + (i % 2) * 5.0
        LL = L * j[i]
        d.form(leaf_round(cx, cy, LL, Wd * j[i], dg, .10), col,
               sweep(cx + LL * .34 * math.sin(math.radians(dg)),
                     cy - LL * .40 * math.cos(math.radians(dg)),
                     Wd * .52, LL * .34, lo=.24, hi=-.40, seed=sd + i),
               sh, ol=ol)


def umbrella_plant():
    d = Doc()
    STALK_Y = 676
    # ---- stalks ----
    for (tx, ty, k, w0, sd, col, sh) in (
            (338, 452, 0.16, 34, 1.1, GRASS_DEEP, GRASS_DARK),
            (676, 470, -0.16, 33, 2.2, GRASS_DEEP, GRASS_DARK),
            (386, 306, 0.10, 36, 3.3, GRASS, GRASS_DEEP),
            (630, 322, -0.11, 35, 4.4, GRASS, GRASS_DEEP),
            (512, 226, 0.03, 38, 5.5, GRASS, GRASS_DEEP)):
        d.form(branch(508, STALK_Y, tx, ty, w0 + 16, w0, k, 7), col,
               sweep((508 + tx) / 2, (STALK_Y + ty) / 2, 120, 180, lo=.16,
                     hi=-.26, seed=sd), sh, ol=OL_PROP)
    # ---- whorls, back rank hue-matched then front rank outlined ----
    for (wx, wy, n, L, Wd, col, sh, sd) in (
            (338, 452, 5, 152, 68, GRASS_DEEP, GRASS_DARK, 11.1),
            (676, 470, 5, 148, 66, GRASS_DEEP, GRASS_DARK, 12.2),
            (386, 306, 6, 158, 72, GRASS, GRASS_DEEP, 15.5),
            (630, 322, 6, 154, 70, GRASS, GRASS_DEEP, 16.6),
            (512, 226, 6, 164, 78, LEAF, GRASS, 17.7)):
        _whorl(d, wx, wy, n, L, Wd, col, sh, sd)
        d.form(circ(wx, wy, 30, sd, 8, .06, 28), col, None, sh, ol=OL_FINE)
    # ---- the pot: the only one in the alphabet, and deliberately huge ----
    d.form(hard_poly([(346, 752), (668, 752), (626, 1000), (392, 1000)], 26),
           ACCENT, sweep_hard(508, 880, 140, 122, lo=.22, hi=-.30),
           ACCENT_DEEP)
    d.form(slab(508, 706, 424, 92, 0.20, 0, 0.02), ACCENT,
           sweep_hard(508, 706, 150, 44, lo=.22, hi=-.30), ACCENT_DEEP)
    # soil showing over the rim
    d.fill(canopy_blob(508, 668, 178, 24, 9,
                       *lobe_profile(19.4, 9, jit=0.10, bul=(6, 16))),
           BARK_DEEP)
    # one long stalk arcs out of the pot to the right and droops
    d.form(branch(548, 672, 838, 578, 40, 28, -0.28, 8), GRASS_DEEP,
           sweep(690, 596, 168, 112, lo=.16, hi=-.26), GRASS_DARK,
           ol=OL_PROP)
    _whorl(d, 838, 578, 5, 138, 62, GRASS, GRASS_DEEP, 18.8)
    d.form(circ(838, 578, 26, 18.8, 8, .06, 24), GRASS, None, GRASS_DEEP,
           ol=OL_FINE)
    # ODDITY: one leaflet has gone yellow and droops off the low-left whorl
    d.form(leaf_round(330, 498, 172, 86, 168, .14), SUN,
           sweep(312, 586, 52, 54, lo=.24, hi=-.40), SUN_DEEP, ol=OL_PROP)
    return d.svg()


# =====================================================================
# 14. u-unicorn-flower   "Unicorn Bloom"   SILLY -- face
#     A broad soft bloom-head with a spiral golden horn on top and two
#     curled petal-ears. Wider than tall: no other flower head here is.
# =====================================================================
def unicorn_flower():
    d = Doc()
    # ---- stem + one leaf ----
    d.form(leaf_pointed(548, 828, 226, 124, 72, -.16), GRASS_DEEP,
           sweep(660, 768, 108, 88, lo=.18, hi=-.34), GRASS_DARK, ol=OL_MAIN)
    d.line(vein(548, 828, 194, 72, .78), OL_FINE)
    d.form(stem_slim(508, 596, BASE_Y, 96, root_seed=95.2, lean=-10,
                     w_base=236, root_lobes=3, root_depth=(18, 32)),
           GRASS, sweep(524, 800, 78, 200, lo=.06, hi=-.12, wob=.03),
           GRASS_DEEP)
    # ---- curled ears, behind the head ----
    for (cx0, cy0, r0, ang, sgn) in ((208, 344, 142, 26, 1),
                                     (816, 326, 136, 154, -1)):
        sp = spiral_pts(cx0, cy0, r0, 0.82, ang, 12, 0.72)
        d.form(ribbon(sp, [64, 60, 55, 50, 45, 40, 35, 31, 27, 23, 19, 15],
                      cap0="round", cap1="round"), BERRY,
               sweep(cx0, cy0, r0, r0, lo=.26, hi=-.40), BERRY_DEEP,
               ol=OL_MAIN)
    # ---- the horn, behind the head ----
    d.form(horn(500, 310, 226, 118, -4, .10), SUN,
           sweep(494, 214, 62, 96, lo=.24, hi=-.40), SUN_DEEP)
    for (hy, hw) in ((248, 96), (202, 74), (160, 52), (124, 32)):
        d.line("M%d,%d Q%d,%d %d,%d"
               % (500 - hw * .5, hy, 500, hy - 22, 500 + hw * .5, hy - 8),
               OL_FINE)
    # ---- the bloom head: WIDER than tall ----
    J, B = lobe_profile(73.6, 9, jit=0.075, bul=(30, 68))
    d.form(canopy_blob(508, 408, 282, 208, 9, J, B, start=-98), ACCENT,
           sweep(508, 408, 282, 208, lo=.30, hi=-.44, wob=.06), ACCENT_DEEP)
    # a soft forelock of petals over the brow
    for (fx, fy, L, Wd, dg) in ((424, 260, 128, 84, -26), (508, 242, 134, 88,
                                                           -4),
                                (588, 258, 124, 82, 22)):
        d.form(leaf_round(fx, fy + 96, L, Wd, dg, .12), ACCENT,
               sweep(fx, fy + 40, Wd * .5, L * .34, lo=.24, hi=-.40,
                     seed=fx * .01), ACCENT_DEEP, ol=OL_PROP)
    # ODDITY: one ear-curl has come unwound into a straight droopy strand
    d.form(ribbon(bow(768, 452, 872, 706, -0.22, 6), [42, 38, 33, 28, 22, 16],
                  cap0="flat", cap1="round"), BERRY,
           sweep(824, 580, 60, 130, lo=.22, hi=-.36), BERRY_DEEP, ol=OL_PROP)
    d.add(face(510, 416, 302, mass_w=558, default="delighted", tilt=-2.0,
               eyes=((-64, 2), (66, -4)), eye_r=(24, 27), mouth=(2, 62),
               mouth_k=1.20))
    return d.svg()


# =====================================================================
# 15. v-violet   REALISTIC -- no face
#     A LOW WIDE clump: heart leaves along the soil and six small five-
#     petal blooms on slim stalks. Nothing about it is a disc on a stick.
# =====================================================================
def _violet_bloom(d, cx, cy, r, col, sh, sd, dg=0.0):
    j = jitter(sd, 5, 0.10, 1.0)
    for i in range(5):
        a = dg - 90 + 72 * i + (i % 2) * 6
        rad = math.radians(a)
        bx, by = cx + r * .22 * math.cos(rad), cy + r * .22 * math.sin(rad)
        d.form(leaf_round(bx, by, r * .92 * j[i], r * .86 * j[i], a + 90,
                          .08), col,
               sweep(bx + r * .4 * math.cos(rad), by + r * .4 * math.sin(rad),
                     r * .40, r * .34, lo=.26, hi=-.42, seed=sd + i), sh,
               ol=OL_PROP)
    d.form(circ(cx, cy, r * .26, sd + 2, 8, .07, r * .24), SUN, None,
           SUN_DEEP, ol=OL_FINE)


def violet():
    d = Doc()
    # ---- heart leaves, a low mound ----
    for (lx, ly, L, Wd, dg, col, sh, sd) in (
            (250, 968, 288, 262, -62, GRASS_DEEP, GRASS_DARK, 1.1),
            (762, 972, 276, 252, 64, GRASS_DEEP, GRASS_DARK, 2.2),
            (398, 992, 258, 246, -26, GRASS, GRASS_DEEP, 3.3),
            (630, 996, 250, 240, 28, GRASS, GRASS_DEEP, 4.4),
            (512, 1000, 236, 250, 2, LEAF, GRASS, 5.5)):
        J, B = lobe_profile(sd * 3.1, 8, jit=0.09, bul=(26, 62))
        cy2 = ly - L * .52
        cx2 = lx + L * .34 * math.sin(math.radians(dg))
        d.form(canopy_blob(cx2, cy2, Wd * .52, L * .40, 8, J, B,
                           start=-96, notch=(3 if sd == 3.3 else None)),
               col, sweep(cx2, cy2, Wd * .52, L * .40, lo=.28, hi=-.42,
                          wob=.08, seed=sd), sh)
        d.line(vein(cx2, cy2 + L * .34, L * .52, dg * .4, .78), OL_FINE)
    # ---- stalks + blooms ----
    for (tx, ty, k, r, col, sh, sd) in (
            (250, 386, 0.16, 128, BERRY, BERRY_DEEP, 6.1),
            (752, 356, -0.16, 124, BERRY, BERRY_DEEP, 7.2),
            (382, 236, 0.09, 132, BERRY, BERRY_DEEP, 8.3),
            (630, 214, -0.10, 130, BERRY, BERRY_DEEP, 9.4),
            (508, 348, 0.02, 118, BERRY, BERRY_DEEP, 10.5)):
        d.form(branch(500, 860, tx, ty, 46, 30, k, 7), GRASS,
               sweep((500 + tx) / 2, (860 + ty) / 2, 90, 220, lo=.14,
                     hi=-.24, seed=sd), GRASS_DEEP, ol=OL_PROP)
        _violet_bloom(d, tx, ty, r, col, sh, sd, dg=(sd * 7) % 40 - 20)
    # ODDITY: one stalk carries a bud that has not opened
    d.form(branch(504, 850, 620, 458, 42, 28, -0.14, 6), GRASS,
           sweep(560, 654, 70, 200, lo=.14, hi=-.24), GRASS_DEEP, ol=OL_PROP)
    d.form(circ(624, 430, 66, 12.6, 10, .06, 82, 12), BERRY,
           sweep(624, 430, 66, 82, lo=.28, hi=-.42), BERRY_DEEP, ol=OL_PROP)
    return d.svg()


# =====================================================================
# 16. v-vole-vine   SILLY -- face on the VOLE
#     A tall S-curved vine with spiral tendrils; a grey vole leans out of
#     the middle bloom. Silhouette is a SNAKING RIBBON, not a mass.
# =====================================================================
def vole_vine():
    d = Doc()
    spine = [(566, 984), (532, 900), (426, 792), (398, 664), (492, 560),
             (606, 470), (596, 344), (486, 246), (398, 190)]
    d.form(ribbon(spine, [116, 100, 88, 82, 78, 74, 68, 60, 50],
                  cap0="flat", cap1="round"), GRASS,
           sweep(496, 600, 130, 400, lo=.16, hi=-.24, wob=.05), GRASS_DEEP)
    # spiral tendrils
    for (tx, ty, r0, ang, tn) in ((744, 566, 116, -40, 0.92),
                                  (272, 700, 104, 150, -0.86),
                                  (688, 258, 92, 20, 0.80)):
        sp = spiral_pts(tx, ty, r0, tn, ang, 13, 0.76)
        d.form(ribbon(sp, [44, 41, 38, 35, 32, 29, 26, 24, 22, 20, 18, 16,
                           14], cap0="round", cap1="round"), GRASS_DEEP,
               sweep(tx, ty, r0, r0, lo=.22, hi=-.36), GRASS_DARK,
               ol=OL_PROP)
    # leaves along the vine
    for (lx, ly, L, Wd, dg, col, sh) in (
            (420, 786, 208, 122, -84, GRASS_DEEP, GRASS_DARK),
            (600, 480, 194, 116, 88, GRASS, GRASS_DEEP),
            (452, 250, 178, 108, -92, GRASS, GRASS_DEEP)):
        d.form(leaf_round(lx, ly, L, Wd, dg, .10), col,
               sweep(lx, ly - L * .4, Wd * .6, L * .32, lo=.22, hi=-.36,
                     seed=ly * .02), sh, ol=OL_PROP)
        d.line(vein(lx, ly, L * .86, dg, .76), OL_FINE)
    # blooms
    _violet_bloom(d, 358, 214, 122, BERRY, BERRY_DEEP, 4.2, -14)
    _violet_bloom(d, 700, 848, 116, BERRY, BERRY_DEEP, 8.4, 22)
    _violet_bloom(d, 404, 560, 190, BERRY, BERRY_DEEP, 6.3, 6)
    # ---- the vole ----
    for (ex, ey, r) in ((300, 470, 74), (492, 462, 70)):
        d.form(circ(ex, ey, r, ex * .01, 10, .05, r * .96), STEEL,
               sweep(ex, ey, r, r, lo=.28, hi=-.42), STEEL_DEEP, ol=OL_PROP)
        d.fill(circ(ex + 4, ey + 6, r * .54, ex * .02, 9, .06, r * .52),
               ACCENT)
    d.form(circ(396, 528, 146, 5.9, 12, .035, 132, -4), STEEL,
           sweep(396, 528, 146, 132, lo=.30, hi=-.44), STEEL_DEEP)
    # snout + nose
    d.fill(circ(392, 578, 68, 7.1, 10, .05, 44, 2), CREAM)
    d.form(smooth_closed([(392, 546), (420, 560), (410, 584), (392, 592),
                          (372, 582), (364, 558)]), BERRY, None, BERRY_DEEP,
           ol=OL_FINE)
    # ODDITY: the vole is clutching one loose seed
    d.form(circ(302, 622, 46, 9.7, 9, .07, 38, 22), BARK,
           sweep(302, 622, 46, 38, lo=.26, hi=-.40), BARK_DEEP, ol=OL_FINE)
    d.add(face(398, 526, 138, mass_w=278, default="surprised", tilt=-3.0,
               eyes=((-50, -16), (52, -22)), eye_r=(20, 24), mouth=(-2, 66),
               mouth_k=0.85, brow_lift=8))
    return d.svg()


# =====================================================================
# 17. v-volcano-tree   WACKY -- face on the CONE
#     A broad banded cone erupting a fountain of lava blobs. The widest,
#     most bottom-heavy trapezoid in the set.
# =====================================================================
def volcano_tree():
    d = Doc()
    # ---- the lava fountain, behind the rim ----
    for (bx, by, r, col, sh, sd) in (
            (232, 410, 58, EMBER, EMBER_DEEP, 1.1),
            (802, 320, 54, EMBER, EMBER_DEEP, 2.2),
            (318, 262, 50, SUN_DEEP, RAY_SHADE, 3.3),
            (700, 176, 56, SUN_DEEP, RAY_SHADE, 4.4),
            (436, 146, 66, SUN, SUN_DEEP, 5.5),
            (160, 528, 46, FRUIT, FRUIT_DEEP, 6.6),
            (872, 430, 48, FRUIT, FRUIT_DEEP, 7.7),
            (398, 322, 42, SUN, SUN_DEEP, 8.8),
            (614, 300, 44, FRUIT, FRUIT_DEEP, 9.9),
            (566, 132, 44, EMBER, EMBER_DEEP, 11.0),
            (268, 336, 36, FRUIT, FRUIT_DEEP, 12.1),
            (786, 234, 40, SUN, SUN_DEEP, 13.2),
            (520, 220, 60, EMBER, EMBER_DEEP, 14.3),
            (638, 402, 38, SUN_DEEP, RAY_SHADE, 15.4),
            (352, 176, 34, FRUIT, FRUIT_DEEP, 16.5)):
        ball(d, bx, by, r, col, sd, OL_PROP, shade=sh, gloss=0.30)

    # ---- the cone ----
    cone = smooth_closed([(268, 1000), (306, 806), (376, 606), (424, 486),
                          (598, 480), (650, 606), (720, 806), (760, 1000),
                          (612, 986), (400, 990)])
    bands = "".join(
        '<path d="M%d,%d Q%d,%d %d,%d" fill="none" stroke="%s" '
        'stroke-width="%d" %s/>' % (ax, ay, (ax + bx) // 2, ay + 26, bx, by,
                                    INK, OL_MAIN, RJ)
        for (ax, ay, bx, by) in ((332, 720, 700, 726), (296, 866, 738, 872)))
    d.form(cone, BARK, sweep(512, 760, 250, 260, lo=.24, hi=-.24, wob=.05),
           BARK_DEEP, inner=bands)
    # the crater rim, with a molten pool sitting in it
    d.form(circ(510, 482, 142, 13.1, 11, .05, 54, -2), BARK_DEEP,
           sweep(510, 482, 142, 54, lo=.22, hi=-.34), INK_SOFT, ol=OL_MAIN)
    d.form(circ(506, 470, 108, 17.5, 10, .06, 38, -2), EMBER,
           sweep(506, 470, 108, 38, lo=.24, hi=-.38), EMBER_DEEP, ol=OL_PROP)
    # a lava dribble down the left flank
    d.form(ribbon(bow(424, 500, 372, 664, 0.18, 6),
                  [62, 56, 50, 44, 40, 44], cap0="flat", cap1="round"),
           EMBER, sweep(396, 582, 48, 84, lo=.22, hi=-.34), EMBER_DEEP,
           ol=OL_PROP)
    # ODDITY: one blob has already landed and sits smoking on the soil
    ball(d, 866, 950, 56, EMBER, 15.2, OL_PROP, ry=44, shade=EMBER_DEEP,
         gloss=0.30)
    swoosh(d, 866, 892, 892, 782, 0.26, ACCENT_DEEP)
    d.add(face(508, 764, 262, mass_w=460, default="mischief", tilt=-2.0,
               eyes=((-56, -14), (58, -20)), eye_r=(23, 25), mouth=(0, 58),
               mouth_k=1.20, brow_lift=14))
    return d.svg()


# =====================================================================
# 18. w-watermelon   REALISTIC -- no face
#     One big striped sphere LOW-LEFT with a cut wedge leaning on it, so
#     the mass is a wide double-lobe, not a single ball.
# =====================================================================
def watermelon():
    d = Doc()
    # ---- vine + leaf, behind ----
    d.form(ribbon(bow(452, 470, 268, 940, 0.24, 7),
                  [42, 40, 38, 36, 34, 32, 30], cap0="round", cap1="flat"),
           GRASS, sweep(352, 700, 90, 240, lo=.16, hi=-.26), GRASS_DEEP,
           ol=OL_PROP)
    d.form(leaf_round(268, 906, 232, 176, -50, .12), GRASS,
           sweep(214, 806, 96, 66, lo=.24, hi=-.38), GRASS_DEEP)
    d.line(vein(268, 906, 200, -50, .78), OL_FINE)
    d.form(ribbon(bow(506, 440, 648, 288, -0.24, 7),
                  [46, 42, 38, 34, 30, 26, 22], cap0="flat", cap1="round"),
           GRASS, sweep(576, 360, 90, 100, lo=.18, hi=-.28), GRASS_DEEP,
           ol=OL_PROP)
    d.form(leaf_round(642, 306, 234, 178, 26, .12), GRASS,
           sweep(704, 236, 96, 66, lo=.24, hi=-.38), GRASS_DEEP)
    d.line(vein(642, 306, 202, 26, .78), OL_FINE)
    d.form(leaf_round(566, 388, 176, 136, -36, .12), GRASS_DEEP,
           sweep(512, 330, 74, 52, lo=.24, hi=-.38), GRASS_DARK, ol=OL_PROP)
    sp = spiral_pts(722, 402, 92, 0.90, -10, 12, 0.74)
    d.form(ribbon(sp, [30, 28, 26, 24, 22, 20, 19, 18, 17, 16, 15, 14],
                  cap0="round", cap1="round"), GRASS_DEEP,
           sweep(722, 402, 92, 92, lo=.22, hi=-.36), GRASS_DARK, ol=OL_FINE)
    # ---- the melon ----
    stripes = "".join(
        '<path d="%s" fill="%s"/>'
        % (leaf_pointed(420 + dx, 668 + 300, 620, 116, dg, .06), GRASS_DARK)
        for (dx, dg) in ((-186, -28), (-92, -14), (4, 0), (100, 14),
                         (190, 28)))
    d.form(circ(420, 668, 268, 4.6, 14, .022, 256, -2), GRASS,
           sweep(420, 668, 268, 256, lo=.30, hi=-.46, wob=.05), GRASS_DEEP,
           inner=stripes)
    # ---- the cut wedge, leaning on the melon ----
    wedge = smooth_closed([(672, 970), (664, 742), (716, 582), (830, 490),
                           (940, 536), (972, 694), (952, 862), (888, 968),
                           (786, 986)])
    d.form(wedge, GRASS_DEEP, sweep(830, 760, 150, 250, lo=.26, hi=-.40),
           GRASS_DARK)
    d.form(smooth_closed([(692, 966), (684, 758), (732, 610), (832, 528),
                          (926, 572), (954, 710), (936, 866), (878, 968),
                          (786, 986)]), CREAM,
           sweep(830, 762, 132, 226, lo=.26, hi=-.40), CREAM_DEEP,
           ol=OL_PROP)
    d.form(smooth_closed([(720, 946), (712, 768), (756, 638), (836, 570),
                          (914, 610), (938, 722), (920, 858), (868, 948),
                          (790, 964)]), FRUIT,
           sweep(830, 768, 116, 202, lo=.26, hi=-.40), FRUIT_DEEP,
           ol=OL_PROP)
    for (sx, sy, dg) in ((796, 680, 12), (866, 728, -18), (778, 800, 24),
                         (878, 842, -8), (812, 890, 16)):
        d.fill(leaf_pointed(sx, sy + 24, 46, 26, dg, .0), INK_SOFT)
    # ODDITY: one pip has dropped out onto the soil
    d.fill(leaf_pointed(650, 984, 48, 28, 118, .0), INK_SOFT)
    return d.svg()


# =====================================================================
# 19. w-whale-wisteria   SILLY -- face on the WHALE
#     A thick vine up the RIGHT edge with two hanging racemes; a round
#     whale beached at the lower-left, spouting.
# =====================================================================
def _raceme(d, cx, cy, L, w, sd, col=BERRY, sh=BERRY_DEEP):
    """A drooping wisteria cluster: pearls that shrink towards the tip."""
    n = 9
    rs = graduated(n, w * .50, w * .17, 1.15)
    for i in range(n):
        t = i / float(n - 1)
        y = cy + L * t
        x = cx + math.sin(t * 4.4 + sd) * w * .30
        for sgn in (-1, 1):
            d.form(circ(x + sgn * rs[i] * .74, y, rs[i], sd + i * .3, 9, .07,
                        rs[i] * .92), col,
                   sweep(x + sgn * rs[i] * .74, y, rs[i], rs[i], lo=.28,
                         hi=-.42), sh, ol=OL_FINE)


def whale_wisteria():
    d = Doc()
    # ---- the vine ----
    spine = [(742, 986), (760, 880), (712, 730), (742, 574), (816, 428),
             (782, 274), (676, 178)]
    d.form(ribbon(spine, [128, 116, 106, 98, 90, 80, 66], cap0="flat",
                  cap1="round"), GRASS,
           sweep(760, 590, 110, 410, lo=.16, hi=-.24, wob=.05), GRASS_DEEP)
    for (lx, ly, L, Wd, dg) in ((706, 700, 206, 124, -88),
                                (824, 448, 190, 114, 84),
                                (704, 232, 176, 106, -96)):
        d.form(leaf_round(lx, ly, L, Wd, dg, .10), GRASS_DEEP,
               sweep(lx, ly - L * .4, Wd * .6, L * .32, lo=.22, hi=-.36,
                     seed=ly * .02), GRASS_DARK, ol=OL_PROP)
        d.line(vein(lx, ly, L * .86, dg, .76), OL_FINE)
    # ---- two hanging racemes ----
    _raceme(d, 566, 246, 372, 156, 1.4)
    _raceme(d, 836, 356, 296, 130, 3.8)
    # ---- the whale ----
    d.form(leaf_pointed(452, 790, 236, 198, 124, -.18), SKY_HI,
           sweep(548, 868, 104, 88, lo=.24, hi=-.38), SKY_DEEP)
    d.form(circ(300, 762, 268, 6.4, 13, .030, 210, -6), SKY_HI,
           sweep(300, 762, 268, 210, lo=.30, hi=-.44, wob=.06), SKY_DEEP)
    # pale belly, flat pattern
    d.fill(canopy_blob(292, 856, 214, 74, 9,
                       *lobe_profile(26.8, 9, jit=0.09, bul=(10, 26))),
           SKY_LO)
    # flipper
    d.form(leaf_round(196, 806, 186, 120, 168, .14), SKY_HI,
           sweep(182, 872, 76, 56, lo=.24, hi=-.38), SKY_DEEP, ol=OL_PROP)
    # spout
    for (sx, sy, k, w0) in ((216, 420, 0.24, 54), (300, 392, -0.10, 48),
                            (132, 480, 0.34, 42)):
        d.form(ribbon(bow(240, 592, sx, sy, k, 6),
                      [w0, w0 * .92, w0 * .84, w0 * .74, w0 * .62,
                       w0 * .48], cap0="flat", cap1="round"), SKY_LO,
               sweep((240 + sx) / 2, (592 + sy) / 2, 60, 90, lo=.24,
                     hi=-.38), SKY_HI, ol=OL_PROP)
    # ODDITY: one spout droplet has broken away and hangs in the air
    d.form(circ(114, 320, 50, 9.3, 10, .07, 58, 14), SKY_LO,
           sweep(114, 320, 50, 58, lo=.26, hi=-.40), SKY_HI, ol=OL_PROP)
    d.add(face(272, 776, 152, mass_w=300, default="delighted", tilt=-4.0,
               eyes=((-56, -18), (52, -24)), eye_r=(21, 25), mouth=(-6, 50),
               mouth_k=1.10))
    return d.svg()


# =====================================================================
# 20. w-waffle-willow   WACKY -- face on the BIG WAFFLE
#     Two long willow arms drooping off a gnarled trunk, with square
#     waffles swinging off them: a wide arch with rectangles in it.
# =====================================================================
def _waffle(d, cx, cy, w, h, dg, sd, big=False):
    outer = slab(cx, cy, w, h, 0.10, dg)
    lines = []
    for i in range(1, 4):
        a = place([(-w * .5, -h * .5 + h * i / 4.), (w * .5, -h * .5 +
                                                     h * i / 4.)],
                  cx, cy, dg)
        lines.append('<path d="M%.1f,%.1f L%.1f,%.1f" fill="none" '
                     'stroke="%s" stroke-width="%d" %s/>'
                     % (a[0][0], a[0][1], a[1][0], a[1][1], INK, OL_FINE, RJ))
        b = place([(-w * .5 + w * i / 4., -h * .5),
                   (-w * .5 + w * i / 4., h * .5)], cx, cy, dg)
        lines.append('<path d="M%.1f,%.1f L%.1f,%.1f" fill="none" '
                     'stroke="%s" stroke-width="%d" %s/>'
                     % (b[0][0], b[0][1], b[1][0], b[1][1], INK, OL_FINE, RJ))
    d.form(outer, SUN_DEEP, sweep_hard(cx, cy, w * .30, h * .5, lo=.24,
                                       hi=-.32), RAY_SHADE,
           ol=OL_MAIN if big else OL_PROP, inner="".join(lines))


def waffle_willow():
    d = Doc()
    # ---- gnarled trunk ----
    d.form(trunk_chunky(506, 486, BASE_Y, 156, 268, root_seed=34.8, lean=-8,
                        root_lobes=4, root_depth=(46, 92), flare=1.26),
           BARK, sweep(526, 740, 130, 262, lo=.14, hi=-.14, wob=.06),
           BARK_DEEP,
           inner=('<path d="M436,600 C452,720 442,860 458,960" fill="none" '
                  'stroke="%s" stroke-width="%d" %s/>'
                  '<path d="M584,640 C596,760 588,880 600,958" fill="none" '
                  'stroke="%s" stroke-width="%d" %s/>'
                  % (INK, OL_MAIN, RJ, INK, OL_MAIN, RJ)))
    # ---- two drooping willow arms ----
    for (x1, y1, k, w0, w1) in ((196, 640, 0.42, 92, 44),
                                (824, 676, -0.40, 88, 42)):
        d.form(branch(486 if x1 < 500 else 528, 470, x1, y1, w0, w1, k, 8),
               BARK, sweep((500 + x1) / 2, 520, 190, 130, lo=.18, hi=-.30,
                           seed=x1 * .01), BARK_DEEP)
        # little sprigs on the arms
        d.form(leaf_round(x1 + (40 if x1 < 500 else -40), y1 - 60, 108, 66,
                          (44 if x1 < 500 else -44), .12), LEAF,
               sweep(x1, y1 - 110, 44, 34, lo=.24, hi=-.38), GRASS,
               ol=OL_FINE)
    # ---- three hanging waffles ----
    d.line("M198,646 L206,748", OL_FINE)
    d.line("M826,678 L832,780", OL_FINE)
    # ODDITY: the low-left waffle has a real bite out of its corner
    lw = slab(206, 850, 212, 204, 0.10, -7) + " " + bite(158, 794, 46)
    d.form(lw, SUN_DEEP, sweep_hard(206, 850, 64, 102, lo=.24, hi=-.32),
           RAY_SHADE, ol=OL_PROP, evenodd=True,
           inner="".join(
               '<path d="M%d,%d L%d,%d" fill="none" stroke="%s" '
               'stroke-width="%d" %s/>' % v
               for v in ((154, 748, 148, 952, INK, OL_FINE, RJ),
                         (206, 746, 202, 954, INK, OL_FINE, RJ),
                         (258, 748, 254, 952, INK, OL_FINE, RJ),
                         (104, 798, 310, 792, INK, OL_FINE, RJ),
                         (104, 850, 310, 846, INK, OL_FINE, RJ),
                         (104, 902, 310, 898, INK, OL_FINE, RJ))))
    _waffle(d, 832, 878, 198, 192, 6, 2.2)
    d.line("M506,300 L506,214", OL_FINE)
    _waffle(d, 506, 320, 372, 348, -2, 3.3, big=True)
    # syrup drizzle + a butter pat on the big waffle
    d.form(ribbon(bow(368, 190, 646, 212, 0.14, 7),
                  [44, 52, 58, 60, 56, 48, 38], cap0="round", cap1="round"),
           BARK, sweep(506, 200, 140, 34, lo=.24, hi=-.34), BARK_DEEP,
           ol=OL_PROP)
    d.form(ribbon(bow(640, 206, 686, 402, -0.20, 6),
                  [38, 35, 32, 28, 24, 19], cap0="flat", cap1="round"),
           BARK, sweep(664, 302, 34, 98, lo=.24, hi=-.34), BARK_DEEP,
           ol=OL_FINE)
    d.form(slab(392, 210, 120, 88, 0.14, -8), CREAM,
           sweep_hard(392, 210, 38, 28, lo=.22, hi=-.30), CREAM_DEEP,
           ol=OL_PROP)
    d.add(face(508, 356, 196, mass_w=372, default="happy", tilt=-2.0,
               eyes=((-54, 4), (56, -2)), eye_r=(21, 24), mouth=(2, 58),
               mouth_k=1.15))
    return d.svg()


def arrow_leaf(cx, cy, L, Wd, deg=0.0, notch=0.30):
    """An arrowhead / elephant-ear blade: pointed tip, two basal lobes."""
    p = [(0, -notch * L), (-.18 * Wd, -.10 * L), (-.40 * Wd, .06 * L),
         (-.54 * Wd, -.18 * L), (-.50 * Wd, -.54 * L), (-.28 * Wd, -.86 * L),
         (0, -L), (.30 * Wd, -.84 * L), (.52 * Wd, -.52 * L),
         (.56 * Wd, -.16 * L), (.42 * Wd, .08 * L), (.20 * Wd, -.09 * L)]
    return smooth_closed(place(p, cx, cy, deg))


# =====================================================================
# 21. x-xanthosoma   REALISTIC -- no face
#     Three enormous arrowhead blades on thick stalks. The whole mass is
#     THREE BIG SHAPES: no scallops, no clumps, nothing else in the set.
# =====================================================================
def xanthosoma():
    d = Doc()
    def _blade(bx, by, L, Wd, dg, col, sh, ol=OL_MAIN, ribs=True):
        d.form(arrow_leaf(bx, by, L, Wd, dg), col,
               sweep(bx + L * .30 * math.sin(math.radians(dg)),
                     by - L * .52, Wd * .56, L * .40, lo=.26, hi=-.42,
                     wob=.06, seed=bx * .01), sh, ol=ol)
        if ribs:
            d.line(vein(bx, by, L * .92, dg, .90), OL_MAIN)
            for (t, sgn, f) in ((.34, -1, .44), (.34, 1, .44),
                                (.56, -1, .36), (.56, 1, .36),
                                (.76, -1, .24), (.76, 1, .24)):
                a0 = place([(0, -L * t)], bx, by, dg)[0]
                a1 = place([(sgn * Wd * f, -L * (t + .16))], bx, by, dg)[0]
                mid = place([(sgn * Wd * f * .45, -L * (t + .11))],
                            bx, by, dg)[0]
                d.line("M%.1f,%.1f Q%.1f,%.1f %.1f,%.1f"
                       % (a0[0], a0[1], mid[0], mid[1], a1[0], a1[1]),
                       OL_FINE)
    # ---- stalks ----
    for (tx, ty, k, w0, w1, col, sh) in (
            (296, 540, 0.10, 74, 46, GRASS_DEEP, GRASS_DARK),
            (742, 516, -0.10, 72, 45, GRASS_DEEP, GRASS_DARK),
            (508, 516, 0.02, 86, 52, GRASS, GRASS_DEEP)):
        d.form(branch(506, 996, tx, ty, w0, w1, k, 7), col,
               sweep((506 + tx) / 2, (996 + ty) / 2, 110, 250, lo=.14,
                     hi=-.22, seed=tx * .01), sh)
    # a sheath where the stalks leave the soil
    d.form(smooth_closed([(414, 1000), (426, 902), (470, 838), (506, 812),
                          (548, 838), (588, 906), (600, 1000), (506, 984)]),
           GRASS, sweep(506, 916, 96, 96, lo=.24, hi=-.38), GRASS_DEEP)
    # ---- the three blades ----
    _blade(296, 540, 372, 330, -24, GRASS, GRASS_DEEP)
    _blade(742, 516, 362, 320, 22, GRASS_DEEP, GRASS_DARK)
    _blade(508, 516, 420, 386, -3, LEAF, GRASS)
    # ODDITY: the right blade has a wind-tear in its edge
    d.line("M842,414 C810,452 792,486 786,522", OL_MAIN)
    return d.svg()


# =====================================================================
# 22. x-fox-xerophyte   SILLY -- face
#     A pale ribbed column cactus that is unmistakably a fox: two pointed
#     ears on top, two stubby arms, a fat curled tail at the foot.
# =====================================================================
def fox_xerophyte():
    d = Doc()
    def _spines(items):
        for (sx, sy, dg) in items:
            for k in (-26, 0, 26):
                q = place([(0, 0), (0, -32)], sx, sy, dg + k)
                d.line("M%.1f,%.1f L%.1f,%.1f" % (q[0] + q[1]), OL_FINE)
    # ---- tail, behind ----
    sp = spiral_pts(786, 838, 168, 0.60, -110, 12, 0.60)
    d.form(ribbon(sp, [96, 94, 92, 88, 84, 80, 74, 68, 62, 55, 48, 40],
                  cap0="flat", cap1="round"), CREAM,
           sweep(786, 838, 168, 168, lo=.26, hi=-.40), CREAM_DEEP)
    d.form(leaf_round(886, 720, 128, 96, 26, .12), BARK_DEEP,
           sweep(918, 672, 52, 40, lo=.24, hi=-.38), INK_SOFT, ol=OL_PROP)
    # ---- ears, behind the body ----
    for (ex, ey, L, w, dg) in ((374, 316, 216, 148, -24), (652, 300, 208,
                                                           142, 22)):
        d.form(horn(ex, ey, L, w, dg, .10), CREAM,
               sweep(ex, ey - L * .5, w * .6, L * .4, lo=.26, hi=-.40),
               CREAM_DEEP)
        q = place([(0, -L * .34)], ex, ey, dg)[0]
        d.fill(horn(q[0], q[1], L * .50, w * .48, dg, .10), BARK_DEEP)
    # ---- arms ----
    for (x1, y1, k, w0, w1) in ((236, 636, 0.22, 92, 74),
                                (786, 604, -0.24, 88, 70)):
        d.form(branch(444 if x1 < 500 else 570, 668, x1, y1, w0, w1, k, 6),
               CREAM, sweep((500 + x1) / 2, (668 + y1) / 2, 120, 70, lo=.24,
                            hi=-.36, seed=x1 * .01), CREAM_DEEP)
        d.form(ribbon(bow(x1, y1, x1 + (0 if x1 < 500 else 4), y1 - 190,
                          0.06, 6), [74, 72, 70, 68, 64, 58], cap0="flat",
                      cap1="round"), CREAM,
               sweep(x1, y1 - 96, 40, 96, lo=.24, hi=-.36), CREAM_DEEP)
    # ---- the body column ----
    body = smooth_closed([(356, 946), (346, 720), (368, 512), (428, 394),
                          (508, 356), (592, 392), (652, 512), (676, 726),
                          (664, 950), (508, 968)])
    ribs = "".join(
        '<path d="M%d,%d C%d,%d %d,%d %d,%d" fill="none" stroke="%s" '
        'stroke-width="%d" %s/>'
        % (ax, 430, ax - 12, 600, ax - 6, 780, ax, 950, INK, OL_MAIN, RJ)
        for ax in (400, 616))
    d.form(body, CREAM, sweep(508, 660, 176, 300, lo=.24, hi=-.30, wob=.05),
           CREAM_DEEP, inner=ribs)
    _spines([(376, 470, -18), (398, 830, -12), (396, 706, -8),
             (622, 776, 14), (632, 496, 10), (516, 902, 2),
             (250, 596, -20), (798, 560, 18)])
    # snout patch, with the nose sitting ABOVE the mouth line
    d.fill(circ(508, 606, 132, 4.9, 10, .05, 84, 2), CREAM_DEEP)
    d.form(smooth_closed([(508, 526), (540, 542), (530, 570), (508, 580),
                          (484, 568), (476, 540)]), INK_SOFT, None, INK_SOFT,
           ol=OL_FINE)
    # ODDITY: a single flower has opened on the fox's head
    d.form(circ(566, 316, 62, 21.7, 10, .08, 54, 12), FRUIT,
           sweep(566, 316, 62, 54, lo=.26, hi=-.40), FRUIT_DEEP, ol=OL_PROP)
    d.fill(circ(566, 316, 24, 3.3, 8, .08, 22), SUN)
    d.add(face(508, 516, 244, mass_w=420, default="mischief", tilt=-2.0,
               eyes=((-66, -56), (64, -62)), eye_r=(28, 30), mouth=(0, 112),
               mouth_k=1.10, brow_lift=14))
    return d.svg()


# =====================================================================
# 23. y-yucca   REALISTIC -- no face
#     A starburst of dead-straight sword blades over a stubby scaled
#     trunk, with a cream flower spike pushing up through the middle.
# =====================================================================
def yucca():
    d = Doc()
    CX0, CY0 = 502, 640
    ang = [-132, -112, -92, -72, -52, -30, -6, 18, 42, 66, 90, 112, 132]
    j = jitter(47.2, len(ang), 0.13, 1.0)
    back, front = [], []
    for i, a in enumerate(ang):
        L = ((534 if i % 3 else 462) * j[i]
             * (1.0 - 0.30 * abs(a) / 132.0))
        col = GRASS_DEEP if i % 3 == 0 else (LEAF if i % 3 == 1 else GRASS)
        sh = GRASS_DARK if i % 3 == 0 else (GRASS if i % 3 == 1 else
                                            GRASS_DEEP)
        item = (CX0 + (i - 6) * 8 + 14, CY0 - abs(i - 6) * 3, L, 88 * j[i], a,
                (0.05 if i % 2 else -0.04), col, sh)
        (back if i % 3 == 0 else front).append(item)

    def _swords(items):
        for (bx, by, L, w, dg, k, col, sh) in items:
            d.form(horn(bx, by, L, w, dg, k), col,
                   sweep(bx + L * .34 * math.sin(math.radians(dg)),
                         by - L * .34 * math.cos(math.radians(dg)),
                         w * .70, L * .34, lo=.24, hi=-.38, seed=bx * .01),
                   sh, ol=OL_MAIN)
    _swords(back)
    # ---- the stubby scaled trunk ----
    d.form(trunk_chunky(504, 648, BASE_Y, 172, 232, root_seed=57.7, lean=4,
                        root_lobes=3, root_depth=(20, 36), flare=1.06),
           BARK, sweep(524, 862, 130, 150, lo=.16, hi=-.16, wob=.05),
           BARK_DEEP)
    for (sy, n) in ((752, 3), (836, 4), (916, 3)):
        for i in range(n):
            sx = 504 - (n - 1) * 58 / 2.0 + i * 58
            d.fill(slab(sx, sy, 52, 44, 0.28, (i - 1) * 6), BARK_DEEP)
    _swords(front)
    # ---- the flower spike, pushing up through the middle ----
    d.form(ribbon(bow(502, 618, 512, 212, 0.04, 6), [58, 54, 50, 46, 40, 34],
                  cap0="flat", cap1="round"), GRASS,
           sweep(508, 446, 44, 184, lo=.20, hi=-.32), GRASS_DEEP, ol=OL_PROP)
    for (bx, by, r, sd) in ((462, 534, 54, 1.2), (554, 496, 52, 2.4),
                            (468, 424, 50, 3.6), (550, 382, 48, 4.8),
                            (490, 300, 46, 6.0), (530, 240, 42, 7.2)):
        d.form(circ(bx, by, r, sd, 10, .07, r * 1.16, (sd * 9) % 24 - 12),
               CREAM, sweep(bx, by, r, r * 1.16, lo=.28, hi=-.42), CREAM_DEEP,
               ol=OL_PROP)
    # ODDITY: one sword has kinked over and points back at the ground
    d.form(horn(586, 652, 372, 84, 120, 0.30), GRASS_DEEP,
           sweep(750, 758, 132, 92, lo=.22, hi=-.36), GRASS_DARK, ol=OL_MAIN)
    return d.svg()


# =====================================================================
# 24. y-yak-yarrow   "Yawning Yak Yarrow"   SILLY -- face, MID-YAWN
#     Shaggy head, two pale horns, eyes screwed shut, mouth wide open with
#     a tongue in it, and two Zs drifting off to the right.
# =====================================================================
def yak_yarrow():
    d = Doc()
    # ---- stem + one feathery yarrow leaf ----
    d.form(leaf_pointed(556, 848, 218, 120, 70, -.16), GRASS_DEEP,
           sweep(664, 790, 104, 84, lo=.18, hi=-.34), GRASS_DARK, ol=OL_MAIN)
    for t in (0.3, 0.5, 0.7):
        q = place([(0, -218 * t)], 556, 848, 70)[0]
        d.line("M%.1f,%.1f L%.1f,%.1f" % (q[0], q[1], q[0] + 46, q[1] + 30),
               OL_FINE)
    d.form(stem_slim(506, 606, BASE_Y, 92, root_seed=39.5, lean=-10,
                     w_base=240, root_lobes=3, root_depth=(18, 32)),
           GRASS, sweep(522, 800, 76, 196, lo=.06, hi=-.12, wob=.03),
           GRASS_DEEP)
    # ---- two flat-topped yarrow umbels on side stalks ----
    for (ux, uy, k, sd, uw) in ((242, 664, 0.18, 3.1, 196),
                                (800, 726, -0.20, 6.2, 176)):
        d.form(branch(506, 866, ux, uy, 46, 30, k, 7), GRASS,
               sweep((506 + ux) / 2, (866 + uy) / 2, 140, 110, lo=.16,
                     hi=-.26, seed=sd), GRASS_DEEP, ol=OL_PROP)
        J2, B2 = lobe_profile(sd * 2.7, 11, jit=0.11, bul=(16, 40))
        d.form(canopy_blob(ux, uy - 24, uw * .52, uw * .30, 11, J2, B2,
                           start=-172), CREAM,
               sweep(ux, uy - 24, uw * .52, uw * .30, lo=.28, hi=-.42,
                     wob=.08, seed=sd), CREAM_DEEP, ol=OL_PROP)
        j = jitter(sd, 5, 0.14, 1.0)
        for i in range(5):
            fx = ux - uw * .34 + uw * .68 * i / 4.0
            d.fill(circ(fx, uy - 34 - (0 if i % 2 else 12), 26 * j[i],
                        sd + i, 9, .10, 22 * j[i]), CREAM_DEEP)
    # ---- horns, behind the head ----
    for (hx, hy, L, w, dg, k) in ((322, 352, 342, 150, -58, 0.30),
                                  (696, 332, 330, 144, 60, -0.30)):
        d.form(horn(hx, hy, L, w, dg, k), CREAM,
               sweep(hx + (L * .4 if dg > 0 else -L * .4), hy - 40, w * .7,
                     L * .34, lo=.26, hi=-.40), CREAM_DEEP)
    # ---- the shaggy head ----
    # the shaggy beard hangs below the jaw, in front of the stem
    JB, BB = lobe_profile(52.6, 11, jit=0.12, bul=(38, 88))
    d.form(canopy_blob(484, 596, 142, 172, 11, JB, BB, start=-84), BARK,
           sweep(484, 596, 142, 172, lo=.28, hi=-.42, wob=.09), BARK_DEEP)
    J, B = lobe_profile(81.3, 15, jit=0.11, bul=(48, 104))
    d.form(canopy_blob(506, 330, 272, 190, 15, J, B, start=-98), BARK,
           sweep(506, 330, 272, 190, lo=.30, hi=-.44, wob=.09), BARK_DEEP)
    # shag marks: flat, unoutlined pattern
    marks(d, [(320, 264, 104, 58, -46, BARK_DEEP), (686, 250, 98, 56, 42,
                                                    BARK_DEEP),
              (256, 386, 96, 54, -76, BARK_DEEP), (752, 372, 92, 52, 72,
                                                   BARK_DEEP),
              (394, 202, 92, 52, -18, BARK_DEEP), (610, 194, 88, 50, 22,
                                                   BARK_DEEP),
              (432, 660, 86, 48, -170, BARK_DEEP), (540, 650, 82, 46, 166,
                                                    BARK_DEEP)])
    # a pale muzzle patch for the yawn to sit on
    d.fill(circ(502, 406, 164, 5.3, 11, .05, 122, 2), BARK_LITE)
    # ---- the two Zs drifting off, foreground weight so they survive ----
    for (zx, zy, zs) in ((806, 214, 68), (896, 118, 48)):
        d.line("M%d,%d L%d,%d L%d,%d L%d,%d"
               % (zx, zy, zx + zs, zy, zx, zy + zs, zx + zs, zy + zs),
               OL_PROP)
    # ODDITY: the left horn is chipped short, the right is full length
    d.form(horn(316, 300, 108, 70, -70, .20), CREAM,
           sweep(288, 266, 38, 44, lo=.26, hi=-.40), CREAM_DEEP, ol=OL_PROP)
    d.add(face(504, 352, 268, mass_w=536, default="delighted", tilt=3.0,
               eyes=((-68, -44), (66, -50)), eye_r=(23, 20), mouth=(0, 48),
               mouth_k=1.42))
    return d.svg()


# =====================================================================
# 25. y-yoyo-tree   WACKY -- face on the canopy
#     A LOW WIDE canopy with two arms, and two yoyos on long strings that
#     hang well below the trunk line -- the silhouette has two holes in it.
# =====================================================================
def _yoyo(d, cx, cy, r, outer, o_sh, inner, i_sh, sd):
    d.form(circ(cx, cy, r, sd, 12, .022, r * .98), outer,
           sweep(cx, cy, r, r, lo=.30, hi=-.44), o_sh)
    d.form(circ(cx, cy, r * .60, sd + 2, 11, .03, r * .58), inner,
           sweep(cx, cy, r * .60, r * .58, lo=.28, hi=-.42), i_sh, ol=OL_PROP)
    d.form(circ(cx, cy, r * .22, sd + 4, 9, .05, r * .21), CREAM,
           None, CREAM_DEEP, ol=OL_FINE)


def yoyo_tree():
    d = Doc()
    d.form(trunk_chunky(504, 452, BASE_Y, 172, 262, root_seed=76.4, lean=6,
                        root_lobes=3, root_depth=(20, 38), flare=1.12),
           BARK, sweep(528, 720, 136, 280, lo=.14, hi=-.14, wob=.06),
           BARK_DEEP,
           inner=('<path d="M436,566 C452,690 442,830 458,958" fill="none" '
                  'stroke="%s" stroke-width="%d" %s/>'
                  % (INK, OL_MAIN, RJ)))
    # two arms holding the strings
    for (x1, y1, k, w0, w1) in ((246, 508, 0.20, 78, 50),
                                (774, 536, -0.22, 74, 48)):
        d.form(branch(470 if x1 < 500 else 540, 486, x1, y1, w0, w1, k, 6),
               BARK, sweep((500 + x1) / 2, (486 + y1) / 2, 120, 60, lo=.20,
                           hi=-.32, seed=x1 * .01), BARK_DEEP)
    # ---- the canopy: LOW and WIDE ----
    clump(d, [(276, 356, 156, 116, GRASS, 9, -102, None, 1.5),
              (748, 344, 152, 114, GRASS, 9, -84, None, 3.0),
              (400, 288, 176, 128, LEAF, 10, -96, None, 4.5),
              (628, 278, 172, 126, LEAF, 10, -90, 5, 6.0),
              (512, 320, 214, 152, LEAF, 11, -97, None, 7.5)])
    marks(d, [(300, 322, 84, 48, -30, GRASS_DARK),
              (716, 310, 80, 46, 26, GRASS_DARK),
              (430, 210, 78, 44, -14, GRASS_DEEP),
              (614, 204, 76, 44, 28, GRASS_DEEP),
              (508, 396, 74, 42, 4, GRASS_DEEP)])
    # ---- the yoyos ----
    d.line("M246,522 L242,706", OL_FINE)
    _yoyo(d, 240, 796, 96, FRUIT, FRUIT_DEEP, SUN, SUN_DEEP, 2.2)
    # ODDITY: the right yoyo is at the very bottom of its string, spinning
    d.line("M776,550 L790,838", OL_FINE)
    _yoyo(d, 792, 908, 86, SKY_HI, SKY_DEEP, CREAM, CREAM_DEEP, 5.5)
    swoosh(d, 692, 884, 700, 946, 0.30, GRASS_DARK)
    swoosh(d, 884, 876, 876, 940, -0.30, GRASS_DARK)
    d.add(face(506, 322, 250, mass_w=470, default="happy", tilt=-2.0,
               eyes=((-58, -8), (60, -14)), eye_r=(22, 25), mouth=(2, 54),
               mouth_k=1.15))
    return d.svg()


# =====================================================================
# 26. z-zinnia   REALISTIC -- no face
#     A dense DOUBLE ring of short blunt petals round a big seeded disc.
#     Petals are short and many; nothing else here has that texture.
# =====================================================================
def zinnia():
    d = Doc()
    d.form(leaf_pointed(414, 880, 296, 164, -84, .16), GRASS,
           sweep(272, 812, 138, 106, lo=.20, hi=-.36), GRASS_DEEP)
    d.line(vein(414, 880, 258, -84, .78), OL_FINE)
    d.form(leaf_pointed(570, 926, 262, 148, 82, -.16), GRASS_DEEP,
           sweep(700, 872, 124, 98, lo=.18, hi=-.34), GRASS_DARK)
    d.line(vein(570, 926, 226, 82, .78), OL_FINE)
    d.form(stem_slim(492, 500, BASE_Y, 74, root_seed=62.9, lean=-22,
                     w_base=204, root_lobes=3, root_depth=(18, 30)),
           GRASS, sweep(516, 780, 62, 226, lo=.06, hi=-.12, wob=.03),
           GRASS_DEEP)
    # a second, smaller bloom on its own stalk, low and to the right
    d.form(branch(514, 620, 810, 550, 44, 30, -0.20, 6), GRASS,
           sweep(662, 586, 150, 60, lo=.16, hi=-.26), GRASS_DEEP, ol=OL_PROP)
    petal_ring(d, 824, 486, 10, 84, 178, 76, BERRY, BERRY_DEEP, 33.9,
               ol=OL_FINE, start=-82, curl=0.06)
    d.form(circ(824, 486, 56, 4.2, 10, .05, 52, -3), SUN,
           sweep(824, 486, 56, 52, lo=.28, hi=-.42), SUN_SHADE, ol=OL_PROP)
    # the main bloom -- smaller and set left of centre
    petal_ring(d, 452, 342, 13, 148, 262, 100, BERRY, BERRY_DEEP, 15.8,
               ol=OL_PROP, start=-94, curl=0.06)
    petal_ring(d, 452, 342, 10, 82, 180, 92, BERRY, BERRY_DEEP, 27.3,
               ol=OL_PROP, start=-72, curl=0.08)
    d.form(circ(452, 342, 90, 8.6, 12, .04, 86, -3), SUN,
           sweep(452, 342, 90, 86, lo=.28, hi=-.42), SUN_SHADE)
    for (dx, dy, r) in ((-40, -20, 15), (2, -36, 14), (40, -12, 15),
                        (-30, 26, 14), (22, 32, 13), (-4, 4, 14),
                        (54, 20, 12), (-54, 8, 13)):
        d.fill(circ(452 + dx, 342 + dy, r, dx * .1, 8, .10, r * .92), SUN_DEEP)
    # ODDITY: one outer petal is missing, leaving a gap in the ring
    d.form(leaf_round(266, 452, 84, 60, -122, .10), BERRY,
           sweep(242, 482, 36, 28, lo=.26, hi=-.42), BERRY_DEEP, ol=OL_FINE)
    return d.svg()


# =====================================================================
# 27. z-zebra-zinnia   SILLY -- face
#     Long narrow striped rays round a pale face disc, on a hard-kinked
#     stem: the head sits well off-centre, unlike every other bloom here.
# =====================================================================
def zebra_zinnia():
    d = Doc()
    d.form(leaf_pointed(508, 848, 236, 128, -74, .16), GRASS,
           sweep(392, 776, 116, 94, lo=.20, hi=-.36), GRASS_DEEP)
    d.line(vein(508, 848, 202, -74, .78), OL_FINE)
    d.form(ribbon([(542, 984), (566, 900), (620, 806), (612, 690),
                   (570, 592), (566, 548)],
                  [206, 132, 104, 94, 88, 82], cap0="flat", cap1="flat"),
           GRASS, sweep(590, 760, 70, 240, lo=.10, hi=-.16, wob=.04),
           GRASS_DEEP)
    d.line("M540,912 C578,834 596,742 578,640", OL_MAIN)
    # ---- striped rays ----
    CXf, CYf = 542, 428
    n = 16
    j = jitter(93.4, n, 0.12, 1.0)
    for i in range(n):
        a = -96 + 360.0 * i / n + (i % 2) * 4
        rad = math.radians(a)
        bx = CXf + 134 * math.cos(rad)
        by = CYf + 134 * math.sin(rad)
        L = 216 * j[i]
        Wd = 100 * j[i]
        d.form(leaf_round(bx, by, L, Wd, a + 90, .06), CREAM,
               sweep(bx + L * .34 * math.cos(rad), by + L * .34 *
                     math.sin(rad), Wd * .5, L * .40, lo=.26, hi=-.42,
                     seed=i), CREAM_DEEP, ol=OL_PROP)
        if i != 5:                      # ODDITY: one ray has no stripes
            for t in (0.34, 0.58, 0.80):
                q = place([(0, -L * t)], bx, by, a + 90)[0]
                d.fill(slab(q[0], q[1], Wd * (1.0 - t * .55), 26, 0.44,
                            a + 90), INK_SOFT)
    d.form(circ(CXf, CYf, 160, 11.7, 13, .035, 152, -3), CREAM,
           sweep(CXf, CYf, 160, 152, lo=.28, hi=-.42), CREAM_DEEP)
    for (dg, w) in ((-46, 38), (-16, 32), (14, 34), (44, 40)):
        q = place([(0, -138)], CXf, CYf, dg)[0]
        d.fill(slab(q[0], q[1], w, 68, 0.42, dg), INK_SOFT)
    d.add(face(544, 424, 188, mass_w=320, default="mischief", tilt=-3.0,
               eyes=((-52, -10), (54, -16)), eye_r=(21, 24), mouth=(2, 56),
               mouth_k=1.05, brow_lift=6))
    return d.svg()


# =====================================================================
# 28. z-zombie-tree   WACKY -- face. FUNNY, NOT SCARY.
#     A lumpy patched head on a split-legged crooked trunk: goggle eyes,
#     two buck teeth, a stitched brow and one hopeful new green sprout.
# =====================================================================
def zombie_tree():
    d = Doc()
    # ---- crooked split trunk ----
    d.form(trunk_chunky(498, 486, BASE_Y, 152, 296, root_seed=49.6, lean=-14,
                        root_lobes=3, root_depth=(64, 118), flare=1.30),
           BARK, sweep(520, 740, 130, 270, lo=.14, hi=-.14, wob=.07),
           BARK_DEEP,
           inner=('<path d="M420,590 C446,700 428,830 452,948" fill="none" '
                  'stroke="%s" stroke-width="%d" %s/>'
                  '<path d="M582,640 C598,748 590,860 606,952" fill="none" '
                  'stroke="%s" stroke-width="%d" %s/>'
                  % (INK, OL_MAIN, RJ, INK, OL_MAIN, RJ)))
    # ---- two crooked arms ----
    for (x1, y1, k, w0, w1, sprout) in ((214, 594, 0.34, 82, 44, False),
                                        (818, 640, -0.30, 78, 42, True)):
        d.form(branch(462 if x1 < 500 else 542, 542, x1, y1, w0, w1, k, 7),
               BARK, sweep((500 + x1) / 2, (542 + y1) / 2, 150, 80,
                           lo=.20, hi=-.32, seed=x1 * .01), BARK_DEEP)
        # crooked fingers
        for (fx, fy, fk) in ((x1 - 70 if x1 < 500 else x1 + 70, y1 - 78,
                              0.24), (x1 - 46 if x1 < 500 else x1 + 46,
                                      y1 + 76, -0.20)):
            d.form(branch(x1, y1, fx, fy, 38, 22, fk, 5), BARK,
                   sweep((x1 + fx) / 2, (y1 + fy) / 2, 50, 50, lo=.20,
                         hi=-.32), BARK_DEEP, ol=OL_PROP)
        if sprout:
            # ODDITY: one bright green sprout on the dead right arm
            d.form(leaf_round(852, 570, 128, 82, 32, .12), LEAF,
                   sweep(884, 522, 52, 40, lo=.24, hi=-.38), GRASS,
                   ol=OL_PROP)
            d.line(vein(852, 570, 108, 32, .74), OL_FINE)
    # moss patches on the dead wood: flat, unoutlined pattern
    for (mx, my, mw, mh, dg) in ((444, 636, 96, 52, -16), (556, 742, 84, 46,
                                                           12),
                                 (430, 858, 90, 48, -8), (600, 880, 76, 42,
                                                          18),
                                 (300, 604, 70, 38, 24), (760, 662, 66, 36,
                                                          -20)):
        d.fill(slab(mx, my, mw, mh, 0.46, dg), GRASS_DARK)
    # ---- the lumpy head ----
    J, B = lobe_profile(88.9, 12, jit=0.135, bul=(34, 92))
    d.form(canopy_blob(504, 344, 268, 232, 12, J, B, start=-98, notch=8),
           GRASS_DEEP, sweep(504, 344, 268, 232, lo=.30, hi=-.44, wob=.10),
           GRASS_DARK)
    # scabby lumps
    for (bx, by, r, sd) in ((360, 220, 44, 1.1), (628, 196, 40, 2.2),
                            (306, 396, 42, 3.3), (686, 424, 38, 4.4),
                            (470, 172, 36, 5.5)):
        d.fill(circ(bx, by, r, sd, 9, .10, r * .88, sd * 8), GRASS_DARK)
    # stitches across the brow
    d.line("M338,268 C424,232 566,224 660,258", OL_MAIN)
    for (sx, sy, dg) in ((372, 250, 22), (438, 232, 12), (508, 226, -2),
                         (578, 230, -10), (640, 250, -20)):
        q = place([(0, -30), (0, 30)], sx, sy, dg)
        d.line("M%.1f,%.1f L%.1f,%.1f" % (q[0] + q[1]), OL_MAIN)
    d.add(face(506, 356, 264, mass_w=490, default="surprised", tilt=-3.0,
               eyes=((-64, -14), (58, -26)), eye_r=(28, 30), mouth=(-4, 62),
               mouth_k=1.25, brow_lift=2))
    # two buck teeth hanging over the open mouth
    s = 264 / 200.0
    mx, my = 506 - 4 * s, 356 + 62 * s
    for (dx, w, h, dg) in ((-30, 52, 76, -5), (26, 46, 66, 6)):
        d.form(slab(mx + dx * s, my + 26 * s, w, h, 0.22, dg), CREAM,
               sweep_hard(mx + dx * s, my + 26 * s, w * .3, h * .4),
               CREAM_DEEP, ol=OL_FINE)
    return d.svg()


# =====================================================================
PLANTS = [
    ("p-palm-tree", palm_tree),
    ("p-panda-pansy", panda_pansy),
    ("q-quaking-aspen", quaking_aspen),
    ("q-quail-quillplant", quail_quillplant),
    ("q-quackers-duckbloom", quackers_duckbloom),
    ("r-red-rose", red_rose),
    ("r-rabbit-radish", rabbit_radish),
    ("s-snail-snapdragon", snail_snapdragon),
    ("s-sock-sprout", sock_sprout),
    ("t-tomato", tomato),
    ("t-turtle-tulip", turtle_tulip),
    ("t-taco-tree", taco_tree),
    ("u-umbrella-plant", umbrella_plant),
    ("u-unicorn-flower", unicorn_flower),
    ("v-violet", violet),
    ("v-vole-vine", vole_vine),
    ("v-volcano-tree", volcano_tree),
    ("w-watermelon", watermelon),
    ("w-whale-wisteria", whale_wisteria),
    ("w-waffle-willow", waffle_willow),
    ("x-xanthosoma", xanthosoma),
    ("x-fox-xerophyte", fox_xerophyte),
    ("y-yucca", yucca),
    ("y-yak-yarrow", yak_yarrow),
    ("y-yoyo-tree", yoyo_tree),
    ("z-zinnia", zinnia),
    ("z-zebra-zinnia", zebra_zinnia),
    ("z-zombie-tree", zombie_tree),
]

if __name__ == "__main__":
    want = sys.argv[1:]
    jobs = [(n, f) for n, f in PLANTS if not want or n in want]
    for name, fn in jobs:
        svg = fn()
        with open(os.path.join(OUT, name + ".svg"), "w") as fh:
            fh.write(svg.strip() + "\n")
        ok = render(name, svg, W, H, os.path.join(OUT, name + ".png"))
        print("%-22s %s" % (name, "OK" if ok else "FAIL"))
