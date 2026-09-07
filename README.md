# 🌱 Alphabet Garden

Copyright (c) 2026 Clint McLeod. All rights reserved.

A wacky, joyful planting game for kindergarteners. Plant **seed letters** and choose
what they grow into — from the totally real to the gloriously impossible. Plant a **B**
and pick whether it blooms into a **Banana Tree**, a **Butterfly Bush**, or a **Burger Bush**.
Your garden is saved and keeps growing across visits — even while you are away.

## Play

It is a static site — no build step. Open `index.html`, or serve the folder:

```bash
python3 -m http.server 8437
# then visit http://localhost:8437
```

## Features

- **78 hand-crafted plants** — 26 letters × 3 (one real, one silly, one wacky)
- **Custom claymation art** for every plant, critter, effect, and UI element
- **Persistent garden** saved to `localStorage`, with offline growth between sessions
- **Sticker book** tracking all 78 discoveries
- **Living world** — day/night cycle, drifting clouds, butterflies and fireflies,
  a rain button, rainbows, synthesized sound effects, and spoken narration for pre-readers
- **Grows with the child** — unlock more garden plots as plants mature

## Project layout

| Path | What |
|---|---|
| `index.html` | Game shell |
| `css/style.css` | All styling |
| `js/game.js` | Game engine |
| `js/plants/` | The 78-plant catalog (data + fallback SVG) |
| `art/assets/` | Custom PNG art (plants, sky, critters, fx, ui, garden) |
| `ART_ASSETS.md` | The art-direction bible used to generate every asset |
