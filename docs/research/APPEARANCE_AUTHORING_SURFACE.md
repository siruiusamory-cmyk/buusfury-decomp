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
| engine lookup of the new id | the retail engine's own search executed and its record read reached index 232, through the base its instruction loads from the pool word measured `0x08800000`. A fall-through of the first loop reaches index 232 without the new record being SELECTED, so this shows the read happened and not that the engine chose it; the register was not read at that instant either | **PARTIAL, and weaker than it first reads** |
| bound sprite/visual configuration | the authored record binds a sprite id the accessor resolves | CONFIRMED statically, unobserved |
| an actor using it | a retail-engine observation | **NOT ESTABLISHED** |

The capability is therefore **not claimed**. `src/data/capabilities.json` keeps
`appearance` at `missing`, and its detail says what is implemented and what is
not.

### SC3.1 - How far the lookup link actually goes

**The matching rule, first, because it decides how much the numbers below are
worth.** The search runs two loops. Loop 1 returns the first record whose sprite
matches AND whose `+0x0C` is negative. Loop 2 is the fallback and returns the
first record whose sprite matches at all. An appended record sits last, so:

* an authored record whose sprite id a canonical record already selects is either
  never reached (loop 1 finds the canonical generic record first) or it replaces
  that record's resolution (loop 1 now matches an id that previously fell through
  to loop 2);
* **reaching index 232 therefore does not by itself mean the authored record was
  chosen.** A full fall-through of both loops reaches index 232 too, which is
  exactly what a search that found nothing would do.

The authoring surface now refuses a sprite id any canonical record selects, so the
first case cannot be authored any more; that refusal is not evidence about runs
made before it existed.

Link 3 is the one link with runtime evidence, and it goes further than a
deduction, but not all the way. Both halves were measured, in the same run:

* **Observed at runtime**, in the operator's own session (run `cale-drive-003`,
  map 40): the engine entered the id search at `0x08027948` **24 times**, entered
  the actor constructor at `0x08027390` **24 times** in the same frame, and the
  instruction at `0x08027968` - the loop's own record read - fired **3,540 times
  with a maximum index of 232**.
* **Measured in the built image**: the register that indexes the table is loaded
  at `0x08027962` from the literal-pool word at file `0x279D8`, whose value in
  this build is `0x08800000`. The loop forms the record address as
  `(index << 4) + base`, so index 232 addresses `0x08800E80`.
* **Measured in the built image**: `0x08800E80` holds the authored record,
  `(1188, 1189, 137, 0, -1)`.

So the engine read the authored record at the address the build placed it, and
that is established by an observed instruction plus a measured word rather than
by inference about behaviour.

**What is still missing, stated plainly.** The register was not read at the
moment of the read, so the chain rests on "the only value that instruction can
have loaded is `0x08800000`" rather than on a recorded `r1 = 0x08800000`. And no
actor has been observed carrying the id. The observer now writes both on the
first hit, but the hit has not recurred since.

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

**Nine sessions were run. Eight were wasted by a mis-armed instrument; the ninth,
driven by the operator, reached the lookup and the observer failed to write down
the value that would have closed it.** The correction is the useful part of this
section, so it is recorded in full: the failure mode, the self-calibration that
proved the instrument, the real measurement about which game paths consult the
appearance table, and the exact single thing still missing.

Vehicles, both tracked and both accepting an expanded image by exact digest and
size:

* `tools/runtime/start_toolkit031_session.ps1` with `-ExpectedRomSize 16777216`;
* `tools/runtime/run_capacity001_expansion.ps1`, the wrapper CAPACITY-001 wrote for
  a generated image, which also writes `state-loaded.txt` and watches the marker's
  content rather than its existence.

Observer: `tools/runtime/appearance001_table_watch.lua`, read-only, added to the
`$allowedLua` allow-list in `tools/runtime/inject_mgba_lua.ps1`, passing
`tests/unit/test_mgba_capture.py` and `tests/unit/test_mgba_runtime_skill.py`. In
its final form it arms fifteen sites: the six reader functions' entry points, the
six literal-pool base-load sites inside them, the search loop's record read, the
roster walk's patched bound, and the animation frame advance as a liveness
channel.

Every run used the same deterministic 16 MiB build, named by exact digest
(`2BC60563B8768E57DAF4D45C2EEF38EC17EB71313DAA211DDF46467A91177495`), and the
canonical game's own state 1.

**The instrument was wrong, and that is what the first eight runs measured.** They
are kept here because the correction is the useful part.

The failure had one shape: **an address that never executes and a channel that
never delivers look identical from outside**, and the early runs had no way to
tell them apart. Three controls and a self-calibration run separated them.

1. `tools/runtime/toolkit031_execution_watch.lua`, the repository's own execution
   observer, unmodified, against the canonical image from the same savestate: 78
   `STRUCT` rows (its frame-driven samples) and **zero `INTERP`, zero `EXEC`
   rows**. It did not settle the question: its execution channels watch the script
   trampoline and the interpreter, which only run when a script does, and that
   scene drives no dialogue.
2. `tools/runtime/run_mgba_capture.ps1`, the GDB venue, on the canonical image from
   the same savestate, after provisioning the two ignored local prerequisites a
   fresh worktree lacks (`roms/` and `.venv/`, both junctions to the primary
   checkout; `.venv` is excluded through the common git directory's
   `info/exclude`, because `.gitignore`'s `.venv/` does not match a Windows
   junction). Two runs, `-MaxStops 4 -WindowSeconds 120`, five ROM addresses
   between them: **zero stops**.
3. `tools/runtime/p006c_dev_breakpoint_probe.lua`, the repository's own capability
   probe: 120 frame rows, **zero breakpoint rows**.

**Self-calibration settled it.** The frame callback works, so the observer was
taught to read the program counter from it, and then to arm a breakpoint on the
address it had actually seen executing. That is a breakpoint on a known-live
address, which removes the guess entirely:

| armed at | address space | observed at run time | breakpoint hits |
| --- | --- | --- | --- |
| `0x03000C5C` | IWRAM | 60 samples in 1500 frames | **24,453** |
| `0x03000C5C` | IWRAM | 6 samples in the same run | **12,404** |
| `0x0803F6D4` | ROM | 5 samples | **421,167** |

So the channel works, in both address spaces, and the addresses the earlier runs
blamed were simply **cold**: idle play, the Status screen, the Skills screen,
walking and NPC dialogue do not execute the appearance readers at all. That is a
real measurement about the engine, and the opposite of what the earlier runs
appeared to say.

**The operator's own session found the path.** With the six reader functions'
entry points armed as well as the base-load sites, a driven session reached it
(run `cale-drive-003`, map 40, frame 7642):

```
entry actor_constructor hits=24   first_frame=7642
entry id_search        hits=24   first_frame=7642
entry record_consumer  hits=8    first_frame=7725
base  constructor hits=24   base search hits=3540   base consumer hits=8
search_hits=3540  max_index=232  .
```

That is the lookup link, and it arrived from an operator's hands, not from a
theory. **The observer then failed to record the values that would have closed
it**: the "is this base the relocated table" test compared a GBA address against a
file-offset range, so nothing was written to disk and the run looked empty. A
second defect was found in the same place: `summarise` referenced `started` as a
global, because the local was declared later in the chunk, so two fields always
read nil.

Both are fixed. The observer now records, on the first hit, the index, the table
base, whether that base is the relocated one, the record address, the record's
sprite id, the record's four words, and a screenshot of the moment; and it writes
a live progress file every 300 frames so a session can be read while it runs.

**Savestates do not reach it.** All five saved states in the local ROM directory
(active maps 39, 38, 27, 247, 138) were loaded against the built image with no
input: **none** enters the appearance readers. The trigger is an in-game event,
and a state load restores already-built actors.

**Automated driving did not reach it either.** Three drives ran without an
operator, with the animation frame advance live in each (768, 1536 and 832 hits),
so gameplay and actor animation were running in every one:

1. a wandering schedule from the canonical state, 12,000 frames, active map 39
   throughout;
2. a boot to a loaded save through the title and continue prompts, 10,800 frames,
   which did cross a real map load (active map 38 becomes 39) and still reported
   none of the six readers;
3. the same boot with the wander appended after the menu, 10,800 frames, active
   map 39.

The one difference that matters is the map: the only run that ever reached the
lookup was on **map 40**, and no savestate in the local set is on map 40. Reach
that map with an operator walking out of the park the canonical state starts in,
and the observer as it now stands writes the register value and the record's words
on the first hit.

**What the whole set establishes.** The instrument works. The appearance table is
not consulted by idle play, the status screens, dialogue, walking, or a state
load. It was reached once, by the operator, at **frame 7642 of a 150-second
session**, and every later session ended earlier - 4800 frames and 3600 frames -
so the mark was never reached again.

**The single next experiment.** One driven session of at least two and a half
minutes on map 40, which is where it fired, with the observer as it now stands.
The first hit writes the register value and the record's words. If the trigger
cannot be re-reached that way, the fallback is the GDB venue, which needs two
changes this ticket does not make: a size guard that admits an expanded image, and
a worktree virtualenv. Both are runtime-infrastructure work and belong to their
own ticket.

## SC7 - Open, and honest about it

* **The runtime chain is unestablished**, and it is the only reason the capability
  is not claimed. Everything else in `SC3` is measured.
* **The roster's flag array is sized for 232 entries** (see the gate record,
  section 5). The theoretical maximum of simultaneously set flags rises by one
  per authored definition, which a scene in ordinary play does not approach.
* **A new text-table id is not authorable**, so an authored definition shares a
  retail definition's on-screen name. That is a limit, not a defect: creating text
  ids is not shipped for any capability.
