#!/usr/bin/env python3
"""Build flat-vector Alphabet Garden assets: SVG -> transparent PNG via headless Chrome.

Batch 2. Fixes the four failures of batch 1 (FLAT_ART_BRIEF Sec 1):
  1. pure #000000 outlines, round joins/caps, weight 1.2-1.7% of object height
  2. two-tone form blocking: base + one hard-edged shadow clipped to the parent
  3. deliberate irregularity everywhere (no mathematical symmetry)
  4. charm / authored character

Render path: SVG -> HTML wrapper -> headless Chrome screenshot at 2x -> LANCZOS
downsample to 1x.  Never use <use> inside <clipPath> (Chrome renders nothing).
"""
import os
import subprocess
import math

OUT = "/Users/clintonmcleod/AI/letter garden/art/flat"
TMP = ("/private/tmp/claude-501/-Users-clintonmcleod-AI-letter-garden/"
       "ce761231-ba83-4ee2-9c8a-70a03ba16f73/scratchpad/svg2")
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
os.makedirs(OUT, exist_ok=True)
os.makedirs(TMP, exist_ok=True)

# ---- palette (FLAT_ART_BRIEF Sec 3 tokens) -------------------------------
GRASS      = "#7ec850"   # grass
GRASS_DEEP = "#5da23c"   # grass-deep   dV 0.149 from grass
SKY_LO     = "#cdefff"   # sky-lo
SOIL       = "#a9713f"   # soil
SOIL_DEEP  = "#8a5a33"   # soil-deep    dV 0.122 from soil
CREAM      = "#fff7e6"   # cream
SUN        = "#ffd23f"   # sun
SUN_DEEP   = "#f0b429"   # sun-deep
ACCENT     = "#ff9d52"   # accent
BERRY      = "#c65fd1"   # berry
INK        = "#000000"   # ink
INK_SOFT   = "#3f3026"   # ink-soft

# Derived shadow tones. The token table's own shadow pairs land in spec
# (grass dV 0.149, soil dV 0.122) but sun/sun-deep is only dV 0.059 and cream
# has no shadow token at all, so these two are derived by the C4 rule:
# surface hue, slightly more saturated, value dropped into the 0.08-0.18 band.
SUN_SHADE   = "#e8a52a"  # from sun      dV 0.090  S 0.82  H 39
RAY_SHADE   = "#d69526"  # from sun-deep dV 0.102  S 0.82  H 38
CLOUD_SHADE = "#c6d8e6"  # from cream    dV 0.098  S 0.14  H 206 (cooler)
SOIL_LITE   = "#c2884e"  # from soil     dV 0.098  raised clods
HILL_LINE   = "#6ab543"  # from grass    dV 0.074  low-contrast background line


def smooth_closed(pts):
    """Catmull-Rom -> cubic bezier through pts, closed. Hand-drawn wobble."""
    n = len(pts)
    d = "M%.1f,%.1f" % pts[0]
    for i in range(n):
        p0, p1 = pts[(i - 1) % n], pts[i]
        p2, p3 = pts[(i + 1) % n], pts[(i + 2) % n]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6.0, p1[1] + (p2[1] - p0[1]) / 6.0)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6.0, p2[1] - (p3[1] - p1[1]) / 6.0)
        d += " C%.1f,%.1f %.1f,%.1f %.1f,%.1f" % (c1 + c2 + p2)
    return d + " Z"


RJ = 'stroke-linejoin="round" stroke-linecap="round"'

# =========================================================================
# 1. SUN_CHARACTER  1024x1024   object height ~900px -> outline 13px (1.44%)
# =========================================================================
SUN_OL = 13
SCX, SCY = 512, 516

# body: 9-point blob, radii jittered around 248 so it is not a circle
_body_pts = []
for _a, _r in zip(range(0, 360, 40),
                  [252, 244, 250, 241, 254, 246, 251, 243, 249]):
    _t = math.radians(_a)
    _body_pts.append((SCX + _r * math.sin(_t), SCY - _r * math.cos(_t)))
BODY_D = smooth_closed(_body_pts)

# 11 rays, irregular angles, lengths varied +-9%, index 6 is deliberately stubby
RAY_A = [-4, 30, 66, 96, 128, 163, 196, 228, 258, 292, 326]
RAY_L = [412, 396, 424, 384, 416, 404, 322, 420, 392, 408, 400]
RAY_W = [50, 45, 53, 44, 51, 47, 42, 50, 46, 48, 47]
RAY_IN = 204


def ray_path(w, r_out):
    tw = w * 0.68
    yi, yt = -RAY_IN, -r_out
    mid = (r_out - RAY_IN) * 0.42
    return ("M%.1f,%.1f C%.1f,%.1f %.1f,%.1f %.1f,%.1f "
            "A%.1f,%.1f 0 0 1 %.1f,%.1f "
            "C%.1f,%.1f %.1f,%.1f %.1f,%.1f Z") % (
        -w, yi, -w, yi - mid, -tw, yt + tw * 2.2, -tw, yt + tw,
        tw, tw, tw, yt + tw,
        tw, yt + tw * 2.2, w, yi - mid, w, yi)


RAYS = [(ray_path(w, l), a) for a, l, w in zip(RAY_A, RAY_L, RAY_W)]
_ray_shapes = "".join(
    '<path d="%s" transform="translate(%d,%d) rotate(%d)"/>' % (d, SCX, SCY, a)
    for d, a in RAYS)
_ray_fills = "".join(
    '<path d="%s" transform="translate(%d,%d) rotate(%d)" fill="%s"/>'
    % (d, SCX, SCY, a, SUN_DEEP) for d, a in RAYS)
_ray_lines = "".join(
    '<path d="%s" transform="translate(%d,%d) rotate(%d)" fill="none" '
    'stroke="%s" stroke-width="%d" %s/>' % (d, SCX, SCY, a, INK, SUN_OL, RJ)
    for d, a in RAYS)

# hand-drawn diagonal terminator for the ray shadow (light from upper-left)
RAY_SHADOW_D = ("M1090,-80 C940,160 800,400 640,600 "
                "C500,770 400,880 300,1100 L1130,1100 Z")
# hand-drawn wavy underside shadow for the body, routed below the face
BODY_SHADOW_D = ("M230,652 C322,618 396,664 468,644 C540,624 604,672 676,644 "
                 "C734,622 774,650 806,694 L806,880 L230,880 Z")

sun_char = f'''
<svg xmlns="http://www.w3.org/2000/svg" width="1024" height="1024" viewBox="0 0 1024 1024">
  <defs>
    <clipPath id="sunRays">{_ray_shapes}</clipPath>
    <clipPath id="sunBody"><path d="{BODY_D}"/></clipPath>
  </defs>
  <!-- rays: fill, clipped hard-edged shadow, then outline on top -->
  {_ray_fills}
  <g clip-path="url(#sunRays)"><path d="{RAY_SHADOW_D}" fill="{RAY_SHADE}"/></g>
  {_ray_lines}
  <!-- body -->
  <path d="{BODY_D}" fill="{SUN}"/>
  <g clip-path="url(#sunBody)"><path d="{BODY_SHADOW_D}" fill="{SUN_SHADE}"/></g>
  <path d="{BODY_D}" fill="none" stroke="{INK}" stroke-width="{SUN_OL}" {RJ}/>
  <!-- face: eyes not level, not equal, cheeks off-centre, lopsided grin -->
  <circle cx="404" cy="556" r="41" fill="{ACCENT}" opacity="0.5"/>
  <circle cx="624" cy="548" r="36" fill="{ACCENT}" opacity="0.5"/>
  <ellipse cx="442" cy="476" rx="29" ry="38" fill="{INK_SOFT}"
           transform="rotate(-7 442 476)"/>
  <ellipse cx="586" cy="466" rx="27" ry="35" fill="{INK_SOFT}"
           transform="rotate(5 586 466)"/>
  <path d="M414,410 C432,402 456,404 470,412" fill="none" stroke="{SOIL_DEEP}"
        stroke-width="15" {RJ}/>
  <path d="M556,404 C576,388 604,390 618,402" fill="none" stroke="{SOIL_DEEP}"
        stroke-width="15" {RJ}/>
  <path d="M448,556 C478,620 556,626 586,550" fill="none" stroke="{INK_SOFT}"
        stroke-width="22" {RJ}/>
</svg>'''

# =========================================================================
# 2. CLOUD_PUFFY  1024x1024   object height ~490px -> outline 8px (1.63%)
# =========================================================================
CLOUD_OL = 8
_lobes = [(256, 520, 112), (398, 452, 162), (566, 410, 198),
          (728, 476, 140), (846, 534, 98), (300, 648, 54)]  # last = odd puff
CLOUD_BASE_D = ("M170,500 L920,500 "
                "C946,540 940,594 906,626 "
                "C862,664 812,640 762,650 "
                "C706,662 668,626 610,638 "
                "C556,650 520,668 466,652 "
                "C416,637 380,662 330,656 "
                "C270,649 214,660 182,620 "
                "C158,590 152,540 170,500 Z")
_cloud_shapes = ('<path d="%s"/>' % CLOUD_BASE_D) + "".join(
    '<circle cx="%d" cy="%d" r="%d"/>' % c for c in _lobes)
_cloud_fills = ('<path d="%s" fill="%s"/>' % (CLOUD_BASE_D, CREAM)) + "".join(
    '<circle cx="%d" cy="%d" r="%d" fill="%s"/>' % (c + (CREAM,))
    for c in _lobes)
CLOUD_SHADOW_D = ("M100,616 C176,584 232,626 306,604 C380,582 424,624 500,600 "
                  "C570,578 610,600 668,570 C728,540 770,566 826,532 "
                  "C872,504 918,522 962,492 L962,780 L100,780 Z")

cloud = f'''
<svg xmlns="http://www.w3.org/2000/svg" width="1024" height="1024" viewBox="0 0 1024 1024">
  <defs><clipPath id="cloudClip">{_cloud_shapes}</clipPath></defs>
  <!-- black union underlay: stroke 2x outline, silhouette rim survives -->
  <g fill="{INK}" stroke="{INK}" stroke-width="{CLOUD_OL * 2}" {RJ}>
    <path d="{CLOUD_BASE_D}"/>
    {"".join('<circle cx="%d" cy="%d" r="%d"/>' % c for c in _lobes)}
  </g>
  {_cloud_fills}
  <g clip-path="url(#cloudClip)">
    <path d="{CLOUD_SHADOW_D}" fill="{CLOUD_SHADE}"/>
    <!-- internal contour lines: lobe seams, real form work -->
    <path d="M452,300 C400,388 418,486 512,522" fill="none" stroke="{INK}"
          stroke-width="{CLOUD_OL}" {RJ}/>
    <path d="M790,432 C758,492 774,548 832,572" fill="none" stroke="{INK}"
          stroke-width="{CLOUD_OL}" {RJ}/>
    <path d="M268,608 C296,632 316,640 348,640" fill="none" stroke="{INK}"
          stroke-width="{CLOUD_OL}" {RJ}/>
  </g>
</svg>'''

# =========================================================================
# 3. HILL_LAYER  2048x700   far background: NO black outline, low-contrast
#    hue-matched line only (dV 0.074). Crest band strengthened to dV 0.149.
# =========================================================================
HILL_D = ("M0,700 L0,470 "
          "C140,436 300,352 470,318 "
          "C610,290 720,336 830,374 "
          "C930,408 1010,404 1096,368 "
          "C1200,324 1290,254 1418,256 "
          "C1520,258 1580,300 1650,332 "
          "C1706,357 1746,338 1790,318 "
          "C1846,292 1930,306 2048,352 "
          "L2048,700 Z")
hill = f'''
<svg xmlns="http://www.w3.org/2000/svg" width="2048" height="700" viewBox="0 0 2048 700">
  <defs><clipPath id="hillClip"><path d="{HILL_D}"/></clipPath></defs>
  <path d="{HILL_D}" fill="{GRASS}"/>
  <g clip-path="url(#hillClip)">
    <!-- shadow body offset down AND sideways so the lit crest band varies in
         thickness along the ridge instead of being a uniform rim -->
    <path d="{HILL_D}" fill="{GRASS_DEEP}" transform="translate(16,66)"/>
  </g>
  <path d="{HILL_D}" fill="none" stroke="{HILL_LINE}" stroke-width="6" {RJ}/>
</svg>'''

# =========================================================================
# 4. GRASS_TUFT  1024x1024   object height ~600px -> outline 9px (1.5%)
#    Painter's algorithm: every blade individually filled + stroked, so
#    overlaps read as separate blades. Rounded tips via an explicit arc cap.
# =========================================================================
GRASS_OL = 9


def blade(bx, by, tx, ty, hw, tw, bend):
    h = by - ty
    return ("M%.1f,%.1f "
            "C%.1f,%.1f %.1f,%.1f %.1f,%.1f "
            "A%.1f,%.1f 0 0 1 %.1f,%.1f "
            "C%.1f,%.1f %.1f,%.1f %.1f,%.1f Z") % (
        bx - hw, by,
        bx - hw + bend * 0.30, by - h * 0.46,
        tx - tw - bend * 0.10, ty + h * 0.34,
        tx - tw, ty,
        tw, tw, tx + tw, ty,
        tx + tw + bend * 0.10, ty + h * 0.34,
        bx + hw + bend * 0.30, by - h * 0.46,
        bx + hw, by)


def bite(cx, cy, r):
    """Irregular hole as a second subpath; with fill-rule=evenodd it punches a
    nibbled-by-an-insect hole through the shape it is appended to."""
    wob = [1.14, 0.86, 1.06, 0.78, 1.10]
    return smooth_closed([
        (cx + r * wob[k] * math.cos(math.radians(k * 72 + 22)),
         cy + r * wob[k] * math.sin(math.radians(k * 72 + 22)))
        for k in range(5)])


# (base x, base y, tip x, tip y, half width, tip radius, bend)
BLADES = [
    (392, 892, 262, 470, 50, 26, -58),
    (632, 890, 768, 500, 48, 25, 60),
    (462, 896, 424, 306, 54, 28, -26),
    (556, 894, 616, 264, 56, 29, 32),
    (438, 898, 358, 610, 44, 23, -26),
    (596, 898, 686, 634, 42, 22, 28),
]
# the flopped-over blade (deliberate oddity #1): arcs up, then droops right
FLOP_D = ("M684,896 C644,724 700,576 792,532 "
          "C866,496 924,540 928,606 "
          "A30,30 0 0 1 868,608 "
          "C866,582 840,572 812,588 "
          "C744,624 712,748 748,892 Z")
# irregular tufty mound; drawn LAST so blade bases disappear behind it.
# Its top edge is scalloped (more grass), never a smooth plate.
MOUND_D = smooth_closed([
    (282, 892), (322, 826), (368, 848), (412, 806), (462, 830), (508, 800),
    (556, 826), (604, 798), (652, 822), (700, 806), (752, 834), (812, 878),
    (818, 898), (702, 910), (520, 916), (368, 910), (292, 902)])

_gr_parts, _gr_defs = [], []
_all_blades = [(i, blade(*b)) for i, b in enumerate(BLADES)]
_all_blades.append((99, FLOP_D))
# oddity #2: a nibbled bite out of the tall right blade's edge
_all_blades[3] = (3, _all_blades[3][1] + " " + bite(617, 470, 21))
_BITTEN = {3}

# blades back-to-front: outer/lower first, tall centre last
_ORDER = [0, 1, 4, 5, 99, 2, 3]
_bl = dict(_all_blades)
# per-blade side shading: the blade re-drawn offset right/down and clipped to
# itself, leaving a hard-edged shaded flank. Offsets differ per blade.
_OFFS = {0: (46, 16), 1: (40, 14), 2: (50, 18), 3: (52, 12),
         4: (38, 14), 5: (36, 16), 99: (10, 34)}
for idx in _ORDER:
    d = _bl[idx]
    er = ' clip-rule="evenodd"' if idx in _BITTEN else ""
    fr = ' fill-rule="evenodd"' if idx in _BITTEN else ""
    dx, dy = _OFFS[idx]
    _gr_defs.append('<clipPath id="gb%d"><path d="%s"%s/></clipPath>'
                    % (idx, d, er))
    _gr_parts.append('<path d="%s" fill="%s"%s/>' % (d, GRASS, fr))
    _gr_parts.append('<g clip-path="url(#gb%d)"><path d="%s" fill="%s"%s '
                     'transform="translate(%d,%d)"/></g>'
                     % (idx, d, GRASS_DEEP, fr, dx, dy))
    _gr_parts.append('<path d="%s" fill="none" stroke="%s" stroke-width="%d" '
                     '%s/>' % (d, INK, GRASS_OL, RJ))

# mound on top: its outline becomes the ground line across every blade
_gr_defs.append('<clipPath id="gm"><path d="%s"/></clipPath>' % MOUND_D)
_gr_parts.append('<path d="%s" fill="%s"/>' % (MOUND_D, GRASS))
_gr_parts.append('<g clip-path="url(#gm)"><path d="M250,872 C330,846 392,882 '
                 '460,864 C528,846 578,880 640,862 C702,844 758,876 826,856 '
                 'L826,980 L250,980 Z" fill="%s"/></g>' % GRASS_DEEP)
_gr_parts.append('<path d="%s" fill="none" stroke="%s" stroke-width="%d" %s/>'
                 % (MOUND_D, INK, GRASS_OL, RJ))

grass_tuft = ('<svg xmlns="http://www.w3.org/2000/svg" width="1024" '
              'height="1024" viewBox="0 0 1024 1024">\n  <defs>'
              + "".join(_gr_defs) + '</defs>\n  '
              + "\n  ".join(_gr_parts) + '\n</svg>')

# =========================================================================
# 5. DIRT_PLOT  1024x1024   object height ~460px -> outline 8px (1.7%)
#    Reads as a heaped, tilled bed of loose soil: scalloped clod-lumpy top
#    edge, tilled furrow grooves, raised clods, one crooked clod, one stone.
# =========================================================================
DIRT_OL = 7
# A flat tilled PATCH lying on the ground -- deliberately 2.4:1 wide and low so
# it cannot read as a dome/loaf/cookie. Its silhouette is broken open by clods
# that straddle the outline, it carries three obvious tilled rows, and loose
# crumbs have spilled outside the edge.
DIRT_D = smooth_closed([
    (88, 556), (112, 492), (172, 458),
    # crumbly back edge: tight, unequal lumps of turned-over soil
    (228, 420), (286, 388), (340, 416), (394, 364), (450, 398),
    (508, 360), (562, 394), (616, 358), (670, 396), (722, 370),
    (774, 404), (828, 426), (878, 454),
    # settled front edge: calm, so the lumpy back reads as loose soil
    (922, 502), (938, 552), (930, 600), (896, 646), (838, 682), (770, 706),
    (700, 718), (628, 730), (552, 734), (476, 730), (404, 726), (334, 712),
    (268, 700), (204, 678), (148, 646), (108, 604)])
# shaded far side of the bed: hard-edged, wavy, roughly the back quarter
DIRT_BACK_D = ("M20,472 C140,438 240,488 340,452 C440,416 512,470 610,442 "
               "C706,414 782,458 882,428 C932,412 984,434 1004,420 "
               "L1004,280 L20,280 Z")
# tilled rows: a hue-matched groove with a lit crest riding just above it
FURROWS = [("M186,514 C320,484 470,500 610,476 C712,459 792,470 856,490", 18),
           ("M154,592 C300,558 452,574 596,550 C702,533 792,546 878,566", 17),
           ("M196,666 C324,638 462,652 602,630 C692,616 766,626 828,640", 15)]
_furrow_svg = ""
for _d, _w in FURROWS:
    _furrow_svg += ('<path d="%s" fill="none" stroke="%s" stroke-width="%d" '
                    '%s/>' % (_d, SOIL_DEEP, _w, RJ))
    _furrow_svg += ('<g transform="translate(0,-%d)"><path d="%s" fill="none" '
                    'stroke="%s" stroke-width="%d" %s/></g>'
                    % (_w - 3, _d, SOIL_LITE, max(8, _w - 8), RJ))


def clod(cx, cy, s, rot, col, wob, squash=0.88):
    """Chunky soil clod: 7 points at jittered radii, so no two are alike and
    none of them is a circle."""
    pts = []
    for k in range(7):
        a = math.radians(k * (360.0 / 7) + 14)
        r = s * wob[k]
        pts.append((cx + r * math.cos(a), cy + r * squash * math.sin(a)))
    tr = ' transform="rotate(%d %d %d)"' % (rot, cx, cy) if rot else ""
    return ('<path d="%s" fill="%s" stroke="%s" stroke-width="6" %s%s/>'
            % (smooth_closed(pts), col, INK, RJ, tr))


# clods seated ON the outline (ragged rim -> not a baked good), plus loose
# crumbs spilled fully outside it. Index 4 is deliberately crooked.
_clod_svg = "".join([
    clod(292, 400, 40, -12, SOIL_LITE, [1.0, .88, 1.10, .92, 1.06, .86, .96]),
    clod(512, 376, 36, 24, SOIL_LITE, [.90, 1.12, .96, 1.04, .86, 1.08, .94]),
    clod(872, 470, 34, -6, SOIL, [1.10, .92, 1.02, .86, 1.12, .94, 1.0]),
    clod(400, 714, 36, 40, SOIL, [.94, 1.06, .88, 1.12, .92, 1.0, 1.08]),
    clod(506, 552, 44, -34, SOIL_LITE,
         [1.12, .90, 1.02, .94, .86, 1.10, .96]),            # crooked
    clod(776, 694, 31, 16, SOIL_LITE, [.90, 1.02, 1.12, .88, .98, 1.06, .92]),
    clod(140, 750, 28, -20, SOIL, [1.06, .90, .96, 1.12, .88, 1.0, .94]),
    clod(234, 784, 22, 34, SOIL_LITE, [.94, 1.10, .88, 1.02, 1.12, .90, 1.0]),
    clod(874, 750, 26, 8, SOIL, [1.12, .90, 1.0, .88, 1.08, .94, 1.02]),
])
# small freckle crumbs, no outline (dressing marks, not props)
FRECKLES = [(232, 552, 15, 10, -18), (444, 646, 13, 9, 12),
            (688, 610, 14, 9, -8), (846, 528, 12, 8, 20),
            (330, 470, 11, 8, 6), (596, 500, 10, 7, -14)]
_freckle_svg = "".join(
    '<ellipse cx="%d" cy="%d" rx="%d" ry="%d" fill="%s" '
    'transform="rotate(%d %d %d)"/>' % (x, y, rx, ry, SOIL_DEEP, r, x, y)
    for x, y, rx, ry, r in FRECKLES)
_STONE_D = smooth_closed([(158, 596), (196, 578), (224, 602),
                          (206, 634), (168, 628)])

dirt_plot = f'''
<svg xmlns="http://www.w3.org/2000/svg" width="1024" height="1024" viewBox="0 0 1024 1024">
  <defs><clipPath id="dirtClip"><path d="{DIRT_D}"/></clipPath></defs>
  <path d="{DIRT_D}" fill="{SOIL}"/>
  <g clip-path="url(#dirtClip)">
    <path d="{DIRT_BACK_D}" fill="{SOIL_DEEP}"/>
    {_furrow_svg}
    {_freckle_svg}
  </g>
  <path d="{DIRT_D}" fill="none" stroke="{INK}" stroke-width="{DIRT_OL}" {RJ}/>
  {_clod_svg}
  <!-- one small stone turned up by the digging -->
  <path d="{_STONE_D}" fill="{CREAM}" stroke="{INK}" stroke-width="6" {RJ}/>
</svg>'''

# =========================================================================
# 6. BUSH_SHRUB  1024x1024   object height ~540px -> outline 9px (1.67%)
#    Deliberately NOT cloud language: many small unequal leaf scallops, a
#    settled flat-ish base, a bitten notch, and three berries.
# =========================================================================
BUSH_OL = 9
# Scalloped foliage mass: 15 SMALL unequal leaf bumps around a dome. This is
# the deliberate opposite of the cloud's 5 big smooth lobes.
_BUSH_JIT = [1.00, 0.93, 1.06, 0.97, 1.09, 0.91, 1.04, 1.00,
             1.07, 0.94, 1.02, 0.89, 1.05, 0.96, 1.00, 0.98]
_BUSH_BUL = [66, 82, 58, 90, 70, 48, 86, 62, 94, 72, 54, 88, 68, 80, 60]
_bp = []
_N = 16
for _i in range(_N):
    _ang = math.radians(206 - _i * (232.0 / (_N - 1)))
    _k = _BUSH_JIT[_i]
    _bp.append((512 + 322 * _k * math.cos(_ang),
                584 - 278 * _k * math.sin(_ang)))
_bd = "M%.1f,%.1f" % _bp[0]
for _i in range(_N - 1):
    _p1, _p2 = _bp[_i], _bp[_i + 1]
    _dx, _dy = _p2[0] - _p1[0], _p2[1] - _p1[1]
    _L = math.hypot(_dx, _dy)
    _nx, _ny = _dy / _L, -_dx / _L          # outward normal, clockwise, y-down
    _b = _BUSH_BUL[_i]
    # oddity: bump 11 is a shallow inward notch (a bitten leaf), not a bump
    if _i == 11:
        _b = -22
    _cx = (_p1[0] + _p2[0]) / 2 + _nx * _b
    _cy = (_p1[1] + _p2[1]) / 2 + _ny * _b
    _bd += " Q%.1f,%.1f %.1f,%.1f" % (_cx, _cy, _p2[0], _p2[1])
# settled base: the bush sits on the ground, but the base is scalloped too so
# it never reads as a slab. Bumps point downward, sizes deliberately unequal.
_base_pts = [(_bp[-1][0], _bp[-1][1]), (742, 784), (638, 800), (528, 808),
             (420, 802), (318, 790), (_bp[0][0], _bp[0][1])]
_base_bul = [58, 34, 44, 26, 50, 62]
for _i in range(len(_base_pts) - 1):
    _p1, _p2 = _base_pts[_i], _base_pts[_i + 1]
    _dx, _dy = _p2[0] - _p1[0], _p2[1] - _p1[1]
    _L = math.hypot(_dx, _dy)
    _nx, _ny = _dy / _L, -_dx / _L
    _b = _base_bul[_i]
    _cx = (_p1[0] + _p2[0]) / 2 + _nx * _b
    _cy = (_p1[1] + _p2[1]) / 2 + _ny * _b
    _bd += " Q%.1f,%.1f %.1f,%.1f" % (_cx, _cy, _p2[0], _p2[1])
_bd += " Z"
BUSH_D = _bd
# shadow follows the leaf clumps and sweeps up the right side (light upper-left)
BUSH_SHADOW_D = ("M110,644 C160,676 196,632 244,660 C296,690 328,644 378,672 "
                 "C432,702 462,652 514,678 C568,706 598,656 650,678 "
                 "C704,700 730,640 774,646 C818,652 838,590 872,540 "
                 "L940,540 L940,880 L110,880 Z")

bush_shrub = f'''
<svg xmlns="http://www.w3.org/2000/svg" width="1024" height="1024" viewBox="0 0 1024 1024">
  <defs><clipPath id="bushClip"><path d="{BUSH_D}"/></clipPath></defs>
  <path d="{BUSH_D}" fill="{GRASS}"/>
  <g clip-path="url(#bushClip)">
    <path d="{BUSH_SHADOW_D}" fill="{GRASS_DEEP}"/>
    <!-- internal contour lines: overlapping leaf clumps do the form work -->
    <path d="M262,432 C332,462 356,538 322,616" fill="none" stroke="{INK}"
          stroke-width="{BUSH_OL}" {RJ}/>
    <path d="M700,368 C650,420 660,492 712,532" fill="none" stroke="{INK}"
          stroke-width="{BUSH_OL}" {RJ}/>
    <path d="M486,320 C444,380 460,448 514,486" fill="none" stroke="{INK}"
          stroke-width="{BUSH_OL}" {RJ}/>
    <path d="M556,660 C606,632 620,584 604,536" fill="none" stroke="{INK}"
          stroke-width="{BUSH_OL}" {RJ}/>
    <path d="M386,690 C428,668 448,624 442,578" fill="none" stroke="{INK}"
          stroke-width="{BUSH_OL}" {RJ}/>
  </g>
  <path d="{BUSH_D}" fill="none" stroke="{INK}" stroke-width="{BUSH_OL}" {RJ}/>
  <!-- three unequal berries, clustered off-centre: the saturation accent -->
  <circle cx="386" cy="470" r="30" fill="{BERRY}" stroke="{INK}"
          stroke-width="7" {RJ}/>
  <circle cx="444" cy="534" r="22" fill="{BERRY}" stroke="{INK}"
          stroke-width="7" {RJ}/>
  <circle cx="628" cy="436" r="26" fill="{BERRY}" stroke="{INK}"
          stroke-width="7" {RJ}/>
</svg>'''

# =========================================================================
ASSETS = [
    ("sun_character", sun_char,   1024, 1024),
    ("cloud_puffy",   cloud,      1024, 1024),
    ("hill_layer",    hill,       2048,  700),
    ("grass_tuft",    grass_tuft, 1024, 1024),
    ("dirt_plot",     dirt_plot,  1024, 1024),
    ("bush_shrub",    bush_shrub, 1024, 1024),
]

HTML = ('<!doctype html><meta charset="utf-8">'
        '<style>html,body{margin:0;padding:0;background:transparent;}'
        'svg{display:block;}</style>')


def render(name, svg, w, h, out_png, scale=2):
    html_path = os.path.join(TMP, name + ".html")
    with open(html_path, "w") as f:
        f.write(HTML + svg)
    big = out_png + ".2x.png"
    r = subprocess.run([
        CHROME, "--headless", "--disable-gpu", "--hide-scrollbars",
        "--force-device-scale-factor=%d" % scale,
        "--default-background-color=00000000",
        "--window-size=%d,%d" % (w, h), "--screenshot=" + big,
        "file://" + html_path,
    ], capture_output=True, text=True)
    if not os.path.exists(big):
        print(r.stderr[-800:])
        return False
    from PIL import Image
    im = Image.open(big).convert("RGBA")
    im = im.resize((w, h), Image.LANCZOS)
    im.save(out_png)
    os.remove(big)
    return True


if __name__ == "__main__":
    for name, svg, w, h in ASSETS:
        with open(os.path.join(OUT, name + ".svg"), "w") as f:
            f.write(svg.strip() + "\n")
        png = os.path.join(OUT, name + ".png")
        ok = render(name, svg, w, h, png)
        print("%-15s %s  %s" % (name, "OK" if ok else "FAIL",
                                "%dx%d" % (w, h)))
