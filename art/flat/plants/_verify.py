#!/usr/bin/env python3
"""Verification harness + BUILD GATES for the flat plant PNGs.

  python3 art/flat/plants/_verify.py [id ...]      # report + gates
  python3 art/flat/plants/_verify.py --report      # report only, no exit code

Per-plant checks, all by decoding actual pixels:
  1. transparency  -- the four corner pixels and the alpha bbox
  2. flatness      -- longest run of *bit-identical* RGB inside a fill
  3. palette       -- distinct opaque colours, max S, fills in the muddy band,
                      pure #FFFFFF count, untinted grey count
  4. outline       -- exact-#000000 pixel count + median black run
  5. saturation    -- median S and the % of the plant above S 0.60

Two hard GATES that fail the build (exit 1):

  G1  DIVERSITY.  Silhouette IoU at 128px between EVERY pair of shipped
      plants must be < 0.70.  Apple vs maple measured 0.930 before this gate
      existed, which is how three plants shipped as one asset in three
      colourways.  IoU is computed on the alpha channel alone, so it is
      blind to colour: you cannot pass it by recolouring.

  G2  SATURATION, PER PLANT.  Each plant INDIVIDUALLY must keep < 10% of its
      own opaque pixels above S 0.60 (TOCA Instant Tell #17).  Averaging
      across the set hides a loud plant; in game a plant renders alone.

Also writes contact sheets to _compare/: original | flat | silhouette@25% |
@128px.
"""
import os
import sys
import colorsys
import itertools
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
ORIG = os.path.join(ROOT, "art", "assets", "plants")
CMP = os.path.join(HERE, "_compare")

IDS = ["s-sunflower", "a-apple-tree", "m-maple-tree", "b-butterfly-bush",
       "p-pizza-palm", "u-ufo-tree", "r-robot-rosebush", "x-xylophone-tree",
       "b-banana-tree"]

IOU_MAX = 0.70          # G1
SAT_CEIL = 0.60         # G2 -- the saturation a fill may not exceed
SAT_MAX_PCT = 10.0      # G2 -- ...on more than this share of one plant
SIL_PX = 128            # both gates measure at the size the game renders


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
           "grey": 0, "black": 0, "top": [], "medS": 0.0, "hotpct": 0.0}
    sats, hot, lit = [], 0, 0
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
        # G2 population: every lit opaque pixel, ink and antialias excluded
        if v > 0.20:
            lit += n
            sats.extend([s] * n)
            if s > SAT_CEIL:
                hot += n
    sats.sort()
    out["medS"] = sats[len(sats) // 2] if sats else 0.0
    out["hotpct"] = 100.0 * hot / float(lit or 1)
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


def sil_mask(path, n=SIL_PX):
    """The G1 silhouette: alpha only, thresholded, at game resolution."""
    im = Image.open(path).convert("RGBA")
    a = im.getchannel("A").resize((n, n), Image.LANCZOS)
    return a.point(lambda v: 255 if v > 110 else 0)


def iou(ma, mb):
    pa, pb = ma.load(), mb.load()
    inter = union = 0
    for y in range(ma.size[1]):
        for x in range(ma.size[0]):
            A, B = pa[x, y] > 0, pb[x, y] > 0
            if A or B:
                union += 1
            if A and B:
                inter += 1
    return inter / float(union or 1)


def gate_diversity(ids):
    """G1: every pair of shipped plants must be < IOU_MAX apart."""
    masks = {i: sil_mask(os.path.join(HERE, i + ".png")) for i in ids}
    rows, worst, fails = [], 0.0, []
    for a, b in itertools.combinations(ids, 2):
        v = iou(masks[a], masks[b])
        rows.append((v, a, b))
        worst = max(worst, v)
        if v >= IOU_MAX:
            fails.append((v, a, b))
    rows.sort(reverse=True)
    print("=" * 78)
    print("G1  SILHOUETTE DIVERSITY -- IoU at %dpx, every pair must be < %.2f"
          % (SIL_PX, IOU_MAX))
    w = max(len(i) for i in ids)
    print("      " + "".join(("%-*s" % (7, i.split("-")[0][:6])) for i in ids))
    for a in ids:
        line = "  %-*s" % (w, a)
        for b in ids:
            line += ("   --  " if a == b
                     else "%-7.3f" % iou(masks[a], masks[b]))
        print(line)
    print("  worst pair: %.3f  (%s / %s)" % rows[0])
    for v, a, b in fails:
        print("  *** FAIL %.3f  %s / %s -- these are the same asset ***"
              % (v, a, b))
    return not fails


def gate_saturation(ids, st):
    """G2: each plant INDIVIDUALLY under SAT_MAX_PCT above S SAT_CEIL."""
    print("=" * 78)
    print("G2  SATURATION, PER PLANT -- each < %.0f%% of its own pixels "
          "above S %.2f" % (SAT_MAX_PCT, SAT_CEIL))
    ok = True
    for i in ids:
        s = st[i]
        bad = s["hotpct"] >= SAT_MAX_PCT
        ok = ok and not bad
        print("  %-18s medS=%.3f  maxS=%.2f  >S%.2f=%5.1f%%   %s"
              % (i, s["medS"], s["maxS"], SAT_CEIL, s["hotpct"],
                 "*** FAIL ***" if bad else "ok"))
    return ok


def sheet(pid):
    flat = Image.open(os.path.join(HERE, pid + ".png")).convert("RGBA")
    op = os.path.join(ORIG, pid + ".png")
    orig = (Image.open(op).convert("RGBA") if os.path.exists(op)
            else Image.new("RGBA", (400, 400), (0, 0, 0, 0)))
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
        out.alpha_composite(g, (1140, 20 + j * 190))
    out.convert("RGB").save(os.path.join(CMP, pid + "-flat.png"))


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    report_only = "--report" in sys.argv
    ids = args or IDS
    os.makedirs(CMP, exist_ok=True)
    allstats = {}
    for pid in ids:
        p = os.path.join(HERE, pid + ".png")
        im = Image.open(p).convert("RGBA")
        px = im.load()
        w, h = im.size
        corners = [px[0, 0], px[w - 1, 0], px[0, h - 1], px[w - 1, h - 1]]
        bbox = im.getchannel("A").getbbox()
        run, at = longest_run(im)
        st = stats(im)
        allstats[pid] = st
        br = black_runs(im)
        opaque = sum(1 for y in range(0, h, 4) for x in range(0, w, 4)
                     if px[x, y][3] > 8)
        print("=" * 78)
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
        print("  saturation   : medS=%.3f  above S%.2f = %.1f%%"
              % (st["medS"], SAT_CEIL, st["hotpct"]))
        print("  black runs   : median=%s p90=%s n=%s  (%.2f%%-%.2f%% of 880)"
              % ((br if br else ("-", "-", 0))
                 + ((br[0] / 8.80, br[1] / 8.80) if br else (0, 0))))
        print("  top fills    : %s" % (st["top"][:8],))
        sheet(pid)

    g2 = gate_saturation(ids, allstats)
    g1 = gate_diversity(ids) if len(ids) > 1 else True
    print("=" * 78)
    print("sheets -> %s" % CMP)
    print("GATES: G1 diversity %s   G2 saturation %s"
          % ("PASS" if g1 else "FAIL", "PASS" if g2 else "FAIL"))
    if not report_only and not (g1 and g2):
        sys.exit(1)


if __name__ == "__main__":
    main()
