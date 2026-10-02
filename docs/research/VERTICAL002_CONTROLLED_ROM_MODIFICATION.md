# VERTICAL-002 first controlled observable ROM modification

A controlled one-byte ROM mutation driven from a semantic SDK operation, with the
prediction recorded before the build and observed in the running game.


## Result

**FIRST CONTROLLED OBSERVABLE SDK->ROM->GAMEPLAY MODIFICATION: YES.**

```text
semantic SDK operation   `stats set enemy:434 hp 1`
-> controlled ROM mutation   exactly 1 byte, 0x00711BE0, 0xAF -> 0x01
-> running Webfoot game      mGBA 0.10.5, modified image
-> predicted gameplay effect newly spawned wolves died in 1 hit, not the baseline 4
```

This closes the gap left open by VERTICAL-001, which reached Outcome C: a patch
that propagated into the live runtime object without changing behavior. The
project can now demonstrate an intentional, *predicted*, *observed* gameplay
change produced entirely through shipped SDK capability.

## Target selection

`enemy:434`, table index 86, ROM file offset `0x00711BDC`.

Identity was corroborated from three independent places before any edit, rather
than assumed from the CLI's example string:

| Evidence | Says |
|---|---|
| `docs/PROJECT_<local-state-name>:198` | "wolf selectors are contiguous 434-439" |
| `docs/PROJECT_<local-state-name>:156` | "Wolf base EXP is 225" - the record's EXP is 225 |
| `docs/PROJECT_<local-state-name>:166-169` | Wolf fixture: 175 displayed HP, **4 hits to kill**, 47-52 displayed damage |
| `tools/webfoot/formats/stat_tables.py:249` | "HP 175, which is unique across the table" |

Decoded canonical record: `hp=175 exp=225 type_id=434 level=60 str=10 pow=0
end=20`. `type_id=434` matches the semantic identity, which is what makes this
the wolf record rather than a record that merely sorts near one.

## Prediction, recorded before the build

Written before `stats set` ran, to prevent retrofitting:

> If `enemy:434` supplies the encountered wolf's initial HP, then after changing
> HP 175 -> 1 the wolf will die from the **first** successful normal melee hit
> instead of the baseline 4, because one hit deals 47-52 displayed damage.

Corollary recorded at the same time: EXP should remain 225, since the EXP field
is untouched. Unchanged EXP alongside changed lethality distinguishes "right
record" from "wrong record".

## The edit

Produced through the supported CLI path; the ROM was not patched by hand.

```text
webfoot stats set "roms/Dragon Ball Z - Buu's Fury (U).gba" enemy:434 hp 1 \
  --output build/vertical-002/buus-fury-wolf-hp1.gba \
  --manifest build/vertical-002/manifest.json
```

| Property | Value |
|---|---|
| Field | `hp`, 3-byte LE at record `+0x04` (`stat_tables.py:302`) |
| Old -> new | 175 -> 1 |
| Changed bytes | **exactly 1 of 8,388,608** |
| Offset | `0x00711BE0`, `0xAF` -> `0x01` |
| Canonical SHA-256 | `940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e`, **unchanged** |
| Output SHA-256 | `4a525eedd23a8c8e4332c7f5a7eff3d3308f29481d6ec514d53f3cf460d06f20` |

Full-image diff was computed byte-by-byte, not sampled: one offset differs.
Re-decoding the modified record returns `hp=1` with `exp=225 type_id=434
level=60 str=10 pow=0 end=20` - every other field intact.

## Runtime

| Item | Value |
|---|---|
| Emulator | pinned mGBA 0.10.5 (`build/tools/mgba-0.10.5/...`) |
| ROM | `build/vertical-002/buus-fury-wolf-hp1.gba` (modified) |
| State | working copy of `build/research/p003-exp/single-wolf.ss1`; original hash re-verified unchanged |
| Action | one hit on the wolf already in the state; then reloaded the area and hit each of the two freshly spawned wolves once |

Observed, in one session:

| Wolf | Constructed by | Hits to kill |
|---|---|---|
| Already present in the loaded savestate | canonical ROM, before the patch existed | **4** (baseline, unchanged) |
| Two wolves spawned after reloading the area | the modified ROM | **1 each** |

**Prediction matched for every wolf constructed after the patch.** Baseline for
this fixture is 4 hits (`PROJECT_<local-state-name>:166-169`).

No runtime instrumentation was needed. Human gameplay observation was
sufficient and unambiguous, so the record's escalation path (section 12) was
never entered.

## New evidence: initial HP is seeded at actor construction

Before the run a risk was flagged: `single-wolf.ss1` was captured on the
canonical ROM with a wolf already spawned, so if HP is seeded at spawn time that
wolf would retain 175 HP, and reading it as a negative result would be an
invalid setup (failure class D) rather than a real refutation. A probe of the
savestate for a baked HP value returned nothing, but savestates are PNG-wrapped
and compressed (`docs/runtime-capture.md:221`), so that probe proved nothing and
was not treated as evidence.

The observation settles it, in the direction the risk anticipated:

- the **pre-existing** wolf still took **4** hits;
- the two wolves constructed **after** the area reload took **1** each.

### OLD CLAIM / NEW EVIDENCE / RESOLUTION

**OLD CLAIM:** the modified enemy stat might be re-read when loading the
savestate, so a savestate wolf would show the change.

**NEW EVIDENCE:** the wolf serialized in the savestate retained its original
effective HP and required four hits, while wolves constructed after the area
reload on the same modified ROM died in one hit.

**RESOLUTION:** enemy base HP is used when constructing/seeding the actor's live
HP state. The instantiated actor thereafter carries live current HP
independently, consistent with the previously established `target+0x28C`
current-HP field (`PROJECT_<local-state-name>:175`).

This makes the run *stronger* than a uniform result would have been. The
surviving 4-hit wolf is an unplanned in-run control: it shows the modified ROM
did not globally weaken combat, damage output, or the hit path, because an actor
built before the patch behaved exactly as it always had **in the same session,
on the same image**. The effect tracked precisely the boundary it should have -
actors constructed from the modified record, and only those. That is what
separates a genuine record-level cause from an incidental one, and no
single-outcome result could have shown it.

Practical rule for future records:

> A savestate only tests ROM stat changes for actors instantiated after the
> state is loaded. Reloading the area is sufficient to construct new actors from
> the modified stat data.

Scope: this rule is established for **enemy stat data only**. Do not generalize
it to text, placements, scripts, dialogs, graphics, or any other resource type;
each has its own load timing and none was tested here.

## Validation

No production code changed, so per record section 15 the full suite was not run.
Focused capability tests:

```text
tests/unit/test_stat_tables.py
tests/integration/test_stat_tables_rom.py
tests/integration/test_stat_write_rom.py
=> 53 passed / 0 failed
```

Five tests initially reported `ERROR at setup` with
`PermissionError: [WinError 5] Access is denied` on pytest's temp directory
(`AppData\Local\Temp\pytest-of-<user>`). That is a Windows sandbox filesystem
restriction, not a test failure. Re-running the affected scope
(`test_stat_write_rom.py`) with a writable `--basetemp` gives **20 passed**. No
assertion failed at any point.

No full-suite rerun was performed, and no derived aggregate suite total is
reported for this record.

Note that `test_wolf_hp_edit_is_attributable_to_its_semantic_owner` already
existed and already passed. The static capability was never in doubt; what was
missing was ever running it in the game.

## Product implication

Per record section 19, this clears TOOLKIT-022 to focus on true authoring rather
than on proving the existing write path works. The write path works, and it is
now demonstrated end to end.

One qualification worth keeping visible: this proves the SDK can **modify** an
existing record and change the game. It does not prove the SDK can **author**
new content - creating a placement, a script, or a text entry remains blocked by
the project format and by verified free capacity. See
`docs/research/SDK_STRATEGIC_AUDIT.md`.
