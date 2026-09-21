# Architecture decisions

These record the small set of engineering decisions a future contributor must not
have to re-derive from ticket history. They are not a ledger and not a second
project state: a ticket records what happened on one ticket, and
`docs/PROJECT_<local-state-name>` records what is currently true, while an ADR here records
a decision that outlives both and that later work is expected to obey.

Keep them short. An ADR earns its place by changing what a future engineer would
otherwise do, so it states the decision, the context that forced it, the
consequences that follow from it, its current status, and the authoritative
evidence that supports it. It should not restate the proof that produced the
decision; that lives in the ticket, research record or module it cites.

## Status vocabulary

| Status | Means |
| --- | --- |
| `accepted` | The project operates this way today and new work follows it. |
| `superseded by NNNN` | Replaced by a later ADR; kept for the record. |

Do not edit an accepted ADR to describe a different decision. Write the new ADR
and mark the old one superseded.

This directory holds only numbered ADRs and this index - not a glossary, not a
scratch note, not a draft. The consistency gate fails on any other markdown file
here, on purpose: a decision that no index lists is a decision nobody reads, and
a silent omission is the worse failure. Put prose that is not a decision in the
document it belongs to and link it from the ADR's evidence.

## Index

| ADR | Decision |
| --- | --- |
| [0001](0001-canonical-rom-immutability.md) | The canonical ROM is source material, never an output target. |
| [0002](0002-authored-derivative-trust.md) | A derivative is trusted only through verified provenance; resemblance is not identity. |
| [0003](0003-authored-image-transaction.md) | Every authored-image editor shares one emit/verify/publish transaction; the domain owns only legality. |
| [0004](0004-proof-levels.md) | Structural, renderer, runtime and product proof are four different claims and are never collapsed into "proven". |
| [0005](0005-naming-precedence.md) | A display name comes from a fixed precedence of sources; it is never inferred from appearance, and canonical ids stay technical metadata. |
| [0006](0006-public-product-screenshots.md) | Human-approved real screenshots of DragonByte Z may be published; that is not permission to publish commercial asset content. |
