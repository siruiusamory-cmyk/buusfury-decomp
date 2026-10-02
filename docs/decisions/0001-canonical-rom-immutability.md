# ADR 0001 - Canonical ROM immutability

- **Status:** accepted (2026-09-21)
- **Evidence:** [`ROM_SAFETY.md`](../ROM_SAFETY.md) ("The canonical input is read-only");
  [`tools/webfoot/authored_image.py`](../../tools/webfoot/authored_image.py)
  (source-alias refusal, `save_authored_image`);
  [`tools/webfoot/workbench/session.py`](../../tools/webfoot/workbench/session.py)
  (`open_rom`); `MAP-LAYOUT-WRITE-001`;
  `DRAGONBYTE-Z-AUTHORED-IMAGE-PIPELINE-001`;
  [`tests/unit/test_authored_image.py`](../../tests/unit/test_authored_image.py);
  [`tests/unit/test_write_invariants_property.py`](../../tests/unit/test_write_invariants_property.py);
  [`tests/integration/test_cross_profile_invariants.py`](../../tests/integration/test_cross_profile_invariants.py)
  (whole-ROM no-op rebuild);
  [`tests/integration/test_authored_placements_rom.py`](../../tests/integration/test_authored_placements_rom.py).

## Decision

The canonical Buu's Fury image is **source material, not an output target**.
DragonByte Z never modifies it in place. Every authored change is emitted to a
**new image**. A build that changes nothing is expected to be **byte-identical**
to its input. Generated ROMs are **never committed**.

## Context

The canonical image is the project's measurement subject: its profile and
SHA-256 anchor every ROM address, offset and capacity figure the SDK resolves,
and [`ROM_SAFETY.md`](../ROM_SAFETY.md) requires each write to follow
`verified base -> working
copy/generated output -> patch/output ROM`. A tool that could rewrite the
canonical file in place would invalidate the evidence base it depends on, and
the project would lose the one trusted baseline it compares every derivative
against.

## Consequences

- A save refuses any path that resolves to its own source - the requested
  output, the derived manifest, and both staging names - before it emits or
  deletes anything.
- The image and its manifest are built at temporary sibling paths, verified
  there, and only then published, so a failed save leaves an existing
  destination byte-for-byte intact.
- No-op identity is a **regression**, not a nicety: it is the measurable proof
  that the writer touched only what it declared. Both the layout writer and the
  project build assert it.
- ROMs, saves, states, memory dumps and generated outputs stay out of version
  control.
- This forbids writing *the canonical local file*, not in-place editing as a
  technique; a future feature may rewrite a working copy, and any such feature
  must still publish to a new image.
