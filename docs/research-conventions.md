# Research Conventions

Every reverse-engineering claim must use one status:

- `CONFIRMED`: directly supported by cited implementation, documentation, or a reproducible observation scoped to a named ROM profile.
- `INFERRED`: best explanation supported by evidence, but not directly proven.
- `UNKNOWN`: evidence is absent, contradictory, or insufficient.

## Evidence types

Keep these separate:

1. **Upstream implementation evidence**: exact repository, commit, source path, and symbol or line.
2. **Upstream documentation**: exact repository, commit, document, and section or line.
3. **Reproducible local observation**: command/procedure, exact profile hashes, result, and date.
4. **Inference**: evidence used, reasoning, alternatives, and missing proof.

Public source does not imply a license. A finding for one game, region, revision, or hash does not transfer to another without evidence.

## Suggested record

```yaml
name: map_entry.music_id
status: CONFIRMED
game: buus_fury
rom_profile: buus_fury_usa_rev0_01c1707f
offset_within_structure: 0x24
width: 4
type: u32
evidence_type: upstream_implementation
source_project: DragonByteZ
source_file: src/analysis.cpp
source_symbol: read_map_entries
source_commit: b2691209fa873cc0c1d7aa9cdea7c1da4430afe4
notes: >-
  The pinned implementation reads this offset as music_id. Independent
  byte-exact validation for our profile remains required by ROM-002.
```

## Promotion rule

Do not promote `INFERRED` to `CONFIRMED` through repetition. Promotion requires new direct evidence or a reproducible test. When sources conflict, record each claim and keep the conflict open.

## Binary discipline

- Never invent structure fields or semantic names.
- Unknown fields remain named and documented as unknown.
- Preserve unknown bytes in future round trips.
- Parsing precedes editing; byte-exact round trip precedes semantic modification.
- Addresses belong to named profiles.
- Record endianness, width, alignment, pointer domain, bounds checks, and failure behavior.
- Do not store proprietary sample bytes in notes or fixtures.

## Static disassembly discipline

A naive linear disassembly sweep can stop at the first undecodable halfword and
silently return nothing for every later address. An empty sweep result is
therefore **not** evidence that no consumer, caller, or reference exists. This
produced a real false negative during `LOGX-MAP-RENDER-001`, where a sweep
reported zero matches for patterns that were in fact present.

For ROM-code analysis:

- Do not treat an empty linear-sweep result as absence evidence.
- Use resynchronising disassembly (advance past undecodable halfwords), known
  function boundaries, cross-references, or another independently grounded
  route before concluding that a reference is absent.
- Distinguish incomplete disassembly from a genuine lack of references, and say
  which one the evidence supports.
- When a negative claim rests on a scan, report the scan's coverage explicitly
  rather than asserting absence from the image as a whole.

### Aggregate and constant-offset access

A constant-offset operand scan is **not** sufficient evidence that a field has no
consumer. Code can consume several adjacent fields through one aggregate access
without ever encoding an individual field offset, and a scan that looks for
`ldr rd,[rn,#off]` will miss it entirely.

`LOGX-CONNECTOR-001` produced a real instance. The consumer of `root + 0x40` and
`root + 0x44` is

```text
08009672  adds r1, #0x40
08009676  ldm  r1, {r1, r2}
```

The base pointer is first advanced to `+0x40`, and the two fields are then read
**together** by one 8-byte `ldm`. Neither word is ever the target of a
constant-offset load, so a scan for displacement `0x40` or `0x44` returns three
unrelated sites and looks like an absence. The scan was correct; the inference
from it would have been wrong.

For absence claims:

- Do not conclude "no consumer" from a constant-offset scan alone.
- Account for **base-pointer adjustment followed by an aggregate access** -
  `ldm`/`stm`, or any equivalent pattern that consumes a run of adjacent fields
  from one adjusted base. Look for an `adds`/`subs` that forms `base + k`
  followed by a multi-register load or store.
- State the scanner's coverage and its deliberate gaps rather than its result
  alone. For an operand scanner those gaps include the aggregate forms, the
  register-offset forms, and any encoding the scanner does not decode.
- A scanner used for absence claims should be **differentially tested against an
  independent disassembler**, with both the site population and the agreement
  count reported. `tools/research/thumb_mem_operands.py` was validated that way
  over `0x08000000..0x08007000` on the canonical image: **3147** in-scope
  constant-immediate sites at real instruction boundaries, **0** misses and
  **0** misreports, where in-scope means the displacement is written out
  (a 16-bit `[Rn]` counts as displacement zero), the base register is neither SP
  nor PC, and the displacement is non-negative. Report the definition alongside
  the count, because the number is meaningless without it.
