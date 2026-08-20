# Architecture

## Phase 0 boundary

Phase 0 identifies ROMs and records evidence. It does not parse game data beyond the standard GBA header and does not write ROMs.

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

- Original ROMs are inputs only and are opened with `rb`.
- Identification hashes and captures header bytes through one descriptor, then checks device/file identity, size, and modification time against the path after reading.
- Future edits must target generated copies beneath ignored output directories.
- A game code, region, revision, or size alone cannot verify identity.
- SHA-256 is required for `VERIFIED`; legacy hashes are corroborating metadata only.
- Different hashes remain different profiles until reproducible evidence proves compatibility.
- Profile-specific addresses must never be transferred to another hash silently.
- Ambiguity and contradictory metadata are errors, not nearest-match opportunities.
- No proprietary ROM bytes, extracted assets, or binary dumps belong in tracked files.

## Deliberate omissions

Phase 0 contains no `MapEntry` parser/serializer, allocator, relocation system, compression integration, script VM, graphics/audio replacement, Tiled support, GUI, emulator automation, or remake content.
