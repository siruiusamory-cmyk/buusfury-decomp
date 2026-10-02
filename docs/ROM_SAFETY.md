# ROM and data safety

The mandatory safety contract for this repository. It applies to every write
path, every experiment and every test. [`DEVELOPMENT.md`](DEVELOPMENT.md) is the
general policy; this document is the safety detail behind it.

## The canonical input is read-only

The commercial ROM a user supplies is a **verified canonical input**, never a
write target. It is opened read-only, it is never overwritten, patched,
truncated, renamed or moved, and it is never copied into an output.

Every write, experimental or shipped, follows this flow:

```text
verified base -> working copy/generated output -> patch/output ROM
```

A build writes a new image. It refuses to write over its source, stages to a
temporary path, verifies the staged result, and only then publishes it, so a
failed build cannot damage what the user already has.

Before and after any authorized ROM-adjacent experiment, verify the image's
identity and confirm the original file was not changed.

## Profile identity

- Verify the exact configured profile before any profile-specific access.
- Fail closed on an identity or provenance mismatch. Never continue past one.
- A profile is trusted and profile-specific. Do not carry a constant, an
  address, a length or a layout between profiles or revisions without
  independent validation for that revision.
- The toolkit refuses an image it cannot identify against a configured profile
  rather than guessing at one.

## Addresses and offsets

- Keep ROM addresses and file offsets explicit and distinct. A value that is
  meaningful as an address is not automatically meaningful as an offset.
- Apply the Thumb state bit only when interpreting an address as executable
  code, and preserve the original raw code pointer separately from its
  normalized fetch address.
- Never mask, align, normalize or reinterpret a raw value silently.
- Use the existing pointer and address helpers instead of ad hoc arithmetic.

## Relocation and allocation

- Relocation must move every reference to a structure, or prove that no
  reference exists. A structure moved without its references is corruption.
- Verify capacity before writing into free space. An allocation proven against
  one image size is not proven against another.
- A grown or resized structure must be verified against the engine's own
  bounds, not only against the file it was written into.
- Provenance is part of the write: a build records what it changed, and the
  application reopens its own output only when that record proves it is the
  canonical image plus exactly the declared edits.

## What must never be committed

Never commit any of the following, anywhere in the repository:

- commercial ROM images (`*.gba`, `*.gb`, `*.gbc`);
- extracted or decoded commercial content, including one indexed PNG per sprite
  payload, tile sheets, palettes, text dumps and compiled asset blobs;
- saves, save states, memory dumps and SRAM files (`*.sav`, `*.srm`, `*.mss`,
  `*.ss?`, `*.state`);
- build output, generated ROMs, generated manifests describing a ROM, and any
  derivative image;
- a checked-out upstream repository under `extern/`;
- proprietary toolchain binaries, libraries or licence files.

`tests/unit/test_project_safety.py` enforces the ignore rules and proves that no
proprietary path is tracked. Machine-local convenience links and directories are
covered by the same rules.

## Runtime inputs

Saves and save states are private local research inputs.

- Preserve the original read-only and experiment on an ignored copy.
- Locate and hash a runtime input before use, and record what was used.
- Treat a runtime capture as evidence about the exact image and state it was
  taken from, never as a general claim about the game.
- A silent instrument is not negative evidence. Report which case a run is in:
  target silent with the liveness channel silent proves nothing, while target
  silent with liveness firing is a real negative.

## Test fixtures

- Use synthetic fixtures for binary logic.
- Portable tests must not require a private save, a save state or a ROM.
- Do not place large ROM-byte fixtures in tests.
- Local-ROM integration tests must be gated so they skip cleanly when no ROM is
  configured, and must not commit anything derived from one.

## Reporting a safety problem

A safety failure is a blocking finding. If a change could overwrite a canonical
input, move a structure without its references, commit proprietary content or
weaken an identity check, stop and report it rather than working around it.
