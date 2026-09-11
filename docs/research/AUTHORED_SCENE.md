# Complete authored scene - TOOLKIT-035

One small authored scene, composed from capabilities proven separately by
TOOLKIT-029 through TOOLKIT-034, built through the ordinary Webfoot SDK
lifecycle and runtime-proven in the original Buu's Fury engine.

The question this ticket exists to answer is not whether the primitives work.
Each was proven alone. The question is whether a mod author can COMPOSE them
through normal project mechanisms into one coherent playable moment.

## Result

The scene composes with **no production code change at all**. Every dimension
was already expressible through existing public SDK entry points, so this
ticket adds evidence and a contract test rather than an authoring primitive.

## The scene

```text
player is on map 40
  -> a newly authored enemy is present, placed by the project
  -> the player fights it through ordinary gameplay
  -> while it is alive, nothing authored happens
  -> the player defeats it
  -> on_defeat runs the authored script
  -> the authored message SCENE CLEAR! appears on screen
```

## Author-facing representation

The whole scene is one authored record plus one text line. No ROM addresses
appear in project source.

```toml
[map."map:0040".authored_placements."map:0040/authored:scene"]
provenance = "AUTHORED_CLONE"
clone_from = "map:0040/placement:0001"
position_low = 176
position_high = 176
behavior = "map:0040/authored:scene/behavior"
script = [
    "show_centered_sprite_text text:1525 120 105",
    "terminate",
]
trigger = "on_defeat"
```

```toml
[text."text:1525"]
text = "SCENE CLEAR!"
```

Authored through public API calls only:

```python
extract_project(rom, root, catalog, graphics=False)
clone_placement(root, map_index=40, source="map:0040/placement:0001",
                name="scene", position_low=176, position_high=176,
                behavior="map:0040/authored:scene/behavior",
                script=["show_centered_sprite_text text:1525 120 105", "terminate"],
                trigger="on_defeat")
# text/strings.toml edited as ordinary authored source
validate_project(root, rom, catalog)
build_project(root, rom, output, catalog)
```

## Authorship classification

Stated precisely, because the value of this record depends on not blurring
these categories.

| Component | Classification | Note |
|---|---|---|
| Placement / entity | **NEW / AUTHORED** | new record in the expanded map object array |
| Position, type | **NEW / AUTHORED** | (176, 176); type inherited from the clone template |
| Behavior descriptor | **NEW / AUTHORED** | allocated at `0x087EA420` |
| Script bytecode | **NEW / AUTHORED** | 11 bytes at `0x087EA428` |
| Scene message text | **MODIFIED EXISTING** | text 1525, in place, inside its existing 30-byte allocation |
| Trigger `on_defeat` | **REUSED RETAIL** | names an existing engine contract; emits zero ROM bytes |
| Native effect slot 178 | **REUSED RETAIL** | handler `0x08003030` |
| Map 40 (stage) | **REUSED RETAIL** | unmodified retail map used as the stage |

**The scene does NOT use newly allocated text.** Text 1525's storage already
existed and is edited in place; its pointer-table entry is byte-identical
between the canonical and generated images. New text resource creation remains
unproven and unimplemented. Claiming otherwise would misrepresent the result.

## Text boundary, measured

The preference for author-controlled wording is satisfied, and its exact limit
was measured rather than assumed.

Text 1525 has a **30-byte allocation**, which is 14 UTF-16LE characters plus a
terminator. A first attempt at `SCENE 035 CLEAR!` was **refused by validation**:

```text
text:1525: encoded text needs 34 bytes but its allocation is 30; 4 bytes too
long. Growing a string requires relocation, and this profile declares no
verified free space.
```

That is the guard working: the build fails closed rather than truncating a
scene's own message. `SCENE CLEAR!` fits and was used. A scene message longer
than its host string's allocation is the boundary, and it is where new text
allocation would be required.

## Build evidence

| Item | Result |
|---|---|
| Canonical input | `940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e`, verified unchanged before and after |
| Generated ROM SHA-256 | `ffde3e85aac247c1d549c23a9a07049f9741c98d0c5599ed9e9c4539631a2793` |
| Changed bytes | 88 |
| Determinism | two independent builds byte-identical |
| Region usage | 71 bytes in `[0x007EA400, 0x007EA500)` |
| Highest occupied | `0x007EA448` |
| Remaining verified capacity | **184 bytes** |
| Production code changed | **none** |

The 88 changed bytes decompose exactly: 75 structural bytes identical to
TOOLKIT-034, plus 13 text bytes at `0x006BBD6`-`0x006BBF0` inside text 1525's
existing allocation. **The scene's text dimension costs zero region bytes**,
because it modifies storage that already exists. Region demand is therefore
unchanged from TOOLKIT-034 despite the scene adding a dimension.

Structures in the generated image, each located by following the pointer chain
the engine itself follows rather than by a remembered address:

| Structure | Address | Size |
|---|---|---|
| Authored placement record | `0x007EA400` | 32 |
| Authored descriptor | `0x007EA420` | 8 |
| Authored script body | `0x007EA428` | 11 |
| Relocated placement array | `0x007EA434` | 20 |

## Runtime evidence

Capture `tk034-trial-d-tk035-scene-20260911`, one run, 6360 frames, maps 39 and
40, observer `tools/runtime/toolkit034_dispatch_caller_watch.lua` unchanged from
TOOLKIT-034. The observer keys on text INDEX 1525, not on string content, so it
required no modification for the authored message.

### Negative control: alive and undefeated does not run the scene

Frames 960 to 3120, before any authored execution:

- **37 `ACTOR-HEARTBEAT` / `AUTHORED-ACTOR-ALIVE` samples**, each re-validating
  the actor's `+0x228` attachment against authored descriptor `0x087EA420`.
- HP read full, `0x0002BC00`, for **35** of those samples, then fell across the
  final two: `0x00022E8A` at frame 3060 and `0x000108A2` at frame 3120. So the
  window covers both an untouched and a damaged living authored entity, with
  most of it quiet rather than under sustained combat.
- **Zero** `TRAMPOLINE`, `SCRIPT`, `NATIVE-OPCODE`, `NATIVE-HANDLER`,
  `DESTRUCTOR-DISPATCH` and `SCREENSHOT` rows.
- **3 `INTERPRETER` liveness rows** inside the same window, at frames 3059,
  3087 and 3115. Counting instead every liveness row before the first authored
  execution at frame 3179 gives 7, but four of those (859 twice, 3143 and 3171)
  fall outside the stated window, and 3171 is the death frame itself, so the
  in-window figure is the one this negative rests on.

Target silent plus liveness firing: this is a **real negative**, not an
unproven instrument. A living authored enemy, including while damaged, does not
run the scene. The liveness margin is thin - three rows - and is reported as
measured rather than rounded up.

### Positive: defeat runs the scene

The operator defeated the authored enemy **twice during the one capture**, and
each defeat produced one complete chain. The repetition is operator action, not
an engine mechanism, and is reported as such; its value is that the same chain
reproduced from two separate kills on one instrument and one load.

```text
frame 3171  DEATH-CALLBACK / AUTHORED-ACTOR-DEATH   actor HP 0, descriptor 0x087EA420
frame 3171  ACTOR-EVENT-CREATE / AUTHORED-ACTOR
frames 3171-3179  DESTRUCTOR-FIRST-DECISION x8, DESTRUCTOR-DECREMENT x8
frame 3179  DESTRUCTOR-DISPATCH                     descriptor 0x087EA420
frame 3179  TRAMPOLINE / AUTHORED-DESCRIPTOR-PAYLOAD
frame 3179  SCRIPT / AUTHORED-SCRIPT                cursor 0x087EA428
frame 3179  NATIVE-OPCODE / AUTHORED-NATIVE-SLOT-178  slot 0xB2, cursor 0x087EA431
frame 3179  NATIVE-HANDLER                          depth 3, args 1525 / 120 / 105
frames 3180, 3184, 3194  SCREENSHOT / AUTHORED-EFFECT-CAPTURED
```

The second defeat reproduces it exactly at frames 4965 to 4973: same descriptor
`0x087EA420`, same cursor `0x087EA428`, same slot `0xB2`, same arguments
`0x5F5` / `0x78` / `0x69` = 1525 / 120 / 105, same depth 3.

### Visible result

`effect-plus1.png`, `effect-plus5.png` and `effect-plus15.png` were captured by
the observer from the emulator's own frame buffer and show the authored banner
reading:

```text
SCENE CLEAR!
```

Retail text 1525 reads `Match 2 Fight!`. The rendered string is the project's,
not the ROM's original, which is what makes the visible result author-controlled
rather than merely author-triggered.

The operator independently confirmed the banner live during play. That is a
FIRSTHAND USER OBSERVATION, recorded distinctly from the captured frames.

### The instrumentation did not cause the result

The observer uses `emu:read*` and breakpoints only; it writes no memory and
drives no input, enforced by `tests/unit/test_mgba_capture.py`. The scene runs
from the generated ROM through the engine itself.

## What this ticket did NOT establish

Recorded so nothing here is later overstated:

- **New text allocation is NOT proven.** The scene modifies existing text
  storage. A scene message longer than its host string's allocation cannot
  currently be authored.
- **Defeat and teardown remain CONFOUNDED**, exactly as TOOLKIT-034 recorded.
  The authored script is still reached only through `DESTRUCTOR-DISPATCH`.
  `on_defeat` names the observed gameplay condition, not an isolated mechanism.
- **No scene abstraction exists or is implied.** A scene here is the composition
  of existing authored resources in one project record. No `Scene` type, graph,
  compiler, scheduler or manifest was added, and none is warranted by one case.
- The trigger declaration still emits **zero ROM bytes**; it validates an
  existing engine relationship and adds authoring attribution.

## Next measured blocker

**New text resource allocation.** The scene's message is author-controlled but
size-bounded by the retail string it reuses. Authoring a message that does not
fit an existing allocation requires text relocation into verified free space
with pointer-table rewriting, which is not implemented and whose ownership and
capacity are unmeasured.
