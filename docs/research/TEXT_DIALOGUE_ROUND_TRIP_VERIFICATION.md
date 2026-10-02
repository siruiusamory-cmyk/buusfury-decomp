# Text and dialogue round trip

The text and dialogue round-trip capability at the ROUND_TRIP rung, the verified
encoding and layout, and why canonical relocation of a new string remains
unavailable.


## Capability rung achieved

**ROUND_TRIP.**

Not `AUTHOR_NEW`. Creating a genuinely new string would require adding a
pointer-table entry, which means growing the table, which means moving it and
rewriting all 51 code references to its base - and there is no verified free
space to move it into. The existing 1,534 strings can be read, decoded, edited,
written and round-tripped exhaustively; a 1,535th cannot yet be created safely.

## Upstream sources audited, before any reverse engineering

| Source | What it gave | Verdict |
|---|---|---|
| `yoav74/BuusFuryToolkit` @ `4353f6a2` | `Findings.txt` (one address: `Rom Dialog - 00057920`), `DialogFinder.py`/`TextEditor.py` (heuristic linguistic scan), `Buu's Fury.tbl`, `Extracted Text.txt` | Confirms only "text near 0x57920, two bytes per character". No pointer table, no count, no extent. Its `.tbl` is unnecessary and its `00=space` row is wrong. **Superseded.** |
| `Arefu/Legacy` @ `d22a556c` | `DBZKit/Assets/Dialog.cs` | Detector evidence covers `ALFE` (LoG II) only; per `docs/upstream-audit.md` not promotable to Buu's Fury. **Not used.** |
| `spicybung/DragonByteZ` @ `b2691209` | Map/graphics/audio/compression | No string-table knowledge. **Not used.** |
| `2genkidev/buusfury` @ `cc53d0cd` | Scatter layout, `INCBIN` ranges | No string-table knowledge. **Not used.** |
| Local research (`docs/research/`, prior record archives) | Prior records P-004..ROM-012, TOOL/TOOLKIT | No prior text/dialogue work existed. |

No upstream code was copied. No dependency was added.

## Verified encoding and layout

Full evidence in [`../research/TEXT_FORMAT.md`](../research/TEXT_FORMAT.md).

- **Encoding** `CONFIRMED_ROM`: UTF-16LE, terminator `0x0000`, strings packed
  contiguously. A unit decodes as a Unicode codepoint - proved by the single
  `0x00E9` (`Hercule Cafe`), which is why no character table is needed.
- **Control codes** `CONFIRMED_ROM` by exhaustive census: `0x0008` + one operand
  (100 occurrences; operands `0x02`/`0x03`/`0x05`/`0x06`/`0x07`/`0x1D`/`0x76`,
  semantics `UNKNOWN` and preserved opaquely), and `0x000A` newline (24).
  `%d`/`%s` are in-band ASCII, not control data.
- **Pool** `CONFIRMED_ROM`: `0x0005792C`..`0x0006BCE6`, 82,874 bytes.
- **Pointer table** `CONFIRMED_ROM`: `0x0006BCE8`, 1,534 little-endian GBA
  addresses, strictly ascending, zero duplicates.
- **Exhaustive tiling** `CONFIRMED_ROM`: every string ends exactly where the next
  begins. This is what makes a *complete* round trip provable, not a sampled one.
- **Reference topology** `CONFIRMED_ROM`: the pool base has exactly **one**
  inbound word-aligned reference in the whole 8 MiB image (the table itself); the
  table base has **51**. Access is by index, so relocating one string is a
  one-word rewrite.
- **Candidates** `INFERRED`: exactly 5 word-aligned words elsewhere coincidentally
  equal a string address, all inside compressed graphics data. Classified
  `CANDIDATE_REFERENCE`; fail-closed.
- **Shared strings** `CONFIRMED_ROM`: 153 texts repeat (one crate line 25 times)
  but every occurrence has its own bytes. Duplicated *content*, never shared
  *storage* - so editing one changes only that one, and no clone operation is
  needed.

## Proofs

| Claim | Evidence |
|---|---|
| Full-extent decode | 1,534 strings enumerated from the pointer table, deterministically, in index order |
| Full-extent byte-identical re-encode | All 1,534 re-encode to their exact original bytes; concatenation reproduces the pool's 82,874 bytes exactly |
| Unknown control data survives | Operand `0x42` (not one of the seven the ROM uses) round-trips; all nine tested operands round-trip |
| Deterministic extraction | Two extractions of the same ROM produce byte-identical `text/strings.toml` |
| Canonical in-place edit | `New Game` -> `Old Game` changes exactly 3 bytes, at `0x000579FC`, `0x000579FE`, `0x00057A00`, owner `text:0010`, reason `text edit` |
| Whole-ROM no-op rebuild | extract -> build produces SHA-256 `940ad5f0...`, identical to canonical, with **0** changes |
| Repeated builds identical | Two builds of the same modified project are byte-identical |
| Canonical ROM immutable | Hash re-checked after the whole read/edit/extract/build path; unchanged |
| Synthetic longer-text relocation | Allocated from declared free space, payload written, decodes back, table slot rewritten to the new address, neighbours untouched |
| Candidate blocks relocation | A planted candidate reference raises `CandidateReferenceError` naming its offset; unrelated strings still relocate |
| Failure emits nothing | Over-capacity relocation raises before any write; over-long or malformed authored text fails the build with no output file created |
| Wrong profile fails closed | A profile whose `pool_size` was altered while keeping the hashes is refused against the packaged contract |

## Canonical relocation: why it remains unavailable

The relocation machinery works and is proved. It is **not** exercised against
Buu's Fury because the profile declares no verified free region - unchanged from
TOOLKIT-003, which reached the same boundary for the same reason.

Per `ARCH-TOOL-001`, free space is profile-declared with recorded evidence and is
never inferred by scanning for `0xFF`/`0x00` runs: a scan cannot distinguish
padding from data and returns different answers on an already-edited image,
destroying reproducibility. No free-space archaeology was performed, as the brief
directs.

The boundary is therefore explicit and asserted by tests:

- text that fits its original allocation - **supported** on the canonical ROM;
- shorter text - **supported**, zero-padded deterministically;
- longer text - **refused**, with the exact byte deficit, on the canonical ROM;
  **proved working** on portable synthetic fixtures.

## Tests

**654 passed, 0 failed** across the repository (was 555 at TOOLKIT-003 closure).

- **555 portable unit** - runs with no ROM present.
- **99 ROM-gated integration** - skip cleanly when the canonical ROM is absent.

TOOLKIT-004 contributes **99** tests:

| File | Tests | Covers |
|---|---|---|
| `tests/unit/test_text_tables.py` | 34 | codec decode/encode, unknown control preservation, identity, pointer encoding, constructed-pool round trip |
| `tests/unit/test_text_relocation.py` | 12 | longer-text relocation, reference rewrite, candidate blocking, atomic failure, determinism, batch ordering |
| `tests/unit/test_text_project.py` | 15 | authored representation, ordering, determinism, validation failures, TOML escapes |
| `tests/integration/test_text_rom.py` | 38 | verified layout contract, tiling, reference topology, shared strings, full-extent round trip, canonical edits, whole-ROM identity, CLI |

No proprietary bytes are committed in any fixture.

## Test notes

Two items were flagged during implementation and reviewed before closure.

### 1. `tmp_path` / `PermissionError: [WinError 5]` - ENVIRONMENTAL, non-blocking

**Verdict: environmental and pre-existing. No production code was changed to
accommodate it, and no test was weakened or skipped.**

Evidence, in order:

1. **Exact failing operation.** `_pytest/pathlib.py:175`, inside `find_prefixed`,
   calling `os.scandir` on
   `<pytest temporary root>`. The call chain is
   `getbasetemp` -> `make_numbered_dir_with_cleanup` -> `make_numbered_dir` ->
   `find_suffixes` -> `find_prefixed`. pytest is *enumerating* the directory to
   choose the next run number; no project code is on the stack.
2. **It is enumeration, not creation, and not an ACL.** On that same path
   `os.stat` succeeds while `os.scandir` and `os.listdir` both raise
   `WinError 5`. A genuine permissions problem on the directory would fail
   `stat` too, so this is a sandbox read-fence over the shared temp tree.
3. **Reproduced on clean baseline code.** A detached worktree at
   `ce8f3b62b813ee8dacb9d042f8df15f7d87935e8` - containing none of the
   TOOLKIT-004 files - runs the *tracked, pre-existing* `tests/unit/test_cli.py`
   and produces **3 passed, 6 errors**, every error the same `PermissionError`.
4. **Control, same commit and same test file.** With an explicitly writable
   `--basetemp`, that identical baseline run gives **9 passed**.

The variable is therefore the temp location - not the code, and not this record.

**Required local invocation.** `-p no:cacheprovider` is needed for the same
reason: the in-repo `.pytest_cache` is access-denied by the same fence.

```
python -m pytest tests -q -p no:cacheprovider --basetemp=<writable dir>
```

Deliberately NOT done: no `tmp_path` monkeypatching, no `conftest.py` shim, no
`TMPDIR` handling in `tools/`. `grep` over `tools/` confirms production code
contains no temp-directory accommodation. Editing shipped code to satisfy a
local sandbox would trade a real invariant for a convenience.

### 2. `test_workflow_migration.py` assertion change - LEGITIMATE, coverage increased

**Verdict: the assertion is a moving pointer by design; the change follows the
precedent set at every previous record transition, and coverage went up.**

- **OLD INVARIANT.** the working queue must carry the heading `# TOOLKIT-003` and the
  STOP directive `Do not begin TOOLKIT-004`.
- **NEW REQUIREMENT.** the working queue must carry `# TOOLKIT-004` and
  `Do not begin TOOLKIT-005`, and must additionally link
  `archive/TOOLKIT-003-COMPLETE.md` alongside the existing
  `archive/TOOLKIT-002-COMPLETE.md`.
- **WHY THE OLD TEST WAS NO LONGER CORRECT.** These two assertions encode *which
  record is active* and *which record must not be started next*. That is a
  pointer at the head of the record chain, not a frozen fact.
  `git log -L82,96:tests/unit/test_workflow_migration.py` shows the same line
  retargeted at every transition: `Do not begin P-008` -> `P-009` -> `P-010` ->
  `P-011` -> `TOOLKIT-004`, with `# TOOLKIT-003` introduced at `ce8f3b6`.
  Leaving them pinned would assert that TOOLKIT-004 must never be activated,
  contradicting the maintainer's authorization. Nothing was lost: the old heading and
  its STOP directive both survive verbatim in
  `archive/TOOLKIT-003-COMPLETE.md` - activation archived the placeholder rather
  than deleting it.
- **WHAT THE NEW ASSERTION PROTECTS.** That activation archives the closed
  record's placeholder instead of discarding it, and that the chain back through
  every earlier placeholder stays reachable from the live file. It is
  load-bearing, not decorative: replacing the `archive/TOOLKIT-003-COMPLETE.md`
  link with `(deleted)` fails the test at line 96. The assertion count went from
  5 to 6 - one added, none removed.

## Defects found and fixed

1. **The TOML emitter refused newlines.** `project/format.py` rejected every
   control character, which made the 24 strings containing a real line break
   unauthorable. Fixed by escaping newline and tab as TOML basic-string escapes
   (`\n`, `\t`) while still refusing every other control character.
2. **Per-subsystem write plans could not detect cross-subsystem overlap.**
   `build` originally called `tables.plan()` alone; adding text as a second plan
   would have let a stat record and a string each validate while together writing
   the same bytes. Fixed by exposing `changes()` on both semantic layers and
   merging into a single `plan_changes` call.
3. **A documented example carried the wrong index.** The `project-format.md`
   worked example initially showed `text:0250` for a string that is actually
   `text:0041`. Fixed, and both printed examples are now pinned by a test so the
   document cannot drift from the ROM.

## Unresolved text-format questions

- **Semantics of each `0x0008` operand.** `UNKNOWN`. Seven distinct operands
  appear; the codec preserves them opaquely rather than naming them. Resolving
  this needs runtime observation of the renderer, which this record did not
  authorize.
- **Text outside this table.** Plain-ASCII debug and assertion strings exist
  elsewhere (around `0x08008A72`, `0x0803E024`) and are **not** part of this pool
  or table. Whether other *game* text exists outside it is `UNKNOWN`.
- **Which table index each consumer uses.** The table base is referenced from 51
  code sites; mapping index to caller is script-VM territory and belongs to
  TOOLKIT-005.
- **Whether a verified free region exists anywhere in the image.** Still
  `UNKNOWN`, and deliberately not investigated here.
