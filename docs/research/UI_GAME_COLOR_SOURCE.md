# UI game colour source study - SUPERSEDED

> **Superseded.** This study sampled the game's *overall* palette (maps, sky,
> grass, combat tones) and produced the interim cool-blue dark theme. The colour
> direction was then narrowed to **Buu's own in-game sprite**, which is what the
> shipped palette is derived from. The authoritative document is
> [UI_BUU_SPRITE_COLOR_SOURCE.md](UI_BUU_SPRITE_COLOR_SOURCE.md), and
> 	heme.py no longer contains any of the values below.
>
> Kept because the method it records - reproduce behaviour from ROM data rather
> than from memory - is the reason the final palette is defensible.

---

# UI game colour source study

`DRAGONBYTE-Z-VISUAL-DIRECTION-PASS-001`, colour-direction revision. This
file is the evidence that the workbench palette is derived from **Buu's
Fury itself** rather than from a generic dark-theme recipe. Every colour
below was sampled from material the game supplies: its own decoded object
palette and the pixels of its decoded sprites, read through the shipped SDK
by `tools/qa/game_color_sample.py`.

No colour here is generated, guessed, or taken from promotional artwork.

## How the sample was taken

```text
python -m tools.qa.game_color_sample
```

Sources, in order of authority:

1. the canonical image's **decoded object palette** (256 real RGB entries,
   weighted as the authoritative source because the game indexes it);
2. the **decoded pixels of the first 400 sprites**, so the counts reflect
   actual artwork rather than one table.

## Sampled source colours

| Visual range | Source | Sampled | Muted for chrome | UI role |
|---|---|---|---|---|
| dark blue / blue-gray | decoded palette + 1,281 sprite pixels | `#00218c` | `#0f215c` | shell background, panels, borders |
| sky / water / ki blue | decoded palette + 2,538 sprite pixels | `#1852f7` | `#3a5297` | selection and primary interaction |
| cyan | decoded palette + 1,307 sprite pixels | `#18bdef` | `#60a2b6` | keyboard focus, active mode |
| forest / grass green | decoded palette + 1,713 sprite pixels | `#007300` | `#2c532c` | valid / safe / confirmed |
| orange | decoded palette + 13,423 sprite pixels | `#ad7b39` | `#8e7f6c` | authored-content marker, rare emphasis (`accent_secondary`) |
| red | decoded palette + 2,094 sprite pixels | `#5a0000` | `#2e1111` | destructive / error / validation failure |
| purple | decoded palette + 3,712 sprite pixels | `#6308ad` | `#432859` | research / specialized state |
| earth / sand | decoded palette + 6,865 sprite pixels | `#f7c673` | `#d2cabc` | neutral surfaces and secondary text warmth |
| light neutral | decoded palette + 4,547 sprite pixels | `#ffffff` | `#ffffff` | primary text |

## How much each colour was muted

A game colour is not a UI colour. Buu's Fury's artwork is pitched for a
240x160 screen at high saturation; a panel of that saturation at desktop
size is unreadable and it competes with the map. Each sampled colour was
pulled a measured amount toward its own luminance, and the exact factor is
recorded above:

- **0.55** for the shell: the game's dark blues stay recognisably blue but
  dark enough for a background.
- **0.30-0.42** for the interaction and semantic colours: enough to read as
  the game's own hue, far enough from it that chrome never fights artwork.
- **0.34** for green and **0.32** for red: semantic roles must stay clearly
  distinguishable from each other under red-green colour blindness, which
  is why they are not muted further and never carry state by hue alone.
- **0.16** and **0.06** for neutrals: type stays neutral. Ordinary text is
  never tinted with a game colour.

## The rule this encodes

```text
GAME-INSPIRED, NOT GAME-THEMED
```

The source is the game. The *code* names UI semantics, never game objects:
`selection`, `accent_secondary`, `success`, `danger`, `research`. There is no
`kiBlue` and no `gokuOrange` in the workbench, because a role name that
describes the inspiration rather than the purpose cannot survive the next
art-direction change.

## The mapping actually implemented in `theme.py`

Each row is one role: the sampled game colour it came from, the value that ships,
and what that role is allowed to mean. A role that is not listed is a neutral and
carries no game colour at all. The muted values below are hand-tuned from the
sampled hues for legibility on a dark panel; the *hue* is the game's.

| UI role | Token | Sampled | Ships as | Used for |
|---|---|---|---|---|
| shell / app background | `background` | `#00218c` | `#101825` | outer shell, menu bar, tool strip, status bar |
| main editor surface | `surface` | `#00218c` | `#151e2c` | panels, tabs, the working surface |
| sidebars / inspector | `surface_raised` | `#00218c` | `#1b2635` | inspector, tool areas, panel headers |
| inputs / rows | `surface_input` | `#00218c` | `#121a26` | text fields, list rows, editable cells |
| canvas | `canvas` | `#00218c` | `#0d141f` | the map canvas, below the artwork |
| borders | `border` / `border_strong` | `#00218c` | `#26313f` / `#35455a` | hairlines and region boundaries |
| **primary interaction** | `accent` | `#1852f7` | `#5b9ada` | selected editor, active mode, selection, primary action |
| focus ring | `focus` | `#18bdef` | `#67c3e8` | keyboard focus, always with a 1-2px width too |
| selected row | `selection` / `selection_edge` | `#1852f7` | `#243b56` / `#4a7ba8` | list and sprite-grid selection |
| **secondary brand accent** | `accent_secondary` | `#ad7b39` | `#c98a45` | authored-content markers, one rare emphasized action, branding |
| valid / safe | `success` | `#007300` | `#6fae72` | validation passed, save confirmed |
| pending / unsaved | `pending` | `#ad7b39` | `#d99a52` | uncommitted edits, always with a glyph and a count |
| destructive / error | `danger` | `#5a0000` | `#dd6b60` | failed validation, refused writes |
| research / specialized | `research` | `#6308ad` | `#b18ad4` | the research-state chip only |
| primary text | `text_primary` | `#ffffff` | `#e9edf2` | labels and values, never tinted |
| secondary text | `text_secondary` | `#ffffff` | `#aab6c4` | captions, hints, metadata |
| technical text | `text_muted` | `#ffffff` | `#7f8d9c` | addresses, offsets, provenance |

## Measured contrast

WCAG relative-luminance ratios computed from the shipped tokens:

| Pair | Ratio | Meets |
|---|---|---|
| `text_primary` on `surface` | 14.24:1 | AAA |
| `text_primary` on `background` | 15.14:1 | AAA |
| `text_primary` on `surface_raised` | 12.99:1 | AAA |
| `text_primary` on `selection` | 9.73:1 | AAA |
| `text_secondary` on `surface` | 8.13:1 | AAA |
| `text_muted` on `surface` | 4.94:1 | AA |
| `text_muted` on `surface_input` | 5.15:1 | AA |
| `text_disabled` on `surface` | 2.94:1 | intentionally below AA: disabled, and still legible |
| `accent` on `background` | 6.00:1 | AA |
| `accent` on `accent_ground` | 4.58:1 | AA |
| `success` / `pending` / `danger` / `research` on `surface` | 6.36 / 6.93 / 5.06 / 5.95:1 | AA |

No state is carried by hue alone: every status role also has a glyph from
`theme.status_glyph`, the maintainer here being red-green colourblind.

## What the identity deliberately is not

- not yellow/gold text on near-black, which is the generic dark-developer-tool
  look the colour review rejected;
- not the game's colours painted onto every widget: no orange tabs, no orange
  headings, no orange body text, no orange borders;
- not a themed launcher: no gradients, glow or faux-HUD decoration.

The game shows through in *relationships* - a cool ki/sky blue meaning "this is
where you are working", an orange meaning "this is content you authored", a green
meaning "this is verified" - and in the real artwork on the canvas, which stays
the most saturated thing on screen.
