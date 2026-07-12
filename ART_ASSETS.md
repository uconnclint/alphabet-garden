# 🌱 Alphabet Garden — Art Asset Bible

Complete AI-art-generation directions for every visual asset in the game. Work through it top to bottom, or jump straight to the section you want to upgrade first. **Suggested order: Garden Elements → Plants → Sky → Critters → FX → UI** (that's the order players stare at things).

---

## How to use this document

1. **Prepend the Master Style Block below to EVERY prompt in this file.** Every entry's "Prompt" describes only the subject; the style block is what makes all 100+ images look like one game.
2. Add the **Negative Prompt** if your generator supports one.
3. Generate at the size listed for each asset (default **1024×1024, transparent background PNG**). If your generator can't do transparency, generate on a solid `#00FF00` green and we'll key it out later — but true transparency is strongly preferred.
4. Save each image with the **exact filename** shown in the entry, into an `assets/` folder inside the game project. The filenames match the game's internal plant IDs, so wiring them in later is automatic.
5. Check each result against the entry's **Must include** list before accepting it. Reroll anything that fails — consistency is the whole trick.

### 🎨 Master Style Block (prepend to every prompt)

```
Adorable soft-3D claymation style children's game asset, kawaii, bright
saturated candy colors, smooth rounded chunky shapes, soft studio lighting
with gentle top-left key light, subtle ambient occlusion, matte clay
texture with a slight sheen, single object isolated on a fully transparent
background, centered composition, crisp silhouette, professional AAA
mobile game art, delightful and huggable —
```

### 🚫 Negative Prompt (append where supported)

```
photorealistic, realistic photo, scary, creepy, sharp teeth, text, letters,
numbers, words, watermark, signature, background scenery, ground plane,
frame, border, blurry, low quality, extra limbs, extra objects, duplicate
subject, harsh shadows, dark mood
```

### 📐 Technical specs

| Property | Value |
|---|---|
| Format | PNG with alpha transparency |
| Default size | 1024×1024 (exceptions noted per entry) |
| Composition | Subject centered; plants anchored to bottom edge |
| Palette anchor | Grass `#7ec850` · Sky `#6ec6ff` · Soil `#8a5a33` · Sunshine `#ffd23f` · Accent `#ff8a3d` |
| Faces | Two dark round dot eyes + small closed smile — same face on every character, ever |
| Outlines | None — shapes read through color and soft shading, not linework |

**The one rule that matters:** every silly/wacky thing in this game wears the *same simple face* (dot eyes, tiny smile). That face is the franchise. Never let the generator give something eyebrows, teeth, or realistic eyes.

---

## 1 · Garden Elements

### `garden/dirt_plot_empty.png` — Empty Dirt Plot
1024×512.
**Prompt:** A plump oval mound of rich chocolate-brown garden soil seen from a three-quarter top angle, gently domed like a fresh brownie, fine crumbly texture on top, a few tiny pebbles and one small curled leaf resting on the surface, edges softly rounded where the soil meets nothing, warm and inviting, wide oval composition filling the frame.
**Must include:** oval dome shape, crumbly soil texture, chocolate-brown color, no grass around it

### `garden/dirt_plot_seeded.png` — Seeded Dirt Plot
1024×512.
**Prompt:** The same plump oval mound of chocolate-brown garden soil, now with a smaller fresh heap piled in its center and one big tan seed peeking out of the heap, a single tiny lime-green sprout tip curling up from the seed's top, three small sparkles floating just above the heap, wide oval composition filling the frame.
**Must include:** central soil heap, visible tan seed, tiny green sprout tip, sparkles

### `garden/seed.png` — Seed Letter Seed
**Prompt:** One giant huggable garden seed, teardrop shaped and softly plump, warm caramel tan with a lighter cream belly stripe, a tiny curling lime-green sprout with two baby leaves emerging from its top, sitting upright at a slight jaunty tilt, two or three small sparkles around it, subject fills 80% of frame height.
**Must include:** teardrop seed shape, caramel color with cream stripe, sprout with two leaves on top

### `garden/sprout.png` — Baby Sprout (growth stage 1)
**Prompt:** A joyful baby plant sprout: one bright spring-green stem curving slightly, topped with two chubby heart-shaped leaves in two greens — one mint, one emerald — with a tiny third leaf bud unfurling between them, small mound of brown soil hugging the stem base, base touching the bottom of frame, subject fills 75% of frame height.
**Must include:** two chubby leaves in different greens, curved stem, small soil mound at base

### `garden/lock_sign.png` — Locked Plot Sign
**Prompt:** A small wooden garden sign on a single post, the board made of two honey-colored rounded planks with visible friendly wood grain, a chunky golden padlock hanging from the board's top edge, one green vine with two leaves curling up the post, slightly tilted for charm, post base touching the bottom of frame, subject fills 80% of frame height.
**Must include:** rounded wooden board, golden padlock, vine on post, blank board with no text

### `garden/grass_foreground.png` — Grass Meadow Strip
2048×512, tileable left-to-right.
**Prompt:** A lush strip of springtime meadow grass viewed straight on, built from overlapping rounded blade clumps in three greens — bright grass green in front, medium green behind, deep green at the back — sprinkled with five tiny white daisies and three little round clover leaves, soft rolling top edge, seamless left and right edges for tiling, fills the bottom two-thirds of frame.
**Must include:** three green tones layered, rounded blade clumps, tiny daisies, tileable sides

### `garden/hills_backdrop.png` — Distant Hills
2048×768.
**Prompt:** Two gentle overlapping meadow hills in soft pastel greens — the nearer hill spring green, the farther hill pale sage — each dotted with two tiny simplified trees shaped like green lollipops, a winding pale cream path curving between them, everything softly lit and dreamy like a distant storybook landscape, hills rise from the bottom edge of frame.
**Must include:** two hill layers in different greens, lollipop trees, winding path

---

## 2 · Sky & Weather

### `sky/sun.png` — Smiling Sun
**Prompt:** A round glowing sun with a warm gradient from butter yellow center to golden orange rim, twelve chunky rounded triangular rays alternating long and short around it, a serene happy face with two dark oval eyes and a small open smile with rosy peach cheek dots, radiating gentle warmth, subject fills 85% of frame.
**Must include:** rounded alternating rays, gradient yellow-to-orange, dot eyes + smile + cheek dots

### `sky/moon.png` — Sleepy Moon
**Prompt:** A crescent moon like a thick banana slice of pale butter-cream, softly glowing with a faint halo, three small round craters like thumbprints on its surface, a peaceful sleeping face on the inner curve — two closed curved-line eyes and a tiny content smile — one small drowsy star tucked in the crescent's hollow, subject fills 80% of frame.
**Must include:** thick crescent shape, closed sleepy eyes, thumbprint craters, small star companion

### `sky/star.png` — Twinkle Star
512×512.
**Prompt:** A single plump five-pointed star with softly rounded points, glowing warm lemon yellow with a paler cream center, a faint four-point sparkle glint on its upper right tip, cheerful and pillowy like a cookie, subject fills 80% of frame.
**Must include:** rounded star points, lemon yellow glow, sparkle glint

### `sky/cloud_puffy.png` — Puffy Day Cloud
1024×640.
**Prompt:** A dreamy cumulus cloud built from five overlapping round puffs like scoops of vanilla ice cream, brilliant white on top fading to the faintest lavender-blue on the flat underside, one small puff drifting just off its right edge, plump and bouncy, cloud fills 85% of frame width.
**Must include:** five distinct round puffs, white-to-lavender shading, flat bottom, small companion puff

### `sky/cloud_wisp.png` — Small Wispy Cloud
1024×512.
**Prompt:** A small lazy cloud of three soft round puffs stretched slightly horizontal, pure white with a whisper of pale blue beneath, lighter and airier than a storm cloud, like a sleepy sheep drifting sideways, cloud fills 75% of frame width.
**Must include:** three puffs, horizontal stretch, airy lightness

### `sky/rain_cloud.png` — Friendly Rain Cloud
**Prompt:** A chubby storm cloud in soft periwinkle blue-grey with lighter silver puffs on top, a gentle concentrating face low on its belly — two dark dot eyes and a small determined smile — five fat teardrop raindrops in two blues falling in a staggered row beneath it, one tiny yellow lightning bolt shaped like a soft zigzag ribbon tucked at its side, subject fills 85% of frame.
**Must include:** periwinkle body with silver top puffs, dot-eye face, five teardrops below, soft lightning bolt

### `sky/raindrop.png` — Single Raindrop
512×512.
**Prompt:** One plump glossy teardrop of fresh rain, gradient from pale sky blue at the rounded bottom to deeper cornflower blue at the pointed top, a single white crescent highlight on its left shoulder, clean and jewel-like, subject fills 75% of frame height.
**Must include:** teardrop shape point-up, blue gradient, crescent highlight

### `sky/rainbow.png` — Rainbow Arc
1536×1024.
**Prompt:** A wide friendly rainbow arc of six thick rounded candy bands — cherry red, tangerine, lemon, spring green, sky blue, and grape purple — each band plump like rolled clay, both ends of the arc tucked into a small puffy white cloud, faint sparkle dust drifting above the crown, arc fills 90% of frame width.
**Must include:** six distinct thick bands, cloud on each end, rounded candy-like band edges

### `sky/firefly.png` — Night Firefly
512×512.
**Prompt:** A tiny round firefly with a plump charcoal-blue body, two small translucent teal wings lifted mid-flutter, an oversized glowing bulb of a tail in radiant warm yellow with a soft halo of light around it, two dark dot eyes and a tiny smile, hovering at a cheerful tilt, subject fills 70% of frame.
**Must include:** glowing yellow tail with halo, translucent wings, dot eyes + smile

---

## 3 · Garden Critters

### `critters/butterfly_pink.png` — Pink Butterfly
768×768.
**Prompt:** A butterfly seen from above with four rounded petal-shaped wings, upper pair bubblegum pink with white polka dots, lower pair soft rose, a slim charcoal body with two curling antennae ending in tiny balls, wings spread wide mid-flap, subject fills 80% of frame.
**Must include:** four rounded wings, pink with polka dots, ball-tipped antennae

### `critters/butterfly_blue.png` — Blue Butterfly
768×768.
**Prompt:** A butterfly seen from above with four rounded petal-shaped wings, upper pair cornflower blue with a sweep of aqua at the tips, lower pair periwinkle, a slim charcoal body with two curling ball-tipped antennae, wings spread wide mid-flap, subject fills 80% of frame.
**Must include:** four rounded wings, blue-aqua gradient tips, ball-tipped antennae

### `critters/bee.png` — Bumblebee
768×768.
**Prompt:** A chubby round bumblebee with a butter-yellow body wrapped in two thick charcoal stripes, two small translucent silver wings raised in a happy V, tiny dangling stubby legs, two dark dot eyes and a small smile, one little motion swirl behind it suggesting a loop-the-loop flight path, subject fills 75% of frame.
**Must include:** round striped body, translucent V wings, dot eyes + smile, motion swirl

### `critters/ladybug.png` — Ladybug
768×768.
**Prompt:** A dome-shaped ladybug like a shiny cherry-red button, five charcoal polka dots across her back, a charcoal half-circle head with two dark dot eyes and a tiny smile, two short antennae with ball tips, six stubby legs peeking from under the dome, subject fills 70% of frame.
**Must include:** red dome with five dots, dot eyes + smile, ball-tipped antennae

### `critters/bluebird.png` — Bluebird
768×768.
**Prompt:** A round little bluebird in mid-flight, plump robin-egg-blue body with a cream belly, two small wings swept upward mid-flap, a tiny triangle beak in marigold orange, fan of three rounded tail feathers, two dark dot eyes and rosy cheek dots, subject fills 75% of frame.
**Must include:** round blue body with cream belly, upswept wings, orange triangle beak

### `critters/owl.png` — Night Owl
768×768.
**Prompt:** A plump perched owl shaped like a soft egg, cocoa-brown body with a scalloped cream belly like overlapping feather petals, two big round mocha eye discs with dark shiny pupils, tiny marigold beak, two small ear tufts, wings folded neatly at its sides, standing on a short mossy twig, subject fills 80% of frame.
**Must include:** egg silhouette, scalloped cream belly, big round eyes, ear tufts, twig perch

### `critters/bat.png` — Friendly Bat
768×768.
**Prompt:** A tiny friendly bat in mid-flight, round plum-purple body, two big rounded scalloped wings in dusty lavender spread wide, oversized perky ears, two dark dot eyes and a small smile with one tiny harmless fang, feet dangling happily, subject fills 75% of frame.
**Must include:** scalloped rounded wings, big ears, dot eyes + smile, cuddly not spooky

---

## 4 · Effects & Celebration

### `fx/sparkle.png` — Magic Sparkle
512×512.
**Prompt:** A single four-pointed magic sparkle with long soft tapered points, glowing white core blending to warm gold at the tips, one small companion diamond-shaped glint floating at its lower right, luminous against nothing, subject fills 70% of frame.
**Must include:** four tapered points, white-to-gold glow, small companion glint

### `fx/water_splash.png` — Watering Splash
768×768.
**Prompt:** A playful burst of watering-can water: five fat teardrop droplets in two shades of sky blue leaping outward in an arc from a small white splash crown at the bottom center, each droplet with a white crescent highlight, fresh and juicy, arc fills 80% of frame width.
**Must include:** splash crown at base, five arcing teardrops, crescent highlights

### `fx/confetti_burst.png` — Confetti Burst
**Prompt:** An explosion of party confetti frozen mid-air: a dozen rounded rectangles and circles tumbling at every rotation in cherry red, tangerine, lemon, spring green, sky blue, and grape purple, mixed with three small gold stars and two curling ribbon strands, radiating outward from the center, pieces fill the frame edge to edge.
**Must include:** six candy colors, tumbling rotation variety, gold stars, ribbon curls

### `fx/poof_cloud.png` — Dig-Up Poof
768×768.
**Prompt:** A cartoon poof cloud of soft dove-grey and white round puffs bursting outward like a dandelion sneeze, four tiny motion stars and two small soil crumbs flying out of its edges, light and comedic, subject fills 80% of frame.
**Must include:** grey-white puff cluster, motion stars, flying soil crumbs

### `fx/celebration_star.png` — Sticker Star
**Prompt:** A grand rounded five-pointed star like a golden award sticker, glossy gradient from lemon center to deep marigold edges, a scalloped cream sticker border running around its outline, two small sparkle glints on its upper points, proud and collectible, subject fills 85% of frame.
**Must include:** scalloped sticker border, gold gradient, sparkle glints

---

## 5 · UI & Icons

*(Icons read at 52px — keep silhouettes chunky. All 768×768 unless noted.)*

### `ui/logo.png` — Game Logo
1536×1024. **Text warning:** generators mangle words — reroll until "Alphabet Garden" is spelled perfectly, or generate the text-free variant below.
**Prompt:** The words "Alphabet Garden" hand-lettered in plump rounded rainbow letters that look grown from the garden — each letter a different candy color with tiny leaves sprouting from their stems, a small smiling sunflower dotting the final "n", one butterfly resting on the capital A, letters bouncing on a gentle arc, filling 90% of frame width.
**Must include:** rainbow letter colors, sprouting leaves on letters, sunflower and butterfly accents

### `ui/logo_badge.png` — Text-Free Logo Badge (fallback)
**Prompt:** A round garden badge: a smiling sunflower and a giant tan seed with a green sprout side by side inside a scalloped cream circle rimmed with grass green, two tiny butterflies orbiting, three sparkles, warm and iconic like an app icon, subject fills 90% of frame.
**Must include:** sunflower + seed duo, scalloped circle rim, butterflies

### `ui/btn_play.png` — Play Button
1024×512.
**Prompt:** A big pill-shaped game button of glossy tangerine candy with a darker orange bottom edge like thick frosting, a chunky white rounded play triangle on its left half, two small shine streaks on the top edge, irresistible to tap, button fills 85% of frame width.
**Must include:** pill shape, tangerine gradient with dark base edge, white play triangle, shine streaks

### `ui/icon_rain.png` — Rain Button Icon
**Prompt:** A chunky miniature rain cloud in periwinkle with a silver top, three fat sky-blue teardrops falling beneath in a neat row, ultra-simple shapes readable at thumbnail size, subject fills 80% of frame.
**Must include:** simple cloud, exactly three drops, thumbnail readability

### `ui/icon_book.png` — Sticker Book Icon
**Prompt:** A chunky open storybook with honey-brown covers and cream pages curling gently, a big gold star sticker on the left page and a small red heart sticker on the right page, a green bookmark ribbon trailing from the spine, subject fills 80% of frame.
**Must include:** open book, star and heart stickers on pages, bookmark ribbon

### `ui/icon_shovel.png` — Shovel Icon
**Prompt:** A chunky toy garden shovel standing at a jaunty angle, rounded cherry-red scoop with a silver shine crescent, short honey-wood handle with a rounded grip, one small crumb of soil dropping from the scoop tip, subject fills 80% of frame.
**Must include:** red rounded scoop, wooden handle, soil crumb

### `ui/icon_sound.png` — Sound Icon
**Prompt:** A chunky megaphone-shaped speaker in golden yellow with a cream horn opening, three curved candy-pink sound waves ringing out of it in growing sizes, tilted upward cheerfully, subject fills 80% of frame.
**Must include:** yellow speaker horn, three pink sound arcs

### `ui/letter_tile.png` — Blank Letter Tile
**Prompt:** A blank rounded square tile of glossy grape-purple candy with a slightly darker purple bottom edge like thick frosting, a soft white shine crescent across the top-left corner, empty center ready for a letter to be added later, subject fills 85% of frame.
**Must include:** rounded square, glossy candy finish, darker base edge, empty face

### `ui/badge_real.png` — "Real!" Badge
512×512.
**Prompt:** A small round badge of fresh spring green with a scalloped cream rim, a single perky emerald leaf with a visible center vein sitting proudly in the middle, tiny dew drop on the leaf tip, subject fills 85% of frame.
**Must include:** green scalloped badge, single leaf, dew drop

### `ui/badge_silly.png` — "Silly!" Badge
512×512.
**Prompt:** A small round badge of bright sky blue with a scalloped cream rim, a laughing open-mouth smiley face in butter yellow at its center with two squeezed-shut happy eyes, one tiny tear of laughter flying off, subject fills 85% of frame.
**Must include:** blue scalloped badge, laughing yellow face, flying tear

### `ui/badge_wacky.png` — "Wacky!" Badge
512×512.
**Prompt:** A small round badge of vivid orchid purple with a scalloped cream rim, a butter-yellow smiley face at its center with one big eye and one small eye, a lolling tongue, and a tiny spiral swirl floating above its head, subject fills 85% of frame.
**Must include:** purple scalloped badge, mismatched eyes, tongue out, spiral swirl

---

## 6 · The Plant Catalog — all 78 plants

The heart of the game. Every letter grows three ways: **Real!** (an actual plant, no face), **Silly!** (a living-thing mashup, friendly face), **Wacky!** (gloriously impossible, friendly face). All are 1024×1024 transparent PNGs, plant anchored to the bottom edge.

**Catalog-wide rules — apply to every plant below:**
- Real plants: botanical but plump and huggable. **No face.**
- Silly & wacky plants: the standard face (two dark dot eyes, small smile) exactly where the entry says.
- One plant per image, nothing else — no pots unless the entry says so, no ground, no companions.
- Reroll until the "Must include" list passes. A kid should shout the plant's name on sight.

## Letter A

### `plants/a-apple-tree.png` — Apple Tree (A · Real!)
**Prompt:** A cheerful little tree with a stubby chocolate-brown trunk and a fat rounded canopy built from three overlapping cloud-puffs of grass green and lime green foliage. Nestled across the leaves sit five plump glossy candy-apple-red apples, evenly scattered from top to sides, each with a tiny brown stem and one soft white highlight. No face. Full plant standing upright, base of trunk touching the bottom of frame, subject fills 85% of frame height.
**Must include:** brown trunk, rounded green cloud-puff canopy, five red apples, tiny stems on apples

### `plants/a-ant-arch.png` — Antsy Ant Plant (A · Silly!)
**Prompt:** A tall slender grass-green stem with a small leaf pair budding near the top, topped by a stack of three round reddish-brown ant body-segments forming a friendly ant head. The ant face sits at the very top: two dark dot eyes, a small smile, and two thin curved antennae poking up. One or two extra tiny ants march up the stem. Bright cheery greens and warm chestnut brown. Full plant standing upright, base of stem touching the bottom of frame, subject fills 85% of frame height.
**Must include:** tall green stem, three-segment brown ant on top, dot eyes + smile + antennae, marching ants on stem

### `plants/a-airplane-tree.png` — Airplane Tree (A · Wacky!)
**Prompt:** A round bushy green tree on a short tan trunk, its canopy sprouting two chunky toy airplanes instead of fruit. One red airplane with butter-yellow wings tilts up on the left, one sky-blue airplane with yellow tail nests on the right, each with a round nose and a white cockpit dot. Playful motion swoosh lines. The tree has a small dot-eye-and-smile face on the trunk. Full plant standing upright, base of trunk touching the bottom of frame, subject fills 85% of frame height.
**Must include:** round green canopy on tan trunk, one red and one blue toy airplane, yellow wings, dot eyes + smile on trunk

## Letter B

### `plants/b-banana-tree.png` — Banana Tree (B · Real!)
**Prompt:** A tropical banana plant with a sturdy olive-green stalk and three huge arching paddle-shaped leaves fanning out in grass green and lime green from the crown. Below the leaves hangs one fat bunch of five to six curved butter-yellow bananas, tips blushing green, clustered in a hand. Glossy soft lighting. No face. Full plant standing upright, base of stalk touching the bottom of frame, subject fills 85% of frame height.
**Must include:** green banana stalk, three big arching paddle leaves, hanging bunch of yellow bananas, green-tipped banana ends

### `plants/b-butterfly-bush.png` — Butterfly Bush (B · Silly!)
**Prompt:** A plump round bush of three overlapping green foliage puffs on a short green stem. Perched on it rest two chunky butterflies: one with hot-pink upper wings and butter-yellow lower wings, one with purple upper wings and sky-blue lower wings, each with a dark rounded body and thin antennae. The bush wears a gentle dot-eye-and-smile face at its center. Bright candy colors. Full plant standing upright, base of stem touching the bottom of frame, subject fills 85% of frame height.
**Must include:** round green bush, pink-and-yellow butterfly, purple-and-blue butterfly, dot eyes + smile on bush

### `plants/b-burger-bush.png` — Burger Bush (B · Wacky!)
**Prompt:** A round green bush on a short green stem, growing one big giggly cheeseburger front and center: a golden sesame-seed top bun, a green lettuce ruffle, a yellow cheese slice with drippy corners, a brown patty, and a golden bottom bun. The burger itself has two dark dot eyes and a happy smile between the layers. One or two smaller burgers tuck into the leaves. Warm toasty tones against bright green. Full plant standing upright, base of stem touching the bottom of frame, subject fills 85% of frame height.
**Must include:** green bush, stacked cheeseburger with sesame bun, lettuce + cheese + patty layers, dot eyes + smile on burger

## Letter C

### `plants/c-carrot-plant.png` — Carrot Plant (C · Real!)
**Prompt:** A single plump tapered orange carrot planted point-down, its wide top just at soil level and sprouting a lush spray of three feathery frilly green carrot-top fronds fanning upward. The carrot body shows faint horizontal ridge lines and a bright orange-to-deep-orange gradient. No face. Full plant standing upright, tip of carrot touching the bottom of frame, subject fills 85% of frame height.
**Must include:** tapered orange carrot, horizontal ridge lines, three feathery green fronds on top, point-down orientation

### `plants/c-caterpillar-vine.png` — Caterpillar Vine (C · Silly!)
**Prompt:** A curling S-shaped dark-green vine studded with a few small leaves and three round light-green leaf-buds climbing its length. Wrapped along the vine crawls a chubby yellow-green caterpillar made of soft round segments, its head at the lower left with two dark dot eyes, a small smile, and two tiny antennae. Cheerful spring greens. Full plant standing upright, base of vine touching the bottom of frame, subject fills 85% of frame height.
**Must include:** curling green vine, round-segment caterpillar, dot eyes + smile + antennae on head, small leaf-buds on vine

### `plants/c-cupcake-tree.png` — Cupcake Tree (C · Wacky!)
**Prompt:** A round green tree on a short brown trunk, its canopy sprouting two chunky frosted cupcakes instead of fruit. One has a pink swirl of frosting in a pink wrapper, one a purple swirl in a yellow wrapper, both dotted with tiny rainbow sprinkles and a cherry-dot on top. The trunk shows a small dot-eye-and-smile face. Candy-bright pastels. Full plant standing upright, base of trunk touching the bottom of frame, subject fills 85% of frame height.
**Must include:** green canopy on brown trunk, two frosted cupcakes in wrappers, rainbow sprinkles, dot eyes + smile on trunk

## Letter D

### `plants/d-daffodil.png` — Daffodil (D · Real!)
**Prompt:** A single classic daffodil on a straight green stem with one slim blade leaf. The bloom faces forward with six pointed butter-yellow petals radiating around a raised bright-orange trumpet cup at the center, softly shaded to a lighter orange rim. Fresh spring greens and sunny yellows. No face. Full plant standing upright, base of stem touching the bottom of frame, subject fills 85% of frame height.
**Must include:** six yellow petals, raised orange trumpet cup center, green stem, single blade leaf

### `plants/d-duck-bloom.png` — Ducky Daisy (D · Silly!)
**Prompt:** A big fluffy white daisy on a green stem with one leaf, its many rounded white petals fanning around a golden-yellow center. Peeking out of that center is a chubby yellow duckling face with two dark dot eyes, a small orange beak, and a happy expression. Clean whites, sunny yellow, spring green. Full plant standing upright, base of stem touching the bottom of frame, subject fills 85% of frame height.
**Must include:** white daisy petals, yellow center, yellow duckling face with orange beak, dot eyes on duck

### `plants/d-donut-tree.png` — Dancing Donut Tree (D · Wacky!)
**Prompt:** A round green tree on a short brown trunk sprouting two dancing frosted donuts instead of fruit. One tan donut has glossy pink icing with a green hole and scattered blue and yellow sprinkles, one has purple icing, each ring wearing two dark dot eyes and a small smile as if wiggling. Playful tilt and motion lines. Bright bakery colors. Full plant standing upright, base of trunk touching the bottom of frame, subject fills 85% of frame height.
**Must include:** green canopy on brown trunk, two ring donuts with holes, pink and purple icing with sprinkles, dot eyes + smile on donuts

## Letter E

### `plants/e-eggplant.png` — Eggplant (E · Real!)
**Prompt:** A single plump glossy deep-purple eggplant hanging from a short green stem, its bulbous teardrop body catching one soft lavender highlight down the side. A green leafy star-shaped calyx caps the top where it meets the stem, and one broad green leaf sits above. Rich aubergine purple, fresh green. No face. Full plant standing upright, base of stem touching the bottom of frame, subject fills 85% of frame height.
**Must include:** glossy purple teardrop eggplant, green star calyx cap, lavender side highlight, green stem and leaf

### `plants/e-elephant-ear.png` — Elephant Ear Plant (E · Silly!)
**Prompt:** A leafy plant arranged to look like a friendly elephant: two big rounded green leaves flare out as floppy ears on either side of a round green central leaf-face, with a curved dangling green leaf hanging down as a trunk. Two dark dot eyes and a small smile sit on the face-leaf. Soft layered greens from lime to deep green. Full plant standing upright, base of stem touching the bottom of frame, subject fills 85% of frame height.
**Must include:** two big round leaves as ears, central round leaf-face, dangling leaf-trunk, dot eyes + smile

### `plants/e-escalator-plant.png` — Escalator Plant (E · Wacky!)
**Prompt:** A goofy green plant with a thick central stem and small side leaves, its front growing four butter-yellow rectangular step-slabs stacked in a rising diagonal staircase from lower left to upper right, joined by a slim blue handrail line. A round red ladybug bug with dot eyes and a smile rides near the top step. Cheery yellows, greens, and a pop of red. Full plant standing upright, base of stem touching the bottom of frame, subject fills 85% of frame height.
**Must include:** green stem plant, four yellow rising steps, blue handrail line, red bug with dot eyes + smile on a step

## Letter F

### `plants/f-fern.png` — Fern (F · Real!)
**Prompt:** A lush fern with three tall arching fronds rising from the base, each central rib lined with rows of small oval leaflets tapering to the tip, layered in grass green and lighter lime green. Graceful symmetric fountain shape, feathery and soft. No face. Full plant standing upright, base of fronds touching the bottom of frame, subject fills 85% of frame height.
**Must include:** three arching fronds, rows of small oval leaflets along each rib, fountain silhouette, layered greens

### `plants/f-firefly-flower.png` — Firefly Flower (F · Silly!)
**Prompt:** A cheerful flower on a green stem with one leaf, its four to five rounded purple petals framing a glowing golden-yellow center. Hovering beside the bloom are two plump fireflies with yellow-green bodies, tiny dot eyes and smiles, each with a soft glowing pale-yellow halo at its tail. Purple, gold, and warm glow against fresh green. Full plant standing upright, base of stem touching the bottom of frame, subject fills 85% of frame height.
**Must include:** purple-petal flower, golden glowing center, two fireflies with glowing tails, dot eyes + smiles on fireflies

### `plants/f-firetruck-flower.png` — Firetruck Flower (F · Wacky!)
**Prompt:** A sunny flower on a green stem with one leaf, its butter-yellow petals ringing the center where a chunky little red firetruck sits like a blossom. The toy truck has a red cab, a pale-blue windshield, a small ladder on top, two dark wheels, and a happy dot-eye-and-smile face on its front. Bright fire-engine red, yellow petals, spring green. Full plant standing upright, base of stem touching the bottom of frame, subject fills 85% of frame height.
**Must include:** yellow-petal flower, red firetruck at center, blue windshield + ladder + wheels, dot eyes + smile on truck

# Alphabet Garden — Art Prompts (Letters G–L)

## Letter G

### `plants/g-grape-vine.png` — Grape Vine (G · Real!)
**Prompt:** A short chunky brown wooden trunk splitting into two curling green tendril arms that spiral at the tips. Hanging from them, one plump pyramid-shaped cluster of round grapes in glossy deep purple-violet fading to lighter lilac highlights, roughly twelve grapes stacked tight. Two broad emerald-green maple-shaped leaves flank the bunch. A few pale frosty shine spots dot the front grapes. Full plant standing upright, base of trunk or stem touching the bottom of frame, subject fills 85% of frame height.
**Must include:** pyramid bunch of purple round grapes, two curling green tendrils, broad emerald grape leaves, glossy grape highlights

### `plants/g-giraffe-grass.png` — Giraffe Grass (G · Silly!)
**Prompt:** A single super-tall blade of grass shaped like a slender giraffe neck, buttery golden-yellow on the left, deeper amber-orange on the right. Scattered irregular brown patch spots run up the stalk like giraffe markings. Two tiny rounded ossicone bumps sit at the very top. Two small bright grass-green leaf tufts sprout low near the base. The face sits near the top of the stalk: two dark dot eyes and a small friendly smile. Full plant standing upright, base of trunk or stem touching the bottom of frame, subject fills 85% of frame height.
**Must include:** tall golden-yellow stalk, brown giraffe patch spots, two ossicone bumps on top, face near top, green leaf tufts at base

### `plants/g-gumball-tree.png` — Gumball Goo Tree (G · Wacky!)
**Prompt:** A stubby brown trunk topped by a round lime-green foliage ball completely studded with glossy round gumballs in candy colors: hot pink, sky blue, sunny yellow, purple, orange, mint green, about seven visible, each with a tiny white shine dot. The foliage reads as a bubbly gumball-machine dome. The face sits on the trunk just below the foliage: two dark dot eyes and a small smile. Full plant standing upright, base of trunk or stem touching the bottom of frame, subject fills 85% of frame height.
**Must include:** lime-green round foliage, multicolored glossy gumballs studding it, white shine dots on gumballs, face on trunk

## Letter H

### `plants/h-hibiscus.png` — Hibiscus Flower (H · Real!)
**Prompt:** A slender grass-green stem holding one big open five-petal hibiscus bloom facing forward. Broad ruffled petals blend from butter-yellow centers to coral-pink then deep crimson-red edges. A long yellow stamen tube juts straight out from the center with a fuzzy golden-orange pollen tip, backed by a small crimson throat. Two pointed green leaves sit midway down the stem. Full plant standing upright, base of trunk or stem touching the bottom of frame, subject fills 85% of frame height.
**Must include:** five ruffled petals yellow-to-red gradient, long protruding yellow stamen tube, crimson center throat, two green stem leaves

### `plants/h-hedgehog-herb.png` — Hedgehog Herb (H · Silly!)
**Prompt:** A rounded caramel-brown herb bush shaped like a curled hedgehog, its back bristling with a fan of sharp olive-green pointed leaf-spines. A small pointed snout pokes out to the left with a tiny dark nose bump. The lower body is a soft tan-caramel dome. The face sits on the snout-side front: two dark dot eyes and a small friendly smile. Full plant standing upright, base of trunk or stem touching the bottom of frame, subject fills 85% of frame height.
**Must include:** caramel-brown rounded body, fan of olive-green pointed leaf spines, pointed snout with nose, face on front

### `plants/h-hotdog-hedge.png` — Hopping Hotdog Hedge (H · Wacky!)
**Prompt:** A long low leafy-green hedge box with a brighter lime top, sprouting two upright hotdogs like topiary: each a golden-tan bun cradling a red sausage, drizzled with a wavy butter-yellow mustard squiggle. The hotdogs stand side by side above the hedge. The face sits centered on the front of the green hedge: two dark dot eyes and a wide happy smile. Full plant standing upright, base of trunk or stem touching the bottom of frame, subject fills 85% of frame height.
**Must include:** leafy-green hedge base, two upright bun-and-sausage hotdogs, yellow mustard squiggles, face on hedge front

## Letter I

### `plants/i-iris.png` — Iris Flower (I · Real!)
**Prompt:** A tall slim green stem topped by one classic iris bloom: three upright inner petals and three drooping outer falls in rich violet-purple gradient, darker at the base, lighter lavender at the edges. A small butter-yellow beard streak sits on the front fall. One long slender sword-shaped green leaf rises beside the stem. Full plant standing upright, base of trunk or stem touching the bottom of frame, subject fills 85% of frame height.
**Must include:** three upright plus three drooping violet petals, yellow beard streak on front fall, tall sword-shaped green leaf, purple gradient petals

### `plants/i-inchworm-ivy.png` — Inchworm Ivy (I · Silly!)
**Prompt:** A zig-zagging green ivy vine climbing upward in inchworm arch loops, dotted with round heart-shaped ivy leaves in two greens. At the top tip the vine becomes a plump bright-green inchworm head with two tiny antennae. The face sits on that top worm head: two dark dot eyes and a small friendly smile. Full plant standing upright, base of trunk or stem touching the bottom of frame, subject fills 85% of frame height.
**Must include:** zig-zag arching green vine, round ivy leaves along it, inchworm head at top with antennae, face on worm head

### `plants/i-icecream-iris.png` — Ice Cream Iris (I · Wacky!)
**Prompt:** A green stem topped by a golden waffle cone with cross-hatch grid texture, holding three stacked round ice-cream scoops: strawberry pink, mint green, peach-orange, crowned by a little cherry-red dot. Two small green leaves sit on the stem below the cone. The face sits on the bottom scoop: two dark dot eyes and a small smile. Full plant standing upright, base of trunk or stem touching the bottom of frame, subject fills 85% of frame height.
**Must include:** golden waffle cone with grid texture, three stacked scoops pink-mint-peach, red cherry on top, face on bottom scoop

## Letter J

### `plants/j-jasmine.png` — Jasmine Flowers (J · Real!)
**Prompt:** A slender arching green stem carrying three dainty five-petal jasmine blossoms in creamy soft-white, each with a tiny sunny-yellow center dot. The little star-shaped flowers cluster near the top and sides. A pair of small pointed green leaves sits along the stem. Delicate, airy, and clean. Full plant standing upright, base of trunk or stem touching the bottom of frame, subject fills 85% of frame height.
**Must include:** three white five-petal star blossoms, yellow center dots, arching green stem, small pointed leaves

### `plants/j-jaguar-jade.png` — Jaguar Jade Plant (J · Silly!)
**Prompt:** A short brown succulent trunk topped with five plump teardrop jade leaves fanning out, colored warm golden-amber like a jaguar coat and dappled with dark brown rosette spots. The thick rounded leaves have a glossy sheen. The face sits on the center top leaf: two dark dot eyes, a small smile, and two tiny whisker ticks at the cheeks. Full plant standing upright, base of trunk or stem touching the bottom of frame, subject fills 85% of frame height.
**Must include:** five plump amber jade leaves, dark brown jaguar rosette spots, short brown trunk, face with tiny whiskers on center leaf

### `plants/j-jellybean-jungle.png` — Jiggly Jellybean Jungle (J · Wacky!)
**Prompt:** A stubby purple trunk topped by a round grass-green foliage ball studded with glossy oval jellybeans in candy colors: pink, sky-blue, yellow, orange, purple, mint, about six visible, each slightly tilted and shiny. The bushy dome reads jiggly and jungly. The face sits on the trunk just below the foliage: two dark dot eyes and a wide happy smile. Full plant standing upright, base of trunk or stem touching the bottom of frame, subject fills 85% of frame height.
**Must include:** grass-green foliage ball, multicolored oval glossy jellybeans, purple trunk, face on trunk

## Letter K

### `plants/k-kale.png` — Curly Kale (K · Real!)
**Prompt:** A single upright bunch of curly kale: a pale green-white lower stalk fanning into big ruffled frilly leaves with tightly crinkled wavy edges, deep forest-green at the tips blending to bright grass-green nearer the center. Fine lighter veins trace through the leaves. Lush, crunchy, dense, and leafy. Full plant standing upright, base of trunk or stem touching the bottom of frame, subject fills 85% of frame height.
**Must include:** frilly crinkled curly leaf edges, dark-to-bright green gradient, pale stalk at base, light leaf veins

### `plants/k-kangaroo-kelp.png` — Kangaroo Kelp (K · Silly!)
**Prompt:** A tall two-tone green kelp frond curving upward like a kangaroo body, brighter on one side, darker on the other, with a few smaller leaf-fronds branching like arms, ears, and a thick tail. A rounded pouch dip sits on the front belly. Two little pointed ear-leaves rise at the top. The face sits near the top: two dark dot eyes and a small friendly smile. Full plant standing upright, base of trunk or stem touching the bottom of frame, subject fills 85% of frame height.
**Must include:** tall curving two-tone green kelp frond, pouch on front belly, two pointed ear-leaves on top, face near top

### `plants/k-ketchup-cactus.png` — Kooky Ketchup Cactus (K · Wacky!)
**Prompt:** A tall rounded cactus shaped like a squeeze bottle in bright tomato-red, with a smaller red cap segment and a yellow nozzle lid on top, plus two red curved cactus arms. A cream-white label panel sits on the belly with faint red lines (no letters). A little squirt of red ketchup arcs from the nozzle tip. The face sits on the label area: two dark dot eyes and a wide friendly smile. Full plant standing upright, base of trunk or stem touching the bottom of frame, subject fills 85% of frame height.
**Must include:** tomato-red squeeze-bottle cactus, yellow nozzle lid, red ketchup squirt from top, cream label panel with face

## Letter L

### `plants/l-lavender.png` — Lavender (L · Real!)
**Prompt:** A small tuft of three tall slender green stems, each topped with a spike of clustered tiny round blossoms in soft purple-violet with lighter lilac highlight buds. The three flower spikes rise close together in a gentle fan. Fine narrow silvery-green leaves sit low on the stems. Calm, soft, and delicate. Full plant standing upright, base of trunk or stem touching the bottom of frame, subject fills 85% of frame height.
**Must include:** three tall thin stems, purple clustered blossom spikes, lighter lilac highlight buds, narrow green leaves at base

### `plants/l-ladybug-lettuce.png` — Ladybug Lettuce (L · Silly!)
**Prompt:** A low rosette of ruffled bright-green lettuce leaves at the base, out of which rises a round red ladybug body split down the middle by a black line, dotted with four black spots. A black domed head sits on top with two tiny white eye shines, two little antennae with dot tips. The face reads on the black head: two white-glint dot eyes and a small smile. Full plant standing upright, base of trunk or stem touching the bottom of frame, subject fills 85% of frame height.
**Must include:** ruffled green lettuce rosette at base, round red ladybug body with black spots and center line, black head with antennae, face on head

### `plants/l-lollipop-lily.png` — Loopy Lollipop Lily (L · Wacky!)
**Prompt:** A green lily stem topped by one big round lollipop disc, glossy pink-and-white swirl spiraling from the center outward. Two pointed green leaves sit midway on the stem. Two soft blush cheek blobs sit on the candy face. The face sits on the lollipop disc: two dark dot eyes and a small friendly smile. Full plant standing upright, base of trunk or stem touching the bottom of frame, subject fills 85% of frame height.
**Must include:** round lollipop disc with pink-white spiral swirl, green stem with two leaves, blush cheek blobs, face on disc

## Letter M

### `plants/m-maple-tree.png` — Maple Tree (M · Real!)
**Prompt:** A chunky rounded maple tree with a stout warm-brown trunk and two short branches. A single fluffy dome canopy blazes in autumn colors: a fiery blend of golden amber, tangerine orange, and deep burnt-red, with a few crisp five-point maple leaf shapes tucked into the surface. Scatter three small leaf clumps in butter yellow and coral for depth. No face. full plant standing upright, base of trunk touching the bottom of frame, subject fills 85% of frame height.
**Must include:** fiery amber-orange-red canopy, visible five-point maple leaf shapes, warm-brown trunk with two branches, no face

### `plants/m-monkey-marigold.png` — Monkey Marigold (M · Silly!)
**Prompt:** A cheerful marigold flower whose bloom is a smiling monkey face. Ruffled petal ring in bright marigold orange and golden yellow frames a tan muzzle with two rounded chocolate-brown monkey ears poking out each side. A short grass-green stem with one small leaf holds it up. The face sits centered in the bloom: two dark dot eyes, rosy cheeks, and a small friendly smile. full plant standing upright, base of stem touching the bottom of frame, subject fills 85% of frame height.
**Must include:** orange-and-gold ruffled petal ring, two brown monkey ears, tan muzzle, dot eyes and small smile, green stem with leaf

### `plants/m-marshmallow-tree.png` — Marshmallow Tree (M · Wacky!)
**Prompt:** A silly little tree whose canopy is a cluster of five puffy pillow-soft marshmallows, each a squishy rounded cube in creamy off-white with the faintest toasted-pink edges. They stack into a soft mound atop a short tan-brown trunk. The front-center marshmallow wears the face: two dark dot eyes, two tiny pink cheek blushes, and a small happy smile. full plant standing upright, base of trunk touching the bottom of frame, subject fills 85% of frame height.
**Must include:** five puffy cube marshmallows in cream white, soft toasted-pink edges, short tan trunk, dot eyes with pink cheeks and smile

## Letter N

### `plants/n-norway-spruce.png` — Norway Spruce (N · Real!)
**Prompt:** A classic tall triangular evergreen spruce built from three stacked cone-shaped tiers of deep forest green, widest at the base and pointed at the top. Short reddish-brown trunk peeks out at the bottom. Dust the needled tiers with a few pale mint-green highlight dots like fresh new growth. Crisp, tidy, upright silhouette. No face. full plant standing upright, base of trunk touching the bottom of frame, subject fills 85% of frame height.
**Must include:** three stacked triangular tiers, deep forest-green needles, mint-green highlight dots, short brown trunk, no face

### `plants/n-narwhal-nettle.png` — Narwhal Nettle (N · Silly!)
**Prompt:** A round plump plant bloom shaped like a happy narwhal head in ocean sky-blue with a paler powder-blue belly patch. A single long spiraled ivory horn twists straight up from the top. A slim sea-green stem with two little leaves holds it. The face is centered on the blue body: two dark dot eyes with tiny white glints and a small smiling mouth. full plant standing upright, base of stem touching the bottom of frame, subject fills 85% of frame height.
**Must include:** round sky-blue narwhal body with powder-blue belly, single spiraled ivory horn pointing up, green stem with leaves, dot eyes and small smile

### `plants/n-noodle-nutbush.png` — Noodle Nutbush (N · Wacky!)
**Prompt:** A round golden bush whose foliage is a tangle of wiggly wavy noodles in warm butter-yellow and deeper amber, looping and curling all over the dome. One noodle strand dangles loose off the lower left like it's being slurped. A short brown trunk anchors it. The face sits low-center among the noodles: two dark dot eyes and a small orange smiling mouth. full plant standing upright, base of trunk touching the bottom of frame, subject fills 85% of frame height.
**Must include:** dome of wiggly wavy noodles in butter-yellow and amber, one dangling loose noodle, short brown trunk, dot eyes and small smile

## Letter O

### `plants/o-orange-tree.png` — Orange Tree (O · Real!)
**Prompt:** A rounded leafy tree with a stout warm-brown trunk and a lush spherical canopy in rich green with lighter grass-green highlight clumps. Nestled across the foliage sit five plump ripe oranges in bright orange and tangerine, each with a tiny dark stipple dimple at the top. Cheerful and full. No face. full plant standing upright, base of trunk touching the bottom of frame, subject fills 85% of frame height.
**Must include:** rounded green canopy with lighter highlights, five bright-orange fruits with dimple tops, stout brown trunk, no face

### `plants/o-owl-orchid.png` — Owl Orchid (O · Silly!)
**Prompt:** A single big orchid bloom shaped like a wise owl face in soft lilac-purple with two little pointed feather-tuft petals at the top corners. Two large round white eye-discs each hold a dark pupil, and a small orange triangular beak-petal sits between them. A slim sea-green stem with one leaf holds it up. Face reads owl-like: dot pupils and a gentle expression. full plant standing upright, base of stem touching the bottom of frame, subject fills 85% of frame height.
**Must include:** lilac-purple owl bloom, two big white eye-discs with dark pupils, orange triangular beak, two feather-tuft top petals, green stem with leaf

### `plants/o-octopus-oakleaf.png` — Octopus Oakleaf (O · Wacky!)
**Prompt:** A goofy plant whose bloom is a round coral-pink octopus head with a lighter blush-pink dome highlight, sitting atop a grass-green stem. Eight curling tentacle-arms in matching coral-pink wave outward and down around the stem, each tapering to a soft point. The face is centered on the round head: two dark dot eyes with white glints and a small smiling mouth. full plant standing upright, base of stem touching the bottom of frame, subject fills 85% of frame height.
**Must include:** round coral-pink octopus head, eight curling coral tentacle-arms, green stem, dot eyes with glints and small smile

## Letter P

### `plants/p-palm-tree.png` — Palm Tree (P · Real!)
**Prompt:** A tall gently curving palm with a slim tan-brown ringed trunk that leans slightly. At the crown, five long arching frond leaves in vivid tropical green fan out and droop gracefully like a starburst. A couple of small brown coconuts cluster where the fronds meet the trunk. Breezy beach feel. No face. full plant standing upright, base of trunk touching the bottom of frame, subject fills 85% of frame height.
**Must include:** slim curving ringed trunk, five arching green fronds fanning out, small brown coconuts at the crown, no face

### `plants/p-panda-pansy.png` — Panda Pansy (P · Silly!)
**Prompt:** A round pansy flower shaped like a baby panda face: a fluffy white bloom with two black rounded ears at the top corners, two black oval eye-patches each holding a white-dotted eye, and a little black nose. A grass-green stem with two small leaves holds it. Face centered and cuddly: dot eyes inside the black patches, tiny nose, and a small soft smile. full plant standing upright, base of stem touching the bottom of frame, subject fills 85% of frame height.
**Must include:** white panda bloom, two black ears, two black eye-patches with dotted eyes, small black nose, green stem with leaves, small smile

### `plants/p-pizza-palm.png` — Pizza Palm (P · Wacky!)
**Prompt:** A wacky palm whose crown grows a fan of five triangular pizza slices instead of fronds, points meeting at the center and spreading outward. Each slice has a golden-yellow cheesy surface, a tan crust edge, and two or three bright pepperoni-red dots. A short tan-brown trunk holds them up. The face sits at the center where the slices meet: two dark dot eyes and a small smiling mouth. full plant standing upright, base of trunk touching the bottom of frame, subject fills 85% of frame height.
**Must include:** fan of five triangular pizza slices, golden cheese with crust edges, red pepperoni dots, short brown trunk, dot eyes and small smile

## Letter Q

### `plants/q-quaking-aspen.png` — Quaking Aspen (Q · Real!)
**Prompt:** A slender upright aspen with a smooth pale chalk-white trunk marked by a few short dark horizontal bark scars. Its rounded canopy is a soft cloud of lively lime and yellow-green rounded leaf clumps, dotted with a few bright golden-yellow leaves that look ready to flutter. Light and airy. No face. full plant standing upright, base of trunk touching the bottom of frame, subject fills 85% of frame height.
**Must include:** pale white trunk with dark bark scars, rounded lime-and-yellow-green canopy, scattered golden leaf dots, no face

### `plants/q-quail-quillplant.png` — Quail Quillplant (Q · Silly!)
**Prompt:** A plump plant bloom shaped like a chubby quail bird in warm sandy-tan and soft brown, tilted like it's mid-bob. A single curved teardrop head-plume curls forward off the top, and a tiny orange beak points out to one side. A grass-green stem with a little leaf holds it. Face on the head: one dark dot eye with a white glint and a cheerful look. full plant standing upright, base of stem touching the bottom of frame, subject fills 85% of frame height.
**Must include:** plump sandy-tan quail body, forward-curling teardrop head-plume, small orange beak, green stem with leaf, dot eye with glint

### `plants/q-quackers-duckbloom.png` — Quackers Duckbloom (Q · Wacky!)
**Prompt:** A goofy flower whose five rounded petals in bright buttercup-yellow ring a golden duck face at the center. A wide orange duck bill sits low on the face and two dark dot eyes with white glints sit above it, giving a happy quacking look. A sea-green stem with one leaf holds it upright. full plant standing upright, base of stem touching the bottom of frame, subject fills 85% of frame height.
**Must include:** five buttercup-yellow petals, golden duck face center, wide orange duck bill, dot eyes with glints, green stem with leaf

## Letter R

### `plants/r-red-rose.png` — Red Rose (R · Real!)
**Prompt:** A single classic rose bloom, a tight spiral of deep crimson and bright scarlet-red layered petals forming a rounded velvety head. A straight forest-green stem holds it, with two pointed green leaves and a couple of tiny thorns along the stem. Elegant and simple. No face. full plant standing upright, base of stem touching the bottom of frame, subject fills 85% of frame height.
**Must include:** spiral of crimson-and-scarlet petals, rounded rose head, green stem with two pointed leaves, tiny thorns, no face

### `plants/r-rabbit-radish.png` — Rabbit Radish (R · Silly!)
**Prompt:** A radish shaped like a hoppy rabbit: a plump round root body in bright cherry-red fading to a creamy-white top, with two tall floppy ears standing up, white outside and soft pink inside. A little tuft of green radish leaves sprouts between the ears. Face on the red body: two dark dot eyes with glints, a tiny pink nose, and a small smile. full plant standing upright, base of root touching the bottom of frame, subject fills 85% of frame height.
**Must include:** cherry-red radish body with creamy-white top, two floppy pink-lined ears, green leaf tuft between ears, dot eyes, pink nose and small smile

### `plants/r-robot-rosebush.png` — Robot Rosebush (R · Wacky!)
**Prompt:** A boxy little robot bush with a brushed metallic silver-grey body and a rectangular head. Two glowing blue square eyes sit on the head above a small dark grille mouth, and a springy antenna with a glowing yellow bulb tops it. Two jointed metal arms end in shiny cherry-red metal roses with darker centers. A segmented grey stem-body base. Face reads friendly and robotic. full plant standing upright, base touching the bottom of frame, subject fills 85% of frame height.
**Must include:** metallic silver-grey robot body and head, two glowing blue square eyes, yellow-bulb antenna, two shiny red metal roses on arms, grille mouth

# Alphabet Garden — Art Prompts (Letters S–Z)

## Letter S

### `plants/s-sunflower.png` — Sunflower (S · Real!)
**Prompt:** A single tall sunflower on a thick grass-green stalk with two pointed leaves fanning left and right. Broad golden butter-yellow petals radiate in a full ring around a domed chocolate-brown seed center flecked with warm caramel. Stem stands straight, leaves slightly upturned, petals plump and rounded like soft clay. No face. Full plant standing upright, base of trunk or stem touching the bottom of frame, subject fills 85% of frame height.
**Must include:** golden butter-yellow petal ring, chocolate-brown domed center, thick green stalk, two green leaves

### `plants/s-snail-snapdragon.png` — Snaily Snapdragon (S · Silly!)
**Prompt:** A slim green snapdragon stem topped with a fat coral-orange bloom made of concentric rings (outer coral, salmon-pink middle, deep orange core). A friendly cartoon snail rides on a low mint-green leaf: rounded coral spiral shell, two stubby eyestalks with dark dot eyes tipped up top, small smiling mouth on its face at the front of the body. Face sits on the snail's head, lower right. Full plant standing upright, base of trunk or stem touching the bottom of frame, subject fills 85% of frame height.
**Must include:** coral concentric snapdragon bloom, spiral-shell snail with eyestalks, dot eyes + smile on snail, mint-green leaf

### `plants/s-sock-sprout.png` — Stinky Sock Sprout (S · Wacky!)
**Prompt:** A green sprout stem growing two chunky tube socks instead of leaves: one candy-red sock and one sky-blue sock, each with a white cuff band at the opening, drooping and wiggly. The red left sock wears a tiny friendly face near its cuff (two dark dot eyes, small smile). A faint wavy stink squiggle curls off the top. Bright saturated candy tones. Full plant standing upright, base of trunk or stem touching the bottom of frame, subject fills 85% of frame height.
**Must include:** one red sock + one blue sock, white cuff bands, dot eyes + smile on red sock, wavy stink squiggle

## Letter T

### `plants/t-tomato.png` — Tomato (T · Real!)
**Prompt:** A plump glossy tomato on an upright green stem with two pointed green leaves fanning out. The round fruit is bright candy-red with a soft white highlight on its upper left and a five-point green star cap and short stub on top. Smooth rounded clay form, cheerful and juicy. No face. Full plant standing upright, base of trunk or stem touching the bottom of frame, subject fills 85% of frame height.
**Must include:** round candy-red tomato, green five-point star cap, white highlight, two green leaves

### `plants/t-turtle-tulip.png` — Turtle Tulip (T · Silly!)
**Prompt:** A green tulip stem topped with a single cupped tulip bloom in coral-orange and salmon petals. Below it, a friendly cartoon turtle body: a domed lime-green shell with darker segment lines, four stubby legs, and a small green head poking out to the left wearing two dark dot eyes and a gentle smile. Rounded, slow, and sweet. Face on the turtle head, left side. Full plant standing upright, base of trunk or stem touching the bottom of frame, subject fills 85% of frame height.
**Must include:** coral tulip bloom, domed lime-green turtle shell with segment lines, turtle head with dot eyes + smile, green stem

### `plants/t-taco-tree.png` — Tumbly Taco Tree (T · Wacky!)
**Prompt:** A short chunky brown tree trunk with two little stub branches, crowned by one giant folded taco instead of leaves. The taco shell is golden-yellow with a crisp curved rim; inside peek layers of green lettuce and red tomato filling. A friendly face sits on the taco shell front (two dark dot eyes, small curved smile). Warm, goofy, appetizing. Full plant standing upright, base of trunk or stem touching the bottom of frame, subject fills 85% of frame height.
**Must include:** golden folded taco shell, green lettuce + red filling inside, dot eyes + smile on shell, brown trunk with stub branches

## Letter U

### `plants/u-umbrella-plant.png` — Umbrella Plant (U · Real!)
**Prompt:** A leafy umbrella plant in a warm terracotta-clay pot. Slender green stalks rise and fan into clusters of oval green leaves that radiate outward like tiny umbrella spokes, layered in medium and light greens. Upright, tidy, and lush. No face. Full plant standing upright, base of trunk or stem touching the bottom of frame, subject fills 85% of frame height.
**Must include:** terracotta pot, radiating umbrella-spoke leaf clusters, layered green tones, upright green stalks

### `plants/u-unicorn-flower.png` — Unicorn Bloom (U · Silly!)
**Prompt:** A green flower stem with one small leaf, topped by a big round blush-pink blossom face. A golden spiral unicorn horn points straight up from the top of the bloom. The flower has two dark dot eyes, two rosy pink cheek circles, and a small happy smile, with little lavender swirl ears curling out each side. Magical and sweet. Face centered on the pink bloom. Full plant standing upright, base of trunk or stem touching the bottom of frame, subject fills 85% of frame height.
**Must include:** golden spiral unicorn horn on top, round blush-pink bloom, dot eyes + rosy cheeks + smile, lavender swirl ears

### `plants/u-ufo-tree.png` — UFO Tree (U · Wacky!)
**Prompt:** A brown-trunked round green space tree with three friendly flying saucers hovering around it. The top saucer is purple with a clear blue glass dome holding a smiling green alien (dot eyes, small smile) and a rim of glowing yellow, orange, and green lights; two smaller saucers in pink and cyan orbit lower left and right, each rimmed with tiny colored lights. Scattered star sparkles. Cosmic and cheerful. Full plant standing upright, base of trunk or stem touching the bottom of frame, subject fills 85% of frame height.
**Must include:** three flying saucers with glowing rim lights, blue-dome saucer with smiling green alien, round green tree + brown trunk, star sparkles

## Letter V

### `plants/v-violet.png` — Violet (V · Real!)
**Prompt:** A low clustered violet plant with slender green stems and two leaves. Several small five-petal blossoms in rich purple and lavender bloom together, each with a tiny sunny-yellow center dot. A little side cluster of pale lilac buds sits near the base. Delicate, tidy, softly rounded. No face. Full plant standing upright, base of trunk or stem touching the bottom of frame, subject fills 85% of frame height.
**Must include:** cluster of purple + lavender five-petal blossoms, yellow center dots, green stems + leaves, pale lilac buds

### `plants/v-vole-vine.png` — Vole Violet Vine (V · Silly!)
**Prompt:** A curling green vine stem with two small leaves and a couple of little purple violet flowers with yellow centers along it. Peeking out from the flowers, a curious round grey vole: soft grey head and body, two big pale-grey ears with pink inner circles, tiny pink nose, two dark dot eyes and a small smile. Cozy and inquisitive. Face on the vole, center. Full plant standing upright, base of trunk or stem touching the bottom of frame, subject fills 85% of frame height.
**Must include:** curly green vine with purple violets, round grey vole with big pink-lined ears, pink nose, dot eyes + smile

### `plants/v-volcano-tree.png` — Vroomy Volcano Tree (V · Wacky!)
**Prompt:** A cone-shaped brown volcano trunk with lighter tan striping, wide at the base. From its crater erupts a fizzy fountain of bright soda-pop bubbles in orange, amber, red, and yellow instead of lava, topping out in cheerful spray. A friendly face sits on the cone's lower slope (two dark dot eyes, small smile). Playful, bubbly, warm. Full plant standing upright, base of trunk or stem touching the bottom of frame, subject fills 85% of frame height.
**Must include:** brown cone volcano trunk, fizzy orange/red/yellow soda bubbles erupting from crater, dot eyes + smile on cone, tan striping

## Letter W

### `plants/w-watermelon.png` — Watermelon (W · Real!)
**Prompt:** A round watermelon resting on a trailing green ground vine with one small leaf. The rind is deep green with lighter green wavy stripes and a tiny leaf sprig on top. Beside it sits a cut wedge showing bright red juicy flesh, a pale rind edge, and a few dark seeds. Glossy, plump, summery. No face. Full plant standing upright, base of trunk or stem touching the bottom of frame, subject fills 85% of frame height.
**Must include:** round striped-green watermelon, red-flesh cut wedge with seeds, trailing green vine, leaf sprig on top

### `plants/w-whale-wisteria.png` — Whaley Wisteria (W · Silly!)
**Prompt:** A green stem with a small leaf and a short hanging cluster of purple wisteria beads (light to deep purple). Beside it, a chubby sky-blue whale with a pale-blue belly, a small curved tail fin, one dark dot eye and a wide friendly smile. A little water spout arcs up from its blowhole. Round, jolly, aquatic. Face on the whale, left of center. Full plant standing upright, base of trunk or stem touching the bottom of frame, subject fills 85% of frame height.
**Must include:** hanging purple wisteria bead cluster, chubby blue whale with pale belly, water spout from blowhole, dot eye + smile

### `plants/w-waffle-willow.png` — Wiggly Waffle Willow (W · Wacky!)
**Prompt:** A curvy brown willow trunk with one drooping branch, hung with two golden-brown waffle squares showing deep criss-cross grid pockets. A glossy amber syrup drizzle drips over the top edges and a pat of butter-yellow butter sits on the larger waffle. A friendly face on the big waffle (two dark dot eyes, small smile). Warm, sweet, breakfast-y. Full plant standing upright, base of trunk or stem touching the bottom of frame, subject fills 85% of frame height.
**Must include:** two golden waffle squares with grid pockets, amber syrup drizzle, yellow butter pat, dot eyes + smile on waffle

## Letter X

### `plants/x-xanthosoma.png` — Xanthosoma (X · Real!)
**Prompt:** A tropical xanthosoma with three slender green stalks each rising to a large arrowhead-shaped leaf. The biggest central leaf is medium green with pale vein lines branching from the midrib; two side leaves are lighter green and slightly smaller. Broad, glossy, jungle-lush. No face. Full plant standing upright, base of trunk or stem touching the bottom of frame, subject fills 85% of frame height.
**Must include:** large arrowhead-shaped leaves, three green stalks, pale branching vein lines, layered green tones

### `plants/x-fox-xerophyte.png` — Foxy Xerophyte (X · Silly!)
**Prompt:** A tall orange cactus-body shaped like a sitting fox: an upright rounded torso in warm orange with two small side-arm pads, a round orange head with two pointed ears (dark brown tips), a cream-white muzzle and chest, a dark-brown nose, and two dark dot eyes with a small smile. Clever and desert-dry. Face centered on the fox head. Full plant standing upright, base of trunk or stem touching the bottom of frame, subject fills 85% of frame height.
**Must include:** orange fox-shaped cactus body, pointed ears with brown tips, cream muzzle + chest, dot eyes + smile + brown nose

### `plants/x-xylophone-tree.png` — Xylophone Xoo Tree (X · Wacky!)
**Prompt:** A brown tree trunk with two stub branches, crowned by a rainbow xylophone: five upright bars in red, orange, yellow, green, and blue, graduated in height. Two wooden-headed mallets rest against the outer bars. A friendly face sits on the trunk just below the bars (two dark dot eyes, small smile). Musical, colorful, playful. Full plant standing upright, base of trunk or stem touching the bottom of frame, subject fills 85% of frame height.
**Must include:** five rainbow xylophone bars (red/orange/yellow/green/blue), two wooden mallets, brown trunk, dot eyes + smile

## Letter Y

### `plants/y-yucca.png` — Yucca (Y · Real!)
**Prompt:** A spiky yucca on a short brown woody trunk, bursting into a starburst of long, stiff, sword-shaped green blades radiating in all directions, lighter green blades near the center. A few tiny pale-cream flower buds nestle among the blade bases. Sharp, upright, desert-hardy. No face. Full plant standing upright, base of trunk or stem touching the bottom of frame, subject fills 85% of frame height.
**Must include:** starburst of sword-shaped green blades, short brown woody trunk, pale-cream flower buds, layered greens

### `plants/y-yak-yarrow.png` — Yawning Yak Yarrow (Y · Silly!)
**Prompt:** A green yarrow stem with a small leaf, topped by a big round fluffy yak-flower head in shaggy brown with a lighter tan face patch. Two little curved cream horns arch up from the top, two soft cream ears fan out the sides, and a wide-open oval mouth mid-yawn shows below two dark dot eyes. Cozy, sleepy, fuzzy. Face centered on the yak head. Full plant standing upright, base of trunk or stem touching the bottom of frame, subject fills 85% of frame height.
**Must include:** shaggy brown fluffy yak head, two curved cream horns, cream ears, dot eyes + wide yawning mouth

### `plants/y-yoyo-tree.png` — Yippee Yoyo Tree (Y · Wacky!)
**Prompt:** A brown-trunked round green tree with two yoyos dangling on white strings from its foliage: a candy-red yoyo lower left and a sky-blue yoyo lower right, each with a lighter concentric center and a tiny dark axle dot. A friendly face sits on the green canopy (two dark dot eyes, small smile). Bouncy, bright, playful. Full plant standing upright, base of trunk or stem touching the bottom of frame, subject fills 85% of frame height.
**Must include:** red yoyo + blue yoyo on white strings, concentric centers with axle dot, round green tree + brown trunk, dot eyes + smile

## Letter Z

### `plants/z-zinnia.png` — Zinnia (Z · Real!)
**Prompt:** A single zinnia on an upright green stem with two leaves. Layered rounded petals in hot pink and lighter rose form a full daisy-like bloom around a small golden-yellow center dotted with orange. Cheerful, full, softly clay-rounded. No face. Full plant standing upright, base of trunk or stem touching the bottom of frame, subject fills 85% of frame height.
**Must include:** layered hot-pink + rose petals, golden-yellow center with orange dot, green stem, two green leaves

### `plants/z-zebra-zinnia.png` — Zippy Zebra Zinnia (Z · Silly!)
**Prompt:** A green stem with a small leaf, topped by a white zinnia bloom whose rounded petals each carry bold black zebra stripes. At the center sits a round pale face with two dark dot eyes, a small smile, and two tiny black tufted ears poking up. Zippy, stripy, and fun. Face at the flower center. Full plant standing upright, base of trunk or stem touching the bottom of frame, subject fills 85% of frame height.
**Must include:** white petals with black zebra stripes, pale round center face, dot eyes + smile, two little black ear tufts

### `plants/z-zombie-tree.png` — Zany Zombie Tree (Z · Wacky!)
**Prompt:** A goofy zombie tree with a mottled olive-green trunk and two crooked wobbly branches, topped by a big round lime-green foliage head. On the face: two white googly eyes with dark pupils, stitched dark-green eyebrows, a wide crooked grin with a few square blocky teeth, and a couple of little stitch marks on the crown. Silly, harmless, and grinning. Face centered on the green head. Full plant standing upright, base of trunk or stem touching the bottom of frame, subject fills 85% of frame height.
**Must include:** lime-green round zombie head, white googly eyes with pupils, crooked grin with blocky teeth, mottled olive trunk + crooked branches
