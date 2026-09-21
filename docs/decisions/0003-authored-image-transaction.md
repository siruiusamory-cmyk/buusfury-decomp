# ADR 0003 - Authored-image transaction safety

- **Status:** accepted (2026-09-21)
- **Evidence:**
  [`tools/webfoot/authored_image.py`](../../tools/webfoot/authored_image.py)
  (module docstring; `save_authored_image`, `verify_authored_image`,
  `normalize_changes`, `manifest_path_for`, `staging_path`);
  [`tools/webfoot/map_layout_edit.py`](../../tools/webfoot/map_layout_edit.py);
  [`tools/webfoot/write.py`](../../tools/webfoot/write.py) (`plan_changes`);
  [`docs/workbench.md`](../workbench.md) ("Map Browser: Edit Layout");
  `DRAGONBYTE-Z-AUTHORED-IMAGE-PIPELINE-001`;
  [`tests/unit/test_authored_image.py`](../../tests/unit/test_authored_image.py);
  [`tests/unit/test_write_invariants_property.py`](../../tests/unit/test_write_invariants_property.py).

## Decision

Every editor domain that publishes an authored derivative performs the same
sequence through **one shared transaction**:

```text
domain editor
-> legal semantic edit
-> bounded byte plan
-> shared authored-image transaction
-> validation
-> provenance
-> publication
```

**The shared transaction owns:** conflict detection, staging, path-collision
refusal, existing-destination preservation, verification before publication, and
derivative-manifest publication. Concretely: manifest and staging path
conventions; refusal of a save whose source is any path it would write or
delete; edit-plan normalization (duplicate physical writes collapse, conflicting
writes to one field fail closed before anything is emitted, applied order is
deterministic); emit at temporary sibling paths, verify there, publish only
afterwards; and the byte-level output checks.

**Domain code owns one thing:** whether its edit is actually legal, and how a
declared change is re-read out of the emitted image.

`write.plan_changes` remains the single implementation of the bounded-write and
overlap rules.

## Context

The proven properties an authored image needs - canonical immutability, a
bounded byte plan, staging, verification before publication, an existing
destination preserved on failure, and provenance that bounds a derivative to
canonical plus its declared edits - were first built inside the Map Layout
Editor. A second authored-image editor would otherwise have had to restate them,
and two copies of a safety rule is how one of them silently drifts.

## Consequences

- A new authored-image domain implements a **change checker** and a
  re-read step. It does not implement a manifest format, a staging scheme, an
  emit order or a publication rule.
- Safety properties are inherited rather than re-proven: a failed emit,
  verification or publish leaves an existing destination byte-for-byte intact
  with no temporary file behind, and a failed provenance publish is reported as
  an image without provenance rather than as a success.
- The split is deliberate and load-bearing. "Is this edit legal?" is domain
  knowledge; everything about *emitting safely* is not.
- This is a responsibility boundary, not a plugin system, an editor registry or
  a command bus: the shared module knows nothing about maps, chunks, tiles or
  any other domain format.
