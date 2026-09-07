#!/usr/bin/env python3
"""Build wave-2 flat-vector plants: the H-O block (23 assets).

    python3 art/flat/plants/_build_w2.py             # all 23
    python3 art/flat/plants/_build_w2.py o-owl-orchid

Authored entirely from `_kit.py`.  This file is deliberately SEPARATE from
`_build_plants.py` (which two other authors are editing concurrently for the
A-G and P-Z blocks); the rasteriser is imported from it, nothing is edited
there.

House rules this file obeys, from KIT.md:
  * palette tokens only, never a literal hex
  * OL_MAIN/OL_PROP/OL_FINE only, round joins + caps (Doc.form does it)
  * two-tone via Doc.form + sweep/sweep_hard, light from the UPPER-LEFT
  * realistic plants get NO face; silly + wacky ones do, and every one of
    them moves `eyes` / `eye_r` / `mouth` / `mouth_k` / `brow_lift` so the
    fourteen faces in this block are fourteen different faces
  * one deliberate oddity per plant, called out in a comment
"""
import os
import sys
import math

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _kit import *                                        # noqa: F401,F403
from _build_plants import render                          # noqa: E402

OUT = HERE


# =====================================================================
# LOCAL SHAPE HELPERS  (built out of the kit's primitives, never around it)
# =====================================================================
def squiggle(x0, y0, x1, y1, w, amp, waves=2.4, phase=0.0, n=11,
             cap0="round", cap1="round", taper=1.0):
    """A wavy ribbon from A to B -- noodles, kelp fronds, ketchup squirts."""
    dx, dy = x1 - x0, y1 - y0
    L = math.hypot(dx, dy) or 1.0
    nx, ny = -dy / L, dx / L
    sp, ws = [], []
    for i in range(n):
        t = i / float(n - 1)
        s = math.sin(t * math.pi * waves + phase) * amp
        sp.append((x0 + dx * t + nx * s, y0 + dy * t + ny * s))
        ws.append(w * (1.0 + (taper - 1.0) * t))
    return ribbon(sp, ws, cap0=cap0, cap1=cap1)


def coil(cx, cy, r0, r1, turns, w, start=0.0, n=44, cw=1.0):
    """A spiral ribbon -- lollipop swirl, a knotted tentacle."""
    sp, ws = [], []
    for i in range(n):
        t = i / float(n - 1)
        a = math.radians(start) + cw * turns * 2.0 * math.pi * t
        r = r0 + (r1 - r0) * t
        sp.append((cx + r * math.cos(a), cy + r * math.sin(a)))
        ws.append(w)
    return ribbon(sp, ws, cap0="round", cap1="round")


def elbow(pts, w, r):
    """An L-shaped limb with square-cut ends and rounded corners."""
    n = len(pts)
    left, right = [], []
    for i in range(n):
        a = pts[max(i - 1, 0)]
        b = pts[min(i + 1, n - 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy) or 1.0
        nx, ny = -dy / L, dx / L
        left.append((pts[i][0] + nx * w * .5, pts[i][1] + ny * w * .5))
        right.append((pts[i][0] - nx * w * .5, pts[i][1] - ny * w * .5))
    return hard_poly(left + list(reversed(right)), r)


def petal_fan(cx, cy, base_a, r_in, r_out, half, seed, ruffle=0.05, stub=1.0):
    """A broad fan petal: hibiscus, marigold, orchid.  Ruffled outer edge."""
    ks = jitter(seed, 5, ruffle, 1.0)
    pts = []
    for i in range(3):                                   # inner edge, L->R
        a = math.radians(base_a - half * .58 + half * 1.16 * i / 2.0)
        pts.append((cx + r_in * math.sin(a), cy - r_in * math.cos(a)))
    a = math.radians(base_a + half * .94)                # right shoulder
    pts.append((cx + r_out * .74 * math.sin(a), cy - r_out * .74 * math.cos(a)))
    for i in range(5):                                   # outer edge, R->L
        t = i / 4.0
        a = math.radians(base_a + half * (1.0 - 2.0 * t))
        rr = r_out * ks[i] * stub
        pts.append((cx + rr * math.sin(a), cy - rr * math.cos(a)))
    a = math.radians(base_a - half * .94)                # left shoulder
    pts.append((cx + r_out * .72 * math.sin(a), cy - r_out * .72 * math.cos(a)))
    return smooth_closed(pts)


def stroked(paths, col=INK, ol=OL_MAIN):
    """Contour lines packaged for Doc.form's `inner=`."""
    if isinstance(paths, str):
        paths = [paths]
    return "".join('<path d="%s" fill="none" stroke="%s" stroke-width="%d" '
                   '%s/>' % (p, col, ol, RJ) for p in paths)


def dots(spots, col):
    """Flat unoutlined round pattern marks."""
    return "".join('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s"/>'
                   % (x, y, r, col) for (x, y, r) in spots)


def cylinder(d, cx, cy, w, h, col, seed, deg=0.0, ol=OL_MAIN):
    """A soft cylinder seen side-on -- a marshmallow.  Rounded, not a slab."""
    body = slab(cx, cy, w, h, r=0.30, deg=deg)
    lip = slab(cx, cy - h * .30, w * .94, h * .40, r=0.44, deg=deg)
    d.form(body, col, sweep_hard(cx, cy, w * .5, h * .5, lo=.30, hi=-.30),
           SHADE[col], ol=ol, inner=stroked(lip, INK, OL_FINE))
    return d


# =====================================================================
# 1. h-hibiscus     REALISTIC -- no face
#    Five fat ruffled petals wide open and tilted off-axis, with the long
#    staminal column shooting out past them to the upper right.  That
#    protruding column is what keeps it off the sunflower's silhouette.
# =====================================================================
def hibiscus():
    d = Doc()
    HX, HY = 472, 398

    # ---- leaves, behind everything ----
    for (lx, ly, L, Wd, dg, sd) in ((452, 856, 322, 208, -66, 3.2),
                                    (566, 786, 300, 196, 62, 8.7),
                                    (602, 906, 232, 148, 86, 14.1)):
        d.form(leaf_pointed(lx, ly, L, Wd, dg, curl=.16), GRASS,
               sweep(lx + (70 if dg > 0 else -70), ly - L * .46, Wd * .8,
                     L * .34, lo=.22, hi=-.36, seed=sd), GRASS_DEEP)
        d.line(vein(lx, ly, L, dg), OL_FINE)

    # ---- stem ----
    d.form(stem_slim(494, 486, BASE_Y, 62, root_seed=201.3, lean=20,
                     w_base=178, root_lobes=3, root_depth=(18, 30)),
           GRASS, sweep(506, 786, 88, 232, lo=.06, hi=-.10, wob=.03),
           GRASS_DEEP)

    # ---- five petals.  index 2 is the ODDITY: a stubby, nibbled petal ----
    for i in range(5):
        a = -104 + 72.0 * i + (4.5 if i == 3 else -2.0 * (i % 2))
        stub = 0.80 if i == 2 else 1.0
        p = petal_fan(HX, HY, a, 104, 324, 43, seed=i * 6.4 + 2.0,
                      ruffle=.07, stub=stub)
        d.form(p, FRUIT, sweep(HX, HY, 330, 330, lo=.42, hi=-.62, wob=.08,
                               seed=i * 1.7), FRUIT_DEEP, ol=OL_MAIN)

    # ---- throat + staminal column, out past the petals to the upper right -
    J, B = lobe_profile(seed=88.6, n=10, jit=0.05, bul=(6, 12))
    d.form(canopy_blob(HX + 4, HY + 4, 106, 100, 10, J, B), SUN,
           sweep(HX, HY, 106, 100, lo=.30, hi=-.46), SUN_SHADE,
           inner=stroked(["M%d,%d L%d,%d" % (HX + 4 + 40 * math.sin(t),
                                             HY + 4 - 40 * math.cos(t),
                                             HX + 4 + 88 * math.sin(t),
                                             HY + 4 - 88 * math.cos(t))
                          for t in (-2.1, -1.1, 0.1, 1.2, 2.3)],
                         FRUIT_DEEP, OL_FINE))
    d.form(branch(HX + 30, HY - 30, 782, 178, 74, 40, k=-0.16), SUN_DEEP,
           sweep(620, 274, 150, 130, lo=.24, hi=-.38), RAY_SHADE, ol=OL_PROP)
    for (px, py, pr) in ((760, 154, 32), (812, 198, 27), (730, 210, 25)):
        d.form(fruit_blob(px, py, pr), SUN, None, None, ol=OL_FINE)
    return d.svg()


# =====================================================================
# 2. h-hedgehog-herb     SILLY -- has a face
#    A low fat body with a snout out to the LEFT and a spray of leaf
#    spines off the back.  Nothing else in the block is a left-facing
#    animal wedge.
# =====================================================================
def hedgehog_herb():
    d = Doc()
    BX, BY = 506, 690

    # ---- the spine spray, behind the body ----
    SP = []
    for i in range(21):
        t = i / 20.0
        a = -50 + 158.0 * t
        k = jitter(11.5 + i, 3, 0.13, 1.0)
        px = BX + 196 * math.sin(math.radians(a))
        py = BY - 168 * math.cos(math.radians(a))
        c = max(0.0, math.cos(math.radians(a)))
        L = (238 + 200 * (c ** 1.6)) * k[0]
        SP.append((px, py, L, 106 * k[1], a,
                   (GRASS_DEEP, GRASS, LEAF)[i % 3], i))
    for (px, py, L, Wd, a, col, i) in SP:
        dg = a + (7 if i % 2 else -6)
        if i == 6:                        # ODDITY: one spine is bent right over
            dg += 40
            L *= 0.64
        d.form(leaf_pointed(px, py, L, Wd, dg, curl=.10), col,
               sweep(px + 30, py - L * .5, Wd, L * .34, lo=.24, hi=-.38,
                     seed=i * 1.3), SHADE[col], ol=OL_PROP)

    # ---- feet ----
    for (fx, fw, fh) in ((386, 124, 168), (550, 110, 156), (680, 98, 146)):
        d.form(slab(fx, 1000 - fh * .5, fw, fh, r=0.42,
                    deg=(3 if fx > 500 else -4)),
               BARK, sweep_hard(fx, 1000 - fh * .5, fw * .5, fh * .5),
               BARK_DEEP, ol=OL_PROP)

    # ---- body + snout ----
    J, B = lobe_profile(seed=57.2, n=12, jit=0.06, bul=(14, 34))
    d.form(canopy_blob(BX, BY, 286, 196, 12, J, B, start=-92), BARK_LITE,
           sweep(BX, BY, 286, 196, lo=.30, hi=-.42, wob=.07, seed=2.4),
           BARK, inner=stroked("M600,524 C650,594 656,706 612,812",
                               INK, OL_MAIN))
    d.form(horn(280, 690, 196, 166, deg=-98, k=0.10), BARK_LITE,
           sweep(230, 718, 96, 66, lo=.26, hi=-.40), BARK, ol=OL_MAIN)
    d.add('<circle cx="116" cy="678" r="40" fill="%s"/>' % INK_SOFT)
    # ear
    d.form(leaf_round(394, 534, 118, 104, -22), BARK, sweep(394, 490, 56, 50,
           lo=.26, hi=-.40), BARK_DEEP, ol=OL_PROP)

    # ---- face: 202 wide on the 404-wide head end = 50.0% ----
    d.add(face(350, 706, 206, mass_w=404, default="happy", tilt=-4.0,
               eyes=((-54, -22), (48, -28)), eye_r=(20, 25),
               mouth=(-4, 38), mouth_k=0.92))
    return d.svg()


# =====================================================================
# 3. h-hotdog-hedge     WACKY -- has a face.  Must be instantly funny.
#    A clipped box hedge caught mid-hop, with two hotdogs standing up out
#    of it like rabbit ears.  Boxy silhouette + two vertical bars: nothing
#    else in the set reads like this.
# =====================================================================
def _hotdog(d, cx, cy, h, deg, seed, drip=False):
    w = h * 0.36
    d.form(slab(cx, cy, w, h, r=0.36, deg=deg), ACCENT,
           sweep_hard(cx, cy, w * .5, h * .5, lo=.28, hi=-.32), ACCENT_DEEP,
           ol=OL_MAIN)
    d.form(slab(cx, cy, w * .62, h * .94, r=0.46, deg=deg), EMBER,
           sweep_hard(cx, cy, w * .32, h * .47, lo=.26, hi=-.34), EMBER_DEEP,
           ol=OL_PROP)
    a = math.radians(deg)
    sp, ws = [], []
    for i in range(13):
        t = i / 12.0
        u = (t - .5) * h * .80
        v = math.sin(t * math.pi * 3.4 + seed) * w * .26
        sp.append((cx + v * math.cos(a) - u * math.sin(a),
                   cy + v * math.sin(a) + u * math.cos(a)))
        ws.append(34)
    d.form(ribbon(sp, ws), SUN, None, None, ol=OL_FINE)
    if drip:                        # ODDITY: mustard has dripped off one end
        d.form(crescent(cx + w * .30, cy + h * .52, 96, 34, 158, arc=-.30,
                        waist=.42), SUN, None, None, ol=OL_FINE)


def hotdog_hedge():
    d = Doc()
    # ---- two feet, mid-hop: the left one flat, the right one on tiptoe ----
    d.form(slab(360, 948, 144, 96, r=0.34, deg=-5), GRASS_DEEP,
           sweep_hard(360, 948, 72, 48), GRASS_DARK, ol=OL_PROP)
    d.form(slab(650, 928, 122, 130, r=0.36, deg=13), GRASS_DEEP,
           sweep_hard(650, 928, 61, 65), GRASS_DARK, ol=OL_PROP)

    # ---- the hedge box ----
    box = hard_poly([(146, 566), (868, 552), (884, 900), (132, 912)], 74)
    d.form(box, GRASS, sweep_hard(506, 732, 372, 178, lo=.26, hi=-.30),
           GRASS_DEEP, ol=OL_MAIN,
           inner=stroked(["M206,600 C238,662 232,742 202,806",
                          "M818,596 C788,656 792,740 822,802"],
                         INK, OL_MAIN))
    for (mx, my, L, Wd, dg, col) in ((208, 640, 92, 56, -30, GRASS_DEEP),
                                     (330, 604, 84, 50, 16, GRASS_DEEP),
                                     (700, 610, 86, 52, -18, GRASS_DEEP),
                                     (812, 690, 88, 52, 26, GRASS_DARK),
                                     (222, 812, 84, 50, 38, GRASS_DARK),
                                     (766, 848, 80, 48, -34, GRASS_DARK),
                                     (346, 872, 78, 46, 12, GRASS_DEEP),
                                     (632, 866, 82, 48, -8, GRASS_DEEP)):
        d.fill(leaf_round(mx, my, L, Wd, dg), col)

    for (sx, sy, L, Wd, dg, col) in ((196, 566, 152, 96, -34, GRASS),
                                     (300, 546, 138, 88, -8, LEAF),
                                     (498, 542, 126, 84, 10, GRASS),
                                     (792, 548, 146, 92, 26, LEAF),
                                     (172, 748, 126, 84, -96, GRASS),
                                     (846, 700, 124, 82, 96, GRASS),
                                     (854, 858, 112, 74, 118, LEAF)):
        d.form(leaf_round(sx, sy, L, Wd, dg), col,
               sweep(sx, sy - L * .4, Wd * .7, L * .3, lo=.24, hi=-.38),
               SHADE[col], ol=OL_PROP)

    # ---- the two hotdog "ears" ----
    _hotdog(d, 366, 356, 448, -9.0, 1.4)
    _hotdog(d, 646, 336, 470, 12.0, 3.1, drip=True)

    # ---- face: 348 wide on the 730-wide hedge = 47.7%.  Huge grin. ----
    d.add(face(492, 736, 348, mass_w=730, default="delighted", tilt=2.5,
               eyes=((-56, -30), (54, -24)), eye_r=(22, 27),
               mouth=(0, 40), mouth_k=1.18))
    return d.svg()


# =====================================================================
# 4. i-iris     REALISTIC -- no face
#    Tall and narrow: three standards up, three falls down, sword leaves
#    running the whole height of the frame.
# =====================================================================
def iris():
    d = Doc()
    FX, FY = 508, 430

    # ---- sword leaves, behind ----
    for (bx, by, tx, ty, hw, tw, bend, col, sd) in (
            (438, 1000, 262, 214, 44, 19, -84, GRASS_DEEP, 2.0),
            (556, 1000, 736, 168, 42, 18, 92, GRASS, 5.0),
            (486, 1000, 386, 302, 40, 17, -46, GRASS, 8.0),
            (600, 1000, 656, 402, 38, 17, 52, GRASS_DEEP, 11.0)):
        d.form(leaf_blade(bx, by, tx, ty, hw, tw, bend), col,
               sweep((bx + tx) / 2 + 26, (by + ty) / 2, 70, (by - ty) * .4,
                     lo=.18, hi=-.30, seed=sd), SHADE[col], ol=OL_MAIN)

    # ---- stem ----
    d.form(stem_slim(506, 486, BASE_Y, 56, root_seed=44.8, lean=-14,
                     w_base=162, root_lobes=3, root_depth=(16, 28)),
           GRASS_DEEP, sweep(514, 790, 84, 226, lo=.06, hi=-.10, wob=.03),
           GRASS_DARK)

    # ---- three falls (drooping, darker) ----
    for (lx, ly, L, Wd, dg, sd) in ((378, 470, 300, 196, -142, 21.0),
                                    (652, 456, 292, 190, 138, 26.0),
                                    (508, 498, 280, 224, 179, 31.0)):
        d.form(leaf_round(lx, ly, L, Wd, dg, curl=.12), BERRY,
               sweep(lx, ly + L * .10, Wd * 1.1, L * .70, lo=.30, hi=-.10,
                     seed=sd), BERRY_DEEP, ol=OL_MAIN,
               inner=stroked([vein(lx, ly, L * k, dg + o, frac=.72)
                              for k, o in ((1.0, 0), (0.72, -13), (0.72, 12))],
                             BERRY_DEEP, OL_FINE))
    # the SUN beard on the front fall
    d.form(leaf_round(506, 512, 192, 82, 179, curl=.05), SUN,
           sweep(506, 616, 48, 64, lo=.26, hi=-.42), SUN_SHADE, ol=OL_FINE)

    # ---- three standards (upright, lighter) ----
    for (lx, ly, L, Wd, dg, sd) in ((418, 452, 300, 186, -22, 36.0),
                                    (598, 442, 306, 192, 20, 41.0),
                                    (506, 428, 324, 206, -1, 46.0)):
        d.form(leaf_round(lx, ly, L, Wd, dg, curl=-.10), BERRY,
               sweep(lx, ly - L * .44, Wd * .8, L * .36, lo=.28, hi=-.42,
                     seed=sd), BERRY_DEEP, ol=OL_MAIN)
        d.line(vein(lx, ly, L, dg, frac=.62), OL_FINE, BERRY_DEEP)

    # ---- ODDITY: one bud on a side shoot has not opened yet ----
    d.add('<path d="M584,806 C664,806 736,786 784,742" fill="none" '
          'stroke="%s" stroke-width="%d" %s/>' % (GRASS_DEEP, OL_PROP, RJ))
    d.form(horn(792, 760, 180, 104, deg=26, k=-0.10), BERRY,
           sweep(824, 696, 56, 70, lo=.26, hi=-.42), BERRY_DEEP, ol=OL_PROP)
    return d.svg()


# =====================================================================
# 5. i-inchworm-ivy     SILLY -- has a face
#    A single tall twisting vine, round ivy leaves stepping up it, and an
#    inchworm arched over the top like a croquet hoop.
# =====================================================================
def inchworm_ivy():
    d = Doc()
    # ---- the vine: one long S, base to y=300 ----
    sp, ws = [], []
    for i in range(23):
        t = i / 22.0
        y = 924 - 624 * t
        x = 500 + 88 * math.sin(t * math.pi * 1.72)
        sp.append((x, y))
        ws.append(96 - 34 * t)
    d.form(ribbon(sp, ws, cap0="round", cap1="round"), GRASS_DEEP,
           sweep(520, 640, 120, 340, lo=.10, hi=-.16, wob=.05), GRASS_DARK,
           ol=OL_MAIN)
    d.form(stem_slim(500, 872, BASE_Y, 118, root_seed=77.2, lean=4,
                     w_base=268, root_lobes=3, root_depth=(16, 28)),
           GRASS_DEEP, sweep(512, 942, 116, 74, lo=.10, hi=-.16),
           GRASS_DARK)

    # ---- ivy leaves, alternating off the vine ----
    IV = [(388, 906, 176, 168, -74, GRASS, 1.0, False),
          (628, 838, 168, 160, 78, LEAF, 2.0, False),
          (378, 760, 172, 164, -84, LEAF, 3.0, True),
          (642, 682, 164, 156, 74, GRASS, 4.0, False),
          (396, 606, 158, 150, -70, GRASS, 5.0, False),
          (624, 528, 152, 146, 82, LEAF, 6.0, False),
          (412, 452, 146, 140, -66, LEAF, 7.0, False)]
    for (lx, ly, L, Wd, dg, col, sd, nib) in IV:
        p = leaf_round(lx, ly, L, Wd, dg, curl=.14)
        if nib:                      # ODDITY: the worm has eaten one leaf
            a = math.radians(dg)
            p += " " + bite(lx + L * .50 * math.sin(a) + Wd * .22 * math.cos(a),
                            ly - L * .50 * math.cos(a) + Wd * .22 * math.sin(a),
                            32)
        d.form(p, col, sweep(lx - L * .3 * math.sin(math.radians(dg)),
                             ly - L * .5, Wd * .7, L * .34, lo=.26, hi=-.40,
                             seed=sd), SHADE[col], ol=OL_PROP, evenodd=nib)
        d.line(vein(lx, ly, L, dg, frac=.60), OL_FINE)

    # ---- the inchworm, arched over the top ----
    sp2 = bow(366, 328, 650, 292, 0.44, 9)
    d.form(ribbon(sp2, [86, 96, 104, 108, 106, 100, 94, 88, 84]), LEAF,
           sweep(506, 220, 168, 96, lo=.28, hi=-.42), GRASS, ol=OL_MAIN,
           inner=stroked(["M%.0f,%.0f L%.0f,%.0f"
                          % (p[0] - 52, p[1] - 6, p[0] + 52, p[1] + 6)
                          for p in sp2[2:7]], INK, OL_FINE))
    J0, B0 = lobe_profile(seed=19.6, n=8, jit=0.06, bul=(6, 12))
    d.form(canopy_blob(356, 356, 62, 58, 8, J0, B0), GRASS,
           sweep(356, 356, 62, 58, lo=.28, hi=-.44), GRASS_DEEP, ol=OL_PROP)
    J, B = lobe_profile(seed=64.3, n=10, jit=0.05, bul=(8, 16))
    d.form(canopy_blob(668, 288, 150, 142, 10, J, B), LEAF,
           sweep(668, 288, 150, 142, lo=.30, hi=-.44), GRASS, ol=OL_MAIN)
    for (ax, ay, bx, by) in ((640, 156, 604, 94), (704, 156, 748, 98)):
        d.add('<path d="M%d,%d Q%d,%d %d,%d" fill="none" stroke="%s" '
              'stroke-width="14" %s/><circle cx="%d" cy="%d" r="19" '
              'fill="%s"/>' % (ax, ay + 6, (ax + bx) // 2 - 12, ay - 34,
                               bx, by, INK_SOFT, RJ, bx, by, INK_SOFT))
    # face: 120 wide on the 236-wide head = 50.8%
    d.add(face(670, 296, 176, mass_w=300, default="mischief", tilt=6.0,
               eyes=((-44, -22), (50, -18)), eye_r=(22, 26),
               mouth=(4, 40), mouth_k=0.92, brow_lift=4))
    return d.svg()


# =====================================================================
# 6. i-icecream-iris     WACKY -- has a face
#    A vertical stack: cone, three scoops, cherry.  A column of circles is
#    a silhouette no other plant in the block owns.
# =====================================================================
def icecream_iris():
    d = Doc()
    # ---- stem + leaves ----
    d.form(stem_slim(506, 806, BASE_Y, 108, root_seed=132.7, lean=-8,
                     w_base=250, root_lobes=3, root_depth=(16, 26)),
           GRASS, sweep(518, 922, 116, 96, lo=.10, hi=-.16), GRASS_DEEP)
    for (lx, ly, L, Wd, dg, sd) in ((424, 918, 232, 132, -74, 3.0),
                                    (556, 906, 218, 124, 70, 6.0)):
        d.form(leaf_pointed(lx, ly, L, Wd, dg, curl=.14), GRASS,
               sweep(lx + (60 if dg > 0 else -60), ly - L * .4, Wd * .8,
                     L * .3, lo=.24, hi=-.38, seed=sd), GRASS_DEEP,
               ol=OL_PROP)

    # ---- the waffle cone ----
    cone = hard_poly([(392, 594), (718, 604), (540, 892), (490, 890)], 36)
    waffle = []
    for i in range(5):
        waffle.append("M%d,%d L%d,%d" % (420 + i * 60, 614 + i * 6,
                                         482 + i * 22, 864))
        waffle.append("M%d,%d L%d,%d" % (410 + i * 10, 644 + i * 48,
                                         700 - i * 34, 636 + i * 48))
    d.form(cone, SUN_DEEP, sweep_hard(548, 712, 168, 160, lo=.26, hi=-.34),
           RAY_SHADE, ol=OL_MAIN, inner=stroked(waffle, RAY_SHADE, OL_FINE))

    # ---- three scoops, bottom first ----
    for (cx, cy, rx, ry, col, n, sd, notch) in (
            (546, 574, 210, 174, FRUIT, 12, 12.4, None),
            (488, 396, 192, 158, LEAF, 12, 26.8, 4),
            (426, 244, 168, 140, SUN, 11, 41.2, None)):
        J, B = lobe_profile(sd, n, jit=0.05, bul=(16, 34))
        d.form(canopy_blob(cx, cy, rx, ry, n, J, B, start=-98, notch=notch),
               col, sweep(cx, cy, rx, ry, lo=.30, hi=-.44, wob=.07,
                          seed=sd * .1), SHADE[col], ol=OL_MAIN)
    # mint chips + sprinkles, flat marks
    d.add(dots([(424, 368, 21), (506, 342, 18), (556, 414, 20),
                (452, 440, 17), (546, 472, 16)], GRASS_DARK))
    for (sx, sy, dg, col) in ((362, 206, 24, FRUIT), (466, 192, -32, SKY_HI),
                              (506, 260, 14, BERRY), (354, 278, -18, FRUIT)):
        d.fill(slab(sx, sy, 46, 20, r=0.48, deg=dg), col)

    # ---- ODDITY: the cherry has slid off centre and is about to fall ----
    d.add('<path d="M356,166 C352,118 336,94 312,82" fill="none" '
          'stroke="%s" stroke-width="%d" %s/>' % (BARK_DEEP, OL_PROP, RJ))
    d.form(fruit_blob(352, 194, 62), FRUIT,
           sweep(352, 194, 62, 62, lo=.28, hi=-.46), FRUIT_DEEP, ol=OL_PROP,
           inner='<path d="%s" fill="%s" opacity="0.8"/>'
                 % (chip(328, 170, 22), CREAM))

    # ---- face on the bottom scoop: 212 on 416 = 51.0% ----
    d.add(face(532, 598, 208, mass_w=412, default="happy", tilt=-6.0,
               eyes=((-48, -8), (50, -14)), eye_r=(17, 24),
               mouth=(-2, 52), mouth_k=1.05))
    return d.svg()


# =====================================================================
# 7. j-jasmine     REALISTIC -- no face
#    An arching sprig, not a bouquet: the stem leans hard left and the
#    three star flowers sit at three different heights.  Airy and lopsided.
# =====================================================================
def _jasmine_flower(d, cx, cy, r, deg, seed):
    for i in range(5):
        a = deg + 72.0 * i + (6.0 if i == 2 else -3.0 * (i % 2))
        k = 0.86 if i == 3 else 1.0
        rad = math.radians(a)
        px = cx + r * .16 * math.sin(rad)
        py = cy - r * .16 * math.cos(rad)
        d.form(leaf_round(px, py, r * .96 * k, r * .74, a, curl=.06),
               CREAM, sweep(cx, cy, r, r, lo=.34, hi=-.50, seed=seed + i),
               CREAM_DEEP, ol=OL_PROP)
    J, B = lobe_profile(seed * 1.7, 8, jit=0.04, bul=(3, 6))
    d.form(canopy_blob(cx + 2, cy + 2, r * .30, r * .28, 8, J, B), SUN,
           sweep(cx, cy, r * .3, r * .3, lo=.30, hi=-.46), SUN_SHADE,
           ol=OL_FINE)


def jasmine():
    d = Doc()
    # ---- the arching main stem ----
    d.form(stem_slim(534, 680, BASE_Y, 62, root_seed=88.1, lean=-26,
                     w_base=182, root_lobes=3, root_depth=(16, 28)),
           GRASS, sweep(546, 856, 88, 170, lo=.08, hi=-.12, wob=.03),
           GRASS_DEEP)
    for (x0, y0, x1, y1, w0, w1, k) in ((520, 706, 300, 388, 60, 44, 0.26),
                                        (508, 742, 690, 512, 54, 40, -0.24),
                                        (392, 500, 594, 244, 46, 34, -0.20)):
        d.form(branch(x0, y0, x1, y1, w0, w1, k), GRASS,
               sweep((x0 + x1) / 2, (y0 + y1) / 2, 110, 110, lo=.20, hi=-.32,
                     seed=x1 * .01), GRASS_DEEP, ol=OL_MAIN)

    # ---- leaves ----
    for (lx, ly, L, Wd, dg, col, sd) in ((452, 660, 238, 130, -58, GRASS, 2.0),
                                         (596, 690, 224, 122, 68, LEAF, 5.0),
                                         (378, 470, 196, 108, -46, LEAF, 8.0),
                                         (628, 546, 186, 102, 74, GRASS, 11.0),
                                         (474, 380, 174, 96, -34, GRASS, 14.0),
                                         (556, 866, 208, 116, 96, GRASS, 17.0)):
        d.form(leaf_pointed(lx, ly, L, Wd, dg, curl=.14), col,
               sweep(lx + (50 if dg > 0 else -50), ly - L * .44, Wd * .8,
                     L * .32, lo=.24, hi=-.38, seed=sd), SHADE[col],
               ol=OL_PROP)
        d.line(vein(lx, ly, L, dg, frac=.66), OL_FINE)

    # ---- three flowers at three heights ----
    _jasmine_flower(d, 256, 336, 176, -96, 3.0)
    _jasmine_flower(d, 614, 244, 160, -78, 21.0)
    _jasmine_flower(d, 736, 486, 148, -110, 39.0)
    # ---- ODDITY: one bud still closed, drooping off the low right branch ---
    d.add('<path d="M700,528 C742,570 762,616 762,668" fill="none" '
          'stroke="%s" stroke-width="%d" %s/>' % (GRASS_DEEP, OL_PROP, RJ))
    d.form(horn(760, 700, 132, 78, deg=178, k=0.12), CREAM,
           sweep(772, 756, 44, 42, lo=.28, hi=-.44), CREAM_DEEP, ol=OL_FINE)
    return d.svg()


# =====================================================================
# 8. j-jaguar-jade     SILLY -- has a face
#    Five fat spotted paddles fanned UP off a squat ringed pot.  A 130-deg
#    fan, not a 360-deg flower: nothing else in the block fans this way.
# =====================================================================
def jaguar_jade():
    d = Doc()
    PX, PY = 500, 744

    # ---- the pot ----
    d.form(trunk_chunky(500, 712, BASE_Y, 212, 306, root_seed=143.6, lean=6,
                        root_lobes=3, root_depth=(14, 24), flare=0.94),
           BARK, sweep(516, 872, 168, 150, lo=.20, hi=-.20, wob=.05),
           BARK_DEEP,
           inner=stroked(["M382,792 C456,812 550,814 626,794",
                          "M376,882 C452,902 550,904 628,884"],
                         INK, OL_MAIN))

    # ---- five paddles.  index 4 is the ODDITY: stubby and rotated out ----
    PAD = [(-84, 384, 168, 6.0), (-44, 520, 196, 13.0), (-2, 606, 262, 20.0),
           (38, 512, 190, 27.0), (78, 370, 162, 34.0)]
    for i, (dg, L, Wd, sd) in enumerate(PAD):
        a = math.radians(dg)
        bx = PX + 66 * math.sin(a)
        by = PY - 30 * math.cos(a)
        # jaguar rosettes, CLIPPED to their own pad (inner=)
        nx, ny = math.cos(a), math.sin(a)          # across the pad
        spots = ""
        for j in range(5):
            t = 0.24 + 0.165 * j
            off = (Wd * .20) * (1 if j % 2 else -1) * (0.6 + 0.4 * (j % 3))
            rx = bx + L * t * math.sin(a) + nx * off
            ry = by - L * t * math.cos(a) + ny * off
            rr = 33 - 2.5 * j
            spots += ('<path d="%s" fill="%s"/><path d="%s" fill="%s"/>'
                      % (fruit_blob(rx, ry, rr, deg=j * 37 + i * 11),
                         EMBER_DEEP,
                         fruit_blob(rx + 2, ry + 2, rr * .44, deg=j * 21),
                         ACCENT))
        d.form(leaf_round(bx, by, L, Wd, dg, curl=.06), ACCENT,
               sweep(bx + L * .30 * math.sin(a), by - L * .46 * math.cos(a),
                     Wd * .8, L * .34, lo=.30, hi=-.44, seed=sd),
               ACCENT_DEEP, ol=OL_MAIN, inner=spots)

    # ---- face on the centre paddle: 138 wide on the 268-wide pad = 51.5% ---
    d.add(face(490, 438, 154, mass_w=262, default="happy", tilt=-2.0,
               eyes=((-44, -4), (48, -12)), eye_r=(24, 26),
               mouth=(2, 48), mouth_k=1.06))
    return d.svg()


# =====================================================================
# 9. j-jellybean-jungle     WACKY -- has a face
#    A TALL upright canopy on a squat, wide, jiggly grey stump.  The stump
#    is the character; the canopy is the sweet jar.
# =====================================================================
def jellybean_jungle():
    d = Doc()
    # ---- the squat stump: wide foot, no trunk to speak of ----
    d.form(stem_slim(504, 636, BASE_Y, 288, root_seed=166.4, lean=-10,
                     w_base=470, root_lobes=4, root_depth=(30, 54)),
           STEEL, sweep(524, 858, 220, 168, lo=.22, hi=-.24, wob=.05),
           STEEL_DEEP,
           inner=stroked(["M392,782 C378,846 384,910 402,962",
                          "M624,796 C640,856 632,912 616,964"],
                         INK, OL_MAIN))

    # ---- a tall narrow canopy: an upright egg, not a wide dome ----
    for (cx, cy, rx, ry, col, n, st, notch, sd) in (
            (438, 274, 166, 158, GRASS, 11, -104, None, 12.6),
            (580, 232, 160, 152, GRASS, 11, -76, 5, 25.3),
            (508, 496, 196, 172, GRASS, 12, -92, None, 38.9),
            (502, 366, 228, 268, LEAF, 13, -96, None, 52.4)):
        J, B = lobe_profile(sd, n, jit=0.10, bul=(24, 58))
        d.form(canopy_blob(cx, cy, rx, ry, n, J, B, start=st, notch=notch),
               col, sweep(cx, cy, rx, ry, lo=.32, hi=-.44, wob=.09,
                          seed=cx * .011), SHADE[col])
    for (mx, my, L, Wd, dg) in ((392, 250, 78, 46, -28), (548, 172, 72, 42, 18),
                                (614, 396, 74, 44, 32), (386, 448, 76, 44, -36),
                                (508, 572, 70, 40, 8)):
        d.fill(leaf_round(mx, my, L, Wd, dg), GRASS_DEEP)

    # ---- the jellybeans ----
    BEANS = [(390, 226, -22, FRUIT), (524, 146, 12, SKY_HI),
             (610, 262, 34, SUN), (398, 380, 8, BERRY),
             (596, 418, -26, ACCENT), (486, 306, 44, FRUIT),
             (554, 542, -14, SKY_HI), (386, 534, 24, SUN),
             (494, 446, -40, ACCENT)]
    for (bx, by, dg, col) in BEANS:
        d.form(slab(bx, by, 104, 66, r=0.48, deg=dg), col,
               sweep_hard(bx, by, 52, 33, lo=.28, hi=-.34), SHADE[col],
               ol=OL_PROP)
    # ODDITY: one bean has rolled out of the tree and lies in the dirt
    d.form(slab(816, 968, 100, 64, r=0.48, deg=-8), BERRY,
           sweep_hard(816, 968, 50, 32, lo=.28, hi=-.34), BERRY_DEEP,
           ol=OL_PROP)

    # ---- face on the stump: 216 wide on a 430-wide stump = 50.2% ----
    d.add(face(494, 812, 216, mass_w=430, default="delighted", tilt=3.0,
               eyes=((-58, -18), (52, -12)), eye_r=(18, 20),
               mouth=(-2, 42), mouth_k=1.1))
    return d.svg()


# =====================================================================
# 10. k-kale     REALISTIC -- no face
#     A TALL frilly column of curl, not a low mound: jit and bul are wound
#     right up so every clump edge is a ruffle, over pale cut stalks.
# =====================================================================
def kale():
    d = Doc()
    # ---- pale ribs at the bottom, fanned, drawn first ----
    for (x0, y0, x1, y1, w0, w1, k) in ((476, 1000, 344, 738, 104, 74, 0.16),
                                        (498, 1000, 448, 682, 108, 76, 0.06),
                                        (508, 1000, 576, 674, 106, 74, -0.06),
                                        (528, 1000, 672, 728, 100, 70, -0.16),
                                        (492, 1000, 508, 782, 92, 68, 0.02)):
        d.form(branch(x0, y0, x1, y1, w0, w1, k, cap="flat"), CREAM,
               sweep((x0 + x1) / 2, (y0 + y1) / 2, 90, 150, lo=.20, hi=-.30,
                     seed=x1 * .02), CREAM_DEEP, ol=OL_MAIN)
    d.form(stem_slim(502, 880, BASE_Y, 224, root_seed=198.2, lean=0,
                     w_base=356, root_lobes=4, root_depth=(16, 28)),
           CREAM, sweep(516, 960, 146, 66, lo=.16, hi=-.22), CREAM_DEEP)

    # ---- the curl: eight ruffled clumps, back rank darkest ----
    CL = [(252, 386, 202, 188, GRASS_DEEP, 18, -104, None, 5.1),
          (760, 364, 200, 188, GRASS_DEEP, 18, -78, None, 11.3),
          (250, 700, 200, 184, GRASS_DEEP, 17, -96, 6, 17.6),
          (764, 686, 198, 182, GRASS_DEEP, 17, -88, None, 23.8),
          (508, 272, 216, 190, GRASS, 18, -94, None, 30.2),
          (320, 540, 194, 186, GRASS, 17, -102, None, 36.5),
          (694, 526, 192, 184, GRASS, 17, -82, None, 42.9),
          (508, 500, 262, 250, GRASS, 20, -92, None, 49.4),
          (500, 722, 248, 172, LEAF, 19, -96, 9, 55.8)]
    for (cx, cy, rx, ry, col, n, st, notch, sd) in CL:
        J, B = lobe_profile(sd, n, jit=0.16, bul=(30, 70))
        d.form(canopy_blob(cx, cy, rx, ry, n, J, B, start=st, notch=notch),
               col, sweep(cx, cy, rx, ry, lo=.30, hi=-.44, wob=.12,
                          seed=cx * .014), SHADE[col])

    # ---- pale midribs: the mark that says KALE and not "a green cloud" ----
    for pth in ("M500,866 C490,782 496,704 510,622",
                "M384,830 C350,762 326,692 310,628",
                "M620,822 C654,754 678,686 696,624",
                "M506,596 C498,534 500,470 510,408",
                "M416,574 C382,518 358,466 342,414",
                "M594,566 C628,510 650,458 664,410",
                "M510,386 C504,336 506,294 512,258"):
        d.line(pth, OL_FINE, CREAM_DEEP)
    for (mx, my, L, Wd, dg) in ((268, 460, 86, 52, -30), (742, 444, 82, 50, 26),
                                (410, 300, 78, 48, -16), (604, 286, 76, 46, 20),
                                (302, 724, 82, 48, 34), (710, 710, 80, 46, -24)):
        d.fill(leaf_round(mx, my, L, Wd, dg), GRASS_DARK)
    # outer leaves lolling out sideways onto the dirt
    for (lx, ly, L, Wd, dg, col, sd) in ((300, 896, 226, 172, -104, GRASS, 2.0),
                                         (716, 880, 218, 166, 102, GRASS, 6.0)):
        d.form(leaf_round(lx, ly, L, Wd, dg, curl=.16), col,
               sweep(lx + (70 if dg > 0 else -70), ly - 24, Wd * .7, 72,
                     lo=.26, hi=-.40, seed=sd), SHADE[col], ol=OL_MAIN)
        d.line(vein(lx, ly, L, dg, frac=.6), OL_FINE)
    # ---- ODDITY: one outer leaf has flopped right over onto the soil ----
    d.form(leaf_round(796, 880, 158, 132, 100, curl=.2), GRASS,
           sweep(732, 862, 76, 56, lo=.26, hi=-.40), GRASS_DEEP, ol=OL_PROP)
    d.line(vein(796, 880, 158, 100, frac=.6), OL_FINE)
    return d.svg()


# =====================================================================
# 11. k-kangaroo-kelp     SILLY -- has a face
#     A tall standing S with a heavy haunch, a long flat foot and two big
#     ears, with kelp fronds trailing off it.
# =====================================================================
def kangaroo_kelp():
    d = Doc()
    # ---- kelp fronds, behind ----
    for (x0, y0, x1, y1, w, amp, ph, col) in (
            (612, 900, 862, 452, 76, 74, 0.4, GRASS_DEEP),
            (392, 918, 168, 596, 70, 66, 2.1, GRASS_DEEP),
            (642, 812, 830, 700, 62, 52, 1.2, GRASS)):
        d.form(squiggle(x0, y0, x1, y1, w, amp, waves=1.7, phase=ph),
               col, sweep((x0 + x1) / 2, (y0 + y1) / 2, 130, 150, lo=.24,
                          hi=-.36, seed=x1 * .02), SHADE[col], ol=OL_MAIN)

    # ---- the tail, curling away to the right ----
    d.form(crescent(544, 830, 320, 112, 104, arc=-.34, waist=.34), GRASS_DEEP,
           sweep(716, 890, 128, 58, lo=.24, hi=-.38), GRASS_DARK, ol=OL_MAIN)

    # ---- the long flat foot ----
    d.form(hard_poly([(276, 924), (492, 906), (516, 986), (262, 998)], 44),
           GRASS, sweep_hard(388, 954, 130, 48, lo=.24, hi=-.30), GRASS_DEEP,
           ol=OL_MAIN)

    # ---- haunch + body: one S ribbon ----
    sp = [(452, 872), (432, 806), (452, 698), (516, 588), (528, 476)]
    d.form(ribbon(sp, [236, 262, 216, 182, 168], cap0="round", cap1="flat"),
           GRASS, sweep(500, 760, 170, 250, lo=.16, hi=-.24, wob=.06),
           GRASS_DEEP, ol=OL_MAIN)
    # the pouch
    d.form(smooth_closed([(348, 706), (446, 690), (470, 776), (438, 856),
                          (356, 848), (326, 782)]), GRASS_DEEP,
           sweep(400, 790, 78, 84, lo=.26, hi=-.40), GRASS_DARK, ol=OL_MAIN)
    # a little arm
    d.form(branch(516, 618, 630, 668, 62, 44, -0.24), GRASS,
           sweep(574, 644, 70, 46, lo=.24, hi=-.36), GRASS_DEEP, ol=OL_PROP)

    # ---- head + ears ----
    for (ex, ey, L, Wd, dg, sd) in ((470, 396, 264, 96, -17, 3.0),
                                    (582, 388, 246, 90, 15, 7.0)):
        d.form(leaf_pointed(ex, ey, L, Wd, dg, curl=.10), GRASS,
               sweep(ex, ey - L * .5, Wd, L * .34, lo=.26, hi=-.40, seed=sd),
               GRASS_DEEP, ol=OL_PROP)
        d.fill(leaf_pointed(ex, ey - 14, L * .62, Wd * .48, dg), GRASS_DEEP)
    J, B = lobe_profile(seed=76.5, n=11, jit=0.05, bul=(10, 22))
    d.form(canopy_blob(528, 396, 168, 148, 11, J, B, start=-94), LEAF,
           sweep(528, 396, 168, 148, lo=.30, hi=-.44, wob=.06), GRASS,
           ol=OL_MAIN)
    # snout
    d.form(leaf_round(392, 452, 132, 106, -84, curl=.10), LEAF,
           sweep(340, 434, 62, 52, lo=.26, hi=-.42), GRASS, ol=OL_PROP)
    d.add('<circle cx="268" cy="440" r="26" fill="%s"/>' % INK_SOFT)
    # ---- ODDITY: a small kelp leaf is tucked in the pouch, like a joey ----
    d.form(leaf_pointed(400, 800, 158, 82, -8, curl=.14), LEAF,
           sweep(400, 730, 66, 54, lo=.26, hi=-.40), GRASS, ol=OL_PROP)

    # ---- face: 168 wide on a 336-wide head = 50.0% ----
    d.add(face(536, 400, 190, mass_w=336, default="surprised", tilt=-5.0,
               eyes=((-46, -20), (52, -14)), eye_r=(19, 26),
               mouth=(0, 50), mouth_k=0.82, brow_lift=8))
    return d.svg()


# =====================================================================
# 12. k-ketchup-cactus     WACKY -- has a face
#     A squeeze bottle that thinks it is a saguaro.  Everything rigid:
#     slab / panel / hard_poly / sweep_hard, with a squirt of ketchup
#     arcing out of the nozzle.
# =====================================================================
def ketchup_cactus():
    d = Doc()
    CXK = 496
    # ---- base pad ----
    plate, pads = plinth(CXK, BASE_Y, 396, 104, r=0.06, feet=3)
    for pad in pads:
        d.form(pad, FRUIT_DEEP, sweep_hard(CXK, 976, 60, 26), FRUIT_DEEP,
               ol=OL_PROP)
    d.form(plate, FRUIT, sweep_hard(CXK, 946, 198, 52, lo=.22, hi=-.28),
           FRUIT_DEEP, ol=OL_MAIN)

    # ---- two arms, drawn behind the body ----
    d.form(elbow([(322, 604), (196, 604), (196, 404)], 116, 54), FRUIT,
           sweep_hard(230, 520, 110, 120, lo=.24, hi=-.30), FRUIT_DEEP,
           ol=OL_MAIN)
    d.form(elbow([(668, 686), (816, 686), (816, 526)], 104, 48), FRUIT,
           sweep_hard(772, 606, 100, 96, lo=.24, hi=-.30), FRUIT_DEEP,
           ol=OL_MAIN)

    # ---- body ----
    d.form(slab(CXK, 630, 392, 618, r=0.15, skew=0.07), FRUIT,
           sweep_hard(CXK, 630, 196, 309, lo=.26, hi=-.30), FRUIT_DEEP,
           ol=OL_MAIN)
    # spines
    for (sx, sy, dg) in ((306, 430, -96), (300, 546, -92), (308, 760, -100),
                         (690, 470, 94), (694, 622, 90), (686, 806, 98),
                         (400, 336, -18), (596, 330, 16)):
        d.form(horn(sx, sy, 64, 34, deg=dg, k=0.08), FRUIT_DEEP, None, None,
               ol=OL_FINE)

    # ---- shoulder, neck, cap, nozzle ----
    d.form(slab(CXK, 318, 252, 108, r=0.28), FRUIT,
           sweep_hard(CXK, 318, 126, 54), FRUIT_DEEP, ol=OL_MAIN)
    d.form(slab(CXK, 246, 168, 62, r=0.30), FRUIT_DEEP, None, None,
           ol=OL_PROP)
    cap = slab(CXK, 186, 208, 96, r=0.16)
    d.form(cap, SUN, sweep_hard(CXK, 186, 104, 48, lo=.24, hi=-.32),
           SUN_SHADE, ol=OL_MAIN,
           inner=stroked(grille(CXK, 186, 168, 76, 6, gap=0.40), SUN_SHADE,
                         OL_FINE))
    d.form(hard_poly([(444, 142), (548, 142), (526, 74), (470, 74)], 22),
           SUN_DEEP, sweep_hard(496, 110, 52, 34), RAY_SHADE, ol=OL_PROP)

    # ---- the squirt ----
    d.form(squiggle(504, 78, 782, 190, 44, 46, waves=1.1, phase=0.2,
                    taper=0.62), FRUIT,
           sweep(650, 118, 130, 60, lo=.26, hi=-.40), FRUIT_DEEP, ol=OL_PROP)
    d.form(fruit_blob(824, 214, 62, deg=18), FRUIT,
           sweep(824, 214, 62, 62, lo=.28, hi=-.44), FRUIT_DEEP, ol=OL_PROP)
    d.form(star4(884, 148, 44, 14, waist=.34), FRUIT, None, None, ol=OL_FINE)

    # ---- the label, carrying the face ----
    outer, inner = panel(CXK - 4, 616, 316, 372, r=0.10, inset=0.14)
    d.form(outer, CREAM, sweep_hard(CXK - 4, 616, 158, 186, lo=.24, hi=-.30),
           CREAM_DEEP, ol=OL_MAIN, inner=stroked(inner, CREAM_DEEP, OL_FINE))
    # ---- ODDITY: a blob has already dripped onto the soil ----
    d.form(fruit_blob(268, 936, 50, deg=-24), FRUIT,
           sweep(268, 936, 50, 50, lo=.28, hi=-.44), FRUIT_DEEP, ol=OL_FINE)

    # ---- face on the label: 174 wide on the 316-wide label = 55.1% ----
    d.add(face(490, 620, 186, mass_w=316, default="mischief", tilt=1.5,
               eyes=((-52, -34), (50, -28)), eye_r=(21, 25),
               mouth=(0, 46), mouth_k=1.0, brow_lift=-4))
    return d.svg()


# =====================================================================
# 13. l-lavender     REALISTIC -- no face
#     Three narrow spikes and a lot of air.  The only plant in the block
#     whose silhouette is mostly gaps.
# =====================================================================
def _lav_spike(d, x, ytop, ybot, hw, seed, lean=0.0):
    n = 15
    J, B = lobe_profile(seed, n, jit=0.16, bul=(16, 34))
    cy = (ytop + ybot) * .5
    ry = (ybot - ytop) * .5
    cx = x + lean
    d.form(canopy_blob(cx, cy, hw, ry, n, J, B, start=-92),
           BERRY, sweep(cx, cy, hw, ry, lo=.30, hi=-.34, wob=.10, seed=seed),
           BERRY_DEEP, ol=OL_MAIN,
           inner=stroked(["M%.0f,%.0f L%.0f,%.0f"
                          % (cx - hw, ytop + (ybot - ytop) * t - 12,
                             cx + hw, ytop + (ybot - ytop) * t + 10)
                          for t in (0.22, 0.42, 0.62, 0.82)], INK, OL_FINE))
    # a few florets breaking the edge so the spike is not a lozenge
    for i, t in enumerate((0.16, 0.36, 0.58, 0.78)):
        sx = cx + hw * (1.02 if i % 2 else -1.02)
        sy = ytop + (ybot - ytop) * t
        d.form(fruit_blob(sx, sy, 34 - 3 * i, deg=i * 41), BERRY,
               sweep(sx, sy, 34, 34, lo=.28, hi=-.44), BERRY_DEEP, ol=OL_FINE)


def lavender():
    d = Doc()
    # ---- grass blades, behind ----
    for (bx, by, tx, ty, hw, tw, bend, col, sd) in (
            (446, 1000, 224, 460, 40, 18, -92, GRASS_DEEP, 2.0),
            (556, 1000, 788, 418, 38, 17, 96, GRASS, 5.0),
            (486, 1000, 356, 616, 36, 16, -54, GRASS, 8.0),
            (592, 1000, 700, 590, 34, 16, 58, GRASS_DEEP, 11.0),
            (520, 1000, 512, 528, 32, 15, 8, GRASS, 14.0)):
        d.form(leaf_blade(bx, by, tx, ty, hw, tw, bend), col,
               sweep((bx + tx) / 2 + 22, (by + ty) / 2, 66, (by - ty) * .4,
                     lo=.18, hi=-.30, seed=sd), SHADE[col], ol=OL_MAIN)

    # ---- three stalks + a short fourth ----
    STALK = [(332, 496, 966, 30, 0.20), (508, 420, 972, 28, -0.10),
             (676, 528, 968, 26, 0.16), (798, 690, 962, 24, -0.22)]
    for (sx, y0, y1, w, k) in STALK:
        d.form(branch(sx + (26 if sx < 500 else -22), y1, sx, y0, w + 12, w,
                      k, cap="round"), GRASS_DEEP,
               sweep(sx, (y0 + y1) / 2, 60, (y1 - y0) * .4, lo=.16, hi=-.26,
                     seed=sx * .02), GRASS_DARK, ol=OL_MAIN)
    d.form(stem_slim(504, 900, BASE_Y, 150, root_seed=210.4, lean=0,
                     w_base=286, root_lobes=3, root_depth=(14, 24)),
           GRASS_DEEP, sweep(516, 958, 110, 62, lo=.14, hi=-.20), GRASS_DARK)

    # ---- the four spikes ----
    _lav_spike(d, 332, 156, 502, 62, 6.4, lean=-6)
    _lav_spike(d, 508, 96, 428, 66, 19.2, lean=4)
    _lav_spike(d, 676, 194, 534, 58, 33.8, lean=8)
    _lav_spike(d, 798, 404, 696, 46, 47.1, lean=-4)
    # ---- ODDITY: one floret has dropped off and lies in the dirt ----
    d.form(fruit_blob(232, 962, 38, deg=22), BERRY,
           sweep(232, 962, 38, 38, lo=.28, hi=-.44), BERRY_DEEP, ol=OL_FINE)
    return d.svg()


# =====================================================================
# 14. l-ladybug-lettuce     SILLY -- has a face
#     A wide flat lettuce skirt on the ground with a big round ladybug
#     riding above it.  Low+wide under, round on top.
# =====================================================================
def ladybug_lettuce():
    d = Doc()
    # ---- the lettuce skirt: low, wide, very ruffled ----
    for (cx, cy, rx, ry, col, n, st, notch, sd) in (
            (252, 816, 158, 106, GRASS_DEEP, 14, -102, None, 4.2),
            (764, 806, 156, 104, GRASS_DEEP, 14, -76, None, 9.8),
            (374, 748, 166, 112, GRASS, 15, -96, 6, 15.3),
            (648, 736, 170, 114, GRASS, 15, -84, None, 21.7),
            (508, 830, 226, 116, LEAF, 17, -92, None, 28.4)):
        J, B = lobe_profile(sd, n, jit=0.16, bul=(28, 58))
        d.form(canopy_blob(cx, cy, rx, ry, n, J, B, start=st, notch=notch),
               col, sweep(cx, cy, rx, ry, lo=.30, hi=-.42, wob=.12,
                          seed=cx * .013), SHADE[col])
    for pth in ("M508,932 C500,894 502,858 512,826",
                "M354,842 C338,814 330,790 328,764",
                "M664,832 C680,806 690,784 694,760"):
        d.line(pth, OL_FINE, CREAM_DEEP)

    # ---- the stalk it perches on ----
    d.form(branch(504, 986, 500, 588, 96, 72, -0.04, cap="flat"), GRASS_DEEP,
           sweep(504, 786, 68, 200, lo=.18, hi=-.26), GRASS_DARK, ol=OL_MAIN)
    for (lx, ly, L, Wd, dg, sd) in ((466, 790, 176, 100, -74, 3.0),
                                    (548, 758, 164, 94, 72, 6.0)):
        d.form(leaf_pointed(lx, ly, L, Wd, dg, curl=.14), GRASS,
               sweep(lx + (50 if dg > 0 else -50), ly - L * .4, Wd * .8,
                     L * .3, lo=.24, hi=-.38, seed=sd), GRASS_DEEP,
               ol=OL_PROP)

    # ---- legs, drawn behind the shell ----
    for (x0, y0, x1, y1) in ((420, 470, 322, 556), (410, 542, 306, 620),
                             (598, 462, 700, 548), (610, 538, 716, 610)):
        d.form(branch(x0, y0, x1, y1, 40, 30, 0.14 if x1 < 500 else -0.14),
               INK_SOFT, None, None, ol=OL_FINE)

    # ---- the shell ----
    J, B = lobe_profile(seed=91.7, n=13, jit=0.04, bul=(10, 20))
    shell = canopy_blob(508, 430, 202, 182, 13, J, B, start=-94)
    spots = dots([(424, 366, 36), (588, 356, 33), (398, 470, 34),
                  (614, 458, 31), (462, 556, 30), (566, 562, 28)], INK_SOFT)
    d.form(shell, FRUIT, sweep(508, 430, 202, 182, lo=.30, hi=-.44, wob=.06),
           FRUIT_DEEP, ol=OL_MAIN,
           inner=spots + stroked("M508,240 L512,620", INK, OL_MAIN))
    # ---- ODDITY: one spot has slid right off the shell onto a lettuce leaf -
    d.fill(fruit_blob(710, 742, 32, deg=18), INK_SOFT)

    # ---- head + cream mask ----
    J, B = lobe_profile(seed=118.3, n=10, jit=0.05, bul=(8, 16))
    d.form(canopy_blob(500, 246, 172, 138, 10, J, B, start=-96), INK_SOFT,
           None, None, ol=OL_MAIN)
    for (ax, ay, bx, by) in ((456, 138, 410, 66), (548, 136, 606, 70)):
        d.add('<path d="M%d,%d Q%d,%d %d,%d" fill="none" stroke="%s" '
              'stroke-width="15" %s/><circle cx="%d" cy="%d" r="24" '
              'fill="%s"/>' % (ax, ay, (ax + bx) // 2, ay - 46, bx, by,
                               INK_SOFT, RJ, bx, by, INK_SOFT))
    J, B = lobe_profile(seed=137.9, n=10, jit=0.04, bul=(6, 12))
    d.form(canopy_blob(500, 280, 150, 106, 10, J, B, start=-92), CREAM,
           sweep(500, 280, 150, 106, lo=.34, hi=-.46), CREAM_DEEP, ol=OL_PROP)
    # ---- face on the cream mask: 172 wide on the 300-wide mask = 57.3% ----
    d.add(face(500, 286, 172, mass_w=300, default="happy", tilt=1.5,
               eyes=((-54, -18), (56, -22)), eye_r=(23, 26),
               mouth=(0, 46), mouth_k=1.0, brow_lift=0))
    return d.svg()


# =====================================================================
# 15. l-lollipop-lily     WACKY -- has a face
#     One clean disc with a real spiral wound into it, on a slim stick.
#     The tidiest silhouette in the block, on purpose.
# =====================================================================
def lollipop_lily():
    d = Doc()
    d.form(stem_slim(500, 480, BASE_Y, 82, root_seed=155.8, lean=10,
                     w_base=224, root_lobes=3, root_depth=(16, 28)),
           GRASS, sweep(512, 780, 96, 250, lo=.06, hi=-.10, wob=.03),
           GRASS_DEEP)
    # ODDITY: the right leaf is half the length of the left and folded over
    for (lx, ly, L, Wd, dg, sd, curl) in ((452, 812, 268, 152, -72, 3.0, .14),
                                          (538, 768, 152, 130, 62, 6.0, -.34)):
        d.form(leaf_pointed(lx, ly, L, Wd, dg, curl=curl), GRASS,
               sweep(lx + (56 if dg > 0 else -56), ly - L * .42,
                     Wd * .8, L * .32, lo=.24, hi=-.38, seed=sd),
               GRASS_DEEP, ol=OL_PROP)
        d.line(vein(lx, ly, L, dg, frac=.58), OL_FINE)

    # ---- the disc ----
    LX, LY, LR = 498, 290, 236
    J, B = lobe_profile(seed=61.2, n=14, jit=0.020, bul=(4, 8))
    disc = canopy_blob(LX, LY, LR, LR * .98, 14, J, B, start=-94)
    swirl = ('<path d="%s" fill="%s"/>'
             % (coil(LX, LY, 24, LR * .90, 2.2, 54, start=-64, n=64),
                ACCENT))
    d.form(disc, CREAM, sweep(LX, LY, LR, LR, lo=.34, hi=-.48), CREAM_DEEP,
           ol=OL_MAIN, inner=swirl)
    # ---- face: 258 wide on the 472-wide disc = 54.7% ----
    d.add(face(492, 300, 258, mass_w=472, default="delighted", tilt=-2.5,
               eyes=((-50, -22), (54, -16)), eye_r=(21, 25),
               mouth=(0, 44), mouth_k=1.14))
    return d.svg()


# =====================================================================
# 16. m-monkey-marigold     SILLY -- has a face
#     A wide, low, double-ruffled bloom with two ear discs sticking out
#     sideways: the widest flower head in the block.
# =====================================================================
def monkey_marigold():
    d = Doc()
    HX, HY = 476, 366
    d.form(stem_slim(524, 560, BASE_Y, 74, root_seed=173.5, lean=-16,
                     w_base=206, root_lobes=3, root_depth=(16, 28)),
           GRASS, sweep(526, 826, 92, 200, lo=.06, hi=-.10, wob=.03),
           GRASS_DEEP)
    d.form(leaf_pointed(560, 830, 242, 136, 76, curl=-.14), GRASS,
           sweep(660, 782, 96, 78, lo=.24, hi=-.38), GRASS_DEEP, ol=OL_PROP)
    d.line(vein(560, 830, 242, 76, frac=.62), OL_FINE)

    # ---- the ears ----
    for (ex, ey, er, sd) in ((186, 384, 102, 3.0), (798, 350, 94, 8.0)):
        J, B = lobe_profile(sd, 10, jit=0.05, bul=(6, 12))
        d.form(canopy_blob(ex, ey, er, er * .96, 10, J, B), BARK,
               sweep(ex, ey, er, er, lo=.30, hi=-.44), BARK_DEEP, ol=OL_MAIN)
        d.form(canopy_blob(ex + 6, ey + 4, er * .58, er * .56, 9,
                           *lobe_profile(sd + 2, 9, jit=0.04, bul=(3, 6))),
               BARK_LITE, sweep(ex, ey, er * .6, er * .6, lo=.30, hi=-.44),
               BARK, ol=OL_FINE)

    # ---- two ruffled petal rings; ring 1 index 5 is a STUB: the oddity ----
    for i in range(19):
        a = -94 + 360.0 * i / 19 + (3.4 if i % 3 == 0 else -2.1)
        stub = 0.70 if i == 5 else 1.0
        d.form(petal_fan(HX, HY, a, 172, 294, 15, seed=i * 3.1, ruffle=.07,
                         stub=stub), ACCENT,
               sweep(HX, HY, 294, 280, lo=.34, hi=-.50, seed=i * .7),
               ACCENT_DEEP, ol=OL_PROP)
    for i in range(14):
        a = -80 + 360.0 * i / 14 + (2.6 if i % 2 else -3.2)
        d.form(petal_fan(HX, HY, a, 136, 226, 17, seed=i * 5.3 + 1.0,
                         ruffle=.06), SUN,
               sweep(HX, HY, 226, 214, lo=.34, hi=-.50, seed=i * .9),
               SUN_SHADE, ol=OL_FINE)

    # ---- the monkey face disc: 200 on 388 = 51.5% ----
    J, B = lobe_profile(seed=104.6, n=12, jit=0.04, bul=(8, 15))
    d.form(canopy_blob(HX - 2, HY + 4, 168, 152, 12, J, B, start=-92),
           BARK_LITE, sweep(HX, HY, 168, 152, lo=.32, hi=-.46), BARK,
           ol=OL_MAIN)
    d.form(canopy_blob(HX, HY + 46, 110, 74, 10,
                       *lobe_profile(112.8, 10, jit=0.04, bul=(5, 10))),
           CREAM, sweep(HX, HY + 46, 110, 74, lo=.32, hi=-.46), CREAM_DEEP,
           ol=OL_FINE)
    d.add(dots([(452, 400, 12), (502, 398, 11)], INK_SOFT))
    d.add(face(HX - 2, HY + 6, 178, mass_w=336, default="neutral", tilt=2.0,
               eyes=((-52, -32), (50, -36)), eye_r=(20, 23),
               mouth=(0, 60), mouth_k=0.94))
    return d.svg()


# =====================================================================
# 17. m-marshmallow-tree     WACKY -- has a face
#     Five fat soft cylinders bunched on a forked trunk.  Flat-topped
#     lozenges, not scallops: it cannot be confused with a leaf canopy.
# =====================================================================
def marshmallow_tree():
    d = Doc()
    for (x0, y0, x1, y1, w0, w1, k) in ((470, 566, 336, 402, 86, 62, 0.18),
                                        (536, 556, 690, 384, 82, 60, -0.20)):
        d.form(branch(x0, y0, x1, y1, w0, w1, k), BARK,
               sweep((x0 + x1) / 2, (y0 + y1) / 2, 100, 90, lo=.22, hi=-.30,
                     seed=x1 * .02), BARK_DEEP, ol=OL_MAIN)
    d.form(trunk_chunky(504, 430, BASE_Y, 128, 262, root_seed=182.9, lean=8,
                        root_lobes=3, root_depth=(18, 32), flare=1.06),
           BARK, sweep(520, 740, 150, 250, lo=.18, hi=-.16, wob=.06),
           BARK_DEEP,
           inner=stroked(["M428,600 C444,700 434,810 452,930",
                          "M584,626 C574,720 588,824 578,942"],
                         INK, OL_MAIN))

    # ---- five marshmallows, back rank first ----
    cylinder(d, 302, 292, 226, 180, CREAM, 1.0, deg=-11)
    cylinder(d, 710, 254, 214, 188, CREAM, 2.0, deg=13)
    cylinder(d, 494, 166, 240, 180, CREAM, 3.0, deg=-4)
    cylinder(d, 332, 468, 200, 172, CREAM, 4.0, deg=7)
    cylinder(d, 684, 442, 206, 164, CREAM, 5.0, deg=-15)
    cylinder(d, 500, 348, 320, 262, CREAM, 6.0, deg=3)
    # ---- ODDITY: one has fallen off and is sitting in the dirt, squashed ---
    cylinder(d, 812, 940, 168, 112, CREAM, 7.0, deg=-11, ol=OL_PROP)

    # ---- face on the front marshmallow: 168 on 320 = 52.5% ----
    d.add(face(498, 364, 190, mass_w=320, default="sleepy", tilt=-2.0,
               eyes=((-58, -8), (54, -14)), eye_r=(22, 25),
               mouth=(-2, 48), mouth_k=0.94, brow_lift=12))
    return d.svg()


# =====================================================================
# 18. n-norway-spruce     REALISTIC -- no face
#     Six graduated tiers of jagged skirt.  The only triangle in the set.
# =====================================================================
def _tier(cx, ytop, ybot, wtop, wbot, n, seed):
    ks = jitter(seed, 2 * n + 1, 0.13, 1.0)
    m = 2 * n + 1
    pts = [(cx - wtop * .5, ytop), (cx + wtop * .5, ytop)]
    for i in range(m):
        t = 1.0 - i / float(m - 1)
        x = cx - wbot * .5 + wbot * t
        y = (ybot + (ks[i] - 1.0) * 96) if i % 2 == 0 else \
            (ybot - (ybot - ytop) * .46 * ks[i])
        pts.append((x, y))
    return smooth_closed(pts)


def norway_spruce():
    d = Doc()
    d.form(trunk_chunky(516, 782, BASE_Y, 128, 226, root_seed=190.6, lean=-6,
                        root_lobes=3, root_depth=(18, 32), flare=1.06),
           BARK, sweep(520, 918, 118, 96, lo=.20, hi=-.18, wob=.05),
           BARK_DEEP,
           inner=stroked("M462,860 C472,908 466,952 476,986", INK, OL_MAIN))

    TIERS = [(432, 112, 258, 92, 226, 4, 3.0, GRASS),
             (452, 232, 384, 190, 366, 5, 9.0, GRASS),
             (446, 342, 500, 296, 500, 6, 15.0, GRASS_DEEP),
             (476, 452, 614, 404, 646, 7, 21.0, GRASS_DEEP),
             (486, 560, 726, 516, 782, 9, 27.0, GRASS_DEEP),
             (516, 672, 840, 616, 900, 11, 33.0, GRASS)]
    for (cx, ytop, ybot, wtop, wbot, n, sd, col) in TIERS:
        d.form(_tier(cx, ytop, ybot, wtop, wbot, n, sd), col,
               sweep(cx, (ytop + ybot) * .5, wbot * .5, (ybot - ytop) * .6,
                     lo=.24, hi=-.40, wob=.08, seed=sd), SHADE[col],
               ol=OL_MAIN)
    # the leader spike
    d.form(horn(432, 172, 118, 74, deg=-5, k=0.06), GRASS,
           sweep(432, 124, 44, 48, lo=.28, hi=-.44), GRASS_DEEP, ol=OL_PROP)
    # new-growth buds -- flat pattern marks, never outlined
    d.add(dots([(360, 300, 17), (548, 322, 15), (282, 414, 18),
                (628, 430, 16), (206, 534, 19), (726, 552, 17),
                (150, 656, 18), (838, 670, 16), (452, 396, 15),
                (390, 622, 17), (528, 512, 15), (306, 746, 18),
                (706, 764, 17)], LEAF))
    # ---- ODDITY: one cone hangs off the third tier, well off centre ----
    d.add('<path d="M842,700 C852,716 858,726 860,740" fill="none" '
          'stroke="%s" stroke-width="%d" %s/>' % (BARK_DEEP, OL_FINE, RJ))
    d.form(horn(862, 740, 110, 62, deg=176, k=0.05), BARK,
           sweep(872, 786, 36, 40, lo=.26, hi=-.42), BARK_DEEP, ol=OL_PROP,
           inner=stroked(["M828,%d L900,%d" % (y, y + 7)
                          for y in (770, 796, 822)], BARK_DEEP, OL_FINE))
    return d.svg()


# =====================================================================
# 19. n-narwhal-nettle     SILLY -- has a face
#     A round blue head with a long CREAM tusk running out of the top of
#     the frame, flippers, and serrated nettle leaves down the stem.
# =====================================================================
def narwhal_nettle():
    d = Doc()
    d.form(stem_slim(506, 590, BASE_Y, 92, root_seed=161.1, lean=8,
                     w_base=232, root_lobes=3, root_depth=(16, 28)),
           GRASS, sweep(518, 810, 100, 210, lo=.06, hi=-.10, wob=.03),
           GRASS_DEEP)
    # nettle leaves: serrated, so it is a nettle and not a daisy stem
    for (lx, ly, L, dg, sd) in ((442, 870, 144, -62, 3.0),
                                (566, 806, 138, 66, 6.0),
                                (460, 696, 126, -74, 9.0),
                                (572, 912, 128, 84, 12.0)):
        d.form(leaf_lobed(lx, ly, L, dg,
                          jit=jitter(sd, 5, 0.10, 1.0)), GRASS,
               sweep(lx, ly, L, L, lo=.28, hi=-.42, seed=sd), GRASS_DEEP,
               ol=OL_PROP)

    # ---- the tusk, drawn behind the head ----
    d.form(horn(500, 306, 250, 124, deg=5, k=0.05), CREAM,
           sweep(526, 176, 66, 122, lo=.24, hi=-.36), CREAM_DEEP, ol=OL_MAIN,
           inner=stroked(["M436,%d C486,%d 540,%d 580,%d"
                          % (y, y - 32, y - 8, y - 46)
                          for y in (262, 190, 122)], INK, OL_FINE))

    # ---- flippers ----
    for (fx, fy, L, Wd, dg, sd) in ((330, 520, 236, 132, -102, 3.0),
                                    (700, 494, 222, 122, 106, 7.0)):
        d.form(leaf_round(fx, fy, L, Wd, dg, curl=.14), SKY_HI,
               sweep(fx, fy, Wd, L * .4, lo=.26, hi=-.40, seed=sd), SKY_DEEP,
               ol=OL_PROP)

    # ---- head ----
    J, B = lobe_profile(seed=126.4, n=12, jit=0.05, bul=(12, 26))
    head = canopy_blob(508, 402, 246, 208, 12, J, B, start=-94)
    belly = canopy_blob(506, 486, 196, 118, 11,
                        *lobe_profile(133.2, 11, jit=0.04, bul=(8, 16)))
    d.form(head, SKY_HI, sweep(508, 402, 246, 208, lo=.32, hi=-.46, wob=.06),
           SKY_DEEP, ol=OL_MAIN,
           inner='<path d="%s" fill="%s"/>' % (belly, SKY_LO)
                 + stroked(belly, INK, OL_FINE))
    # ---- ODDITY: one small bubble has escaped past the tusk ----
    d.form(canopy_blob(690, 216, 44, 42, 9,
                       *lobe_profile(147.5, 9, jit=0.03, bul=(2, 4))),
           SKY_LO, sweep(690, 216, 44, 42, lo=.30, hi=-.46), SKY_HI,
           ol=OL_FINE)
    # ---- face: 248 wide on a 492-wide head = 50.4% ----
    d.add(face(504, 414, 248, mass_w=492, default="happy", tilt=1.0,
               eyes=((-56, -16), (58, -22)), eye_r=(24, 22),
               mouth=(0, 40), mouth_k=1.12))
    return d.svg()


# =====================================================================
# 20. n-noodle-nutbush     WACKY -- has a face
#     A wide, low, ragged mass of curls with one long noodle hanging clear
#     off the left side, on a narrow trunk.
# =====================================================================
def noodle_nutbush():
    d = Doc()
    # ---- the dangling noodle, drawn first so the mass covers its root ----
    for (x0, y0, x1, y1, w, amp, ph, sd) in (
            (272, 322, 176, 946, 56, 74, 0.6, 1.0),
            (742, 306, 856, 908, 52, 68, 2.2, 2.0),
            (350, 402, 288, 792, 46, 54, 4.1, 3.0),
            (668, 392, 738, 758, 44, 50, 5.3, 4.0)):
        d.form(squiggle(x0, y0, x1, y1, w, amp, waves=2.6, phase=ph),
               SUN, sweep((x0 + x1) / 2, (y0 + y1) / 2, 86, (y1 - y0) * .4,
                          lo=.24, hi=-.34, wob=.08, seed=sd),
               SUN_SHADE, ol=OL_PROP)
    d.form(trunk_chunky(506, 484, BASE_Y, 158, 300, root_seed=176.3, lean=-6,
                        root_lobes=3, root_depth=(18, 30), flare=1.04),
           BARK, sweep(520, 760, 150, 200, lo=.18, hi=-.16, wob=.06),
           BARK_DEEP,
           inner=stroked(["M428,600 C444,700 434,800 452,912",
                          "M596,624 C586,714 600,812 590,924"],
                         INK, OL_MAIN))

    # ---- the noodle mass: a very ragged wide blob ----
    J, B = lobe_profile(seed=59.8, n=22, jit=0.16, bul=(34, 86))
    mass = canopy_blob(510, 330, 336, 232, 22, J, B, start=-94)
    curls = ""
    for i in range(11):
        t = i / 10.0
        x0 = 208 + 610 * t
        curls += ('<path d="%s" fill="%s"/>'
                  % (squiggle(x0, 110 + 76 * math.sin(i * 1.7), x0 + 36,
                              560 - 54 * math.cos(i * 2.1), 42,
                              62 + 14 * (i % 3), waves=3.1, phase=i * 1.3),
                     SUN_SHADE))
    d.form(mass, SUN, sweep(510, 330, 336, 232, lo=.30, hi=-.42, wob=.10),
           SUN_SHADE, ol=OL_MAIN, inner=curls)
    # outlined curls riding the edge, so the boundary is noodles not a blob
    for (x0, y0, x1, y1, w, amp, ph) in (
            (222, 226, 268, 424, 50, 56, 0.3),
            (368, 122, 404, 268, 48, 52, 1.4),
            (628, 116, 662, 258, 48, 54, 2.6),
            (786, 236, 818, 408, 50, 58, 0.9),
            (694, 474, 740, 540, 46, 42, 2.0),
            (312, 486, 360, 552, 46, 40, 3.3)):
        d.form(squiggle(x0, y0, x1, y1, w, amp, waves=2.2, phase=ph), SUN,
               sweep((x0 + x1) / 2, (y0 + y1) / 2, 80, 120, lo=.26, hi=-.38,
                     seed=x0 * .02), SUN_SHADE, ol=OL_FINE)

    # ---- the front clump the face sits on ----
    J2, B2 = lobe_profile(seed=73.4, n=14, jit=0.12, bul=(22, 50))
    d.form(canopy_blob(492, 398, 228, 152, 14, J2, B2, start=-92), SUN,
           sweep(492, 398, 228, 152, lo=.32, hi=-.44, wob=.10), SUN_SHADE,
           ol=OL_MAIN)
    # ---- ODDITY: one stray curl has flicked up above the whole bush ----
    d.form(squiggle(560, 176, 644, 78, 42, 46, waves=1.9, phase=1.1), SUN,
           sweep(602, 126, 66, 72, lo=.26, hi=-.40), SUN_SHADE, ol=OL_FINE)
    # ---- face: 232 wide on the 456-wide front clump = 50.9% ----
    d.add(face(488, 408, 232, mass_w=456, default="delighted", tilt=-2.0,
               eyes=((-52, -20), (50, -14)), eye_r=(19, 24),
               mouth=(0, 44), mouth_k=1.0))
    return d.svg()


# =====================================================================
# 21. o-orange-tree     REALISTIC -- no face
#     TWO canopy lobes with a deep V between them, on a splayed twin
#     trunk.  Deliberately not the apple tree's closed dome.
# =====================================================================
def orange_tree():
    d = Doc()
    for (cx, top, base, wt, wb, sd, lean, fl) in (
            (368, 552, BASE_Y, 124, 216, 213.7, -30, 1.18),
            (652, 540, BASE_Y, 118, 206, 227.4, 32, 1.14)):
        d.form(trunk_chunky(cx, top, base, wt, wb, root_seed=sd, lean=lean,
                            root_lobes=3, root_depth=(18, 30), flare=fl),
               BARK, sweep(cx + 14, 820, 130, 190, lo=.18, hi=-.16, wob=.06),
               BARK_DEEP,
               inner=stroked("M%d,%d C%d,%d %d,%d %d,%d"
                             % (cx - 40, 640, cx - 52, 730, cx - 44, 830,
                                cx - 56, 946), INK, OL_MAIN))
    d.form(branch(444, 596, 330, 480, 88, 60, 0.20), BARK,
           sweep(388, 538, 84, 74, lo=.22, hi=-.30), BARK_DEEP, ol=OL_MAIN)
    d.form(branch(578, 588, 690, 470, 86, 58, -0.22), BARK,
           sweep(634, 528, 82, 72, lo=.22, hi=-.30), BARK_DEEP, ol=OL_MAIN)

    # ---- two lobes and a low collar; the V between them is the point ----
    for (cx, cy, rx, ry, col, n, st, notch, sd) in (
            (306, 348, 194, 182, GRASS, 11, -104, None, 8.3),
            (706, 318, 198, 188, GRASS, 11, -82, 5, 16.7),
            (330, 528, 156, 120, LEAF, 10, -96, None, 25.1),
            (682, 508, 160, 122, LEAF, 10, -88, None, 33.6),
            (504, 528, 176, 128, GRASS, 11, -92, None, 42.2)):
        J, B = lobe_profile(sd, n, jit=0.08, bul=(30, 68))
        d.form(canopy_blob(cx, cy, rx, ry, n, J, B, start=st, notch=notch),
               col, sweep(cx, cy, rx, ry, lo=.30, hi=-.42, wob=.09,
                          seed=cx * .012), SHADE[col])
    for (mx, my, L, Wd, dg, col) in ((214, 312, 74, 44, -30, GRASS_DEEP),
                                     (326, 246, 70, 42, 14, GRASS_DEEP),
                                     (686, 214, 72, 42, -20, GRASS_DEEP),
                                     (824, 296, 72, 42, 26, GRASS_DARK),
                                     (288, 494, 68, 40, 36, GRASS_DARK),
                                     (742, 476, 70, 40, -28, GRASS_DARK),
                                     (494, 524, 64, 38, 10, GRASS_DEEP),
                                     (554, 606, 62, 36, -12, GRASS_DEEP)):
        d.fill(leaf_round(mx, my, L, Wd, dg), col)

    # ---- the oranges ----
    for (ax, ay, r, dg) in ((228, 366, 64, -8), (356, 274, 60, 6),
                            (652, 248, 62, -12), (784, 336, 58, 10),
                            (330, 528, 56, 4), (688, 512, 54, -6)):
        d.form(fruit_blob(ax, ay, r, dg), ACCENT,
               sweep(ax, ay, r, r, lo=.30, hi=-.46), ACCENT_DEEP, ol=OL_PROP,
               inner='<path d="%s" fill="%s" opacity="0.8"/>'
                     % (chip(ax - r * .40, ay - r * .42, r * .28), CREAM))
        d.fill(leaf_round(ax + 20, ay - r * 1.02, 46, 30, 58), GRASS_DEEP)
    # ---- ODDITY: one orange has dropped and is lying in the dirt ----
    d.form(fruit_blob(846, 930, 62, 28), ACCENT,
           sweep(846, 930, 62, 62, lo=.30, hi=-.46), ACCENT_DEEP, ol=OL_PROP)
    d.fill(leaf_round(808, 900, 46, 30, -34), GRASS_DEEP)
    return d.svg()


# =====================================================================
# 22. o-owl-orchid     SILLY -- has a face
#     Orchid petals arranged into an owl: two huge cream eye discs, a
#     beak, ear tufts, and a bare grey stem.
# =====================================================================
def owl_orchid():
    d = Doc()
    # ---- the grey stem ----
    d.form(stem_slim(510, 668, BASE_Y, 68, root_seed=205.9, lean=14,
                     w_base=196, root_lobes=3, root_depth=(16, 28)),
           STEEL, sweep(522, 800, 88, 226, lo=.08, hi=-.12, wob=.03),
           STEEL_DEEP)
    d.form(leaf_pointed(534, 832, 264, 140, 78, curl=-.14), STEEL,
           sweep(646, 784, 100, 82, lo=.24, hi=-.36), STEEL_DEEP, ol=OL_PROP)
    d.line(vein(534, 832, 264, 78, frac=.64), OL_FINE, STEEL_DARK)

    # ---- petals: two ear tufts up, two wings out, two lobes down ----
    PET = [(-32, 392, 166, 2.0, 1.00), (26, 404, 172, 7.0, 0.78),
           (-88, 322, 186, 12.0, 1.00), (84, 316, 182, 17.0, 1.00),
           (-136, 258, 172, 22.0, 1.00), (132, 252, 166, 27.0, 1.00)]
    for (dg, L, Wd, sd, k) in PET:      # k<1 on tuft 2 == the ODDITY
        a = math.radians(dg)
        bx = 502 + 60 * math.sin(a)
        by = 496 - 46 * math.cos(a)
        d.form(leaf_pointed(bx, by, L * k, Wd, dg, curl=.10), BERRY,
               sweep(bx + L * .3 * math.sin(a), by - L * .42 * math.cos(a),
                     Wd * .8, L * .34, lo=.30, hi=-.44, seed=sd),
               BERRY_DEEP, ol=OL_MAIN)

    # ---- the face disc ----
    J, B = lobe_profile(seed=99.3, n=12, jit=0.05, bul=(10, 20))
    d.form(canopy_blob(500, 494, 188, 172, 12, J, B, start=-92), BERRY,
           sweep(500, 494, 188, 172, lo=.32, hi=-.46), BERRY_DEEP, ol=OL_MAIN)
    # the two big owl eye discs the rig's pupils sit inside
    for (ex, ey, er, sd) in ((436, 468, 82, 4.0), (566, 460, 79, 9.0)):
        d.form(canopy_blob(ex, ey, er, er * .98, 10,
                           *lobe_profile(sd, 10, jit=0.03, bul=(4, 8))),
               CREAM, sweep(ex, ey, er, er, lo=.34, hi=-.48), CREAM_DEEP,
               ol=OL_PROP)
    # the beak
    d.form(horn(502, 542, 86, 70, deg=178, k=0.04), ACCENT,
           sweep(508, 586, 30, 36, lo=.26, hi=-.42), ACCENT_DEEP, ol=OL_PROP)
    # ---- face: 322 wide on the 664-wide bloom = 48.5% ----
    d.add(face(502, 482, 322, mass_w=664, default="surprised", tilt=-1.0,
               eyes=((-40, -9), (40, -14)), eye_r=(21, 22),
               mouth=(2, 78), mouth_k=0.62, brow_lift=14, with_blush=False))
    return d.svg()


# =====================================================================
# 23. o-octopus-oakleaf     WACKY -- has a face.  Must be instantly funny.
#     A coral octopus sitting on an oak stem, eight tentacles going eight
#     different ways -- and one of them tied in a knot.
# =====================================================================
def octopus_oakleaf():
    d = Doc()
    # ---- stem + oak leaves ----
    d.form(stem_slim(504, 560, BASE_Y, 104, root_seed=219.3, lean=-12,
                     w_base=248, root_lobes=3, root_depth=(16, 28)),
           GRASS, sweep(516, 790, 104, 230, lo=.06, hi=-.10, wob=.03),
           GRASS_DEEP)
    for (lx, ly, L, dg, sd) in ((350, 812, 176, -58, 3.0),
                                (676, 780, 168, 62, 8.0),
                                (414, 886, 118, -84, 13.0)):
        d.add('<path d="M%d,%d L%.0f,%.0f" fill="none" stroke="%s" '
              'stroke-width="%d" %s/>'
              % (504, ly + 20, lx, ly, GRASS_DEEP, OL_PROP, RJ))
        d.form(leaf_lobed(lx, ly, L, dg, jit=jitter(sd, 5, 0.09, 1.0)),
               GRASS, sweep(lx, ly, L, L, lo=.28, hi=-.42, seed=sd),
               GRASS_DEEP, ol=OL_PROP)

    # ---- eight tentacles, all different ----
    TENT = [(-94, 274, 84, 0.42, 2.0), (-118, 352, 88, -0.46, 7.0),
            (-144, 382, 84, 0.54, 12.0), (-168, 358, 80, -0.44, 17.0),
            (168, 350, 78, 0.46, 22.0), (146, 366, 86, -0.56, 27.0),
            (98, 276, 82, 0.48, 32.0)]
    for (dg, L, w, arc, sd) in TENT:
        a = math.radians(dg - 90.0)
        bx = 506 + 178 * math.sin(math.radians(dg))
        by = 404 - 148 * math.cos(math.radians(dg))
        pth = crescent(bx, by, L, w, dg, arc=arc, waist=.44)
        d.form(pth, EMBER, sweep(bx + L * .4 * math.cos(a),
                                 by + L * .4 * math.sin(a), L * .4, w,
                                 lo=.28, hi=-.42, seed=sd), EMBER_DEEP,
               ol=OL_MAIN)
        sp = bow(bx, by, bx + L * math.cos(a), by + L * math.sin(a), arc, 6)
        d.add(dots([(p[0], p[1], 16 - i * 1.6) for i, p in enumerate(sp[1:5])],
                   ACCENT))
    # ---- ODDITY: the eighth tentacle is tied in a knot ----
    d.form(coil(838, 656, 26, 100, 1.55, 70, start=150, n=48), EMBER,
           sweep(838, 656, 100, 100, lo=.28, hi=-.42, seed=41.0), EMBER_DEEP,
           ol=OL_MAIN)

    # ---- the head ----
    J, B = lobe_profile(seed=83.6, n=13, jit=0.05, bul=(14, 28))
    d.form(canopy_blob(506, 314, 236, 208, 13, J, B, start=-94), EMBER,
           sweep(506, 314, 236, 208, lo=.32, hi=-.46, wob=.06), EMBER_DEEP,
           ol=OL_MAIN,
           inner='<path d="%s" fill="%s" opacity="0.75"/>'
                 % (chip(408, 206, 58), ACCENT))
    # ---- face: 244 wide on a 472-wide head = 51.7% ----
    d.add(face(500, 326, 244, mass_w=472, default="delighted", tilt=3.0,
               eyes=((-54, -24), (52, -18)), eye_r=(22, 26),
               mouth=(-2, 46), mouth_k=1.08))
    return d.svg()


# =====================================================================
PLANTS = [
    ("h-hibiscus", hibiscus),
    ("h-hedgehog-herb", hedgehog_herb),
    ("h-hotdog-hedge", hotdog_hedge),
    ("i-iris", iris),
    ("i-inchworm-ivy", inchworm_ivy),
    ("i-icecream-iris", icecream_iris),
    ("j-jasmine", jasmine),
    ("j-jaguar-jade", jaguar_jade),
    ("j-jellybean-jungle", jellybean_jungle),
    ("k-kale", kale),
    ("k-kangaroo-kelp", kangaroo_kelp),
    ("k-ketchup-cactus", ketchup_cactus),
    ("l-lavender", lavender),
    ("l-ladybug-lettuce", ladybug_lettuce),
    ("l-lollipop-lily", lollipop_lily),
    ("m-monkey-marigold", monkey_marigold),
    ("m-marshmallow-tree", marshmallow_tree),
    ("n-norway-spruce", norway_spruce),
    ("n-narwhal-nettle", narwhal_nettle),
    ("n-noodle-nutbush", noodle_nutbush),
    ("o-orange-tree", orange_tree),
    ("o-owl-orchid", owl_orchid),
    ("o-octopus-oakleaf", octopus_oakleaf),
]

if __name__ == "__main__":
    want = sys.argv[1:]
    for name, fn in PLANTS:
        if want and name not in want:
            continue
        svg = fn()
        with open(os.path.join(OUT, name + ".svg"), "w") as fh:
            fh.write(svg.strip() + "\n")
        ok = render(name, svg, W, H, os.path.join(OUT, name + ".png"))
        print("%-20s %s" % (name, "OK" if ok else "FAIL"))
