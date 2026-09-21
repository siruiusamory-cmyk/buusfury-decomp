# Golden user journeys

A golden journey is the **shortest sequence that answers "what does success look
like from the user's perspective?"** for a capability that already ships. It is
not a test suite and not a specification: it names the real steps a user takes,
in the order the product actually takes them, and it stops at the strongest
evidence the product actually has for the end of that sequence.

Two rules keep them honest:

- **Real behaviour only.** Steps come from the shipped code and the accepted
  ticket record, not from memory or from a plausible workflow. Where a step is
  bounded - a supported type, a single operation, an exact length - the journey
  says so.
- **Stop at the strongest real evidence.** Each journey records which level of
  [ADR 0004](../decisions/0004-proof-levels.md) its last step reaches. A journey
  whose edit was never run in the original engine does not claim RUNTIME PROOF
  because a capability it touches has one.

Journeys reference existing tests instead of duplicating them. Where a step is
already pinned by a test, the front matter names the file; the journey text does
not re-describe the assertion.

## Format

Each journey is a Markdown file in this directory whose first block is
machine-readable front matter, parsed by
[`tests/unit/test_decisions_and_journeys.py`](../../tests/unit/test_decisions_and_journeys.py):

```yaml
---
id: map-layout-editing
title: Reassign one chunk cell and reopen the result
capabilities:
  - layout
  - save-as
proof: renderer
tests:
  - tests/integration/test_map_layout_editor_rom.py
---
```

| Key | Means |
| --- | --- |
| `id` | Stable kebab-case key, matching the filename. |
| `title` | One line, user-facing. |
| `capabilities` | Stable ids from [`src/data/capabilities.json`](../../src/data/capabilities.json). A journey may cover several, and a capability needs no journey. |
| `proof` | The strongest level the journey's own last step reaches: `structural`, `renderer` or `runtime`. |
| `tests` | Existing test files that pin a step or a contract in this journey. |

There is no second capability list and no journey index database: the front
matter above is the only machine-readable half, and
[`tests/unit/test_decisions_and_journeys.py`](../../tests/unit/test_decisions_and_journeys.py)
checks that every referenced capability is a shipped capability and that every
referenced test exists.

## The journeys

| Journey | Capabilities | Ends at |
| --- | --- | --- |
| [Map layout editing](map-layout-editing.md) | `shell`, `atlas`, `map-browser`, `layout`, `save-as`, `provenance` | renderer proof |
| [Dialogue editing](dialogue-editing.md) | `shell`, `atlas`, `inspector`, `dialogue`, `validate`, `launch` | runtime proof |
| [Scene authoring](scene-authoring.md) | `shell`, `atlas`, `entity`, `behavior`, `validate`, `launch` | runtime proof |
| [Safe build and derivative reopen](safe-build-and-derivative-reopen.md) | `validate`, `save-as`, `provenance` | renderer proof |

Not every shipped capability has a journey, and that is deliberate. A journey
exists where a user's path crosses several components and the acceptance
contract would otherwise have to be rediscovered.
