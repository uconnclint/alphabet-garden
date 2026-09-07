#!/usr/bin/env python3
"""Build wave-1 flat-vector plants (ids A-G, 18 plants).

    python3 art/flat/plants/_build_w1.py            # all 18
    python3 art/flat/plants/_build_w1.py d-donut-tree

Authored entirely from `_kit.py`.  Rasteriser is reused from
`_build_plants.py` (2x headless Chrome -> LANCZOS to 1x).

DO NOT edit `_build_plants.py`, `_kit.py`, `KIT.md` or `_verify.py` from
here -- those are shared with other authors working concurrently.
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
    """A hand-drawn circle/ellipse: the kit has no primitive for a ball."""
    ry = r if ry is None else ry
    j = jitter(seed, n, amp, 1.0)
    p = [(r * j[i] * math.cos(2 * math.pi * i / n - 1.25),
          ry * j[i] * math.sin(2 * math.pi * i / n - 1.25)) for i in range(n)]
    return smooth_closed(place(p, cx, cy, deg))


def ball(d, cx, cy, r, base, seed=0.0, ol=OL_PROP, ry=None, deg=0.0,
         shade=None, gloss=0.0, amp=0.030):
    """A two-tone sphere with an optional cream gloss chip."""
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
        J, B = lobe_profile(sd, n, jit=0.075, bul=(30, 74))
        d.form(canopy_blob(cx, cy, rx, ry, n, J, B, start=st, notch=notch),
               col, sweep(cx, cy, rx, ry, lo=.27 + (int(cx) % 7) * .012,
                          hi=-.39 - (int(cy) % 5) * .012, wob=.09,
                          seed=sd * .7))


def swoosh(d, x0, y0, x1, y1, k, col, ol=OL_BG):
    """A hue-matched motion arc. Background layer only -- never black."""
    sp = bow(x0, y0, x1, y1, k, 6)
    d.add('<path d="M%.1f,%.1f%s" fill="none" stroke="%s" stroke-width="%d" '
          '%s/>' % (sp[0][0], sp[0][1], smooth_open(sp), col, ol, RJ))


def spiral(cx, cy, r0, turns, seed_ang, n=14, shrink=0.80):
    """Points along an inward spiral -- tendrils, fiddleheads, gum curls."""
    pts = []
    for i in range(n):
        t = i / float(n - 1)
        a = math.radians(seed_ang) + turns * 2 * math.pi * t
        r = r0 * (1.0 - shrink * t)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def sprinkle(d, items):
    """Flat unoutlined confetti lozenges (frosting sprinkles)."""
    for (x, y, L, Wd, dg, col) in items:
        d.fill(slab(x, y, L, Wd, 0.50, dg), col)


def dot_spots(d, items, col):
    for (x, y, r, sd, dg) in items:
        d.fill(circ(x, y, r, sd, 8, 0.10, r * 0.82, dg), col)


# =====================================================================
# 1. a-ant-arch   "Antsy Ant Plant"   SILLY -- face
#    A totem-pole ant riding a tall stem, with a conga line of workers
#    marching up it.  Silhouette is a NARROW VERTICAL -- deliberately the
#    opposite of every canopy plant in the set.
# =====================================================================
def _worker_ant(d, cx, cy, s, deg, seed, carry=None):
    """One marching worker ant, `s` = body length. Legs are strokes."""
    def P(lx, ly):
        return rot(cx + lx * s, cy + ly * s, cx, cy, deg)
    for (ax, ay, bx, by) in ((-.18, .10, -.44, .40), (.02, .10, .06, .46),
                             (.20, .08, .44, .38), (-.18, -.02, -.48, -.26),
                             (.20, -.04, .46, -.24)):
        p, q = P(ax, ay), P(bx, by)
        d.add('<path d="M%.1f,%.1f Q%.1f,%.1f %.1f,%.1f" fill="none" '
              'stroke="%s" stroke-width="%d" %s/>'
              % (p[0], p[1], (p[0] + q[0]) / 2 + s * .06,
                 (p[1] + q[1]) / 2 + s * .10, q[0], q[1],
                 INK, OL_PROP, RJ))
    for (ax, bx, by) in ((.30, .42, -.46), (.36, .64, -.34)):
        p, q = P(ax, -.10), P(bx, by)
        d.add('<path d="M%.1f,%.1f Q%.1f,%.1f %.1f,%.1f" fill="none" '
              'stroke="%s" stroke-width="%d" %s/>'
              % (p[0], p[1], p[0] + s * .18, p[1] - s * .30, q[0], q[1],
                 INK, OL_FINE, RJ))
    for (ax, rr) in ((-.36, .24), (-.02, .19), (.30, .22)):
        c = P(ax, 0)
        ball(d, c[0], c[1], rr * s, BARK_DEEP, seed + ax, OL_FINE,
             ry=rr * s * .90, shade=INK_SOFT, gloss=0.32)
    if carry:
        c = (cx + s * .22, cy - s * .30)
        d.form(leaf_round(c[0], c[1], 108, 68, 22), LEAF,
               sweep(c[0], c[1] - 44, 54, 36, lo=.24, hi=-.40), GRASS,
               ol=OL_PROP)


def ant_arch():
    d = Doc()
    # ---- two stem leaves, behind the stem ----
    d.form(leaf_pointed(474, 742, 268, 150, deg=-68, curl=.18), GRASS,
           sweep(360, 640, 140, 116, lo=.20, hi=-.36), GRASS_DEEP)
    d.line("M470,732 C424,690 386,652 342,614", OL_MAIN)
    d.form(leaf_pointed(540, 872, 232, 128, deg=63, curl=-.16), GRASS_DEEP,
           sweep(650, 792, 124, 104, lo=.18, hi=-.34), GRASS_DARK)
    d.line("M546,864 C588,824 626,790 668,754", OL_MAIN)

    # ---- the stem ----
    d.form(stem_slim(500, 452, BASE_Y, 76, root_seed=31.4, lean=-16,
                     w_base=206, root_lobes=3, root_depth=(18, 30)),
           GRASS, sweep(516, 760, 60, 262, lo=.06, hi=-.12, wob=.03),
           GRASS_DEEP)
    d.line("M478,540 C492,660 480,790 494,918", OL_MAIN)

    # ---- the totem ant: abdomen / thorax / head, stacked on the stem ----
    ball(d, 502, 388, 108, BARK, 4.1, OL_MAIN, ry=96, deg=-5,
         shade=BARK_DEEP, gloss=0.34)
    d.line("M424,352 C468,378 520,382 574,356", OL_MAIN)
    ball(d, 496, 268, 76, BARK, 8.3, OL_MAIN, ry=68, deg=4,
         shade=BARK_DEEP, gloss=0.30)
    # legs off the thorax
    for (bx, by, cx2, cy2) in ((410, 300, 318, 372), (582, 292, 676, 358),
                               (416, 252, 322, 218), (580, 246, 674, 214)):
        d.add('<path d="M%d,%d Q%d,%d %d,%d" fill="none" stroke="%s" '
              'stroke-width="%d" %s/>'
              % (bx, by, (bx + cx2) // 2, by + 26, cx2, cy2, INK, OL_PROP, RJ))
    ball(d, 506, 160, 96, BARK, 12.7, OL_MAIN, ry=86, deg=-3,
         shade=BARK_DEEP, gloss=0.32)
    # antennae
    for (tx, ty, kx) in ((436, 104, -34), (584, 114, 30)):
        d.add('<path d="M%d,%d Q%d,%d %d,%d" fill="none" stroke="%s" '
              'stroke-width="%d" %s/>'
              % (496 if tx < 500 else 520, 96, (tx + 500) // 2 + kx, 66,
                 tx, ty, INK, OL_PROP, RJ))
        ball(d, tx, ty, 24, BARK_DEEP, tx * .01, OL_FINE, shade=INK_SOFT)
    d.add(face(506, 168, 100, mass_w=184, default="delighted", tilt=-3.0,
               eyes=((-52, -20), (50, -26)), eye_r=(21, 29), mouth=(4, 50),
               mouth_k=1.10))

    # ---- the conga line ----
    _worker_ant(d, 386, 624, 152, -62, 2.2)
    _worker_ant(d, 614, 792, 146, 58, 5.5)
    # ODDITY: the last ant is going the WRONG WAY, carrying a leaf
    _worker_ant(d, 408, 856, 142, 126, 9.9, carry=True)
    return d.svg()


# =====================================================================
# 2. a-airplane-tree   WACKY -- face on the TRUNK (not the canopy)
#    Wide, low, flat-shouldered canopy; two aeroplanes fly OUT of the
#    silhouette on both sides so the dome is broken on purpose.
# =====================================================================
def _plane(d, cx, cy, L, deg, body, wing, seed):
    """Side-on toy aeroplane: fuselage + one fat wing + tail fin + prop."""
    H = L * 0.34

    def P(pts, r):
        return hard_poly(place([(x * L, y * H) for x, y in pts], cx, cy,
                               deg), r)

    def A(x, y):
        return place([(x * L, y * H)], cx, cy, deg)[0]

    # tail fin, behind everything
    d.form(P([(-.52, -.06), (-.34, -.86), (-.16, -.84), (-.20, -.02)], L * .05),
           wing, sweep_hard(A(-.32, -.44)[0], A(-.32, -.44)[1], L * .11,
                            H * .34), None, ol=OL_PROP)
    # fuselage: fat cigar, blunt tail, rounded nose
    d.form(P([(-.54, -.20), (-.16, -.34), (.26, -.32), (.50, -.10),
              (.50, .12), (.24, .32), (-.18, .34), (-.52, .20)], L * .12),
           body, sweep_hard(cx, cy, L * .32, H * .34, lo=.20, hi=-.32),
           None, ol=OL_MAIN)
    # cockpit bubble
    cp = A(.10, -.22)
    d.form(circ(cp[0], cp[1], L * .105, seed, 10, .04, L * .082, deg),
           CREAM, sweep(cp[0], cp[1], L * .105, L * .082, lo=.26, hi=-.42),
           CREAM_DEEP, ol=OL_FINE)
    # THE wing -- one fat paddle crossing the belly, sticking out below
    d.form(P([(-.10, .12), (.26, .06), (.10, .70), (-.46, .82)], L * .08),
           wing, sweep_hard(A(-.06, .50)[0], A(-.06, .50)[1], L * .22,
                            H * .28), None, ol=OL_MAIN)
    d.line(("M%.1f,%.1f L%.1f,%.1f" % (A(.14, .26) + A(-.18, .74))),
           OL_FINE)
    # propeller + spinner at the nose
    n0 = A(.52, .00)
    d.form(slab(n0[0], n0[1], L * .075, L * .30, 0.46, deg + 9), STEEL,
           sweep_hard(n0[0], n0[1], L * .05, L * .15), STEEL_DEEP, ol=OL_FINE)
    d.form(circ(n0[0], n0[1], L * .055, seed + 2, 9, .05, L * .055, deg),
           STEEL_DEEP, None, STEEL_DARK, ol=OL_FINE)


def airplane_tree():
    d = Doc()
    # ---- trunk (drawn first: canopy always covers the tips) ----
    d.form(trunk_chunky(500, 458, BASE_Y, 146, 244, root_seed=7.7, lean=6,
                        root_lobes=3, root_depth=(18, 30), flare=1.10),
           BARK, sweep(516, 760, 122, 270, lo=.14, hi=-.12, wob=.06),
           BARK_DEEP,
           inner=('<path d="M418,700 C432,790 424,880 440,952" fill="none" '
                  'stroke="%s" stroke-width="%d" %s/>'
                  % (INK, OL_MAIN, RJ)))
    # ---- vapour trails: background weight, hue-matched, never black ----
    swoosh(d, 150, 232, 336, 176, 0.24, GRASS_DARK)
    swoosh(d, 166, 286, 342, 228, 0.20, GRASS_DARK)
    swoosh(d, 902, 748, 742, 632, -0.22, GRASS_DARK)

    # a LONG, SHALLOW cloud-bank canopy: the anti-dome
    clump(d, [(232, 402, 138, 96, GRASS, 9, -100, None, 2.2),
              (796, 406, 136, 94, GRASS, 9, -84, None, 4.4),
              (338, 350, 178, 112, LEAF, 10, -96, None, 6.6),
              (688, 356, 174, 110, LEAF, 10, -92, 5, 8.8),
              (424, 436, 150, 92, GRASS, 9, -105, None, 13.2),
              (622, 440, 146, 90, GRASS, 9, -85, None, 15.4),
              (512, 344, 196, 122, LEAF, 11, -97, None, 11.0)])
    marks(d, [(206, 376, 84, 48, -28, GRASS_DARK),
              (330, 404, 82, 46, 16, GRASS_DEEP),
              (424, 300, 86, 48, -22, GRASS_DEEP),
              (620, 306, 78, 44, 30, GRASS_DEEP),
              (822, 382, 82, 48, -14, GRASS_DARK),
              (742, 404, 80, 46, 22, GRASS_DARK),
              (268, 438, 82, 48, -34, GRASS_DEEP),
              (566, 424, 76, 44, 8, GRASS_DEEP),
              (782, 316, 78, 44, 40, GRASS_DARK)])

    _plane(d, 246, 196, 296, -22, FRUIT, SUN, 3.3)
    _plane(d, 808, 654, 262, 17, SKY_HI, CREAM, 6.1)
    # ODDITY: a paper plane stuck nose-first in the canopy
    d.form(hard_poly([(452, 216), (538, 172), (482, 254), (468, 230)], 10),
           CREAM, sweep_hard(494, 216, 40, 30), CREAM_DEEP, ol=OL_FINE)

    # face lives on the TRUNK -- 140 on a 260-wide shaft = 53.8%
    d.add(face(492, 740, 122, mass_w=224, default="surprised", tilt=2.0,
               eyes=((-44, -8), (46, -16)), eye_r=(24, 28), mouth=(0, 50),
               mouth_k=1.05, brow_lift=6))
    return d.svg()


# =====================================================================
# 3. b-burger-bush   WACKY -- face on the TOP BUN
#    A whole burger sitting on a low bush: the mass is a WIDE HORIZONTAL
#    LAYER STACK, which no other plant in the set has.
# =====================================================================
def burger_bush():
    d = Doc()
    d.form(stem_slim(508, 600, BASE_Y, 82, root_seed=19.3, lean=10,
                     w_base=214, root_lobes=3, root_depth=(18, 32)),
           GRASS, sweep(520, 850, 66, 170, lo=.06, hi=-.12, wob=.03),
           GRASS_DEEP)
    clump(d, [(304, 872, 122, 94, GRASS, 9, -102, None, 3.3),
              (712, 862, 126, 96, GRASS, 9, -86, None, 5.5),
              (508, 848, 156, 102, LEAF, 10, -96, 6, 7.7)])
    marks(d, [(286, 856, 74, 42, -26, GRASS_DARK),
              (700, 844, 70, 40, 24, GRASS_DARK),
              (470, 824, 76, 44, -12, GRASS_DEEP),
              (588, 884, 68, 40, 34, GRASS_DEEP)])

    # ---- mini burgers hanging like fruit ----
    for (bx, by, s, sd) in ((172, 908, 0.24, 21.1), (856, 890, 0.21, 24.4)):
        w = 620 * s
        d.form(hard_poly([(bx - w * .5, by + w * .16),
                          (bx + w * .5, by + w * .16),
                          (bx + w * .44, by + w * .40),
                          (bx - w * .46, by + w * .40)], w * .14),
               SUN_DEEP, sweep_hard(bx, by + w * .30, w * .3, w * .12),
               RAY_SHADE, ol=OL_FINE)
        d.form(hard_poly([(bx - w * .52, by), (bx + w * .52, by),
                          (bx + w * .46, by + w * .18),
                          (bx - w * .48, by + w * .18)], w * .08), BARK,
               sweep_hard(bx, by + w * .10, w * .3, w * .09), BARK_DEEP,
               ol=OL_FINE)
        J, B = lobe_profile(sd, 9, jit=0.09, bul=(6, 15))
        d.form(canopy_blob(bx, by - w * .18, w * .50, w * .30, 9, J, B),
               SUN_DEEP, sweep(bx, by - w * .18, w * .5, w * .3, lo=.28,
                               hi=-.44), RAY_SHADE, ol=OL_FINE)

    # ---- THE BURGER ----
    # bottom bun
    d.form(hard_poly([(206, 512), (804, 512), (770, 602), (240, 602)], 44),
           SUN_DEEP, sweep_hard(504, 562, 268, 46, lo=.24, hi=-.30),
           RAY_SHADE, ol=OL_MAIN)
    # patty
    d.form(hard_poly([(184, 434), (826, 434), (818, 524), (190, 524)], 34),
           BARK, sweep_hard(504, 482, 290, 46, lo=.22, hi=-.30), BARK_DEEP,
           ol=OL_MAIN)
    # cheese, with two drips
    d.form(smooth_closed([(196, 384), (814, 384), (824, 432),
                          (776, 498), (718, 434), (604, 450), (494, 432),
                          (376, 452), (280, 434), (222, 504), (188, 430)]),
           SUN, sweep(504, 436, 288, 52, lo=.22, hi=-.34), SUN_SHADE,
           ol=OL_MAIN)
    # lettuce frill -- pokes out WIDER than the buns
    J, B = lobe_profile(31.8, 17, jit=0.10, bul=(12, 30))
    d.form(canopy_blob(506, 376, 344, 52, 17, J, B, start=-8), LEAF,
           sweep(506, 376, 344, 52, lo=.26, hi=-.40, wob=.10), GRASS,
           ol=OL_MAIN)
    # a pickle peeking out
    d.form(circ(300, 418, 56, 7.7, 10, .07, 34, -14), GRASS_DEEP,
           sweep(300, 418, 56, 34, lo=.26, hi=-.42), GRASS_DARK, ol=OL_FINE)
    # top bun (the dome the face lives on)
    d.form(smooth_closed([(200, 380), (214, 282), (300, 204), (428, 168),
                          (552, 162), (686, 192), (778, 262), (812, 364),
                          (786, 388), (506, 398), (230, 392)]),
           SUN_DEEP, sweep(506, 292, 306, 120, lo=.30, hi=-.42, wob=.06),
           RAY_SHADE, ol=OL_MAIN)
    for (sx, sy, dg) in ((326, 262, -22), (426, 224, 8), (540, 212, -12),
                         (640, 240, 26), (704, 306, -6), (392, 306, 18)):
        d.fill(slab(sx, sy, 46, 22, 0.50, dg), CREAM)
    # ODDITY: one sesame seed has slid off and sits on the lettuce
    d.fill(slab(614, 370, 44, 21, 0.50, 62), CREAM)

    d.add(face(504, 284, 322, mass_w=608, default="delighted", tilt=-1.5,
               eyes=((-58, -4), (60, -10)), eye_r=(26, 22), mouth=(2, 40),
               mouth_k=1.30))
    return d.svg()


# =====================================================================
# 4. c-carrot-plant   REALISTIC -- NO FACE
#    A fat orange cone under a feathery fan.  Mass is bottom-heavy and
#    pointed: the inverse of every canopy-on-a-trunk in the set.
# =====================================================================
def _feather(d, x0, y0, x1, y1, k, w0, w1, Lp, col, colsh, n=9,
             outlined=True, tilt=22, wide=0.60, seed=0.0):
    """A pinnate frond: a tapered rachis with leaflets down both sides.

    The rachis is deliberately FAT (never under ~26px) -- a thin ribbon at
    OL_PROP renders as a bare black stick at game size, which is what the
    first pass of both the fern and the carrot looked like.
    """
    sp = bow(x0, y0, x1, y1, k, n)
    ws = [w0 + (w1 - w0) * (i / float(n - 1)) ** 0.8 for i in range(n)]
    rach = ribbon(sp, ws, cap0="flat", cap1="round")
    if outlined:
        d.form(rach, colsh,
               sweep((x0 + x1) / 2, (y0 + y1) / 2, abs(x1 - x0) * .5 + 30,
                     abs(y1 - y0) * .5 + 30, lo=.24, hi=-.38, seed=k * 9),
               colsh, ol=OL_FINE)
    else:
        # background rank: hue-matched, NO black outline (TOCA depth-step)
        d.fill(rach, colsh)
    jz = jitter(seed + 1.7, n, 0.13, 1.0)
    for i in range(1, n):
        t = i / float(n - 1)
        px, py = sp[i]
        ang = math.degrees(math.atan2(sp[i][1] - sp[i - 1][1],
                                      sp[i][0] - sp[i - 1][0]))
        L = Lp * (1.0 - 0.60 * t) * jz[i]
        for sgn in (-1, 1):
            dg = ang + sgn * (90 - tilt) + 90
            lf = leaf_round(px, py, L, L * wide, dg,
                            curl=.12 * sgn)
            if outlined:
                d.form(lf, col, sweep(px, py, L * .32, L * .32, lo=.26,
                                      hi=-.42, seed=i + t), colsh,
                       ol=OL_FINE)
            else:
                d.fill(lf, col)


def carrot_plant():
    d = Doc()
    # ---- the fronds, back rank first (unoutlined = depth-stepped) ----
    for (tx, ty, k, w0, Lp, col, sh, ou, nn, sd) in (
            (140, 300, 0.22, 52, 118, GRASS_DEEP, GRASS_DEEP, False, 10, 1.1),
            (876, 340, -0.22, 50, 114, GRASS_DEEP, GRASS_DEEP, False, 10, 2.2),
            (280, 190, 0.14, 54, 120, GRASS, GRASS, False, 10, 3.3),
            (738, 208, -0.15, 52, 130, GRASS, GRASS_DEEP, True, 8, 4.4),
            (430, 122, 0.05, 58, 142, LEAF, GRASS, True, 9, 5.5),
            (618, 146, -0.06, 56, 138, LEAF, GRASS, True, 8, 6.6)):
        _feather(d, 504, 486, tx, ty, k, w0, 26, Lp, col, sh, nn, ou,
                 tilt=26, wide=0.66, seed=sd)
    # ODDITY: one frond has flopped right over and hangs down
    _feather(d, 520, 492, 902, 616, -0.34, 48, 24, 112, GRASS, GRASS_DEEP,
             8, True, tilt=26, wide=0.66, seed=7.7)

    # ---- the carrot ----
    body = smooth_closed([(374, 458), (352, 566), (378, 692), (416, 810),
                          (462, 928), (498, 1000), (532, 926),
                          (578, 806), (620, 676), (646, 552), (652, 452),
                          (560, 424), (498, 416), (432, 428)])
    ridges = "".join(
        '<path d="M%d,%d Q%d,%d %d,%d" fill="none" stroke="%s" '
        'stroke-width="%d" %s/>' % (ax, ay, (ax + bx) // 2, ay + 26, bx, by,
                                    INK, OL_MAIN, RJ)
        for (ax, ay, bx, by) in ((360, 528, 646, 512), (368, 622, 634, 600),
                                 (390, 726, 610, 700), (416, 828, 578, 804),
                                 (444, 916, 546, 898)))
    d.form(body, ACCENT_DEEP, sweep(504, 700, 160, 300, lo=.22, hi=-.30,
                                    wob=.05), EMBER_DEEP, inner=ridges)
    # root hairs
    for (hx, hy, dx, dy) in ((362, 590, -54, 34), (640, 672, 56, 28),
                             (392, 786, -48, 30), (600, 826, 46, 26)):
        d.add('<path d="M%d,%d Q%d,%d %d,%d" fill="none" stroke="%s" '
              'stroke-width="%d" %s/>'
              % (hx, hy, hx + dx // 2, hy + dy - 10, hx + dx, hy + dy,
                 EMBER_DEEP, OL_FINE, RJ))
    # green shoulder collar
    J, B = lobe_profile(26.4, 10, jit=0.10, bul=(10, 24))
    d.form(canopy_blob(506, 452, 152, 50, 10, J, B, start=-4), GRASS,
           sweep(506, 452, 152, 50, lo=.24, hi=-.38), GRASS_DEEP, ol=OL_MAIN)
    return d.svg()


# =====================================================================
# 5. c-caterpillar-vine   SILLY -- face
#    An S-curved vine with a fat yellow caterpillar humping up it.
# =====================================================================
def caterpillar_vine():
    d = Doc()
    d.form(stem_slim(492, 890, BASE_Y, 92, root_seed=17.2, lean=-8,
                     w_base=224, root_lobes=3, root_depth=(18, 30)),
           GRASS, sweep(500, 950, 70, 60, lo=.10, hi=-.16, wob=.03),
           GRASS_DEEP)
    spine = [(492, 936), (466, 848), (390, 776), (346, 672), (388, 566),
             (494, 508), (588, 440), (620, 336), (568, 250)]
    sp = []
    for i in range(len(spine) - 1):
        sp.append(spine[i])
        sp.append(((spine[i][0] + spine[i + 1][0]) / 2.0,
                   (spine[i][1] + spine[i + 1][1]) / 2.0))
    sp.append(spine[-1])
    ws = [84 - 34 * (i / float(len(sp) - 1)) for i in range(len(sp))]
    d.form(ribbon(sp, ws, cap0="flat", cap1="round"), GRASS,
           sweep(480, 600, 190, 320, lo=.20, hi=-.28, wob=.07), GRASS_DEEP)
    # the tendril curl at the top
    cu = spiral(506, 214, 106, 0.92, 8, 13, 0.72)
    d.form(ribbon([(568, 250)] + cu, [50] + [48 - 24 * (i / 12.0)
                                             for i in range(13)],
                  cap0="flat", cap1="round"), GRASS,
           sweep(506, 214, 110, 110, lo=.24, hi=-.40), GRASS_DEEP, ol=OL_PROP)

    # ---- vine leaves ----
    for (lx, ly, L, Wd, dg, col, sh, nib) in (
            (414, 782, 232, 148, -58, GRASS_DEEP, GRASS_DARK, False),
            (348, 646, 214, 136, -122, GRASS, GRASS_DEEP, True),
            (612, 456, 216, 134, 84, GRASS, GRASS_DEEP, False),
            (626, 336, 178, 114, 132, GRASS_DEEP, GRASS_DARK, False),
            (486, 512, 198, 126, 44, LEAF, GRASS, False)):
        pth = leaf_round(lx, ly, L, Wd, dg)
        eo = False
        if nib:                      # ODDITY: the caterpillar has been eating
            tip = place([(0, -L * .62)], lx, ly, dg)[0]
            pth += " " + bite(tip[0], tip[1], 34)
            eo = True
        d.form(pth, col, sweep(lx, ly, Wd * .6, L * .5, lo=.22, hi=-.38,
                               seed=lx * .01), sh, ol=OL_PROP, evenodd=eo)
        d.line(vein(lx, ly, L, dg), OL_FINE)

    # ---- the caterpillar ----
    SEG = [(300, 872, 96), (356, 748, 82), (330, 632, 78), (400, 534, 74),
           (498, 462, 70), (582, 392, 64), (626, 300, 52)]
    for i, (bx, by, r) in enumerate(reversed(SEG)):
        ball(d, bx, by, r, SUN if i % 2 else SUN_DEEP, 3.1 + i * 2.7,
             OL_PROP, ry=r * .94, deg=i * 7 - 10,
             shade=SUN_SHADE if i % 2 else RAY_SHADE, gloss=0.30)
        if i < 6:
            fx, fy = bx - r * .30, by + r * .86
            d.form(circ(fx, fy, r * .26, i * 3.3, 8, .08, r * .20), ACCENT,
                   None, ACCENT_DEEP, ol=OL_FINE)
    for (tx, ty, kx) in ((238, 706, -30), (352, 700, 26)):
        d.add('<path d="M%d,%d Q%d,%d %d,%d" fill="none" stroke="%s" '
              'stroke-width="%d" %s/>'
              % (286 if tx < 300 else 320, 812, (tx + 300) // 2 + kx, 744,
                 tx, ty, INK, OL_PROP, RJ))
        ball(d, tx, ty, 26, FRUIT, tx * .01, OL_FINE, shade=FRUIT_DEEP)
    d.add(face(300, 880, 100, mass_w=184, default="happy", tilt=8.0,
               eyes=((-40, -22), (44, -16)), eye_r=(22, 30), mouth=(-4, 52),
               mouth_k=1.15))
    return d.svg()


# =====================================================================
# 6. c-cupcake-tree   WACKY -- face on the WRAPPER
#    One enormous cupcake as the crown: a soft-serve swirl over a fluted
#    trapezoid over a trunk.  Nothing else in the set is a cone.
# =====================================================================
def cupcake_tree():
    d = Doc()
    d.form(trunk_chunky(500, 700, BASE_Y, 128, 236, root_seed=13.9, lean=-8,
                        root_lobes=3, root_depth=(18, 30), flare=0.95),
           BARK, sweep(514, 860, 130, 160, lo=.16, hi=-.16, wob=.06),
           BARK_DEEP,
           inner=('<path d="M446,780 C458,850 450,910 462,964" fill="none" '
                  'stroke="%s" stroke-width="%d" %s/>' % (INK, OL_MAIN, RJ)))
    # two little leaves sprouting from the trunk
    for (lx, ly, L, Wd, dg) in ((424, 812, 190, 118, -78), (582, 852, 170,
                                                            104, 74)):
        d.form(leaf_round(lx, ly, L, Wd, dg), GRASS,
               sweep(lx, ly - L * .4, Wd * .6, L * .4, lo=.22, hi=-.38),
               GRASS_DEEP, ol=OL_PROP)
        d.line(vein(lx, ly, L, dg), OL_FINE)

    # ---- the wrapper ----
    wrap = hard_poly([(316, 578), (696, 578), (648, 806), (366, 806)], 26)
    flutes = "".join(
        '<path d="M%d,%d L%d,%d" fill="none" stroke="%s" stroke-width="%d" '
        '%s/>' % (tx, 584, bx, 802, INK, OL_MAIN, RJ)
        for (tx, bx) in ((370, 410), (642, 606)))
    d.form(wrap, ACCENT, sweep_hard(506, 692, 200, 114, lo=.20, hi=-.28),
           ACCENT_DEEP, inner=flutes)
    d.form(slab(506, 570, 414, 46, 0.34), ACCENT_DEEP,
           sweep_hard(506, 570, 207, 23), BARK, ol=OL_MAIN)

    # ---- the frosting swirl ----
    for (cx, cy, rx, ry, n, sd) in ((506, 520, 202, 100, 12, 5.1),
                                    (498, 414, 162, 90, 11, 9.3),
                                    (510, 318, 122, 78, 10, 14.7),
                                    (500, 238, 76, 56, 9, 19.1)):
        J, B = lobe_profile(sd, n, jit=0.09, bul=(14, 34))
        d.form(canopy_blob(cx, cy, rx, ry, n, J, B, start=-4), BERRY,
               sweep(cx, cy, rx, ry, lo=.28, hi=-.42, wob=.08, seed=sd),
               BERRY_DEEP)
    sprinkle(d, [(392, 486, 46, 20, -34, SUN), (582, 500, 44, 19, 22, CREAM),
                 (470, 424, 46, 20, 58, GRASS), (566, 396, 42, 19, -18,
                                                 SKY_HI),
                 (430, 330, 44, 20, 34, SUN), (556, 316, 42, 18, -46, CREAM),
                 (488, 268, 40, 18, 12, GRASS), (620, 470, 42, 18, -8, SUN),
                 (352, 512, 44, 19, 44, SKY_HI), (528, 350, 40, 18, 70,
                                                  ACCENT)])
    # cherry, on a bent stalk
    d.add('<path d="M508,198 C516,150 546,132 578,126" fill="none" '
          'stroke="%s" stroke-width="%d" %s/>' % (GRASS_DEEP, OL_PROP, RJ))
    d.form(fruit_blob(506, 172, 62, -8), FRUIT,
           sweep(506, 172, 62, 62, lo=.30, hi=-.46), FRUIT_DEEP, ol=OL_PROP,
           inner='<path d="%s" fill="%s" opacity="0.80"/>'
                 % (chip(482, 148, 22), CREAM))
    # ODDITY: one sprinkle has fallen onto the trunk
    d.fill(slab(468, 830, 44, 19, 0.50, -62), SUN)

    d.add(face(504, 682, 208, mass_w=380, default="happy", tilt=-2.5,
               eyes=((-50, -12), (52, -18)), eye_r=(20, 24), mouth=(6, 44)))
    return d.svg()


# =====================================================================
# 7. d-daffodil   REALISTIC -- NO FACE
#    Six pointed petals around a deep frilled trumpet, on a narrow stem
#    with two blade leaves.  Tall and slim where the sunflower is broad.
# =====================================================================
def daffodil():
    d = Doc()
    for (bx, by, tx, ty, hw, tw, bend) in ((456, 998, 358, 402, 46, 20, -66),
                                           (552, 998, 646, 356, 42, 18, 58),
                                           (516, 998, 560, 542, 34, 15, 26)):
        d.form(leaf_blade(bx, by, tx, ty, hw, tw, bend), GRASS_DEEP,
               sweep((bx + tx) / 2, (by + ty) / 2, 70, 300, lo=.16, hi=-.24,
                     wob=.04, seed=bx * .01), GRASS_DARK)
    d.form(stem_slim(496, 470, BASE_Y, 64, root_seed=23.6, lean=14,
                     w_base=176, root_lobes=3, root_depth=(16, 28)),
           GRASS, sweep(508, 760, 54, 264, lo=.06, hi=-.12, wob=.03),
           GRASS_DEEP)
    # papery spathe where the flower meets the stem
    d.form(leaf_pointed(486, 512, 152, 74, deg=-38, curl=.10), BARK_LITE,
           sweep(452, 460, 46, 62, lo=.24, hi=-.38), BARK, ol=OL_PROP)

    HX, HY = 500, 344
    LEN = (272, 258, 280, 264, 196, 268)          # index 4 is the stub petal
    ANG = (-2.5, 3.0, -1.6, 4.2, -6.5, 1.8)
    for i in range(6):
        dg = i * 60 + ANG[i]
        d.form(leaf_pointed(HX, HY, LEN[i], 128, dg, curl=.16 if i % 2 else -.13),
               SUN, sweep(HX, HY - LEN[i] * .4, 92, LEN[i] * .48, lo=.26,
                          hi=-.40, seed=i * 1.7), SUN_SHADE)
        d.line(vein(HX, HY, LEN[i] * .92, dg, frac=0.62), OL_FINE)
    # the trumpet: a frilled cup with a dark mouth
    J, B = lobe_profile(37.2, 13, jit=0.09, bul=(10, 26))
    d.form(canopy_blob(HX, HY + 2, 126, 114, 13, J, B, start=-96), ACCENT,
           sweep(HX, HY, 126, 114, lo=.26, hi=-.42, wob=.08), ACCENT_DEEP)
    J, B = lobe_profile(41.8, 10, jit=0.06, bul=(4, 10))
    d.form(canopy_blob(HX + 8, HY + 10, 54, 48, 10, J, B, start=-84),
           ACCENT_DEEP, None, EMBER_DEEP, ol=OL_PROP)
    # a few frill ticks on the rim only -- never a full spoke wheel
    for a0 in (-152, -74, 22, 112):
        a = math.radians(a0)
        d.line("M%.1f,%.1f L%.1f,%.1f"
               % (HX + 68 * math.cos(a), HY + 62 * math.sin(a),
                  HX + 116 * math.cos(a), HY + 104 * math.sin(a)), OL_FINE)
    return d.svg()


# =====================================================================
# 8. d-duck-bloom   "Ducky Daisy"   SILLY -- face, bill, and WEBBED FEET
# =====================================================================
def duck_bloom():
    d = Doc()
    # webbed feet FIRST is wrong -- they go in front; stem and leaf first
    d.form(leaf_round(566, 812, 250, 158, deg=70), GRASS,
           sweep(680, 736, 90, 120, lo=.22, hi=-.38), GRASS_DEEP)
    d.line(vein(566, 812, 250, 70), OL_FINE)
    d.form(leaf_pointed(444, 890, 186, 104, deg=-66, curl=.14), GRASS_DEEP,
           sweep(360, 838, 60, 78, lo=.20, hi=-.36), GRASS_DARK, ol=OL_PROP)
    d.form(stem_slim(500, 520, 972, 70, root_seed=8.8, lean=-12,
                     w_base=150, root_lobes=3, root_depth=(14, 24)),
           GRASS, sweep(512, 760, 56, 230, lo=.06, hi=-.12, wob=.03),
           GRASS_DEEP)

    HX, HY = 500, 342
    PL = (206, 214, 262, 268, 240, 208, 216, 202, 210, 218, 204, 212)
    for i in range(12):
        dg = i * 30 + (2.4 if i % 3 else -3.1) + (i % 5) * 1.2
        d.form(leaf_round(HX, HY, PL[i], 128, dg, curl=.10 if i % 2 else -.08),
               CREAM, sweep(HX, HY - PL[i] * .40, 72, PL[i] * .46, lo=.26,
                            hi=-.40, seed=i * 2.3), CREAM_DEEP, ol=OL_PROP)
    J, B = lobe_profile(28.9, 12, jit=0.05, bul=(6, 14))
    d.form(canopy_blob(HX, HY + 4, 134, 126, 12, J, B, start=-92), SUN,
           sweep(HX, HY, 134, 126, lo=.28, hi=-.44, wob=.06), SUN_SHADE)
    # the bill
    d.form(smooth_closed([(414, 398), (500, 384), (592, 400), (600, 440),
                          (500, 478), (406, 440)]), ACCENT,
           sweep(500, 432, 96, 42, lo=.20, hi=-.32), ACCENT_DEEP,
           ol=OL_PROP)
    for (nx, ny) in ((466, 404), (538, 402)):
        d.fill(circ(nx, ny, 11, nx * .01, 8, .10, 9), INK_SOFT)
    d.add(face(500, 364, 150, mass_w=264, default="happy", tilt=3.0,
               eyes=((-42, -30), (44, -34)), eye_r=(18, 23), mouth=(0, 58),
               mouth_k=0.85))

    # ---- webbed feet, in front of everything ----
    for (fx, fy, dg, w) in ((430, 926, -12, 150), (578, 930, 9, 140)):
        toes = place([(-w * .5, 0), (-w * .30, -34), (-w * .10, 2),
                      (0, -36), (w * .14, 0), (w * .34, -32),
                      (w * .5, 4), (w * .30, 46), (-w * .28, 44)],
                     fx, fy + 8, dg)
        d.form(smooth_closed(toes), ACCENT,
               sweep(fx, fy + 14, w * .5, 30, lo=.18, hi=-.32),
               ACCENT_DEEP, ol=OL_PROP)
        d.line("M%.0f,%.0f L%.0f,%.0f" % (fx, fy + 40, fx, fy - 24), OL_FINE)
    # ODDITY: a third, smaller "chick" foot print left in the dirt
    d.form(smooth_closed(place([(-34, 0), (-18, -20), (0, 2), (16, -20),
                                (34, 2), (18, 28), (-18, 26)],
                               748, 960, 22)), ACCENT_DEEP, None, EMBER_DEEP,
           ol=OL_FINE)
    return d.svg()


# =====================================================================
# 9. d-donut-tree   "Dancing Donut Tree"   WACKY -- face on the trunk
#    An S-bent trunk with both arms thrown up, a donut in each hand, and
#    one root foot KICKED clean off the ground.
# =====================================================================
def _donut(d, cx, cy, R, hole, ice, ice_sh, seed, drips=6):
    ring = circ(cx, cy, R, seed, 14, .028) + " " + bite(cx, cy, hole)
    d.form(ring, BARK_LITE, sweep(cx, cy, R, R, lo=.30, hi=-.44, seed=seed),
           BARK, ol=OL_MAIN, evenodd=True)
    # frosting: the top of the ring with a drippy lower edge
    pts = []
    for i in range(11):
        a = math.radians(178 - 176 * i / 10.0)
        pts.append((cx + R * .995 * math.cos(a), cy - R * .995 * math.sin(a)))
    dj = jitter(seed + 3.0, drips, 0.34, 1.0)
    for i in range(drips):
        t = 1.0 - i / float(drips - 1)
        x = cx - R * .96 + 2 * R * .96 * t
        pts.append((x, cy + R * (0.10 + 0.44 * dj[i])))
        pts.append((x - R * .16, cy - R * 0.02))
    d.form(smooth_closed(pts) + " " + bite(cx, cy, hole * 1.08), ice,
           sweep(cx, cy - R * .1, R, R * .7, lo=.28, hi=-.44, seed=seed + 1),
           ice_sh, ol=OL_PROP, evenodd=True)
    sp = []
    for i in range(9):
        a = math.radians(-152 + i * 34 + (i % 3) * 9)
        rr = R * (0.52 + 0.13 * ((i * 5) % 3))
        sp.append((cx + rr * math.cos(a), cy + rr * math.sin(a) * .92,
                   40, 17, (i * 47) % 180,
                   (CREAM, SUN, GRASS, SKY_HI)[i % 4]))
    sprinkle(d, sp)


def donut_tree():
    d = Doc()
    d.form(trunk_chunky(452, 690, BASE_Y, 198, 274, root_seed=27.1, lean=40,
                        root_lobes=3, root_depth=(20, 34), flare=1.22),
           BARK, sweep(470, 850, 150, 180, lo=.16, hi=-.16, wob=.06),
           BARK_DEEP)
    # upper trunk bends back the other way: the S
    up = bow(494, 726, 470, 476, -0.16, 6)
    d.form(ribbon(up, [186, 176, 168, 158, 150, 142], cap0="flat",
                  cap1="round"), BARK,
           sweep(482, 600, 100, 140, lo=.18, hi=-.20, wob=.05), BARK_DEEP)
    # arms thrown up
    for (x0, y0, x1, y1, w0, w1, k) in ((432, 546, 240, 344, 104, 62, -0.24),
                                        (508, 520, 770, 326, 100, 58, 0.30)):
        d.form(branch(x0, y0, x1, y1, w0, w1, k), BARK,
               sweep((x0 + x1) / 2, (y0 + y1) / 2, 110, 90, lo=.20, hi=-.26),
               BARK_DEEP)
    swoosh(d, 132, 240, 244, 160, 0.22, BARK_DEEP)
    swoosh(d, 918, 226, 814, 146, -0.22, BARK_DEEP)
    swoosh(d, 596, 866, 742, 856, -0.30, BARK_DEEP)
    _donut(d, 214, 292, 142, 50, FRUIT, FRUIT_DEEP, 4.4, 6)
    _donut(d, 810, 268, 130, 46, BERRY, BERRY_DEEP, 11.9, 6)
    # ODDITY: one root foot has kicked free of the soil
    d.form(smooth_closed(place([(-84, -30), (-30, -56), (44, -46),
                                (88, -8), (52, 40), (-26, 48), (-82, 24)],
                               662, 928, -22)), BARK,
           sweep(662, 928, 86, 46, lo=.22, hi=-.34), BARK_DEEP, ol=OL_PROP)
    d.line("M600,916 C632,934 676,940 730,924", OL_FINE)
    d.add(face(468, 792, 150, mass_w=262, default="mischief", tilt=-8.0,
               eyes=((-48, -16), (54, -22)), eye_r=(23, 25), mouth=(8, 46),
               mouth_k=1.20, brow_lift=-4))
    return d.svg()


# =====================================================================
# 10. e-eggplant   REALISTIC -- NO FACE
#     A heavy purple teardrop hanging OFF-CENTRE from an arching stalk.
# =====================================================================
def eggplant():
    d = Doc()
    d.form(leaf_round(650, 448, 390, 282, deg=36), GRASS,
           sweep(812, 244, 140, 158, lo=.22, hi=-.38), GRASS_DEEP)
    d.line(vein(650, 448, 390, 36), OL_MAIN)
    for k in (-32, 30):
        d.line(vein(650, 448, 232, 36 + k, frac=0.80), OL_FINE)
    d.form(leaf_round(276, 838, 248, 172, deg=-66), GRASS_DEEP,
           sweep(154, 762, 92, 100, lo=.20, hi=-.36), GRASS_DARK)
    d.line(vein(276, 838, 248, -66), OL_FINE)
    d.form(leaf_round(596, 620, 232, 160, deg=88), GRASS_DEEP,
           sweep(706, 592, 88, 92, lo=.20, hi=-.36), GRASS_DARK, ol=OL_PROP)

    d.form(stem_slim(574, 560, BASE_Y, 100, root_seed=5.2, lean=-14,
                     w_base=232, root_lobes=3, root_depth=(18, 30)),
           GRASS, sweep(586, 800, 80, 210, lo=.08, hi=-.14, wob=.03),
           GRASS_DEEP)
    arc = bow(566, 578, 380, 278, 0.28, 7)
    d.form(ribbon(arc, [96, 90, 84, 78, 72, 66, 58], cap0="flat",
                  cap1="round"), GRASS,
           sweep(466, 450, 110, 150, lo=.18, hi=-.28, wob=.05), GRASS_DEEP)

    fruit = smooth_closed([(376, 302), (282, 366), (210, 500), (192, 674),
                           (254, 838), (374, 922), (494, 852), (556, 682),
                           (528, 496), (450, 368)])
    d.form(fruit, BERRY, sweep(372, 616, 182, 310, lo=.26, hi=-.40, wob=.05),
           BERRY_DEEP,
           inner='<path d="%s" fill="%s" opacity="0.55"/>'
                 % (chip(284, 480, 88, -34), CREAM))
    # calyx: five green lobes clasping the shoulder
    for (dg, L, Wd) in ((-58, 150, 76), (-22, 168, 84), (12, 158, 80),
                        (48, 140, 72), (86, 118, 64)):
        d.form(leaf_pointed(380, 278, L, Wd, dg + 168, curl=.10), GRASS_DEEP,
               sweep(380, 278 + L * .4, Wd * .5, L * .4, lo=.24, hi=-.38),
               GRASS_DARK, ol=OL_PROP)
    # ODDITY: one baby eggplant is only just starting
    d.form(smooth_closed(place([(0, -46), (44, -10), (36, 52), (-4, 74),
                                (-44, 44), (-46, -12)], 636, 690, 14)),
           BERRY, sweep(636, 690, 46, 60, lo=.28, hi=-.42), BERRY_DEEP,
           ol=OL_PROP)
    d.form(leaf_pointed(646, 522, 74, 46, -30), GRASS_DEEP, None,
           GRASS_DARK, ol=OL_FINE)
    return d.svg()


# =====================================================================
# 11. e-elephant-ear   SILLY -- face, two ear-leaves, a dangling trunk
# =====================================================================
def elephant_ear():
    d = Doc()
    d.form(stem_slim(506, 700, BASE_Y, 104, root_seed=33.6, lean=6,
                     w_base=240, root_lobes=4, root_depth=(18, 30)),
           GRASS, sweep(520, 870, 84, 150, lo=.08, hi=-.14, wob=.03),
           GRASS_DEEP)
    for (lx, ly, L, Wd, dg, col, sh) in (
            (472, 902, 258, 156, -62, GRASS_DEEP, GRASS_DARK),
            (548, 916, 246, 148, 58, GRASS_DEEP, GRASS_DARK),
            (486, 852, 216, 134, -100, GRASS, GRASS_DEEP),
            (540, 862, 208, 130, 96, GRASS, GRASS_DEEP)):
        d.form(leaf_round(lx, ly, L, Wd, dg), col,
               sweep(lx, ly - L * .4, Wd * .6, L * .4, lo=.20, hi=-.36,
                     seed=lx * .01), sh, ol=OL_PROP)
        d.line(vein(lx, ly, L, dg), OL_FINE)

    # ---- the ears ----
    for (bx, by, L, Wd, dg, nib) in ((352, 348, 306, 334, -104, False),
                                     (668, 342, 298, 320, 100, True)):
        pth = leaf_round(bx, by, L, Wd, dg)
        eo = False
        if nib:                                   # ODDITY: a notched ear
            tip = place([(Wd * .30, -L * .70)], bx, by, dg)[0]
            pth += " " + bite(tip[0], tip[1], 44)
            eo = True
        d.form(pth, LEAF, sweep(bx + (-140 if dg < 0 else 140), by - 40,
                                Wd * .5, L * .5, lo=.26, hi=-.40,
                                seed=bx * .01), GRASS, evenodd=eo)
        d.line(vein(bx, by, L * .96, dg, frac=0.66), OL_MAIN)
        for k in (-30, 30):
            d.line(vein(bx, by, L * .62, dg + k, frac=0.72), OL_FINE)

    # ---- the head ----
    J, B = lobe_profile(46.2, 11, jit=0.07, bul=(16, 40))
    d.form(canopy_blob(508, 344, 186, 174, 11, J, B, start=-94), LEAF,
           sweep(508, 344, 186, 174, lo=.28, hi=-.42, wob=.08, seed=4.6),
           GRASS)
    d.add(face(508, 338, 190, mass_w=360, default="happy", tilt=1.5,
               eyes=((-62, -22), (64, -26)), eye_r=(17, 21), mouth=(0, 34),
               mouth_k=0.80))
    # a tuft sprouting from the crown
    for (dg, L) in ((-16, 136), (10, 156), (32, 124)):
        d.form(leaf_pointed(506, 216, L, 66, dg, curl=.14), GRASS,
               sweep(506, 216 - L * .4, 30, L * .4, lo=.22, hi=-.38),
               GRASS_DEEP, ol=OL_PROP)
    # ---- the trunk, hanging down and curling up ----
    tp = [(504, 456), (498, 570), (460, 678), (450, 782), (494, 850),
          (558, 846), (584, 794)]
    d.form(ribbon(tp, [104, 96, 88, 80, 70, 60, 48], cap0="flat",
                  cap1="round"), LEAF,
           sweep(500, 700, 78, 160, lo=.22, hi=-.30, wob=.06), GRASS)
    for (rx, ry, rr) in ((498, 552, 44), (464, 664, 40), (460, 772, 36)):
        d.line("M%.0f,%.0f Q%.0f,%.0f %.0f,%.0f"
               % (rx - rr, ry, rx, ry + 18, rx + rr, ry - 6), OL_FINE)
    # two droplets from the trunk tip
    for (dx, dy, r) in ((640, 786, 26), (690, 736, 19)):
        d.form(smooth_closed(place([(0, -r * 1.5), (r * .9, 0),
                                    (0, r * 1.05), (-r * .9, 0)],
                                   dx, dy, 18)), SKY_HI,
               sweep(dx, dy, r, r, lo=.28, hi=-.44), SKY_DEEP, ol=OL_FINE)
    return d.svg()


# =====================================================================
# 12. e-escalator-plant   WACKY -- face on the base mound
#     Five yellow steps climbing left-to-right on green stalks, with a
#     sky-blue handrail.  A diagonal silhouette: unique in the set.
# =====================================================================
def escalator_plant():
    d = Doc()
    XS = graduated(5, 268, 846)
    YS = graduated(5, 848, 300)
    for i, (sx, sy) in enumerate(zip(XS, YS)):
        d.form(stem_slim(sx + (6 if i % 2 else -8), sy + 30, BASE_Y, 60,
                         root_seed=3.4 + i * 6.1, lean=(-9 if i % 2 else 7),
                         w_base=146, root_lobes=3, root_depth=(16, 28)),
               GRASS, sweep(sx, (sy + BASE_Y) / 2, 62, (BASE_Y - sy) * .5,
                            lo=.06, hi=-.12, wob=.03), GRASS_DEEP)
        d.form(leaf_pointed(sx + (34 if i % 2 else -34), sy + 132, 150, 84,
                            (62 if i % 2 else -62), curl=.12), GRASS_DEEP,
               sweep(sx, sy + 66, 46, 60, lo=.20, hi=-.36), GRASS_DARK,
               ol=OL_PROP)
    # handrail, behind the steps
    rail = bow(186, 706, 936, 142, -0.05, 7)
    d.form(ribbon(rail, [46] * 7, cap0="round", cap1="round"), SKY_HI,
           sweep(560, 424, 390, 300, lo=.10, hi=-.16, wob=.04), SKY_DEEP,
           ol=OL_PROP)
    for i in (0, 2, 4):
        px, py = XS[i], YS[i]
        ry = 706 + (142 - 706) * ((px - 186) / 750.0)
        d.form(slab(px - 52, (py + ry) / 2 - 16, 32, abs(py - ry) + 20,
                    0.44, 2), SKY_DEEP,
               sweep_hard(px - 52, (py + ry) / 2 - 16, 16, abs(py - ry) * .5),
               STEEL_DARK, ol=OL_FINE)
    for i, (sx, sy) in enumerate(zip(XS, YS)):
        dg = (2.5, -1.5, 1.0, -2.0, 5.5)[i]      # ODDITY: top step is askew
        outer, inner = panel(sx, sy, 214, 70, r=0.16, deg=dg, inset=0.22)
        d.form(outer, SUN, sweep_hard(sx, sy, 107, 35, lo=.22, hi=-.30),
               SUN_SHADE)
        d.line(inner, OL_FINE)
    # a leaf growing right through step 2
    d.form(leaf_pointed(XS[1] + 40, YS[1] - 14, 168, 92, 22, curl=.14), LEAF,
           sweep(XS[1] + 70, YS[1] - 90, 52, 66, lo=.22, hi=-.38), GRASS,
           ol=OL_PROP)
    # ladybird riding the top step
    LX, LY = XS[4] + 22, YS[4] - 78
    d.form(circ(LX, LY, 66, 8.4, 12, .04, 58), FRUIT,
           sweep(LX, LY, 66, 58, lo=.28, hi=-.44), FRUIT_DEEP, ol=OL_PROP)
    d.line("M%.0f,%.0f L%.0f,%.0f" % (LX - 4, LY - 56, LX + 2, LY + 54),
           OL_FINE)
    dot_spots(d, [(LX - 30, LY - 12, 16, 1.1, 0), (LX + 26, LY - 20, 14, 2.2, 0),
                  (LX - 20, LY + 26, 13, 3.3, 0), (LX + 30, LY + 20, 15, 4.4, 0)],
              INK_SOFT)
    d.form(circ(LX - 4, LY - 72, 34, 5.5, 10, .05, 26), INK_SOFT, None,
           INK_SOFT, ol=OL_FINE)
    for (ax, ay) in ((-26, -104), (22, -108)):
        d.line("M%.0f,%.0f Q%.0f,%.0f %.0f,%.0f"
               % (LX + ax * .5, LY - 82, LX + ax, LY - 96, LX + ax, LY + ay),
               OL_FINE)

    # ---- the base mound, wearing the face ----
    mound = smooth_closed(
        [(104, 984), (128, 862), (198, 782), (296, 748), (398, 782),
         (462, 856), (492, 982)]
        + list(reversed(root_pts(298, 194, BASE_Y, 17.5, lobes=4,
                                 depth=(16, 28)))))
    d.form(mound, LEAF, sweep(298, 880, 196, 130, lo=.24, hi=-.34, wob=.07),
           GRASS)
    marks(d, [(178, 852, 76, 44, -28, GRASS_DEEP),
              (416, 872, 70, 40, 26, GRASS_DEEP)])
    # two tall leaves lean out over the empty upper-left corner
    for (lx, ly, L, Wd, dg, col, sh) in ((214, 856, 312, 148, -62, GRASS,
                                          GRASS_DEEP),
                                         (256, 900, 214, 112, -84,
                                          GRASS_DEEP, GRASS_DARK)):
        d.form(leaf_pointed(lx, ly, L, Wd, dg, curl=.14), col,
               sweep(lx - 70, ly - L * .5, Wd * .6, L * .45, lo=.20,
                     hi=-.36), sh, ol=OL_PROP)
        d.line(vein(lx, ly, L, dg), OL_FINE)
    d.add(face(296, 866, 230, mass_w=420, default="surprised", tilt=-4.0,
               eyes=((-38, -18), (40, -12)), eye_r=(25, 31), mouth=(-2, 52),
               mouth_k=1.05, brow_lift=10))
    return d.svg()


# =====================================================================
# 13. f-fern   REALISTIC -- NO FACE
#     A fountain of arching pinnate fronds with one fiddlehead still
#     curled.  No trunk at all: a wide vase, not a lollipop.
# =====================================================================
def fern():
    d = Doc()
    d.form(stem_slim(506, 856, BASE_Y, 104, root_seed=42.1, lean=0,
                     w_base=262, root_lobes=4, root_depth=(16, 28)),
           GRASS_DEEP, sweep(516, 946, 84, 74, lo=.10, hi=-.16, wob=.03),
           GRASS_DARK)
    BACK = ((58, 512, 0.36, 104, 1.3), (956, 546, -0.36, 100, 2.6),
            (150, 286, 0.28, 106, 3.9), (872, 318, -0.28, 102, 5.2),
            (322, 150, 0.16, 110, 6.5), (698, 166, -0.17, 106, 7.8))
    FRONT = ((150, 440, 0.36, 118, 9.1), (880, 470, -0.36, 114, 10.4),
             (300, 168, 0.24, 124, 11.7), (726, 190, -0.25, 120, 13.0),
             (528, 104, 0.03, 126, 14.3))
    OX = (452, 560, 468, 552, 486, 530)
    for j, (tx, ty, k, Lp, sd) in enumerate(BACK):
        _feather(d, OX[j], 900, tx, ty, k, 40, 18, Lp * 1.16, GRASS_DEEP,
                 GRASS_DEEP, 21, False, tilt=10, wide=0.32, seed=sd)
    FX = (414, 604, 452, 570, 510)
    for i, (tx, ty, k, Lp, sd) in enumerate(FRONT):
        _feather(d, FX[i], 906, tx, ty, k, 44, 20, Lp * 1.16,
                 LEAF if i > 2 else GRASS, GRASS if i > 2 else GRASS_DEEP,
                 21, True, tilt=10, wide=0.32, seed=sd)
    # ODDITY: one frond is still a tightly coiled fiddlehead
    cu = spiral(292, 486, 118, 1.05, 24, 14, 0.78)
    d.form(ribbon([(376, 852), (338, 736), (306, 620)] + cu,
                  [56, 52, 50] + [48 - 26 * (i / 13.0) for i in range(14)],
                  cap0="flat", cap1="round"), GRASS,
           sweep(316, 660, 120, 210, lo=.20, hi=-.32, wob=.05), GRASS_DEEP)
    # a low ruff of short blades round the crown
    for (bx, tx, ty, hw, bend) in ((430, 300, 776, 40, -46),
                                   (470, 386, 730, 36, -22),
                                   (546, 622, 726, 38, 26),
                                   (584, 712, 782, 34, 44)):
        d.form(leaf_blade(bx, 992, tx, ty, hw, 16, bend), GRASS,
               sweep((bx + tx) / 2, (992 + ty) / 2, 60, 130, lo=.18,
                     hi=-.28, seed=bx * .01), GRASS_DEEP, ol=OL_PROP)
    return d.svg()


# =====================================================================
# 14. f-firefly-flower   SILLY -- face, plus two fireflies OFF the mass
# =====================================================================
def _firefly(d, cx, cy, s, deg, seed, lit=True):
    def A(x, y):
        return place([(x * s, y * s)], cx, cy, deg)[0]
    if lit:
        g = A(-.62, .10)
        d.form(star4(g[0], g[1], s * .52, deg - 14, 0.34), BEAM,
               None, SUN, ol=OL_BG, stroke=SUN_DEEP)
    for (ax, ay, r) in ((-.10, -.30, .36), (.22, -.24, .30)):
        w = A(ax, ay)
        d.form(leaf_round(w[0], w[1] + s * .22, s * r * 1.9, s * r * 1.25,
                          deg - 46 + (28 if ax > 0 else 0)), CREAM,
               sweep(w[0], w[1], s * r, s * r, lo=.26, hi=-.42), CREAM_DEEP,
               ol=OL_FINE)
    ab = A(-.34, .06)
    ball(d, ab[0], ab[1], s * .34, SUN if lit else BARK_LITE, seed, OL_PROP,
         ry=s * .29, deg=deg, shade=SUN_SHADE if lit else BARK, gloss=0.32)
    th = A(.04, .00)
    ball(d, th[0], th[1], s * .30, GRASS, seed + 2, OL_PROP, ry=s * .27,
         deg=deg, shade=GRASS_DEEP, gloss=0.30)
    hd = A(.36, -.04)
    ball(d, hd[0], hd[1], s * .26, INK_SOFT, seed + 4, OL_FINE, ry=s * .24,
         deg=deg, shade=INK_SOFT)
    for (tx, ty) in ((.62, -.44), (.72, -.16)):
        t = A(tx, ty)
        d.line("M%.1f,%.1f Q%.1f,%.1f %.1f,%.1f"
               % (hd[0], hd[1] - s * .16, (hd[0] + t[0]) / 2,
                  t[1] - s * .18, t[0], t[1]), OL_FINE)
    if lit:
        for (sx, sy, r) in ((-1.02, -.42, .16), (-.90, .52, .13),
                            (-1.20, .16, .11)):
            q = A(sx, sy)
            d.fill(star4(q[0], q[1], s * r, deg + 24, 0.30), BEAM)


def firefly_flower():
    d = Doc()
    d.form(leaf_round(548, 812, 268, 168, deg=72), GRASS,
           sweep(676, 742, 96, 122, lo=.22, hi=-.38), GRASS_DEEP)
    d.line(vein(548, 812, 268, 72), OL_FINE)
    d.form(leaf_pointed(444, 892, 216, 118, deg=-68, curl=.14), GRASS_DEEP,
           sweep(342, 826, 68, 88, lo=.20, hi=-.36), GRASS_DARK, ol=OL_PROP)
    d.form(stem_slim(488, 560, BASE_Y, 68, root_seed=36.4, lean=-18,
                     w_base=180, root_lobes=3, root_depth=(16, 28)),
           GRASS, sweep(500, 790, 56, 220, lo=.06, hi=-.12, wob=.03),
           GRASS_DEEP)

    HX, HY = 472, 396
    PL = (262, 250, 268, 244, 258, 236)
    for i in range(6):
        dg = i * 60 + (3.2 if i % 2 else -2.6) + (i % 3) * 1.6
        d.form(leaf_round(HX, HY, PL[i], 216, dg, curl=.10 if i % 2 else -.09),
               BERRY, sweep(HX, HY - PL[i] * .38, 118, PL[i] * .44, lo=.26,
                            hi=-.40, seed=i * 2.9), BERRY_DEEP)
    J, B = lobe_profile(52.3, 12, jit=0.05, bul=(6, 15))
    d.form(canopy_blob(HX, HY + 4, 122, 114, 12, J, B, start=-92), SUN,
           sweep(HX, HY, 122, 114, lo=.28, hi=-.44, wob=.06), SUN_SHADE)
    d.add(face(472, 400, 132, mass_w=236, default="sleepy", tilt=2.0,
               eyes=((-46, -10), (48, -6)), eye_r=(20, 18), mouth=(2, 40),
               mouth_k=0.95, brow_lift=4))
    _firefly(d, 244, 246, 176, -12, 3.7, lit=True)
    # ODDITY: the second firefly's lamp has gone out
    _firefly(d, 826, 350, 166, 14, 8.1, lit=False)
    return d.svg()


# =====================================================================
# 15. f-firetruck-flower   WACKY -- a fire engine parked across a bloom
# =====================================================================
def firetruck_flower():
    d = Doc()
    d.form(leaf_round(588, 806, 262, 172, deg=74), GRASS,
           sweep(714, 738, 96, 120, lo=.22, hi=-.38), GRASS_DEEP)
    d.line(vein(588, 806, 262, 74), OL_FINE)
    d.form(stem_slim(506, 552, BASE_Y, 76, root_seed=44.2, lean=14,
                     w_base=194, root_lobes=3, root_depth=(18, 30)),
           GRASS, sweep(518, 790, 62, 226, lo=.06, hi=-.12, wob=.03),
           GRASS_DEEP)

    HX, HY = 500, 374
    PL = (312, 300, 320, 306, 298, 316, 304, 214, 308, 314)
    for i in range(10):
        dg = i * 36 + (2.8 if i % 2 else -3.4) + (i % 4) * 1.3
        d.form(leaf_round(HX, HY, PL[i], 178, dg, curl=.09 if i % 2 else -.08),
               SUN, sweep(HX, HY - PL[i] * .38, 94, PL[i] * .44, lo=.26,
                          hi=-.40, seed=i * 3.1), SUN_SHADE)
    J, B = lobe_profile(57.6, 12, jit=0.05, bul=(6, 14))
    d.form(canopy_blob(HX, HY + 4, 118, 110, 12, J, B, start=-92), SUN_DEEP,
           sweep(HX, HY, 118, 110, lo=.28, hi=-.44, wob=.06), RAY_SHADE)

    # ---- the fire engine, parked right across the bloom ----
    # ladder on the roof
    lad = [(288, 312), (668, 280)]
    for off in (-24, 24):
        d.form(slab((lad[0][0] + lad[1][0]) / 2,
                    (lad[0][1] + lad[1][1]) / 2 + off, 392, 20, 0.44, -4.8),
               STEEL, sweep_hard((lad[0][0] + lad[1][0]) / 2,
                                 (lad[0][1] + lad[1][1]) / 2 + off, 196, 10),
               STEEL_DEEP, ol=OL_FINE)
    for x in graduated(6, 318, 640):
        y = 312 + (280 - 312) * ((x - 288) / 380.0)
        d.form(slab(x, y, 19, 40, 0.44, -4.8), STEEL_DEEP, None, STEEL_DARK,
               ol=OL_FINE)
    # rear body
    d.form(hard_poly([(520, 332), (734, 332), (734, 476), (520, 476)], 24),
           FRUIT, sweep_hard(628, 404, 108, 74, lo=.22, hi=-.30), FRUIT_DEEP,
           ol=OL_MAIN)
    for sd in grille(628, 408, 148, 78, 4, gap=0.40):
        d.form(sd, FRUIT_DEEP, None, EMBER_DEEP, ol=OL_FINE)
    # cab
    d.form(hard_poly([(280, 326), (524, 326), (524, 480), (274, 480)], 26),
           FRUIT, sweep_hard(400, 404, 126, 78, lo=.22, hi=-.30), FRUIT_DEEP,
           ol=OL_MAIN)
    d.form(slab(398, 358, 202, 52, 0.24), SKY_HI,
           sweep_hard(398, 358, 101, 26, lo=.20, hi=-.30), SKY_DEEP,
           ol=OL_PROP)
    # beacon + two flat sparkles: wee-woo
    d.form(hard_poly([(356, 320), (436, 320), (426, 288), (368, 288)], 12),
           SUN, sweep_hard(376, 274, 44, 20), SUN_SHADE, ol=OL_FINE)
    for (sx, sy, r) in ((306, 276, 32), (478, 266, 26)):
        d.fill(star4(sx, sy, r, 18, 0.30), BEAM)
    # wheels
    for (wx, wy) in ((356, 482), (668, 482)):
        d.form(circ(wx, wy, 62, wx * .01, 12, .02), INK_SOFT,
               None, INK_SOFT, ol=OL_MAIN)
        d.form(circ(wx, wy, 30, wx * .02, 10, .04), STEEL,
               sweep(wx, wy, 30, 30, lo=.28, hi=-.44), STEEL_DEEP, ol=OL_FINE)
    d.add(face(398, 414, 130, mass_w=244, default="delighted", tilt=-1.0,
               eyes=((-54, -18), (52, -24)), eye_r=(22, 26), mouth=(0, 48),
               mouth_k=1.10))
    # ODDITY: the hose has slipped off the back and dangles in the dirt
    hs = bow(734, 432, 858, 806, -0.32, 7)
    d.form(ribbon(hs, [30] * 7, cap0="flat", cap1="round"), CREAM_DEEP,
           sweep(800, 620, 78, 190, lo=.14, hi=-.22, wob=.05), BARK_LITE,
           ol=OL_PROP)
    d.form(slab(858, 812, 40, 66, 0.34, 12), STEEL,
           sweep_hard(858, 812, 20, 33), STEEL_DEEP, ol=OL_FINE)
    return d.svg()


# =====================================================================
# 16. g-grape-vine   REALISTIC -- NO FACE
#     A forked goblet trunk with the bunch hanging in the crotch.
# =====================================================================
def grape_vine():
    d = Doc()
    d.form(trunk_chunky(496, 706, BASE_Y, 178, 322, root_seed=15.8, lean=-4,
                        root_lobes=3, root_depth=(20, 34), flare=1.28),
           BARK, sweep(516, 856, 148, 160, lo=.16, hi=-.16, wob=.06),
           BARK_DEEP,
           inner=('<path d="M424,772 C438,846 430,904 442,966" fill="none" '
                  'stroke="%s" stroke-width="%d" %s/>'
                  '<path d="M576,782 C566,850 578,908 570,962" fill="none" '
                  'stroke="%s" stroke-width="%d" %s/>'
                  % (INK, OL_MAIN, RJ, INK, OL_MAIN, RJ)))
    for (x0, y0, x1, y1, w0, w1, k) in ((450, 738, 214, 452, 130, 74, -0.24),
                                        (548, 732, 786, 424, 124, 70, 0.28),
                                        (486, 716, 452, 452, 104, 66, 0.10)):
        d.form(branch(x0, y0, x1, y1, w0, w1, k), BARK,
               sweep((x0 + x1) / 2, (y0 + y1) / 2, 120, 100, lo=.18,
                     hi=-.24, wob=.05), BARK_DEEP)
    # tendrils
    for (cx, cy, r0, sa, w) in ((178, 496, 92, 20, 34), (856, 462, 86, 160, 32)):
        cu = spiral(cx, cy, r0, 0.95, sa, 12, 0.74)
        d.form(ribbon(cu, [w - 14 * (i / 11.0) for i in range(12)],
                      cap0="flat", cap1="round"), GRASS_DEEP,
               sweep(cx, cy, r0, r0, lo=.24, hi=-.40), GRASS_DARK, ol=OL_FINE)
    # two lobed vine leaves
    for (lx, ly, L, dg, col, sh) in ((262, 364, 232, -20, GRASS, GRASS_DEEP),
                                     (782, 340, 216, 24, GRASS, GRASS_DEEP),
                                     (534, 276, 190, 6, GRASS_DEEP,
                                      GRASS_DARK)):
        d.form(leaf_lobed(lx, ly, L, dg), col,
               sweep(lx, ly, L * .8, L * .8, lo=.26, hi=-.40, seed=lx * .01),
               sh, ol=OL_PROP)
        for k in (-46, 0, 46):
            d.line(vein(lx, ly + L * .2, L * .78, dg + k, frac=0.80), OL_FINE)

    # ---- the bunch ----
    ROWS = ((5, 486, 134), (4, 588, 108), (4, 686, 84), (3, 776, 58),
            (2, 854, 34), (1, 912, 0))
    for (n, ry, half) in ROWS:
        for i in range(n):
            t = (i - (n - 1) / 2.0) / max((n - 1) / 2.0, 1)
            gx = 500 + t * half * 1.62 + 10
            ball(d, gx, ry - 14, 64, BERRY_DEEP, gx * .01 + ry * .001,
                 OL_FINE, ry=60, shade=BERRY_DEEP)
    for (n, ry, half) in ROWS:
        for i in range(n):
            t = (i - (n - 1) / 2.0) / max((n - 1) / 2.0, 1)
            gx = 494 + t * half * 2.0
            ball(d, gx, ry, 66, BERRY, gx * .013 + ry * .002, OL_PROP,
                 ry=63, deg=(i * 9) % 17 - 8, shade=BERRY_DEEP, gloss=0.32)
    # ODDITY: one grape has dropped off and lies in the dirt
    ball(d, 768, 944, 54, BERRY, 3.9, OL_PROP, ry=46, deg=14,
         shade=BERRY_DEEP, gloss=0.30)
    return d.svg()


# =====================================================================
# 17. g-giraffe-grass   SILLY -- face; a tall spotted neck in a grass tuft
# =====================================================================
def giraffe_grass():
    d = Doc()
    for (bx, tx, ty, hw, bend, col, sh) in (
            (330, 176, 604, 46, -60, GRASS_DEEP, GRASS_DARK),
            (694, 848, 636, 44, 58, GRASS_DEEP, GRASS_DARK),
            (392, 288, 690, 42, -40, GRASS, GRASS_DEEP),
            (648, 748, 712, 40, 38, GRASS, GRASS_DEEP),
            (452, 396, 748, 38, -22, GRASS, GRASS_DEEP),
            (588, 632, 766, 36, 20, GRASS, GRASS_DEEP)):
        d.form(leaf_blade(bx, 1000, tx, ty, hw, 16, bend), col,
               sweep((bx + tx) / 2, (1000 + ty) / 2, 90, 190, lo=.18,
                     hi=-.28, seed=bx * .01), sh, ol=OL_PROP)

    neck = smooth_closed(
        [(402, 972), (414, 838), (428, 690), (442, 540), (452, 402),
         (460, 306), (470, 264), (566, 258), (574, 306), (582, 402),
         (594, 540), (608, 690), (622, 838), (634, 972)]
        + list(reversed(root_pts(518, 116, BASE_Y, 29.7, lobes=3,
                                 depth=(18, 30)))))
    d.form(neck, SUN, sweep(518, 640, 120, 360, lo=.16, hi=-.20, wob=.04),
           SUN_SHADE)
    dot_spots(d, [(452, 906, 46, 1.1, 12), (576, 830, 42, 2.2, -8),
                  (462, 764, 44, 3.3, 20), (582, 690, 40, 4.4, -14),
                  (472, 626, 42, 5.5, 8), (568, 552, 38, 6.6, 24),
                  (486, 490, 38, 7.7, -6), (556, 420, 34, 8.8, 16),
                  (498, 358, 32, 9.9, -18)], BARK)
    # mane
    for i, my in enumerate(graduated(6, 300, 620)):
        d.form(leaf_pointed(462 - i * 2, my + 46, 74, 42, -22 - i * 3),
               BARK, sweep(462, my, 24, 32, lo=.24, hi=-.38), BARK_DEEP,
               ol=OL_FINE)

    # ---- the head ----
    for (ex, ey, L, Wd, dg) in ((424, 214, 116, 78, -74), (612, 200, 110, 74,
                                                           70)):
        d.form(leaf_round(ex, ey, L, Wd, dg), SUN,
               sweep(ex + (-40 if dg < 0 else 40), ey - 20, Wd * .5, L * .5,
                     lo=.24, hi=-.38), SUN_SHADE, ol=OL_PROP)
    for (hx, hy, dg) in ((468, 196, -12), (556, 188, 11)):
        d.form(horn(hx, hy, 92, 40, dg, k=0.10), BARK,
               sweep(hx, hy - 46, 22, 40, lo=.24, hi=-.38), BARK_DEEP,
               ol=OL_FINE)
        d.form(circ(hx + (dg // 2), hy - 92, 27, hx * .01, 9, .06, 24),
               BARK_DEEP, None, INK_SOFT, ol=OL_FINE)
    d.form(smooth_closed(place([(-104, -20), (-72, -78), (10, -92),
                                (92, -66), (114, -4), (96, 62), (16, 84),
                                (-74, 62), (-108, 26)], 512, 226, -5)),
           SUN, sweep(512, 226, 112, 88, lo=.26, hi=-.40, wob=.06),
           SUN_SHADE)
    d.form(smooth_closed(place([(-52, -26), (28, -34), (58, 4), (30, 44),
                                (-46, 38), (-64, 6)], 546, 268, -5)),
           BARK_LITE, sweep(546, 268, 60, 40, lo=.24, hi=-.38), BARK,
           ol=OL_PROP)
    d.add(face(508, 220, 110, mass_w=200, default="mischief", tilt=6.0,
               eyes=((-44, -26), (46, -20)), eye_r=(19, 27), mouth=(6, 50),
               mouth_k=0.90))
    # ODDITY: it is chewing a blade of grass
    d.form(leaf_blade(566, 288, 664, 214, 22, 12, 26), GRASS,
           sweep(614, 252, 46, 40, lo=.22, hi=-.38), GRASS_DEEP, ol=OL_FINE)
    return d.svg()


# =====================================================================
# 18. g-gumball-tree   "Gumball Goo Tree"   WACKY -- face on the trunk
#     A gooey canopy studded with gumballs, long stretchy drips hanging
#     off its underside, and one enormous bubble blown out the side.
# =====================================================================
def gumball_tree():
    d = Doc()
    d.form(trunk_chunky(498, 636, BASE_Y, 190, 320, root_seed=39.5, lean=-10,
                        root_lobes=3, root_depth=(18, 30), flare=1.16),
           BARK, sweep(516, 830, 150, 190, lo=.16, hi=-.16, wob=.06),
           BARK_DEEP,
           inner=('<path d="M420,730 C434,812 426,890 438,958" fill="none" '
                  'stroke="%s" stroke-width="%d" %s/>'
                  % (INK, OL_MAIN, RJ)))
    # ---- the goo drips, drawn BEHIND the canopy so they hang out of it --
    for (dx, dy, dl, w0, w1, k, r) in ((238, 502, 296, 60, 32, 0.10, 42),
                                       (668, 578, 138, 54, 30, 0.09, 38),
                                       (786, 496, 244, 52, 28, -0.10, 36)):
        sp = bow(dx, dy, dx + (18 if k > 0 else -16), dy + dl, k, 6)
        d.form(ribbon(sp, [w0 + (w1 - w0) * (i / 5.0) for i in range(6)],
                      cap0="flat", cap1="round"), LEAF,
               sweep(dx, dy + dl * .5, w0, dl * .5, lo=.20, hi=-.30,
                     seed=dx * .01), GRASS, ol=OL_PROP)
        ball(d, sp[-1][0], sp[-1][1] + r * .5, r, LEAF, dx * .01, OL_PROP,
             ry=r * 1.06, shade=GRASS, gloss=0.30)
    # ---- the bubble, blown out to the right ----
    d.form(ribbon(bow(748, 402, 800, 332, 0.10, 5), [70, 62, 56, 50, 46],
                  cap0="flat", cap1="flat"), LEAF,
           sweep(774, 366, 46, 42, lo=.22, hi=-.34), GRASS, ol=OL_PROP)
    d.form(circ(852, 236, 134, 6.4, 14, .022, 128), ACCENT,
           sweep(852, 236, 134, 128, lo=.30, hi=-.46), ACCENT_DEEP,
           inner='<path d="%s" fill="%s" opacity="0.75"/>'
                 % (chip(806, 188, 48, -30), CREAM))
    # ---- the gooey canopy ----
    clump(d, [(320, 452, 150, 142, GRASS, 9, -104, None, 2.4),
              (692, 424, 152, 144, GRASS, 9, -82, None, 4.8),
              (400, 274, 166, 146, LEAF, 10, -96, None, 7.2),
              (628, 288, 160, 142, LEAF, 10, -90, 4, 9.6),
              (508, 372, 206, 190, LEAF, 11, -97, None, 12.0)])
    marks(d, [(300, 410, 86, 48, -30, GRASS_DARK),
              (704, 386, 82, 46, 24, GRASS_DARK),
              (394, 222, 80, 46, -14, GRASS_DEEP),
              (628, 240, 78, 44, 28, GRASS_DEEP),
              (350, 528, 76, 44, -38, GRASS_DEEP),
              (652, 528, 74, 42, 18, GRASS_DARK)])
    # ---- the gumballs ----
    for (gx, gy, r, col, sh, sd) in ((316, 400, 74, FRUIT, FRUIT_DEEP, 1.5),
                                     (410, 232, 68, SUN, SUN_SHADE, 3.0),
                                     (562, 212, 64, SKY_HI, SKY_DEEP, 4.5),
                                     (676, 320, 72, BERRY, BERRY_DEEP, 6.0),
                                     (368, 520, 66, ACCENT, ACCENT_DEEP, 7.5),
                                     (528, 372, 78, CREAM, CREAM_DEEP, 9.0),
                                     (620, 508, 62, GRASS_DEEP, GRASS_DARK,
                                      10.5)):
        ball(d, gx, gy, r, col, sd, OL_PROP, shade=sh, gloss=0.34)
    # ODDITY: one gumball has escaped, still on a stretched string of goo
    st = bow(452, 566, 402, 796, 0.14, 6)
    d.form(ribbon(st, [30, 26, 22, 20, 19, 18], cap0="flat", cap1="flat"),
           LEAF, sweep(426, 680, 26, 116, lo=.20, hi=-.30), GRASS, ol=OL_FINE)
    ball(d, 396, 838, 62, FRUIT, 13.5, OL_PROP, shade=FRUIT_DEEP, gloss=0.34)
    d.add(face(490, 796, 150, mass_w=272, default="delighted", tilt=-3.0,
               eyes=((-56, -14), (50, -20)), eye_r=(21, 23), mouth=(-8, 42),
               mouth_k=1.25))
    return d.svg()


# =====================================================================
PLANTS = [
    ("a-ant-arch", ant_arch),
    ("a-airplane-tree", airplane_tree),
    ("b-burger-bush", burger_bush),
    ("c-carrot-plant", carrot_plant),
    ("c-caterpillar-vine", caterpillar_vine),
    ("c-cupcake-tree", cupcake_tree),
    ("d-daffodil", daffodil),
    ("d-duck-bloom", duck_bloom),
    ("d-donut-tree", donut_tree),
    ("e-eggplant", eggplant),
    ("e-elephant-ear", elephant_ear),
    ("e-escalator-plant", escalator_plant),
    ("f-fern", fern),
    ("f-firefly-flower", firefly_flower),
    ("f-firetruck-flower", firetruck_flower),
    ("g-grape-vine", grape_vine),
    ("g-giraffe-grass", giraffe_grass),
    ("g-gumball-tree", gumball_tree),
]

if __name__ == "__main__":
    want = sys.argv[1:]
    jobs = [(n, f) for n, f in PLANTS if not want or n in want]
    for name, fn in jobs:
        svg = fn()
        with open(os.path.join(OUT, name + ".svg"), "w") as fh:
            fh.write(svg.strip() + "\n")
        ok = render(name, svg, W, H, os.path.join(OUT, name + ".png"))
        print("%-20s %s" % (name, "OK" if ok else "FAIL"))
