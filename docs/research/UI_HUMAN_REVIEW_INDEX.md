# DragonByte Z, human visual review index

`DRAGONBYTE-Z-VISUAL-DIRECTION-PASS-001`, corrected candidate. **Not frozen, not
staged, not committed.** Nothing here is generated artwork: every image is a real
screenshot of the running PySide6 application against the canonical Buu's Fury
USA rev0 image.

Start with the contact sheet, then open whichever full-resolution capture you want
to judge. Every capture is 1440x900 except the three narrow states, which are
1100x720.

## Look at these first

| | Path |
|---|---|
| **Contact sheet, all 18 candidate states, one image** | `<temp>\dbz-visual-pass\after-contact-sheet.png` |
| **Before/after sheets, 18 side-by-side pairs with captions** | `<temp>\dbz-visual-pass\comparison\compare-*.png` |
| Comparison index (markdown, embeds every sheet) | `<temp>\dbz-visual-pass\comparison\index.md` |

## A. Reference matrix (what the real tools do)

`docs/research/UI_REFERENCE_MATRIX.md`, 13-row × 9-column matrix over GB Studio,
Porymap, Tiled, LDtk, Godot, Aseprite, RPG Maker MZ and HexManiacAdvance, with the
verified findings that changed a decision and the confirmed anti-AI constraints.

## B. BEFORE captures (baseline `ad3c022`)

`<temp>\dbz-visual-pass\before\`, 18 PNGs.

## C. AFTER captures (this candidate)

`<temp>\dbz-visual-pass\after\`, 18 PNGs.

## D. Comparison sheets

`<temp>\dbz-visual-pass\comparison\`, 18 PNGs plus `index.md`.

## E. Per-sheet visual verdicts

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
| 14 | `14-build-surface` | PASS WITH NOTE |
| 15 | `15-run-configuration` | PASS WITH NOTE |
| 16 | `16-narrow-shell` | PASS |
| 17 | `17-narrow-maps-browse` | PASS |
| 18 | `18-narrow-shell-atlas` | PASS |

**PASS: 14. PASS WITH NOTE: 4. FIX REQUIRED: 0.**

The four notes are recorded under "Known visual deviations" below and are all
consequences of the corrected information architecture rather than defects.

## F. Reference-fidelity matrix

`docs/research/UI_REFERENCE_FIDELITY_MATRIX.md`, 23 rows including the nine the
correction required: ROM-editor top-bar structure, primary editor taxonomy, map
workspace consolidation, global action duplication, Graphics empty state,
contextual inspector behaviour, status-bar density, shell visual coherence, and
data/content dominance. **No row is MISSING.**

## G. Functional diff

`docs/research/UI_FUNCTIONAL_DIFF.md`, presentation changes versus behaviour
changes, with the unchanged list verified rather than assumed.

## H. Overlap / clipping / elision probe

`tools/qa/overlap_probe.py` walks the live widget tree in the same 16 states and
reports overlap, elision, clipping, squeezed controls and missing gutters.

**Result: 0 problems across 16 states**, after fixing four real defects it found
(see "Defects found and fixed" below).

## I. Focused test results

| Gate | Result |
|---|---|
| `tests/unit` (portable) | **2179 passed, 10 skipped** (skips are environmental: no canonical ROM, no built site) |
| Re-pointed shell tests | `test_workbench_smoke.py` 6 passed; the Graphics shell-mount and preview-size tests re-pointed, not deleted |
| Compile / import | clean |
| `git diff --check` | clean |

## J. Known visual deviations

1. **`03-maps-layout`, the map is framed by a faint gold chunk grid.** Intentional:
   the grid is the cell hit-target and the mode's only affordance. It is drawn
   cosmetic (one device pixel at any zoom) and does not obscure the artwork.
2. **`09-maps-objects`, the canvas shows a black band beside a 256px-wide map.**
   The retail map for `map:0040` is narrower than the placements its scene can hold,
   so the scrollable scene is wider than the image. That is truthful: the band is
   the reachable area the editor is showing, not padding.
3. **`14-build-surface` / `15-run-configuration`, sparse by design.** Neither is a
   workspace any more; each is a short configuration dialogue. They carry a stated
   purpose and no decorative chrome. `15` additionally states what the surface does
   *not* do, which is the one prose line either surface carries.
4. **The inspector's empty state leaves the lower pane empty.** With nothing
   selected there is nothing to say; the alternative the correction rejected was
   reserving rectangles for every possible relation.

## Defects found by this self-review and fixed

1. **The application theme was never applied in the capture path**, every earlier
   "after" capture was stock light Qt with dark strips pasted on, which is exactly
   the "black header pasted onto stock Qt panels" defect the correction named. The
   harness now applies the same theme the real entry point does.
2. **Panel headers painted over their own children** (a `paintEvent` fill running
   after the child label), making every section header nearly invisible. The fill
   moved into the widget palette.
3. **A stale status label was never hidden**, so a previous editor's status line
   stayed on screen beside the current editor's. The shell now owns one status
   label and copies the active editor's text into it.
4. **The Maps editor's status line was one host too deep to find**, so the wrong
   line was mounted. The Maps editor is now its own host.
5. **The chunk palette clipped its own selection tag** and, on a read-only map,
   stayed open and empty. Its height is now derived from its content, and it
   collapses to its header when there is nothing to choose.
6. **The Graphics inspector rendered empty scaffolding**, an empty preview box,
   rows reading `-`, a disabled Export button and an empty animation pane. It is
   now one sentence when nothing is selected and a populated contextual inspector
   when something is.
7. **Two status labels sat 7px apart**, reading as one run-on string. There is now
   an explicit gutter.
8. **The Graphics editor's own minimum was 1475px tall** (two stacked 320px
   previews), which forced the window floor above a laptop screen. The previews now
   sit side by side and the editor's minimum is 324px.

## What to check for yourself

- Does the shell read as a ROM editor: **menu bar -> one strip -> workspace**?
- Are there exactly four editor destinations, with no project action duplicated as
  a workspace?
- Is the map the dominant object in the Maps editor in all three modes?
- Is each mode's palette/tooling adjacent to the map rather than in a dialogue?
- Does the Graphics inspector feel populated by the selected sprite and empty when
  nothing is selected?
- Is `11-graphics-empty` genuinely free of scaffolding?
- Does the one status line say one thing on the left and project state on the
  right, without repeating itself?
- Does `01-shell-no-rom` look like one designed application rather than stock Qt
  with dark bars?
