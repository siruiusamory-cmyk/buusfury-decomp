# ADR 0004 - Proof levels

- **Status:** accepted (2026-09-21)
- **Evidence:** [`src/data/capabilities.json`](../../src/data/capabilities.json)
  (`proof`, and `researchOnly`); [`docs/capability-registry.md`](../capability-registry.md)
  ("Fields"); [`DEVELOPMENT.md`](../DEVELOPMENT.md) ("Evidence discipline");
  the capability registry record and
  [`../PROJECT_STATE.md`](../PROJECT_STATE.md) (the corrected
  `visual-editor-foundation` proof claim); `WORKBENCH-002` (dialogue, runtime);
  `MAP-LAYOUT-WRITE-001` ("Emulator runtime validation was not performed");
  [`docs/research/MAP_RENDER_FORMAT.md`](../research/MAP_RENDER_FORMAT.md)
  ("Reference comparison and retail validation").

## Decision

Four different claims are kept apart, and none of them is ever replaced by the
word "proven" on its own.

| Level | Claim |
| --- | --- |
| **STRUCTURAL / STATIC PROOF** | A relationship is established from the ROM, its code or its data - a decode, a round-trip, a disassembly-derived binding. |
| **RENDERER PROOF** | The accepted renderer produces the expected visual result. |
| **RUNTIME PROOF** | The original game engine was observed executing or using the authored result. |
| **PRODUCT CAPABILITY** | A user can perform the operation through the shipped tool. |

The first three are **evidence levels about a result**. The fourth is a claim
about the **product**, and it is orthogonal to them: a shipped capability is
recorded together with whichever evidence level supports it.

## Context

These collapsed once, in public wording, and the collapse was load-bearing:
a completed milestone stated that sprite browsing and palette recolouring were
runtime-proven, when the accepted record (`TOOLKIT-010`) says that runtime
in-game validation was not performed and every visual proof there is static.
The capability registry now carries a `proof` field, so the distinction has a
machine-readable home and that correction is its worked example.

The levels are not interchangeable in either direction, and neither is stronger
in every respect:

- **Renderer proof is not runtime proof of authored content.** Matching a
  captured VRAM oracle shows the renderer reproduces what the engine loaded. It
  says nothing about whether an authored edit was ever executed by the engine.
- **A build or emit proof establishes the emitted image**, not engine
  behaviour: it proves the bytes, and the no-op/round-trip properties, and
  nothing about how the game reacts to them.
- **A static binding is not a runtime observation.** Resolving a consumer from
  the executable is strong evidence about the code path; it is not an
  observation of that path running.

## Consequences

- A capability states which level it reached, and does not report a bare "proven".
- **RUNTIME PROOF requires an engine observation of the specific authored
  result.** No amount of static or emitted-image evidence promotes to it.
- A golden journey ends at the **strongest level it actually reaches** and says
  so, even when that is weaker than the level claimed for one of the
  capabilities the journey touches. Reopening a derivative and seeing the edited
  layout is an application-level proof, not an emulator run of that edit.
- The capability registry's `proof` field is the two-value product projection of
  this table: `runtime` means the RUNTIME level was reached, and `application`
  means the result was established inside the shipped application by its own
  round-trip, a rendered image or a ROM-gated build proof - the
  structural/renderer levels, without an engine run. The registry is the
  product-facing record; where a reader needs the finer level, the cited research record is the authority.
- `DEVELOPMENT.md`'s `CONFIRMED` / `INFERRED` / `UNKNOWN` labels and its `LEVEL 0..4`
  runtime scale are unchanged and remain the vocabulary for binary and
  executable claims. This ADR is about which *kind* of claim a proof is, not
  about how confident one claim is.
