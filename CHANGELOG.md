# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Changed

- The eight images under `assets/` are no longer tracked: `extract.cmd` decodes each one from the
  user's own ROM into an ignored payload, and `rebuild.cmd` re-encodes it with grit and the
  compressor to the exact bytes the assembly includes.
- The project is named a disassembly, not a decompilation, in `README.md` and `.recomp.json`:
  the code is assembly with address-named symbols, and the README says so before the progress
  figure.

### Added

- `tools/recomp/export_inputs.py` bounds a proven entry whose flow returns by that extent, and starts a
  row at the byte after a row's return or padding when no row starts there, so the recompiler's inputs
  reach code that had no block before.
- `tools/research/coverage_gap.py` classifies the addresses a play trace reaches that no translated
  block covers.
- `tools/research/test_tracked_checks.py` also runs `tools/research/endrom_index_census.py
  --check`, so the end-of-ROM index census fails the suite when its page drifts from the run and
  row-hit tables.
- `tools/research/test_tracked_checks.py` runs the `--check` of every generator that carries a
  tracked census, table or assembly fragment, one case per tool, so a stale document fails the
  suite.

- `docs/research/UNKNOWN_CENSUS.csv` and `docs/research/UNKNOWN_CENSUS.md` are re-derived: the
  `unknown` class is 2,306 rows / 476,899 B of the 3,128 raw rows / 494,250 B the assembler still
  carries.

- `tools/research/row_readers.py` keeps the verdict section `tools/research/region_readers.py`
  appends to `docs/research/R32_NULL_CENSUS.md`, defers the `code-without-entry` rows to
  `docs/research/CODE_FRAGMENT_NULL_CENSUS.md`, and the re-derived census carries 4,346 walked
  bodies and 1,631 converted ones.

- `docs/research/ENDROM_INDEX_CENSUS.md`, generated and checked by
  `tools/research/endrom_index_census.py`, states how far the read watch reached into the three
  end-of-ROM arrays whose stride no instruction bounds: one of 102 map runs read the 60-byte row at
  `0x72D6B8` and reached index 2 of its 268 whole records, and no run read a byte of `0x762270` or
  `0x77B2A8`. An observed index is a lower bound, so all three rows stay raw-data;
  `docs/research/OTHERS_FOUND_TRIAGE.md` states their steps as `null` and `blocked`, and the plan
  falls from 55,988 B to 0.
- `docs/research/OPCODE_STREAM_CENSUS.md` gives the opcode table the interpreter at `0x08004038`
  dispatches through: 31 handlers, each with the retail halfwords of its operand read, and the null
  `0x11` entry that ends a stream. `tools/research/opcode_stream.py` decodes the 132 rows the
  `MapEntry` `+0x30` field names: 34 rows / 1,004 B are consumed to the row's last byte and end on
  `0x11`, and each is re-emitted byte-exact from the decode into `build\opcode\gen_<start>_<end>.bin`
  by the build-time generator; 98 rows / 13,853 B keep a measured stop point in
  `docs/research/R19_NULL_CENSUS.md`. `docs/research/ENDROM_BOUND_CENSUS.md` records that the
  `0x0800B57E` reader copies its row's own bytes to VRAM through `0x08049138` and decodes none of
  them. The index, the triage, the raw remainder and the ledger are re-derived: 3,128 rows /
  494,250 B, and the triage's class 1,071 rows / 334,140 B with 55,988 B of plan.
- `docs/research/OTHERS_FOUND_TRIAGE.md` breaks the index's `others found` class down by citation
  kind, region, row and reader address, and states the measured next step of every group of 4 KiB
  or more: 1,105 rows / 335,144 B in 845 groups, 17 of them at or above 4 KiB, and the steps that
  would move bytes come to 70,845 B. `tools/research/others_found_triage.py --check` re-derives the
  page, refuses a group with no next step or a next step for a group under 4 KiB, and asserts the
  class against `tools/research/residual_index.py` and the gate's cited and runtime-cited counts.
  The index's `pending-image-route` description states what the image route leaves: a row that
  holds no frame, a frame that crosses a carrier token, a refused row, or the carve-out.
- `docs/research/RESIDUAL_INDEX.md` joins every raw row to the census line that gives its
  verdict: 3,287 rows / 579,162 B in four classes and 26,112 B of identity copies, per class and
  region, each with the document that carries it. `tools/research/residual_index.py --check`
  re-derives the table and refuses a row with no verdict line or with one in two documents;
  `docs/research/ROUTE_TO_100.md` names the join.

### Changed

- The text table record is derived again from the merged census: the 34 opcode rows that became
  source are `unknown` there, so `docs/research/TEXT_TABLES.csv` keeps all 713 rows, their line
  values and 13,788 B.
- `docs/research/TEXT_TABLES.csv` is regenerated: 264 of its 713 rows carried a `line` value from 1
  to 669 lines behind the census it copies, and `tools/research/text_tables.py --check` now compares
  every column `--write` emits, the page included, so a stale line fails it.
- `docs/research/RUNTIME_READ_RUNS.csv`, `docs/research/RUNTIME_READ_CITATIONS.csv`,
  `docs/research/RUNTIME_READ_ROW_HITS.csv` and the page `docs/research/RUNTIME_READ_RESULTS.md`
  carry the read watch's 102 map runs over the three end-of-ROM rows: 170 runs and 801 citations,
  each run with its log digest and liveness count, and each reading run with the highest offset it
  read inside its row.
- `tools/runtime/recomp_read_sweep.py` records the highest offset it read inside each watched row
  (`max_address` in its `row-hits.csv`), so a watched read can name the record of a strided array
  the game used instead of only the number of hits.
- The runtime read survey's citations and campaign figures are unchanged, and the work-unit tag is
  gone from the six `asm/rawlabeled_*.s` carriers, `docs/research/TEXT_TABLES.md`,
  `docs/research/PLAY_CHECKLIST.md`, `docs/research/RUNTIME_READ_PLAN.md` and the citation comment
  `tools/research/recomp_cited.py` writes.
- The public tree names no local path and no read-logging build: `docs/research/PLAY_CHECKLIST.md`
  describes its instrument as a read-logging GBA runtime with a range file, without its run blocks,
  environment names or instrument source citations; `docs/research/RUNTIME_READ_PLAN.md`,
  `docs/research/RUNTIME_READ_RESULTS.md` (regenerated by its generator),
  `docs/research/RUNTIME_READ_RUNS.csv`, `docs/research/SLICE_RESIDUE_ROWS.md`, `INSTALL.md` and
  `rebuild.cmd` follow, and `tools/runtime/recomp_read_sweep.py` takes its binary and DLL directory
  from `READ_LOG_EXE` and `READ_LOG_PATH_PREFIX`; every measured figure is unchanged.
- `docs/research/PLAY_CHECKLIST.md` names the IWRAM routine its read alarm caught at `0x03000068`
  as what it is: the JCALG1 decoder entered at `0x03000040`, 166 ARM instructions, so the animation
  frame payload it reads is decoded and then copied.
- `docs/research/OTHER_COMPRESSED.md` re-derived by its generator: the decoder's line citations
  are `asm/rest_of_the_game.s:14391` (bit reader `:14556`, end code `:14575`), where the stale
  12,830 / 12,995 / 13,014 pointed at a line that had moved.
- The map block's frame payloads are a compressed stream the JCALG1 decoder at `0x03000040`
  expands, not bytes copied verbatim: `docs/research/MAP_BLOCK_NULL_CENSUS.md`,
  `tools/mapcontainer/animrow.py` and the index say so, and the index's `pending-image-route`
  description reads `compressed frame stream pending an image route as source`. Verdict classes are
  unchanged. The documents the BF-504 branch writes keep master's text until that branch lands its
  own decoder wording: `MAP_BLOCK_LAYOUTS.md`, `R33_R35_NULL_CENSUS.md`, `REGION_READ_CENSUS.md`
  and `tools/research/region_readers.py`. One writer per file.
- `tools/research/test_residual_index.py` doctors a row so the index's two refusals fail on the
  row they name, not on the byte total.
- `tools/research/residual_index.py` spells the lookup of a row's census document `carrier_of`,
  matching the column's own wording.
- The 11 `code-without-entry` rows leave the `R32` and `R00` per-row nulls:
  `docs/research/CODE_FRAGMENT_NULL_CENSUS.md` is the class's own census, and both region
  documents name where those rows' null is; `tools/research/region_readers.py` names the class
  rows its read verdict no longer carries. The map census's header renders `map_anim_row` with
  its own markup again.
- `docs/research/MAP_BLOCK_NULL_CENSUS.md` carries the 27 `in progress` rows of `R02` and
  `R12`-`R15` as its per-row null, and the other 147 rows' map evidence without a second verdict
  because `R33`-`R35`'s census carries their lines; `docs/research/R02_NULL_CENSUS.md` covers the
  region's 85 rows outside the block.
- `docs/research/R02_NULL_CENSUS.md` is new: the region's 90 raw rows / 34,132 B, each with the
  run-time `(pc, address)` pairs its carrier comment records and the null a read leaves, since a
  read states no field and no extent; `tools/research/residual_verdicts.py --r02` derives it.
- `docs/research/R19_NULL_CENSUS.md` carries the region's 17 remaining raw rows / 200 B in its
  per-row null, with their bytes, entropy, zero share and in-image words;
  `tools/research/residual_verdicts.py --r19` derives that section.
- `docs/research/CODE_FRAGMENT_NULL_CENSUS.md` re-measured: the 11 remaining `code-without-entry` rows / 20 B carry 12 branch entry sites, no naming word, no decoded literal load and no read in the 452-map sweep, `tools/research/thumb_body_convert.py` refuses all 11 (9 rows cross the row end, 2 are not an ARMv4T Thumb instruction), and the whole instruction is not a span the tree carries as one INCBIN row; 454 B of the class's 502 B are already source and the other 28 B are class `unknown`.
- `docs/research/MAP_BLOCK_LAYOUTS.md` names the animation frame's IWRAM target at file
  `0x049128` (bus `0x08049128`), not `0x009D28`: the word at file `0x009D28` is
  `0xb9488c46`, and the `0x08049120` veneer's `ldr pc,[pc,#-4]` reads `0x03000040` from
  file `0x049128`.
- The end-of-ROM facing-vector table at 0x7594F0 is generated source: four 8-byte pairs
  bounded by the sprite-descriptor table's own four records.
- The public repository is one import commit of the development tree. Local history and
  untracked build inputs are not published, and tracked prose names the change instead of
  citing a local commit SHA.
- Tracked prose describes work units as tickets.
- `tools/check_links.py` checks that every relative markdown link resolves and refuses a
  commit-SHA citation; the pre-commit hook and CI run it beside the lint and the tests.
- The ARM body classifier reads its base rows from a tracked fixture, so no test needs
  repository history.
- Asset-directory PCM: `tools/mapcontainer/audiodir.py` ties both 12-byte directories to the engine's sample and music tables and `assetdirectory.block_blob` emits each run from its decoded stream at build time. The music slot engine reads a music record's `+8` at `0x0803E542`, indexes the 79-record table by `12 * byte`, and stores the record at `slot+0x28`; source 7,432,058 -> 7,775,068 B and identity copies 369,122 -> 26,112 B.

### Added

- The 16-byte method records five readers state a field set for (68 records / 1,088 B, 976 B net of overlap) are source through `tools/structured/families.py`: `0x0800A7C2` reads `ldr r1,[r5,#4]`, `0x0800A7CC`/`0x0800A7CE`/`0x0800A7D0`/`0x0800A7D2` read `ldrh` at `+8`, `+0xa`, `+0xc` and `+0xe`, the record's first word is `0x0800A7A1` (the Thumb constructor at `0x0800A7A0`) in every one of them and its second is `0x40` or `0x80`, the signature's hits run 44 B apart, and 42 of the 68 were read by the 452-map sweep; `docs/research/R19_NULL_CENSUS.md` carries the row bases derived from the read offsets and the reasons the other two reader sets stay raw. Source 7,778,826 -> 7,779,802 B, raw-data 583,670 -> 582,694 B.
- The 12-byte child definitions a placement record's pointer array names (80 records / 960 B, 736 B net of overlap) are source through `tools/structured/families.py`: a child's first word is a Thumb code pointer, the parent record's count at `+0x18` bounds its child array, the constructor at `0x08039DBC` copies the child's `+4`, `+6` and `+8` halfwords into a `0x1C`-byte instance, and the descriptor's child pointers step 12 B; source 7,778,090 -> 7,778,826 B, raw-data 584,406 -> 583,670 B.
- The map block's animation rows are source: a map root's `+0x0C`/`+0x10` list names rows whose `+0` frame count, `+1` VRAM units, `+2` VRAM slot and `+4` frame pointers are read at `0x08009BC2`, `0x08009B32`, `0x08009B34`, `0x08009B26` and `0x08009D02`, and `tools/mapcontainer/animrow.py` emits 122 rows / 3,500 B as `map_anim_row` tables with the layout in `docs/research/MAP_BLOCK_LAYOUTS.md`; source 7,777,706 -> 7,781,206 B, raw-data 584,790 -> 581,290 B.
- Every one of the map block's 174 still-raw rows (86,736 B) has a per-row measured null in `docs/research/MAP_BLOCK_NULL_CENSUS.md`: 166 rows carry a runtime reader, the reads are the copy call site and the frame duration word, and no row fires a structural test; `tools/mapcontainer/animrow.py --census` derives the doc and the `MAP_BLOCK_CENSUS.csv` table from `MAP_BLOCK_ROWS.csv`, `MAP_ROW_OWNERS.csv`, `RECOMP_CITED.csv`, a read log and the image.
- `docs/research/REGION_READ_CENSUS.md`: the ten regions' 1,568 raw rows / 153,456 B joined to the 452-map read sweep - 318 rows / 85,135 B reached by a logged read, 1,250 rows / 68,321 B by none - with the reader class of every read pc (11 copy returns, 9 copy-routine bodies, 663 field loads, 2 unclassified of 685 distinct pcs), the four read shapes those rows fall into, the null each shape beats, and the 147 rows / 63,788 B that carry `pending-image-route`; no row of the ten regions bounds both a layout and an extent this round, so none converts. `docs/research/REGION_READS.csv` holds the read facts and `tools/research/region_readers.py` derives the doc, and `--check` compares it against the image.
- `docs/research/R00_R22_NULL_CENSUS.md`, `docs/research/R32_NULL_CENSUS.md` and `docs/research/R33_R35_NULL_CENSUS.md`: a generated section per document with one line per raw row of the regions it covers, naming the read pcs and the share of the row they reached, or `no reader in the 452-map sweep`.
- R20's 4 x 36 B sprite-descriptor table at `0x76E264` (144 B) is source: `0x08038458` `A34B` `ldr r3,[pc,#0x28c]` names it, `0x0803845A` `C100`, `0x0803845C` `0918` and `0x0803845E` `8900` compute `36 * index`, all 12 entries hold a `0x0808...` dest word, size `0x2000`, a mode of at most `0x2000` and a tile pointer, the six tile pointers name six `0x40`-byte blocks that tile `0x76E0E4..0x76E264`, and the 13th record at `0x76E2F4` holds zero and fails the dest word's high half; `tools/mapcontainer/pairsprite.py` emits it under `--block endrom`. Source 7,777,946 -> 7,778,090 B, raw-data 584,550 -> 584,406 B.
- R25's 4 x 36 B sprite-descriptor table at `0x75043C` (144 B) is source: `0x0802A37A` `4B84` `ldr r3,[pc,#0x210]` names it, `0x0802A37C` `C100`, `0x0802A37E` `0918` and `0x0802A380` `8900` compute `36 * index`, all 12 entries hold a `0x08080000` dest word, size `0x2000`, a mode of at most `0x2000` and a tile pointer, the six tile pointers name six `0x40`-byte blocks that tile `0x7502BC..0x75043C`, and the next structure's base literal at file `0x02A9FC` is exactly the table's end. Source 7,777,946 -> 7,778,090 B, raw-data 584,550 -> 584,406 B.
- R30's 4 x 24 B pair-sprite table at `0x759620` (96 B) is source: the consumer at `0x08035670` walks it with stride 24, reads each entry's tile pointer at `+8` and `+0x14` and copies `0x40` B to VRAM, the next structure's base literal at file `0x051CCC` is exactly the table's end, and the four tile pointers name four `0x40`-byte blocks that tile `0x759520..0x759620`; `tools/mapcontainer/pairsprite.py` emits it under `--block endrom`. Source 7,777,706 -> 7,777,802 B, raw-data 584,790 -> 584,694 B.
- `docs/research/ENDROM_NULL_CENSUS.md`: R20/R21/R23-R31's 1,128 raw rows / 328,986 B measured per row on six reader channels (a cited read, a read logged in play, a decoded pc-literal load, a decoded branch, a decoded load whose literal names the row, and a naming word), each row carrying its class and one measured reason it stays raw; `docs/research/ENDROM_READS.csv` holds the read pcs and `tools/research/endrom_readers.py` derives the doc, and `--check` compares it against the image.
- `docs/research/ENDROM_LAYOUTS.md`: the biggest named row of each of those regions with its reader quote, the six rows with a stride and no count, the reads logged in play, and the three sprite-descriptor tables with the null they beat.
- `docs/research/R32_NULL_CENSUS.md`: the first-MiB code band's 1,173 raw rows / 38,182 B measured per row on five reader channels, each row carrying its class, its byte statistics and one measured reason it stays raw; `tools/research/row_readers.py` derives the doc from `docs/research/R32_ROWS.csv` and `--check` compares it against the image.
- The 27 literal-pool rows of the first-MiB code band (264 B) are source: each starts on the word grid, is a whole number of words and every word is the literal address of a decoded `ldr [pc,#imm]` in a walked body, so each row is one `DCD` per word at its own address; the site side byte-permuted names 3 rows / 24 B against these 27 / 264 B. Source 7,776,988 -> 7,777,252 B, raw-data 585,508 -> 585,244 B.
- The three whole spans of `code-without-entry` are source: branch sites in transcribed code enter `0x042118..0x042188`, `0x0426D0..0x042750` and `0x042784..0x042876`, the transcribed row ending at `0x042118` falls through into it, the walk from those sites covers 454 B and `tools/research/thumb_body_convert.py` splices it byte-exact; source 7,777,252 -> 7,777,706 B, raw-data 585,244 -> 584,790 B.
- Every one of `code-without-entry`'s 11 remaining rows (20 B) has a per-row measured null in `docs/research/CODE_FRAGMENT_NULL_CENSUS.md`: each is one half of an instruction whose other half is a raw row of another class (9 rows a `BL` halfword, 2 rows a byte of a `PUSH`), and the entry channel that converted the class's whole spans beats its byte-permuted source 2.36 to 1 per instruction at the class's own denominator.
- `.recomp.json` describes the project for recomp.fyi and other readers of that format.
- The 53 x 20 B music record table at `0x3BB78C` (1,060 B) is source: four sites compute `20 * index` (`0x080008BE`, `0x080041BC`, `0x080053FE`, `0x08008C8A`), the stream machine reads `+0`, `+4`, `+8`, `+0xC`, `+0x10` and `+0x11`, and `tools/assetrecords/records_table.py` emits every record from `tools/assetrecords/musicrecords_layout.json` at build time; source 7,775,928 -> 7,776,988 B, raw-data 586,568 -> 585,508 B.
- Every one of R00/R07/R09/R10/R18/R22's still-raw rows (210 rows / 28,991 B after the table above is decoded) has a per-row measured null in `docs/research/R00_R22_NULL_CENSUS.md`: 57 rows carry a decoded reader that bounds no stride and count, 3 R00 rows are entered by a branch and decode to no body, and the rest have no decoded reader at all.
- The 3-entry pointer array at `0x6B8028` (12 B) is source: the loop at `0x080141D6..0x080141E8` strides 4 and bounds the table at 3 records (`cmp r4,#3`), and `tools/research/pointer_rows.py` emits the three addresses; source 7,775,916 -> 7,775,928 B, raw-data 586,580 -> 586,568 B.
- Every one of R33-R35's 160 still-raw rows (89,873 B) has a per-row measured null in `docs/research/R33_R35_NULL_CENSUS.md`: R34 and R35 have no naming literal in a code row, R33's 34 decoded readers bound no layout, and one row is decoded.
- 53 x 16 B cell-map records at `0x7198E4` (848 B) are source through `tools/mapcontainer/cellmap.py`: the reader at `0x080196E8` strides 16 and bounds the table at `0x35` records, each record four byte offsets into its `0x200`-byte block; source 7,775,068 -> 7,775,916 B, raw-data 587,428 -> 586,580 B.
- Six end-of-ROM rows (82,737 B) with a reader that proves a stride and none that proves a count stay raw-data: `docs/research/ENDROM_BOUND_CENSUS.md` quotes each stride, the index each reader uses and every bound route that came back empty.
- Every one of `R19`'s 574 raw rows (42,756 B) has a per-row measured null in `docs/research/R19_NULL_CENSUS.md`: no literal load, branch, class-table slot or odd pointer word names a byte of any row, and the two rows the shape predicate labels code are level with its own control.
- `tools/objdiff/objdiff_gen.py` writes `objdiff.json` from `work/ledger.csv`, and
  `tools/bytematch_upload.ps1` uploads the local objdiff report.
- The one kind-1 `other-compressed` container (0x29B308, 24 B) stays raw: both body token streams
  and the token where they diverge are recorded in `docs/research/ROUTE_TO_100.md`.
- 11 pointer-table rows (166 B) whose grid words do not cover the row are pc-relative literal
  pools: the 2-byte alignment pad is `DCB`, the words `DCD` (numeric where unnamed or Thumb-bit);
  source 7,040,991 -> 7,041,157 B, raw-data 587,594 -> 587,428 B.
- 10 `graphics` sprite rows (3,656 B) are 126 per-animation cell grids emitted from the
  sprite definitions' `+0x50` slots, each grid's extent 8 B times the animation record's
  frame count; source 7,037,335 -> 7,040,991 B, raw-data 591,250 -> 587,594 B.
- 7 `text/tables` rows (12,650 B) assemble as `DCD`/`DCW` self-relative method offsets;
  `docs/research/NUMBER_TABLES.csv` records the layout, the class bases and the residue, and
  `tools/research/text_tables.py --groups` prints the class census including the converted rows.
- 14 pointer-table rows (204 B) assemble as `DCD` of symbols; `docs/research/POINTER_ROWS.csv`
  gives every remaining pointer row one measured reason.
- The Mozilla Public License 2.0 as `LICENSE`, named in `README.md`.
- A CI workflow that runs the link check, the lint and the test suite on a single-commit
  checkout.
