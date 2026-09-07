#!/usr/bin/env python3
"""Build the flat-vector plants (+ the kit reference sheet).

    python3 art/flat/plants/_build_plants.py            # all
    python3 art/flat/plants/_build_plants.py s-sunflower

Everything is authored from `_kit.py`.  The rasteriser is reused verbatim
from `../_build_flat.py` (2x headless-Chrome screenshot -> LANCZOS to 1x).

Shipped set: six pilots (m-maple-tree re-authored with a real branching
structure, b-butterfly-bush re-massed) plus three stress-test plants chosen
to break a foliage kit -- r-robot-rosebush, x-xylophone-tree, b-banana-tree.
Every pair must measure silhouette IoU < 0.70 at 128px; `_verify.py` fails
the build otherwise.
"""
import os
import sys
import math
import importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _kit import *                                            # noqa: F401,F403

# --- rasteriser: reuse ../_build_flat.py's `render` when it is available,
# otherwise fall back to an identical local copy.
# ---------------------------------------------------------------------
TMP = os.path.join(HERE, "..", ".render-tmp")


def _render_local(name, svg, w, h, out_png, scale=2):
    """SVG -> HTML -> headless-Chrome screenshot at 2x -> LANCZOS to 1x."""
    import subprocess
    from PIL import Image
    chrome = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    os.makedirs(TMP, exist_ok=True)
    html = os.path.join(TMP, name + ".html")
    with open(html, "w") as fh:
        fh.write('<!doctype html><meta charset="utf-8"><style>'
                 'html,body{margin:0;padding:0;background:transparent;}'
                 'svg{display:block;}</style>' + svg)
    big = out_png + ".2x.png"
    r = subprocess.run([
        chrome, "--headless", "--disable-gpu", "--hide-scrollbars",
        "--force-device-scale-factor=%d" % scale,
        "--default-background-color=00000000",
        "--window-size=%d,%d" % (w, h), "--screenshot=" + big,
        "file://" + html], capture_output=True, text=True)
    if not os.path.exists(big):
        print(r.stderr[-800:])
        return False
    im = Image.open(big).convert("RGBA").resize((w, h), Image.LANCZOS)
    im.save(out_png)
    os.remove(big)
    return True


try:
    _spec = importlib.util.spec_from_file_location(
        "_build_flat_shared", os.path.join(HERE, "..", "_build_flat.py"))
    _bf = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(_bf)
    render = _bf.render                 # render(name, svg, w, h, out_png, 2)
except Exception as _e:                 # noqa: BLE001 - any breakage at all
    print("note: ../_build_flat.py unusable (%s); using local rasteriser" % _e)
    render = _render_local

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

    LEN_JIT = [1.00, .95, 1.04, .97, 1.02, .93, 1.05, .70, 1.01, .96,
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
    LB += " " + bite(343, 762, 30)              # ODDITY: caterpillar nibble
    d.form(LB, GRASS, sweep(368, 786, 165, 132, lo=.20, hi=-.34),
           GRASS_DEEP, ol=OL_MAIN, evenodd=True)
    d.line("M470,868 C428,820 380,776 330,738", OL_MAIN)
    RB = leaf_pointed(544, 838, 272, 164, deg=57, curl=-.16)
    d.form(RB, GRASS, sweep(662, 748, 150, 122, lo=.18, hi=-.36), GRASS_DEEP)
    d.line("M552,828 C596,784 640,746 688,712", OL_MAIN)

    # ---- stem ----   its own root seed; no two plants share a foot
    d.form(stem_slim(498, 596, BASE_Y, 62, root_seed=11.3, lean=16,
                     w_base=172, root_lobes=3, root_depth=(18, 32)),
           GRASS, sweep(510, 800, 90, 210, lo=.05, hi=-.10, wob=.03),
           GRASS_DEEP)

    # ---- petal rings ----
    cid = d._cid()
    d.defs.append('<clipPath id="%s">%s/></clipPath>'
                  % (cid, "/>".join(back)))
    d.add("".join('%s fill="%s"/>' % (p, SUN_SHADE) for p in back))
    d.add('<g clip-path="url(#%s)"><path d="%s" fill="%s"/></g>'
          % (cid, sweep(HX, HY, 300, 280, lo=.30, hi=-.40), RAY_SHADE))
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
    J, B = lobe_profile(seed=7.4, n=11, jit=0.012, bul=(6, 11))
    disc = canopy_blob(HX, HY + 2, 136, 128, 11, J, B)
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
#    THE dome.  It is the reference silhouette every other tree in the set
#    has to measure < 0.70 IoU against.
# =====================================================================
def apple_tree():
    d = Doc()
    d.form(trunk_chunky(508, 380, BASE_Y, 178, 334, root_seed=2.6, lean=8,
                        root_lobes=3, root_depth=(18, 30)),
           SOIL, sweep(524, 760, 168, 250, lo=.18, hi=-.14, wob=.06),
           SOIL_DEEP,
           inner=('<path d="M424,560 C440,660 430,760 448,900" fill="none" '
                  'stroke="%s" stroke-width="%d" %s/>'
                  '<path d="M604,600 C592,700 606,798 596,916" fill="none" '
                  'stroke="%s" stroke-width="%d" %s/>'
                  % (INK, OL_MAIN, RJ, INK, OL_MAIN, RJ)))

    # ---- canopy: 6 clumps, back to front, alternating the two greens ----
    # every clump gets its OWN lobe profile from its own seed
    CL = [(256, 428, 196, 156, GRASS, 9, -102, None, 3.1),
          (794, 444, 202, 160, GRASS, 9, -84, None, 5.7),
          (512, 246, 222, 164, LEAF, 10, -95, None, 9.2),
          (704, 568, 206, 158, GRASS, 9, -110, 4, 12.8),
          (318, 550, 214, 164, LEAF, 9, -88, None, 15.4),
          (516, 430, 244, 188, LEAF, 11, -97, None, 18.9)]
    for (cx, cy, rx, ry, col, n, st, notch, sd) in CL:
        J, B = lobe_profile(sd, n, jit=0.07, bul=(34, 72))
        d.form(canopy_blob(cx, cy, rx, ry, n, J, B, start=st, notch=notch),
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
        d.fill(leaf_round(mx, my, L, Wd, dg), col)

    # ---- apples ----
    AP = [(254, 448, 80, -6, False), (498, 280, 86, 5, False),
          (708, 410, 76, 9, False), (348, 592, 82, -11, True),
          (716, 622, 70, 4, False)]
    for (ax, ay, r, dg, bitten) in AP:
        p = fruit_blob(ax, ay, r, dg)
        eo = False
        if bitten:                                   # ODDITY: a bitten apple
            p += " " + bite(ax + r * .32, ay - r * .04, r * .32)
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
        d.fill(leaf_round(ax + 24, ay - r * 1.24, 52, 34, 62), GRASS_DEEP)
    return d.svg()


# =====================================================================
# 3. m-maple-tree   realistic, NO face   *** RE-AUTHORED ***
#
# v1 was the apple canopy on the apple trunk on the apple foot in autumn
# colours: measured IoU 0.929 against apple.  v2 is built the other way
# round -- the STRUCTURE is the subject.  A short trunk forks at y~690 into
# four real tapered limbs (`branch`), each limb carries its own small,
# separated foliage plume, and the sky shows through between them.  The
# silhouette is a wide airy candelabra with three deep notches in its top
# edge; apple's is a closed dome.  That is a different tree, not a recolour.
# =====================================================================
def maple_tree():
    d = Doc()

    # ---- limbs FIRST, so the trunk paints over their inner ends ----
    LIMBS = [(472, 764, 210, 442, 104, 54, 0.18),
             (492, 738, 336, 296, 96, 50, -0.12),
             (534, 736, 636, 282, 92, 46, 0.11),
             (548, 752, 780, 400, 88, 44, -0.17),
             (562, 792, 872, 588, 78, 40, -0.22)]
    for (x0, y0, x1, y1, w0, w1, k) in LIMBS:
        d.form(branch(x0, y0, x1, y1, w0, w1, k),
               SOIL, sweep((x0 + x1) / 2, (y0 + y1) / 2, 120, 120,
                           lo=.24, hi=-.30, seed=x1 * .02),
               SOIL_DEEP, ol=OL_MAIN)

    # ---- a SHORT trunk: the tree's mass is in the limbs, not the column --
    # trunk runs UP into the middle plume so it has no visible flat top
    d.form(trunk_chunky(512, 500, BASE_Y, 118, 300, root_seed=27.5, lean=-14,
                        root_lobes=3, root_depth=(20, 34), flare=1.08),
           SOIL, sweep(516, 850, 150, 170, lo=.14, hi=-.18, wob=.05),
           SOIL_DEEP,
           inner=('<path d="M436,760 C450,830 442,890 456,948" fill="none" '
                  'stroke="%s" stroke-width="%d" %s/>'
                  '<path d="M584,772 C574,844 588,896 578,952" fill="none" '
                  'stroke="%s" stroke-width="%d" %s/>'
                  % (INK, OL_MAIN, RJ, INK, OL_MAIN, RJ)))

    # ---- five SEPARATE plumes, one per limb tip + a small binding clump ----
    # deliberately unequal, deliberately not touching in the middle
    CL = [(176, 404, 116, 100, EMBER, 9, -104, None, 31.2),
          (312, 232, 122, 104, ACCENT, 9, -92, None, 44.6),
          (652, 214, 122, 106, ACCENT, 10, -86, 4, 57.1),
          (790, 358, 116, 98, SUN, 9, -112, None, 69.8),
          (890, 596, 94, 84, EMBER, 8, -96, None, 82.3)]
    for (cx, cy, rx, ry, col, n, st, notch, sd) in CL:
        J, B = lobe_profile(sd, n, jit=0.12, bul=(16, 40))
        d.form(canopy_blob(cx, cy, rx, ry, n, J, B, start=st, notch=notch),
               col, sweep(cx, cy, rx, ry, lo=.30, hi=-.42, seed=cx * .013))

    # a small collar clump over the trunk top so it has no visible flat edge
    J, B = lobe_profile(95.4, 8, jit=0.09, bul=(14, 34))
    d.form(canopy_blob(472, 452, 92, 76, 8, J, B, start=-98), SUN,
           sweep(472, 452, 92, 76, lo=.30, hi=-.42, seed=3.3))

    # ---- the maple leaves: the identity of this asset ----
    LV = [(158, 366, 70, 14, FRUIT), (280, 190, 74, -20, EMBER),
          (218, 442, 64, 28, SUN), (626, 170, 76, -10, FRUIT),
          (352, 268, 68, 18, SUN), (690, 256, 66, -24, SUN),
          (762, 318, 68, 10, FRUIT), (816, 402, 62, -30, EMBER),
          (898, 560, 60, 6, SUN), (462, 442, 58, 22, EMBER),
          (246, 952, 64, 152, FRUIT)]       # ODDITY: one leaf has fallen
    for (lx, ly, L, dg, col) in LV:
        px = lx + L * .52 * math.sin(math.radians(dg))
        py = ly + L * .52 * math.cos(math.radians(dg))
        d.add('<path d="M%.0f,%.0f L%.0f,%.0f" fill="none" stroke="%s" '
              'stroke-width="%d" %s/>'
              % (lx, ly, px, py, SOIL_DEEP, OL_FINE, RJ))
        d.form(leaf_lobed(lx, ly, L, dg,
                          jit=jitter(lx * .01, 5, 0.07, 1.0)), col,
               sweep(lx, ly, L, L, lo=.30, hi=-.44, wob=.10, seed=lx * .02),
               ol=OL_PROP)
    return d.svg()


# =====================================================================
# 4. b-butterfly-bush   silly, HAS a face + two butterflies
#    RE-MASSED: v1 was a stemmed dome and measured 0.777 IoU against apple.
#    A bush is not a small tree -- this one is a LOW WIDE MOUND that sits in
#    the dirt, with the butterflies carrying the height instead.
# =====================================================================
def _butterfly(d, cx, cy, span, low_col, deg=0.0, fold=1.0):
    """Wings STEEL up / accent low, fat ink body, ball-tipped antennae."""
    s = span / 260.0

    def P(pts):
        return place(pts, cx, cy, deg, s)
    uw_l = smooth_closed(P([(-14, -18), (-64, -96), (-124, -84), (-134, -20),
                            (-96, 22), (-38, 16)]))
    uw_r = smooth_closed(P([(14, -20), (66, -100), (128, -86), (136, -22),
                            (98, 20), (40, 14)]))
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
    for (px, py, pr) in ((-88, -44, 17), (-52, -14, 12), (92, -48, 16),
                         (58, -16, 11)):
        q = P([(px, py)])[0]
        d.add('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s"/>'
              % (q[0], q[1], pr * s, CREAM))
    body = smooth_closed(P([(0, -86), (17, -50), (20, 6), (14, 66),
                            (0, 100), (-14, 66), (-20, 6), (-17, -50)]))
    d.form(body, INK_SOFT, None, None, ol=olw)
    hq = P([(0, -96)])[0]
    # antennae at 15*s (>= the 11px floor even on the smaller butterfly);
    # a 7px antenna ghosted out at 128px -- that bug is why OL_FINE is 11.
    for (ax, ay, bx, by, tx, ty) in ((-6, -100, -34, -140, -46, -158),
                                     (6, -100, 30, -142, 44, -158)):
        a, b, t = P([(ax, ay)])[0], P([(bx, by)])[0], P([(tx, ty)])[0]
        d.add('<path d="M%.1f,%.1f Q%.1f,%.1f %.1f,%.1f" fill="none" '
              'stroke="%s" stroke-width="%.1f" %s/>'
              % (a[0], a[1], b[0], b[1], t[0], t[1], INK_SOFT,
                 max(OL_FLOOR, 15 * s), RJ))
        d.add('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s"/>'
              % (t[0], t[1], 16 * s, INK_SOFT))
    d.add('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s"/>'
          % (hq[0], hq[1], 26 * s, INK_SOFT))


def butterfly_bush():
    d = Doc()
    # ---- a short WOODY base; the mound sits on it, not on a stalk ----
    d.form(stem_slim(508, 838, BASE_Y, 116, root_seed=53.9, lean=-8,
                     w_base=252, root_lobes=3, root_depth=(12, 22)),
           GRASS_DEEP, sweep(518, 930, 120, 90, lo=.08, hi=-.12, wob=.03),
           GRASS_DARK)

    # ---- the mound: wide and LOW.  Nothing above y=470. ----
    for (cx, cy, rx, ry, col, n, st, notch, sd) in (
            (232, 772, 176, 144, GRASS, 10, -104, None, 91.4),
            (798, 758, 178, 148, GRASS, 10, -80, None, 104.7),
            (340, 634, 194, 142, GRASS, 11, -96, 5, 118.2),
            (700, 618, 200, 146, GRASS, 11, -88, None, 131.6)):
        J, B = lobe_profile(sd, n, jit=0.09, bul=(26, 62))
        d.form(canopy_blob(cx, cy, rx, ry, n, J, B, start=st, notch=notch),
               col, sweep(cx, cy, rx, ry, lo=.32, hi=-.44, wob=.09,
                          seed=cx * .011))
    # front clump wears the face; internal contour lines do the form work
    seams = "".join(
        '<path d="%s" fill="none" stroke="%s" stroke-width="%d" %s/>' % (
            sd, INK, OL_MAIN, RJ)
        for sd in ("M280,676 C338,714 350,788 306,852",
                   "M742,688 C696,730 700,794 744,834",
                   "M386,892 C430,866 448,826 442,782",
                   "M646,898 C604,872 588,832 596,790"))
    J, B = lobe_profile(146.9, 13, jit=0.08, bul=(28, 70))
    d.form(canopy_blob(508, 712, 288, 208, 13, J, B, start=-94), LEAF,
           sweep(508, 712, 288, 208, lo=.32, hi=-.44, wob=.09, seed=5.1),
           inner=seams)

    # ---- leaf marks; one of them is nibbled: THE ODDITY ----
    for (mx, my, L, Wd, dg, col, nib) in (
            (152, 694, 94, 56, -30, GRASS_DEEP, False),
            (300, 574, 88, 50, 18, GRASS_DEEP, False),
            (470, 540, 92, 54, -12, GRASS_DEEP, False),
            (660, 548, 84, 48, 28, GRASS_DEEP, False),
            (908, 694, 90, 52, -20, GRASS_DEEP, False),
            (826, 852, 86, 50, 34, GRASS_DEEP, True),
            (240, 866, 88, 52, -36, GRASS_DEEP, False),
            (596, 906, 78, 46, 10, GRASS_DEEP, False)):
        p = leaf_round(mx, my, L, Wd, dg)
        if nib:
            p += " " + bite(859, 820, 13)
        d.fill(p, col, evenodd=nib)

    # two prop leaves on the flanks of the woody base, in FRONT of the mound
    d.form(leaf_pointed(322, 972, 196, 116, deg=-68, curl=.2), GRASS,
           sweep(246, 918, 96, 78, lo=.24, hi=-.30), GRASS_DEEP, ol=OL_PROP)
    d.form(leaf_pointed(694, 962, 184, 108, deg=64, curl=-.2), GRASS,
           sweep(772, 912, 92, 74, lo=.20, hi=-.34), GRASS_DEEP, ol=OL_PROP)

    # ---- the face: 264 wide on a 576-wide front clump = 45.8% ----
    d.add(face(500, 728, 264, mass_w=576, default="happy", tilt=-2.0,
               eyes=((-50, -12), (52, -17)), eye_r=(20, 27),
               mouth=(3, 46)))

    # ---- butterflies carry the height ----
    _butterfly(d, 254, 268, 292, SUN, deg=-14, fold=0.78)
    _butterfly(d, 796, 342, 268, SKY_HI, deg=16)
    return d.svg()


# =====================================================================
# 5. p-pizza-palm   wacky, HAS a face; grows pizza slices
# =====================================================================
def pizza_palm():
    d = Doc()
    HX, HY = 512, 450
    R0, R1, R2 = 150, 330, 400
    ANG = [-86, -44, -2, 41, 83]
    HA = [17.0, 18.0, 16.5, 17.5, 16.0]      # < half the 43 deg pitch -> gaps
    LENK = [0.94, 1.02, 1.00, 0.97, 0.92]

    def polar(r, deg):
        a = math.radians(deg)
        return (HX + r * math.sin(a), HY - r * math.cos(a))

    # ---- trunk first, behind the slices ----
    rings = trunk_palm(512, 432, BASE_Y, 74, 172, n=7)
    for i, (pth, hw, cy) in enumerate(rings):
        d.form(pth, BARK_LITE,
               sweep(512, cy, hw, hw * .40, lo=.26, hi=-.40, seed=i * 1.7),
               SOIL, ol=OL_MAIN)

    # ---- five slices ----
    for i, base_a in enumerate(ANG):
        ha, k = HA[i], LENK[i]
        r1, r2 = R1 * k, R2 * k

        def arc(r, f, base_a=base_a, ha=ha):
            return [polar(r, base_a + ha * (2 * t / 4.0 - 1) * f)
                    for t in range(5)]
        crust = smooth_closed(
            arc(r1 - 6, 1.0) + [polar(r2 * 1.0, base_a + ha * 1.02)]
            + list(reversed(arc(r2, 1.03)))
            + [polar(r2 * 0.99, base_a - ha * 1.02)])
        d.form(crust, ACCENT,
               sweep(HX, HY, 300, 300, lo=.30, hi=-.44), ACCENT_DEEP,
               ol=OL_MAIN)
        cheese = smooth_closed(
            [polar(R0 * .92, base_a - ha * .80),
             polar(R0 + (r1 - R0) * .45, base_a - ha * .96)]
            + arc(r1 + 6, 0.99)
            + [polar(R0 + (r1 - R0) * .45, base_a + ha * .96),
               polar(R0 * .92, base_a + ha * .80)])
        d.form(cheese, SUN, sweep(HX, HY, 300, 300, lo=.32, hi=-.46),
               SUN_SHADE, ol=OL_MAIN)
        for j, (rr, off, pr) in enumerate(((0.38, -0.46, 34), (0.64, 0.44, 31),
                                           (0.87, -0.20, 35))):
            px, py = polar(R0 + (r1 - R0) * rr, base_a + ha * off)
            if i == 1 and j == 2:            # ODDITY: one crooked pepperoni
                px, py = polar(r1 * 1.10, base_a + ha * .74)
            J, B = lobe_profile(px * .01 + i, 8, jit=0.018, bul=(2, 4))
            d.form(canopy_blob(px, py, pr, pr * .94, 8, J, B),
                   FRUIT, sweep(px, py, pr, pr, lo=.28, hi=-.48),
                   FRUIT_DEEP, ol=OL_FINE)

    # ---- the face hub: 304 wide, face 160 = 52.6% ----
    J, B = lobe_profile(23.8, 10, jit=0.014, bul=(5, 8))
    hub = canopy_blob(HX, HY - 4, 152, 146, 10, J, B)
    d.form(hub, SUN, sweep(HX, HY, 152, 146, lo=.34, hi=-.46), SUN_SHADE,
           ol=OL_MAIN)
    d.add(face(HX - 4, HY - 2, 160, mass_w=304, default="delighted",
               tilt=-3.0, eyes=((-44, -16), (46, -20)), eye_r=(18, 25),
               mouth=(2, 46)))
    return d.svg()


# =====================================================================
# 6. u-ufo-tree   wacky, HAS a face; saucers + tractor beam
# =====================================================================
def _saucer(d, cx, cy, rx, ry, dome_k=1.5, flip=False, alien=False, deg=0.0,
            seed=0.0):
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
                     cx + sx * ar * .64, ay - ar * 1.16, INK,
                     max(OL_FLOOR, ar * .30), RJ,
                     cx + sx * ar * .64, ay - ar * 1.18, ar * .22, GRASS,
                     INK, OL_FINE, RJ))
        J, B = lobe_profile(seed + 1.5, 9, jit=0.03, bul=(3, 6))
        ah = canopy_blob(cx - 5, ay, ar, ar * .90, 9, J, B)
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
                 cx + ar * .36, ay + ar * .36, INK_SOFT,
                 max(OL_FLOOR, ar * .17), RJ))
    d.form(hull, STEEL, sweep(cx, cy, rx, ry * 1.4, lo=.22, hi=-.40),
           STEEL_DEEP, ol=ol)
    lights = (SUN, ACCENT, LEAF, SUN, ACCENT)
    n = 5 if rx > 160 else 3
    for i in range(n):
        t = (i + .5) / n
        lx = cx - rx * .72 + rx * 1.44 * t
        ly = cy + (ry * .58) * f + (4 if i % 2 else -3)
        lr = rx * .10
        J, B = lobe_profile(seed + i, 7, jit=0.015, bul=(1, 2))
        d.form(canopy_blob(lx, ly, lr, lr * .95, 7, J, B),
               lights[i % 5], None, None, ol=OL_FINE)


def ufo_tree():
    d = Doc()
    beam = smooth_closed([(464, 262), (564, 262), (726, 536), (316, 536)])
    d.form(beam, BEAM, sweep(516, 404, 204, 150, lo=.06, hi=-.36), SUN,
           ol=OL_BG, stroke=SUN_DEEP)
    d.form(leaf_round(448, 366, 126, 88, deg=38), GRASS,
           sweep(458, 320, 62, 56, lo=.24, hi=-.42), GRASS_DEEP, ol=OL_PROP)
    d.line(vein(448, 366, 126, 38), OL_FINE)

    d.form(trunk_chunky(504, 680, BASE_Y, 156, 306, root_seed=38.4, lean=6,
                        root_lobes=3, root_depth=(16, 28)),
           SOIL, sweep(518, 860, 150, 170, lo=.18, hi=-.14, wob=.06),
           SOIL_DEEP,
           inner=('<path d="M424,740 C440,812 430,872 448,940" fill="none" '
                  'stroke="%s" stroke-width="%d" %s/>'
                  '<path d="M598,762 C588,830 602,882 592,944" fill="none" '
                  'stroke="%s" stroke-width="%d" %s/>'
                  % (INK, OL_MAIN, RJ, INK, OL_MAIN, RJ)))

    for (cx, cy, rx, ry, col, n, st, notch, sd) in (
            (276, 634, 184, 140, GRASS, 9, -102, None, 61.3),
            (746, 624, 180, 138, GRASS, 9, -84, 3, 74.8),
            (508, 582, 204, 138, LEAF, 10, -96, None, 88.1),
            (496, 668, 254, 156, LEAF, 12, -92, None, 101.5)):
        J, B = lobe_profile(sd, n, jit=0.06, bul=(32, 66))
        d.form(canopy_blob(cx, cy, rx, ry, n, J, B, start=st, notch=notch),
               col, sweep(cx, cy, rx, ry, lo=.30, hi=-.44, wob=.09,
                          seed=cx * .012))
    for (mx, my, L, Wd, dg) in ((224, 580, 88, 50, -28), (696, 554, 82, 48,
                                24), (818, 660, 80, 46, -16),
                                (306, 748, 84, 48, 32), (626, 778, 74, 44,
                                -10)):
        d.fill(leaf_round(mx, my, L, Wd, dg), GRASS_DEEP)

    # face: 236 wide on the 508-wide front clump = 46.5%
    d.add(face(470, 678, 236, mass_w=508, default="surprised", tilt=-2.0,
               eyes=((-42, -18), (50, -14)), eye_r=(21, 28), mouth=(0, 48),
               brow_lift=6))

    _saucer(d, 514, 208, 198, 52, dome_k=1.56, alien=True, seed=2.0)
    _saucer(d, 146, 800, 126, 38, dome_k=1.42, deg=-9, seed=9.0)
    _saucer(d, 892, 736, 116, 35, dome_k=1.42, flip=True, deg=7,
            seed=16.0)                                          # ODDITY
    for (sx, sy, sr, sd) in ((122, 420, 46, 8), (902, 430, 40, -12),
                             (62, 618, 36, 20), (958, 880, 42, -6),
                             (272, 176, 40, 14), (760, 214, 34, -18)):
        d.form(star4(sx, sy, sr, sd), SUN, None, None, ol=OL_FINE)
    return d.svg()


# =====================================================================
# 7. r-robot-rosebush   *** STRESS TEST: MECHANICAL ***
#
# The plant the old kit literally could not draw.  Every mass here is
# rectilinear -- `slab`, `panel`, `hard_poly`, `plinth`, `trunk_stack`,
# `bolt`, `grille` -- with `sweep_hard` shadows so no shadow edge wobbles
# inside a machined part.  The only organic shapes in the whole asset are
# the two roses, and that contrast IS the joke.
# =====================================================================
def _rose(d, cx, cy, r, deg=0.0, seed=0.0):
    """A rose: three nested whorls of petals + a tight bud eye.

    Organic on purpose -- it is the one soft thing on the robot.
    """
    for i, (k, col, sh, n) in enumerate(((1.00, FRUIT, FRUIT_DEEP, 11),
                                         (0.68, FRUIT_DEEP, FRUIT_DEEP, 9),
                                         (0.40, FRUIT, FRUIT_DEEP, 7))):
        J, B = lobe_profile(seed + i * 4.0, n, jit=0.10, bul=(10, 26))
        d.form(canopy_blob(cx, cy, r * k, r * k * .94, n, J, B,
                           start=deg - 90 + i * 27),
               col, sweep(cx, cy, r * k, r * k, lo=.30, hi=-.44,
                          seed=seed + i),
               sh, ol=OL_PROP if k > .5 else OL_FINE)
    d.form(slab(cx + r * .04, cy + r * .02, r * .30, r * .28, 0.42, deg),
           FRUIT_DEEP, None, None, ol=OL_FINE)
    # the calyx it is bolted into
    d.form(hard_poly([(cx - r * .46, cy + r * .74), (cx + r * .44, cy + r * .70),
                      (cx + r * .26, cy + r * 1.24),
                      (cx - r * .30, cy + r * 1.26)], r * .18),
           STEEL, sweep_hard(cx, cy + r * .98, r * .4, r * .3), STEEL_DEEP,
           ol=OL_PROP)


def robot_rosebush():
    d = Doc()
    CXR = 504

    # ---- machined base plate: root lobes are wrong on a robot ----
    plate, pads = plinth(CXR, BASE_Y, 430, 118, r=0.05, feet=3)
    for pad in pads:
        d.form(pad, STEEL_DEEP, sweep_hard(CXR, 970, 60, 30), STEEL_DARK,
               ol=OL_PROP)
    d.form(plate, STEEL, sweep_hard(CXR, 942, 215, 60, lo=.22, hi=-.28),
           STEEL_DEEP, ol=OL_MAIN)
    for i, bx in enumerate((362, 508, 650)):
        hd, sl = bolt(bx, 918, 21, deg=i * 23)
        d.form(hd, STEEL_DEEP, None, None, ol=OL_FINE)
        d.line(sl, OL_FINE, STEEL_DARK)

    # ---- stamped steel leaves on the spine (drawn behind it) ----
    for (lx, ly, L, Wd, dg) in ((442, 858, 212, 118, -76), (572, 838, 202,
                                112, 74), (450, 742, 180, 100, -62),
                                (562, 722, 172, 96, 60)):
        d.form(leaf_pointed(lx, ly, L, Wd, dg, curl=0.0), STEEL,
               sweep_hard(lx + (60 if dg > 0 else -60), ly - L * .45,
                          Wd * .7, L * .34), STEEL_DEEP, ol=OL_PROP)
        d.line(vein(lx, ly, L, dg), OL_FINE, STEEL_DARK)

    # ---- segmented machined spine ----
    for i, (sd, w, cy, h) in enumerate(trunk_stack(CXR, 626, 902, 116, 152,
                                                   4, r=0.14, seed=6.2)):
        d.form(sd, STEEL, sweep_hard(CXR, cy, w * .5, h * .5), STEEL_DEEP,
               ol=OL_MAIN)
        if i < 3:                       # collar ring between the segments
            d.form(slab(CXR, cy + h * .5, w * 1.30, 26, 0.40),
                   STEEL_DEEP, None, None, ol=OL_PROP)

    # ---- arms, out and up, with an elbow bolt each ----
    for (x0, y0, x1, y1, w0, w1, k, ex, ey) in (
            (408, 528, 182, 350, 94, 66, -0.20, 268, 476),
            (604, 520, 838, 322, 88, 62, 0.24, 766, 468)):
        d.form(branch(x0, y0, x1, y1, w0, w1, k),
               STEEL, sweep_hard((x0 + x1) / 2, (y0 + y1) / 2, 110, 90),
               STEEL_DEEP, ol=OL_MAIN)
        hd, sl = bolt(ex, ey, 25, deg=14)
        d.form(hd, STEEL_DEEP, None, None, ol=OL_FINE)
        d.line(sl, OL_FINE, STEEL_DARK)

    # ---- the roses ----
    _rose(d, 168, 306, 128, deg=8, seed=3.4)
    _rose(d, 852, 278, 120, deg=-14, seed=21.7)

    # ---- body: panel + recessed face plate + grille + bolts ----
    outer, inner = panel(CXR, 540, 336, 250, r=0.09, inset=0.30)
    d.form(outer, STEEL, sweep_hard(CXR, 540, 168, 125, lo=.26, hi=-.30),
           STEEL_DEEP, ol=OL_MAIN)
    d.form(inner, STEEL_DEEP, sweep_hard(CXR, 540, 118, 88, lo=.24, hi=-.32),
           STEEL_DARK, ol=OL_PROP)
    for sd in grille(CXR, 542, 168, 96, 5, gap=0.44):
        d.form(sd, STEEL_DARK, None, None, ol=OL_FINE)
    for i, (bx, by) in enumerate(((378, 442), (630, 438), (376, 640),
                                  (632, 636))):
        hd, sl = bolt(bx, by, 23, deg=17 + i * 31)
        d.form(hd, STEEL_DEEP, None, None, ol=OL_FINE)
        d.line(sl, OL_FINE, STEEL_DARK)

    # ---- neck ----
    d.form(slab(500, 400, 104, 66, 0.22), STEEL_DEEP, None, None, ol=OL_PROP)

    # ---- head: rectilinear, with a cream visor the face lives on ----
    d.form(slab(500, 268, 344, 244, r=0.10, skew=0.05), STEEL,
           sweep_hard(500, 268, 172, 122, lo=.24, hi=-.30), STEEL_DEEP,
           ol=OL_MAIN)
    for sx in (-1, 1):                                   # ear caps
        d.form(slab(500 + sx * 190, 274, 46, 92, 0.30), STEEL_DEEP,
               None, None, ol=OL_PROP)
    d.form(slab(500, 262, 262, 164, r=0.11), CREAM,
           sweep_hard(500, 262, 131, 82, lo=.22, hi=-.34), CREAM_DEEP,
           ol=OL_PROP)
    # face: 178 wide on the 344-wide head = 51.7%; wide-set eyes, deadpan
    d.add(face(500, 262, 178, mass_w=344, default="neutral", tilt=-1.0,
               eyes=((-54, -10), (56, -12)), eye_r=(23, 24), mouth=(0, 50),
               mouth_k=0.9))

    # ---- antenna: a hard zigzag coil + a SUN bulb ----
    coil = [(500, 148)]
    for i in range(6):
        coil.append((500 + (26 if i % 2 == 0 else -26), 141 - i * 8))
    d.add('<path d="%s" fill="none" stroke="%s" stroke-width="%d" %s/>'
          % (poly(coil, close=False), STEEL_DEEP, OL_PROP, RJ))
    d.form(hard_poly([(462, 110), (546, 108), (556, 66), (504, 44),
                      (456, 70)], 30), SUN,
           sweep_hard(504, 84, 52, 34, lo=.26, hi=-.36), SUN_SHADE,
           ol=OL_PROP)

    # ---- ODDITY: one bolt has worked loose and lies in the dirt ----
    hd, sl = bolt(786, 970, 24, deg=-41)
    d.form(hd, STEEL_DEEP, None, None, ol=OL_FINE)
    d.line(sl, OL_FINE, STEEL_DARK)
    return d.svg()


# =====================================================================
# 8. x-xylophone-tree   *** STRESS TEST: GRADUATED RIGID REPETITION ***
#
# Five hard-edged bars whose lengths come from `graduated()`, hung on two
# straight rails, over a splayed root foot that deliberately opts IN to deep
# notches (root_depth=(46,88)) -- the one place claws are the right answer.
# =====================================================================
def xylophone_tree():
    d = Doc()
    BAR_COL = [FRUIT, ACCENT, SUN, GRASS, SKY_HI]
    XS = graduated(5, 162, 858)
    ANG = [-19, -9.5, 0.5, 9, 19.5]
    CY = [333, 308, 284, 310, 366]              # last bar sits LOW: the oddity
    LEN = [334, 404, 444, 388, 324]
    WID = [128, 134, 138, 130, 122]             # gapped: the rails show

    # ---- trunk: wide, splayed, claw-footed ----
    d.form(trunk_chunky(498, 622, BASE_Y, 286, 452, root_seed=64.1, lean=4,
                        root_lobes=4, root_depth=(34, 62), flare=1.14),
           SOIL, sweep(516, 800, 220, 210, lo=.16, hi=-.20, wob=.05),
           SOIL_DEEP,
           inner=("".join(
               '<path d="%s" fill="none" stroke="%s" stroke-width="%d" %s/>'
               % (sd, INK, OL_MAIN, RJ)
               for sd in ("M406,660 C392,760 400,860 386,962",
                          "M598,672 C610,768 600,864 614,966"))))

    # a wobbly cap so the stump has no dead-straight top edge
    JC, BC = lobe_profile(70.5, 9, jit=0.03, bul=(6, 16))
    d.form(canopy_blob(500, 640, 176, 44, 9, JC, BC, start=-96), SOIL,
           sweep(500, 640, 176, 44, lo=.20, hi=-.34), SOIL_DEEP)

    # ---- two side arms holding the mallets ----
    for (x0, y0, x1, y1, w0, w1, k) in ((392, 740, 172, 676, 78, 58, 0.14),
                                        (614, 730, 852, 690, 74, 56, 0.17)):
        d.form(branch(x0, y0, x1, y1, w0, w1, k), SOIL,
               sweep((x0 + x1) / 2, (y0 + y1) / 2, 110, 60, lo=.22, hi=-.28),
               SOIL_DEEP, ol=OL_MAIN)

    # ---- the trunk's face: 168 wide on a ~336-wide shaft = 50.0% ----
    d.add(face(492, 764, 168, mass_w=336, default="mischief", tilt=2.0,
               eyes=((-48, -16), (44, -12)), eye_r=(17, 23), mouth=(4, 42),
               mouth_k=0.95))

    # ---- rails behind the bars (straight, machined) ----
    for (ry, rw) in ((246, 792), (452, 836)):
        d.form(slab(506, ry, rw, 34, 0.48, deg=1.5), BARK_LITE,
               sweep_hard(506, ry, rw * .5, 17, lo=.20, hi=-.30), SOIL,
               ol=OL_PROP)

    # ---- the bars ----
    for i in range(5):
        bd = slab(XS[i], CY[i], WID[i], LEN[i], r=0.09,
                  deg=ANG[i] + (4.5 if i == 4 else 0.0), skew=0.03)
        d.form(bd, BAR_COL[i],
               sweep_hard(XS[i], CY[i], WID[i] * .5, LEN[i] * .5,
                          lo=.24, hi=-.30), SHADE[BAR_COL[i]], ol=OL_MAIN)
        # cream knobs where the bar crosses each rail
        for t in (-0.30, 0.28):
            a = math.radians(ANG[i] + (4.5 if i == 4 else 0.0))
            kx = XS[i] - LEN[i] * t * math.sin(a)
            ky = CY[i] + LEN[i] * t * math.cos(a)
            d.form(slab(kx, ky, 54, 40, 0.46, deg=ANG[i]), CREAM,
                   sweep_hard(kx, ky, 27, 20, lo=.24, hi=-.34), CREAM_DEEP,
                   ol=OL_FINE)

    # ---- two mallets, in front of the bars ----
    for (hx, hy, tx, ty, hr, k) in ((128, 372, 190, 664, 62, 0.13),
                                    (912, 366, 838, 678, 58, -0.15)):
        d.form(branch(hx, hy, tx, ty, 34, 30, k), BARK_LITE,
               sweep_hard((hx + tx) / 2, (hy + ty) / 2, 70, 120), SOIL,
               ol=OL_PROP)
        J, B = lobe_profile(hx * .01, 9, jit=0.03, bul=(4, 8))
        d.form(canopy_blob(hx, hy, hr, hr * .84, 9, J, B), BARK_LITE,
               sweep(hx, hy, hr, hr, lo=.28, hi=-.44), SOIL, ol=OL_PROP)
    return d.svg()


# =====================================================================
# 9. b-banana-tree   *** STRESS TEST: NO ROUND CANOPY AT ALL ***
#
# Six long `crescent` tubes radiating off a segmented pseudo-stem, plus a
# hand of five more as fruit.  There is not one `canopy_blob` in this asset.
# =====================================================================
def banana_tree():
    d = Doc()
    CXB, CROWN = 498, 534

    # ---- leaves, back pair first so the front ones overlap them ----
    LEAVES = [(-90, 424, 158, 0.30, GRASS, 7.0),
              (86, 418, 150, -0.32, GRASS, 12.0),
              (-56, 432, 168, 0.25, LEAF, 17.0),
              (52, 428, 162, -0.27, LEAF, 22.0),
              (-19, 408, 176, 0.15, LEAF, 27.0),
              (16, 400, 170, -0.16, GRASS, 32.0)]
    for (dg, L, w, arc, col, sd) in LEAVES:
        pth = crescent(CXB, CROWN, L, w, dg, arc, waist=0.34)
        a = math.radians(dg - 90.0)
        mx, my = CXB + L * .5 * math.cos(a), CROWN + L * .5 * math.sin(a)
        d.form(pth, col, sweep(mx, my, L * .42, w * .8, lo=.26, hi=-.40,
                               wob=.06, seed=sd), SHADE[col], ol=OL_MAIN)
        # midrib + a few ribs: the contour lines do the form work
        d.line("M%.0f,%.0f %s" % (CXB, CROWN,
                                  smooth_open(bow(CXB, CROWN,
                                                  CXB + L * .92 *
                                                  math.cos(a),
                                                  CROWN + L * .92 *
                                                  math.sin(a), arc, 6))),
               OL_FINE)
        for t in (0.34, 0.56, 0.78):
            sp = bow(CXB, CROWN, CXB + L * math.cos(a),
                     CROWN + L * math.sin(a), arc, 6)
            k = int(t * 5)
            px, py = sp[k]
            nx, ny = math.cos(a + math.pi / 2), math.sin(a + math.pi / 2)
            side = 1 if arc > 0 else -1
            d.line("M%.0f,%.0f L%.0f,%.0f"
                   % (px, py, px + nx * w * .34 * side,
                      py + ny * w * .34 * side), OL_FINE)

    # ---- segmented pseudo-stem ----
    for i, (pth, hw, cy) in enumerate(trunk_palm(CXB, 458, 994,
                                                 92, 178, n=4,
                                                 wob=(0, 7, -5, 6))):
        d.form(pth, GRASS_DEEP,
               sweep(CXB, cy, hw, hw * .55, lo=.24, hi=-.38, seed=i * 2.3),
               GRASS_DARK, ol=OL_MAIN)
        # the chevron leaf-sheath scar that says "banana", not "palm"
        d.line("M%.0f,%.0f L%.0f,%.0f L%.0f,%.0f"
               % (CXB - hw * .74, cy - 6, CXB + 4, cy + 44,
                  CXB + hw * .78, cy - 12), OL_FINE)

    # ---- the hand of bananas, hung off a curved stalk ----
    d.form(branch(560, 590, 668, 648, 46, 62, -0.30, cap="flat"),
           GRASS_DARK, sweep_hard(614, 618, 60, 40), GRASS_DARK, ol=OL_PROP)
    # the purple flower bud hangs UNDER the hand, so it is drawn first
    d.form(horn(742, 852, 132, 104, deg=176, k=0.07), BERRY,
           sweep(760, 908, 60, 48, lo=.26, hi=-.42), BERRY_DEEP, ol=OL_PROP)
    for i, (dg, L, w, sd) in enumerate(((116, 244, 78, 41.0),
                                        (129, 258, 82, 46.0),
                                        (142, 262, 84, 51.0),
                                        (154, 250, 80, 56.0),
                                        (166, 232, 74, 61.0))):
        a = math.radians(dg - 90.0)
        bx, by = 668 + i * 4, 642 + i * 5
        pth = crescent(bx, by, L, w, dg, -0.34, waist=0.46)
        d.form(pth, SUN, sweep(bx + L * .4 * math.cos(a),
                               by + L * .4 * math.sin(a), L * .38, w * .7,
                               lo=.28, hi=-.42, seed=sd), SUN_SHADE,
               ol=OL_PROP)
        tx = bx + L * .94 * math.cos(a)
        ty = by + L * .94 * math.sin(a)
        d.form(slab(tx, ty, w * .40, w * .34, 0.44, deg=dg), GRASS_DEEP,
               None, None, ol=OL_FINE)

    # ---- ODDITY: one banana has dropped and lies in the dirt ----
    d.form(crescent(176, 936, 166, 62, 94, -0.28, waist=0.48), SUN,
           sweep(256, 932, 72, 28, lo=.24, hi=-.40), SUN_SHADE, ol=OL_PROP)
    return d.svg()


# =====================================================================
# KIT REFERENCE SHEET
# =====================================================================
def kit_sheet():
    d = Doc(2040, 1560)
    d.add('<rect x="0" y="0" width="2040" height="1560" fill="%s"/>' % CREAM)
    F = "Verdana,DejaVu Sans,sans-serif"

    def T(x, y, sz, txt, col=INK_SOFT, w="bold"):
        d.add('<text x="%d" y="%d" font-family="%s" font-size="%d" '
              'font-weight="%s" fill="%s">%s</text>'
              % (x, y, F, sz, w, col, txt))

    T(44, 66, 42, "ALPHABET GARDEN &#8212; PLANT KIT")
    T(44, 102, 21, "1024x1024 &#183; stem base y=1000 &#183; object height "
                   "~880 (86% of frame) &#183; light from UPPER-LEFT on every "
                   "plant", INK_SOFT, "normal")
    T(44, 130, 21, "outlines 13 main / 12 prop / 11 fine &#8212; 11px is the "
                   "FLOOR (0.9px at game size ghosts out) &#183; round joins "
                   "+ caps &#183; two-tone hard-edged, never a gradient",
      INK_SOFT, "normal")
    T(44, 158, 21, "canopy_blob(n, jit, bul) and the root foot take a "
                   "PER-PLANT seed. They are required arguments on purpose.",
      ACCENT_DEEP, "normal")

    # ---------------- leaves ----------------
    T(44, 226, 26, "ORGANIC VOCABULARY &#8212; leaves, crescents, horns")
    lv = [("round", leaf_round(120, 454, 180, 116, -6), GRASS, 120, 372),
          ("pointed", leaf_pointed(310, 460, 196, 104, 4), GRASS, 310, 374),
          ("lobed / maple", leaf_lobed(486, 374, 98, -8), EMBER, 486, 374),
          ("frond", leaf_frond(652, 458, 190, 116, -4), GRASS, 666, 374),
          ("crescent", crescent(796, 300, 190, 78, 150, -0.34), SUN,
           838, 376),
          ("horn", horn(968, 460, 178, 86, -4, 0.14), GRASS, 962, 386)]
    for nm, pth, col, sx, sy in lv:
        d.form(pth, col, sweep(sx, sy, 96, 96, lo=.30, hi=-.44), ol=OL_PROP)
    for i, x in enumerate((70, 254, 414, 610, 764, 940)):
        T(x, 520, 20, lv[i][0])

    # ---------------- trunks + branch ----------------
    T(44, 600, 26, "TRUNK / STEM  +  BRANCH  +  THE GROUND ANCHOR")
    d.form(stem_slim(130, 650, 980, 58, root_seed=1.0, lean=14, w_base=160),
           GRASS, sweep(140, 834, 84, 180, lo=.06, hi=-.10), GRASS_DEEP)
    T(50, 1026, 20, "slim stem")
    d.form(trunk_chunky(354, 650, 980, 150, 292, root_seed=2.0), SOIL,
           sweep(366, 840, 140, 180, lo=.18, hi=-.14), SOIL_DEEP)
    T(276, 1026, 20, "chunky trunk")
    for i, (pth, hw, cy) in enumerate(trunk_palm(600, 650, 980, 62, 140, n=6)):
        d.form(pth, BARK_LITE, sweep(600, cy, hw, hw * .4, lo=.26, hi=-.40,
                                     seed=i * 1.7), SOIL)
    T(512, 1026, 20, "segmented palm")
    for i, (sd, w, cy, h) in enumerate(trunk_stack(830, 650, 980, 86, 122,
                                                   4, seed=3.0)):
        d.form(sd, STEEL, sweep_hard(830, cy, w * .5, h * .5), STEEL_DEEP)
    T(744, 1026, 20, "machined stack")
    d.form(branch(760, 900, 986, 700, 74, 40, -0.20), SOIL,
           sweep(870, 800, 110, 90, lo=.22, hi=-.30), SOIL_DEEP)
    T(930, 1026, 20, "branch")
    d.add('<path d="M50,980 L1000,980" stroke="%s" stroke-width="6" '
          'stroke-dasharray="20 16" fill="none"/>' % ACCENT)
    T(50, 1078, 19, "y = 1000. root_pts(seed, lobes, depth) &#8212; the foot "
                    "is PER PLANT. Default notches 16-30px;", ACCENT_DEEP,
      "normal")
    T(50, 1106, 19, "deeper reads as claws, so opt in explicitly when you "
                    "actually want claws (a xylophone tree does).",
      ACCENT_DEEP, "normal")

    # ---------------- rectilinear ----------------
    T(44, 1186, 26, "RECTILINEAR / MECHANICAL &#8212; the opt-out of "
                    "smooth_closed")
    out, inn = panel(150, 1300, 210, 150, r=0.08, inset=0.28)
    d.form(out, STEEL, sweep_hard(150, 1300, 105, 75), STEEL_DEEP)
    d.form(inn, STEEL_DEEP, None, None, ol=OL_PROP)
    for sd in grille(150, 1300, 100, 56, 4):
        d.form(sd, STEEL_DARK, None, None, ol=OL_FINE)
    T(60, 1420, 20, "panel + grille")
    d.form(slab(370, 1300, 170, 150, 0.07), SKY_HI,
           sweep_hard(370, 1300, 85, 75), SKY_DEEP)
    T(322, 1420, 20, "slab")
    for i, bx in enumerate((560, 630, 700)):
        hd, sl = bolt(bx, 1290, 26, deg=i * 29)
        d.form(hd, STEEL, None, None, ol=OL_FINE)
        d.line(sl, OL_FINE, STEEL_DARK)
    T(576, 1420, 20, "bolt")
    for i, hh in enumerate(graduated(5, 176, 96)):
        d.form(slab(800 + i * 74, 1330 - hh * .5, 60, hh, 0.09), BAR5[i],
               sweep_hard(800 + i * 74, 1330 - hh * .5, 30, hh * .5),
               SHADE[BAR5[i]], ol=OL_PROP)
    T(818, 1420, 20, "graduated bars")
    plate, pads = plinth(1160, 1400, 250, 84, feet=3)
    for p in pads:
        d.form(p, STEEL_DEEP, None, None, ol=OL_PROP)
    d.form(plate, STEEL, sweep_hard(1160, 1370, 125, 42), STEEL_DEEP)
    T(1090, 1450, 20, "plinth (machined foot)")

    # ---------------- two-tone ----------------
    T(1180, 226, 26, "TWO-TONE RECIPE  (base / shadow)")
    T(1180, 256, 18, "shadow = base hue, ~10 deg cooler, S +0.05, "
                     "V -0.09..-0.14, hard edge", INK_SOFT, "normal")
    pairs = [("grass", GRASS, GRASS_DEEP), ("leaf", LEAF, GRASS),
             ("soil", SOIL, SOIL_DEEP), ("bark-lite", BARK_LITE, SOIL),
             ("sun", SUN, SUN_SHADE), ("accent", ACCENT, ACCENT_DEEP),
             ("fruit", FRUIT, FRUIT_DEEP), ("ember", EMBER, EMBER_DEEP),
             ("steel", STEEL, STEEL_DEEP), ("steel-deep", STEEL_DEEP,
                                            STEEL_DARK),
             ("sky-hi", SKY_HI, SKY_DEEP), ("cream", CREAM, CREAM_DEEP),
             ("berry", BERRY, BERRY_DEEP), ("beam", BEAM, SUN)]
    for i, (nm, b, s) in enumerate(pairs):
        px = 1200 + (i % 3) * 276
        py = 316 + (i // 3) * 112
        J, B = lobe_profile(i * 3.7, 9, jit=0.02, bul=(4, 7))
        d.form(canopy_blob(px, py, 42, 38, 9, J, B), b,
               sweep(px, py, 42, 38, lo=.30, hi=-.44), s, ol=OL_PROP)
        T(px + 62, py - 4, 19, nm)
        T(px + 62, py + 22, 15, b + " / " + s, INK_SOFT, "normal")

    # ---------------- faces ----------------
    # 7 states in a 4+3 grid, each label directly UNDER its own head with
    # 96px of clear air before the next row (v1 buried row 1's labels).
    T(1180, 900, 26, "FACE SYSTEM &#8212; 7 SWAPPABLE STATES")
    T(1180, 930, 18, "silly + wacky only. state = eyes(1) + mouth(1) "
                     "[+ brows(1)]. Blush always on.", INK_SOFT, "normal")
    T(1180, 956, 18, "anchors, eye radius and mouth are per-plant "
                     "arguments; face width must be 45-60% of its mass.",
      ACCENT_DEEP, "normal")
    for i, ex in enumerate(EXPRESSIONS):
        px = 1258 + (i % 4) * 196
        py = 1090 + (i // 4) * 268
        J, B = lobe_profile(i * 5.3 + 2.0, 10, jit=0.015, bul=(6, 9))
        d.form(canopy_blob(px, py, 84, 80, 10, J, B), LEAF,
               sweep(px, py, 84, 80, lo=.34, hi=-.46), GRASS)
        d.add(face(px, py, 92, mass_w=168, default=ex))
        T(px - 62, py + 122, 18, "face-" + ex)
    return d.svg()


BAR5 = [FRUIT, ACCENT, SUN, GRASS, SKY_HI]


# =====================================================================
PLANTS = [
    ("s-sunflower", sunflower),
    ("a-apple-tree", apple_tree),
    ("m-maple-tree", maple_tree),
    ("b-butterfly-bush", butterfly_bush),
    ("p-pizza-palm", pizza_palm),
    ("u-ufo-tree", ufo_tree),
    ("r-robot-rosebush", robot_rosebush),
    ("x-xylophone-tree", xylophone_tree),
    ("b-banana-tree", banana_tree),
]

if __name__ == "__main__":
    want = sys.argv[1:]
    jobs = [(n, f) for n, f in PLANTS if not want or n in want]
    if not want or "_kit" in want:
        svg = kit_sheet()
        with open(os.path.join(OUT, "_kit.svg"), "w") as fh:
            fh.write(svg.strip() + "\n")
        ok = render("_kit", svg, 2040, 1560, os.path.join(OUT, "_kit.png"))
        print("%-18s %s" % ("_kit", "OK" if ok else "FAIL"))
    for name, fn in jobs:
        svg = fn()
        with open(os.path.join(OUT, name + ".svg"), "w") as fh:
            fh.write(svg.strip() + "\n")
        png = os.path.join(OUT, name + ".png")
        ok = render(name, svg, W, H, png)
        print("%-18s %s" % (name, "OK" if ok else "FAIL"))
