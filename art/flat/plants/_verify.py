#!/usr/bin/env python3
"""Verification harness for the flat plant PNGs.

  python3 art/flat/plants/_verify.py [id ...]

Checks, all by decoding actual pixels:
  1. transparency  -- the four corner pixels and the alpha bbox
  2. flatness      -- longest run of *bit-identical* RGB inside a fill
  3. palette       -- distinct opaque colours, max S, fills in the muddy band,
                      pure #FFFFFF count, untinted grey count
  4. outline       -- exact-#000000 pixel count + median black run
  5. thinness      -- min load-bearing dimension survives a 25% silhouette
Writes contact sheets to _compare/: original | flat | silhouette@25% | @128px.
"""
import os
import sys
import colorsys
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
ORIG = os.path.join(ROOT, "art", "assets", "plants")
CMP = os.path.join(HERE, "_compare")
IDS = ["s-sunflower", "a-apple-tree", "m-maple-tree", "b-butterfly-bush",
       "p-pizza-palm", "u-ufo-tree"]


def longest_run(im):
    """Longest horizontal run of identical RGB among fully-opaque pixels."""
    px = im.load()
    w, h = im.size
    best, best_at = 0, None
    for y in range(0, h, 2):
        run, prev = 0, None
        for x in range(w):
            r, g, b, a = px[x, y]
            cur = (r, g, b) if a == 255 else None
            if cur is not None and cur == prev:
                run += 1
                if run > best:
                    best, best_at = run, (x - run, y, cur)
            else:
                run = 1 if cur is not None else 0
            prev = cur
    return best, best_at


def stats(im):
    px = im.load()
    w, h = im.size
    hist = {}
    for y in range(0, h, 2):
        for x in range(0, w, 2):
            r, g, b, a = px[x, y]
            if a == 255:
                hist[(r, g, b)] = hist.get((r, g, b), 0) + 1
    tot = sum(hist.values()) or 1
    out = {"colours": 0, "maxS": 0.0, "muddy": 0.0, "white": 0,
           "grey": 0, "black": 0, "top": []}
    for c, n in sorted(hist.items(), key=lambda kv: -kv[1]):
        r, g, b = c
        hh, s, v = colorsys.rgb_to_hsv(r / 255., g / 255., b / 255.)
        frac = n / float(tot)
        if frac > 0.002:
            out["colours"] += 1
            if len(out["top"]) < 14:
                out["top"].append(("#%02x%02x%02x" % c, round(frac * 100, 1),
                                   round(s, 2), round(v, 2)))
            if v > 0.20:
                out["maxS"] = max(out["maxS"], s)
            if 0.35 <= v <= 0.55 and s > 0.05:
                out["muddy"] += frac
        if c == (255, 255, 255):
            out["white"] += n
        if c == (0, 0, 0):
            out["black"] += n
        if s < 0.04 and 0.25 < v < 0.95:
            out["grey"] += n
    out["muddy"] = round(out["muddy"] * 100, 2)
    out["white"] = round(out["white"] / float(tot) * 100, 3)
    out["grey"] = round(out["grey"] / float(tot) * 100, 3)
    out["black"] = round(out["black"] / float(tot) * 100, 2)
    return out


def black_runs(im):
    px = im.load()
    w, h = im.size
    runs = []
    for y in range(0, h, 3):
        run = 0
        for x in range(w):
            r, g, b, a = px[x, y]
            if a > 200 and r < 24 and g < 24 and b < 24:
                run += 1
            else:
                if 2 <= run <= 60:
                    runs.append(run)
                run = 0
    runs.sort()
    if not runs:
        return None
    return (runs[len(runs) // 2], runs[int(len(runs) * .9)], len(runs))


def silhouette(im, scale=0.25):
    a = im.getchannel("A").point(lambda v: 255 if v > 110 else 0)
    s = (int(im.width * scale), int(im.height * scale))
    sil = Image.new("RGBA", im.size, (0, 0, 0, 0))
    sil.paste((0, 0, 0, 255), (0, 0), a)
    return sil.resize(s, Image.LANCZOS)


def sheet(pid):
    flat = Image.open(os.path.join(HERE, pid + ".png")).convert("RGBA")
    orig = Image.open(os.path.join(ORIG, pid + ".png")).convert("RGBA")
    G = (242, 242, 240, 255)
    W, H = 420 * 3 + 200, 440
    out = Image.new("RGBA", (W, H), G)
    for i, im in enumerate((orig, flat)):
        t = im.resize((400, 400), Image.LANCZOS)
        out.alpha_composite(t, (20 + i * 420, 20))
    sil = silhouette(flat)
    bg = Image.new("RGBA", (256, 256), (255, 255, 255, 255))
    bg.alpha_composite(sil)
    out.alpha_composite(bg, (860, 20))
    # real game size: .plot .plant-art is 128x150 css px
    for j, sz in enumerate((128, 150)):
        g = flat.resize((sz, int(sz * 150 / 128.0)), Image.LANCZOS)
        out.alpha_composite(g, (1140 + (0 if j == 0 else 0), 20 + j * 190))
    out.convert("RGB").save(os.path.join(CMP, pid + "-flat.png"))


def main():
    ids = sys.argv[1:] or IDS
    os.makedirs(CMP, exist_ok=True)
    for pid in ids:
        p = os.path.join(HERE, pid + ".png")
        im = Image.open(p).convert("RGBA")
        px = im.load()
        w, h = im.size
        corners = [px[0, 0], px[w - 1, 0], px[0, h - 1], px[w - 1, h - 1]]
        bbox = im.getchannel("A").getbbox()
        run, at = longest_run(im)
        st = stats(im)
        br = black_runs(im)
        opaque = sum(1 for y in range(0, h, 4) for x in range(0, w, 4)
                     if px[x, y][3] > 8)
        print("=" * 72)
        print("%s   %dx%d  bbox=%s  opaque=%.1f%%"
              % (pid, w, h, bbox, opaque / float((w // 4) * (h // 4)) * 100))
        print("  corners      : %s  -> %s"
              % (corners, "TRANSPARENT OK" if all(c[3] == 0 for c in corners)
                 else "*** NOT TRANSPARENT ***"))
        print("  longest run  : %d px identical RGB at %s" % (run, at))
        print("  colours>0.2%% : %d   maxS=%.2f  muddy=%.2f%%  "
              "pureWhite=%.3f%%  untintedGrey=%.3f%%  ink=%.2f%%"
              % (st["colours"], st["maxS"], st["muddy"], st["white"],
                 st["grey"], st["black"]))
        print("  black runs   : median=%s p90=%s n=%s"
              % (br if br else ("-", "-", 0)))
        print("  top fills    : %s" % (st["top"][:8],))
        sheet(pid)
    print("\nsheets -> %s" % CMP)


if __name__ == "__main__":
    main()
