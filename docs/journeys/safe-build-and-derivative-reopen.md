---
id: safe-build-and-derivative-reopen
title: Deliver authored changes to a new image and reopen a verified derivative
capabilities:
  - validate
  - save-as
  - provenance
proof: renderer
tests:
  - tests/unit/test_authored_image.py
  - tests/unit/test_write_invariants_property.py
  - tests/unit/test_workbench_session.py
  - tests/integration/test_map_layout_editor_rom.py
  - tests/integration/test_project_build_rom.py
---

# Journey - safe build and derivative reopen

This is the **cross-domain delivery contract**: the same shape every writer
follows, whichever editor produced the change. It is kept separate from
[map layout editing](map-layout-editing.md) because it is the part a *future*
writer ticket reuses, and because its last two steps are domain-gated where the
editing journey's are not.

```text
canonical source
-> authored changes
-> validate / build
-> Save As to a new image
-> provenance emitted
-> derivative verified
-> derivative reopened
-> source unchanged
```

## Steps

1. Open the canonical image and a project, then make a supported authored change
   in whichever editor owns it.
2. **Validate** the project. Nothing is written while the output does not yet
   exist, so a rejected build leaves nothing behind to mistake for a good one.
3. **Build** or **Save As** to a destination that is not the source. The build
   panel refuses to write over the source image, and every path a save touches
   is resolved and refused against the source before anything is deleted or
   emitted.
4. The new image and its provenance document are written **at temporary sibling
   paths and verified there**, and only then published onto the destinations.
5. A failure at emit, verification or publication leaves whatever already
   existed at the destination **byte-for-byte intact**, with no temporary file
   behind. A failed provenance publication is reported as an image without
   provenance, not as a success.
6. A build that changes nothing is **byte-identical** to its input.
7. **Reopen the derivative through the application's normal ROM open.** It is
   accepted only when its provenance proves it is the canonical image plus
   exactly its declared, domain-legal changes.
8. An accepted derivative is browseable, renders its edited state, and is
   **read-only**.
9. The **source image is unchanged** - by hash, size and modification time.

## Proof level and domain coverage

**Proof level reached: renderer proof.**

The emitted image is verified and, where the domain supports reopening, renders
its edited state.

The build half is shipped for every project-backed editor domain. The **reopen**
half is not: derivative acceptance is declared legal change-class by change-class,
and today exactly one class is declared - the dominant-layer chunk replacement
[ADR 0002](../decisions/0002-authored-derivative-trust.md) describes.

| Domain | Build to a new image | Derivative reopened by the application |
| --- | --- | --- |
| Map layout (Map Browser Save As) | yes | **yes**, read-only |
| Dialogue, entity, behavior, palette, relocated text (Build tab) | yes | no - not a recognized derivative |

Do not read this journey as "any authored ROM reopens". An image built from
another domain's edits is emitted and launchable, but the application refuses to
recognize it as a derivative, and that refusal is the designed outcome rather
than a gap to paper over.

## Why this is one contract and not per-domain code

The transaction is shared, and the split is deliberate: the shared layer owns
conflict detection, staging, path-collision refusal, existing-destination
preservation, verification before publication and manifest publication, while
the domain owns only **whether its edit is legal** and how a declared change is
re-read out of the emitted image. A new writer domain therefore supplies a
change checker, not a second manifest format, a second staging scheme or a
second publication order.

## Limits

- Only declared, policy-legal edit classes are accepted on reopen. Everything
  else is refused **with the reason stated**.
- The canonical image is accepted by identity *before* any manifest is
  consulted, so provenance cannot make a foreign image acceptable.
- The source-alias guard is path-based and does not detect a hard link to the
  source.
- Arbitrary modified images, tampered images and tampered provenance all fail
  closed.
