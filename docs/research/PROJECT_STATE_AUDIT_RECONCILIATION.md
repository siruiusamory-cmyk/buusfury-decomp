# Project-state audit reconciliation

Status surfaces, the audit backlog and the next product capability, reconciled
against the repository as it actually is.

| | |
| --- | --- |
| **Ticket** | `PROJECT-STATE-AUDIT-RECONCILIATION-001` |
| **Date** | 2026-10-07 |
| **Baseline** | `67e0c27b1dd5525f23d928a3b16fbd60765b568a`, the tip of `origin/master` |
| **Worktree** | `log1-remake-project-state-audit-001`, branch `ticket/project-state-audit-reconciliation-001` |
| **Read-mostly** | No production feature work, no audit remediation, no graphics or map implementation, no runtime infrastructure, no archive purge |
| **Authority** | [`src/data/capabilities.json`](../../src/data/capabilities.json) defines product completeness. This document reconciles status surfaces to it; it does not define capabilities. |

Four read-only investigators each worked a separate question: the audit-finding
inventory, the 24-capability measurement, the merged-work chronology, and the
release/public-debt measurement. A fifth independently reviewed the result against
the baseline; it returned one blocking verdict, and every finding it raised is
resolved and recorded in section H. Their reports are the evidence behind the
tables below; the editing recorded in section F was done once, after every
measurement was taken.

---

## A. Current capability scoreboard

### A.1 Measured score

    READ    5 / 5
    EDIT    8 / 8
    AUTHOR  4 / 7
    DELIVER 4 / 4
    TOTAL  21 / 24

Measured from `src/data/capabilities.json`: 24 records, 21 `shipped`, 3
`missing`. The three missing are `sprite-new`, `appearance` and `map-new`.
`gfx-import` is `shipped`.

The registry's counted states are **correct** and are not changed by this ticket:
it gains no capability and loses none. Two record-level statements inside it were
provably false against the tree and were corrected as text, with no state, count
or proof level touched (findings 69 and 70, and the rows in section F).
`README.md:87` ("21 / 24 capabilities (88%)") and the rendered site, which derives
its count from the registry through `src/data/project.ts:250-267`, already agreed
with it.

Two tracked narrative surfaces did **not** agree, and are corrected by this
ticket (see section F):

- `docs/ROADMAP_TO_1_0.md` said 20/24 (83%) and "graphics import NEXT, not
  started" in eleven places.
- `docs/PROJECT_STATE.md:2158-2165` said 20/24 and "the next capability is
  graphics import".

### A.2 Twenty-four row evidence table

`Merged` means the named ticket's merge commit is an ancestor of the baseline. A
registry `proof` of `runtime` means the claim depends on engine behaviour and was
observed in the retail engine; `application` means it was proven by the
application's own round-trip, a rendered image, or a ROM-gated build proof. Where
the registry's own proof level is contested, the row prints the registry value and
says so, and the question is recorded as a finding rather than silently changed.

| # | Capability | Family | Registry | Measured | Merged evidence | Proof | Acceptance met |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `shell` Desktop application shell | READ | shipped | SHIPPED | `WORKBENCH-001` `16ba237`; `WORKBENCH-006` `55a5681` | application | yes |
| 2 | `atlas` Full-ROM atlas search | READ | shipped | SHIPPED | `WORKBENCH-001` `16ba237`; `TEXT-INDEX-001` (tree: `tests/integration/test_decoded_text_rom.py`) | application | yes |
| 3 | `inspector` Recovered-record inspector | READ | shipped | SHIPPED | `WORKBENCH-001` `16ba237`; `WORKBENCH-002` `f0b78cc` | application | yes |
| 4 | `graphics` Sprite, animation and palette browsing | READ | shipped | SHIPPED | `TOOLKIT-010`; `LOGX-SPRITE-001`; `tools/webfoot/workbench/graphics_tab.py` | application | yes |
| 5 | `map-browser` Map browsing, every map and layer | READ | shipped | SHIPPED | `DRAGONBYTE-Z-MAP-BROWSER-001`, delivered at the baseline by `ff4a1fb4` (2026-09-19); `LOGX-MAP-RENDER-001` | runtime as recorded; contested, see finding 68 | yes, 452 maps |
| 6 | `dialogue` Dialogue line editing | EDIT | shipped | SHIPPED | `DIALOGUE-VARIABLE-LENGTH-001` `1977e00` | runtime | yes, longer line displayed |
| 7 | `palette` Shared palette recolour | EDIT | shipped | SHIPPED | `TOOLKIT-010`; `tests/integration/test_graphics_override_build_rom.py` | application | yes |
| 8 | `placement` Object placement on the rendered map | EDIT | shipped | SHIPPED | `PLACEMENT-POS-001` `8616413`; `docs/research/PLACEMENT_POSITION_PROVENANCE.md` | runtime | yes |
| 9 | `layout` Map layout editing, chunk-cell replacement | EDIT | shipped | SHIPPED | `MAP-LAYOUT-WRITE-001`; `DRAGONBYTE-Z-MAP-LAYOUT-EDITOR-001`; `docs/research/MAP_LAYOUT_EDITOR_VERIFICATION.md` | application | yes |
| 10 | `tiles` Tile painting | EDIT | shipped | SHIPPED | `MAP-TILE-PAINT-001` `f5c2b99` (2026-09-25); `docs/research/MAP_TILE_PAINT.md` | runtime | yes |
| 11 | `chunks` Chunk creation and editing | EDIT | shipped | SHIPPED | `MAP-CHUNK-AUTHORING-001` `5948f91` (2026-09-25); `docs/research/MAP_CHUNK_AUTHORING.md` | runtime | yes |
| 12 | `resize` Map resizing and layer changes | EDIT | shipped | SHIPPED | `MAP-RESIZE-AND-LAYERS-001` `ad03b89` (2026-09-26); `docs/research/MAP_RESIZE_AND_LAYERS.md` | runtime | yes |
| 13 | `warps` Warp and connection editing | EDIT | shipped | SHIPPED | `MAP-WARPS-AND-CONNECTIONS-001`; merges `7800412`, `197c667`, `5294934`, `3d8d373`, `aea91c9`, `11dc4eb`, `28836d7`, `5ec2c67`, closeout `cdbe51c` (2026-09-28) | runtime | yes, 735 records round-trip |
| 14 | `entity` Authored entities and placements | AUTHOR | shipped | SHIPPED | `TOOLKIT-022`; `TOOLKIT-027`; `TOOLKIT-029`; `docs/research/AUTHORED_PLACEMENTS.md`, `AUTHORED_RUNTIME_PROOF.md` | runtime | yes |
| 15 | `behavior` Authored behavior and scripts | AUTHOR | shipped | SHIPPED | `TOOLKIT-031`; `TOOLKIT-032`; `TOOLKIT-034`; `docs/research/AUTHORED_BEHAVIOR_EXECUTION.md`, `AUTHORED_SCRIPT_BODY.md` | runtime | yes |
| 16 | `text` Authored text beyond the retail slot | AUTHOR | shipped | SHIPPED | `TOOLKIT-037`; `TEXT-HANDLE-001`; `TEXT-HANDLE-002`; `ROM-EXPAND-001` | runtime | yes |
| 17 | `gfx-import` Graphics replacement and import | AUTHOR | shipped | SHIPPED | `GRAPHICS-IMPORT-BOUNDARY-001` `be93182` (2026-10-03); `docs/research/GRAPHICS_PIXEL_OVERRIDE.md` | runtime | yes, actor-sprite containers only |
| 18 | `sprite-new` New sprite, animation and frame authoring | AUTHOR | missing | PARTIALLY SHIPPED | Ten merged tickets: `0ff29c1`, `64acf63`, `70dacdd`, `4054152`, `215dc77`, `5f3fab5`, `144d06b`, `aba1257`, `954a402`, `4ee7d12` (2026-10-04/05); `docs/research/SPRITE_NEW_RUNTIME.md`, `SPRITE_NEW_PROJECT_SURFACE.md`, `SPRITE_NEW_COMPOSITION_GUARD.md` | runtime proof exists, for one narrow composition shape | **no**, see A.3 |
| 19 | `appearance` New appearance definitions | AUTHOR | missing | MISSING | `GRAPHICS-COVERAGE-001`; `docs/research/GRAPHICS_COVERAGE.md` | none | no; whether the table can grow is unresolved |
| 20 | `map-new` New map and scene materialisation | AUTHOR | missing | MISSING | `DRAGONBYTE-Z-MAP-LAYOUT-EDITOR-001`; `docs/research/POST_LOGX_IMPLEMENTATION_ROADMAP.md` | none | no; terminal frontier |
| 21 | `validate` Deterministic validate and build | DELIVER | shipped | SHIPPED | `WORKBENCH-001` `16ba237`; `WORKBENCH-002` `f0b78cc` | application | yes |
| 22 | `save-as` Safe Save As to a new file | DELIVER | shipped | SHIPPED | `DRAGONBYTE-Z-AUTHORED-IMAGE-PIPELINE-001` `cd49aa5` (2026-09-20); `docs/research/AUTHORED_IMAGE_PIPELINE_VERIFICATION.md` | application | yes |
| 23 | `provenance` Derivative provenance and reopen | DELIVER | shipped | SHIPPED | `DRAGONBYTE-Z-MAP-LAYOUT-EDITOR-001`; `DRAGONBYTE-Z-AUTHORED-IMAGE-PIPELINE-001`; `docs/decisions/0002-authored-derivative-trust.md` | application | yes |
| 24 | `launch` Launch the build in an emulator | DELIVER | shipped | SHIPPED | `WORKBENCH-001`; `tools/webfoot/workbench/launcher.py` | application | yes |

### A.3 Why `sprite-new` is not shipped, although ten tickets merged

The ten merged tickets built a real mechanism. `docs/research/SPRITE_NEW_RUNTIME.md`
records the retail engine resolving and drawing an actor-sprite identity the
image does not contain: `new_sprite_id=307`, `structure=0x088005B4` above
canonical EOF, `actors_using_new_identity=1`, `frame=3178`. That is a
`RUNTIME PROVEN` research result.

It is not the capability, and the repository says so in its own words:
`docs/research/SPRITE_NEW_PROJECT_SURFACE.md:18-19` - "`sprite-new` is still
**not shipped**, and this ticket does not change that status" - and `:181-184` -
"No authoring surface ... a person writes `sprites/sprites.toml` and supplies the
sheet PNGs. There is no GUI, no CLI subcommand".

The rule that decides it is the roadmap's definition of done
(`docs/ROADMAP_TO_1_0.md:713-732`), item 1 at `:715-716`: "A semantic user
workflow exists; no manual ROM offset is required for the supported case." For
`sprite-new` no semantic user workflow exists yet: the author hand-writes a
document that no shipped command emits, and no editor surface authors a new
sprite, animation or frame.

**The precedent that nearly decides it the other way, stated openly.**
`gfx-import` ships with `surface: "Project workflow: extract, edit an extracted
sprite PNG, validate, build"` while its own limit says "No editor surface edits
pixels yet", so the absence of a GUI is not by itself disqualifying. What
separates the two is the entry point, not the absence of windows:
`webfoot extract` (`tools/webfoot/cli.py:520`) is a shipped command that produces
the exact PNG the author then edits, and `validate` and `build` consume it.
Nothing in the product emits or scaffolds `sprites/sprites.toml`; the author must
write that document by hand and there is no subcommand for it at all. A capability
whose only entry is hand-authoring a document the tool never produces has no user
workflow to count.

**This is a product decision, and it belongs to the owner.**
`docs/capability-registry.md:57` records that shipping or retiring a capability is
a product decision, and both sprite tickets deliberately declined to take it
(`SPRITE_NEW_PROJECT_SURFACE.md:185-187`). If the owner applies the `gfx-import`
precedent to `sprite-new` - a project-document workflow reachable through the
shipped binary - the count would read 22/24 and every surface would have to be
restated. This reconciliation keeps 21/24 because no shipped entry point exists for
the sprite document, records the alternative explicitly as finding 72 instead of
burying it, and does not decide a product question on the owner's behalf.

What remains, from `SPRITE_NEW_PROJECT_SURFACE.md:172-184` and
`SPRITE_NEW_COMPOSITION_GUARD.md:23-40`:

- no authoring surface anywhere in DragonByte Z;
- no frame-composition budget: every authored frame copies the donor's own
  first frame, so the budget is unchanged rather than modelled;
- no direction-slot-to-facing mapping project-wide.

The categories stay separate here on purpose: `FORMAT UNDERSTOOD`,
`EXISTING CONTENT EDITABLE`, `AUTHOR_NEW`, `RUNTIME PROVEN` and `SHIPPED
CAPABILITY` are five different claims.

### A.4 Scoreboard history, for reference only

| Point in time | Score | Note |
| --- | --- | --- |
| `src/data/capabilities.json` at the baseline | 21/24 | The authority. 21 shipped, 3 missing. |
| `README.md:87`, rendered site | 21/24 | Agrees with the registry. |
| `docs/ROADMAP_TO_1_0.md`, `docs/PROJECT_STATE.md` before this ticket | 20/24 | Stale: written before `GRAPHICS-IMPORT-BOUNDARY-001` merged. Corrected in section F. |
| September roadmap snapshot recorded in history | 17/24 | Historical measurement at the Phase 2A point. Not restated as current. |

---

## B. Ponytail audit reconciliation

### B.1 What the backlog actually is

The ticket asked for the complete Ponytail / project-quality / public-readiness
audit backlog. Measured on the baseline:

- **The Ponytail name has no in-tree finding records.** A case-insensitive
  search for `ponytail` over the whole worktree returns zero matches in tracked
  text, and `git log --all --grep='ponytail' -i` returns zero commits. There is
  no deliberate-shortcut marker comment and no debt ledger in the baseline.
- **The project-quality audit is real and complete.**
  [`PROJECT_CODE_QUALITY_AUDIT.md`](PROJECT_CODE_QUALITY_AUDIT.md) carries
  `CQA-01` through `CQA-58` plus two records it spawned. That is the backlog.
- **Most of the public-readiness findings are not recoverable from the tree.**
  The audit artifact `AI_SURFACE_AUDIT.md` and the whole `docs/tickets/` ledger
  (141 process records) are absent at the baseline, and **no commit reachable
  from the baseline ever named either path**
  (`git log --full-history 67e0c27b -- docs/tickets` returns 0 lines). They were
  removed inside the `DRAGONBYTEZ-PUBLIC-REPO-HARDENING-001` branch before its
  merge, so the closeout documents for the individual CQA tickets cannot be
  recovered from git. What survives is the audit's own remediation table
  (`:1507-1525`), its in-place annotations (`:1531-1559`), the gates under
  `tools/quality/`, and the merge commits.
- **Durable records outside the tree still carry findings**, and they are folded
  in below: a read-only over-engineering audit of `tools/webfoot`, the
  runtime-foundation cross-audit residuals, a nightly cross-audit note, and two
  carried follow-ups.

**Total findings reconciled: 73.** Every one appears exactly once below, with a
single disposition from `CLOSED`, `SUPERSEDED`, `RELEASE-BLOCKING` or
`DEFERRED`. Three findings could not be re-measured this pass; they are marked
`UNVERIFIED` inside the evidence cell and carried as `DEFERRED`, which asserts
nothing about closure. Seven rows were found by the reconciliation itself rather
than by the original audit: six labelled `AUDIT-RECON-*` and one `*-GAP` row. They
are labelled that way so they cannot be mistaken for original audit findings.

| Disposition | Count |
| --- | --- |
| CLOSED | 25 |
| SUPERSEDED | 1 |
| RELEASE-BLOCKING | 4 |
| DEFERRED | 43 |

### B.2 Findings

`Original status` is the severity and the claim as recorded, compressed. `Source`
is the current-evidence citation. Where the audit's cited line numbers have
drifted, the citation is to the line read in the baseline tree.

| # | Finding | Original status | Current evidence | Final disposition | Why |
| --- | --- | --- | --- | --- | --- |
| 1 | `CQA-01` | CRITICAL: PNG export wrote a caller-supplied path with no alias guard, so the verified ROM could be destroyed | `tools/webfoot/write.py:140` `ensure_not_source_alias`, called at `cli.py:1624` and `graphics_tab.py:1072`; `tests/unit/test_output_safety.py:131-175` | CLOSED | One SDK owner of the source-alias rule and both destructive call paths apply it. Merge `f61c9b6` is an ancestor. |
| 2 | `CQA-02` | CRITICAL: packed encoder output not provably self-terminating; two exclusive engine termination rules asserted | `tools/webfoot/formats/webfoot_lz.py:83-84,497` `validate_retail_termination`; escape emitted `:641,820` | CLOSED | One production postcondition, enforced before any size decision. |
| 3 | `CQA-03` | HIGH: Workbench paired the open ROM with an atlas built for a different profile, no identity comparison | `tools/webfoot/profile.py:95,665` `AtlasIdentity` / `require_identity` | CLOSED | The identity contract owns the rule and is called before atlas assignment. |
| 4 | `CQA-04` | HIGH: map/graphics concepts decoded by two production stacks never compared; a production writer built on the export-side one | `tools/webfoot/formats/map_graphics.py:3`; `map_layout_write.py:12-31` has no `tools.export` import | CLOSED | One shared binary-interpretation authority; the writer is off the export layer. |
| 5 | `CQA-05` | HIGH: a project mutation silently destroyed staged layout edits and the placement undo history | `workbench/app.py:251-256` `on_project_mutated`; `editors.py:345-378`; `map_browser_tab.py:2863` | CLOSED | Project mutation and session change are separate entry points; staged state survives. |
| 6 | `CQA-06` | HIGH: `Session.open_rom` let sibling SDK error families escape the Open ROM slot as a dead click | `workbench/session.py:77` `OPEN_ROM_FAILURES`; `atlas_browser.py:172` | CLOSED | `open_rom` is total over the declared families; the slot catches one owned tuple. |
| 7 | `CQA-07` | HIGH: palette editor and `palette_users` did full-project work per UI element on the UI thread | `graphics_tab.py:688` `_repaint_project_state`; `warp_tab.py:672-680`; `map_browser_tab.py:5344` | CLOSED | One repaint path with a re-entrancy guard and a memoized consumer inverse. |
| 8 | `CQA-08` | HIGH: CI installed only `.[dev]`, so 258 collected portable tests skipped whole at import | `.gitlab-ci.yml:96` installs `.[dev,workbench,research]`; `:39` offscreen; `tests/gates.py:129-151` `REQUIRED_GUI_MODULES`; `tests/conftest.py` session guard | CLOSED | Whole-module collapses driven to zero; the guard is independent of the dependency. |
| 9 | `CQA-09` | MEDIUM: the canonical-EOF straddle guard is load-bearing and had zero test coverage | `tests/unit/test_rom_expansion.py:168-190` straddle case plus its positive control | CLOSED | The exact synthetic case the finding demanded is present. |
| 10 | `CQA-10` | MEDIUM: output-path safety has no single owner; four divergent policies and two writers with none | Source-alias half owned at `write.py:121,140`; remainder open at `atlas_build.py:539,553` and `authored_image.py:376`. Audit `:1525` still reads PARTIAL / REMAINDER: OPEN | DEFERRED | The audit records the remainder as exporter/output-policy hygiene that does not block the milestone, and the roadmap lists it as known deferred debt. Cannot touch the canonical ROM. |
| 11 | `CQA-11` | MEDIUM: overwrite policy is three policies - refuse, silently replace, delete-then-rebuild | `authored_image.py:376-378` unconditional `os.replace`; `build_panel.py:405-406` unlinks occupied outputs before `_run_build` | **RELEASE-BLOCKING** | Threatens the Build and Save As publication path: the irreversible delete still precedes a known-good rebuild, so a failed build leaves the destination destroyed. Must close before RC/v1.0. |
| 12 | `CQA-12` | MEDIUM: the Build path emitted no provenance document although the delivery contract names manifest publication | `build.py:152,171,1264,1767` `MANIFEST_BESIDE_OUTPUT`; `build_panel.py:85-89` | CLOSED | Default sibling publication plus the reopen/identify assertions the finding required. |
| 13 | `CQA-13` | MEDIUM: `atlas_build.write_atlas` truncates its destination in place, unguarded and non-atomic | `atlas_build.py:537-541` and `:544-553` still `path.open("w", ...)`, no staging, no refusal | DEFERRED | Re-judged down from release-blocking: it takes no ROM or source parameter, so it cannot alias the verified input, and the atlas is a regenerable derived artifact. An interrupted regenerate leaves a truncated atlas, which is a bounded loss. |
| 14 | `CQA-14` | MEDIUM: `verify_emitted_image` scans all 8 MiB in Python on every authored save, on the UI thread | `authored_image.py:222-224` still `enumerate(zip(base, data))` over the whole image | DEFERRED | Re-judged down: a latency cost on a save that already verifies, not a correctness or data-loss path. Worth its own ticket, not a release blocker. |
| 15 | `CQA-15` | MEDIUM: load-bearing constants and verified extents had multiple owners, one a live index bound | `tools/webfoot/binary.py:8` `GBA_ROM_BASE`; grep for `940ad5f0` under `tools/` returns no match | CLOSED | Behavioural authorities migrated onto the profile and catalog. |
| 16 | `CQA-16` | MEDIUM: `handles.recover_handle` hard-codes one profile contract and verifies no identity | `handles.py:296` `CONTRACTS["buus_fury_usa_rev0_01c1707f"]` still literal-keyed | DEFERRED | Boundary correct for the only supported profile; escalate only if `reference_sites` reaches a patcher. |
| 17 | `CQA-17` | MEDIUM: a CONFIRMED placement-to-enemy link is minted by an address-alignment test, not declared identity | `entities.py:96-98` congruence test | DEFERRED | Correct for the current profile; under-specified for a new one. Accepted carry. |
| 18 | `CQA-18` | MEDIUM: an author-facing trigger is documented runtime-proven while its contract records an inference | `project/placements.py:34` `"runtime-proven semantics"` | DEFERRED | Wording versus evidence discipline; no behaviour wrong. |
| 19 | `CQA-19` | MEDIUM: `webfoot_lz._gamma` is unbounded, so a malformed container costs quadratic time | `webfoot_lz.py:225-231` is still a bare bit loop with no internal bound. `_marker_scan_limit` `:234-250` and `_emit_raw` `:252-266` bound the read only on the marker-terminated path, which is not the default (`require_end_marker`, `:314-322`); `tools/webfoot/atlas_producers/scan.py:345` calls `lz.unpack(data, offset)` with no input-consumption bound | DEFERRED | Partially remediated, not superseded: the marker-terminated path is bounded, the default decode path keeps the unbounded loop, so the debt is carried rather than dismissed. Low in practice, because a malformed container wastes time rather than corrupting anything, and no hostile input was measured. See section G. |
| 20 | `CQA-20` | MEDIUM: the deploy job is not gated by the test job | `.gitlab-ci.yml:149-169` `deploy-site` has rules only, no `needs:`. Its own steps re-run `npm run check`, `npm run build` and `site_check.py` | DEFERRED | Re-judged down: the published artifact is still validated in the deploy job, so the exposure is publishing a site from a commit whose SDK suite did not run, not publishing an unchecked page. |
| 21 | `CQA-21` | MEDIUM: the `fast` gate is not hermetic, and the only published-page-versus-registry check was inert everywhere | Closed half: `site_check.py` runs in `test-site` (`.gitlab-ci.yml:144`) and `deploy-site` (`:166`). Open half: `docs/testing.md:18-19` still says `fast` needs nothing beyond the dev extra | DEFERRED | Split finding. The inert-check half is CLOSED; the hermeticity and stale contract wording remain and are carried; neither is release-affecting because CI itself is now honest. |
| 22 | `CQA-22` | MEDIUM: `tools/qa` probes are owned by no test and no gate; the cited one can pass vacuously | `tools/qa/status_duplication_probe.py` keeps the vacuity path; the claim "no test imports `tools.qa`" is now false (`tests/unit/test_qa_capture_shell.py:21`); the real defect class is pinned by `tests/unit/test_workbench_project_status.py`, which runs in CI | DEFERRED | Instrument-only silence with no shipping path; the premise that both guards could be quiet at once is gone. |
| 23 | `CQA-23` | MEDIUM: undo ownership is inconsistent - Maps undo mode-blind, layout edits have no history, the shell cannot reach the Graphics history | `editors.py:403-414` now routes by mode, and Layout, Browse and Warps have stacks; `graphics_tab.py:583-585` still installs its own Ctrl+Z beside the shell's `app.py:319` | **RELEASE-BLOCKING** | Threatens the editor UX path a v1.0 user meets: two undo systems over one document, one of them unreachable from the shell. Two of three halves are already fixed, so the residue is bounded. |
| 24 | `CQA-24` | MEDIUM: "Revert unapplied" discarded pending colours but left Apply enabled and the list on screen | `graphics_tab.py:1574-1582` clears pending, repopulates and calls `_refresh_pending_ui()` | CLOSED | The refresh-call remediation is present. |
| 25 | `CQA-25` | MEDIUM: shell undo lambdas raised an unhandled exception on every shutdown with a wired history | `app.py:645-658` catches `RuntimeError` and disables the actions; `:663-674` tracks every stack in a set | CLOSED | The escaping traceback is contained and the single-flag defect is fixed. |
| 26 | `CQA-26` | MEDIUM: SDK failures rendered as plausible zero/empty values instead of errors | `map_browser_tab.py:4367,4371` return `0`; `:3546` and `:5331` render that `0` as "an empty cell" | **RELEASE-BLOCKING** | Threatens the Maps editor path and the next capability's own surface: a confident falsehood in an authoring view is a data-loss trap. The audit ranked it SHOULD FIX before major new authoring, and the next capability is major new authoring. |
| 27 | `CQA-27` | MEDIUM: layout authoring has no SDK-side session facade, so pending-edit policy lives in a 1,986-line widget | `map_browser_tab.py:5169` `unsaved_edit_count`; `:3253` and `:7849` `_saved` state in the widget; the file is now 7,870 lines | **RELEASE-BLOCKING** | Threatens the same path: unsaved-edit policy that the shell cannot see is how authored work is lost. It has grown, not shrunk, and the next capability extends this editor. |
| 28 | `CQA-28` | LOW: six definitions referenced nowhere | `write.py:278` `contains_allocated` still has no caller; `map_render.py:801` `load_canonical_rom` is now live at `cli.py:1793,1800` | DEFERRED | Dead-code hygiene in a public repo; one of six has since become live. The audit itself said deletion should be deliberate. |
| 29 | `CQA-29` | LOW: publication uses `os.link`, which fails on FAT/exFAT and some network shares | `write.py:1379` `os.link(temporary, path)`; rollback `:1381-1385` intact, staged temps always unlinked `:1386-1388` | DEFERRED | Fails closed with no leftovers. A usability ceiling, not a corruption path. |
| 30 | `CQA-30` | LOW: Windows/platform assumptions - trailing-dot `--out`, unvalidated profile id in the output filename, hard-coded checkout paths | `git grep` for `[A-Za-z]:[\\/]+Users`, `AppData`, `OneDrive`, `/home/`, `/Users/` returns 6 lines, none a leak: one synthetic control and five detector definitions. QA and runtime offenders now read `WINDIR` or carry standard-install defaults. `build_panel.py:55` still interpolates `profile_id` | CLOSED | The documented calibration is what separates a per-user path (a leak) from a build path and a doc example. The remaining filename interpolation is covered by CQA-13's deferred family, not by this finding. |
| 31 | `CQA-31` | LOW: Workbench session imports the CLI's private `_default_atlas_directory` | `session.py:24`, used at `:284` | DEFERRED | Real coupling, bounded and harmless while the helper is stable. |
| 32 | `CQA-32` | LOW: repeated whole-table work - `MapLayoutWriter._layer` re-reads all map records per call | `map_layout_write.py:96-112` calls `read_map_entries` per `_layer` call | DEFERRED | Bounded today; becomes a stall only when allocation adds per-cell work. |
| 33 | `CQA-33` | LOW: every over-length text edit re-derives the whole relocation plan, so N edits cost O(N^2) | `text.py` carries no `lru_cache` or `_cache`; the cited lines no longer exist after the module's rework | DEFERRED | Fails safe and costs latency only. Line-level re-measurement was not possible; recorded as UNVERIFIED detail in section G. |
| 34 | `CQA-34` | LOW: a shared graphic's dimensions and depth come from the first consumer and are never reconciled | `graphics.py:300-323` takes `first = refs[0]` with no reconciliation step | DEFERRED | Whether the canonical corpus contains a divergent pair remains UNKNOWN; needs the ROM. |
| 35 | `CQA-35` | LOW: the one authorable dialogue target's numeric fields live in code and the GBA-window arithmetic is hand-rolled | `compressed_dialogue.py:56` imports `GBA_ROM_BASE`, no `0x08000000` literal remains; `:277-279` still hard-codes the target tuple | DEFERRED | The hand-rolled arithmetic that made it SHOULD FIX is fixed; the remaining literal is data-placement hygiene. |
| 36 | `CQA-36` | LOW: seed rows cite `config/roms.yaml` by line number and feed CONFIRMED atlas coverage; citations had already drifted | 17 such citations in `seed.py`. Provably wrong and worse than recorded: `seed.py:504` cites `config/roms.yaml:47` for `enemy_stats`, but `:47` is `count: 452` under `map_entries` and `enemy_stats:` begins at `:49` | DEFERRED | Evidence-integrity debt on a research artifact consumed by the Atlas browser, not a runtime break. It has drifted further since the audit; no gate validates these citations. |
| 37 | `CQA-37` | LOW: `image[dialog + 2]` indexed without a bound check, raising a raw `IndexError` | `formats/placement_links.py:240` unguarded | DEFERRED | Loud failure, LOW as recorded. |
| 38 | `CQA-38` | LOW: the PNG reader verifies no chunk CRC and inflates with no output bound | `formats/indexed_png.py:158` `zlib.decompress(...)` unbounded; the writer emits CRCs at `:52` | DEFERRED | Malformed-input robustness bound with no shipping-path corruption. |
| 39 | `CQA-39` | LOW: docstring claims a caller cannot get a plausible offset out of an opaque slot, but `source_file_offset` is unconditional | `formats/map_slots.py:167`, `:171` | DEFERRED | Documentation overclaim only. |
| 40 | `CQA-40` | LOW: a data table with documented-UNKNOWN extent is indexed as production truth for relocation anchors and Thumb fetches | UNVERIFIED: the cited UNKNOWN-extent assertion was not located at its current line | DEFERRED | Carried without a closure claim. The finding is not refuted and not confirmed this pass. |
| 41 | `CQA-41` | LOW: the `writer` gate is a filename heuristic, so write-path tests with unrelated names carry only `-m fast` | `tests/gates.py:51-109` still fnmatch on filename; `tests/unit/test_asset_export_strict_lz.py` matches no writer pattern | DEFERRED | `fast` is all of `tests/unit` and CI runs `tests/unit`, so nothing escapes the pipeline; only a developer's blast-radius run is affected. |
| 42 | `CQA-42` | LOW: `scripts/test.ps1` runs the bare ~90-minute full suite with no gate selection | `scripts/test.ps1:9` `& $Python -m pytest`; `docs/testing.md:3-5` states the policy it contradicts | DEFERRED | Developer wall clock, not a shipped property. |
| 43 | `CQA-43` | LOW: a test asserted exact English phrases in the policy files and counted as passing | File absent from the baseline tree; merge `3dc606b` is an ancestor | CLOSED | Closed by removing the file, exactly as the finding records. |
| 44 | `CQA-44` | LOW: the property sweep is derandomized at a fixed 50 examples and nothing raises `WEBFOOT_PROPERTY_EXAMPLES` | `test_write_invariants_property.py:48-60` default `"50"`, `derandomize=True`; no test sets the variable | DEFERRED | Frozen discovery power with no shipping path. |
| 45 | `CQA-45` | LOW: View then Detailed Editor follows an editor switch but not the Maps mode change it depends on | `app.py:616-617` `_sync_scene_action`, called at `:481`; `_maps.modeChanged` `:168` is wired only to `_refresh_undo_actions()` | DEFERRED | The mode-change dependency is still not the trigger. |
| 46 | `CQA-46` | LOW: `projectChanged` in the map browser was declared and wired but never emitted | `map_browser_tab.py:1740` signal, emitted at `:4597` and `:7728` | CLOSED | The signal is now emitted. |
| 47 | `CQA-47` | LOW: the atlas browser error path dereferences `self._host` unguarded | `atlas_browser.py:55` `self._host = None`; unguarded `set_status_text` at `:176,197,213,236,245` | DEFERRED | Only reachable when the tab is built without a host. |
| 48 | `CQA-48` | LOW: ROM-format constants and offset formatting in view code | `map_browser_tab.py:1332,1335` literal `256` geometry in the grid painter | DEFERRED | Layering smell, no correctness defect. |
| 49 | `CQA-49` | LOW: the placement workspace renders from `session.rom_image` where the contract says `map_image`; latent | `map_tab.py:936` guards on `maps is None`; `:947` renders from `rom_image` | DEFERRED | Unchanged and still latent for exactly the reason the audit gave. |
| 50 | `CQA-50` | LOW: duplicated UI state - two `selected_map` writers, the map-support label built twice, two differing role-to-colour tables | UNVERIFIED: `theme.state_color` is still defined and unreferenced; the other two claims were not traced | DEFERRED | Carried without a closure claim. |
| 51 | `CQA-51` | LOW: `QTimer.singleShot` callbacks hold widgets with no receiver context, so a timer can fire into a destroyed object | Two-arg sites at `map_tab.py:970,1555`, `launcher.py:232`, `graphics_tab.py:801,827,856,929` | DEFERRED | The pattern persists at new sites; the audit's line numbers are stale, the pattern is not. |
| 52 | `CQA-52` | LOW: the status line is set locally without publishing to the shell, so the authoritative status bar can go stale | UNVERIFIED: the Graphics half appears addressed (`graphics_tab.py:1595-1596`); the map-browser publish path was not traced | DEFERRED | Carried without a closure claim. |
| 53 | `CQA-53` | INFO: the allocator is single-sourced (positive control) | `tools/webfoot/allocation.py` present | CLOSED | Informational control with no defect. |
| 54 | `CQA-54` | INFO: `docs/workbench.md` still described the removed eight-tab shell | `docs/workbench.md:23-27` names four primary editors plus the Maps modes; no "eight" match | CLOSED | Not reproducible. |
| 55 | `CQA-55` | INFO: verified-sound catalogue recorded so it is not re-litigated | Audit `:189-203` and `:1356` | CLOSED | Informational control list with no defect. |
| 56 | `CQA-56` | INFO: a second expanding domain has no coordinator; nothing merges two domains into one `GeneratedImage` | Audit `:1357`; not re-measured | DEFERRED | Explicitly "not a defect"; a prerequisite to design for when a second domain expands. |
| 57 | `CQA-57` | INFO: host-side decoder bounds cap declared output and packed input at 64 KiB | Audit `:1358`; constants not re-read this pass | DEFERRED | A documented ceiling a capacity feature must revisit deliberately rather than discover. |
| 58 | `CQA-58` | INFO: audit-method note - a mutation experiment edited `write.py` in the shared audit checkout and was reverted | Audit `:1359` | CLOSED | Process note; the checkout was clean as recorded. |
| 59 | `ROM-CAPACITY-ATLAS-SEED-OVERLAY-001` | debt recorded at the CQA closeout, no severity: the atlas seed records four SDK-authored derivative structures inside the canonical free window `[0x7EA400,0x7EA500)`, so a canonical atlas disagrees with the canonical free declaration | `docs/research/ROM_CAPACITY_AND_ALLOCATION.md:519-554`; `docs/ROADMAP_TO_1_0.md:733-734` | DEFERRED | The roadmap lists it as known open debt and records that the allocator deliberately does not use the atlas seed as free-space authority. |
| 60 | `REJECTED-WORKBENCH-CANNOT-REOPEN` | rejected at verification: the Workbench "cannot reopen its own output" was reported as a provenance defect | Audit `:1600-1606`; `docs/journeys/safe-build-and-derivative-reopen.md:79` - "that refusal is the designed outcome" | SUPERSEDED | Documented, accepted product behaviour. Only the missing provenance document survived, as CQA-12, now closed. |
| 61 | `AUDIT-RECON-01` | not a CQA finding, found by this reconciliation: two tracked public status documents contradicted the registry on the headline capability count and on which capability is next | `docs/ROADMAP_TO_1_0.md` and `docs/PROJECT_STATE.md` said 20/24 and "graphics import NEXT, not started" while `src/data/capabilities.json` and `README.md:87` said 21/24 with graphics import shipped | CLOSED | Fixed by this ticket in the same change: both surfaces corrected to 21/24 and to the next capability, section F. `CONTRIBUTING.md:85-86` is explicit that a stale status page is a release defect, and no gate compares their status claims to the registry (`tests/unit/test_public_surface.py:47-48` only checks that their relative links resolve), which is why it survived. |
| 62 | `PONYTAIL-OVERENGINEERING-001` | read-only over-engineering audit of `tools/webfoot` excluding the workbench, at `origin/master` `4ee7d126`, dated 2026-10-06: verdict "NOT a bloated tree", with seven ranked safe simplifications totalling about 270-310 lines | Durable record: Adja node `047c9b09`. The seven: `commands/randomize.py` re-implements the randomizer run boundary that `randomizer/service.py` owns; nine identical optional-document writers in `project/model.py`; a duplicated `randomize` definition in `enemyrand/service.py:229,241`; byte-identical `canonical_json`/`digest_of` duplicated across two manifest modules; byte-identical `read_map_structure`/`_project_structure` in `map_resize.py:988,995`; two one-line aliases in `build.py:856,903`; a one-module package `commands/`. Its one correctness sub-item (`webfoot randomize --overwrite` could never succeed) was fixed by `RANDOMIZER-CLI-OVERWRITE-001`, merge `0bbab02` | DEFERRED | Real, bounded, non-shipping simplification debt; the audit's own verdict is that the tree is not bloated. No release consequence, and this ticket does not implement cleanup. |
| 63 | `RUNTIME-CROSS-AUDIT-9` | nine nonblocking static-analysis findings carried out of the runtime-foundation cross-audit, explicitly not fixed | Durable record: Adja nodes `f1cbff6c` and `44fb1ba6`. Named: a `.ps1` file-version proof satisfied by the token appearing anywhere in the file; `&&` inside a string literal read as a process start; `.ps1` exemption anchors being the literal `&`; a new launcher in an already-registered file whose argv[0] carries no mGBA text; a second start inside a registered `.ps1`; a stale exemption never flagged; the mGBA trigger reading argv[0] only, which weakens both the exemption table and the anchor guard; registered `.py` sites in a file with no launch of its own being skipped; PowerShell discovery matching the token inside prose | DEFERRED | All are residuals of the AST launch-coverage predicate, which is enforced by `tests/unit/test_mgba_launch_coverage.py` and is strictly stronger than the text scan it replaced. None is reachable as an ungoverned launch today; the ticket's own scope excludes fixing them, and the runtime foundation is closed. |
| 64 | `NIGHTLY-CROSS-AUDIT-001` | LOW, from an automated cross-audit: a docstring claimed the canonical-copy rule was applied at the shared output-safety boundary so every authored-image domain inherits it, but the Workbench confirmed-overwrite path did not go through that boundary and could still unlink a clean canonical copy | Adja node `9c30c05b`. Fixed by `WORKBENCH-OVERWRITE-CANONICAL-GUARD-001`: merge `ad96227`, commit `8291f71`, which adds `refuse_canonical_destination` to `build_panel._on_build` ahead of the first unlink, with its own RED-at-baseline regression test | CLOSED | The gap the finding named was closed by a later merged ticket with a test that fails at the baseline. |
| 65 | `TOOLKIT031-LOAD-STATE-001` | carried follow-up: `tools/runtime/toolkit031_load_state.ps1:52-90` is a second Scripting-window `SetValue` driver beside the tracked, allowlisted injector | Durable record: Adja task node `62937d26`; `tools/runtime/toolkit031_load_state.ps1` present at the baseline | CLOSED | Resolved by `RUNTIME-LOAD-STATE-ROUTING-001`, which withdrew the second driver to a tracked tombstone (one failing statement) and left the inject-then-load route to the one launch authority, `Start-MgbaSession -StatePath` (`tools/runtime/mgba_session.ps1:146-148`), which runs the load after the observer's `dofile` and before the ready marker is written; the capability is the one `start_toolkit031_session.ps1:117` already asked for. `tools/runtime/README.md` files the tombstone in its retired table with the replacement route, and the `NON_MGBA_SITES` exemption row for its retired `Start-Process` site was removed because the tombstone starts no process. |
| 66 | `CAPTURE-MGBA-EVENT-BUNDLE-001` | carried follow-up: `tools/runtime/capture_mgba_event.py` is not wired for evidence bundles because it never sees the emulator or ROM path | Durable record: Adja node `f1cbff6c`, carried item 2; `tools/runtime/capture_mgba_event.py` present at the baseline | DEFERRED | Covering it needs new launcher-supplied arguments, which the runtime foundation ticket deliberately left out. The three standard probes and both live-watch probes do emit bundles, so the evidence path is not ungoverned. |
| 67 | `ROM-GATED-NOT-IN-CI` | not a numbered CQA finding, recorded in the audit's test and CI observations: the ROM-gated integration suite never runs in CI | `docs/testing.md:18-19` records 985 collected tests needing a canonical local image; `.gitlab-ci.yml:100` runs `pytest tests/unit` only, and `:6-7` says so | DEFERRED | Accepted and documented: no commercial ROM may live in CI. The largest residual in the release family, because a regression only those tests would catch is invisible to the pipeline. The portable write-path tests do run. |
| 68 | `AUDIT-RECON-02` | not a CQA finding, found by this reconciliation: the registry claims `map-browser` reached `proof: runtime` | `src/data/capabilities.json` `map-browser` `proof: "runtime"`. The strongest tracked evidence is a retained VRAM-oracle comparison (`docs/research/MAP_RENDER_FORMAT.md:183-215`, which states the oracle is actual captured engine state) plus read-only visual inspection of generated ROM-only outputs. `docs/research/LOGX_MAP_RENDER_VERIFICATION.md:4` reads "Static analysis only; no runtime capture was made for this pass", and `docs/decisions/0004-proof-levels.md:42-50` separates RENDERER PROOF from RUNTIME PROOF | DEFERRED, owner decision | Deliberately **not** changed by this ticket. ADR 0004's `runtime` projection means the RUNTIME level was reached, and its worked example is about an authored result, while `map-browser` is a read capability whose rendering was checked against captured engine state. Two readings are defensible and one read-only pass could not settle which was intended, so this is recorded for the owner rather than silently downgraded. It changes no count either way. |
| 69 | `AUDIT-RECON-03` | not a CQA finding, found by this reconciliation: the registry told the public site that `sprite-new` is "Not implemented" | `src/data/capabilities.json` `sprite-new` `detail` read "Not implemented. Needs allocation plus same-count in-place replacement of animation cell pointers and frame piece records", and its first limit read "Not implemented, and no editor surface authors a new sprite, animation or frame" | CLOSED | Fixed by this ticket: the record now states that the mechanism, project document and build path are merged and runtime-proven (citing `SPRITE-NEW-RUNTIME-001`, `SPRITE-NEW-AUTHORING-CORE-001`, `SPRITE-NEW-ATTACHMENT-RUNTIME-PARITY-001`, `SPRITE-NEW-PROJECT-SURFACE-001`, `SPRITE-NEW-COMPOSITION-GUARD-001`) and that what is missing is the authoring surface. The counted `state` stays `missing` and the total stays 21, so no public figure changes. |
| 70 | `AUDIT-RECON-04` | not a CQA finding, found by this reconciliation: the registry and `PROJECT_STATE.md` both claimed a 16 MiB derivative cannot be reopened | `src/data/capabilities.json` `chunks` limit 6 and two places in `docs/PROJECT_STATE.md` (`:1761-1764` "Debt retained" and deferred defect 5) stated that the shared derivative verifier reconstructs and hashes the whole file, so an expanded derivative never reopens. `DERIVATIVE-16M-REOPEN-001` (merge `ee0667ac`, commit `bb452504`, ancestor) changed exactly that: the caller states the canonical span and only that span is verified. `tests/unit/test_authored_image.py:500` and `tests/unit/test_map_layout_provenance.py:172` assert a valid expanded derivative verifies and reopens. A fourth survivor, `docs/research/MAP_CHUNK_AUTHORING.md:215-222`, is a research record | CLOSED | Fixed by this ticket: the stale limit was removed from the registry, both survivors in `PROJECT_STATE.md` were replaced by the closed-debt statement naming the ticket and the two tests, and the research record was annotated in the repository's established SUPERSEDED style rather than rewritten, because historical records are not restated. The first review pass caught the second `PROJECT_STATE.md` survivor, which this row now names. |
| 71 | `SPRITE-NEW-REVIEW-GAP-001` | not a CQA finding, found by this reconciliation: no independent review record exists for two of the ten merged sprite-new tickets | `docs/research/SPRITE_NEW_PROJECT_SURFACE.md` and `docs/research/SPRITE_NEW_COMPOSITION_GUARD.md` carry no review section, and a search of `docs/research/` for their ticket names returns no review record. By contrast `SPRITE_NEW_AUTHORING_CORE.md:166` has "## 6. Independent review and its findings" | DEFERRED | The review gate (`docs/REVIEW.md`) applies to code-bearing changes; the two tickets added the project surface and a production guard. Input to the next capability rather than a release blocker: the next ticket extends exactly this path, so its own review must cover the inherited behaviour. Recorded so the gap does not travel silently. |
| 72 | `AUDIT-RECON-05` | not a CQA finding, found by this reconciliation and by the independent review: `sprite-new` might be countable at the same level as the shipped `gfx-import` | `gfx-import` ships with `surface: "Project workflow: extract, edit an extracted sprite PNG, validate, build"` while its own limit records "No editor surface edits pixels yet". `sprite-new` has the same shape except for the entry point: `webfoot extract` (`tools/webfoot/cli.py:520`) produces the PNG `gfx-import` edits, while nothing emits or scaffolds `sprites/sprites.toml` | DEFERRED, owner decision | Recorded rather than buried, because it changes the headline number. This reconciliation keeps 21/24 on the narrower rule that a capability needs a shipped entry point, which `sprite-new` lacks; the full argument and the counter-argument are in section A.3. `docs/capability-registry.md:57` makes shipping a product decision, so the owner settles it. If it went the other way the count would read 22/24 and every surface corrected in section F would have to be restated. |
| 73 | `AUDIT-RECON-06` | not a CQA finding, found by the independent review: `layout` and `tiles` may describe the same write twice | `src/data/capabilities.json` `layout` (one 256x256 chunk-cell reassignment to a chunk the same layer already uses) and `tiles` (click or drag the same replacement onto the same 256x256 unit) describe the same four-byte in-place write reached through the same Maps Layout mode; `tiles` adds multi-cell gestures, undo and an eyedropper | DEFERRED | The registry's decomposition, unchanged by this ticket, and both records are counted as shipped so no total moves. Recorded because "is anything double-counted" is one of the questions this reconciliation had to answer, and the honest answer is that this pair is the closest case and the owner's call. |

### B.3 What this reconciliation does not claim

- **No finding is marked CLOSED on the strength of a later ticket's word.** Every
  `CLOSED` above cites code, a test or a gate read in the baseline tree, or a
  merge verified as an ancestor. Where a finding's original line numbers had
  drifted, the citation is to the baseline line.
- **The three `UNVERIFIED` items are carried, not closed.** Marking them
  `DEFERRED` asserts that they are outside the v1.0 shipping-critical path, which
  is different from asserting they are fixed.
- **Four findings are release-blocking and none of them is implemented here.**
  CQA-11, CQA-23, CQA-26 and CQA-27 respectively threaten the Build/Save As
  publication path, the editor undo contract, the truthfulness of the Maps
  editor's rendered state, and the safety of unsaved layout work. Each is small
  and bounded; each should close before RC/v1.0, and none blocks the next
  capability from starting.

---

## C. Roadmap reconciliation

### C.1 Why the old roadmap said `MAP-CHUNK-AUTHORING-001` was next

It never did, at the baseline. The claim is two planning baselines stale, and
the chain is short:

1. `docs/ROADMAP_TO_1_0.md` was written when Phase 2 map editing had just
   completed. Its status block says 20/24 and names Phase 3A graphics import as
   "NEXT, not started" (`:15`, `:115`, `:288`, `:470-487`, `:905-907`).
2. `MAP-CHUNK-AUTHORING-001` is Phase 2B, and it was recorded COMPLETE on
   2026-09-25 in the roadmap's own phase table (`:285`) and ticket list
   (`:315-316`). The merge is `5948f91`, 2026-09-25.
3. Graphics import then shipped too: `GRAPHICS-IMPORT-BOUNDARY-001`, merge
   `be93182`, 2026-10-03, and the registry recorded it.
4. The registry was updated for that; the roadmap and `PROJECT_STATE.md` were
   not. So the roadmap's headline number and its "next" claim went stale while
   its phase table stayed internally consistent.

`MAP-CHUNK-AUTHORING-001` is therefore **obsolete as future work**, and the
roadmap's "graphics import is next" claim was **already false when the baseline
was frozen**. The old assumption in this ticket's brief that
`MAP-CHUNK-AUTHORING-001` is next is refuted by the roadmap's own text.

The mechanics, measured, because the same failure mode is what let this happen:

- The roadmap was adopted at 16/24 with Phase 1 next (`0d2d6668`, 2026-09-24).
- Tile painting shipped and the roadmap was rewritten to mark 2A complete
  (`c8d7e6bf`, 2026-09-25 05:09), leaving the line "runtime-prove new chunks.
  **NEXT** (not started)".
- Chunk authoring then shipped at 11:48 the same day (`8ef74869`) and the
  registry advanced to 18/24 at 12:14 (`f9d9d029`), but neither commit touched
  `docs/ROADMAP_TO_1_0.md`: only `src/data/project.ts` was updated, the same day,
  by `70b55e48` "Stop the roadmap promising a capability that has shipped".
- The markdown roadmap kept claiming chunks were next for about two days, until
  `6c583d05` (2026-09-27 20:17) recorded Phase 2 complete.
- Graphics import then repeated it: the registry flipped `gfx-import` to shipped
  on 2026-10-02 (`b0bbd994`), merged 2026-10-03 (`be93182`), and the markdown
  roadmap's last status edit was still 2026-09-27. The public site was current
  throughout, because it derives from the registry.

The lesson this reconciliation adds to the repository, rather than a new gate:
the registry-to-site path is machine-checked, and the registry-to-markdown path
is not. Every status edit that moves a capability has to touch
`docs/ROADMAP_TO_1_0.md` and `docs/PROJECT_STATE.md` by hand, and nothing fails
when it does not. That is recorded as finding 61.

### C.1.1 The roadmap's planning baseline

`docs/ROADMAP_TO_1_0.md` records its planning baseline as
`a commit consolidated into a later one`, which is a deliberate placeholder, not
a loss. The reference was first written as a full hash, then named, then replaced
with a null placeholder by `a1c9f04c` and reworded by `20b31182` and `9b20ac35`.

Settled value in the current published history:
**`1977e003449eba40bdc3c9ac1d8c593c18b60ebb`**, the
`dialogue-variable-length-001` merge, whose tree is identical to `16123d78`
"Close variable-length dialogue authoring". The roadmap's own original value was
`d8c82ef6640a1eb786ec40223f3538e7b8cf8634`, which **still resolves locally but is
not an ancestor of the baseline** (`git merge-base --is-ancestor` exits 1): it
survives only on stale ticket branch refs, because the published history was
rebuilt and the adoption commit now sits directly on `1977e003`.

This is why the retired ledger cannot be recovered from git (see section B.1).
The same rebuild is why a historical SHA quoted in a durable record can name an
object that no longer sits on any published branch, and why the repository
replaced those references with a placeholder on purpose. Historical documents
that quote a superseded SHA are not wrong; they are records of the tree they were
written against.

### C.2 Merged work that changed authoring capability

First-parent merges on the baseline's master line, latest first. Only merges
that moved a capability or materially changed an authoring path are listed.

| Ticket | Merge | Date | Capability moved |
| --- | --- | --- | --- |
| `RUNTIME-INSTRUMENTED-CAPTURE-CLOSURE-001` | `67e0c27` | 2026-10-07 | none; runtime proof closure, see section D |
| `RUNTIME-FOUNDATION-CONSOLIDATION-001` | `b943d13` | 2026-10-07 | none; runtime infrastructure, see section D |
| `RUNTIME-MGBA-IDENTITY-GATE-SWEEP-001` | `5e4f50e` | 2026-10-07 | none; runtime infrastructure |
| `RUNTIME-LUA-INJECTOR-CONSOLIDATION-001` | `278374b` | 2026-10-07 | none; runtime tooling |
| `RUN-CONFIG-ROM-PICKER-001` | `333b1b8` | 2026-10-07 | `launch` strengthened |
| `WORKBENCH-CANONICAL-OVERWRITE-GUARD-001` | `ad96227` | 2026-10-06 | `save-as`; closes audit finding 64 |
| `AUTHORED-SAVE-AS-CANONICAL-GUARD-001` | `464e88b` | 2026-10-06 | `save-as` |
| `RANDOMIZER-CLI-OVERWRITE-001` | `0bbab02` | 2026-10-06 | none; closes the correctness sub-item of finding 62 |
| `WARP-CREATION-ARRIVAL-WIRING-001` | `4127101` | 2026-10-06 | `warps` |
| `WORKBENCH-OVERWRITE-ATOMICITY-001` | `32f3f80` | 2026-10-06 | `validate` and `save-as` |
| `SPRITE-NEW-COMPOSITION-GUARD-001` | `4ee7d12` | 2026-10-05 | `sprite-new` (partial) |
| `SPRITE-NEW-PROJECT-SURFACE-001` | `954a402` | 2026-10-05 | `sprite-new` (partial) |
| `SPRITE-NEW-ATTACHMENT-RUNTIME-PARITY-001` | `aba1257` | 2026-10-05 | `sprite-new` (partial) |
| `SPRITE-NEW-ATTACHMENT-CORE-001` | `144d06b` | 2026-10-05 | `sprite-new` (partial) |
| `SPRITE-NEW-PARITY-HYGIENE-001` | `5f3fab5` | 2026-10-04 | `sprite-new` (partial) |
| `SPRITE-NEW-RUNTIME-PARITY-001` | `215dc77` | 2026-10-04 | `sprite-new` (partial) |
| `SPRITE-NEW-AUTHORING-CORE-001` | `4054152` | 2026-10-04 | `sprite-new` (partial) |
| `SPRITE-NEW-MOVEMENT-DATA-001` | `70dacdd` | 2026-10-04 | `sprite-new` (partial) |
| `SPRITE-NEW-BEHAVIOR-001` | `64acf63` | 2026-10-04 | `sprite-new` (partial) |
| `SPRITE-NEW-RECORD-RUN-001` | `0ff29c1` | 2026-10-04 | `sprite-new` (partial) |
| `EXE-FUTURE-GUARD-001` | `7ce5b7b` | 2026-10-03 | none; release guard |
| `GRAPHICS-IMPORT-BOUNDARY-001` | `be93182` | 2026-10-03 | **`gfx-import` shipped, 20/24 to 21/24**; the registry record flipped on 2026-10-02 (`b0bbd994`) |
| `DERIVATIVE-16M-REOPEN-001` | `ee0667ac` | 2026-09-28 | `provenance`: the verifier now checks only the profile's canonical span, so an expanded derivative reopens. Closes finding 70 |
| `PUBLIC-REPO-HARDENING-001` | `3dc606b` | 2026-10-02 | none; tree, gates and public surface. The retired `docs/tickets/` ledger and `AI_SURFACE_AUDIT.md` are outside the baseline's reachable history |
| `CQA-05-06-WORKBENCH-STATE-AND-ERRORS-001` | `28f8290` | 2026-09-25 | none; closes findings 5 and 6, and is the safety gate the map editors were built on |
| `CQA-07-08-WORKBENCH-PERF-AND-CI-001` | `469d853` | 2026-09-25 | none; closes findings 7 and 8, and makes CI execute the shipping GUI surface |
| `MAP-WARPS-AND-CONNECTIONS-001` | `cdbe51c` | 2026-09-28 | **`warps` shipped, 19/24 to 20/24** |
| `MAP-RESIZE-AND-LAYERS-001` | `ad03b89` | 2026-09-26 | **`resize` shipped, 18/24 to 19/24** |
| `MAP-CHUNK-AUTHORING-001` | `5948f91` | 2026-09-25 | **`chunks` shipped, 17/24 to 18/24** |
| `MAP-TILE-PAINT-001` | `f5c2b99` | 2026-09-25 | **`tiles` shipped, 16/24 to 17/24** |
| `DIALOGUE-VARIABLE-LENGTH-001` | `1977e00` | 2026-09-25 | `dialogue` strengthened, no denominator move |
| `AUTHORED-IMAGE-PIPELINE-001` | `cd49aa5` | 2026-09-20 | `save-as`, `provenance` |
| `PLACEMENT-POS-001` | `8616413` | 2026-09-15 | `placement` |
| `WORKBENCH-006` | `55a5681` | 2026-09-14 | `shell`, `placement` |
| `WORKBENCH-001` | `16ba237` | 2026-09-12 | `shell`, `atlas`, `inspector`, `validate`, `launch` |

Two things this chronology shows that the roadmap could not: every Phase 2
capability landed inside four days (2026-09-25 to 2026-09-28), and Phase 3 work
then ran ahead of its own plan, with graphics import on 2026-10-03 and the whole
sprite-new family on 2026-10-04/05.

### C.3 Classification of every previously planned remaining capability

| Planned item (roadmap name) | Classification | Evidence |
| --- | --- | --- |
| Phase 2A tile painting (`MAP-TILE-PAINT-001`) | SHIPPED | `f5c2b99` 2026-09-25; `tiles` shipped, runtime-proven |
| Phase 2B chunk creation (`MAP-CHUNK-AUTHORING-001`) | SHIPPED | `5948f91` 2026-09-25; `chunks` shipped, runtime-proven |
| Phase 2C resize and layers (`MAP-RESIZE-AND-LAYERS-001`) | SHIPPED | `ad03b89` 2026-09-26; `resize` shipped, runtime-proven |
| Phase 2D warps and connections (`MAP-WARPS-AND-CONNECTIONS-001`) | SHIPPED | merges through `cdbe51c` 2026-09-28; `warps` shipped, runtime-proven |
| Phase 3A graphics import (`GRAPHICS-IMPORT-001`) | SHIPPED, under a different ticket name | `GRAPHICS-IMPORT-BOUNDARY-001`, merge `be93182` 2026-10-03; `gfx-import` is `shipped` in the registry with `proof: runtime` |
| Phase 3B sprite and animation authoring (`SPRITE-ANIMATION-AUTHORING-001`) | **PARTIALLY SHIPPED** | Ten merged `sprite-new-*` tickets built the mechanism, the project model, the build path and a runtime proof, but there is no authoring surface and the composition budget is unmodelled; `SPRITE_NEW_PROJECT_SURFACE.md:181-187` states the capability is still not shipped |
| Phase 3C appearance authoring (`APPEARANCE-AUTHORING-001`) | STILL MISSING | `appearance` is `missing`; whether the table can be grown at all is unresolved, so this is an open question rather than a scheduled task |
| Phase 4 new map authoring (`MAP-AUTHOR-NEW-001`) | STILL MISSING | `map-new` is `missing`; the terminal frontier, blocked on map-root fields that remain unresolved |
| Phase 1 CQA-05/06 workbench state and errors | SHIPPED | merges `28f8290`; audit `:1519-1520`; findings 5 and 6 CLOSED |
| Phase 1 CQA-07/08 workbench perf and CI honesty | SHIPPED | merge `469d853`; audit `:1521-1522`; findings 7 and 8 CLOSED |
| `ROM-CAPACITY-ATLAS-SEED-OVERLAY-001` | STILL MISSING | Finding 59, DEFERRED; deliberately not consumed by the allocator |
| Phase 0 landing (`DIALOGUE-VARIABLE-LENGTH-001`) | SHIPPED | `1977e00` 2026-09-25 |
| Phase 5 creator UX and RC | STILL MISSING | No ticket started; unchanged by this ticket |
| Phase 6 v1.0 shipping gate | STILL MISSING | Four release-blocking findings remain (section B.2) plus the release family's deferred items |
| Any remaining runtime-foundation or infrastructure ticket | SUPERSEDED BY LATER WORK | Runtime foundation is closed, section D. No forward document names runtime-foundation work: `grep` for `RUNTIME-FOUNDATION` or `RUNTIME-INSTRUMENTED` matches nothing in `docs/ROADMAP_TO_1_0.md`, and the only other tracked occurrences are provenance comments describing closed work (`tests/unit/test_mgba_instrumented_identity.py:3`, `tools/runtime/evidence_bundle.py:3`) plus this document's own rows. It must not re-enter the forward queue. |

### C.4 Roadmap items that were completed under a different name

- Graphics import: planned as `GRAPHICS-IMPORT-001`, delivered as
  `GRAPHICS-IMPORT-BOUNDARY-001`, with the evidence in
  `docs/research/GRAPHICS_PIXEL_OVERRIDE.md`. The audit-boundary name is the one
  the registry cites, so the roadmap's proposed name was never used.
- Sprite and animation authoring: planned as `SPRITE-ANIMATION-AUTHORING-001`,
  in practice delivered as ten `SPRITE-NEW-*` tickets. The capability id in the
  registry is `sprite-new`.
- The CQA Phase 1 items: planned as `CQA-05-06-WORKBENCH-STATE-AND-ERRORS-001`
  and `CQA-07-08-WORKBENCH-PERF-AND-CI-001`, both delivered under exactly those
  names.

### C.5 The other forward queue

`docs/research/POST_LOGX_IMPLEMENTATION_ROADMAP.md` still exists and is still
cited by the registry (`sprite-new` and `map-new` both name it in `evidence`),
while `docs/ROADMAP_TO_1_0.md` demotes it to an implementation queue. Its items
classify as follows, and this is the last place an abandoned forward plan could
hide.

| Queue item | Classification | Evidence |
| --- | --- | --- |
| `FIX-1`, `FIX-2`, `FIX-5` | SHIPPED | Its own status rows, executed 2026-09-20 by `EVIDENCE-RISK-DEBT-001`, before the planning baseline |
| `FIX-3` count-bounded animation traversal | STILL MISSING | Status row says NOT STARTED; `docs/PROJECT_STATE.md` still lists the unbounded `_animations_in` walk as deferred defect 1 |
| `FIX-4` multipart-aware OAM path | STILL MISSING | `docs/PROJECT_STATE.md` records the multipart composite and replacement path as unbuilt; no status row exists |
| `TOOLS-1` character and appearance inspector | PARTIALLY SHIPPED | The READ family's sprite/animation/palette browsing ships, but one piece per direction slot and no frame compositing |
| `TOOLS-2` multipart sprite and animation preview | STILL MISSING | The `graphics` capability's own limits record that compositing a frame's pieces is not built |
| `TOOLS-3` warp destination inspector and editor | SUPERSEDED BY LATER WORK | Delivered as the Maps editor's Warps mode, `MAP-WARPS-AND-CONNECTIONS-001` `cdbe51c` |
| `TOOLS-4` warp randomizer | SHIPPED, outside this denominator | `WARPRAND-APP-001`, merge `781d4e71`; it is a separate product, not one of the 24 capabilities |
| `TOOLS-5`, `NEW-1`, `NEW-2` animation and sprite authoring | PARTIALLY SHIPPED / SUPERSEDED BY LATER WORK | The `sprite-new` family delivered the mechanism through a project document and production planners instead of a table-expansion editor |
| `WRITE-4` graphics replacement and insertion | SHIPPED | `GRAPHICS-IMPORT-BOUNDARY-001` `be93182` |
| `NEW-3` new appearance definition | STILL MISSING | The `appearance` capability is `missing` and table growth is unresolved |
| `NEW-4` arbitrary new warp authoring | PARTIALLY SHIPPED | Creation ships for the 566-class family; the 169-class family is refused, and the registry says so |
| `NEW-5` new map and scene | STILL MISSING | The `map-new` capability is `missing` |
| `WRITE-1`, `WRITE-2`, `WRITE-3` raw container writer, packed encoder, allocator integration | NOT SETTLED | No status row in the queue, and the registry's `researchOnly` note still says no packed-container encoder ships. Recorded as unsettled rather than guessed; see section G |

None of the still-missing queue items is a denominator capability. They are
either prerequisites to the three remaining capabilities or work the later
architecture made unnecessary.

---

## D. Completed infrastructure

This work is DONE. It is recorded here as infrastructure, and it is explicitly
**not** counted as capability progress. None of it moved the 21/24 score, and
none of it belongs in the forward implementation queue.

| Infrastructure | State | Evidence at the baseline |
| --- | --- | --- |
| mGBA identity governance | Complete | `tools/runtime/mgba_identity.py`: `LAUNCH_SITES` (31 entries over 30 files) with a `proof` field per site; `require_mgba_build` hashes the executable and fails closed on a mismatch; `tools/mgba_probe/runtime.py` `verify_instrumented_mgba` carries the separate instrumented policy |
| Governed launch inventory | Complete | The same registry, named in `tools/runtime/README.md` as the registry of every repository-controlled place an mGBA process can start; enforced by `tests/unit/test_mgba_launch_coverage.py` (an AST predicate), `test_mgba_launch_sites.py` and `test_mgba_identity_gate.py`, all under `tests/unit` so CI executes them |
| Instrumented provenance | Complete | `tools/mgba_probe/build.ps1` builds the instrumented executable from a pinned source commit plus a tracked patch; the manifest records both digests and the build refuses a superseded patch by name |
| `log1-runtime-evidence/1` | Complete | Schema constant defined once in `tools/runtime/evidence_bundle.py:48`; deterministic JSON, UTF-8 without BOM, measured ROM and emulator identity, `repository.dirty` nullable, a missing artifact omitted rather than given an unmeasured digest |
| Offline evidence inspection | Complete | `tools/runtime/evidence_report.py` reads one bundle with zero emulator processes created; an absent artifact prints "absent" and a file with no recorded digest claims neither match nor mismatch |
| Completed native instrumented capture | Complete | One native instrumented probe ran to completion in 13.9 s. Recorded values, sourced from the durable record rather than the tracked tree (see the note below) |
| Runtime foundation closure | Complete | `RUNTIME-INSTRUMENTED-CAPTURE-CLOSURE-001` merged as `67e0c27`; runtime foundation declared done; no forward document mentions it |

### D.1 The successful instrumented proof

| Field | Value |
| --- | --- |
| executable SHA-256 | `33b2b518ce4b5c4dcd4b6645b914370b21534abe3dadbc71e150521b006b401f` |
| tracked patch | `8ee9d92dd1d69fda96f7c31bc8b10e17d6aa7195b56ab103e56cb5f8d9583346` |
| source commit | `26b7884bc25a5933960f3cdcd98bac1ae14d42e2` |
| result | `FIRST_HIT` |
| event | `1` |
| descriptor | `0x08294948` |
| read | `0x0203DE88` |
| PC | `0x080510AA` |
| evidence schema | `log1-runtime-evidence/1` |

Probe: `python -m tools.runtime.rom011_live_watch run <canonical rom>
build\rom011\human-native-02\input.ss1 <save> --state-sha256
ea500f3a... --save-sha256 9bbd7cb6... --mgba <rebuilt rom011 exe> --manifest
build\rom011\mgba-probe-sdl\log1-probe-build.json --run-root
build\rom011\native-06 --timeout 300`. Phases: capture-ready, then armed 5 s
later, then result and evidence within 3 s. `evidence_report` read the bundle
offline with exit 0 and zero mGBA processes before and after.

**Source note, so the citation is honest.** These values are not in the tracked
tree: the run directory lives under the ignored `build/`, and the closure
commit `969eb7d` changed exactly one file, renaming
`tests/unit/test_mgba_instrumented_identity.py`'s on-disk-artifact test to
`test_the_on_disk_rom011_build_now_matches_the_tracked_patch`. The recorded
values come from the durable session record (Adja node `76e74919`). What the
baseline tree itself proves is the surrounding governance: the schema constant,
the governed inventory, the identity gates, the offline inspector, and the
renamed assertion. Three earlier attempts on other routes never armed, because
the population event needs the game played; that lesson is carried in
`docs/skills/mgba-runtime.md`.

---

## E. Next product capability

**Next product ticket: `SPRITE-ANIMATION-AUTHORING-001`**, completing the
registry capability `sprite-new`, which moves the score to **22 / 24**.

### Why not graphics import

Graphics import already met its acceptance target. `GRAPHICS-IMPORT-BOUNDARY-001`
merged on 2026-10-03 (`be93182`), the registry records `gfx-import` as `shipped`
with `proof: runtime`, and `docs/research/GRAPHICS_PIXEL_OVERRIDE.md` records a
human-operated run in which the retail engine rendered the authored pixels, both
in place and from expanded storage after a rewritten reference. The
`GRAPHICS-IMPORT-001` hypothesis in this ticket's brief is refuted; that work is
history.

### Why sprite authoring is the first genuinely missing capability

Three capabilities remain: `sprite-new`, `appearance`, `map-new`. Order is
decided by dependency, not by preference.

- `sprite-new` is the graphics-side capability that `appearance` composes on.
  The roadmap's own sequence has 3B before 3C for that reason
  (`docs/ROADMAP_TO_1_0.md:489-500`).
- `appearance` is not merely unimplemented, it is unresolved: the registry
  records that the record count appears as compiled-in engine bounds with no
  terminator, so whether the table can be grown at all is an open question
  rather than a scheduled task. Starting there begins with research that may end
  in "this cannot be done in place".
- `map-new` is deliberately last. It composes nearly every other authoring
  system, and the roadmap is explicit that it must not be the place where every
  subsystem is invented at once.
- `sprite-new` is the only one of the three with a proven mechanism already in
  the tree, so its remaining work is engineering with a known shape rather than
  an open question.

### Why it is not already shipped, and what the ticket has to do

Ten merged tickets proved the mechanism. `docs/research/SPRITE_NEW_RUNTIME.md`
records the retail engine resolving a new sprite identity above canonical EOF
and drawing it. What is missing is the product around the mechanism:

1. **An authoring surface.** Today a person hand-writes `sprites/sprites.toml`
   and supplies sheet PNGs. There is no GUI and no CLI subcommand
   (`SPRITE_NEW_PROJECT_SURFACE.md:181-184`). The registry cannot count a
   capability with no surface, which is exactly the rule
   `src/data/project.ts:205-214` enforces.
2. **The frame-composition budget.** Every authored frame currently copies the
   donor's own first frame, so the budget is unchanged rather than modelled, and
   attaching an identity to an actor that draws smaller frames than its donor
   remains the open case (`SPRITE_NEW_PROJECT_SURFACE.md:174-177`). The guard
   admits only the donor's proven composition shape
   (`SPRITE_NEW_COMPOSITION_GUARD.md:23-40`).
3. **A stated position on frame geometry.** Whether an author may choose frame
   geometry, and what the engine's actual composition limit is, is unresolved;
   the honest form is to keep the guard and state the limit, not to claim a
   budget nobody measured.

Item 1 is what turns `RUNTIME PROVEN` into `SHIPPED CAPABILITY`. It is also the
reason the capability stays `missing` until the ticket lands: the roadmap's
definition of done (`docs/ROADMAP_TO_1_0.md:713-732`) requires, at item 1
(`:715-716`), that "A semantic user workflow exists; no manual ROM offset is
required for the supported case", and for `sprite-new` no shipped entry point
exists at all. Finding 72 records the counter-argument and leaves the product
decision to the owner.

### Explicitly not in the next ticket

No graphics import (done), no appearance definitions, no new maps, no runtime
infrastructure, no audit remediation except where the next ticket's own surface
touches it. `CQA-23`, `CQA-26` and `CQA-27` are release-blocking and all three
sit on the Maps and Graphics editor path the next ticket extends; they should be
sequenced deliberately rather than folded in silently.

---

## F. Status surfaces corrected by this ticket

| Surface | Was | Is | Why |
| --- | --- | --- | --- |
| `docs/ROADMAP_TO_1_0.md:15` | 20 / 24 capabilities (83%) | 21 / 24 capabilities (88%) | Registry authority; graphics import shipped 2026-10-03 |
| `docs/ROADMAP_TO_1_0.md:115-129` | 20/24, AUTHOR 3/7, four missing | 21/24, AUTHOR 4/7, three missing | Same |
| `docs/ROADMAP_TO_1_0.md:186-194` | four missing capabilities, graphics import next | three missing capabilities, sprite authoring next | Same |
| `docs/ROADMAP_TO_1_0.md:288`, `:470-487` | Phase 3A NEXT, not started | Phase 3A COMPLETE 2026-10-03; phase 3 started | Merge `be93182` and its runtime proof |
| `docs/ROADMAP_TO_1_0.md:322-323` | `GRAPHICS-IMPORT-001` NEXT | `GRAPHICS-IMPORT-001` COMPLETE; `SPRITE-ANIMATION-AUTHORING-001` NEXT | Same |
| `docs/ROADMAP_TO_1_0.md:642` | Graphics replacement and import: Missing, 3A NEXT | Shipped, Phase 3A complete 2026-10-03 | Same |
| `docs/ROADMAP_TO_1_0.md:666` | Graphics containers: prove at Phase 3A | Phase 3A proven | Same |
| `docs/ROADMAP_TO_1_0.md:894-896` | 20 shipped, next graphics import | 21 shipped, next sprite authoring | Same |
| `docs/ROADMAP_TO_1_0.md:905-907` | Now 20/24, Next graphics import | Now 21/24, Next sprite authoring | Same |
| `docs/PROJECT_STATE.md:2158-2165` | 20/24, four unshipped, next graphics import | 21/24, three unshipped, next sprite authoring | Same |
| `src/data/capabilities.json` `sprite-new` record | `detail` and first limit read "Not implemented" | States that the mechanism, project document and build path are merged and runtime-proven, and that the missing piece is the authoring surface; `evidence` now names the `sprite-new` tickets and runtime records | Finding 69: the mechanism is implemented and runtime-proven (`SPRITE_NEW_RUNTIME.md`, `SPRITE_NEW_ATTACHMENT_RUNTIME_PARITY.md`), so the text was false on a public surface. `state` stays `missing`: there is still no editor surface |
| `src/data/capabilities.json` `chunks` limit 6 | Claimed a 16 MiB derivative is never reopened by the shared derivative verifier | Removed; the limit no longer exists | Finding 70: `DERIVATIVE-16M-REOPEN-001` (`bb452504`) fixed exactly that, with tests at `test_authored_image.py:500` and `test_map_layout_provenance.py:172` |
| `docs/PROJECT_STATE.md` deferred defect list | Item 5 claimed the same 16 MiB reopen limitation | Item struck, the list renumbered, and a note records that `DERIVATIVE-16M-REOPEN-001` fixed it and which tests pin it | Finding 70 |

Not changed, deliberately:

- `src/data/capabilities.json` counted states, `proof` levels and measurements.
  No `state` moved, so the total stays 21 and **no public capability figure
  changes**. `AUDIT-RECON-02` records why the `map-browser` `proof` level was
  left alone: two readings of ADR 0004 are defensible and the choice is the
  owner's, not this ticket's.
- `src/data/project.ts` and every `src/components/*.astro` surface. They already
  agree with the registry, and the rendered count is derived rather than written.
- `README.md` and `CHANGELOG.md`, which already read 21/24.
- `docs/research/MAP_WARPS_*.md` and `MAP_WARP_*.md`, which record 20/24 as a
  past-tense measurement of that session. Historical documents remain
  historical. They are not restated, and they are not wrong.
- `docs/ROADMAP_TO_1_0.md`'s per-phase progress column for phases 2A to 2D
  (17/24, 18/24, 19/24, 20/24), which are the counts at each of those completed
  phases.
- The roadmap's planning-baseline placeholder (`a commit consolidated into a
  later one`), which is deliberate. The settled value is recorded in C.1.1.
- Any historical ticket record. `docs/tickets/` is absent at the baseline and is
  not restored by this ticket.

---

## G. Limits of this reconciliation

Measured, then stated plainly so nothing here is read as stronger than it is.

- **The Ponytail backlog does not exist as tracked records.** Its name appears
  nowhere in the baseline tree, and the only Ponytail review of substance is the
  read-only over-engineering audit recorded as finding 62, which lives in the
  durable record rather than in git.
- **The CQA closeout documents are unrecoverable from the baseline.** No commit
  reachable from the baseline ever named `docs/tickets/` or
  `docs/research/AI_SURFACE_AUDIT.md`. Seventeen of the `CLOSED` dispositions in
  section B lean on the audit's own remediation table and on the presence of the
  named guards rather than on a re-run mutation proof. That is evidence, but it
  is not the same as re-executing each proof.
- **Three findings could not be re-measured** (CQA-40, CQA-50, CQA-52) and are
  carried as `DEFERRED` with no closure claim.
- **Four re-judgements moved a finding down** from the first inventory's
  release-blocking rating: CQA-13, CQA-14, CQA-19 and CQA-20. Each is recorded
  with the reason, and the strongest counter-argument is that the audit itself
  ranked them SHOULD FIX. They are not closed, only carried.
- **No hostile input was measured for CQA-19**, and no emulator run, test suite
  or site build was executed by the investigators. Validation of the changed
  documentation surfaces is recorded in the ticket closure, not here.
- **The capability measurement is a registry-and-evidence measurement, not a
  re-execution of each runtime proof.** `runtime` claims were checked against
  the existence of their evidence records; they were not re-run.
- **`map-browser`'s proof level is not settled** (finding 68). The tracked
  evidence is a retained VRAM oracle, which `MAP_RENDER_FORMAT.md` states is
  actual captured engine state, compared against the ROM-only renderer. Whether
  that is the intended meaning of `runtime` for a read capability, under an ADR
  whose `runtime` level is defined around observing an authored result, is an
  owner decision. It changes no count either way.
- **Two of the ten merged `sprite-new` tickets carry no independent review
  record** (finding 71), which matters because the next capability extends
  exactly that path.
- **`POST_LOGX` `WRITE-1`, `WRITE-2` and `WRITE-3` are recorded as not settled**
  (section C.5) rather than resolved. Settling them needs the codec and write
  planner read end to end, which no investigator did.
- **The four investigator reports are the evidence behind sections A to C**, and
  they disagreed in four places. Each disagreement was re-judged here and the
  reason is recorded in the finding's row: CQA-13, CQA-14, CQA-19 and CQA-20 were
  rated release-blocking by the inventory pass and carried as deferred after a
  measurement of their blast radius. Nothing was dropped in the reconciliation.
- **One independent review pass follows this document** and its verdict is
  recorded below, not silently absorbed.

---

## H. Independent reconciliation review

One review pass, by a fresh-context reviewer that did not write any of it, against
the baseline and the uncommitted diff. **Verdict: `BLOCKING`.** Its ten questions
were answered as follows, and its findings were dispositioned rather than argued
with.

| Question | Reviewer verdict |
| --- | --- |
| Every finding accounted for exactly once | YES: 73 rows, unique ids, rows 1 to 58 are `CQA-01` to `CQA-58` in order |
| Any `CLOSED` still reproducible | NO; 12 of them re-verified by reading the cited code or test |
| `SUPERSEDED` abused | NO; the one remaining row reproduces the audit's rejected finding accurately |
| Anything `DEFERRED` on the v1.0 path | NO; all four release-blocking rows verified live in code |
| 21/24 supported by implementation and acceptance evidence | YES for the registry's own rule and 20 of 21 records; `sprite-new` was the contested row and its argument had to be corrected |
| Any capability double-counted or counted without a surface | No surface-less shipped record by construction; the `layout`/`tiles` overlap is the closest case, now recorded as finding 73 |
| Later tickets completed roadmap work under different names | YES, and stated correctly; `be93182` and all ten `SPRITE-NEW-*` merges verified as ancestors |
| The next capability is genuinely the first missing one | YES, on dependency: `sprite-new` has a merged mechanism and runtime proof, `appearance` is unresolved, `map-new` is terminal |
| Runtime-foundation work gone from the forward roadmap | YES in substance; the reconciliation's own grep wording was wrong and is corrected |
| Any reason graphics import should not be next | NO; its shipped claim is sound (`GRAPHICS_PIXEL_OVERRIDE.md:89-96`, `:117`, `:175-176`) |

Findings and their resolutions:

| # | Severity | Finding | Resolution |
| --- | --- | --- | --- |
| 1 | **BLOCKING** | `docs/PROJECT_STATE.md:1761-1764` still read "**Debt retained:** a 16 MiB derivative is not reopened ...", a live present-tense contradiction of the section-F correction | Fixed: replaced with a closed-debt statement naming `DERIVATIVE-16M-REOPEN-001` and the two tests. Finding 70's row now names all surviving copies, and `docs/research/MAP_CHUNK_AUTHORING.md:215-222` is annotated as SUPERSEDED. The reviewer was right that only one of the two survivors had been struck |
| 2 | **BLOCKING** | The justification for keeping `sprite-new` at `missing` cited the roadmap's definition of done at the wrong lines, paraphrased its first item as "no manual file editing", and argued that no surface could be named while `gfx-import` ships on a project-workflow surface | Fixed: the definition of done is cited at `docs/ROADMAP_TO_1_0.md:713-732` with item 1 quoted exactly, the surface-string argument is replaced by the real rule (a shipped entry point; `webfoot extract` produces what `gfx-import` edits and nothing produces `sprites/sprites.toml`), and the counter-argument is recorded openly as finding 72 and left to the owner |
| 3 | NONBLOCKING | The claim that a `docs/` grep for `RUNTIME-FOUNDATION` returns no match was false in the tree containing the claim | Fixed in section C.3: no match in the roadmap, with the two provenance comments named |
| 4 | NONBLOCKING | "no gate reads these two files" was false; `test_public_surface.py:47-48` lists both in its front-door set | Fixed: the accurate claim is that no gate compares their status claims to the registry |
| 5 | NONBLOCKING | The "not shipped" quote was cited at `SPRITE_NEW_PROJECT_SURFACE.md:185-187` instead of `:18-19` | Fixed in section A.3 |
| 6 | NONBLOCKING | `CQA-19` marked `SUPERSEDED` overstated the bound: `_marker_scan_limit` applies only under `require_end_marker`, and the default decode path has no input bound | Fixed: `CQA-19` is now `DEFERRED`, with the conditional bound and the unbounded default path both stated |
| 7 | NONBLOCKING | `docs/research/MAP_CHUNK_AUTHORING.md:215-222` still recorded the 16 MiB limit as live | Fixed by in-place SUPERSEDED annotation, the repository's established pattern, rather than by rewriting the research record |
| 8 | NONBLOCKING | `b4ca061` in the `map-browser` evidence cell is not an ancestor of the baseline, breaking the table's own legend | Fixed: the cell cites `ff4a1fb4` (2026-09-19), verified as an ancestor and the real baseline delivery |
| 9 | NONBLOCKING | The document promised a review verdict "below" with nothing below, and counted five investigators against four reports | Fixed: section H is this section, and the introduction now says four investigators plus one review |
| 10 | NONBLOCKING | The proof legend asserted an engine observation while row 68 says the `map-browser` evidence is a retained oracle and read-only inspection | Fixed: the legend now says a contested registry value is printed and recorded, and row 5 points at finding 68 |
| 11 | NONBLOCKING | `layout` and `tiles` may describe the same write twice | Recorded as finding 73, unchanged, owner's decomposition |

The reviewer also confirmed the parts that matter most to this ticket: no live
status surface still disagrees with the registry, no em dash or en dash was
introduced, no capability number moved other than 20 to 21 and its derivatives, and
the five evidence labels added to the registry all resolve in tracked documents, so
`tests/unit/test_capability_registry.py:313-328` still passes.

Reviewer's own unverified list, carried verbatim in substance: no suite, site
build, emulator or ROM-gated test was run by the reviewer; `CQA-40`, `CQA-50` and
`CQA-52` stay unverified; 17 `CLOSED` rows rest on the audit's remediation table
plus the presence of the named guard rather than on a re-executed proof; the
`POST_LOGX` `WRITE-1`, `WRITE-2` and `WRITE-3` items stay unsettled; and the retired
ledger remains unrecoverable from git.
