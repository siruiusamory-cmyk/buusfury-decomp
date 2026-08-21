# ROM-005/ROM-006 executable consumer analysis

## Scope and profile

This analysis targets only `buus_fury_usa_rev0_01c1707f`, SHA-256 `940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e`. The ROM-004 baseline is commit `6cbf218f8894618dfd55342c48e48baecc994292` (`feat: add variation-array first-word analysis`). The MapEntry contract remains a `0x38`-byte record with `variation_array_pointer_raw` at `+0x2C`; the project reader still reads only the four bytes at variation target `+0x00` and never follows the resulting value.

## Static evidence

The pinned `2genkidev/buusfury@cc53d0cd2d1c167e749419187e2d92017ac07468` source retains this executable region inside `INCBIN` (`extern/buusfury/asm/buu.s:11`), so the evidence below comes from direct Thumb decoding of the verified ROM. Addresses are even instruction-fetch addresses. An address stored as a Thumb function pointer would have bit 0 set, for example `0x080089CD` for fetch address `0x080089CC`. No state bit was removed from either variation data address or `first_word_raw`.

### MapEntry lookup

Thumb function `0x080089FC` directly references the canonical table. At `0x08008A0A`, `LDR r1,[pc,#0x4C]` reads the literal at `0x08008A58`, whose value is `0x0808E2E0`. The function compares the first two MapEntry bytes, advances by `0x38`, and returns the matching record pointer in `r0`. Direct `BL` call sites were found at `0x08004A82`, `0x08008D2A`, `0x08008D6C`, `0x08008E94`, and `0x08009056`.

### Indexed variation-word resolver

The strongest consumer is Thumb fetch address `0x080089CC`:

```text
080089CC  6AC0  LDR  r0,[r0,#0x2C]
080089CE  0089  LSLS r1,r1,#2
080089D0  1840  ADDS r0,r0,r1
080089D2  3840  SUBS r0,#0x40
080089D4  6BC0  LDR  r0,[r0,#0x3C]
080089D6  4770  BX   lr
```

The exact effective address is:

```text
MapEntry[+0x2C] + 4 * (selector - 1)
```

Therefore selector `1` makes the final `LDR` consume exactly `first_word_raw` at variation target `+0x00`. This function is more accurately an indexed variation-word resolver than a dedicated first-word getter. Its three direct Thumb callers are `0x08008ABA`, `0x08008BC4`, and `0x0800906A`.

### Downstream use

One complete lookup path is:

```text
08008D2A/08008D6C/08008E94  BL 080089FC
08008D38/08008D7A/08008EA4  BL 08008B30
08008B9C                    STR r1,[r4,#4]
08008BAE                    BL 080089A0
08008BB2                    STRB r0,[r4,#2]
08008BC0                    LDRB r1,[r4,#2]
08008BC2                    LDR r0,[r4,#4]
08008BC4                    BL 080089CC
08008BC8                    MOV r1,r0
08008BD0                    BL 0800953E
08009540                    MOV r5,r1
08009552                    STR r5,[r4,#0xC]
```

At entry to `0x0800953E`, the destination structure base is input `r0 + 0x80`; the selected variation word is retained at structure offset `+0x8C`. A second call path at `0x0800906A` likewise moves the resolver result to `r1` and passes it to `0x0800953E` at `0x08009078`.

The alternative caller at `0x08008ABA` passes the resolver result in `r1` to `0x08009670`. That callee performs `ADD r1,#0x40` followed by `LDMIA r1!,{r1,r2}`. Static executable behavior therefore treats the selected variation word as an address/base and dereferences words at `selected_value + 0x40` and `selected_value + 0x44`. This establishes pointer use for that path, but neither the stored object's type nor the dereferenced target's subsystem is independently identified.

No independently substantiated ARM-state consumer was found. Dynamic calls and code that synthesizes the table base without the literal `0x0808E2E0` remain possible.

## Recomp evidence

The pinned recomp checkout cannot supply behavioral correspondence in its present state. `extern/dbz-buus-fury-recomp/generated/README.md:1-4` states that generated output belongs in that directory, but no generated C++ is checked in. Its configuration requires SHA-1 `e65738e9d67688309f09811a54f495523ec9aada` (`extern/dbz-buus-fury-recomp/game.toml:19-21` and `:28-30`), while this ticket's verified ROM has SHA-1 `f1c4b07554d2a3b1ad2f325307051e775ce68087`. `extern/dbz-buus-fury-recomp/tools/regen.ps1:16-19` enforces the configured input before generation.

Consequently there is no generated function identifier, C++ dataflow, or recomp address safe to transfer. Only the behavioral search method is portable: independently find stride `0x38`, field `+0x2C`, indexed indirection, and downstream address use in each profile.

## Runtime experiment

### Samples

The added exact-value lookup identified this deliberate adjacent pair:

| Kind | MapEntry | Entry address | `+0x2C` field | Variation source | `first_word_raw` | Frequency |
|---|---:|---:|---:|---:|---:|---:|
| Shared | 172 | `0x08090880` | `0x080908AC` | `0x0807D294` | `0x0822CC08` | 10 |
| Unique | 173 | `0x080908B8` | `0x080908E4` | `0x0807D38C` | `0x0822A798` | 1 |

These values came from the existing exact-width `target[0:4]` reader. No adjacent variation words and no `first_word_raw` targets were read by project tooling.

### mGBA capability verification

Installed `mGBA.exe --version` reports `0.10.5 (26b7884bc25a5933960f3cdcd98bac1ae14d42e2)`, and installed `--help` exposes `--gdb` on TCP port 2345. Matching mGBA source implements GDB hardware breakpoints and read watchpoints in `src/debugger/gdb-stub.c:573-610`, register reads in `:361-382`, stepping in `:251-256`, and packet dispatch in `:704-759`. The ARM watch shim covers 32-, 16-, and 8-bit loads plus load-multiple at `src/arm/debugger/memory-debugger.c:38-47` and `:84-91`.

### Attempt and result

The unchanged verified ROM was run twice through mGBA's GDB stub. This was a local, non-canonical observation: the bounded harness remained under ignored `build/` and is not a committed replay test. The reproducible project procedure is the manual debugger sequence below; the automated no-hit result is reported only as an attempted reachability check and contributes no evidence-level promotion. The harness sent no GDB memory-write packet and installed:

```text
Z0,80089d4,2   -> OK
Z3,807d294,4   -> OK
Z3,807d38c,4   -> OK
```

The first run stopped after 150 seconds. The second stopped after 200 seconds after detecting one visible emulator window and delivering 31 ordinary host inputs using mGBA's default Qt bindings: Return for GBA Start and X for GBA A (`mGBA@26b7884... src/platform/qt/InputController.cpp:65-69`). Neither run reached the consumer breakpoint or either sample watchpoint. No PC or register dataflow was observed, so this is not Level 3 evidence and is not evidence that the code is unreachable. There was no known save, savestate, or independently established route to records 172 and 173.

For a route-known reproduction, use the Qt debugger console:

```text
watch/r 0x0807D294
watch/r 0x0807D38C
listw
reset
continue
```

At a hit, require the expected full 32-bit value, capture `status`, and disassemble the triggering PC. A code-first alternative is a breakpoint at `0x080089D4`; `r1 == 4` there proves original selector `1`, effective address is `r0 + 0x3C`, and one step should put `first_word_raw` in `r0`. No such hit is claimed here.

### ROM safety

Before and after both runs:

```text
SHA-256: 940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e
Size:    8388608
mtime:   1787188212329572100 ns
```

No GDB/debugger-requested memory write, ROM-mapping write, ROM patch, copied proprietary fixture, or persistent emulator artifact was created. Ordinary emulated CPU execution necessarily continued to mutate emulated runtime state.

## Consumer graph

```text
MapEntry lookup 0x080089FC
  -> MapEntry +0x2C
  -> variation source
  -> 0x080089CC indexed load at source + 4*(selector-1)
  -> selector 1: first_word_raw
  -> either retained at destination structure +0x8C
     or passed to 0x08009670
  -> 0x08009670 dereferences first_word_raw +0x40/+0x44
```

## Evidence level and semantic conclusion

Result is **Level 2 - static downstream role**. Verified-ROM code loads the value and one downstream path uses it as an address/base. Runtime tracing was genuinely attempted but did not reach the consumer, so Level 3 and Level 4 are not claimed.

Keep the project name `first_word_raw`. Evidence supports pointer use in one static path, but does not identify a graphics loader, decompressor, resource class, target structure, or runtime-reached first-word sample. `graphics_pointer_raw` and even `resource_pointer_raw` would overstate the established subsystem semantics.

## Unresolved questions

- Which ordinary game state reaches selector `1` for a known MapEntry?
- Does the stored `runtime-object +0x8C` value later feed the same address consumer?
- What subsystem owns `0x08009670` and the target fields at `+0x40/+0x44`?
- Do indirect or ARM-state consumers exist?
- Do all variation elements have the same pointer role?

The next ticket should obtain or create a reproducible route/save for one known map, capture the `0x080089D4` dataflow, then step only through `0x08009670` far enough to identify its owning subsystem. It should not parse the target structure first.

# ROM-006 runtime reachability and subsystem ownership

ROM-006 supersedes the ROM-005 runtime no-hit result above. It raises the resolver evidence to Level 3 on the same verified profile while retaining `first_word_raw` and the no-target-parsing boundary.

## ROM-005 baseline

ROM-005 was committed before this work as `245a6efc9f4fb78b683b27ab6a6960bcf9682769` (`feat: identify variation-array executable consumer`). Its pre-commit suite passed 118 tests, prior ROM-002 through ROM-004 regressions matched their recorded counts, evidence remained Level 2, and the worktree was clean before ROM-006 began.

## Selector provenance

All addresses below are Thumb instruction-fetch addresses. Stored Thumb code pointers would carry bit 0; arbitrary data values are not normalized.

The resolver receives `r0 = MapEntry*` and `r1 = selector`. At `0x080089CE`, `LSLS r1,r1,#2` changes selector `1` to the scaled value `4` observed at `0x080089D4`. The final effective address is still:

```text
MapEntry[+0x2C] + 4 * (selector - 1)
```

The three direct callers have distinct selector sources:

- `0x08008ABA`: byte `[r7+0x02]`, with MapEntry pointer `[r7+0x04]`; this path passes the selected value to `0x08009670`.
- `0x08008BC4`: byte `[r4+0x02]`, populated from helper `0x080089A0`; this path passes the selected value to `0x0800953E`.
- `0x0800906A`: low byte of the `0x080089A0` result; this also passes the selected value to `0x0800953E`.

Helper `0x080089A0` returns a nonzero supplied selector unchanged. With supplied selector zero, it returns exactly `1` when MapEntry `+0x28` is null; all 452 verified-profile `variation_script_pointer_raw` observations at that offset are null. A statically simple route is `0x08008EA4 -> 0x08008B30`: `r3` is set to zero before the call, so the null `+0x28` case selects `1`. The runtime captures below instead returned through `LR = 0x0800906F`, proving the reached caller was `0x0800906A`.

No executable path examined here derives the selector from MapEntry byte `variation_raw` at `+0x03`. That relationship remains unknown.

## Reproducible runtime route

The installed emulator was `mGBA 0.10.5 (26b7884bc25a5933960f3cdcd98bac1ae14d42e2)`. Matching source exposes the Qt Scripting window at `src/platform/qt/Window.cpp:1673-1675`, attaches the active core as Lua global `emu` at `src/core/scripting.c:679-697`, exposes frame/key/state/screenshot methods at `src/core/scripting.c:431-466`, implements GDB register reads at `src/debugger/gdb-stub.c:357-382`, and installs hardware breakpoints without ROM patching at `src/debugger/gdb-stub.c:573-610`.

Tracked helper source contains no save state or extracted ROM data:

- `tools/runtime/load_mgba_lua.ps1` verifies the trusted ROM before launch, gives each run a fresh task-local save directory, loads Lua through Qt UI Automation, and verifies hash, size, and mtime afterward.
- `tools/runtime/rom006_bootstrap.lua` resets the core, pulses GBA A on frames `1210..1214`, `1810..1814`, and `2410..2414`, then saves ignored local state `build/rom006/bootstrap.mss` at frame `2420`.
- `tools/runtime/rom006_bootstrap_map4.lua` adds pulses at `2630..2634` and `2960..2964`, then saves ignored local state `build/rom006/bootstrap-map4.mss` at frame `2970`.
- `tools/runtime/rom006_gdb_probe.py` gives mGBA a fresh state-adjacent save directory, allowlists only `?`, `qSupported`, `g`, `Z0`, `z0`, `s`, and `c`, rejects GDB memory/register-write packets, and compares observed `r0` against the profile-scoped first-word census.

Exact first-sample replay from reset:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File `
  ".\tools\runtime\load_mgba_lua.ps1" `
  -RomPath "<checkout>\roms\Dragon Ball Z - Buu's Fury (U).gba" `
  -LuaPath "<checkout>\tools\runtime\rom006_bootstrap.lua" `
  -ExpectedState "<checkout>\build\rom006\bootstrap.mss"

.\.venv\Scripts\python.exe -m tools.runtime.rom006_gdb_probe `
  "<checkout>\roms\Dragon Ball Z - Buu's Fury (U).gba" `
  "<checkout>\build\rom006\bootstrap.mss" `
  --timeout 20
```

The second sample uses the same commands with `rom006_bootstrap_map4.lua` and `bootstrap-map4.mss`. No existing save or human reaction timing is required. Save files, screenshots, states, and run directories stay beneath ignored `build/rom006/`.

## Level 3 captures

Both selected raw values are unique in the 452-entry census. A heavily duplicated sample was not early-reachable within the bounded route, so it was not substituted for these deterministic captures.

| Capture | MapEntry | Entry address | Variation source | Expected | Observed | Match |
|---|---:|---:|---:|---:|---:|---|
| Reset route | 1 | `0x0808E318` | `0x080728D4` | `0x082B5FA0` | `0x082B5FA0` | yes |
| Early prologue transition | 4 | `0x0808E3C0` | `0x080728E0` | `0x082B5B2C` | `0x082B5B2C` | yes |

First capture register flow:

```text
PC 080089CC  r0=0808E318  r1=00000001  lr=0800906F  CPSR=0000003F
PC 080089D4  r0=08072898  r1=00000004  lr=0800906F  CPSR=2000003F
effective source = r0 + 0x3C = 080728D4
single-step
PC 080089D6  r0=082B5FA0
```

Second capture register flow:

```text
PC 080089CC  r0=0808E3C0  r1=00000001  lr=0800906F  CPSR=0000003F
PC 080089D4  r0=080728A4  r1=00000004  lr=0800906F  CPSR=2000003F
effective source = r0 + 0x3C = 080728E0
single-step
PC 080089D6  r0=082B5B2C
```

The CPSR T bit is set in every captured state. These are even logical instruction-fetch addresses reported by mGBA, not raw stored code pointers.

## `0x08009670` subsystem ownership

Thumb function `0x08009670..0x0800967F` is a thin population adapter. It ignores its incoming `r0`, advances selected-value argument `r1` by `0x40`, loads two words from selected value `+0x40/+0x44` into `r1/r2`, resolves global `0x03002A64`, and calls `0x08012664`:

```text
08009670  PUSH {r3,lr}
08009672  ADDS r1,#0x40
08009674  LDR  r0,[pc,#0x280]  ; literal 080716C4
08009676  LDM  r1,{r1,r2}
08009678  LDR  r0,[r0,#8]      ; 080716CC -> 03002A64
0800967A  BL   08012664
0800967E  POP  {r3,pc}
```

The only direct Thumb `BL` reference is `0x08008AC2` inside `0x08008AA0`. That caller selects a variation word through `0x08008ABA -> 0x080089CC`, moves the selected address to `r1`, and calls the adapter. `0x08008AA0` itself is reached at `0x0800271A` and `0x08008C66`; the latter is in the broader MapEntry load flow begun at `0x08008B30`.

`0x08012664` treats the two loaded words as a count and pointer-array base. It iterates descriptors backward, loads each descriptor's first word as an indirect factory target, calls it through the Thumb `BX r1` veneer at `0x08046AA2`, then appends each returned runtime pointer to the IWRAM registry at `0x03002A64` while incrementing its count. Mode-dependent neighboring paths destroy or prune old registry entries through `0x08012628` and `0x08012900`.

Immediate proven writes are IWRAM registry count/pointers only. This path has no direct VRAM (`0x06000000`), palette RAM (`0x05000000`), OAM (`0x07000000`), I/O (`0x04000000`), DMA setup, decompression call, or graphics copy. Indirect factories may have further effects and were not resolved.

Neighboring manager functions `0x080126D4..0x080128F2` compare positions against four signed bounds at managed entries `+0x04/+0x06/+0x08/+0x0A`, perform rectangle-overlap queries, and dispatch relative virtual methods. Combined with its placement in MapEntry loading, this strongly supports **map-load spatial-object/region registry population**. Exact subtype remains unresolved: collision region, trigger region, activation/event zone, or a mixture.

The deterministic early routes hit `0x0800906A -> 0x0800953E`, not `0x08008ABA -> 0x08009670`; bounded attempts to reach the adapter at runtime produced no hit. Therefore subsystem ownership is **STRONGLY SUPPORTED** by static executable behavior, not runtime-confirmed Level 4 evidence.

## Evidence and naming decision

Overall result is **Level 3 - runtime observed on the verified ROM**. Two reproducible captures satisfy the required chain:

```text
verified MapEntry
  -> +0x2C variation source
  -> selector 1
  -> source +0x00
  -> predicted first_word_raw
  -> same value observed in r0 after 080089D4
```

Subsystem classification does not raise the overall result to Level 4 because `0x08009670` was not reached in the bounded runtime route and its dynamic factory targets remain unknown. Keep `first_word_raw`; neither `graphics_pointer_raw` nor a narrower spatial-object name is justified for every selected value.

No project data reader follows `first_word_raw` or reads target `+0x40/+0x44`. Those offsets appear only because executable instructions access them.

## ROM-006 unresolved questions

- Which ordinary route reaches the `0x08008ABA -> 0x08009670` caller with selector `1`?
- What exact semantic types do the count and pointer-array words loaded at selected value `+0x40/+0x44` have?
- Which factory targets can occur, and what concrete region subtypes do they create?
- Is the registry homogeneous, or does it combine collision, trigger, activation, and event objects?
- Can an early duplicated `first_word_raw` sample be reached without unrelated progression?

The next ticket should obtain a deterministic state immediately before `0x08008ABA -> 0x08009670`, capture the adapter and one indirect factory at runtime, and stop before general target parsing.

# ROM-007 Higher Plane factory capture

ROM-007 used the user-provided playable state at the first save point outside Grand Kai's mansion in the Higher Plane. Original `.ss1` and `.sav` stayed beneath ignored `roms/`; byte-identical working copies stayed beneath ignored `build/rom007/`. Installed emulator remained `mGBA 0.10.5 (26b7884bc25a5933960f3cdcd98bac1ae14d42e2)`.

## Reproducible runtime route

At paused save state, a read-only GDB packet for instruction-referenced global `0x03001980` (`context 0x0300197C + 4`) returned MapEntry pointer `0x0808EB30`, canonical index 38. Webfoot independently predicted variation source `0x08075278` and `first_word_raw = 0x08295C58` for that entry.

Tracked Lua holds GBA Down for frames 1 through 120. This crosses nearby south transition without human timing. Probe opens mGBA's Scripting window only after its title reports loaded game, preventing execution before Lua global `emu` is attached. Exact local command:

```powershell
.\.venv\Scripts\python.exe -m tools.runtime.rom007_factory_probe `
  "roms\Dragon Ball Z - Buu's Fury (U).gba" `
  "build\rom007\higher-plane-original.ss1" `
  "build\rom007\higher-plane-original.sav" `
  --state-sha256 329b06bc1adc458e637bd1a3afc1692ee40854d327567ea0885379c275baeb28 `
  --save-sha256 e12c350970b21ac0b5df32dba0a76b3a333c2a17a976f12a6cc5844880f08e5a `
  --lua tools\runtime\rom007_move_south.lua `
  --injector tools\runtime\inject_mgba_lua.ps1 `
  --timeout 20
```

Probe allowlists register reads, one exact four-byte RAM read at `0x03001980`, hardware-breakpoint operations, continue, and single-step. It never sends GDB memory-write or register-write packets. Each run uses fresh save/state/screenshot directories under ignored `build/rom007/`.

## Active MapEntry and adapter capture

South transition selected MapEntry 39, not starting MapEntry 38. Runtime and Webfoot agreed exactly:

| Evidence | Value |
|---|---:|
| MapEntry | `0x0808EB68` (index 39) |
| Resolver selector | `1` |
| Variation source | `0x080753F0` |
| Predicted `first_word_raw` | `0x08294968` |
| Observed after `0x080089D4` | `0x08294968` |
| Resolver LR | `0x08008ABF` |

At `0x080089D4`, `r0 = 0x080753B4`, scaled `r1 = 4`, `PC = 0x080089D4`, and CPSR T was set. One step reached `0x080089D6` with `r0 = 0x08294968`.

Same selected value then reached required adapter:

```text
PC=08009670  LR=08008AC7
r0=030019A4  r1=08294968  r2=03002B24  r3=00000000
```

CPU stepping through `0x08009672..0x08009678` observed, without a Webfoot target parser:

```text
field_40_raw = 00000002
field_44_raw = 08294960
manager      = 03002A64
```

At `0x08012664`, these arrived as `r0 = 0x03002A64`, `r1 = 2`, and `r2 = 0x08294960`. Function iterated two array elements in reverse. For each it loaded descriptor pointer, loaded raw factory target `[descriptor+0]`, dispatched through `0x08046AA2: BX r1`, incremented manager count, and stored returned `r0` at `manager + 4 + old_count*4`.

## Concrete factory

First runtime dispatch:

| Item | Runtime value |
|---|---:|
| Descriptor argument `r0` | `0x08294948` |
| Raw factory target `r1` | `0x08007675` |
| Execution state | Thumb |
| Fetch address after `BX r1` | `0x08007674` |
| Return pointer | `0x0203DEBC` |
| Registry slot | `0x03002A68` |
| Old/new registry count | `0` / `1` |

Static executable tracing identifies `0x08007674` as a 24-byte allocator/initializer factory:

```text
08007674  save descriptor argument
08007678  r0 = 0x18
0800767A  BL 0803D5B8              ; allocation-like call
0800768A  BL 08009AEC              ; common initializer
08007690  install table base 0804A09C at object+0
08007694  retain descriptor at object+0x14
08007696..080076A0 initialize bytes object+0x10/+0x11
```

Common initializer copies descriptor words `+0x08/+0x0C` into object `+0x04/+0x08`. Those four signed halfword lanes become object `+0x04/+0x06/+0x08/+0x0A`, exactly AABB bounds tested by registry consumers `0x080126D4..0x08012843`. It also stores at object `+0x0C` a dynamically produced callback reference later used by overlap-gated relative dispatch. Table bases `0x0804A09C` and `0x0804E444` are data, not direct code pointers.

This proves captured factory creates and registers a 24-byte rectangle-aware runtime object. It does not prove collision, trigger, activation, event, or transition semantics.

## Bounded behavior experiment

Controlled action was same 120-frame south movement. After population, breakpoint `0x08012784` caught one AABB-gated callback:

```text
queried object = 0203DDD4
query context  = 0202E56C
callback raw   = 080077B1
callback fetch = 080077B0 Thumb
callback body  = MOVS r0,#1; BX lr
```

Callback returned true and had no direct memory side effect. Crucially, queried object `0x0203DDD4` was neither captured return `0x0203DEBC` nor second return `0x0203DF2C`. Experiment therefore does **not** attribute callback or visible map transition to captured factory. No matching callback for `0x0203DEBC` was reached within bounded route. This is precise runtime blocker to a collision/trigger/transition label.

## Registry model and conclusion

Same population call ran a second distinct Thumb factory, raw `0x080072CD` / fetch `0x080072CC`, returning `0x0203DF2C` into slot `0x03002A6C`. Two distinct factories populated same registry in one count-2 pass, so this active load has **clearly heterogeneous construction paths**. Whether all produced objects share one semantic family remains unknown.

Semantic classification for factory `0x08007675`: **STRONGLY SUPPORTED - 24-byte rectangle-aware runtime object**. This is narrower than generic registry object and no stronger than executable evidence permits. Overall evidence remains **Level 3**: runtime confirms resolver, adapter, factory dispatch, returned object, and insertion, but no runtime callback was matched to that object and no meaningful collision/trigger/transition role is confirmed. Keep `first_word_raw`.

No general parser was added for selected values, `+0x40/+0x44`, descriptors, or runtime objects. Next bounded work should track `0x0203DEBC` from insertion to its first overlap-gated callback, including prune/repopulation events, before any source-format parser is designed.

# ROM-008 Exact Object Behavior Trace

ROM-008 keeps the Higher Plane state, in-game save, and ROM as read-only sources. Experiments use byte-identical copies below ignored `build/rom008/`. Canonical identities rechecked before the bounded probe were:

| Artifact | Size | SHA-256 |
|---|---:|---|
| Verified ROM | 8,388,608 | `940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e` |
| Original `.ss1` | 70,875 | `329b06bc1adc458e637bd1a3afc1692ee40854d327567ea0885379c275baeb28` |
| Original `.sav` | 8,192 | `e12c350970b21ac0b5df32dba0a76b3a333c2a17a976f12a6cc5844880f08e5a` |

## Factory instance and verified load epoch

The deterministic MapEntry-38-to-39 south transition reproduced the target tuple without assuming a fixed EWRAM address:

```text
active load       MapEntry 39 / selected value 08294968
manager           03002A64
load epoch        1
descriptor        08294948
factory raw       08007675
factory fetch     08007674 Thumb
returned object   0203DEBC
registry slot     03002A68
count             0 -> 1
runtime bounds    left=592, top=136, right=601, bottom=241
```

The object became live only after `0x08012682` stored its return pointer. A replay identifier is the tuple `(verified MapEntry/selector/value, manager, probe load epoch, descriptor, raw factory target, returned pointer, insertion serial)`. The EWRAM pointer alone is not durable identity. The probe load epoch begins only after the runtime resolver, adapter, active MapEntry, and static census all agree on MapEntry 39, selector 1, variation source `0x080753F0`, and selected value `0x08294968`; it is not claimed to be an internal game generation counter.

Static lifecycle evidence supports that rule:

- `0x08048488` clears registry count at `0x03002A64` without walking stale slots.
- `0x0801268A` removes one matching pointer, commits the lower count at `0x080126AC`, compacts later slots, and invokes object cleanup at `0x080126CE`.
- For dispatch base `0x0804A09C`, the cleanup entry has raw target `0x080510A1`, Thumb fetch `0x080510A0`, and reaches allocator-release path `0x0803D63C`.
- A committed reset, committed target removal, or a new verified population load epoch invalidates the old runtime pointer. The probe retires on reset only after `0x08048488` stores count zero, and on removal only after `0x080126AC` commits a one-step count decrease. No reset or target-removal event occurred between insertion and the bounded ROM-008 observation window.

## Dispatch-table boundary

Factory `0x08007674` installs data/table base `0x0804A09C` at object `+0`. Its evidence-backed entry in this ticket is cleanup raw `0x080510A1` / Thumb fetch `0x080510A0`, reached from registry removal.

The AABB callback source is separate. Common initializer `0x08009AEC` calls a descriptor-driven function from descriptor `+0x04` and stores the returned callback reference at object `+0x0C`. AABB consumers then derive relative callback targets from that reference at `0x08012784`, `0x0801279C`, and `0x08012832`. No concrete callback target from this reference was captured for the `0x08007675` object, so dispatch base `0x0804A09C` is not mislabeled as its spatial callback table.

## Query correction and bounded runtime result

Independent Thumb-1 `BL` decoding over the verified ROM established the real query entries and callers:

```text
08006E4E -> 080126D4
08021DFE -> 080126D4
08021E06 -> 080126D4
08012AEC -> 080127AE
08022142 -> 08012846
```

`0x080127AC` is the `POP` ending `0x080126D4`, not an entry. `0x08012844` is the terminal branch of the routine beginning at `0x080127AE`, not an entry. Earlier after-guard candidate breakpoints at `0x0801273C`, `0x080127F4`, and `0x08012864` therefore cannot distinguish an uncalled query routine from an entry rejected by a pre-loop guard.

Three bounded replays reproduced the target factory and live insertion. The standard 120-frame south route and one six-second Down-only extension produced no after-guard AABB candidate for object `0x0203DEBC`; they also produced no reset or removal of that object. No unrelated object callback was accepted. The extension was discarded after this negative result and is not tracked.

The next minimum runtime check is entry-level, not more navigation: break at `0x080126D4`, `0x080127AE`, and `0x08012846`, verify LR against the callers above, and record the first rejecting guard. For `0x080126D4`, `0x080126F4/0x080126F8` additionally expose its dynamic precursor and the signed halfword gate at returned value `+0x16`. The tracked `rom008_query_probe` encodes exact current-load-epoch identity checks and rejects wrong-object callbacks. Only direct point-query callsites `0x08012784/0x0801279C`, where `r1` is the current target object, may satisfy callback completion; the other callback families remain observation-only until their `this` provenance is proven. Its GUI replay could not be executed after implementation because the environment rejected further mGBA launches at the approval quota; this is an external runtime blocker, not evidence that the queries are unreachable.

Entry-level replay command, once GUI launch approval is available:

```powershell
.\.venv\Scripts\python.exe -m tools.runtime.rom008_query_probe `
  "roms\Dragon Ball Z - Buu's Fury (U).gba" `
  "build\rom008\higher-plane-original.ss1" `
  "build\rom008\higher-plane-original.sav" `
  --state-sha256 329b06bc1adc458e637bd1a3afc1692ee40854d327567ea0885379c275baeb28 `
  --save-sha256 e12c350970b21ac0b5df32dba0a76b3a333c2a17a976f12a6cc5844880f08e5a `
  --lua tools\runtime\rom007_move_south.lua `
  --injector tools\runtime\inject_mgba_lua.ps1 `
  --timeout 25
```

Exit `0` requires one same-load-epoch population, target factory, live insertion, exact target AABB, and exact target callback chain. An incomplete bounded route exits `2`; MapEntry/selector/value, descriptor, factory, manager, slot, epoch, pointer, callback order, Thumb state, and original-artifact identity mismatches raise rather than being accepted.

## Attribution and semantic conclusion

No AABB query or callback for the exact load-epoch-1 object was captured. Consequently there is no executable chain from this object to movement rejection, script/event activation, map transition, interaction, or another meaningful consequence.

Classification remains **STRONGLY SUPPORTED: 24-byte rectangle-aware runtime object**. Evidence remains **Level 3**, not Level 4. `first_word_raw` remains the correct global field name. A ROM descriptor parser is **not ready**: the smallest blocker is one same-load-epoch target AABB/callback capture plus its immediate downstream behavior. No selected-value, descriptor, callback-table, or runtime-object parser was introduced.

# ROM-009 Clean Gameplay Exact-Object Callback Trace

## Inputs, reviews, and safety

ROM-009 located the newer private runtime inputs beneath ignored `roms/` without
assuming their names. Canonical identities recorded before use were:

| Artifact | Size | SHA-256 |
|---|---:|---|
| Verified ROM | 8,388,608 | `940ad5f01db4465b8877dfe739510cbf34f4ea3d390f3df13519808bc36f059e` |
| Original `.ss1` | 72,775 | `ea500f3a774d42032202d9c3d7bfb437478417ba37e4b72c634993d7d701ac82` |
| Original `.sav` | 8,192 | `9bbd7cb67b724fbe1263d9b5b7cedf0a6c935a2ff6448befd0a0348b7607f46a` |

Byte-identical working sources remained under ignored `build/rom009/`. The ROM
and working sources retained their pre-run hashes, sizes, and mtimes after every
completed replay; the untouched originals matched their before-ticket identities
again after runtime work. The canonical profile was reidentified as
`buus_fury_usa_rev0_01c1707f` before and after runtime work. No ROM, register, or
memory write packet was sent.

The required pre-runtime static review kept dispatch base `0x0804A09C` separate
from object `+0x0C`: the former has a verified cleanup entry, while the latter is
the dynamically produced reference used by spatial callback callsites. The
required runtime design rejected ROM-008's fixed MapEntry-39 and descriptor
assumptions. ROM-009 therefore derives the load from the runtime resolver and
active MapEntry, then captures the first aligned trusted-ROM descriptor whose raw
factory is exactly `0x08007675`.

## Exact runtime identity and bounded result

Five completed bounded replays reproduced one exact current-load identity:

```text
active load          MapEntry 39 / address 0808EB68 / selector 1
variation source     080753F0
selected value       08294968
manager              03002A64
probe load epoch     1
descriptor           08294948
factory raw/fetch    08007675 / 08007674 Thumb
returned object X    0203DE7C
registry slot        03002A68
insertion serial     1
count                0 -> 1
runtime bounds       (592,136)..(601,241)
```

The clean route used 120 no-input frames, 120 Down frames, then no input through
frame 400. A second bounded route used the same single south transition followed
by 60 Left and 60 Right frames on MapEntry 39. No second population epoch or X2
was observed.

After X became live, none of the three verified query entries, five verified BL
callsites, four query-capable caller entries, or three instrumented internal
guard sites executed. No exact AABB or callback was captured. The runtime slot
`0x03001C34`, loaded as the point-query context by verified caller `0x08006E3C`,
contained raw zero at X insertion. This is an observed input/runtime-environment
blocker, not a proven guard and not a proven cause of absent scheduling.

The conditional an independent reviewer scheduler review was used because the clean replay
produced no exact callback. It confirmed that zero query-entry hits cannot be
promoted to an instruction-level rejection. Further state creation, story
progression, or gameplay expansion would exceed the ticket boundary.

Required classifications:

- Primary runtime result: **D. ENVIRONMENT BLOCKED**.
- Dialogue hypothesis: **UNRESOLVED**.
- Evidence remains **Level 3**.

The D result is limited to this supplied state and allowed route: they did not
instantiate a query-capable scheduler context after X became live. The causal
relationship between the null context slot and absent scheduling is `UNKNOWN`.
It is not evidence that X is never queried or that dialogue controls the path.

## Structural parser readiness

Structural parser readiness is **NO**. Family factory identity, rectangle source
fields, retained descriptor, and callback-producing source field have evidence,
but the source descriptor's minimal extent/boundary and complete lossless field
map remain unestablished. No parser was implemented.

Portable validation after ROM-009 is **208 passed, 0 failed, 0 skipped**. Runtime
checks remain private and ignored; no ROM, save, state, dump, screenshot, or
extracted proprietary artifact is tracked or staged.
