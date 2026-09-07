#!/usr/bin/env python3
"""Diff docs/FLAT_ART_BRIEF.md's palette tables against `_kit.py` -- the
single source of truth for every plant-kit hex.

    python3 art/flat/plants/_check_palette.py

`_kit.py`'s PALETTE section (core + extended tokens) is read directly with
`vars(_kit)` -- not a hand-copied list -- so a new token added to the kit is
picked up automatically, the same fix applied to `_verify.py`'s shipped-plant
glob. For every such token this script finds every `` `token` | `#hex` ``
occurrence in the brief (matched by name: `SUN_SHADE` <-> `` `sun-shade` ``)
and reports:

  DRIFT      the brief's hex does not match `_kit.py`'s
  DUPLICATE  the token appears more than once in the brief with different
             hexes (the `accent-deep` failure this gate caught)
  MISSING    the token's hex appears nowhere in the brief under any name
             (the `steel-dark` failure this gate caught)

A token whose hex DOES appear in the brief under a different name (e.g.
`_kit.py`'s `BARK_LITE` ships as the brief's `soil-lite`, a deliberate
alias noted in `_kit.py`'s own comment) is reported as ALIAS, not MISSING --
that is not drift, just a second name for the same value.

Exits 0 with "zero drift" when every check passes; exits 1 and lists every
problem otherwise. This is intentionally NOT a full brief-generator: the
brief's tables mix `_kit.py` tokens with scene/background-only tokens
(`stone`, `worm`, `hill-far`, `bush`, prop-variant bands...) that have no
`_kit.py` counterpart to check against. What it CAN check mechanically, it
does, so a hex typo'd into the brief cannot silently ship again.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import _kit as K

BRIEF = os.path.abspath(os.path.join(HERE, "..", "..", "..", "docs",
                                      "FLAT_ART_BRIEF.md"))

HEX_RE = re.compile(r'^#[0-9a-fA-F]{6}$')
ROW_RE = re.compile(r'`([a-z][a-z0-9-]*)`\s*\|\s*`(#[0-9a-fA-F]{6})`')


def kit_tokens():
    """{VAR_NAME: '#rrggbb'} for every uppercase hex-string constant in
    _kit.py's PALETTE section -- read from the live module, not retyped."""
    out = {}
    for name, val in vars(K).items():
        if name.isupper() and isinstance(val, str) and HEX_RE.match(val):
            out[name] = val.lower()
    return out


def kebab(var):
    return var.lower().replace("_", "-")


def brief_occurrences():
    """token -> [hex, hex, ...] for every markdown-table hit, in file order."""
    text = open(BRIEF, encoding="utf-8").read()
    out = {}
    for m in ROW_RE.finditer(text):
        tok, hexv = m.group(1), m.group(2).lower()
        out.setdefault(tok, []).append(hexv)
    return out


def main():
    kit = kit_tokens()
    brief = brief_occurrences()
    by_hex = {}
    for tok, hexes in brief.items():
        for h in hexes:
            by_hex.setdefault(h, set()).add(tok)

    problems, aliases, ok = [], [], []
    for var, hexv in sorted(kit.items()):
        tok = kebab(var)
        if tok not in brief:
            other_names = by_hex.get(hexv, set())
            if other_names:
                aliases.append("ALIAS    %-14s kit hex %s ships in the brief "
                                "as %s, not `%s` -- not drift, just a second "
                                "name" % (tok, hexv,
                                          sorted("`%s`" % n for n in other_names),
                                          tok))
            else:
                problems.append("MISSING  %-14s %s is not documented in "
                                 "FLAT_ART_BRIEF.md under any name" % (tok, hexv))
            continue
        uniq = sorted(set(brief[tok]))
        if len(uniq) > 1:
            problems.append("DUPLICATE %-13s appears %d times in the brief "
                             "with different hexes %s (kit says %s)"
                             % (tok, len(brief[tok]), uniq, hexv))
        elif uniq[0] != hexv:
            problems.append("DRIFT    %-14s brief=%s  kit=%s"
                             % (tok, uniq[0], hexv))
        else:
            ok.append(tok)

    print("=" * 78)
    print("PALETTE DRIFT CHECK -- %d _kit.py tokens checked against %s"
          % (len(kit), os.path.relpath(BRIEF, os.path.join(HERE, "..", "..", ".."))))
    print("  %d match exactly" % len(ok))
    for a in aliases:
        print("  %s" % a)
    if not problems:
        print("  zero drift -- every _kit.py hex that names a brief token "
              "matches it, no token is duplicated with two values, and "
              "nothing is undocumented.")
    else:
        for p in problems:
            print("  *** %s" % p)
    print("=" * 78)
    if problems:
        sys.exit(1)


if __name__ == "__main__":
    main()
