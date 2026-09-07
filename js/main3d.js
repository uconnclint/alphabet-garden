// main3d.js — boots the WebGL world layer and marries it to the game model in game.js.
//
// Load order matters and is enforced by the browser, not by us: index.html loads the plant DB
// and game.js as classic scripts, and this module is deferred, so `window.GardenGame` is
// guaranteed to exist by the time we run. If it somehow does not, we bail loudly and leave the
// DOM UI (title screen, modals, HUD) working rather than throwing on boot.

import { createStage } from './systems/stage.js';
import { attachTweensTo, tweens } from './systems/tween.js';
import { createParticles } from './systems/particles.js';
import * as Textures from './systems/textures.js';
import { createInput } from './systems/input.js';
import { createGardenScene } from './scenes/GardenScene.js';

const game = window.GardenGame;

if (!game) {
  console.error('[garden] game.js did not publish window.GardenGame — the world cannot be drawn.');
} else {
  const stage = createStage({
    container: document.getElementById('stage3d'),
    background: null            // the sky plate is a sprite, so the clear colour stays transparent
  });

  Textures.setRenderer(stage.renderer);
  Textures.setBasePath('art/assets/');
  attachTweensTo(stage);

  const fx = createParticles(stage, { max: 800 });
  const input = createInput(stage);

  // Everything the world needs on its FIRST frame. Plant art (78 files) is deliberately not in
  // here — it loads per plot, on demand, so a kid with one seed planted downloads one PNG.
  const CORE = [
    'sky/sun.png', 'sky/moon.png', 'sky/star.png',
    'sky/cloud_puffy.png', 'sky/cloud_wisp.png', 'sky/rain_cloud.png', 'sky/rainbow.png',
    'garden/hills_backdrop.png', 'garden/grass_foreground.png',
    'garden/dirt_plot_empty.png', 'garden/dirt_plot_seeded.png',
    'garden/seed.png', 'garden/sprout.png', 'garden/lock_sign.png',
    'fx/sparkle.png', 'fx/poof_cloud.png', 'fx/water_splash.png', 'fx/celebration_star.png'
  ];
  await Textures.loadAll(CORE);   // never rejects — a missing file becomes procedural art

  const scene = createGardenScene({ stage: stage, fx: fx, input: input, game: game });

  // Development handle. Harmless in production and invaluable when a teacher reports
  // "the garden looks weird on the classroom iPad".
  window.__garden3d = {
    stage: stage, fx: fx, input: input, scene: scene, Textures: Textures, tweens: tweens
  };

  let logged = false;
  stage.onResize(s => {
    if (logged) return;
    logged = true;
    console.log('[garden] world booted —',
      Math.round(s.worldWidth) + '×' + Math.round(s.worldHeight),
      '| css', s.cssWidth + '×' + s.cssHeight, '| dpr', s.dpr.toFixed(2));
  });
}
