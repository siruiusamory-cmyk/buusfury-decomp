# Documentation

The index for everything under `docs/`. Start with the root
[`README.md`](../README.md) for what the product is, and
[`CONTRIBUTING.md`](../CONTRIBUTING.md) if you want to change something.

## Working on the project

| Document | Read it for |
| --- | --- |
| [`DEVELOPMENT.md`](DEVELOPMENT.md) | The engineering policy: the product and its acceptance target, evidence discipline, reverse-engineering policy, determinism, testing, Git safety, third-party boundaries. |
| [`REVIEW.md`](REVIEW.md) | The code-review gate: when it applies, what it examines, the verdicts and the closure sequence. |
| [`ROM_SAFETY.md`](ROM_SAFETY.md) | The mandatory safety contract: the read-only canonical input, profile identity, addresses and offsets, relocation, and what must never be committed. |
| [`testing.md`](testing.md) | The focused validation gates, how to run one, and what the full suite costs. |
| [`line-endings.md`](line-endings.md) | The byte-safe way to edit a tracked file without rewriting its line endings. |
| [`git-workflow.md`](git-workflow.md) | Pushing a branch, opening a merge request and finalizing after a merge. |

## The product

| Document | Read it for |
| --- | --- |
| [`architecture.md`](architecture.md) | The identification boundary, the dependency layers, safety invariants and future direction. |
| [`project-format.md`](project-format.md) | The authored project format and its determinism guarantees. |
| [`capability-registry.md`](capability-registry.md) | How the public capability list is defined and changed. |
| [`ROADMAP_TO_1_0.md`](ROADMAP_TO_1_0.md) | The complete route to a 1.0 release. |
| [`PROJECT_STATE.md`](PROJECT_STATE.md) | Current verified facts: the canonical image, established formats, executable flow and open questions. |
| [`workbench.md`](workbench.md) | The Maps editor's Layout mode and reopening a ROM the tool wrote. |
| [`workbench-architecture.md`](workbench-architecture.md) | The desktop editor's structure and its hard rules. |
| [`desktop-ui.md`](desktop-ui.md) | How a DragonByte Z editor surface should look, behave and be reviewed. |
| [`asset-export.md`](asset-export.md) | Exporting game resources out of a project. |
| [`relocation.md`](relocation.md) | Trust boundaries, limitations and APIs of the relocation layer. |
| [`rom-profiles.md`](rom-profiles.md) | Supported images and how identity is configured. |

## Reverse engineering

| Document | Read it for |
| --- | --- |
| [`reverse-engineering.md`](reverse-engineering.md) | The consolidated reverse-engineering notes and measured formats. |
| [`research-conventions.md`](research-conventions.md) | How a research record is written and when a claim is promoted. |
| [`runtime-capture.md`](runtime-capture.md) | The canonical emulator capture pipeline, its ordering and its tooling rules. |
| [`ghidra-workflow.md`](ghidra-workflow.md) | The static-analysis workflow and its calibration. |
| [`hash-investigation.md`](hash-investigation.md) | What the hashes of the shipped images are, and what they do and do not prove. |
| [`consumer-analysis.md`](consumer-analysis.md) | The executable consumer analysis behind the map data model. |
| [`upstream-audit.md`](upstream-audit.md) | What prior work was examined, and what it may and may not be used for. |
| [`research/`](research/) | The detailed evidence documents: formats, provenance and runtime findings. |

## Decisions and history

| Document | Read it for |
| --- | --- |
| [`decisions/`](decisions/) | Accepted architecture decisions, each recording its context and consequences. |
| [`journeys/`](journeys/) | End-to-end authoring walkthroughs through the tool. |
| [`warprand/`](warprand/) | The packaged warp randomizer application. |
| [`enemyrand/`](enemyrand/) | The packaged enemy randomizer application. |

## Conventions used here

- File names are lower case with hyphens, except the evidence documents under
  `research/`, which use upper-case names matching the subsystem they describe.
- A claim about the binary is labelled `CONFIRMED`, `INFERRED` or `UNKNOWN`;
  `docs/DEVELOPMENT.md` defines what those mean and what promotes a claim.
- Evidence belongs in a document, never in production source. Production source
  says what the code does; a test says what proves it; a document says how it was
  established.
