# TOOLKIT-030 - Authored behavior attachment

Canonical ROM `940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e`
(`Dragon Ball Z - Buu's Fury (U).gba`, 8,388,608 bytes). Read-only throughout.
Baseline `20bf1c8674451a81345e47868cf2f71c193c54f1`.

TOOLKIT-029 proved the engine instantiates an SDK-authored entity, and claimed
nothing about its behavior. This ticket gives one authored placement its own
**explicitly selected** behavior and proves the selection is made by project
state rather than inherited from the record it was cloned from.

Scope is level **#2** of the ticket's three-level distinction: an authored
attachment. No new descriptor, script or event body is created here.

**Outcome B.**

> **AUTHORED ENTITY BEHAVIOR ATTACHMENT: YES**
>
> **RUNTIME-PROVEN AUTHORED BEHAVIOR: NO - not established**
>
> **NEXT BLOCKER: establish whether the attached descriptor/script path executes at runtime**

The engine loads and consumes a placement body carrying the authored descriptor.
Whether it then *executes* that descriptor's script is **UNKNOWN**: the effect
channel built to answer it turned out to be non-discriminating, and a broken
instrument is not evidence in either direction. Section 6 records both halves.

## 1. What made the TOOLKIT-029 clone behave like its source

Measured, not assumed. The clone copies its template's `+0x14` word verbatim,
and on map 40 that word is the **null** behavior descriptor:

| Record | `+0x14` | Descriptor | Handler | Meaning |
|---|---|---|---|---|
| `map:0040/placement:0000` | `0x080555A0` | `{0x0800421D, 0x03004A68}` | `0x0800421D` | `bx lr` |
| `map:0040/placement:0001` (clone source) | `0x080555A0` | `{0x0800421D, 0x03004A68}` | `0x0800421D` | `bx lr` |
| `map:0040/authored:tk029` | `0x080555A0` | inherited | `0x0800421D` | `bx lr` |

So the honest answer to the ticket's question is that the TOOLKIT-029 clone
inherited **no behavior at all**. Handler `0x0800421D` is a bare return
(TOOLKIT-016). Both of map 40's canonical placements share it, so no sibling
could have supplied one either.

The field responsible for the relationship is exactly one word - the placement
record's `descriptor_pointer_raw` at `+0x14` - and before this ticket the
authored declaration did not control it. `AuthoredPlacement.serialize` copied
the template and overrode only the two position halfwords.

This makes map 40 a **stronger** independence case than the ticket's preferred
substitution form, not a weaker one: a behavior that appears on the authored
record cannot have arrived by cloning, because the template has none to give.

## EXTERNAL BEHAVIOR TARGET

Map collision. In Buu's Fury, as in every Legacy-of-Goku-engine game, some parts
of a room are walkable and some are not; walking into a blocked tile stops the
player. This needs no reverse engineering to establish - it is the most basic
observable in the game and the owner has extensive firsthand play experience of
it. External evidence is used only to pick the effect, exactly as the
external-research-first rule requires.

## WHY THIS EFFECT IS SUITABLE

* **Binary.** The player is either stopped or not. There is no interpretation
  step between the observation and the YES/NO the ticket asks for.
* **Already understood.** The behavior is an existing canonical event; nothing
  about it is authored here.
* **Cheap to control.** The same tiles are sampled on the canonical build and on
  the authored build, so the comparison is like-for-like.
* **No confounders.** It avoids dialogue state, input handling, scene flow, save
  flags and combat, all of which the ticket asks to keep out of a first
  behavior-attachment proof.

> **CORRECTION, after the runtime session.** The reasoning above is sound about
> the *effect* and wrong about the *instrument*. Sampling the collision grid
> turned out not to be discriminating on this target: the chosen tiles read set
> on both builds, so a like-for-like comparison still yields no signal. The
> effect may well be binary in-game; what failed is the attempt to read it out
> of memory. See section 6.

## 2. The authored behavior declaration

`behavior` names an **existing** descriptor by the identity the SDK already
publishes for it. No new namespace was invented, and no raw ROM address is
accepted from project source.

```toml
[map."map:0040".authored_placements."map:0040/authored:tk030"]
provenance = "AUTHORED_CLONE"
clone_from = "map:0040/placement:0001"
behavior = "map:0428/placement:0000/descriptor"
position_low = 176
position_high = 176
```

```powershell
webfoot placement clone PROJECT --map map:0040 `
  --source map:0040/placement:0001 --name tk030 `
  --position-low 176 --position-high 176 `
  --behavior map:0428/placement:0000/descriptor
```

The field is **optional**. Omitting it reproduces the pre-TOOLKIT-030 path
exactly, and the build proves this by byte-identical output (below). Project
format version remains **1**: `behavior` is the only field the additive surface
gained, and every other unknown key is still refused as structural fabrication.

Resolution happens at build time against `PlacementEvents`, the same read-only
catalog that publishes descriptor identities, so a behavior can only ever name a
descriptor this profile has actually verified. Four shapes are refused before a
project is even written - a raw address `0x0808D788`, a bare word `0808D788`,
the `/event` identity rather than the `/descriptor` one, and an invented
`behavior:` namespace - and a well-formed but unknown identity fails the build
with no ROM published.

The SDK can therefore distinguish, as the ticket requires:

```text
clone template structure   (factory, flags, type, id, children - from canonical bytes)
+ authored behavior choice (the +0x14 descriptor word - from project state)
```

## 3. The selected behavior

`map:0428/placement:0000/descriptor` is descriptor `0x0808D788`:

```text
0x0808D788  {0x0800421F, 0x0808D77C}
             |            |
             |            +-- script root
             +-- script dispatch trampoline (TOOLKIT-016)
```

Script `0x0808D77C`, 9 bytes, `1d0468830081288310`, decoded with the existing
`stack_be16_buu_v1` opcode set - no new VM, no assembler:

```text
1D  push_many(4, 52, 192, 84, 200)
02  native_stack(43)
11  terminate
```

### Native slot 43, disassembled for this ticket

Secondary dispatch table `0x08055098`, slot 43 holds `0x0800099D`, entry
`0x0800099C`. It pops exactly four values into a 16-byte stack struct and calls
`0x08009930` twice:

```text
0x0800099C  push {r4, lr}
0x0800099E  ldr  r1,[r0]          ; stack depth
0x080009A2  subs r1,#1            ; pop -> [sp+0x0C]
...                                 (four times, x0/y0/x1/y1)
0x080009D8  ldr  r0,[pc,#0x198]   ; -> 0x08054FBC
0x080009DA  ldr  r4,[r0,#0x24]
0x080009DE  adds r4,#0x80
0x080009E0  ldr  r1,[r4,#0x28]    ; first grid
0x080009E2  movs r2,#1            ; SET
0x080009E4  bl   0x08009930
0x080009EC  ldr  r1,[r4,#0x30]    ; second grid
0x080009EE  bl   0x08009930
```

`0x08009930` divides each edge by 8 (`asrs #3`, pixel -> tile), then walks the
tile rectangle setting bits, indexing rows at 32 bytes and columns by
`(x >> 5) * 4` with bit `x & 31`.

The direction is identified by its own sibling, not by naming: `0x080009F6` is
byte-for-byte the same routine with `movs r2,#0`, i.e. bit **clear**. Slot 43 is
therefore the **set** form.

`0x08009930` is a shared routine. Per the standing shared-handler rule no
gameplay name is claimed for it beyond what its own arithmetic shows: it sets
bits over a tile rectangle in two grids reached from `0x08054FBC`.

### The operands are literal, not entity-relative

The script pushes `52, 192, 84, 200` as constants and the handler never reads
the placement's position, so the rectangle lands at tiles **(6,24)..(10,25)**
regardless of where the authored entity sits - the authored entity is at
(176,176), tile (22,22). This is recorded plainly because a later reader could
otherwise mistake the offset for a defect. It does not weaken the proof: the
question is whether the engine executes the attachment, not whether the
attachment is positioned at its owner.

## 4. Independence proof

The ticket's **acceptable alternative** form, which for this target is the
stronger one: the template carries no behavior, and the authored clone
explicitly adds one.

| Record | descriptor | source of that value |
|---|---|---|
| clone template `map:0040/placement:0001` | `0x080555A0` | canonical ROM |
| authored, `behavior` omitted | `0x080555A0` | inherited |
| authored, `behavior` declared | **`0x0808D788`** | **project state** |

Ancestry is unchanged - `factory_raw`, `flags_raw`, `type_raw`, `id_raw` and the
child pointer array are all identical to the template - so the body is still
structurally a clone of A while its behavior is B.

**Exactly three bytes** separate the two builds, and all three are the descriptor
word of the authored body:

```text
0x7EA414..0x7EA416   a05505 -> 88d708
```

## 5. Static build proof

| Check | Result |
|---|---|
| authored declaration accepted | YES |
| attachment serialized through the production codec | YES - `PlacementRecord.to_bytes` |
| expected descriptor relationship exists | `+0x14` = `0x0808D788`, `{0x0800421F, 0x0808D77C}` |
| authored entity body still materializes | YES - 32 bytes at `0x087EA400` |
| map object array remains valid | YES - 5 slots at `0x087EA420`, `MapEntry+0x04` = 5 |
| verified capacity sufficient | YES - 52 of 256 bytes; 204 free |
| canonical source immutable | YES - SHA-256 and mtime unchanged |
| output deterministic | YES - byte-identical across rebuilds |

Changed structures, all intended, 56 bytes of 8,388,608:

| Offset | Size | Before | After |
|---|---|---|---|
| `0x08EBA4` | 1 | `04` | `05` (MapEntry+0x04 count) |
| `0x08EBB4` | 3 | `905607` | `20a47e` (MapEntry+0x14 owner pointer) |
| `0x7EA400` | 52 | `FF`... | body (32) + expanded array (20) |

| Artifact | SHA-256 |
|---|---|
| canonical | `940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e` |
| authored, behavior attached | `f6595c4e89189f6420130f2bb5f09e447621ee095f16bff4074f12678ea0a9fb` |
| authored, behavior omitted (control) | `a425ae73af5c5b4029882e8fb62ca398ee0e3b8a9a4fbb63dee8dc9834d7bed4` |

The control hash is **byte-identical to TOOLKIT-029's published ROM**. Removing
the declaration does not merely produce a similar image; it reproduces the prior
proof exactly. That is the removal/reversion control the ticket asks for.

**This is a static result and is not runtime success.** It establishes that the
attachment exists in the built image, nothing more. Section 6 adds that the
engine goes on to *consume* that image's authored descriptor at runtime, and
that whether it *executes* the script remains unproven.

## 9. Capacity

TOOLKIT-028's confirmed region `[0x007EA400, 0x007EA500)` is 256 bytes.
Measured demand for this ticket is **52 bytes** - unchanged from TOOLKIT-029,
because attaching a behavior rewrites a word inside the existing body rather
than allocating anything. Headroom is 204 bytes and every untouched byte in the
region still reads `0xFF`. No free-space hunt was opened, per the ticket's
instruction.

## 6. Runtime result - Outcome B

Two mGBA 0.10.5 sessions on the same savestate, one per build, driven by the
read-only observer `tools/runtime/toolkit030_behavior_watch.lua`.

### OBSERVED - the engine consumes the AUTHORED descriptor

Read live through `0x03001980`, the runtime MapEntry pointer established by
ROM-007:

| | authored build | inherited control |
|---|---|---|
| `MapEntry+0x04` count | 5 | 5 |
| `MapEntry+0x14` array | `0x087EA420` | `0x087EA420` |
| last slot (`count-1`) | `0x087EA400` | `0x087EA400` |
| body `+0x14` descriptor | **`0x0808D788`** | **`0x080555A0`** |
| classification | `AUTHORED-BEHAVIOR` | `INHERITED-NULL` |

The authored descriptor was **stable across 67 samples**. The engine therefore
instantiated the authored entity and consumed a placement body carrying the
**explicitly authored** descriptor rather than the one inherited from the clone
source. That is what closes the attachment question:

> **AUTHORED ENTITY BEHAVIOR ATTACHMENT: YES**

### The collision channel is INVALID / NON-DISCRIMINATING

| Run | descriptor | rect set | off-rect control tile |
|---|---|---|---|
| authored | `0x0808D788` | 10/10 | 1 |
| inherited control | `0x080555A0` | 10/10 | 1 |

Both builds read identically, and the off-rect control tile also reads set, so
the sampled region is saturated. These readings **cannot distinguish authored
collision behavior from baseline state**.

The `10/10` result is therefore **not** evidence that the script executed, and
it is equally **not** evidence that it failed to. The correct conclusion is that
**execution remains UNKNOWN** - the same discipline TOOLKIT-029 applied when its
EWRAM scan failed its own positive control.

> **RUNTIME-PROVEN AUTHORED BEHAVIOR: NO - not established**

### OBSERVED vs INFERRED

**OBSERVED.** Count 5, array `0x087EA420`, last slot `0x087EA400`, and body
`+0x14` = `0x0808D788` on the authored build against `0x080555A0` on the
control, stable across 67 samples, in ordinary gameplay on the modified image.

**INFERRED - and explicitly NOT claimed.** That the engine *executed* the script
the attached descriptor names. Nothing measured here reaches the interpreter.
A descriptor being live in a consumed record is a necessary condition for
execution, not a sufficient one.

### Instrumentation defect, corrected mid-session

The first run recorded `grid_a = grid_b = 0xE3A00001`, an ARM instruction word
(`mov r0,#1`), not a pointer. Cause, read from the encoding rather than guessed:
`ldr r0,[pc,#N]` loads the **literal value** into r0, so `r0` **is**
`0x08054FBC` - the base of a table of object pointers - and the next access is
`[r0+0x24]`. The observer dereferenced `0x08054FBC` itself, one step too many.

Corrected, the chain resolves against live memory:

```text
[0x08054FBC+0x24] = 0x030019A4        ; object
  + 0x80          = 0x03001A24        ; base
  [base+0x28]     = 0x0203A3BC        ; first grid
  [base+0x30]     = 0x020363AC        ; second grid
```

The invalid capture is preserved as
`toolkit030-behavior-run1-broken-grid.transcribed.csv` and is **not** deleted or
reinterpreted. It carries a provenance warning: the original file was
overwritten when the corrected observer reopened the same path in mode `"w"` (an
attempted rename did not take effect while the first Lua chunk still held the
handle), so the preserved file is a **transcription** of rows quoted during the
run rather than the raw artifact. It is labelled as such rather than presented
as recovered.

Channel 1 was unaffected by the defect and agrees across both runs.

## HARNESS LIMITATION: canonical-only SHA guard cannot currently launch generated authored ROMs

`tools/runtime/run_mgba_capture.ps1:118` hard-pins the canonical SHA-256 and
refuses any other image before launch, with no override parameter. It therefore
**cannot** launch an authored build by design, which is why this ticket started
mGBA directly.

That direct launch is accepted as valid evidence here because the generated ROM
and canonical ROM hashes were both checked explicitly before the run, the
canonical ROM was never opened for writing, and the modified image was a
separate generated artifact under the ignored `build/` tree.

The guard was **not** weakened or removed, and ad-hoc bypassing is **not** the
normal workflow. If repeatable modified-ROM captures are needed, a later ticket
may decide whether an explicit, safe generated-ROM mode is warranted.

## Exact next blocker

> Does runtime execution reach the attached descriptor/script path at all, and
> under what trigger?

The candidate investigation is a bounded call-site and runtime census around
`0x0800421E` / `0x0800421F`. It is **not** performed here.

Do not assume the path runs at map load. Do not assume it requires interaction.
Both readings are open, and the next ticket measures which holds.

## Method note

No new reverse engineering was opened for the behavior question itself; the
placement -> descriptor -> script chain came from TOOLKIT-016 and the VM from
TOOLKIT-013/015. RE was spent only where external and project sources cannot
reach: the disassembly of native slot 43 and `0x08009930`, which is what
identifies the effect as a tile-rectangle set rather than something merely
plausible. The descriptor census was re-measured from the ROM rather than taken
from the earlier documents, which is how the null-handler inheritance in section
1 was found rather than assumed.
