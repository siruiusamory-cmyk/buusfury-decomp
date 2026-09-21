---
id: map-layout-editing
title: Reassign a map's dominant-layer chunk cell and reopen the result
capabilities:
  - shell
  - atlas
  - map-browser
  - layout
  - save-as
  - provenance
proof: renderer
tests:
  - tests/integration/test_map_layout_editor_rom.py
  - tests/integration/test_map_layout_write_rom.py
  - tests/unit/test_map_layout_edit.py
  - tests/unit/test_map_layout_provenance.py
  - tests/unit/test_workbench_map_browser.py
  - tests/unit/test_workbench_session.py
  - tests/unit/test_authored_image.py
---

# Journey - map layout editing

**The bounded operation.** Reassigning one **existing same-layer dominant-layer
chunk cell** to another **non-null chunk that same layer already uses**. Nothing
else is implied or available: no tile painting, no new or edited chunks, no
resizing, no layer changes, no relocation, no arbitrary map formats. A journey
that reads as more than that is wrong.

## Steps

1. Open a supported canonical Buu's Fury image in the Atlas tab. Only Atlas is
   enabled until an image is open, and the image must match a configured
   profile identity.
2. Open the Map Browser tab.
3. Select a map that exposes an editable layer. 341 of the 452 maps do; the
   other 111 state why they are read-only.
4. Switch on **Edit Layout**.
5. Click a chunk cell of the map's dominant layer.
6. Choose another chunk **from that same layer** in the chooser.
7. Observe the live preview. The swap is previewed in memory; no ROM file is
   opened to preview it.
8. **Apply** the pending edit.
9. **Save As** to a new ROM. The image and its provenance manifest are built at
   temporary sibling paths and verified there before the destinations are
   replaced, so an existing file at the chosen path survives a failed save.
10. Leave or unload the canonical source.
11. Reopen the DragonByte Z-authored derivative through the normal Atlas ROM
    open, which accepts it through the manifest it wrote.
12. Re-select the map.
13. Observe the edited layout. The derivative renders the reconstructed
    canonical bytes with the verified edits applied as overrides, and is
    read-only.
14. Confirm the canonical source is unchanged.

## What this proves, and what it does not

**Proof level reached: renderer proof.**

The emitted image reopens and renders the edited layout through the accepted
renderer. The writer's own evidence is structural - two changed ROM bytes at file
`0x00292CA0-1` for the proof case, plus a no-op save that is byte-identical.

It is **not** runtime proof. Emulator validation of the layout write was not
performed; the application round-trip, which reopens the feature's own emitted
ROM through the manifest it wrote, was. Do not report this journey as the
original engine having run the edited layout.

## Limits

- 111 of the 452 maps are read-only: 110 dominant grids use a single chunk and
  so have nothing to substitute, and `map:0008` has no dominant layer.
- 156 of the 4,274 dominant cells are null; a null cell can be filled from its
  own layer and reverted to null, but it cannot be pointed at a chunk the layer
  does not already use.
- Map 19's terrain field is outside the proven form and stays view-only.
- A reopened derivative is read-only: further layout editing belongs to the
  canonical image it derives from.
