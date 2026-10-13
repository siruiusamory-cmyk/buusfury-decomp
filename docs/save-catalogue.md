# The save catalogue

An index of every battery save and savestate on this machine, so that "which file
is which" is a query rather than four wrong guesses. It is a library plus a small
CLI under `tools/save_catalogue/`, and it is tracked code even though the store it
writes is not.

## The one command an owner needs

```powershell
python -m tools.save_catalogue register "<path to the save>" --note "what this is"
```

That copies the file into the owner inbox, records the note and the time, and
leaves the original untouched. Nothing is ever written back to a source.

To index the corpus, one call:

```powershell
python -m tools.save_catalogue scan
```

`scan` walks the roots it can derive (each `log1-*` checkout's `build\` beside
this repository, the emulator's own save and state directories from `config.ini`
and `qt.ini`, `Downloads`, and the protected backup directory), hashes each
candidate once, and indexes by `(path, size, mtime)` so a re-scan of an unchanged
tree re-hashes nothing. It still re-derives each entry's kind, geometry and
provenance from the file, so an entry is always what the tool would write today.
A root that does not exist is reported as `missing_roots`, never silently
skipped. `--root DIR` adds a root, repeatable; `--verify` re-hashes every indexed
source on purpose and reports drift without ever repairing it; `--rehash`
re-derives every file even where the fingerprint is unchanged, which is the one
case the fingerprint cannot see: a change to the tool's own reading rules.

## Where the store lives

`LOG1_SAVE_CATALOGUE_HOME` if it is set, otherwise `~/.dsh/work/saves` (outside
this repository, so no machine-specific path is tracked and no save byte is ever
committed).

| Path | What it holds |
| --- | --- |
| `index.db` | SQLite: `entries`, `sources`, `slots`, `runs`, `state_rom`, `roots` |
| `owner/` | the inbox of copies made by `register` |
| `log/register.jsonl` | append-only register log |

SQLite rather than one JSON document because `sqlite3` is standard library and
because registration is a one-row transaction, `find` and `diff` are indexed
queries instead of a full parse, and the whole file still dumps to JSON.

## The commands

Every command answers in one call and takes `--json`.

| Command | Question it answers |
| --- | --- |
| `scan [--root DIR] [--verify] [--rehash] [--protected DIR]` | index the roots; re-hash only what changed |
| `find [--game G] [--kind K] [--provenance P] [--valid-only] [--newest N] [--contains-slot K] [--path-contains TEXT]` | which entries match |
| `show <sha256\|path>` | one entry: sources, kind evidence, provenance evidence, per-slot facts |
| `which-rom <state>` | the ROM a state was staged with, from a recorded run |
| `diff <a> <b>` | slot-level comparison: counts and offsets only, never bytes |
| `verify` | re-hash indexed sources, report drift, repair nothing |
| `register <path> --note "..." [--force]` | copy into the owner inbox, keep the original |
| `record-run --run-dir DIR --tool ID --label L` | the one call a launcher makes |

`--contains-slot K` selects entries whose slot *K* passes its checksum, which is
the game's own test of whether a slot is kept. `find --valid-only` is the same
predicate over any slot.

`register` refuses a file the index has not seen (scan its root first, so the
entry carries a kind and a geometry) and refuses a known staged blank without
`--force`, because recording a tool's own scratch pattern as the owner's save
would be a false statement about a file no owner chose.

## What it will and will not claim

**Kind comes from the content, never the extension.** An mGBA savestate is a PNG
container carrying a private `gbAs` chunk: that chunk is what makes a `.ss*` a
state. A PNG *without* it is `kind=screenshot-png` with `misnamed=1` when the
extension says state, and it is never offered as a state to load. Anything else
with a state extension is `unknown-state`: no game and no ROM are attributed from
an unverified header.

**Battery validity is computed only where a geometry is proven, and per title.**
`tools/save_catalogue/geometry.py` holds that as a table, `GEOMETRIES`, one row
per title, each carrying its own evidence level, so a number verified against
real files and a number derived from code are never confused:

| Title | Medium | Slot *k* at | Payload | Integrity | Scope |
| --- | --- | --- | --- | --- | --- |
| Buu's Fury | 8,192 B | `0x10 + k*0x8B0` | `0x8A8` | `adler32`, stored at buffer `slot+0x8A8` (file `slot+0x8AC`) | verified against four real saves; stride and count code-verified |
| Legacy of Goku II | 8,192 B | `0x10 + k*0x168` | `0x164` | `adler32`, stored at `slot+0x164` | slot 0 verified against three real saves; stride and count derived from code |
| Legacy of Goku | 512 B | `0x08 + k*0xAC` | `0xA4` | the word at `slot+0x08` is a rolling XOR key over 168 bytes from `slot+0x0C` that reads no payload byte but the seed, so it cannot detect corruption | slot base `0x08` and the block reversal PROVEN BY ONE FILE (the owner's save of 2026-10-12: key `0xAAAAAAEB` matches `x1..x168` reversed, nothing in raw order); slot count `2` OWNER-REPORTED ("two slots and the second one is empty rn") and consistent with the file (slot 1 erased at `0x08 + 0xAC`); stride `0xAC` code-derived and consistent with the file; payload `0xA4` arithmetic from the layout, with the key's own span 168 bytes; validity `UNKNOWN` by design |

The verification counts in that table are from the seed measurements of 2026-10-12
and do not move; the live-corpus counts, dated where they appear, do.

The family shares the medium and the **8-byte-block byte reversal** (the medium
stores each 8-byte block byte-reversed relative to the game's buffer, so a block
is de-swizzled before the checksum is computed); it does not share the slot
layout. `transform_scope` records which titles the reversal is proven for, and the
reversal is applied only where the scope claims it. All three titles now claim it:
Legacy of Goku I's scope was `unknown` until the owner's 512-byte save of
2026-10-12 matched its key word under the reversal and under no other order.

Two coordinate frames matter for Buu's Fury and both are named in the code:
the game writes its checksum at **buffer** `slot+0x8A8`, and the file holds that
same word byte-reversed as the little-endian u32 at **file** `slot+0x8AC`. A
strict read of file `slot+0x8A8` is zero in every populated slot, which is what
makes the wrong offset look like an absent field.

Three facts are indexed apart, because they answer three questions:
`code_occupancy_bit` (the game's own "a slot record exists" bit, which is set on
an erased slot too), `checksum_ok` (`PASS`, `CORRUPT` or `UNKNOWN`; this is the
game's gate), and `erased_all_ff` (measured on this corpus). A slot that is not
erased and fails a checksum that covers the payload is `CORRUPT`.

The per-8-byte-block reversal is recorded as `transform_scope` on each entry and
is never applied to a title whose scope does not claim it.

**Provenance is a class plus the evidence that fired**, never a guess: `OWNER`
(registered, or a save beside a ROM in the emulator's own recent list whose mtime
is equal to or later than that image's), `TOOL-STAGED` (a known staged blank
digest), `DERIVED` (a run directory whose `inputs.json` names this file's digest
and label), `BACKUP` (a copy under a protected backup directory: its author is not
known, so it is not asserted `OWNER`), and `UNKNOWN` with the reason every rule
failed. A save older than the ROM copy beside it was not written by that copy, so
the mtime rule refuses it and the reason is recorded.

Not yet claimed, and recorded as such: which slot offset names the map the player
stands on, and any decoded field. The 8-byte settings header (`checksum(first 4)`
plus the word `0x12345678`) is read at image offset 0 in the medium's frame: the
header block is de-swizzled before the rule is applied, because the medium stores
every 8-byte block byte-reversed.

**Measured corpus figures, as of 2026-10-12, over the 1,026 held 8,192-byte
battery sources (34 distinct digests); the store is live, so these move.** Each
count is printed with the filter that produced it, from one query:

| Filter | Sources | Distinct digests |
| --- | --- | --- |
| held 8,192-byte sources | 1,026 | 34 |
| `header_written` true | 354 | 11 |
| of those, the SAVE's filename names Buu's Fury | 53 | 2 |
| of those, the SAVE's filename names no title | 301 | 9 |
| of those, the BYTES validate as Buu's Fury | 348 | 9 |
| of those, the BYTES validate as no other title | 6 | 2 |

A filename filter is a property of the path and a byte filter is a property of the
digest, so the two splits do not have to agree and here they do not: by filename
53 sources over 2 digests are titled and 301 over 9 are not; by the bytes 348 over
9 validate as Buu's Fury and 6 over 2 do not. Each row prints both counts from the
one query, and no row pairs a source count with a digest count from another filter.

The check agrees with `validate_rev8.py`'s own implementation (its header block
read out of its source and executed) with no disagreement on any held source. The
header payloads are `04040500`, `06060300` and `08000000`; an erased block
(`FF`/`00`) is not a written header in either implementation. `header_written` is a
reading of the file, never a claim about what the game intended, and the store's
`slots.header_written` column stays at 0 until the next real scan re-derives it:
that is a known state of a live store, not a defect.

Legacy of the check that measured the LoG I row: `build\savegeom\log1_save_check.py`
in the retro worktree read `slot 0 @0x10 + k*0xAC` and indexed the last payload byte
at `+179`, past the 172-byte stride, so it raised `IndexError` on its first slot and
never reached a verdict. The patched logic, applied there and recorded here because
that file is not tracked: a slot is skipped with its gap named when
`LAST_PAYLOAD_BYTE + 1 > STRIDE` or the slot runs past the image; the slot base is
`0x08`; and the whole image is additionally read as ONE slot at offset 0, both in
raw order and with every 8-byte block reversed. The verdict above comes from that
run: reversed order matches, raw order does not.

## Safety

* sources are opened read-only, and every write refuses a target inside a scanned
  root or over an indexed source;
* the index, the logs and every report contain hashes, sizes, mtimes, offsets,
  field names and notes only: never save bytes, never decoded text or art;
* an unattributable file is `UNKNOWN` with the evidence string saying why;
* `register` copies and leaves the original alone; `verify` only reports.

## The launcher call

`tools/runtime/mgba_session.ps1` defines `Register-SaveCatalogueRun`, and each
launcher that stages a save or a state calls it once after writing its
`inputs.json`. It records the tool id, the label and the ROM, save and state
hashes from that block. It cannot fail a launch: a missing interpreter or a
refused record prints one line and the session continues.

See also [`docs/testing.md`](testing.md) for the focused gate commands, and
[`tools/README.md`](../tools/README.md) for the format-to-reader index.
