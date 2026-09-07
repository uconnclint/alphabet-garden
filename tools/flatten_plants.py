#!/usr/bin/env python3
"""
flatten_plants.py — convert glossy soft-3D "claymation" plant renders into flat,
outlined artwork that targets docs/TOCA_STANDARD.md.

Reads   : art/assets/plants/*.png      (NEVER modified)
Writes  : art/flat/plants/*.png        (1024x1024 RGBA, same canvas/registration)

Pipeline
  1. alpha mask + outside-RGB nearest-fill (stops the black matte bleeding in)
  2. specular kill — small bright low-saturation blobs are Telea-inpainted back
     into their surrounding fill (instant tell #9)
  3. crease extraction — a difference-of-gaussians valley detector run on the
     ORIGINAL luminance finds the shading grooves the render uses to separate
     petals / lobes / panels, and re-authors them as internal contour lines
     (§3.3 "internal contour lines ... is why gradients are unnecessary")
  4. edge-preserving smoothing at a reduced working resolution
  5. k-means colour quantisation in Lab
  6. region hygiene — open/close + small-component removal + nearest refill
  7. palette discipline — tiered hue families (ink / neutral / chroma), S/V band
     enforcement, neutral tinting, no pure white, no muddy V 0.35-0.55
  8. two-tone form — per family: base + one shadow (dV 0.12, hue-shifted cooler)
     + at most one flat highlight chip
  9. smooth label upscale (bilinear per-label masks, argmax)
 10. outlines — pure #000000, distance-transform based so joins are inherently
     ROUND. Weight is PER CONNECTED COMPONENT (0.014 x that component's height,
     capped so it can never eat a small prop). Silhouette is drawn INWARD so the
     canvas footprint and registration are untouched.

Usage
  python3 tools/flatten_plants.py                     # all 78
  python3 tools/flatten_plants.py s-sunflower u-ufo-tree
  python3 tools/flatten_plants.py --contact --measure
"""

from __future__ import annotations

import argparse
import colorsys
import os
import sys

import cv2
import numpy as np
from PIL import Image
from skimage.morphology import skeletonize

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC_DIR = os.path.join(ROOT, "art", "assets", "plants")
OUT_DIR = os.path.join(ROOT, "art", "flat", "plants")

# ------------------------------------------------------------------------ parameters
P = dict(
    work=560,              # segmentation resolution
    k=16,                  # initial k-means clusters
    merge_lab=12.0,        # merge clusters closer than this in Lab
    bilateral_iters=3,
    bilateral_d=9,
    bilateral_sc=38,
    bilateral_ss=9,
    ms_sp=12, ms_sr=22,    # pyrMeanShift
    spec_v=0.86,
    spec_s=0.32,
    spec_max_frac=0.010,
    open_r=4,
    close_r=5,
    min_area_frac=0.0016,
    label_smooth=2.2,      # gaussian sigma on label probabilities (work res)
    # --- families
    ink_v=0.30,            # below this V -> ink tier (eyes, pupils, seams)
    ink_max_frac=0.035,    # ...but only if the region is small. A LARGE dark area
                           # is a fill in shadow, not ink - forcing it to near-black
                           # punches holes in the art (§3.1 "no dark mid-tone fills"
                           # means lift it, not blacken it).
    neutral_s=0.16,        # below this S -> neutral tier
    hue_bucket=40.0,       # agglomerative hue merge width, degrees
    max_chroma_fams=5,
    # --- colour discipline
    s_cap=0.82,
    s_large_cap=0.70,
    v_floor=0.60,
    v_ceil=0.965,
    ink_v_set=0.14,
    shadow_dv=0.12,
    shadow_cool=10.0,
    shadow_ds=0.05,
    hi_dv=0.10,
    hi_max_frac=0.18,
    fam_hue_lock=25.0,     # max hue shift the two-tone collapse may impose (deg)
    house_pull=0.45,
    house_tol=0.70,
    # --- creases
    crease=1,
    crease_sigma=0.016,    # x object height
    crease_t=0.070,        # DoG response threshold (0-1)
    crease_min_len=0.055,  # min skeleton length, x object height
    crease_long_len=0.150, # a stroke this long may float free of the silhouette
    crease_density=0.26,   # drop components whose ink fills >this of their bbox
    crease_max_frac=0.045, # raw crease mask <= this share of object area
    # --- silhouette
    sil_smooth=0.007,      # morphological smoothing radius, x object height
    # --- outlines
    outline_pct=0.014,
    outline_min=2.0,
    outline_max_rel=0.16,  # <= this x component's short side (never eat a prop)
    internal_scale=0.72,
    # An internal contour line is only legitimate where the ORIGINAL geometry has
    # an actual edge (a crease) or where two genuinely different materials meet.
    # Outlining every quantiser boundary traces lighting level-sets, which is the
    # "flattened 3D render" tell.
    internal_de_min=36.0,  # min Lab distance for a material boundary to be inked
)

PALETTE_ANCHORS = [
    "#7ec850", "#5da23c", "#93d762", "#72be46",
    "#a9713f", "#8a5a33", "#bd8450", "#93633a",
    "#fff7e6", "#ffd23f", "#ffc42c", "#ff9d52", "#ffab86", "#cdefff",
]
NEUTRAL_TINT_HUE = 222.0 / 360.0
NEUTRAL_TINT_S = 0.14
CREAM_HUE = 40.0 / 360.0
CREAM_S = 0.09


# ------------------------------------------------------------------------ utilities
def hex2rgb(h):
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], np.float64)


def rgb2hsv(rgb):
    r, g, b = [float(c) / 255.0 for c in rgb]
    return colorsys.rgb_to_hsv(r, g, b)


def hsv2rgb(h, s, v):
    r, g, b = colorsys.hsv_to_rgb(h % 1.0, max(0.0, min(1.0, s)), max(0.0, min(1.0, v)))
    return np.array([r * 255.0, g * 255.0, b * 255.0])


def disc(r):
    r = max(1, int(r))
    return cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 1, 2 * r + 1))


def hue_dist(a, b):
    d = abs((a - b) * 360.0) % 360.0
    return min(d, 360.0 - d)


def nearest_fill(values, known_mask):
    unknown = (~known_mask).astype(np.uint8)
    if unknown.sum() == 0 or known_mask.sum() == 0:
        return values
    _, lbl = cv2.distanceTransformWithLabels(
        unknown, cv2.DIST_L2, 5, labelType=cv2.DIST_LABEL_PIXEL)
    flat_known = np.flatnonzero(known_mask.ravel())
    idx = np.zeros(int(lbl.max()) + 1, np.int64)
    idx[lbl.ravel()[flat_known]] = flat_known
    nearest = idx[lbl.ravel()]
    flatv = values.reshape(values.shape[0] * values.shape[1], -1)
    return flatv[nearest].reshape(values.shape)


# --------------------------------------------------------------------- gloss removal
def kill_speculars(rgb, mask):
    hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV_FULL).astype(np.float32)
    s = hsv[..., 1] / 255.0
    v = hsv[..., 2] / 255.0
    cand = ((v > P["spec_v"]) & (s < P["spec_s"]) & mask).astype(np.uint8)
    if cand.sum() == 0:
        return rgb, 0
    obj_area = float(mask.sum())
    n, lab, stats, _ = cv2.connectedComponentsWithStats(cand, 8)
    keep = np.zeros_like(cand)
    hit = 0
    for i in range(1, n):
        if stats[i, cv2.CC_STAT_AREA] <= obj_area * P["spec_max_frac"]:
            keep[lab == i] = 1
            hit += 1
    if keep.sum() == 0:
        return rgb, 0
    keep = (cv2.dilate(keep, disc(3)).astype(bool) & mask).astype(np.uint8)
    return cv2.inpaint(rgb, keep, 14, cv2.INPAINT_TELEA), hit


# ------------------------------------------------------------------- crease detection
def creases(rgb, mask, obj_h, obj_area):
    """Find the dark shading grooves the 3D render uses to separate forms and
    return them as a 1px SKELETON, so they can be re-drawn as uniform-weight,
    round-joined flat contour lines rather than as traced blobs."""
    if not P["crease"]:
        return np.zeros(mask.shape, bool)
    g = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY).astype(np.float32) / 255.0
    g = cv2.bilateralFilter(g, 7, 0.06, 6)
    sg = max(1.5, P["crease_sigma"] * obj_h)
    lo = cv2.GaussianBlur(g, (0, 0), sg)
    hi = cv2.GaussianBlur(g, (0, 0), sg * 0.35)
    resp = lo - hi                       # positive inside dark valleys
    resp[~mask] = 0.0

    t = P["crease_t"]
    for _ in range(10):
        if ((resp > t) & mask).sum() <= P["crease_max_frac"] * obj_area:
            break
        t *= 1.2
    c = ((resp > t) & mask).astype(np.uint8)
    c = cv2.morphologyEx(c, cv2.MORPH_CLOSE, disc(2))

    # drop dense texture meshes (seed-head bumps, bark stipple) before thinning
    n, lab, stats, _ = cv2.connectedComponentsWithStats(c, 8)
    keep = np.zeros_like(c)
    for i in range(1, n):
        bw = stats[i, cv2.CC_STAT_WIDTH]
        bh = stats[i, cv2.CC_STAT_HEIGHT]
        a = stats[i, cv2.CC_STAT_AREA]
        if a > P["crease_density"] * max(1, bw * bh):
            continue
        keep[lab == i] = 1

    return prune_strokes(skeletonize(keep.astype(bool)), mask, obj_h)


def prune_strokes(edges, mask, obj_h):
    """Drop orphan strokes. A drawn contour line either runs a long way across the
    form or it terminates on the silhouette; a short stroke floating in the middle
    of a fill is a render artifact and reads as dirt on the canvas."""
    sk = skeletonize(edges.astype(bool)).astype(np.uint8)
    min_len = P["crease_min_len"] * obj_h
    long_len = P["crease_long_len"] * obj_h
    m8 = mask.astype(np.uint8)
    rim = cv2.dilate(m8 - cv2.erode(m8, disc(max(2, int(0.02 * obj_h)))), disc(2))
    n, lab, stats, _ = cv2.connectedComponentsWithStats(sk, 8)
    out = np.zeros_like(sk)
    for i in range(1, n):
        ln = stats[i, cv2.CC_STAT_AREA]
        if ln < min_len:
            continue
        sel = lab == i
        if ln >= long_len or rim[sel].any():
            out[sel] = 1
    return out.astype(bool)


# ---------------------------------------------------------------------- palette work
def snap_house(h, s, v):
    best, bd = None, 1e9
    for hx in PALETTE_ANCHORS:
        ah, asat, av = rgb2hsv(hex2rgb(hx))
        d = (hue_dist(h, ah) / 22.0) ** 2 + ((s - asat) * 1.5) ** 2 + ((v - av) * 1.5) ** 2
        if d < bd:
            bd, best = d, (ah, asat, av)
    if best is None or bd > P["house_tol"]:
        return h, s, v
    ah, asat, av = best
    t = P["house_pull"] * (1.0 - bd / P["house_tol"])
    dh = ((ah - h + 0.5) % 1.0) - 0.5
    return (h + dh * t) % 1.0, s + (asat - s) * t, v + (av - v) * t


def discipline(h, s, v, frac):
    if v < P["ink_v"] and frac < P["ink_max_frac"]:
        return h, min(s, 0.55), P["ink_v_set"]
    if s < 0.07:
        h, s = (CREAM_HUE, CREAM_S) if v > 0.86 else (NEUTRAL_TINT_HUE, NEUTRAL_TINT_S)
    elif s < P["neutral_s"]:
        h, s = (CREAM_HUE, max(s, CREAM_S)) if v > 0.86 else (NEUTRAL_TINT_HUE, max(s, NEUTRAL_TINT_S))
    s = min(s, P["s_cap"])
    if frac > 0.12:
        s = min(s, P["s_large_cap"])
    v = min(max(v, P["v_floor"]), P["v_ceil"])
    h, s, v = snap_house(h, s, v)
    return h, min(s, P["s_cap"]), min(max(v, P["v_floor"]), P["v_ceil"])


def assign_families(colors, fracs):
    """Tiered grouping: ink / neutral-light / neutral-dark / chroma hue buckets.
    Hues are NEVER moved by this step - it only decides which colours share a
    two-tone group and where an internal contour line is warranted."""
    n = len(colors)
    fam = [None] * n
    chroma = []
    for i, (h, s, v) in enumerate(colors):
        if v < P["ink_v"] and fracs[i] < P["ink_max_frac"]:
            fam[i] = "ink"
        elif s < P["neutral_s"]:
            fam[i] = "neutral_hi" if v > 0.86 else "neutral_lo"
        else:
            chroma.append(i)
    # agglomerative hue merge, seeded from the largest area
    groups = []   # (hue centre, [indices], area)
    for i in sorted(chroma, key=lambda i: -fracs[i]):
        h = colors[i][0]
        for gi, (gh, mem, ar) in enumerate(groups):
            if hue_dist(h, gh) <= P["hue_bucket"] / 360.0 * 360.0 / 360.0 * 1.0 and \
               hue_dist(h, gh) <= P["hue_bucket"]:
                mem.append(i)
                groups[gi] = (gh, mem, ar + fracs[i])
                break
        else:
            groups.append((h, [i], fracs[i]))
    # cap the number of chroma families (§3.1: 3-4 hue families do 95% of work)
    while len(groups) > P["max_chroma_fams"]:
        groups.sort(key=lambda g: g[2])
        small = groups.pop(0)
        tgt = min(range(len(groups)), key=lambda j: hue_dist(small[0], groups[j][0]))
        gh, mem, ar = groups[tgt]
        groups[tgt] = (gh, mem + small[1], ar + small[2])
    for gi, (gh, mem, ar) in enumerate(groups):
        for i in mem:
            fam[i] = "c%d" % gi
    return fam


def two_tone(colors, fracs, fam_of):
    out = list(colors)
    for f in sorted(set(fam_of)):
        idx = [i for i in range(len(colors)) if fam_of[i] == f]
        if f == "ink":
            for i in idx:
                h, s, _ = colors[i]
                out[i] = (h, min(s, 0.55), P["ink_v_set"])
            continue
        if len(idx) <= 1:
            continue
        base_i = max(idx, key=lambda i: fracs[i])
        bh, bs, bv = colors[base_i]
        sh = (bh + P["shadow_cool"] / 360.0) % 1.0
        sv = max(bv - P["shadow_dv"], 0.56)
        ss = min(bs + P["shadow_ds"], P["s_cap"])
        hv = min(bv + P["hi_dv"], P["v_ceil"])
        hs = max(bs - 0.10, 0.05)
        tot = sum(fracs[i] for i in idx) or 1e-9
        for i in idx:
            if i == base_i:
                out[i] = (bh, bs, bv)
            elif colors[i][2] < bv:
                out[i] = (sh, ss, sv)
            elif fracs[i] / tot <= P["hi_max_frac"]:
                out[i] = (bh, hs, hv)
            else:
                out[i] = (bh, bs, bv)
    # Guard: two-tone collapse may only restate a region's VALUE, never invent a
    # new hue for it. Without this a dark neutral (a saucer rim, a metal edge)
    # that happens to share a family with a big green mass comes out green.
    for i, ((h0, _, _), (h1, s1, v1)) in enumerate(zip(colors, out)):
        if hue_dist(h0, h1) > P["fam_hue_lock"]:
            out[i] = (h0, s1, v1)
    return out


# ------------------------------------------------------------------------- main pass
def flatten(path, out_path, measure=False):
    im = Image.open(path).convert("RGBA")
    W, H = im.size
    arr = np.array(im)
    rgb = arr[..., :3].copy()
    alpha = arr[..., 3].astype(np.float32) / 255.0
    mask = alpha >= 0.5
    if mask.sum() < 100:
        raise RuntimeError("empty alpha: " + path)

    ys, xs = np.where(mask)
    obj_h = float(ys.max() - ys.min() + 1)
    obj_area = float(mask.sum())

    # ---- silhouette hygiene: the render's micro-lumpiness is not design intent.
    # Open+close with a small disc gives the clean closed blob the standard wants
    # without moving the shape's centre, extent or registration.
    sr = int(round(P["sil_smooth"] * obj_h))
    if sr >= 1:
        m8 = mask.astype(np.uint8)
        m8 = cv2.morphologyEx(m8, cv2.MORPH_OPEN, disc(sr))
        m8 = cv2.morphologyEx(m8, cv2.MORPH_CLOSE, disc(sr))
        if m8.sum() > 0.7 * mask.sum():
            mask = m8.astype(bool)
    # rebuild a clean anti-aliased alpha from the (possibly smoothed) mask
    sd = (cv2.distanceTransform(mask.astype(np.uint8), cv2.DIST_L2, 5)
          - cv2.distanceTransform((~mask).astype(np.uint8), cv2.DIST_L2, 5))
    alpha = np.clip(sd + 0.5, 0.0, 1.0)

    rgb = nearest_fill(rgb, mask).astype(np.uint8)
    rgb, n_spec = kill_speculars(rgb, mask)
    crease = creases(rgb, mask, obj_h, obj_area)

    # ---- smooth + quantise at working resolution
    w = P["work"]
    small = cv2.resize(rgb, (w, w), interpolation=cv2.INTER_AREA)
    m_small = cv2.resize(mask.astype(np.uint8) * 255, (w, w),
                         interpolation=cv2.INTER_AREA) > 127
    small = cv2.pyrMeanShiftFiltering(small, P["ms_sp"], P["ms_sr"], maxLevel=2)
    for _ in range(P["bilateral_iters"]):
        small = cv2.bilateralFilter(small, P["bilateral_d"],
                                    P["bilateral_sc"], P["bilateral_ss"])

    lab = cv2.cvtColor(small, cv2.COLOR_RGB2LAB).astype(np.float32)
    samples = lab[m_small]
    k = min(P["k"], max(2, len(np.unique(samples.round(0), axis=0))))
    crit = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 40, 0.5)
    _, lbl_s, centers = cv2.kmeans(samples, k, None, crit, 8, cv2.KMEANS_PP_CENTERS)
    lbl_s = lbl_s.ravel()

    order = np.argsort(-np.bincount(lbl_s, minlength=k))
    remap, kept = {}, []
    for i in order:
        for j in kept:
            if np.linalg.norm(centers[i] - centers[j]) < P["merge_lab"]:
                remap[int(i)] = j
                break
        else:
            kept.append(int(i))
            remap[int(i)] = int(i)
    lbl_s = np.array([remap[int(x)] for x in lbl_s])
    compact = {c: i for i, c in enumerate(sorted(set(lbl_s.tolist())))}
    lbl_s = np.array([compact[int(x)] for x in lbl_s])
    nk = len(compact)

    labmap = np.full((w, w), -1, np.int32)
    labmap[m_small] = lbl_s

    # ---- region hygiene
    for i in range(nk):
        b = (labmap == i).astype(np.uint8)
        b = cv2.morphologyEx(b, cv2.MORPH_OPEN, disc(P["open_r"]))
        b = cv2.morphologyEx(b, cv2.MORPH_CLOSE, disc(P["close_r"]))
        labmap[(labmap == i) & (b == 0)] = -1
        labmap[(b == 1) & m_small] = i
    min_a = max(6, int(P["min_area_frac"] * m_small.sum()))
    for i in range(nk):
        n, cc, stats, _ = cv2.connectedComponentsWithStats((labmap == i).astype(np.uint8), 8)
        for c in range(1, n):
            if stats[c, cv2.CC_STAT_AREA] < min_a:
                labmap[cc == c] = -1
    known = labmap >= 0
    if known.sum() == 0:
        raise RuntimeError("hygiene wiped everything: " + path)
    labmap = nearest_fill(labmap[..., None], known)[..., 0]
    labmap[~m_small] = -1

    present = sorted(set(labmap[m_small].tolist()))
    lm = labmap.copy()
    for i, c in enumerate(present):
        lm[labmap == c] = i
    labmap = lm
    nk = len(present)

    colors, fracs = [], []
    for i in range(nk):
        sel = labmap == i
        colors.append(rgb2hsv(np.median(small[sel].astype(np.float64), axis=0)))
        fracs.append(sel.sum() / float(m_small.sum()))

    fam_of = assign_families(colors, fracs)
    colors = [discipline(h, s, v, f) for (h, s, v), f in zip(colors, fracs)]
    colors = two_tone(colors, fracs, fam_of)
    rgb_of = [hsv2rgb(*c) for c in colors]

    # ---- smooth upscale
    probs = np.zeros((H, W, nk), np.float32)
    for i in range(nk):
        b = cv2.GaussianBlur((labmap == i).astype(np.float32), (0, 0), P["label_smooth"])
        probs[..., i] = cv2.resize(b, (W, H), interpolation=cv2.INTER_LINEAR)
    full = np.argmax(probs, axis=2).astype(np.int32)
    full[~mask] = -1
    full = nearest_fill(full[..., None], mask)[..., 0]

    fill = np.zeros((H, W, 3), np.float32)
    for i in range(nk):
        fill[full == i] = rgb_of[i]

    # ---- outline weight field, PER connected component of the silhouette
    m_u8 = mask.astype(np.uint8)
    ncc, cc, stats, _ = cv2.connectedComponentsWithStats(m_u8, 8)
    wfield = np.zeros((H, W), np.float32)
    widths = []
    for i in range(1, ncc):
        ch = stats[i, cv2.CC_STAT_HEIGHT]
        cwd = stats[i, cv2.CC_STAT_WIDTH]
        ow = P["outline_pct"] * ch
        ow = min(ow, P["outline_max_rel"] * min(ch, cwd))
        ow = max(P["outline_min"], ow)
        wfield[cc == i] = ow
        widths.append(round(ow, 1))

    d_in = cv2.distanceTransform(m_u8, cv2.DIST_L2, 5)
    ink_sil = np.clip(wfield + 0.5 - d_in, 0.0, 1.0) * m_u8

    # ---- internal contour lines: inter-family region boundaries + creases
    # Only ink a region boundary when the two fills are genuinely different
    # MATERIALS (large Lab distance) - not when they are a base/shadow pair or two
    # neighbouring steps of the same lighting ramp.
    labcols = cv2.cvtColor(
        np.array(rgb_of, np.float32).reshape(1, -1, 3).astype(np.uint8),
        cv2.COLOR_RGB2LAB).astype(np.float32)[0]
    mat = np.zeros((nk, nk), bool)
    for i in range(nk):
        for j in range(nk):
            mat[i, j] = np.linalg.norm(labcols[i] - labcols[j]) >= P["internal_de_min"]
    idxmap = np.clip(full, 0, nk - 1)
    e = np.zeros((H, W), bool)
    e[:, :-1] |= mat[idxmap[:, :-1], idxmap[:, 1:]]
    e[:-1, :] |= mat[idxmap[:-1, :], idxmap[1:, :]]
    e &= mask
    e |= crease
    e = prune_strokes(e, mask, obj_h)
    if e.any():
        d_e = cv2.distanceTransform((~e).astype(np.uint8), cv2.DIST_L2, 5)
        iwf = wfield * P["internal_scale"]
        ink_int = np.clip(iwf / 2.0 + 0.5 - d_e, 0.0, 1.0) * m_u8
    else:
        ink_int = np.zeros((H, W), np.float32)

    ink = np.maximum(ink_sil, ink_int)
    out_rgb = fill * (1.0 - ink[..., None])
    out = np.dstack([np.clip(out_rgb, 0, 255), alpha * 255.0]).astype(np.uint8)

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    Image.fromarray(out).save(out_path)

    info = dict(name=os.path.basename(path), colors=nk, spec_blobs=n_spec,
                widths=widths[:6], fams=len(set(fam_of)),
                ink_frac=round(float((ink > 0.5).sum()) / obj_area, 3),
                hexes=["#%02x%02x%02x" % tuple(int(round(x)) for x in c) for c in rgb_of])
    if measure:
        info["run"] = longest_flat_run(out)
    return info


# ----------------------------------------------------------------- flatness measuring
def longest_flat_run(out):
    """Longest horizontal run of literally identical RGB inside the opaque area."""
    a = out[..., 3] >= 250
    v = out[..., :3].astype(np.int32)
    key = (v[..., 0] << 16) | (v[..., 1] << 8) | v[..., 2]
    key = np.where(a, key, -1)
    best = 0
    for y in range(out.shape[0]):
        row = key[y]
        chg = np.flatnonzero(np.diff(row) != 0)
        bounds = np.concatenate(([-1], chg, [len(row) - 1]))
        lens = np.diff(bounds)
        valid = row[bounds[1:]] >= 0
        if valid.any():
            best = max(best, int(lens[valid].max()))
    return best


GAME_PX = 150   # .plot .plant-art is 128x150 css px -> this is the real read size


def contact_sheet(src, dst, out_png, size=460):
    """orig | flat | flat as the game actually shows it (150px, re-magnified)"""
    a = Image.open(src).convert("RGBA").resize((size, size), Image.LANCZOS)
    b = Image.open(dst).convert("RGBA").resize((size, size), Image.LANCZOS)
    tiny = Image.open(dst).convert("RGBA").resize((GAME_PX, GAME_PX), Image.LANCZOS)
    c = tiny.resize((size, size), Image.NEAREST)
    sheet = Image.new("RGB", (size * 3 + 48, size), (242, 242, 240))
    for i, im in enumerate((a, b, c)):
        bg = Image.new("RGB", (size, size), (242, 242, 240))
        bg.paste(im, (0, 0), im)
        sheet.paste(bg, (i * (size + 24), 0))
    sheet.save(out_png)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("names", nargs="*")
    ap.add_argument("--contact", action="store_true")
    ap.add_argument("--measure", action="store_true")
    ap.add_argument("--contact-dir", default=None)
    ap.add_argument("--set", action="append", default=[])
    args = ap.parse_args()

    for kv in args.set:
        key, val = kv.split("=", 1)
        P[key] = int(float(val)) if isinstance(P[key], int) else float(val)

    names = args.names or sorted(
        os.path.splitext(f)[0] for f in os.listdir(SRC_DIR) if f.endswith(".png"))
    for n in names:
        src = os.path.join(SRC_DIR, n + ".png")
        dst = os.path.join(OUT_DIR, n + ".png")
        info = flatten(src, dst, measure=args.measure)
        extra = ("  run=%d" % info["run"]) if args.measure else ""
        print("%-26s cols=%-2d fams=%d spec=%-3d ink=%.3f w=%s%s\n    %s" % (
            n, info["colors"], info["fams"], info["spec_blobs"], info["ink_frac"],
            info["widths"], extra, " ".join(info["hexes"])))
        if args.contact:
            cdir = args.contact_dir or os.path.join(OUT_DIR, "_compare")
            os.makedirs(cdir, exist_ok=True)
            contact_sheet(src, dst, os.path.join(cdir, n + ".png"))


if __name__ == "__main__":
    sys.exit(main())
