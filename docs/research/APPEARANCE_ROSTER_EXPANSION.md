# Growing the roster/display-list structure

APPEARANCE-ROSTER-EXPANSION-001. Base candidate `a57a332`.

The appearance work can append records, but the engine's roster builder is sized
for exactly the 232 canonical ones. This document is the required proof pass that
comes before any implementation: what the structure is, who owns it, every site
that states its layout, and how far the count can go.

Evidence labels are the project's: CONFIRMED means the bytes were read here,
INFERRED means the conclusion rests on reasoning over measurements. Addresses are
GBA addresses; file offset is address minus `0x08000000`.

## 1. The containing object, and its extent - CONFIRMED

The builder is `0x08024F3C`. Its first instructions decide everything:

```
08024f3e  adds r4, r0, #0        ; r4 = arg0
08024f40  bne  0x08024F52        ; a caller-supplied buffer is used as-is
08024f42  movs r0, #0x59
08024f44  lsls r0, r0, #5        ; 0xB20
08024f46  bl   0x0803D5B8        ; heap allocation
```

**The one caller passes NULL.** At `0x08007510`-`0x08007512` inside the function
at `0x080073F0`:

```
08007510  movs r0, #0            ; arg0 = 0
08007512  bl   0x08024F3C
```

So the object is heap-allocated per construction and there is **no static buffer
to enlarge**. `0x08024F3C` has exactly one BL caller in the image; that caller is
itself reached indirectly and has no BL callers.

The layout, read from the builder's own arithmetic, is parameterised by the entry
count N:

| offset | field |
| --- | --- |
| `+0x00` | vtable word |
| `+0x10` | entry count |
| `+0x14` | N entries, 4 bytes each |
| `+0x14 + 4N` | second count (the display-list count) |
| `+0x18 + 4N` | N display entries, 8 bytes each |
| `+0x18 + 12N` | tail fields |
| total | **`0x40 + 12N`** |

`N = 232` gives `64 + 2784 = 2848 = 0xB20`, which is the allocation size. The
arithmetic is confirmed by the code that performs it, not by assumption.

The append loop, `0x08024F6E`-`0x08024F94`:

```
08024f6e  ldr  r3, [r6, #8]      ; the seen-flag block
08024f70  asrs r5, r0, #3        ; index >> 3
08024f74  adds r3, #0xC0
08024f7a  ldrb r3, [r3, #5]      ; block + 0xC5 + (index>>3)
08024f7c  movs r5, #1
08024f7e  lsls r5, r7            ; 1 << (index & 7)
08024f80  ands r3, r5
08024f82  beq  0x08024F90        ; not seen, next index
08024f84  ldr  r3, [r1]          ; count at +0x10
08024f88  lsls r3, r3, #2
08024f8a  adds r3, r3, r1
08024f8e  str  r0, [r3, #4]      ; entry[count] = index, at +0x14 + 4*count
08024f90  adds r0, #1
08024f92  cmp  r0, #0xE8
08024f94  blt  0x08024F6E
```

There is **no bounds check on the count**. The loop is bounded only by the index
bound `0xE8`, and one entry is appended per seen appearance. With 233 seen
appearances the second count at `+0x3B4` - the very next field - is overwritten.

The display half, `0x08024F96`-`0x08024FD4`, walks the entries, reads each
record's first halfword (`ldrh r5, [record + 0x00]`, table base from the pool at
`0x08024FA0`), skips a value equal to the previous one, and appends **8 bytes per
kept entry** at `base + 0x3B8 + 8 * displayCount`.

The tail, `0x08024FD6`-`0x08024FFE`, is built as `0x2B << 6` (`0xAC0`) plus stride
`+0x38` / `+0x3C`, and `0xB << 8` (`0xB00`) plus `+0x0C` / `+0x10` / `+0x14`.

## 2. Ownership of the roster bitset - CONFIRMED

The bitset is **not** in the roster object. It lives in the block reached as
`[X + 8]` (`0x03001068` at run time): bit `index & 7` of the byte at
`block + 0xC5 + (index >> 3)`.

Exactly two sites in the whole image touch it:

- `0x08024F74`, the roster builder's read (quoted above);
- `0x08025E86`, the appearance constructor's write, in the function at
  `0x08025E50`:

```
08025e76  asrs r2, r5, #3        ; index >> 3
08025e80  ldr  r1, [r0, #8]      ; the block
08025e86  adds r1, #0xC0
08025e8a  ldrb r2, [r1, #5]      ; block + 0xC5 + (index>>3)
08025e8c  lsls r3, r6            ; 1 << (index & 7)
08025e8e  orrs r2, r3
08025e90  strb r2, [r1, #5]
08025e92  lsls r1, r5, #4
08025e9a  str  r1, [r4, #0x20]   ; record[index]
```

Both derive the byte from the index, so **the loop bound the build already patches
is the only thing that decides how far the bitset is reached**. The constructor
also shows the coupling that started this ticket: one index sets both the flag and
the record pointer.

## 3. Ownership of the display list - CONFIRMED

Inside the roster object, at `+0x3B8`, 8 bytes per entry, capacity N, written by
the builder at `0x08024FBE`-`0x08024FCC` as `r2 + displayCount * 8 + 4` where `r2`
is the object base plus the second-count offset.

## 4. Every reader and writer - CONFIRMED

Fourteen sites for the roster object, across five functions:

| function | sites | what they state |
| --- | --- | --- |
| `0x08024F3C` | `0x08024F42`, `0x08024F60`, `0x08024F6C`, `0x08024FD6`, `0x08024FE0`, `0x08024FE4`, `0x08024FF4`, `0x08024FFE`, `0x0802502C` | size, both counts, both tail bases |
| `0x08025354` | `0x0802536E` | tail-B |
| `0x08025404` | `0x0802541C` | second count |
| `0x08025510` | `0x08025514`, `0x0802552C` | second count, tail-B |
| `0x080255C4` | `0x0802561E`, `0x08025638` | tail-B, tail-A |

Callers: `0x08024F3C` from `0x08007512`; `0x08025404` from `0x080255BE`;
`0x08025354`, `0x08025510` and `0x080255C4` have no BL callers and are reached
indirectly.

Two apparent extra bitset sites at `0x08044206` and `0x0804459E` are **false
positives**: both reach `block+0xDC`, a pointer, and then dereference it
(`ldr r0, [r0, #0x1C]` then `ldrb r0, [r0, #5]`). They never touch the array.

## 5. Every layout-dependent constant - CONFIRMED

Found by scanning the image for the exact `movs` + `lsls` idioms and for literal
words equal to each constant:

| constant | idiom | sites |
| --- | --- | --- |
| `0xB20` size | `0x59 << 5` | **1** - `0x08024F42` |
| `0x3B4` second count | `0xED << 2` | **4** - `0x08024F60`, `0x08025112`, `0x0802541C`, `0x08025514` |
| `0xAC0` tail-A | `0x2B << 6` | **4** - `0x08024FD6`, `0x0802502C`, `0x08025106`, `0x08025638` |
| `0xB00` tail-B | `0x0B << 8` | **5** - `0x08024FE0`, `0x0802500E`, `0x0802536E`, `0x0802552C`, `0x0802561E` |

No literal pool word in the image equals `0xB20`, `0x3B4`, `0xAF8`, `0xAC0` or
`0xB00`. One data word equals `0x3B8` at GBA `0x08072158`, in the map/data region,
unrelated to this object.

## 6. Can the data at +0x3B4 move independently - CONFIRMED, yes

The second count is named by four sites as an offset from the object base, and the
display-entry base is **derived** from it (`r2 + 4`). Moving both is therefore
those four patches and no data movement: no pointer to fix up, no relocation
table, nothing else refers to the array's address.

## 7. Maximum count the encoded widths support

- The record count is a Thumb `cmp rN,#imm8`, so **255 is the hard cap**.
- The bitset needs `ceil(N/8)` bytes from `block+0xC5`. N=240 ends at `+0xE2`;
  N=248 adds `+0xE3`; N=248 or above would write the word the block's initializer
  zeroes at `+0xE4`, so **248 is unreachable**.
- Nothing in the appearance/roster region `0x08024000`-`0x08026000` adds `0xE0`,
  `0xE1`, `0xE2`, `0xE3` or `0xE4` to any base. The initializer region
  `0x08004000`-`0x08005000` adds `0xE4` at seven sites (the block-init family) and
  none of `0xE0`..`0xE3`.

**Supported N is therefore 240**, which needs only `+0xE2` - the single byte
immediately after the canonical 232-bit array. `0xE3` would be reachable at 248
and is left unused deliberately.

## 8. Save data and narrower fields

**OUTSTANDING.** Whether any save block or subsystem stores an appearance id or
count in a field narrower than the table's 32-bit form has not been established
here. Four bounded read-only passes were run against this and the other items;
their results must be folded in before this proof is called complete.

## The fixture for N = 240

| what | canonical | at N = 240 |
| --- | --- | --- |
| size | `0xB20` | `0xB80` |
| entries end | `+0x3B3` | `+0x3D3` |
| second count | `+0x3B4` | `+0x3D4` |
| display entries | `+0x3B8`..`+0xAF7` | `+0x3D8`..`+0xB57` |
| tail-A | `+0xAF8` | `+0xB58` |
| tail-B | `+0xB00` | `+0xB60` |

Every value is encodable with the same two-instruction idiom the code already
uses, so the change is a constant patch rather than new code:

- size: `movs #0x5C; lsls #5` (shift unchanged from `0x59<<5`)
- second count: `movs #0xF5; lsls #2` (shift unchanged from `0xED<<2`)
- tail-A: `movs #0x59; lsls #5` then strides `+0x38`/`+0x3C` (shift 6 becomes 5)
- tail-B: `movs #0x5B; lsls #5` (shift 8 becomes 5)

**23 halfword patches across the fourteen sites, no data movement, no extra
allocation, deterministic.**

## What this leaves

The builder's overflow is confirmed rather than refuted, so the structural route
is required: grow the object and move its two dependent offsets, with the count
itself capped at 240 and a build that fails closed above it. The bitset needs no
separate allocation - it has room for 240 bits in the block it already lives in,
and only the two sites above ever touch it.
