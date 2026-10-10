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

## Where each journey lives in DragonByte Z

These journeys were written for the beta Workbench. DragonByte Z keeps the same
real behaviour and delivers it through five destinations plus the action bar, so
each journey is mapped to the surface that now owns it, or recorded as having no
home yet. This is a mapping of surfaces and not a second capability list: the
front matter above stays the only machine-readable half.

| Journey | Home | What has no home yet |
| --- | --- | --- |
| [Map layout editing](map-layout-editing.md) | **Maps**, whose chunk cells are exactly the bounded operation this journey's own limits section describes. **ROM**, which renders a reopened derivative read-only. **Action bar**, whose Build and Export patch are the Save As half. | Nothing in this journey is without a destination. The beta's live in-memory preview is a render of the Maps page rather than a surface of its own. |
| [Dialogue editing](dialogue-editing.md) | **Scripts & Text**, whose Spoken dialogue mode carries the SDK's one authored record. **Action bar**, whose Validate, Build and Run are the journey's last three steps. | The entry path: searching the image for a line and activating the decoded result is the semantic search surface, which no destination carries yet. Until it ships, the record is reached through its own row in the destination rather than by searching for its text. |
| [Scene authoring](scene-authoring.md) | **Entities**, which shows the placement family, its behaviours and their attachments, and **Scripts & Text**, which owns the text a behaviour shows. **Action bar**, whose Validate, Build and Run are the journey's delivery steps. | The journey's first half: authoring a placement from a clone source, choosing its behaviour and attaching the one trigger is the beta Scene tab's creation form, and no destination offers one. The Entities destination displays the family and edits one position; it does not create a record. |
| [Safe build and derivative reopen](safe-build-and-derivative-reopen.md) | **Action bar**, whose Validate, Build and Export patch are the delivery contract every destination's writer follows. **ROM**, which accepts and reopens a derivative read-only through the provenance the build wrote. | The reopen half for every change class but the dominant-layer chunk replacement, which is the one class ADR 0002 declares. A build from any other destination is emitted and launchable and is refused as a derivative, and that refusal is stated rather than papered over. |

Two beta surfaces are renamed rather than moved, and are named here so a reader
of these journeys can follow them: the **Atlas** tab is the ROM destination (the
image as an address space) with the Data destination's coverage view beside it,
and the **Build** and **Launch** tabs are the action bar's Validate, Build, Run
and Export patch.
