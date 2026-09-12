# Regenerating the Buu's Fury structural atlas

Measured against canonical `buus_fury_usa_rev0_01c1707f`, sha256
`940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e`.

ROM-ATLAS-001 assembled ten evidence artifacts into one atlas, but only the
assembler (`tools/webfoot/atlas_build.py`) was tracked. The scripts that
*produced* those ten artifacts lived in session scratchpads and were never
committed, so the atlas could be queried but not rebuilt. This document records
the promoted producers, the one command that runs them, and what changed when
the chain was repaired.

## The command

```
python -m tools.webfoot atlas regenerate "roms/Dragon Ball Z - Buu's Fury (U).gba" --out build/atlas_fresh
```

`--out` must name an empty or absent directory; the command refuses to write
into one that already holds artifacts, so the historical `build/atlas/` cannot
be clobbered by accident. `--no-assemble` stops after the evidence artifacts;
otherwise `atlas.jsonl` and `atlas_conflicts.jsonl` are written too.

The ROM is opened read-only and its SHA-256 is checked before and after the run.
A full run takes roughly nine minutes, almost all of it in the compression probe
(a decode attempt every 4 bytes across 8 MiB).

## The producers

`tools/webfoot/atlas_producers/`: one module per recovered scratchpad script,
with the hardcoded `<checkout>` roots replaced by explicit `rom_path` /
`out_dir` parameters and every threshold, sort order and serialization detail
preserved.

| module | artifacts | ported from |
| --- | --- | --- |
| `seed.py` | `seed_knowledge.jsonl` | `build_seed.py` |
| `graphics_extents.py` | `graphics_extents.jsonl` | `gen_graphics_extents.py` |
| `scan.py` | the six `scan_*.jsonl` | `atlas_scan.py` |
| `code_functions.py` | `code_functions.jsonl`, `code_functions_wave4.jsonl`, `code_coverage_wave4.json` | `trace.py`, `wave4.py` |
| `regions.py` | `code_regions.jsonl` | replaces `regen.py` |
| `traversal.py` | (shared) | the shared `walk` body of `trace.py` / `wave4.py` |

`pipeline.py` runs them in the one canonical order, fixed by real data
dependencies:

```
seed -> graphics_extents -> scan -> code_functions(wave 2)
     -> code_functions(wave 4) -> regions -> atlas_build
```

`seed` reads repository documents only and no ROM bytes. `scan` needs the seed
rows for its `in_claimed_region` column. Wave 4's delta rule needs wave 2's
function set. `regions` needs both traversals' reach records.

## Two defects in the historical chain

### The pass selector: CONFIRMED, and harmless

`atlas_scan.py:23` gated its six passes behind
`ONLY = set((sys.argv[2] if ...).split(","))`, and the artifact mtimes prove it
ran in three separate partial invocations (entropy 09:15, compression 09:32, the
other four 09:47) whose argv was never recorded. The passes are mutually
independent. Each derives from the ROM bytes and the seed rows only, so the
promoted `scan.build` always runs all six.

**The six regenerated scan artifacts are byte-identical to the historical
ones.** Whatever the lost argv was, it covered every pass; this defect cost
nothing.

### The `code_regions` self-dependency: CONFIRMED, and it did cost something

`regen.py` read the existing `code_regions.jsonl` (`regen.py:19-21`), reused its
published extents as the wave-2 reach record, copied its `jump_table` rows
verbatim (`regen.py:104-106`), and then overwrote that same file
(`regen.py:121`). The artifact therefore depended on a now-lost earlier version
of itself. Its own docstring says the method was "reconstructed from the wave-2
artifact itself".

`regions.py` derives every row from upstream evidence instead: the ROM, the two
traversals' per-byte reach records and literal-pool word addresses, and jump
tables re-derived from ROM bytes by the surviving `trace.py:234-258` logic.

Both consequences are measured below.

## What the clean chain changed

Nine artifacts reproduce the historical outputs byte-identically. The seed
artifact differs only in two repository-policy-driven notes-string rewrites.
`code_regions.jsonl` differs because the clean producer chain recovers
traversal/literal-pool evidence unavailable to the historical self-referential
regeneration step.

Those are two unrelated kinds of difference and this audit keeps them apart: the
seed drift is prose only and changes no analysis, while the region drift is
substantive and moves 2,842 bytes of classification.

### The seed drift is intentional, and note-only

Each `seed_knowledge.jsonl` row carries a `notes` string. Two of the 51 rows used
a phrase the repository's pre-commit policy forbids in tracked code, so the
tracked producer says `Flagged for follow-up` instead.

| row identity | historical tail | tracked tail |
| --- | --- | --- |
| `script_vm.native_dispatch_table` | named an agent workflow role | `... Flagged for follow-up.` |
| `event_resource.record_pool` | named the same role, plus `rather than resolved` | `... Flagged for follow-up.` |

Measured, not assumed:

- Exactly 2 of 51 rows differ, in the `notes` field only.
- Comparing every row with `notes` excluded returns identical. No file offset,
  size, kind, identity, confidence, source or evidence field moved.
- `atlas_build.py` reads seed rows through `row["kind"]`, `row["confidence"]`,
  `row["file_offset"]`, `row["size"]` and `row["identity"]`
  (`atlas_build.py:203`, `:214-222`, `:355`). It never reads `notes`.
- The phrase occurs zero times in the generated `atlas.jsonl`.
- The final atlas digest is unchanged by the rewording.

So the seed artifact's own SHA-256 moves while nothing downstream of it does.

### The region drift is substantive

`code_regions.jsonl` is the only artifact that differs for analytical reasons,
and it differs in one direction.

| classification | historical | clean | delta |
| --- | --- | --- | --- |
| `code_reached` | 290 rows / 51,314 B | 286 rows / 53,816 B | **+2,502 B** |
| `literal_pool` | 164 rows / 2,028 B | 175 rows / 2,368 B | **+340 B** |
| `jump_table` | 2 rows / 1,184 B | 2 rows / 1,184 B | identical |
| `data_between_code` | 363 rows / 296,342 B | 313 rows / 292,988 B | **-3,354 B** |

**No byte lost a real classification.** Every historical `code_reached` byte is
still `code_reached` and every historical `literal_pool` byte is still
`literal_pool`. The 2,842 recovered bytes all came out of `data_between_code`,
which is the "reached span, but nothing reached it" bucket, so the repair turns
unexplained bytes into explained ones and never the reverse.

The clean file is **not** a strict superset, however: 354 bytes carry a
`data_between_code` row historically and no region row at all in the clean
output. Those are audited separately at the end of this document.

### Where the recovered bytes came from: CONFIRMED

The historical `literal_pool` set is **exactly** wave 2's pool words, byte for
byte. Wave 4's pools are absent from it entirely.

`regen.py:56-60` says so in its own words: wave 4 "published only aggregate
counts (102 words / 408 bytes raw, 324 bytes net after dedup ...), never the
word addresses. Without addresses the 324 net bytes cannot be placed, so only
wave 2's addressable pools are emitted as rows."

Running the wave-4 traversal rather than reading its published summary recovers
those addresses directly: 102 pool words, 408 bytes raw, **340 bytes net** after
dedup against wave 2. The 340 is the measured figure and supersedes the 324 the
wave-4 summary recorded.

The 2,502 recovered `code_reached` bytes are the same story one level up: wave
4's reached bytes outside wave 2's span, which `regen.py` could only approximate
from wave 4's published function extents.

### The jump tables were never at risk: CONFIRMED

`regen.py` copied both `jump_table` rows verbatim because it had no traversal to
derive them from. Re-deriving them from ROM bytes reproduces both exactly:
`0x55098` / 1,132 bytes / 283 entries, and `0x55508` / 52 bytes / 13 entries.
The copying was convenience, not necessity.

## The atlas digest

| stage | `atlas.jsonl` sha256 |
| --- | --- |
| historical ROM-ATLAS-001 artifact | `7c7087a88614ad8c97414599e3aa557cc8aa70d0529756318bbc21f49ee08ca9` |
| clean chain, pre-policy rewording | `8b6e440023eb61fdaf0e00a3ee205ebb83e62774273b29bedf021081c7533adb` |
| clean chain, tracked at ROM-ATLAS-001 closure | `8b6e440023eb61fdaf0e00a3ee205ebb83e62774273b29bedf021081c7533adb` |
| clean chain, tracked at TOOLKIT-038 closure | `5350ba1d8708564e6408fe8db1e532b897a6cf746198d6384b5f6e290d20553a` |
| clean chain, tracked at TEXT-INDEX-001 closure | `3121faa123cdf2745c386c679c39fa46de71c4e5b7ed5133a46e1e40ad89b7f1` |
| clean chain, tracked at the Latin-1 text reclassification | `030fe799db12b37f62ba87eefb14d0bb3f2e76791673f7cea2b00274b96e7d57` |
| clean chain, tracked at TEXT-HANDLE-001 closure | `e0bcf1b4a572401bd85a86e762c067ae2d9614fea58e9dc433388ea53352bd89` |
| **clean chain, measured at TEXT-HANDLE-002 closure (canonical)** | `5347bb720d59f80312520a38ee11d073a12a1b86e07c854117e657499fa38023` |

The first seven are retained as provenance baselines. **The eighth is what the
tracked tooling produces for the measured TEXT-HANDLE-002 evidence and is the
canonical atlas going forward.**

The second and third are the same value, which is itself a measured result: the
notes rewording changes `seed_knowledge.jsonl` but not one byte of the atlas,
because `notes` never reaches it.

The fourth differs from the third because TOOLKIT-038 added 18 seed rows for the
shop scenario arrays, their type-0x05 descriptors, five shop object records and
the scenario master index. That delta is **purely additive**: +18 rows, none
removed and none reclassified, so no earlier classification moved. See
[BUU_SHOP_SCENARIO_MODEL.md](BUU_SHOP_SCENARIO_MODEL.md).

The fifth differs from the fourth for a reason that is **not** a structural
change. TEXT-INDEX-001 changed no seed row, no classification, no coverage span
and no object: the atlas has the same rows it had, saying the same things about
the same bytes. Two things changed the generated bytes:

- `Observation.detail` for a `text-run-*` observation now carries the run's
  **full** decoded text. It previously carried a prefix truncated at 40
  characters, so a run longer than that could not be matched by its own text.
- The regeneration additionally writes `scan_decoded_text.jsonl`, the
  decoded-container text index, as a sibling artifact.

The digest therefore moved because text observations became richer, not because
anything was reclassified.

The sixth differs from the fifth for the same kind of reason, and again not a
structural one. Three halfwords that the decoded-container scanner classified as
control units are ordinary text: `0x00A0` (non-breaking space, seven
occurrences), `0x00E9` (`e` with acute, one occurrence) and `0x00EF` (`i` with
diaeresis, one occurrence). They are the only units in the seven containers
whose low byte exceeds `0x7E`, and every one of them sits mid-word, so treating
them as run boundaries split those words in half. They are now carried inside a
run. No seed row, no classification, no coverage span and no object changed, and
the true control units still end runs: the control census falls from 1,032 to
1,023, which is exactly the nine reclassified halfwords. Measured effect on the
decoded-text index: 688 runs / 195,328 characters becomes 681 runs / 195,342
characters, because nine boundaries disappear and the fragments they separated
merge.

The seventh differs from the sixth because TEXT-HANDLE-001 added five seed rows
and extended a sixth, and unlike the two preceding moves this one **is** a
structural change: the atlas now carries objects it did not have. The added rows
are the two handle consumers `0x08012230` and `0x080122B4`, the ROM-resident
dialog record `0x08781CF8` that owns the packed compressed-text handle, the
handle word itself at `0x08781CFC`, and container 0's selector evidence; the
extended row is `compressed_text.pointer_table`, whose table role moved from
`OBSERVED` to `CONFIRMED` on the consumer's own indexed load. The delta is
additive: no existing row was removed and no classification moved, and the only
coverage change is the 4 bytes at `0x781CFC`, which the handle row now owns at
`RUNTIME_CONFIRMED` inside the enclosing record pool. See
[BUU_EVENT_RESOURCE.md](BUU_EVENT_RESOURCE.md).

The eighth differs from the seventh because TEXT-HANDLE-002 adds the executed
byte-`0x05` dispatch loop and its selected handler thunk as seed objects. The
new evidence corrects the apparent `0xNN05` opcode family boundary: only record
byte `+0x02` selects this handler; byte `+0x03` is a downstream parameter. The
change is additive and does not reclassify existing coverage. See
[BUU_DIALOG_RUNTIME.md](BUU_DIALOG_RUNTIME.md#executable-compressed-text-dispatch).

Note that a seed row's `evidence` and `source` do reach `atlas.jsonl` even though
its `notes` does not, so the note-only invariant recorded above for the second
and third digests is specific to `notes` and does not generalise.

Regenerating the measured producer state via the documented command reproduces
`5347bb72...`; two consecutive clean runs into separate empty directories
produced byte-identical output across every artifact, so determinism holds.
`build/atlas/` still holds the previous `030fe799...` output and is stale
against this row until it is regenerated; `build/atlas_v2a/` is retained as the
pre-TOOLKIT-038 `8b6e4400...` comparison oracle.

### The decoded-container index is gated, deliberately

`scan_decoded_text.jsonl` indexes **only** the seven containers reachable from
the seeded `compressed_text.pointer_table` at `0x7B5B64`: 681 runs, 195,342
characters. It does not index the blind compression probe, whose 24,285 hits
decode and round-trip into roughly 68.7 MiB of output.

> Compression validity is necessary but not sufficient for text-container
> membership. Decoded-text indexing is restricted to structurally supported
> reachable containers to avoid indexing compression-probe noise.

Widening the gate would find more text, and nearly all of it would be decode
noise presented as a text source. The gate is a safety property, not a tuning
parameter.

| artifact | sha256 |
| --- | --- |
| `seed_knowledge.jsonl`, historical | `0a54c87d1f3c410a...` |
| `seed_knowledge.jsonl`, tracked | `bfa8ed22d4d22299959f7d4be134e8b06171db1efe1054a40093b069a15810b8` |

**The historical atlas digest is not reproducible, and the clean one is
correct.** The difference is entirely attributable to the 2,842 bytes `regen.py`
could not place, all of which move from `data_between_code` to a real
classification, plus the 354 bytes audited below. No threshold, ordering or
tie-break was changed to influence any of it.

Two consecutive full clean runs into separate empty directories produce
byte-identical output across every file, so the tracked pipeline reproduces its
own digest exactly.

The canonical claim is therefore: **the atlas is reproducible from the canonical
ROM using tracked tooling; historical outputs are retained as comparison
baselines, with all measured differences explicitly audited.**

## Status of the claims here

- `CONFIRMED`: nine artifacts reproduce byte-identically; the jump tables
  re-derive exactly; the historical `literal_pool` equals wave 2's pools exactly;
  wave 4 resolves 102 pool words / 340 net bytes; the function counts are
  628 + 66 = 694; the seed drift is confined to two `notes` strings and reaches
  nothing downstream; two clean runs agree byte for byte.
- `INFERRED`: that the lost `atlas_scan.py` argv covered all six passes. The
  artifacts match, which is strong evidence, but the argv itself is gone.
- `UNKNOWN`: whether the historical run had any step not represented by a
  recovered script. Nine artifacts matching exactly, and the tenth differing only
  where the clean chain has strictly better evidence, says probably not.

## The 354 bytes that leave `code_regions.jsonl`

The clean chain is not a strict superset of the historical region file. Alongside
the 2,842 reclassified bytes, 354 bytes spread over 49 extents carry a
`data_between_code` row historically and carry no region row at all in the clean
output. Every one was audited.

**48 extents of exactly 2 bytes.** Each reads `0x0000` in the ROM and each sits
between the end of a `code_reached` run and the start of the next span, for
example `0x000B72` between code ending at `0xB72` and a literal pool starting at
`0xB74`, or `0x0502AA` and `0x0502BA` between two `code_reached` runs. These are
the halfword alignment gaps a Thumb function leaves before a word-aligned
literal pool. `regen.py` carved holes out of the reached span and labelled every
hole `data_between_code` regardless of width; the clean producer does not emit a
row for a gap this small.

**One extent of 258 bytes at `0x055646..0x055748`.** It is the trailing hole
inside the reached span, immediately after code ends at `0x055646` and before the
final `literal_pool` at `0x055748`, which is the end of the reached span in both
files (`0x05574C`). Its bytes are high-entropy with no discernible structure
(`62f2 9825 4665 2f4f 5d05 4abd ...`). It falls inside the
`0x55098..0x55646` cluster tracked as its own ticket.

Both cases are the same carve/boundary effect, not a gap in the atlas. Layer A
coverage still tiles all 8,388,608 bytes with zero gaps across 7,833 spans; these
bytes simply fall through to the scan-derived claims rather than carrying a
region row. `0x055646` is covered as `UNKNOWN` at `OBSERVED` in the fresh atlas.

That is the more honest outcome. `data_between_code` asserts "inside the reached
code span but never reached by traversal", which is a claim about code; two zero
bytes of alignment padding and an unexamined 258-byte hole do not earn it. The
rows were not restored, because restoring them would have been tuning toward the
historical hash rather than correcting an error.
