# Legacy of Goku II String Table Format

Profile `legacy_of_goku_ii_usa_rev0_204142e1`, SHA-256
`6e6c370c339ec9171cb1956adf837a0d342a197f78964882ef46c3086656ff75`.

Evidence labels follow `docs/DEVELOPMENT.md`. Every `CONFIRMED_ROM` claim below was
established by reading the canonical image directly and is reproduced by the
tests named in each section - not taken on an upstream project's word.

**Scope warning, stated first because the name invites the wrong assumption.**
This document describes the game's **menu, item, quest and map-name string
table**. It is *not* the dialogue system. Legacy of Goku II's dialogue is a
separate, script-interleaved and partly compressed structure that this ticket
did not decode; see [Dialogue is a different problem](#dialogue-is-a-different-problem).

## ROM identity

`CONFIRMED_ROM`, measured locally, and corroborated independently.

| Field | Value |
|-------|-------|
| Title / game code | `DBZLGCYGOKU2` / `ALFE` (header `0xA0`) |
| Region / revision | USA / 0 |
| Size | 8,388,608 bytes |
| CRC32 | `204142e1` |
| MD5 | `4e1565aa1f0627c2bf5e51019440cb70` |
| SHA-1 | `18e0715dec419f3501c301511530d2edcd590f8b` |
| SHA-256 | `6e6c370c339ec9171cb1956adf837a0d342a197f78964882ef46c3086656ff75` |

`UPSTREAM_FACT`: the same size, game code, revision, CRC32, MD5 and SHA-1 are
recorded in `mstan/DragonBallZLegacyofGokuIIRecomp`
(pinned `add98b5d76fb2b822be870f29fa27b22c9a95631`) in both `baserom.md` and
`game.toml`. The profile was already in `config/roms.yaml` from that source
before this ticket; TOOLKIT-005 re-measured the local image and confirmed every
field matches. Two independent statements of one identity, agreeing.

Every other revision fails closed. No Europe revision was targeted, and no LOG1
work was performed.

## Upstream audit, performed first

Per the ticket's ordering, existing knowledge was audited before any new
analysis of the binary.

`Arefu/Legacy` (pinned `d22a556cd33dee56513d5b606b6ae8065ccc5752`) is the only
upstream with Legacy of Goku II text knowledge. What it actually contains:

- `DBZKit/Legacy/Dependencies/DBZLOG2/ALFE.json`, in full:
  `{"gameCode": "ALFE", "mapEntries": "0x08409368"}`. One address. Its config
  schema (`DrGero/Config.cs`) declares fields named `MapNameTableOffset`,
  `DefaultCharStats` and `DefaultExpThresholds`, but **the shipped JSON
  populates none of them** - they are empty slots, not findings.
- `Bulma/DBZLOG2.cs`: reads map entries, and resolves a map name by indexing
  `MapNameTableOffset` and reading a **null-terminated** string. It guards with
  `if (nameIndex > 0x0000FFFF) return string.Empty; // likely a pointer, not an
  index`, which is upstream acknowledging its own map record is a variant type.
- `DBZKit/Assets/Dialog.cs`: a dialogue parser, discussed below. Not this table.
- `DBZKit/JCALG1.cs` and `ROM Code/String_DASM.asm`: the compression side,
  discussed below. Not this table.

`UPSTREAM_FACT`, and the entirety of what upstream establishes about this
structure: a table of pointers to **null-terminated** strings exists and is used
for map names, reached through a config field upstream never fills in.

Upstream supplies **no address, no count, no extent, no encoding statement and
no codec** for this table. `DragonByteZ` and the recomp projects carry map,
graphics, audio and compression knowledge and no string-table knowledge.

Everything below is this project's own work.

Note on terminology, per the ticket's instruction not to silently promote
upstream words: upstream calls its unfilled field `MapNameTableOffset`. Map names
are only the **tail** of what this table holds - it also carries menu labels,
item names, quest text and technique descriptions - so this project calls it the
string table and does not adopt the narrower upstream name.

## Table extent

`CONFIRMED_ROM`.

| Property | Value |
|----------|-------|
| Pointer table | file `0x000E2840`, GBA `0x080E2840` |
| Entries | 260 |
| Entry width | 4 bytes, little-endian GBA address |
| Table size | `0x410` bytes, ending at `0x000E2C50` |

Both boundaries are sharp, which is what makes the extent a measurement rather
than a choice:

- The word immediately **before** the run is `0x48900000`, which is not a GBA
  ROM address, so the run cannot start earlier.
- The run's last entry ends at exactly `0x000E2C50`, which is the pool's first
  byte, so the run cannot continue.

**A correction worth recording.** This table was first measured at
`0x080E28EC` with 217 entries, by scanning forward for a run of pointers that
dereference to ASCII and taking the first long run found. That start was 43
entries **into** the table: a forward-only scan cannot distinguish a table's
start from its middle. Walking backwards from the first hit while the words
remained pool-range pointers found the true base. The 43 missed entries are
exactly the ones reaching the strings that the truncated reading appeared to
leave unreferenced - so the "unreferenced strings" that reading produced were an
artefact of the wrong base, not a property of the game. Any future table located
by scanning must be walked backwards before its extent is declared.

## String pool extent

`CONFIRMED_ROM`.

| Property | Value |
|----------|-------|
| Pool | file `0x000E2C50` .. `0x000E4090` |
| Size | 5,184 bytes |
| Strings | 246 |

The pool begins immediately where the pointer table ends, with zero bytes
between them.

## Encoding

`CONFIRMED_ROM`. The pool is **8-bit ASCII**, one byte per character, terminated
by the byte `0x00`. Strings are packed contiguously with no padding or alignment
between them; `alignment: 1` in the profile records that.

A census over all 246 strings finds 71 distinct byte values, spanning `0x0A` to
`0x7A`. Every one is printable ASCII except a single `0x0A`, which is a real
newline inside the label `No\nPortrait\nData`. **There are no control codes and
no escape grammar** - the contrast with Buu's Fury, whose UTF-16LE pool carries a
`0x0008`-prefixed control grammar, is the reason these are two codecs rather than
one parameterised reader.

`INFERENCE`: six strings contain `printf`-style specifiers - `%d` and `%s` only -
so the game substitutes values into them at display time. The bytes are preserved
verbatim and never interpreted; this document does not claim to know any
specifier's argument.

Longest string: 190 bytes (a technique description). No string is empty, unlike
Buu's Fury, where 11 of 1,534 are.

## Pointer and reference structure

`CONFIRMED_ROM`.

- **260 slots resolve to 246 distinct targets.** Nine strings are shared, taking
  14 extra slots between them. `Find the seven Dragon Balls` is reached from
  seven separate slots; `***`, `Golden Cap.`, `Scouter Part`, `Kamehameha` and
  four others from two each.
- Because of that aliasing, **pointers are neither unique nor strictly
  ascending**. Buu's Fury's table is both, and its codec may rely on it. This one
  may not.
- **Every table target is a string start, and every string has a slot.** Both
  directions were checked. Neither alone is sufficient: a slot could point
  mid-string and still decode, and a string could exist that nothing reaches.
- Inbound word-aligned references to the **pool base**: 2, at `0x000E2840` and
  `0x000E2BB4`. The first of those is this table's own first entry.
- Inbound word-aligned references to the **table base**: 0. The table is reached
  through a computed address, so its base cannot be relocated by rewriting a
  reference list - the same conclusion Buu's Fury reached for a different reason
  (there, 51 references exist and would all need rewriting).

## Exhaustive round-trip evidence

`CONFIRMED_ROM`. The ship gate for the capability ladder's ROUND_TRIP rung is
byte-identical `parse -> serialize` over the **whole extent**, not a sample.

- The pool's 5,184 bytes are tiled exhaustively by the 246 strings: each ends
  exactly where the next begins, the first starts at the pool base, and the last
  ends at the pool end. No gap, no overlap, no byte outside a string.
- All 246 strings re-encode to their original bytes. Concatenating every
  re-encoded string reproduces `rom[0x000E2C50:0x000E4090]` exactly.
- Enumeration walks the **pool**, then looks each string's slot up, rather than
  following the table. Following an aliasing table would visit 246 strings in an
  order that proves nothing about coverage; walking the extent proves coverage
  directly. A pool string reached by no slot is refused rather than represented,
  because it would have no durable identity.

Identity is the **pointer-table index**, never the address. An address is where a
string sits right now.

## Whole-ROM no-op rebuild

`CONFIRMED_ROM`. Extract the verified ROM to a project, build it unchanged:

```
input  SHA-256  6e6c370c339ec9171cb1956adf837a0d342a197f78964882ef46c3086656ff75
output SHA-256  6e6c370c339ec9171cb1956adf837a0d342a197f78964882ef46c3086656ff75
```

All 8,388,608 bytes reproduce, including every region this toolkit cannot
decode. Validation reports 246 strings, 0 enemy records, 0 character records and
0 problems.

## Semantic edit proof

`CONFIRMED_ROM`. One edit, authored as a semantic value in project source:

```
text:0259   "Yunzabit Heights"  ->  "Yunzabit Wastes"
```

| Property | Result |
|----------|--------|
| Output SHA-256 | `0028cbabb2333d84facd4527b368a4d1c0577cd54d66b842fd3b41cbf8633de3` |
| Bytes changed | exactly 7 |
| Range | `0x000E4088` .. `0x000E408E`, contiguous |
| Before | `Yunzabit Heights\x00` |
| After | `Yunzabit Wastes\x00\x00` |
| Provenance | owner `text:0259`, reason `text edit`, record at `0x000E407F (+17)` |
| Repeated build | byte-identical |
| Base ROM | unchanged, `6e6c370c...` |

The changed offsets are exactly those the write manifest names. The replacement
is one byte shorter than the original and is deterministically zero-padded to its
17-byte allocation rather than the pool being repacked - repacking would move
every later string and rewrite the pointers to reclaim one byte.

## Over-length behaviour

`CONFIRMED_ROM`. Because the pool is exhaustively tiled, no string has slack to
grow into. `"Yunzabit Highland"` against the same 17-byte allocation is refused
**before anything is written**, with the exact deficit:

```
text:0259: encoded text needs 18 bytes but its allocation is 17;
1 bytes too long. Growing a string requires relocation, and this
profile declares no verified free space.
```

Growing a string requires relocation, which requires profile-declared free space.
This profile declares none - `free_regions` is empty, and free space is never
inferred by scanning for runs of a fill byte, because a scan cannot distinguish
padding from data and gives different answers on an already-edited image.

## Dialogue is a different problem

`UPSTREAM_FACT`, recorded so a later reader does not mistake this table for the
game's dialogue and does not re-derive why dialogue was out of scope.

`Arefu/Legacy`'s `DBZKit/Assets/Dialog.cs` describes a dialogue stream whose
entries carry a `u16` index and a `u8` mode byte, with six modes:

| Mode | Name | Upstream status |
|------|------|-----------------|
| `0x0` | `DIALOG_SCRIPT` | bytecode, walked opcode-by-opcode |
| `0x1` | `DIALOG_TEXT` | charmap text |
| `0x2` | `DIALOG_TEXT_JCALG1` | `"[JCALG1 - TODO decompress]"`, `"JCALG1 length unknown"` |
| `0x3` | `DIALOG_TEXT_INTERPOLATE` | format pointer + script data + text |
| `0x4` | `DIALOG_TEXT_JCALG1_INTERPOLATE` | `"[JCALG1_INTERPOLATE - TODO]"` |
| `0x5` | `DIALOG_JUMP` | jump target |

Two independent reasons this cannot reach ROUND_TRIP without work the ticket
forbids:

1. **Compression.** Two of the six modes are JCALG1-compressed and upstream marks
   both undecompressed and of unknown length. The decompressor exists in the ROM
   at `0x87FD6BC` and is reproduced in `Arefu/Legacy`'s
   `ROM Code/String_DASM.asm` - an ARM bit-stream LZ routine copied to
   `0x03000000`, with back-references (`ldrb r8,[r0,-r12]`). Reimplementing it is
   real work and was not attempted.
2. **Enumeration requires a script VM.** Entries are variable-length and
   interleaved with bytecode, so finding entry *n+1* means walking entry *n*'s
   opcodes. Upstream's own operand sizes carry `// TODO: confirm operand size
   (guessing 1 byte)` on the jump opcodes. An enumeration built on guessed
   operand widths cannot support a byte-exact round trip.

TOOLKIT-005 forbids script-VM work. Dialogue therefore stays at **DISCOVERED**,
and the profile declares nothing for it rather than declaring it approximately.

## What remains UNKNOWN

- `UNKNOWN`: what consumes each string. The table base has no direct inbound
  references, so the index-to-consumer mapping is unresolved. This mirrors the
  same open question on Buu's Fury and is not needed for the round trip.
- `UNKNOWN`: whether a further string table exists elsewhere in the image. This
  table is complete and self-consistent, but no exhaustive search of the ROM for
  other ASCII pointer tables was performed - the one scan that ran looked for
  tables whose entries dereference to ASCII and found this one.
- `UNKNOWN`: the runtime argument of every `%d` and `%s`.
- `UNKNOWN`: LOGII stat table structure and location. A structural scanner that
  correctly locates Buu's Fury's enemy table at `0x00711274` finds **zero**
  matches anywhere in the LOGII image. The correct conclusion is that the Buu
  record shape is **not transferable** - not that LOGII lacks stat tables.
- `UNKNOWN`: LOGII map record semantics. A real 0x38-stride table of 327 records
  exists at GBA `0x08409368`, with a sharp end where IWRAM pointers begin, but
  only 260 of 327 records carry small values in both the name-index and music
  slots; the rest hold ROM pointers there. The record is a variant type. No
  semantic layout is claimed and `map_entries` is not declared.
- `UNKNOWN`: whether `free_regions` could ever be non-empty for this profile. No
  verified free region was found, and none was invented.

## Provenance sources

- Canonical local image, SHA-256 `6e6c370c...`, read directly. Never modified.
- `mstan/DragonBallZLegacyofGokuIIRecomp` @ `add98b5d76fb2b822be870f29fa27b22c9a95631`
  - `baserom.md`, `game.toml`: ROM identity only.
- `Arefu/Legacy` @ `d22a556cd33dee56513d5b606b6ae8065ccc5752`
  - `DBZKit/Legacy/Dependencies/DBZLOG2/ALFE.json`: map-entries address.
  - `DBZKit/Bulma/DBZLOG2.cs`: null-terminated map-name strings via a pointer
    table; the variant-record guard.
  - `DBZKit/Assets/Dialog.cs`: dialogue mode enum and its TODOs.
  - `ROM Code/String_DASM.asm`, `DBZKit/JCALG1.cs`: the compression routine.
  - Used as **research reference only**. No upstream code was copied; every fact
    used here was re-derived against the canonical image.
