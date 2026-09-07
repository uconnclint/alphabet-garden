#!/usr/bin/env python3
"""Build the six PILOT flat-vector plants (+ the kit reference sheet).

    python3 art/flat/plants/_build_plants.py            # all
    python3 art/flat/plants/_build_plants.py s-sunflower

Everything is authored from `_kit.py`.  The rasteriser is reused verbatim
from `../_build_flat.py` (2x headless-Chrome screenshot -> LANCZOS to 1x).
"""
import os
import sys
import math
import importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _kit import *                                            # noqa: F401,F403

# --- reuse the batch-2 rasteriser -------------------------------------
_spec = importlib.util.spec_from_file_location(
    "_build_flat", os.path.join(HERE, "..", "_build_flat.py"))
_bf = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_bf)
render = _bf.render                     # render(name, svg, w, h, out_png, 2)

OUT = HERE


# =====================================================================
# 1. s-sunflower   realistic, NO face
#    iconic double petal ring, seeded disc, two big leaves, chunky stem
# =====================================================================
def sunflower():
    d = Doc()
    HX, HY = 506, 424
    R_IN, R_FRONT, R_BACK = 112, 302, 264
    N = 13

    def petal(r_in, r_out, hw):
        p = [(0, -r_out), (hw * .52, -r_out * .88),
             (hw, -(r_in + (r_out - r_in) * .42)), (hw * .86, -r_in * 1.02),
             (0, -r_in * .90), (-hw * .82, -r_in * 1.04),
             (-hw, -(r_in + (r_out - r_in) * .45)), (-hw * .58, -r_out * .86)]
        return smooth_closed(p)

    LEN_JIT = [1.00, .95, 1.04, .97, 1.02, .93, 1.05, .78, 1.01, .96,
               1.03, .94, 1.00]          # index 7 = the deliberately stub petal
    ANG_JIT = [0, 2.2, -1.8, 1.4, -2.6, 1.9, -1.2, 4.8, -2.1, 1.6, -1.5,
               2.4, -0.9]

    front, back = [], []
    for i in range(N):
        a = -90 + 360.0 * i / N + ANG_JIT[i]
        hw = 58 * (0.94 + 0.10 * LEN_JIT[i])
        front.append(('<path d="%s" transform="translate(%d,%d) rotate(%.1f)"'
                      % (petal(R_IN, R_FRONT * LEN_JIT[i], hw), HX, HY,
                         a + 90)))
        ab = -90 + 360.0 * (i + .5) / N + ANG_JIT[(i + 4) % N] * .7
        back.append(('<path d="%s" transform="translate(%d,%d) rotate(%.1f)"'
                     % (petal(R_IN, R_BACK * LEN_JIT[(i + 6) % N], 54),
                        HX, HY, ab + 90)))

    # ---- leaves (behind the stem) ----
    LB = leaf_pointed(474, 880, 296, 182, deg=-63, curl=.18)
    LB += " " + bite(398, 702, 46)                       # ODDITY: nibbled leaf
    d.form(LB, GRASS, sweep(368, 786, 165, 132, lo=.20, hi=-.34),
           GRASS_DEEP, ol=OL_MAIN, evenodd=True)
    d.line("M470,868 C428,820 380,776 330,738", OL_MAIN)
    RB = leaf_pointed(544, 838, 272, 164, deg=57, curl=-.16)
    d.form(RB, GRASS, sweep(662, 748, 150, 122, lo=.18, hi=-.36), GRASS_DEEP)
    d.line("M552,828 C596,784 640,746 688,712", OL_MAIN)

    # ---- stem ----
    d.form(stem_slim(498, 596, BASE_Y, 62, lean=16, w_base=172),
           GRASS, sweep(510, 800, 90, 210, lo=.05, hi=-.10, wob=.03),
           GRASS_DEEP)

    # ---- petal rings ----
    cid = d._cid()
    d.defs.append('<clipPath id="%s">%s/></clipPath>'
                  % (cid, "/>".join(back)))
    d.add("".join('%s fill="%s"/>' % (p, SUN_SHADE) for p in back))
    d.add('<g clip-path="url(#%s)"><path d="%s" fill="%s"/></g>'
          % (cid, sweep(HX, HY, 300, 280, lo=.30, hi=-.40), "#d69526"))
    d.add("".join('%s fill="none" stroke="%s" stroke-width="%d" %s/>'
                  % (p, INK, OL_MAIN, RJ) for p in back))

    cid = d._cid()
    d.defs.append('<clipPath id="%s">%s/></clipPath>'
                  % (cid, "/>".join(front)))
    d.add("".join('%s fill="%s"/>' % (p, SUN) for p in front))
    d.add('<g clip-path="url(#%s)"><path d="%s" fill="%s"/></g>'
          % (cid, sweep(HX, HY, 300, 300, lo=.34, hi=-.42), SUN_SHADE))
    d.add("".join('%s fill="none" stroke="%s" stroke-width="%d" %s/>'
                  % (p, INK, OL_MAIN, RJ) for p in front))

    # ---- seed disc ----
    disc = canopy_blob(HX, HY + 2, 136, 128, n=11,
                       jit=(1.0, .99, 1.01, .995, 1.005, .99, 1.01, 1.0,
                            .995, 1.005, .99),
                       bul=(9, 7, 10, 6, 11, 8, 7, 10, 6, 9, 8))
    seeds = ""
    SEED_N = 19
    for i in range(SEED_N):
        t = i / float(SEED_N)
        rr = 22 + 96 * math.sqrt(t)
        aa = i * 2.399963                       # phyllotaxis
        sx = HX + rr * math.cos(aa) + 4 * math.sin(i * 2.1)
        sy = HY + 2 + rr * math.sin(aa) * .95
        sr = 16 - 4 * t + 2 * math.sin(i * 1.7)
        seeds += ('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" '
                  'fill="%s" transform="rotate(%d %.1f %.1f)"/>'
                  % (sx, sy, sr, sr * .82, INK_SOFT, (i * 37) % 60 - 30,
                     sx, sy))
    d.form(disc, SOIL, sweep(HX, HY, 136, 128, lo=.28, hi=-.46), SOIL_DEEP,
           inner=seeds)
    return d.svg()


# =====================================================================
# 2. a-apple-tree   realistic, NO face
# =====================================================================
def apple_tree():
    d = Doc()
    # ---- trunk (behind the canopy) ----
    d.form(trunk_chunky(508, 380, BASE_Y, 178, 334, lean=8),
           SOIL, sweep(524, 760, 168, 250, lo=.18, hi=-.14, wob=.06),
           SOIL_DEEP,
           inner=('<path d="M424,560 C440,660 430,760 448,900" fill="none" '
                  'stroke="%s" stroke-width="%d" %s/>'
                  '<path d="M604,600 C592,700 606,798 596,916" fill="none" '
                  'stroke="%s" stroke-width="%d" %s/>'
                  % (INK, OL_MAIN, RJ, INK, OL_MAIN, RJ)))

    # ---- canopy: 6 clumps, back to front, alternating the two greens ----
    CL = [(256, 428, 196, 156, GRASS, 9, -102, None),
          (794, 444, 202, 160, GRASS, 9, -84, None),
          (512, 246, 222, 164, LEAF, 10, -95, None),
          (704, 568, 206, 158, GRASS, 9, -110, 4),
          (318, 550, 214, 164, LEAF, 9, -88, None),
          (516, 430, 244, 188, LEAF, 11, -97, None)]
    for (cx, cy, rx, ry, col, n, st, notch) in CL:
        d.form(canopy_blob(cx, cy, rx, ry, n=n, start=st, notch=notch),
               col, sweep(cx, cy, rx, ry, lo=.28 + (cx % 7) * .012,
                          hi=-.40 - (cy % 5) * .012, wob=.09,
                          seed=cx * .01))

    # ---- leaf marks: flat pattern shapes, no black outline ----
    MARKS = [(198, 378, 92, 52, -28, GRASS_DARK), (330, 446, 84, 48, 14,
             GRASS_DEEP), (452, 196, 88, 50, -20, GRASS_DEEP),
             (622, 280, 80, 46, 30, GRASS_DEEP), (848, 404, 90, 52, -14,
             GRASS_DARK), (764, 534, 82, 48, 22, GRASS_DARK),
             (390, 614, 86, 50, -34, GRASS_DEEP), (598, 504, 78, 44, 8,
             GRASS_DEEP), (248, 534, 80, 46, 40, GRASS_DARK),
             (672, 656, 74, 42, -18, GRASS_DARK)]
    for (mx, my, L, Wd, dg, col) in MARKS:
        d.add('<path d="%s" fill="%s"/>' % (leaf_round(mx, my, L, Wd, dg),
                                            col))

    # ---- apples ----
    AP = [(254, 448, 80, -6, False), (498, 280, 86, 5, False),
          (708, 410, 76, 9, False), (348, 592, 82, -11, True),
          (716, 622, 70, 4, False)]
    for (ax, ay, r, dg, bitten) in AP:
        p = fruit_blob(ax, ay, r, dg)
        eo = False
        if bitten:                                   # ODDITY: a bitten apple
            p += " " + bite(ax + r * .96, ay - r * .10, r * .46)
            eo = True
        d.add('<path d="M%.0f,%.0f C%.0f,%.0f %.0f,%.0f %.0f,%.0f" '
              'fill="none" stroke="%s" stroke-width="%d" %s/>'
              % (ax + 2, ay - r * .62, ax + 6, ay - r * 1.02,
                 ax + 16, ay - r * 1.16, ax + 26, ay - r * 1.30,
                 SOIL_DEEP, OL_PROP, RJ))
        d.form(p, FRUIT, sweep(ax, ay, r, r, lo=.30, hi=-.46), FRUIT_DEEP,
               ol=OL_PROP, evenodd=eo,
               inner='<path d="%s" fill="%s" opacity="0.85"/>'
                     % (chip(ax - r * .40, ay - r * .40, r * .30), CREAM))
        d.add('<path d="%s" fill="%s"/>'
              % (leaf_round(ax + 24, ay - r * 1.24, 52, 34, 62), GRASS_DEEP))
    return d.svg()


# =====================================================================
# 3. m-maple-tree   realistic, NO face
# =====================================================================
def maple_tree():
    d = Doc()
    d.form(trunk_chunky(506, 430, BASE_Y, 150, 286, lean=-6),
           SOIL, sweep(516, 780, 145, 240, lo=.14, hi=-.18, wob=.05),
           SOIL_DEEP,
           inner=('<path d="M424,600 C440,700 430,800 448,900" fill="none" '
                  'stroke="%s" stroke-width="%d" %s/>'
                  '<path d="M590,640 C580,742 594,830 584,918" fill="none" '
                  'stroke="%s" stroke-width="%d" %s/>'
                  % (INK, OL_MAIN, RJ, INK, OL_MAIN, RJ)))
    # branch stubs reaching into the canopy (outline first, then fill over it)
    for bd, bw in (("M474,520 C452,470 408,438 358,418", 46),
                   ("M552,530 C580,478 630,450 682,436", 42)):
        d.add('<path d="%s" fill="none" stroke="%s" stroke-width="%d" %s/>'
              % (bd, INK, bw + 2 * OL_MAIN, RJ))
    for bd, bw in (("M474,520 C452,470 408,438 358,418", 46),
                   ("M552,530 C580,478 630,450 682,436", 42)):
        d.add('<path d="%s" fill="none" stroke="%s" stroke-width="%d" %s/>'
              % (bd, SOIL, bw, RJ))

    CL = [(248, 438, 190, 152, EMBER, 9, -100, None),
          (786, 452, 196, 156, EMBER, 9, -82, None),
          (508, 250, 226, 168, ACCENT, 10, -94, None),
          (692, 570, 200, 158, ACCENT, 9, -112, 3),
          (318, 552, 208, 162, SUN, 9, -86, None),
          (512, 438, 246, 192, ACCENT, 11, -98, None)]
    for (cx, cy, rx, ry, col, n, st, notch) in CL:
        d.form(canopy_blob(cx, cy, rx, ry, n=n, start=st, notch=notch),
               col, sweep(cx, cy, rx, ry, lo=.30, hi=-.42, seed=cx * .013))

    # ---- the maple leaves: the identity of this asset ----
    LV = [(232, 380, 84, 12, FRUIT), (424, 232, 90, -18, EMBER),
          (614, 258, 78, 26, SUN), (782, 384, 86, -8, FRUIT),
          (326, 498, 76, 34, SUN), (534, 384, 92, -6, FRUIT),
          (704, 498, 80, 16, SUN), (444, 568, 84, -26, EMBER),
          (858, 548, 72, 20, SUN), (192, 562, 74, -14, FRUIT),
          (628, 640, 78, 8, EMBER),
          (722, 932, 70, 152, FRUIT)]        # ODDITY: one leaf has fallen
    for (lx, ly, L, dg, col) in LV:
        # petiole: a short stem tick leaving the leaf base, hue-matched brown
        px = lx + L * .52 * math.sin(math.radians(dg))
        py = ly + L * .52 * math.cos(math.radians(dg))
        d.add('<path d="M%.0f,%.0f L%.0f,%.0f" fill="none" stroke="%s" '
              'stroke-width="%d" %s/>'
              % (lx, ly, px, py, SOIL_DEEP, OL_FINE + 2, RJ))
        d.form(leaf_lobed(lx, ly, L, dg), col,
               sweep(lx, ly, L, L, lo=.30, hi=-.44, wob=.10, seed=lx * .02),
               ol=OL_PROP)
    return d.svg()


# =====================================================================
# 4. b-butterfly-bush   silly, HAS a face + two butterflies
# =====================================================================
def _butterfly(d, cx, cy, span, low_col, deg=0.0, fold=1.0):
    """Wings STEEL up / accent low, fat ink body, ball-tipped antennae."""
    s = span / 260.0

    def P(pts):
        return place(pts, cx, cy, deg, s)
    # upper wings
    uw_l = smooth_closed(P([(-14, -18), (-64, -96), (-124, -84), (-134, -20),
                            (-96, 22), (-38, 16)]))
    uw_r = smooth_closed(P([(14, -20), (66, -100), (128, -86), (136, -22),
                            (98, 20), (40, 14)]))
    # lower wings (fold<1 folds the left one -> deliberate asymmetry)
    lw_l = smooth_closed(P([(-16, 14), (-70 * fold, 34), (-108 * fold, 84),
                            (-72 * fold, 116), (-24, 82)]))
    lw_r = smooth_closed(P([(16, 12), (74, 32), (114, 82), (76, 118),
                            (26, 84)]))
    olw = ol_for(span * .34)
    for pth, col, sh, sd in ((uw_l, STEEL, STEEL_DEEP, 1.0),
                             (uw_r, STEEL, STEEL_DEEP, 2.0),
                             (lw_l, low_col, SHADE[low_col], 3.0),
                             (lw_r, low_col, SHADE[low_col], 4.0)):
        d.form(pth, col, sweep(cx, cy, span * .30, span * .30,
                               lo=.34, hi=-.40, seed=sd), sh, ol=olw)
    # wing spots
    for (px, py, pr) in ((-88, -44, 17), (-52, -14, 12), (92, -48, 16),
                         (58, -16, 11)):
        q = P([(px, py)])[0]
        d.add('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s"/>'
              % (q[0], q[1], pr * s, CREAM))
    # body
    body = smooth_closed(P([(0, -86), (17, -50), (20, 6), (14, 66),
                            (0, 100), (-14, 66), (-20, 6), (-17, -50)]))
    d.form(body, INK_SOFT, None, None, ol=olw)
    # head + antennae
    hq = P([(0, -96)])[0]
    for (ax, ay, bx, by, tx, ty) in ((-6, -100, -34, -140, -46, -158),
                                     (6, -100, 30, -142, 44, -158)):
        a, b, t = P([(ax, ay)])[0], P([(bx, by)])[0], P([(tx, ty)])[0]
        d.add('<path d="M%.1f,%.1f Q%.1f,%.1f %.1f,%.1f" fill="none" '
              'stroke="%s" stroke-width="%.1f" %s/>'
              % (a[0], a[1], b[0], b[1], t[0], t[1], INK_SOFT, 11 * s, RJ))
        d.add('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s"/>'
              % (t[0], t[1], 13 * s, INK_SOFT))
    d.add('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s"/>'
          % (hq[0], hq[1], 26 * s, INK_SOFT))


def butterfly_bush():
    d = Doc()
    # ---- stem + its two little leaves ----
    d.form(leaf_pointed(474, 900, 176, 104, deg=-72, curl=.2), GRASS,
           sweep(400, 852, 92, 74, lo=.24, hi=-.30), GRASS_DEEP, ol=OL_PROP)
    d.form(leaf_pointed(536, 872, 164, 96, deg=68, curl=-.2), GRASS,
           sweep(614, 826, 88, 70, lo=.20, hi=-.34), GRASS_DEEP, ol=OL_PROP)
    d.form(stem_slim(504, 640, BASE_Y, 60, lean=-12, w_base=150),
           GRASS, sweep(514, 840, 92, 190, lo=.06, hi=-.10, wob=.03),
           GRASS_DEEP)

    # ---- bush: 3 back clumps + 1 big front clump that wears the face ----
    for (cx, cy, rx, ry, col, n, st, notch) in (
            (252, 462, 202, 162, GRASS, 10, -104, None),
            (788, 476, 206, 164, GRASS, 10, -80, None),
            (520, 316, 230, 172, GRASS, 11, -96, 5)):
        d.form(canopy_blob(cx, cy, rx, ry, n=n, start=st, notch=notch),
               col, sweep(cx, cy, rx, ry, lo=.32, hi=-.44, wob=.09,
                          seed=cx * .011))
    # front clump wears the face; internal contour lines do the form work
    seams = "".join(
        '<path d="%s" fill="none" stroke="%s" stroke-width="%d" %s/>' % (
            sd, INK, OL_MAIN, RJ)
        for sd in ("M268,470 C330,506 344,588 300,660",
                   "M736,486 C688,530 692,600 738,644",
                   "M382,706 C428,678 448,632 442,584",
                   "M636,712 C592,684 574,640 582,594"))
    d.form(canopy_blob(500, 508, 274, 232, n=13, start=-94), LEAF,
           sweep(500, 508, 274, 232, lo=.32, hi=-.44, wob=.09, seed=5.1),
           inner=seams)

    # ---- leaf marks; one of them is nibbled: THE ODDITY ----
    for (mx, my, L, Wd, dg, col, nib) in (
            (206, 400, 96, 56, -30, GRASS_DEEP, False),
            (330, 372, 88, 50, 18, GRASS_DEEP, False),
            (470, 214, 92, 54, -12, GRASS_DEEP, False),
            (664, 268, 84, 48, 28, GRASS_DEEP, False),
            (860, 452, 90, 52, -20, GRASS_DEEP, False),
            (762, 618, 86, 50, 34, GRASS_DEEP, True),
            (268, 618, 88, 52, -36, GRASS_DEEP, False),
            (600, 664, 78, 46, 10, GRASS_DEEP, False)):
        p = leaf_round(mx, my, L, Wd, dg)
        if nib:
            p += " " + bite(mx + 34, my - L * .70, 22)
        d.add('<path d="%s" fill="%s"%s/>'
              % (p, col, ' fill-rule="evenodd"' if nib else ""))

    # ---- the face ----
    d.add(face(492, 520, 216, default="happy", tilt=-2.0))

    # ---- butterflies ----
    _butterfly(d, 232, 246, 268, SUN, deg=-14, fold=0.78)
    _butterfly(d, 818, 330, 252, SKY_HI, deg=16)
    return d.svg()


# =====================================================================
# 5. p-pizza-palm   wacky, HAS a face; grows pizza slices
# =====================================================================
def pizza_palm():
    d = Doc()
    HX, HY = 512, 424
    R0, R1, R2 = 96, 306, 372
    ANG = [-86, -44, -2, 41, 83]
    HA = [17.0, 18.0, 16.5, 17.5, 16.0]      # < half the 43 deg pitch -> gaps
    LENK = [0.94, 1.02, 1.00, 0.97, 0.92]

    def polar(r, deg):
        a = math.radians(deg)
        return (HX + r * math.sin(a), HY - r * math.cos(a))

    # ---- trunk first, behind the slices ----
    rings = trunk_palm(512, 406, BASE_Y, 72, 170, n=7)
    for i, (pth, hw, cy) in enumerate(rings):
        d.form(pth, BARK_LITE,
               sweep(512, cy, hw, hw * .40, lo=.26, hi=-.40, seed=i * 1.7),
               SOIL, ol=OL_MAIN)

    # ---- five slices ----
    for i, base_a in enumerate(ANG):
        ha, k = HA[i], LENK[i]
        r1, r2 = R1 * k, R2 * k
        arc = lambda r, f: [polar(r, base_a + ha * (2 * t / 4.0 - 1) * f)
                            for t in range(5)]
        # crust band
        crust = smooth_closed(
            arc(r1 - 6, 1.0) + [polar(r2 * 1.0, base_a + ha * 1.02)]
            + list(reversed(arc(r2, 1.03)))
            + [polar(r2 * 0.99, base_a - ha * 1.02)])
        eo = (i == 4)          # ODDITY: someone has taken a bite out of one
        bx, by = polar(r2 * 1.00, base_a + ha * .30)
        if eo:
            crust += " " + bite(bx, by, 66)
        d.form(crust, ACCENT,
               sweep(HX, HY, 300, 300, lo=.30, hi=-.44), ACCENT_DEEP,
               ol=OL_MAIN, evenodd=eo)
        # cheese wedge
        cheese = smooth_closed(
            [polar(R0 * .92, base_a - ha * .80),
             polar(R0 + (r1 - R0) * .45, base_a - ha * .96)]
            + arc(r1 + 6, 0.99)
            + [polar(R0 + (r1 - R0) * .45, base_a + ha * .96),
               polar(R0 * .92, base_a + ha * .80)])
        if eo:
            cheese += " " + bite(bx, by, 66)
        d.form(cheese, SUN, sweep(HX, HY, 300, 300, lo=.32, hi=-.46),
               SUN_SHADE, ol=OL_MAIN, evenodd=eo)
        # pepperoni
        for j, (rr, off, pr) in enumerate(((0.44, -0.42, 33), (0.62, 0.40, 30),
                                           (0.82, -0.14, 34))):
            px, py = polar(R0 + (r1 - R0) * rr, base_a + ha * off)
            if i == 1 and j == 2:            # ODDITY: one crooked pepperoni
                px, py = polar(r1 * 1.02, base_a + ha * .58)
            d.form(canopy_blob(px, py, pr, pr * .94, n=8,
                               jit=(1, .98, 1.02, .99, 1.01, .98, 1.02, 1),
                               bul=(3, 2, 4, 2, 3, 2, 4, 3)),
                   FRUIT, sweep(px, py, pr, pr, lo=.28, hi=-.48),
                   FRUIT_DEEP, ol=OL_FINE + 2)

    # ---- the face hub ----
    hub = canopy_blob(HX, HY - 4, 104, 100, n=10,
                      jit=(1, .99, 1.01, .995, 1.005, .99, 1.01, 1, .995,
                           1.005),
                      bul=(6, 4, 7, 5, 6, 4, 7, 5, 6, 4))
    d.form(hub, SUN, sweep(HX, HY, 104, 100, lo=.34, hi=-.46), SUN_SHADE,
           ol=OL_MAIN)
    d.add(face(HX - 4, HY - 2, 168, default="delighted", tilt=-3.0))
    return d.svg()


# =====================================================================
# 6. u-ufo-tree   wacky, HAS a face; saucers + tractor beam
# =====================================================================
def _saucer(d, cx, cy, rx, ry, dome_k=1.5, flip=False, alien=False, deg=0.0):
    """Flying saucer: STEEL hull, SKY dome, rim lights, optional alien."""
    f = -1 if flip else 1
    kx, ky = rx / 215.0, (ry / 54.0) * f
    ol = OL_PROP if rx < 160 else OL_MAIN
    hull = smooth_closed(place(
        [(-215, -6), (-150, -44), (-56, -56), (44, -54), (140, -42),
         (212, -4), (196, 34), (96, 56), (-10, 60), (-118, 52), (-196, 30)],
        cx, cy, deg, kx, ky))
    dm = smooth_closed(place(
        [(-98, 6), (-86, -50), (-40, -90), (16, -98), (74, -78), (98, -32),
         (102, 8)], cx, cy, deg, kx, ky * dome_k))
    d.form(dm, SKY_HI, sweep(cx, cy - 52 * ky * dome_k, rx * .48, rx * .44,
                             lo=.28, hi=-.48), SKY_DEEP, ol=ol)
    if alien:
        ay = cy - 96 * ky * dome_k * 0.50
        ar = rx * 0.30
        for sx in (-1, 1):                      # antenna nubs, drawn behind
            d.add('<path d="M%.0f,%.0f L%.0f,%.0f" stroke="%s" '
                  'stroke-width="%.0f" fill="none" %s/>'
                  '<circle cx="%.0f" cy="%.0f" r="%.0f" fill="%s" '
                  'stroke="%s" stroke-width="%d" %s/>'
                  % (cx + sx * ar * .42, ay - ar * .60,
                     cx + sx * ar * .64, ay - ar * 1.16, INK, ar * .30, RJ,
                     cx + sx * ar * .64, ay - ar * 1.18, ar * .20, GRASS,
                     INK, OL_FINE, RJ))
        ah = canopy_blob(cx - 5, ay, ar, ar * .90, n=9,
                         jit=(1, .97, 1.03, .98, 1.02, .96, 1.04, .99, 1.01),
                         bul=(5, 3, 6, 4, 5, 3, 6, 4, 5))
        d.form(ah, LEAF, sweep(cx, ay, ar, ar, lo=.28, hi=-.48), GRASS,
               ol=OL_PROP)
        e = ar * 0.44
        d.add('<ellipse cx="%.0f" cy="%.0f" rx="%.0f" ry="%.0f" fill="%s" '
              'transform="rotate(-8 %.0f %.0f)"/>'
              '<ellipse cx="%.0f" cy="%.0f" rx="%.0f" ry="%.0f" fill="%s" '
              'transform="rotate(7 %.0f %.0f)"/>'
              '<path d="M%.0f,%.0f Q%.0f,%.0f %.0f,%.0f" fill="none" '
              'stroke="%s" stroke-width="%.0f" %s/>'
              % (cx - e, ay - 4, ar * .23, ar * .29, INK_SOFT, cx - e, ay - 4,
                 cx + e * .90, ay - 8, ar * .21, ar * .27, INK_SOFT,
                 cx + e * .90, ay - 8,
                 cx - ar * .34, ay + ar * .40, cx - 2, ay + ar * .68,
                 cx + ar * .36, ay + ar * .36, INK_SOFT, ar * .17, RJ))
    d.form(hull, STEEL, sweep(cx, cy, rx, ry * 1.4, lo=.22, hi=-.40),
           STEEL_DEEP, ol=ol)
    lights = (SUN, ACCENT, LEAF, SUN, ACCENT)
    n = 5 if rx > 160 else 3
    for i in range(n):
        t = (i + .5) / n
        lx = cx - rx * .72 + rx * 1.44 * t
        ly = cy + (ry * .58) * f + (4 if i % 2 else -3)
        lr = rx * .085
        d.form(canopy_blob(lx, ly, lr, lr * .95, n=7,
                           jit=(1, .99, 1.01, 1, .99, 1.01, 1),
                           bul=(2, 1, 2, 1, 2, 1, 2)),
               lights[i % 5], None, None, ol=OL_FINE)


def ufo_tree():
    d = Doc()
    # ---- tractor beam, behind everything ----
    beam = smooth_closed([(464, 262), (564, 262), (726, 536), (316, 536)])
    d.form(beam, BEAM, sweep(516, 404, 204, 150, lo=.06, hi=-.36), SUN,
           ol=OL_BG, stroke=SUN_DEEP)
    # the leaf it is lifting
    d.form(leaf_round(448, 366, 126, 88, deg=38), GRASS,
           sweep(458, 320, 62, 56, lo=.24, hi=-.42), GRASS_DEEP, ol=OL_PROP)
    d.line(vein(448, 366, 126, 38), OL_FINE)

    # ---- trunk ----
    d.form(trunk_chunky(504, 680, BASE_Y, 156, 306, lean=6),
           SOIL, sweep(518, 860, 150, 170, lo=.18, hi=-.14, wob=.06),
           SOIL_DEEP,
           inner=('<path d="M424,740 C440,812 430,872 448,940" fill="none" '
                  'stroke="%s" stroke-width="%d" %s/>'
                  '<path d="M598,762 C588,830 602,882 592,944" fill="none" '
                  'stroke="%s" stroke-width="%d" %s/>'
                  % (INK, OL_MAIN, RJ, INK, OL_MAIN, RJ)))

    # ---- canopy ----
    for (cx, cy, rx, ry, col, n, st, notch) in (
            (276, 634, 184, 140, GRASS, 9, -102, None),
            (746, 624, 180, 138, GRASS, 9, -84, 3),
            (508, 582, 204, 138, LEAF, 10, -96, None),
            (496, 668, 248, 156, LEAF, 12, -92, None)):
        d.form(canopy_blob(cx, cy, rx, ry, n=n, start=st, notch=notch),
               col, sweep(cx, cy, rx, ry, lo=.30, hi=-.44, wob=.09,
                          seed=cx * .012))
    for (mx, my, L, Wd, dg) in ((224, 580, 88, 50, -28), (696, 554, 82, 48,
                                24), (818, 660, 80, 46, -16),
                                (306, 748, 84, 48, 32), (626, 778, 74, 44,
                                -10)):
        d.add('<path d="%s" fill="%s"/>' % (leaf_round(mx, my, L, Wd, dg),
                                            GRASS_DEEP))

    # ---- the tree's face: it has noticed ----
    d.add(face(470, 678, 208, default="surprised", tilt=-2.0))

    # ---- saucers ----
    _saucer(d, 514, 208, 198, 52, dome_k=1.56, alien=True)
    _saucer(d, 146, 800, 126, 38, dome_k=1.42, deg=-9)
    _saucer(d, 892, 736, 116, 35, dome_k=1.42, flip=True, deg=7)  # ODDITY

    # ---- sparkle stars ----
    for (sx, sy, sr, sd) in ((122, 420, 42, 8), (902, 430, 36, -12),
                             (62, 618, 32, 20), (958, 880, 38, -6),
                             (272, 176, 36, 14), (760, 214, 30, -18)):
        d.form(star4(sx, sy, sr, sd), SUN, None, None, ol=OL_FINE)
    return d.svg()


# =====================================================================
# KIT REFERENCE SHEET
# =====================================================================
def kit_sheet():
    d = Doc(1820, 1300)
    d.add('<rect x="0" y="0" width="1820" height="1300" fill="%s"/>' % CREAM)
    F = "Verdana,DejaVu Sans,sans-serif"

    def T(x, y, sz, txt, col=INK_SOFT, w="bold"):
        d.add('<text x="%d" y="%d" font-family="%s" font-size="%d" '
              'font-weight="%s" fill="%s">%s</text>'
              % (x, y, F, sz, w, col, txt))

    T(44, 66, 42, "ALPHABET GARDEN &#8212; PLANT KIT")
    T(44, 102, 21, "1024x1024 &#183; stem base y=1000 &#183; object height "
                   "~880 (86% of frame) &#183; light from UPPER-LEFT on every "
                   "plant", INK_SOFT, "normal")
    T(44, 130, 21, "outlines 13px main / 10px prop / 7px fine &#183; round "
                   "joins + caps everywhere &#183; two-tone hard-edged, "
                   "never a gradient", INK_SOFT, "normal")

    # ---------------- leaves ----------------
    T(44, 198, 26, "LEAF VOCABULARY")
    lv = [("round", leaf_round(120, 430, 180, 116, -6), GRASS, 120, 348),
          ("pointed", leaf_pointed(316, 436, 196, 104, 4), GRASS, 316, 350),
          ("lobed / maple", leaf_lobed(500, 350, 98, -8), EMBER, 500, 350),
          ("frond", leaf_frond(676, 434, 190, 116, -4), GRASS, 690, 350),
          ("blade", leaf_blade(866, 436, 902, 250, 30, 18, 40), GRASS,
           884, 350)]
    for nm, pth, col, sx, sy in lv:
        d.form(pth, col, sweep(sx, sy, 96, 96, lo=.30, hi=-.44), ol=OL_PROP)
    for i, x in enumerate((72, 264, 428, 634, 838)):
        T(x, 486, 20, lv[i][0])

    # ---------------- trunks ----------------
    T(44, 566, 26, "TRUNK / STEM  +  THE GROUND ANCHOR")
    d.form(stem_slim(140, 616, 946, 58, lean=14, w_base=160), GRASS,
           sweep(150, 800, 84, 180, lo=.06, hi=-.10), GRASS_DEEP)
    T(60, 992, 20, "slim stem")
    d.form(trunk_chunky(400, 616, 946, 150, 292), SOIL,
           sweep(412, 806, 140, 180, lo=.18, hi=-.14), SOIL_DEEP)
    T(320, 992, 20, "chunky trunk")
    for i, (pth, hw, cy) in enumerate(trunk_palm(700, 616, 946, 62, 140, n=6)):
        d.form(pth, BARK_LITE, sweep(700, cy, hw, hw * .4, lo=.26, hi=-.40,
                                     seed=i * 1.7), SOIL)
    T(612, 992, 20, "segmented palm")
    d.add('<path d="M60,946 L900,946" stroke="%s" stroke-width="6" '
          'stroke-dasharray="20 16" fill="none"/>' % ACCENT)
    T(60, 1044, 19, "y = 1000. Every trunk splays into 3 unequal, shallow "
                    "root lobes;", ACCENT_DEEP, "normal")
    T(60, 1072, 19, "notches stay 15-30px deep &#8212; deeper reads as claws "
                    "at game size.", ACCENT_DEEP, "normal")

    # ---------------- two-tone ----------------
    T(1000, 198, 26, "TWO-TONE RECIPE  (base / shadow)")
    T(1000, 228, 18, "shadow = base hue, ~10 deg cooler, S +0.05, "
                     "V -0.09..-0.14, hard edge", INK_SOFT, "normal")
    pairs = [("grass", GRASS, GRASS_DEEP), ("leaf", LEAF, GRASS),
             ("soil", SOIL, SOIL_DEEP), ("bark-lite", BARK_LITE, SOIL),
             ("sun", SUN, SUN_SHADE), ("accent", ACCENT, ACCENT_DEEP),
             ("fruit", FRUIT, FRUIT_DEEP), ("ember", EMBER, EMBER_DEEP),
             ("steel", STEEL, STEEL_DEEP), ("sky-hi", SKY_HI, SKY_DEEP),
             ("cream", CREAM, CREAM_DEEP), ("berry", BERRY, "#a94bb3")]
    for i, (nm, b, s) in enumerate(pairs):
        px = 1010 + (i % 3) * 272
        py = 288 + (i // 3) * 116
        d.form(canopy_blob(px, py, 42, 38, n=9,
                           jit=(1, .98, 1.02, .99, 1.01, .98, 1.02, .99, 1),
                           bul=(6, 4, 7, 5, 6, 4, 7, 5, 6)),
               b, sweep(px, py, 42, 38, lo=.30, hi=-.44), s, ol=OL_PROP)
        T(px + 62, py - 4, 19, nm)
        T(px + 62, py + 22, 15, b + " / " + s, INK_SOFT, "normal")

    # ---------------- faces ----------------
    T(1000, 792, 26, "FACE SYSTEM &#8212; 6 SWAPPABLE STATES")
    T(1000, 822, 18, "silly + wacky only. state = eyes(1) + mouth(1) "
                     "[+ brows(1)]. Blush always on.", INK_SOFT, "normal")
    for i, ex in enumerate(EXPRESSIONS):
        px = 1074 + (i % 3) * 254
        py = 924 + (i // 3) * 200
        d.form(canopy_blob(px, py, 92, 86, n=10,
                           jit=(1, .99, 1.01, 1, .99, 1.01, 1, .99, 1.01, 1),
                           bul=(8, 5, 9, 6, 8, 5, 9, 6, 8, 5)),
               LEAF, sweep(px, py, 92, 86, lo=.34, hi=-.46), GRASS)
        d.add(face(px, py, 152, default=ex))
        T(px - 66, py + 126, 19, "face-" + ex)
    return d.svg()




# =====================================================================
PLANTS = [
    ("s-sunflower", sunflower),
    ("a-apple-tree", apple_tree),
    ("m-maple-tree", maple_tree),
    ("b-butterfly-bush", butterfly_bush),
    ("p-pizza-palm", pizza_palm),
    ("u-ufo-tree", ufo_tree),
]

if __name__ == "__main__":
    want = sys.argv[1:]
    jobs = [(n, f) for n, f in PLANTS if not want or n in want]
    if not want or "_kit" in want:
        svg = kit_sheet()
        with open(os.path.join(OUT, "_kit.svg"), "w") as fh:
            fh.write(svg.strip() + "\n")
        ok = render("_kit", svg, 1820, 1300, os.path.join(OUT, "_kit.png"))
        print("%-18s %s" % ("_kit", "OK" if ok else "FAIL"))
    for name, fn in jobs:
        svg = fn()
        with open(os.path.join(OUT, name + ".svg"), "w") as fh:
            fh.write(svg.strip() + "\n")
        png = os.path.join(OUT, name + ".png")
        ok = render(name, svg, W, H, png)
        print("%-18s %s" % (name, "OK" if ok else "FAIL"))
