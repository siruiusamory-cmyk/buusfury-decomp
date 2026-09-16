# LOGX-MAP-RECORD-001: Buu map-list/root structure

## Scope and input

This is a read-only investigation of the canonical Buu's Fury USA Rev. 0
image, SHA-256
`940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e`.
No ROM, save, state, derived ROM, or emulator was used or written.

The external hypothesis source is
[`mainant/LOGExtractor`](https://github.com/mainant/LOGExtractor), current
`main` observed 2026-09-15.  The relevant source is
`MapViewer/MainForm.cs`, `ReadMapsFromROM` and `UxMapCanvas_Paint`; its ROM
reader is `MapViewer/Gba/ROM.cs`.  LOGExtractor hard-codes `map_count = 0x1c4`,
starts at `0x08e2e0`, advances by `0x38`, reads a big-endian short at `+0`, a
little-endian short at `+0x0c`, and manually follows `+0x2c` twice.  Its
`ReadPointer` masks a pointer-like value to 24 bits, so it is not used as this
project's pointer-validation rule.

## Reproduction

Run the checked-in probe against the local, read-only input:

```powershell
python -m tools.research.logx_map_record_probe 'C:\path\to\Dragon Ball Z - Buu''s Fury (U).gba'
```

`tools/research/logx_map_record_probe.py:1-126` opens its argument through
`Path.read_bytes`, performs no write, requires the exact 8 MiB size, and emits
deterministic JSON.  `tests/integration/test_logx_map_record_rom.py:1-74` is
the ROM-gated regression form; set `LOGX_CANONICAL_ROM` when the input is not
under this worktree's ignored `roms/` directory.

The text procedure is not a heuristic scan: the probe reads the lower 16 bits
of the raw little-endian word at `record+0x0c`, reads its little-endian pointer
slot from the independently verified table at `0x06bce8`, range-checks the
GBA address, then decodes UTF-16LE through its NUL.  See
`tools/webfoot/formats/text_tables.py:37-56,221-239`.

## Observations

The candidate extent is `[0x08e2e0, 0x0945c0)`: `0x1c4 * 0x38 = 0x62e0`
bytes.  The immediately preceding 32 bytes are:

```text
997400080d770008160022004100490000000000ace2080800000000c0e20808
```

The immediately following 32 bytes are:

```text
0100000000400000fa4f912081c596a691ca01263561563405d82436f82cb6d7
```

Neither boundary has a per-record terminator or padding sentinel.  Static
project evidence independently identifies a fixed-count lookup: the project
record documents the table literal, `0x38` advance, and helper returning
`0x1c4` at `docs/reverse-engineering.md:37-44`; the table is therefore not
ended by interpreting the adjacent bytes.  This ticket's byte census verifies
that exact bound, but does not assign semantics to either adjacent structure.

Across all 452 candidate records, the two raw bytes at `+0x00` interpreted as
a big-endian u16 are unique, nonzero values from `0x0001` through `0x1601`.
There are no duplicates.  Little-endian u16 interpretation is also unique but
does not match the statically verified two-byte lookup ordering.  This proves
a two-byte big-endian lookup key, not that its semantic name is "map ID".

Every `+0x0c` raw word has upper 16 bits zero.  Its lower little-endian u16 is
in `[0,1534)`, giving 70 distinct slots; 23 rows use zero and decode to the
empty text entry.  Thus this physical field reproducibly resolves through the
known text pointer table.  The field's *purpose* is unresolved: repeated
readable labels are useful correlation, but no consumer of `MapEntry+0x0c` was
identified in this ticket, so it is not promoted as a map-name field.

All 452 `+0x2c` raw words are 4-byte aligned, in-ROM, and unique.  Reading one
little-endian word at every validated target produces 452 further aligned,
in-ROM words, with 421 unique values.  This is an indexed word source rather
than a universally established two-object schema: static project evidence
shows the engine computes `MapEntry[+0x2c] + 4*(selector-1)`
(`docs/consumer-analysis.md:26-34`).  Selector 1 consumes target `+0x00`; it
does not establish an arbitrary second pointer hop for all records.

## Representative raw records

| index | record offset | key (`+0`) | `+0c` / decoded text | `+2c` raw | selected word at target `+0` |
| ---: | ---: | ---: | --- | ---: | ---: |
| 0 | `0x08e2e0` | `0x0001` | `0x0000` / `""` | `0x080728cc` | `0x082b8c38` |
| 1 | `0x08e318` | `0x0002` | `0x0000` / `""` | `0x080728d4` | `0x082b5fa0` |
| 39 | `0x08eb68` | `0x010b` | `0x0228` / `Grand Kai's Planet` | `0x080753f0` | `0x08294968` |
| 100 | `0x08f8c0` | `0x0317` | `0x022c` / `Hercule City` | `0x080782f4` | `0x0826ad50` |
| 225 | `0x091418` | `0x090f` | `0x024d` / `Thieves Den` | `0x0807f930` | `0x08216a18` |
| 338 | `0x092cd0` | `0x0e05` | `0x0236` / `Kyodai Pyramid` | `0x08087c40` | `0x081dad0c` |
| 451 | `0x094588` | `0x1601` | `0x022a` / `Heaven` | `0x0808e1e0` | `0x0817b1b0` |

Record 39 raw bytes are
`010b01040b0000000100000028020000fc550708805507080000000000000000000000000f00000000000000f0530708d053070800000000`.
The existing independent map-render evidence identifies only this selected
value (`0x08294968`) as a scene descriptor for map 39
(`docs/research/MAP_RENDER_FORMAT.md:33-34`).  That is representative support,
not a declaration that every selected word has that destination identity.

## Claim ledger

| External claim | project conclusion | classification | support |
| --- | --- | --- | --- |
| start `0x08e2e0` | exact candidate start | **CONFIRMED** | static executable/table literal, byte inspection |
| count `0x1c4` | fixed count 452 | **CONFIRMED** | static count helper, table-wide census |
| stride `0x38` | fixed stride `0x38` | **CONFIRMED** | static advance, table-wide byte offsets |
| `+0x00` is a BE map ID | BE u16 lookup key; semantic identity unproven | **PARTIALLY CONFIRMED** | static lookup, uniqueness census |
| `+0x0c` is a name/text index | low u16 resolves through text table; purpose unproven | **PARTIALLY CONFIRMED** | table-wide range/text resolution, verified text infrastructure |
| `+0x2c` starts pointer chain | aligned in-ROM indexed-word source | **CONFIRMED** | table-wide pointer validation, static consumer |
| `+0x2c -> target -> render structure` | selector 1 reads target `+0`; map 39 destination is independently scene-supported, general destination identity unproven | **PARTIALLY CONFIRMED** | static consumer; map-39 cross-reference; no runtime used here |
| all destinations are map render structures | not established | **UNRESOLVED** | no table-wide destination typing performed |

## Disagreements and open questions

LOGExtractor's UI calls the `+0x0c` result a map name and follows `+0x2c`
twice as a render chain.  This ticket retains only the byte-level resolution
and the selector-dependent indexed-word behaviour.  It does **not** accept its
semantic names, its masked pointer conversion, a sentinel rule, or a
table-wide render-structure identity.

Unresolved: the semantic meaning of the key bytes; a consumer proving what the
`+0x0c` index denotes; bounds/variant grammar of every `+0x2c` word array; and
which selected words are render descriptors versus other data.  Those last
questions are the precise input to LOGX-MAP-RENDER-001.
