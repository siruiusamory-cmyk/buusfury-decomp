# PROJECT-CODE-QUALITY-AUDIT-001 - whole-project code quality / failure-mode audit

- **Baseline audited:** `origin/master` at `1b276e3fe3b8b3170618567bd5a4306e79a2cea2`
  (the merged closeout of DRAGONBYTE-Z-VISUAL-DIRECTION-PASS-001).
- **Audit worktree:** `<temp>\log1-remake-cq-audit-001`, detached at that SHA,
  created for this ticket. The dirty WORKBENCH-006 checkout was never read as
  the baseline and was never touched.
- **Ticket:** see [`../tickets/PROJECT_<local-state-name>`](../tickets/PROJECT_<local-state-name>) and the review
  record [`../tickets/PROJECT-CODE-QUALITY-AUDIT-001-review.md`](../tickets/PROJECT-CODE-QUALITY-AUDIT-001-review.md).
- **Product capability:** unchanged. DragonByte Z remains 16 / 24 (67%).
- **No remediation was performed.** This document is the ticket's output; the
  next phase is the remediation set in section F.

## Method

1. Five fresh-context, adversarial domain reviews were run independently
   (ROM/core; writer/provenance; map/graphics/script/entity; Workbench;
   tests/tooling), each producing its own findings without seeing the others'.
   They are deduplicated here, and every CRITICAL/HIGH claim was re-verified
   against the source by the ticket owner before it was retained, re-classified
   or rejected.
2. Static inventory was produced with a temporary AST/text analyzer kept
   outside the repository (`<temp>\cq-audit\inventory.py`, plus
   `crossscan.py`, `fanin_scan.py`, `globals_scan.py`, `name_refs.py`). No new
   project dependency was added and no tool output is dumped here.
3. Material claims were probed: CLI/GUI reproduction scripts, call-count and
   timing measurements, a simulated missing-dependency collection run,
   repo-wide caller searches, and mutation experiments run against a
   `git archive` copy or reverted immediately (section G records one process
   consequence of that).
4. **The full test suite was not run** (standing human policy). Focused runs
   only; the reviewers' focused runs are recorded with their findings.

Evidence labels follow the project's existing discipline: `CONFIRMED`
(directly established here), `INFERRED`, `UNKNOWN`.

---

## A. Executive summary

### Overall structural condition

The SDK's **write core is the strongest part of the codebase and does not need
replacing.** `tools/webfoot/write.py` and `tools/webfoot/authored_image.py`
implement a staged, fsynced, link-published, rollback-on-failure emission path;
every hostile output shape probed (input alias, existing destination, directory,
junction alias, hard link, read-only file, trailing-dot and reserved names,
mid-stage failure, mid-publish failure, simulated race) all failed closed with no
leftover temporary file and no damage to the input. `allocation.allocate`/`withhold` is genuinely the **single** allocator:
no duplicated allocator logic exists anywhere, and the three decompositions
that matter for the roadmap (identity, address/offset typing, span arithmetic)
are typed and validated rather than ad hoc.

Repository discipline is also unusually good for a rapidly developed codebase: **no** `TODO`/`FIXME`/`HACK`/`XXX` markers in production code (one
marker line exists repository-wide, inside a gate test), **zero** import cycles
among `tools.webfoot` modules, **no** mutable module-level state in production
(every module-level collection is a `frozenset`, tuple, regex or frozen
dataclass), and no per-pixel Qt call loops remain after the visual pass fixed
that class.

The risk is concentrated in three places, and none of them is the codec layer:

1. **The boundary around the write layer.** The rule "never write the verified
   input" is implemented by two modules, not by an output-path authority, so
   the writers that do not route through them have no rule at all. One of those
   writers destroys the canonical ROM (**CQA-01**, demonstrated).
2. **Two independent decode stacks for the same binary concepts**, one of which
   a production writer depends on, never compared by any test (**CQA-04**), on
   top of load-bearing constants that have three to eight owners each
   (**CQA-15**).
3. **Workbench state ownership.** In-memory authored state is destroyed by an
   unrelated editor's action (**CQA-05**), SDK failures escape slots as dead
   clicks (**CQA-06**), and the refresh paths do full-corpus work per UI element
   (**CQA-07**). The GUI is also the part CI never exercises (**CQA-08**).

One further item is a **premise** problem rather than a bug: the packed-container
encoder's output is not provably self-terminating, and the repository records two
mutually exclusive beliefs about how the engine decides a packed stream has
ended, with the write path depending on the uncited one (**CQA-02**).

### Is major new architecture work safe to continue?

**Yes, on top of the existing foundations, after the two CRITICAL items and the
six HIGH items are closed.** Nothing found requires a redesign, a new
abstraction layer, or a rewrite. Every remediation in section F is a guard, a
wiring change, a single-source extraction, or one test. The allocator in
particular is an extension target, not a replacement target.

### Counts by severity

| severity | count | IDs |
| --- | --- | --- |
| CRITICAL | 2 | CQA-01, CQA-02 |
| HIGH | 6 | CQA-03 - CQA-08 |
| MEDIUM | 19 | CQA-09 - CQA-27 |
| LOW | 25 | CQA-28 - CQA-52 (compact, section C.4) |
| INFO | 6 | CQA-53 - CQA-58 (compact, section C.5) |

Severity was assigned by the ticket's model, not by reviewer vote. Where a
reviewer and the owner disagreed, the disagreement and the reason are recorded
in the finding; two reviewer HIGH ratings were reduced (CQA-09) and one
reviewer finding was rejected outright (section G).

### Biggest risk themes

1. **Guard coverage is a property of call paths, not of the tool.** The
   invariant that matters most is enforced where the SDK emitter is used and
   nowhere else. New writers are new opportunities to lose it, and
   ROM-CAPACITY-AND-ALLOCATION-001 will add writers.
2. **Duplication at the seams, not inside the modules.** Individually each
   subsystem is disciplined; the same binary concept is nonetheless decoded in
   two production stacks, the same ROM identity is written three to eight times,
   and the same "may I write here?" question has four different answers.
3. **Silence instead of failure.** Module-level test skips in CI (258 tests), a
   dead GUI click instead of a message box, an invalid image accepted with no
   manifest, a vacuity hole in a QA probe cited as whole-class evidence.
4. **Untested boundaries on the expansion path.** The one guard that keeps a
   generated write from crossing canonical EOF has zero coverage, and the
   packed encoder's termination postcondition is asserted nowhere on the write
   side.

---

## B. Inventory

Bounded, reproducible facts. Nothing here is a finding by itself.

### Scale (tracked tree, 706 files; `1b276e3`)

| class | files | code LOC | note |
| --- | --- | --- | --- |
| PRODUCTION - SDK (`tools/webfoot/`, excl. workbench) | 70 | 20,821 | the shipping product |
| PRODUCTION - Workbench (`tools/webfoot/workbench/`) | 17 | 7,242 | PySide6 client |
| PRODUCTION-ADJACENT - asset export (`tools/export/`) | 10 | 6,741 | reads the same structures as the SDK |
| TEST (`tests/`) | 168 | 37,771 | 103 unit, 61 integration, conftest/gates/helpers |
| QA / RESEARCH (`tools/qa`, `tools/research`, `tools/runtime`, `tools/mgba_probe`) | 48 | 18,892 | plus 68 `.lua`, 20 `.ps1` |
| SITE (`src/`, `public/`) | 12 | - | Astro; not a code-quality subject here |
| ARCHIVED / HISTORICAL | - | - | `docs/research/archive/`, older `PROJECT_STATE_*.md` parts, superseded probes. Not reviewed as shipping code. |

Total Python: 314 files, ~91,468 code lines. Test code exceeds the SDK it tests
(37.8k vs 20.8k lines), which is a healthy ratio for a project whose stated
proof of correctness is its tests.

### Largest production modules (lines)

`cli.py` 1,932 · `authored_placements.py` ~1,400 · `text.py` ~1,000 ·
`build.py` ~1,035 · `maps.py` · `graphics.py` · `profile.py` · `atlas.py` ·
`map_layout_edit.py` · `map_render.py` · `scene.py` · `authored_image.py` ·
`atlas_build.py` · `write.py` (583).
Workbench: `map_browser_tab.py` 1,986 · `graphics_tab.py` ~1,432 ·
`map_tab.py` ~950 · `app.py` ~700 · `theme.py` · `scene_tab.py`.

### Largest units and hotspots

- Largest functions: `atlas_producers/seed.py::_rows` 833 lines (**a data
  table**, not logic - each row carries `source=`, `evidence=` and a
  `CONFIRMED`/`INFERRED` label), `cli.py::build_parser` 477,
  `map_browser_tab.py::MapBrowserTab.__init__` 409,
  `graphics_tab.py::GraphicsTab.__init__` 363, `theme.py::app_stylesheet` 330,
  `cli.py::main` 230, `build.py::build_project` 178,
  `project/model.py::_read_maps` 174.
- Largest classes: `MapBrowserTab` 1,580 lines / 60 methods,
  `export::Exporter` 1,495 / 30, `GraphicsTab` 1,156 / 41,
  `export::Curator` 846 / 15, `MainWindow` 709 / 37, `MapWorkspaceTab` 676 / 31,
  `SceneTab` 610 / 20, `ActorSprites` 549 / 23.
- Highest complexity: `cli.py::main` (cx 71), `relocation.py::plan_relocation`
  (42), `atlas_producers/traversal.py::walk` (40),
  `formats/indexed_png.py::decode` (39), `formats/script_vm.py::assemble_source`
  (32), `build.py::_check_maps` (30), `formats/script_vm.py::disassemble` (30).
- Fan-in (production modules imported from the most places):
  `webfoot.profile` 58 · `webfoot.formats` 38 · `webfoot` 34 · `webfoot.binary`
  27 · `webfoot.project` 26 · `webfoot.cli` 26 · `webfoot.layout` 23 ·
  `webfoot.maps` 21 · `workbench.session` 20 · `webfoot.build` 20.
- Fan-out: only `workbench/map_browser_tab.py` (4) and
  `map_layout_write.py` (2) import more than one project module beyond their
  own layer.

### Cross-cutting scans

| signal | result |
| --- | --- |
| `TODO`/`FIXME`/`HACK`/`XXX` markers in production | **0** |
| Import cycles among `tools.webfoot.*` | **0** |
| Non-final mutable module-level state in production | **0** |
| Broad `except Exception` handlers in production | 9 in the SDK (8 of them in `atlas_producers/scan.py` + `traversal.py`, each commented as a pathological-input guard), 3 in `launcher.py` (all `# pragma: no cover`) |
| `except BaseException` in production | 2 (`write.py:575`, `authored_image.py:316`) - both are deliberate cleanup-and-reraise blocks |
| Production file-write sites | 24 in the SDK, 4 in the Workbench, 39 in `tools/export` |
| Production subprocess sites | 2 (both `subprocess.Popen([...])` list form, no shell, in `workbench/launcher.py`) |
| Production env-var reads | 1 (`workbench/settings.py:30`) |
| Top-level optional imports in production | PySide6 only, and only under `tools/webfoot/workbench/` - the SDK itself imports no optional dependency |
| Per-pixel Qt loops in the Workbench | 0 remaining (bulk `QImage` construction at `graphics_tab.py:207` and `map_browser_tab.py:1141`) |
| Production modules importing research/QA/runtime code | **0** |
| Production modules importing `tools.export` | 5 (`map_layout_edit.py`, `map_layout_provenance.py`, `map_layout_write.py`, `workbench/map_browser_tab.py`) - see CQA-04 |

### Verified-positive controls (recorded so they are not re-litigated)

`write.emit_image` re-stats the source through both the descriptor and the path
and refuses a plan whose recorded base identity differs; `apply_plan` re-runs
`plan_changes`; `ByteChange` refuses resizing, empty and ownerless changes;
`plan_changes` refuses out-of-image spans, base-byte disagreement and any
overlap; `authored_image.save_authored_image` refuses a source alias for all
four paths it writes or deletes and re-proves the source hash before and after;
`allocation.allocate` is deterministic with no allocator state; `withhold` can
only ever offer **less** than the profile declared; `capability.require` is
fail-closed and profile-generalised; the packed codec round-trips 400
adversarial payloads; the swizzle/unswizzle pair is an exact inverse at every OAM
dimension; `script_vm.assemble` refuses bytes it cannot represent and
re-disassembles itself; `atlas_build` demotes non-seed `VERIFIED_FREE` claims and
caps scanner output at `CANDIDATE`/`OBSERVED` by type.

---

## C. Findings

### C.1 CRITICAL

#### CQA-01 [CRITICAL] PNG export writes a caller-supplied path with no alias guard, so the verified ROM can be destroyed

> **REMEDIATED: CQA-01-OUTPUT-SAFETY-001 (2026-09-23).** Both destructive call
> paths now apply one shared SDK source-alias policy
> (`write.ensure_not_source_alias`, owned by `tools/webfoot/write.py`) before any
> destination write, and both refuse with the source byte-identical.
> `build_panel.is_safe_output_path` no longer re-derives the rule. Finding
> **CLOSED**; CQA-10 is **PARTIAL / IMPROVED** (overwrite-policy divergence,
> repository-output policy, atlas atomic publication and the remaining
> unguarded writers are still open). Reproduction, mutation check, canonical-ROM
> hash and focused validation:
> [`../tickets/CQA-01-OUTPUT-SAFETY-001.md`](../tickets/CQA-01-OUTPUT-SAFETY-001.md).
> The text below is the finding **as originally recorded** and is not restated.

- **Subsystem:** PRODUCTION - `tools/webfoot/cli.py`, `tools/webfoot/workbench/graphics_tab.py`.
- **Location:** `cli.py:1543-1555` (`_run_graphics`, `elif command == "export":`, write at `:1554`); `workbench/graphics_tab.py:930-956` (`GraphicsTab._on_export`, write at `:952`).
- **Observed:**
  ```python
  identification = identify_rom(args.rom, catalog)   # cli.py:1486
  image = Path(args.rom).read_bytes()                # cli.py:1487
  ...
  out = Path(args.out)                               # cli.py:1552
  out.parent.mkdir(parents=True, exist_ok=True)
  out.write_bytes(blob)                              # cli.py:1554
  ```
  Nothing compares `args.out` with `args.rom`, and nothing checks that the
  destination does not already exist. `_run_graphics` contains no safety
  predicate at all: a repository-wide search finds no `samefile`, no
  `resolve()` comparison and no shared guard anywhere in `cli.py`. Every other
  ROM-writing command routes through `write.emit_image`, which refuses both the
  same-path case and an existing destination (`write.py:508-516`) - so the one
  command that writes a *non-ROM* artefact is the one command with no rule. The
  Workbench has the identical hole one module away: `Path(path).write_bytes(blob)`
  after a `QFileDialog.getSaveFileName`, with no `is_safe_output_path` call even
  though that helper exists and a sibling tab imports it.
- **Why it matters:** `--out` is free-form. A typo, a shell-history reuse or a
  copy-paste that names the verified image destroys the single irreplaceable
  input this project measures everything against - truncated to the size of a
  PNG, with no backup, no manifest and no warning - and the command reports
  success. This is the exact event `docs/DEVELOPMENT.md` ("Original ROM Safety -
  Mandatory") and [ADR 0001](../decisions/0001-canonical-rom-immutability.md)
  exist to prevent.
- **Evidence:** owner probe `<temp>\cq-audit\probe_cli_export_alias.py` drives the
  real `_run_graphics` with only the read-only SDK calls stubbed (there is no
  ROM in the audit worktree): a 2,077-byte input named as both `--rom` and
  `--out` came back as 15 bytes, `exit code 0`, result JSON printed the
  clobbered path. Independently reproduced by the writer review with a
  4,096-byte input (probe `probe_graphics_cli.py`), which also confirmed the
  file's first bytes are a PNG signature.
- **Tests covering it:** **no.** `tests/unit/test_graphics_cli.py:75-87` asserts
  only that `--out` is *required*. Nothing in `tests/**` passes an aliasing path
  to `graphics export`. Contrast `tests/integration/test_stat_write_rom.py:259`,
  which does pin the equivalent refusal for the `emit_image` path.
- **Bounded remediation idea:** give the decision one owner - a
  `write.ensure_safe_output_path(source, destination)` (or routing the PNG
  through the existing staged-publish primitive) - and call it from
  `_run_graphics` and `GraphicsTab._on_export`. Add one test per command that
  passes the ROM path as the output and asserts a refusal plus a byte-identical
  input.
- **Blast radius:** every `graphics export` invocation; every Workbench sprite
  export; unrecoverable and silent.
- **Before ROM-capacity/allocation work?** **yes, first.**

#### CQA-02 [CRITICAL] The packed encoder's output is not provably self-terminating, and the repository asserts two mutually exclusive engine termination rules while the write path depends on the uncited one

> **REMEDIATED: CQA-02-PACKED-STREAM-TERMINATION-001 (2026-09-23).** The evidence
> question was resolved by two independent investigations plus an adjudication as
> **CASE A**: the retail decoder (`0x087B79E4` = IWRAM `0x03000040`) takes
> `(source, destination)`, keeps no output counter and compares nothing against its
> destination cursor, so it terminates on the bitstream's own escape - twelve zero
> bits at a token boundary - and on nothing else. The declared size is a host-side
> bound, not the engine's rule. `pack` now emits that escape through its bit writer
> after the final token and before the final word is padded, so every output is
> self-terminating by construction; `webfoot_lz.validate_retail_termination` is the
> one production implementation of the postcondition, and the shipped
> compressed-dialogue path and the sprite payload planner both invoke it and fail
> closed before any size decision or plan. Final encoded length drives fit and
> allocation. The contradictory claims this finding names were corrected **with
> their evidence, not deleted**. Finding **CLOSED**; CQA-10 is unchanged
> (**PARTIAL / IMPROVED**). Frozen implementation `2138635`, independent review
> `PASS` with no blocking findings, canonical ROM unchanged, no capability change.
> Record, mutation table, corpus counts, and the explicitly recorded Phase-1
> measurement correction:
> [`../tickets/CQA-02-PACKED-STREAM-TERMINATION-001.md`](../tickets/CQA-02-PACKED-STREAM-TERMINATION-001.md);
> closure:
> [`../tickets/archive/CQA-02-PACKED-STREAM-TERMINATION-001-COMPLETE.md`](../tickets/archive/CQA-02-PACKED-STREAM-TERMINATION-001-COMPLETE.md).
> The text below is the finding **as originally recorded** and is not restated. Its
> "not yet confirmed" list is now answered by Phase 1 of the closing ticket.

- **Subsystem:** PRODUCTION - compression (`tools/webfoot/formats/webfoot_lz.py`) and its write-path consumers.
- **Location:** `formats/webfoot_lz.py:490-495` (`_WordBitWriter.finish`), `:515-626` (`pack`), `:251` (shipping decoder loop); accepted by `formats/sprite_graphics.py:640-653`; shipped caller `compressed_dialogue.py:111`; contradicting claims at `tools/export/webfoot_strict.py:48-75`, `tests/unit/test_asset_export_strict_lz.py:153-171`, and `tools/research/webfoot_codec_reference.py:14-17,31-33,179-182`.
- **Observed (owner-verified in source):**
  - `finish()` pads with zero bits only `while self._count:`: when the final
    token ends exactly on a 32-bit word boundary, **no padding is emitted**, and
    `pack` never writes the decoder's own end-marker escape token (its token
    kinds are literal / one / short / previous / long only). A flush stream
    therefore carries no terminator.
  - The shipping decoder loops `while len(out) < expected` (`:251`), i.e. it
    terminates on the **declared length**, so it accepts such a stream. The
    strict export reader with `require_end_marker=True` refuses it.
  - `tools/research/webfoot_codec_reference.py` transcribes the engine's
    dispatcher `0x0803D940` as taking `(source, destination)`, never reading
    `container[+0x04]` on the packed path, and storing with `strb` "without
    comparing against a destination limit" - i.e. the engine terminates on the
    **escape**, not the declared size. `webfoot_strict.py:69-75` and
    `test_asset_export_strict_lz.py:159-161` assert the opposite ("the engine
    stops at the declared size"). Both cannot be true; the write path relies on
    the one that cites no disassembly.
- **Why it matters:** a payload emitted by `pack` whose final token lands flush
  can decode past its declared length **in the engine**, into an unchecked
  destination, reading whatever bytes follow (in-place edits pad with the
  original container's tail: `graphics.py:555-558`, `compressed_dialogue.py:121`).
  Nothing on the write path detects this: no module under `tools/webfoot/**`
  re-decodes a planned payload with `require_end_marker=True`. The failure mode
  is in-game garbage or memory corruption, not ROM corruption, but the toolkit
  emits the bytes claiming success.
- **What is CONFIRMED here:**
  - `pack` output is not always demonstrably self-terminating under the strict
    end-marker interpretation: `finish()` pads only while bits remain, and `pack`
    never writes the decoder's own escape token.
  - The repository contains **contradictory termination claims** for the engine
    (the `webfoot_strict.py` / `test_asset_export_strict_lz.py` assertions versus
    the transcribed dispatcher in `research/webfoot_codec_reference.py`).
  - The shipped **compressed-dialogue** authoring path consumes `pack` output,
    including into generated expansion.
  - The write path does **not currently prove** the end-marker postcondition: no
    module under `tools/webfoot/**` re-decodes a planned payload with
    `require_end_marker=True`.
- **What is NOT YET CONFIRMED:**
  - **which** termination rule the actual retail engine uses in the relevant
    path (the two in-repo claims cannot be reconciled from this environment);
  - **whether** a currently emitted flush-boundary stream will actually overrun
    in retail runtime.
  This finding is therefore **not a proven runtime corruption event**, and it
  must not be recorded as one. Its first remediation step is **evidence
  resolution**, not a code change. Reachability also differs by path: the
  **compressed-dialogue** build is shipped and already writes `pack` output,
  while the **sprite-payload** path has no GUI or CLI caller today, so for it
  this is a blocked gate rather than a live defect. The single runtime
  observation that exists (an authored compressed dialogue line displayed by the
  retail engine, `config/roms.yaml:161-170`) is consistent with the marker
  *happening* to fall inside the trailing zero padding, so it does not establish
  engine-side termination.
- **Evidence:** independent ROM/core review probes `probe_pack_marker.py`,
  `probe_marker_rate.py`, `probe_marker_reasons.py`: `pack(b"A"*64)` is refused
  by `webfoot_strict.unpack(..., require_end_marker=True)`; in situ, **23/100**
  random 64-byte and **36/100** random 256-byte payloads violate the
  postcondition (second sample 8/60), with continued decodes producing output
  ("match at output 64 would produce 69 bytes against a declared 64"). The
  marker was inside the trailing zero padding for 51/60 - the accident the
  current design depends on. Owner verified the mechanism and the docstring
  contradiction directly in source.
- **Tests covering it:** partially and not on the write side.
  `test_webfoot_lz.py` checks `pack` only through the shipping decoder;
  `test_asset_export_strict_lz.py` documents the flush case but encodes the
  uncited engine claim as its justification. No test asserts that `pack` output
  satisfies the end-marker postcondition that all 11,712 canonical packed
  containers satisfy.
- **Bounded remediation idea:** this is a **two-stage** remediation and the order
  matters. **Stage 1 (evidence resolution):** settle which termination rule the
  engine implements on the relevant path (a targeted runtime capture or a
  disassembly read of `0x0803D940`) and record the answer in one place, since
  the repository currently asserts both. **Stage 2 (code, chosen from that
  answer):** either emit the end-marker escape after the final token in `pack`
  (legal for both readers, and it makes the marker fall exactly at the declared
  size) or refuse/re-encode when the marker does not fall within the final
  word's padding; and add a write-path guard that re-decodes every planned packed
  payload with `webfoot_strict.unpack(..., require_end_marker=True)` before it
  enters a plan. Stage 1 may conclude that the shipped encoder is already
  correct for retail; that is an acceptable outcome and still resolves the
  finding, because the contradiction is what makes the write path untrustworthy.
- **Blast radius:** every `pack` consumer: `sprite_graphics.plan_graphic_payload`,
  `compressed_dialogue._prepare_replacement` (shipped dialogue authoring and
  expansion allocation), `atlas_producers/scan.py` self-checks, plus every
  capability claim that depends on "we can write packed assets".
- **Before ROM-capacity/allocation work?** **yes**: the dialogue path already
  writes `pack` output into generated expansion, and pixel authoring is the next
  feature.

### C.2 HIGH

#### CQA-03 [HIGH] The Workbench pairs the open ROM with an atlas built for a different profile, with no identity comparison

> **REMEDIATED: CQA-03-15-IDENTITY-AND-EXTENTS-001 (2026-09-23).** One identity
> contract now owns the rule, in the profile domain rather than in the Workbench,
> the CLI or an editor: `tools/webfoot/profile.py` carries `AtlasIdentity`,
> `AtlasIdentityMismatch`, `RomProfile.identity` and
> `RomProfile.require_identity`. It is called from exactly one production site,
> `workbench/session.py:245`, **before** `self.atlas = atlas` and before maps or
> text load, so a refusal publishes no atlas-backed state. Both the profile id and
> the canonical base hash are checked, plus image size, because each alone is
> insufficient; the comparison reads the atlas's identity structurally, so
> `profile` does not import `atlas` and a value lacking the triple is refused by
> name rather than defaulted. The failure arrives as the existing `SessionError`
> naming both identities, with **no silent rebuild and no automatic regeneration**.
> The derivative path is covered because the session has already required a
> derivative's manifest to name the profile *of* its canonical base, so the atlas
> is compared against the reconstructed canonical identity - not the derivative's
> output digest - and a derivative is not made to need a rebuilt atlas. A focused
> regression proves a `VERIFIED_FREE` span from another profile cannot reach the
> session while the same span under the right identity is accepted. Finding
> **CLOSED**; CQA-04 remains **OPEN** and CQA-10 is unchanged
> (**PARTIAL / IMPROVED**). Frozen implementation `1067a539` (unamended, corrected
> through separate commits), independent review `PASS` with **no blocking
> findings** at the final correction head, canonical ROM unchanged, no capability
> change. Record, retained-literal classification and mutation table:
> [`../tickets/CQA-03-15-IDENTITY-AND-EXTENTS-001.md`](../tickets/CQA-03-15-IDENTITY-AND-EXTENTS-001.md);
> closure:
> [`../tickets/archive/CQA-03-15-IDENTITY-AND-EXTENTS-001-COMPLETE.md`](../tickets/archive/CQA-03-15-IDENTITY-AND-EXTENTS-001-COMPLETE.md).
> The text below is the finding **as originally recorded** and is not restated.

- **Subsystem:** PRODUCTION - `workbench/session.py` (atlas ownership).
- **Location:** `workbench/session.py:216-258` (`open_rom`); `atlas.py:410-421`
  (`Atlas.profile_id` / `base_sha256` and `Atlas.validate`); atlas directory at
  `cli.py:1323-1329`.
- **Observed:** `open_rom` identifies the ROM, resolves the profile, then loads
  one global `build/atlas/atlas.jsonl` and assigns it:
  ```python
  atlas_dir = _default_atlas_directory()
  atlas = load_atlas(atlas_path)
  ...
  self.atlas = atlas                       # session.py:255
  ```
  `Atlas` already carries `profile_id` and `base_sha256`, and `Atlas.validate()`
  only checks that its internal provenance agrees with its own declared
  identity. `Session` never compares either field with
  `match_profile.id` / `identification.hashes.sha256`.
- **Why it matters:** the atlas is documented as "a byte-addressable structural
  map of one verified ROM image". Pairing it with a different image makes every
  offset, coverage class and `VERIFIED_FREE` span a claim about bytes that are
  not there - silently. `config/roms.yaml` declares four 8 MiB profiles, so the
  wrong pairing is one ordinary "open another supported game" away. This is the
  highest-priority HIGH because the atlas is the evidence base the capacity
  ticket will read for free space.
- **Evidence:** independent map/graphics review probe
  (`probe_atlas_profile.py`) stubs identification to a verified LoG II match,
  points the atlas directory at a Buu-built `atlas.jsonl`, and calls the real
  `Session.open_rom`:
  `session.profile.id = legacy_of_goku_ii_usa_rev0_204142e1`,
  `session.atlas.profile_id = buus_fury_usa_rev0_01c1707f`, **no exception**.
  Owner verified the code path, the two Atlas fields, and that `VERIFIED_FREE`
  is a live atlas classification (`atlas.py:93,239-245`).
- **Tests covering it:** **no.** `tests/unit/test_workbench_session.py` covers
  only the canonical ROM and only ROM/manifest mismatch, never the atlas.
- **Bounded remediation idea:** refuse in `open_rom` unless
  `atlas.base_sha256 == identification.hashes.sha256` (and
  `atlas.profile_id == match_profile.id`, or `authored.canonical_sha256` for a
  derivative), raising the existing `SessionError` with both identities named.
  One comparison; it also covers the derivative path.
- **Blast radius:** every atlas-backed surface (Atlas browser, map/text search)
  and `atlas text --rom`.
- **Before ROM-capacity/allocation work?** **yes.**

#### CQA-04 [HIGH] The same map/graphics concepts are decoded by two production stacks that are never compared, and a production writer is built on the export-side one

- **Subsystem:** PRODUCTION - map and graphics decode/render, plus the map-layout write path.
- **Location:** `tools/export/canonical.py:501-902,1099-1172` +
  `tools/export/render.py:142-171,261-342,483-523` +
  `tools/export/map_browser.py:307-434` **versus**
  `tools/webfoot/map_render.py:264-430,558-641` +
  `tools/webfoot/formats/bg_tilemap.py:96-228` +
  `tools/webfoot/formats/sprite_graphics.py:261-325`. Consumers:
  `workbench/map_browser_tab.py:1036` (`mb.render_map`) and
  `workbench/map_tab.py:595` (`map_render.render_map`); writer dependency
  `tools/webfoot/map_layout_write.py:18-20`, `map_layout_edit.py:32-35`,
  `map_layout_provenance.py:41-42`.
- **Observed:** selector delta-decode, character-block assembly, animated-tile
  records, tile unswizzle, tile flip, OAM dimension tables and BG-palette
  requantisation each exist twice, with no shared code, no cross-import in
  either direction, and no test that compares them. `canonical.py:3-8` justifies
  the second stack partly by a sprite/frame reading that has since been replaced
  (EVIDENCE-RISK-DEBT-001) and now agrees exactly with the SDK's, so that part
  of the justification is dead. The two stacks are **not** equivalent and both
  are user-visible in the shipped Maps editor: the Browse/Layout surface renders
  five layer handlers including the Map 19 terrain field, while Objects accepts
  only `0x08008087` (`map_render.py:66,301-306`) and shows "Map unavailable" for
  the same map. Separately, the **production map-layout writer** gates its
  canonical-identity check on `tools.export.map_browser.SUPPORTED_ROM_SHA256` and
  reads map records through `tools.export.canonical`, i.e. a shipped write path
  depends on the export/research reader rather than the SDK's `formats` layer.
- **Why it matters:** this is the defect class the project was already bitten by
  in the visual pass - one concept implemented independently per surface - one
  level up. A newly verified field or a fix has to be made twice, and the two
  copies already disagree observably for one map. The writer's dependency also
  means a profile-level change to the declared map-entry table would not reach
  the write path (see CQA-15).
- **Owner correction to the reviewer's version:** the reviewer additionally
  claimed the two surfaces render *different images* for a derivative, because
  Objects reads `session.rom_image` while Browse reads `session.map_image`. That
  is not reachable: `open_rom` sets `maps = None` for a derivative
  (`session.py:240-244`), so Objects mode is unavailable for derivatives. The
  divergent-*image-source* half is therefore recorded as LOW (CQA-49), and only
  the divergent-*capability* half is HIGH.
- **Evidence:** each duplicated pair read in both copies by the independent
  review; `grep` shows no test importing both stacks
  (`test_map_render_rom.py` uses only `mr`; `test_map_layout_write_rom.py:39` and
  `test_map_layout_editor_rom.py:114` use only `canon`); map 19's terrain field
  is deliberately exercised through the browser path and deliberately refused on
  the renderer path (`test_map_render.py:214-217` pins the refusal). Owner
  verified the dual mount (`workbench/editors.py:192,196`), the handler
  restriction (`map_render.py:301-306`) and the five writer/consumer imports.
- **Tests covering it:** partially - each stack is tested against its own
  expectations; nothing tests agreement, and the ROM-gated tests skip without a
  ROM.
- **Bounded remediation idea:** make one stack the reader of record per concept
  (the cheap direction is for `webfoot.map_render` to consume `canonical`'s
  readers, or to move the shared codecs into `webfoot.formats` and have
  `canonical` import them), and add a ROM-gated equivalence test over every map
  both can render. Correct `canonical.py:3-8` to state only the surviving
  (layer-classification) reason.
- **Blast radius:** the whole map visual layer, both GUI map modes, the graphics
  exporter, and any future allocation work that must agree with rendering.
- **Before ROM-capacity/allocation work?** **yes.**

#### CQA-05 [HIGH] A project mutation in any editor silently destroys the Map Browser's staged layout edits and the placement undo history, and the mode strip then lies

- **Subsystem:** PRODUCTION - Workbench shell / Maps editor state ownership.
- **Location:** `workbench/app.py:179-188` (`MainWindow._on_project_changed`);
  `workbench/editors.py:294-296`; `workbench/map_browser_tab.py:930-935` →
  `:1225-1253` (`_reset_editor`); `workbench/map_tab.py:534-540`.
- **Observed:** one shell callback answers two different events.
  `_on_project_changed()` - fired by *any* editor's `projectChanged`, i.e. a
  dialogue Apply, a palette Apply/Undo, a Scene NPC add or a placement drag -
  calls `self._maps.on_session_changed()` (`app.py:184`), which forwards
  straight to `MapBrowserTab.on_session_changed()`, which runs
  `self._reset_editor()` **unconditionally** (`:935`), nulling `_editor`,
  `_saved = {}` and `_edit_mode = False`. `MapWorkspaceTab` clears its placement
  undo stack the same way. `MapsEditor._mode` is not reset, so the mode strip
  keeps "Layout" checked while the editor it names is no longer in edit mode.
  The reset is called on a *project* change even though its own docstring says
  "the ROM, and so the base, has changed", and the layout session is built from
  ROM bytes alone (`MapLayoutEditor(self._session.rom_image)`), so a project
  write does not invalidate it.
- **Why it matters:** the only authoring state that editor holds is discarded
  with no message, no confirmation and no way back, whenever the user touches
  any other editor; the window's "N unsaved" count drops to 0, so nothing on
  screen reports the loss. Allocation work will add more in-memory authored
  state to exactly these surfaces, and this callback destroys in-memory state by
  design.
- **Evidence:** independent Workbench review probe `probe_pending.py` (offscreen
  `MainWindow`, two staged edits, one in-memory mutation): before
  `mode=layout | edit mode=True | pending edits=2 | unsaved=2 | history=1`;
  after `mode=layout | Layout checked=True | edit mode=False | _editor=None |
  unsaved=0 | history=0`. Owner verified `app.py:184`, the unconditional
  `_reset_editor()` call and its docstring.
- **Tests covering it:** partially - `test_workbench_map_browser.py:585` pins the
  reset for a *session* (ROM) change, which is intended. Nothing asserts what a
  project mutation does to staged layout edits.
- **Bounded remediation idea:** split the two events. Keep
  `on_session_changed()` for ROM identity/atlas/maps reload, and add a
  project-mutation entry point that re-reads only what a project can change,
  preserving `_editor`, `_saved` and `_edit_mode`; have `MapsEditor` re-assert
  its own mode afterwards so the strip and the editor cannot disagree. If a
  discard is genuinely required, gate it on `unsaved_edit_count()` and ask.
- **Blast radius:** `MapBrowserTab`, `MapWorkspaceTab`, `MapsEditor` mode strip,
  `MainWindow._on_project_changed`, and every future in-memory authoring surface.
- **Before ROM-capacity/allocation work?** **yes.**

#### CQA-06 [HIGH] `Session.open_rom` lets sibling SDK error families escape the Open ROM slot, reproducing the project's documented dead-click failure mode

- **Subsystem:** PRODUCTION - Workbench error handling at the SDK boundary.
- **Location:** `workbench/session.py:170-250` (notably `:180` `identify_rom`
  unguarded, `:229` `path.read_bytes()` unguarded, `:240-244` only
  `MapEntryProfileError` caught around `load_maps`);
  `workbench/atlas_browser.py:159-165` (`except SessionError`). Escaping
  families: `rom.RomReadError`/`RomChangedError` (`rom.py:14-19`, both `OSError`)
  and `maps.MapError`/`UnknownMapError` (`maps.py:53,775-877`, `ValueError`).
- **Observed:** `open_rom` wraps `load_text_strings` failures in `SessionError`
  but leaves identification, the byte read, and `load_maps` raising their own
  types. The Open ROM slot catches `SessionError` only, so those families
  escape: no status text, no identity-chip update, no `QMessageBox`.
- **Why it matters:** this is the failure the project's own Workbench skill
  names as its most expensive lesson - a GUI slot must catch the SDK exception
  *family parent*, or the click simply looks dead. It is reachable today (a file
  renamed, locked or modified between the dialog and the read) and becomes more
  reachable as `load_maps` gains fail-closed fences, since each new fence lands
  on this uncaught path.
- **Evidence:** independent Workbench review probe `probe_workbench.py` P1 with
  a real `AtlasBrowserTab` and a stubbed file dialog:
  `SessionError -> handled`; `MapError (placement overlaps map table) ->
  ESCAPED`; `RomReadError (ROM does not exist) -> ESCAPED`. Owner verified the
  `except SessionError` at `atlas_browser.py:161` and the unguarded calls in
  `session.py`.
- **Tests covering it:** partially - `test_workbench_map_browser.py:139,152`
  cover `MapBrowserError` inside the tab and `test_workbench_session.py` covers
  `SessionError`; nothing drives a sibling family through the Open ROM slot.
  The graphics slot tests show the intended shape (SDK family + `OSError` in one
  tuple).
- **Bounded remediation idea:** make `open_rom` total - wrap its body so every
  failure leaves as `SessionError`, or catch the family parents at the slot -
  and add one parameterised test per family at the slot boundary.
- **Blast radius:** `session.open_rom`, `atlas_browser.open_rom_dialog`, and the
  QA capture harness that opens ROMs through it.
- **Before ROM-capacity/allocation work?** **yes.**

#### CQA-07 [HIGH] The palette editor and `palette_users` do full-project and full-corpus work per UI element, on the UI thread

- **Subsystem:** PRODUCTION - Graphics editor refresh cost.
- **Location:** `workbench/graphics_tab.py:1206-1207` (`_palette_swatch` →
  `_effective_rgb`), `:669-691` (`_effective_rgb` →
  `graphics_sdk.get_palette_overrides`), `:1108-1130` (`_populate_palette`),
  `:1266-1298` (`_refresh_pending_ui`), `:1300-1343` (`_on_apply`),
  `:1376-1398` (`_after_undo_redo`); `graphics.py:776-785` (`read_project`,
  uncached) and `:508-524` (`palette_users` walks the whole ~7.4k-graphic
  corpus per call).
- **Observed:** `_populate_palette` builds 256 swatches and each one re-reads
  and re-parses the whole project to find the override map, although the caller
  computed that map one line earlier. `_refresh_pending_ui` and `_on_apply` each
  call `palette_users` once **per pending colour**, and each call rescans every
  decoded graphic's pixels. A single Apply performs **two** full repaints, on
  the UI thread, inside a click handler.
- **Why it matters:** cost scales with the palette size times the number of
  colours the user recolours in one gesture (up to 256), synchronously, freezing
  the window; a slow or network-backed project volume multiplies it. It is the
  per-pixel-`pixelIndex` defect class the visual pass fixed, one layer up, with
  SDK calls in place of Qt calls - and the palette editor is the template the
  next colour-bearing editor will copy.
- **Evidence:** independent Workbench review probes: `probe_workbench.py` P4
  measured `get_palette_overrides` calls = **257** for a full repaint (5 for a
  4-swatch repaint) and **4** full-corpus `palette_users` scans for 4 pending
  colours; `probe_projectcost.py` measured a **2.12 ms/call** floor on a
  deliberately *empty* project (184-byte `project.toml`), i.e. a ≥0.54 s floor
  per full repaint and ≥1.09 s per Apply; `probe_misc.py` B confirmed two
  `_populate_palette` and two `_populate_grid` calls per Apply. The independent
  map/graphics review measured the `palette_users` half separately
  (~1.71 s for 256 indices on corpus-shaped synthetic data). Wall-clock on real
  ROM data is **not** measured (no ROM in the audit worktree).
- **Tests covering it:** **no** - the graphics tests assert behaviour, never call
  counts; nothing asserts a performance budget.
- **Bounded remediation idea:** pass the already-computed `rgb` map into the
  swatch factory (one `_effective_rgb` per repaint instead of 257); build one
  index→consumer-count map per repaint instead of calling `palette_users` per
  index (or compute an inverse palette index once per session from the pixels
  already held in memory); and give `_after_undo_redo` a single refresh path.
  All three are local to `graphics_tab.py`.
- **Blast radius:** Graphics editor responsiveness, the Apply/undo path, and the
  Objects-mode canvas that shares `indexed_pixmap`.
- **Before ROM-capacity/allocation work?** **yes** - the planned next authoring
  surface is modelled on this code.

#### CQA-08 [HIGH] CI installs only `.[dev]`, so 258 collected portable tests are skipped whole at import - including the entire Workbench suite

- **Subsystem:** TOOLING (CI) / TEST.
- **Location:** `.gitlab-ci.yml:28` (`-e ".[dev]"`) and `:32`
  (`pytest tests/unit -q`); `pyproject.toml:18-28`; skip sites are the
  module-level `pytest.importorskip` calls in 12 PySide6 modules and 3 capstone
  modules under `tests/unit/`.
- **Observed:** `dev` is `pip, pytest, setuptools, hypothesis`; PySide6 lives in
  the separate `workbench` extra and capstone is in no extra at all. The guarded
  modules each collapse to a single `SKIPPED [1]` line and the job exits 0.
  Measured: `tests/unit` collects **2,228** items in a full environment and
  **1,970** with those imports blocked, so **258 tests** (170 in 12 PySide6
  modules, 88 in 3 capstone modules) are collected in CI but never executed.
- **Why it matters:** `tests/unit` is the only automated gate for the shipping
  product, and the deliverable includes the desktop application. The strongest
  GUI regressions are in the skipped files - `test_workbench_project_status.py`
  holds the four status-duplication guards recorded as mutation-proven (25 tests
  in that file alone) - so a green pipeline says nothing about 100% of the
  Workbench suite. Owner note: the SDK's own write guards are *not* part of the
  skipped set, and `write.emit_image` refuses the input-alias case independently,
  so the ROM-safety invariant is still enforced in CI even though the GUI layer
  that duplicates part of it is not.
- **Evidence:** independent tests/tooling review measured both collections and
  the per-file counts with an out-of-repo plugin; the owner reproduced the class
  independently with a fake `PySide6` package on `PYTHONPATH` (12 module skips,
  2,058 collected, exit 0). The quoted CI baseline "1960 passed, 25 skipped" is
  arithmetically consistent with a 15-module-skip run, not with 2,228 portable
  tests - `INFERRED` corroboration, not a measurement of CI.
- **Tests covering it:** this *is* the gap. `test_test_gates.py` proves every
  file carries an axis gate, which is what makes the skip count inconspicuous.
- **Bounded remediation idea:** install `.[dev,workbench]` plus `capstone` in
  the test job so the workbench gate actually runs, and add a session-end
  assertion that fails on module-level (whole-file) skips rather than reporting
  them as a number.
- **Blast radius:** the whole `workbench` non-integration gate and 3 research
  modules; CI's claim to be "the whole portable suite".
- **Before ROM-capacity/allocation work?** no for allocation correctness;
  **yes** if the Workbench remains the authoring surface.

### C.3 MEDIUM

Each entry gives location, the observed structure, why it matters, the evidence,
and whether it gates the capacity work. Evidence is owner-verified unless it is
attributed to an independent review probe.

#### CQA-09 [MEDIUM] The canonical-EOF straddle guard is load-bearing and has zero test coverage

- **Location:** `write.py:418-421` (`plan_changes`, `change.offset < len(base) < change.end`).
- **Observed:** for a change beginning in the last canonical byte and ending in
  the appended padding, `offset >= len(base)` is false, so the
  allocator-authorization branch at `:422-429` is skipped entirely; only this
  branch refuses it. Deleting the branch leaves the documented `writer` gate at
  **443 passed** and `fast and (map or research)` at **1003 passed** (mutation
  experiment, run against a `git archive` copy and against the worktree with an
  immediate revert).
- **Why it matters:** it is the exact boundary the capacity ticket will extend.
  The guard is correct today, so this is not a live defect - it is a guard whose
  removal is invisible in a function that is certain to be refactored.
- **Evidence:** two independent reviews reached this by mutation (writer and
  tests/tooling); a purpose-built probe shows a 2-byte write at the last
  canonical byte with a 1-byte allocator span flipping from `REFUSED` to
  `ACCEPTED` when the branch is removed.
- **Tests covering it:** no. `test_rom_expansion.py` covers the sibling rules
  (past-EOF, no-provenance, foreign-owner, span mismatch) but every case it
  builds places the change at or beyond `len(base)`; the property suite draws
  `old` from the image itself, so it cannot construct a straddle.
- **Remediation:** one synthetic case in `test_rom_expansion.py` - 10-byte base,
  16-byte generated output, a 1-byte allocator span, and a 2-byte change at
  offset 9 expecting `ChangeValidationError` matching `straddles canonical EOF`.
- **Severity note:** both reviewers rated this HIGH; the owner retains MEDIUM
  (the guard is present and correct, so this is weakly-tested boundary coverage,
  which the ticket's model classes as MEDIUM) but keeps it in the
  must-fix-before-capacity set.
- **Before ROM-capacity/allocation work?** **yes (same ticket that extends it).**

#### CQA-10 [MEDIUM] Output-path safety has no single owner: four divergent policies and two writers with none

> **PARTIALLY REMEDIATED: CQA-01-OUTPUT-SAFETY-001 (2026-09-23).** The
> **source-alias invariant** now has one SDK owner (`tools/webfoot/write.py`:
> `paths_are_the_same_file`, `ensure_not_source_alias`, `ensure_new_destination`),
> `emit_image` and the two previously unguarded writers apply it, and
> `build_panel.is_safe_output_path` is a thin GUI wrapper over it rather than a
> second comparison. Still open: the **overwrite-policy** divergence
> (CQA-11), the **repository/raw-input-root** output policy and the eight copied
> helpers in `tools/export/`, **atlas atomic publication** (CQA-13),
> `.gitignore` coverage for stray exported artefacts, and the remaining
> unguarded write sites across the wider repository. Details:
> [`../tickets/CQA-01-OUTPUT-SAFETY-001.md`](../tickets/CQA-01-OUTPUT-SAFETY-001.md).
> The text below is the finding **as originally recorded** and is not restated.

- **Location:** `write.py:508-516` (file equality + existence);
  `authored_image.py:108-124,273-281` (four-path alias set);
  `workbench/build_panel.py:46-54` (`is_safe_output_path`, deliberately not
  delegated to the SDK, and imported by `map_browser_tab.py:78`);
  `tools/export/buu_resource_export.py:163-175` and
  `tools/export/buu_resource_curate.py:755-791` (a different policy: no output
  inside a git work tree / no output inside the raw input root); and no policy at
  all at `cli.py:1554`, `graphics_tab.py:952` (CQA-01) and
  `atlas_build.py:503-530` (CQA-13).
- **Observed:** one question - "may this path be written?" - is answered by
  three unrelated predicates with three different scopes, plus one deliberate
  GUI duplicate, plus writers that ask nobody. The ROM writers do **not** apply
  the exporter's repository guard: a probe emitted a full ROM into a directory
  containing `.git/HEAD`, which `tools/export` refuses for its own outputs.
  `.gitignore` covers `*.gba` but not the `.json`/`.toml` manifests that carry
  ROM-derived provenance, nor a stray exported sprite `*.png`.
- **Why it matters:** this is the mechanism behind CQA-01 - the invariant is a
  property of one layer, not of the tool, so each new writer is a new chance to
  lose it. Capacity work will add output artefacts and probably a build-directory
  convention, and it should not have to reason about safety in three places.
- **Evidence:** reviewer probe case C (`emit_image` writing a ROM into a git
  repo: OK); the two export tools additionally carry eight near-identical copied
  helpers (`sha256_bytes`, `is_repository_root`, `find_repository_root`,
  `ensure_outside_repository`, `audit_root_for`, `_has_files`,
  `_empty_directory`, `clear_generated`) whose `audit_root_for` has already
  diverged in its naming convention (`_Audit` vs ` Audit`).
- **Tests covering it:** partially and separately - `test_build_panel_guard.py`,
  `test_asset_export_output_safety.py`, `test_stat_write_rom.py:259,264`,
  `test_cross_profile_invariants.py:203,218`. No test asserts the same rule holds
  across implementations, and none covers the unguarded writers.
- **Remediation:** declare `write.py` the owner of "is this a safe ROM/artefact
  output path"; have `authored_image` and the GUI call it (the GUI may keep a
  thin wrapper for its dialog text); give the export/atlas writers the staged
  publish primitive instead of raw `write_bytes`/`open("w")`.
- **Before ROM-capacity/allocation work?** **yes** (the wiring, not a redesign).

#### CQA-11 [MEDIUM] Overwrite policy is three policies: refuse, silently replace, and delete-then-rebuild

- **Location:** `write.py:513-516` (refuse an existing destination);
  `authored_image.py:326-339` (unconditional `os.replace` over the destination
  **and** its manifest, with no existence check and no stated policy);
  `workbench/build_panel.py:327-339` (ask, then `unlink()` the existing output
  and rebuild).
- **Observed:** the Build/CLI/`stats set`/`text set` path refuses to touch an
  existing artefact; the authored-image transaction silently replaces whatever
  is there; the Build tab deletes the previous output *before* the rebuild, so a
  failed rebuild leaves no artefact at all where one existed.
- **Why it matters:** "did this run produce that file, and what did it replace?"
  is answerable for one writer and not the others. The Build tab's order is the
  sharpest: the one irreversible act (deleting a user's existing output) happens
  before the operation that was supposed to replace it is known to succeed.
- **Evidence:** reviewer probe case J (a pre-filled destination replaced on a
  successful `save_authored_image`, manifest included) against case B
  (`emit_image` raising the same situation); `build_panel.py:327-339` read
  directly by the owner.
- **Tests covering it:** partially - `test_authored_image.py:222-266` proves an
  existing destination survives a *failed* save; nothing pins a successful save
  over an existing destination, and nothing covers the Build-tab delete order.
- **Remediation:** give the shared transaction an explicit `overwrite` policy
  (refuse by default) so callers choose, and rebuild to a temporary sibling
  before removing the previous output.
- **Before ROM-capacity/allocation work?** unknown - yes if capacity artefacts
  reuse `save_authored_image`.

#### CQA-12 [MEDIUM] The Build path emits no provenance document, although the recorded delivery journey describes manifest publication as part of the shared contract

- **Location:** `workbench/build_panel.py:341-348` (`_run_build` passes no
  `manifest_path`); `build.py:823-830,984-993`; `cli.py:570,1801`
  (`--manifest` defaults to `None`).
- **Observed:** the GUI never supplies `manifest_path`, and the CLI only records
  one when asked, so the primary authoring surface emits an 8 MiB derivative
  whose only provenance is in memory. `docs/journeys/safe-build-and-derivative-reopen.md`
  step 4 describes the shared layer as owning "manifest publication" and lists
  the Build-tab domains as covered by the build half.
- **Why it matters:** the deliverable of the whole pipeline is byte-indistinguishable
  from an arbitrary modified ROM: it does not say which base or which spans
  produced it, and the "verified base -> working copy -> output ROM" chain stops
  at the last link. For a roadmap whose next step is *allocation and expansion*,
  an output that cannot state its base is the wrong default, because expansion
  makes silent divergence inaudible.
- **Owner correction to the reviewer's version:** the reviewer also presented
  "the Workbench cannot reopen its own output" as part of this defect. That is
  **documented, accepted behaviour** - the same journey's coverage table states
  that Build-tab domains are built but **not** reopened, and that "that refusal
  is the designed outcome rather than a gap to paper over". Only the missing
  provenance document is retained.
- **Evidence:** `build_panel.py:343-345` read directly; the journey table at
  `docs/journeys/safe-build-and-derivative-reopen.md:72-80`.
- **Tests covering it:** no test asserts that a build leaves a provenance
  document.
- **Remediation:** have `_run_build` write the manifest beside the image by
  default (or have `build_project` do so unless told otherwise), and add a
  reopen/`identify` assertion for the produced file.
- **Before ROM-capacity/allocation work?** **yes** - capacity work will produce
  images whose base identity must be provable.

#### CQA-13 [MEDIUM] `atlas_build.write_atlas` truncates its destination in place: unguarded, non-atomic, destructive on failure

- **Location:** `atlas_build.py:503-521` (`path.open("w", ...)` for the atlas and
  for `atlas_conflicts.jsonl`); callers `cli.py:1347,1361` and
  `atlas_producers/pipeline.py:89-90`.
- **Observed:** the caller-supplied path is opened `"w"` with no existence check,
  no alias check, no temporary file and no replace. The destination is destroyed
  before the first byte of the replacement is known to be writable. This is the
  only writer in `tools/webfoot/` that is both destructive and non-atomic.
- **Why it matters:** the atlas is not scratch - `Session.open_rom` refuses to
  work without it, so a failed or interrupted `atlas build` silently replaces a
  good atlas with a truncated one and the Workbench is broken until someone
  regenerates it. `webfoot atlas build --atlas <any path>` also truncates any
  existing file at that path.
- **Evidence:** reviewer probe `probe_atlas.py`: a 4,096-byte existing file was
  reduced to 3 bytes (`{}`), and a mid-write failure left a previously good
  atlas replaced by a partial document. Owner read the two `open("w")` sites.
- **Tests covering it:** no - `test_atlas_build.py:325` calls `write_atlas` on a
  fresh path only.
- **Remediation:** stage to a temporary sibling and `os.replace` on success (the
  pattern `authored_image` already implements), plus the shared output-path
  refusal from CQA-10.
- **Before ROM-capacity/allocation work?** no, but cheap - and the atlas is the
  evidence base the capacity work reads.

#### CQA-14 [MEDIUM] `verify_emitted_image` scans all 8 MiB in Python on every authored save, on the UI thread

- **Location:** `authored_image.py:184-186`, called at `:314`, plus two full
  source re-reads and SHA-256s at `:284` and `:322`.
- **Observed:** the "nothing outside a declared field changed" check is a
  per-byte Python enumeration of the whole image, executed synchronously inside
  a Qt slot.
- **Why it matters:** a Save As that changes four bytes spends ~1.7 s, of which
  ~1.34 s is this diff, with the window frozen. The check is also unnecessary in
  its current form: `plan_changes` already proved every declared span, so the
  invariant can be verified per span instead of over the whole image.
- **Evidence:** reviewer probe `probe_perf.py`: `save_authored_image` over 8 MiB
  = 1.700 s (changed=4); `verify_emitted_image` alone = 1.336 s; one SHA-256 over
  8 MiB = 0.041 s.
- **Tests covering it:** yes for correctness
  (`test_write_invariants_property.py:274-281`, `test_authored_image.py:344-395`);
  no performance budget.
- **Remediation:** compute differing offsets from the declared spans only (that
  is exactly the invariant being asserted), keeping the current semantics and
  adding an equivalence test.
- **Before ROM-capacity/allocation work?** no, but on the same ticket - expansion
  adds spans to this same verification step.

#### CQA-15 [MEDIUM] Load-bearing constants and verified extents have multiple owners, and one copy is a live index bound

> **REMEDIATED: CQA-03-15-IDENTITY-AND-EXTENTS-001 (2026-09-23).** The inventory
> was re-run by measurement and found **more** owners than this finding records:
> **13** production GBA-base definitions under **four** spellings rather than eight
> under three, and **three live index bounds** it had missed
> (`data/placement_contracts.py` dialog text count, `data/script_effects.py` text
> count, and the character-roster bound). Migrated onto the profile/catalog
> authority: the canonical identity (six owners), the map-entry table address,
> count and stride, the text pointer-table address and count, the stat extents,
> both palette addresses, and the GBA base. The export stack resolves identity and
> extents through a thin `tools/export/profile_authority.py` over the **packaged**
> catalog, and the reader object carries accessors rather than module constants;
> the text codec lost the game extents it could not own and takes them from its
> caller. All four **live index bounds** now read the profile, including the
> `export/canonical.py` text index bound this finding names. The four contract-hash
> gates compare against `profile.sha256`, with each contract literal retained as a
> **pinned cross-check** asserted against the catalog for every profile. The GBA
> base has one authority, `webfoot/binary.GBA_ROM_BASE`.
>
> **The closure claim is precise:** *independent behavioural authorities* were
> removed or migrated. It is **not** that every canonical literal vanished: two
> pinned cross-checks survive in production data and no longer gate, format
> constants stay in the format layer, evidence/provenance labels stay as labels,
> and test oracles and research tooling keep independent measurements on purpose.
> The classification of every retained literal is in the record. Synthetic-profile
> tests replace every load-bearing extent with a different value and drive the
> production readers through it, so a reintroduced Buu literal fails; mutations
> confirm each guard is load-bearing. Finding **CLOSED**; CQA-04 remains **OPEN**
> and CQA-10 is unchanged (**PARTIAL / IMPROVED**). Record:
> [`../tickets/CQA-03-15-IDENTITY-AND-EXTENTS-001.md`](../tickets/CQA-03-15-IDENTITY-AND-EXTENTS-001.md);
> closure:
> [`../tickets/archive/CQA-03-15-IDENTITY-AND-EXTENTS-001-COMPLETE.md`](../tickets/archive/CQA-03-15-IDENTITY-AND-EXTENTS-001-COMPLETE.md).
> The text below is the finding **as originally recorded** and is not restated.

- **Location:** canonical ROM identity `940ad5f0...f059e` written three times in
  production (`map_render.py:72-74`, `export/map_browser.py:53-55`,
  `export/buu_resource_export.py:62-64`) plus `config/roms.yaml:13` as data, with
  a further copy in `atlas_build.py:36`, `atlas_producers/code_functions.py:33`,
  `atlas_producers/graphics_extents.py:30`, `data/behavior_triggers.py:12`,
  `data/placement_contracts.py:520` and `tests/conftest.py:43`;
  `MAP_ENTRY_TABLE_ADDRESS`/`COUNT` in `export/canonical.py:39-41`,
  `map_render.py:48`, `config/roms.yaml:44-47`,
  `atlas_producers/seed.py:290`, `export/buu_resource_export.py:96`;
  `GBA_ROM_BASE` redefined in eight modules under three spellings despite
  `binary.GbaRomBase`/`FileOffset` being the sanctioned helper;
  text count `1534` in `config/roms.yaml:58`, `formats/text_tables.py:65`,
  `data/placement_contracts.py:60`, `data/script_effects.py:11`,
  `export/canonical.py:223`, `placement_links.py:305`;
  stat extents in `formats/stat_tables.py:42-64` versus `config/roms.yaml:48-55`.
- **Observed:** the same identity/extent is restated in three to eight
  independent places with no cross-check. Two of the copies are not inert:
  `export/canonical.py:478-480` uses its own `TEXT_POINTER_COUNT` as a live index
  bound (ignoring the profile), and `map_render._verify_supported_rom` and
  `export/map_browser._verify_supported_rom` are the same function implemented
  twice against their own copies of the hash - while the **production map-layout
  writer** gates on the export module's copy.
- **Why it matters:** the portability claim is "per-game numbers live in
  `config/roms.yaml`, never in code" (`text.py:23-26`, `stats.py:15-20`). Adding a
  profile or a revision becomes a multi-file edit in which a missed copy fails
  **silently** in the readers and, for the writer, refuses with a message about a
  constant nobody changed. Allocation decisions must read one declared extent,
  not one of several copies.
- **Evidence:** repo-wide greps (owner and both reviewers, independently); the
  three byte-identical SHA literals compared character-by-character by the writer
  review; `_verify_supported_rom` diffed by the owner (identical condition, own
  constant, different error type).
- **Tests covering it:** no test asserts cross-module equality of any of these.
  The ROM-gated assertions each pin one copy to the local file, which is not the
  same check.
- **Remediation:** derive the accepted identity/extents from the verified profile
  (which `capability.require` already has) and keep at most one literal beside the
  profile catalog; at minimum, add an equality assertion so drift is loud.
- **Before ROM-capacity/allocation work?** **yes** - allocation must read one
  declared extent.

#### CQA-16 [MEDIUM] `handles.recover_handle` hard-codes one profile's contract and verifies no identity, so it fabricates identities for other 8 MiB images

- **Location:** `handles.py:34-70` (notably `:62` `CONTRACTS["buus_fury_usa_rev0_01c1707f"]`
  and the `:65` guard `0 <= pool < table <= len(image)`); called from
  `atlas.py:678-693` (`search_text`); reachable from `cli.py:1431-1435` and the
  Workbench Atlas browser.
- **Observed:** the function takes no profile, resolves the record pool from a
  literal key, and guards only with image *size* - which passes for all four
  catalogued profiles. It then scans Buu's pool range for a word whose bitfields
  match the caller's span and returns `packed_handle` and `reference_sites` as if
  they were that string's durable identity.
- **Why it matters:** the result is presented as "the packed u32 an event-resource
  record stores to address it". For a non-Buu image it reports an identity derived
  from unrelated bytes, with no indication that the wrong profile's contract was
  used - a research-vs-production boundary leak driven by a literal id inside a
  game-neutral API signature.
- **Evidence:** independent ROM/core review probe: a uniform 8 MiB image with one
  planted word returns `packed_handle 0x01002003` and
  `reference_sites ["0x0877C5E4"]`; the tests pin the profile-free behaviour.
  Owner read `handles.py:60-70`.
- **Tests covering it:** partially - the arithmetic is covered, the Buu path is
  covered (ROM-gated), no test passes a second profile.
- **Remediation:** make the contract an argument (or require the exact base hash),
  and have `search_text` take the profile from the session.
- **Before ROM-capacity/allocation work?** no - but before any second-profile text
  search is presented as trustworthy. Escalate if a patcher ever consumes
  `reference_sites`.

#### CQA-17 [MEDIUM] A `CONFIRMED` placement-to-enemy link is minted by an address-alignment test rather than by declared table identity

- **Location:** `entities.py:88-104`; consumed as `PlacementType.classification`,
  and as the author-facing gate in `scene.py:116-120,443-448` and
  `data/behavior_triggers.py:14-17`.
- **Observed:** the link is claimed when the placement-type table entry's address
  falls inside the enemy-stats extent on a record boundary
  (`relative % stats.record_size == 0`). The real justification is that both
  declarations name the same table in `config/roms.yaml:34,49` - a fact about the
  profile, not about arithmetic congruence. `docs/DEVELOPMENT.md` forbids promotion on
  alignment grounds.
- **Why it matters:** it is correct today only because the two declarations
  coincide. A profile that declared a placement-type table merely overlapping its
  enemy table would silently mint `CONFIRMED` links, and that string is the gate
  that authorises the `on_defeat` trigger.
- **Evidence:** owner read `entities.py:94-101`; profile declarations at
  `config/roms.yaml:33-51`; acceptance string at `data/behavior_triggers.py:17`.
- **Tests covering it:** partially - the ROM-gated test pins the Buu counts, not
  the derivation rule.
- **Remediation:** require the two declarations to name the same table explicitly
  and name that check as the evidence for the link.
- **Before ROM-capacity/allocation work?** no.

#### CQA-18 [MEDIUM] An author-facing trigger is documented "runtime-proven" while its own contract records the reading as an inference

- **Location:** `project/placements.py:33-37` (`BehaviorTrigger` docstring);
  `data/behavior_triggers.py:13-48` (the evidence text); surfaced at
  `scene.py:423-449,625-628` and `workbench/scene_tab.py:456-461`.
- **Observed:** the API docstring says "runtime-proven semantics" and the UI shows
  `on_defeat`, while the contract that authorises it says defeat and teardown are
  "CONFOUNDED in the captures" and that reading defeat as the gate "is therefore
  an INFERENCE ... not a measurement isolating defeat from teardown".
- **Why it matters:** the project's evidence discipline is applied correctly in the
  data file and discarded one layer up. An author choosing `on_defeat` is told the
  semantics are proven; the measured observable is "the actor was destroyed",
  which differs wherever an actor is removed without being defeated.
- **Evidence:** both texts quoted from source by the independent map review; owner
  confirmed the docstring at `project/placements.py:34` and the contract text.
- **Tests covering it:** partially - the trigger is tested for availability, not
  for what its label claims.
- **Remediation:** keep the mechanism, change the words - document the
  evidence-scoped reading and let the UI carry a tooltip citing the confound.
- **Before ROM-capacity/allocation work?** no.

#### CQA-19 [MEDIUM] `webfoot_lz._gamma` is unbounded, so a malformed container costs quadratic time

- **Location:** `formats/webfoot_lz.py:188-194`, reachable from
  `atlas_producers/scan.py:343,349,401,417` and `map_render.py:251,386`.
- **Observed:** the gamma loop has no bound on iterations, so a crafted stream
  grows an unbounded integer; measured 0.099 s / 8 KiB, 0.958 s / 32 KiB,
  12.7 s / 128 KiB, 46.8 s / 256 KiB, extrapolating to ~13 h at the 8 MiB image
  size. The export-side reader has `MAX_INPUT_BYTES`; the shipping decoder has no
  equivalent.
- **Why it matters:** a single malformed or hostile container turns a scan, a
  render or an open into an apparent hang. Ordinary canonical data is unaffected,
  so this is a robustness boundary rather than a live defect.
- **Evidence:** independent ROM/core review measurements; owner confirmed the loop
  body has no iteration cap.
- **Tests covering it:** partially - malformed-input cases exist for the strict
  reader, not for this bound.
- **Remediation:** bound the gamma loop the way `webfoot_strict` bounds input
  consumption, and refuse on exhaustion.
- **Before ROM-capacity/allocation work?** no.

#### CQA-20 [MEDIUM] The deploy job is not gated by the test job

- **Location:** `.gitlab-ci.yml:44-58` (`deploy-site`) versus `:37-42` (`test-sdk`).
- **Observed:** `deploy-site` has no `needs:` and no reference to the test job; its
  only rule is "default branch". `test-sdk`'s second rule
  (`$CI_COMMIT_BRANCH && $CI_OPEN_MERGE_REQUESTS == null`) can exclude the test job
  from a default-branch pipeline, and a rule-excluded job cannot fail anything -
  while `deploy-site` still matches and publishes.
- **Why it matters:** the deploy step is the one irreversible action in CI and the
  documented verification path for the public capability list. A commit whose
  tests never ran can be published. No public capability changes as a result of
  this audit, and `public progress impact` remains `NONE`.
- **Evidence:** structural fact `CONFIRMED` from the file; the
  `CI_OPEN_MERGE_REQUESTS` race is `INFERRED` (not reproducible here).
- **Tests covering it:** no.
- **Remediation:** give `deploy-site` `needs: ["test-sdk"]` (fails closed when the
  job is absent), or run the fast gate inside the deploy job before building.
- **Before ROM-capacity/allocation work?** no, but cheap.

#### CQA-21 [MEDIUM] The `fast` gate is not hermetic, and the only check that the published page matches the registry is inert everywhere

- **Location:** `tests/gates.py:40` and `docs/testing.md:18` (the "nothing beyond
  `.[dev]`" contract) versus
  `tests/unit/test_capability_registry.py:124-127,435-499`,
  `test_questline_rail.py:80`, `test_map_render.py:249`,
  `test_workbench_graphics.py:750-765`, `test_workbench_session.py:35-89`,
  `test_workbench_session.py` atlas skips, `test_resource_library_curation.py:498`,
  `test_mgba_capture.py:159`.
- **Observed:** gate members skip when a local build artefact is absent and fail
  when the temp root is inside the work tree. `dist/` is absent and gitignored, so
  the rendered-page check - the only assertion that the *published* page agrees
  with `src/data/capabilities.json` on ordering, tallies and the derived
  percentage - skips locally and is unreachable in CI, because the test job never
  runs Node and the deploy job never runs pytest.
- **Why it matters:** "`-m fast` passed" is not a machine-independent statement,
  and the deployed artifact's only semantic guard is inert everywhere. A ticket
  author reading a green local run cannot tell which assertions executed.
- **Evidence:** `Test-Path dist` false in the worktree; `.gitignore` ignores
  `dist/`; the CI file installs no Node in the test job and runs no pytest in the
  deploy job; `docs/testing.md:84-102` records the temp-root failures by name.
- **Tests covering it:** partially - `test_test_gates.py` verifies gate
  *membership*, never that gate members executed.
- **Remediation:** mark artefact-dependent assertions explicitly (and say so in
  the gate description), report a skip census, and run the registry check before
  `npm run build` in the deploy job.
- **Before ROM-capacity/allocation work?** no.

#### CQA-22 [MEDIUM] `tools/qa` probes are owned by no test and no gate, and the one cited as whole-class evidence can pass vacuously

- **Location:** `tools/qa/status_duplication_probe.py:52-60,99-121`; no test
  imports `tools.qa`.
- **Observed:** `status_sentences` reads private shell attributes
  (`window._status_context`, `window._status_project`). If that list is empty -
  attribute renamed, refactor, or nothing rendered - `offenders` is empty for all
  screens, the probe prints "clean" nine times and exits 0. There is no vacuity
  guard and no assertion that nine screens were reached, yet
  `docs/PROJECT_<local-state-name>:55-61` cites exactly this output as the whole-class
  evidence for a defect that took four rounds to close.
- **Why it matters:** the instrument, not the thing measured, silently stops
  working. The pytest guard for the same defect does assert non-vacuity, but that
  module is skipped in CI (CQA-08), so both can be quiet at once.
  `overlap_probe.py` is the better-behaved sibling (fixed `STATES` list, prints
  its denominator) and the two should share that discipline.
- **Evidence:** source read plus a repo-wide `grep` showing no test imports
  `tools.qa`; owner confirmed the vacuity path.
- **Tests covering it:** no.
- **Remediation:** make the probe fail closed on an empty measurement (assert the
  screen count and a non-empty sentence list) and add one test over its pure
  helpers.
- **Before ROM-capacity/allocation work?** no.

#### CQA-23 [MEDIUM] Undo ownership is inconsistent: the Maps undo is mode-blind, layout edits have no history, and the shell cannot reach the Graphics history

- **Location:** `workbench/editors.py:305`; `workbench/app.py:108-111,560-582`
  (`_active_undo_stack`); `workbench/graphics_tab.py:573-589` (a second
  window-context Ctrl+Z); `workbench/map_tab.py:534-540`.
- **Observed:** Edit -> Undo in Browse/Layout targets a hidden editor's placement
  history; the layout edit session has no history at all; the shell's
  `EditorHost.undo_stack()` returns `None` for the Graphics tab, which instead
  installs its own Ctrl+Z shortcut in the same window.
- **Why it matters:** the same key means different things on different surfaces,
  and one surface's undo silently mutates state the user cannot see. Adding
  allocation-bearing editors multiplies the ambiguity.
- **Evidence:** independent Workbench review reading plus probes; owner verified
  the second shortcut and the `None` return path.
- **Tests covering it:** partially - undo/redo behaviour per tab, not ownership.
- **Remediation:** settle one owner for the active undo stack (declare it on
  `EditorHost`) and either give layout edits a history or state plainly that they
  have none.
- **Before ROM-capacity/allocation work?** no.

#### CQA-24 [MEDIUM] "Revert unapplied" discards pending colours but leaves Apply enabled and the pending list on screen; Apply then silently does nothing

- **Location:** `workbench/graphics_tab.py:1400-1403` (`_on_revert`).
- **Observed:** the pending changes are cleared without refreshing the pending
  list or disabling Apply, so the next Apply is a no-op with no feedback.
- **Why it matters:** it is the same silence class as CQA-06/CQA-26 - the UI
  contradicts its own state - and the fix is one refresh call.
- **Evidence:** independent Workbench review probe; owner read the handler.
- **Tests covering it:** no.
- **Remediation:** call the pending-UI refresh after the revert and re-evaluate
  the Apply action's enabled state from the (now empty) pending set.
- **Before ROM-capacity/allocation work?** no.

#### CQA-25 [MEDIUM] Shell undo lambdas raise an unhandled exception on every shutdown with a wired history

- **Location:** `workbench/app.py:575-582` (`_refresh_undo_actions`).
- **Observed:** `canUndoChanged`/`canRedoChanged` are connected to Python lambdas
  that close over the shell and call back into `_refresh_undo_actions()`, which
  re-derives the stack and calls `canUndo()` on it. During teardown the stack's C++
  object is already deleted, so the call raises; the same function sets one
  `_undo_wired` flag, so only the first stack ever found is tracked.
- **Why it matters:** every quit with a non-empty Maps history prints tracebacks
  from inside Qt (exit code is still 0 on the version here). The codebase has
  already recorded this exact shape as a crash and fixed it in the Graphics tab by
  connecting to a C++ slot rather than a Python closure; the fix was not applied
  here. The single-flag wiring would also silently fail to track a second stack if
  another editor ever exposes one.
- **Evidence:** reviewer probe `probe_undo.py` reproduced
  `RuntimeError: libshiboken: Internal C++ object (QUndoStack) already deleted`
  from `app.py:580` and `:581`; owner verified the closure connections.
- **Tests covering it:** no.
- **Remediation:** connect the signal to a receiver-context slot (or guard the
  closure against a deleted object) and track connections per stack.
- **Before ROM-capacity/allocation work?** no.

#### CQA-26 [MEDIUM] SDK failures rendered as plausible zero/empty values instead of errors

- **Location:** `workbench/map_browser_tab.py:1574-1581` (`_working_pointer`
  returns `0`, which the same module then describes as "an empty cell" at
  `:1904-1906`); `workbench/graphics_tab.py:686` (`_effective_rgb` returns the
  canonical palette when the project read fails).
- **Observed:** a failed SDK read is converted into a value that is
  indistinguishable from a legal state, so the UI reports a confident falsehood
  rather than an error.
- **Why it matters:** this is the project's own named GUI failure mode, and it is
  worse than a dead click because the screen looks correct. In a map editor,
  "this cell is empty" is exactly the claim a user acts on.
- **Evidence:** independent Workbench review reading and probes; owner confirmed
  the fallback paths.
- **Tests covering it:** partially - the error fallbacks are asserted for value,
  not for what the user is shown.
- **Remediation:** return a sentinel that cannot be rendered as a legal state (or
  raise into the slot's handler) and show the failure in the status line.
- **Before ROM-capacity/allocation work?** unknown - yes if allocation surfaces
  reuse these readers.

#### CQA-27 [MEDIUM] Layout authoring has no SDK-side session facade, so pending-edit policy lives in a 1,986-line widget

- **Location:** `workbench/map_browser_tab.py:455,1893-1902,1965` (pending-edit and
  saved-vs-unsaved policy) versus the dialogue domain, which has
  `tools/webfoot/dialogue.py` as its facade.
- **Observed:** "what is pending", "what has been saved", "may Save As proceed"
  and "what does the title's unsaved count mean" are computed inside the widget,
  in the same class that owns layout, painting, mouse handling and the mode strip.
- **Why it matters:** the policy is untestable without a GUI, is duplicated in
  spirit by the shell's own `unsaved_edit_count()` path, and is the state that
  CQA-05 destroys. Every new authored surface either re-implements it or grows the
  widget further.
- **Evidence:** independent Workbench review reading; owner confirmed the class
  size (1,580 lines / 60 methods) and the absence of an SDK-side session object.
- **Tests covering it:** partially - behaviours are tested through the widget.
- **Remediation:** extract a thin SDK-side session object for the layout domain
  (mirroring `dialogue.py`) and let the tab render it.
- **Before ROM-capacity/allocation work?** no, but it is the cheapest way to make
  CQA-05's fix durable.

### C.4 LOW

Compact entries: location, issue, and the reason it is not higher. All are real
and none is currently worth a dedicated ticket.

| ID | Location | Issue |
| --- | --- | --- |
| CQA-28 | `write.py:140`, `workbench/theme.py:302,368`, `analysis/thumb.py:196`, `scene.py:410`, `map_render.py:688` | Six definitions referenced nowhere in the repository (verified by whole-repo token search): `GeneratedImage.contains_allocated`, `theme.css_rgba`, `theme.state_color`, `thumb.scan_push_prologues`, `scene.visible_text_options`, `map_render.load_canonical_rom`. Two of them (`contains_allocated`, `load_canonical_rom`) are plausible convenience API for the allocation work, so deletion should be a deliberate choice. |
| CQA-29 | `write.py:572-573` | Publication uses `os.link`, which fails on FAT/exFAT/some network shares, so a build cannot be written to a typical flashcart volume. Fails closed with no leftovers; no fallback and no filesystem-naming diagnostic. |
| CQA-30 | `write.py:508`, `workbench/build_panel.py:41-43`, `export/buu_resource_curate.py:2345`, `tools/qa/*`, `tools/runtime/*` | Windows/platform assumptions: `--out x.gba.` silently creates `x.gba`; the build output filename interpolates an unvalidated profile id; the curator CLI hard-codes `<resource-library>` as a default; three QA/runtime tools hard-code one developer's checkout path (a class the project has already fixed once elsewhere). |
| CQA-31 | `workbench/session.py:23` | The Workbench session model imports the CLI's **private** `_default_atlas_directory`; a refactor of a private CLI helper silently changes GUI behaviour. |
| CQA-32 | `map_layout_write.py:48-58`, `map_layout_edit.py:306-350`, `maps.py:548-559` | Repeated whole-table work: `MapLayoutWriter._layer` re-reads all 452 map records per call (measured 2.75 ms/call; 176 ms for a 64-cell grid build), and `Maps.map_placements` rescans all placements per call (78 ms across 452 maps). Bounded today; the pattern is what becomes a stall when allocation adds per-cell work. |
| CQA-33 | `text.py:689-755,839-852` | Every over-length text edit re-derives the whole relocation plan (document rebuild + allocator run) to learn whether the new total fits, so N over-length edits cost O(N²) document builds. Fails safe; latency only. |
| CQA-34 | `graphics.py:292-319` | A shared graphic's dimensions/depth are taken from the **first** consumer piece and never reconciled against the other consumers, so two pieces declaring different extents of equal byte size would silently transpose one of them. Whether the canonical corpus contains such a pair is UNKNOWN (needs the ROM). |
| CQA-35 | `compressed_dialogue.py:46-51,61-76,112-118` | The only authorable dialogue target's four numeric fields live in code rather than in profile data, and the GBA-window arithmetic is done by hand (`old_pointer - 0x08000000`) while the same function uses the sanctioned helper 25 lines later. It is the one path that writes a relocated payload and rewrites a pointer. |
| CQA-36 | `atlas_producers/seed.py:481-505` and siblings | Seed rows cite `config/roms.yaml` by **line number** and feed `CONFIRMED` atlas coverage; two citations have already drifted (`:501` cites `:47` for `enemy_stats`, actually `:48`). Cite the profile key instead, or assert the cited line's text. |
| CQA-37 | `formats/placement_links.py:235-242` | `image[dialog + 2]` is indexed without a bound check, so a boundary dialog pointer raises a raw `IndexError` instead of the function's own refusal. |
| CQA-38 | `formats/indexed_png.py:139-155,173` | The reader verifies no chunk CRC (the writer emits them) and calls `zlib.decompress` with no output bound, checking the expected size only after inflating. |
| CQA-39 | `formats/map_slots.py:163-171` | The docstring claims a caller "cannot get a plausible offset out of an opaque slot", but `source_file_offset` is unconditional and `ArrayShape`/`is_typed` are advisory. Documentation overclaim. |
| CQA-40 | `data/placement_contracts.py:9`, `atlas_producers/seed.py:346-357`, `placement_events.py:293-305` | A data table whose extent is documented UNKNOWN (the seed file says extent and count are "not simultaneously consistent") is indexed as production truth for relocation anchors and Thumb handler fetches. Fails loud (a `ValueError` on a non-Thumb word), hence LOW. |
| CQA-41 | `tests/gates.py:51-106` | The `writer` gate is a filename heuristic, so write-path tests whose names do not state the concern (the LZ encoder, the sprite payload planner) carry only `-m fast`; a ticket that edits the encoder and runs `-m writer` sees green. |
| CQA-42 | `scripts/test.ps1:9` | The repository's single test entry point runs the bare ~90-minute full suite with no gate selection, contradicting the Full-Suite Policy and `docs/testing.md`. |
| CQA-43 | `tests/unit/test_code_review_workflow.py` | Asserts exact English phrases in `docs/DEVELOPMENT.md` and is counted in the "passed" total, so a documentation reword turns CI red and the cheapest fix is to weaken the test. |
| CQA-44 | `tests/unit/test_write_invariants_property.py:47-61` | The property sweep is derandomized at a fixed 50 examples and nothing raises `WEBFOOT_PROPERTY_EXAMPLES`, so its discovery power is frozen. |
| CQA-45 | `workbench/app.py:546` | View -> Detailed Editor follows an editor *switch* but not the Maps mode change it depends on; the smoke test and a QA probe both work around it by forcing the action. |
| CQA-46 | `workbench/map_browser_tab.py` (`projectChanged`) | Declared and wired but never emitted. |
| CQA-47 | `workbench/atlas_browser.py` error path | Dereferences `self._host` unguarded, raising `AttributeError` instead of the message box when the tab is constructed without a host. |
| CQA-48 | `workbench/graphics_tab.py`, `map_browser_tab.py` (painter) | ROM-format constants and offset formatting in view code ("4 bytes, in place"; a literal 256 in the grid painter). |
| CQA-49 | `workbench/map_tab.py:595` | The placement workspace renders from `session.rom_image` where the documented contract says `map_image`. Safe today only because `maps` is `None` for a derivative, so it is latent rather than wrong. |
| CQA-50 | `workbench/map_tab.py:319-331`, `graphics_tab.py`, `widgets.py:_COLORS`, `theme.STATE_COLORS` | Duplicated UI state: `selected_map` has two writers; the map-support label is built twice; two role→colour tables exist, and the two differ (`theme.state_color` is unused and lacks the `edit` role). |
| CQA-51 | `workbench/map_tab.py:617,854`, `graphics_tab.py:722,748,777,850`, `launcher.py:201` | `QTimer.singleShot` callbacks holding widgets with no receiver context, so a timer can fire into a destroyed object. |
| CQA-52 | `workbench/map_browser_tab.py` `_on_save_as`, `graphics_tab.py` `_on_export` | The status line is set locally without publishing to the shell, so the authoritative status bar can go stale after a successful save/export. |

### C.5 INFO

| ID | Note |
| --- | --- |
| CQA-53 | **The allocator is single-sourced (positive).** `allocation.allocate`/`withhold` are the only first-fit and span-subtraction implementations; all four allocating call sites use them, and the build coordinator threads one reservation set through the domains in existing order. Two structural facts for the capacity ticket: (a) `capacity_regions`/`image_size` (generated expansion) reaches exactly one production domain today (`compressed_dialogue`), while placements and text are bounded by `profile.free_regions` and `profile.size`; (b) `GeneratedImage` requires the expansion to begin exactly at canonical EOF, so a "grow into a mid-image hole" policy is not expressible without a change to `write.py`. |
| CQA-54 | `docs/workbench.md:23-26` still describes the removed eight-tab shell. Stale documentation; the accepted visual direction changed the shell. |
| CQA-55 | **Verified-sound catalogue.** Recorded in section B so these are not re-litigated: ROM-write identity re-proof and rollback, `ByteChange`/`plan_changes` validation, `withhold`'s one-directional subtraction, `capability.require` fail-closedness, packed round-trip on 400 adversarial payloads, swizzle/unswizzle inverses at every OAM dimension, `script_vm.assemble` refusal and self-disassembly, atlas classification caps, and the Workbench's `is_safe_output_path` behaviour under case/separator/dot/junction/hard-link aliases. |
| CQA-56 | **Second expanding domain has no coordinator.** `plan_changes` requires `generated_allocations` spans to equal `generated_image.allocated_spans` exactly, and `build_project` derives `allocated_spans` from dialogue provenance alone. A second domain that expands must merge into one `GeneratedImage`, and no function does that today. Not a defect; a prerequisite to design for. |
| CQA-57 | **Host-side decoder bounds.** `tools/export/webfoot_strict.py` caps declared output at 64 KiB (`MAX_OUTPUT`) and packed input at 64 KiB (`MAX_INPUT_BYTES`). Both are documented as host-side safety bounds, not format limits; a capacity feature that legitimately exceeds them must revisit the constants deliberately rather than discover them. |
| CQA-58 | **Audit-method note (process, not product).** During this audit one reviewer's mutation experiment edited `tools/webfoot/write.py` in the shared audit worktree (removing the canonical-EOF straddle guard, marked `MUTATION-AUDIT-TT`) and reverted it. It was caught by a second reviewer reading the file, and the worktree ends clean at `1b276e3`. Consequence: citations taken from `write.py` during that window would have described mutated source. Mutation experiments in a shared worktree are worth isolating (`git archive` to a scratch copy), which one reviewer did. |

---

## D. Domain review summaries

**REVIEW A - ROM / CORE: COMPLETE.** 8 findings (1 CRITICAL, 3 MEDIUM, 4 LOW);
focused validation 480 passed. Verdict: the codec and address layers are
disciplined - typed `FileOffset`/`GbaRomAddress`, checked encode/decode pairs,
round-trip proofs, honest `UNKNOWN` labels - and the CRITICAL is a *premise*
problem (packed self-termination, CQA-02) rather than a parsing defect. Its
durable contribution is the identification of the conflicting engine-termination
claims and of the multi-owner constant/extent problem (CQA-15). The reviewer
explicitly verified as sound: pack/unpack round-trip on 400 adversarial payloads,
the indexed-PNG reader against Qt's independent decoder, swizzle inverses at
every OAM dimension, `capability.require`, MapEntry layout/struct/dataclass
agreement, stat codec span preservation, and the `data/` numeric tables.

**REVIEW B - WRITER / PROVENANCE: COMPLETE.** 11 findings (1 CRITICAL, 6 MEDIUM,
3 LOW, 1 INFO); focused validation 53 passed. Verdict: the ROM-write layer itself
is the strongest part of the codebase and needs extension, not replacement -
every hostile output shape it probed failed closed with the input intact - while the
*boundary* around it is where the risk is (CQA-01, CQA-10, CQA-11, CQA-13). Its
`os.link`/staging/rollback analysis, its hostile-path probe matrix, and
its `git archive`-based mutation method are the most reusable evidence in this
audit. One of its findings was **rejected by the owner** after verification
(CQA-12, reviewer correction recorded).

**REVIEW C - MAP / GRAPHICS / SCRIPT / ENTITY: COMPLETE.** 12 findings (2 HIGH,
5 MEDIUM, 5 LOW); focused validation 27 passed / 5 ROM-gated skips. Verdict: each
subsystem's interior is unusually disciplined (frozen records, fail-closed
codecs, explicit identity vs provenance), but the *seams* are the risk - two
production decode stacks never compared (CQA-04) and a session that pairs a
device-independent reader with a device-specific atlas without checking they
describe the same ROM (CQA-03). It also produced the sharpest evidence-discipline
findings (CQA-17, CQA-18) and measured the `palette_users` cost. One sub-claim was
narrowed by the owner after verification (the derivative image-source divergence,
recorded as CQA-49).

**REVIEW D - WORKBENCH: COMPLETE.** 19 findings (3 HIGH, 6 MEDIUM, 8 LOW,
2 INFO); focused validation 33 passed / 4 skipped and 120 passed / 1 skipped.
Verdict: no CRITICAL, and the canonical-ROM guard held under every alias probed
(case, separator, dotted, junction, hard link). The GUI's risk is state
ownership and refresh cost, not safety: in-memory authored state destroyed by an
unrelated editor (CQA-05), SDK error families escaping slots (CQA-06), and
full-corpus work per UI element (CQA-07). It also confirmed PySide6 optionality
is clean, which is a genuine positive. It made no visual claim, correctly: there
is no ROM in the audit worktree, so the GUI was never launched against real data.

**REVIEW E - TESTS / TOOLING: COMPLETE.** 10 findings (2 HIGH, 3 MEDIUM, 5 LOW).
Verdict: no CRITICAL, but two HIGH - CI silently skips 258 portable tests
(CQA-08) and the canonical-EOF straddle guard is untested (CQA-09). Its most
valuable contribution is the mutation-verified commendation list: it broke the
base-byte agreement check in `plan_changes` and two tests failed, which is the
standard the rest of the write path should meet. It also confirmed the ROM-gated
integration tree (61 files) cannot be verified in this environment **and is not
run by CI either**, so the entire real-ROM write/expansion/relocation proof set is
local-only.

---

## E. Test / CI observations

1. **CI's portable gate is not the portable suite.** 258 of 2,228 collected
   `tests/unit` items are hidden behind 15 module-level skips because CI installs
   `.[dev]` only (CQA-08). The older "PySide6 aborts collection" failure is
   genuinely fixed - collection now exits 0 - so the failure mode has changed
   from an error to a silence. This is the single most consequential CI fact in
   the audit.
2. **The real-ROM gate is local-only.** `tests/integration` is 61 files and never
   runs in CI; the audit worktree has no ROM, so every capacity, expansion,
   relocation, stat and text write proof was unverifiable here. The merged
   baseline's CI numbers therefore describe the *portable* suite only.
3. **Two guards are mutation-proven; one is not.** Deleting the base-byte
   agreement check in `plan_changes` fails two tests (commended). Deleting the
   canonical-EOF straddle guard fails **none** (CQA-09). That contrast is the
   best available summary of where the write path's test coverage is thick and
   where it is thin.
4. **The deploy job is not downstream of the test job** (CQA-20), and the only
   check that the published page matches `src/data/capabilities.json` is inert in
   every environment (CQA-21).
5. **QA tooling is untested and ungated**, and the probe cited as whole-class
   evidence for a GUI defect class can pass vacuously (CQA-22).
6. **Gate selection is a filename heuristic** and misses the write-path codec
   tests (CQA-41); the property sweep is frozen at 50 derandomized examples
   (CQA-44); `scripts/test.ps1` still runs the forbidden bare full suite
   (CQA-42).
7. **High-value guards that work well, and should be preserved as the pattern:**
   the base-byte agreement and forged-manifest cases in
   `test_write_invariants_property.py`; the allocation
   determinism/padding-exhaustion/ownership rules in `test_relocation.py` and
   `test_rom_expansion.py`; the negative-evidence-with-positive-controls
   discipline in `test_capacity_proof.py`; the four status-duplication guards in
   `test_workbench_project_status.py`; and `load_mgba_lua.ps1`'s before/after ROM
   hash checks.

---

## F. Remediation set

Bounded follow-up work, not a rewrite. Nothing here requires a new architecture.

### MUST FIX BEFORE ROM-CAPACITY-AND-ALLOCATION-001

| ID | Why it gates the capacity work |
| --- | --- |
| CQA-01 | One shared output-path guard plus tests. Capacity work adds more user-pathed writers, on top of a boundary that currently permits destroying the verified input. |
| CQA-02 | **Evidence resolution first** (which termination rule the engine uses), then make `pack` self-terminating (or refuse) and re-decode planned payloads on the write path. Expansion already writes packed output. |
| CQA-03 | One identity comparison in `open_rom`. The atlas carries `VERIFIED_FREE` spans and is the evidence base an allocator UI would read; a mismatched pairing is silent today. |
| CQA-04 | Decide one reader of record per binary concept and add an equivalence test. Capacity/allocation must agree with rendering, and the writer currently depends on the export-layer reader. |
| CQA-05 | Budget reallocation next to the existing writer, not alongside a callback that destroys in-memory authored state. |
| CQA-06 | Capacity fences in the loaders will each land on this uncaught path; a dead click is the worst possible signal for a fail-closed fence. |
| CQA-07 | The planned next authoring surface is modelled on this code; fix the shape before copying it. |
| CQA-08 | If the Workbench remains the authoring surface, its suite must actually run in CI. |
| CQA-09 | One regression test on the exact boundary the capacity ticket extends. |
| CQA-10 | One output-path policy owner, so new artefacts inherit the rule instead of re-deriving it. |
| CQA-12 | Capacity work will produce images whose base identity must be provable from disk. |
| CQA-15 | Allocation must read one declared extent/identity, not one of three-to-eight copies. |

### REMEDIATION ORDER

A roadmap aid, **not** permission to start: these are bounded tickets, not one
giant remediation branch.

1. **FIRST: CQA-01, output safety.** There is a demonstrated path that can
   overwrite the verified input and report success. Nothing else should be
   sequenced ahead of it.
2. **SECOND: CQA-02, packed-stream termination premise.** This needs an
   evidence-resolution step *before* the implementation correction can be
   selected safely, so it is not a straightforward code fix.

Then, dependency-aware grouping for the remaining must-fix set:

| group | findings | concern |
| --- | --- | --- |
| A | CQA-01 + CQA-10 | output-path safety ownership |
| B | CQA-02 | packed-stream termination evidence + encoder/write guard |
| C | CQA-03 + CQA-15 | ROM/profile/atlas identity and single-source constants/extents |
| D | CQA-04 | duplicated production decode-stack ownership/equivalence |
| E | CQA-05 + CQA-06 | Workbench state preservation and error-boundary handling |
| F | CQA-07 | Graphics refresh/corpus performance |
| G | CQA-08 | CI actually executes the portable Workbench/Capstone tests |
| H | CQA-09 | canonical-EOF straddle regression guard |
| I | CQA-12 | build provenance publication |

The MEDIUM set is **not** automatically promoted into mandatory work, and the LOW
findings are **not** to be batch-fixed.

### REMEDIATION STATUS

Added at the CQA-03-15 closeout (2026-09-23). This is the running state of the
must-fix set above; a finding's text is never edited, only annotated in place.

| finding | severity | status |
| --- | --- | --- |
| CQA-01 | CRITICAL | **CLOSED** - CQA-01-OUTPUT-SAFETY-001 |
| CQA-02 | CRITICAL | **CLOSED** - CQA-02-PACKED-STREAM-TERMINATION-001 |
| CQA-03 | HIGH | **CLOSED** - CQA-03-15-IDENTITY-AND-EXTENTS-001 |
| CQA-15 | MEDIUM | **CLOSED** - CQA-03-15-IDENTITY-AND-EXTENTS-001 |
| CQA-04 | HIGH | **CLOSED** - CQA-04-DECODE-STACK-AUTHORITY-001. Shared binary interpretation has one production authority (`tools/webfoot/formats/map_graphics.py`), the production map-layout writer no longer reads through `tools.export`, common-corpus equivalence was proved before the duplicate implementation was removed, and the two genuine historical divergences (layer-handler support; tile-bank decoded-extent policy) are reconciled or documented as deliberate outer policy. Independent review APPROVE, no findings. |
| CQA-05 | HIGH | **ACTIVE** - CQA-05-06-WORKBENCH-STATE-AND-ERRORS-001 |
| CQA-06 | HIGH | **ACTIVE** - CQA-05-06-WORKBENCH-STATE-AND-ERRORS-001 |
| CQA-07 | HIGH | OPEN |
| CQA-08 | HIGH | OPEN |
| CQA-09 | HIGH | OPEN |
| CQA-12 | HIGH | OPEN |
| CQA-10 | MEDIUM | **PARTIAL / IMPROVED** (not closed; output-safety ownership is done, overwrite-policy divergence remains) |

Remaining pre-capacity blockers, in the dependency-aware groups above:
**CQA-05 + CQA-06**, **CQA-07**, **CQA-08**, **CQA-09**, **CQA-12**, and
**CQA-10**. `ROM-CAPACITY-AND-ALLOCATION-001` therefore stays **BLOCKED**.

Next active ticket: **CQA-05-06-WORKBENCH-STATE-AND-ERRORS-001**, the group E work:
CQA-05 (a project mutation must not silently destroy staged map/layout edits) and
CQA-06 (`Session.open_rom` must not let sibling SDK error families escape the Open
ROM slot as a dead click). CQA-07's refresh-cost work is **not** folded in; its
dependency on these two is not established.

### SHOULD FIX BEFORE MAJOR NEW AUTHORING FEATURES

CQA-11 (one overwrite policy), CQA-13 (atomic atlas publication), CQA-14
(per-span verification cost, which grows with declared spans), CQA-23 (undo
ownership, before more editors arrive), CQA-26 (SDK failures must not render as
legal states in authoring surfaces), CQA-27 (an SDK session facade for layout
authoring, which makes CQA-05's fix durable), CQA-35 (dialogue pointer arithmetic
through the existing helpers), CQA-19 (bound the decoder before scanning more
inputs), CQA-20 and CQA-21 (CI honesty).

### CAN DEFER

CQA-16, CQA-17, CQA-18 (identity/evidence discipline at boundaries that are
correct today but under-specified), CQA-22, CQA-24, CQA-25, and everything in
C.4/C.5 except where noted above. LOW items should not be worked as a batch; the
two dead-code groups (CQA-28, CQA-50) are worth folding into whichever file is
touched next.

---

## G. Deferred / non-actionable notes

- **Rejected finding, recorded for transparency.** The writer review reported
  that the Workbench "cannot reopen its own output" as part of a provenance
  defect. That is documented, accepted behaviour:
  `docs/journeys/safe-build-and-derivative-reopen.md:72-80` states that
  Build-tab domains are built but not reopened, and that "that refusal is the
  designed outcome rather than a gap to paper over". Only the missing provenance
  *document* survived (CQA-12).
- **Narrowed finding.** The claim that two GUI map modes render *different
  images* for a derivative is not reachable (`maps` is `None` for a derivative);
  only the divergent rendering *capability* on the canonical ROM is retained
  (CQA-04), with the image-source half demoted to CQA-49.
- **Two reviewer HIGH ratings were reduced to MEDIUM** (CQA-09), because the
  guard in question is present and correct and the ticket's model classes weak
  boundary coverage as MEDIUM. The finding is still in the must-fix set.
- **Deliberate duplication that should NOT be "fixed":**
  `tools/export/webfoot_strict.py` against `webfoot_lz` is documented,
  reasoned, and asserted to agree on malformed cases by a dedicated test;
  `map_render`'s restated map-entry constants carry a cross-reference comment;
  the two `roms.yaml` files are byte-identical and guarded by a whole-file
  equality test. The problem in CQA-15 is the *unguarded* copies and the writer's
  dependence on one of them, not duplication as such.
- **The atlas is a research artifact loaded by a production surface.** Its
  identity check is CQA-03; its placement in a single global directory
  (`build/atlas`) and its non-atomic writer (CQA-13) are the adjacent facts worth
  remembering.
- **`atlas regenerate --out <a file>`** reaches `any(out.iterdir())` on a file and
  raises `NotADirectoryError` rather than a clean error. Folded into CQA-13's
  remediation rather than listed separately.
- **`webfoot graphics export` is the only unguarded write in `cli.py`;** the
  other ROM-writing commands are protected by `emit_image`. That asymmetry is
  what made CQA-01 possible and is worth remembering when adding the next
  subcommand.

---

## Special decision gate: can ROM-CAPACITY-AND-ALLOCATION-001 proceed?

**Not directly. It can proceed immediately after the must-fix set above.**

Answering the ticket's question literally: are there code-quality findings that
would make capacity experiments or a future production allocator unsafe or
misleading?

- **Unclear write ownership:** partly. The allocator is single-sourced
  (CQA-53, positive), but the *output-path* ownership is not (CQA-10) and the
  writer's canonical-identity gate comes from the export layer (CQA-15). Both are
  wiring changes.
- **Offset/address confusion:** no finding. `FileOffset`/`GbaRomAddress` are
  typed, distinct and validated; ad-hoc window arithmetic exists in exactly one
  production place (CQA-35, LOW).
- **Unsafe output handling:** **yes: CQA-01 (CRITICAL)**, plus CQA-10/CQA-11/
  CQA-13.
- **Untrustworthy provenance:** partly. The derivative-trust machinery is sound;
  the atlas pairing is not identity-checked (CQA-03) and the Build path emits no
  provenance document (CQA-12).
- **Duplicated allocator-like logic:** **no.** One allocator, one subtraction
  primitive, no duplicates. The duplication is in *readers* (CQA-04) and
  *constants* (CQA-15).
- **Binary-size assumptions:** partly. The generated-image contract is explicit
  and validated, and the canonical-EOF guard exists, but it is untested
  (CQA-09), and the packed encoder's termination is an unresolved premise
  (CQA-02). The 64 KiB host-side decoder bounds (CQA-57) are a known ceiling to
  revisit deliberately.
- **Platform/file corruption risks:** no data-loss risk found beyond CQA-01;
  `os.link`'s filesystem requirement (CQA-29) is a fail-closed usability limit.
- **Insufficient tests around mutation boundaries:** **yes: CQA-09**, and the
  real-ROM integration gate does not run in CI at all (section E).

---

## Limits of this audit

- **No canonical ROM was available** in the audit worktree, so every ROM-gated
  integration test skipped: no real-image capacity, expansion, relocation, stat,
  text, graphics or map-write behaviour was re-verified here. Claims about
  canonical data are either read from tracked documents or marked `INFERRED`.
- **The GUI was never launched against real data**, so no visual or
  interaction-quality claim is made, and the Workbench timing figures are
  measured floors (call counts and empty-project cost), not wall clock on real
  content.
- **Two findings depend on evidence outside this worktree** and are labelled as
  such: the engine's packed-stream termination rule (CQA-02, from transcribed
  disassembly) and the atlas-mismatch demonstration (CQA-03, from a reviewer
  probe with stubbed identification).
- **Coverage is representative, not exhaustive.** The reviews prioritised
  mutation boundaries, the write path, the map/graphics seams and the GUI state
  model. `tools/ghidra`, the Lua runtime probes, the Astro site and the archived
  research tree were inventoried but not reviewed as engineering subjects.
- Two independent reviewers' findings were re-verified by the owner; the owner
  rejects or narrows a finding only with a citation, recorded in section G.
