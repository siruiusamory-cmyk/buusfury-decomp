# The authored-appearance surface (APPEARANCE-AUTHORING-GATE-001, Phase B)

Phase A proved growth; this is what was built on it, and it is honest about the
one thing that is not finished. The gate record, the census and the exact
required updates are `docs/research/APPEARANCE_TABLE_GROWTH.md`.

Baseline `ticket/appearance-authoring-gate-001` at
`9360379df45b2b928c0321d76c54226799b8235a`, canonical image
`940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e`, re-hashed
unchanged after every run described here.

## SC1 - The ten-question design pass

`docs/desktop-ui.md` requires these answers before any widget code. The answers
are short because the surface is a strip plus one form dialog, and the shape is
the authored-sprite strip `SPRITE-PROJECT-SURFACE-001` established.

1. **Primary task.** Create, edit and remove the project's new appearance
   definitions, and see what each one binds.
2. **Primary visual object.** The selected definition, described in the words the
   author chose: its project name, the on-screen name index and the sprite id.
3. **Selection and context model.** A combo of the project's authored definitions
   in name order. The tab has one selection at a time; the strip's Edit and Remove
   act on it.
4. **Primary actions.** `New authored appearance...`, `Edit...`, `Remove`, each
   writing `appearances/appearances.toml` through the domain's one write path.
5. **Secondary actions.** None. Undo and Redo are the tab's existing stack, and
   Apply/Revert is the palette's; the authored document commits on accept, exactly
   as the authored-sprite document does.
6. **Hidden technical information.** The record's own index, the record layout,
   the relocation, the five rewritten literal words and the three patched count
   bounds. None of them is a control.
7. **Keyboard path.** The dialog's own focus order - name, on-screen name, sprite
   identity - and its OK/Cancel buttons. The strip buttons are ordinary push
   buttons reachable by tab.
8. **Empty, error and disabled states.** No project: "No project open." and every
   button disabled. Project unreadable: "Project unreadable." and the parse error
   in the summary. Profile without the table: "Authoring not available." No
   authored definitions: "No authored appearance." and only Create enabled.
   A draft the SDK refuses: the dialog states the refusal and disables its OK
   button, so a refused draft can never be committed.
9. **Expected data volume.** One to twenty-three definitions, bounded by the count
   a Thumb `cmp rN,#imm8` can state.
10. **Performance risks.** None measured. Validation reads the image's five
    published words and the 232 records - microseconds - and the allocation is the
    build's, not the dialog's.

## SC2 - What the surface exposes, and what it refuses

Exposed: the project name, the on-screen name (an existing text index, labelled
with the retail string it resolves to when the project carries a text table), and
the sprite identity (the ids the canonical records select, plus the id an authored
actor-sprite identity in the same project takes, each labelled with the retail
definition that first selects it).

Refused by name, from the shared validation the build runs: a text index outside
the declared table or one with no successor inside it; a sprite id below the
accessor's floor of 10 or above what the registry reaches; a project that would
exceed the count ceiling; and a project whose image does not publish the table's
anchor, its five inbound words, or a relocatable anchor.

Not offered, and stated as out of contract: a new text-table id, a portrait slot,
and a stat record.

## SC3 - The evidence chain for the capability claim

| link | evidence | status |
| --- | --- | --- |
| authored appearance id | the document, re-read by `read_project` after a write | CONFIRMED |
| built table record | a real build: the 233rd record at file `0x800000`, the five words and three bounds patched, nothing else canonical changed | CONFIRMED |
| engine lookup of the new id | a retail-engine observation | **NOT ESTABLISHED** |
| bound sprite/visual configuration | the authored record binds a sprite id the accessor resolves | CONFIRMED statically, unobserved |
| an actor using it | a retail-engine observation | **NOT ESTABLISHED** |

The capability is therefore **not claimed**. `src/data/capabilities.json` keeps
`appearance` at `missing`, and its detail says what is implemented and what is
not.

## SC4 - What shipped

* `tools/webfoot/appearances.py` - the declared table, the record codec, the
  vocabulary helpers and the published reference graph (one anchor plus the five
  `CONFIRMED_REFERENCE` `ABSOLUTE_ROM_U32_LE` words, re-checked against the image
  before they are rewritten).
* `tools/webfoot/appearance_authoring.py` - the plan and the project surface.
  The plan re-emits the whole table above canonical EOF with the authored records
  appended, copies the canonical records verbatim, rewrites the five words,
  patches the three count halfwords, fails closed past the `imm8` ceiling, fails
  closed when the profile declares no generated expansion, and produces a
  `RelocationProvenance` plus a `GeneratedAllocationProvenance` for the manifest.
* `appearances/appearances.toml` in the project model, with `AuthoredAppearance`,
  `AuthoredAppearances`, a writer and a reader, wired into `read_project`.
* `tools/webfoot/build.py` - `_check_appearances` (validation) and the
  materialisation, which runs after the sprite identity so a definition may bind
  the id that identity takes.
* `tools/webfoot/workbench/appearance_dialog.py` and an "Authored appearance"
  strip in the Graphics tab, with its own `AuthoredAppearanceCommand`.
* Five SDK seams, each named by a measurement rather than a preference:
  `AllocationKind.APPEARANCE_RECORD_TABLE` and its `EXPANDED_ONLY`
  addressability; `appearance_record_table` in `layout.RELOCATION_ELIGIBLE_KINDS`
  and in `relocation._ALLOCATION_KIND`; the profile's `appearances` table in both
  the local and the packaged `roms.yaml`; and `Capability.APPEARANCES`.

## SC5 - Validation

Measured in the ticket worktree, canonical image unchanged throughout.

```text
python -m pytest tests/unit -q
  4186 passed, 45 skipped

python -m pytest tests/integration/test_appearance_authoring_rom.py -q
  16 passed          (canonical-ROM gated, read-only)

python -m pytest tests/unit/test_appearance_authoring.py \
                 tests/unit/test_workbench_appearance_authoring.py -q
  26 passed
```

The integration suite builds a real image twice from the same project and asserts
the two are byte-identical, that the manifest records the relocation, that no
canonical byte outside the eight named sites changed, and that a project which
authors nothing reproduces the base image exactly.

## SC6 - The runtime attempt, and its honest result

**Five runs were made under two governed vehicles, and none of them produced
execution evidence. A control run then showed why: the scripted-breakpoint
channel is inert in this environment, for every observer, not only this one.**
The record is here because the failure is the instrument's and because the next
attempt should not repeat any of it.

Vehicles, both tracked and both accepting an expanded image by exact digest and
size:

* `tools/runtime/start_toolkit031_session.ps1` with `-ExpectedRomSize 16777216`,
  runs 1 to 3;
* `tools/runtime/run_capacity001_expansion.ps1`, the wrapper
  CAPACITY-001 wrote for a generated image, runs 4 and 5.

Observer: `tools/runtime/appearance001_table_watch.lua`, read-only, added to the
`$allowedLua` allow-list in `tools/runtime/inject_mgba_lua.ps1`, passing
`tests/unit/test_mgba_capture.py` and `tests/unit/test_mgba_runtime_skill.py`.
Five sites: the id search's record read at `0x08027968`, the roster walk's patched
bound at `0x08024F92`, the sprite-id accessor at `0x08000158`, the appearance
record consumer at `0x08025E50`, and the animation frame advance at `0x0800DE6E`.

Each run: a deterministic 16 MiB build named by exact digest
(`2BC60563B8768E57DAF4D45C2EEF38EC17EB71313DAA211DDF46467A91177495`), the
canonical game's own state 1, observer injected, state loaded afterwards through
the wrapper's confirmed path, 1800 frames after the load signal.

| run | vehicle | liveness channel | observed |
| --- | --- | --- | --- |
| 1 | toolkit session | sprite accessor, record consumer | nothing fired |
| 2 | toolkit session | plus the roster bound | nothing fired, active map 39 |
| 3 | toolkit session | plus the animation frame advance | nothing fired, active map 39 |
| 4 | capacity wrapper | all five sites, marker protocol | nothing fired |
| 5 | capacity wrapper | all five sites, state-loaded gated | nothing fired |

Every run reported the core running gameplay (`active_map_index=39`) and every
arming call returned a breakpoint id, so the API accepted every registration.
Run 5's liveness channel was the animation frame advance at `0x0800DE6E`, which
executes once per animating actor per frame; it fired zero times.

**The control, and exactly how far it goes.** Three controls were run, in
increasing order of how much they settle.

1. `tools/runtime/toolkit031_execution_watch.lua`, the repository's own execution
   observer, unmodified, against the canonical image from the same savestate under
   the same vehicle: 78 `STRUCT` rows and **zero `INTERP`, zero `EXEC` rows**. That
   control does not separate a broken channel from a scene that ran no script: its
   two execution channels watch the script trampoline and the interpreter, which
   only run when a script does, and this scene drives no dialogue.
2. `tools/runtime/run_mgba_capture.ps1`, the GDB venue, on the canonical image
   from the same savestate, after provisioning the two ignored local prerequisites
   a fresh worktree lacks (`roms/` and `.venv/`, both junctions to the primary
   checkout; `.venv` is excluded through the common git directory's
   `info/exclude`, because `.gitignore`'s `.venv/` does not match a Windows
   junction). Two runs, `-MaxStops 4 -WindowSeconds 120`: one with
   `-Breakpoint 0x0800DE6E`, one with `-Breakpoint 0x0800F3C0` plus
   `0x08000158`, `0x0800DE6E` and `0x08008086`. **Zero stops in both.**
3. `tools/runtime/p006c_dev_breakpoint_probe.lua`, the repository's own capability
   probe, whose header states its purpose as confirming that a scripted breakpoint
   callback resumes emulation and exposes live registers. Run against the canonical
   image from the same savestate: 120 frame rows and **zero breakpoint rows**.

**What the whole set establishes.** The frame callback works, memory reads work and
the core runs gameplay. Five appearances runs and three controls produced not one
observed instruction, by either venue, on any address tried. So the honest
statement is narrower than "the appearance path was not taken" and wider than "the
Lua channel is broken": **instruction execution could not be observed at all with
the tooling available in this worktree.** Under `docs/skills/mgba-runtime.md`
section 8 the instrument is unproven, and no absence measured with it means
anything about the appearance path. It also does not mean the addresses are cold:
that question is not settled either, and settling it needs the instrument fixed
first.

That is a runtime-infrastructure matter. This ticket's non-goals forbid runtime
infrastructure work, so it is recorded rather than repaired here.

**The single next experiment.** Fix or replace the execution instrument before
making any more appearance runs, and prove it on a control first. The order that
settles it fastest:

1. Determine why no instruction executes under observation here, using the
   repository's own probe as the test:
   `tools/runtime/p006c_dev_breakpoint_probe.lua` against the pinned mGBA build
   (`0.11.0.0`, sha256
   `C91FF99B8F267A57EF50237166B715DCE2FB978A63D23A75E14E6B356BD5C9BD`) on a scene
   that certainly reaches its address, or on a reset core. If that probe records
   breakpoint rows anywhere, the instrument works and the appearance run's
   addresses were the problem instead.
2. Only then repeat the appearance observation, with the animation frame advance
   as the liveness channel it was always meant to be.
3. If the instrument cannot be made to work under this build, the GDB venue is the
   fallback, and it needs two deliberate changes that this ticket does not make:
   a size guard that admits an expanded image, and a worktree virtualenv.

All three are runtime-infrastructure work and belong to their own ticket.

## SC7 - Open, and honest about it

* **The runtime chain is unestablished**, and it is the only reason the capability
  is not claimed. Everything else in `SC3` is measured.
* **The roster's flag array is sized for 232 entries** (see the gate record,
  section 5). The theoretical maximum of simultaneously set flags rises by one
  per authored definition, which a scene in ordinary play does not approach.
* **A new text-table id is not authorable**, so an authored definition shares a
  retail definition's on-screen name. That is a limit, not a defect: creating text
  ids is not shipped for any capability.
