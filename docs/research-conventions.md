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
