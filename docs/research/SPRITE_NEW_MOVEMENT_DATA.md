# SPRITE-NEW-MOVEMENT-DATA-001: why Cui did not move, and what did

Baseline `origin/master` = `0ff29c1d32f20a1fd40b2618366ae476d865efb6`. Ticket
worktree `C:\Dev\log1-remake-sprite-new-behavior-001`, branch
`ticket/sprite-new-movement-data-001`, branched from the previous ticket's
tooling commit `186ef15`. Canonical image read only and re-verified after every
run (`940ad5f0...36f059e`); the private source save likewise
(`8062e8bf...3080953`).

## Verdict

The first candidate, record `+0x0C`, is **refuted**. The movement data is the
**wander box carried by the template the record's `+0x18` names**: four
halfwords at template `+8..+0xF`, which the class-A handler copies to the
behaviour object's `+0x48..+0x57`. The walk method accepts a step only while the
actor's own rect, translated by that step, stays inside the box; Cui's authored
position (`x 0xD1`, `y 0x244`) is outside the box he inherited
(`x 0x148..0x1A0`), so **every step in x was declined**. Widening the authored
template's box to contain his position makes him walk.

**MOVEMENT DATA BOUNDARY: CONFIRMED.**

## 1. `+0x0C` is not movement data

`0x08017C1C` stores its third argument, `record + 0x0C`, in the actor:

```text
08017c5e  ldr  r2,[sp,#0x1c]      ; record + 0x0C
08017c62  str  r2,[r1,#0x10]      ; r1 = actor + 0x1C0, so actor + 0x1D0
```

Every site that addresses an actor offset above `0xFF` in this image uses
`adds rD,#0xFF ; adds rD,#rest`. A whole-image scan of that idiom finds:

| actor field | sites |
| --- | --- |
| `+0x1A0` (position x) | 161 |
| `+0x1A4` (position y) | 20 |
| `+0x1BC` | 1 (the constructor's own store) |
| `+0x1C0` | 87 |
| `+0x1C4`, `+0x1C8`, `+0x1CC` | 0 |
| **`+0x1D0`** | **1** |
| `+0x1D4` | 4 |

The single site is `0x0801455E..0x08014568`, inside `0x08014526`:

```text
08014544  movs r0,#0xff
08014546  adds r0,#0x1d
08014548  ldr  r0,[r0,r4]        ; *(actor + 0x11C)
0801454a  cmp  r0,#0
0801454c  bne  0x0801455e
0801454e  adds r2,r4,#0xff ; adds r2,#0x2d   ; actor + 0x12D
08014558  bl   0x08014424
0801455e  adds r2,r4,#0xff ; adds r2,#0xd1   ; actor + 0x1D0
08014568  bl   0x08014424        ; (actor, sp, actor + 0x1D0)
```

`0x08014424` is a **formatting** path: it writes through the pointer argument
and the enclosing routine formats with `0x0803F540` and `0x08049150` at
`0x08014574`. The field's *address* is what is handed over, and no routine that
moves an actor reads it. `record + 0x0C` also has only two referencing sites in
the whole image: the record's own field and a table at `0x0879B9D4/N8/DC`, the
resource-table region.

**Measured:** changing it to the moving sibling's value changed nothing (section
4, arm `mv001-data`).

## 2. What actually decides a step

The class-A behaviour object is built by `0x0800A7A0`, whose class word is
`0x0804D4E4`. Its `vtable+0x10` is `0x0800A624`:

```text
0800a624  ldr r2,[r0,#0x48]   ; obj+0x48   x1  \
0800a626  ldr r3,[r0,#0x38]   ; obj+0x38   x1'  |  accept only while the
0800a628  cmp r2,r3                                     translated rect
0800a62a  bgt 0x0800a644      ; x1 > x1'  -> decline    (obj+0x38..0x44)
0800a62c  ldr r2,[r0,#0x4c]   ; y1                      stays inside the
0800a62e  ldr r3,[r0,#0x3c]   ; y1'                     bounds
0800a630  bgt 0x0800a644      ; -> decline              (obj+0x48..0x54)
0800a634  ldr r2,[r0,#0x50]   ; x2
0800a636  ldr r3,[r0,#0x40]   ; x2'
0800a638  blt 0x0800a644      ; -> decline
0800a63c  ldr r2,[r0,#0x54]   ; y2
0800a63e  ldr r3,[r0,#0x44]   ; y2'
0800a640  cmp r2,r3
0800a642  bge 0x0800a648      ; accept, walk at 0x0800A526
0800a644  movs r0,#0
0800a646  bx   lr             ; DECLINE: return 0, no movement
```

- `obj+0x28..0x37` is the actor's own rect, filled by `0x0800FDFA` from the
  actor; `obj+0x38..0x47` is that rect translated by the step (built at
  `0x0800A360..0x0800A39A`).
- `obj+0x48..0x57` is four **words** (not packed halfwords):
  `0x0800A7CC..0x0800A7D6` does four `ldrh` from template `+8,+0xA,+0xC,+0xE`
  and `stm r4!,{r0,r1,r2,r3}` stores each zero-extended halfword as a word.
  They are the wander box `(x1, y1, x2, y2)` in pixels.

The class-A think routine `0x0800A2A8` steps the target by `+/-0x80` (128 px)
along a random heading and then calls `vtable+0x10`; a decline leaves the actor
where it is and a later frame tries again.

## 3. The measurement that named it

Observer `tools/runtime/spritenew004_registration.lua`, cold boot, map 102,
1800 frames, breakpoint `0x0800A3B0` (the instruction after the think routine's
walk call) logging the result and both rectangles. Same run, same instrument
for Cui and every retail sibling:

| actor | record | result | obj+0x38..0x44 (translated rect) | obj+0x48..0x54 (bounds) |
| --- | --- | --- | --- | --- |
| Cui `0x0202D0CC` | `0x08801F38` | **0** | `0xD1,0x254,0xE1,0x25C` | `0x148,0x238,0x1A0,0x298` |
| `0x0202D894` | `0x0807846C` (mover) | **1** | `0x170,0x270,0x180,0x278` | `0x148,0x238,0x1A0,0x298` |
| `0x0202D4B0` | `0x08078498` (mover) | 1 | `0x300,0x168,0x310,0x170` | `0x2D8,0x138,0x348,0x1A8` |
| `0x0203DC78` | `0x08078348` (mover) | 1 | `0x288,0x220,0x298,0x228` | `0x250,0x200,0x2F0,0x2A0` |

Cui and `0x0807846C` dispatch **byte-identical** templates (the builder asserts
it), yet the same box accepts the sibling at `x 0x170` and refuses Cui at
`x 0xD1`, because `0x148 > 0xD1`: the first comparison fails. In 289 samples
Cui's walk returned 0 every time, while every moving sibling returned 1 at least
once and 0 on other attempts (a step that would leave the box is declined
normally).

## 4. The experiments

Builder `tools/research/sprite_new_behavior_registration.py` emits every image
from the same identity material; only the listed words differ.

| arm | image sha256 | change from the behaviour fix | result |
| --- | --- | --- | --- |
| `after` (previous ticket) | `9e384a7b...` | `+0x18` = own class-A template | walks declined, no movement |
| `mv001-data` | `983323814c536497b7097f688f381f4d470b0865cbacfd49afc7ad1fe5c81146` | `+0x0C` `0x0878565C -> 0x0878566C` (the moving sibling's) | **no change**: walk still 0 every time, position static |
| `mv003-bounds` | `3354d7c3082209ebf33bda6ce0e05e290a9845593e1b8ce842083da40dd16a40` | template box `x 0x148..0x1A0, y 0x238..0x298` -> `x 0xC0..0x110, y 0x220..0x270` | **Cui moves** |

`mv003-bounds`, measured:

```text
walk.txt 647 0x0202D0CC result 1  rect 0xD1,0x254,0xE1,0x25C  bounds 0xC0,0x220,0x110,0x270
walk.txt 751 0x0202D0CC result 0  rect 0xD1,0x274,0xE1,0x27C  bounds 0xC0,0x220,0x110,0x270
actor 0x0202D0CC record 0x08801F38 sprite 307  +0x1A0:0x0000D100 -> 0x0000F100
                                              +0x1A4:0x00024480 -> 0x00026400
```

Cui's position moved 32 px in x and 31.5 px in y, the accept/decline rhythm is
the one the retail movers show, the class-A behaviour object is still built
(`allocated.txt` row for `0x08801F38`, sprite 307), its target and rect words
track the movement, the seven retail movers still move, and the two class-B
records (`0x08078440`, `0x0807841C`) still do not. Sprite identity 307, the
graphics, the placement and `+0x18` are untouched.

Images reproduced for the record: `after` `29f9195a` for the pre-behaviour build
and `9e384a7b` for the behaviour build; `mv001-data` and `mv003-bounds` above.
Both images are 16 MiB, the changes are inside the generated expansion, and the
canonical image and the private save were re-verified unchanged after every run.

## 5. Acceptance

- **Meaning of `+0x0C` if proven:** a resource pointer kept at `actor + 0x1D0`,
  consumed only as an address by the formatting path at `0x0801455E`. **Not**
  movement data.
- **Runtime consumer:** `0x0800A624` (class `0x0804D4E4` `vtable+0x10`), which
  reads the box at `obj+0x48..0x57` (from the template) and the actor rect at
  `obj+0x28..0x37` / `obj+0x38..0x47`.
- **Exact before/after field values:** `+0x0C` `0x0878565C -> 0x0878566C`
  (inert); template box `x 0x0148..0x01A0, y 0x0238..0x0298` ->
  `x 0x00C0..0x0110, y 0x0220..0x0270` (moves).
- **Does Cui's position change?** Yes, in `mv003-bounds`: `x 0x0000D100 ->
  0x0000F100`, `y 0x00024480 -> 0x00026400`. No, in `mv001-data`.
- **Smallest remaining unknown:** none for movement on this map. The box that
  contains a given authored position is still chosen by eye; nothing has
  measured how each template's box relates to its own actor's spawn, and the
  box semantics are measured only on map 102.

## 6. Instrument notes

1. Breakpoint sites inside a routine fire reliably here (`0x0800A93C`,
   `0x0800A9A4`, `0x0800A7C0`, `0x0800A3B0`, `0x08017DA2`, `0x08017DB0`); the
   routine-entry sites that failed in the earlier tickets were not used.
2. The upper-actor-offset scan is only correct with the compiler's own idiom
   (`adds #0xFF` then `adds #(offset - 0xFF)`). A first scan that split the
   offset into high and low bytes reported "0 readers" for `+0x1D0`, which would
   have been a false negative.
3. `walk.txt` is written from the post-call site, so its rectangle values are
   the live ones the walk method itself compared, not a reconstruction.
