---
id: dialogue-editing
title: Rewrite the supported dialogue line and see it in the retail dialogue box
capabilities:
  - shell
  - atlas
  - inspector
  - dialogue
  - validate
  - launch
proof: runtime
tests:
  - tests/unit/test_workbench_dialogue.py
  - tests/unit/test_dialogue_authoring.py
  - tests/unit/test_build_panel_guard.py
  - tests/unit/test_workbench_session.py
  - tests/integration/test_rom_expand_001.py
---

# Journey - dialogue editing

## Steps

1. Open the canonical Buu's Fury image in the Atlas tab.
2. Open or **Extract** a project in the Build tab. Editing requires an open
   project; without one the Inspector's authoring controls stay disabled.
3. In the Atlas tab's text search, search for the line (the recorded walkthrough
   searched `Good luck, Goku!`).
4. **Activate the decoded result.** The application switches to the Inspector.
   A result the SDK cannot resolve as a mapped target stays read-only and has no
   address- or text-based fallback.
5. In the Inspector's **Compressed Dialogue** group, edit the line. Validation
   runs as the text is typed; **Apply** is enabled only when the text is valid
   *and* changed.
6. **Apply.** The project override is persisted and the earlier validation and
   build result are invalidated; the Build tab then requires Validate again.
7. In the Build tab, choose an output directory, **Validate**, then **Build**.
   The build emits a **new** image and refuses to write over the source image.
8. In the Launch tab, launch the emitted image in the configured emulator.
9. Trigger the greeting in the game and observe the authored line in the
   **normal retail dialogue box**.

## What this proves

**Proof level reached: runtime proof.**

This reaches the strongest level the project records for a product feature: the
owner performed the walkthrough above and saw `Nice work, Goku!` in
the retail dialogue box, and the emitted image was separately observed through
the retail consumer at `0x08012240` in a tracked mGBA session. The build path
itself is pinned at the emitted-image level by a ROM-gated test.

The runtime claim rests on **recorded** observations. A later reader should not
restate it as a fresh run without making one.

## Limits

- **Exactly one editable target.** `AUTHORED_DIALOGUE_TARGETS` holds a single
  entry, `goku-greeting`; resolution matches the exact packed handle. Everything
  else is read-only until a target is registered.
- **The replacement may change decoded length.** The editor is a single-line
  field, and a line longer or shorter than the one it replaces is accepted; an
  unencodable line is refused by validation rather than truncated. The bound for
  this target is not the record's own length but the container: the rebuilt
  container must stay inside the toolkit's 64 KiB decoded-container limit, which
  puts the ceiling at a 94-byte line.
- **Relocation happens at build, and a longer line re-authors the handle.** The
  retail container recompresses 1,076 bytes larger (16,856 to 17,932) and is
  placed in the profile's generated-expansion region, so the emitted image is a
  16 MiB generated image rather than an 8 MiB in-place patch. That is generated
  expansion, not canonical free space. A longer replacement re-authors the
  record's durable handle and re-lays out its decoded container, so every record
  after it moves inside the container.
- Creating new text-table ids is not claimed: an **existing** mapped record is
  rewritten, and a container whose records cross the edited one is refused rather
  than reinterpreted.
- No automated test drives the shipped GUI end to end on a real ROM. The
  headless tests pin the state transitions (supported target enables editing,
  unsupported result fails closed, invalid apply does not mutate the project,
  apply invalidates validation and build, revert removes the override), and the
  ROM-gated test pins the emitted image.
