#!/usr/bin/env python3
"""Build the last 18 flat-vector WORLD assets: critters, sky, garden, fx.

    python3 art/flat/_build_world.py              # all 18
    python3 art/flat/_build_world.py bee moon     # by short name

Sibling of `_build_flat.py` (sun/cloud/hill/grass/dirt/bush) and
`plants/_build_plants.py` (the 78 plants).  It reuses BOTH: the plant kit
(`plants/_kit.py`) for geometry, the face rig and the palette, and
`_build_flat.py`'s rasteriser verbatim (2x headless Chrome -> LANCZOS to 1x).

WHY THESE 18.  Everything else in the game is flat vector; these were the
last glossy claymation renders still on screen.  Three critters are in frame
at all times and they fly across the sky at 52-86 css px, which is a ~16:1
downscale from a 768 canvas -- so every decision here is made for the SMALL
size first.  Faces are drawn oversized against their masses (still inside the
kit's 45-60% rule), outlines sit at the TOP of the brief's 1.2-1.7% band, and
nothing carries a detail that dies below 50px.

CANVAS + REGISTRATION.  Each file keeps the exact canvas of the claymation
PNG it replaces, and its content is placed on the same alpha bounding box, so
`js/data/flat-assets.js` can measure it and the game's existing positioning
still lands.  Canvas sizes: critters 768, sky/moon + sky/rain_cloud +
garden/* + fx/celebration_star 1024, sky/rainbow 1536x1024, sky/star +
sky/firefly + fx/sparkle 512, fx/poof_cloud + fx/water_splash 768.

THE FX OUTLINE DECISION (FLAT_ART_BRIEF Sec 2 makes outlines mandatory; the
four fx particles are the sanctioned exception).  Measured, not guessed:

  sparkle            8-30px, ADDITIVE  -> NO outline.  Black adds nothing
                     under additive blending, so an outline is literally
                     invisible; all it would do is eat 2 canvas px of arm.
  celebration_star   same star family  -> NO outline, for the same reason and
                     so the two star marks stay siblings.
  water_splash       16-34px, opaque   -> NO outline.  1.4% of its 485px
                     object is 7px, which lands at 0.3px at 34px display: it
                     does not draw a line, it just greys the blue.
  poof_cloud         30-180px, opaque  -> OUTLINED at 10px.  This one never
                     renders at 12px (its scale ramp is 0.6->1.9 of a 50-96px
                     size), the contour IS the read on a cream-on-sky puff,
                     and at its working size the line lands at 0.4-2.3px.

Everything else in the file is outlined at 1.2-1.7% of its own object height,
pure #000000, round joins and caps, no gradient and no filter anywhere.
"""
import os
import sys
import math
import importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "plants"))
from _kit import *                                     # noqa: F401,F403
from _kit import (INK, INK_SOFT, CREAM, CREAM_DEEP, ACCENT, ACCENT_DEEP,
                  SUN, SUN_DEEP, RAY_SHADE, BEAM, FRUIT, FRUIT_DEEP, GRASS,
                  GRASS_DEEP, GRASS_DARK, LEAF, BARK, BARK_DEEP, BARK_LITE,
                  SKY_HI, SKY_DEEP, STEEL, STEEL_DEEP, STEEL_DARK, BERRY,
                  RJ, Doc, face, smooth_closed, place, jitter, sweep,
                  sweep_hard, chip, poly, hard_poly, slab, horn, ribbon,
                  bow, leaf_round, vein, canopy_blob, lobe_profile,
                  stem_slim)

_spec = importlib.util.spec_from_file_location(
    "_build_flat_shared", os.path.join(HERE, "_build_flat.py"))
_bf = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_bf)
render = _bf.render                       # render(name, svg, w, h, png, 2)

SOIL = _bf.SOIL
SOIL_DEEP = _bf.SOIL_DEEP
SOIL_LITE = _bf.SOIL_LITE
CONTACT = _bf.CONTACT
CLOUD_SHADE = _bf.CLOUD_SHADE

# =====================================================================
# NEW PALETTE TOKENS
# Derived by the FLAT_ART_BRIEF Sec 3.4 rule (same hue family, a little more
# saturated, value dropped into the C4 dV 0.08-0.18 window) and APPENDED to
# the brief's table so the next author reuses them instead of inventing a
# near-miss.  Nothing here is above S 0.55; nothing sits in the muddy
# V 0.35-0.55 band.
# =====================================================================
VIOLET_LITE = "#c9b6ea"   # violet-lite  bat wing membrane, butterfly wing
VIOLET      = "#a58fd1"   # violet       bat body / shadow for violet-lite  dV .098
VIOLET_DEEP = "#8a74b3"   # violet-deep  shadow for violet                  dV .118
BLOSSOM     = "#f2a7c4"   # blossom      pink butterfly wing
BLOSSOM_DEEP = "#d489a8"  # blossom-deep shadow for blossom                 dV .118
CLOUD_DEEP  = "#a3bccc"   # cloud-deep   shadow for cloud-shade             dV .102

SHADE.update({VIOLET_LITE: VIOLET, VIOLET: VIOLET_DEEP,
              BLOSSOM: BLOSSOM_DEEP, CLOUD_SHADE: CLOUD_DEEP,
              SOIL: SOIL_DEEP, SOIL_LITE: SOIL})

OUT = HERE


# =====================================================================
# LOCAL GEOMETRY  (everything else comes from the kit)
# =====================================================================
def oval(cx, cy, rx, ry, deg=0.0, n=9, seed=0.0, wob=0.055):
    """A round-ish mass that is NOT an ellipse.  Radii vary per vertex."""
    k = jitter(seed, n, wob, 1.0)
    p = [(rx * k[i] * math.cos(2 * math.pi * i / n),
          ry * k[i] * math.sin(2 * math.pi * i / n)) for i in range(n)]
    return smooth_closed(place(p, cx, cy, deg))


def teardrop(cx, cy, w, h, deg=0.0, seed=0.0):
    """Raindrop / water droplet: round belly, drawn-out point at the top."""
    hw = w * 0.5
    k = jitter(seed, 4, 0.05, 1.0)
    p = [(0, -h * 0.50),
         (hw * 0.52 * k[0], -h * 0.10), (hw * k[1], h * 0.16),
         (hw * 0.72, h * 0.42), (0, h * 0.50),
         (-hw * 0.70, h * 0.44), (-hw * k[2], h * 0.14),
         (-hw * 0.50 * k[3], -h * 0.12)]
    return smooth_closed(place(p, cx, cy, deg))


def arc_pts(cx, cy, rr, ta, tb, cw, n):
    """Sample a circular arc from ta to tb, clockwise or counter-clockwise."""
    if cw:
        while tb < ta:
            tb += 2 * math.pi
    else:
        while tb > ta:
            tb -= 2 * math.pi
    return [(cx + rr * math.cos(ta + (tb - ta) * i / n),
             cy + rr * math.sin(ta + (tb - ta) * i / n)) for i in range(n + 1)]


def crescent_moon(c1, R, c2, r, n=22, wob=9.0, seed=3.0):
    """A crescent as ONE closed path -- never two circles with evenodd.

    An evenodd hole would punch an enclosed transparent region, which is the
    exact bug FLAT_ART_BRIEF Sec 5 makes you verify against.  Outer arc of
    circle 1 (the part outside circle 2), then the inner arc of circle 2
    (the part inside circle 1), sampled so the contour can carry a wobble.
    """
    (c1x, c1y), (c2x, c2y) = c1, c2
    dx, dy = c2x - c1x, c2y - c1y
    d = math.hypot(dx, dy)
    a = (R * R - r * r + d * d) / (2 * d)
    h = math.sqrt(max(R * R - a * a, 1.0))
    bx, by = c1x + a * dx / d, c1y + a * dy / d
    ux, uy = -dy / d, dx / d
    p1 = (bx + h * ux, by + h * uy)
    p2 = (bx - h * ux, by - h * uy)
    t1a = math.atan2(p1[1] - c1y, p1[0] - c1x)
    t2a = math.atan2(p2[1] - c1y, p2[0] - c1x)
    t1b = math.atan2(p1[1] - c2y, p1[0] - c2x)
    t2b = math.atan2(p2[1] - c2y, p2[0] - c2x)

    def pick(cx, cy, rr, ta, tb, want_out, ox, oy, orr):
        for cw in (True, False):
            q = arc_pts(cx, cy, rr, ta, tb, cw, 6)[3]
            far = math.hypot(q[0] - ox, q[1] - oy) > orr
            if far == want_out:
                return cw
        return True

    cw_o = pick(c1x, c1y, R, t1a, t2a, True, c2x, c2y, r)
    cw_i = pick(c2x, c2y, r, t2b, t1b, False, c1x, c1y, R)
    outer = arc_pts(c1x, c1y, R, t1a, t2a, cw_o, n)
    inner = arc_pts(c2x, c2y, r, t2b, t1b, cw_i, int(n * 0.7))[1:-1]
    pts = outer + inner
    k = jitter(seed, len(pts), 1.0, 0.0)
    out, m = [], len(outer)
    for i, q in enumerate(pts):
        # taper to zero at both horns: a wobbled vertex sitting ON the joint
        # between the two arcs grows a visible spur at the crescent's tip
        t = (i / float(m - 1)) if i < m else ((i - m + 1) / float(len(inner) + 1))
        f = math.sin(math.pi * min(max(t, 0.0), 1.0))
        out.append((q[0] + wob * f * k[i], q[1] + wob * f * k[(i + 5) % len(k)]))
    return smooth_closed(out)


def arc_band(cx, cy, rxo, ryo, rxi, ryi, a0=180.0, a1=360.0, n=44,
             wob=0.0, seed=0.0):
    """One band of the rainbow: outer elliptical arc out, inner arc back."""
    pts = []
    for i in range(n + 1):
        a = math.radians(a0 + (a1 - a0) * i / n)
        k = 1.0 + wob * math.sin(i * 0.83 + seed)
        pts.append((cx + rxo * k * math.cos(a), cy + ryo * k * math.sin(a)))
    for i in range(n + 1):
        a = math.radians(a1 + (a0 - a1) * i / n)
        k = 1.0 + wob * math.sin(i * 0.83 + seed + 1.7)
        pts.append((cx + rxi * k * math.cos(a), cy + ryi * k * math.sin(a)))
    return poly(pts)


def star_pts(cx, cy, r, n=5, waist=0.46, deg=0.0, jit=(1.0,)):
    """n-point star point list, outer radii jittered so it is never perfect."""
    p = []
    for i in range(n):
        k = jit[i % len(jit)]
        a = math.radians(-90 + 360.0 * i / n)
        b = math.radians(-90 + 360.0 * (i + 0.5) / n)
        p.append((r * k * math.cos(a), r * k * math.sin(a)))
        p.append((r * waist * math.cos(b), r * waist * math.sin(b)))
    return place(p, cx, cy, deg)


def lr(cx, cy, rx, ry, seed=0.0, lo=0.44, hi=-0.08, wob=0.07):
    """The house shadow: light upper-left, so the shade is the lower-right
    ~third of the mass.  Thin wrapper on the kit's `sweep` that fixes the
    lo/hi pair for round masses -- the kit's own defaults cut a round shape
    nearly in half, which reads as a fold rather than as form."""
    return sweep(cx, cy, rx, ry, lo, hi, wob, seed)


def contact_ell(cx, cy, rx, ry, col=CONTACT):
    return ('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="%s"/>'
            % (cx, cy, rx, ry, col))


def dot(cx, cy, r, col):
    return '<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s"/>' % (cx, cy, r, col)


def flat_form(doc, d, base, shade, shadow_d):
    """Two-tone form blocking with NO outline -- the fx-particle exception."""
    cid = doc._cid()
    doc.defs.append('<clipPath id="%s"><path d="%s"/></clipPath>' % (cid, d))
    doc.body.append('<path d="%s" fill="%s"/>' % (d, base))
    doc.body.append('<g clip-path="url(#%s)"><path d="%s" fill="%s"/></g>'
                    % (cid, shadow_d, shade))
    return doc


# outline ladder, per canvas.  1.2-1.7% of the object's own height.
OL_C = 10      # critters, 768 canvas, object ~520-700px  -> 1.5-1.9%... 1.6% typ
OL_CF = 8      # critter internal detail / small props
OL_K = 13      # 1024-canvas masses (moon, rain cloud, sprout, sign)
OL_KF = 11     # 1024-canvas detail
OL_S = 6       # 512-canvas masses (star, firefly) ~430px object -> 1.4%
OL_SF = 5      # 512-canvas detail


# =====================================================================
# CRITTERS  (768 x 768).  Seven silhouettes that must not be confusable at
# 46px: 4 round lobes / 4 pointed lobes with tails / horizontal capsule with
# high wings / dome / teardrop with a tail wedge / upright with ear tufts /
# wide angular membranes with ears.
# =====================================================================
def butterfly_pink():
    """Round-lobed butterfly, head-on.  The WIDEST, ROUNDEST critter: four
    fat circular lobes, a real negative-space gap between the upper and lower
    pair, cream polka dots."""
    d = Doc(768, 768)
    wings = [  # (cx, cy, rx, ry, deg, seed)
        (198, 300, 178, 148, -13, 1.3),
        (568, 300, 170, 144, 12, 2.7),
        (232, 512, 142, 124, 16, 4.1),
        (546, 512, 150, 116, -11, 5.9),
    ]
    for cx, cy, rx, ry, deg, sd in wings:
        w = oval(cx, cy, rx, ry, deg, n=9, seed=sd, wob=0.075)
        d.form(w, BLOSSOM, lr(cx, cy, rx, ry, sd, wob=0.09),
               shade=BLOSSOM_DEEP, ol=OL_C)
    spots = [(172, 246, 30), (246, 214, 22), (140, 328, 25), (228, 344, 33),
             (600, 234, 28), (530, 218, 21), (626, 316, 31), (548, 330, 24),
             (228, 540, 24), (284, 580, 19), (536, 550, 26), (496, 588, 20),
             (590, 288, 15)]
    for sx, sy, sr in spots:
        d.add(dot(sx, sy, sr, CREAM))
    # antennae -- ball-tipped, never mirrored
    d.line("M332,170 C302,116 294,94 270,72", ol=15, col=INK_SOFT)
    d.line("M436,166 C468,114 484,98 510,84", ol=15, col=INK_SOFT)
    d.add(dot(268, 70, 17, INK_SOFT))
    d.add(dot(512, 82, 15, INK_SOFT))
    # abdomen -- slimmer than the head, tapering to a round tip
    th = oval(384, 404, 108, 94, -3, n=9, seed=3.3, wob=0.05)
    d.form(th, ACCENT, lr(384, 404, 108, 94, 3.3), shade=ACCENT_DEEP, ol=OL_C)
    ab = ribbon(bow(384, 296, 392, 624, 0.02, 6), [110, 102, 90, 74, 58, 46],
                cap0="round", cap1="round")
    d.form(ab, ACCENT, lr(388, 460, 46, 160, 2.0, 0.20, -0.24, 0.05),
           shade=ACCENT_DEEP, ol=OL_C)
    d.line("M348,398 L428,394", ol=OL_CF)
    d.line("M352,478 L424,474", ol=OL_CF)
    hd = oval(382, 222, 122, 116, -4, n=9, seed=7.7, wob=0.04)
    d.form(hd, ACCENT, lr(382, 222, 122, 116, 1.1),
           shade=ACCENT_DEEP, ol=OL_C)
    d.add(face(380, 228, 136, mass_w=244, default="happy",
               eyes=((-48, -8), (50, -13)), eye_r=(25, 30), mouth=(2, 46),
               mouth_k=0.92, tilt=-3))
    return d.svg()


def butterfly_blue():
    """Swallowtail: broad wings with POINTED outer corners and a drawn-out
    lower tail.  Taller and pointier than the pink one, and marked with sky
    spots instead of cream dots."""
    d = Doc(768, 768)
    lu = smooth_closed([(352, 336), (300, 236), (198, 142), (78, 92),
                        (30, 152), (74, 262), (170, 344), (274, 388)])
    ru = smooth_closed([(412, 328), (468, 232), (570, 144), (690, 100),
                        (738, 164), (690, 272), (592, 350), (492, 384)])
    ll = smooth_closed([(352, 394), (248, 420), (150, 482), (100, 574),
                        (152, 648), (240, 604), (322, 534), (350, 472)])
    rl = smooth_closed([(410, 390), (516, 414), (614, 470), (664, 562),
                        (606, 636), (520, 592), (438, 526), (412, 466)])
    for w, (cx, cy, rx, ry, sd) in zip(
            (lu, ru, ll, rl),
            ((182, 232, 158, 126, 1.1), (588, 226, 156, 128, 2.3),
             (238, 508, 122, 112, 3.5), (528, 510, 124, 114, 4.9))):
        d.form(w, VIOLET_LITE, lr(cx, cy, rx, ry, sd, wob=0.09),
               shade=VIOLET, ol=OL_C)
    for sx, sy, sr in [(130, 190, 32), (216, 256, 25), (92, 260, 21),
                       (640, 190, 31), (548, 256, 26), (692, 260, 20),
                       (206, 548, 26), (250, 604, 18),
                       (562, 548, 27), (516, 604, 19)]:
        d.add(dot(sx, sy, sr, SKY_HI))
    d.line("M326,206 C300,156 286,130 258,108", ol=14, col=INK_SOFT)
    d.line("M440,200 C468,148 484,126 514,108", ol=14, col=INK_SOFT)
    d.add(dot(256, 106, 15, INK_SOFT))
    d.add(dot(516, 106, 13, INK_SOFT))
    ab = ribbon(bow(380, 330, 388, 596, 0.02, 6), [84, 78, 68, 56, 46, 36],
                cap0="round", cap1="round")
    d.form(ab, CREAM, lr(384, 464, 42, 134, 6.0, 0.22, -0.22, 0.05),
           shade=CREAM_DEEP, ol=OL_C)
    d.line("M352,410 L418,406", ol=OL_CF)
    d.line("M356,478 L414,474", ol=OL_CF)
    hd = oval(378, 254, 108, 104, 5, n=9, seed=8.3, wob=0.045)
    d.form(hd, CREAM, lr(378, 254, 108, 104, 3.3), shade=CREAM_DEEP, ol=OL_C)
    d.add(face(376, 258, 120, mass_w=216, default="delighted",
               eyes=((-48, -10), (50, -6)), eye_r=(24, 28), mouth=(0, 44),
               mouth_k=0.80, tilt=2))
    return d.svg()


def bee():
    """Horizontal capsule: round head + striped abdomen, two SMALL separated
    wings sitting high.  The only critter whose mass runs sideways."""
    d = Doc(768, 768)
    # the two wings must overlap EACH OTHER and the body, or the three
    # masses enclose a lens-shaped transparent hole over the bee's shoulders
    for cx, cy, rx, ry, deg, sd in [(352, 232, 98, 58, -38, 1.7),
                                    (456, 238, 92, 54, 17, 2.9)]:
        w = oval(cx, cy, rx, ry, deg, n=9, seed=sd, wob=0.06)
        d.form(w, CREAM, lr(cx, cy, rx, ry, sd), shade=CREAM_DEEP, ol=OL_CF)
    for x0, y0, x1, y1 in [(326, 522, 286, 638), (410, 548, 404, 682),
                           (500, 534, 540, 626)]:
        d.line("M%d,%d C%d,%d %d,%d %d,%d"
               % (x0, y0, x0 - 6, y0 + 50, x1 - 10, y1 - 38, x1, y1),
               ol=14, col=INK_SOFT)
    d.add('<path d="%s" fill="%s" stroke="%s" stroke-width="%d" %s/>'
          % (horn(652, 424, 78, 58, deg=104), INK_SOFT, INK, OL_CF, RJ))
    ab = oval(508, 410, 168, 152, 7, n=9, seed=4.4, wob=0.05)
    bands = ("".join(
        '<path d="%s" fill="%s"/>'
        % (slab(cx, 410 + dy, 60, 340, 0.30, deg=9), INK_SOFT)
        for cx, dy in ((466, 0), (570, 6))))
    d.form(ab, SUN_DEEP, lr(508, 410, 168, 152, 4.4),
           shade=RAY_SHADE, ol=OL_C, inner=bands)
    hd = oval(296, 396, 160, 154, -5, n=9, seed=6.6, wob=0.045)
    d.form(hd, SUN_DEEP, lr(296, 396, 160, 154, 6.6),
           shade=RAY_SHADE, ol=OL_C)
    d.line("M242,272 C224,214 212,190 186,166", ol=13, col=INK_SOFT)
    d.line("M328,258 C334,200 334,176 320,146", ol=13, col=INK_SOFT)
    d.add(dot(184, 164, 14, INK_SOFT))
    d.add(dot(318, 144, 12, INK_SOFT))
    d.add(face(294, 402, 170, mass_w=320, default="happy",
               eyes=((-48, -12), (50, -8)), eye_r=(25, 30), mouth=(2, 48),
               mouth_k=0.98, tilt=-4))
    return d.svg()


def ladybug():
    """A DOME.  Top-down: red shell with a real elytra seam, and a small dark
    head tucked under it carrying a cream face plate the eyes can live on."""
    d = Doc(768, 768)
    for x0, y0, x1, y1, w in [(152, 290, 76, 226, 15), (114, 396, 40, 388, 15),
                              (146, 492, 78, 554, 15),
                              (622, 282, 700, 220, 15),
                              (660, 392, 728, 384, 12),
                              (628, 486, 696, 546, 15)]:
        d.line("M%d,%d L%d,%d" % (x0, y0, x1, y1), ol=w, col=INK_SOFT)
    sh = oval(386, 358, 292, 254, -3, n=11, seed=2.2, wob=0.035)
    d.form(sh, FRUIT, lr(386, 358, 292, 254, 2.2, 0.42, -0.10, 0.05),
           shade=FRUIT_DEEP, ol=OL_C)
    d.line("M382,112 C396,248 392,428 388,596", ol=OL_C)
    for sx, sy, sr in [(252, 258, 44), (208, 404, 38), (286, 480, 34),
                       (508, 244, 42), (556, 394, 40), (474, 486, 26)]:
        d.add(dot(sx, sy, sr, INK_SOFT))
    d.line("M306,570 C280,610 264,630 242,638", ol=13, col=INK_SOFT)
    d.line("M466,566 C494,608 510,628 534,636", ol=13, col=INK_SOFT)
    d.add(dot(240, 638, 14, INK_SOFT))
    d.add(dot(536, 636, 12, INK_SOFT))
    hd = oval(386, 570, 162, 116, 2, n=9, seed=5.5, wob=0.04)
    d.form(hd, INK_SOFT, lr(386, 570, 162, 116, 5.5), shade=INK, ol=OL_C)
    fp = oval(386, 576, 124, 82, -2, n=9, seed=9.1, wob=0.035)
    d.form(fp, CREAM, lr(386, 576, 124, 82, 9.1), shade=CREAM_DEEP, ol=OL_CF)
    d.add(face(384, 580, 132, mass_w=248, default="happy",
               eyes=((-46, -6), (48, -10)), eye_r=(24, 26), mouth=(2, 40),
               mouth_k=0.78, tilt=1))
    return d.svg()


def bluebird():
    """A TEARDROP with an angular three-feather tail.  Only side-on critter;
    the raised wing breaks the body silhouette so it cannot read as a decal."""
    d = Doc(768, 768)
    tl = poly([(512, 336), (620, 268), (716, 238), (700, 316), (748, 350),
               (674, 404), (700, 458), (598, 462), (518, 438)])
    d.form(tl, SKY_HI, lr(636, 356, 116, 108, 3.1, 0.36, -0.14),
           shade=SKY_DEEP, ol=OL_C)
    d.line("M614,300 L676,346", ol=OL_CF)
    d.line("M600,384 L662,414", ol=OL_CF)
    bd = oval(340, 400, 250, 218, -7, n=11, seed=1.9, wob=0.04)
    d.form(bd, SKY_HI, lr(340, 400, 250, 218, 1.9, 0.40, -0.12, 0.05),
           shade=SKY_DEEP, ol=OL_C)
    br = oval(282, 490, 166, 120, -12, n=9, seed=4.6, wob=0.045)
    d.form(br, CREAM, lr(282, 490, 166, 120, 4.6), shade=CREAM_DEEP, ol=OL_CF)
    # the wing runs UP AND OUT past the back, so its tip breaks the outline
    # a smooth rounded blade whose TIP clears the back, against the angular
    # tail behind it -- two different shape languages, so neither reads as a
    # duplicate of the other
    wg = smooth_closed([(358, 344), (406, 252), (494, 180), (600, 152),
                        (628, 210), (562, 284), (468, 340), (390, 378)])
    d.form(wg, SKY_HI, lr(500, 262, 138, 112, 6.3, 0.26, -0.28, 0.07),
           shade=SKY_DEEP, ol=OL_C)
    d.line("M416,332 C476,282 534,238 596,206", ol=OL_CF)
    d.line("M402,364 C452,326 496,292 540,268", ol=8, col=SKY_DEEP)
    bk = smooth_closed([(174, 356), (72, 392), (172, 434), (194, 396)])
    d.form(bk, ACCENT, lr(146, 394, 62, 40, 2.5, 0.20, -0.24, 0.05),
           shade=ACCENT_DEEP, ol=OL_CF)
    d.line("M90,392 L176,396", ol=7)
    d.line("M292,204 C288,156 300,130 330,116", ol=OL_CF)   # cowlick: oddity
    d.add(face(262, 366, 190, mass_w=372, default="happy",
               eyes=((-50, -12), (48, -18)), eye_r=(25, 29), mouth=(6, 46),
               mouth_k=0.86, tilt=-6))
    return d.svg()


def owl():
    """UPRIGHT with two ear tufts.  Tallest critter, biggest eyes."""
    d = Doc(768, 768)
    for cx, cy, L, w, deg in [(252, 214, 148, 96, -26), (508, 200, 132, 88, 22)]:
        d.add('<path d="%s" fill="%s" stroke="%s" stroke-width="%d" %s/>'
              % (horn(cx, cy, L, w, deg=deg), BARK, INK, OL_C, RJ))
    bd = oval(382, 448, 258, 286, 2, n=11, seed=1.4, wob=0.035)
    d.form(bd, BARK, lr(382, 448, 258, 286, 1.4, 0.40, -0.12, 0.05),
           shade=BARK_DEEP, ol=OL_C)
    for cx, cy, rx, ry, deg, sd in [(176, 476, 76, 174, -8, 3.3),
                                    (588, 462, 72, 166, 7, 5.1)]:
        w = oval(cx, cy, rx, ry, deg, n=9, seed=sd, wob=0.06)
        # BARK over a generous BARK_DEEP face: the value step that separates
        # the folded wing from the body, with no undocumented third brown
        # (BARK_DEEP's own shadow would land in the muddy V 0.35-0.55 band).
        d.form(w, BARK, lr(cx, cy, rx, ry, sd, 0.86, 0.44),
               shade=BARK_DEEP, ol=OL_CF)
    bl = oval(376, 566, 172, 158, -3, n=11, seed=7.2, wob=0.05)
    d.form(bl, CREAM, lr(376, 566, 172, 158, 7.2), shade=CREAM_DEEP, ol=OL_CF)
    for y in (508, 578, 648):
        d.line("M%d,%d Q%d,%d %d,%d" % (286, y, 378, y + 44, 468, y - 2),
               ol=7, col=CREAM_DEEP)
    fd = oval(380, 300, 214, 158, -2, n=11, seed=9.8, wob=0.04)
    d.form(fd, CREAM, lr(380, 300, 214, 158, 9.8), shade=CREAM_DEEP, ol=OL_C)
    bkd = smooth_closed([(378, 330), (416, 352), (382, 410), (346, 350)])
    d.form(bkd, ACCENT, lr(380, 372, 34, 40, 1.0, 0.20, -0.30, 0.05),
           shade=ACCENT_DEEP, ol=OL_CF)
    for fx in (326, 434):
        d.line("M%d,%d L%d,%d" % (fx, 700, fx, 734), ol=18, col=ACCENT)
        d.line("M%d,%d L%d,%d" % (fx - 26, 734, fx + 26, 734), ol=18,
               col=ACCENT)
    d.add(face(378, 296, 240, mass_w=428, default="surprised",
               eyes=((-56, -6), (58, -10)), eye_r=(31, 33), mouth=(2, 62),
               mouth_k=0.7, tilt=-2))
    return d.svg()


def bat():
    """WIDE and ANGULAR.  Two big straight-edged membranes with two deep
    scallops each -- the only critter built from straight lines, so it can
    never be confused with the two butterflies."""
    d = Doc(768, 768)
    # leading edge runs shoulder -> wing tip; the membrane HANGS BELOW it
    # with two fingers, which is what stops a bat reading as a collar.
    lw = poly([(310, 302), (168, 240), (24, 200), (60, 392), (168, 352),
               (198, 492), (272, 432), (306, 490)])
    rw = poly([(458, 296), (598, 228), (744, 190), (712, 386), (604, 348),
               (578, 498), (500, 438), (462, 484)])
    for w, (cx, cy, rx, ry, sd) in zip((lw, rw), ((166, 352, 150, 148, 2.1),
                                                  (604, 346, 148, 146, 4.7))):
        d.form(w, VIOLET_LITE, lr(cx, cy, rx, ry, sd, 0.30, -0.22, 0.0),
               shade=VIOLET, ol=OL_C)
    d.line("M300,318 L100,270", ol=OL_CF)       # finger bones, straight
    d.line("M304,368 L168,378", ol=OL_CF)
    d.line("M466,312 L668,268", ol=OL_CF)
    d.line("M464,362 L604,374", ol=OL_CF)
    # ears: one deliberately shorter and cocked further out -- the oddity
    for cx, cy, L, w, deg in [(328, 256, 138, 84, -21), (444, 250, 106, 74, 31)]:
        d.add('<path d="%s" fill="%s" stroke="%s" stroke-width="%d" %s/>'
              % (horn(cx, cy, L, w, deg=deg), VIOLET, INK, OL_C, RJ))
    for fx in (348, 420):
        d.line("M%d,%d L%d,%d" % (fx, 520, fx - 6, 586), ol=20, col=VIOLET)
    bd = oval(384, 396, 142, 160, 3, n=9, seed=6.8, wob=0.04)
    d.form(bd, VIOLET, lr(384, 396, 142, 160, 6.8), shade=VIOLET_DEEP, ol=OL_C)
    d.add('<path d="%s" fill="%s"/>' % (poly([(354, 438), (378, 438),
                                              (366, 472)]), CREAM))
    d.add('<path d="%s" fill="%s"/>' % (poly([(396, 438), (418, 438),
                                              (408, 468)]), CREAM))
    d.add(face(384, 390, 152, mass_w=284, default="happy",
               eyes=((-48, -14), (50, -10)), eye_r=(24, 28), mouth=(0, 42),
               mouth_k=0.72, tilt=2))
    return d.svg()


# =====================================================================
# SKY
# =====================================================================
def moon():
    """1024.  A sleepy crescent, built as ONE closed path (never evenodd, which
    would punch an enclosed transparent hole).  The face sits on the FAT lower
    belly, where the crescent is 380px wide -- put it at the waist and half of
    it hangs over the hollow."""
    d = Doc(1024, 1024)
    cr = crescent_moon((518, 518), 440, (738, 420), 372, n=24, wob=8.0)
    craters = "".join(dot(cx, cy, r, CREAM_DEEP) for cx, cy, r in
                      [(360, 286, 52), (206, 470, 36), (172, 610, 20),
                       (392, 856, 40), (556, 904, 24)])
    d.form(cr, CREAM, lr(518, 518, 440, 440, 1.5, 0.50, 0.04, 0.05),
           shade=CREAM_DEEP, ol=OL_K, inner=craters)
    # a little star asleep in the crescent's hollow -- the oddity
    st = smooth_closed(star_pts(826, 600, 106, 5, 0.50, deg=14,
                                jit=(1.0, 0.9, 1.05, 0.95, 1.02)))
    d.form(st, SUN, lr(826, 600, 106, 106, 2.5, 0.40, -0.10),
           shade=RAY_SHADE, ol=OL_KF)
    d.add(face(300, 658, 190, mass_w=352, default="sleepy",
               eyes=((-52, -10), (54, -4)), eye_r=(24, 28), mouth=(4, 54),
               mouth_k=0.72, tilt=-5))
    return d.svg()


def star():
    """512, renders 10-26px.  Dead simple: one fat 5-point star, nothing else."""
    d = Doc(512, 512)
    p = star_pts(258, 254, 214, 5, 0.50, deg=7,
                 jit=(1.0, 0.94, 1.06, 0.92, 1.01))
    sd = hard_poly(p, 20)
    d.form(sd, SUN, sweep(258, 254, 214, 214, 0.26, -0.32, 0.05, 1.0),
           shade=RAY_SHADE, ol=OL_S)
    return d.svg()


def firefly():
    """512.  ONE round body with the face on it and ONE glowing tail bulb.
    An earlier head + thorax + tail chain read as a caterpillar; three round
    segments in a row always will.  The glow is a FLAT spiky halo -- no blur,
    no filter, no gradient; the spikes are what make a flat shape read as
    light."""
    d = Doc(512, 512)
    hp, hk = [], jitter(4.2, 14, 0.10, 1.0)
    for i in range(14):
        a = 2 * math.pi * i / 14 + 0.2
        rr = (142 if i % 2 == 0 else 96) * hk[i]
        hp.append((rr * math.cos(a), rr * math.sin(a) * 0.96))
    d.fill(smooth_closed(place(hp, 302, 352)), SUN)
    # the bulb is CREAM inside a SUN starburst: BEAM would have matched the
    # halo's value exactly (both V 1.00) and the lamp would have vanished
    bulb = oval(300, 350, 88, 84, 8, n=9, seed=6.1, wob=0.05)
    d.form(bulb, CREAM, lr(300, 350, 88, 84, 6.1), shade=CREAM_DEEP, ol=OL_S)
    # wings splayed OUT off the shoulders -- upright they read as rabbit ears
    for cx, cy, L, Wd, deg, sd in [(154, 206, 138, 92, -48, 1.2),
                                   (226, 200, 122, 84, 42, 3.4)]:
        w = leaf_round(cx, cy, L, Wd, deg=deg)
        d.form(w, CREAM, lr(cx, cy - L * 0.55, Wd * 0.5, L * 0.4, sd),
               shade=CREAM_DEEP, ol=OL_SF)
    d.line("M158,168 C142,120 136,100 120,74", ol=10, col=INK_SOFT)
    d.line("M224,164 C236,116 242,96 260,72", ol=10, col=INK_SOFT)
    d.add(dot(118, 72, 12, INK_SOFT))
    d.add(dot(262, 70, 10, INK_SOFT))
    bd = oval(188, 250, 126, 118, -8, n=11, seed=2.8, wob=0.04)
    d.form(bd, GRASS_DEEP, lr(188, 250, 126, 118, 2.8), shade=GRASS_DARK,
           ol=OL_S)
    d.add(dot(400, 468, 14, SUN))          # one stray spark: the oddity
    d.add(face(186, 254, 136, mass_w=252, default="happy",
               eyes=((-50, -8), (52, -12)), eye_r=(26, 30), mouth=(2, 46),
               mouth_k=0.9, tilt=-4))
    return d.svg()


def rain_cloud():
    """1024.  Very visible during rain: a determined little face and 5 drops."""
    d = Doc(1024, 1024)
    # drops first so the cloud's outline sits over their tops
    drops = [(238, 706, 104, 152, -4, 1.1), (404, 800, 88, 130, 3, 2.3),
             (566, 716, 96, 140, -6, 3.5), (712, 838, 116, 168, 5, 4.7),
             (860, 700, 76, 112, -3, 5.9)]
    for cx, cy, w, h, deg, sd in drops:
        dr = teardrop(cx, cy, w, h, deg, sd)
        d.form(dr, SKY_HI, sweep(cx, cy, w * 0.5, h * 0.5, 0.16, -0.30,
                                 0.06, sd), shade=SKY_DEEP, ol=OL_KF)
    # the cloud mass
    J, B = lobe_profile(12.7, 11, 0.085, (34, 78))
    cl = canopy_blob(506, 386, 402, 246, 11, J, B, start=-92, notch=7)
    d.form(cl, CLOUD_SHADE, lr(506, 386, 402, 246, 4.2, 0.68, 0.24, 0.05),
           shade=CLOUD_DEEP, ol=OL_K)
    # lightning bolt, flat, hard-edged
    bl = poly([(806, 486), (694, 664), (778, 672), (700, 830), (876, 616),
               (790, 606), (884, 480)])
    d.form(bl, SUN, sweep_hard(788, 656, 96, 176, 0.16, -0.24),
           shade=RAY_SHADE, ol=OL_KF)
    d.add(face(452, 396, 392, mass_w=760, default="mischief",
               eyes=((-52, -12), (54, -6)), eye_r=(24, 29), mouth=(4, 52),
               mouth_k=1.05, tilt=-2))
    return d.svg()


def rainbow():
    """1536x1024, renders ~260px wide-arc.  Six flat bands + two foot clouds."""
    d = Doc(1536, 1024)
    CX, CY = 768, 878
    RXO, RYO = 688, 758
    BANDS = [(FRUIT, 1.00), (ACCENT, 1.06), (SUN, 0.96), (GRASS, 1.02),
             (SKY_HI, 0.98), (BERRY, 1.04)]         # one band deliberately fat
    tot = sum(b[1] for b in BANDS)
    step_x = (RXO - 252) / tot
    step_y = (RYO - 306) / tot
    rxo, ryo = RXO, RYO
    for col, k in BANDS:
        rxi, ryi = rxo - step_x * k, ryo - step_y * k
        # each band reaches 4px PAST its neighbour: two independently wobbled
        # arcs that merely share a radius leave hairline transparent slivers
        d.fill(arc_band(CX, CY, rxo + 4, ryo + 4, rxi - 4, ryi - 4,
                        179, 358, 44, 0.006, 2.0), col)
        rxo, ryo = rxi, ryi
    # ONE silhouette outline over the whole arc; band seams are colour only
    sil = arc_band(CX, CY, RXO, RYO, rxo, ryo, 179, 358, 44, 0.006, 2.0)
    d.line(sil, ol=11)
    # foot clouds, different sizes, the right one lower (the arc is not mirrored)
    for cx, cy, rx, ry, sd in [(176, 800, 146, 92, 3.1),
                               (1352, 826, 170, 102, 6.4)]:
        J, B = lobe_profile(sd, 9, 0.09, (20, 46))
        cd = canopy_blob(cx, cy, rx, ry, 9, J, B)
        d.form(cd, CREAM, sweep(cx, cy, rx, ry, 0.24, -0.32, 0.07, sd),
               shade=CLOUD_SHADE, ol=11)
    return d.svg()


# =====================================================================
# GARDEN
# =====================================================================
def sprout():
    """1024.  Growth stage 1.  Same soil mound + husk material as prop_seed,
    so seed -> sprout -> plant reads as one family."""
    d = Doc(1024, 1024)
    d.add(contact_ell(508, 968, 268, 26))
    # stem
    st = stem_slim(504, 372, 946, 58, root_seed=17.3, lean=-14.0, w_base=132)
    d.form(st, GRASS, sweep(504, 660, 40, 300, 0.16, -0.24, 0.05, 3.2),
           shade=GRASS_DEEP, ol=OL_K)
    # two cotyledon leaves, deliberately unequal, the bigger one nibbled
    l1 = leaf_round(468, 424, 330, 274, deg=-54, curl=0.14)
    d.form(l1, LEAF, sweep(300, 268, 150, 130, 0.24, -0.34, 0.08, 4.4),
           shade=GRASS, ol=OL_K)
    d.line(vein(468, 424, 330, deg=-54), ol=OL_KF, col=GRASS_DEEP)
    l2 = leaf_round(534, 418, 362, 288, deg=50, curl=-0.12)
    d.form(l2, LEAF, sweep(716, 246, 158, 138, 0.22, -0.34, 0.08, 6.6),
           shade=GRASS, ol=OL_K)
    d.line(vein(534, 418, 362, deg=50), ol=OL_KF, col=GRASS_DEEP)
    # a third baby leaf just breaking -- the oddity
    l3 = leaf_round(520, 552, 138, 112, deg=88, curl=0.10)
    d.form(l3, GRASS, sweep(600, 528, 62, 52, 0.20, -0.30, 0.08, 8.1),
           shade=GRASS_DEEP, ol=OL_KF)
    # the split seed husk, still on the stem, in prop_seed's own material
    for cx, cy, rx, ry, deg, sd in [(430, 862, 92, 64, -22, 2.6),
                                    (592, 878, 80, 58, 18, 5.2)]:
        hu = oval(cx, cy, rx, ry, deg, n=9, seed=sd, wob=0.06)
        d.form(hu, SOIL_LITE, sweep(cx, cy, rx, ry, 0.28, -0.30, 0.07, sd),
               shade=SOIL, ol=OL_KF)
    # soil mound, drawn last so its lip crosses the stem and buries it
    mo = smooth_closed([(238, 968), (286, 906), (392, 878), (508, 872),
                        (626, 882), (730, 908), (782, 966), (700, 986),
                        (508, 992), (312, 986)])
    d.form(mo, SOIL, sweep(508, 930, 272, 60, 0.06, -0.34, 0.06, 7.7),
           shade=SOIL_DEEP, ol=OL_K)
    for cx, cy, r in [(352, 944, 13), (612, 936, 16), (472, 958, 11),
                      (700, 950, 12)]:
        d.add(dot(cx, cy, r, SOIL_DEEP))
    return d.svg()


def lock_sign():
    """1024, renders ~70px, and 4-12 are on screen for a new player.  Calm:
    muted bark and stone, no red, no shout, one small vine for warmth."""
    d = Doc(1024, 1024)
    d.add(contact_ell(510, 960, 148, 22))
    # post
    po = slab(506, 640, 104, 660, 0.09, deg=0.8, skew=0.06)
    d.form(po, BARK, sweep_hard(506, 640, 56, 330, 0.30, 0.12),
           shade=BARK_DEEP, ol=OL_K)
    # plank
    pl = slab(508, 302, 688, 262, 0.10, deg=-2.0, skew=0.03)
    d.form(pl, BARK_LITE, sweep_hard(508, 302, 350, 132, 0.34, 0.14),
           shade=BARK, ol=OL_K)
    for y in (238, 366):
        d.line("M228,%d C420,%d 620,%d 792,%d" % (y, y - 8, y + 6, y - 4),
               ol=8, col=BARK)
    # padlock: shackle first, then the body over its feet
    d.line("M452,322 C444,116 576,112 568,322", ol=76, col=INK)
    d.line("M452,322 C444,116 576,112 568,322", ol=52, col=STEEL_DEEP)
    lb = slab(509, 316, 218, 208, 0.24, deg=1.4, skew=0.05)
    d.form(lb, STEEL, sweep_hard(509, 316, 110, 104, 0.30, 0.06),
           shade=STEEL_DEEP, ol=OL_K)
    d.add(dot(509, 296, 30, STEEL_DARK))
    d.add('<path d="%s" fill="%s"/>'
          % (poly([(496, 306), (524, 306), (534, 380), (486, 380)]),
             STEEL_DARK))
    # a vine up the post -- the oddity, and what keeps the sign gardeny
    d.line("M474,948 C560,876 452,806 540,720 C606,656 500,608 556,540",
           ol=17, col=GRASS_DEEP)
    lf = leaf_round(560, 552, 122, 90, deg=58, curl=0.12)
    d.form(lf, GRASS, sweep(608, 520, 54, 42, 0.22, -0.30, 0.08, 4.2),
           shade=GRASS_DEEP, ol=OL_KF)
    lf2 = leaf_round(492, 800, 96, 74, deg=-64, curl=0.10)
    d.form(lf2, GRASS, sweep(444, 776, 44, 36, 0.22, -0.30, 0.08, 6.3),
           shade=GRASS_DEEP, ol=OL_KF)
    return d.svg()


# =====================================================================
# FX PARTICLES  (see the outline decision in the module docstring)
# =====================================================================
def sparkle():
    """512, additive, 8-30px.  NO outline: black adds nothing under additive
    blending, so an outline would be invisible and would only eat the arms.
    Form instead comes from three concentric flat steps -- RAY_SHADE arms,
    a SUN core (dV .141) and one flat cream chip."""
    d = Doc(512, 512)
    d.fill(smooth_closed(star_pts(252, 246, 206, 4, 0.38, deg=6,
                                  jit=(1.0, 0.88, 1.05, 0.94))), RAY_SHADE)
    d.fill(smooth_closed(star_pts(252, 246, 142, 4, 0.46, deg=6,
                                  jit=(1.0, 0.9, 1.03, 0.95))), SUN)
    d.fill(chip(232, 218, 48, deg=-30), CREAM)
    d.fill(smooth_closed(star_pts(408, 400, 78, 4, 0.40, deg=24,
                                  jit=(1.0, 0.9, 1.06, 0.92))), RAY_SHADE)
    d.fill(smooth_closed(star_pts(408, 400, 50, 4, 0.48, deg=24)), SUN)
    return d.svg()


def celebration_star():
    """1024, additive burst star.  NO outline, same reason as sparkle.  A FAT
    soft-cornered 5-point star -- deliberately a different shape family from
    sky/star, which is crisp and straight-edged."""
    d = Doc(1024, 1024)
    p = star_pts(508, 502, 448, 5, 0.58, deg=-9,
                 jit=(1.0, 0.93, 1.05, 0.90, 1.02))
    body = smooth_closed(p)
    flat_form(d, body, SUN, RAY_SHADE,
              sweep(508, 502, 448, 448, 0.20, -0.34, 0.06, 3.7))
    d.fill(chip(400, 356, 118, deg=-32), CREAM)
    d.fill(chip(322, 452, 54, deg=-26), CREAM)
    return d.svg()


def water_splash():
    """768, opaque, 16-34px.  NO outline: 1.4% of its 485px object lands at
    0.3px at working size, so it would not draw a line, it would only grey
    the blue.  A narrow plume, three flung drops and a cream foam crown --
    four masses, which is all that survives at 16px."""
    d = Doc(768, 768)
    # foam crown: a low mass with three up-lobes, cream over cream-deep
    J, B = lobe_profile(9.4, 9, 0.12, (18, 46))
    d.fill(canopy_blob(384, 566, 232, 78, 9, J, B), CREAM_DEEP)
    d.fill(canopy_blob(378, 552, 214, 62, 9, J, B), CREAM)
    for cx, cy, w, h, deg, sd in [(150, 390, 152, 208, -48, 1.5),
                                  (622, 376, 146, 200, 44, 3.9),
                                  (266, 256, 118, 170, -22, 2.7),
                                  (512, 272, 110, 160, 20, 5.1)]:
        dr = teardrop(cx, cy, w, h, deg, sd)
        flat_form(d, dr, SKY_HI, SKY_DEEP,
                  lr(cx, cy, w * 0.5, h * 0.5, sd, 0.34, -0.16))
    pl = teardrop(386, 314, 214, 396, 3, 7.3)
    flat_form(d, pl, SKY_HI, SKY_DEEP,
              lr(386, 314, 107, 198, 7.3, 0.30, -0.20, 0.05))
    d.fill(chip(344, 236, 52, deg=-24), CREAM)
    d.fill(chip(150, 314, 28, deg=-30), CREAM)
    return d.svg()


def poof_cloud():
    """768, opaque, 30-180px.  OUTLINED at 10px: this is the one fx particle
    that never renders tiny, and a cream puff on a pale sky is nothing but
    its contour."""
    d = Doc(768, 768)
    J, B = lobe_profile(21.3, 13, 0.11, (30, 74))
    pf = canopy_blob(378, 386, 322, 288, 13, J, B, start=-98, notch=9)
    inner = "".join(
        '<path d="%s" fill="none" stroke="%s" stroke-width="15" %s/>'
        % (dd, CREAM_DEEP, RJ)
        for dd in ["M176,314 C226,250 320,240 374,296",
                   "M420,224 C486,206 556,246 568,314",
                   "M226,492 C284,542 370,540 420,492"])
    d.form(pf, CREAM, sweep(378, 386, 322, 288, 0.24, -0.34, 0.07, 5.4),
           shade=CREAM_DEEP, ol=10, inner=inner)
    return d.svg()


# =====================================================================
ASSETS = [
    ("critters/butterfly_pink", butterfly_pink, 768, 768),
    ("critters/butterfly_blue", butterfly_blue, 768, 768),
    ("critters/bee", bee, 768, 768),
    ("critters/ladybug", ladybug, 768, 768),
    ("critters/bluebird", bluebird, 768, 768),
    ("critters/owl", owl, 768, 768),
    ("critters/bat", bat, 768, 768),
    ("sky/moon", moon, 1024, 1024),
    ("sky/star", star, 512, 512),
    ("sky/firefly", firefly, 512, 512),
    ("sky/rain_cloud", rain_cloud, 1024, 1024),
    ("sky/rainbow", rainbow, 1536, 1024),
    ("garden/sprout", sprout, 1024, 1024),
    ("garden/lock_sign", lock_sign, 1024, 1024),
    ("fx/sparkle", sparkle, 512, 512),
    ("fx/poof_cloud", poof_cloud, 768, 768),
    ("fx/water_splash", water_splash, 768, 768),
    ("fx/celebration_star", celebration_star, 1024, 1024),
]


# =====================================================================
# REGISTRATION PASS
# "Keep each asset's existing canvas size and anchor" is not something you
# can eyeball into a point list.  So every asset is rendered once, its alpha
# box is measured, and the drawing is then wrapped in ONE uniform
# translate+scale that lands that box on the alpha box of the claymation PNG
# it replaces (measured live from `art/assets/`, not copied into a table).
# Uniform scale, so outline weight stays the same fraction of object height;
# `min()` on the two axes, so a design with a different aspect can never
# overflow the canvas edge.
# =====================================================================
def clay_box(name):
    """(u0, u1, v0, v1) of the claymation PNG this asset replaces."""
    from PIL import Image
    im = Image.open(os.path.join(HERE, "..", "assets", name + ".png"))
    w, h = im.size
    x0, y0, x1, y1 = im.convert("RGBA").split()[3].getbbox()
    return (x0 / w, x1 / w, y0 / h, y1 / h)


def wrap_xf(svg, tx, ty, s):
    """One uniform transform around the whole drawing.  The clipPaths in
    <defs> are userSpaceOnUse, so they follow their referencing element's
    coordinate system and move with it -- no need to transform them too."""
    i = svg.index("</defs>") + len("</defs>")
    j = svg.rindex("</svg>")
    return (svg[:i] + '\n  <g transform="translate(%.3f,%.3f) scale(%.5f)">'
            % (tx, ty, s) + svg[i:j] + "</g>\n" + svg[j:])


def fit_to(svg, name, w, h, tmp_png):
    from PIL import Image
    if not render("_fit_" + name.split("/")[-1], svg, w, h, tmp_png):
        return svg
    bb = Image.open(tmp_png).convert("RGBA").split()[3].getbbox()
    os.remove(tmp_png)
    if not bb:
        return svg
    x0, y0, x1, y1 = bb
    u0, u1, v0, v1 = clay_box(name)
    tw, th = (u1 - u0) * w, (v1 - v0) * h
    sc = min(tw / float(x1 - x0), th / float(y1 - y0))
    tx = (u0 + u1) * 0.5 * w - sc * (x0 + x1) * 0.5
    ty = (v0 + v1) * 0.5 * h - sc * (y0 + y1) * 0.5
    return wrap_xf(svg, tx, ty, sc)


def main(argv):
    want = set(argv[1:])
    for name, fn, w, h in ASSETS:
        short = name.split("/")[-1]
        if want and short not in want and name not in want:
            continue
        path = os.path.join(OUT, name)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        svg = fit_to(fn(), name, w, h, path + ".fit.png")
        with open(path + ".svg", "w") as fh:
            fh.write(svg.strip() + "\n")
        ok = render(short, svg, w, h, path + ".png")
        print("%-28s %s  %dx%d" % (name, "OK" if ok else "FAIL", w, h))


if __name__ == "__main__":
    main(sys.argv)
