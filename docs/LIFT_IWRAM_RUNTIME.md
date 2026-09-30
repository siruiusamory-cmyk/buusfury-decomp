# DECOMP-RUNTIME-IWRAM-001 - the runtime-installed IWRAM call subsystem

**Status:** the mechanism is recovered and reproducible. Slot `0x030007A8` is
resolved, its install path is proven from the reset code's own instructions, the
relevant veneer family is mapped exhaustively, and the operation inside
`sub_08011B04` that the previous ticket could not characterise is explained.

**Baseline:** `4c9101bab63178c3690de846dc2bd6e7ffbdef93`.
**Canonical ROM:** `f1c4b07554d2a3b1ad2f325307051e775ce68087` (unchanged).

This document is the integration of five independent investigations. Every claim
carries a label:

* **CONFIRMED** - read from the cartridge and independently reproduced;
* **INFERRED** - a conclusion drawn from the instructions that the bytes do not
  state outright;
* **UNKNOWN** - not settled by this work.

---

## 1. The mechanism in one page

A Thumb call site does `bl 0x0804912C`. That address holds:

```
0x0804912C   78 47        Thumb   bx pc
0x0804912E   C0 46        Thumb   nop            (never executed)
0x08049130   04 F0 1F E5  ARM     ldr pc, [pc, #-4]
0x08049134   A8 07 00 03  ARM     dcd 0x030007A8
```

`bx pc` exists only in Thumb and uses *instruction address + 4*, which is word
aligned, so it clears the T bit and the word at `+4` is fetched in **ARM** state.
That word is `ldr pc,[pc,#-4]`: PC reads as `instruction + 8` and the `-4` lands
on **stub + 8**, the literal. So the stub jumps to the literal itself.

> **CONFIRMED: the literal IS the destination. The trampoline does not load a
> function pointer from `0x030007A8`, and there is nothing opaque about the
> callee.** The previous ticket recorded the opposite - "jumps to whatever is
> stored at `0x030007A8` ... not statically resolvable" - and that reading was
> wrong. Section 9 lists the corrections.

`0x030007A8` is IWRAM, which has no ROM bytes of its own - but the reset code
copies a 4100-byte ROM block there at boot, verbatim, so the bytes that execute
at `0x030007A8` are known: they are ROM `0x087B814C`.

---

## 2. The install path

The arm7tdmi reset routine at `0x080000C0` (ARM, ending at its tail branch
`0x08000130 b 0x08049114`; literal pool `0x08000134..0x08000158`) programs DMA3
**twice**:

| | setup 1 | setup 2 |
| --- | --- | --- |
| SAD `0x040000D4` | `SP`, pointing at the single zero word it pushes | `0x087B79A4` |
| DAD `0x040000D8` | `0x03001004` | `0x03000000` |
| CNT `0x040000DC` | `0x850010BE` | `0x84000401` |
| CNT_L | `0x10BE` = 4286 | `0x0401` = 1025 |
| transfers | 32-bit, source address **fixed** | 32-bit, both addresses incrementing |
| therefore | a zero fill of **17144 bytes**: `0x03001004..0x030052FC` | a block copy of **4100 bytes**: `0x087B79A4..0x087B89A8` -> `0x03000000..0x03001004` |

CONFIRMED, from the instructions and their literal pool: `r0` is `0x04000000`
(`mov r0, #64, #12`, which the ARM immediate rotation turns into `0x04000000`),
the three stores are `str r1,[r0,#0xd4]` / `[r0,#0xd8]` / `[r0,#0xdc]` at
`0x0800010C`, `0x08000114` and `0x08000124`, and the control word is built by
`lsrs r1,r1,#2` on the literal `0x00001007` followed by `orr` with `0x84000000`.
The stores carry the `ne` condition only because the flags come from that `lsrs`;
both counts are non-zero, so both execute.

INFERRED, and only for the *first* setup's source-address field: `SAD = SP` points
at a word the routine pushes (`stmdb sp!,{r1}` with `r1 = 0`) and pops
(`add sp,sp,#4`) exactly once, so the transfer must read that one word repeatedly.
The instruction says the source address is held fixed; the surrounding code is
what makes that the only sensible reading.

**The 4100-byte length is not assumed.** Both readings of the control word's
count are computed and reported, and the 32-bit one is the one that tiles: it
ends at `0x087B89A8`, the first byte of the 0xFF fill run in ROM, *and* at
`0x03001004`, the destination of the first DMA in IWRAM. The 16-bit reading gives
2050 bytes and leaves three of the thirteen veneer destinations outside the copied
block - `0x03000858`, `0x03000A4C` and `0x03000CA0` - destinations the ROM itself
branches to. The two DMA setups also tile IWRAM exactly, with no gap and no overlap.

The odd literal `0x00001007` explains itself: `0x1007 >> 2 = 0x401`, so the
truncating shift is *why* the length is `0x1004` bytes and not `0x1007` units.

**How the slots are named.** Eight of the thirteen destination addresses - and
three of the four block-memory slots, `0x030007FC` being the exception - occur in
the whole 8 MiB image **exactly once**, and that occurrence is their own veneer's
literal. The other five (`0x03000000`, `0x03000040`, `0x03000700`, `0x030007FC`,
`0x03000CA0`) have further matches, and every one of those is either at an **odd**
offset, where no aligned 32-bit stored word can live, or inside a region the ROM
map classes as `unknown`, `compressed_asset` or `library_data` - never in a
confirmed code region.

**What else writes the block.** An independent sweep found post-boot writers, and
they matter for the claim above. Every one of them lands in the block's **192-byte
data tail**, `0x03000F44..0x03001004`: the lowest address written after boot is
`0x03000F70`, and the writers are ordinary game code (`0x080393A6`, `0x0803D820`,
`0x08040092`, `0x080419E0` and neighbours) plus the block's own IRQ dispatcher at
`0x087B85F8`. **No writer of any kind was found below `0x03000F44`**, which is the
whole code half - and the four block-memory routines sit at `0x03000768` and
`0x03000858`, far inside it. So the mapping "`0x030007A8` holds ROM `0x087B814C`"
is CONFIRMED for the boot copy and holds for every later instant as far as static
analysis reaches: a runtime-computed store cannot be excluded in principle, but
two independent searches over both instruction sets, every DMA register setup in
the image, and every absolute store found nothing that can reach those addresses.

---

## 3. The veneer family

The family is walked from the byte pattern, not declared. It is **fifteen
entries, `0x08049120..0x080491CC` (172 bytes)**, in two forms:

| # | entry | form | size | destination | state |
| ---: | --- | --- | ---: | --- | --- |
| 1 | `0x08049120` | `bx pc` + `ldr pc,[pc,#-4]` | 12 | `0x03000040` | ARM |
| 2 | `0x0804912C` | " | 12 | `0x030007A8` | ARM |
| 3 | `0x08049138` | " | 12 | `0x03000768` | ARM |
| 4 | `0x08049144` | " | 12 | `0x030007FC` | ARM |
| 5 | `0x08049150` | " | 12 | `0x03000388` | ARM |
| 6 | `0x0804915C` | " | 12 | `0x030004C0` | ARM |
| 7 | `0x08049168` | " | 12 | `0x03000858` | ARM |
| 8 | `0x08049174` | " | 12 | `0x03000560` | ARM |
| 9 | `0x08049180` | " | 12 | `0x03000700` | ARM |
| 10 | `0x0804918C` | " | 12 | `0x030002DC` | ARM |
| 11 | `0x08049198` | `bx pc` + ARM `b` | 8 | `0x08047040` | ARM |
| 12 | `0x080491A0` | " | 8 | `0x08047450` | ARM |
| 13 | `0x080491A8` | `bx pc` + `ldr pc,[pc,#-4]` | 12 | `0x03000CA0` | ARM |
| 14 | `0x080491B4` | " | 12 | `0x03000A4C` | ARM |
| 15 | `0x080491C0` | " | 12 | `0x03000000` | ARM |

CONFIRMED properties:

* **fifteen occurrences of `78 47 c0 46` exist in the whole 8 MiB image, and they
  are exactly these fifteen**. Every destination is distinct, and every one is
  ARM - bit 0 is clear in all thirteen literal words.
* **why two forms, arithmetically**: an ARM `B` reaches +/-0x2000000 (+/-32 MB).
  The thirteen IWRAM destinations are 83.9 MB *below* the stubs, so no branch can
  encode them and an absolute literal load is forced. The two ROM destinations
  are `0x2164` and `0x1D5C` bytes away, well inside range, so a plain `b` is used.
* the two branch targets `0x08047040` and `0x08047450` decode cleanly as ARM
  prologues (`push {r7,r8,sl,fp,lr}` at both), and as Thumb they are garbage.

The window around the family is not all veneer:

* `0x08049114` is a 12-byte **ARM -> Thumb** thunk (`E59FC000 ldr ip,[pc]` /
  `E12FFF1C bx ip` / `dcd 0x08046AED`), the same form as `0x080491CC`,
  `0x080491D8`, `0x080491E4`. These are ARM-state long calls and are not
  Thumb-callable.
* `0x08048ED8..0x08049110` is 143 consecutive words that are all condition field
  `0xF` (NV) and sorted ascending as signed 32-bit values. **UNKNOWN**: nothing
  in the image reads them through an ARM literal load, and no role is claimed.
* `0x080491F0..` is data: no ARM literal load, no Thumb `ldr rX,[pc,#imm]` and no
  Thumb `add rX,pc,#imm` anywhere in the image targets it. **UNKNOWN**.

---

## 4. What is installed (the block at `0x087B79A4`)

4100 bytes, copied verbatim, sha1 `99b20b07fe643fbc3c9802f9288efa8682a02782`.

It is **not** the ADS C library, and the earlier working assumption that it was
should be dropped. CONFIRMED counter-evidence: it is linked *for* IWRAM (its one
self-referential absolute word is `0x03000FB0`); it carries a 192-byte
initialised `.data` section and a 14-entry interrupt vector table; it contains a
`REG_IE`/`REG_IME`-wrangling IRQ dispatcher with an ARM -> Thumb -> ARM trampoline;
its copy/fill-shaped entries round their counts *up* and always move at least one
unit, which a conforming C library `memcpy`/`memset` never does; and its content is
two byte-table decoders, a signed-byte fixed-point resampler, Q10 dot products and
strided rectangle gathers. The characterisation "a game codec/mixing overlay placed
in IWRAM" is INFERRED; each individual mechanism below is CONFIRMED.

It holds 20 ARM functions plus one Thumb halfword (`IWRAM 0x03000C98 = 0x4720`,
`bx r4`, the dispatcher's interworking return) and the `.data` section. The split is
clean: **code `0x03000000..0x03000F44`** (3908 bytes, ending at `bx lr` at
`0x087B88E4`) and a **192-byte initialised data tail `0x03000F44..0x03001004`**
(ROM `0x087B88E8..0x087B89A8`, whose words decode only as garbage) - and it is
exactly that tail that game code writes after boot. The thirteen veneers are **not**
the only entry points: three further functions
(`0x03000330`, `0x03000414`, `0x03000868`... see the census in the report) have no
caller inside the blob and two of them are named by ROM words outside it
(`0x0803E36C = 0x03000868`, `0x0803F3BC = 0x03000AE0`, `0x0803F434 = 0x03000B6C`),
so a second dispatch path exists through stored pointers. The block also contains
two byte-identical copies of one 72-byte helper (`0x087B7C30`, `0x087B8898`), which
means it is at least two separately compiled objects and not one translation unit.

---

## 5. The resolved targets - the four block-memory routines

These are the routines the collection cluster reaches, and they are what
`0x030007A8` actually is. They tile `0x087B810C..0x087B820C` with no padding and
no literal pool: **every instruction is register-only**, so the pool test is not
applicable rather than failed.

| ROM | IWRAM | veneer | bytes | instr | role |
| --- | --- | --- | ---: | ---: | --- |
| `0x087B810C` | `0x03000768` | `0x08049138` | 64 | 16 | block copy, 4-byte units |
| `0x087B814C` | **`0x030007A8`** | `0x0804912C` | 84 | 21 | block fill, whole 32-bit value |
| `0x087B81A0` | `0x030007FC` | `0x08049144` | 92 | 23 | block copy, 2-byte units |
| `0x087B81FC` | `0x03000858` | `0x08049168` | 16 | 4 | block fill, 2-byte units |

**The contract, measured from the instructions and then measured again by running
the reconstruction:**

* every size argument is in **BYTES**, including the 2-byte pair. That is what
  `subs r2,r2,#0x10` after eight halfword moves and `subs r2,r2,#2` after one
  halfword move both say;
* each routine has a fast path - eight *words* (32 bytes) or eight *halfwords*
  (16 bytes) per iteration - and a tail entered by a **sized** compare;
* the tail therefore **runs at least once**: a zero-size call still stores one
  unit. `0x087B810C` and `0x087B814C` store 4 bytes at size 0, `0x087B81FC`
  stores 2, and `0x087B81A0`'s own dispatch entry cannot produce fewer than eight
  halfwords (16 bytes);
* a size that is not a whole number of units is **rounded up**: 5 -> 8 for the
  4-byte pair, 7 -> 8 and 17 -> 18 for the 2-byte pair;
* `0x087B814C` stores the **whole 32-bit** `r1`. It replicates `r1` into `r3`,
  `r4`, `r5`, `r6`, `r7`, `r8` and `ip` and never masks it to a byte - which is
  exactly why its callers can pass an **address** as the pattern;
* `0x087B81A0` enters its unrolled tail through `add pc, pc, r3, lsl #2` with
  `r3 = (16 - size) & 0xE`, an offset in *pairs*, so its first pass moves
  `8 - ((16 - size) & 0xE)/2` halfwords;
* **no zero check and no alignment check is added.** The round-up is the
  behaviour, not a bug to be tidied.

---

## 6. `sub_08011B04` and the object at `0x03001C4C`

`sub_08011B04` occupies `[0x08011B04, 0x08011C0C)` - 264 bytes, 124 instructions,
terminator `0x08011C0A pop {r4,r5,r6,r7,pc}`. It is a **reset**, and with the fill
resolved its opaque operation is now explicit. In effect order:

1. three **backward** virtual-destructor loops, one per collection, each guarded
   on `count - 1` so a zero count skips:
   * count `+0x04`, elements `+0x08+4i`, method `table + *(table+4)`;
   * count `+0x40C`, elements `+0x410+4i`, method `table + *(table+4)`;
   * count `+0x610`, elements `+0x614+4i`, method `table + *(table+8)`;
2. **five calls to the fill at `0x0804912C`** (all literals resolved from the
   pool at `0x08011DA4..0x08011DB0`):

   | # | site | destination | value | size |
   | ---: | --- | --- | --- | ---: |
   | 1 | `0x08011B76` | `object+0x08` | `0x03002A4C` | `0x200` |
   | 2 | `0x08011B8A` | `object+0x20C` | `0x03002A4C` | `0x200` |
   | 3 | `0x08011B96` | `object+0x410` | `0x03002A4C` | `0x200` |
   | 4 | `0x08011BA0` | `object+0x614` | `0x03001C44` | `0x80` |
   | 5 | `0x08011BBA` | `object+0x694` | `0xFFFFFFFF` | `0x564` |

3. the four counts `+0x04`, `+0x208`, `+0x40C`, `+0x610` all set to zero;
4. a header at `+0x694` (byte 0), `+0x696` (halfword 0), `+0x698` (halfword
   `0x200`);
5. a loop writing **137** records: byte `i+1` at `object+0x6A4+10(i-1)` and byte
   `i-1` at `object+0x6A5+10(i-1)`, for `i = 1..137`;
6. `0xFF` at `object+0x6A5` and at `object+0xBF4` - record 1's previous field and
   record 137's next field, INFERRED as the null index of a doubly linked list;
7. `object+0x00 = 0` and `object+0x01 = 1`, both bytes, at `0x08011C02` and
   `0x08011C06`.

**The arrays are NOT cleared, and the third collection still has no population
path.** The fills write the *element slots* with sentinel words (`0x03002A4C`
three times, `0x03001C44` once), and no instruction of `sub_08011B04` writes a
distinct element or increments a count. The counts are zeroed immediately after,
so no element is readable and the drain stays vacuous. "No population path"
survives in the append sense; "the area is never written" does not.

**The four collections tile contiguously**, which the sizes prove: count `+0x04`
with array `+0x08..+0x208` (128 pointers), count `+0x208` with array
`+0x20C..+0x40C` (128), count `+0x40C` with array `+0x410..+0x610` (128), count
`+0x610` with array `+0x614..+0x694` (32). Note the memory order differs from the
discovery order: the region previously called "third" sits between the "first" and
the "second".

The two fill values are themselves IWRAM objects: the stub at
`0x08048E5C..0x08048E68` stores `0x08049AF0` to `0x03001C44` and `0x0804E454` to
`0x03002A4C`, so both hold a code address in word 0 and the `table + *(table+slot)`
convention would work on them. **UNKNOWN**: what those objects are, and whether
`0x03001C4C` is a subobject of a container whose vtable word sits at `-8`.

---

## 7. Call sites

Resolved from the instructions, not by naming:

* **`sub_08011A4E` calls `0x08049138`** with `r0 = &elements[i]`,
  `r1 = &elements[i+1]`, `r2 = (count-1-i)*4`. That is a **compaction copy**,
  moving the tail of a list down over a removed slot - and it is the first call
  site whose three arguments are all resolved, which is what fixes the copy's
  byte-counted contract.
* **`sub_08011B04` calls `0x0804912C` five times** as tabulated above.
* The earlier ticket recorded the caller *functions* of this family as
  `sub_08011B04`, `sub_08011D36`, `sub_0800938C`, `sub_0803DA54`, `sub_08012230`,
  `sub_080122B4`, `sub_0803DF14` and `sub_080176AC`; each of those contains a real
  Thumb `bl` to a veneer, and `sub_08011B04` contains exactly five to `0x0804912C`.
* **No ARM `b`, `bl` or `blx` anywhere in the image reaches any veneer.** That
  sweep is arithmetic over aligned words (an ARM branch is identified from bits
  27-25 of the encoding), so it has no alignment blind spot: the result is an
  exact **zero**, and every counted caller of the family is a Thumb `bl`.

The per-veneer counts are re-derived on every run in
`config/lift_iwramblock.json` under `boundary_evidence.iwram_runtime.veneer_callers`.
That derivation is a **pattern scan and is therefore only an upper bound**: at an
offset that is not an instruction boundary four bytes can still spell a `BL`
encoding. The authoritative census was done separately, as an **aligned
chain-walk** seeded from 725 evidenced entries and expanded in tiers until 449 of
450 sites lay on a decoded chain:

| veneer | destination | sites (aligned walk) | re-derived bound (agrees) |
| --- | --- | ---: | ---: |
| `0x08049120` | `0x03000040` | 10 | 10 |
| `0x0804912C` | `0x030007A8` | **125** | 125 |
| `0x08049138` | `0x03000768` | 164 | 164 |
| `0x08049144` | `0x030007FC` | 53 | 53 |
| `0x08049150` | `0x03000388` | 32 (31 confirmed, 1 UNKNOWN) | 32 |
| `0x0804915C` | `0x030004C0` | 30 | 30 |
| `0x08049168` | `0x03000858` | 21 | 21 |
| `0x08049174`/`180`/`18C`/`198`/`1A0`/`1A8`/`1B4`/`1C0` | - | 1/1/3/1/1/1/6/1 | same |
| **total** | | **450** (449 confirmed) | 450 |

The two independent methods agree exactly, which is the strongest statement this
ticket can make about the census. One site (`0x08016A80`, into `0x08049150`) is
reached by the walk but its containing function entry is not established, and it is
recorded as UNKNOWN rather than counted as confirmed.

**Nothing takes a veneer address as a value.** A search of the whole image for the
32-bit word of each of the fifteen entries and of their odd (Thumb) forms found
exactly one hit, at an **unaligned** offset inside a compressed-asset region - a
byte coincidence, not a stored pointer. So no pointer table, literal pool or vtable
holds one of these addresses, and no register-indirect caller is hidden from the
`BL` census.

**The argument shapes, which is where the primitives become visible.** For the fill
at `0x0804912C`, `r1` is `0x00000000` at **118 of the 125 sites**. The only
resolvable non-zero fills are the three `0x03002A4C` calls and one `0x03001C44`
call in `sub_08011B04`, one `0x03001C44` call in `sub_08011D36`, and one
`r1 = 0x200`. The destinations cluster on VRAM (`0x06000000`, `0x06009640`,
`0x0600F800`, `0x0600E000`, `0x0600F000`), the palette (`0x05000000`,
`0x05000200`), EWRAM (`0x02000000`) and the caller's own pointer. So the dominant
use of the slot the previous ticket could not resolve is **filling a region with a
zero word**; the pointer-valued fills are the exception.

For the copy at `0x08049144` the shapes are the strongest single cluster in the
family: **28 sites** pass `r1` = the ROM literal `0x0805652C`, `r0` = `0x05000000`
or `0x05000200`, and `r2 = 0x200` - a 512-byte transfer from ROM into the palette
banks. That confirms the copy's `(destination, source, bytes)` contract from its
call sites rather than from its own code.

Two bound caveats are recorded rather than smoothed over: `r0` is statically
unresolved (a memory-loaded base) at a large minority of the fill sites and is
labelled unknown there rather than guessed; and the second halfword fill
(`0x03000858`) has four sites with `r1 = 0`, `r2 = 0x18` - a 24-byte zero fill -
and nothing else resolved.

---

## 8. The lift

Two things are machine-checked rather than asserted:

1. **`derive_iwram_runtime`** (in `tools/buusfury/lift.py`) re-derives, on every
   run, the DMA3 register writes, the transfer length (by which reading tiles),
   the whole veneer family, the slot-to-ROM mapping and the per-slot address
   census. Its result is committed inside `config/lift_iwramblock.json`, so a
   drift in the ROM or in the derivation is a report failure rather than a silent
   change.
2. **`src/IwramBlock.c`** reconstructs the four routines as real C, with
   `src/probes/IwramBlock.c` as a one-line shim and
   `src/probes/iwramblock_selftest.c` as the behavioural check.

| | |
| --- | --- |
| target | `iwramblock`, translation unit `iwram_block_tu`, **ARM**, `-mcpu=arm7tdmi -marm -O1` |
| ROM extent | `0x087B810C..0x087B820C` (256 bytes, no pool) |
| SEMANTIC | **PROVEN** - 165 assertions, 0 failures (minimum 160), run with MSVC 32-bit |
| MODERN_BUILD | **PASS** - arm-none-eabi-gcc 16.1.0, linked at `0x087B810C`, 552 bytes emitted |
| ADS_MATCH | **BLOCKED** - `ADS12_LICENSE_UNAVAILABLE`; no compile attempted, no configuration tested |
| comparison | 256 original vs 552 modern, 226 differing bytes, **0** matching instruction spans, `is_a_match_claim: false` |

What the self-check pins, because each is what a "tidier" reconstruction gets
wrong: the byte counts of all four routines for sixteen sizes each (computed by
hand from the ARM instructions, not from the C); the round-up tails; the
zero-size store; that the fill stores the whole 32-bit word (`0xDEADBEEF` must
not become `0xEFEFEFEF`); and that the 2-byte copy's dispatch entry always starts
at source offset 0.

**The veneers themselves are not a lift target, deliberately.** A veneer is a
hybrid Thumb/ARM stub with no single instruction set, so the harness's ISA-keyed
instruction comparison would be meaningless on it; and emitting its bytes as a
data table would be copying the image rather than reconstructing source. The
family is therefore carried as derived, machine-checked structure instead, and the
one thing a reconstruction of it must get right - the destination of each stub -
is asserted entry by entry.

---

## 9. Corrections this ticket carries

Three earlier artifacts contained claims that this work refutes. All three are
corrected in place and each correction is visible:

1. **`config/lift_targets.json` - the `collectionflush3` note**, and
   `src/ByteCodeInterpreter_collectionflush3.c` and
   [`LIFT_COLLECTIONFLUSH3.md`](LIFT_COLLECTIONFLUSH3.md) with it. The claim that
   the trampoline "jumps to whatever is stored at `0x030007A8`" and that the call
   is "NOT statically resolvable" is **REFUTED** by `0xE51FF004`.
   `config/lift_collectionflush3.json` was regenerated as a result: **only its
   `target.notes` field differs from the previous revision**, and that is a
   deliberate deviation from "existing reports stay byte-identical".
2. **[`ROM_MAP_PROVENANCE.md`](ROM_MAP_PROVENANCE.md) section 2** left the DMA3
   transfer size unresolved, reading `CNT_H = 0x8400` as "16-bit + source
   decrement -> 2050 bytes below `0x7B79A4`". **RESOLVED here**: the control word
   is `0x84000401` and the 32-bit reading is the only one that closes the block at
   both ends, giving 4100 bytes from `0x087B79A4` to `0x087B89A8` exactly where the
   0xFF fill begins. LOG1-REMAKE's 4100 was right and the alternative reading is
   refuted by internal consistency, not by preference.
3. **[`LIFT_COLLECTIONFLUSH3.md`](LIFT_COLLECTIONFLUSH3.md) and
   [`LIFT_APPEND.md`](LIFT_APPEND.md) / [`LIFT_NATIVE178.md`](LIFT_NATIVE178.md)**
   recorded that `object + 0x00` is touched by no lifted routine.
   **REFUTED for `sub_08011B04`**: `0x08011C02` writes `0` and `0x08011C06`
   writes `1` to `object+0x00` and `object+0x01`. The earlier wording held for the
   routines lifted *before* it and is corrected in the flush3 document.

The first of these also changed one test in an earlier ticket's file
(`tests/test_lift_collectionflush3.py`), which had pinned the refuted sentence;
it now pins the correction.

---

## 10. Still unknown

* The role of the two fill values `0x03002A4C` and `0x03001C44` as objects, and
  what `table+0x14` means for the third region's elements.
* What the 143-word NV table at `0x08048ED8` and the data run at `0x080491F0` are.
* The 10-byte record framing of the 137-entry list: `0x6A4 + 10k` and
  `0x69C + 10k` are both consistent with the writes here.
* What the `0x200` halfword at `object+0x698` counts (written, never read by this
  routine).
* The meaning of `0xF6400004` and of the record `0x087B8484` builds.
* Whether the object at `0x03001C4C` is also a container based at `0x03001C44`.
* Nothing here is named semantically. No name is imported from another title, and
  the block is **not** called the ADS C library.

---

## 11. Recommended next subsystem ticket

1. **The block's second dispatch path.** Five functions of the IWRAM block are
   reached only through ROM words (`0x0803E36C`, `0x0803F3BC`, `0x0803F434`,
   `0x0803FB...`) or not at all, and the IRQ dispatcher at `0x03000B6C` reaches
   fourteen handlers through a vector table at `0x03000FB0`. That is a whole
   subsystem - the IWRAM overlay's own entry protocol - and it is the natural next
   unit rather than another single function.
2. **The object at `0x03001C4C`**: `table+0x14`, the `0x200` count at `+0x698`,
   the 137-record list, and the `+0x694..0xBF8` region the reset fills with
   `0xFF`.
3. **The 143-word NV table at `0x08048ED8`** - a distinct, unreferenced structure.
4. **`sub_0804FE54`** - does it compact, and what does it do with the count?
