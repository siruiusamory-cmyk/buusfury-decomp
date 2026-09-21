# ADR 0002 - Authored derivative trust

- **Status:** accepted (2026-09-21)
- **Evidence:**
  [`tools/webfoot/authored_image.py`](../../tools/webfoot/authored_image.py)
  (`verify_authored_image`);
  [`tools/webfoot/write.py`](../../tools/webfoot/write.py) (`WriteManifest`, the
  one provenance document, built by `emit_image`, which is the call
  `save_authored_image` obtains it from: base profile and SHA-256, output digest
  and size, changed-byte count, and every change with its offset and both byte
  values);
  [`tools/webfoot/map_layout_provenance.py`](../../tools/webfoot/map_layout_provenance.py);
  [`tools/webfoot/workbench/session.py`](../../tools/webfoot/workbench/session.py)
  (`_verify_derivative`, called from `open_rom`);
  [`docs/workbench.md`](../workbench.md) ("Reopening a ROM this feature wrote");
  `DRAGONBYTE-Z-MAP-LAYOUT-EDITOR-001`;
  `DRAGONBYTE-Z-AUTHORED-IMAGE-PIPELINE-001`;
  [`tests/integration/test_map_layout_editor_rom.py`](../../tests/integration/test_map_layout_editor_rom.py);
  [`tests/unit/test_workbench_session.py`](../../tests/unit/test_workbench_session.py).

## Decision

There are exactly two trust tiers, and they are not interchangeable.

| Image | Trusted how |
| --- | --- |
| Canonical Buu's Fury image | By **canonical identity** - profile and SHA-256 - and accepted *before* any manifest is consulted. |
| DragonByte Z derivative | **Only** through verified provenance. |

Provenance must bind all five of these, and a derivative is accepted only when
every one holds:

1. the **canonical base identity** it derives from (base SHA-256 and the profile
   that names it);
2. the **emitted image's own digest and byte count**;
3. the **declared changes** - each with its offset and both byte values;
4. **reconstruction back to the canonical basis**: restoring every declared old
   value must reproduce the canonical image exactly, which bounds an accepted
   derivative to canonical plus exactly its declared fields and needs no copy of
   the canonical file;
5. **domain legality** of each declared change.

**Arbitrary modified ROMs are not accepted merely because they resemble a known
image.** Similarity is not identity, and a reader that resolves fixed
profile-specific addresses cannot tell the two apart by inspection.

There is **one** provenance document format - the project's existing
write-manifest document shape - and there is no second one.

## Context

The accepted readers resolve profile-specific ROM addresses, so the SDK must
know whether it is reading the canonical image or an image derived from it. The
product requirement that a user can reopen what the editor wrote therefore
cannot be met by "accept any ROM that looks right"; it needs a positive proof
that the file *is* the canonical image plus known, legal edits.

## Consequences

- A derivative is browseable and **read-only**. Further editing belongs to the
  canonical image it derives from.
- A derivative is rendered from the **reconstructed canonical bytes** with its
  verified edits applied as overrides. It is never parsed as if it were
  canonical.
- Refusal is the designed outcome, and it states its reason: no manifest, a
  malformed or mismatched manifest, a base that is not canonical, a file that
  does not match its declared output, or a declared change outside the domain's
  legal set.
- Provenance acceptance is **per domain**: today only the dominant-layer chunk
  replacement class is declared legal. An image built from another domain's
  edits is emitted and launchable but is not reopened as a recognized
  derivative.
- A new authored-image domain supplies a change checker rather than a manifest
  format; see [ADR 0003](0003-authored-image-transaction.md).
