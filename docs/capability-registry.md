# The DragonByte Z capability registry

`src/data/capabilities.json` is the one current list of what DragonByte Z can
do. The public site derives its buildout list, its per-family tallies and its
percentage from it (`src/data/project.ts`), and
`tests/unit/test_capability_registry.py` is the gate that keeps the registry,
the site source, the rendered page and the repository's own provenance records
in agreement.

It is not a ticket ledger, a roadmap, a metrics store or a project-management
tool. It records current product state only, and only the fields that prevent
that state from being restated wrongly somewhere else. The build order for the
capabilities still `missing` here - and the release gate that follows once all 24
ship - lives in [`ROADMAP_TO_1_0.md`](ROADMAP_TO_1_0.md); the open technical risks
live in
[`research/PROJECT_CODE_QUALITY_AUDIT.md`](research/PROJECT_CODE_QUALITY_AUDIT.md).

## What belongs

A **product capability**: something an author can reach from DragonByte Z
today, or something the product deliberately does not do yet. Every record
carries the bounded scope that a bare "supported" label would erase.

Research knowledge does **not** belong in `capabilities`. Knowing a binary
structure is not a shipped feature, however complete the evidence is. The
proven facts most easily mistaken for capabilities live in `researchOnly`, which
is never counted and whose records deliberately carry no state, surface or
proof of their own.

## Fields

| Field | Meaning |
|---|---|
| `id` | Stable, unique, kebab-case. The site's row key and the tests' join key. |
| `family` | One of the declared `families`; capabilities are counted per family. |
| `title` | Short name, shown in the roadmap. |
| `state` | `shipped` or `missing`. Only `shipped` is counted. |
| `detail` | The current-scope sentence the site shows. |
| `limits` | Mandatory bounded scope: what it does not do, or why it is missing. |
| `surface` | Where in DragonByte Z it is reachable. Shipped records only. |
| `proof` | `runtime` (performed and observed in the original engine) or `application` (proven by the application's own round-trip, a rendered image, or a ROM-gated build proof). Shipped records only. |
| `evidence` | Provenance: ticket ids or repository paths, both of which a test resolves against the checked-out tree. Nothing here may need repository history, because CI clones shallowly. |
| `measurements` | Optional counts this record owns, so a quoted figure has one owner. |

`researchOnly` records carry `statement`, `contributesTo` (the capability ids
the fact supports) and `doesNotConfer` (what proving it still does not ship).
`doesNotConfer` is the point of the record.

`limits`, `surface`, `proof` and `measurements` are registry data, not page
copy: the site renders each capability's `detail`, so a limitation can be
recorded here without changing the public design. That also means `proof` is
where a proof-strength claim is corrected first - if milestone or research prose
ever disagrees with it, this file is the current record and the prose follows.

## Changing it

Shipping or retiring a capability is a product decision, so it is a deliberate
edit and a test run:

1. change the capability's `state`, its `limits` and, when shipping it, add the
   `surface`, `proof` and `evidence`;
2. update `track.capabilityTotal` if the list itself gained or lost a record;
3. run `python -m pytest tests/unit/test_capability_registry.py` and
   `npm run check`, then classify `public progress impact` as usual.

The percentage is never edited: it is computed from the `shipped` states.

Public progress also lives in `src/data/project.ts`, which holds the milestone
programme, the blocker prose and the measured-fact ledger. Two rules keep the
counts single-sourced:

- the blocker prose is hand-written and may quote a count only when some
  capability declares it in `measurements`, so a stale public figure becomes a
  failing test rather than a surviving sentence;
- a capability figure the page states outside the roadmap, meaning the measured
  strip and the product-capture captions, is read from `measurements` by
  `capabilityCount()`, never written again.

The ledger's remaining figures (tile banks, frame records, object slots and the
like) are corpus measurements rather than capability facts; they are still a
hand-written list, and deriving them is a separate concern.
