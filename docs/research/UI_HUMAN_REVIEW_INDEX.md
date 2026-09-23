# DragonByte Z, human visual review index

`DRAGONBYTE-Z-VISUAL-DIRECTION-PASS-001`, final accepted candidate: frozen at
`13d2ab2`, with the post-review corrections committed on top. Nothing here is
generated artwork: every image is a real screenshot of the running PySide6
application against the canonical Buu's Fury USA rev0 image.

Most captures are 1440x900. Four are 1100x720 (the narrow states plus
`g8-graphics-narrow`), and the two project-action dialogues are their own
content-sized dimensions, 542x350 for Build and 480x326 for Run.

## Look at these first

| | Path |
|---|---|
| **Contact sheet, all 25 candidate states in one image** | `<temp>\dbz-visual-pass\light-contact-sheet.png` |
| **Palette comparison, dark interim theme vs the accepted pink theme** | `<temp>\dbz-visual-pass\palette-comparison-buu.png` |
| **Before/after sheets, 17 pairs with captions** | `<temp>\dbz-visual-pass\comparison-light\` |

## A. Reference matrix (what the real tools do)

`docs/research/UI_REFERENCE_MATRIX.md`, a 14-row x 9-column matrix over GB Studio,
Porymap, Tiled, LDtk, Godot, Aseprite, RPG Maker MZ and HexManiacAdvance, with the
verified findings that changed a decision and the confirmed anti-AI constraints.

## B. BEFORE captures (baseline `ad3c022`)

`<temp>\dbz-visual-pass\before\`, 18 PNGs.

## C. AFTER captures (accepted candidate)

`<temp>\dbz-visual-pass\light\`, 25 PNGs:

- the 18 review states, `01-shell-no-rom` through `18-narrow-shell-atlas`;
- six Graphics states: `g2-graphics-static-sprite`, `g3-graphics-animated-sprite`,
  `g5-graphics-playing`, `g6-graphics-swatch-selected`,
  `g7-graphics-pending-recolour`, `g8-graphics-narrow`;
- `19-scene-editor-empty`, the Scene editor. It is not a strip destination: it is
  reached from a placement through View -> Detailed Editor, which the Maps editor's
  Objects mode enables. It is captured here because that editor had no evidence of
  its own, and because it is where one of the duplicated status sentences was found.

Two of the 18 are captured as the **modal dialogues** they are, not as pages:
`14-build-action` (Build) and `15-run-configuration` (Run). Because `14-build-surface`
was renamed to `14-build-action`, the comparison directory holds 17 sheets rather
than 18; the only missing pair is `compare-14`.

## D. Comparison sheets

`<temp>\dbz-visual-pass\comparison-light\`, 17 PNGs plus `index.md`.

## E. Per-state verdicts

| # | Capture | Verdict |
|---|---|---|
| 1 | `01-shell-no-rom` | PASS |
| 2 | `02-maps-browse` | PASS |
| 3 | `03-maps-layout` | PASS WITH NOTE |
| 4 | `04-maps-layout-cell` | PASS |
| 5 | `05-maps-pending-pick` | PASS |
| 6 | `06-maps-unsaved` | PASS |
| 7 | `07-maps-derivative-read-only` | PASS |
| 8 | `08-maps-read-only-map19` | PASS |
| 9 | `09-maps-objects` | PASS WITH NOTE |
| 10 | `10-inspector-dialogue` | PASS |
| 11 | `11-graphics-empty` | PASS |
| 12 | `12-graphics-selected` | PASS |
| 13 | `13-atlas-rom-open` | PASS |
| 14 | `14-build-action` | PASS |
| 15 | `15-run-configuration` | PASS |
| 16 | `16-narrow-shell` | PASS |
| 17 | `17-narrow-maps-browse` | PASS |
| 18 | `18-narrow-shell-atlas` | PASS |

**PASS: 16. PASS WITH NOTE: 2. FIX REQUIRED: 0.**

## F. Reference-fidelity matrix

`docs/research/UI_REFERENCE_FIDELITY_MATRIX.md`, 24 rows including the nine the
correction required: ROM-editor top-bar structure, primary editor taxonomy, map
workspace consolidation, global action duplication, Graphics empty state,
contextual inspector behaviour, status-bar density, shell visual coherence, and
data/content dominance. No row is MISSING.

## G. Functional diff

`docs/research/UI_FUNCTIONAL_DIFF.md`, presentation changes versus behaviour
changes, with the unchanged list verified rather than assumed.

## H. Palette provenance

`docs/research/UI_BUU_SPRITE_COLOR_SOURCE.md`, the sampling record for the
accepted palette: canonical sprite, raw indices, the pink ramp, the UI role
mapping and the two documented semantic exceptions. Reproduce it with
`python -m tools.qa.buu_sprite_palette`.

`docs/research/UI_GAME_COLOR_SOURCE.md` is the superseded earlier study and is
banner-marked as such.

## I. Automated probes

| Check | Command | Result |
|---|---|---|
| Overlap / clipping / elision, 16 states | `python -m tools.qa.overlap_probe` | 0 problems |
| Status parity across editor and width | `pytest tests/unit/test_workbench_project_status.py` | 22 passed |
| Duplicated status sentences, 9 screens | `python -m tools.qa.status_duplication_probe` | 0 duplicated labels |

| Build / Run dialogue behaviour | `pytest tests/unit/test_workbench_build_run_dialogs.py` | see the module |
| Sprite palette reproduction | `python -m tools.qa.buu_sprite_palette` | graphic:903 top-ranked |

The overlap probe lays the Build and Run surfaces out as editor pages for its
states 14 and 15, so it does not cover the shipped dialogue geometry.

## J. Known visual deviations

1. **`03-maps-layout`, the map is framed by a thin magenta cell grid.**
   Intentional: the grid is the cell hit-target and the mode's only affordance. It
   is drawn cosmetic, one device pixel at any zoom, and does not obscure artwork.
2. **`09-maps-objects`, the canvas shows a mauve field beside a 256px-wide map.**
   The retail map for `map:0040` is narrower than the placements its scene can
   hold, so the scrollable scene is wider than the image. That is truthful: the
   band is the reachable area the editor is showing, not padding.

## K. Closed since the first review

The independent review of the frozen candidate found no blocking issues and eight
non-blocking ones. The post-review correction closed the two material items and
the documentation items:

1. **Atlas drew its own status row** beside the shell's. The Atlas surface now
   publishes its status through its host instead of rendering it, so the shell bar
   is the only place the line appears.
2. **The index-0 transparency pass cost a Qt call per pixel** (3.3 s for a 9.2 Mpx
   composite). It is now one bulk byte translation feeding `setAlphaChannel`,
   byte-for-byte identical output, 0.042 s on the same input.
3. The palette provenance document's four stale values and one stale contrast
   ratio were corrected, and the second palette exception is now documented.
4. This index and `UI_FUNCTIONAL_DIFF.md` were reconciled with the final history.

## What to check for yourself

- Does the shell read as a ROM editor: **menu bar, one strip, workspace**?
- Are exactly four editors named, with no project action duplicated as a workspace?
- Is the map the dominant object in all three Maps modes?
- Does the Graphics inspector follow the selection, with one preview only?
- Does the one status bar say one thing on the left and project state on the right,
  with no second row anywhere?
- Does the pink read as Buu-derived rather than as arbitrary branding?
