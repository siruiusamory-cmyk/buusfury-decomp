# TOOLKIT-031 - Runtime execution of the attached behavior

Canonical ROM `940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e`
(`Dragon Ball Z - Buu's Fury (U).gba`, 8,388,608 bytes). Read-only throughout.
Baseline `862a0c9d06f97136c882665b60bc4d1b125720ba`, present on the canonical remote.

TOOLKIT-030 proved **AUTHORED ENTITY BEHAVIOR ATTACHMENT: YES** and left one
question: does the attached `0x0808D788` descriptor's script path execute, and
under what trigger? This ticket answers the static half first, because the
runtime experiment cannot be designed without it.

## 1. Bounded static call-site census

### Method

All figures below are measured from the canonical image by halfword-exact
scanning, never by linear disassembly from a fixed origin. That distinction
matters: the ROM header is not Thumb code, so a linear sweep from offset 0
desynchronises and silently reports zero hits. Two early scans in this session
did exactly that and were discarded; every census below tests **every 2-byte
alignment independently** and is reproducible from
`tests/integration/test_authored_behavior_execution_rom.py`.

Thumb `BL` is decoded as an explicit halfword pair (`F000-F7FF`, `F800-FFFF`)
rather than trusted from a disassembler's linear output, for the same reason.

### The handler is never called directly

| Handler | Direct `BL` callers |
|---|---|
| `0x0800421C` (null, `bx lr`) | **0** |
| `0x0800421E` (script trampoline) | **0** |
| `0x0800424E` (other consumer) | **0** |

So the trampoline is reached **only** indirectly, through a descriptor's `+0x00`
word. This is the first thing that had to be established: a census of "who calls
`0x0800421E`" has no direct answer, and the question must be restated as *who
loads a descriptor and calls its first word*.

### Indirect calls go through interworking veneers

This build has no `blx <reg>` (ARMv4T does not provide it). Every indirect call
is `bl` to one of eight `bx <reg>` veneers:

```text
08046AA0  bx r0        08046AA8  bx r4
08046AA2  bx r1        08046AAA  bx r5
08046AA4  bx r2        08046AAC  bx r6
08046AA6  bx r3        08046AAE  bx r7
```

**1,265** call sites reach these veneers. Of those, **1,215** load the called
register from a struct field.

### Descriptor dispatch vs. vtable dispatch

The engine has two distinct indirect-call shapes, and separating them is what
makes the census bounded:

```text
vtable      ldr rH,[rObj]  ;  ldr rT,[rH,#SLOT]  ;  adds rH,rT,rH  ;  bl via rH
descriptor  ldr rH,[rDesc] ;                        bl via rH
```

Vtable entries are **relative** (slot value plus vtable base), which is why the
`adds` fixup is present and why a raw pointer search for a method address finds
nothing. Filtering out every site with that fixup leaves **71** non-vtable
indirect dispatches, and those are the only sites that can call a descriptor's
handler in the TOOLKIT-016 sense.

### The placement descriptor is stashed, not called

Following the placement record into the engine:

```text
placement +0x00 factory 0x0800FD55
  -> 0x0800FD54  factory wrapper
  -> 0x0800F68C  constructor (r5 = placement record, r4 = actor object)
```

At `0x0800F6E0..0x0800F6F4`, measured instruction by instruction:

```text
0800F6E2  movs r3,#1
0800F6E4  lsls r3,r3,#9        ; r3 = 0x200
0800F6EA  adds r7,r4,r3        ; r7 = actor + 0x200
0800F6F0  ldr  r3,[r5,#0x14]   ; the placement's behavior descriptor
0800F6F4  str  r3,[r7,#0x28]   ; -> actor + 0x228
```

> **The constructor does not call the descriptor. It stores it.**

This is the single most important finding of the census, and it reframes the
question the ticket asks. Attachment being live in a consumed record (TOOLKIT-030's
result) is upstream of execution by two steps, not one.

### Complete census of `actor + 0x228`

Scanning for every site that forms `base + 0x200` via `movs`/`lsls` and then
accesses `[.,#0x28]` - the exact idiom the constructor uses:

| Site | Access | Role |
|---|---|---|
| `0x0800F6F4` | `str r3,[r7,#0x28]` | **the only writer** - the constructor above |
| `0x0800F8B2` | `ldr r5,[r0,#0x28]` | reader |
| `0x08018842` | `ldr r2,[r1,#0x28]` | reader |
| `0x0803C850` | `ldr r2,[r1,#0x28]` | reader |
| `0x0804F866` | `ldr r0,[r0,#0x28]` | reader - a **pure getter** (`ldr; bx lr`) |

One writer, four readers. The getter at `0x0804F860` is the one that hands the
descriptor out, and it is reached only as **vtable slot `+0x78`** of the actor
vtable `0x0804C484` installed by the constructor at `0x0800F6C8`.

### Where slot `+0x78` is dispatched

| Dispatch site | Enclosing function |
|---|---|
| `0x08032CE4` | `0x08032B98` |

`0x08032B98` has **zero** direct `BL` callers and **zero** absolute pointer
references; it is itself reached only through a relative vtable slot. Testing
every 4-aligned word in the image for a slot that resolves to it yields three
candidates, of which two are real (all 40 probed slots resolve to odd/Thumb ROM
addresses; the third resolves 0/40 and is coincidence):

| Vtable | Slot | Valid |
|---|---|---|
| `0x080243BC` | `+0x198` | no - 0/40 slots resolve |
| `0x0804AF18` | `+0x234` | **yes** - 40/40 |
| `0x0804BBE8` | `+0x194` | **yes** - 40/40 |

### What the census establishes

**OBSERVED.** The descriptor named by a placement's `+0x14` is copied into the
constructed actor at `+0x228` and is read back only through one getter, exposed
as vtable slot `+0x78`, dispatched from one site inside a function that is itself
virtual. Handler `0x0800421E` has no direct callers anywhere in the image.

**NOT CLAIMED.** That any of this executes on map 40, or on the authored entity,
or at all in the sampled savestate. The census bounds *where* execution could
happen; it is not evidence that it *does*. That is a runtime question and is
answered - or not - by measurement, not by reading the chain and finding it
plausible.

## OLD CLAIM / NEW EVIDENCE / RESOLUTION - "the attached descriptor is invoked"

**OLD CLAIM.** TOOLKIT-030's next-blocker note framed the open question as a
census "around `0x0800421E` / `0x0800421F`", implicitly treating the handler as
something the engine calls on a placement's behalf during map construction,
interaction, or per-frame update - the three trigger classes it named.

**NEW EVIDENCE.** `0x0800421E` has zero direct callers. The construction path
that consumes the placement record does not call the descriptor at all; it
copies the pointer to `actor + 0x228` and returns. The only consumer of that
field is a getter behind vtable slot `+0x78`.

**RESOLUTION.** The trigger is **not** map construction. Construction stores the
descriptor and stops. Any execution must come from whatever dispatches slot
`+0x78`, which is a narrower and different question than the one TOOLKIT-030
anticipated. The three trigger classes it listed are not equally open: the
construction hypothesis is **refuted** by this census.

## 2. Positive control

The ticket requires a canonical placement that is known to use the same handler
family and can actually be exercised, observed **before** any authored miss is
interpreted. Building it took two corrections worth recording, because both are
the kind of mistake that would otherwise look like a result.

### The control map cannot be reached

Census of every placement reached through `MapEntry[+0x14]` whose `+0x14`
descriptor names handler `0x0800421F`:

| Maps with a script-bearing placement | 13 |
|---|---|
| Script-bearing placements | 53 |
| Densest | map 21 (15), map 22 (15), map 19 (10) |
| Owner of **our** descriptor `0x0808D788` | **map 428, slot 0**, record `0x0808D790` |

The available savestate starts on **map 40**, and map 40's zone byte is 1. Every
map in zone 1 (maps 33..46) carries only the null descriptor, so the trampoline
can never fire there no matter how long it is watched. Maps 19/21/22 are zone 0;
map 428 is zone 21. The operator confirmed independently that none of them is
reachable from the start position in a session.

Retargeting a door was considered and rejected on measured grounds, not
preference: map connection **destinations are UNKNOWN** in this SDK
(`docs/research/MAP_FORMAT.md` - 89 edges decoded across 35 maps, destinations
unresolved), so a warp would require transition reverse engineering that this
ticket's scope exclusions forbid.

### OLD CLAIM / NEW EVIDENCE / RESOLUTION - the first "control" was not one

**OLD CLAIM.** Cloning map 40's own slot 1 and setting its `behavior` to
`map:0428/placement:0000/descriptor` gives a positive control carrying the
canonical descriptor.

**NEW EVIDENCE.** That build hashes
`f6595c4e89189f6420130f2bb5f09e447621ee095f16bff4074f12678ea0a9fb` - **byte for
byte identical to TOOLKIT-030's authored ROM**, verified by `cmp`.

**RESOLUTION.** It is not a control at all; it is the experimental build under a
different name, and it would have "confirmed" whatever the authored build did.
The control must differ from the authored build in the thing under test.

### The control actually used

Clone the canonical script-bearing **record itself** into map 40, rather than
copying its descriptor onto a map-40 template:

```powershell
webfoot placement clone PROJECT --map map:0040 `
  --source map:0428/placement:0000 --name tk031control `
  --position-low 176 --position-high 176
```

This uses only authoring the SDK had already proven. The two builds then differ
exactly where it matters - the control carries the canonical record's own type
and id, the authored build carries map 40's:

| | control | authored (TOOLKIT-030) |
|---|---|---|
| ROM SHA-256 | `59f28fea4c4a9240a5c0c5415ae0c774226fa6d59c88bbd0c45d0852476764f3` | `f6595c4e89189f6420130f2bb5f09e447621ee095f16bff4074f12678ea0a9fb` |
| body `type` | **`0x06`** (canonical) | `0x56` (map 40's) |
| body `id` | **`0x20`** (canonical) | `0xD3` (map 40's) |
| body `+0x14` | `0x0808D788` | `0x0808D788` |
| descriptor | `{0x0800421F, 0x0808D77C}` | `{0x0800421F, 0x0808D77C}` |
| changed bytes vs canonical | 56 | 56 |

Canonical ROM SHA-256 and mtime unchanged by both builds.

## 3. Runtime instrumentation

`tools/runtime/toolkit031_execution_watch.lua`, read-only, on mGBA
`0.11-9128-c65e8a3d4` (the 0.10.5 stable build has no scripted-breakpoint API).

Three channels, deliberately separated so none can be read as another:

| Channel | What it watches | What it proves |
|---|---|---|
| **A/B EXEC** | breakpoint at trampoline `0x0800421E`, recording `r0` and `[r0+4]` | a script ran, **and which descriptor ran it** |
| **D INTERP** | breakpoint at interpreter `0x08004038` | the instrument can see execution at all |
| **C STRUCT** | live `MapEntry` -> last slot -> `+0x14` | the entity is present; **not** execution |

Channel D is the lesson of TOOLKIT-029's EWRAM scan and TOOLKIT-030's collision
sampler, both of which were invalidated for reporting a silent instrument as a
result. Zero hits on channel A mean nothing unless channel D fired.

### Control run - the instrument is proven live

Run `build/toolkit031/control-play`, 8,460 frames of ordinary play by the
operator, ROM hash verified unchanged after the run.

| Channel | Count |
|---|---:|
| **EXEC** (trampoline `0x0800421E`) | **0** |
| **INTERP** (interpreter `0x08004038`) | **20** |
| STRUCT | 141 |

The 20 interpreter entries are at PC `0x0800403A` across maps 39 and 40, in
ordinary play on the control build. So:

> **The instrument sees script execution. The placement-descriptor path was not
> taken.**

That is the discriminating case the liveness channel exists to produce: this is
a **real negative**, not a blind one. Had both channels been silent, nothing
could have been concluded in either direction.

## 4. Authored run - execution observed

Run `build/toolkit031/authored-play`, TOOLKIT-030's authored ROM
`f6595c4e89189f6420130f2bb5f09e447621ee095f16bff4074f12678ea0a9fb`, same
savestate, same observer, ordinary play by the operator.

At frame **2577** on map **40**:

```text
EXEC,2577,40,0x08004220,0x0808D788,0x0808D77C,AUTHORED-BEHAVIOR,
     AUTHORED attachment reached the trampoline
```

Read field by field, because each one carries part of the claim:

| Field | Value | What it establishes |
|---|---|---|
| PC | `0x08004220` | inside the trampoline, at `ldr r1,[r0,#4]` |
| `r0` | **`0x0808D788`** | the **authored** descriptor, written from project state |
| `[r0+4]` | **`0x0808D77C`** | the attached script root |
| map | 40 | the authored entity's map |

The surrounding rows show the interpreter entered on the same frame - interpreter
liveness hits 15, 16, 17 immediately before and 18 immediately after - so the
trampoline did not merely get entered, it went on to run the script it names.

This closes the chain the ticket asked for:

```text
authored entity instantiated        (TOOLKIT-029)
-> engine consumes authored descriptor   (TOOLKIT-030, 67 samples)
-> descriptor handler reached            <- frame 2577, r0 = 0x0808D788
-> attached script root consumed         <- [r0+4] = 0x0808D77C
-> interpreter executes                  <- INTERP on the same frame
```

### The type confound, raised by the operator

The operator observed that the control entity **moves** and the authored one does
not, and identified the cause correctly: the two builds use different entity
types. That is a real confound and it is recorded rather than argued away.

| build | type | id | descriptor | handler |
|---|---|---|---|---|
| authored | `0x56` | `0xD3` | `0x0808D788` | `0x0800421F` (script) |
| type control (map-428 clone) | `0x06` | `0x20` | `0x0808D788` | `0x0800421F` (script) |
| **inheritance control** (TOOLKIT-029 ROM) | **`0x56`** | **`0xD3`** | `0x080555A0` | `0x0800421D` (`bx lr`) |

So the map-428 clone is **not** a clean control for the execution question: it
varies type and id as well. What the authored run establishes independently of
type is narrower but still exact - the descriptor in `r0` was `0x0808D788`, the
value the SDK wrote from project state, not the `0x080555A0` the clone template
carried. The thing that executed was the attachment.

The **inheritance control** is the clean A/B, and it is the one the ticket's
independence requirement actually wants: it differs from the authored build in
**exactly one word**, the descriptor, with type and id held identical. It is
TOOLKIT-029's published ROM
`a425ae73af5c5b4029882e8fb62ca398ee0e3b8a9a4fbb63dee8dc9834d7bed4`, verified
above to carry type `0x56`, id `0xD3` and the null handler `0x0800421D`.

### Repeat, and attribution at every hit

The trampoline was reached **five** times in one authored session, all with the
same descriptor and payload:

| # | frame | approx. seconds | `r0` | `[r0+4]` |
|---:|---:|---:|---|---|
| 1 | 2,577 | 43.0 | `0x0808D788` | `0x0808D77C` |
| 2 | 5,551 | 92.5 | `0x0808D788` | `0x0808D77C` |
| 3 | 6,543 | 109.0 | `0x0808D788` | `0x0808D77C` |
| 4 | 9,701 | 161.7 | `0x0808D788` | `0x0808D77C` |
| 5 | 11,918 | 198.6 | `0x0808D788` | `0x0808D77C` |

Two things follow that a single hit could not establish.

**It is repeatable, not incidental.** Five occurrences over 13,680 frames of one
session rules out a one-off coincidence of timing.

**It is not a timer.** The gaps are 49.6 s, 16.5 s, 52.6 s and 37.0 s. An
interval that irregular is driven by what the player is doing, not by a fixed
period, so the trigger is tied to gameplay rather than to elapsed time.

**Ownership holds at every hit.** The structural channel sampled the live
placement slot within a second either side of all five, and every sample read
`+0x14 = 0x0808D788`. The entity that owned the executing descriptor was the
authored one, throughout.

## 5. Runtime results, side by side

Three builds, one savestate, one observer, ordinary play by the operator.

| | authored | inheritance control | type control |
|---|---|---|---|
| ROM SHA-256 | `f6595c4e` | `a425ae73` | `59f28fea` |
| body type / id | `0x56` / `0xD3` | **`0x56` / `0xD3`** | `0x06` / `0x20` |
| body `+0x14` | **`0x0808D788`** | `0x080555A0` | `0x0808D788` |
| handler named | `0x0800421F` script | `0x0800421D` `bx lr` | `0x0800421F` script |
| **EXEC** (trampoline) | **5** | **0** | **0** |
| **INTERP** (liveness) | 20 | 20 | 20 |
| live descriptor observed | `0x0808D788` | `0x080555A0` | `0x0808D788` |
| frames | 13,680 | 7,380 | 8,460 |

Every run reached the interpreter 20 times, so no run is a blind one: a zero in
the EXEC row of any column is a measured absence, not an unproven instrument.

### The inheritance control settles the type confound

The operator observed that the map-428 clone moves and the authored entity does
not, and correctly identified the cause: the two builds use different entity
types. That made the type control unusable for the execution question on its own,
because it varies type and id as well as being a different record.

The inheritance control is the answer, and it is the form the ticket's
independence requirement actually asks for. It differs from the authored build in
**exactly one word** - the `+0x14` descriptor - with type and id held identical:

| | authored | inheritance control |
|---|---|---|
| ROM SHA-256 | `f6595c4e89189f6420130f2bb5f09e447621ee095f16bff4074f12678ea0a9fb` | `a425ae73af5c5b4029882e8fb62ca398ee0e3b8a9a4fbb63dee8dc9834d7bed4` |
| body type | `0x56` | **`0x56`** |
| body id | `0xD3` | **`0xD3`** |
| body `+0x14` | `0x0808D788` | `0x080555A0` |
| handler named | `0x0800421F` (script) | `0x0800421D` (`bx lr`) |
| frames observed | 13,680 | 7,380 |
| **trampoline hits** | **5** | **0** |
| interpreter hits | 20 | 20 |
| live descriptor | `0x0808D788` | `0x080555A0` |

Both runs reached the interpreter 20 times, so the control's zero is a measured
absence rather than a blind instrument. Entity type is held constant across the
pair. The only thing that changed is the attachment, and the execution changed
with it.

> **RUNTIME-PROVEN AUTHORED BEHAVIOR: YES**

## 6. What is claimed, and what is not

**OBSERVED.** On the authored build, the program counter reached the script
trampoline `0x0800421E` five times across one session, each time with
`r0 = 0x0808D788` - the descriptor the SDK wrote from project state - and
`[r0+4] = 0x0808D77C`, its attached script root, with the interpreter entered on
the same frame. The live placement slot held that same descriptor at every hit.
On a build differing only in that word, with the same entity type and id and the
same instrument proven live, the trampoline was reached zero times.

**NOT CLAIMED.** A visible gameplay consequence of the script. The attached
script sets a collision rectangle at tiles (6,24)..(10,25) from literal operands,
nowhere near the authored entity at (22,22), and TOOLKIT-030 already showed that
region reads saturated. The ticket explicitly allows this: a visible consequence
is desirable but not mandatory when execution attribution is exact, and here the
attribution is exact.

**NOT CLAIMED.** That the type control's movement is script-driven. That entity
moves because of its own type, and its trampoline count was zero.

## 7. The trigger

The static census refuted map construction: the constructor stores the
descriptor at `actor + 0x228` and returns without calling it. The runtime data
agrees and narrows it further.

The five hits fall at 43.0 s, 92.5 s, 109.0 s, 161.7 s and 198.6 s, so the gaps
are 49.6 s, 16.5 s, 52.6 s and 37.0 s. That is not a fixed period, so the
invocation is not a timer. It is also not construction: the entity was present
and holding the authored descriptor continuously from early in the run, while
execution occurred only at those five moments.

What is established is therefore: **the trigger is gameplay-driven and
intermittent, not construction-time and not periodic.** Identifying the exact
player action that produces it is the next question, and is deliberately not
claimed here on five samples with no per-hit input record.
