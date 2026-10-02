# ADR 0005 - Naming precedence

- **Status:** accepted (2026-09-21)
- **Evidence:**
  [`docs/research/RESOURCE_LIBRARY_CURATION.md`](../research/RESOURCE_LIBRARY_CURATION.md)
  ("Name authority", lines 22-55; and line 175);
  [`tools/export/buu_resource_curate.py`](../../tools/export/buu_resource_curate.py)
  (`animation_slot_name`, `scan_tree_technical_ids`);
  [`tools/export/map_browser.py`](../../tools/export/map_browser.py) (the
  ROM-derived label and its `map:NNNN` fallback);
  [`tools/webfoot/maps.py`](../../tools/webfoot/maps.py) ("Identity is not an
  address"); [`tools/webfoot/stats.py`](../../tools/webfoot/stats.py) (`alias`
  is a display name, never an identity);
  [`tests/unit/test_resource_library_curation.py`](../../tests/unit/test_resource_library_curation.py)
  (`test_no_animation_name_is_invented_from_appearance`);
  `RESOURCE-LIBRARY-CURATION-001`; `DRAGONBYTE-Z-MAP-BROWSER-001`.

## Decision

A human-facing display name comes from a fixed precedence, and nothing else:

1. **Verified ROM-derived name.** A map's `MapEntry +0x0C` low half, or an
   appearance definition's `+0x00`, resolved through the verified text pointer
   table and recorded as ROM text.
2. **Accepted, human-verified external or curated name.** The pinned
   `mainant/LOGExtractor` animation-slot table, or an equivalent curated name
   whose source is recorded on the record it names. Its status is recorded, not
   promoted: giving a folder the name `Walk` makes no engine-behaviour claim.
3. **Neutral fallback.** Where neither source supplies a name, a neutral label
   that describes position in the corpus rather than what the thing is - the
   `map:NNNN` identity, or a contiguous human sequence such as `Map 1` /
   `Sprite 1` / `Animation 5`.

Two rules follow, and they are the point of the decision:

- **Never infer a semantic name from appearance.** No name is invented from
  rendered pixels or from a plausible resemblance.
- **Canonical ids and addresses stay technical metadata.** They remain
  available as the stable join key and as inspectable detail; they are not
  promoted to the user-facing identity when a name exists, and a name is not
  promoted to an identity when it is a display convenience.

There is **one naming authority**. A new editor surface resolves a display name
through the existing source for its domain, or starts at the neutral fallback.
It does not build its own name list.

## Context

The project has ROM text, a pinned external tool's table, and a curated
resource pack, at different levels of proof, and the UI must show something for
every record - including the ones no source names. Guessing from appearance is
the failure mode this precedence exists to prevent: a plausible-looking name
silently becomes a claim about what a structure *is*, and later work then has to disprove it.

## Consequences

- Every name is attributable to a source, and the source travels with the
  record it names.
- The precedence is a lookup order, not a merge: source 1 wins where it exists,
  and the fallback is a label rather than a claim.
- **Current wiring is partial, and that is deliberate rather than drift to be
  silently corrected.** The curated pack implements all three rungs; the
  DragonByte Z surface today resolves rung 1 and falls back to rung 3, and its
  Map Browser reported 429 ROM-derived labels (69 distinct) against 23
  `map:NNNN` fallbacks across 452 maps. Rung 2 exists only in the curation
  pipeline.
- The SDK's stat layer holds a separate **display alias** (`BASE_STAT_NAMES`,
  labelled `INFERRED`, emitted for characters and never for enemies). It is a
  display convenience, not identity, and not a second naming database - but it
  is a fourth source that this precedence does not describe, and it is named
  here so a later reader does not mistake it for one of the three rungs.
