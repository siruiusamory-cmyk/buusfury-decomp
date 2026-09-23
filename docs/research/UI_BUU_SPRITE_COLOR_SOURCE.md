# UI Buu-sprite colour source study

`DRAGONBYTE-Z-VISUAL-DIRECTION-PASS-001`, final colour direction. This file is
the provenance for the DragonByte Z palette: **every UI colour traces to one
sprite, read out of ROM data**, not to a generic theme, not to the game's maps,
and not to Dragon Ball brand colours.

Reproduce it with:

```text
python -m tools.qa.buu_sprite_palette
```

## Canonical Buu sprite

| | |
|---|---|
| **Graphic identity** | `buus_fury_usa_rev0_01c1707f/graphic:0903` (32×64, idle) |
| **Corroborating graphic** | `…/graphic:0904` (64×64, action pose) |
| **Source** | the canonical Buu's Fury USA rev0 image, `sprites.graphic(identity)` |
| **Palette source** | `sprites.palette.rgb`, the game's own 256-entry object palette |

**How it was found.** Not by eye. `tools/qa/buu_sprite_palette.py` scans every
decoded graphic and scores it on the presence of **all four** of Buu's design
colour families at once, pink skin, violet cape, white mantle and dark outline -
using the palette entries the game actually indexes. That combination is the
character design; any single hue (of which the game has many) appears on dozens of
unrelated sprites. The top-ranked candidates were then rendered and inspected to
confirm they are Majin Buu.

**Why this sprite is the identity source.** It is the character the game is named
for, it is the actor sprite the game itself uses for him in play (not a
promotional or menu-only asset), and it carries the full design: skin, antenna,
mantle, trousers, belt and eye, so the whole palette in one place.

## Raw palette, as the ROM supplies it

Indices and RGB exactly as decoded from the object palette, with where each
appears on the rendered sprite:

| Index | Raw RGB | Color | Where it appears on Buu |
|---|---|---|---|
| 42 | `#ff73b5` | pink | skin, lit |
| 40 | `#bd397b` | pink | skin, mid |
| 43 | `#ff8cbd` | pink | skin, highlight |
| 41 | `#de5294` | pink | skin, base |
| 44 | `#ffa5ce` | pink | skin, top highlight |
| 39 | `#9c185a` | deep magenta | skin, shadow |
| 38 | `#8c0052` | deep magenta | skin/cape, deepest shadow |
| 46 | `#ffd6e7` | pale pink | skin, specular |
| 136 | `#ffbde7` | pale pink | skin, specular |
| 2 | `#ffffff` | white | mantle and trousers, lit |
| 120 | `#f7f7f7` | white | mantle |
| 119 | `#dedede` | light grey | mantle, mid |
| 118 | `#c6c6c6` | grey | mantle, shadow |
| 117 | `#a5a5a5` | grey | trousers, shadow |
| 115 | `#7b7b7b` | grey | deep shadow |
| 114 | `#636363` | dark grey | outline, soft |
| 1 | `#000000` | black | outline |
| 63 | `#ad4a00` | gold-brown | belt, shadow |
| 65 | `#ff7300` | orange | belt, lit |
| 109 | `#ffad00` | gold | belt, lit |
| 79 | `#733900` | dark brown | belt, deep shadow |
| 77 | `#392100` | near-black brown | belt outline |
| 33 | `#c60000` | red | eye |

## The pink ramp is the product identity

Pink is DragonByte Z's **primary product colour**, taken from Buu's skin. It is
not a neutral to be apologised for, and it is not decoration: the four steps below
are a hierarchy, so pink does the work a grey ramp would do in a conventional
editor. Large areas take the *lightest* step and small interaction details take
the *deepest*, exactly as a grey ramp would be used.

| Ramp step | Token | Buu source | Used for |
|---|---|---|---|
| 1 lightest | `pink_soft` `#f2ccdf` | skin specular `#ffd6e7`, highlight `#ffa5ce` | the application background: large, low-priority shell areas |
| 2 mid | `pink_mid` `#eebfd6` | the same, one value deeper | chrome: menu bar, editor strip, status bar, panel headers |
| 3 strong | `pink_strong` `#a81560` | skin base `#de5294` deepened | interaction: active editor, active Maps mode, selection fill, primary action |
| 4 deepest | `pink_deep` `#6d0c3c` | skin shadow `#8c0052` | small high-contrast edges and text, pressed state, selection outline |

`background` is an alias of `pink_soft` and `chrome` an alias of `pink_mid`:
the shell *is* the pink, so one value carries two role names rather than two
similar values drifting apart.

**Selection uses ramp step 3, not a tint of step 1.** A pale-pink band on pale-pink
chrome is not a selection, so the selected row, sprite and map cell are a saturated
`#f2b3d0` fill with a step-4 outline (`#8f1350`), which is unmistakably stronger
than ordinary chrome while staying entirely inside the Buu family.

## UI translation

Raw source → adjusted UI value → semantic role. Adjustments are lightness and
saturation only; hue relationships are preserved.

| Semantic role | Token | Raw source | Ships as | Why the value moved |
|---|---|---|---|---|
| app background / shell | `background` | `#ffd6e7` + `#ffa5ce` | `#f2ccdf` | **Buu's own pink**, muted into a chrome value: the shell carries the identity rather than a neutral |
| shell mid step | `chrome` | `#ffd6e7` | `#eebfd6` | one value below the shell, for the menu bar, editor strip and status bar |
| editor surface | `surface` | `#ffffff` / `#f7f7f7` | `#fdfbfc` | the white mantle, lifted off the pink so it reads as the surface you work on |
| sidebars / inspector | `surface_raised` | `#ffffff` | `#ffffff` | the pure mantle |
| inputs / rows | `surface_input` | `#ffffff` | `#ffffff` | the same white; here the *border* separates a field, not another value step |
| canvas | `canvas` | `#a5a5a5` | `#c3a3b4` | the grey ramp warmed toward the skin, so it belongs to the same world |
| borders | `border` / `border_strong` | `#c6c6c6` / `#7b7b7b` | `#e4d2db` / `#cbadbc` | the grey ramp warmed toward the skin; on white panels these are the main separator |
| primary text | `text_primary` | `#000000` | `#2a2229` | the outline, lifted off pure black so it is a type colour |
| secondary text | `text_secondary` | `#636363` | `#5c525a` | a lighter step of the same ramp |
| technical text | `text_muted` | `#7b7b7b` | `#756970` | recessive, darkened to clear AA on white |
| disabled | `text_disabled` | `#a5a5a5` | `#938990` | clearly disabled, still legible |
| **primary interaction** | `accent` | `#de5294` / `#9c185a` | `#a81560` | Buu's skin, deepened so it separates from the pink shell *and* carries white text on white |
| accent hover / pressed | `accent_hover` / `accent_pressed` | `#ff73b5` / `#9c185a` | `#930f53` / `#6d0c3c` | the skin ramp, pressed to the deepest ramp step |
| accent ground | `accent_ground` | `#ffd6e7` | `#f7dbe8` | the specular pink, muted into a control fill |
| **secondary accent** | `accent_secondary` | `#ad4a00` / `#ffad00` | `#9a5300` | Buu's belt, deepened for legibility; authored content and brand detail only |
| selection | `selection` / `selection_edge` | `#de5294` / `#8c0052` | `#f2b3d0` / `#8f1350` | ramp steps 3 and 4: selection must beat the chrome, not blend into it |
| focus | `focus` | `#de5294` | `#c9186a` | the skin, at full strength: focus must not be mistakable |
| pending / unsaved | `pending` | `#ad4a00` | `#8a5a00` | the belt, so "waiting on you" is the authored-change colour |
| danger | `danger` | `#c60000` | `#b3261e` | the eye red, darkened for a light surface |
| research | `research` | none (see exceptions) | `#6b3fa0` | a violet the sprite does not carry; the second documented exception |
| checkerboard | `checker_dark` / `checker_light` | `#c6c6c6` / `#dedede` | `#cdbcc6` / `#ded1d8` | the grey ramp, warmed |
| preview canvas | `preview` | `#dedede` | `#e8dae1` | a light technical ground; black was replaced (see below) |
| grid / retail marker | `grid` / `marker_retail` | `#de5294` | `#b81f6b` | the identity colour at full skin strength, so map selection belongs to the same family |
| authored marker | `marker_authored` | `#ad4a00` | `#9a5300` | authored content uses the belt gold |

## Semantic exceptions

**Two**, and both are recorded here rather than hidden behind a claim of source
purity.

1. **`success` (`#1f7a3d`) is a conventional editor green.** Buu's sprite contains
   no green at all. "Valid / safe / confirmed" is a domain fact the product must
   communicate unambiguously, and a green that is recognisably green beats a hue
   that merely happens to sit in the sprite.
2. **`research` (`#6b3fa0`) is a violet the sprite does not carry.** It was
   originally documented as coming from the sprite's cape; the reproduced 24-entry
   palette has no violet, and the value sits about 55 degrees from the nearest
   sprite hue. The research role needs to be separable from both the pink accent
   and the blue-free neutral ramp, so a violet earns its place on distinctness
   rather than on provenance. Nothing in the accepted visual direction changes as
   a result: this is a correction to the provenance record, not to the palette.

Everything else, including `danger` (his eye) and `pending` (his belt), comes from
the sprite.

## Measured contrast

WCAG relative-luminance ratios for the shipped tokens:

| Pair | Ratio | Meets |
|---|---|---|
| `text_primary` on `surface` | 14.99:1 | AAA |
| `text_primary` on `surface_input` | 15.45:1 | AAA |
| `text_primary` on `background` (the pink) | 10.65:1 | AAA |
| `text_primary` on `chrome` | 9.61:1 | AAA |
| `text_primary` on `selection` | 8.93:1 | AAA |
| `text_secondary` on `surface` | 7.25:1 | AAA |
| `text_secondary` on `background` | 5.15:1 | AA |
| `text_secondary` on `chrome` | 4.65:1 | AA |
| `text_muted` on `surface` | 5.08:1 | AA |
| `text_disabled` on `surface` | 3.28:1 | intentionally below AA: disabled, still legible |
| `accent` on `surface` | 6.93:1 | AA |
| `accent` on `background` | 4.92:1 | AA |
| `accent_ink` on `accent` | 7.14:1 | AAA |
| `selection_edge` on `selection` | 5.11:1 | AA, so a selected row has a real outline, not a colour-only cue |
| `selection_edge` on `surface` | 8.57:1 | AAA |
| `success` / `pending` / `danger` / `research` on `surface` | 5.21 / 5.75 / 6.34 / 7.17:1 | AA |
| `accent_secondary` on `surface` | 5.64:1 | AA |

The accent was deepened from `#b81f6b` to `#a81560` specifically so it separates
from the pink shell (4.92:1 on `background`) as well as from the white panels,
rather than relying on the shell being neutral.

No state is carried by hue alone: every status role also has a glyph from
`theme.status_glyph`, the maintainer here being red-green colourblind.

## Preview canvas

The selected-sprite preview was a large black field. On a light editor that read
as a hole punched in the pane, and it was never load-bearing: a sprite's edge is
carried by its own outline (Buu's is `#000000`), not by the backdrop. The preview
now uses `preview` (`#e8dae1`), a light technical ground from the sprite's own
neutral ramp, so the artwork stays the subject.

## What this palette deliberately is not

- not yellow-on-near-black, the rejected generic developer-tool look;
- not a conventional desktop blue, which the review named as the other failure
  mode: there is no blue in this file;
- not the game's maps or grass/sky colours;
- not a themed launcher: no gradients, glow, faux-HUD decoration or character
  names in the code. `theme.py` names UI semantics only.
