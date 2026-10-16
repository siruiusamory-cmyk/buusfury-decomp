# Release-candidate debt ledger

The current debt position, recorded once so the next ticket can answer "what
remains?" without reconstructing the conversation that produced it.

| Field | Value |
| --- | --- |
| Status | Current layer. Supersedes no record; it reconciles the older ones. |
| Ticket | `RC-DEBT-SWEEP-001` |
| Baseline | `3444cf5bc142cf0189168fc1587782a449f97069` (the merge of `AUTHORED-WORK-SAFETY-001`) |
| Date | 2026-10-08 |
| Supersedes | nothing. The historical records it summarises stay where they are. |

## 1. How to read this

Three older records hold debt, at three baselines, and none of them is current:

| Record | What it is | Baseline it describes |
| --- | --- | --- |
| `RELEASE-STATE-REASSESSMENT-001` (31 findings, `N-01`..`N-31`) | the pre-RC reassessment this ticket starts from | `d2b667bb` |
| `docs/research/PROJECT_STATE_AUDIT_RECONCILIATION.md` (73 numbered rows) | the reconciled code-quality audit | `67e0c27b` |
| `docs/research/PROJECT_CODE_QUALITY_AUDIT.md` (`CQA-01`..`CQA-58`) | the original backlog | earlier still |

This file is the current layer. It does not rewrite any of them: a row that later
work closed is dispositioned here and left intact there, exactly as
`DERIVATIVE-16M-REOPEN-001` was annotated rather than restated. Where this file
and an older record disagree, this file is current and the older record is that
record's history.

Counting correction, recorded because the ticket inherited a wrong number: the
73-row reconciliation holds **44** deferred rows (42 marked `DEFERRED`, plus rows
68 and 72 marked `DEFERRED, owner decision`), not 43. Every number 1..73 is
present exactly once. Rows 11, 23, 26 and 27 are the four `RELEASE-BLOCKING`
rows, and all four are now closed.

## 2. Current position

The capability denominator is complete and unchanged by this ticket:
**24 / 24 (100%)** - READ 5/5, EDIT 8/8, AUTHOR 7/7, DELIVER 4/4, 0 missing,
verified against `src/data/capabilities.json`. No capability is decremented for a
release-polish item, and no count moved in this pass.

Two release blockers remain, both outside this ticket:

- `N-01` no distributable patch path (BPS): the written contract requires one and
  no implementation exists anywhere in the tree.
- `N-02` no packaged DragonByte Z release and no visible version identity.

## 3. The 31 reassessment findings

Baseline `d2b667bb`. Dispositions are this ticket's.

| ID | Subject | Disposition |
| --- | --- | --- |
| N-01 | No distributable patch path (BPS) | BUNDLE - RELEASE-ARTEFACT-001 (release blocker) |
| N-02 | No packaging path, no visible version | BUNDLE - RELEASE-ARTEFACT-001 (release blocker) |
| N-03 | Extract destroys authored files | SUPERSEDED by `AUTHORED-WORK-SAFETY-001` |
| N-04 | Pending palette colour invisible to the unsaved total | SUPERSEDED by `AUTHORED-WORK-SAFETY-001` |
| N-05 | Save As confirmation reads as "nothing was pending" | FIXED NOW |
| N-06 | The `text` record names a surface that cannot author it | FIXED NOW (surface corrected; decomposition question recorded in section 7) |
| N-07 | Inspector keeps the previous image's content | FIXED NOW |
| N-08 | Project documents written non-atomically | SUPERSEDED by `AUTHORED-WORK-SAFETY-001` |
| N-09 | Scene Add-NPC form crosses a project switch | SUPERSEDED by `AUTHORED-WORK-SAFETY-001` |
| N-10 | Roadmap AUTHOR tally says 5 / 7 | FIXED NOW |
| N-11 | Rendered-row assertions run in no CI job | BUNDLE - GOLDEN/CI PREP |
| N-12 | 11 of 28 Qt-guarded unit modules can collapse to a green skip | FIXED NOW |
| N-13 | Portable gate members silently need the canonical ROM | FIXED NOW (documented, count corrected to six); the test relocation is BUNDLE - GOLDEN/CI PREP |
| N-14 | Deploy ends at `wrangler deploy`, nothing verifies the live site | BUNDLE - GOLDEN/CI PREP |
| N-15 | Dialogue journey states the pre-variable-length limit | FIXED NOW |
| N-16 | Golden journey has no tracked driver or record | BUNDLE - GOLDEN/CI PREP |
| N-17 | "using only DragonByte Z" with no in-app pixel surface | BUNDLE - RELEASE-ARTEFACT-001 |
| N-18 | `sprite-new` limits omit the map-level refusals | FIXED NOW |
| N-19 | Getting started omits the atlas prerequisite | FIXED NOW |
| N-20 | `_cell_read_error` survives a layer switch | FIXED NOW |
| N-21 | Create Chunk from an unread cell reports the wrong reason | DEFER - 1.x (the branch is not reachable from the GUI) |
| N-22 | A failed project palette read renders canonical colours | FIXED NOW |
| N-23 | `docs/workbench.md` understates Layout mode | FIXED NOW |
| N-24 | `PROJECT_STATE.md` points at a 21 / 24 scoreboard unlabelled | FIXED NOW |
| N-25 | GUI pixel export suggests a filename no build reads | FIXED NOW |
| N-26 | Packaged randomizer records a null build commit | BUNDLE - RELEASE-ARTEFACT-001 |
| N-27 | Documentation index promises a project export | FIXED NOW |
| N-28 | README "What it can do" omits graphics authoring | FIXED NOW |
| N-29 | `capability-registry.md` says capabilities are still missing | FIXED NOW |
| N-30 | No CI job builds the frozen executables | BUNDLE - RELEASE-ARTEFACT-001 (platform/cost decision recorded in section 7) |
| N-31 | Instrumented mGBA identity proofs skip in CI by construction | DEFER - 1.x (machine-local evidence, not a shipping surface) |

## 4. The 73-row audit ledger, reconciled

Counts at this baseline, one disposition per row and every row present exactly
once. Rows that later merged work closed are `SUPERSEDED` here; the older record
keeps its own label.

| Disposition | Rows | Count |
| --- | --- | --- |
| SUPERSEDED (no longer a defect) | 1-9, 11, 12, 15, 23, 24, 25, 26, 27, 30, 43, 46, 54, 60, 61, 64, 69, 70, 72 | 27 |
| FIXED NOW | 13 (the canonical-image alias half), 45 | 2 |
| BUNDLE - RELEASE-ARTEFACT-001 | 10, plus row 13's remaining atomic write | 1 + 1 |
| BUNDLE - GOLDEN/CI PREP | 20, 21, 36, 41, 42, 44, 67 | 7 |
| DEFER - 1.x | 14, 16, 17, 18, 19, 22, 28, 29, 31-35, 37-40, 47-52, 56, 57, 59, 62, 63, 65, 66, 71 | 31 |
| FALSE POSITIVE (the row describes no defect) | 53, 55, 58 | 3 |
| OWNER DECISION REQUIRED | 68, 73 | 2 |

Movement since the reconciliation's own baseline:

- rows 11, 23, 26 and 27, the four `RELEASE-BLOCKING` rows, were closed by
  `RELEASE-READINESS-CONSOLIDATION-001` (commits `1670289` and `d9cabf1`, merge
  `d2b667bb`);
- row 72 is moot: `sprite-new` shipped (merge `9360379`), so the 21-versus-22
  question it recorded no longer exists;
- row 45 was open and is fixed now: `tools/webfoot/workbench/app.py` re-enabled
  the View action only on an editor switch, so a Maps mode change left it stale.
  `_maps.modeChanged` now also reaches `_sync_scene_action`.

## 5. Persistence and recovery residuals

Carried out of `AUTHORED-WORK-SAFETY-001` and re-measured here.

| Residual | Disposition | Why |
| --- | --- | --- |
| A multi-document project write is not one transaction (a crash between `maps/layout.toml` and `maps/chunks.toml` can leave a project that will not load) | DEFER - 1.x | No production caller passes a cross-validated pair today, and the Workbench's narrow writers hold the invariant by construction |
| Interrupted extraction is not resumable in place | DEFER - 1.x | Deliberate, documented and tested; no authored file is at risk. The one cheap clarity tweak (`project.toml` last) is recorded here for whoever takes it |
| A Windows read-only destination can leave one `.webfoot-partial` sibling | DEFER - 1.x | Nothing is lost; the previous document survives byte-identical |
| The atlas is written in place, unguarded and non-atomic | FIXED NOW for the canonical-image alias; the atomic write is BUNDLE - RELEASE-ARTEFACT-001 | A caller-supplied `--atlas` path could name the canonical image, which is the one irreplaceable input. The truncated-atlas half is regenerable evidence |

## 6. CI and test honesty

| Item | Disposition | Statement |
| --- | --- | --- |
| `N-12` guard coverage | FIXED NOW | `tests/conftest.py` now fails the session for any opened module that collapsed on a PySide6 import, not only for the named regression list |
| `N-13` portable/ROM axis | FIXED NOW (documented) / BUNDLE - GOLDEN/CI PREP (relocation) | Six members of the `fast` gate need the canonical image; the count is corrected from three to six and named in `docs/testing.md` |
| `N-11`, `N-14`, `N-16`, rows 20, 21, 36, 41, 42, 44 | BUNDLE - GOLDEN/CI PREP | CI wiring and gate hygiene; no local proof is possible for a pipeline change |
| Row 67, `N-31` | DEFER - 1.x / manual gate | No commercial image and no locally built instrumented emulator may live in public CI. The ROM-gated suite and the instrumented identity proofs are owner-run gates before a release freeze |

## 7. Open owner decisions

1. **Row 68** - `map-browser` is registered at `proof: "runtime"` while its
   strongest tracked evidence is a retained VRAM oracle. ADR 0004 admits two
   readings and no count moves either way.
2. **Row 73** - `layout` and `tiles` may describe the same four-byte write through
   the same Maps Layout mode. Both are counted shipped, so no total moves.
3. **`N-06` decomposition** - the `text` record's surface is corrected here to the
   path that actually authors it, but whether `text` and `dialogue` are two
   capabilities or one remains a registry-decomposition decision.
4. **`N-30` platform** - building the frozen executables needs a Windows runner
   (PyInstaller does not cross-compile to win64) or a deliberate owner-built
   release. Cost decision, not a code decision.

## 8. What this pass fixed

Twenty-one findings, each proven to exist at the baseline before it was touched:
seventeen reassessment items, two audit rows, one carried Inspector residual, and
one public claim found while validating the current-state surfaces.

| Item | File |
| --- | --- |
| Row 45, stale View action | `tools/webfoot/workbench/app.py` |
| `N-07` and the carried Inspector residual | `tools/webfoot/workbench/session.py`, `inspector.py` |
| `N-20` stale cell-read error | `tools/webfoot/workbench/map_browser_tab.py` |
| `N-05` Save As confirmation | `tools/webfoot/workbench/map_browser_tab.py` |
| `N-22` palette read failure | `tools/webfoot/workbench/graphics_tab.py` |
| `N-25` export filename | `tools/webfoot/workbench/graphics_tab.py` |
| Row 13, canonical-image alias | `tools/webfoot/atlas_build.py` |
| `N-12` collapse guard | `tests/conftest.py` |
| `N-06`, `N-18` registry surfaces and limits | `src/data/capabilities.json` |
| `N-10`, `N-23`, `N-24`, `N-27`, `N-29`, `N-19`, `N-28`, stale "Next" claim | `docs/ROADMAP_TO_1_0.md`, `docs/workbench.md`, `docs/PROJECT_STATE.md`, `docs/README.md`, `docs/capability-registry.md`, `README.md`, `src/data/project.ts` |
| `N-15` journey limits | `docs/journeys/dialogue-editing.md` |
| `N-13` (documentation half) and the stale gate counts | `docs/testing.md` |

## 9. What remains

**Before the release candidate can ship, in order:**

1. `RELEASE-ARTEFACT-001`: `N-01` (BPS), `N-02` (packaging and visible version),
   `N-17` (the "using only DragonByte Z" acceptance wording), `N-26` (packaged
   build provenance), `N-30` (a Windows build path or an owner-built release),
   row 10 and row 13's remaining atomic write.
2. `GOLDEN/CI PREP`: `N-11` (rendered-row assertions in the site job), `N-14`
   (live-site verification after deploy), `N-16` (a tracked golden driver and
   record), `N-13`'s relocation, and rows 20, 21, 36, 41, 42, 44.

**Consciously deferred to 1.x:** `N-21`, `N-31`, the 31 deferred audit rows in
section 4, and the three persistence residuals in section 5.

**Nothing in this ledger is undecided.** Every row above carries one disposition,
and the ten release-debt questions the sweep was asked are answered in the ticket
record.

## 10. `RELEASE-ARTEFACT-001` dispositions

| Field | Value |
| --- | --- |
| Status | Current layer for the rows this ticket owns. It supersedes section 9's reading of them and rewrites no older record. |
| Ticket | `RELEASE-ARTEFACT-001` |
| Baseline | `b7f90a42393c42cea03cfbd36b8967621dbefca6` (the merge of `RC-DEBT-SWEEP-001`) |
| Date | 2026-10-08 |
| Supersedes | nothing. Section 9's list is where this ticket was assigned, not a claim it left untouched. |

### 10.1 The product boundary this ticket was corrected to

The owner corrected the direction during this ticket: the existing Webfoot
Workbench and the two randomizers are engineering and reference surfaces, not the
future shipping DragonByte Z application, which is being built as its own product
over the same SDK. Packaging the beta Workbench and calling it DragonByte Z is
therefore not an honest close of `N-02`, and the row splits.

### 10.2 Row dispositions

| Row | Disposition | Where it is proved |
| --- | --- | --- |
| `N-01` no distributable patch path | **CLOSED** | `tools/webfoot/formats/bps.py` (encoder and applier), `tools/webfoot/patch.py` (the one export and verify service), `webfoot patch export` / `webfoot patch verify`, `tests/unit/test_bps.py`, `tests/unit/test_patch_export.py`, and the ROM-gated `tests/integration/test_patch_export_rom.py` (verified source plus built derivative to patch, and back to the exact image) |
| `N-02` no packaged release path and no visible version | **SPLIT**, see 10.3 | `N-02a` in the same files as the version authority and the release guards; `N-02b` belongs to the new product |
| `N-17` "using only DragonByte Z" with no in-app pixel surface | **CORRECTED NOW** as a wording defect, and its feature gap **MOVED** to the new product | the limits note under the golden acceptance list in `docs/ROADMAP_TO_1_0.md` section 15, which names the one step that consumes a file edited outside the application and records that the section is the new product's acceptance target |
| `N-26` packaged randomizer records a null build commit | **CLOSED** | `tools/webfoot/release_identity.py` bakes the identity in, `scripts/build-warprand.ps1` and `scripts/build-enemy-randomizer.ps1` write it before PyInstaller runs, and `tools/webfoot/randomizer/service.py` reports it instead of a null. Proved by `tests/unit/test_release_identity.py`; the packaged-manifest readback is an owner-run gate (10.4) |
| `N-30` no CI job builds the frozen executables | **SPLIT**: the portable and static half **CLOSED**, the platform half an **OWNER DECISION**, recorded | 10.4 |
| row 10 output-path safety has no single owner | **SPLIT AND RE-LABELLED** | the source-alias half was already owned by `tools/webfoot/write.py`; the atomic half is row 13 and closes with it; the exporter and output-directory policy with the eight `tools/export` helpers stays `DEFER - 1.x` with the audit's own reason (exporter hygiene that does not block the milestone) |
| row 13's remaining atomic write | **CLOSED** | `atlas_build.write_atlas` and `write_conflicts` now replace through `tools/webfoot/project/atomic.replace_document`, the discipline the project documents already use. Proved by the two interrupted-write tests in `tests/unit/test_atlas_build.py`, whose positive control is the ordinary replacement that must keep working |
| section 5's atlas residual | **CLOSED for the two writers**, COUNTED and deferred for the producers | `atlas_producers/_io.py:22`, `code_functions.py:348` and `scan.py:554` write under the ignored `build/` tree, and `webfoot atlas regenerate` already refuses a non-empty target, so they are the same class as this row but not this row's citation. Recorded here rather than discovered later |

### 10.3 `N-02`, split honestly

| Row | Disposition | Statement |
| --- | --- | --- |
| `N-02a` reusable packaging and version foundation | **CLOSED** | One version and build identity authority (`tools/webfoot/release_identity.py`), a portable census of a staged package (`tools/quality/package_content.py`) that reports ROMs, saves, machine paths and absent resources, a release-definition guard that now fails a definition naming a resource nobody wrote (`tools/quality/public_release.py`), and a test that the archive a packaging script names carries the version the product reports. The internal packaging shape, the packaging-time probe and the owner-run gate are recorded in `docs/release-artefacts.md` and `docs/DEVELOPMENT.md` |
| `N-02b` final DragonByte Z packaging and visible in-product identity | **DEFERRED TO THE NEW PRODUCT** | The application the user runs does not exist yet. Its package definition, entry point, About surface, visible version and packaged resource list are that product's to define, and this ticket deliberately does not approximate them by packaging an engineering surface under the product's name. This is a corrected product boundary, not a regression and not a new blocker. One consequence is already visible and is left for that product: the `dragonbyte-z` console entry point in `pyproject.toml` still starts the engineering Workbench |

The capability denominator is unchanged by this ticket: **24 / 24 (100%)**, no
capability added, none decremented. Packaging and patch support are release
obligations around a complete product, not a twenty-fifth capability.

### 10.4 `N-30`, and what CI can honestly prove

The real position, measured at this baseline: `.gitlab-ci.yml` declares no `tags`
at all, and its two test jobs run on Linux images. PyInstaller does not
cross-compile to win64, and the packaging-time byte probe needs the canonical
image, which may never live in public CI. So no job can build or smoke a frozen
executable here, and none pretends to.

| Half | Disposition | Statement |
| --- | --- | --- |
| Portable and static validation | **CLOSED** | It runs in the existing `test-sdk` job, through `python -m pytest tests/unit`: the release-definition guard's new resource and entry-script checks, the single-version-source test, and the package census's own tests |
| A Windows packaging job | **OWNER DECISION, recorded** | Adding a Windows runner is a cost decision, not a code decision, exactly as section 7 item 4 states. Declined for this ticket rather than faked. The owner-run gate that replaces it is named in `docs/DEVELOPMENT.md` and `docs/release-artefacts.md`, with the artifact digests recorded alongside the release |

No byte-identical executable claim is made anywhere, and none may be added:
PyInstaller's archive carries per-entry timestamps and the PE carries build
metadata. The reproducible claim is about product content, and it is asserted
separately.

### 10.5 Owner-run verification still owed

Two facts cannot be proved from a Linux checkout and are recorded rather than
claimed:

1. a manifest written by a **packaged** randomizer, read back to confirm
   `build.commit` is no longer null (`pwsh scripts/build-warprand.ps1 -Clean`,
   then `smoke-warprand-packaged.ps1`, then the manifest);
2. a third-party BPS applier accepting an exported patch. The round trip here is
   proved against an independent decoder written from the published specification
   in `tests/unit/test_bps.py`, and no external BPS tool is installed on this
   machine, so the ecosystem cross-check remains owner-run.

### 10.6 A finding this ticket measured

- **NEW-1** ROM discovery in the ROM-gated suite takes the first filesystem match:
  `glob("roms/*Buu*.gba")[0]` in `tests/integration/test_project_build_rom.py` (and
  the copies of that helper). A worktree that also holds randomized derivatives
  matches eight files and the canonical image is not the first, so the proof
  silently skips while reporting that the ROM is absent. Measured here. The patch
  proof finds the image by digest instead.
  Disposition: **BUNDLE - GOLDEN/CI PREP**, which owns gate honesty and the
  ROM-gated gate's relocation, because fixing every copy is a sweep rather than a
  release artefact.

### 10.7 What is now blocked

Nothing in this ledger is release-blocking. `N-01` and `N-02a` are closed, `N-02b`
waits on a product that has not been started, and every other row above carries one
disposition.
