#!/usr/bin/env python3
"""Alphabet Garden -- FLAT-VECTOR HUD ICONS, BADGE AND WORDMARK.

The last claymation surface in the game.  Six DOM images in index.html were still
glossy 3D renders sitting permanently over a flat-vector world:

    icon_rain, icon_book, icon_shovel, icon_sound   (HUD buttons)
    logo_badge                                       (HUD badge + favicon)
    logo                                             (title-screen wordmark)

Canvas sizes and registration match the originals exactly so index.html/style.css
need no layout change:  icons + badge 768x768, wordmark 1536x1024.

WHY THIS FILE IS NOT _build_flat.py
-----------------------------------
Every other flat asset is a *scene texture* rendered by Phaser at world scale.
These six are DOM <img>s rendered at 32-46 css px inside a 52px (44px on phones)
white circle.  That is a 20:1 downscale -- an iconography problem, not an
illustration one -- so this file carries its own, much bolder, outline ladder:

    ICON_OL = 40 on a 768 canvas  (5.2% of the frame, ~2.0 css px at render size)

and a hard floor of ~8% of the icon box on every feature (TOCA 5.2), against
_kit.py's 1.25-1.48% ladder which would land at 0.6 css px here and ghost out.

THE UNION-DILATION CONSTRUCTION (why there are no internal black nubs)
---------------------------------------------------------------------
Every object is built from several overlapping primitives.  Each is drawn twice:
once filled AND stroked black at 2*OL (a dilation by OL), then again in colour
with no stroke.  Minkowski dilation distributes over union, so

    union(shape_i (+) OL)  ==  (union shape_i) (+) OL

i.e. painting per-part black dilations underneath the colour pass yields exactly
one uniform OL-wide outline around the *silhouette of the union* -- including
around counters -- and never a stray black seam where two parts overlap.  This
is what lets the wordmark's letters be built as round-capped stroke skeletons.

Two-tone shading is the house `twotone` recipe: lay the whole form down in its
shadow tone, then lay the SAME form back down in the base tone shifted toward
the light and masked to itself.  The lit/shade boundary is therefore always
concentric with the form that owns it.  No gradients, no filters, no blur.

Run:  python3 "art/flat/ui/_build_ui.py"
"""
import math
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = HERE
TMP = ("/private/tmp/claude-501/-Users-clintonmcleod-AI-letter-garden/"
       "ce761231-ba83-4ee2-9c8a-70a03ba16f73/scratchpad/svgui")
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
os.makedirs(TMP, exist_ok=True)

# ---------------------------------------------------------------- palette ---
# Verbatim FLAT_ART_BRIEF Sec 3 / plants/_kit.py tokens.  Nothing invented
# except CLOUD_DEEP, derived below by the brief's documented shadow rule.
INK         = "#000000"
CREAM       = "#fff7e6"
CREAM_DEEP  = "#e8dcc4"
CLOUD_SHADE = "#c6d8e6"
CLOUD_DEEP  = "#a9bdcc"   # derived: cloud-shade at dV 0.10 / dS +0.035, hue held 206
SKY_HI      = "#8fd3ff"
SKY_DEEP    = "#6cacd9"
GRASS       = "#9ddb76"
GRASS_DEEP  = "#79b85c"
LEAF        = "#c3f598"
SUN         = "#ffe07a"
SUN_SHADE   = "#eebf62"
SUN_DEEP    = "#f0c665"
RAY_SHADE   = "#dbab58"
ACCENT      = "#ffb77e"
ACCENT_DEEP = "#e09863"
FRUIT       = "#d96a62"
FRUIT_DEEP  = "#b8544e"
BERRY       = "#c65fd1"
BERRY_DEEP  = "#a44ead"
BARK        = "#c2946b"
BARK_DEEP   = "#a37855"
BARK_LITE   = "#dbad7f"

RJ = 'stroke-linejoin="round" stroke-linecap="round"'

# ============================================================== geometry ====


def P(pts, close=False):
    d = "M%.1f,%.1f" % pts[0] + "".join("L%.1f,%.1f" % p for p in pts[1:])
    return d + ("Z" if close else "")


def arcp(cx, cy, rx, ry, a0, a1, step=4.0, wob=0.0, seed=0):
    """Sample an elliptical arc as a polyline.  Angles in degrees, y down.

    4-degree steps on a 300px radius leave a 0.15px sagitta -- invisible at 1x,
    and it lets every form carry a little radius wobble (the charm rule) that a
    real <ellipse> cannot.
    """
    n = max(2, int(abs(a1 - a0) / step) + 1)
    pts = []
    for i in range(n + 1):
        t = i / n
        a = math.radians(a0 + (a1 - a0) * t)
        k = 1.0
        if wob:
            k = 1.0 + wob * math.sin(t * 6.3 + seed * 1.7) * 0.5 \
                    + wob * math.sin(t * 11.1 + seed * 3.1) * 0.5
        pts.append((cx + rx * k * math.cos(a), cy + ry * k * math.sin(a)))
    return pts


def ell(cx, cy, rx, ry, wob=0.0, seed=0, rot=0.0):
    pts = arcp(cx, cy, rx, ry, 0, 360, 5.0, wob, seed)[:-1]
    if rot:
        pts = rotate(pts, cx, cy, rot)
    return pts


def rotate(pts, cx, cy, deg):
    a = math.radians(deg)
    c, s = math.cos(a), math.sin(a)
    return [(cx + (x - cx) * c - (y - cy) * s,
             cy + (x - cx) * s + (y - cy) * c) for x, y in pts]


def rrect(x, y, w, h, r):
    """Rounded rect as a polyline (corner radius scales with the shape)."""
    r = min(r, w / 2, h / 2)
    pts = []
    pts += arcp(x + w - r, y + r, r, r, -90, 0, 6)
    pts += arcp(x + w - r, y + h - r, r, r, 0, 90, 6)
    pts += arcp(x + r, y + h - r, r, r, 90, 180, 6)
    pts += arcp(x + r, y + r, r, r, 180, 270, 6)
    return pts


def petal(cx, cy, rx, ry, ang):
    """A rounded teardrop petal pointing along `ang`, wider at the tip."""
    pts = arcp(cx, cy, rx, ry, 0, 360, 6.0, 0.02, int(ang))[:-1]
    # pinch the root so it reads as a petal, not a floating egg
    out = []
    for x, y in pts:
        dy = (y - cy) / ry
        k = 1.0 - 0.42 * max(0.0, dy)
        out.append((cx + (x - cx) * k, y))
    return rotate(out, cx, cy, ang)


def teardrop(cx, top, bot, hw):
    """Rain drop: point up, round below.  Built as an explicit polyline so the
    tip is a true round-capped point and not a Bezier's flat nose."""
    h = bot - top
    pts = [(cx, top)]
    for i in range(1, 25):
        t = i / 24.0
        # right flank: narrow near the tip, full width low down
        w = hw * math.sin(t ** 0.72 * math.pi * 0.5) ** 0.85
        y = top + h * (0.16 + 0.84 * t) if t < 1 else bot
        pts.append((cx + w, y))
    pts += arcp(cx, bot - hw * 0.86, hw, hw * 0.9, 0, 180, 8)
    for i in range(23, 0, -1):
        t = i / 24.0
        w = hw * math.sin(t ** 0.72 * math.pi * 0.5) ** 0.85
        y = top + h * (0.16 + 0.84 * t)
        pts.append((cx - w, y))
    return pts


def star(cx, cy, r_out, r_in, n=5, rot=-90):
    pts = []
    for i in range(n * 2):
        a = math.radians(rot + i * 180.0 / n)
        r = r_out if i % 2 == 0 else r_in
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


# ============================================================== emitters ====

_uid = [0]


def _nid():
    _uid[0] += 1
    return "u%d" % _uid[0]


class Group(object):
    """One physical object: a set of overlapping primitives that share a black
    outline, a base tone and a shadow tone.

    prims are ('fill', pts) or ('stroke', pts, width, closed).
    """

    def __init__(self, base, shade, ol, dx, dy):
        self.base, self.shade, self.ol = base, shade, ol
        self.dx, self.dy = dx, dy
        self.prims = []

    def fill(self, pts):
        self.prims.append(("fill", pts, 0, True))
        return self

    def stroke(self, pts, w, closed=False):
        self.prims.append(("stroke", pts, w, closed))
        return self

    # -- rendering ---------------------------------------------------------
    def _paths(self, fillcol, extra_stroke=0.0, strokecol=None):
        out = []
        for kind, pts, w, closed in self.prims:
            d = P(pts, close=(closed if kind == "stroke" else True))
            if kind == "fill":
                if extra_stroke:
                    out.append('<path d="%s" fill="%s" stroke="%s" '
                               'stroke-width="%.2f" %s/>'
                               % (d, fillcol, strokecol or fillcol,
                                  extra_stroke, RJ))
                else:
                    out.append('<path d="%s" fill="%s"/>' % (d, fillcol))
            else:
                out.append('<path d="%s" fill="none" stroke="%s" '
                           'stroke-width="%.2f" %s/>'
                           % (d, strokecol or fillcol, w + extra_stroke, RJ))
        return "".join(out)

    def svg(self):
        mid = _nid()
        # 1. black dilation of the union (see module docstring)
        black = self._paths(INK, extra_stroke=2 * self.ol, strokecol=INK)
        # 2. whole form in its shadow tone
        shade = self._paths(self.shade, strokecol=self.shade)
        # 3. same form, base tone, shifted toward the light, masked to itself
        mask = ('<mask id="%s" maskUnits="userSpaceOnUse" x="-400" y="-400" '
                'width="2600" height="2600">%s</mask>'
                % (mid, self._paths("#ffffff", strokecol="#ffffff")))
        lit = ('<g mask="url(#%s)"><g transform="translate(%.1f,%.1f)">%s</g>'
               '</g>' % (mid, self.dx, self.dy,
                         self._paths(self.base, strokecol=self.base)))
        return mask, black + shade + lit

    def bbox(self):
        xs, ys = [], []
        for kind, pts, w, closed in self.prims:
            pad = self.ol + (w / 2.0 if kind == "stroke" else 0.0)
            for x, y in pts:
                xs += [x - pad, x + pad]
                ys += [y - pad, y + pad]
        return min(xs), min(ys), max(xs), max(ys)

    def transform(self, fn, sw=1.0):
        g = Group(self.base, self.shade, self.ol * sw,
                  self.dx * sw, self.dy * sw)
        g.prims = [(k, [fn(p) for p in pts], w * sw, c)
                   for k, pts, w, c in self.prims]
        return g


def compose(w, h, groups, seams=""):
    defs, body = [], []
    for g in groups:
        m, s = g.svg()
        defs.append(m)
        body.append(s)
    return ('<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" '
            'viewBox="0 0 %d %d">\n  <defs>%s</defs>\n  %s\n  %s\n</svg>'
            % (w, h, w, h, "".join(defs), "".join(body), seams))


# ================================================================= ICONS ====
# 768x768.  Rendered at 38 css px (52px button - 7px padding either side) and
# 32 css px on phones under 620px wide.  Every decision below is made for 32px.
ICON_OL = 40.0          # 5.2% of frame -> ~1.7 css px at 32px render
DX, DY = -26.0, -32.0   # light from up-left, same vector on every icon


def icon_rain():
    """RAIN -- bumpy-topped cloud, three long drops.  The only icon in the set
    with a lobed top edge, and the only cool-neutral one."""
    g = []
    cloud = Group(CLOUD_SHADE, CLOUD_DEEP, ICON_OL, DX, DY)
    # lobes deliberately unequal (charm rule); flat-bottomed slab welds them
    cloud.fill(ell(218, 300, 122, 118, 0.02, 1))
    cloud.fill(ell(372, 236, 152, 148, 0.02, 4))
    cloud.fill(ell(546, 296, 126, 124, 0.02, 7))
    cloud.fill(rrect(96, 296, 576, 116, 54))
    g.append(cloud)

    drops = Group(SKY_HI, SKY_DEEP, ICON_OL, DX, DY)
    for cx, top, bot, hw in ((176, 470, 664, 40),
                             (384, 500, 706, 42),
                             (592, 462, 648, 38)):
        drops.fill(teardrop(cx, top, bot, hw))
    g.append(drops)
    return compose(768, 768, g)


def icon_book():
    """BOOK -- open book seen from the front: both edges dip at the spine.

    The first cut had a nearly flat top edge and read as a picture frame at
    32px, and its ink was 688x420 against the shovel's 500x700, so it also
    carried visibly less mass inside its `object-fit: contain` box.  The fan is
    now 112 units deep at the top and the ink is 736x492 -- the same area as
    the rest of the set."""
    g = []
    cover = Group(ACCENT, ACCENT_DEEP, ICON_OL, DX, DY)
    cover.fill([(56, 268)] + arcp(90, 302, 34, 34, 180, 270, 8) +
               [(360, 350), (408, 350)] + arcp(678, 302, 34, 34, 270, 360, 8) +
               [(712, 268), (712, 566)] + arcp(678, 600, 34, 34, 0, 90, 8) +
               [(408, 656), (360, 656)] + arcp(90, 600, 34, 34, 90, 180, 8) +
               [(56, 566)])
    g.append(cover)

    pages = Group(CREAM, CREAM_DEEP, ICON_OL * 0.8, DX, DY)
    pages.fill([(102, 314), (356, 382), (356, 618), (102, 552)])
    pages.fill([(412, 382), (666, 314), (666, 552), (412, 618)])
    g.append(pages)

    st = Group(SUN, SUN_SHADE, ICON_OL * 0.8, DX * 0.6, DY * 0.6)
    st.fill(rotate(star(212, 462, 92, 42), 212, 462, 7))
    g.append(st)

    # the spine: the one internal contour that does real work at this size
    seams = ('<path d="M384,362 L384,644" fill="none" stroke="%s" '
             'stroke-width="30" %s/>' % (INK, RJ))
    return compose(768, 768, g, seams)


def icon_shovel():
    """SHOVEL -- the only tall diagonal in the set.  T-grip, shaft, spade."""
    g = []
    handle = Group(BARK_LITE, BARK, ICON_OL, DX, DY)
    handle.fill(rrect(252, 60, 264, 90, 44))          # T-grip
    handle.fill(rrect(348, 118, 72, 300, 34))         # shaft
    g.append(handle)

    blade = Group(FRUIT, FRUIT_DEEP, ICON_OL, DX, DY)
    blade.fill([(232, 396)] +
               arcp(258, 422, 26, 26, 270, 180, 8)[::-1][:0] +
               [(232, 396), (536, 396), (540, 470)] +
               arcp(384, 466, 156, 244, -12, 90, 5) +
               arcp(384, 466, 156, 244, 90, 192, 5) +
               [(228, 470)])
    g.append(blade)

    # collar where blade meets shaft -- reads as a real tool, one mark
    seams = ('<path d="M300,404 L468,404" fill="none" stroke="%s" '
             'stroke-width="30" %s/>' % (INK, RJ))
    body = compose(768, 768, g, seams)
    # tip the whole tool: a perfectly upright shovel is instant tell #23
    return body.replace('<defs>', '<defs>', 1).replace(
        '</defs>\n  ', '</defs>\n  <g transform="rotate(-11 384 400)">', 1
    ).replace('\n</svg>', '</g>\n</svg>')


def icon_sound():
    """SOUND -- speaker cone plus two waves.

    The muted state is CSS: `#btn-sound.muted img` drops to 0.4 opacity and a
    red -45deg bar is laid across the middle by ::after.  So the mass is kept
    left-of-centre and low-contrast detail is kept out of the bar's path -- the
    slash crosses the waves, which is exactly where a mute slash belongs."""
    g = []
    cone = Group(SUN, SUN_SHADE, ICON_OL, DX, DY)
    cone.fill(rrect(74, 300, 132, 168, 34))
    cone.fill([(178, 306)] + arcp(322, 196, 44, 44, 210, 340, 8) +
              [(366, 236), (366, 532)] +
              arcp(322, 572, 44, 44, 20, 150, 8) + [(178, 462)])
    g.append(cone)

    waves = Group(ACCENT, ACCENT_DEEP, ICON_OL, DX, DY)
    waves.stroke(arcp(300, 384, 178, 178, -48, 48, 4), 48)
    waves.stroke(arcp(300, 384, 344, 344, -47, 47, 4), 48)
    g.append(waves)
    return compose(768, 768, g)


def logo_badge():
    """BADGE -- HUD chip at 40-42px AND the favicon at 16px.

    Two bold shapes only: a six-petal rosette and a dark centre disc.  At 16px
    that resolves to a yellow ring with a brown dot, which is still a flower;
    the claymation badge it replaces was a four-object scene that turned to
    mush below about 28px."""
    g = []
    stem = Group(GRASS, GRASS_DEEP, ICON_OL, DX, DY)
    stem.stroke([(384, 430), (390, 560), (378, 688)], 56)
    stem.fill(rotate(ell(238, 596, 108, 60, 0.02, 2), 238, 596, -22))
    stem.fill(rotate(ell(534, 578, 96, 54, 0.02, 5), 534, 578, 20))
    g.append(stem)

    petals = Group(SUN, SUN_SHADE, ICON_OL, DX, DY)
    for i in range(6):
        a = -90 + i * 60 + (7 if i == 2 else 0)      # one petal sits crooked
        r = 168 + (10 if i in (1, 4) else 0)
        cx = 384 + r * math.cos(math.radians(a))
        cy = 372 + r * math.sin(math.radians(a))
        petals.fill(petal(cx, cy, 84, 132, a - 90))
    g.append(petals)

    core = Group(BARK, BARK_DEEP, ICON_OL, DX * 0.7, DY * 0.7)
    core.fill(ell(384, 372, 118, 114, 0.015, 9))
    g.append(core)
    return compose(768, 768, g)


# ============================================================== WORDMARK ====
# Chunky rounded letterforms drawn as round-capped stroke skeletons.
#
# METRICS, AND WHY THEY ARE WHAT THEY ARE
# ---------------------------------------
# Glyph space: baseline 100, cap top 0, x-height top 18, ascender -6.5,
# descender 132.  The x-height is 82% of the cap -- very large, which is a
# hallmark of friendly children's faces and is also load-bearing here:
#
#   For a lowercase 'e', the enclosed counter and the aperture below the bar
#   share  (x-height - 2*stem - bar)  units of vertical space, and the black
#   outline then eats 2*LOL out of each.  At the first weight tried (stem 23,
#   x-height 70) that budget was  70 - 46 - 16 = 8 units for BOTH, and the two
#   e's rendered as solid blobs.  The published metrics give
#   82 - 42 - 14 = 26 units -> a 13-unit counter and a 13-unit aperture, 7.8
#   of each surviving the outline, ~6.6 css px at the title screen's real size.
#
# Horizontals (the bars of e, A, t) are 0.72 of the stem, as in any real face;
# at parity they close the e's counter on their own.
BL, CAP, XT, ASC, DESC, BOT = 100.0, 10.5, 28.5, 4.0, 121.5, 89.5
LW = 21.0        # stem weight (0.256 x-height -- bold, and the e's ceiling)
BAR = 0.72       # horizontals are thinner than stems
LOL = 2.6        # letter outline: 2.0% of the 132-unit object height, and
                 # ~2.0 css px at render -- the icon set's weight, on purpose
BCY, BRX, BRY = 59.0, 27.0, 30.5     # lowercase bowl (outer 18..100)
ACY, ARX, ARY = 57.5, 27.0, 29.0     # n/h/r shoulder arch


def _glyphs():
    """name -> (advance, [(points, closed, width-multiplier), ...])"""
    G = {}
    G["l"] = (21, [([(10.5, ASC), (10.5, BOT)], 0, 1)])
    G["a"] = (75, [(ell(37.5, BCY, BRX, BRY, 0.012, 1), 1, 1),
                   ([(64.5, XT), (64.5, BOT)], 0, 1)])
    G["b"] = (75, [([(10.5, ASC), (10.5, BOT)], 0, 1),
                   (ell(37.5, BCY, BRX, BRY, 0.012, 2), 1, 1)])
    G["d"] = (75, [([(64.5, ASC), (64.5, BOT)], 0, 1),
                   (ell(37.5, BCY, BRX, BRY, 0.012, 3), 1, 1)])
    G["p"] = (75, [([(10.5, XT), (10.5, DESC)], 0, 1),
                   (ell(37.5, BCY, BRX, BRY, 0.012, 4), 1, 1)])
    G["e"] = (75, [([(10.5, 59.0), (64.5, 58.0)], 0, BAR),
                   (arcp(37.5, BCY, BRX, BRY, 0, -300, 4, 0.012, 5), 0, 1)])
    G["h"] = (75, [([(10.5, ASC), (10.5, BOT)], 0, 1),
                   (arcp(37.5, ACY, ARX, ARY, 180, 360, 4, 0.012, 6), 0, 1),
                   ([(64.5, ACY), (64.5, BOT)], 0, 1)])
    G["n"] = (75, [([(10.5, XT), (10.5, BOT)], 0, 1),
                   (arcp(37.5, ACY, ARX, ARY, 180, 360, 4, 0.012, 7), 0, 1),
                   ([(64.5, ACY), (64.5, BOT)], 0, 1)])
    G["r"] = (68, [([(10.5, XT), (10.5, BOT)], 0, 1),
                   (arcp(37.5, ACY, ARX, ARY, 180, 316, 4, 0.012, 8), 0, 1)])
    G["t"] = (60, [([(29.0, 10.0), (29.0, 72.0)] +
                    arcp(49.0, 72, 20, 17.5, 180, 90, 8), 0, 1),
                   ([(7.0, 28.5), (50.0, 26.5)], 0, BAR)])   # bar rides up 2deg
    G["A"] = (84, [([(10.5, BOT), (42.0, CAP), (73.5, BOT)], 0, 1),
                   ([(23.0, 66.0), (61.0, 66.0)], 0, BAR)])
    G["G"] = (88, [(arcp(44, 50, 32, 39.5, -50, -360, 4, 0.010, 9) +
                    [(42.0, 50.0)], 0, 1)])
    return G


GLY = _glyphs()

# 5 hue families, warm-dominant, no two neighbours sharing one.  Every fill is
# under S 0.55; BERRY is the brief's "rare high-sat accent" and appears twice.
PAL = {"F": (FRUIT, FRUIT_DEEP), "O": (ACCENT, ACCENT_DEEP),
       "Y": (SUN, SUN_SHADE), "G": (GRASS, GRASS_DEEP),
       "B": (BERRY, BERRY_DEEP)}
LINE1 = list(zip("Alphabet", "FOYGBFOY"))
LINE2 = list(zip("Garden", "GBFOYG"))
TRACK = 14.0        # letters need air: TRACK - 2*LOL leaves ~8.8u of daylight


def _lay(line, y0, tilt_seed):
    """Lay one word out, each letter on its own slight rotation and bounce."""
    total = sum(GLY[c][0] for c, _ in line) + TRACK * (len(line) - 1)
    x = -total / 2.0
    out = []
    for i, (ch, col) in enumerate(line):
        adv, prims = GLY[ch]
        base, shade = PAL[col]
        rot = math.sin((i + tilt_seed) * 2.3) * 3.4
        dy = math.sin((i + tilt_seed) * 1.7) * 3.2
        w = LW + math.sin((i + tilt_seed) * 3.9) * 0.6
        g = Group(base, shade, LOL, -4.0, -5.5)
        cx, cy = x + adv / 2.0, y0 + 50.0 + dy
        for pts, closed, wm in prims:
            pp = [(px + x, py + y0 + dy) for px, py in pts]
            g.stroke(rotate(pp, cx, cy, rot), w * wm, closed)
        out.append((g, ch, x, y0 + dy, adv))
        x += adv + TRACK
    return out


def _sprout(x, y, s, flip, seed):
    """A stem with two leaves -- the wordmark's garden accents."""
    g = Group(GRASS, GRASS_DEEP, LOL, -4.0, -5.5)
    f = -1 if flip else 1
    g.stroke([(x, y), (x + 2 * f * s, y - 16 * s), (x - 1 * f * s, y - 34 * s)],
             7.5 * s)
    l1 = ell(x - 15 * s * f, y - 26 * s, 15 * s, 8.6 * s, 0.03, seed)
    l2 = ell(x + 14 * s * f, y - 34 * s, 13 * s, 7.6 * s, 0.03, seed + 1)
    g.fill(rotate(l1, x - 15 * s * f, y - 26 * s, -24 * f))
    g.fill(rotate(l2, x + 14 * s * f, y - 34 * s, 20 * f))
    return g


def _flower(cx, cy, s, seed):
    out = []
    st = Group(GRASS, GRASS_DEEP, LOL, -4.0, -5.5)
    st.stroke([(cx - 2 * s, cy + 16 * s), (cx + 3 * s, cy + 54 * s)], 7.0 * s)
    st.fill(rotate(ell(cx - 16 * s, cy + 46 * s, 15 * s, 8 * s, 0.03, seed),
                   cx - 16 * s, cy + 46 * s, -22))
    out.append(st)
    pt = Group(SUN, SUN_SHADE, LOL, -4.0, -5.5)
    for i in range(7):
        a = -90 + i * 360.0 / 7 + (6 if i == 3 else 0)
        px = cx + 17 * s * math.cos(math.radians(a))
        py = cy + 17 * s * math.sin(math.radians(a))
        pt.fill(petal(px, py, 8.6 * s, 13.5 * s, a - 90))
    out.append(pt)
    co = Group(BARK, BARK_DEEP, LOL, -3.0, -4.0)
    co.fill(ell(cx, cy, 12 * s, 11.6 * s, 0.02, seed + 3))
    out.append(co)
    return out


def wordmark():
    W, H = 1536, 1024
    l1 = _lay(LINE1, 0.0, 0.3)
    l2 = _lay(LINE2, 170.0, 1.9)
    groups = [g for g, *_ in l1] + [g for g, *_ in l2]

    # Garden accents: sprouts pushing up out of the wordmark, one flower at the
    # end of the second line.  Placed against named letters, never on a grid.
    acc = []
    def at(row, i, ddx, ddy):
        g, ch, x, y, adv = row[i]
        return x + ddx, y + ddy
    acc.append(_sprout(*at(l1, 3, 52, 20), 0.95, False, 2))    # h of Alphabet
    acc.append(_sprout(*at(l1, 1, -6, 4), 0.72, True, 11))     # l of Alphabet
    acc.append(_sprout(*at(l2, 3, 62, 20), 0.9, False, 8))     # d of Garden
    acc += _flower(*at(l2, 5, 112, 60), 1.2, 4)                # after the n
    groups += acc

    # fit: content bbox -> canvas, centred, at the old logo's ink proportions
    xs = [b for g in groups for b in (g.bbox()[0], g.bbox()[2])]
    ys = [b for g in groups for b in (g.bbox()[1], g.bbox()[3])]
    bw, bh = max(xs) - min(xs), max(ys) - min(ys)
    s = min(1428.0 / bw, 800.0 / bh)
    ox = W / 2.0 - (min(xs) + bw / 2.0) * s
    oy = H / 2.0 - (min(ys) + bh / 2.0) * s
    fn = lambda p: (p[0] * s + ox, p[1] * s + oy)
    groups = [g.transform(fn, s) for g in groups]
    return compose(W, H, groups)


# ================================================================= build ====
HTML = ('<!doctype html><meta charset="utf-8">'
        '<style>html,body{margin:0;padding:0;background:transparent;}'
        'svg{display:block;}</style>')


def render(name, svg, w, h, out_png, scale=2):
    hp = os.path.join(TMP, name + ".html")
    with open(hp, "w") as f:
        f.write(HTML + svg)
    big = out_png + ".2x.png"
    r = subprocess.run([
        CHROME, "--headless", "--disable-gpu", "--hide-scrollbars",
        "--force-device-scale-factor=%d" % scale,
        "--default-background-color=00000000",
        "--window-size=%d,%d" % (w, h), "--screenshot=" + big,
        "file://" + hp,
    ], capture_output=True, text=True)
    if not os.path.exists(big):
        print(r.stderr[-900:])
        return False
    from PIL import Image
    im = Image.open(big).convert("RGBA").resize((w, h), Image.LANCZOS)
    im.save(out_png)
    os.remove(big)
    return True


ASSETS = [("icon_rain", icon_rain, 768, 768),
          ("icon_book", icon_book, 768, 768),
          ("icon_shovel", icon_shovel, 768, 768),
          ("icon_sound", icon_sound, 768, 768),
          ("logo_badge", logo_badge, 768, 768),
          ("logo", wordmark, 1536, 1024)]

if __name__ == "__main__":
    for name, fn, w, h in ASSETS:
        svg = fn()
        with open(os.path.join(OUT, name + ".svg"), "w") as f:
            f.write(svg.strip() + "\n")
        png = os.path.join(OUT, name + ".png")
        ok = render(name, svg, w, h, png)
        print("%-14s %s  %dx%d" % (name, "OK" if ok else "FAIL", w, h))
