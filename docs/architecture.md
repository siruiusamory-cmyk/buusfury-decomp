# Architecture

## Identification boundary

Identification opens a ROM read-only, hashes it, and matches it against an exact
profile. Everything above it depends on that verdict: no decode, edit or build
path runs against an unverified image.

Current flow:

```text
local file opened read-only
        |
        +-- streaming hashes
        +-- minimal GBA header
        |
        v
config/roms.yaml exact identity match
        |
        +-- VERIFIED: one exact cryptographic profile and matching metadata
        +-- UNKNOWN: no cryptographic profile
        +-- CONFLICT: cryptographic identity but contradictory configured metadata
        +-- error: malformed input or ambiguous profiles
```

`tools.webfoot.hashing` owns streaming hashes. `tools.webfoot.gba_header` owns standard header interpretation. `tools.webfoot.profile` owns configuration validation and conservative identity matching. `tools.webfoot.rom` hashes and captures the header through one read-only descriptor, then compares descriptor/path identity metadata to detect ordinary concurrent changes. `tools.webfoot.cli` is presentation only.

No game-specific data offsets exist in Python application code. Profile metadata stays in `config/roms.yaml`.

## Layers (ARCH-TOOL-001)

Each layer depends only downward, so a decomp backend can later replace the
binary one without touching anything above it:

```text
webfoot.binary    address arithmetic and ROM-window checks
webfoot.rom       identity, read-only access, change detection
webfoot.layout    anchors, owned regions, typed references, free regions (TOOLKIT-003)
webfoot.formats   PURE byte <-> record codecs; no I/O, no paths          (TOOLKIT-001)
                  formats.text_tables: the UTF-16LE string codec        (TOOLKIT-004)
webfoot.stats     semantic records; callers name a field, not an offset  (TOOLKIT-001)
webfoot.text      semantic strings; callers name an identity, not a slot (TOOLKIT-004)
webfoot.allocation deterministic first-fit over declared free space      (TOOLKIT-003)
webfoot.relocation atomic anchor movement with reference rewriting       (TOOLKIT-003)
webfoot.write     validated, attributed emission of a NEW image          (TOOLKIT-001)
webfoot.project   authored source: project.toml + per-table TOML         (TOOLKIT-002)
webfoot.build     extract / validate / build orchestration               (TOOLKIT-002)
webfoot.cli       argument parsing and presentation only
```

`webfoot.text` is the first **variable-length** subsystem and sits beside
`webfoot.stats` rather than under it: both are semantic layers over their own
codec, and `webfoot.build` merges their changes into one write plan so overlap
detection spans subsystems instead of only within one.

Two rules are load-bearing and are enforced by tests rather than by convention:
codecs never perform I/O, so the byte source is swappable; and the project format
stores semantic values rather than addresses, so a mod does not depend on the
backend. See [`project-format.md`](project-format.md) for the authored format and
its determinism guarantees.

Writing exists as of TOOLKIT-001 and always produces a **new** image: the
canonical ROM is an input on every path and an output on none.

## Future direction

Later work may introduce title-specific readers feeding a neutral Webfoot internal representation:

```text
LoG / LoG II / Buu ROM readers
              |
              v
       neutral Webfoot IR
          /          \
      tooling        Tiled
          \          /
           Buu compiler
                |
                v
      generated copy of Buu ROM
```

The Buu's Fury engine is the target. Direct LoG1-binary-to-Buu-binary conversion is not planned. Unknown bytes must survive future parse/serialize round trips exactly before semantic editing is allowed.

## Safety invariants

- Original ROMs are inputs only and are opened with `rb`. Every write path emits a separate image and refuses to write over its input or over an existing output.
- Identification hashes and captures header bytes through one descriptor, then checks device/file identity, size, and modification time against the path after reading.
- Future edits must target generated copies beneath ignored output directories.
- A game code, region, revision, or size alone cannot verify identity.
- SHA-256 is required for `VERIFIED`; legacy hashes are corroborating metadata only.
- Different hashes remain different profiles until reproducible evidence proves compatibility.
- Profile-specific addresses must never be transferred to another hash silently.
- Ambiguity and contradictory metadata are errors, not nearest-match opportunities.
- No proprietary ROM bytes, extracted assets, or binary dumps belong in tracked files.

## Relocation infrastructure (TOOLKIT-003)

The new foundation uses `binary` and `layout` contracts, trusted `profile`
metadata, a verified `document` and deterministic `allocation`. `relocation`
compiles the batch into the shared `write` layer; semantic stat/project consumers
remain independent. These additions are separate from earlier toolkit work.

Anchors carry a logical identity separately from their current typed file range.
The document accepts profile-bound layout/research contracts and validates their
source bytes; numeric scanning produces candidates only. Declared and confirmed
references may be rewritten; unresolved candidates affected by movement abort.
Allocation uses only explicit verified profile free regions, in stable anchor
order and lowest aligned first-fit order. No existing game profile declares
free space. The portable proof uses a constructed synthetic profile.

A relocation batch verifies the original image, plans all destinations, retains
interior target deltas, moves source fields with their containing anchors, then
validates the proposed graph before invoking the existing image writer. Old
regions remain intact and reserved in the output document. Fixed-size stat and
project builds remain independent of relocation. See [relocation.md](relocation.md)
for trust boundaries, limitations, APIs and the executable proof command.

## Deliberate omissions

No content authoring system, compression integration, script VM, graphics/audio
replacement, Tiled support, GUI, plugin system, expansion or reclamation is
introduced by TOOLKIT-003. No canonical relocation safety claim is made.
