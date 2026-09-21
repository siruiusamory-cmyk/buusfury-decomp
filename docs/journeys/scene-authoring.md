---
id: scene-authoring
title: Author an interactive NPC scene and see it in the running game
capabilities:
  - shell
  - atlas
  - entity
  - behavior
  - validate
  - launch
proof: runtime
tests:
  - tests/unit/test_workbench_scene.py
  - tests/unit/test_scene_authoring.py
  - tests/unit/test_authored_placements.py
  - tests/unit/test_authored_behavior_body.py
  - tests/unit/test_authored_behavior_trigger.py
  - tests/integration/test_authored_scene_rom.py
  - tests/integration/test_authored_behavior_execution_rom.py
---

# Journey - scene authoring

A "scene" here is not a container type: the toolkit adds no `Scene` type, graph,
compiler, scheduler or manifest. It is **one authored placement record plus its
behavior or authored script plus the text that behavior shows**, held in one
project and built through the normal project path. The UI surface is the tab
labelled **Maps** (the Scene tab); the visually-oriented **Map** tab is a
separate workspace over the same project.

## Steps

1. Open the canonical Buu's Fury image in the Atlas tab.
2. Open or **Extract** a project in the Build tab.
3. In the **Maps** tab, choose a map from the map list, which reports each map's
   support state and placement count.
4. Pick a **clone source** placement from that map's table. The authored entity
   is built from an existing placement type - no new record format is invented.
5. In the Add NPC form, give the entity a name, set its position, and choose a
   behavior: either an existing descriptor, or the authored
   `show_centered_sprite_text` script with its message text and X/Y.
6. Optionally attach the trigger the engine offers. It is offered only when the
   chosen source qualifies, and an unsupported combination fails closed.
7. **Apply.** The authored placement is written to the project, and the earlier
   validation and build result are invalidated. A **Revert** control removes the
   authored placement again.
8. In the Build tab, **Validate**, then **Build** - a new image, with the source
   never written.
9. In the Launch tab, launch it, reach the trigger in game, and observe the
   authored result.

## What this proves, and what it does not

**Proof level reached: runtime proof.**

It is worth being precise about which observation supports which half, because
the two halves are **different runs and different artefacts**:

- **Through the shipped GUI**, human-observed: a complete interactive NPC scene
  was authored entirely in DragonByte Z - map selection, placement clone, entity
  configuration, `on_defeat` behavior plus an authored script, Validate, Build,
  Launch and in-game interaction with no Python, TOML, CLI or hex editor - and
  the authored banner appeared in game. A second map scene was authored and run
  the same way.
- **Through the SDK build path**, instrumented: an authored placement that does
  not exist in the original game was read by the running engine's own array, an
  authored behavior body was entered by the engine, and the authored trigger
  reached a native handler whose visible result was captured.

**No scene authored through the GUI has been observed by captured
instrumentation.** The instrumented proofs and the GUI proofs are separate
evidences; neither one is evidence for the other's last mile. Do not merge them
into a single "proven" claim.

## Limits

These are the boundaries that currently constrain what a scene can be, and they
are ROM-verified rather than editorial:

- **Verified writable capacity is one 256-byte region** at
  `[0x007EA400, 0x007EA500)`. Measured against it: one complete authored
  interactive NPC used 63 bytes, and a full authored scene's region usage was
  recorded as 71 bytes with **184 bytes reported remaining**. Those last two
  figures are quoted from the record rather than re-derived from the region
  bounds - they sum to 255, not 256, so treat the remaining figure as the
  record's stated value. Region demand is per target map, since the object array
  grows by four bytes per placement.
- **Only 3 of the 452 maps offer the fully editable authoring path**; 265 are
  partial and 184 are read-only.
- **One trigger exists**: `on_defeat`, offered only for a qualifying enemy
  placement type with a confirmed enemy stat link. The trigger declaration
  itself emits no ROM bytes. Defeat and teardown remain confounded in the
  evidence, so the trigger's dispatch is not claimed to be uniquely attributable
  to the defeat condition.
- **One authored script effect exists**: `show_centered_sprite_text`, a
  straight-line effect with no branches and no native calls. The other native
  handlers have no established gameplay meaning, so a new effect is research
  work rather than an authoring option.
- **Text reuses an existing id and must fit its host string's allocation.** An
  over-long message is refused by validation rather than truncated (a first
  attempt was refused for being four bytes too long). Relocation can lift the
  allocation limit for a relocatable table and a single-reference entry, but
  creating new text ids is not claimed.
- **New maps and scenes are not materialised.** `map-new` is a missing
  capability: it needs an authored warp and map-root fields that are still
  unresolved.
