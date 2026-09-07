#!/usr/bin/env python3
"""Build flat-vector Alphabet Garden assets: SVG -> transparent PNG via headless Chrome.

Batch 3.  Batch 2 failed review (C1 5, C2 6, C4 6, C5 5, C7 4, C8 4).  What changed:

  1. REVISED PALETTE.  Batch 2 measured median fill S 0.63 against the reference's
     0.27, 86.4% of pixels above the S 0.55 ceiling.  Every hex is now the
     desaturated token from FLAT_ART_BRIEF Sec 3 (revised).
  2. HILL GETS ITS OWN BACK-LAYER PALETTE.  It used to share the exact two hexes
     with the foreground bush and grass, so the layers vanished into each other.
  3. HARD BUG: grass_tuft had a 744px fully-transparent enclosed hole punched by
     the evenodd `bite()` oddity.  bite() is deleted; the oddity is now an edge
     notch that is open to the silhouette.
  4. HARD BUG: hill_layer was stroked #6ab543 w6 with the viewBox clipping the
     outer half, leaving an 18862px hairline seam on three edges.  The stroke is
     gone; the hill is also now horizontally tileable (y matches at x=0/x=W).
  5. SHADING FOLLOWS GEOMETRY.  Batch 2 reused one wavy horizontal band on the
     sun, cloud, bush and dirt.  Every shadow is now built by the same honest
     construction: fill the shape with its shadow tone, then overlay the SAME
     path shifted toward the light and clipped to itself.  The lit/shade
     boundary is therefore always concentric with the form that owns it.
  6. DIRT IS AN EXCAVATED HOLE, not a mound: saddle-notched dug rim, interior a
     step darker than the lip, lit far wall, flat ground line, round-capped
     scrapes.  The cream pebble (an every-plot constant = instancing) is gone.
  7. GRASS SILHOUETTE REBUILT: no hooked blade, real negative-space gaps, widths
     varied 52-112px.
  8. CONTACT SHADOWS on plot, bush and grass.
  9. THREE VARIANTS of every prop (recolour within band + shape change), plus
     three narrative props (seed, trowel, worm) to kill the instancing read.
 10. SUN FACE: eyes widened to w/h 1.15 and dropped below the disc midline,
     brows moved to the `brow` token, six swappable <g id="face-*"> expressions.

Render path: SVG -> HTML wrapper -> headless Chrome screenshot at 2x -> LANCZOS
downsample to 1x.  Never use <use> inside <clipPath> (Chrome renders nothing).
"""
import os
import subprocess
import math

OUT = "/Users/clintonmcleod/AI/letter garden/art/flat"
TMP = ("/private/tmp/claude-501/-Users-clintonmcleod-AI-letter-garden/"
       "ce761231-ba83-4ee2-9c8a-70a03ba16f73/scratchpad/svg3")
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
os.makedirs(OUT, exist_ok=True)
os.makedirs(TMP, exist_ok=True)

# ---- palette (FLAT_ART_BRIEF Sec 3, REVISED) ------------------------------
# Layer 1 - foreground / interactive (full black outlines)
GRASS      = "#9ddb76"   # grass          S .461 V .859
GRASS_DEEP = "#79b85c"   # grass-deep     S .500 V .722   dV .137
SOIL       = "#c2946b"   # soil           S .448 V .761
SOIL_DEEP  = "#a37855"   # soil-deep      S .478 V .639   dV .122
SOIL_LITE  = "#dbad7f"   # soil-lite      S .420 V .859
SOIL_DARK  = "#8a6345"   # soil-dark      S .500 V .541   dV .098 from soil-deep
SUN        = "#ffe07a"   # sun            S .522 V 1.00
SUN_DEEP   = "#f0c665"   # sun-deep       S .579 V .941
SUN_SHADE  = "#eebf5c"   # sun-shade      S .613 V .933
RAY_SHADE  = "#dbab58"   # ray-shade      S .598 V .859
CREAM      = "#fff7e6"   # cream          S .098 V 1.00
CLOUD_SHADE = "#c6d8e6"  # cloud-shade    S .139 V .902   dV .098
# Layer 2 - far background (NO black outline, must sit back)
HILL       = "#d0edbe"   # hill-far       S .198 V .929
HILL_DEEP  = "#badea9"   # hill-far-deep  S .239 V .871
# accents & ink
ACCENT     = "#ffb77e"   # accent         S .506 V 1.00
BERRY      = "#c65fd1"   # berry          S .545 V .820
INK        = "#000000"
INK_SOFT   = "#3f3026"   # eyes
BROW       = "#6b5342"   # brows - deliberately NOT the eye hex
# derived here, added back into FLAT_ART_BRIEF Sec 3 for the next author
CONTACT    = "#93d56c"   # ground-contact  hue-matched to grass, dV .024
STONE      = "#b8c2cc"   # stone / metal   S .098 V .800
STONE_DEEP = "#9aa6b3"   # stone-deep      dV .098
WORM       = "#f0a8a0"   # worm            S .333 V .941
WORM_DEEP  = "#d98f88"   # worm-deep       dV .090

# variant bands (recolour WITHIN the S .35-.55 / V .70-.90 band, C7)
GRASS_V = [("#9ddb76", "#79b85c"), ("#a8de88", "#86bd6b"), ("#8fd472", "#6faf55")]
SOIL_V = [("#c2946b", "#a37855", "#dbad7f", "#8a6345"),
          ("#cb9d74", "#ab8060", "#e2b689", "#916b4d"),
          ("#b98a63", "#9a704e", "#d3a577", "#82603f")]
CLOUD_V = ["#c6d8e6", "#cbdae4", "#c0d5e8"]
HILL_V = [("#d0edbe", "#badea9"), ("#c9ecc6", "#b4ddb1"), ("#d6ecb8", "#c1dda8")]

RJ = 'stroke-linejoin="round" stroke-linecap="round"'


def smooth_closed(pts):
    """Catmull-Rom -> cubic bezier through pts, closed.  Hand-drawn wobble."""
    n = len(pts)
    d = "M%.1f,%.1f" % tuple(pts[0])
    for i in range(n):
        p0, p1 = pts[(i - 1) % n], pts[i]
        p2, p3 = pts[(i + 1) % n], pts[(i + 2) % n]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6.0, p1[1] + (p2[1] - p0[1]) / 6.0)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6.0, p2[1] - (p3[1] - p1[1]) / 6.0)
        d += " C%.1f,%.1f %.1f,%.1f %.1f,%.1f" % (
            c1 + c2 + (p2[0], p2[1]))
    return d + " Z"


def twotone(cid, d, base, shade, dx, dy, rot=0.0, rcx=0, rcy=0):
    """Honest two-tone form blocking.

    Fill the shape with its SHADOW tone, then lay the *same path* back down
    shifted toward the light source (up-left) and clipped to itself.  What is
    left uncovered is a crescent that hugs the lower-right rim and is, by
    construction, concentric with the form that owns it.  No decorative wavy
    band, no formula shared between unrelated objects.  An optional small
    rotation makes the crescent breathe in thickness along its length.
    """
    tr = "translate(%.1f,%.1f)" % (dx, dy)
    if rot:
        tr += " rotate(%.2f %d %d)" % (rot, rcx, rcy)
    return ('<path d="%s" fill="%s"/>'
            '<g clip-path="url(#%s)">'
            '<path d="%s" fill="%s" transform="%s"/></g>'
            % (d, shade, cid, d, base, tr))


def clip(cid, d):
    return '<clipPath id="%s"><path d="%s"/></clipPath>' % (cid, d)


def contact(cx, cy, rx, ry, col=CONTACT):
    """Hard-edged hue-matched contact shadow.  Never grey, never blurred."""
    return ('<ellipse cx="%d" cy="%d" rx="%d" ry="%d" fill="%s"/>'
            % (cx, cy, rx, ry, col))


# =========================================================================
# 1. SUN_CHARACTER   1024x1024
#    object height (rays included) ~900px -> outline 13px = 1.44%
# =========================================================================
SUN_OL = 13
SCX, SCY = 512, 516

_body_pts = []
for _a, _r in zip(range(0, 360, 40),
                  [252, 244, 250, 241, 254, 246, 251, 243, 249]):
    _t = math.radians(_a)
    _body_pts.append((SCX + _r * math.sin(_t), SCY - _r * math.cos(_t)))
BODY_D = smooth_closed(_body_pts)

# 11 rays, irregular angles, lengths varied +-9%, index 6 deliberately stubby
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
# rays: shadow tone first, then the SAME rays shifted toward the light.  Every
# ray therefore carries a shaded flank on its own lower-right side, at an angle
# that agrees with the body terminator instead of contradicting it.
_ray_shade = "".join(
    '<path d="%s" transform="translate(%d,%d) rotate(%d)" fill="%s"/>'
    % (d, SCX, SCY, a, RAY_SHADE) for d, a in RAYS)
_ray_lit = "".join(
    '<path d="%s" transform="translate(%d,%d) rotate(%d)" fill="%s"/>'
    % (d, SCX - 26, SCY - 32, a, SUN_DEEP) for d, a in RAYS)
_ray_lines = "".join(
    '<path d="%s" transform="translate(%d,%d) rotate(%d)" fill="none" '
    'stroke="%s" stroke-width="%d" %s/>' % (d, SCX, SCY, a, INK, SUN_OL, RJ)
    for d, a in RAYS)

# ---- face parts.  Every expression is <=3 marks off the default: eyes,
#      mouth, brows.  Cheeks are constant and live outside the groups.
EYE_L = (440, 528)      # both below the disc midline (y 516), not level
EYE_R = (582, 534)
EYE_RX, EYE_RY = 34, 29.5      # w/h = 1.153 -> slightly wider than tall


def _eyes_open(rx=EYE_RX, ry=EYE_RY):
    return ('<ellipse cx="%d" cy="%d" rx="%.1f" ry="%.1f" fill="%s" '
            'transform="rotate(-6 %d %d)"/>'
            '<ellipse cx="%d" cy="%d" rx="%.1f" ry="%.1f" fill="%s" '
            'transform="rotate(5 %d %d)"/>'
            % (EYE_L[0], EYE_L[1], rx, ry, INK_SOFT, EYE_L[0], EYE_L[1],
               EYE_R[0], EYE_R[1], rx * 0.94, ry * 0.94, INK_SOFT,
               EYE_R[0], EYE_R[1]))


def _eyes_arc(lift=1.0):
    """Closed happy eyes: upward round-capped arcs."""
    return ('<path d="M%d,%d C%d,%d %d,%d %d,%d" fill="none" stroke="%s" '
            'stroke-width="19" %s/>'
            '<path d="M%d,%d C%d,%d %d,%d %d,%d" fill="none" stroke="%s" '
            'stroke-width="18" %s/>'
            % (EYE_L[0] - 36, EYE_L[1] + 8,
               EYE_L[0] - 16, EYE_L[1] - 26 * lift,
               EYE_L[0] + 16, EYE_L[1] - 27 * lift,
               EYE_L[0] + 36, EYE_L[1] + 5, INK_SOFT, RJ,
               EYE_R[0] - 34, EYE_R[1] + 6,
               EYE_R[0] - 14, EYE_R[1] - 25 * lift,
               EYE_R[0] + 15, EYE_R[1] - 24 * lift,
               EYE_R[0] + 34, EYE_R[1] + 8, INK_SOFT, RJ))


def _eyes_half():
    """Half-lidded: flat top edge, curved bottom.  Reads sly, not sleepy."""
    def one(cx, cy, rx, ry):
        return ('<path d="M%.1f,%.1f L%.1f,%.1f C%.1f,%.1f %.1f,%.1f '
                '%.1f,%.1f Z" fill="%s"/>'
                % (cx - rx, cy - ry * 0.15, cx + rx, cy - ry * 0.42,
                   cx + rx * 0.9, cy + ry * 0.86, cx - rx * 0.9,
                   cy + ry * 0.92, cx - rx, cy - ry * 0.15, INK_SOFT))
    return one(*EYE_L, rx=EYE_RX, ry=EYE_RY) + one(
        *EYE_R, rx=EYE_RX * 0.94, ry=EYE_RY * 0.94)


def _brows(lx1, ly1, lcx, lcy, lx2, ly2, rx1, ry1, rcx, rcy, rx2, ry2):
    return ('<path d="M%d,%d Q%d,%d %d,%d" fill="none" stroke="%s" '
            'stroke-width="15" %s/>'
            '<path d="M%d,%d Q%d,%d %d,%d" fill="none" stroke="%s" '
            'stroke-width="14" %s/>'
            % (lx1, ly1, lcx, lcy, lx2, ly2, BROW, RJ,
               rx1, ry1, rcx, rcy, rx2, ry2, BROW, RJ))


BROW_DEFAULT = _brows(404, 470, 442, 452, 478, 468,
                      548, 474, 586, 454, 622, 472)
BROW_HIGH = _brows(404, 442, 442, 420, 478, 440,
                   548, 448, 586, 424, 622, 446)
BROW_SAD = _brows(404, 482, 444, 452, 480, 448,      # inner ends lifted
                  550, 452, 584, 450, 622, 484)
BROW_MISCHIEF = _brows(404, 480, 442, 462, 478, 478,  # left low
                       548, 452, 586, 424, 624, 446)  # right high

MOUTH_DEFAULT = ('<path d="M448,596 C482,656 560,660 594,592" fill="none" '
                 'stroke="%s" stroke-width="22" %s/>' % (INK_SOFT, RJ))
MOUTH_BIG = ('<path d="M424,586 C468,676 578,682 618,580" fill="none" '
             'stroke="%s" stroke-width="24" %s/>' % (INK_SOFT, RJ))
MOUTH_LAUGH = (
    '<path d="M430,580 C478,566 566,568 612,578 C606,660 552,700 512,698 '
    'C470,696 434,652 430,580 Z" fill="%s"/>'
    '<path d="M438,588 C482,576 560,578 604,586 C602,600 596,606 588,604 '
    'C544,596 480,594 448,602 C440,604 436,598 438,588 Z" fill="%s"/>'
    % (INK_SOFT, CREAM))
MOUTH_O = ('<ellipse cx="516" cy="622" rx="31" ry="39" fill="%s"/>'
           % INK_SOFT)
MOUTH_SAD = ('<path d="M452,640 C486,586 562,584 596,634" fill="none" '
             'stroke="%s" stroke-width="21" %s/>' % (INK_SOFT, RJ))
MOUTH_SMIRK = ('<path d="M442,606 C486,652 566,646 606,568" fill="none" '
               'stroke="%s" stroke-width="21" %s/>' % (INK_SOFT, RJ))

FACES = [
    ("default", _eyes_open() + BROW_DEFAULT + MOUTH_DEFAULT),
    ("happy", _eyes_arc() + BROW_HIGH + MOUTH_BIG),
    ("laughing", _eyes_arc(1.25) + BROW_HIGH + MOUTH_LAUGH),
    ("surprised", _eyes_open(36, 34) + BROW_HIGH + MOUTH_O),
    ("sad", _eyes_open() + BROW_SAD + MOUTH_SAD),
    ("mischievous", _eyes_half() + BROW_MISCHIEF + MOUTH_SMIRK),
]

CHEEKS = ('<circle cx="388" cy="598" r="40" fill="%s" opacity="0.5"/>'
          '<circle cx="642" cy="604" r="35" fill="%s" opacity="0.5"/>'
          % (ACCENT, ACCENT))


def build_sun(visible="default"):
    groups = "".join(
        '<g id="face-%s"%s>%s</g>'
        % (n, "" if n == visible else ' display="none"', body)
        for n, body in FACES)
    return f'''
<svg xmlns="http://www.w3.org/2000/svg" width="1024" height="1024" viewBox="0 0 1024 1024">
  <defs>
    <clipPath id="sunRays">{_ray_shapes}</clipPath>
    <clipPath id="sunBody"><path d="{BODY_D}"/></clipPath>
  </defs>
  <!-- RAYS.  Shadow tone laid down first, then the same rays shifted 26,32
       toward the light, clipped to the ray union.  Each ray keeps a shaded
       flank on its own lower-right side. -->
  {_ray_shade}
  <g clip-path="url(#sunRays)">{_ray_lit}</g>
  {_ray_lines}
  <!-- BODY.  Terminator = the silhouette itself, shifted 44,52 toward the
       light.  What is left is a crescent concentric with the disc, hugging the
       lower-right rim, with no flat rim terminations.  Agrees with the rays. -->
  {twotone("sunBody", BODY_D, SUN, SUN_SHADE, -44, -52, 2.0, SCX, SCY)}
  <path d="{BODY_D}" fill="none" stroke="{INK}" stroke-width="{SUN_OL}" {RJ}/>
  <!-- FACE.  Eyes w/h 1.15, sitting just below the disc midline (y 516).
       Brows on the `brow` token, never the eye hex.  Six swappable groups. -->
  {CHEEKS}
  {groups}
</svg>'''


# =========================================================================
# 2. CLOUD_PUFFY   1024x1024   object height ~490px -> outline 8px = 1.63%
# =========================================================================
CLOUD_OL = 8
CLOUD_LOBES = [
    [(256, 520, 112), (398, 452, 162), (566, 410, 198),
     (728, 476, 140), (846, 534, 98), (300, 648, 54)],
    [(268, 546, 96), (376, 470, 144), (520, 428, 176), (664, 452, 158),
     (812, 520, 120), (872, 596, 62)],
    [(292, 512, 128), (452, 448, 178), (626, 464, 150),
     (766, 522, 106), (350, 636, 46), (560, 372, 118)],
]
CLOUD_BASE = [
    ("M170,500 L920,500 C946,540 940,594 906,626 C862,664 812,640 762,650 "
     "C706,662 668,626 610,638 C556,650 520,668 466,652 C416,637 380,662 "
     "330,656 C270,649 214,660 182,620 C158,590 152,540 170,500 Z"),
    ("M186,540 L900,540 C930,578 922,632 884,660 C840,692 792,668 742,676 "
     "C688,684 652,652 596,662 C544,671 508,690 456,676 C408,663 372,686 "
     "324,680 C268,673 216,682 190,644 C170,616 168,570 186,540 Z"),
    ("M206,514 L836,514 C864,552 858,606 822,636 C780,670 730,646 682,656 "
     "C628,667 592,634 538,644 C486,654 452,672 400,658 C352,645 318,668 "
     "272,662 C218,655 176,660 194,616 C182,588 190,542 206,514 Z"),
]


def build_cloud(i):
    lobes, base, shade = CLOUD_LOBES[i], CLOUD_BASE[i], CLOUD_V[i]
    circles = "".join('<circle cx="%d" cy="%d" r="%d"/>' % c for c in lobes)
    shapes = ('<path d="%s"/>' % base) + circles
    fills = ('<path d="%s" fill="%s"/>' % (base, shade)) + "".join(
        '<circle cx="%d" cy="%d" r="%d" fill="%s"/>' % (c + (shade,))
        for c in lobes)
    # lit pass: the SAME lobe union shifted toward the light, clipped to the
    # silhouette.  Every puff keeps its own crescent, including inside the
    # scallops between lobes -- the shadow describes the lobes, not a waterline.
    lit = ('<g transform="translate(-30,-34)">'
           + ('<path d="%s" fill="%s"/>' % (base, CREAM))
           + "".join('<circle cx="%d" cy="%d" r="%d" fill="%s"/>'
                     % (c + (CREAM,)) for c in lobes) + '</g>')
    seams = ["M452,300 C400,388 418,486 512,522",
             "M790,432 C758,492 774,548 832,572",
             "M268,608 C296,632 316,640 348,640"]
    if i == 1:
        seams = ["M406,326 C356,410 372,494 460,528",
                 "M736,344 C700,414 716,494 782,530",
                 "M840,600 C812,628 790,636 758,636"]
    if i == 2:
        seams = ["M498,330 C444,412 460,502 552,538",
                 "M690,388 C650,452 662,528 726,562",
                 "M318,596 C346,622 366,630 398,630"]
    seam_svg = "".join(
        '<path d="%s" fill="none" stroke="%s" stroke-width="%d" %s/>'
        % (s, INK, CLOUD_OL, RJ) for s in seams)
    return f'''
<svg xmlns="http://www.w3.org/2000/svg" width="1024" height="1024" viewBox="0 0 1024 1024">
  <defs><clipPath id="cloudClip">{shapes}</clipPath></defs>
  <!-- black union underlay: stroke 2x outline, silhouette rim survives -->
  <g fill="{INK}" stroke="{INK}" stroke-width="{CLOUD_OL * 2}" {RJ}>
    <path d="{base}"/>{circles}
  </g>
  {fills}
  <g clip-path="url(#cloudClip)">
    {lit}
    <!-- internal contour lines: lobe seams, real form work -->
    {seam_svg}
  </g>
</svg>'''


# =========================================================================
# 3. HILL_LAYER   2048x700   far background.
#    Layer 2 palette, never shared with the foreground.  NO outline at all --
#    the old #6ab543 stroke sat half outside the viewBox and left a 2-3px
#    hairline on the left, right and bottom edges that would have tiled as a
#    visible seam.  The ridge also starts and ends at the same y so the band
#    tiles horizontally without a step.
# =========================================================================
HILL_RIDGES = [
    ("M0,700 L0,452 C90,452 190,430 300,404 C420,376 520,412 640,438 "
     "C760,464 860,436 980,396 C1110,352 1210,300 1340,304 C1450,308 "
     "1520,352 1610,382 C1690,408 1760,384 1830,368 C1912,350 1984,452 "
     "2048,452 L2048,700 Z"),
    ("M0,700 L0,486 C86,486 176,462 280,436 C396,406 496,442 612,462 "
     "C728,482 828,442 946,410 C1068,378 1166,336 1290,344 C1398,352 "
     "1470,394 1560,418 C1642,440 1716,414 1794,394 C1888,370 1978,486 "
     "2048,486 L2048,700 Z"),
    ("M0,700 L0,424 C80,424 168,398 268,370 C382,338 480,376 594,398 "
     "C712,420 812,376 930,342 C1054,306 1152,364 1276,378 C1382,390 "
     "1456,340 1548,320 C1636,300 1714,332 1798,358 C1900,390 1986,424 "
     "2048,424 L2048,700 Z"),
]


def build_hill(i):
    d = HILL_RIDGES[i]
    base, deep = HILL_V[i]
    # Lit crest band: the hill body dropped 64px back down over itself, so the
    # uncovered strip is the land immediately under the ridge line.  The band
    # thins automatically where the slope steepens and widens over the summits
    # -- the ridge describing itself, not a stripe laid across it.
    return f'''
<svg xmlns="http://www.w3.org/2000/svg" width="2048" height="700" viewBox="0 0 2048 700">
  <defs>{clip("hillClip", d)}</defs>
  {twotone("hillClip", d, deep, base, 0, 64)}
</svg>'''


# =========================================================================
# 4. GRASS_TUFT   1024x1024   object height ~658px -> outline 9px = 1.37%
#    Silhouette rebuilt: six upright blades of clearly unequal width (52-112px
#    full width) and unequal height, fanning apart so there is real sky between
#    them.  The hooked "shepherd's crook" blade is gone.  The evenodd bite()
#    that punched a 744px transparent hole through the tall blade is gone; the
#    oddity is now a notch that opens onto the silhouette.
# =========================================================================
GRASS_OL = 9


def blade_path(bx, by, tx, ty, hw, tw, bend, notch=None, n=10):
    """Blade as an explicit outline: left edge up, round cap, right edge down.
    Simply connected by construction -- it cannot enclose a transparent hole."""
    L, R = [], []
    for i in range(n + 1):
        t = i / float(n)
        cx = bx + (tx - bx) * t + bend * math.sin(math.pi * t)
        cy = by + (ty - by) * t
        w = hw + (tw - hw) * (t ** 1.15)   # chunky at the base, never spiky
        L.append([cx - w, cy])
        R.append([cx + w, cy])
    if notch:                       # nibbled edge: open to the outside
        ni, nd = notch
        L[ni][0] += nd
        L[ni - 1][0] -= nd * 0.15
        L[ni + 1][0] -= nd * 0.15
    cap = [(tx - tw * 0.72, ty - tw * 0.70), (tx, ty - tw),
           (tx + tw * 0.72, ty - tw * 0.70)]
    return smooth_closed(L + cap + R[::-1])


# (base x, base y, tip x, tip y, base half-width, tip half-width, bend)
# Full widths 60..124px: no two blades within 12px of each other.  Heights
# 118..626.  Bends kept under 26 so nothing curls into a shepherd's crook.
GRASS_SETS = [
    [(300, 888, 214, 566, 40, 13, -34),
     (392, 892, 336, 356, 52, 16, -22),
     (496, 894, 500, 262, 62, 19, -4),
     (596, 892, 660, 392, 48, 15, 24),
     (686, 888, 786, 566, 38, 12, 38),
     (470, 896, 446, 690, 30, 10, -12)],
    [(288, 890, 200, 616, 34, 11, -30),
     (382, 894, 320, 402, 46, 14, -26),
     (484, 892, 478, 292, 58, 18, -8),
     (582, 894, 642, 340, 54, 17, 20),
     (672, 888, 768, 496, 42, 13, 34),
     (770, 890, 820, 748, 30, 10, 22)],
    [(318, 888, 236, 520, 44, 14, -30),
     (414, 892, 356, 322, 56, 17, -20),
     (516, 894, 528, 396, 48, 15, 10),
     (608, 890, 686, 452, 38, 12, 28),
     (700, 894, 800, 640, 32, 10, 36),
     (556, 896, 578, 726, 26, 9, 10)],
]
# notch (sample index, inward depth) on the tallest blade of each set.  Shallow
# on purpose: a nibble, not a kink.
GRASS_NOTCH = [(2, (7, 7)), (2, (6, 7)), (1, (7, 7))]
GRASS_MOUNDS = [
    [(214, 902), (240, 872), (282, 886), (326, 858), (374, 878), (424, 852),
     (474, 872), (524, 846), (574, 870), (624, 850), (674, 872), (724, 858),
     (770, 878), (806, 896), (810, 914), (768, 924), (640, 930), (500, 932),
     (360, 928), (252, 918)],
    [(204, 904), (230, 876), (272, 890), (318, 862), (366, 882), (416, 856),
     (466, 878), (516, 850), (566, 874), (616, 854), (666, 876), (714, 862),
     (760, 882), (796, 900), (800, 918), (758, 928), (630, 934), (492, 936),
     (352, 932), (242, 922)],
    [(228, 900), (254, 868), (296, 882), (340, 854), (388, 876), (438, 848),
     (488, 870), (538, 842), (588, 866), (638, 846), (688, 868), (738, 854),
     (784, 876), (820, 892), (824, 910), (782, 920), (654, 926), (514, 928),
     (374, 924), (266, 914)],
]


def build_grass(i):
    base, deep = GRASS_V[i]
    blades = GRASS_SETS[i]
    nb, nspec = GRASS_NOTCH[i]
    # back-to-front: short outer blades first, tall centre last
    order = sorted(range(len(blades)), key=lambda k: blades[k][3])
    defs, parts = [], []
    parts.append(contact(530, 916, 322, 30))
    for k in order:
        bx, by, tx, ty, hw, tw, bend = blades[k]
        d = blade_path(bx, by, tx, ty, hw, tw, bend,
                       notch=nspec if k == nb else None)
        cid = "gb%d" % k
        defs.append(clip(cid, d))
        # shadow crescent runs down the blade's own lower-right flank
        parts.append(twotone(cid, d, base, deep, -hw * 0.42, -hw * 0.5))
        parts.append('<path d="%s" fill="none" stroke="%s" stroke-width="%d" '
                     '%s/>' % (d, INK, GRASS_OL, RJ))
    mound = smooth_closed(GRASS_MOUNDS[i])
    defs.append(clip("gm", mound))
    # mound: the body dropped 42px back over itself, so only the scalloped
    # crest catches light.  Follows the mound's own top edge, scallop for
    # scallop -- it is not the horizontal band the old batch used everywhere.
    parts.append(twotone("gm", mound, deep, base, 0, 26))
    parts.append('<path d="%s" fill="none" stroke="%s" stroke-width="%d" %s/>'
                 % (mound, INK, GRASS_OL, RJ))
    return ('<svg xmlns="http://www.w3.org/2000/svg" width="1024" '
            'height="1024" viewBox="0 0 1024 1024">\n  <defs>'
            + "".join(defs) + '</defs>\n  ' + "\n  ".join(parts) + '\n</svg>')


# =========================================================================
# 5. DIRT_PLOT   1024x1024   object height ~420px -> outline 6px = 1.43%
#    An EXCAVATED HOLE the child plants into -- not a mound, not a loaf.
#      * dug rim whose back bank dips into a saddle in the middle, so the
#        silhouette carries a visible depression at 25% black
#      * slightly elliptical top opening
#      * interior a full step darker than the outer lip
#      * lit far wall as a crescent concentric with the opening
#      * flat ground line across the base
#      * round-capped scrape marks (the old tapered furrow strokes are gone)
#      * NO cream pebble -- an every-plot constant is instancing (C7)
# =========================================================================
DIRT_OL = 6
DIRT_RIMS = [
    [(76, 640), (96, 556), (150, 486), (218, 424), (290, 394), (362, 424),
     (430, 456), (512, 468), (592, 456), (664, 424), (736, 396), (802, 402),
     (866, 452), (918, 522), (948, 606), (944, 686), (908, 748), (836, 786),
     (740, 804), (620, 812), (500, 812), (380, 806), (272, 792), (180, 764),
     (114, 712)],
    [(88, 664), (104, 578), (156, 508), (226, 448), (300, 424), (368, 456),
     (436, 484), (512, 496), (594, 482), (664, 452), (730, 424), (798, 432),
     (860, 480), (912, 548), (936, 628), (930, 700), (896, 756), (824, 790),
     (730, 806), (614, 812), (498, 812), (382, 806), (278, 792), (188, 766),
     (124, 720)],
    [(92, 620), (110, 540), (162, 474), (232, 418), (308, 392), (376, 428),
     (444, 458), (516, 470), (594, 454), (662, 420), (726, 392), (794, 400),
     (856, 448), (906, 516), (930, 598), (926, 678), (892, 740), (822, 780),
     (728, 798), (614, 806), (500, 806), (386, 800), (282, 786), (192, 758),
     (128, 706)],
]
# opening: slightly elliptical, sitting low in the rim so the back bank is
# thicker than the near lip -- you are looking over the near edge into a hole.
DIRT_OPEN = [(512, 636, 336, 108), (512, 656, 322, 102), (512, 638, 316, 100)]
DIRT_OPEN_JIT = [1.00, 0.97, 1.03, 0.98, 1.02, 0.96, 1.04, 0.99,
                 1.01, 0.95, 1.03, 0.98]


def ellipse_pts(cx, cy, rx, ry, jit, phase=0.0):
    n = len(jit)
    return [(cx + rx * jit[i] * math.cos(phase + 2 * math.pi * i / n),
             cy + ry * jit[i] * math.sin(phase + 2 * math.pi * i / n))
            for i in range(n)]


def clod(cx, cy, s, rot, col, wob, ol=5, squash=0.86):
    pts = []
    for k in range(7):
        a = math.radians(k * (360.0 / 7) + 14)
        r = s * wob[k]
        pts.append((cx + r * math.cos(a), cy + r * squash * math.sin(a)))
    tr = ' transform="rotate(%d %d %d)"' % (rot, cx, cy) if rot else ""
    return ('<path d="%s" fill="%s" stroke="%s" stroke-width="%d" %s%s/>'
            % (smooth_closed(pts), col, INK, ol, RJ, tr))


DIRT_CLODS = [
    # (cx, cy, size, rot, which colour index, wobble)  index 2 = crooked one
    [(258, 404, 40, -14, 2, [1.00, .88, 1.10, .92, 1.06, .86, .96]),
     (352, 436, 30, 20, 0, [.90, 1.12, .96, 1.04, .86, 1.08, .94]),
     (512, 474, 26, -8, 0, [1.10, .92, 1.02, .86, 1.12, .94, 1.00]),
     (676, 428, 34, 38, 2, [.94, 1.06, .88, 1.12, .92, 1.00, 1.08]),
     (778, 400, 44, -36, 2, [1.12, .90, 1.02, .94, .86, 1.10, .96]),
     (884, 496, 30, 12, 0, [.90, 1.02, 1.12, .88, .98, 1.06, .92]),
     (118, 596, 28, -22, 0, [1.06, .90, .96, 1.12, .88, 1.00, .94]),
     (152, 692, 22, 30, 2, [.94, 1.10, .88, 1.02, 1.12, .90, 1.00]),
     (904, 656, 25, 8, 0, [1.12, .90, 1.00, .88, 1.08, .94, 1.02])],
    [(292, 430, 36, -10, 2, [1.02, .90, 1.08, .94, 1.04, .88, .98]),
     (400, 464, 26, 24, 0, [.92, 1.10, .94, 1.06, .88, 1.06, .96]),
     (516, 500, 24, -6, 0, [1.08, .94, 1.00, .88, 1.10, .92, 1.02]),
     (652, 456, 30, 34, 2, [.96, 1.04, .90, 1.10, .94, 1.02, 1.06]),
     (760, 428, 40, -30, 2, [1.10, .92, 1.04, .92, .88, 1.08, .98]),
     (872, 520, 27, 14, 0, [.92, 1.00, 1.10, .90, 1.00, 1.04, .94]),
     (132, 624, 25, -18, 0, [1.04, .92, .98, 1.10, .90, 1.02, .92]),
     (160, 714, 20, 26, 2, [.96, 1.08, .90, 1.00, 1.10, .92, 1.02]),
     (892, 686, 23, 6, 0, [1.10, .92, 1.02, .90, 1.06, .96, 1.00])],
    [(300, 400, 42, -16, 2, [1.04, .86, 1.12, .90, 1.08, .88, .94]),
     (388, 438, 28, 18, 0, [.88, 1.14, .94, 1.02, .90, 1.10, .92]),
     (516, 478, 22, -10, 0, [1.12, .90, 1.04, .88, 1.10, .96, .98]),
     (664, 424, 32, 42, 2, [.92, 1.08, .86, 1.14, .94, .98, 1.10]),
     (752, 398, 38, -40, 2, [1.14, .88, 1.00, .96, .88, 1.12, .94]),
     (874, 486, 28, 10, 0, [.94, 1.04, 1.08, .90, .96, 1.08, .90]),
     (126, 578, 30, -24, 0, [1.08, .88, .94, 1.10, .92, 1.00, .96]),
     (148, 676, 24, 32, 2, [.92, 1.12, .90, 1.04, 1.08, .88, 1.02]),
     (898, 640, 27, 4, 0, [1.10, .92, .98, .90, 1.10, .92, 1.04])],
]


def build_dirt(i):
    soil, deep, lite, dark = SOIL_V[i]
    rim = smooth_closed(DIRT_RIMS[i])
    cx, cy, rx, ry = DIRT_OPEN[i]
    hole = smooth_closed(ellipse_pts(cx, cy, rx, ry, DIRT_OPEN_JIT, 0.22))
    # scrape marks: short round-capped arcs concentric with the opening, sitting
    # on the hole floor.  Round caps only -- tapered strokes are banned.
    scrapes = ""
    for j, (sr, sy, w) in enumerate([(0.80, -10, 14), (0.60, 22, 12),
                                     (0.38, 50, 10)]):
        a0, a1 = math.radians(28 + j * 9), math.radians(152 - j * 11)
        p = []
        for k in range(9):
            a = a0 + (a1 - a0) * k / 8.0
            p.append((cx + rx * sr * math.cos(a),
                      cy + sy + ry * sr * 0.7 * math.sin(a)))
        dd = "M%.1f,%.1f " % p[0] + " ".join("L%.1f,%.1f" % q for q in p[1:])
        scrapes += ('<path d="%s" fill="none" stroke="%s" stroke-width="%d" '
                    '%s/>' % (dd, dark, w, RJ))
    cols = [soil, deep, lite]
    clods = "".join(clod(a, b, c, d, cols[e], f) for a, b, c, d, e, f
                    in DIRT_CLODS[i])
    return f'''
<svg xmlns="http://www.w3.org/2000/svg" width="1024" height="1024" viewBox="0 0 1024 1024">
  <defs>{clip("rimClip", rim)}{clip("holeClip", hole)}</defs>
  <!-- contact shadow: hue-matched to the ground green, hard edge, ~2% dV -->
  {contact(516, 792, 434, 40)}
  <!-- dug rim.  Lit face up-left, shade crescent down-right, concentric with
       the rim itself.  The back bank dips into a saddle at the centre so the
       silhouette reads as a depression, not a loaf. -->
  {twotone("rimClip", rim, lite, soil, -46, -58, 1.2, 512, 620)}
  <path d="{rim}" fill="none" stroke="{INK}" stroke-width="{DIRT_OL}" {RJ}/>
  <!-- interior: a full step darker than the lip.  The lit far wall is a
       crescent concentric with the opening, made by dropping the opening back
       down over itself -- it follows the hole, it is not a wavy band. -->
  <path d="{hole}" fill="{soil}"/>
  <g clip-path="url(#holeClip)">
    <path d="{hole}" fill="{deep}" transform="translate(0,66)"/>
    {scrapes}
  </g>
  <path d="{hole}" fill="none" stroke="{INK}" stroke-width="{DIRT_OL}" {RJ}/>
  <!-- clods straddling the rim: ragged edge, one deliberately crooked -->
  {clods}
</svg>'''


# =========================================================================
# 6. BUSH_SHRUB   1024x1024   object height ~584px -> outline 9px = 1.54%
#    Deliberately NOT cloud language: many small unequal leaf scallops.
# =========================================================================
BUSH_OL = 9
BUSH_SETS = [
    dict(n=16, rx=322, ry=278, jit=[1.00, .93, 1.06, .97, 1.09, .91, 1.04,
                                    1.00, 1.07, .94, 1.02, .89, 1.05, .96,
                                    1.00, .98],
         bul=[66, 82, 58, 90, 70, 48, 86, 62, 94, 72, 54, 88, 68, 80, 60],
         notch=11, base=[(742, 784), (638, 800), (528, 808), (420, 802),
                         (318, 790)], bbul=[58, 34, 44, 26, 50, 62],
         berry=[(386, 470, 30), (444, 534, 22), (628, 436, 26)],
         seams=["M262,432 C332,462 356,538 322,616",
                "M700,368 C650,420 660,492 712,532",
                "M486,320 C444,380 460,448 514,486",
                "M556,660 C606,632 620,584 604,536",
                "M386,690 C428,668 448,624 442,578"]),
    dict(n=18, rx=286, ry=316, jit=[1.00, .96, 1.08, .92, 1.05, 1.00, .94,
                                    1.07, .90, 1.03, .97, 1.06, .93, 1.01,
                                    .95, 1.04, .98, 1.00],
         bul=[52, 70, 46, 78, 58, 40, 74, 50, 82, 60, 44, 76, 54, 68, 48,
              72, 56],
         notch=6, base=[(716, 802), (620, 816), (516, 822), (416, 814),
                        (332, 800)], bbul=[46, 30, 38, 22, 44, 54],
         flower=[(404, 424, 26), (452, 386, 20), (596, 452, 23),
                 (628, 402, 17)],
         seams=["M300,470 C364,506 380,578 344,646",
                "M676,398 C630,452 640,522 690,558",
                "M498,286 C458,352 472,424 522,462",
                "M566,682 C614,650 626,606 610,562",
                "M398,704 C438,682 456,640 450,596"]),
    dict(n=15, rx=252, ry=336, jit=[1.00, 1.05, .92, 1.08, .96, 1.02, .90,
                                    1.06, .94, 1.03, .98, 1.07, .93, 1.00,
                                    .97],
         bul=[60, 44, 74, 52, 38, 68, 48, 80, 56, 42, 70, 50, 64, 46],
         notch=8, base=[(680, 806), (596, 820), (508, 826), (420, 818),
                        (352, 804)], bbul=[42, 26, 34, 20, 40, 48],
         berry=[(438, 388, 27)],
         seams=["M338,486 C392,522 404,588 372,650",
                "M646,414 C606,464 614,528 656,560",
                "M508,264 C470,330 484,400 530,438",
                "M556,688 C598,658 608,616 594,576"]),
]


def bush_path(s):
    n, rx, ry = s["n"], s["rx"], s["ry"]
    pts = []
    for i in range(n):
        ang = math.radians(206 - i * (232.0 / (n - 1)))
        k = s["jit"][i]
        pts.append((512 + rx * k * math.cos(ang), 584 - ry * k * math.sin(ang)))
    d = "M%.1f,%.1f" % pts[0]

    def arc(p1, p2, bul):
        dx, dy = p2[0] - p1[0], p2[1] - p1[1]
        L = math.hypot(dx, dy)
        nx, ny = dy / L, -dx / L
        return " Q%.1f,%.1f %.1f,%.1f" % (
            (p1[0] + p2[0]) / 2 + nx * bul, (p1[1] + p2[1]) / 2 + ny * bul,
            p2[0], p2[1])
    for i in range(n - 1):
        b = s["bul"][i]
        if i == s["notch"]:
            b = -22                 # one bitten leaf, inward
        d += arc(pts[i], pts[i + 1], b)
    bp = [pts[-1]] + s["base"] + [pts[0]]
    for i in range(len(bp) - 1):
        d += arc(bp[i], bp[i + 1], s["bbul"][i])
    return d + " Z"


def build_bush(i):
    s = BUSH_SETS[i]
    base, deep = GRASS_V[i]
    d = bush_path(s)
    seams = "".join('<path d="%s" fill="none" stroke="%s" stroke-width="%d" '
                    '%s/>' % (x, INK, BUSH_OL, RJ) for x in s["seams"])
    acc = ""
    for bx, by, br in s.get("berry", []):
        acc += ('<circle cx="%d" cy="%d" r="%d" fill="%s" stroke="%s" '
                'stroke-width="7" %s/>' % (bx, by, br, BERRY, INK, RJ))
    for fx, fy, fr in s.get("flower", []):
        acc += ('<circle cx="%d" cy="%d" r="%d" fill="%s" stroke="%s" '
                'stroke-width="7" %s/>' % (fx, fy, fr, ACCENT, INK, RJ))
    return f'''
<svg xmlns="http://www.w3.org/2000/svg" width="1024" height="1024" viewBox="0 0 1024 1024">
  <defs>{clip("bushClip", d)}</defs>
  {contact(516, 812, 268, 32)}
  <!-- shadow crescent follows the scalloped silhouette itself (the same path
       shifted toward the light, plus 2 degrees of rotation so the band
       breathes instead of reading as an extruded rim) -->
  {twotone("bushClip", d, base, deep, -34, -40, 2.0, 512, 600)}
  <g clip-path="url(#bushClip)">
    <!-- internal contour lines: overlapping leaf clumps do the form work -->
    {seams}
  </g>
  <path d="{d}" fill="none" stroke="{INK}" stroke-width="{BUSH_OL}" {RJ}/>
  {acc}
</svg>'''


# =========================================================================
# 7. NARRATIVE PROPS   512x512   object height ~250-300 -> outline 4px
#    These replace the cream pebble that used to be baked into every plot.
# =========================================================================
PROP_OL = 4

_seed_d = smooth_closed([(256, 168), (306, 196), (322, 258), (300, 320),
                         (256, 344), (212, 320), (190, 258), (206, 196)])
_seed_soil = smooth_closed([(96, 340), (168, 314), (240, 326), (312, 310),
                            (392, 332), (416, 366), (400, 392), (300, 402),
                            (200, 404), (110, 392), (86, 366)])
prop_seed = f'''
<svg xmlns="http://www.w3.org/2000/svg" width="512" height="512" viewBox="0 0 512 512">
  <defs>{clip("sdClip", _seed_d)}{clip("smClip", _seed_soil)}</defs>
  {contact(252, 398, 178, 20)}
  <!-- the seed, half sunk: the soil lip crosses it, so it reads as buried -->
  {twotone("sdClip", _seed_d, SOIL_LITE, SOIL, -14, -18)}
  <path d="{_seed_d}" fill="none" stroke="{INK}" stroke-width="{PROP_OL}" {RJ}/>
  <path d="M242,214 C230,252 236,290 258,318" fill="none" stroke="{SOIL_DEEP}"
        stroke-width="7" {RJ}/>
  {twotone("smClip", _seed_soil, SOIL, SOIL_DEEP, -12, -16)}
  <path d="{_seed_soil}" fill="none" stroke="{INK}" stroke-width="{PROP_OL}" {RJ}/>
</svg>'''

def capsule(ax, ay, bx, by, r, n=9):
    """Round-capped bar as a closed outline (so it can take two-tone blocking).
    Sampled rather than arc-flagged, which also gives it a hand-drawn wobble."""
    dx, dy = bx - ax, by - ay
    L = math.hypot(dx, dy)
    ux, uy = dx / L, dy / L
    nx, ny = -uy, ux
    pts = []
    for k in range(n + 1):                     # cap round the B end
        a = math.pi * k / n
        pts.append((bx + r * (nx * math.cos(a) + ux * math.sin(a)),
                    by + r * (ny * math.cos(a) + uy * math.sin(a))))
    for k in range(n + 1):                     # cap round the A end
        a = math.pi + math.pi * k / n
        pts.append((ax + r * (nx * math.cos(a) + ux * math.sin(a)),
                    ay + r * (ny * math.cos(a) + uy * math.sin(a))))
    return smooth_closed(pts)


# leaf-shaped blade, point at the lower left; two close points at the tip keep
# the point from rounding off into a spoon
_tr_blade = smooth_closed([(140, 352), (158, 378), (200, 360), (240, 324),
                           (268, 262), (258, 200), (214, 174), (166, 190),
                           (130, 232), (122, 296)])
_tr_ferrule = capsule(222, 208, 262, 168, 21)
_tr_handle = capsule(250, 186, 358, 92, 29)
prop_trowel = f'''
<svg xmlns="http://www.w3.org/2000/svg" width="512" height="512" viewBox="0 0 512 512">
  <defs>{clip("tbClip", _tr_blade)}{clip("tfClip", _tr_ferrule)}{clip("thClip", _tr_handle)}</defs>
  {contact(232, 386, 150, 18)}
  {twotone("tbClip", _tr_blade, STONE, STONE_DEEP, -16, -20)}
  <path d="{_tr_blade}" fill="none" stroke="{INK}" stroke-width="{PROP_OL}" {RJ}/>
  <path d="M198,224 C182,262 168,296 156,330" fill="none" stroke="{INK}"
        stroke-width="4" {RJ}/>
  {twotone("tfClip", _tr_ferrule, STONE_DEEP, "#7f8b99", -10, -12)}
  <path d="{_tr_ferrule}" fill="none" stroke="{INK}" stroke-width="{PROP_OL}" {RJ}/>
  {twotone("thClip", _tr_handle, ACCENT, "#e08e52", -12, -14)}
  <path d="{_tr_handle}" fill="none" stroke="{INK}" stroke-width="{PROP_OL}" {RJ}/>
</svg>'''

# arched worm: thick through the arch, round-capped at both ends
_worm_d = ("M110,374 C100,296 142,236 218,220 C296,204 336,266 334,346 "
           "A24,24 0 0 1 286,346 "
           "C288,282 264,262 216,274 C156,288 140,318 144,374 "
           "A17,17 0 0 1 110,374 Z")
prop_worm = f'''
<svg xmlns="http://www.w3.org/2000/svg" width="512" height="512" viewBox="0 0 512 512">
  <defs>{clip("wClip", _worm_d)}</defs>
  {contact(224, 388, 132, 16)}
  {twotone("wClip", _worm_d, WORM, WORM_DEEP, -14, -18)}
  <path d="{_worm_d}" fill="none" stroke="{INK}" stroke-width="{PROP_OL}" {RJ}/>
  <path d="M168,256 C176,268 180,280 180,294" fill="none" stroke="{WORM_DEEP}"
        stroke-width="7" {RJ}/>
  <path d="M262,250 C266,264 268,278 266,292" fill="none" stroke="{WORM_DEEP}"
        stroke-width="7" {RJ}/>
  <ellipse cx="300" cy="322" rx="9" ry="8" fill="{INK_SOFT}"/>
  <ellipse cx="324" cy="330" rx="8" ry="7" fill="{INK_SOFT}"/>
</svg>'''

# =========================================================================
ASSETS = []
for _n, _s in [("sun_character", build_sun("default"))]:
    ASSETS.append((_n, _s, 1024, 1024))
for _e, _ in FACES[1:]:
    ASSETS.append(("sun_character_" + _e, build_sun(_e), 1024, 1024))
for _i, _sfx in enumerate(["", "_b", "_c"]):
    ASSETS.append(("cloud_puffy" + _sfx, build_cloud(_i), 1024, 1024))
    ASSETS.append(("hill_layer" + _sfx, build_hill(_i), 2048, 700))
    ASSETS.append(("grass_tuft" + _sfx, build_grass(_i), 1024, 1024))
    ASSETS.append(("dirt_plot" + _sfx, build_dirt(_i), 1024, 1024))
    ASSETS.append(("bush_shrub" + _sfx, build_bush(_i), 1024, 1024))
ASSETS += [("prop_seed", prop_seed, 512, 512),
           ("prop_trowel", prop_trowel, 512, 512),
           ("prop_worm", prop_worm, 512, 512)]

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
        print("%-24s %s  %s" % (name, "OK" if ok else "FAIL",
                                "%dx%d" % (w, h)))
