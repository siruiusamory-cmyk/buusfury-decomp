# ROM-005 executable consumer analysis

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
