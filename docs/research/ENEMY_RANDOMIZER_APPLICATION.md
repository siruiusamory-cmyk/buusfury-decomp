# The shared randomizer foundation and the standalone Enemy Randomizer

ENEMY-RANDOMIZER-EXE-001. Two deliverables that are really one: a reusable
application foundation under the randomizers, and the second product built on it.
The Map Warp Randomizer was retrofitted onto the same foundation in the same
change, because a foundation with one client is a guess.

## Product identity

| | |
| --- | --- |
| Product name | Enemy Randomizer |
| Version | 0.1.0 |
| Modules | `enemy-placement` v1, `enemy-stat` v1 |
| Launch seed | `StreamBlind-0001` |
| Supported image | US Buu's Fury, `8,388,608` bytes, `940AD5F0…F059E` |
| Executable | `Enemy-Randomizer.exe` |
| Release artifact | `Enemy-Randomizer-v0.1.0-win64.zip` |
| Sibling product | Buu's Fury Warp Randomizer v0.1.0, `map-warp` v1 |

The ticket's working name was "Enemy Randomizer" and that is what ships. It is
deliberately not an "Enemy Type Randomizer": nothing in it changes an enemy's
species, and every manifest it writes says so.

## What was built

The layers, outermost last:

```text
tools/webfoot/warp_randomizer.py            the warp algorithm - unchanged, reused
tools/webfoot/enemy_randomizer/             the enemy pack - unchanged, reused
tools/webfoot/randomizer/module.py          what a module is and may not do
tools/webfoot/randomizer/registry.py        which modules exist, in what order
tools/webfoot/randomizer/modules/           map-warp, enemy-placement, enemy-stat
tools/webfoot/randomizer/context.py         one verified image, loaded once
tools/webfoot/randomizer/service.py         one run, one safe write, one record
tools/webfoot/randomizer/gui.py             one window over that boundary
tools/webfoot/warprand/                     the warp product's configuration of it
tools/webfoot/enemyrand/                    the enemy product's configuration of it
Enemy-Randomizer.spec.in                    the tracked PyInstaller config
scripts/build-enemy-randomizer.ps1          generate the .spec and build
scripts/smoke-enemy-randomizer-packaged.ps1 the packaged-executable gate
scripts/package-enemy-randomizer.ps1        the release zip and content gate
```

**No randomizer algorithm was reimplemented, and no core file was modified.**
`warp_randomizer.py` and the whole `enemy_randomizer/` pack are untouched: they
still own every permutation, pairing, scale factor and refusal. What the shared
package adds is the part a *product* has to answer around them.

### The products are compositions

```python
RandomizerApp(allowed_modules=["map-warp"])
RandomizerApp(allowed_modules=["enemy-placement", "enemy-stat"])
```

The eventual combined `Buu's Fury Randomizer` is the same shell with three ids in
that list. That is the property the retrofit was for, and it is checked: the
registry is a static tuple, the order is written down, and the progress display,
the manifest and the enabled set are all derived from whatever the product
composes.

### The module contract

A module declares a stable id, a display name, a description, a default-enabled
flag, an algorithm version, a seed namespace, a progress caption and a tuple of
settings descriptors, and implements two calls: `validate(context, settings)` and
`plan(context, settings, seed=...)`, returning a
`ModulePlan` of `ByteChange` objects plus its own manifest and spoiler sections.
The rules a module may not break are mechanical and tested:

1. **no RNG of its own.** A module is handed its derived seed. Nothing under
   `randomizer/modules/` imports `random` or `secrets`.
2. **no ROM writes.** A module returns semantic changes; only
   `service.py` calls `emit_image`, and an architecture test parses every module
   file to prove neither it nor `open`/`write_text`/`unlink` appears there.
3. **no widgets.** Only `randomizer/gui.py` may import Qt.
4. **no context of its own.** A module reads the run context it is given, so one
   image load serves every module in a run.

### Seed namespaces and algorithm versions

Each module owns a permanent namespace, and the manifest records the namespace,
the derived seed and the module's algorithm version beside every section.

| Module | Namespace | Derivation |
| --- | --- | --- |
| `map-warp` | `master-legacy` | the master seed, verbatim |
| `enemy-placement` | `enemy-placement` | `sha256(pack master domain \| seed \| module id)` |
| `enemy-stat` | `enemy-stat` | `sha256(pack master domain \| seed \| module id)` |

`map-warp` is the one namespace that is not a hash, and the reason is load-bearing
rather than historical accident: the warp core draws from
`sha256(SEED_DOMAIN | seed | group | step)` using the string the user typed, and
`SEED_DOMAIN` is frozen because changing it changes every warp mapping ever
produced. Feeding the core a *derived* seed would silently break every warp seed
that already exists. The module therefore consumes the master seed itself, and a
test pins both halves of that: `map-warp`'s derived seed equals the master seed,
and every other module's differs from it and from its siblings'.

The enemy modules keep the pack's own derivation unchanged, which is what makes
the application route and the `webfoot randomize` CLI route produce the same ROM
for the same seed.

Adding a module cannot perturb an existing one: the derivation takes the master
seed and the module's own id and nothing else, so there is no enabled set or
iteration order in scope for it to depend on.

### One manifest, one spoiler

Both products write the shared, versioned document
(`format_version: 1`, `tool`, `build`, `source`, `master_seed`,
`seed_derivation`, `module_order`, `modules`, `output`, `spoiler`,
`limitations`, `progression`). Every registered module gets a section whether or
not it ran, so "off" is distinguishable from "did nothing"; each section carries
the module's own algorithm version, namespace, derived seed and bounded detail.
Nothing in the document is an absolute path - the output contributes its basename
only - so two runs of the same seed and output name in two directories produce
byte-identical manifests.

The warp product's manifest information did not move *out* of the document, only
under the module that owns it: the policy, the counts, the skip reasons, the class
counts, the forced dead-end links and the core randomizer's full 735-row record
now live at `modules["map-warp"]`.

The spoiler is one document with one section per module that has something to
hide. A module never opens a file: it returns a mapping, and the application
decides whether a spoiler exists at all. A run whose enabled modules have nothing
to hide writes none - and does not fail, because aborting after the ROM is already
written would be worse than either alternative.

### Ordering and collisions

Execution, presentation and manifest order is `MODULE_ORDER`, declared by hand as
`("map-warp", "enemy-placement", "enemy-stat")` and checked at import for
uniqueness, coverage and canonical order. Nothing depends on dictionary
iteration, import order, checkbox order or the filesystem.

Every enabled module's changes go into ONE `WritePlan` built by
`write.plan_changes`, which refuses any two changes that write the same byte.
There is no "last module wins" resolution anywhere: a collision means no plan is
built and the run stops with `ModuleConflictError`. For the three shipping
modules the absence of a collision is not merely asserted but *measured*: the
combined run's changed-byte count is exactly the sum of the three modules' own
runs, so nothing was dropped and nothing was written twice.

### The two modules that plan together

`enemy-placement` and `enemy-stat` are independently toggleable and each produces
a different ROM, but the registry declares them a **group**: the foundation calls
the group once and the group returns one plan per enabled member. That is a
measured property of the pack rather than a preference - the pack loads one image,
builds one slot model and returns one merged change set whose records are encoded
exactly once - and planning them in separate passes would build the model twice
and would put two overlapping plans over one image, which is the shape that lets a
collision hide from the writer's per-plan overlap check. The group is where the
two modules meet; what each does is still entirely the pack's.

## The retrofit of the Map Warp Randomizer

Three things had to survive, and each is pinned by a test:

* **its public surface.** `verify_rom`, `randomize_warps`,
  `RandomizationOutcome` and the six refusal classes are what the shipped window,
  the focused tests and the packaged smoke all call, so `warprand/service.py` is
  now a facade that translates a request in and a result out; it is still the
  only thing the product's window calls.
* **the launch seed's output, byte for byte.** The packaged v0.1.0 executable
  reproduces `Goku` = `ed167ca1…abdc` exactly, and the ROM-gated test recomputes
  it from the canonical image.
* **the phase list.** `PROGRESS_STEPS` is derived from the module that runs rather
  than restated, and for this product the derivation reproduces the v0.1.0 list
  down to the wording, including "Randomizing warp destinations".

The user-visible window is the same window: one module is offered, so the shared
window draws no options area at all, and the same twelve-line success block is
produced by a product override.

### Map Warp old to new: what changed and what did not

| | v0.1.0 | after the retrofit |
| --- | --- | --- |
| Randomized ROM for `Goku` | `ed167ca1…abdc` | `ed167ca1…abdc` |
| Seed handling | master seed verbatim | master seed verbatim |
| Progress phases | 4, warp-worded | 4, warp-worded (derived) |
| Window layout | ROM, seed, output, Randomize, status | unchanged |
| Manifest format | `warprand` schema v1 | shared format v1, warp facts under `modules["map-warp"]` |
| Refusals | warp-private classes | the shared families, same names and messages |
| Algorithm | `warp_randomizer.py` | `warp_randomizer.py`, unmodified |

The manifest format change is deliberate: a combined run has one output and
therefore needs one document describing it, so the two products could not keep two
formats. The *information* is preserved - the Golden `Goku` transition record, its
per-transition rows, the skip reasons and the counts are all still written.

## Evidence

### Focused tests

Measured per file with `pytest <file> -q -p no:randomly`, on the frozen candidate:

| File | Gate | Result |
| --- | --- | --- |
| `tests/unit/test_warp_randomizer.py` | `fast` | 38 passed |
| `tests/unit/test_warp_randomizer_app.py` | `fast` | 43 passed |
| `tests/unit/test_warp_randomizer_gui.py` | `fast` | 50 passed |
| `tests/unit/test_randomizer_foundation.py` | `fast` | 35 passed |
| `tests/unit/test_randomizer_architecture.py` | `fast` | 11 passed |
| `tests/unit/test_enemy_randomizer_gui.py` | `fast` | 19 passed |
| `tests/integration/test_warp_randomizer_rom.py` | `rom` | 19 passed |
| `tests/integration/test_warp_randomizer_app_rom.py` | `rom` | 16 passed |
| `tests/integration/test_enemy_randomizer_app_rom.py` | `rom` | 22 passed |
| `tests/integration/test_randomizer_combined_rom.py` | `rom` | 13 passed |
| **total** | | **266 passed** |

The portable gate - `pytest tests/unit` - was run once at the candidate:
**3744 passed, 15 skipped**. The skips are the site-not-built, capstone-present
and ROM-not-present families that skip in any worktree.

### The golden cross-check

For one fixed image, seed and configuration the production core's own route and
the executable's application route were run and compared:

```text
core route (plan_enemy_randomization + apply_plan) : 4d4cf624681803a2...e7895f
app route  (EnemyRandomizerService.randomize)      : 4d4cf624681803a2...e7895f
```

Identical bytes, and the module seed map is the pack's own, so the executable is a
frontend to the same product rather than a subtly different randomizer.

### StreamBlind-0001

The ticket's regression seed, and the seed the randomized ROM merged to master
was produced with, reproduces the recorded output
`4d4cf624681803a227c26a44bc08b3c6b6cf71539c0a283a03fabd0561e7895f`, with 1177
placements moved and 91 stat records changed. The packaged executable reproduces
it too, which is why the smoke script treats the value as a version bump when it
moves.

### Combined mode, headlessly

`tests/integration/test_randomizer_combined_rom.py` runs `map-warp` +
`enemy-placement` + `enemy-stat` in ONE request against the canonical image and
establishes: accepted output; determinism across two runs (image and manifest);
additivity (`5948 changed bytes = 2746 + 1177-slot shuffle + 91 stat records`
counted as `3202 + 2746`); all three manifest sections present, enabled and
versioned; a disabled module still described; module seeds unmoved; a spurious
collision would have failed closed; and the source image untouched.

### Combined mode at runtime

One internal combined ROM
(`8215dcdb1220a7c5526ec1d4c092d53720f70a67a56f4e01b254ed75d97ed33b`, 5,948
changed bytes) was booted under mGBA 0.11-9128 with an isolated `savegamePath`:
the window reported `DBZBUUSFURY` at 60 fps, the process stayed alive for 40 s
without exiting, and the canonical ROM was still `940AD5F0…F059E` afterwards.

**What that proves**: the engine accepts the composed image as a Buu's Fury
cartridge and runs it without crashing. **What it does not prove**: that a
particular randomized enemy is reachable, that a map is completable, or anything
about beatability. Enemy placement was already proved reachable at runtime by
RANDOMIZER-ENEMY-PACK-001's controlled A/B on one savestate, and warp destinations
by the warp randomizer's own record; this run is evidence about composition and is
deliberately not stretched further. It is not the public combined application.

### Quality gates

| Gate | Result |
| --- | --- |
| `python -m tools.quality.architecture` | 794 tracked files, 0 violations, 4 observations |
| `python -m tools.quality.public_surface --all` | 790 tracked text files, 0 findings |
| `python -m tools.quality.readability --all` | 558 files, 0 hard hits, 73 advisories |

### Packaged smoke

`scripts/smoke-enemy-randomizer-packaged.ps1` drives the real release binary
through its own `--smoke` entry, which goes through the same window, verification,
worker thread and boundary the Randomize button uses. Result: **PASS** - the
launch seed's golden hash reproduced, the manifest and spoiler written, a second
run byte-identical, the canonical ROM unchanged, and a third run with
`--without enemy-stat` producing a *different* ROM, which is the only way a
packaged build can be shown to honour a module toggle rather than always running
both.

`scripts/smoke-warprand-packaged.ps1` was re-run against the rebuilt sibling
executable and also **PASS**es, reproducing `ed167ca1…abdc`.

## Known limits, stated rather than implied

- Randomization is verified against **one** image. Another region, revision or a
  pre-patched dump is refused; there is no "continue anyway".
- **Enemy identity or type swapping is not supported.** Enemy identity is the
  ordered pair (stat selector, sprite id), and within one coupled-field group
  every member already agrees on its flags, descriptor and children, so exchanging
  identity between two members is exactly exchanging their positions. No identity
  can cross a coupled-field boundary without producing an actor whose behaviour
  belongs to a different enemy than its sprite and stats, which nothing
  establishes is coherent. The module is not registered in the foundation at all,
  so no product built on it can offer one.
- **No boss, NPC or quest-critical classification exists** in the project's
  evidence, so none is claimed. The consequence is stated in every enemy run's
  manifest: a boss that is neither script-attached nor alone in its map is
  indistinguishable from an ordinary enemy and may be randomized. The owner
  accepted that limitation in writing for RANDOMIZER-ENEMY-PACK-001.
- The progress bar is phase-based, so it steps rather than sweeps.
- `--smoke` is a **release-verification hook**, not product configuration: it
  cannot change what the randomizer does, and with no arguments the window is
  unchanged.
- Windows x64 only. Nothing was verified on another platform.
- `build.commit` in a manifest is `null` in a packaged build: the executable has
  no repository to ask. That is a provenance gap recorded rather than hidden, and
  it is why the release record names the source commit instead.
- The release archive ships the executable and a brief README only, at the
  owner's direction, so `docs/enemyrand/THIRD-PARTY-NOTICES.txt` does not reach
  the person who downloads it. That gap is inherited from the sibling product and
  is one owner decision covering both.
- The ROM-content probe in `scripts/randomizer-release.ps1` samples the image:
  its 48 needles span 96.5% of the offsets but search 2,304 bytes of 8,388,608.
  Its blind spots are stated in that file's header.

## A future combined application

`Buu's Fury Randomizer`, with toggles for map warps, enemy placements and enemy
stats, is now a configuration rather than a build: a third product module with
`allowed_modules=["map-warp", "enemy-placement", "enemy-stat"]`, a presentation,
a spec template and the same three release scripts. The headless test that proves
the three modules compose already exists, and the composition is already proved
additive and collision-free. What a combined tool would still need is a decision
about its default module set and its disclaimer, not engineering.

This ticket deliberately did not build it.
